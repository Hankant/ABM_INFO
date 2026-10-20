"""Validate a completed V6 run without making requests or changing results."""
import argparse
import json
from pathlib import Path
from model import digest


def verify(path):
    path = Path(path)
    state = json.loads((path / "status.json").read_text(encoding="utf-8"))
    assert state["last_completed_tick"] == 40
    assert state["status"] in ("completed_offline", "completed_live")
    for tick in range(1, 41):
        data = json.loads((path / "checkpoints" / f"tick-{tick:03d}.json").read_text(encoding="utf-8"))
        actions = data["actions"]
        assert digest(actions) == data["sha256"]
        assert len(actions) == 582
        assert {a["agent_id"] for a in actions} == {f"A{i:04d}" for i in range(1, 583)}
        assert all(a["step"] == tick for a in actions)
    rows = json.loads((path / "trajectory/metrics_history.json").read_text(encoding="utf-8"))["rows"]
    assert [r["step"] for r in rows] == list(range(41))
    for r in rows:
        assert sum(r[f"all_{s}"] for s in ("unjudged", "uncertain", "believe", "reject")) == 582
    result = dict(status=state["status"], ticks=40, agents=582,
                  reread_presentations=sum(r.get("reread_presentations", 0) for r in rows),
                  comment_presentations=sum(r.get("visible_comment_presentations", 0) for r in rows))
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    verify(parser.parse_args().run_dir)
