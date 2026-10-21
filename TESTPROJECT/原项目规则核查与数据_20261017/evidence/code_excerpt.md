# 现有单事件代码核查摘录

来源文件名与行号均为本次读取版本；不是原稿空间代码。摘录供核查，不是完整可运行模块。

## core.py:L67-L94

```python
67: 
68: def belief_class(score: int | None, config: dict) -> str:
69:     if score is None:
70:         return "unaware"
71:     if type(score) is not int or not 0 <= score <= 100:
72:         raise ValueError("belief_score must be an integer within 0..100 or None")
73:     if score >= config["belief"]["accept_min"]:
74:         return "accept"
75:     if score <= config["belief"]["reject_max"]:
76:         return "reject"
77:     return "uncertain"
78: 
79: 
80: def _source_post(event: dict) -> dict:
81:     event_id = event["event_id"]
82:     source = event.get("rumor_source_id", "SOURCE")
83:     return {
84:         "post_id": f"{event_id}:source:0", "parent_post_id": None,
85:         "claim_id": event["claim_id"], "content_id": f"{event_id}:rumor_origin",
86:         "author_id": source, "kind": "rumor_original", "created_round": 0,
87:         "visible_from": 1, "text": event["rumor_text"], "quoted_context": None,
88:         "root_text": event["rumor_text"], "root_evidence": "",
89:         "root_source_id": source,
90:         "root_source_profile": _profile_counts(event.get("source_profile", {}), strict=False),
91:         "source_cue": event.get("rumor_source_cue", "一名用户发布的待核实信息。"),
92:         "public_stance": None, "direct_only": False,
93:     }
94: 
```

## core.py:L105-L201

```python
105: def initialize(config: dict, event: dict, d_seed: float, seed: int) -> dict:
106:     """Generate fixed marginal profiles, directed follows, and an unexposed state.
107: 
108:     Historical comments/reposts in an input event are deliberately not imported as
109:     memory, initial belief or interactions. Use ``apply_profiles`` only after an
110:     explicit, deidentified static-field mapping has been established.
111:     """
112:     pop, prior, network = config["population"], config["prior"], config["network"]
113:     ni = _integer(pop["n_inside"], "n_inside", 1)
114:     no = _integer(pop["n_outside"], "n_outside", 1)
115:     if ni % 2 or no % 2:
116:         raise ValueError("Equal +/- prior offsets require even sizes in both groups")
117:     _integer(seed, "seed")
118:     d_seed = _finite_number(d_seed, "d_seed")
119:     mu = _finite_number(prior["overall_mean"], "overall_mean")
120:     offset = _finite_number(prior["within_group_offset"], "within_group_offset")
121:     same = _integer(network["same_group_follows"], "same_group_follows")
122:     cross = _integer(network["cross_group_follows"], "cross_group_follows")
123:     if same >= min(ni, no) or cross > min(ni, no):
124:         raise ValueError("Requested directed degrees exceed eligible user pools")
125:     if network.get("directed", True) is not True:
126:         raise ValueError("This study requires directed following edges")
127:     if network.get("pre_follow_government", False):
128:         raise ValueError("The fixed study has no pre-followed government account")
129:     if network.get("outside_follow_source", False):
130:         raise ValueError("Outside users cannot follow the source at initialization")
131:     if not network.get("inside_follow_source", True):
132:         raise ValueError("Inside users must follow the source at initialization")
133:     for field in ("event_id", "claim_id", "original_claim", "rumor_text"):
134:         if not isinstance(event.get(field), str) or not event[field].strip():
135:             raise ValueError(f"event.{field} must be text")
136:     if config["time"].get("source_round", 0) != 0 or config["time"].get("first_decision_round", 1) != 1:
137:         raise ValueError("The fixed study starts with source round 0 and decisions at round 1")
138: 
139:     ids = {"inside": [f"C{i:03d}" for i in range(1, ni + 1)],
140:            "outside": [f"O{i:03d}" for i in range(1, no + 1)]}
141:     source = event.get("rumor_source_id", "SOURCE")
142:     government = event.get("government_id", "GOV")
143:     all_ids = set(ids["inside"] + ids["outside"])
144:     if source == government or source in all_ids or government in all_ids:
145:         raise ValueError("Scripted account IDs must be distinct from all user IDs")
146:     agents = {}
147:     for group, n in (("inside", ni), ("outside", no)):
148:         counts = pop["inside_counts" if group == "inside" else "outside_counts"]
149:         traits = {}
150:         for field, levels in (("activity", pop["activity_levels"]),
151:                               ("prior_government_trust", pop["trust_levels"]),
152:                               ("sharing_style", pop["sharing_styles"])):
153:             expanded = _expand(levels, counts, n, field)
154:             traits[field] = _shuffled(expanded, seed, group, "trait", field)
155:         willing_n = _integer(pop["willing_inside" if group == "inside" else "willing_outside"], "willing_count")
156:         if willing_n > n:
157:             raise ValueError("Willing count exceeds group size")
158:         traits["correction_share_willingness"] = _shuffled(
159:             ["willing"] * willing_n + ["reading_only"] * (n - willing_n),
160:             seed, group, "trait", "correction_share_willingness")
161:         signs = _shuffled([-1] * (n // 2) + [1] * (n // 2),
162:                           seed, group, "trait", "prior_offset")
163:         group_mean = mu + no / (ni + no) * d_seed if group == "inside" else mu - ni / (ni + no) * d_seed
164:         for i, aid in enumerate(ids[group]):
165:             p = group_mean + signs[i] * offset
166:             if not 0 <= p <= 1:
167:                 raise ValueError("Initial prior is outside [0,1]; do not silently clip it")
168:             agent = {"agent_id": aid, "group": group,
169:                      **{k: values[i] for k, values in traits.items()},
170:                      "prior_acceptance": p, "follows": [],
171:                      "belief_score": None, "belief_state": "unaware", "memory": [],
172:                      "seen_posts": {}, "reposted_content_ids": [],
173:                      "first_exposure_round": None, "last_action": "idle",
174:                      "observed_profile": {}, "profile_origin": "designed_baseline"}
175:             for field in ("activity", "prior_government_trust"):
176:                 if not 0 <= _finite_number(agent[field], field) <= 1:
177:                     raise ValueError(f"{field} must be within [0,1]")
178:             agents[aid] = agent
179:     for aid in sorted(agents):
180:         group = agents[aid]["group"]
181:         other = "outside" if group == "inside" else "inside"
182:         same_ids = [x for x in ids[group] if x != aid]
183:         follows = _shuffled(same_ids, seed, aid, "same_group_follows")[:same]
184:         follows += _shuffled(ids[other], seed, aid, "cross_group_follows")[:cross]
185:         if group == "inside":
186:             follows.append(source)
187:         agents[aid]["follows"] = sorted(follows)
188:     post = _source_post(event)
189:     return {
190:         "schema_version": "rumor-core-1", "round": 0, "seed": seed,
191:         "d_seed": d_seed, "event_id": event["event_id"], "claim_id": event["claim_id"],
192:         "original_claim": event["original_claim"], "source_id": source,
193:         "government_id": government, "agents": agents, "posts": {post["post_id"]: post},
194:         "pbd": None, "policy": None, "risk_ids": [], "first_rejections": {},
195:         "round_metrics": [],
196:         "direct_budget": _integer(config["policy"]["direct_unique_users"], "direct_unique_users", 1),
197:     }
198: 
199: 
200: def apply_profiles(state: dict, profiles: list[dict],
201:                    allowed_fields: Iterable[str] = OBSERVED_PROFILE_FIELDS) -> dict:
```

