import copy
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import pytest
from test_recovery import client, observation, response, valid
from test_dropout import setup
from model import V4Decision, digest
from run import defaults, SOURCE
from llm_client import QuotaPause, AgentRequestFailure


@pytest.mark.parametrize("workers", [5, 10])
def test_parallel_ledger_context_and_cache(tmp_path, monkeypatch, workers):
    c = client(tmp_path, monkeypatch)
    c.cfg["max_concurrency"] = workers
    barrier = threading.Barrier(workers)
    def create(**kwargs):
        barrier.wait(timeout=15)
        return response(valid())
    c.client.chat.completions.create = create
    obs = []
    for i in range(workers):
        ob = copy.deepcopy(observation(tmp_path))
        ob.agent_id = f"A{i+1:04d}"
        obs.append(ob)
    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(lambda ob: c.decide(ob, "{当前观察}"), obs))
    b = json.loads(c.budget_path.read_text())
    assert b["requests"] == workers and b["actual_input_tokens"] == 100 * workers
    assert b["actual_output_tokens"] == 20 * workers
    records = [json.loads(p.read_text(encoding="utf-8")) for p in tmp_path.glob("request-*.json")]
    mapping = {r["request_number"]: r["agent_id"] for r in records}
    assert len(mapping) == workers and len(set(mapping.values())) == workers
    for line in (tmp_path/"request-events.jsonl").read_text().splitlines():
        e = json.loads(line)
        if "request_number" in e:
            assert mapping[e["request_number"]] == e["agent_id"]
    recovered = client(tmp_path, monkeypatch)
    def forbidden(**kwargs):
        raise AssertionError("cache recovery must not issue a request")
    recovered.client.chat.completions.create = forbidden
    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(lambda ob: recovered.decide(ob, "{当前观察}"), obs))
    assert recovered.budget["requests"] == workers


def test_parallel_hard_cap(tmp_path, monkeypatch):
    c = client(tmp_path, monkeypatch); c.cfg["max_requests"] = 2
    c.client.chat.completions.create = lambda **kwargs: response(valid())
    def task(i):
        ob = observation(tmp_path); ob.agent_id = f"A{i+1:04d}"
        try:
            c.decide(ob, "{当前观察}")
            return True
        except RuntimeError:
            return False
    with ThreadPoolExecutor(5) as pool:
        assert sum(pool.map(task, range(5))) == 2
    assert json.loads(c.budget_path.read_text())["requests"] == 2


def test_round_barrier_dropout_and_global_stop(tmp_path):
    env, _ = setup(tmp_path)
    ids = [a for a,r in env.by_id.items() if r["decision_mode"]=="llm"
           and env.observe(a,1).local_information["posts"]][:10]
    observations = [env.observe(a,1) for a in ids]
    dec = V4Decision(defaults(), SOURCE/"02_Prompt固定提示词.md", tmp_path, "scripted")
    dec.mode = "openai"
    original = digest(env.snapshot())
    called = []
    barrier = threading.Barrier(5)
    def decide(ob, template):
        called.append(ob.agent_id)
        barrier.wait(timeout=15)
        assert digest(env.snapshot()) == original
        if ob.agent_id == ids[0]:
            raise QuotaPause("fake quota")
        time.sleep(.1)  # Let the scheduler observe the global error before any refill.
        return valid(), ob.local_information["posts"], {}
    dec.client = SimpleNamespace(decide=decide)
    with pytest.raises(QuotaPause):
        dec.decide_batch(observations, {})
    assert set(called) == set(ids[:5])
    assert digest(env.snapshot()) == original
    def dropout(ob, template):
        if ob.agent_id == ids[0]:
            raise AgentRequestFailure("fake exhausted timeout")
        return valid(), ob.local_information["posts"], {}
    dec.client.decide = dropout
    actions = dec.decide_batch(observations, {})
    assert [a.agent_id for a in actions] == ids
    assert not env.offline
    env.apply(actions)
    assert set(env.offline) == {ids[0]}
    assert all(env.beliefs[a] == "reject" for a in ids[1:])


@pytest.mark.parametrize("workers", [5, 10])
def test_rolling_refill_does_not_wait_for_slowest_and_preserves_order(tmp_path, workers):
    dec = V4Decision(defaults(), SOURCE/"02_Prompt固定提示词.md", tmp_path, "scripted")
    dec.mode = "openai"
    dec.cfg["max_concurrency"] = workers
    released = threading.Event()
    lock = threading.Lock()
    active = 0
    peak = 0
    def fake(obs, memories):
        nonlocal active, peak
        idx = obs[0].agent_id
        with lock:
            active += 1
            peak = max(peak, active)
        try:
            if idx == 0:
                assert released.wait(3), "rolling refill blocked behind the slowest task"
            if idx == workers:
                released.set()
            return [idx]
        finally:
            with lock:
                active -= 1
    dec._decide_serial = fake
    obs = [SimpleNamespace(agent_id=i) for i in range(workers+5)]
    assert dec.decide_batch(obs, {}) == list(range(workers+5))
    assert peak <= workers
