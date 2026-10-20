from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rumor_sim.import_data import (SOURCE_COLUMNS, USER_COLUMNS, extract_table,
    import_directory, normalize_user_id, parse_public_count, sample_donor_profiles)


class ImportDataTests(unittest.TestCase):
    def test_id_query_parameters_and_homepage(self):
        self.assertEqual(normalize_user_id("id=1234567890&flag=1&refer_flag="), "1234567890")
        self.assertEqual(normalize_user_id("id=1234567890"), "1234567890")
        self.assertEqual(normalize_user_id(None, "https://weibo.com/u/1234567890"), "1234567890")
        self.assertIsNone(normalize_user_id(None))

    def test_public_count_parser(self):
        for raw, expected in [("粉丝1.2万", 12000), ("关注 1,234", 1234), ("微博：0", 0), (3.0, 3), ("--", None), (-1, None)]:
            self.assertEqual(parse_public_count(raw), expected)

    def test_headerless_reposts_preserve_first_row(self):
        row = ["url", "PRIVATE_NAME", "id=2000000001", "url", "private comment", "2020-01-01", "转发", "女", "12", "40", 100, "PRIVATE_LOCATION"]
        table = extract_table([row, row], "reposts")
        self.assertTrue(table["header_missing"])
        self.assertEqual(len(table["rows"]), 2)
        self.assertEqual(table["rows"][0]["excel_row"], 1)
        self.assertEqual(table["rows"][0]["values"]["id"], "id=2000000001")

    def test_import_dedup_whitelist_and_private_archive(self):
        source_row = ["url", "SOURCE_PRIVATE", "id=1000000001&flag=1", "url", "2020", "一项待核实的事件主张", "device", "8", "9", "10", "男", "100", "200", "300", "PRIVATE_LOCATION"]
        user_row = ["url", "PRIVATE_NAME", "id=2000000001", "url", "FUTURE_COMMENT_SECRET", "2020-01-02", "评论", "女", "12", "40", 100, "PRIVATE_LOCATION"]
        second_row = list(user_row); second_row[6] = "转发"; second_row[9] = "41"
        footer = [None] * 12; footer[10] = 456.5
        sheets = [("Sheet1", [SOURCE_COLUMNS, source_row]), ("Sheet2", [USER_COLUMNS + ["立场"], user_row + ["支持"], footer]), ("Sheet3", [second_row])]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root / "source"; source.mkdir()
            (source / "event.xls").write_bytes(b"fixture handled by patched reader")
            with patch("rumor_sim.import_data._read_sheets", return_value=sheets):
                report = import_directory(source, root / "output")
            self.assertEqual(report["totals"]["unique_profile_donors"], 1)
            self.assertEqual(report["totals"]["comments_excluded_no_user_id"], 1)
            self.assertEqual(report["totals"]["headerless_repost_sheet"], 1)
            folder = root / "output/event_001"
            public = (folder / "profiles.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("PRIVATE_NAME", public)
            self.assertNotIn("FUTURE_COMMENT_SECRET", public)
            self.assertNotIn("2000000001", public)
            self.assertNotIn("prior_government_trust", public)
            profile = json.loads(public)
            self.assertEqual(profile["observed_profile"], {"followers_count": 40, "following_count": 12, "statuses_count": 100})
            event = json.loads((folder / "event.json").read_text(encoding="utf-8"))
            self.assertEqual(event["correction_mode"], "scripted_no_evidence")
            self.assertEqual(event["evidence_text"], "")
            self.assertNotIn("FUTURE_COMMENT_SECRET", json.dumps(event))
            private = json.loads((folder / "_private/provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(len(next(iter(private["donor_provenance"].values()))["field_conflicts"]), 1)
            self.assertIn("FUTURE_COMMENT_SECRET", json.dumps(private))

    def test_missing_source_text_not_filled_from_filename(self):
        source_row = ["url", "source", "id=1000000001", "url", "2020", None]
        user = ["url", "name", "id=2000000001"]
        sheets = [("S1", [SOURCE_COLUMNS, source_row]), ("S2", [USER_COLUMNS, user]), ("S3", [USER_COLUMNS])]
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); (base/"source").mkdir(); (base/"source/FILENAME_CLAIM.xls").write_bytes(b"fixture")
            with patch("rumor_sim.import_data._read_sheets", return_value=sheets):
                report = import_directory(base/"source", base/"out")
            event = json.loads((base/"out/event_001/event.json").read_text(encoding="utf-8"))
            self.assertEqual(event["rumor_text"], "")
            self.assertEqual(event["correction_text"], "")
            self.assertEqual(report["events"][0]["status"], "missing_rumor_text")

    def test_profile_sampling_independence_and_no_leaky_fields(self):
        pool = [{"donor_id": "a", "observed_profile": {"followers_count": 10, "comment": "secret"}}, {"donor_id": "b", "observed_profile": {"followers_count": 20}}]
        assigned = sample_donor_profiles(pool, [f"a{i}" for i in range(6)], 1)
        self.assertEqual(assigned, sample_donor_profiles(pool, [f"a{i}" for i in range(6)], 1))
        self.assertEqual(len(assigned), 6)
        self.assertEqual({x["donor_id"] for x in assigned}, {"a", "b"})
        self.assertNotIn("secret", json.dumps(assigned))
        assigned[0]["observed_profile"]["followers_count"] = 999
        self.assertTrue(all(x["observed_profile"]["followers_count"] != 999 for x in assigned[1:]))
        self.assertTrue(all(x["observed_profile"]["followers_count"] != 999 for x in pool))


if __name__ == "__main__":
    unittest.main()