## core.py:L237-L279

```python
237:                 if targeting == "random" or a["group"] == targeting]
238:     if n > len(eligible):
239:         raise ValueError("Direct budget exceeds the eligible group size")
240:     return sorted(eligible, key=lambda aid: (
241:         _digest(state["event_id"], state["seed"], tg, targeting, "recipients", aid), aid))[:n]
242: 
243: 
244: def _validate_policy(state: dict, policy: dict, budget: int) -> None:
245:     if policy.get("enabled") is not True:
246:         raise ValueError("Use policy=None for an untreated trajectory")
247:     _integer(policy.get("government_round"), "government_round", 1)
248:     if policy.get("targeting") not in {"inside", "outside", "random"}:
249:         raise ValueError("Unknown targeting category")
250:     gt = _finite_number(policy.get("credibility"), "credibility")
251:     if gt not in (0.2, 0.6, 1.0):
252:         raise ValueError("Credibility must be one of .2/.6/1.0 in this fixed study")
253:     recipients = policy.get("recipients")
254:     if not isinstance(recipients, list) or any(not isinstance(x, str) for x in recipients):
255:         raise ValueError("recipients must be a JSON list of anonymous IDs")
256:     if len(recipients) != budget or len(set(recipients)) != budget:
257:         raise ValueError("Direct recipients must be exactly the fixed unique budget")
258:     if any(aid not in state["agents"] for aid in recipients):
259:         raise ValueError("Unknown direct recipient")
260:     if policy["targeting"] != "random" and any(
261:             state["agents"][aid]["group"] != policy["targeting"] for aid in recipients):
262:         raise ValueError("Direct recipient outside the selected target group")
263: 
264: 
265: def branch(parent_state: dict, policy: dict) -> dict:
266:     if parent_state.get("policy") is not None:
267:         raise ValueError("Policy branches must start from an untreated parent state")
268:     _validate_policy(parent_state, policy, parent_state["direct_budget"])
269:     if parent_state["round"] != policy["government_round"] - 1:
270:         raise ValueError("Branch point must be the end of T_G-1")
271:     if parent_state["pbd"] is None:
272:         raise ValueError("The common pre-intervention PBd checkpoint must already exist")
273:     result = copy.deepcopy(parent_state)
274:     result["policy"] = copy.deepcopy(policy)
275:     result["risk_ids"] = sorted(aid for aid, a in result["agents"].items()
276:                                 if a["belief_state"] == "accept")
277:     result["first_rejections"] = {}
278:     return result
279: 
```

## core.py:L281-L308

