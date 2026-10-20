import copy
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rumor_sim.cli import init_files
from rumor_sim.config import research_config, smoke_config, validate_config, validate_event, estimate
from rumor_sim.runner import execute, load_event_file, attach_donor_profiles
from rumor_sim.storage import read_json, digest, atomic_json, read_round
from rumor_sim import core
from rumor_sim.provider import MockDecisionProvider, BudgetExceeded


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        init_files(self.root)
        self.event, _ = load_event_file(self.root / "data/synthetic_event.json")

    def tearDown(self): self.tmp.cleanup()

    def test_new_grid_and_horizon(self):
        c = research_config(); e = estimate(c)
        self.assertEqual(e["logical_trajectories"], 414)
        self.assertEqual(e["policy_trajectories"], 405)
        self.assertEqual(e["parent_trajectories"], 9)
        c["time"]["last_round"] = 79
        with self.assertRaises(ValueError): validate_config(c)

    def test_scripted_no_evidence_is_explicit(self):
        validate_event(self.event, allow_synthetic=True)
        del self.event["correction_origin"]
        with self.assertRaises(ValueError): validate_event(self.event, allow_synthetic=True)

    def test_complete_tg50_and_resume_export(self):
        c = smoke_config(); out = self.root / "study"
        result = execute(self.event, [], c, out, tg=50, allow_synthetic=True)
        self.assertEqual(len(result), 2)
        branch = next(p for p in (out / "runs").iterdir() if "_t50_" in p.name)
        with (branch / "exports/states.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 80 * 10)
        self.assertEqual({int(r["round"]) for r in rows}, set(range(1,81)))
        original = (branch / "exports/states.csv").read_bytes()
        provider = MockDecisionProvider()
        execute(self.event, [], c, out, tg=50, allow_synthetic=True, provider=provider)
        self.assertEqual(provider.decisions, 0)
        self.assertEqual(original, (branch / "exports/states.csv").read_bytes())
        self.assertEqual(read_json(branch / "status.json")["status"], "completed")

    def test_donor_sampling_does_not_overwrite_experiment(self):
        c = smoke_config(); state = core.initialize(c, self.event, .2, 1)
        profiles = [{"donor_id":"d0", "observed_profile":{"followers_count":321, "following_count":7, "statuses_count":500}}]
        applied = attach_donor_profiles(state, profiles, 1)
        self.assertEqual(applied["profile_sampling"]["unique_donors_used"], 1)
        self.assertEqual(len(applied["profile_assignments"]), 10)
        for aid, a in state["agents"].items():
            for key in ("activity", "prior_government_trust", "prior_acceptance", "belief_score", "memory", "follows"):
                self.assertEqual(a[key], applied["agents"][aid][key])
            self.assertEqual(applied["agents"][aid]["observed_profile"]["followers_count"],321)

    def test_partial_round_failure_then_resume_matches_fresh(self):
        c = smoke_config(); out = self.root / "interrupted"
        class Stops(MockDecisionProvider):
            def decide(self, view, call_identity):
                if self.decisions >= 3: raise BudgetExceeded("Test cap")
                return super().decide(view, call_identity)
        with self.assertRaises(BudgetExceeded):
            execute(self.event, [], c, out, mode="parent", allow_synthetic=True, provider=Stops())
        status = read_json(next((out / "runs").iterdir()) / "status.json")
        self.assertEqual(status["status"], "budget_exhausted")
        resumed = execute(self.event, [], c, out, mode="parent", allow_synthetic=True)
        fresh = execute(self.event, [], c, self.root / "fresh", mode="parent", allow_synthetic=True)
        self.assertEqual(resumed, fresh)

    def test_changed_config_cannot_overwrite_existing_run(self):
        c = smoke_config(); out = self.root / "safe"
        execute(self.event, [], c, out, mode="parent", allow_synthetic=True)
        c["feed"]["recommendation_probability"] = .2
        with self.assertRaises(ValueError):
            execute(self.event, [], c, out, mode="parent", allow_synthetic=True)

    def test_corrupt_checkpoint_is_detected(self):
        c = smoke_config(); out = self.root / "corrupt"
        execute(self.event, [], c, out, mode="parent", allow_synthetic=True)
        folder = next((out / "runs").iterdir())
        path = folder / "rounds/00080.json.gz"
        envelope = read_json(path)
        envelope["state"]["pbd"] = 0.123456
        atomic_json(path, envelope, compressed=True)
        with self.assertRaisesRegex(ValueError, "hash mismatch"): read_round(path)

    def test_decision_cache_identity_is_scoped_to_run(self):
        class Recording(MockDecisionProvider):
            def __init__(self): super().__init__(); self.ids = []
            def decide(self, view, identity):
                self.ids.append(identity); return super().decide(view, identity)
        provider = Recording(); c = smoke_config()
        execute(self.event, [], c, self.root / "identities", tg=50,
                allow_synthetic=True, provider=provider)
        self.assertTrue(any("_parent|" in x for x in provider.ids))
        self.assertTrue(any("_t50_inside_gt0.6|" in x for x in provider.ids))
        self.assertEqual(len(provider.ids), len(set(provider.ids)))

    def test_parent_needs_no_correction_and_empty_tbu_schema_is_stable(self):
        event = copy.deepcopy(self.event)
        event.pop("correction_text"); event.pop("evidence_text")
        out = self.root / "parent_only"
        execute(event, [], smoke_config(), out, mode="parent", allow_synthetic=True)
        folder = next((out / "runs").iterdir())
        with (folder / "exports/tbu_individual.csv").open(encoding="utf-8-sig") as f:
            self.assertEqual(next(csv.reader(f)), ["agent_id", "group", "government_round", "first_reject", "event", "duration", "followup_complete"])

    def test_multi_event_summary_preserves_previous_events(self):
        out = self.root / "batch"
        execute(self.event, [], smoke_config(), out, mode="parent", allow_synthetic=True)
        second = copy.deepcopy(self.event); second["event_id"] = "synthetic_second"
        second["claim_id"] = "synthetic_second_claim"
        execute(second, [], smoke_config(), out, mode="parent", allow_synthetic=True)
        self.assertEqual(len(read_json(out / "study_summary.json")), 2)


if __name__ == "__main__": unittest.main()
