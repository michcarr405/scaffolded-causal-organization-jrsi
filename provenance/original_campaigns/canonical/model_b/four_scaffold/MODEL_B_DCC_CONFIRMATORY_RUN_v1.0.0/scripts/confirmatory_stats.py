from __future__ import annotations
import math
import numpy as np
from scipy.stats import binomtest

ANALYSIS_ROOT_SEED = 145617781


def _seeded_rng(*keys):
    import hashlib
    payload = "\x1f".join(str(k) for k in keys).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    entropy = [ANALYSIS_ROOT_SEED] + [int.from_bytes(digest[i:i+4], "little") for i in range(0, 32, 4)]
    return np.random.default_rng(np.random.SeedSequence(entropy))


def paired_effect(selected, neutral):
    s = np.asarray(selected, dtype=float).reshape(-1)
    n = np.asarray(neutral, dtype=float).reshape(-1)
    if len(s) != len(n) or len(s) < 1:
        raise ValueError("paired vectors must have equal nonzero length")
    return s - n


def mean_bootstrap_ci(values, *, ci=0.95, n_boot=50000, key="default"):
    v = np.asarray(values, dtype=float).reshape(-1)
    if len(v) < 1:
        raise ValueError("empty values")
    rng = _seeded_rng("paired-block-bootstrap", key, len(v), n_boot, ci)
    idx = rng.integers(0, len(v), size=(int(n_boot), len(v)))
    b = v[idx].mean(axis=1)
    alpha = (1.0 - float(ci)) / 2.0
    lo, hi = np.quantile(b, [alpha, 1.0 - alpha])
    return {
        "n": int(len(v)),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "ci": float(ci),
        "low": float(lo),
        "high": float(hi),
        "n_boot": int(n_boot),
    }


def exact_one_sided_sign_test(values):
    v = np.asarray(values, dtype=float).reshape(-1)
    n = int(len(v))
    if n < 1:
        raise ValueError("empty values")
    k = int(np.sum(v > 0))
    # Exact zero is deliberately counted as nonpositive because n includes all entries.
    p = float(binomtest(k, n=n, p=0.5, alternative="greater").pvalue)
    return {"n": n, "positive": k, "nonpositive": n-k, "p_value": p}


def holm_adjust(p_values):
    p = np.asarray(p_values, dtype=float).reshape(-1)
    if np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must lie in [0,1]")
    m = len(p)
    order = np.argsort(p)
    out = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * p[idx]
        running = max(running, val)
        out[idx] = min(1.0, running)
    return out


def stratified_pooled_bootstrap(mapping_values: dict[str, np.ndarray], *, ci=0.95, n_boot=50000, key="pooled"):
    names = list(mapping_values)
    arrays = [np.asarray(mapping_values[n], dtype=float).reshape(-1) for n in names]
    if not arrays or any(len(a) < 1 for a in arrays):
        raise ValueError("all strata must be nonempty")
    rng = _seeded_rng("stratified-bootstrap", key, tuple((n, len(a)) for n, a in zip(names, arrays)), n_boot, ci)
    vals = np.empty(int(n_boot), dtype=float)
    for b in range(int(n_boot)):
        means = []
        for a in arrays:
            idx = rng.integers(0, len(a), size=len(a))
            means.append(float(a[idx].mean()))
        vals[b] = float(np.mean(means))
    alpha = (1.0 - float(ci)) / 2.0
    lo, hi = np.quantile(vals, [alpha, 1.0-alpha])
    point = float(np.mean([a.mean() for a in arrays]))
    return {"mean": point, "ci": float(ci), "low": float(lo), "high": float(hi), "n_boot": int(n_boot), "n_strata": len(arrays)}
