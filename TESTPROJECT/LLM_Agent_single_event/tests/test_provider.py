"""Provider tests use injected transport only: zero live HTTP and no credentials."""
import copy
from email.message import Message
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib import request
from urllib.error import HTTPError
from urllib.response import addinfourl

from rumor_sim.provider import (BudgetExceeded, DecisionValidationError, HTTPDecisionProvider,
                                MockDecisionProvider, ProviderError, ProviderLocked, validate_decision,
                                _NoRedirectHandler, SYSTEM_PROMPT, PROMPT_VERSION)


VIEW = {"visible_posts": [{"post_id": "p1", "text": "Unverified test post"},
                           {"post_id": "p2", "text": "Another test post"}],
        "eligible_repost_post_ids": ["p1"], "previous_belief_score": None,
        "profile_text": "Synthetic user", "memory": []}
SILENT = {"belief_score": 50, "action": "silent", "target_post_id": None,
          "public_stance": "none", "comment": "", "reason": "我尚不确定。"}


def reply(decision=None, **extra):
    return {"model": "reported-model-revision", "id": "response-test",
            "usage": {"prompt_tokens": 123, "completion_tokens": 45},
            "choices": [{"message": {"content": json.dumps(decision or SILENT, ensure_ascii=False)}}], **extra}


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, payload, headers, timeout):
        self.calls.append({"url": url, "payload": copy.deepcopy(payload), "timeout": timeout})
        result = self.responses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


class DecisionValidationTests(unittest.TestCase):
    def test_system_prompt_does_not_disclose_claim_truth_label(self):
        self.assertNotIn("谣言", SYSTEM_PROMPT)
        self.assertIn("相信原始待核实主张", SYSTEM_PROMPT)
        self.assertEqual(PROMPT_VERSION, "rumor-decision-1.2-social")

    def test_silent_and_all_score_boundaries(self):
        for score in (0, 40, 41, 59, 60, 100):
            self.assertEqual(validate_decision({**SILENT, "belief_score": score}, VIEW)["belief_score"], score)

    def test_rejects_types_extra_duplicate_and_wrapped_json(self):
        for score in (True, False, 0.0, "20", -1, 101, None):
            with self.assertRaises(DecisionValidationError):
                validate_decision({**SILENT, "belief_score": score}, VIEW)
        for value in ({**SILENT, "extra": 1}, "```json\n{}\n```", '{"belief_score":2,"belief_score":3}'):
            with self.assertRaises(DecisionValidationError):
                validate_decision(value, VIEW)

    def test_silent_strict_fields(self):
        for field, value in (("target_post_id", "p1"), ("public_stance", "uncertain"), ("comment", " ")):
            with self.assertRaises(DecisionValidationError):
                validate_decision({**SILENT, field: value}, VIEW)

    def test_comment_visible_target_and_length(self):
        good = {**SILENT, "action": "comment", "target_post_id": "p2", "public_stance": "support", "comment": "字" * 80}
        self.assertEqual(validate_decision(good, VIEW), good)
        for field, value in (("target_post_id", "unseen"), ("public_stance", "none"),
                             ("comment", "字" * 81), ("comment", ""), ("reason", "字" * 41)):
            with self.assertRaises(DecisionValidationError):
                validate_decision({**good, field: value}, VIEW)

    def test_repost_enforces_lineage_eligibility_and_empty_comment(self):
        good = {**SILENT, "action": "repost", "target_post_id": "p1", "public_stance": "oppose"}
        self.assertEqual(validate_decision(good, VIEW), good)
        for field, value in (("target_post_id", "p2"), ("comment", "附言")):
            with self.assertRaises(DecisionValidationError):
                validate_decision({**good, field: value}, VIEW)


class HTTPProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = {"max_api_requests": 10, "max_retries": 2}

    def tearDown(self):
        self.temp.cleanup()

    def test_two_repairs_then_success_are_all_counted(self):
        bad = reply({**SILENT, "belief_score": True})
        fake = FakeTransport([bad, reply({**SILENT, "target_post_id": "p1"}), reply()])
        with HTTPDecisionProvider(self.config, self.root, transport=fake) as client:
            result = client.decide(VIEW, "event/e1/seed/1/d/0.2/t/1/a/C001")
            self.assertEqual(result["decision"], SILENT)
            self.assertEqual(result["audit"]["attempts"], 3)
            self.assertEqual(result["audit"]["provider_model"], "reported-model-revision")
            self.assertEqual(client.http_requests, 3)
            self.assertEqual(len(fake.calls[2]["payload"]["messages"]), 6)
            self.assertEqual(fake.calls[0]["payload"]["thinking"], {"type": "disabled"})
        self.assertEqual(json.loads((self.root / "budget.json").read_text())["http_requests"], 3)

    def test_cache_requires_same_view_parameters_and_call_identity(self):
        fake = FakeTransport([reply(), reply(), reply()])
        with HTTPDecisionProvider(self.config, self.root, transport=fake) as client:
            first = client.decide(VIEW, "same-key")
            cached = client.decide(VIEW, "same-key")
            self.assertFalse(first["audit"]["cache_hit"])
            self.assertTrue(cached["audit"]["cache_hit"])
            client.decide({**VIEW, "memory": ["new input"]}, "same-key")
            client.decide(VIEW, "independent-replicate")
            self.assertEqual(client.http_requests, 3)
        new_transport = FakeTransport([reply()])
        with HTTPDecisionProvider({**self.config, "temperature": 0.4}, self.root, transport=new_transport) as client:
            changed = client.decide(VIEW, "same-key")
            self.assertFalse(changed["audit"]["cache_hit"])
            self.assertEqual(client.http_requests, 4)

    def test_cache_survives_restart_without_api_key_or_http(self):
        with HTTPDecisionProvider(self.config, self.root, transport=FakeTransport([reply()])) as client:
            client.decide(VIEW, "key")
        with patch.dict(os.environ, {}, clear=True):
            with HTTPDecisionProvider(self.config, self.root) as client:
                result = client.decide(VIEW, "key")
                self.assertTrue(result["audit"]["cache_hit"])
                self.assertEqual(client.http_requests, 1)

    def test_persistent_budget_includes_failed_requests_and_survives_restart(self):
        fake = FakeTransport([TimeoutError("offline timeout"), TimeoutError("offline timeout")])
        with HTTPDecisionProvider({**self.config, "max_api_requests": 2}, self.root, transport=fake) as client:
            with self.assertRaises(BudgetExceeded):
                client.decide(VIEW, "key")
            self.assertEqual(len(fake.calls), 2)
        never = FakeTransport([])
        with HTTPDecisionProvider({**self.config, "max_api_requests": 2}, self.root, transport=never) as client:
            with self.assertRaises(BudgetExceeded):
                client.decide(VIEW, "another-key")
            self.assertEqual(len(never.calls), 0)

    def test_bad_outputs_never_become_fallback_decisions(self):
        fake = FakeTransport([reply({**SILENT, "belief_score": -1})] * 3)
        with HTTPDecisionProvider(self.config, self.root, transport=fake) as client:
            with self.assertRaises(ProviderError):
                client.decide(VIEW, "key")
            self.assertEqual(client.decisions, 0)
            self.assertEqual(client.http_requests, 3)
        self.assertEqual(list((self.root / "success_cache").glob("*.json")), [])
        records = [json.loads(line) for line in (self.root / "http_audit.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(records[-1]["event"], "decision_failed")
        self.assertEqual(len([r for r in records if r["event"] == "request_failed"]), 3)

    def test_exclusive_lock_prevents_parallel_provider(self):
        with HTTPDecisionProvider(self.config, self.root, transport=FakeTransport([])):
            with self.assertRaises(ProviderLocked):
                HTTPDecisionProvider(self.config, self.root, transport=FakeTransport([]))
        with HTTPDecisionProvider(self.config, self.root, transport=FakeTransport([])):
            pass

    def test_http_error_audit_redacts_key(self):
        token = "private-test-token-not-a-real-key"
        body = ("Unauthorized Bearer " + token).encode()
        fake = FakeTransport([HTTPError("https://example.invalid", 401, "Denied " + token, {}, io.BytesIO(body))])
        with patch.dict(os.environ, {"RUMOR_LLM_API_KEY": token}):
            with HTTPDecisionProvider({**self.config, "max_retries": 0}, self.root, transport=fake) as client:
                with self.assertRaises(ProviderError) as caught:
                    client.decide(VIEW, "key")
                self.assertNotIn(token, str(caught.exception))
        text = (self.root / "http_audit.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(token, text)
        self.assertIn('"status":401', text)
        self.assertIn("[REDACTED]", text)

    def test_missing_key_does_not_consume_budget(self):
        with patch.dict(os.environ, {}, clear=True):
            with HTTPDecisionProvider(self.config, self.root) as client:
                with self.assertRaises(ProviderError):
                    client.decide(VIEW, "key")
                self.assertEqual(client.http_requests, 0)

    def test_auth_denials_stop_after_one_request_despite_retry_allowance(self):
        for status in (401, 403):
            with self.subTest(status=status):
                folder = self.root / str(status)
                fake = FakeTransport([HTTPError("https://example.invalid", status, "User disabled", {},
                                                io.BytesIO(b'{"error":"User disabled"}'))])
                with HTTPDecisionProvider(self.config, folder, transport=fake) as client:
                    with self.assertRaisesRegex(ProviderError, "Non-retryable HTTP " + str(status)):
                        client.decide(VIEW, "key")
                    self.assertEqual(client.http_requests, 1)
                    self.assertEqual(len(fake.calls), 1)
                records = [json.loads(line) for line in (folder / "http_audit.jsonl").read_text(encoding="utf-8").splitlines()]
                self.assertEqual(records[-1]["attempts"], 1)
                failure = next(row for row in records if row["event"] == "request_failed")
                self.assertFalse(failure["retryable"])
                self.assertEqual(failure["error"]["status"], status)

    def test_redirect_transport_refuses_cross_origin_without_second_request(self):
        calls = []

        class OfflineHTTPSHandler(request.HTTPSHandler):
            def https_open(self, outgoing):
                calls.append(outgoing)
                headers = Message()
                headers["Location"] = "https://other-origin.invalid/collect"
                response = addinfourl(io.BytesIO(b"Redirect fixture"), headers, outgoing.full_url, 302)
                response.msg = "Found"
                return response

        # Replace the network handler, not the redirect policy: no socket is used.
        real_build_opener = request.build_opener
        def offline_opener(*handlers):
            self.assertTrue(any(isinstance(handler, _NoRedirectHandler) for handler in handlers))
            return real_build_opener(OfflineHTTPSHandler(), *handlers)

        with patch("rumor_sim.provider.request.build_opener", side_effect=offline_opener):
            with self.assertRaisesRegex(HTTPError, "redirect refused"):
                HTTPDecisionProvider._urllib_transport("https://original-origin.invalid/v1/chat/completions", {},
                                                       {"Authorization": "Bearer offline-fake-token"}, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].host, "original-origin.invalid")

    def test_redirect_failure_is_counted_once_and_not_retried(self):
        fake = FakeTransport([HTTPError("https://example.invalid", 307, "HTTP redirect refused", {}, io.BytesIO(b""))])
        with HTTPDecisionProvider(self.config, self.root, transport=fake) as client:
            with self.assertRaisesRegex(ProviderError, "Non-retryable HTTP 307"):
                client.decide(VIEW, "key")
            self.assertEqual(client.http_requests, 1)
            self.assertEqual(len(fake.calls), 1)

    def test_extra_body_cannot_override_controlled_fields(self):
        for field in ("model", "messages", "api_key", "Authorization", "temperature"):
            with self.assertRaises(ProviderError):
                HTTPDecisionProvider({**self.config, "extra_body": {field: "bad"}}, self.root, transport=FakeTransport([]))
            self.assertFalse((self.root / ".provider.lock").exists())


class MockProviderTests(unittest.TestCase):
    def test_mock_is_strict_deterministic_and_covers_protocol_states(self):
        with MockDecisionProvider() as client:
            values = [client.decide(VIEW, str(i)) for i in range(100)]
            self.assertEqual({v["decision"]["action"] for v in values}, {"silent", "comment", "repost"})
            self.assertEqual({v["decision"]["belief_score"] for v in values}, {20, 50, 80})
            self.assertEqual(values[0], client.decide(VIEW, "0"))
            self.assertEqual(client.http_requests, 0)
            for result in values:
                validate_decision(result["decision"], VIEW)
                self.assertEqual(result["audit"]["provider_mode"], "mock")


if __name__ == "__main__":
    unittest.main()
