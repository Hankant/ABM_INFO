import copy
from statistics import mean
import pytest
from government import select_targets, trust_values
from run import defaults, make_bundles, SOURCE
from model import load_rows, V4Environment, V4Decision, V4Metrics
from llm_client import render_prompt


@pytest.mark.parametrize("ratio,inside", [(0, 0), (.5, 20), (1, 40)])
def test_target_ratio(ratio, inside):
    rows = load_rows(SOURCE / "01_Agent基础信息表.csv")
    cfg = {**defaults(), "targeting_inside_ratio": ratio}
    ids = select_targets(rows, cfg)
    assert ids == select_targets(rows, cfg)
    assert len(set(ids)) == 40
    assert sum(r["group"] == "inside" for r in rows if r["agent_id"] in ids) == inside
    with pytest.raises(ValueError):
        select_targets(rows, {**cfg, "targeting_inside_ratio": 1, "government_reach": 100})


@pytest.mark.parametrize("mu", [.25, .5, .75])
def test_trust_mean_and_rank(mu):
    rows = load_rows(SOURCE / "01_Agent基础信息表.csv")
    values = trust_values(rows, {**defaults(), "government_trust_mean": mu})
    reference = trust_values(rows, {**defaults(), "government_trust_mean": .5})
    for mode in ("llm", "rule"):
        ids = [r["agent_id"] for r in rows if r["decision_mode"] == mode]
        assert mean(values[a] for a in ids) == pytest.approx(mu)
        assert all(0 <= values[a] <= 1 for a in ids)
        assert sorted(ids, key=values.get) == sorted(ids, key=reference.get)


def test_schedule_tbu_and_individual_gt(tmp_path):
    cfg = {**defaults(), "government_tick": 5, "government_trust_mean": .75}
    b = make_bundles(SOURCE/"01_Agent基础信息表.csv", SOURCE/"02_Prompt固定提示词.md", cfg, tmp_path)
    assert b[1].scheduled_events[0].at_step == 5
    assert b[1].information_program.broadcasts[0].at_step == 5
    env = V4Environment(b[1]); env.reset(1)
    aid = next(a for a in env.direct_targets if env.by_id[a]["decision_mode"] == "rule")
    env.beliefs[aid] = "believe"
    env.advance_to(4); env.apply([])
    assert aid in env.cohort and "G001" not in env.posts
    env.advance_to(5)
    ob = env.observe(aid, 5)
    assert ob.local_information["posts"][0]["content_id"] == "G001"
    dec = V4Decision(**b[3].decision_args)
    _, draws = dec._rule(ob)
    assert draws[0]["probability"] == ob.local_physical["government_trust"]
    env.transitions[aid] = 7
    assert V4Metrics().collect(env, [], 7)["tbu_engineering"] == 2
    llm = next(a for a in env.by_id if env.by_id[a]["decision_mode"] == "llm")
    ob = env.observe(llm, 5)
    prompt = render_prompt("{稳定个人资料}", ob, [], [])
    assert "覆盖资料表" in prompt
