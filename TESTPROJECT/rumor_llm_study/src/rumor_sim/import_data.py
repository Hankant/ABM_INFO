"""Read-only import of the user's three-sheet rumor-event workbooks.

The source books are never changed. Only an explicit whitelist of public account
counts enters profiles.jsonl. Text, raw identities, labels and timestamps are
archived under _private and are never used as t=0 memory, belief or trust.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import datetime as dt
import hashlib
import json
from pathlib import Path
import random
import re
from typing import Any


SOURCE_COLUMNS = ["微博地址", "发博用户", "id", "微博主页", "发博时间", "微博内容", "设备", "转发人数", "评论人数", "点赞人数", "博主性别", "关注数量", "粉丝数量", "发布微博数量", "博主所在地"]
USER_COLUMNS = ["微博地址", "评论用户", "id", "用户微博主页", "评论内容", "评论时间", "评论类型", "性别", "关注数量", "粉丝数量", "发布微博数量", "所在地"]
KNOWN_HEADERS = set(SOURCE_COLUMNS + USER_COLUMNS + ["点赞数", "情感分类结果", "分类的置信度", "积极类别概率", "消极类别概率", "立场", "态度", "赞同/中立/否定", "赞同/否定/中立"])
PROFILE_FIELDS = {"followers_count": "粉丝数量", "following_count": "关注数量", "statuses_count": "发布微博数量"}
CORRECTION_TEMPLATE = "针对网上流传的“{original_claim}”，本账号澄清：这一说法不属实。请勿继续传播未经核实的信息。"


def _blank(v: Any) -> bool:
    return v is None or isinstance(v, str) and not v.strip()


def _jsonable(value: Any) -> Any:
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, float) and (value != value or abs(value) == float("inf")):
        return None
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def normalize_user_id(value: Any, homepage: Any = None) -> str | None:
    """Recover the user ID from 'id=123&...' without retaining URL parameters."""
    if not _blank(value):
        s = str(value).strip().strip("'\"")
        m = re.search(r"(?:^|[?&])(?:u?id)=(\d+)(?:[&#]|$)", s, re.I)
        if m:
            return m.group(1)
        if re.fullmatch(r"\d+(?:\.0+)?", s):
            return s.split(".")[0]
        if re.fullmatch(r"\d+(?:\.\d+)?[Ee][+\-]?\d+", s):
            try:
                number = Decimal(s)
                if number >= 0 and number == number.to_integral_value():
                    return str(int(number))
            except InvalidOperation:
                pass
    if not _blank(homepage):
        m = re.search(r"(?:weibo\.com|weibo\.cn)/(?:u/)?(\d+)(?:[/?#]|$)", str(homepage), re.I)
        if m:
            return m.group(1)
    return None


def parse_public_count(value: Any) -> int | None:
    """Parse plain numbers or public counter labels with 万/亿/K/M units."""
    if _blank(value) or isinstance(value, bool):
        return None
    s = str(value).strip().replace(",", "").replace("，", "")
    match = re.search(r"(?<![\d.])(-?\d+(?:\.\d+)?)\s*([万亿kKmM]?)", s)
    if not match:
        return None
    multiplier = {"": 1, "万": 10000, "亿": 100000000, "k": 1000, "K": 1000, "m": 1000000, "M": 1000000}[match.group(2)]
    try:
        number = Decimal(match.group(1)) * multiplier
    except InvalidOperation:
        return None
    if not number.is_finite() or number < 0:
        return None
    return int(number)


def _read_sheets(path: Path) -> list[tuple[str, list[list[Any]]]]:
    if path.suffix.lower() == ".xls":
        try:
            import xlrd
        except ImportError as exc:
            raise RuntimeError("Reading .xls requires xlrd>=2.0.1; install the project dependencies") from exc
        book = xlrd.open_workbook(path, on_demand=True)
        try:
            return [(s.name, [s.row_values(i) for i in range(s.nrows)]) for s in book.sheets()]
        finally:
            book.release_resources()
    if path.suffix.lower() == ".xlsx":
        try:
            import openpyxl
        except ImportError as exc:
            raise RuntimeError("Reading .xlsx requires openpyxl>=3.1; install the project dependencies") from exc
        book = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            return [(s.title, [list(r) for r in s.iter_rows(values_only=True)]) for s in book]
        finally:
            book.close()
    raise ValueError("Only .xls and .xlsx inputs are supported")


def _header_score(row: list[Any]) -> int:
    return sum(str(v).strip() in KNOWN_HEADERS for v in row if not _blank(v))


def extract_table(rows: list[list[Any]], role: str) -> dict[str, Any]:
    """Detect a real header. Headerless repost sheet row 1 remains a record."""
    first = next((i for i, r in enumerate(rows) if any(not _blank(v) for v in r)), None)
    if first is None:
        return {"headers": [], "rows": [], "header_missing": True, "header_row": None, "repeated_header_rows": 0}
    has_header = _header_score(rows[first]) >= 3
    default = SOURCE_COLUMNS if role == "source" else USER_COLUMNS
    raw_header = rows[first] if has_header else []
    begin = first + 1 if has_header else first
    width = max([len(raw_header)] + [len(r) for r in rows[begin:]], default=0)
    headers = []
    for i in range(width):
        if has_header and i < len(raw_header) and not _blank(raw_header[i]):
            name = str(raw_header[i]).strip()
        elif not has_header and i < len(default):
            name = default[i]
        else:
            name = f"__unnamed_{i + 1}"
        if name in headers:
            name = f"{name}__column_{i + 1}"
        headers.append(name)
    records = []
    repeated = 0
    for index, row in enumerate(rows[begin:], begin + 1):
        if not any(not _blank(v) for v in row):
            continue
        if _header_score(row) >= 3:
            repeated += 1
            continue
        records.append({"excel_row": index, "values": {h: _jsonable(row[i]) if i < len(row) else None for i, h in enumerate(headers)}})
    return {"headers": headers, "rows": records, "header_missing": not has_header, "header_row": first + 1 if has_header else None, "repeated_header_rows": repeated}


def _anonymous_id(event_id: str, user_id: str) -> str:
    return "donor_" + hashlib.sha256(f"{event_id}\0{user_id}".encode("utf-8")).hexdigest()[:20]


def _observed_profile(values: dict[str, Any]) -> dict[str, int]:
    result = {}
    for safe_key, source_column in PROFILE_FIELDS.items():
        parsed = parse_public_count(values.get(source_column))
        if parsed is not None:
            result[safe_key] = parsed
    return result


def import_directory(source_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Import every workbook into event folders; do not call a model or network."""
    source = Path(source_dir).resolve()
    target = Path(output_dir).resolve()
    if not source.is_dir():
        raise ValueError("source_dir must be an existing directory")
    if target == source or source in target.parents:
        raise ValueError("output_dir must be outside the read-only source directory")
    paths = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in (".xls", ".xlsx") and not p.name.startswith("~$"))
    report: dict[str, Any] = {"schema_version": "1.0", "source_file_count": len(paths), "events": [], "totals": {}, "warning": "Observed profile counts are collected public account snapshots, not established pre-event measurements. Network groups, latent belief and government trust are experimental settings. Raw identities/text/labels are private and must never be included in model payloads."}
    totals: Counter[str] = Counter()
    for ordinal, path in enumerate(paths, 1):
        event_id = f"event_{ordinal:03d}"
        folder = target / event_id
        try:
            sheets = _read_sheets(path)
            if len(sheets) != 3:
                raise ValueError("Expected source, comments and reposts as exactly three worksheets")
            tables = {role: extract_table(sheets[i][1], role) for i, role in enumerate(("source", "comments", "reposts"))}
            source_records = tables["source"]["rows"]
            source_record = next((r for r in source_records if normalize_user_id(r["values"].get("id"), r["values"].get("微博主页"))), None)
            if source_record is None:
                raise ValueError("Source sheet has no identifiable source account record")
            source_values = source_record["values"]
            source_uid = normalize_user_id(source_values.get("id"), source_values.get("微博主页"))
            # Identity fields are deliberately absent from public event/profile files.
            source_profile = _observed_profile(source_values)
            rumor_text = str(source_values.get("微博内容") or "").strip()
            original_claim = rumor_text
            correction = CORRECTION_TEMPLATE.format(original_claim=original_claim) if original_claim else ""
            donors: dict[str, dict[str, Any]] = {}
            private_map: dict[str, dict[str, Any]] = {}
            event_counts: Counter[str] = Counter()
            for role in ("comments", "reposts"):
                for record in tables[role]["rows"]:
                    values = record["values"]
                    uid = normalize_user_id(values.get("id"), values.get("用户微博主页"))
                    if uid is None:
                        event_counts[f"{role}_excluded_no_user_id"] += 1
                        continue
                    event_counts[f"{role}_records"] += 1
                    if uid == source_uid:
                        event_counts["source_account_engagement_rows_excluded"] += 1
                        continue
                    donor_id = _anonymous_id(event_id, uid)
                    observed = _observed_profile(values)
                    if uid not in donors:
                        donors[uid] = {"donor_id": donor_id, "observed_profile": observed, "profile_provenance": "observed_public_account_snapshot", "observation_time_status": "not_verified_as_pre_event"}
                        private_map[donor_id] = {"raw_user_id": uid, "record_locations": [], "field_conflicts": []}
                    else:
                        event_counts["duplicate_engagement_rows_collapsed"] += 1
                        current = donors[uid]["observed_profile"]
                        for key, value in observed.items():
                            if key not in current:
                                current[key] = value
                            elif current[key] != value:
                                private_map[donor_id]["field_conflicts"].append({"field": key, "retained_first_value": current[key], "later_value": value, "sheet_role": role, "excel_row": record["excel_row"]})
                    private_map[donor_id]["record_locations"].append({"sheet_role": role, "excel_row": record["excel_row"]})
            profiles = sorted(donors.values(), key=lambda x: x["donor_id"])
            event_counts["unique_profile_donors"] = len(profiles)
            event_counts["missing_rumor_text"] = int(not rumor_text)
            event_counts["headerless_repost_sheet"] = int(tables["reposts"]["header_missing"])
            event_counts["profile_donors_below_582"] = int(len(profiles) < 582)
            event = {"schema_version": "1.0", "event_id": event_id, "claim_id": "claim_" + event_id,
                     "original_claim": original_claim, "rumor_text": rumor_text, "is_synthetic": False,
                     "rumor_origin": "source_workbook_post_text", "claim_origin": "source_post_verbatim_requires_content_review",
                     "correction_text": correction, "correction_mode": "scripted_no_evidence", "correction_origin": "experimental_script",
                     "correction_status": "experimental_script_not_verified_official", "evidence_text": "", "evidence_status": "not_provided",
                     "source_profile": source_profile, "profiles_file": "profiles.jsonl",
                     "import_status": "ready_for_content_review" if rumor_text and profiles else "missing_rumor_text" if not rumor_text else "missing_profile_donors",
                     "metadata": {"counts": dict(event_counts), "empirical_follow_source_available": False,
                                  "network_group_origin": "experimental_assignment", "profile_sampling": "without_replacement_then_replacement_if_needed",
                                  "initial_memory": "empty_no_historical_comments", "trust_and_private_belief_origin": "experimental_not_inferred_from_comments",
                                  "official_correction_supplied": False, "content_review_required_before_external_API": True}}
            private = {"contains_personal_source_data": True, "never_send_to_model": True,
                       "relative_source_path": str(path.relative_to(source)), "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "source_record": source_record, "all_sheet_data": {role: {"sheet_name": sheets[i][0], **tables[role]} for i, role in enumerate(("source", "comments", "reposts"))},
                       "donor_provenance": private_map, "deduplication_rule": "normalized user ID; source excluded; first nonmissing profile value retained; all conflicts recorded"}
            _write_json(folder / "event.json", event)
            (folder / "profiles.jsonl").write_text("".join(json.dumps(p, ensure_ascii=False, allow_nan=False) + "\n" for p in profiles), encoding="utf-8")
            _write_json(folder / "_private" / "provenance.json", private)
            report["events"].append({"event_id": event_id, "event_file": f"{event_id}/event.json", "status": event["import_status"], **dict(event_counts)})
            totals.update(event_counts)
            totals["imported_events"] += 1
        except Exception as exc:
            # Exceptions do not include raw cells, names or user IDs.
            report["events"].append({"event_id": event_id, "status": "import_error", "error_type": type(exc).__name__, "error": str(exc)})
            totals["failed_events"] += 1
    report["totals"] = dict(totals)
    _write_json(target / "import_report.json", report)
    return report


def sample_donor_profiles(profile_pool: list[dict[str, Any]], agent_ids: list[str], seed: int) -> list[dict[str, Any]]:
    """Assign anonymous count-only profiles; repeated donors yield independent dicts."""
    if not profile_pool:
        raise ValueError("No observed profile donors are available")
    if len(set(agent_ids)) != len(agent_ids):
        raise ValueError("Agent IDs must be unique")
    ordered = sorted(profile_pool, key=lambda p: p["donor_id"])
    stable_seed = int.from_bytes(hashlib.sha256(f"profile-draw:{seed}".encode()).digest()[:8], "big")
    rng = random.Random(stable_seed)
    selected = rng.sample(ordered, min(len(ordered), len(agent_ids)))
    if len(selected) < len(agent_ids):
        selected += rng.choices(ordered, k=len(agent_ids) - len(selected))
    rng.shuffle(selected)
    assignments = []
    for agent_id, donor in zip(agent_ids, selected):
        observed = {k: v for k, v in donor.get("observed_profile", {}).items() if k in PROFILE_FIELDS and type(v) is int and v >= 0}
        assignments.append({"agent_id": agent_id, "donor_id": donor["donor_id"], "observed_profile": deepcopy(observed)})
    return assignments