```python
281: def is_read_eligible(post: dict, agent: dict, t: int, config: dict) -> bool:
282:     feed = config["feed"]
283:     age = t - post["created_round"]
284:     if post["visible_from"] > t or not 0 <= age < feed["post_ttl_rounds"]:
285:         return False
286:     seen = agent["seen_posts"].get(post["post_id"])
287:     if seen:
288:         if seen["count"] >= feed["max_reads_per_post"]:
289:             return False
290:         if t - seen["last_seen_round"] < feed["repeat_gap_rounds"]:
291:             return False
292:     return True
293: 
294: 
295: def _weighted_posts(candidates: list[dict], n: int, state: dict, aid: str,
296:                     t: int, channel: str, config: dict) -> list[dict]:
297:     half_life = _finite_number(config["feed"]["recency_half_life_rounds"], "half_life")
298:     if half_life <= 0:
299:         raise ValueError("Recency half life must be positive")
300:     scored = []
301:     for p in candidates:
302:         weight = 2 ** (-(t - p["created_round"]) / half_life)
303:         u = keyed_uniform(state["event_id"], state["seed"], t, aid, channel, p["post_id"])
304:         scored.append((-math.log(u) / weight, p["post_id"], p))
305:     return [p for _, _, p in sorted(scored, key=lambda x: (x[0], x[1]))[:n]]
306: 
307: 
308: def _social_config(config: dict | None) -> dict | None:
```

## core.py:L327-L408

```python
327:         return "source", "non_peer"
328:     peer = state["agents"].get(author)
329:     relation = "followed_peer" if author in reader["follows"] else "unfollowed_peer"
330:     group = ("same_group" if peer["group"] == reader["group"] else "cross_group") if peer else "non_peer"
331:     return relation, group
332: 
333: 
334: def _thread_feed(state: dict, agent: dict, chosen: list[dict], t: int,
335:                  config: dict, social: dict) -> list[dict]:
336:     """Read bounded public thread context from the same frozen post collection.
337: 
338:     Reading a root topic or receiving a reply to one's own post opens a thread.
339:     Merely sharing an event with an unseen post never makes that post visible.
340:     """
341:     aid = agent["agent_id"]
342:     topics = {item["post"]["content_id"] for item in chosen}
343:     own_posts = {pid for pid, p in state["posts"].items()
344:                  if p["author_id"] == aid and p["visible_from"] <= t}
345:     excluded = {item["post"]["post_id"] for item in chosen}
346:     follows = set(agent["follows"])
347:     selected = []
348:     for kind, maximum in (("comment", 2), ("repost", 1)):
349:         channel = f"thread_{kind}"
350:         n = social.get(f"{channel}_slots", maximum)
351:         candidates = [p for p in state["posts"].values()
352:                       if p["kind"] == kind and p["author_id"] != aid
353:                       and not p["direct_only"] and p["post_id"] not in excluded
354:                       and is_read_eligible(p, agent, t, config)
355:                       and (p["content_id"] in topics or p.get("parent_post_id") in own_posts)]
356:         for priority in (0, 1, 2):
357:             group = [p for p in candidates if
358:                      (0 if p.get("parent_post_id") in own_posts else
359:                       1 if p["author_id"] in follows else 2) == priority]
360:             picked = _weighted_posts(group, n, state, aid, t, channel, config)
361:             selected.extend({"post": p, "channel": channel} for p in picked)
362:             excluded.update(p["post_id"] for p in picked)
363:             n -= len(picked)
364:             if n == 0:
365:                 break
366:     return selected
367: 
368: 
369: def build_feed(state: dict, agent_id: str, t: int, config: dict,
370:                direct_post: dict | None = None) -> tuple[list[dict], bool]:
371:     """Return slot-tagged posts without changing reading history or any state."""
372:     agent, cfg = state["agents"][agent_id], config["feed"]
373:     probability = _finite_number(cfg["recommendation_probability"], "recommendation_probability")
374:     if not 0 <= probability <= 1:
375:         raise ValueError("Recommendation slot probability must be within [0,1]")
376:     active = keyed_uniform(state["event_id"], state["seed"], t, agent_id, "active") < agent["activity"]
377:     chosen = []
378:     if active:
379:         ordinary = [p for p in state["posts"].values()
380:                     if not p["direct_only"] and p["author_id"] != agent_id
381:                     and is_read_eligible(p, agent, t, config)]
382:         follows = set(agent["follows"])
383:         selected = _weighted_posts([p for p in ordinary if p["author_id"] in follows],
384:                                    cfg["following_slots"], state, agent_id, t, "following", config)
385:         chosen.extend({"post": p, "channel": "following"} for p in selected)
386:         if keyed_uniform(state["event_id"], state["seed"], t, agent_id, "reco") < probability:
387:             excluded = {p["post_id"] for p in selected}
388:             reco = [p for p in ordinary if p["author_id"] not in follows and p["post_id"] not in excluded]
389:             selected = _weighted_posts(reco, cfg["recommendation_slots"], state, agent_id, t,
390:                                        "recommendation", config)
391:             chosen.extend({"post": p, "channel": "recommendation"} for p in selected)
392:     if direct_post is not None:
393:         if cfg["direct_extra_slots"] != 1:
394:             raise ValueError("The fixed study requires exactly one extra direct slot")
395:         if not is_read_eligible(direct_post, agent, t, config):
396:             raise ValueError("An official direct delivery is unexpectedly unreadable")
397:         chosen.append({"post": direct_post, "channel": "government_direct"})
398:     social = _social_config(config)
399:     if social is not None and (active or direct_post is not None):
400:         chosen.extend(_thread_feed(state, agent, chosen, t, config, social))
401:     if len({x["post"]["post_id"] for x in chosen}) != len(chosen):
402:         raise AssertionError("The same post was assigned to multiple slots")
403:     return chosen, active
404: 
405: 
406: def _visible_post(post: dict) -> dict:
407:     # No internal 'rumor_original' label, content_id, truth label or complete event.
408:     keys = ("post_id", "author_id", "created_round", "text", "quoted_context",
```

