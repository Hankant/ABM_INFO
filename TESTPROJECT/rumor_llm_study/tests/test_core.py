"""Offline tests of research-relevant core behavior; never call an HTTP provider."""
import copy
import json
import unittest
from collections import Counter

from rumor_sim import core


def fixture(full=False):
    cfg = {
        "population": {
            "n_inside": 82 if full else 4, "n_outside": 500 if full else 6,
            "activity_levels": [.1, .2, .3],
            "inside_counts": [27, 28, 27] if full else [1, 2, 1],
            "outside_counts": [167, 166, 167] if full else [2, 2, 2],
            "trust_levels": [.25, .5, .75], "sharing_styles": ["rare", "sometimes", "often"],
            "willing_inside": 49 if full else 2, "willing_outside": 300 if full else 4,
        },
        "prior": {"overall_mean": .579, "d_seed": .2, "within_group_offset": .05},
        "network": {"directed": True, "same_group_follows": 8 if full else 2,
                    "cross_group_follows": 2 if full else 1,
                    "inside_follow_source": True, "outside_follow_source": False,
                    "pre_follow_government": False},
        "feed": {"following_slots": 1, "recommendation_probability": .1,
                 "recommendation_slots": 1, "direct_extra_slots": 1,
                 "post_ttl_rounds": 40, "recency_half_life_rounds": 5,
                 "max_reads_per_post": 3, "repeat_gap_rounds": 5,
                 "max_reposts_per_content": 1, "new_user_post_delay": 1,
                 "memory_decision_rounds": 5},
        "time": {"source_round": 0, "first_decision_round": 1, "last_round": 80,
                 "pb_checkpoint_round": 5, "followup_max_elapsed": 30,
                 "followup_include_both_endpoints": True},
        "policy": {"direct_unique_users": 40 if full else 2, "direct_delivery_rounds": 1},
        "belief": {"accept_min": 60, "reject_max": 40},
        "llm": {"comment_max_characters": 80, "reason_max_characters": 40},
    }
    event = {"event_id": "fictional_event", "claim_id": "claim_001",
             "original_claim": "博物馆展览已永久取消。", "rumor_text": "听说博物馆展览已经永久取消。",
             "correction_text": "实验性说明：展览推迟，并非永久取消。",
             "evidence_text": "", "rumor_source_id": "SOURCE", "government_id": "GOV",
             "correction_origin": "experimental_script"}
    return cfg, event


class Recorder:
    def __init__(self, score=80, action="silent", government_score=None):
        self.score, self.action, self.government_score = score, action, government_score
        self.calls = []

    def __call__(self, view, call_identity):
        self.calls.append((copy.deepcopy(view), call_identity))
        score = self.score
        if self.government_score is not None and any(p["root_source_id"] == "GOV" for p in view["visible_posts"]):
            score = self.government_score
        action = self.action
        target = view["visible_posts"][0]["post_id"] if action != "silent" else None
        if action == "repost":
            eligible = view["eligible_repost_post_ids"]
            if eligible:
                target = eligible[0]
            else:
                action, target = "silent", None
        decision = {"belief_score": score, "action": action, "target_post_id": target,
                    "public_stance": "none" if action == "silent" else "uncertain",
                    "comment": "请继续核实这条消息。" if action == "comment" else "",
                    "reason": "仅为协议测试的固定回答。"}
        return {"decision": decision, "audit": {"provider": "offline-test-fixture"}}


def advance(state, cfg, event, end, provider):
    while state["round"] < end:
        state = core.step(state, cfg, event, provider)["state"]
    return state


def active_state(cfg, event, d=.2, seed=1):
    state = core.initialize(cfg, event, d, seed)
    for agent in state["agents"].values():
        agent["activity"] = 1.0
    return state


def policy(state, tg=10, targeting="inside", credibility=.6):
    return {"enabled": True, "government_round": tg, "targeting": targeting,
            "credibility": credibility,
            "recipients": core.select_recipients(state, targeting, tg, state["direct_budget"])}


