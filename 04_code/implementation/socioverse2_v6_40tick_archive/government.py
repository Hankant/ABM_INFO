"""Explicit government experiment parameters; deterministic matched assignments."""
from statistics import NormalDist
import numpy as np


def validate(cfg):
    if type(cfg["government_tick"]) is not int or not 1 <= cfg["government_tick"] <= 40:
        raise ValueError("government_tick must be an integer in 1..40")
    if type(cfg["government_reach"]) is not int or not 0 <= cfg["government_reach"] <= 582:
        raise ValueError("government_reach must be an integer in 0..582")
    ratio = cfg["targeting_inside_ratio"]
    if ratio is not None and (not 0 <= ratio <= 1 or
            abs(cfg["government_reach"] * ratio - round(cfg["government_reach"] * ratio)) > 1e-9):
        raise ValueError("targeting ratio must yield an exact integer inside count")
    mu = cfg["government_trust_mean"]
    if mu is not None and not 0 <= mu <= 1:
        raise ValueError("government_trust_mean must be in 0..1 or null")
    if not 0 <= cfg["government_trust_sd"] <= .5:
        raise ValueError("government_trust_sd must be in 0..0.5")
    if not 0 <= cfg["gt"] <= 1:
        raise ValueError("gt must be in 0..1")


def select_targets(rows, cfg):
    validate(cfg)
    rng = np.random.Generator(np.random.PCG64(cfg["government_target_seed"]))
    n, ratio = cfg["government_reach"], cfg["targeting_inside_ratio"]
    if ratio is None:
        pool = [r["agent_id"] for r in rows
                if cfg["strategy"] == "random" or r["group"] == cfg["strategy"]]
        if len(pool) < n:
            raise ValueError("target pool smaller than government_reach; no silent reduction")
        return sorted(map(str, rng.choice(pool, n, replace=False)))
    count = round(n * ratio)
    chosen = []
    for group, size in (("inside", count), ("outside", n-count)):
        pool = [r["agent_id"] for r in rows if r["group"] == group]
        if size > len(pool):
            raise ValueError(f"{group} population too small for requested targeting count")
        chosen.extend(map(str, rng.choice(pool, size, replace=False)))
    return sorted(chosen)


def trust_values(rows, cfg):
    mu, sd = cfg["government_trust_mean"], cfg["government_trust_sd"]
    if mu is None:
        return {}  # Preserve fixed GT for rules and existing synthetic LLM persona.
    rng = np.random.Generator(np.random.PCG64(cfg["government_trust_seed"]))
    result = {}
    # Symmetric truncated quantiles preserve the requested mean in each decision group.
    for mode in ("llm", "rule"):
        ids = sorted(r["agent_id"] for r in rows if r["decision_mode"] == mode)
        if sd == 0 or mu in (0, 1):
            values = [mu] * len(ids)
        else:
            normal = NormalDist(mu, sd)
            width = min(mu, 1-mu)
            lo, hi = normal.cdf(mu-width), normal.cdf(mu+width)
            values = [normal.inv_cdf(lo+(i+.5)/len(ids)*(hi-lo)) for i in range(len(ids))]
        for aid, val in zip(ids, rng.permutation(values)):
            result[aid] = float(val)
    return result