## core.py:L511-L548

```python
511: def _official_post(event: dict, policy: dict) -> dict:
512:     if not isinstance(event.get("correction_text"), str) or not event["correction_text"].strip():
513:         raise ValueError("Government intervention requires a nonempty correction_text")
514:     if not isinstance(event.get("evidence_text"), str):
515:         raise ValueError("evidence_text must be a string; empty is allowed for the explicitly scripted experiment")
516:     tg, gt = policy["government_round"], policy["credibility"]
517:     correct = {0.2: 2, 0.6: 6, 1.0: 10}[float(gt)]
518:     source = event.get("government_id", "GOV")
519:     return {
520:         "post_id": f"{event['event_id']}:government:{tg}", "parent_post_id": None,
521:         "claim_id": event["claim_id"], "content_id": f"{event['event_id']}:correction_origin",
522:         "author_id": source, "kind": "correction_original", "created_round": tg,
523:         "visible_from": tg, "text": event["correction_text"], "quoted_context": None,
524:         "root_text": event["correction_text"], "root_evidence": event["evidence_text"],
525:         "root_source_id": source,
526:         "root_source_profile": {},
527:         "material_origin": event.get("correction_origin", "unspecified"),
528:         "source_cue": "该账号为当地官方信息发布账号。平台展示的既往独立核验记录为："
529:                       f"最近10条可核验信息中，{correct}条被核验与事实一致。",
530:         "public_stance": None, "direct_only": True,
531:     }
532: 
533: 
534: def _user_post(state: dict, agent_id: str, decision: dict, parent: dict, t: int,
535:                config: dict | None = None) -> dict:
536:     public_stance = decision["public_stance"]
537:     if decision["action"] == "repost" and _social_config(config) is not None:
538:         public_stance = None
539:     return {
540:         "post_id": f"{state['event_id']}:user:{t}:{agent_id}",
541:         "parent_post_id": parent["post_id"], "claim_id": parent["claim_id"],
542:         "content_id": parent["content_id"], "author_id": agent_id,
543:         "kind": decision["action"], "created_round": t, "visible_from": t + 1,
544:         "text": decision["comment"] if decision["action"] == "comment" else parent["text"],
545:         "quoted_context": {"post_id": parent["post_id"], "author_id": parent["author_id"],
546:                            "text": parent["text"]},
547:         "root_text": parent["root_text"], "root_evidence": parent["root_evidence"],
548:         "root_source_id": parent["root_source_id"], "source_cue": parent["source_cue"],
```

## core.py:L594-L722