class PopulationTests(unittest.TestCase):
    def test_full_population_marginals_and_weighted_prior_are_exact(self):
        cfg, event = fixture(full=True)
        state = core.initialize(cfg, event, .4, 1)
        self.assertEqual(len(state["agents"]), 582)
        for group, counts, n, willing in (("inside", [27, 28, 27], 82, 49),
                                           ("outside", [167, 166, 167], 500, 300)):
            users = [a for a in state["agents"].values() if a["group"] == group]
            self.assertEqual(len(users), n)
            for field, levels in (("activity", [.1, .2, .3]),
                                  ("prior_government_trust", [.25, .5, .75]),
                                  ("sharing_style", ["rare", "sometimes", "often"])):
                self.assertEqual(Counter(a[field] for a in users), dict(zip(levels, counts)))
            self.assertEqual(sum(a["correction_share_willingness"] == "willing" for a in users), willing)
            self.assertEqual(len({a["prior_acceptance"] for a in users}), 2)
            self.assertEqual(set(Counter(a["prior_acceptance"] for a in users).values()), {n // 2})
        self.assertAlmostEqual(sum(a["prior_acceptance"] for a in state["agents"].values()) / 582, .579)
        inside = [a["prior_acceptance"] for a in state["agents"].values() if a["group"] == "inside"]
        outside = [a["prior_acceptance"] for a in state["agents"].values() if a["group"] == "outside"]
        self.assertAlmostEqual(sum(inside) / 82 - sum(outside) / 500, .4)
        self.assertTrue(all(a["belief_score"] is None and a["belief_state"] == "unaware" for a in state["agents"].values()))
        self.assertEqual(json.loads(json.dumps(state)), state)

    def test_only_prior_changes_across_d_and_traits_are_separately_shuffled(self):
        cfg, event = fixture(full=True)
        a = core.initialize(cfg, event, 0, 3)
        b = core.initialize(cfg, event, .4, 3)
        for aid in a["agents"]:
            x, y = copy.deepcopy(a["agents"][aid]), copy.deepcopy(b["agents"][aid])
            self.assertNotEqual(x.pop("prior_acceptance"), y.pop("prior_acceptance"))
            self.assertEqual(x, y)
        activity = [x["activity"] for x in a["agents"].values()]
        trust_mapped = [{.25: .1, .5: .2, .75: .3}[x["prior_government_trust"]] for x in a["agents"].values()]
        self.assertNotEqual(activity, trust_mapped)

    def test_directed_network_degrees_and_no_self_or_duplicate_edges(self):
        cfg, event = fixture(full=True)
        state = core.initialize(cfg, event, .2, 1)
        for aid, a in state["agents"].items():
            self.assertNotIn(aid, a["follows"])
            self.assertEqual(len(a["follows"]), len(set(a["follows"])))
            regular = [state["agents"][x] for x in a["follows"] if x in state["agents"]]
            self.assertEqual(sum(x["group"] == a["group"] for x in regular), 8)
            self.assertEqual(sum(x["group"] != a["group"] for x in regular), 2)
            self.assertEqual("SOURCE" in a["follows"], a["group"] == "inside")
            self.assertNotIn("GOV", a["follows"])

    def test_observed_static_counts_do_not_override_designed_traits_or_leak_ids(self):
        cfg, event = fixture()
        event["source_profile"] = {"followers_count": 1200, "statuses_count": 50,
                                   "nickname": "NEVER_SEND_REAL_NAME"}
        state = active_state(cfg, event)
        changed = core.apply_profiles(state, [{"agent_id": "C001", "observed_profile": {
            "followers_count": 12, "following_count": 30, "statuses_count": 70},
            "provenance": "DONOR_HASH_ONLY_NOT_PROFILE"}])
        self.assertEqual(changed["agents"]["C001"]["prior_acceptance"], state["agents"]["C001"]["prior_acceptance"])
        self.assertEqual(changed["agents"]["C001"]["observed_profile"]["statuses_count"], 70)
        self.assertEqual(state["agents"]["C001"]["observed_profile"], {})
        rec = Recorder()
        core.step(changed, cfg, event, rec)
        text = json.dumps(rec.calls, ensure_ascii=False)
        self.assertNotIn("NEVER_SEND_REAL_NAME", text)
        self.assertNotIn("DONOR_HASH_ONLY_NOT_PROFILE", text)
        self.assertIn('"followers_count": 1200', text)
        self.assertIn('"statuses_count": 70', text)
        with self.assertRaises(ValueError):
            core.apply_profiles(state, [{"agent_id": "C001", "observed_profile": {"comment_text": "historic outcome"}}])


class ExposureTests(unittest.TestCase):
    def test_lifetime_read_limit_and_interval_boundaries(self):
        cfg, event = fixture()
        state = core.initialize(cfg, event, .2, 1)
        post = next(iter(state["posts"].values()))
        agent = state["agents"]["C001"]
        self.assertFalse(core.is_read_eligible(post, agent, 0, cfg))
        self.assertTrue(core.is_read_eligible(post, agent, 39, cfg))
        self.assertFalse(core.is_read_eligible(post, agent, 40, cfg))
        agent["seen_posts"][post["post_id"]] = {"count": 1, "last_seen_round": 8}
        self.assertFalse(core.is_read_eligible(post, agent, 12, cfg))
        self.assertTrue(core.is_read_eligible(post, agent, 13, cfg))
        agent["seen_posts"][post["post_id"]]["count"] = 3
        self.assertFalse(core.is_read_eligible(post, agent, 30, cfg))
        another = {**post, "post_id": "another-post-same-content"}
        self.assertTrue(core.is_read_eligible(another, agent, 30, cfg))

    def test_recommendation_is_one_slot_gate_not_a_per_post_probability(self):
        cfg, event = fixture()
        state = active_state(cfg, event)
        cfg["feed"]["recommendation_probability"] = 0
        items, _ = core.build_feed(state, "O001", 1, cfg)
        self.assertEqual(items, [])
        cfg["feed"]["recommendation_probability"] = 1
        source = next(iter(state["posts"].values()))
        for i in range(20):
            state["posts"][f"copy-{i}"] = {**source, "post_id": f"copy-{i}"}
        items, _ = core.build_feed(state, "O001", 1, cfg)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["channel"], "recommendation")
        cfg["feed"]["recommendation_probability"] = 0
        items, _ = core.build_feed(state, "C001", 1, cfg)
        self.assertEqual(len(items), 1)  # Following delivery does not use recommendation gate.

    def test_direct_extra_slot_and_inactive_recipients(self):
        cfg, event = fixture()
        state = active_state(cfg, event)
        cfg["feed"]["recommendation_probability"] = 1
        source = next(iter(state["posts"].values()))
        outside_author = next(aid for aid in state["agents"] if aid.startswith("O")
                              and aid not in state["agents"]["C001"]["follows"])
        state["posts"]["other"] = {**source, "post_id": "other", "author_id": outside_author}
        direct = {**source, "post_id": "gov", "author_id": "GOV", "direct_only": True,
                  "created_round": 1, "visible_from": 1}
        before, _ = core.build_feed(state, "C001", 1, cfg)
        with_direct, _ = core.build_feed(state, "C001", 1, cfg, direct)
        self.assertEqual(len(before), 2)
        self.assertEqual(len(with_direct), 3)
        self.assertEqual(with_direct[:2], before)
        state["agents"]["C001"]["activity"] = 0
        only_direct, active = core.build_feed(state, "C001", 1, cfg, direct)
        self.assertFalse(active)
        self.assertEqual([x["channel"] for x in only_direct], ["government_direct"])

    def test_government_original_never_enters_organic_pools(self):
        cfg, event = fixture()
        state = active_state(cfg, event)
        cfg["feed"]["recommendation_probability"] = 1
        source = next(iter(state["posts"].values()))
        state["posts"] = {"gov": {**source, "post_id": "gov", "author_id": "GOV", "direct_only": True}}
        state["agents"]["C001"]["follows"].append("GOV")
        self.assertEqual(core.build_feed(state, "C001", 1, cfg)[0], [])
        self.assertEqual(core.build_feed(state, "O001", 1, cfg)[0], [])


class SynchronousTests(unittest.TestCase):
    def test_unexposed_users_remain_unaware_and_future_correction_is_not_in_view(self):
        cfg, event = fixture()
        state = core.initialize(cfg, event, .4, 1)
        for agent in state["agents"].values():
            agent["activity"] = 0
        rec = Recorder()
        env = core.step(state, cfg, event, rec)
        self.assertEqual(rec.calls, [])
        self.assertEqual(len(env["states"]), 10)
        self.assertTrue(all(row["score"] is None and row["state"] == "unaware" for row in env["states"]))
        state = active_state(cfg, event)
        rec = Recorder()
        core.step(state, cfg, event, rec)
        encoded = json.dumps(rec.calls, ensure_ascii=False)
        self.assertNotIn(event["correction_text"], encoded)
        self.assertNotIn("最近10条", encoded)
        self.assertNotIn("rumor_original", encoded)
        self.assertTrue(all(view["original_claim"] == event["original_claim"] for view, _ in rec.calls))

    def test_new_posts_wait_until_next_round_and_parent_quotes_do_not_nest(self):
        cfg, event = fixture()
        cfg["feed"]["recommendation_probability"] = 1
        state = active_state(cfg, event)
        first = Recorder(action="comment")
        env = core.step(state, cfg, event, first)
        self.assertTrue(env["posts"])
        self.assertTrue(all(p["created_round"] == 1 and p["visible_from"] == 2 for p in env["posts"]))
        self.assertTrue(all(p["created_round"] == 0 for v, _ in first.calls for p in v["visible_posts"]))
        second = Recorder(action="comment")
        env2 = core.step(env["state"], cfg, event, second)
        self.assertTrue(any(p["created_round"] == 1 for v, _ in second.calls for p in v["visible_posts"]))
        for post in env2["posts"]:
            self.assertEqual(set(post["quoted_context"]), {"post_id", "author_id", "text"})
            self.assertEqual(post["content_id"], f"{event['event_id']}:rumor_origin")

    def test_failed_round_leaves_every_original_field_unchanged(self):
        cfg, event = fixture()
        state = active_state(cfg, event)
        original = copy.deepcopy(state)
        good = Recorder(action="comment")
        def fail_second(view, identity):
            if good.calls:
                raise RuntimeError("simulated provider failure")
            return good(view, identity)
        with self.assertRaises(RuntimeError):
            core.step(state, cfg, event, fail_second)
        self.assertEqual(state, original)
        self.assertEqual(state["round"], 0)
        self.assertEqual(len(state["posts"]), 1)

    def test_iteration_order_cannot_change_synchronous_results(self):
        cfg, event = fixture()
        state = active_state(cfg, event)
        reverse = copy.deepcopy(state)
        reverse["agents"] = dict(reversed(list(reverse["agents"].items())))
        a = core.step(state, cfg, event, Recorder(action="comment"))
        b = core.step(reverse, cfg, event, Recorder(action="comment"))
        self.assertEqual(a, b)

    def test_read_and_repost_counts_use_different_identifiers(self):
        cfg, event = fixture()
        cfg["feed"]["recommendation_probability"] = 1
        state = active_state(cfg, event)
        rec = Recorder(action="repost")
        env = core.step(state, cfg, event, rec)
        state = env["state"]
        self.assertTrue(all(len(a["reposted_content_ids"]) == 1 for a in state["agents"].values()))
        second = Recorder(action="repost")
        env2 = core.step(state, cfg, event, second)
        self.assertTrue(second.calls)
        self.assertTrue(all(not v["eligible_repost_post_ids"] for v, _ in second.calls))
        self.assertFalse(env2["posts"])
        self.assertTrue(any(len(a["seen_posts"]) > 1 for a in env2["state"]["agents"].values()))

    def test_first_prior_only_once_and_memory_keeps_five_decision_rounds(self):
        cfg, event = fixture()
        cfg["feed"]["recommendation_probability"] = 1
        state = active_state(cfg, event)
        rec = Recorder(action="comment")
        state = advance(state, cfg, event, 8, rec)
        calls = [v for v, _ in rec.calls if v["agent_id"] == "C001"]
        self.assertIn("prior_acceptance", calls[0])
        self.assertTrue(all("prior_acceptance" not in view for view in calls[1:]))
        self.assertEqual(len(state["agents"]["C001"]["memory"]), 5)
        self.assertEqual([m["round"] for m in state["agents"]["C001"]["memory"]], [4, 5, 6, 7, 8])
        for memory in state["agents"]["C001"]["memory"]:
            self.assertEqual(memory["comment"], "请继续核实这条消息。")
            self.assertEqual(memory["public_stance"], "uncertain")
            self.assertIn(memory["target_post_id"], [p["post_id"] for p in memory["visible_posts"]])
        self.assertEqual(calls[-1]["memory"][-1]["comment"], "请继续核实这条消息。")

    def test_checkpoint_uses_all_group_members_and_then_freezes(self):
        cfg, event = fixture()
        state = core.initialize(cfg, event, .4, 1)
        for a in state["agents"].values():
            a["activity"] = 0
        state = advance(state, cfg, event, 4, Recorder())
        state["agents"]["C001"].update(belief_score=70, belief_state="accept")
        for aid in ("O001", "O002", "O003"):
            state["agents"][aid].update(belief_score=80, belief_state="accept")
        state = core.step(state, cfg, event, Recorder())["state"]
        self.assertEqual(state["pbd"], 1/4 - 3/6)
        self.assertNotEqual(state["pbd"], state["d_seed"])
        state["agents"]["C001"].update(belief_score=0, belief_state="reject")
        state = core.step(state, cfg, event, Recorder())["state"]
        self.assertEqual(state["pbd"], -.25)


class BranchAndMetricTests(unittest.TestCase):
    def parent_at(self, tg):
        cfg, event = fixture()
        cfg["feed"]["recommendation_probability"] = 1
        parent = advance(active_state(cfg, event), cfg, event, tg - 1, Recorder())
        return cfg, event, parent

    def test_recipient_selection_is_fixed_unique_and_not_belief_filtered(self):
        cfg, event = fixture()
        state = core.initialize(cfg, event, .2, 1)
        a = core.select_recipients(state, "inside", 10, 2)
        changed = copy.deepcopy(state)
        for x in changed["agents"].values():
            x.update(belief_score=0, belief_state="reject", activity=0)
        self.assertEqual(a, core.select_recipients(changed, "inside", 10, 2))
        self.assertEqual(len(set(a)), 2)
        self.assertTrue(all(x.startswith("C") for x in a))
        with self.assertRaises(ValueError):
            core.select_recipients(state, "inside", 10, 5)

    def test_branch_deepcopy_keeps_prefix_and_resets_followup_state(self):
        cfg, event, parent = self.parent_at(10)
        parent_before = copy.deepcopy(parent)
        a = core.branch(parent, policy(parent, credibility=.2))
        b = core.branch(parent, policy(parent, credibility=1))
        self.assertEqual(a["risk_ids"], b["risk_ids"])
        self.assertEqual(a["policy"]["recipients"], b["policy"]["recipients"])
        self.assertEqual(a["round_metrics"], parent["round_metrics"])
        a["agents"]["C001"]["memory"].append({"fake": "one branch only"})
        self.assertEqual(parent, parent_before)
        self.assertNotEqual(a["agents"]["C001"]["memory"], b["agents"]["C001"]["memory"])
        self.assertEqual(a["first_rejections"], {})

    def test_government_direct_once_correction_lineage_retains_evidence_and_cue(self):
        cfg, event, parent = self.parent_at(10)
        for a in parent["agents"].values():
            a["activity"] = 0
        pol = policy(parent)
        state = core.branch(parent, pol)
        rec = Recorder(action="comment", government_score=20)
        env = core.step(state, cfg, event, rec)
        direct = [x for x in env["exposures"] if x["channel"] == "government_direct"]
        self.assertEqual({x["agent_id"] for x in direct}, set(pol["recipients"]))
        self.assertEqual(len(direct), 2)
        self.assertTrue(all(len(v["visible_posts"]) == 1 for v, _ in rec.calls))
        self.assertEqual(len(env["state"]["first_rejections"]), 2)
        for p in env["posts"]:
            self.assertEqual(p["root_text"], event["correction_text"])
            self.assertEqual(p["root_evidence"], "")
            self.assertIn("6条", p["source_cue"])
            self.assertEqual(p["material_origin"], "experimental_script")
        next_env = core.step(env["state"], cfg, event, Recorder())
        self.assertEqual(next_env["exposures"], [])
        self.assertTrue(all(p["direct_only"] == (p["kind"] == "correction_original") for p in env["posts"]))

    def test_tbu_zero_censoring_and_full_common_endpoint(self):
        cfg, event, parent = self.parent_at(10)
        for a in parent["agents"].values():
            a["activity"] = 0
        state = core.branch(parent, policy(parent))
        state = advance(state, cfg, event, 80, Recorder(government_score=20))
        rows = core.individual_tbu(state, cfg)
        observed = [x for x in rows if x["event"] == 1]
        censored = [x for x in rows if x["event"] == 0]
        self.assertEqual(len(observed), 2)
        self.assertTrue(all(x["duration"] == 0 for x in observed))
        self.assertTrue(all(x["duration"] == 30 for x in censored))
        summary = core.summarize(state, cfg)
        self.assertEqual(summary["TBU_mean"], 0)
        self.assertEqual(summary["risk_n"], 10)
        self.assertEqual(summary["update_rate"], .2)
        self.assertEqual(summary["end_round"], 80)
        self.assertEqual(len(state["round_metrics"]), 80)
        self.assertEqual(summary["cumulative_acceptance_1_to_end"], sum(m["accept_rate"] for m in state["round_metrics"]))

    def test_TG50_window_includes_round80_but_TG20_excludes_round51(self):
        for tg, reject_round, expected_event in ((50, 80, 1), (20, 50, 1), (20, 51, 0)):
            with self.subTest(tg=tg, reject_round=reject_round):
                cfg, event, parent = self.parent_at(tg)
                for a in parent["agents"].values():
                    a["activity"] = 0
                state = core.branch(parent, policy(parent, tg=tg))
                aid = state["policy"]["recipients"][0]
                provider = Recorder(score=80, government_score=80)
                state = advance(state, cfg, event, reject_round - 1, provider)
                # A valid controlled fixture for a round's starting state: insert a
                # newly visible user post and force this one recipient active.
                source = next(p for p in state["posts"].values() if p["kind"] == "rumor_original")
                fresh = {**source, "post_id": "fresh-at-test-boundary", "created_round": reject_round - 1,
                         "visible_from": reject_round, "author_id": "SOURCE", "direct_only": False}
                state["posts"][fresh["post_id"]] = fresh
                state["agents"][aid]["activity"] = 1
                state = core.step(state, cfg, event, Recorder(score=20))["state"]
                state["agents"][aid]["activity"] = 0
                state = advance(state, cfg, event, 80, Recorder())
                row = next(x for x in core.individual_tbu(state, cfg) if x["agent_id"] == aid)
                self.assertEqual(row["event"], expected_event)
                self.assertEqual(row["duration"], 30)

    def test_uncertain_intermediate_and_later_reacceptance_do_not_reset_first_event(self):
        cfg, event, parent = self.parent_at(10)
        for a in parent["agents"].values():
            a["activity"] = 0
        state = core.branch(parent, policy(parent))
        aid = state["policy"]["recipients"][0]
        state = core.step(state, cfg, event, Recorder(government_score=50))["state"]
        self.assertNotIn(aid, state["first_rejections"])
        state["agents"][aid].update(belief_score=20, belief_state="reject")
        state = core.step(state, cfg, event, Recorder())["state"]
        self.assertEqual(state["first_rejections"][aid], 11)
        state["agents"][aid].update(belief_score=90, belief_state="accept")
        state = core.step(state, cfg, event, Recorder())["state"]
        self.assertEqual(state["first_rejections"][aid], 11)

    def test_no_event_empty_risk_and_control_have_no_fake_TBU(self):
        cfg, event, parent = self.parent_at(10)
        for a in parent["agents"].values():
            a["activity"] = 0
        control = advance(copy.deepcopy(parent), cfg, event, 80, Recorder())
        self.assertIsNone(core.summarize(control, cfg)["TBU_mean"])
        self.assertEqual(core.individual_tbu(control, cfg), [])
        state = advance(core.branch(parent, policy(parent)), cfg, event, 80, Recorder(score=80))
        self.assertIsNone(core.summarize(state, cfg)["TBU_mean"])
        self.assertEqual(core.summarize(state, cfg)["update_rate"], 0)
        for a in parent["agents"].values():
            a.update(belief_score=20, belief_state="reject")
        empty = advance(core.branch(parent, policy(parent)), cfg, event, 80, Recorder(score=20))
        self.assertEqual(core.summarize(empty, cfg)["risk_n"], 0)
        self.assertIsNone(core.summarize(empty, cfg)["TBU_mean"])
        self.assertIsNone(core.summarize(empty, cfg)["update_rate"])

    def test_model_call_identity_does_not_include_policy_or_future_values(self):
        cfg, event, parent = self.parent_at(10)
        low, high = Recorder(), Recorder()
        core.step(core.branch(parent, policy(parent, credibility=.2)), cfg, event, low)
        core.step(core.branch(parent, policy(parent, credibility=1)), cfg, event, high)
        self.assertEqual([identity for _, identity in low.calls], [identity for _, identity in high.calls])
        self.assertEqual([json.loads(identity) for _, identity in low.calls],
                         [[event["event_id"], 1, .2, 10, view["agent_id"]] for view, _ in low.calls])


class ValidationTests(unittest.TestCase):
    def test_invalid_outputs_never_become_valid_states(self):
        cfg, event = fixture()
        state = active_state(cfg, event)
        recorder = Recorder()
        core.step(state, cfg, event, recorder)
        view = recorder.calls[0][0]
        base = recorder(view, "fixture")["decision"]
        for bad in ({**base, "belief_score": True}, {**base, "belief_score": 101},
                    {**base, "belief_score": "60"}, {**base, "belief_score": None},
                    {**base, "reason": ""}, {**base, "action": "comment", "target_post_id": "hidden",
                                            "public_stance": "support", "comment": "text"}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    core.validate_decision(bad, view, cfg)
        opposite_public = {**base, "action": "comment", "public_stance": "oppose",
                           "target_post_id": view["visible_posts"][0]["post_id"], "comment": "公开表达不同观点。"}
        self.assertEqual(core.validate_decision(opposite_public, view, cfg)["belief_score"], 80)


if __name__ == "__main__":
    unittest.main(verbosity=2)
