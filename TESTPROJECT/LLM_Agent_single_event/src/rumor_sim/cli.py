"""Command line entrypoints. HTTP requires explicit --provider http."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

from .config import load_json, research_config, smoke_config, single_event_config, validate_config, validate_event, estimate
from .storage import atomic_json


ROOT = Path(__file__).resolve().parents[2]


def _print(value):
    # ASCII-escaped JSON is safe even in Windows legacy code pages.
    print(json.dumps(value, ensure_ascii=True, indent=2), flush=True)


def parser():
    p = argparse.ArgumentParser(description="LLM rumor-cocoon simulation; no hidden mock fallback")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Write documented baseline configurations and a labelled synthetic event")
    init.add_argument("--directory", type=Path, default=ROOT)
    imp = sub.add_parser("import-data", help="Read XLS/XLSX source files without modifying them")
    imp.add_argument("--source", required=True, type=Path)
    imp.add_argument("--output", required=True, type=Path)
    check = sub.add_parser("check", help="Validate config and event without any API request")
    check.add_argument("--config", type=Path, default=ROOT / "config/research.json")
    check.add_argument("--event", type=Path)
    check.add_argument("--allow-synthetic", action="store_true")
    est = sub.add_parser("estimate", help="Count full experiments and conservative request bounds")
    est.add_argument("--config", type=Path, default=ROOT / "config/research.json")
    est.add_argument("--events", type=int, default=1)
    prep = sub.add_parser("prepare-single", help="Derive one event's empirical behavior summaries locally; no API calls")
    prep.add_argument("--source", type=Path, default=ROOT / "data/imported/event_052")
    prep.add_argument("--output", type=Path, default=ROOT / "data/single_event/event_052")
    report = sub.add_parser("report", help="Build a self-contained single-event HTML report from committed exports")
    report.add_argument("--run", required=True, type=Path)
    report.add_argument("--output", type=Path)
    for name in ("run", "grid", "parent", "single-event"):
        cmd = sub.add_parser(name, help={"run": "One parent and one policy branch",
            "grid": "All policy combinations; resumes exactly matching completed rounds",
            "parent": "No-correction trajectory only",
            "single-event": "ONE continuous rumor-to-correction trajectory; no extra untreated run"}[name])
        cmd.add_argument("--config", type=Path, default=ROOT / ("config/single_event.json" if name == "single-event" else "config/research.json"))
        event = cmd.add_mutually_exclusive_group(required=True)
        event.add_argument("--event", type=Path)
        event.add_argument("--event-list", type=Path, help="JSON array of event.json paths (relative to list)")
        cmd.add_argument("--output", required=True, type=Path)
        cmd.add_argument("--provider", choices=["mock", "http"], default="mock")
        cmd.add_argument("--max-api-requests", type=int, help="Absolute cumulative cap for this output/provider directory")
        cmd.add_argument("--allow-synthetic", action="store_true")
        cmd.add_argument("--d-seed", type=float, default=.2)
        cmd.add_argument("--seed", type=int, default=1)
        cmd.add_argument("--tg", type=int, default=20)
        cmd.add_argument("--targeting", choices=["inside", "random", "outside"], default="inside")
        cmd.add_argument("--gt", type=float, default=.6)
    return p


def init_files(directory):
    directory = Path(directory)
    files = {"config/research.json": research_config(), "config/smoke.json": smoke_config(),
        "config/single_event.json": single_event_config(),
        "data/synthetic_event.json": {
            "event_id": "synthetic_library", "claim_id": "synthetic_claim",
            "is_synthetic": True, "language": "zh-CN",
            "original_claim": "虚构场景中的星湾图书馆将在下周永久关闭。",
            "rumor_text": "虚构程序测试：听说星湾图书馆下周将永久关闭，目前没有更多依据。",
            "correction_text": "针对网上流传的图书馆下周永久关闭的说法，本账号澄清：这一说法不属实。请勿继续传播未经核实的信息。",
            "correction_mode": "scripted_no_evidence", "correction_origin": "experimental_script",
            "evidence_text": "", "evidence_status": "not_provided",
            "rumor_source_id": "SOURCE", "government_id": "GOV"}}
    for rel, data in files.items():
        path = directory / rel
        if path.exists() and load_json(path) != data:
            raise ValueError(f"Refusing to overwrite changed input: {path}")
        atomic_json(path, data)
    return {"created_or_verified": list(files), "root": str(directory)}


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            _print(init_files(args.directory)); return 0
        if args.command == "import-data":
            from .import_data import import_directory
            report = import_directory(args.source, args.output)
            _print(report); return 0
        if args.command == "prepare-single":
            from .empirical import prepare_single_event
            _print(prepare_single_event(args.source, args.output)); return 0
        if args.command == "report":
            from .report import build_report
            _print(build_report(args.run, args.output)); return 0
        config = validate_config(load_json(args.config))
        if args.command == "estimate":
            if args.events < 1: raise ValueError("events must be positive")
            _print(estimate(config, args.events)); return 0
        from .runner import execute, load_event_file, publish_aggregate
        if args.command == "check":
            result = {"config_valid": True, "grid": estimate(config)}
            if args.event:
                event, profiles = load_event_file(args.event)
                validate_event(event, allow_synthetic=args.allow_synthetic)
                result.update(event_valid=True, event_id=event["event_id"], donor_profiles=len(profiles),
                    correction_origin=event.get("correction_origin"))
            _print(result); return 0
        if args.provider == "http" and args.max_api_requests is None:
            raise ValueError("Explicit --max-api-requests is required for HTTP runs; retries count against it")
        if args.max_api_requests is not None and args.max_api_requests < 1:
            raise ValueError("max-api-requests must be positive")
        from .provider import HTTPDecisionProvider, MockDecisionProvider
        paths = [args.event]
        if args.event_list:
            raw = load_json(args.event_list)
            if not isinstance(raw, list) or any(not isinstance(v, str) for v in raw):
                raise ValueError("event-list must be an array of event.json paths")
            paths = [(args.event_list.parent / v).resolve() for v in raw]
        if not paths: raise ValueError("No events selected")
        if args.command == "single-event" and len(paths) != 1:
            raise ValueError("single-event accepts exactly one event")
        # Validate every input before the first API request or trajectory mutation.
        loaded = [load_event_file(p) for p in paths]
        for event, _ in loaded:
            validate_event(event, allow_synthetic=args.allow_synthetic, require_correction=args.command != "parent")
        if len({e["event_id"] for e, _ in loaded}) != len(loaded): raise ValueError("Duplicate event_id in batch")
        llm = dict(config["llm"])
        if args.max_api_requests is not None: llm["max_api_requests"] = args.max_api_requests
        cls = HTTPDecisionProvider if args.provider == "http" else MockDecisionProvider
        last_update = [0.0]
        def progress(run_id, round_no, calls, requests):
            now = time.monotonic()
            if round_no % 10 == 0 or now - last_update[0] >= 20:
                _print({"run": run_id, "round": round_no, "round_decisions": calls,
                        "total_http_requests": requests})
                last_update[0] = now
        all_summaries = []
        with cls(llm, args.output / "provider") as provider:
            for event, profiles in loaded:
                results = execute(event, profiles, config, args.output, provider_mode=args.provider,
                    mode={"run": "single", "grid": "grid", "parent": "parent", "single-event": "timeline"}[args.command],
                    d_seed=args.d_seed, seed=args.seed, tg=args.tg, targeting=args.targeting, gt=args.gt,
                    allow_synthetic=args.allow_synthetic, provider=provider, progress=progress)
                all_summaries.extend(results)
            publish_aggregate(args.output)
            _print({"status": "completed", "trajectories": len(all_summaries),
                "provider_mode": args.provider, "total_http_requests": provider.http_requests,
                "output": str(args.output.resolve())})
        if args.command == "single-event":
            from .report import build_report
            for summary in all_summaries:
                _print(build_report(args.output / "runs" / summary["run_id"]))
        return 0
    except KeyboardInterrupt:
        if getattr(args, "output", None) and (args.output / "event_summaries").exists():
            from .runner import publish_aggregate
            publish_aggregate(args.output)
        _print({"status": "interrupted", "note": "Rerun the identical command to resume committed rounds"})
        return 130
    except Exception as exc:
        if getattr(args, "output", None) and (args.output / "event_summaries").exists():
            from .runner import publish_aggregate
            publish_aggregate(args.output)
        _print({"status": "failed", "type": type(exc).__name__, "message": str(exc)})
        return 2
