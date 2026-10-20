import copy
import csv
from collections import Counter
from statistics import mean

from model import V4Decision, exposure_summary, digest
from llm_client import render_prompt, repetition_context
from run import SOURCE
from build_personas import generate, SOURCE as ORIGINAL
from test_model import bundles, env


def test_persona_reproducible_and_preserves_original():
    with ORIGINAL.open(encoding="utf-8-sig", newline="") as f:
        original = list(csv.DictReader(f))
    rows, _ = generate(original)
    assert rows == generate(original)[0]
    for old, new in zip(original, rows):
        for key, value in old.items():
            if key != "persona_version":
                assert new[key] == value
    people = [r for r in rows if r["decision_mode"] == "llm"]
    for field in ("sharing_propensity", "verification_preference", "source_prior",
                  "government_prior", "repetition_sensitivity"):
        values = sorted(float(r[field]) for r in people)
        assert .05 < min(values) < max(values) < .95
        assert abs(mean(values)-.5) < 1e-6
        assert len(values) == len(set(values)) == 305
        assert sum(.32 < x < .68 for x in values) > 190  # bell-shaped, not uniform
    assert sorted(Counter(r["synthetic_pre_event_experience"] for r in people).values()) == [101, 102, 102]
    assert all("synthetic_persona_basis" not in r for r in rows if r["decision_mode"] == "rule")


def test_reread_cooldown_caps_and_idempotent_counts(env, bundles):
    dec = V4Decision(**bundles[3].decision_args)
    aid = "A0002"
    for tick in (1, 4, 7, 10):
        env.advance_to(tick)
        ob = env.observe(aid, tick)
        assert [p["content_id"] for p in ob.local_information["posts"]] == ["P001"]
        actions = dec.decide_batch([ob], {})
        env.apply(actions)
        state = digest(env.snapshot())
        env.apply(actions)
        assert digest(env.snapshot()) == state
        env.advance_to(tick+1)
        assert not env.observe(aid, tick+1).local_information["posts"]
    env.advance_to(13)
    assert not env.observe(aid, 13).local_information["posts"]
    s = exposure_summary(env.exposure_history[aid], [], 13)["P001"]
    assert s["observed_post_count"] == 1
    assert s["presentation_count"] == s["exposure_tick_count"] == 4
    assert env.reposted[aid] == {"P001"}


def test_comment_change_wakes_old_reader_only_once(env, bundles):
    dec = V4Decision(**bundles[3].decision_args)
    env.advance_to(1)
    env.apply(dec.decide_batch([env.observe("A0002", 1)], {}))
    env.comments["test-comment"] = dict(comment_id="test-comment", author_id="A0003",
        published_tick=1, target_content_id="P001", text="能提供出处吗？")
    env.advance_to(2)
    ob = env.observe("A0002", 2)
    assert "test-comment" in {c["comment_id"] for c in ob.local_information["posts"][0]["comments"]}
    env.apply(dec.decide_batch([ob], {}))
    env.advance_to(3)
    assert not env.observe("A0002", 3).local_information["posts"]


def test_prompt_boundaries_and_saturation(env):
    env.advance_to(1)
    ob = env.observe("A0002", 1)
    feed = ob.local_information["posts"]
    prompt = render_prompt("{稳定个人资料}\n{当前观察}", ob, feed, [])
    assert "合成角色设定" in prompt and "sharing_propensity" in prompt
    assert "G001" not in prompt
    assert "不是已校准" in prompt
    assert "repeated_rounds" not in render_prompt("{当前观察}", ob, [], [])
    row = ob.local_physical["persona"]
    values = [repetition_context(row, {"P001":{"exposure_tick_count":n}})["P001"]
              for n in (1, 2, 4, 10, 100)]
    assert values[0]["familiarity_increment"] == 0
    assert all(a["familiarity_increment"] <= b["familiarity_increment"] for a,b in zip(values,values[1:]))
    assert values[-1]["familiarity_increment"] <= .35
    assert values[-1]["sharing_increment"] <= .25
    assert values[-1]["sharing_disposition"] <= .95


def test_trimmed_and_duplicate_feed_not_counted_twice(env):
    env.advance_to(1)
    feed = env.observe("A0002", 1).local_information["posts"]
    assert exposure_summary({}, feed, 1) == exposure_summary({}, feed+feed, 1)
    assert exposure_summary({}, [], 1) == {}
