import copy
import json
from types import SimpleNamespace

import pytest
from socioverse.engine import build_simulator
from socioverse.schemas import Action, WarmStartSpec
from model import (V4Environment, V4Decision, load_rows, make_network, targets,
                   normalize_answer, empty_answer, digest)
from run import SOURCE, defaults, make_bundles


@pytest.mark.parametrize("text", ['{"ok":true}', '```json\n{"ok":true}\n```', '```\n{"ok":true}\n```'])
def test_json_transport_wrapper(text):
    from llm_client import parse_json_object
    assert parse_json_object(text) == {"ok": True}


@pytest.mark.parametrize("text", ['Here is JSON: {"ok":true}', '[{"ok":true}]',
    '```json\n{"ok":true}\n```\nextra', '{"ok":true', '<think>x</think>{"ok":true}'])
def test_json_rejects_prose_and_malformed(text):
    from llm_client import parse_json_object
    with pytest.raises(ValueError):
        parse_json_object(text)


def test_minimax_request_profile():
    from llm_client import request_options
    cfg = {**defaults(), "api_profile": "minimax_m3", "model": "MiniMax-M3"}
    options = request_options(cfg)
    assert options["extra_body"]["thinking"] == {"type": "disabled"}
    assert options["extra_body"]["reasoning_split"] is True
    assert options["max_tokens"] == 512
    assert "response_format" not in options
    assert request_options(defaults())["response_format"] == {"type": "json_object"}
    cfg["model"] = "MiniMax-M3.1-Flash"
    with pytest.raises(ValueError):
        request_options(cfg)


@pytest.fixture
def bundles(tmp_path):
    return make_bundles(SOURCE / "01_Agent基础信息表.csv", SOURCE / "02_Prompt固定提示词.md",
                        defaults(), tmp_path / "audit")


@pytest.fixture
def env(bundles):
    e = V4Environment(bundles[1])
    e.reset(20261020)
    return e


def test_network_population_and_initial(env):
    edges = make_network(env.rows)
    assert len(edges) == len(set(edges)) == 5902
    assert edges == make_network(env.rows)
    for row in env.rows:
        aid = row["agent_id"]
        ordinary = [b for a, b in edges if a == aid and b != "SOURCE"]
        assert aid not in ordinary
        assert sum(env.by_id[b]["group"] == row["group"] for b in ordinary) == 8
        assert sum(env.by_id[b]["group"] != row["group"] for b in ordinary) == 2
    assert set(env.beliefs.values()) == {"unjudged"}
    assert all(not m for m in env.memory.values())
    assert len(targets(env.rows)) == 40


def test_schedule_visibility_and_targets(env):
    assert not env.observe("A0002", 0).local_information["posts"]
    first = env.observe_batch(list(env.by_id), 1)
    assert sum(bool(o.local_information["posts"]) for o in first) == 82
    assert all("G001" not in str(o.local_information) for o in first)
    env.advance_to(20)
    obs = env.observe_batch(list(env.by_id), 20)
    seen = [o for o in obs if any(p["content_id"] == "G001" for p in o.local_information["posts"])]
    assert len(seen) == 40
    assert {o.agent_id for o in seen} == set(env.direct_targets)
    assert all(o.local_information["posts"][0]["content_id"] == "G001" for o in seen)
    assert all(len(o.local_information["posts"]) <= 5 for o in obs)
    assert not any(p["content_id"] == "G001" for o in env.observe_batch(list(env.by_id), 21) for p in o.local_information["posts"])


def test_duplicate_repost_preserves_belief_comment_and_raw(env, bundles, tmp_path):
    env.advance_to(1)
    ob = env.observe("A0002", 1)
    dec = V4Decision(**bundles[3].decision_args)
    a = dec.decide_batch([ob], {})[0]
    env.apply([a])
    assert env.beliefs["A0002"] == "believe"
    assert env.reposted["A0002"] == {"P001"}
    snapshot = digest(env.snapshot())
    env.apply([a])
    assert digest(env.snapshot()) == snapshot
    # A different delivery of the same root is visible, but cannot be reposted twice.
    author = next(x for x in env.following["A0002"] if x != "SOURCE")
    env.posts["RP-test"] = {**env.posts["P001"], "content_id": "RP-test", "author_id": author,
                            "published_tick": 1, "available_tick": 2}
    env.advance_to(2)
    second = dec.decide_batch([env.observe("A0002", 2)], {})[0]
    assert second.payload["raw_answer"]["repost"]["enabled"] is True
    assert second.payload["answer"]["repost"]["enabled"] is False
    assert second.payload["decision_status"] == "partially_applied"
    env.apply([second])
    assert "C02-A0002" in env.comments
    assert "RP02-A0002" not in env.posts
    assert len(env.memory["A0002"]) == 2


