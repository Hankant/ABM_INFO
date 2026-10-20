"""Public, bounded social context tests; no HTTP or outcome-shaped mock curves."""
import copy
import json
import unittest

from rumor_sim import core
from test_core import fixture, active_state, Recorder


class SocialInteractionTests(unittest.TestCase):
    def setUp(self):
        self.cfg, self.event = fixture()
        self.cfg["social"] = {"protocol": "single_event_social_v1", "enabled": True,
                              "thread_comment_slots": 2, "thread_repost_slots": 1}
        self.cfg["feed"]["recommendation_probability"] = 0
        self.state = active_state(self.cfg, self.event)
        self.reader = self.state["agents"]["C001"]
        self.reader["follows"] = ["SOURCE", "C002"]
        self.source = next(iter(self.state["posts"].values()))

    def post(self, pid, author="O001", kind="comment", parent=None, content=None,
             created=1, visible=2, stance="support"):
        post = {**copy.deepcopy(self.source), "post_id": pid, "author_id": author,
                "kind": kind, "created_round": created, "visible_from": visible,
                "parent_post_id": parent or self.source["post_id"],
                "content_id": content or self.source["content_id"],
                "text": "Synthetic public opinion for a visibility test.",
                "public_stance": stance}
        self.state["posts"][pid] = post
        return post

    def context(self, t=3):
        return core._thread_feed(self.state, self.reader,
                                 [{"post": self.source, "channel": "following"}],
                                 t, self.cfg, self.cfg["social"])

    def test_thread_prioritizes_own_reply_then_followed_author_with_separate_caps(self):
        own = self.post("own", "C001")
        self.post("reply_to_me", "O001", parent=own["post_id"], created=1)
        self.post("followed_comment", "C002", created=1)
        self.post("newer_stranger", "O002", created=2, visible=3)
        self.post("repost", "O003", kind="repost")
        chosen = self.context()
        self.assertEqual([r["post"]["post_id"] for r in chosen],
                         ["reply_to_me", "followed_comment", "repost"])
        self.assertEqual([r["channel"] for r in chosen],
                         ["thread_comment", "thread_comment", "thread_repost"])
        self.assertNotIn("own", [r["post"]["post_id"] for r in chosen])

    def test_thread_rejects_unopened_topic_future_expired_and_overread_posts(self):
        self.post("unopened", content="different_root")
        self.post("future", visible=4)
        self.post("expired", created=-40, visible=0)
        self.post("overread")
        self.post("too_soon")
        self.reader["seen_posts"] = {
            "overread": {"count": 3, "last_seen_round": -5},
            "too_soon": {"count": 1, "last_seen_round": 1}}
        self.assertEqual(self.context(t=3), [])

    def test_own_public_post_reply_can_open_thread_but_inactivity_cannot(self):
        self.reader["follows"] = []
        own = self.post("own", "C001")
        self.post("reply", parent=own["post_id"])
        items, active = core.build_feed(self.state, "C001", 3, self.cfg)
        self.assertTrue(active)
        self.assertEqual([x["post"]["post_id"] for x in items], ["reply"])
        self.reader["activity"] = 0
        self.assertEqual(core.build_feed(self.state, "C001", 3, self.cfg)[0], [])
        direct = {**self.source, "post_id": "official", "author_id": "GOV",
                  "root_source_id": "GOV", "content_id": "government_root", "direct_only": True}
        items, active = core.build_feed(self.state, "C001", 3, self.cfg, direct)
        self.assertFalse(active)
        self.assertEqual([x["channel"] for x in items], ["government_direct", "thread_comment"])

    def test_existing_feed_is_not_duplicated_in_threads_and_disabled_mode_is_unchanged(self):
        self.post("peer", "C002")
        self.post("peer_repost", "O001", kind="repost")
        enabled = core.build_feed(self.state, "C001", 3, self.cfg)[0]
        ids = [r["post"]["post_id"] for r in enabled]
        self.assertEqual(len(ids), len(set(ids)))
        baseline = copy.deepcopy(self.cfg); baseline.pop("social")
        disabled = copy.deepcopy(self.cfg); disabled["social"]["enabled"] = False
        self.assertEqual(core.build_feed(self.state, "C001", 3, baseline),
                         core.build_feed(self.state, "C001", 3, disabled))
        old = core._make_view(self.state, self.reader, enabled[:1], 3, baseline)
        self.assertNotIn("social_observation", old)
        self.assertNotIn("relationship", old["visible_posts"][0])

    def test_social_observation_uses_only_latest_visible_public_stance_per_author(self):
        a = self.post("a", "C002", stance="support", created=1)
        b = self.post("b", "C002", stance="oppose", created=2, visible=3)
        c = self.post("c", "O001", stance="uncertain")
        self.post("unseen", "O002", stance="oppose")
        self.state["agents"]["O002"]["belief_score"] = 7
        self.state["agents"]["O002"]["secret_reason"] = "PRIVATE_NEVER_SEND"
        self.reader["empirical_behavior"] = {"comment_count": 2, "repost_count": 1}
        feed = [{"post": p, "channel": "thread_comment"} for p in (a, b, c)]
        view = core._make_view(self.state, self.reader, feed, 3, self.cfg)
        observation = view["social_observation"]
        self.assertEqual(observation["public_stance_author_counts"],
                         {"support": 0, "oppose": 1, "uncertain": 1})
        self.assertEqual(observation["unique_visible_author_count"], 2)
        self.assertEqual(observation["followed_author_count"], 1)
        self.assertEqual(observation["same_group_author_count"], 1)
        self.assertEqual(observation["cross_group_author_count"], 1)
        self.assertEqual(view["visible_posts"][0]["relationship"], "followed_peer")
        self.assertEqual(view["visible_posts"][2]["author_group_relation"], "cross_group")
        self.assertNotIn("PRIVATE_NEVER_SEND", json.dumps(view))
        self.assertNotIn("O002", json.dumps(view))
        self.assertEqual(view["profile"]["empirical_behavior"]["comment_count"], 2)
        self.state["agents"]["C002"]["belief_score"] = 98
        self.assertEqual(view, core._make_view(self.state, self.reader, feed, 3, self.cfg))

    def test_same_round_posts_are_invisible_but_next_round_thread_can_be_targeted(self):
        # C001 waits while its peers comment; on its first browsing round it sees
        # the source and the bounded public thread. No desired belief change is encoded.
        self.reader["activity"] = 0
        self.reader["follows"] = ["SOURCE"]
        recorder = Recorder(score=50, action="comment")
        first = core.step(self.state, self.cfg, self.event, recorder)
        self.assertTrue(first["posts"])
        for view, _ in recorder.calls:
            self.assertTrue(all(p["created_round"] == 0 for p in view["visible_posts"]))
            self.assertNotIn("rumor_original", json.dumps(view))
            self.assertNotIn("correction_original", json.dumps(view))
        next_state = first["state"]
        next_state["agents"]["C001"]["activity"] = 1
        views = []
        def target_thread(view, identity):
            views.append(copy.deepcopy(view))
            posts = [p for p in view["visible_posts"] if p.get("exposure_channel") == "thread_comment"]
            target = posts[0] if posts else view["visible_posts"][0]
            return {"decision": {"belief_score": 50, "action": "comment",
                    "target_post_id": target["post_id"], "public_stance": "uncertain",
                    "comment": "请核实信息。", "reason": "仅为可见性测试。"},
                    "audit": {"provider": "offline_visibility_fixture"}}
        second = core.step(next_state, self.cfg, self.event, target_thread)
        c_view = next(v for v in views if v["agent_id"] == "C001")
        threads = [p for p in c_view["visible_posts"] if p["exposure_channel"] == "thread_comment"]
        self.assertTrue(threads)
        self.assertTrue(all(p["created_round"] < 2 for p in c_view["visible_posts"]))
        new_post = next(p for p in second["posts"] if p["author_id"] == "C001")
        self.assertEqual(new_post["parent_post_id"], threads[0]["post_id"])
        self.assertEqual(new_post["visible_from"], 3)

    def test_exposure_metadata_metrics_and_summary_count_indirect_government(self):
        self.reader["follows"] = ["SOURCE"]
        # Read a genuine public descendant, not the direct-only government original.
        post = self.post("gov_descendant", "O001")
        post["root_source_id"] = "GOV"
        # This fixture retains the visible root content ID to exercise accounting.
        result = core.step(self.state, self.cfg, self.event, Recorder(score=50))
        # Post is not visible at round1.
        self.assertNotIn("gov_descendant", [r["post_id"] for r in result["exposures"]])
        later = result["state"]
        later["agents"]["C001"]["seen_posts"] = {}
        result = core.step(later, self.cfg, self.event, Recorder(score=50))
        rows = [r for r in result["exposures"] if r["post_id"] == "gov_descendant"]
        self.assertTrue(rows)
        self.assertTrue(all(r["author_id"] == "O001" and r["kind"] == "comment" for r in rows))
        self.assertTrue(all(r["root_source_id"] == "GOV" for r in rows))
        metrics = result["state"]["round_metrics"][-1]
        self.assertEqual(sum(metrics[f"{s}_count"] for s in ("accept", "reject", "uncertain", "unaware")), 10)
        self.assertEqual(metrics["exposures_government_indirect"], len(rows))
        self.assertGreater(metrics["exposures_thread_comment"], 0)
        summary = core.summarize(result["state"], self.cfg)
        self.assertEqual(summary["exposure_totals"]["thread_comment"], metrics["exposures_thread_comment"])
        self.assertEqual(summary["social_exposure_totals"]["government_indirect"], len(rows))

    def test_unseen_topic_without_own_reply_cannot_create_exposure(self):
        self.reader["follows"] = []
        self.post("unseen_comment")
        self.post("unseen_repost", kind="repost")
        self.assertEqual(core.build_feed(self.state, "C001", 3, self.cfg)[0], [])

    def test_plain_repost_does_not_publish_the_decisions_unexpressed_stance(self):
        parent = self.post("supporting_parent", "C002", stance="support")
        parent["text"] = "I support the original claim."
        decision = {"belief_score": 20, "action": "repost",
                    "target_post_id": parent["post_id"], "public_stance": "oppose",
                    "comment": "", "reason": "Protocol fixture: quoting without an added comment."}
        repost = core._user_post(self.state, "O001", decision, parent, 3, self.cfg)
        self.assertIsNone(repost["public_stance"])
        self.assertEqual(repost["text"], parent["text"])
        self.assertEqual(decision["public_stance"], "oppose")  # audit remains intact
        view = core._make_view(self.state, self.reader,
                              [{"post": repost, "channel": "thread_repost"}], 4, self.cfg)
        self.assertIsNone(view["visible_posts"][0]["public_stance"])
        self.assertEqual(view["social_observation"]["public_stance_author_counts"],
                         {"support": 0, "oppose": 0, "uncertain": 0})
        self.assertEqual(view["social_observation"]["unique_visible_author_count"], 1)
        baseline = copy.deepcopy(self.cfg); baseline.pop("social")
        self.assertEqual(core._user_post(self.state, "O001", decision, parent, 3, baseline)["public_stance"], "oppose")

    def test_newer_plain_repost_does_not_override_its_authors_visible_comment(self):
        comment = self.post("earlier_comment", "O001", stance="oppose", created=1)
        parent = self.post("supporting_parent", "C002", stance="support")
        decision = {"belief_score": 80, "action": "repost",
                    "target_post_id": parent["post_id"], "public_stance": "support",
                    "comment": "", "reason": "Visibility fixture."}
        repost = core._user_post(self.state, "O001", decision, parent, 3, self.cfg)
        view = core._make_view(self.state, self.reader,
                              [{"post": comment, "channel": "thread_comment"},
                               {"post": repost, "channel": "thread_repost"}], 4, self.cfg)
        self.assertEqual(view["social_observation"]["public_stance_author_counts"],
                         {"support": 0, "oppose": 1, "uncertain": 0})
        self.assertEqual(view["social_observation"]["unique_visible_author_count"], 1)

    def test_synchronous_step_applies_plain_repost_visibility_rule(self):
        result = core.step(self.state, self.cfg, self.event, Recorder(score=80, action="repost"))
        self.assertTrue(result["posts"])
        self.assertTrue(all(p["kind"] == "repost" and p["public_stance"] is None for p in result["posts"]))
        self.assertTrue(all(r["decision"]["public_stance"] == "uncertain" for r in result["decisions"]))

    def test_thread_repeat_limits_and_iteration_order_are_respected(self):
        self.post("repeat")
        self.reader["seen_posts"]["repeat"] = {"count": 2, "last_seen_round": 3}
        self.assertNotIn("repeat", [r["post"]["post_id"] for r in self.context(7)])
        self.assertIn("repeat", [r["post"]["post_id"] for r in self.context(8)])
        self.reader["seen_posts"]["repeat"]["count"] = 3
        self.assertNotIn("repeat", [r["post"]["post_id"] for r in self.context(8)])
        reverse = copy.deepcopy(self.state)
        reverse["agents"] = dict(reversed(list(reverse["agents"].items())))
        a = core.step(self.state, self.cfg, self.event, Recorder(score=50, action="comment"))
        b = core.step(reverse, self.cfg, self.event, Recorder(score=50, action="comment"))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
