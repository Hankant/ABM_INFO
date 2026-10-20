"""Deterministic synthetic extensions; never infer psychological facts from demographics."""
import csv
import hashlib
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "04_code/implementation/socioverse2-contest/research_archive/inputs/01_Agent基础信息表.csv"
DEST = ROOT / "TESTPROJECT/V6_四份交付文件"
SEED = 20261021
TRAITS = ("sharing_propensity", "verification_preference", "source_prior",
          "government_prior", "repetition_sensitivity")


def generate(rows):
    rows = [dict(r) for r in rows]
    people = [r for r in rows if r["decision_mode"] == "llm"]
    rng = np.random.Generator(np.random.PCG64(SEED))
    normal = NormalDist(.5, .18)
    lo, hi = normal.cdf(.05), normal.cdf(.95)
    # Stratified quantiles of a truncated normal, not uniformly distributed values.
    values = [round(normal.inv_cdf(lo + (i+.5)/len(people)*(hi-lo)), 6)
              for i in range(len(people))]
    for trait in TRAITS:
        assigned = rng.permutation(values)
        for r, v in zip(people, assigned):
            r[trait] = str(v)
    # Account volume is NOT a measured sharing rate. Use it only as a weak,
    # explicitly synthetic assignment constraint, with seeded noise dominating.
    counts = sorted({float(r["statuses_count"]) for r in people if r["statuses_count"].strip()})
    rank = {v: (i+.5)/len(counts) for i, v in enumerate(counts)}
    scored = [(0.25*rank.get(float(r["statuses_count"]) if r["statuses_count"].strip() else None, .5)
               + .75*rng.random(), r) for r in people]
    for value, (_, r) in zip(values, sorted(scored, key=lambda x: (x[0], x[1]["agent_id"]))):
        r["sharing_propensity"] = str(value)
    histories = [
        "合成背景：过去更常旁观社会话题，很少公开表达；不是该账户的已核实经历。",
        "合成背景：过去会把感兴趣的社会话题发给他人讨论或求证；不是该账户的已核实经历。",
        "合成背景：过去曾在分享消息后见到不同说法，逐渐留意消息来源；不是该账户的已核实经历。",
    ]
    order = rng.permutation(len(people))
    for j, index in enumerate(order):
        r = people[index]
        r["synthetic_pre_event_experience"] = histories[j % 3]
    for r in rows:
        if r["decision_mode"] != "llm":
            continue
        r["synthetic_sharing_habit"] = (
            f"合成分享倾向{r['sharing_propensity']}（0低1高）；可为表达、讨论、求证而转发，"
            "并非每次必须转发。")
        r["synthetic_source_evaluation"] = f"合成初始来源接受倾向{r['source_prior']}，不代表已核实信任。"
        r["synthetic_government_evaluation"] = f"合成初始政府来源接受倾向{r['government_prior']}，仍可审查具体证据。"
        r["synthetic_persona_basis"] = (
            "V6 researcher_assigned; seed=20261021; bounded_normal(mu=.5,sigma=.18,range=.05:.95); "
            "sharing assignment=.25 account-status-rank+.75 seeded-noise; other traits independently shuffled; "
            "no psychology inferred from sex/location; synthetic history balanced 102/102/101")
        r["persona_version"] = "V6-synthetic"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    return rows, fields


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        original = list(csv.DictReader(f))
    rows, fields = generate(original)
    DEST.mkdir(parents=True, exist_ok=True)
    with (DEST / "01_Agent基础信息表.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    output = ROOT / "06_experiments/configs/socioverse2_v6/persona_generation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "seed": SEED, "synthetic": True, "n_llm": 305, "n_rule": 277,
        "distribution": "stratified quantiles of truncated N(.5,.18^2), [.05,.95]",
        "traits": TRAITS, "not_inferred": ["real personal history", "true belief", "real sharing rate"],
        "assignment": "sharing: 25% account statuses rank + 75% seeded noise; others independent permutations",
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
