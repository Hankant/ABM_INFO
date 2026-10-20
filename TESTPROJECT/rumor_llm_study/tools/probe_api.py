"""One deliberately synthetic protocol probe; reads key from environment only."""
from pathlib import Path
import json
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rumor_sim.config import research_config
from rumor_sim.provider import HTTPDecisionProvider

c = research_config()["llm"]
c["max_retries"] = 0
view = {
    "agent_id": "TEST_ONLY", "round": 1,
    "profile": {"prior_government_trust": .5, "sharing_style": "sometimes",
                "correction_share_willingness": "reading_only"},
    "original_claim": "虚构研究测试中的星湾图书馆将在下周永久关闭。",
    "previous_belief_score": None, "previous_belief_state": "unaware",
    "prior_acceptance": .579, "memory": [],
    "visible_posts": [{"post_id": "probe_rumor", "author_id": "SOURCE",
         "text": "虚构研究测试：听说星湾图书馆下周将永久关闭，尚无其他依据。",
         "content_id": "probe_content", "source_cue": None}],
    "eligible_repost_post_ids": ["probe_rumor"],
}
try:
    with HTTPDecisionProvider(c, ROOT / "outputs/api_verification/provider") as provider:
        before = provider.http_requests
        result = provider.decide(view, "synthetic_api_probe_" + uuid.uuid4().hex)
        audit = result["audit"]
        report = {"success": True, "base_url": c["base_url"], "requested_model": c["model"],
            "actual_model": audit.get("provider_model"), "decision": result["decision"],
            "usage": audit.get("usage"), "requests_used": provider.http_requests,
            "requests_this_probe": provider.http_requests - before,
            "allowed_total": c["max_api_requests"], "cache_hit": audit.get("cache_hit"),
            "scope": "synthetic single-decision protocol probe; not a full study trajectory"}
        (ROOT / "verification").mkdir(exist_ok=True)
        (ROOT / "verification/api_probe_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True))
except Exception as exc:
    report = {"success": False, "base_url": c["base_url"], "requested_model": c["model"],
        "error_type": type(exc).__name__, "error": str(exc), "allowed_total": c["max_api_requests"]}
    if "provider" in globals():
        report.update(requests_used=provider.http_requests, requests_this_probe=provider.http_requests-before)
    (ROOT / "verification").mkdir(exist_ok=True)
    (ROOT / "verification/api_probe_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    raise SystemExit(1)
