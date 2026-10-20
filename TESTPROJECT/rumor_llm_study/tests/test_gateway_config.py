"""Endpoint migration regression checks; no network or real credentials."""
from pathlib import Path
import json
import tempfile
import unittest
from rumor_sim.config import research_config, smoke_config
from rumor_sim.provider import DEFAULT_BASE_URL, DEFAULT_MODEL, HTTPDecisionProvider


class GatewayConfigTests(unittest.TestCase):
    def test_runtime_and_packaged_config_match_new_gateway(self):
        root = Path(__file__).resolve().parents[1]
        configs = [research_config(), smoke_config()]
        configs += [json.loads((root / "config" / name).read_text(encoding="utf-8"))
                    for name in ("research.json", "smoke.json")]
        self.assertEqual(DEFAULT_BASE_URL, "https://api.zetatechs.com/v1")
        self.assertEqual(DEFAULT_MODEL, "deepseek-v4-flash")
        for c in configs:
            self.assertEqual(c["llm"]["base_url"], DEFAULT_BASE_URL)
            self.assertEqual(c["llm"]["model"], DEFAULT_MODEL)

    def test_http_uses_new_gateway_completion_path(self):
        calls = []
        def transport(url, payload, headers, timeout):
            calls.append((url, payload["model"]))
            return {"model": DEFAULT_MODEL, "choices": [{"message": {"content": json.dumps({
                "belief_score": 50, "action": "silent", "target_post_id": None,
                "public_stance": "none", "comment": "", "reason": "暂不判断"})}}]}
        with tempfile.TemporaryDirectory() as td:
            with HTTPDecisionProvider(research_config()["llm"], td, transport=transport) as p:
                p.decide({"visible_posts": [{"post_id": "p1"}], "eligible_repost_post_ids": []}, "offline_endpoint_check")
        self.assertEqual(calls, [("https://api.zetatechs.com/v1/chat/completions", "deepseek-v4-flash")])