```python
594: def step(state: dict, config: dict, event: dict,
595:          decide: Callable[[dict, str], dict]) -> dict:
596:     """Commit one synchronous round iff every required decision is valid.
597: 
598:     All views are frozen before any injected decision call. A raised exception is
599:     intentionally propagated; the runner should audit/retry/resume without using a
600:     partially committed state. Decision retries themselves belong in the provider.
601:     """
602:     t = state["round"] + 1
603:     if t > config["time"]["last_round"]:
604:         raise ValueError("Cannot advance past the configured common endpoint")
605:     if event["event_id"] != state["event_id"] or event["original_claim"] != state["original_claim"]:
606:         raise ValueError("Event identity or focal claim changed during the run")
607:     if len(state["round_metrics"]) != state["round"]:
608:         raise ValueError("State must include the complete metrics prefix, one row per round")
609:     old = state
610:     new = copy.deepcopy(state)
611:     policy = state.get("policy")
612:     official = None
613:     if policy is not None:
614:         _validate_policy(state, policy, config["policy"]["direct_unique_users"])
615:         if policy["government_round"] + config["time"]["followup_max_elapsed"] > config["time"]["last_round"]:
616:             raise ValueError("The common endpoint is too early for the complete TBU window")
617:         if config["policy"]["direct_delivery_rounds"] != 1:
618:             raise ValueError("The fixed study permits one direct-delivery round")
619:         if t == policy["government_round"]:
620:             new["risk_ids"] = sorted(aid for aid, a in old["agents"].items()
621:                                       if a["belief_state"] == "accept")
622:             new["first_rejections"] = {}
623:             official = _official_post(event, policy)
624:             if official["post_id"] in new["posts"]:
625:                 raise ValueError("Official correction was already published")
626:             new["posts"][official["post_id"]] = official
627: 
628:     inputs = []
629:     activity_by_agent = {}
630:     for aid in sorted(old["agents"]):
631:         direct = official if official is not None and aid in policy["recipients"] else None
632:         feed, active = build_feed(old, aid, t, config, direct)
633:         activity_by_agent[aid] = active
634:         if not feed:
635:             continue
636:         view = _make_view(old, old["agents"][aid], feed, t, config)
637:         identity = _canonical([old["event_id"], old["seed"], old["d_seed"], t, aid])
638:         inputs.append((aid, feed, view, identity))
639: 
640:     pending = []
641:     for aid, feed, view, identity in inputs:
642:         result = decide(copy.deepcopy(view), identity)
643:         if not isinstance(result, dict) or not isinstance(result.get("audit"), dict):
644:             raise ValueError("Decision provider must return {'decision': ..., 'audit': dict}")
645:         decision = validate_decision(result.get("decision"), view, config)
646:         _canonical(result["audit"])
647:         pending.append((aid, feed, view, identity, decision, copy.deepcopy(result["audit"])))
648: 
649:     # No external calls happen below this point. All changes affect only the copy.
650:     exposures, decisions, created_posts = [], [], []
651:     if official is not None:
652:         created_posts.append(copy.deepcopy(official))
653:     for aid, feed, view, identity, decision, audit in pending:
654:         agent = new["agents"][aid]
655:         agent["belief_score"] = decision["belief_score"]
656:         agent["belief_state"] = belief_class(decision["belief_score"], config)
657:         agent["last_action"] = decision["action"]
658:         if agent["first_exposure_round"] is None:
659:             agent["first_exposure_round"] = t
660:         for item in feed:
661:             post, channel = item["post"], item["channel"]
662:             previous = agent["seen_posts"].get(post["post_id"])
663:             count = 1 + (previous["count"] if previous else 0)
664:             relationship, group_relation = _post_relationship(old, old["agents"][aid], post)
665:             exposures.append({"round": t, "agent_id": aid, "group": agent["group"],
666:                 "post_id": post["post_id"], "content_id": post["content_id"], "channel": channel,
667:                 "author_id": post["author_id"], "kind": post["kind"],
668:                 "relationship": relationship, "author_group_relation": group_relation,
669:                 "parent_post_id": post.get("parent_post_id"), "public_stance": post["public_stance"],
670:                 "root_source_id": post["root_source_id"],
671:                 "reading_count": count, "previous_read_round": previous["last_seen_round"] if previous else None,
672:                 "post_age": t - post["created_round"], "is_repeat": previous is not None})
673:             agent["seen_posts"][post["post_id"]] = {"count": count, "last_seen_round": t}
674:         if decision["action"] != "silent":
675:             parent = next(x["post"] for x in feed if x["post"]["post_id"] == decision["target_post_id"])
676:             post = _user_post(new, aid, decision, parent, t, config)
677:             if post["post_id"] in new["posts"]:
678:                 raise AssertionError("Duplicate user post ID")
679:             new["posts"][post["post_id"]] = post
680:             created_posts.append(copy.deepcopy(post))
681:             if decision["action"] == "repost":
682:                 agent["reposted_content_ids"] = sorted(agent["reposted_content_ids"] + [parent["content_id"]])
683:         memory = {"round": t, "visible_posts": copy.deepcopy(view["visible_posts"]),
684:                   "belief_score": decision["belief_score"], "action": decision["action"],
685:                   "target_post_id": decision["target_post_id"], "comment": decision["comment"],
686:                   "public_stance": decision["public_stance"], "reason": decision["reason"]}
687:         n_memory = _integer(config["feed"]["memory_decision_rounds"], "memory_decision_rounds", 1)
688:         agent["memory"] = (agent["memory"] + [memory])[-n_memory:]
689:         decisions.append({"round": t, "agent_id": aid, "call_identity": identity,
690:                           "view": copy.deepcopy(view), "decision": decision, "audit": audit})
691: 
692:     called = {aid for aid, *_ in pending}
693:     exposed_by_agent = {aid: [] for aid in new["agents"]}
694:     for exposure in exposures:
695:         exposed_by_agent[exposure["agent_id"]].append(exposure)
696:     panel = []
697:     for aid in sorted(new["agents"]):
698:         agent = new["agents"][aid]
699:         agent_exposures = exposed_by_agent[aid]
700:         panel.append({"round": t, "agent_id": aid, "group": agent["group"],
701:                       "score": agent["belief_score"], "state": agent["belief_state"],
702:                       "exposed": bool(agent_exposures), "action": agent["last_action"] if aid in called else "idle",
703:                       "naturally_active": activity_by_agent[aid], "called_llm": aid in called,
704:                       "n_feed_posts": len(agent_exposures),
705:                       "government_direct": any(x["channel"] == "government_direct" for x in agent_exposures)})
706:     new["round"] = t
707:     metric = _round_metric(new, t, exposures, decisions)
708:     new["round_metrics"].append(metric)
709:     if t == config["time"]["pb_checkpoint_round"]:
710:         if new["pbd"] is not None:
711:             raise ValueError("PBd checkpoint cannot be overwritten")
712:         new["pbd"] = metric["accept_rate_inside"] - metric["accept_rate_outside"]
713:     if policy is not None:
714:         tg = policy["government_round"]
715:         if tg <= t <= tg + config["time"]["followup_max_elapsed"]:
716:             for aid in new["risk_ids"]:
717:                 if aid not in new["first_rejections"] and new["agents"][aid]["belief_state"] == "reject":
718:                     new["first_rejections"][aid] = t
719:     return {"state": new, "exposures": exposures, "decisions": decisions,
720:             "posts": created_posts, "states": panel}
721: 
722: 
```

