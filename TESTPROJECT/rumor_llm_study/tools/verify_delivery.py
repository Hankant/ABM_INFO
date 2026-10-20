"""Offline end-to-end release verification. Does not call any HTTP provider."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rumor_sim.config import research_config, smoke_config, validate_event
from rumor_sim.runner import load_event_file, code_hash

verification = ROOT / "verification"; verification.mkdir(exist_ok=True)
started = time.time()
report = {"started_at_unix": started, "code_hash": code_hash(), "python": sys.version,
          "provider_mode": "mock", "real_llm_success": False}

def run(command, name):
    result = subprocess.run([sys.executable, *map(str, command)], cwd=ROOT, capture_output=True,
                            encoding="utf-8", errors="replace")
    (verification / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode: raise RuntimeError(f"{name} failed; see verification/{name}.log")

run([ROOT / "test_all.py"], "unit_tests")
print("Offline unit tests passed", flush=True)
valid = []
missing = []
for p in sorted((ROOT / "data/imported").glob("event_*/event.json")):
    event, profiles = load_event_file(p)
    if event["rumor_text"].strip():
        validate_event(event); valid.append(event["event_id"])
    else: missing.append(event["event_id"])
assert len(valid) == 75 and len(missing) == 50
report["import"] = {"total_events":125, "nonempty_source_events":75, "missing_source_events":50}

full_out = ROOT / ("outputs/release_check_582_" + report["code_hash"][:12])
run([ROOT / "run.py", "run", "--event", ROOT / "data/imported/event_052/event.json",
     "--provider", "mock", "--tg", "50", "--output", full_out], "full_582")
print("582-agent run through round 80 passed", flush=True)
child = next(p for p in (full_out / "runs").iterdir() if "_t50_" in p.name)
with (child / "exports/states.csv").open(encoding="utf-8-sig") as f: rows = list(csv.DictReader(f))
assert len(rows) == 582 * 80
assert {int(r["round"]) for r in rows} == set(range(1,81))
exposures = [json.loads(s) for s in (child / "exports/exposures.jsonl").read_text(encoding="utf-8").splitlines()]
direct = [r for r in exposures if r["channel"] == "government_direct"]
assert len(direct) == 40 and len({r["agent_id"] for r in direct}) == 40
assert {r["round"] for r in direct} == {50}
before = hashlib.sha256((child / "exports/states.csv").read_bytes()).hexdigest()
run([ROOT / "run.py", "run", "--event", ROOT / "data/imported/event_052/event.json",
     "--provider", "mock", "--tg", "50", "--output", full_out], "full_582_resume")
assert before == hashlib.sha256((child / "exports/states.csv").read_bytes()).hexdigest()
report["full_population_check"] = {"agents":582, "last_round":80, "parent_and_policy_runs":2,
    "policy_tg":50, "states_rows":len(rows), "unique_direct_recipients":40,
    "exact_export_after_resume":True, "http_requests":0}

c = smoke_config(); c["grid"]["d_seed"] = [.2]; c["grid"]["seeds"] = [1]
cfg = verification / "smoke_grid_config.json"
cfg.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
grid_out = ROOT / ("outputs/release_check_grid_" + report["code_hash"][:12])
run([ROOT / "run.py", "grid", "--config", cfg,
     "--event", ROOT / "data/imported/event_052/event.json", "--provider", "mock",
     "--output", grid_out], "smoke_grid")
summary = json.loads((grid_out / "study_summary.json").read_text(encoding="utf-8"))
assert len(summary) == 46
branches = [r for r in summary if r["policy"] is not None]
assert len(branches) == 45
assert {r["policy"]["government_round"] for r in branches} == {10,20,30,40,50}
assert all(r["end_round"] == 80 for r in summary)
for tg in [10,20,30,40,50]:
    for target in ["inside", "random", "outside"]:
        variants = [r for r in branches if r["policy"]["government_round"]==tg and r["policy"]["targeting"]==target]
        assert len(variants) == 3
        assert len({tuple(r["policy"]["recipients"]) for r in variants}) == 1
assert len({r["PBd"] for r in summary}) == 1
report["grid_check"] = {"agents":10, "policy_branches":45, "parent_trajectories":1,
    "tg":[10,20,30,40,50], "last_round":80, "same_recipients_across_gt":True,
    "shared_baseline_pbd":True, "http_requests":0}

api_dir = ROOT / "outputs/api_verification/provider"
if (api_dir / "budget.json").exists():
    report["real_api_probe_requests"] = json.loads((api_dir / "budget.json").read_text())["http_requests"]
latest_probe = verification / "api_probe_result.json"
if latest_probe.exists():
    api_result = json.loads(latest_probe.read_text(encoding="utf-8"))
    matches_current = (api_result.get("base_url") == research_config()["llm"]["base_url"]
                       and api_result.get("requested_model") == research_config()["llm"]["model"])
    report["real_llm_success"] = bool(matches_current and api_result.get("success"))
    report["real_api_probe_scope"] = "single-decision interface check; full trajectories above are mock"
report["finished_at_unix"] = time.time()
report["elapsed_seconds"] = round(time.time()-started,2)
report["offline_verification_passed"] = True
(verification / "verification_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=True, indent=2))
