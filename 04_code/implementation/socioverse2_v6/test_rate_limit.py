import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import pytest
from test_recovery import client, observation, response, valid
from llm_client import QuotaPause
from throttle import RateGate, safe_response_metadata


class Limit(Exception):
    status_code = 429
    code = "rate_limit"
    body = {"error": {"message": "concurrent requests exceed limit; secret=do-not-log"}}
    response = SimpleNamespace(headers={"retry-after": "0", "Authorization": "secret"})


def fast(c):
    c.cfg.update(rate_limit_wait_seconds=0, rate_limit_spacing_seconds=0)


@pytest.mark.parametrize("status", [429, 529])
def test_429_recovers_same_prompt_no_dropout(tmp_path, monkeypatch, status):
    monkeypatch.setattr(Limit, "status_code", status)
    c = client(tmp_path, monkeypatch); fast(c)
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise Limit()
        return response(valid())
    c.client.chat.completions.create = create
    answer, _, _ = c.decide(observation(tmp_path), "{当前观察}")
    assert answer["belief"] == "reject" and calls[0] == calls[1]
    assert c.budget["requests"] == 2
    assert c.budget["usage_unknown_requests"] == 1
    assert c.gate.state["effective_concurrency"] == 2
    text = (tmp_path/"request-events.jsonl").read_text()
    assert "rate_limit_cooldown" in text and "validation_passed" in text
    assert "do-not-log" not in text and "Authorization" not in text
    first = json.loads((tmp_path/"request-000001.json").read_text(encoding="utf-8"))
    assert first["diagnostic"]["provider_hints"] == ["concurrency"]


@pytest.mark.parametrize("status", [429, 529])
def test_retry_limit_persists_across_restart(tmp_path, monkeypatch, status):
    monkeypatch.setattr(Limit, "status_code", status)
    c = client(tmp_path, monkeypatch); fast(c)
    def create(**kwargs):
        raise Limit()
    c.client.chat.completions.create = create
    ob = observation(tmp_path)
    with pytest.raises(QuotaPause):
        c.decide(ob, "{当前观察}")
    assert c.budget["requests"] == 7
    recovered = client(tmp_path, monkeypatch); fast(recovered)
    recovered.client.chat.completions.create = lambda **kwargs: pytest.fail("must not dispatch")
    with pytest.raises(QuotaPause):
        recovered.decide(ob, "{当前观察}")
    assert recovered.budget["requests"] == 7


def test_global_cooldown_then_single_concurrency(tmp_path):
    events = []
    gate = RateGate({"max_concurrency":5, "rate_limit_wait_seconds":.12,
                     "rate_limit_spacing_seconds":.01}, tmp_path,
                    lambda stage, **kw: events.append((stage, kw)))
    gate.limited(1)
    gate.limited(2)
    assert gate.state["effective_concurrency"] == 1
    entered, active, peak = [], 0, 0
    lock = threading.Lock()
    end = gate.state["cooldown_until"]
    def work():
        nonlocal active, peak
        with gate.slot():
            with lock:
                entered.append(time.time()); active += 1; peak = max(active, peak)
            time.sleep(.02)
            with lock:
                active -= 1
    with ThreadPoolExecutor(5) as pool:
        list(pool.map(lambda _: work(), range(5)))
    assert min(entered) >= end
    assert peak == 1
    restored = RateGate({"max_concurrency":5}, tmp_path, lambda *a, **k: None)
    assert restored.state["effective_concurrency"] == 1
    assert any(s == "rate_gate_wait" for s,_ in events)


def test_retry_after_and_success_service_refusal(tmp_path, monkeypatch):
    assert safe_response_metadata(SimpleNamespace(headers={"retry-after":"17","set-cookie":"secret"})) == {"retry_after_seconds":17}
    assert safe_response_metadata(SimpleNamespace(headers={"retry-after":"nan"})) == {}
    c = client(tmp_path, monkeypatch); fast(c)
    calls = []
    def create(**kwargs):
        calls.append(1); r = response(valid())
        if len(calls) == 1:
            r.base_resp = {"status_code":1002}
        return r
    c.client.chat.completions.create = create
    c.decide(observation(tmp_path), "{当前观察}")
    assert len(calls) == 2
    assert json.loads((tmp_path/"request-000001.json").read_text())["status"] == "quota_paused"


def test_default_backoff_sequence_and_cap(tmp_path):
    events = []
    gate = RateGate({"max_concurrency": 5}, tmp_path,
                    lambda stage, **kw: events.append((stage, kw)))
    for failure in range(1, 9):
        gate.limited(failure)
    assert [data["wait_seconds"] for stage, data in events] == [2, 4, 8, 16, 32, 60, 60, 60]
    gate.limited(1, retry_after=90)
    assert events[-1][1]["wait_seconds"] == 90

def test_recovery_needs_success_and_time_and_persists(tmp_path, monkeypatch):
    clock = [1000.]
    monkeypatch.setattr('throttle.time.time', lambda: clock[0])
    events=[]
    cfg={'max_concurrency':5,'rate_recovery_successes':3,'rate_recovery_seconds':60}
    gate=RateGate(cfg,tmp_path,lambda stage,**kw:events.append((stage,kw)))
    gate.limited(1)
    for _ in range(3):gate.succeeded()
    assert gate.state['effective_concurrency']==2
    clock[0]=1062
    gate.succeeded()
    assert gate.state['effective_concurrency']==3
    assert gate.state['dispatch_spacing']==.5
    gate=RateGate(cfg,tmp_path,lambda *a,**k:None)
    assert gate.state['effective_concurrency']==3
    for _ in range(3):gate.succeeded()
    assert gate.state['effective_concurrency']==3
    gate.failed()
    clock[0]+=61
    gate.succeeded()
    assert gate.state['effective_concurrency']==3
    gate.succeeded();gate.succeeded()
    assert gate.state['effective_concurrency']==4
    clock[0]+=61
    for _ in range(3):gate.succeeded()
    assert gate.state['effective_concurrency']==5 and gate.state['dispatch_spacing']==0
    clock[0]+=61
    for _ in range(4):gate.succeeded()
    assert gate.state['effective_concurrency']==5
    gate.limited(1)
    assert gate.state['effective_concurrency']==2 and gate.state['success_streak']==0
    assert any(s=='decision_throughput' for s,_ in events)


def test_halted_gate_does_not_recover(tmp_path,monkeypatch):
    gate=RateGate({'max_concurrency':10,'rate_recovery_successes':1,'rate_recovery_seconds':0},tmp_path,lambda *a,**k:None)
    gate.limited(1);gate.halt()
    gate.state['cooldown_until']=0
    gate.succeeded()
    assert gate.state['effective_concurrency']==5
