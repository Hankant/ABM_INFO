"""V4 native SocioVerse2 providers. Scientific inputs: the user's four V4 files.

The rule contract is explicitly ENGINEERING ONLY until confirmed. No LLM fallback.
Core is reused unchanged; environment owns memories so action replay restores them.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import tempfile
import time
from collections import Counter
from pathlib import Path
from statistics import mean

import numpy as np
from socioverse.abc import PopulationProvider, EnvironmentProvider, DecisionModel, MetricCollector
from socioverse.engine import register
from socioverse.schemas import Persona, Observation, Action


def retry_file(operation):
    for attempt in range(6):
        try:
            return operation()
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(0.2 * (attempt + 1))


def read_json(path):
    return retry_file(lambda: json.loads(Path(path).read_text(encoding="utf-8")))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace only after the complete JSON is flushed: interruption cannot leave half a ledger.
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        retry_file(lambda: os.replace(temporary, path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: r["agent_id"])
    assert len(rows) == 582 and len({r["agent_id"] for r in rows}) == 582
    assert Counter(r["decision_mode"] for r in rows) == {"llm": 305, "rule": 277}
    assert Counter(r["group"] for r in rows) == {"inside": 82, "outside": 500}
    return rows


def make_network(rows):
    rng = np.random.Generator(np.random.PCG64(20261018))
    edges = []
    for r in rows:
        for same, count in ((True, 8), (False, 2)):
            candidates = [p["agent_id"] for p in rows if p != r and (p["group"] == r["group"]) == same]
            edges.extend((r["agent_id"], str(j)) for j in rng.choice(candidates, count, replace=False))
        if r["group"] == "inside":
            edges.append((r["agent_id"], "SOURCE"))
    return edges


def targets(rows, strategy="inside"):
    pool = [r["agent_id"] for r in rows if strategy == "random" or r["group"] == strategy]
    rng = np.random.Generator(np.random.PCG64(20261019))
    return sorted(map(str, rng.choice(pool, min(40, len(pool)), replace=False)))


@register("population", "rumor_v5_dropout.population")
class V4Population(PopulationProvider):
    def __init__(self, bundle):
        self.bundle = bundle
        self.rows = load_rows(bundle.provider_args["roster_csv"])
        self.edges = bundle.interaction.edges

    def build(self, seed):
        return [Persona(agent_id=r["agent_id"], group_key=r["group"], attributes=r,
                        init_state={"current_belief": "unjudged"}) for r in self.rows]

    def neighbors(self, aid):
        return [b for a, b in self.edges if a == aid]


@register("environment", "rumor_v5_dropout.environment")
class V4Environment(EnvironmentProvider):
    def __init__(self, bundle):
        self.bundle = bundle
        self.cfg = bundle.provider_args
        self.rows = load_rows(self.cfg["roster_csv"])
        self.by_id = {r["agent_id"]: r for r in self.rows}
        self.following = {a: set() for a in self.by_id}
        for a, b in self.cfg["edges"]:
            self.following[a].add(b)
        self.direct_targets = self.cfg["direct_targets"]

    def reset(self, seed):
        self.t = 0
        self.offline = {}
        self.beliefs = {a: "unjudged" for a in self.by_id}
        self.seen = {a: set() for a in self.by_id}
        self.reposted = {a: set() for a in self.by_id}
        self.memory = {a: [] for a in self.by_id}
        self.exposure_history = {a: {} for a in self.by_id}
        self.rule_corrected = set()
        self.last_updated = {a: None for a in self.by_id}
        self.posts = {}
        self.comments = {}
        self.applied = {}
        self.cohort = set()
        self.transitions = {}
        self._publish_root("P001", "SOURCE", 0, self.cfg["rumor_text"])

    def _publish_root(self, cid, author, tick, text):
        self.posts[cid] = dict(content_id=cid, root_content_id=cid, author_id=author,
                               original_author_id=author, published_tick=tick,
                               available_tick=1 if tick == 0 else tick,
                               text=text, repost_text="")

    def advance_to(self, t):
        self.t = t
        if t == 20 and "G001" not in self.posts:
            self._publish_root("G001", "GOVERNMENT", 20, self.cfg["correction_text"])
        return [e for e in self.bundle.scheduled_events if e.at_step == t]

    def observe_batch(self, agent_ids, t, round_idx=0):
        out = []
        for aid in agent_ids:
            eligible = [p for p in self.posts.values()
                        if p["available_tick"] <= t and 0 <= t - p["published_tick"] < 40
                        and p["content_id"] not in self.seen[aid]
                        and p["author_id"] in self.following[aid]]
            eligible.sort(key=lambda p: (-p["published_tick"], p["content_id"]))
            direct = t == 20 and aid in self.direct_targets
            chosen = ([self.posts["G001"]] + [p for p in eligible if p["content_id"] != "G001"]) if direct else eligible
            feed = []
            for p in ([] if aid in self.offline else chosen[:5]):
                post = copy.deepcopy(p)
                cs = [c for c in self.comments.values() if c["target_content_id"] == p["content_id"] and c["published_tick"] < t]
                post["comments"] = sorted(cs, key=lambda c: (-c["published_tick"], c["comment_id"]))[:2]
                post["delivery"] = "direct_government" if direct and p["content_id"] == "G001" else "followee"
                post["can_repost"] = p["root_content_id"] not in self.reposted[aid]
                post["block_reason"] = None if post["can_repost"] else "duplicate_root_repost"
                feed.append(post)
            out.append(Observation(agent_id=aid, step=t,
                local_physical={"persona": self.by_id[aid], "current_belief": self.beliefs[aid], "technical_offline": aid in self.offline,
                                "exposure_history": copy.deepcopy(self.exposure_history[aid]), "rule_corrected": aid in self.rule_corrected,
                                "memory": copy.deepcopy(self.memory[aid]), "already_reposted": sorted(self.reposted[aid])},
                local_information={"posts": feed}))
        return out

    def apply(self, actions):
        # Validate the entire batch BEFORE committing any agent (atomic decision stage).
        prepared = []
        for a in actions:
            key = (a.step, a.agent_id)
            signature = digest(a.payload)
            if key in self.applied:
                if self.applied[key] != signature:
                    raise ValueError("conflicting action for an already committed agent/tick")
                continue
            if a.payload.get("decision_status") == "technical_dropout":
                if a.kind != "idle" or a.step != self.t or a.agent_id not in self.by_id or self.by_id[a.agent_id]["decision_mode"] != "llm":
                    raise ValueError("invalid technical dropout")
            if a.kind == "idle":
                prepared.append((a, signature, None))
                continue
            if a.step != self.t or a.agent_id not in self.by_id:
                raise ValueError("action step/agent mismatch")
            valid_feed = {p["content_id"]: p for p in self.observe(a.agent_id, a.step).local_information["posts"]}
            feed = a.payload["observed_posts"]
            for p in feed:
                original = valid_feed.get(p["content_id"])
                if original is None or any(p.get(k) != v for k, v in original.items() if k != "comments"):
                    raise ValueError("observation contains invisible/altered content")
                if any(c not in original["comments"] for c in p["comments"]):
                    raise ValueError("observation contains invisible comment")
            used_memory = [m for m in self.memory[a.agent_id] if m["tick"] in a.payload["used_memory_ticks"]]
            answer = normalize_answer(a.payload["answer"], feed, used_memory, self.reposted[a.agent_id])
            prepared.append((a, signature, answer))
        for a, signature, answer in prepared:
            aid = a.agent_id
            if a.payload.get("decision_status") == "technical_dropout":
                self.offline.setdefault(aid, {"tick": a.step, "reason": a.payload["failure_reason"]})
            if answer is not None:
                feed = a.payload["observed_posts"]
                before = self.beliefs[aid]
                self.beliefs[aid] = answer["belief"]
                self.last_updated[aid] = a.step
                for p in feed:
                    self.exposure_history[aid].setdefault(p["content_id"], {
                        "root_content_id": p["root_content_id"], "author_id": p["author_id"], "tick": a.step})
                if any(d.get("name") == "GT" and d.get("passed") for d in a.payload.get("draws", [])):
                    self.rule_corrected.add(aid)
                self.seen[aid].update(p["content_id"] for p in feed)
                if answer["comment"]["enabled"]:
                    cid = f"C{a.step:02d}-{aid}"
                    # V4 has no comment target field: explicitly target first shown post.
                    self.comments[cid] = dict(comment_id=cid, author_id=aid, published_tick=a.step,
                        target_content_id=feed[0]["content_id"], text=answer["comment"]["text"])
                if answer["repost"]["enabled"]:
                    target = self.posts[answer["repost"]["target_content_id"]]
                    cid = f"RP{a.step:02d}-{aid}"
                    self.posts[cid] = dict(content_id=cid, root_content_id=target["root_content_id"],
                        author_id=aid, original_author_id=target["original_author_id"],
                        published_tick=a.step, available_tick=a.step + 1, text=target["text"],
                        repost_text=answer["repost"]["text"], parent_content_id=target["content_id"])
                    self.reposted[aid].add(target["root_content_id"])
                self.memory[aid].append(dict(agent_id=aid, tick=a.step, observed_posts=copy.deepcopy(feed),
                    belief_before=before, belief_after=answer["belief"],
                    comment=answer["comment"], repost=answer["repost"]))
                self.memory[aid] = self.memory[aid][-5:]
                if aid in self.cohort and a.step >= 20 and answer["belief"] == "reject":
                    self.transitions.setdefault(aid, a.step)
            self.applied[(a.step, aid)] = signature
        if self.t == 19:
            self.cohort = {a for a, b in self.beliefs.items() if b == "believe"}

    def agent_state(self, aid):
        return dict(exposure_summary=exposure_summary(self.exposure_history[aid], [], self.t), current_belief=self.beliefs[aid], last_updated_tick=self.last_updated[aid],
                    decision_mode=self.by_id[aid]["decision_mode"], group=self.by_id[aid]["group"],
                    memory_count=len(self.memory[aid]), seen_count=len(self.seen[aid]),
                    reposted_roots=sorted(self.reposted[aid]))

    def snapshot(self):
        return dict(technical_offline=self.offline, exposure_history=self.exposure_history, rule_corrected=sorted(self.rule_corrected), tick=self.t, beliefs=self.beliefs, memory=self.memory,
                    posts=self.posts, comments=self.comments,
                    seen={a: sorted(x) for a, x in self.seen.items()},
                    reposted={a: sorted(x) for a, x in self.reposted.items()},
                    cohort=sorted(self.cohort), transitions=self.transitions)


def exposure_summary(history, feed, tick):
    events = copy.deepcopy(history)
    for p in feed:
        events.setdefault(p["content_id"], {"root_content_id": p["root_content_id"],
            "author_id": p["author_id"], "tick": tick})
    result = {}
    for e in events.values():
        root = e["root_content_id"]
        row = result.setdefault(root, {"post_count": 0, "authors": set(), "ticks": set()})
        row["post_count"] += 1
        row["authors"].add(e["author_id"])
        row["ticks"].add(e["tick"])
    return {root: {"observed_post_count": r["post_count"], "distinct_author_count": len(r["authors"]),
        "exposure_tick_count": len(r["ticks"]), "first_seen_tick": min(r["ticks"]),
        "last_seen_tick": max(r["ticks"])} for root, r in sorted(result.items())}


def allowed_evidence_ids(feed, memories):
    ids = set()
    for p in feed + [p for m in memories for p in m["observed_posts"]]:
        ids.add(p["content_id"])
        ids.update(c["comment_id"] for c in p.get("comments", []))
        # Provider text holds original/root text, not the repost caption.
        if isinstance(p.get("text"), str) and p["text"].strip() and p.get("root_content_id"):
            ids.add(p["root_content_id"])
    return ids


def normalize_answer(raw, feed, memories, already_reposted):
    if not feed:
        raise ValueError("no content must use idle")
    answer = copy.deepcopy(raw)
    repairs = list(answer.get("format_repairs", []))
    # Only the explicit false shorthand is unambiguous. Never infer a true action.
    if answer.get("repost") is False and answer.get("target_content_id") is None and answer.get("text", "") == "":
        answer["repost"] = {"enabled": False, "target_content_id": None, "text": ""}
        answer.pop("target_content_id", None)
        answer.pop("text", None)
        repairs.append("explicit_false_repost_to_disabled_object")
    if repairs:
        answer["format_repairs"] = repairs
    if answer.get("belief") not in ("believe", "uncertain", "reject", "unjudged"):
        raise ValueError("invalid belief")
    for field in ("comment", "repost"):
        item = answer.get(field)
        if not isinstance(item, dict) or type(item.get("enabled")) is not bool or not isinstance(item.get("text"), str):
            raise ValueError("invalid action schema")
        if item["enabled"] and field == "comment" and not item["text"].strip():
            raise ValueError("empty enabled comment")
    visible_ids = allowed_evidence_ids(feed, memories)
    evidence = answer.get("evidence_ids")
    if not isinstance(evidence, list) or any(not isinstance(i, str) or i not in visible_ids for i in evidence):
        raise ValueError("invalid/invisible evidence")
    answer["decision_status"] = "applied"
    if answer["repost"]["enabled"]:
        target = next((p for p in feed if p["content_id"] == answer["repost"].get("target_content_id")), None)
        if target is None:
            raise ValueError("invisible repost target")
        if target["root_content_id"] in already_reposted:
            answer["repost"] = {"enabled": False, "target_content_id": None, "text": ""}
            answer["decision_status"] = "partially_applied"
            answer["repost_rejection_reason"] = "duplicate_root_repost"
    for field in ("comment", "repost"):
        if not answer[field]["enabled"]:
            answer[field]["text"] = ""
    if not answer["repost"]["enabled"]:
        answer["repost"]["target_content_id"] = None
    return answer


def empty_answer(belief):
    return dict(belief=belief, comment={"enabled": False, "text": ""},
                repost={"enabled": False, "target_content_id": None, "text": ""}, evidence_ids=[])


@register("decision", "rumor_v5_dropout.decision")
class V4Decision(DecisionModel):
    def __init__(self, config, prompt_file, audit_dir, llm_kind="scripted"):
        self.cfg = config
        self.mode = llm_kind
        if llm_kind not in ("scripted", "openai"):
            raise ValueError("unsupported llm_kind")
        self.template = Path(prompt_file).read_text(encoding="utf-8").split("```text", 1)[1].split("```", 1)[0].strip()
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        if llm_kind == "openai":
            from llm_client import LiveClient
            self.client = LiveClient(config, self.audit_dir)

    def _rule(self, ob):
        feed = ob.local_information["posts"]
        state = ob.local_physical["current_belief"]
        answer = empty_answer(state)
        draws = []
        # Per-agent/tick stream: calls, retries and ordering cannot shift rule draws.
        rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
            [self.cfg["behavior_seed"], ob.step, int(ob.agent_id[1:])])) )
        def trial(name, probability):
            value = float(rng.random())
            draws.append(dict(name=name, probability=probability, uniform=value, passed=value < probability))
            return value < probability
        corrections = [p for p in feed if p["root_content_id"] == "G001"]
        pool = corrections or [p for p in feed if p["root_content_id"] == "P001"]
        if not pool:
            return answer, draws
        target = pool[0]
        answer["evidence_ids"] = [target["content_id"]]
        eligible = target["root_content_id"] not in ob.local_physical["already_reposted"]
        if corrections:
            if trial("GT", self.cfg["gt"]):
                answer["belief"] = "reject"
                repost = eligible and trial("RF", self.cfg["rf"])
            else:
                repost = False  # GT failure preserves even unjudged.
        else:
            inside = ob.local_physical["persona"]["group"] == "inside"
            pb, rc = {0.0: (.579, .579, .100, .100), .2: (.679, .479, .117, .083),
                      .4: (.779, .379, .135, .065)}[self.cfg["pbd"]][0 if inside else 1::2]
            if state in ("unjudged", "uncertain") or (state == "reject" and self.cfg.get("rule_reconsider_rumor", False) and not ob.local_physical.get("rule_corrected", False)):
                answer["belief"] = "believe" if trial("PB", pb) else "reject"
            repost = answer["belief"] == "believe" and eligible and trial("RC", rc)
        if repost:
            answer["repost"] = {"enabled": True, "target_content_id": target["content_id"], "text": ""}
        return answer, draws

    def _scripted(self, ob):
        # Fixed artificial replies exercise propagation, comments and duplicate rejection.
        feed = ob.local_information["posts"]
        target = next((p for p in feed if p["root_content_id"] == "G001"), feed[0])
        answer = empty_answer("reject" if target["root_content_id"] == "G001" else "believe")
        answer["repost"] = {"enabled": True, "target_content_id": target["content_id"], "text": "离线工程测试附言"}
        answer["comment"] = {"enabled": True, "text": "离线工程测试评论"}
        answer["evidence_ids"] = [target["content_id"]]
        return answer

    def decide_batch(self, obs, memories):
        actions = []
        # Sequential requests intentionally stay below V4's maximum concurrency of five.
        for ob in obs:
            feed = ob.local_information["posts"]
            if not feed:
                actions.append(Action(agent_id=ob.agent_id, step=ob.step, kind="idle", source="rule",
                                      payload={"decision_status": "idle", "dry_run": self.mode == "scripted"}))
                continue
            used = copy.deepcopy(feed)
            draws, meta = [], {}
            is_llm = ob.local_physical["persona"]["decision_mode"] == "llm"
            try:
                if not is_llm:
                    raw, draws = self._rule(ob)
                elif self.mode == "scripted":
                    raw = self._scripted(ob)
                else:
                    raw, used, meta = self.client.decide(ob, self.template)
                    if raw.get("belief") not in ("believe", "uncertain", "reject"):
                        raise ValueError("LLM must not return unjudged")
                used_ticks = meta.get("used_memory_ticks", [m["tick"] for m in ob.local_physical["memory"]])
                used_memory = [m for m in ob.local_physical["memory"] if m["tick"] in used_ticks]
                answer = normalize_answer(raw, used, used_memory, ob.local_physical["already_reposted"])
            except Exception as exc:
                from llm_client import AgentRequestFailure, FormatAttemptsExhausted
                if is_llm and isinstance(exc, (AgentRequestFailure, FormatAttemptsExhausted)):
                    payload = {"decision_status": "technical_dropout", "failure_reason": type(exc).__name__,
                               "dry_run": False}
                    dump(self.audit_dir / f"dropout-{ob.step:02d}-{ob.agent_id}.json", {
                        "agent_id": ob.agent_id, "tick": ob.step, **payload,
                        "note": "proposed dropout; effective only after complete tick commit"})
                    actions.append(Action(agent_id=ob.agent_id, step=ob.step, kind="idle", source="rule", payload=payload))
                    continue
                dump(self.audit_dir / f"failure-{ob.step:02d}-{ob.agent_id}.json", {
                    "agent_id": ob.agent_id, "tick": ob.step, "decision_status": "error",
                    "error_type": type(exc).__name__, "file_error": {"filename":getattr(exc,"filename",None), "filename2":getattr(exc,"filename2",None), "errno":getattr(exc,"errno",None), "winerror":getattr(exc,"winerror",None)}, "observed_posts": used,
                    "note": "batch not committed; see safe request diagnostics; no fallback"})
                raise
            payload = dict(answer=answer, raw_answer=raw, observed_posts=used, draws=draws,
                           dry_run=self.mode == "scripted", api=meta, used_memory_ticks=used_ticks,
                           decision_status=answer["decision_status"])
            actions.append(Action(agent_id=ob.agent_id, step=ob.step, kind="decide", payload=payload,
                                  source="llm" if is_llm and self.mode == "openai" else "rule"))
        return actions


@register("collector", "rumor_v5_dropout.metrics")
class V4Metrics(MetricCollector):
    def collect(self, env, actions, t):
        result = {}
        for mode in ("all", "llm", "rule"):
            counts = Counter(b for a, b in env.beliefs.items() if mode == "all" or env.by_id[a]["decision_mode"] == mode)
            for b in ("unjudged", "believe", "uncertain", "reject"):
                result[f"{mode}_{b}"] = counts[b]
        result.update(remaining_agents=len(env.by_id)-len(env.offline), technical_dropout_count=len(env.offline),
            remaining_llm=sum(r["decision_mode"] == "llm" and aid not in env.offline for aid,r in env.by_id.items()),
            remaining_rule=sum(r["decision_mode"] == "rule" and aid not in env.offline for aid,r in env.by_id.items()))
        for belief in ("unjudged", "believe", "uncertain", "reject"):
            result["remaining_"+belief] = sum(b == belief and aid not in env.offline for aid,b in env.beliefs.items())
        result.update(posts=len(env.posts), comments=len(env.comments),
            partial_actions=sum(a.payload.get("decision_status") == "partially_applied" for a in actions),
            idle_actions=sum(a.kind == "idle" for a in actions),
            tbu_cohort=len(env.cohort), tbu_completed=len(env.transitions),
            tbu_engineering=mean(v - 20 for v in env.transitions.values()) if env.transitions else None)
        return result

    def columns(self):
        return []
