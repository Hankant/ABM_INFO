"""Single source of configuration and input validation."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path


def research_config():
    return {
        "schema_version": "1.0", "label": "research_582",
        "population": {"n_inside": 82, "n_outside": 500,
            "activity_levels": [0.1, 0.2, 0.3],
            "inside_counts": [27, 28, 27], "outside_counts": [167, 166, 167],
            "trust_levels": [0.25, 0.5, 0.75],
            "sharing_styles": ["rare", "sometimes", "often"],
            "willing_inside": 49, "willing_outside": 300},
        "prior": {"overall_mean": 0.579, "within_group_offset": 0.05},
        "network": {"directed": True, "same_group_follows": 8,
            "cross_group_follows": 2, "inside_follow_source": True,
            "outside_follow_source": False, "pre_follow_government": False},
        "feed": {"following_slots": 1, "recommendation_probability": 0.1,
            "recommendation_slots": 1, "direct_extra_slots": 1,
            "post_ttl_rounds": 40, "recency_half_life_rounds": 5,
            "max_reads_per_post": 3, "repeat_gap_rounds": 5,
            "max_reposts_per_content": 1, "new_user_post_delay": 1,
            "memory_decision_rounds": 5},
        "time": {"source_round": 0, "first_decision_round": 1,
            "last_round": 80, "pb_checkpoint_round": 5,
            "followup_max_elapsed": 30, "followup_include_both_endpoints": True},
        "policy": {"direct_unique_users": 40, "direct_delivery_rounds": 1},
        "belief": {"accept_min": 60, "reject_max": 40},
        "grid": {"d_seed": [0.0, 0.2, 0.4],
            "government_round": [10, 20, 30, 40, 50],
            "targeting": ["inside", "random", "outside"],
            "credibility": [0.2, 0.6, 1.0], "seeds": [1, 2, 3]},
        "llm": {"base_url": "https://api.zetatechs.com/v1",
            "model": "deepseek-v4-flash",
            "api_key_env": "RUMOR_LLM_API_KEY", "temperature": 0.7,
            "top_p": 0.8, "max_output_tokens": 384, "max_retries": 2,
            "comment_max_characters": 80, "reason_max_characters": 40,
            "json_mode": True,
            "extra_body": {"thinking": {"type": "disabled"}},
            "timeout_seconds": 90, "max_api_requests": 20},
    }


def smoke_config():
    """Explicitly different engineering fixture, never an empirical result."""
    c = research_config()
    c["label"] = "engineering_smoke_10"
    c["population"].update(n_inside=4, n_outside=6,
        inside_counts=[1, 2, 1], outside_counts=[2, 2, 2],
        willing_inside=2, willing_outside=4)
    c["network"].update(same_group_follows=2, cross_group_follows=1)
    c["policy"]["direct_unique_users"] = 2
    return c


def load_json(path):
    with Path(path).open(encoding="utf-8-sig") as f:
        return json.load(f)


def _int(v, name, minimum=0):
    if type(v) is not int or v < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _prob(v, name):
    if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1:
        raise ValueError(f"{name} must be finite and within [0, 1]")


def validate_config(c):
    for section in ("population", "prior", "network", "feed", "time", "policy", "belief", "grid", "llm"):
        if not isinstance(c.get(section), dict):
            raise ValueError(f"Missing configuration section: {section}")
    p, net, feed, time = c["population"], c["network"], c["feed"], c["time"]
    for group in ("inside", "outside"):
        n = p[f"n_{group}"]; _int(n, f"n_{group}", 2)
        if n % 2:
            raise ValueError("Group sizes must be even for the exact half +/- prior assignment")
        counts = p[f"{group}_counts"]
        if len(counts) != 3 or any(type(x) is not int or x < 0 for x in counts) or sum(counts) != n:
            raise ValueError(f"{group}_counts must be 3 nonnegative counts summing to group size")
        _int(p[f"willing_{group}"], f"willing_{group}")
        if p[f"willing_{group}"] > n:
            raise ValueError("Willing count exceeds group size")
    for key in ("activity_levels", "trust_levels"):
        if len(p[key]) != 3: raise ValueError(f"{key} needs exactly 3 values")
        for v in p[key]: _prob(v, key)
    if p["sharing_styles"] != ["rare", "sometimes", "often"]:
        raise ValueError("Sharing styles must match the documented three profile levels")
    _int(net["same_group_follows"], "same_group_follows")
    _int(net["cross_group_follows"], "cross_group_follows")
    if net["same_group_follows"] >= min(p["n_inside"], p["n_outside"]):
        raise ValueError("Too few peers for same-group follows")
    if net["cross_group_follows"] > min(p["n_inside"], p["n_outside"]):
        raise ValueError("Too few peers for cross-group follows")
    fixed_net = {"directed": True, "inside_follow_source": True,
                 "outside_follow_source": False, "pre_follow_government": False}
    if any(net.get(k) != v for k, v in fixed_net.items()):
        raise ValueError("Network direction/source/government-follow flags contradict the protocol")
    for key in ("following_slots", "recommendation_slots", "direct_extra_slots",
                "max_reposts_per_content", "new_user_post_delay"):
        if feed.get(key) != 1: raise ValueError(f"This protocol requires feed.{key}=1")
    for key in ("post_ttl_rounds", "max_reads_per_post", "repeat_gap_rounds", "memory_decision_rounds"):
        _int(feed[key], key, 1)
    if feed["recency_half_life_rounds"] <= 0: raise ValueError("Invalid half life")
    _prob(feed["recommendation_probability"], "recommendation_probability")
    for k in ("last_round", "pb_checkpoint_round", "followup_max_elapsed"):
        _int(time[k], k, 1)
    if time["source_round"] != 0 or time["first_decision_round"] != 1:
        raise ValueError("Source must publish at 0; first decision round must be 1")
    if time["followup_include_both_endpoints"] is not True:
        raise ValueError("TBU includes both endpoints")
    n_direct = c["policy"]["direct_unique_users"]; _int(n_direct, "direct_unique_users", 1)
    if n_direct > min(p["n_inside"], p["n_outside"]): raise ValueError("Direct budget exceeds target group")
    if c["policy"]["direct_delivery_rounds"] != 1: raise ValueError("Direct correction is delivered once")
    if c["belief"] != {"accept_min": 60, "reject_max": 40}:
        raise ValueError("Belief thresholds must remain 60 and 40 in this protocol")
    g = c["grid"]
    for k in ("d_seed", "government_round", "targeting", "credibility", "seeds"):
        if not g.get(k) or len(g[k]) != len(set(g[k])): raise ValueError(f"Invalid or duplicate grid: {k}")
    for tg in g["government_round"]:
        _int(tg, "government_round", 1)
        if tg <= time["pb_checkpoint_round"]: raise ValueError("PBd checkpoint must precede all policies")
        if tg + time["followup_max_elapsed"] > time["last_round"]:
            raise ValueError("last_round does not cover the latest policy's full followup")
    if set(g["targeting"]) - {"inside", "random", "outside"}: raise ValueError("Unknown targeting")
    for v in g["credibility"]: _prob(v, "credibility")
    if set(g["credibility"]) - {0.2, 0.6, 1.0}:
        raise ValueError("Only the documented 2/10, 6/10 and 10/10 credibility stimuli are implemented")
    for seed in g["seeds"]: _int(seed, "seed")
    _prob(c["prior"]["overall_mean"], "overall_mean")
    offset = c["prior"]["within_group_offset"]
    if not 0 <= offset <= .5: raise ValueError("Invalid prior offset")
    n = p["n_inside"] + p["n_outside"]
    for d in g["d_seed"]:
        if type(d) not in (int, float) or not math.isfinite(d): raise ValueError("Invalid d_seed")
        for mean in (c["prior"]["overall_mean"] + p["n_outside"] / n * d,
                     c["prior"]["overall_mean"] - p["n_inside"] / n * d):
            if mean - offset < 0 or mean + offset > 1: raise ValueError("Prior would leave [0,1]")
    llm = c["llm"]
    if not llm.get("base_url", "").startswith("https://"): raise ValueError("HTTPS endpoint required")
    if not llm.get("model"): raise ValueError("Model ID required")
    if any(k in llm for k in ("api_key", "apikey", "key", "Authorization")):
        raise ValueError("Use an environment variable, never a key in JSON")
    _int(llm["max_api_requests"], "max_api_requests", 1)
    if llm["max_retries"] != 2: raise ValueError("Protocol uses initial request + at most 2 retries")
    return c


def validate_event(event, allow_synthetic=False, require_correction=True):
    if not isinstance(event, dict): raise ValueError("Event must be an object")
    for k in ("event_id", "claim_id", "original_claim", "rumor_text"):
        if not isinstance(event.get(k), str) or not event[k].strip(): raise ValueError(f"Missing event.{k}")
    for k in ("event_id", "claim_id"):
        if not all(x.isalnum() or x in "_-" for x in event[k]): raise ValueError(f"Unsafe identifier: {k}")
    if event.get("is_synthetic") and not allow_synthetic:
        raise ValueError("Synthetic event requires --allow-synthetic; its results are not research evidence")
    if require_correction:
        for k in ("correction_text",):
            if not isinstance(event.get(k), str) or not event[k].strip():
                raise ValueError(f"Missing real {k}; supply a matched official correction before policy runs")
        scripted = event.get("correction_mode") == "scripted_no_evidence"
        if scripted:
            if event.get("correction_origin") != "experimental_script" or event.get("evidence_status") != "not_provided":
                raise ValueError("Scripted correction must be explicitly labelled as an experiment with no supplied evidence")
        elif not isinstance(event.get("evidence_text"), str) or not event["evidence_text"].strip():
            raise ValueError("Missing evidence; explicitly select scripted_no_evidence only for an experimental stimulus")
        if event.get("correction_status") in ("missing", "unverified"):
            raise ValueError("Correction has not been supplied/verified")
    return event


def estimate(c, event_count=1):
    validate_config(c)
    g, t, p = c["grid"], c["time"], c["population"]
    parents = len(g["d_seed"]) * len(g["seeds"])
    per_tg = len(g["targeting"]) * len(g["credibility"])
    branches = parents * len(g["government_round"]) * per_tg
    simulated_rounds = parents * (t["last_round"] + per_tg * sum(t["last_round"]-tg+1 for tg in g["government_round"]))
    n = p["n_inside"] + p["n_outside"]
    return {"events": event_count, "parent_trajectories": parents * event_count,
        "policy_trajectories": branches * event_count,
        "logical_trajectories": (parents + branches) * event_count,
        "simulated_rounds_with_prefix_reuse": simulated_rounds * event_count,
        "decision_upper_bound": simulated_rounds * n * event_count,
        "http_attempt_upper_bound_including_retries": simulated_rounds * n * 3 * event_count,
        "last_round": t["last_round"],
        "note": "Conservative bounds, not a cost quote. Actual calls depend on exposure and cache."}