## core.py:L723-L775

```python
723: def individual_tbu(state: dict, config: dict) -> list[dict]:
724:     if state.get("policy") is None:
725:         return []
726:     tg = state["policy"]["government_round"]
727:     W = config["time"]["followup_max_elapsed"]
728:     complete = state["round"] >= tg + W
729:     result = []
730:     for aid in sorted(state["risk_ids"]):
731:         first = state["first_rejections"].get(aid)
732:         if first is not None and not tg <= first <= min(state["round"], tg + W):
733:             raise ValueError("Stored first rejection is outside its valid TBU window")
734:         observed = first is not None
735:         result.append({"agent_id": aid, "group": state["agents"][aid]["group"],
736:                        "government_round": tg, "first_reject": first,
737:                        "event": 1 if observed else (0 if complete else None),
738:                        "duration": first - tg if observed else (W if complete else None),
739:                        "followup_complete": complete})
740:     return result
741: 
742: 
743: def summarize(state: dict, config: dict) -> dict:
744:     metric = state["round_metrics"][-1] if state["round_metrics"] else _round_metric(state, 0, [], [])
745:     individuals = individual_tbu(state, config)
746:     completed = [row["duration"] for row in individuals if row["event"] == 1]
747:     risk_n = len(individuals)
748:     policy = state.get("policy")
749:     full_followup = (policy is not None and state["round"] >=
750:                      policy["government_round"] + config["time"]["followup_max_elapsed"])
751:     channels = set(EXPOSURE_CHANNELS)
752:     for m in state["round_metrics"]:
753:         channels.update(m.get("exposures_by_channel", {}))
754:     return {
755:         "event_id": state["event_id"], "seed": state["seed"], "d_seed": state["d_seed"],
756:         "end_round": state["round"], "PBd": state["pbd"], "policy": copy.deepcopy(policy),
757:         "risk_n": risk_n, "updated_n": len(completed),
758:         "update_rate": len(completed) / risk_n if risk_n else None,
759:         "TBU_mean": sum(completed) / len(completed) if completed else None,
760:         "censored_n": risk_n - len(completed) if full_followup else None,
761:         "followup_complete": bool(full_followup),
762:         "RMST": sum(row["duration"] for row in individuals) / risk_n if full_followup and risk_n else None,
763:         "accept_rate_end": metric["accept_rate"],
764:         "accept_rate_end_inside": metric["accept_rate_inside"],
765:         "accept_rate_end_outside": metric["accept_rate_outside"],
766:         "accept_rate_end_by_group": {g: metric[f"accept_rate_{g}"] for g in ("inside", "outside")},
767:         "cumulative_acceptance_1_to_end": sum(m["accept_rate"] for m in state["round_metrics"]),
768:         "cumulative_acceptance_by_group": {g: sum(m[f"accept_rate_{g}"] for m in state["round_metrics"])
769:                                             for g in ("inside", "outside")},
770:         "exposure_totals": {channel: sum(m.get(f"exposures_{channel}", 0) for m in state["round_metrics"])
771:                              for channel in sorted(channels)},
772:         "social_exposure_totals": {name: sum(m.get(f"exposures_{name}", 0) for m in state["round_metrics"])
773:                                    for name in ("same_group", "cross_group", "non_peer", "government_indirect")},
774:         "comments": sum(m["comments"] for m in state["round_metrics"]),
775:         "reposts": sum(m["reposts"] for m in state["round_metrics"]),
```

## runner.py:L132-L181

