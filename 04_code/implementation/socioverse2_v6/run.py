"""Run a unique, local V4 study using the unmodified upstream engine."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from socioverse.engine import build_simulator
from socioverse.schemas import (StudySpec, EnvironmentBundle, EnvironmentLayer, ScheduledEvent,
    InformationProgram, Broadcast, PopulationBundle, InteractionStructure, SimulationConfig, WarmStartSpec)
from model import load_rows, make_network, targets, dump, digest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "TESTPROJECT/V6_四份交付文件"
UPSTREAM = ROOT / "04_code/third_party_reference/SocioVerse2"
CODE = Path(__file__).resolve().parent
RESULTS = ROOT / "06_experiments/results/socioverse2_v6"
CONFIGS = ROOT / "06_experiments/configs/socioverse2_v6"
LOGS = ROOT / "06_experiments/logs/socioverse2_v6"


from government import validate, select_targets, trust_values


def defaults():
    return dict(contract_status="engineering_only_pending_confirmation", pbd=0.0, gt=.6, rf=.6,
        behavior_seed=20261020, strategy="inside", base_url="https://api.zetatechs.com/v1",
        model="deepseek-v4-flash", max_requests=12200,
        government_tick=8, government_reach=40, targeting_inside_ratio=None,
        government_trust_mean=None, government_trust_sd=.10,
        government_target_seed=20261019, government_trust_seed=20261022,
        tbu_definition="pre_government_tick_believers_first_reject_mean_wait_completers",
        probability_precision="table_values", contact_rule="once_per_tick_correction_priority",
        rule_rebelief=False, direct_relay_same_gt=True,
        comment_target="first_displayed_post", token_guard="cl100k_base_estimate_15percent_plus64",
        runtime_version="v6-adaptive-rolling-6", rate_recovery_successes=20, rate_recovery_seconds=60., rate_limit_max_retries=6,
        rate_limit_wait_seconds=2., rate_limit_max_wait_seconds=60., rate_limit_spacing_seconds=1., max_concurrency=5, format_max_attempts=4, rule_reconsider_rumor=True)


def make_bundles(roster, prompt, cfg, audit, study_id="government-rumor-v6", steps=10, mode="scripted"):
    rows = load_rows(roster)
    env_text = (Path(roster).parent / "03_新环境设定.md").read_text(encoding="utf-8")
    quotes = [line[2:].strip() for line in env_text.splitlines() if line.startswith("> ")]
    if len(quotes) != 2:
        raise ValueError("V4 event paragraphs changed; review extraction before run")
    edges = make_network(rows)
    direct = select_targets(rows, cfg)
    trust = trust_values(rows, cfg)
    tg = cfg["government_tick"]
    study = StudySpec(study_id=study_id, title="V6 政府谣言辟谣：本地混合模型" + ("（离线工程测试）" if mode == "scripted" else "（真实调用）"),
        research_question="在既定关注网络与展示规则下，不同目标范围的政府回应伴随怎样的信念与传播轨迹？本次仅构建inside首跑。",
        n_steps=steps, seed=cfg["behavior_seed"], time_unit="abstract", step_meaning="一轮同步观察与决策，无现实分钟映射",
        key_attributes=["current_belief", "decision_mode", "group"],
        metrics=["remaining_agents", "remaining_llm", "technical_dropout_count", "all_believe", "all_uncertain", "all_reject", "comments", "posts"],
        display_metrics=["remaining_agents", "remaining_llm", "technical_dropout_count"],
        metric_descriptions={"all_believe": "当前相信人数", "all_uncertain": "当前不确定人数", "all_reject": "当前不相信人数",
                             "comments": "累计公开评论数", "posts": "累计帖子数（含原帖与转发）"},
        domain="rumor", tags=["V6", "hybrid", "local"], legacy_simulator="from_scratch",
        provider_refs=["rumor_v6.population", "rumor_v6.environment", "rumor_v6.decision", "rumor_v6.metrics"],
        status="engineering-only", resources_ref=None,
        adjustable_params=["pbd", "gt", "rf", "strategy", "government_tick", "government_reach", "targeting_inside_ratio", "government_trust_mean", "government_trust_sd", "model", "base_url"])
    env = EnvironmentBundle(study_id=study_id, provider_ref="rumor_v6.environment", provider_args={
        "roster_csv": str(roster), "edges": edges, "direct_targets": direct,
        "government_tick": tg, "government_trust": trust,
        "rumor_text": quotes[0], "correction_text": quotes[1], "correction_mode": "scripted_no_evidence", "reread_interval": 3, "max_post_reads": 4},
        layers=[EnvironmentLayer(name=name, modality=mod, scope=scope, dynamics=dyn, description=desc)
                for name, mod, scope, dyn, desc in [
                    ("follow_network", "physical", "local", "static", "5902有向边；关注者到发布者"),
                    ("reading_policy", "physical", "macro", "static", "全部活跃，每轮最多5帖，每帖最多2评论"),
                    ("government_policy", "physical", "macro", "scheduled", f"tick{tg}定向{len(direct)}人，保证首位展示"),
                    ("content_feed", "information", "local", "endogenous", "关注流；新行动下一轮可见"),
                    ("correction_content", "information", "local", "scheduled", "固定实验回应；非真实通告"),
                    ("personal_memory", "information", "local", "endogenous", "最近5次成功经历；不读取他人私态")]],
        scheduled_events=[ScheduledEvent(at_step=tg, target_layer="government_policy", op="set",
                          property_name="enabled", value=True, note="G001一次性定向展示，非全员广播")],
        information_program=InformationProgram(broadcasts=[Broadcast(message_id="G001", content=quotes[1],
            at_step=tg, ttl=1, audience={"agent_ids": direct}, note="scripted_no_evidence；消耗1个阅读名额")]))
    pop = PopulationBundle(study_id=study_id, provider_ref="rumor_v6.population",
        provider_args={"roster_csv": str(roster)}, materialized_count=582,
        interaction=InteractionStructure(kind="explicit_network", edges=edges), propagation="broadcast_then_local")
    sim = SimulationConfig(study_id=study_id, n_steps=steps, seed=cfg["behavior_seed"],
        decision_ref="rumor_v6.decision", decision_args={"config": cfg, "prompt_file": str(prompt),
            "audit_dir": str(audit), "llm_kind": mode}, collector_ref="rumor_v6.metrics",
        interaction_rounds=1, engine_args={"memory_window": 5})
    return study, env, pop, sim


def execute(args):
    if any(getattr(args, k, False) for k in ("retry_policy_migration", "evidence_policy_migration", "dropout_migration", "io_repair_migration")):
        raise ValueError("V6 requires a new experiment; no V4/V5 checkpoint migration")
    if getattr(args, "rate_migration_manifest", None) and not args.resume:
        raise ValueError("Rate migration requires an explicit parent")
    cfg = defaults()
    if args.config:
        cfg.update(json.loads(Path(args.config).read_text(encoding="utf-8")))
    if getattr(args, "concurrency", None) is not None:
        cfg["max_concurrency"] = args.concurrency
    adjustable = {"contract_status", "pbd", "gt", "rf", "behavior_seed", "strategy", "base_url", "model", "max_requests", "api_profile", "rule_reconsider_rumor"}
    adjustable.update({"government_tick", "government_reach", "targeting_inside_ratio", "government_trust_mean", "government_trust_sd", "government_target_seed", "government_trust_seed"})
    adjustable.add("max_concurrency")
    if type(cfg["max_concurrency"]) is not int or not 1 <= cfg["max_concurrency"] <= 10:
        raise ValueError("max_concurrency must be an integer in 1..10")
    validate(cfg)
    for key, val in cfg.items():
        if key not in adjustable and defaults().get(key) != val:
            raise ValueError(f"Unsupported rule change: {key}; implement and test a new version")
    if cfg["pbd"] not in (0, .2, .4) or cfg["rf"] != .6:
        raise ValueError("Use V4 probability table and RF=.6")
    if cfg["strategy"] not in ("inside", "outside", "random") or not 1 <= cfg["max_requests"] <= 12200:
        raise ValueError("invalid strategy or request limit")
    mode = "openai" if args.live else "scripted"
    if cfg.get("api_profile") not in (None, "minimax_m3"):
        raise ValueError("unsupported api_profile")
    if args.live:
        subscription_run = getattr(args, "token_plan_run", False)
        if subscription_run:
            if cfg.get("api_profile") != "minimax_m3" or cfg["base_url"] != "https://api.minimax.cn/v1":
                raise ValueError("Token Plan launch is restricted to the configured MiniMax endpoint")
            if cfg["contract_status"] not in ("confirmed", "authorized_engineering_run"):
                raise ValueError("Token Plan launch needs an explicitly authorized run configuration")
            if not (os.environ.get("RUMOR_LLM_API_KEY") or "").strip().startswith("sk-cp-"):
                raise ValueError("Token Plan launch expects a subscription key (sk-cp-); no pay-as-you-go fallback")
        elif not args.cost_limit_configured or cfg["contract_status"] != "confirmed":
            raise ValueError("Live requires a confirmed contract and --cost-limit-configured; offline remains available")
        if not os.environ.get("RUMOR_LLM_API_KEY"):
            raise ValueError("Set RUMOR_LLM_API_KEY; no paid request made")
        if not 1 <= args.max_requests <= 12200:
            raise ValueError("max_requests must be 1..12200")
        cfg["max_requests"] = args.max_requests  # default20: real-interface smoke, not 40-round claim
    if not 1 <= args.steps <= 40:
        raise ValueError("steps must be 1..40")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    sid = f"government-rumor-v6-{mode}-{stamp}"
    run_dir, audit, config_dir = RESULTS / sid, LOGS / sid, CONFIGS / sid
    run_dir.mkdir(parents=True, exist_ok=False)
    audit.mkdir(parents=True, exist_ok=False)
    config_dir.mkdir(parents=True, exist_ok=False)
    # Local-only frozen inputs. Original materials remain untouched.
    hashes = {}
    for p in SOURCE.iterdir():
        if p.is_file():
            hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
            shutil.copy2(p, config_dir / p.name)
    code_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in CODE.glob("*.py")}
    provenance = dict(input_sha256=hashes, code_sha256=code_hashes, numpy_version=np.__version__, total_steps=args.steps,
        upstream_url="https://github.com/sii-research/SocioVerse2",
        upstream_commit=subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip(),
        mode=mode, dry_run=not args.live, config=cfg, audit_dir=str(audit), config_dir=str(config_dir))
    dump(run_dir / "provenance.json", provenance)
    study, env, pop, simcfg = make_bundles(config_dir / "01_Agent基础信息表.csv",
        config_dir / "02_Prompt固定提示词.md", cfg, audit, sid, args.steps, mode)
    if args.resume:
        parent = Path(args.resume).resolve()
        previous = json.loads((parent / "provenance.json").read_text(encoding="utf-8"))
        migration = getattr(args, "retry_policy_migration", False)
        evidence_migration = getattr(args, "evidence_policy_migration", False)
        manifest_path = getattr(args, "rate_migration_manifest", None)
        if manifest_path:
            manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
            validate_rate_migration(previous, provenance, parent, manifest)
            provenance["engineering_migration"] = manifest
        elif any(previous[k] != provenance[k] for k in ("input_sha256", "code_sha256", "config", "mode", "upstream_commit", "total_steps")):
            raise ValueError("V6 resume requires identical inputs, code, config, mode and upstream")
        completed, replay_file = prepare_replay(parent, run_dir, upto=args.steps)
        if migration and completed != 19:
            raise ValueError("migration requires complete checkpoints through tick19")
        if evidence_migration and completed != 21:
            raise ValueError("evidence migration requires completed tick21")
        if getattr(args, "dropout_migration", False) and completed != 21:
            raise ValueError("dropout migration expects completed tick21")
        simcfg.warm_start = WarmStartSpec(source_version=parent.name,
            source_trajectory=str(replay_file), resume_from=completed)
        shutil.copytree(previous["audit_dir"], audit, dirs_exist_ok=True)
        provenance["resumed_from"] = str(parent)
        provenance["inherited_completed_tick"] = completed
        dump(run_dir / "provenance.json", provenance)
    for name, obj in (("study.yaml", study), ("environment/environment.json", env),
                      ("population/population.json", pop), ("simulation/simulation.json", simcfg)):
        dump(run_dir / name, obj.model_dump(mode="json"))
    dump(config_dir / "behavior_contract.json", cfg)
    dump(config_dir / "network_edges.json", env.provider_args["edges"])
    dump(config_dir / "government_targets.json", env.provider_args["direct_targets"])
    dump(config_dir / "government_trust.json", env.provider_args["government_trust"])
    dump(config_dir / "frozen_input_hashes.json", {"network": digest(env.provider_args["edges"]),
         "government_targets": digest(env.provider_args["direct_targets"]), "behavior_contract": digest(cfg)})
    dump(run_dir / "grounding/grounding.json", {"method_notes": "V4用户指定工程模型，合成网络；实验性纠正文本。",
        "assumptions": [{"id": "pending-rule-contract", "claim": cfg["contract_status"]}]})
    shutil.copy2(CODE / "model.py", run_dir / "model.py")
    state = {"status": "running", "last_completed_tick": 0, "dry_run": not args.live}
    metrics = []
    def on_step(t, m):
        metrics.append(m)
        dump(run_dir / "reports" / "technical_dropout.json", {"tick":t,
             "remaining_agents":m.get("remaining_agents"), "remaining_llm":m.get("remaining_llm"),
             "technical_dropout_count":m.get("technical_dropout_count"),
             "offline_agents":simulator.env.offline})
        # Durable whole-tick action checkpoint. Independent of open DuckDB/WAL files.
        records = simulator.store._con.execute(
            "SELECT agent_id, action_kind, action_payload FROM panel WHERE step=? ORDER BY agent_id", [t]).fetchall()
        if t > 0 and len(records) != 582:
            raise ValueError("refusing incomplete tick checkpoint")
        if t > 0:
            actions = [{"agent_id": aid, "step": t, "action_kind": kind,
                        "action_payload": json.loads(payload)} for aid, kind, payload in records]
            dump(run_dir / "checkpoints" / f"tick-{t:03d}.json", {"actions": actions, "sha256": digest(actions)})
        state["last_completed_tick"] = t
        dump(run_dir / "status.json", state)
        dump(run_dir / "trajectory/metrics_history.json", {"study_id": sid, "rows": metrics})
        print(f"tick {t}/{args.steps}: believe={m['all_believe']} reject={m['all_reject']} remaining={m['remaining_agents']} dropout={m['technical_dropout_count']}", flush=True)
    simulator = build_simulator(env_bundle=env, pop_bundle=pop, sim_config=simcfg,
        store_path=run_dir / "trajectory/study.duckdb", on_step=on_step)
    personas, initial = simulator.materialize_initial()
    (run_dir / "population/roster.jsonl").write_text(
        "\n".join(p.model_dump_json() for p in personas) + "\n", encoding="utf-8")
    dump(config_dir / "initial_state.json", [r.model_dump() for r in initial])
    dump(run_dir / "status.json", state)
    failed = None
    try:
        history = simulator.run()
        state["status"] = "completed_offline" if not args.live else "completed_live"
        dump(run_dir / "trajectory/metrics_history.json", history.model_dump())
    except (Exception, KeyboardInterrupt) as exc:
        failed = exc
        import traceback
        dump(run_dir / "failure_diagnostic.json", {
            "type":type(exc).__name__, "filename":getattr(exc,"filename",None),
            "filename2":getattr(exc,"filename2",None), "errno":getattr(exc,"errno",None), "winerror":getattr(exc,"winerror",None),
            "frames":[{"file":f.filename,"line":f.lineno,"function":f.name} for f in traceback.extract_tb(exc.__traceback__)]})
        state["status"] = "paused_quota" if type(exc).__name__ == "QuotaPause" else "interrupted"
        state["error_type"] = type(exc).__name__
        # Finalize only committed panel rows; never label failed tick completed.
        if simulator.store._con is not None:
            simulator.store.finalize()
    finally:
        dump(run_dir / "status.json", state)
        snapshot = simulator.env.snapshot()
        snapshot["last_completed_tick"] = state["last_completed_tick"]
        snapshot["note"] = "May include scheduled exogenous update for attempted tick; resume replays committed DB actions."
        dump(run_dir / "trajectory/final_snapshot.json", snapshot)
        dump(RESULTS / "latest.json", {"run_dir": str(run_dir), **state})
    import duckdb
    con = duckdb.connect(str(run_dir / "trajectory/study.duckdb"), read_only=True)
    panel = con.execute("SELECT * FROM panel ORDER BY step, agent_id").df()
    con.close()
    panel.to_csv(run_dir / "trajectory/panel.csv", index=False, encoding="utf-8-sig")
    report = (f"# V4 本地运行\n\n状态：{state['status']}。最后完整轮次：{state['last_completed_tick']}。\n\n"
        f"582人，305名LLM角色、277名规则角色。运行模式：{mode}；panel共{len(panel)}行（含tick0）。\n\n"
        "离线模式中的LLM角色使用固定测试回答，不能解释为LLM行为或辟谣效果。G001是研究者脚本，不是真实官方通告。\n\n"
        f"规则合同状态：{cfg['contract_status']}。TBU仅按工程候选口径输出。\n\n"
        "原始四文件及哈希、边表、投放名单、初态已冻结；provenance.json记录位置。\n")
    (run_dir / "reports").mkdir(exist_ok=True)
    (run_dir / "reports/report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), **state}, ensure_ascii=False), flush=True)
    if failed:
        raise RuntimeError(f"Run interrupted ({type(failed).__name__}); inspect local logs; no fallback") from None
    return run_dir


def validate_rate_migration(previous, current, parent, manifest):
    if str(parent.resolve()) != manifest["parent_run"]:
        raise ValueError("Rate migration parent mismatch")
    if previous["code_sha256"] != manifest["old_code_sha256"] or current["code_sha256"] != manifest["new_code_sha256"]:
        raise ValueError("Rate migration code hash mismatch")
    if previous["config"] != manifest["old_config"] or current["config"] != manifest["new_config"]:
        raise ValueError("Rate migration configuration mismatch")
    for key in ("input_sha256", "mode", "dry_run", "upstream_commit", "upstream_url", "numpy_version", "total_steps"):
        if previous[key] != current[key]:
            raise ValueError("Rate migration cannot change " + key)
    allowed = {"runtime_version", "rate_limit_max_retries", "rate_limit_wait_seconds",
               "rate_limit_max_wait_seconds", "rate_limit_spacing_seconds"}
    for key in previous["config"].keys() | current["config"].keys():
        if key not in allowed and previous["config"].get(key) != current["config"].get(key):
            raise ValueError("Rate migration cannot change research/budget configuration: " + key)


def validate_retry_migration(previous, current, parent_name, manifest):
    if parent_name != manifest["parent_run"]:
        raise ValueError("retry migration only applies to the explicitly authorized parent")
    for key in ("input_sha256", "mode", "upstream_commit", "numpy_version"):
        if previous[key] != current[key]:
            raise ValueError("migration cannot change source/model environment")
    expected = {**previous["config"], "format_max_attempts": 4}
    if expected != current["config"]:
        raise ValueError("migration may only add the four-generation retry policy")
    if previous["code_sha256"] != manifest["parent_code_sha256"] or current["code_sha256"] != manifest["target_code_sha256"]:
        raise ValueError("migration code hashes differ from the reviewed version")
    if previous["code_sha256"]["model.py"] != current["code_sha256"]["model.py"]:
        raise ValueError("environment and behavioral rules must remain unchanged")


def prepare_replay(parent, destination, upto=40):
    """Only contiguous, checksummed, complete ticks can enter a recovery replay."""
    completed = 0
    lines = []
    for tick in range(1, upto + 1):
        path = parent / "checkpoints" / f"tick-{tick:03d}.json"
        if not path.exists():
            break
        data = json.loads(path.read_text(encoding="utf-8"))
        actions = data["actions"]
        if digest(actions) != data["sha256"] or len(actions) != 582:
            raise ValueError("checkpoint checksum/count mismatch")
        if {a["agent_id"] for a in actions} != {f"A{i:04d}" for i in range(1, 583)} or any(a["step"] != tick for a in actions):
            raise ValueError("checkpoint population/tick mismatch")
        lines.extend(json.dumps(a, ensure_ascii=True) for a in actions)
        completed = tick
    replay_file = destination / "recovery_actions.jsonl"
    replay_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return completed, replay_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, choices=range(1, 11), help="Execution concurrency only; no research rule changes")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--config")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--cost-limit-configured", action="store_true")
    parser.add_argument("--token-plan-run", action="store_true", help="Authorize subscription quota use; does not assert a currency cap")
    parser.add_argument("--max-requests", type=int, default=20)
    parser.add_argument("--io-repair-migration", action="store_true")
    parser.add_argument("--dropout-migration", action="store_true")
    parser.add_argument("--rate-migration-manifest", help="Reviewed exact-parent/code-hash rate policy migration")
    parser.add_argument("--resume", help="parent run directory; exact same input/code/config required")
    parser.add_argument("--evidence-policy-migration", action="store_true")
    parser.add_argument("--retry-policy-migration", action="store_true", help="Reviewed one-time migration; replay through19, continue20")
    args = parser.parse_args()
    # Windows process lock prevents two launchers spending the same run budget concurrently.
    import msvcrt
    lock_path = CODE / ".simulation.lock"
    with open(lock_path, "a+b") as lock:
        if lock.tell() == 0:
            lock.write(b"0")
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise SystemExit("Another simulation is running; do not launch a second copy")
        try:
            execute(args)
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == "__main__":
    main()
