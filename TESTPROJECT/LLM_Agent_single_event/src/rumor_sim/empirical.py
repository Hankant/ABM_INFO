"""Prepare one empirically informed event without replaying historical text.

The measured behavior is conditional on observed public expressions in this
event. It is retrospective, not a pre-event trait or a probability per browsing
opportunity. Historical utterances are written only to a local review artifact;
they are never placed in agent memory, belief, trust, or a model payload here.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path
import re
from statistics import median
from typing import Any


_COUNT_FIELDS = ("followers_count", "following_count", "statuses_count")
_IDENTITY_FIELDS = ("发博用户", "评论用户", "id", "微博主页", "用户微博主页", "微博地址")
_CORRECTION_WORDS = ("辟谣", "不实", "假的", "反转", "澄清", "官方", "警方")
_SCOPE = "this_event_observed_public_expressions_not_all_browsing_opportunities"
_BEHAVIOR_KEYS = {
    "schema_version", "status", "measurement_scope", "retrospective",
    "resolved_observed_posts", "unresolved_record_locations", "comment_records",
    "repost_records", "repost_fraction_among_observed_posts", "nonempty_comment_records",
    "nonempty_observed_text_records", "median_comment_characters", "question_fraction",
    "question_fraction_denominator", "length_measure",
}
_LIMITATIONS = [
    "Behavior summaries are retrospective descriptions of this event's observed public expressions.",
    "They are not pre-event psychological traits, private beliefs, government trust, or observed social ties.",
    "A repost fraction is conditional on recorded public posts, not a probability of reposting after browsing.",
    "No recorded comment does not imply silence during unobserved browsing; unavailable text metrics remain null.",
    "Historical text and annotation labels are not initial memory and are not forwarded to the LLM.",
    "Conditioning profiles on this event's completed behavior is a retrospective scenario, not a leakage-free historical forecast.",
]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def validate_behavior(behavior: dict) -> dict:
    """Validate the exact content-free prompt whitelist and return a deep copy."""
    if not isinstance(behavior, dict) or set(behavior) != _BEHAVIOR_KEYS:
        raise ValueError("Empirical behavior requires exactly the documented content-free fields")
    fixed = {
        "schema_version": "1.0", "measurement_scope": _SCOPE,
        "question_fraction_denominator": "nonempty_cleaned_comment_and_repost_texts",
        "length_measure": "characters_in_identifier_redacted_normalized_text",
    }
    if any(behavior[key] != value for key, value in fixed.items()) or behavior["retrospective"] is not True:
        raise ValueError("Empirical behavior metadata must use the fixed retrospective schema")
    for key in ("resolved_observed_posts", "unresolved_record_locations"):
        if type(behavior[key]) is not int or behavior[key] < 0:
            raise ValueError("Empirical record counts must be nonnegative integers")
    observed = behavior["resolved_observed_posts"]
    unresolved = behavior["unresolved_record_locations"]
    expected_status = "partial" if observed and unresolved else "observed" if observed else "unknown"
    if behavior["status"] != expected_status:
        raise ValueError("Empirical behavior status disagrees with observed/missing provenance")
    count_keys = ("comment_records", "repost_records", "nonempty_comment_records", "nonempty_observed_text_records")
    numeric_keys = ("repost_fraction_among_observed_posts", "median_comment_characters", "question_fraction")
    if not observed:
        if any(behavior[key] is not None for key in count_keys + numeric_keys):
            raise ValueError("Unobserved behavioral metrics must remain null")
        return deepcopy(behavior)
    for key in count_keys:
        if type(behavior[key]) is not int or not 0 <= behavior[key] <= observed:
            raise ValueError("Observed behavior counts are outside their possible range")
    if behavior["comment_records"] + behavior["repost_records"] != observed:
        raise ValueError("Comment/repost counts must sum to resolved observations")
    nc, nt = behavior["nonempty_comment_records"], behavior["nonempty_observed_text_records"]
    if nc > behavior["comment_records"] or nc > nt or nt - nc > behavior["repost_records"]:
        raise ValueError("Nonempty-text counts disagree with observed post types")
    for key in numeric_keys:
        value = behavior[key]
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError("Behavior metrics must be finite nonnegative numbers or null")
    fraction = behavior["repost_fraction_among_observed_posts"]
    if fraction is None or not math.isclose(fraction, behavior["repost_records"] / observed, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Repost fraction must be conditional on the observed public posts")
    length = behavior["median_comment_characters"]
    if (nc == 0 and length is not None) or (nc > 0 and (length is None or length < 1)):
        raise ValueError("Comment-length metric requires at least one nonempty comment")
    question = behavior["question_fraction"]
    if (nt == 0 and question is not None) or (nt > 0 and (question is None or question > 1)):
        raise ValueError("Question fraction requires a nonempty-text denominator and lies between zero and one")
    return deepcopy(behavior)


def _records_and_identifiers(provenance: dict) -> tuple[dict, set[str], dict]:
    index: dict[tuple[str, int], dict] = {}
    identifiers: set[str] = set()
    role_counts: dict[str, int] = {}
    for role, table in provenance.get("all_sheet_data", {}).items():
        rows = table.get("rows", [])
        role_counts[role] = len(rows)
        for record in rows:
            values = record.get("values", {})
            for field in _IDENTITY_FIELDS:
                raw = values.get(field)
                if raw is None:
                    continue
                identifier = str(raw).strip()
                if len(identifier) >= 2:
                    identifiers.add(identifier)
                if field == "id":
                    identifiers.update(re.findall(r"\d{6,}", identifier))
            row = record.get("excel_row")
            if role in ("comments", "reposts") and type(row) is int:
                key = (role, row)
                if key in index:
                    raise ValueError("Ambiguous duplicate sheet-role/row location in provenance")
                index[key] = values
    for item in provenance.get("donor_provenance", {}).values():
        raw = str(item.get("raw_user_id") or "").strip()
        if len(raw) >= 2:
            identifiers.add(raw)
    return index, identifiers, role_counts


def _clean_text(value: Any, identifiers: set[str]) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"(?:https?://|www\.)[^\s<>，。！？；]+", "[链接]", text, flags=re.I)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[邮箱]", text)
    text = re.sub(r"@[\w\u4e00-\u9fff\-]+", "[用户]", text)
    for identifier in sorted(identifiers, key=lambda x: (-len(x), x)):
        text = text.replace(identifier, "[用户]")
    text = re.sub(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)", "[电话]", text)
    return re.sub(r"\s+", " ", text).strip()


def _summarize(records: list[tuple[str, int, dict]], unresolved: int,
               identifiers: set[str]) -> dict:
    kinds = Counter(role for role, _, _ in records)
    cleaned = [(role, _clean_text(values.get("评论内容"), identifiers))
               for role, _, values in records]
    comments = [text for role, text in cleaned if role == "comments" and text]
    texts = [text for _, text in cleaned if text]
    observed = len(records)
    return {
        "schema_version": "1.0",
        "status": "partial" if observed and unresolved else "observed" if observed else "unknown",
        "measurement_scope": _SCOPE,
        "retrospective": True,
        "resolved_observed_posts": observed,
        "unresolved_record_locations": unresolved,
        "comment_records": kinds["comments"] if observed else None,
        "repost_records": kinds["reposts"] if observed else None,
        "repost_fraction_among_observed_posts": kinds["reposts"] / observed if observed else None,
        "nonempty_comment_records": len(comments) if observed else None,
        "nonempty_observed_text_records": len(texts) if observed else None,
        "median_comment_characters": median([len(text) for text in comments]) if comments else None,
        "question_fraction": sum("?" in text or "？" in text for text in texts) / len(texts) if texts else None,
        "question_fraction_denominator": "nonempty_cleaned_comment_and_repost_texts",
        "length_measure": "characters_in_identifier_redacted_normalized_text",
    }


def prepare_single_event(imported_event_dir: str | Path, output_dir: str | Path) -> dict:
    """Write a derivative event and behavioral profiles; never mutate source.

    Required inputs are event.json, its local profiles file, and
    _private/provenance.json. Missing per-donor links yield unknown metrics.
    Malformed/ambiguous global provenance fails explicitly rather than inventing
    observations. The local examples artifact is explicitly outside model input.
    """
    source, target = Path(imported_event_dir).resolve(), Path(output_dir).resolve()
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Output must be separate from the imported event and its ancestor directories")
    event = _read_json(source / "event.json")
    relative_profiles = Path(event.get("profiles_file", "profiles.jsonl"))
    profiles_path = (source / relative_profiles).resolve()
    if relative_profiles.is_absolute() or not profiles_path.is_relative_to(source):
        raise ValueError("profiles_file must resolve within the imported event directory")
    profiles = [json.loads(line) for line in profiles_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    provenance = _read_json(source / "_private" / "provenance.json")
    index, identifiers, role_counts = _records_and_identifiers(provenance)
    donor_map = provenance.get("donor_provenance", {})
    seen_donors: set[str] = set()
    all_locations: dict[tuple[str, int], dict] = {}
    prepared = []
    for profile in profiles:
        donor = profile.get("donor_id")
        if not isinstance(donor, str) or not donor or donor in seen_donors:
            raise ValueError("Each profile requires a unique anonymous donor_id")
        seen_donors.add(donor)
        locations = donor_map.get(donor, {}).get("record_locations", [])
        resolved: list[tuple[str, int, dict]] = []
        unresolved = 0
        seen_locations: set[tuple] = set()
        for location in locations:
            key = (location.get("sheet_role"), location.get("excel_row"))
            if key in seen_locations:
                continue
            seen_locations.add(key)
            if key not in index:
                unresolved += 1
                continue
            values = index[key]
            resolved.append((key[0], key[1], values))
            all_locations[key] = values
        observed_profile = {key: value for key, value in profile.get("observed_profile", {}).items()
                            if key in _COUNT_FIELDS and type(value) is int and value >= 0}
        prepared.append({
            "donor_id": donor,
            "observed_profile": observed_profile,
            "profile_provenance": "observed_public_account_snapshot",
            "observation_time_status": "not_verified_as_pre_event",
            "empirical_behavior": validate_behavior(_summarize(resolved, unresolved, identifiers)),
        })

    examples = []
    examples_by_role: Counter = Counter()
    correction_hits: Counter = Counter()
    nonempty: Counter = Counter()
    kind_counts: Counter = Counter()
    nonempty_times: Counter = Counter()
    for (role, row), values in sorted(all_locations.items()):
        kind_counts[role] += 1
        text = _clean_text(values.get("评论内容"), identifiers)
        if str(values.get("评论时间") or "").strip():
            nonempty_times[role] += 1
        if not text:
            continue
        nonempty[role] += 1
        hits = [word for word in _CORRECTION_WORDS if word in text]
        correction_hits[role] += bool(hits)
        # At most 20 ordinary examples per role; also retain every flagged item
        # for local stage/leakage review. None becomes an executable post.
        if examples_by_role[role] < 20 or hits:
            examples.append({
                "sample_id": f"{role}_{row:05d}",
                "sheet_role": role,
                "source_excel_row": row,
                "observed_at": values.get("评论时间") or None,
                "text": text,
                "correction_related_keyword_flag": bool(hits),
                "correction_related_keywords": hits,
                "truth_status": "not_assessed_keyword_flag_is_not_verification",
            })
            examples_by_role[role] += 1

    status_counts = Counter(row["empirical_behavior"]["status"] for row in prepared)
    summary = {
        "schema_version": "1.0", "event_id": event.get("event_id"),
        "profile_count": len(prepared), "profile_status_counts": dict(status_counts),
        "source_sheet_row_counts": role_counts,
        "resolved_unique_observed_records": dict(kind_counts),
        "nonempty_cleaned_text_records": dict(nonempty),
        "records_with_nonempty_observed_time": dict(nonempty_times),
        "correction_keyword_flagged_records": dict(correction_hits),
        "local_review_examples": len(examples),
        "calibration_mode": "descriptive_behavior_conditioning_not_parameter_estimation_or_fine_tuning",
        "network_relationships": "not_reconstructed_no_explicit_follow_or_reply_edges_available",
        "historical_text_in_model_payload": False,
        "historical_text_replay": False,
        "limitations": _LIMITATIONS,
    }
    derivative = deepcopy(event)
    derivative["profiles_file"] = "profiles.jsonl"
    derivative.setdefault("metadata", {}).update({
        "empirical_behavior_origin": _SCOPE,
        "empirical_behavior_retrospective": True,
        "empirical_behavior_summary_file": "behavior_summary.json",
        "empirical_behavior_calibration": summary["calibration_mode"],
        "historical_text_in_model_payload": False,
        "historical_text_replay": False,
        "initial_memory": "empty_no_historical_comments",
        "network_group_origin": "experimental_assignment",
        "empirical_behavior_limitations": _LIMITATIONS,
    })
    local_examples = {
        "event_id": event.get("event_id"), "local_review_only": True,
        "never_send_to_model": True,
        "redaction": "known_account_identifiers_urls_handles_emails_phone_numbers_removed; unrecognized personal references require human review",
        "correction_flag_meaning": "keyword-based audit aid, neither truth classification nor permission for pre-intervention exposure",
        "examples": examples,
    }
    # All validation and reading precede writing; imported inputs stay untouched.
    target.mkdir(parents=True, exist_ok=True)
    _write_json(target / "event.json", derivative)
    (target / "profiles.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in prepared), encoding="utf-8")
    _write_json(target / "behavior_summary.json", summary)
    _write_json(target / "local_comment_examples.json", local_examples)
    return deepcopy(summary)
