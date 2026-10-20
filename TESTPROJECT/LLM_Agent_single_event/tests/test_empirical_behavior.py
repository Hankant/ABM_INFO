from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from rumor_sim.empirical import prepare_single_event, validate_behavior


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


class EmpiricalBehaviorTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        source = root / "imported"
        event = {"event_id": "event_052", "original_claim": "原始待核实主张",
                 "rumor_text": "原始待核实主张", "correction_text": "实验纠正",
                 "profiles_file": "profiles.jsonl", "metadata": {}}
        write_json(source / "event.json", event)
        profiles = [{"donor_id": f"donor_{i}", "observed_profile": {"followers_count": 10}}
                    for i in range(1, 6)]
        (source / "profiles.jsonl").write_text("\n".join(json.dumps(x) for x in profiles), encoding="utf-8")
        def row(n, text, role):
            return {"excel_row": n, "values": {"评论内容": text,
                    "评论用户": "PRIVATE_NAME", "id": "id=12345678901",
                    "评论时间": "2021-02-03 10:08", "评论类型": role}}
        provenance = {
            "all_sheet_data": {
                "comments": {"rows": [row(2, "确定吗？", "评论"), row(3, "我暂不相信", "评论"),
                    row(4, "@private_handle PRIVATE_NAME https://example.invalid/path 辟谣了吗？", "评论"),
                    row(5, "", "评论")]},
                "reposts": {"rows": [row(2, "转发微博", "转发"), row(3, "？", "转发")]},
            },
            "donor_provenance": {
                "donor_1": {"record_locations": [
                    {"sheet_role": "comments", "excel_row": 2},
                    {"sheet_role": "comments", "excel_row": 3},
                    {"sheet_role": "reposts", "excel_row": 2},
                    {"sheet_role": "comments", "excel_row": 2}]},
                "donor_2": {"record_locations": [{"sheet_role": "reposts", "excel_row": 3}]},
                "donor_3": {"record_locations": [{"sheet_role": "comments", "excel_row": 4},
                                                  {"sheet_role": "comments", "excel_row": 999}]},
                "donor_5": {"record_locations": [{"sheet_role": "comments", "excel_row": 5}]},
            },
        }
        write_json(source / "_private/provenance.json", provenance)
        return source

    def read_profiles(self, output):
        return {p["donor_id"]: p for p in (json.loads(x) for x in
                (output / "profiles.jsonl").read_text(encoding="utf-8").splitlines())}

    def test_conditional_behavior_and_missingness(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.fixture(root); output = root / "prepared"
            report = prepare_single_event(source, output)
            rows = self.read_profiles(output)
            first = rows["donor_1"]["empirical_behavior"]
            self.assertEqual(first["comment_records"], 2)
            self.assertEqual(first["repost_records"], 1)
            self.assertEqual(first["resolved_observed_posts"], 3)  # duplicated location counted once
            self.assertAlmostEqual(first["repost_fraction_among_observed_posts"], 1 / 3)
            self.assertEqual(first["median_comment_characters"], 4.5)
            self.assertAlmostEqual(first["question_fraction"], 1 / 3)
            second = rows["donor_2"]["empirical_behavior"]
            self.assertEqual(second["comment_records"], 0)
            self.assertIsNone(second["median_comment_characters"])
            self.assertEqual(second["repost_fraction_among_observed_posts"], 1)
            self.assertEqual(second["question_fraction"], 1)
            self.assertEqual(rows["donor_3"]["empirical_behavior"]["status"], "partial")
            self.assertEqual(rows["donor_3"]["empirical_behavior"]["unresolved_record_locations"], 1)
            unknown = rows["donor_4"]["empirical_behavior"]
            for key in ("comment_records", "repost_records", "repost_fraction_among_observed_posts",
                        "median_comment_characters", "question_fraction"):
                self.assertIsNone(unknown[key])
            self.assertEqual(unknown["status"], "unknown")
            empty = rows["donor_5"]["empirical_behavior"]
            self.assertEqual(empty["comment_records"], 1)
            self.assertIsNone(empty["median_comment_characters"])
            self.assertIsNone(empty["question_fraction"])
            self.assertEqual(report["resolved_unique_observed_records"], {"comments": 4, "reposts": 2})

    def test_raw_text_only_in_redacted_local_artifact_and_source_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.fixture(root); output = root / "prepared"
            hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob("*") if p.is_file()}
            prepare_single_event(source, output)
            for path, digest in hashes.items():
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            public = (output / "profiles.jsonl").read_text(encoding="utf-8")
            for forbidden in ("确定吗", "我暂不相信", "辟谣", "PRIVATE_NAME", "private_handle", "12345678901"):
                self.assertNotIn(forbidden, public)
            examples = json.loads((output / "local_comment_examples.json").read_text(encoding="utf-8"))
            self.assertTrue(examples["never_send_to_model"])
            blob = json.dumps(examples)
            for forbidden in ("PRIVATE_NAME", "private_handle", "https://example", "12345678901"):
                self.assertNotIn(forbidden, blob)
            flagged = [x for x in examples["examples"] if x["correction_related_keyword_flag"]]
            self.assertEqual(len(flagged), 1)
            self.assertEqual(flagged[0]["truth_status"], "not_assessed_keyword_flag_is_not_verification")
            event = json.loads((output / "event.json").read_text(encoding="utf-8"))
            self.assertEqual(event["original_claim"], "原始待核实主张")
            self.assertFalse(event["metadata"]["historical_text_replay"])
            self.assertEqual(event["profiles_file"], "profiles.jsonl")

    def test_output_cannot_modify_source_and_escaping_profile_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.fixture(root)
            for target in (source, source / "derived", root):
                with self.assertRaises(ValueError):
                    prepare_single_event(source, target)
            event = json.loads((source / "event.json").read_text(encoding="utf-8"))
            event["profiles_file"] = "../outside.jsonl"
            write_json(source / "event.json", event)
            with self.assertRaises(ValueError):
                prepare_single_event(source, root / "prepared")

    def test_duplicate_donor_and_ambiguous_rows_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.fixture(root)
            path = source / "profiles.jsonl"
            path.write_text(path.read_text(encoding="utf-8") + "\n" + json.dumps({"donor_id": "donor_1"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare_single_event(source, root / "prepared")
            self.assertFalse((root / "prepared").exists())
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.fixture(root)
            path = source / "_private/provenance.json"
            raw = json.loads(path.read_text(encoding="utf-8"))
            raw["all_sheet_data"]["comments"]["rows"].append(raw["all_sheet_data"]["comments"]["rows"][0])
            write_json(path, raw)
            with self.assertRaises(ValueError):
                prepare_single_event(source, root / "prepared")

    def test_behavior_prompt_whitelist_rejects_text_bad_metadata_and_impossible_values(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.fixture(root); output = root / "prepared"
            prepare_single_event(source, output)
            original = self.read_profiles(output)["donor_1"]["empirical_behavior"]
            valid = validate_behavior(original)
            self.assertEqual(valid, original)
            self.assertIsNot(valid, original)
            for key, value in (("text", "PRIVATE COMMENT"), ("raw_user_id", "PRIVATE ID"),
                               ("measurement_scope", "untrusted custom instructions"),
                               ("retrospective", False), ("question_fraction", 2),
                               ("repost_fraction_among_observed_posts", 0.8),
                               ("median_comment_characters", float("nan")),
                               ("comment_records", True), ("status", "unknown")):
                bad = dict(original); bad[key] = value
                with self.subTest(key=key), self.assertRaises(ValueError):
                    validate_behavior(bad)
            unknown = self.read_profiles(output)["donor_4"]["empirical_behavior"]
            unknown["comment_records"] = 0
            with self.assertRaises(ValueError):
                validate_behavior(unknown)


if __name__ == "__main__":
    unittest.main()
