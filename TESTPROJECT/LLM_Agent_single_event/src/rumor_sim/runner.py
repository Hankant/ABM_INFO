"""Experimental scheduling, persistence, empirical donor assignment and resume."""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
import platform
import random
import time

from . import __version__
from . import core
from .config import validate_config, validate_event
from .provider import HTTPDecisionProvider, MockDecisionProvider, BudgetExceeded, PROMPT_VERSION, SYSTEM_PROMPT
from .storage import RunStore, atomic_json, read_json, digest, export_run


def code_hash():
    here = Path(__file__).parent
    return digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(here.glob("*.py"))})


def behavioural_config(c):
    result = copy.deepcopy(c)
    for k in ("max_api_requests", "timeout_seconds"):
        result["llm"].pop(k, None)
    return result


def attach_donor_profiles(state, profiles, seed):
    if not profiles: return state
    state = copy.deepcopy(state)
    allowed = {"followers_count", "following_count", "statuses_count"}
    pool = sorted(profiles, key=lambda p: p["donor_id"])
    if len({p["donor_id"] for p in pool}) != len(pool): raise ValueError("Duplicate donor IDs")
    key = int(digest(["profile_donors", state["event_id"], seed])[:16], 16)
    ids = sorted(state["agents"])
    from .import_data import sample_donor_profiles
    sampled = sample_donor_profiles(pool, ids, key)
    donors_by_id = {p["donor_id"]: p for p in pool}
    assignments = []
    for donor in sampled:
        aid = donor["agent_id"]
        observed = {k: v for k, v in donor["observed_profile"].items() if k in allowed and v is not None}
        for key, value in observed.items():
            if type(value) not in (int, float) or value < 0: raise ValueError(f"Invalid observed profile: {key}")
        state["agents"][aid]["observed_profile"] = observed
        behavior = donors_by_id[donor["donor_id"]].get("empirical_behavior")
        if behavior is not None:
            from .empirical import validate_behavior
            state["agents"][aid]["empirical_behavior"] = validate_behavior(behavior)
        # Donor linkage stays in checkpoints/provenance, not the prompt whitelist.
        assignments.append({"agent_id": aid, "donor_id": donor["donor_id"], "observed_profile": observed,
                            "has_empirical_behavior": behavior is not None})
    state["profile_assignments"] = assignments
    state["profile_sampling"] = {"pool_size": len(pool), "assigned": len(ids),
        "replacement": len(pool) < len(ids), "unique_donors_used": len({p["donor_id"] for p in sampled}),
        "method": "without_replacement_then_replacement_if_needed",
        "scope": "public account counts and optional event-conditional behavior summaries; group/network/trust/priors remain experiment settings"}
    return state


def load_event_file(path):
    path = Path(path).resolve()
    event = read_json(path)
    profiles = []
    if event.get("profiles_file"):
        pp = (path.parent / event["profiles_file"]).resolve()
        if pp.parent != path.parent:
            raise ValueError("profiles_file must reference the event's own directory")
        with pp.open(encoding="utf-8-sig") as f:
            profiles = [json.loads(line) for line in f if line.strip()]
    return event, profiles


def _manifest(config, event, provider_mode, run_id, profiles, policy):
    return {"schema_version": "1.0", "package_version": __version__,
        "run_id": run_id, "provider_mode": provider_mode,
        "is_synthetic_event": bool(event.get("is_synthetic")),
        "contains_real_llm_decisions": provider_mode == "http",
        "publication_validation": "not_established_by_software_tests",
        "correction_origin": event.get("correction_origin", "supplied_document"),
        "evidence_status": event.get("evidence_status", "supplied"),
        "config": behavioural_config(config), "event_hash": digest(event),
        "profiles_hash": digest(profiles), "code_hash": code_hash(),
        "prompt_version": PROMPT_VERSION, "system_prompt": SYSTEM_PROMPT,
        "policy": policy, "python": platform.python_version(),
        "third_party_model_version_note": "Requested alias and response model are recorded. Server weight revision cannot be independently verified."}


def _finish(store, state, config):
    summary = core.summarize(state, config)
    summary.update(run_id=store.manifest["run_id"], provider_mode=store.manifest["provider_mode"],
        is_synthetic_event=store.manifest["is_synthetic_event"],
        correction_origin=store.manifest["correction_origin"],
        empirical_profile_sampling=state.get("profile_sampling"))
    export_run(store.path, summary, core.individual_tbu(state, config))
    store.set_status("completed", last_committed_round=state["round"])
    return summary