```python
132: def execute(event, profiles, config, output, provider_mode="mock", mode="single",
133:             d_seed=.2, seed=1, tg=20, targeting="inside", gt=.6,
134:             allow_synthetic=False, max_api_requests=None, progress=None, provider=None):
135:     validate_config(config)
136:     validate_event(event, allow_synthetic=allow_synthetic, require_correction=mode != "parent")
137:     if mode not in ("single", "grid", "parent", "timeline"): raise ValueError("Unknown experiment mode")
138:     if provider_mode not in ("mock", "http"): raise ValueError("Unknown provider mode")
139:     grid = config["grid"]
140:     if mode != "grid":
141:         if d_seed not in grid["d_seed"] or seed not in grid["seeds"]:
142:             raise ValueError("Requested d_seed/seed must appear in the frozen grid configuration")
143:         if mode in ("single", "timeline") and (tg not in grid["government_round"] or targeting not in grid["targeting"] or gt not in grid["credibility"]):
144:             raise ValueError("Requested policy must appear in frozen grid configuration")
145:     if provider is not None and provider.provider_mode != provider_mode: raise ValueError("Provider mode mismatch")
146:     output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
147:     owns = provider is None
148:     if owns:
149:         llm = copy.deepcopy(config["llm"])
150:         if max_api_requests is not None: llm["max_api_requests"] = max_api_requests
151:         cls = HTTPDecisionProvider if provider_mode == "http" else MockDecisionProvider
152:         provider = cls(llm, output / "provider")
153:     bases = itertools.product(grid["d_seed"], grid["seeds"]) if mode == "grid" else [(d_seed, seed)]
154:     summaries = []
155:     summary_path = output / "event_summaries" / f"{event['event_id']}.json"
156:     try:
157:         for d, s in bases:
158:             base_id = f"{event['event_id']}_d{d:g}_s{s}"
159:             initial = attach_donor_profiles(core.initialize(config, event, d, s), profiles, s)
160:             if mode == "timeline":
161:                 # The policy schedule is not in any agent's prompt. At TG, core.step
162:                 # forms the risk set from the actually committed TG-1 beliefs.
163:                 initial["policy"] = policy_spec(initial, config, tg, targeting, gt)
164:                 run_id = f"{base_id}_timeline_t{tg}_{targeting}_gt{gt:g}"
165:                 _, summary = run_trajectory(output / "runs" / run_id, initial, config,
166:                     event, profiles, provider, run_id, progress=progress)
167:                 summaries.append(summary)
168:                 atomic_json(summary_path, summaries)
169:                 continue
170:             parent_dir = output / "runs" / f"{base_id}_parent"
171:             parent_store, summary = run_trajectory(parent_dir, initial, config, event, profiles, provider,
172:                 f"{base_id}_parent", progress=progress)
173:             summaries.append(summary)
174:             atomic_json(summary_path, summaries)
175:             if mode == "parent": continue
176:             policies = itertools.product(grid["government_round"], grid["targeting"], grid["credibility"]) if mode == "grid" else [(tg, targeting, gt)]
177:             for t, target, credibility in policies:
178:                 pre = parent_store.state_at(t - 1)
179:                 policy = policy_spec(pre, config, t, target, credibility)
180:                 child = core.branch(pre, policy)
181:                 run_id = f"{base_id}_t{t}_{target}_gt{credibility:g}"
```

## cli.py:L48-L61

```python
48:         cmd.add_argument("--config", type=Path, default=ROOT / ("config/single_event.json" if name == "single-event" else "config/research.json"))
49:         event = cmd.add_mutually_exclusive_group(required=True)
50:         event.add_argument("--event", type=Path)
51:         event.add_argument("--event-list", type=Path, help="JSON array of event.json paths (relative to list)")
52:         cmd.add_argument("--output", required=True, type=Path)
53:         cmd.add_argument("--provider", choices=["mock", "http"], default="mock")
54:         cmd.add_argument("--max-api-requests", type=int, help="Absolute cumulative cap for this output/provider directory")
55:         cmd.add_argument("--allow-synthetic", action="store_true")
56:         cmd.add_argument("--d-seed", type=float, default=.2)
57:         cmd.add_argument("--seed", type=int, default=1)
58:         cmd.add_argument("--tg", type=int, default=20)
59:         cmd.add_argument("--targeting", choices=["inside", "random", "outside"], default="inside")
60:         cmd.add_argument("--gt", type=float, default=.6)
61:     return p
```

## storage.py:L1-L148

