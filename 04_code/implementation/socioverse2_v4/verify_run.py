"""Post-run invariant checks over actual persisted panel, not just model objects."""
import json
from pathlib import Path
import duckdb
from model import dump
from run import RESULTS


def verify(run_dir):
    run_dir = Path(run_dir)
    status = json.loads((run_dir / "status.json").read_text(encoding="utf-8"))
    assert status["status"] == "completed_offline"
    con = duckdb.connect(str(run_dir / "trajectory/study.duckdb"), read_only=True)
    rows = con.execute("SELECT agent_id,step,state,action_payload,action_source FROM panel ORDER BY step,agent_id").fetchall()
    con.close()
    n = status["last_completed_tick"]
    assert len(rows) == 582 * (n + 1)
    assert len({(r[0], r[1]) for r in rows}) == len(rows)
    reposts, direct, partial, draws = set(), set(), 0, 0
    for aid, tick, state_json, payload_json, source in rows:
        state, payload = json.loads(state_json), json.loads(payload_json)
        assert state["memory_count"] <= 5
        if tick == 0:
            assert state["current_belief"] == "unjudged"
            continue
        assert source != "llm" and payload["dry_run"] is True
        feed = payload.get("observed_posts", [])
        assert len(feed) <= 5
        for p in feed:
            assert len(p["comments"]) <= 2
            assert p["available_tick"] <= tick
            assert all(c["published_tick"] < tick for c in p["comments"])
            if p["delivery"] == "direct_government":
                assert tick == 20 and p is feed[0]
                direct.add(aid)
        if "answer" in payload:
            a = payload["answer"]
            assert state["current_belief"] == a["belief"]
            if a["repost"]["enabled"]:
                target = next(p for p in feed if p["content_id"] == a["repost"]["target_content_id"])
                key = (aid, target["root_content_id"])
                assert key not in reposts
                reposts.add(key)
            partial += a["decision_status"] == "partially_applied"
            if state["decision_mode"] == "rule":
                assert not a["comment"]["enabled"]
            for d in payload["draws"]:
                assert d["passed"] == (d["uniform"] < d["probability"])
                draws += 1
    assert len(direct) == (40 if n >= 20 else 0)
    result = dict(passed=True, panel_rows=len(rows), unique_agents=582, completed_ticks=n,
        direct_government_recipients=len(direct), successful_unique_root_reposts=len(reposts),
        partial_actions=partial, audited_probability_draws=draws, api_requests=0,
        conclusion="工程不变量通过；固定回答不能作为研究结果")
    dump(run_dir / "verification.json", result)
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    latest = json.loads((RESULTS / "latest.json").read_text(encoding="utf-8"))
    verify(latest["run_dir"])