def test_new_actions_next_tick_and_comment_limit(env, bundles):
    env.advance_to(1)
    dec = V4Decision(**bundles[3].decision_args)
    actions = dec.decide_batch(env.observe_batch(list(env.by_id), 1), {})
    env.apply(actions)
    assert all(p["published_tick"] == 0 for o in env.observe_batch(list(env.by_id), 1)
               for p in o.local_information["posts"])
    assert any(p["content_id"].startswith("RP") for o in env.observe_batch(list(env.by_id), 2)
               for p in o.local_information["posts"])
    assert all(len(p["comments"]) <= 2 for o in env.observe_batch(list(env.by_id), 2)
               for p in o.local_information["posts"])


def test_gt_failure_preserves_unjudged(env, bundles):
    env.advance_to(20)
    aid = next(a for a in env.direct_targets if env.by_id[a]["decision_mode"] == "rule")
    args = copy.deepcopy(bundles[3].decision_args)
    args["config"]["gt"] = 0
    a = V4Decision(**args).decide_batch([env.observe(aid, 20)], {})[0]
    assert a.payload["answer"]["belief"] == "unjudged"
    assert [d["name"] for d in a.payload["draws"]] == ["GT"]
    env.apply([a])
    assert env.beliefs[aid] == "unjudged"


def test_invisible_target_rejected_atomically(env, bundles):
    env.advance_to(1)
    dec = V4Decision(**bundles[3].decision_args)
    actions = dec.decide_batch(env.observe_batch(["A0002", "A0003"], 1), {})
    bad = copy.deepcopy(actions[-1])
    bad.payload["answer"]["repost"] = {"enabled": True, "target_content_id": "future", "text": ""}
    before = digest(env.snapshot())
    with pytest.raises(ValueError, match="invisible"):
        env.apply([actions[0], bad])
    assert digest(env.snapshot()) == before


def test_no_content_no_decision(env, bundles):
    dec = V4Decision(**bundles[3].decision_args)
    a = dec.decide_batch([env.observe("A0582", 1)], {})[0]
    assert a.kind == "idle"
    assert "draws" not in a.payload


def test_prompt_no_private_state_or_future(env, bundles):
    from llm_client import prepare_prompt
    dec = V4Decision(**bundles[3].decision_args)
    prompt, feed, mem, units = prepare_prompt(dec.template, env.observe("A0002", 1))
    assert units <= 4096
    assert "G001" not in prompt and "scripted_no_evidence" not in prompt
    assert "decision_mode" not in prompt and "cohort" not in prompt
    assert "P001" in prompt and mem == []


def test_replay_restores_memories_and_matches_run(bundles, tmp_path):
    _, eb, pb, sc = bundles
    sc.n_steps = 5
    one = build_simulator(env_bundle=eb, pop_bundle=pb, sim_config=sc, store_path=tmp_path / "one.duckdb")
    one.run()
    sc.warm_start = WarmStartSpec(source_version="test", source_trajectory=str(tmp_path / "one.duckdb"), resume_from=3)
    two = build_simulator(env_bundle=eb, pop_bundle=pb, sim_config=sc, store_path=tmp_path / "two.duckdb")
    two.run()
    assert digest(one.env.snapshot()) == digest(two.env.snapshot())


def test_api_failure_does_not_apply_batch(env, bundles):
    class Broken:
        def decide(self, *args):
            raise RuntimeError("test transport error")
    dec = V4Decision(**bundles[3].decision_args)
    dec.mode = "openai"
    dec.client = Broken()
    env.advance_to(1)
    snapshot = digest(env.snapshot())
    with pytest.raises(RuntimeError):
        dec.decide_batch(env.observe_batch(["A0001", "A0002"], 1), {})
    assert digest(env.snapshot()) == snapshot


def test_570_no_retry_and_keeps_reservation(tmp_path):
    from llm_client import LiveClient
    class Failure(Exception):
        status_code = 570
        code = "bad_response_status_code"
    class Chat:
        count = 0
        def create(self, **kwargs):
            self.count += 1
            raise Failure("must not be logged, secret=abc")
    client = LiveClient.__new__(LiveClient)
    client.cfg = defaults()
    client.audit = tmp_path
    client.cache = tmp_path / "cache"
    client.cache.mkdir()
    client.budget_path = tmp_path / "budget.json"
    client.budget = {k: 0 for k in ("requests", "input_reserved_units", "output_reserved_tokens",
        "actual_input_tokens", "actual_output_tokens", "usage_unknown_requests")}
    chat = Chat()
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=chat))
    _, eb, _, _ = make_bundles(SOURCE / "01_Agent基础信息表.csv", SOURCE / "02_Prompt固定提示词.md", defaults(), tmp_path)
    e = V4Environment(eb)
    e.reset(1)
    with pytest.raises(RuntimeError):
        client.decide(e.observe("A0002", 1), "{当前观察}")
    assert chat.count == 1
    assert client.budget["usage_unknown_requests"] == 1
    assert client.budget["input_reserved_units"] > 0
    assert "secret=abc" not in (tmp_path / "request-000001.json").read_text(encoding="utf-8")
