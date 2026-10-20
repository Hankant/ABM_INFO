"""Pure, synchronous rumor-study simulation core.

No HTTP or filesystem operations occur here. States and returned envelopes consist
only of JSON-compatible values. ``step`` is transactional: even a failed decision
cannot modify the supplied state. The injected decision function owns model I/O.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import random
from typing import Any, Callable, Iterable


DECISION_FIELDS = frozenset({
    "belief_score", "action", "target_post_id", "public_stance", "comment", "reason"
})
OBSERVED_PROFILE_FIELDS = frozenset({
    "followers_count", "following_count", "statuses_count",
})
EXPOSURE_CHANNELS = ("following", "recommendation", "government_direct",
                     "thread_comment", "thread_repost")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _digest(*parts: Any) -> bytes:
    return hashlib.sha256(_canonical(parts).encode("utf-8")).digest()


def keyed_uniform(*parts: Any) -> float:
    """A stable, process-independent number strictly between zero and one."""
    bits = int.from_bytes(_digest(*parts)[:8], "big") >> 11
    return (bits + 1) / (2**53 + 2)


def _shuffled(values: list, *key: Any) -> list:
    result = list(values)
    random.Random(int.from_bytes(_digest(*key), "big")).shuffle(result)
    return result


def _integer(value: Any, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _expand(levels: list, counts: list, n: int, name: str) -> list:
    if len(levels) != len(counts):
        raise ValueError(f"{name}: levels and counts do not match")
    if sum(_integer(c, name) for c in counts) != n:
        raise ValueError(f"{name}: counts do not sum to group size")
    return [value for value, count in zip(levels, counts) for _ in range(count)]


def belief_class(score: int | None, config: dict) -> str:
    if score is None:
        return "unaware"
    if type(score) is not int or not 0 <= score <= 100:
        raise ValueError("belief_score must be an integer within 0..100 or None")
    if score >= config["belief"]["accept_min"]:
        return "accept"
    if score <= config["belief"]["reject_max"]:
        return "reject"
    return "uncertain"


def _source_post(event: dict) -> dict:
    event_id = event["event_id"]
    source = event.get("rumor_source_id", "SOURCE")
    return {
        "post_id": f"{event_id}:source:0", "parent_post_id": None,
        "claim_id": event["claim_id"], "content_id": f"{event_id}:rumor_origin",
        "author_id": source, "kind": "rumor_original", "created_round": 0,
        "visible_from": 1, "text": event["rumor_text"], "quoted_context": None,
        "root_text": event["rumor_text"], "root_evidence": "",
        "root_source_id": source,
        "root_source_profile": _profile_counts(event.get("source_profile", {}), strict=False),
        "source_cue": event.get("rumor_source_cue", "一名用户发布的待核实信息。"),
        "public_stance": None, "direct_only": False,
    }


def _profile_counts(observed: dict, strict: bool = True) -> dict:
    if not isinstance(observed, dict):
        raise ValueError("Observed static profile must be an object")
    if strict and not set(observed) <= OBSERVED_PROFILE_FIELDS:
        raise ValueError("Observed profile contains non-whitelisted fields")
    return {key: _integer(value, key) for key, value in observed.items()
            if key in OBSERVED_PROFILE_FIELDS and value is not None}


def initialize(config: dict, event: dict, d_seed: float, seed: int) -> dict:
    """Generate fixed marginal profiles, directed follows, and an unexposed state.

    Historical comments/reposts in an input event are deliberately not imported as
    memory, initial belief or interactions. Use ``apply_profiles`` only after an
    explicit, deidentified static-field mapping has been established.
    """
    pop, prior, network = config["population"], config["prior"], config["network"]
    ni = _integer(pop["n_inside"], "n_inside", 1)
    no = _integer(pop["n_outside"], "n_outside", 1)
    if ni % 2 or no % 2:
        raise ValueError("Equal +/- prior offsets require even sizes in both groups")
    _integer(seed, "seed")
    d_seed = _finite_number(d_seed, "d_seed")
    mu = _finite_number(prior["overall_mean"], "overall_mean")
    offset = _finite_number(prior["within_group_offset"], "within_group_offset")
    same = _integer(network["same_group_follows"], "same_group_follows")
    cross = _integer(network["cross_group_follows"], "cross_group_follows")
    if same >= min(ni, no) or cross > min(ni, no):
        raise ValueError("Requested directed degrees exceed eligible user pools")
    if network.get("directed", True) is not True:
        raise ValueError("This study requires directed following edges")
    if network.get("pre_follow_government", False):
        raise ValueError("The fixed study has no pre-followed government account")
    if network.get("outside_follow_source", False):
        raise ValueError("Outside users cannot follow the source at initialization")
    if not network.get("inside_follow_source", True):
        raise ValueError("Inside users must follow the source at initialization")
    for field in ("event_id", "claim_id", "original_claim", "rumor_text"):
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise ValueError(f"event.{field} must be text")
    if config["time"].get("source_round", 0) != 0 or config["time"].get("first_decision_round", 1) != 1:
        raise ValueError("The fixed study starts with source round 0 and decisions at round 1")

    ids = {"inside": [f"C{i:03d}" for i in range(1, ni + 1)],
           "outside": [f"O{i:03d}" for i in range(1, no + 1)]}
    source = event.get("rumor_source_id", "SOURCE")
    government = event.get("government_id", "GOV")
    all_ids = set(ids["inside"] + ids["outside"])
    if source == government or source in all_ids or government in all_ids:
        raise ValueError("Scripted account IDs must be distinct from all user IDs")
    agents = {}
    for group, n in (("inside", ni), ("outside", no)):
        counts = pop["inside_counts" if group == "inside" else "outside_counts"]
        traits = {}
        for field, levels in (("activity", pop["activity_levels"]),
                              ("prior_government_trust", pop["trust_levels"]),
                              ("sharing_style", pop["sharing_styles"])):
            expanded = _expand(levels, counts, n, field)
            traits[field] = _shuffled(expanded, seed, group, "trait", field)
        willing_n = _integer(pop["willing_inside" if group == "inside" else "willing_outside"], "willing_count")
        if willing_n > n:
            raise ValueError("Willing count exceeds group size")
        traits["correction_share_willingness"] = _shuffled(
            ["willing"] * willing_n + ["reading_only"] * (n - willing_n),
            seed, group, "trait", "correction_share_willingness")
        signs = _shuffled([-1] * (n // 2) + [1] * (n // 2),
                          seed, group, "trait", "prior_offset")
        group_mean = mu + no / (ni + no) * d_seed if group == "inside" else mu - ni / (ni + no) * d_seed
        for i, aid in enumerate(ids[group]):
            p = group_mean + signs[i] * offset
            if not 0 <= p <= 1:
                raise ValueError("Initial prior is outside [0,1]; do not silently clip it")
            agent = {"agent_id": aid, "group": group,
                     **{k: values[i] for k, values in traits.items()},
                     "prior_acceptance": p, "follows": [],
                     "belief_score": None, "belief_state": "unaware", "memory": [],
                     "seen_posts": {}, "reposted_content_ids": [],
                     "first_exposure_round": None, "last_action": "idle",
                     "observed_profile": {}, "profile_origin": "designed_baseline"}
            for field in ("activity", "prior_government_trust"):
                if not 0 <= _finite_number(agent[field], field) <= 1:
                    raise ValueError(f"{field} must be within [0,1]")
            agents[aid] = agent
    for aid in sorted(agents):
        group = agents[aid]["group"]
        other = "outside" if group == "inside" else "inside"
        same_ids = [x for x in ids[group] if x != aid]
        follows = _shuffled(same_ids, seed, aid, "same_group_follows")[:same]
        follows += _shuffled(ids[other], seed, aid, "cross_group_follows")[:cross]
        if group == "inside":
            follows.append(source)
        agents[aid]["follows"] = sorted(follows)
    post = _source_post(event)
    return {
        "schema_version": "rumor-core-1", "round": 0, "seed": seed,
        "d_seed": d_seed, "event_id": event["event_id"], "claim_id": event["claim_id"],
        "original_claim": event["original_claim"], "source_id": source,
        "government_id": government, "agents": agents, "posts": {post["post_id"]: post},
        "pbd": None, "policy": None, "risk_ids": [], "first_rejections": {},
        "round_metrics": [],
        "direct_budget": _integer(config["policy"]["direct_unique_users"], "direct_unique_users", 1),
    }


def apply_profiles(state: dict, profiles: list[dict],
                   allowed_fields: Iterable[str] = OBSERVED_PROFILE_FIELDS) -> dict:
    """Attach already-deidentified static observations without changing the design.

    Each row has an anonymous simulation ``agent_id`` and ``observed_profile``.
    The caller must verify anonymization and mapping; this hook is not an identity
    resolver. Historical outcomes, handles, raw biographies, trust/prior assignments,
    memory and network overrides are never accepted as observed profile fields.
    """
    allowed = frozenset(allowed_fields)
    if not allowed <= OBSERVED_PROFILE_FIELDS:
        raise ValueError("Unknown observed-profile whitelist fields")
    if state["round"] != 0:
        raise ValueError("Static observed profiles must be attached before simulation")
    result = copy.deepcopy(state)
    used = set()
    for row in profiles:
        aid = row.get("agent_id")
        if aid not in result["agents"] or aid in used:
            raise ValueError("Unknown or repeated anonymous agent_id in observed profiles")
        used.add(aid)
        observed = row.get("observed_profile", {})
        if not isinstance(observed, dict) or not set(observed) <= allowed:
            raise ValueError("Observed profile contains non-whitelisted fields")
        observed = _profile_counts(observed)
        result["agents"][aid]["observed_profile"] = observed
        result["agents"][aid]["observed_profile_provenance"] = copy.deepcopy(
            row.get("provenance", "explicit_deidentified_static_mapping"))
    return result


def select_recipients(state: dict, targeting: str, tg: int, n: int) -> list[str]:
    if targeting not in {"inside", "outside", "random"}:
        raise ValueError("Unknown targeting category")
    _integer(tg, "government_round", 1)
    _integer(n, "direct_unique_users", 1)
    eligible = [aid for aid, a in state["agents"].items()
                if targeting == "random" or a["group"] == targeting]
    if n > len(eligible):
        raise ValueError("Direct budget exceeds the eligible group size")
    return sorted(eligible, key=lambda aid: (
        _digest(state["event_id"], state["seed"], tg, targeting, "recipients", aid), aid))[:n]


def _validate_policy(state: dict, policy: dict, budget: int) -> None:
    if policy.get("enabled") is not True:
        raise ValueError("Use policy=None for an untreated trajectory")
    _integer(policy.get("government_round"), "government_round", 1)
    if policy.get("targeting") not in {"inside", "outside", "random"}:
        raise ValueError("Unknown targeting category")
    gt = _finite_number(policy.get("credibility"), "credibility")
    if gt not in (0.2, 0.6, 1.0):
        raise ValueError("Credibility must be one of .2/.6/1.0 in this fixed study")
    recipients = policy.get("recipients")
    if not isinstance(recipients, list) or any(not isinstance(x, str) for x in recipients):
        raise ValueError("recipients must be a JSON list of anonymous IDs")
    if len(recipients) != budget or len(set(recipients)) != budget:
        raise ValueError("Direct recipients must be exactly the fixed unique budget")
    if any(aid not in state["agents"] for aid in recipients):
        raise ValueError("Unknown direct recipient")
    if policy["targeting"] != "random" and any(
            state["agents"][aid]["group"] != policy["targeting"] for aid in recipients):
        raise ValueError("Direct recipient outside the selected target group")


def branch(parent_state: dict, policy: dict) -> dict:
    if parent_state.get("policy") is not None:
        raise ValueError("Policy branches must start from an untreated parent state")
    _validate_policy(parent_state, policy, parent_state["direct_budget"])
    if parent_state["round"] != policy["government_round"] - 1:
        raise ValueError("Branch point must be the end of T_G-1")
    if parent_state["pbd"] is None:
        raise ValueError("The common pre-intervention PBd checkpoint must already exist")
    result = copy.deepcopy(parent_state)
    result["policy"] = copy.deepcopy(policy)
    result["risk_ids"] = sorted(aid for aid, a in result["agents"].items()
                                if a["belief_state"] == "accept")
    result["first_rejections"] = {}
    return result


def is_read_eligible(post: dict, agent: dict, t: int, config: dict) -> bool:
    feed = config["feed"]
    age = t - post["created_round"]
    if post["visible_from"] > t or not 0 <= age < feed["post_ttl_rounds"]:
        return False
    seen = agent["seen_posts"].get(post["post_id"])
    if seen:
        if seen["count"] >= feed["max_reads_per_post"]:
            return False
        if t - seen["last_seen_round"] < feed["repeat_gap_rounds"]:
            return False
    return True


def _weighted_posts(candidates: list[dict], n: int, state: dict, aid: str,
                    t: int, channel: str, config: dict) -> list[dict]:
    half_life = _finite_number(config["feed"]["recency_half_life_rounds"], "half_life")
    if half_life <= 0:
        raise ValueError("Recency half life must be positive")
    scored = []
    for p in candidates:
        weight = 2 ** (-(t - p["created_round"]) / half_life)
        u = keyed_uniform(state["event_id"], state["seed"], t, aid, channel, p["post_id"])
        scored.append((-math.log(u) / weight, p["post_id"], p))
    return [p for _, _, p in sorted(scored, key=lambda x: (x[0], x[1]))[:n]]


def _social_config(config: dict | None) -> dict | None:
    social = (config or {}).get("social")
    if not social or not social.get("enabled", False):
        return None
    protocol = social.get("protocol", social.get("mode", "single_event_social_v1"))
    if protocol != "single_event_social_v1":
        raise ValueError("Unknown social interaction protocol")
    for key, maximum in (("thread_comment_slots", 2), ("thread_repost_slots", 1)):
        value = _integer(social.get(key, maximum), key)
        if value > maximum:
            raise ValueError(f"{key} cannot exceed {maximum} in single_event_social_v1")
    return social


def _post_relationship(state: dict, reader: dict, post: dict) -> tuple[str, str]:
    author = post["author_id"]
    if author == state["government_id"]:
        return "official", "non_peer"
    if author == state["source_id"]:
        return "source", "non_peer"
    peer = state["agents"].get(author)
    relation = "followed_peer" if author in reader["follows"] else "unfollowed_peer"
    group = ("same_group" if peer["group"] == reader["group"] else "cross_group") if peer else "non_peer"
    return relation, group


def _thread_feed(state: dict, agent: dict, chosen: list[dict], t: int,
                 config: dict, social: dict) -> list[dict]:
    """Read bounded public thread context from the same frozen post collection.

    Reading a root topic or receiving a reply to one's own post opens a thread.
    Merely sharing an event with an unseen post never makes that post visible.
    """
    aid = agent["agent_id"]
    topics = {item["post"]["content_id"] for item in chosen}
    own_posts = {pid for pid, p in state["posts"].items()
                 if p["author_id"] == aid and p["visible_from"] <= t}
    excluded = {item["post"]["post_id"] for item in chosen}
    follows = set(agent["follows"])
    selected = []
    for kind, maximum in (("comment", 2), ("repost", 1)):
        channel = f"thread_{kind}"
        n = social.get(f"{channel}_slots", maximum)
        candidates = [p for p in state["posts"].values()
                      if p["kind"] == kind and p["author_id"] != aid
                      and not p["direct_only"] and p["post_id"] not in excluded
                      and is_read_eligible(p, agent, t, config)
                      and (p["content_id"] in topics or p.get("parent_post_id") in own_posts)]
        for priority in (0, 1, 2):
            group = [p for p in candidates if
                     (0 if p.get("parent_post_id") in own_posts else
                      1 if p["author_id"] in follows else 2) == priority]
            picked = _weighted_posts(group, n, state, aid, t, channel, config)
            selected.extend({"post": p, "channel": channel} for p in picked)
            excluded.update(p["post_id"] for p in picked)
            n -= len(picked)
            if n == 0:
                break
    return selected


def build_feed(state: dict, agent_id: str, t: int, config: dict,
               direct_post: dict | None = None) -> tuple[list[dict], bool]:
    """Return slot-tagged posts without changing reading history or any state."""
    agent, cfg = state["agents"][agent_id], config["feed"]
    probability = _finite_number(cfg["recommendation_probability"], "recommendation_probability")
    if not 0 <= probability <= 1:
        raise ValueError("Recommendation slot probability must be within [0,1]")
    active = keyed_uniform(state["event_id"], state["seed"], t, agent_id, "active") < agent["activity"]
    chosen = []
    if active:
        ordinary = [p for p in state["posts"].values()
                    if not p["direct_only"] and p["author_id"] != agent_id
                    and is_read_eligible(p, agent, t, config)]
        follows = set(agent["follows"])
        selected = _weighted_posts([p for p in ordinary if p["author_id"] in follows],
                                   cfg["following_slots"], state, agent_id, t, "following", config)
        chosen.extend({"post": p, "channel": "following"} for p in selected)
        if keyed_uniform(state["event_id"], state["seed"], t, agent_id, "reco") < probability:
            excluded = {p["post_id"] for p in selected}
            reco = [p for p in ordinary if p["author_id"] not in follows and p["post_id"] not in excluded]
            selected = _weighted_posts(reco, cfg["recommendation_slots"], state, agent_id, t,
                                       "recommendation", config)
            chosen.extend({"post": p, "channel": "recommendation"} for p in selected)
    if direct_post is not None:
        if cfg["direct_extra_slots"] != 1:
            raise ValueError("The fixed study requires exactly one extra direct slot")
        if not is_read_eligible(direct_post, agent, t, config):
            raise ValueError("An official direct delivery is unexpectedly unreadable")
        chosen.append({"post": direct_post, "channel": "government_direct"})
    social = _social_config(config)
    if social is not None and (active or direct_post is not None):
        chosen.extend(_thread_feed(state, agent, chosen, t, config, social))
    if len({x["post"]["post_id"] for x in chosen}) != len(chosen):
        raise AssertionError("The same post was assigned to multiple slots")
    return chosen, active


def _visible_post(post: dict) -> dict:
    # No internal 'rumor_original' label, content_id, truth label or complete event.
    keys = ("post_id", "author_id", "created_round", "text", "quoted_context",
            "root_text", "root_evidence", "root_source_id", "root_source_profile",
            "source_cue", "public_stance")
    return copy.deepcopy({key: post[key] for key in keys})


def _make_view(state: dict, agent: dict, feed: list[dict], t: int,
               config: dict | None = None) -> dict:
    if not feed:
        raise ValueError("Never ask about an unexposed claim using an empty feed")
    if any(item["post"]["claim_id"] != state["claim_id"] for item in feed):
        raise ValueError("This single-event study cannot silently label unrelated posts as its claim")
    profile = {k: copy.deepcopy(agent[k]) for k in (
        "prior_government_trust", "sharing_style", "correction_share_willingness")}
    profile["observed_profile"] = copy.deepcopy(agent.get("observed_profile", {}))
    view = {
        "profile": profile, "agent_id": agent["agent_id"], "round": t,
        "original_claim": state["original_claim"],
        "previous_belief_score": agent["belief_score"],
        "previous_belief_state": agent["belief_state"],
        "memory": copy.deepcopy(agent["memory"]),
        "visible_posts": [_visible_post(x["post"]) for x in feed],
        "eligible_repost_post_ids": [x["post"]["post_id"] for x in feed
                                     if x["post"]["content_id"] not in agent["reposted_content_ids"]],
    }
    if agent["first_exposure_round"] is None:
        view["prior_acceptance"] = agent["prior_acceptance"]
    if _social_config(config) is not None:
        if "empirical_behavior" in agent:
            behavior = agent["empirical_behavior"]
            if not isinstance(behavior, dict):
                raise ValueError("empirical_behavior must be a sanitized, text-free statistical object")
            _canonical(behavior)
            view["profile"]["empirical_behavior"] = copy.deepcopy(behavior)
        latest_by_author = {}
        latest_comment_stance_by_author = {}
        for visible, item in zip(view["visible_posts"], feed):
            post = item["post"]
            relation, group_relation = _post_relationship(state, agent, post)
            public_kind = {"rumor_original": "source_post", "correction_original": "official_post"}.get(
                post["kind"], post["kind"])
            visible.update(relationship=relation, author_group_relation=group_relation,
                           exposure_channel=item["channel"], parent_post_id=post.get("parent_post_id"),
                           kind=public_kind)
            previous = latest_by_author.get(post["author_id"])
            if previous is None or (post["created_round"], post["post_id"]) > (
                    previous["created_round"], previous["post_id"]):
                latest_by_author[post["author_id"]] = visible
            # A plain repost exposes its quoted content, not a new public stance
            # by the reposter. Only an explicitly expressed comment is counted.
            if post["kind"] == "comment" and post["public_stance"] in {"support", "oppose", "uncertain"}:
                previous_comment = latest_comment_stance_by_author.get(post["author_id"])
                if previous_comment is None or (post["created_round"], post["post_id"]) > (
                        previous_comment["created_round"], previous_comment["post_id"]):
                    latest_comment_stance_by_author[post["author_id"]] = visible
        counts = {stance: sum(p["public_stance"] == stance for p in latest_comment_stance_by_author.values())
                  for stance in ("support", "oppose", "uncertain")}
        view["social_observation"] = {
            "scope": "current_round_visible_posts_only",
            "stance_basis": "latest_explicit_stance_comment_per_distinct_visible_author",
            "unique_visible_author_count": len(latest_by_author),
            "public_stance_author_counts": counts,
            "followed_author_count": sum(p["relationship"] == "followed_peer" for p in latest_by_author.values()),
            "same_group_author_count": sum(p["author_group_relation"] == "same_group" for p in latest_by_author.values()),
            "cross_group_author_count": sum(p["author_group_relation"] == "cross_group" for p in latest_by_author.values()),
            "interpretation": "Only the public expressions you saw this round, not network-wide opinion or anyone's private belief.",
        }
    return view


def validate_decision(decision: dict, view: dict, config: dict) -> dict:
    if not isinstance(decision, dict) or set(decision) != DECISION_FIELDS:
        raise ValueError("Decision must have exactly the six specified fields")
    belief_class(decision["belief_score"], config)
    if decision["belief_score"] is None:
        raise ValueError("An exposed agent must supply an integer belief_score")
    action, stance, target = decision["action"], decision["public_stance"], decision["target_post_id"]
    if not isinstance(action, str) or action not in {"silent", "comment", "repost"}:
        raise ValueError("Invalid action")
    for field, limit_field in (("comment", "comment_max_characters"), ("reason", "reason_max_characters")):
        if not isinstance(decision[field], str) or len(decision[field]) > config["llm"][limit_field]:
            raise ValueError(f"Invalid {field} text or length")
    if not decision["reason"].strip():
        raise ValueError("A short nonempty reason is required")
    if action == "silent":
        if target is not None or stance != "none" or decision["comment"] != "":
            raise ValueError("Silent requires null target, stance='none', and empty comment")
    else:
        visible = {p["post_id"] for p in view["visible_posts"]}
        if not isinstance(target, str) or target not in visible:
            raise ValueError("An action target must be visible in the current round")
        if not isinstance(stance, str) or stance not in {"support", "oppose", "uncertain"}:
            raise ValueError("Public stance must evaluate the original claim")
        if action == "comment" and not decision["comment"].strip():
            raise ValueError("A comment action requires nonempty public text")
        if action == "repost":
            if target not in view["eligible_repost_post_ids"]:
                raise ValueError("This content lineage has already been reposted")
            if decision["comment"] != "":
                raise ValueError("A plain repost cannot add comment text")
    return copy.deepcopy(decision)


def _official_post(event: dict, policy: dict) -> dict:
    if not isinstance(event.get("correction_text"), str) or not event["correction_text"].strip():
        raise ValueError("Government intervention requires a nonempty correction_text")
    if not isinstance(event.get("evidence_text"), str):
        raise ValueError("evidence_text must be a string; empty is allowed for the explicitly scripted experiment")
    tg, gt = policy["government_round"], policy["credibility"]
    correct = {0.2: 2, 0.6: 6, 1.0: 10}[float(gt)]
    source = event.get("government_id", "GOV")
    return {
        "post_id": f"{event['event_id']}:government:{tg}", "parent_post_id": None,
        "claim_id": event["claim_id"], "content_id": f"{event['event_id']}:correction_origin",
        "author_id": source, "kind": "correction_original", "created_round": tg,
        "visible_from": tg, "text": event["correction_text"], "quoted_context": None,
        "root_text": event["correction_text"], "root_evidence": event["evidence_text"],
        "root_source_id": source,
        "root_source_profile": {},
        "material_origin": event.get("correction_origin", "unspecified"),
        "source_cue": "该账号为当地官方信息发布账号。平台展示的既往独立核验记录为："
                      f"最近10条可核验信息中，{correct}条被核验与事实一致。",
        "public_stance": None, "direct_only": True,
    }


def _user_post(state: dict, agent_id: str, decision: dict, parent: dict, t: int,
               config: dict | None = None) -> dict:
    public_stance = decision["public_stance"]
    if decision["action"] == "repost" and _social_config(config) is not None:
        public_stance = None
    return {
        "post_id": f"{state['event_id']}:user:{t}:{agent_id}",
        "parent_post_id": parent["post_id"], "claim_id": parent["claim_id"],
        "content_id": parent["content_id"], "author_id": agent_id,
        "kind": decision["action"], "created_round": t, "visible_from": t + 1,
        "text": decision["comment"] if decision["action"] == "comment" else parent["text"],
        "quoted_context": {"post_id": parent["post_id"], "author_id": parent["author_id"],
                           "text": parent["text"]},
        "root_text": parent["root_text"], "root_evidence": parent["root_evidence"],
        "root_source_id": parent["root_source_id"], "source_cue": parent["source_cue"],
        "root_source_profile": copy.deepcopy(parent["root_source_profile"]),
        "material_origin": parent.get("material_origin"),
        "public_stance": public_stance, "direct_only": False,
    }


def _round_metric(state: dict, t: int, exposures: list, decisions: list) -> dict:
    metric = {"round": t, "accept_count": 0, "accept_rate": 0.0,
              "exposures_following": 0, "exposures_recommendation": 0,
              "exposures_government_direct": 0, "comments": 0, "reposts": 0,
              "decisions": len(decisions),
              "exposures_same_group": 0, "exposures_cross_group": 0,
              "exposures_non_peer": 0, "exposures_government_indirect": 0,
              "exposures_by_channel": {channel: 0 for channel in EXPOSURE_CHANNELS}}
    for channel in EXPOSURE_CHANNELS:
        metric.setdefault(f"exposures_{channel}", 0)
    for belief in ("reject", "uncertain", "unaware"):
        metric[f"{belief}_count"] = 0
    for group in ("inside", "outside"):
        users = [a for a in state["agents"].values() if a["group"] == group]
        n_accept = sum(a["belief_state"] == "accept" for a in users)
        metric[f"accept_count_{group}"] = n_accept
        metric[f"accept_rate_{group}"] = n_accept / len(users)
        metric[f"unaware_count_{group}"] = sum(a["belief_state"] == "unaware" for a in users)
        metric["accept_count"] += n_accept
        for belief in ("reject", "uncertain", "unaware"):
            count = sum(a["belief_state"] == belief for a in users)
            metric[f"{belief}_count_{group}"] = count
            metric[f"{belief}_count"] += count
    metric["accept_rate"] = metric["accept_count"] / len(state["agents"])
    for row in exposures:
        channel = row["channel"]
        metric[f"exposures_{channel}"] = metric.get(f"exposures_{channel}", 0) + 1
        metric["exposures_by_channel"][channel] = metric["exposures_by_channel"].get(channel, 0) + 1
        group_relation = row.get("author_group_relation", "non_peer")
        metric[f"exposures_{group_relation}"] += 1
        if row.get("root_source_id") == state["government_id"] and channel != "government_direct":
            metric["exposures_government_indirect"] += 1
    for row in decisions:
        action = row["decision"]["action"]
        if action in ("comment", "repost"):
            metric["comments" if action == "comment" else "reposts"] += 1
    return metric


def step(state: dict, config: dict, event: dict,
         decide: Callable[[dict, str], dict]) -> dict:
    """Commit one synchronous round iff every required decision is valid.

    All views are frozen before any injected decision call. A raised exception is
    intentionally propagated; the runner should audit/retry/resume without using a
    partially committed state. Decision retries themselves belong in the provider.
    """
    t = state["round"] + 1
    if t > config["time"]["last_round"]:
        raise ValueError("Cannot advance past the configured common endpoint")
    if event["event_id"] != state["event_id"] or event["original_claim"] != state["original_claim"]:
        raise ValueError("Event identity or focal claim changed during the run")
    if len(state["round_metrics"]) != state["round"]:
        raise ValueError("State must include the complete metrics prefix, one row per round")
    old = state
    new = copy.deepcopy(state)
    policy = state.get("policy")
    official = None
    if policy is not None:
        _validate_policy(state, policy, config["policy"]["direct_unique_users"])
        if policy["government_round"] + config["time"]["followup_max_elapsed"] > config["time"]["last_round"]:
            raise ValueError("The common endpoint is too early for the complete TBU window")
        if config["policy"]["direct_delivery_rounds"] != 1:
            raise ValueError("The fixed study permits one direct-delivery round")
        if t == policy["government_round"]:
            new["risk_ids"] = sorted(aid for aid, a in old["agents"].items()
                                      if a["belief_state"] == "accept")
            new["first_rejections"] = {}
            official = _official_post(event, policy)
            if official["post_id"] in new["posts"]:
                raise ValueError("Official correction was already published")
            new["posts"][official["post_id"]] = official

    inputs = []
    activity_by_agent = {}
    for aid in sorted(old["agents"]):
        direct = official if official is not None and aid in policy["recipients"] else None
        feed, active = build_feed(old, aid, t, config, direct)
        activity_by_agent[aid] = active
        if not feed:
            continue
        view = _make_view(old, old["agents"][aid], feed, t, config)
        identity = _canonical([old["event_id"], old["seed"], old["d_seed"], t, aid])
        inputs.append((aid, feed, view, identity))

    pending = []
    for aid, feed, view, identity in inputs:
        result = decide(copy.deepcopy(view), identity)
        if not isinstance(result, dict) or not isinstance(result.get("audit"), dict):
            raise ValueError("Decision provider must return {'decision': ..., 'audit': dict}")
        decision = validate_decision(result.get("decision"), view, config)
        _canonical(result["audit"])
        pending.append((aid, feed, view, identity, decision, copy.deepcopy(result["audit"])))

    # No external calls happen below this point. All changes affect only the copy.
    exposures, decisions, created_posts = [], [], []
    if official is not None:
        created_posts.append(copy.deepcopy(official))
    for aid, feed, view, identity, decision, audit in pending:
        agent = new["agents"][aid]
        agent["belief_score"] = decision["belief_score"]
        agent["belief_state"] = belief_class(decision["belief_score"], config)
        agent["last_action"] = decision["action"]
        if agent["first_exposure_round"] is None:
            agent["first_exposure_round"] = t
        for item in feed:
            post, channel = item["post"], item["channel"]
            previous = agent["seen_posts"].get(post["post_id"])
            count = 1 + (previous["count"] if previous else 0)
            relationship, group_relation = _post_relationship(old, old["agents"][aid], post)
            exposures.append({"round": t, "agent_id": aid, "group": agent["group"],
                "post_id": post["post_id"], "content_id": post["content_id"], "channel": channel,
                "author_id": post["author_id"], "kind": post["kind"],
                "relationship": relationship, "author_group_relation": group_relation,
                "parent_post_id": post.get("parent_post_id"), "public_stance": post["public_stance"],
                "root_source_id": post["root_source_id"],
                "reading_count": count, "previous_read_round": previous["last_seen_round"] if previous else None,
                "post_age": t - post["created_round"], "is_repeat": previous is not None})
            agent["seen_posts"][post["post_id"]] = {"count": count, "last_seen_round": t}
        if decision["action"] != "silent":
            parent = next(x["post"] for x in feed if x["post"]["post_id"] == decision["target_post_id"])
            post = _user_post(new, aid, decision, parent, t, config)
            if post["post_id"] in new["posts"]:
                raise AssertionError("Duplicate user post ID")
            new["posts"][post["post_id"]] = post
            created_posts.append(copy.deepcopy(post))
            if decision["action"] == "repost":
                agent["reposted_content_ids"] = sorted(agent["reposted_content_ids"] + [parent["content_id"]])
        memory = {"round": t, "visible_posts": copy.deepcopy(view["visible_posts"]),
                  "belief_score": decision["belief_score"], "action": decision["action"],
                  "target_post_id": decision["target_post_id"], "comment": decision["comment"],
                  "public_stance": decision["public_stance"], "reason": decision["reason"]}
        n_memory = _integer(config["feed"]["memory_decision_rounds"], "memory_decision_rounds", 1)
        agent["memory"] = (agent["memory"] + [memory])[-n_memory:]
        decisions.append({"round": t, "agent_id": aid, "call_identity": identity,
                          "view": copy.deepcopy(view), "decision": decision, "audit": audit})

    called = {aid for aid, *_ in pending}
    exposed_by_agent = {aid: [] for aid in new["agents"]}
    for exposure in exposures:
        exposed_by_agent[exposure["agent_id"]].append(exposure)
    panel = []
    for aid in sorted(new["agents"]):
        agent = new["agents"][aid]
        agent_exposures = exposed_by_agent[aid]
        panel.append({"round": t, "agent_id": aid, "group": agent["group"],
                      "score": agent["belief_score"], "state": agent["belief_state"],
                      "exposed": bool(agent_exposures), "action": agent["last_action"] if aid in called else "idle",
                      "naturally_active": activity_by_agent[aid], "called_llm": aid in called,
                      "n_feed_posts": len(agent_exposures),
                      "government_direct": any(x["channel"] == "government_direct" for x in agent_exposures)})
    new["round"] = t
    metric = _round_metric(new, t, exposures, decisions)
    new["round_metrics"].append(metric)
    if t == config["time"]["pb_checkpoint_round"]:
        if new["pbd"] is not None:
            raise ValueError("PBd checkpoint cannot be overwritten")
        new["pbd"] = metric["accept_rate_inside"] - metric["accept_rate_outside"]
    if policy is not None:
        tg = policy["government_round"]
        if tg <= t <= tg + config["time"]["followup_max_elapsed"]:
            for aid in new["risk_ids"]:
                if aid not in new["first_rejections"] and new["agents"][aid]["belief_state"] == "reject":
                    new["first_rejections"][aid] = t
    return {"state": new, "exposures": exposures, "decisions": decisions,
            "posts": created_posts, "states": panel}


def individual_tbu(state: dict, config: dict) -> list[dict]:
    if state.get("policy") is None:
        return []
    tg = state["policy"]["government_round"]
    W = config["time"]["followup_max_elapsed"]
    complete = state["round"] >= tg + W
    result = []
    for aid in sorted(state["risk_ids"]):
        first = state["first_rejections"].get(aid)
        if first is not None and not tg <= first <= min(state["round"], tg + W):
            raise ValueError("Stored first rejection is outside its valid TBU window")
        observed = first is not None
        result.append({"agent_id": aid, "group": state["agents"][aid]["group"],
                       "government_round": tg, "first_reject": first,
                       "event": 1 if observed else (0 if complete else None),
                       "duration": first - tg if observed else (W if complete else None),
                       "followup_complete": complete})
    return result


def summarize(state: dict, config: dict) -> dict:
    metric = state["round_metrics"][-1] if state["round_metrics"] else _round_metric(state, 0, [], [])
    individuals = individual_tbu(state, config)
    completed = [row["duration"] for row in individuals if row["event"] == 1]
    risk_n = len(individuals)
    policy = state.get("policy")
    full_followup = (policy is not None and state["round"] >=
                     policy["government_round"] + config["time"]["followup_max_elapsed"])
    channels = set(EXPOSURE_CHANNELS)
    for m in state["round_metrics"]:
        channels.update(m.get("exposures_by_channel", {}))
    return {
        "event_id": state["event_id"], "seed": state["seed"], "d_seed": state["d_seed"],
        "end_round": state["round"], "PBd": state["pbd"], "policy": copy.deepcopy(policy),
        "risk_n": risk_n, "updated_n": len(completed),
        "update_rate": len(completed) / risk_n if risk_n else None,
        "TBU_mean": sum(completed) / len(completed) if completed else None,
        "censored_n": risk_n - len(completed) if full_followup else None,
        "followup_complete": bool(full_followup),
        "RMST": sum(row["duration"] for row in individuals) / risk_n if full_followup and risk_n else None,
        "accept_rate_end": metric["accept_rate"],
        "accept_rate_end_inside": metric["accept_rate_inside"],
        "accept_rate_end_outside": metric["accept_rate_outside"],
        "accept_rate_end_by_group": {g: metric[f"accept_rate_{g}"] for g in ("inside", "outside")},
        "cumulative_acceptance_1_to_end": sum(m["accept_rate"] for m in state["round_metrics"]),
        "cumulative_acceptance_by_group": {g: sum(m[f"accept_rate_{g}"] for m in state["round_metrics"])
                                            for g in ("inside", "outside")},
        "exposure_totals": {channel: sum(m.get(f"exposures_{channel}", 0) for m in state["round_metrics"])
                             for channel in sorted(channels)},
        "social_exposure_totals": {name: sum(m.get(f"exposures_{name}", 0) for m in state["round_metrics"])
                                   for name in ("same_group", "cross_group", "non_peer", "government_indirect")},
        "comments": sum(m["comments"] for m in state["round_metrics"]),
        "reposts": sum(m["reposts"] for m in state["round_metrics"]),
        "decision_calls": sum(m["decisions"] for m in state["round_metrics"]),
    }