```python
1: """Atomic round journals and reproducible exports. Pure standard library."""
2: from __future__ import annotations
3: 
4: import csv
5: import gzip
6: import hashlib
7: import json
8: import os
9: from pathlib import Path
10: import uuid
11: 
12: 
13: def canonical(value):
14:     return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
15: 
16: 
17: def digest(value):
18:     return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()
19: 
20: 
21: def atomic_json(path, value, compressed=False):
22:     path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
23:     tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
24:     try:
25:         data = (canonical(value) + "\n").encode("utf-8")
26:         if compressed: data = gzip.compress(data, compresslevel=2, mtime=0)
27:         with tmp.open("wb") as f:
28:             f.write(data); f.flush(); os.fsync(f.fileno())
29:         os.replace(tmp, path)
30:     finally:
31:         if tmp.exists(): tmp.unlink()
32: 
33: 
34: def read_json(path):
35:     path = Path(path)
36:     if path.suffix == ".gz":
37:         return json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
38:     return json.loads(path.read_text(encoding="utf-8-sig"))
39: 
40: 
41: class RunStore:
42:     """Each committed round is one atomic file containing state and its log rows.
43: 
44:     A failed round has no journal file; the provider success cache can safely reuse
45:     already answered requests after restart. CSV/JSONL are derived exports only.
46:     """
47:     def __init__(self, path, manifest, initial, prefix_path=None):
48:         self.path = Path(path).resolve()
49:         self.path.mkdir(parents=True, exist_ok=True)
50:         self.round_dir = self.path / "rounds"; self.round_dir.mkdir(exist_ok=True)
51:         manifest = dict(manifest)
52:         manifest["initial_round"] = initial["round"]
53:         manifest["initial_state_hash"] = digest(initial)
54:         manifest["prefix_path"] = os.path.relpath(Path(prefix_path).resolve(), self.path) if prefix_path else None
55:         mp = self.path / "manifest.json"
56:         if mp.exists():
57:             if read_json(mp) != manifest:
58:                 raise ValueError("Existing run uses different inputs/code/provider. Use a new output directory; no overwrite.")
59:             if not (self.path / "initial.json.gz").exists():
60:                 raise ValueError("Existing manifest has no initial snapshot")
61:             if digest(read_json(self.path / "initial.json.gz")) != manifest["initial_state_hash"]:
62:                 raise ValueError("Initial snapshot hash mismatch")
63:         else:
64:             atomic_json(self.path / "initial.json.gz", initial, compressed=True)
65:             atomic_json(mp, manifest)
66:         self.manifest = manifest
67: 
68:     def latest(self):
69:         files = sorted(self.round_dir.glob("*.json.gz"))
70:         if not files: return read_json(self.path / "initial.json.gz")
71:         indices = [int(f.name.split(".")[0]) for f in files]
72:         expected = list(range(self.manifest["initial_round"] + 1, indices[-1] + 1))
73:         if indices != expected: raise ValueError("Round journal gap detected; refusing an incomplete resume")
74:         return read_round(files[-1])["state"]
75: 
76:     def state_at(self, t):
77:         if t == self.manifest["initial_round"]: return read_json(self.path / "initial.json.gz")
78:         return read_round(self.round_dir / f"{t:05d}.json.gz")["state"]
79: 
80:     def commit(self, envelope):
81:         t = envelope["state"]["round"]
82:         dst = self.round_dir / f"{t:05d}.json.gz"
83:         if dst.exists():
84:             if digest(read_round(dst)["state"]) != digest(envelope["state"]):
85:                 raise ValueError("Refusing a different second commit for the same round")
86:             return
87:         if t != self.latest()["round"] + 1:
88:             raise ValueError("Round commits must be consecutive")
89:         atomic_json(dst, {**envelope, "state_hash": digest(envelope["state"])}, compressed=True)
90: 
91:     def set_status(self, status, **details):
92:         atomic_json(self.path / "status.json", {"status": status, **details})
93: 
94: 
95: def read_round(path):
96:     path = Path(path)
97:     record = read_json(path)
98:     state = record["state"]
99:     expected_round = int(path.name.split(".")[0])
100:     if state["round"] != expected_round or len(state["round_metrics"]) != expected_round:
101:         raise ValueError("Checkpoint round or cumulative-metrics length mismatch")
102:     if digest(state) != record.get("state_hash"):
103:         raise ValueError("Checkpoint state hash mismatch")
104:     return record
105: 
106: 
107: def _records(path, stop=None):
108:     path = Path(path).resolve(); manifest = read_json(path / "manifest.json")
109:     initial_round = manifest["initial_round"]
110:     if manifest.get("prefix_path"):
111:         prefix = (path / manifest["prefix_path"]).resolve()
112:         yield from _records(prefix, stop=initial_round)
113:     for f in sorted((path / "rounds").glob("*.json.gz")):
114:         t = int(f.name.split(".")[0])
115:         if stop is not None and t > stop: break
116:         yield read_round(f)
117: 
118: 
119: def export_run(run_path, summary, individual):
120:     """Rebuild exports, avoiding duplicate rows even after interruption/restart."""
121:     run_path = Path(run_path)
122:     out = run_path / "exports"; out.mkdir(exist_ok=True)
123:     atomic_json(out / "summary.json", summary)
124:     json_streams = {name: (out / f"{name}.jsonl").open("w", encoding="utf-8", newline="\n")
125:                     for name in ("posts", "exposures", "decisions", "round_metrics")}
126:     state_handle = (out / "states.csv").open("w", encoding="utf-8-sig", newline="")
127:     writer = None
128:     try:
129:         initial = read_json(run_path / "initial.json.gz")
130:         # The base source post appears once, including for a branch export.
131:         source_posts = [p for p in initial["posts"].values() if p.get("kind") == "rumor_original"]
132:         for post in source_posts: json_streams["posts"].write(canonical(post) + "\n")
133:         for rec in _records(run_path):
134:             for name in ("posts", "exposures", "decisions"):
135:                 for row in rec[name]: json_streams[name].write(canonical(row) + "\n")
136:             metrics = rec["state"].get("round_metrics", [])
137:             if metrics: json_streams["round_metrics"].write(canonical(metrics[-1]) + "\n")
138:             for row in rec["states"]:
139:                 if writer is None:
140:                     writer = csv.DictWriter(state_handle, fieldnames=list(row)); writer.writeheader()
141:                 writer.writerow(row)
142:     finally:
143:         state_handle.close()
144:         for handle in json_streams.values(): handle.close()
145:     fields = ["agent_id", "group", "government_round", "first_reject", "event", "duration", "followup_complete"]
146:     with (out / "tbu_individual.csv").open("w", encoding="utf-8-sig", newline="") as f:
147:         writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(individual)
148:     return out
```