def run_trajectory(path, initial, config, event, profiles, provider, run_id, prefix_path=None, progress=None):
    manifest = _manifest(config, event, provider.provider_mode, run_id, profiles, initial.get("policy"))
    store = RunStore(path, manifest, initial, prefix_path=prefix_path)
    state = store.latest()
    store.set_status("running", last_committed_round=state["round"])
    try:
        while state["round"] < config["time"]["last_round"]:
            def decide_in_run(view, identity):
                return provider.decide(view, run_id + "|" + identity)
            result = core.step(state, config, event, decide_in_run)
            store.commit(result); state = result["state"]
            if progress: progress(run_id, state["round"], len(result["decisions"]), getattr(provider, "http_requests", 0))
        return store, _finish(store, state, config)
    except BaseException as exc:
        status = "budget_exhausted" if isinstance(exc, BudgetExceeded) else "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        store.set_status(status, last_committed_round=state["round"], error_type=type(exc).__name__, error=str(exc))
        # Partial exports are explicit, never a completed research summary.
        export_run(store.path, {"run_id": run_id, "status": status, "last_committed_round": state["round"],
                   "provider_mode": provider.provider_mode, "complete": False}, [])
        raise


def policy_spec(state, config, tg, targeting, gt):
    recipients = core.select_recipients(state, targeting, tg, config["policy"]["direct_unique_users"])
    return {"enabled": True, "government_round": tg, "targeting": targeting,
            "credibility": gt, "recipients": recipients}


def execute(event, profiles, config, output, provider_mode="mock", mode="single",
            d_seed=.2, seed=1, tg=20, targeting="inside", gt=.6,
            allow_synthetic=False, max_api_requests=None, progress=None, provider=None):
    validate_config(config)
    validate_event(event, allow_synthetic=allow_synthetic, require_correction=mode != "parent")
    if mode not in ("single", "grid", "parent", "timeline"): raise ValueError("Unknown experiment mode")
    if provider_mode not in ("mock", "http"): raise ValueError("Unknown provider mode")
    grid = config["grid"]
    if mode != "grid":
        if d_seed not in grid["d_seed"] or seed not in grid["seeds"]:
            raise ValueError("Requested d_seed/seed must appear in the frozen grid configuration")
        if mode in ("single", "timeline") and (tg not in grid["government_round"] or targeting not in grid["targeting"] or gt not in grid["credibility"]):
            raise ValueError("Requested policy must appear in frozen grid configuration")
    if provider is not None and provider.provider_mode != provider_mode: raise ValueError("Provider mode mismatch")
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    owns = provider is None
    if owns:
        llm = copy.deepcopy(config["llm"])
        if max_api_requests is not None: llm["max_api_requests"] = max_api_requests
        cls = HTTPDecisionProvider if provider_mode == "http" else MockDecisionProvider
        provider = cls(llm, output / "provider")
    bases = itertools.product(grid["d_seed"], grid["seeds"]) if mode == "grid" else [(d_seed, seed)]
    summaries = []
    summary_path = output / "event_summaries" / f"{event['event_id']}.json"
    try:
        for d, s in bases:
            base_id = f"{event['event_id']}_d{d:g}_s{s}"
            initial = attach_donor_profiles(core.initialize(config, event, d, s), profiles, s)
            if mode == "timeline":
                # The policy schedule is not in any agent's prompt. At TG, core.step
                # forms the risk set from the actually committed TG-1 beliefs.
                initial["policy"] = policy_spec(initial, config, tg, targeting, gt)
                run_id = f"{base_id}_timeline_t{tg}_{targeting}_gt{gt:g}"
                _, summary = run_trajectory(output / "runs" / run_id, initial, config,
                    event, profiles, provider, run_id, progress=progress)
                summaries.append(summary)
                atomic_json(summary_path, summaries)
                continue
            parent_dir = output / "runs" / f"{base_id}_parent"
            parent_store, summary = run_trajectory(parent_dir, initial, config, event, profiles, provider,
                f"{base_id}_parent", progress=progress)
            summaries.append(summary)
            atomic_json(summary_path, summaries)
            if mode == "parent": continue
            policies = itertools.product(grid["government_round"], grid["targeting"], grid["credibility"]) if mode == "grid" else [(tg, targeting, gt)]
            for t, target, credibility in policies:
                pre = parent_store.state_at(t - 1)
                policy = policy_spec(pre, config, t, target, credibility)
                child = core.branch(pre, policy)
                run_id = f"{base_id}_t{t}_{target}_gt{credibility:g}"
                _, summary = run_trajectory(output / "runs" / run_id, child, config, event,
                    profiles, provider, run_id, prefix_path=parent_dir, progress=progress)
                summaries.append(summary)
                atomic_json(summary_path, summaries)
        publish_aggregate(output)
        return summaries
    finally:
        if owns: provider.close()


def publish_aggregate(output):
    output = Path(output)
    summaries = []
    for path in sorted((output / "event_summaries").glob("*.json")):
        summaries.extend(read_json(path))
    atomic_json(output / "study_summary.json", summaries)
    return summaries
