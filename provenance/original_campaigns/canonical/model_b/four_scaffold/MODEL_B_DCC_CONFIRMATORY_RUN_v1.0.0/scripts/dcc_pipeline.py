from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np
from numba import njit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "source"
import sys
sys.path.insert(0, str(SRC))

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.core import compute_fitnesses_and_observations
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator

N_MOTIFS = 4 ** 5
N_STATES = 4
N_SEGMENTS = 4
CHECKPOINTS = (0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250)
PROBE_MAPPINGS = (
    (2, 0, 3, 1),
    (0, 1, 2, 3),
    (1, 3, 0, 2),
    (3, 2, 1, 0),
)
PROBE_IDS = ("SCF0", "SCF1", "SCF2", "SCF3")
N_PROBE_DRAWS = 16
N_UNIT_SHUFFLES = 128
N_GENS = 250
P_INHERIT = 0.975
BETA = 4.0
THETA = 1.2
MU = 0.001


def state_hash(pop: np.ndarray) -> str:
    a = np.ascontiguousarray(pop)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(b"|")
    h.update(("x".join(str(x) for x in a.shape)).encode("ascii"))
    h.update(b"|")
    h.update(a.tobytes(order="C"))
    return h.hexdigest()


def motif_tensor(pop: np.ndarray) -> np.ndarray:
    pop = np.asarray(pop, dtype=np.int64)
    if pop.ndim != 3 or pop.shape[-1] < 5:
        raise ValueError("population must have shape (cells, seqs, seq_len>=5)")
    w = np.lib.stride_tricks.sliding_window_view(pop, 5, axis=-1)
    powers = np.asarray([256, 64, 16, 4, 1], dtype=np.int64)
    return np.tensordot(w, powers, axes=([-1], [0])).astype(np.int64, copy=False)


def position_segment_labels(chain_len: int = 56, n_segments: int = 4) -> np.ndarray:
    if chain_len % n_segments != 0:
        raise ValueError("equal segment lengths required")
    return np.repeat(np.arange(n_segments, dtype=np.int64), chain_len // n_segments)


def population_segment_labels(pop_shape=(80, 8, 60)) -> np.ndarray:
    n_cells, n_seqs, seq_len = pop_shape
    pos = position_segment_labels(seq_len - 4, N_SEGMENTS)
    return np.tile(pos, n_cells * n_seqs)


def unit_segment_labels(n_seqs: int = 8, seq_len: int = 60) -> np.ndarray:
    return np.tile(position_segment_labels(seq_len - 4, N_SEGMENTS), n_seqs)


def motif_segment_counts_from_motifs(motifs3: np.ndarray) -> np.ndarray:
    m = np.asarray(motifs3, dtype=np.int64)
    seg = position_segment_labels(m.shape[-1], N_SEGMENTS)
    flat_m = m.reshape(-1)
    flat_s = np.broadcast_to(seg, m.shape).reshape(-1)
    idx = flat_s * N_MOTIFS + flat_m
    return np.bincount(idx, minlength=N_SEGMENTS * N_MOTIFS).reshape(N_SEGMENTS, N_MOTIFS).astype(np.int64)


def motif_segment_counts(pop: np.ndarray) -> np.ndarray:
    return motif_segment_counts_from_motifs(motif_tensor(pop))


def make_kernel(affinity: np.ndarray, mapping: Iterable[int], beta: float = BETA, temperature: float = THETA) -> np.ndarray:
    mapping = tuple(int(x) for x in mapping)
    if len(mapping) != N_SEGMENTS:
        raise ValueError("mapping length must equal n_segments")
    logits = np.broadcast_to(np.asarray(affinity, dtype=np.float64)[None, :, :], (N_SEGMENTS, N_MOTIFS, N_STATES)).copy()
    for s, fav in enumerate(mapping):
        logits[s, :, fav] += float(beta)
    x = logits / float(temperature)
    x -= x.max(axis=2, keepdims=True)
    ex = np.exp(x)
    return ex / ex.sum(axis=2, keepdims=True)


def jsd_bits(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64).reshape(-1)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    if np.any(p < 0) or np.any(q < 0):
        raise ValueError("probabilities must be nonnegative")
    sp = float(p.sum())
    sq = float(q.sum())
    if sp <= 0 or sq <= 0:
        raise ValueError("probabilities must have positive mass")
    p = p / sp
    q = q / sq
    m = 0.5 * (p + q)
    mp = p > 0
    mq = q > 0
    klp = np.sum(p[mp] * np.log2(p[mp] / m[mp]))
    klq = np.sum(q[mq] * np.log2(q[mq] / m[mq]))
    return float(0.5 * (klp + klq))


def c_down_from_counts(counts: np.ndarray, kernel: np.ndarray) -> dict:
    counts = np.asarray(counts, dtype=np.int64)
    if counts.shape != (N_SEGMENTS, N_MOTIFS):
        raise ValueError("counts shape mismatch")
    total = int(counts.sum())
    if total <= 0:
        raise ValueError("counts must have positive mass")
    p_sm = counts.astype(np.float64) / total
    p_s = p_sm.sum(axis=1, keepdims=True)
    p_m = p_sm.sum(axis=0, keepdims=True)
    erased = p_s @ p_m
    intact_sz = np.einsum("sm,smz->sz", p_sm, kernel)
    erased_sz = np.einsum("sm,smz->sz", erased, kernel)
    return {
        "jsd_bits": jsd_bits(intact_sz, erased_sz),
        "p_sm": p_sm,
        "p_sm_erased": erased,
        "p_sz_intact": intact_sz,
        "p_sz_erased": erased_sz,
        "motif_marginal_error": float(np.max(np.abs(erased.sum(axis=0) - p_m.reshape(-1)))),
        "segment_marginal_error": float(np.max(np.abs(erased.sum(axis=1) - p_s.reshape(-1)))),
    }


def c_down_primary(pop: np.ndarray, affinity: np.ndarray, mapping: Iterable[int], beta: float = BETA, temperature: float = THETA) -> dict:
    counts = motif_segment_counts(pop)
    kernel = make_kernel(affinity, mapping, beta, temperature)
    return c_down_from_counts(counts, kernel)


def unitshuffle_cdown(
    pop: np.ndarray,
    affinity: np.ndarray,
    mapping: Iterable[int],
    root_seed: int,
    n_shuffles: int = N_UNIT_SHUFFLES,
    beta: float = BETA,
    temperature: float = THETA,
    return_values: bool = False,
) -> dict:
    motifs3 = motif_tensor(pop)
    n_cells, n_seqs, chain_len = motifs3.shape
    unit_motifs = motifs3.reshape(n_cells, n_seqs * chain_len)
    useg = unit_segment_labels(n_seqs=n_seqs, seq_len=chain_len + 4)
    all_seg = np.broadcast_to(useg, unit_motifs.shape).reshape(-1)
    kernel = make_kernel(affinity, mapping, beta, temperature)
    intact_counts = motif_segment_counts_from_motifs(motifs3)
    intact = c_down_from_counts(intact_counts, kernel)["p_sz_intact"]
    vals = np.empty(int(n_shuffles), dtype=np.float64)
    global_before = np.bincount(unit_motifs.reshape(-1), minlength=N_MOTIFS)
    seg_sizes_before = intact_counts.sum(axis=1)
    max_global_motif_error = 0
    max_segment_size_error = 0
    rng = make_generator(int(root_seed), "confirmatory-unitshuffle")
    for k in range(int(n_shuffles)):
        shuffled = rng.permuted(unit_motifs, axis=1)
        flat_m = shuffled.reshape(-1)
        idx = all_seg * N_MOTIFS + flat_m
        counts = np.bincount(idx, minlength=N_SEGMENTS * N_MOTIFS).reshape(N_SEGMENTS, N_MOTIFS).astype(np.int64)
        max_global_motif_error = max(max_global_motif_error, int(np.max(np.abs(counts.sum(axis=0) - global_before))))
        max_segment_size_error = max(max_segment_size_error, int(np.max(np.abs(counts.sum(axis=1) - seg_sizes_before))))
        p_sm = counts.astype(np.float64) / int(counts.sum())
        p_sz = np.einsum("sm,smz->sz", p_sm, kernel)
        vals[k] = jsd_bits(intact, p_sz)
    out = {
        "mean_jsd_bits": float(vals.mean()),
        "sd_jsd_bits": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
        "n_shuffles": int(n_shuffles),
        "max_global_motif_count_error": int(max_global_motif_error),
        "max_segment_size_error": int(max_segment_size_error),
    }
    if return_values:
        out["values"] = vals
    return out


def mapping_cdf_table(affinity: np.ndarray, mappings=PROBE_MAPPINGS, beta: float = BETA, temperature: float = THETA) -> np.ndarray:
    table = np.empty((len(mappings), N_SEGMENTS, N_MOTIFS, N_STATES), dtype=np.float64)
    for i, mapping in enumerate(mappings):
        table[i] = np.cumsum(make_kernel(affinity, mapping, beta, temperature), axis=2)
    table[:, :, :, -1] = 1.0
    return table


@njit
def probe_mapping_fitnesses_from_motifs(motifs3, cdf_table, productive, anti, reward, penalty, uniforms):
    n_maps = cdf_table.shape[0]
    n_draws = uniforms.shape[0]
    n_cells, n_seqs, chain_len = motifs3.shape
    seg_len = chain_len // 4
    out = np.empty((n_maps, n_draws), dtype=np.float64)
    for mp in range(n_maps):
        for d in range(n_draws):
            total_fit = 0.0
            obs_idx = 0
            for ci in range(n_cells):
                prod_sum = 0.0
                anti_sum = 0.0
                for si in range(n_seqs):
                    prev = -1
                    for pos in range(chain_len):
                        seg = pos // seg_len
                        if seg >= 4:
                            seg = 3
                        motif = motifs3[ci, si, pos]
                        u = uniforms[d, obs_idx]
                        obs_idx += 1
                        c0 = cdf_table[mp, seg, motif, 0]
                        c1 = cdf_table[mp, seg, motif, 1]
                        c2 = cdf_table[mp, seg, motif, 2]
                        if u <= c0:
                            chosen = 0
                        elif u <= c1:
                            chosen = 1
                        elif u <= c2:
                            chosen = 2
                        else:
                            chosen = 3
                        if pos > 0:
                            if productive[prev, chosen]:
                                prod_sum += 1.0
                            if anti[prev, chosen]:
                                anti_sum += 1.0
                        prev = chosen
                mean_prod = prod_sum / n_seqs
                mean_anti = anti_sum / n_seqs
                fit = 1.0 + reward * mean_prod - penalty * mean_anti
                if fit < 0.1:
                    fit = 0.1
                total_fit += fit
            out[mp, d] = total_fit / n_cells
    return out


def cross_evaluate(pop: np.ndarray, params: dict, root_seed: int, mappings=PROBE_MAPPINGS, n_draws: int = N_PROBE_DRAWS, uniforms: np.ndarray | None = None) -> dict:
    motifs3 = motif_tensor(pop)
    if uniforms is None:
        rng = make_generator(int(root_seed), "confirmatory-cross-eval")
        uniforms = rng.random((int(n_draws), motifs3.size))
    else:
        uniforms = np.asarray(uniforms, dtype=np.float64)
        if uniforms.shape != (int(n_draws), motifs3.size):
            raise ValueError("cross-evaluation uniform shape mismatch")
    cdf = mapping_cdf_table(params["motif_affinity_matrix"], mappings, params["bias_strength"], params["temperature"])
    vals = probe_mapping_fitnesses_from_motifs(
        motifs3,
        cdf,
        params["productive_pairs"],
        params["anti_pairs"],
        float(params["reward_strength"]),
        float(params["penalty_strength"]),
        uniforms,
    )
    means = vals.mean(axis=1)
    return {
        "mapping_means": means,
        "draw_values": vals,
        "uniforms": uniforms,
    }


def historical_match_score(mapping_means: np.ndarray, historical_index: int) -> float:
    m = np.asarray(mapping_means, dtype=np.float64).reshape(-1)
    if len(m) != 4:
        raise ValueError("historical score requires four mappings")
    other = np.delete(m, int(historical_index))
    return float(m[int(historical_index)] - other.mean())


def observe(pop: np.ndarray, params: dict, rng: np.random.Generator):
    n_windows = int(params["n_cells"] * params["n_seqs"] * (params["seq_len"] - 4))
    u = rng.random(n_windows)
    return compute_fitnesses_and_observations(
        pop,
        params["motif_affinity_matrix"],
        params["segment_favored_met"],
        params["bias_strength"],
        params["productive_pairs"],
        params["anti_pairs"],
        params["reward_strength"],
        params["penalty_strength"],
        params["temperature"],
        u,
    )


def parse_mapping_text(text: str) -> tuple[int, int, int, int]:
    x = json.loads(text)
    return tuple(int(v) for v in x)


def scaffold_index(scaffold_id: str) -> int:
    return PROBE_IDS.index(str(scaffold_id))


def make_params(mapping: Iterable[int]) -> dict:
    p = default_parameters()
    p["segment_favored_met"] = np.asarray(tuple(mapping), dtype=np.int64)
    p["bias_strength"] = BETA
    p["temperature"] = THETA
    p["mutation_rate"] = MU
    p["n_gens"] = N_GENS
    return p


def _write_metrics_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _write_json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def run_pair_block(pair: dict, outdir: Path, validation_version: str = "v1.0.0") -> dict:
    block_id = str(pair["paired_block_id"])
    scaffold_id = str(pair["scaffold_id"])
    mapping = parse_mapping_text(str(pair["scaffold_mapping"]))
    seed = int(pair["base_seed_uint32"])
    sel_run = str(pair["selected_run_id"])
    neu_run = str(pair["neutral_run_id"])
    hist_idx = scaffold_index(scaffold_id)
    params = make_params(mapping)
    affinity = params["motif_affinity_matrix"]

    init_rng = make_generator(seed, "baseline-initialization")
    pop0 = init_population(params["n_cells"], params["n_seqs"], params["seq_len"], init_rng)
    pop_sel = pop0.copy()
    pop_neu = pop0.copy()

    obs_sel = make_generator(seed, "baseline-observation")
    obs_neu = make_generator(seed, "baseline-observation")
    prop_sel = make_generator(seed, "baseline-propagation")
    prop_neu = make_generator(seed, "baseline-propagation")

    metrics = {"selected": [], "neutral": []}
    for g in range(N_GENS + 1):
        fit_s, _, _ = observe(pop_sel, params, obs_sel)
        fit_n, _, _ = observe(pop_neu, params, obs_neu)
        if g in CHECKPOINTS:
            cds = c_down_primary(pop_sel, affinity, mapping, BETA, THETA)
            cdn = c_down_primary(pop_neu, affinity, mapping, BETA, THETA)
            metrics["selected"].append({
                "run_id": sel_run,
                "paired_block_id": block_id,
                "scaffold_id": scaffold_id,
                "mode": "selected",
                "base_seed_uint32": seed,
                "generation": g,
                "mean_fitness": float(fit_s.mean()),
                "C_down_primary": float(cds["jsd_bits"]),
                "population_hash": state_hash(pop_sel),
                "validation_version": validation_version,
            })
            metrics["neutral"].append({
                "run_id": neu_run,
                "paired_block_id": block_id,
                "scaffold_id": scaffold_id,
                "mode": "neutral",
                "base_seed_uint32": seed,
                "generation": g,
                "mean_fitness": float(fit_n.mean()),
                "C_down_primary": float(cdn["jsd_bits"]),
                "population_hash": state_hash(pop_neu),
                "validation_version": validation_version,
            })
        if g < N_GENS:
            pop_sel = reproduce_with_partitioning(pop_sel, fit_s, params["mutation_rate"], P_INHERIT, prop_sel)
            pop_neu = reproduce_with_partitioning(pop_neu, np.ones_like(fit_n), params["mutation_rate"], P_INHERIT, prop_neu)

    # Cross-evaluation uses one common uniform array for all four mappings and both modes.
    cross_rng = make_generator(seed, "confirmatory-cross-eval")
    n_windows = int(params["n_cells"] * params["n_seqs"] * (params["seq_len"] - 4))
    common_u = cross_rng.random((N_PROBE_DRAWS, n_windows))
    ce_sel = cross_evaluate(pop_sel, params, seed, PROBE_MAPPINGS, N_PROBE_DRAWS, uniforms=common_u)
    ce_neu = cross_evaluate(pop_neu, params, seed, PROBE_MAPPINGS, N_PROBE_DRAWS, uniforms=common_u)
    h_sel = historical_match_score(ce_sel["mapping_means"], hist_idx)
    h_neu = historical_match_score(ce_neu["mapping_means"], hist_idx)

    alt_sel = unitshuffle_cdown(pop_sel, affinity, mapping, seed, N_UNIT_SHUFFLES, BETA, THETA, return_values=False)
    alt_neu = unitshuffle_cdown(pop_neu, affinity, mapping, seed, N_UNIT_SHUFFLES, BETA, THETA, return_values=False)
    if alt_sel["max_global_motif_count_error"] != 0 or alt_sel["max_segment_size_error"] != 0:
        raise RuntimeError(f"unitshuffle invariant failed for {sel_run}")
    if alt_neu["max_global_motif_count_error"] != 0 or alt_neu["max_segment_size_error"] != 0:
        raise RuntimeError(f"unitshuffle invariant failed for {neu_run}")

    final_hash_sel = state_hash(pop_sel)
    final_hash_neu = state_hash(pop_neu)
    ancestor_hash = state_hash(pop0)

    run_endpoints = {
        "selected": {
            "run_id": sel_run,
            "paired_block_id": block_id,
            "scaffold_id": scaffold_id,
            "scaffold_mapping": list(mapping),
            "mode": "selected",
            "base_seed_uint32": seed,
            "C_down_primary_g250": float(metrics["selected"][-1]["C_down_primary"]),
            "C_down_unitshuffle_g250": float(alt_sel["mean_jsd_bits"]),
            "C_down_unitshuffle_sd": float(alt_sel["sd_jsd_bits"]),
            "cross_eval_mapping_means": {PROBE_IDS[i]: float(ce_sel["mapping_means"][i]) for i in range(4)},
            "historical_match_H": float(h_sel),
            "ancestor_hash": ancestor_hash,
            "final_hash": final_hash_sel,
            "validation_version": validation_version,
        },
        "neutral": {
            "run_id": neu_run,
            "paired_block_id": block_id,
            "scaffold_id": scaffold_id,
            "scaffold_mapping": list(mapping),
            "mode": "neutral",
            "base_seed_uint32": seed,
            "C_down_primary_g250": float(metrics["neutral"][-1]["C_down_primary"]),
            "C_down_unitshuffle_g250": float(alt_neu["mean_jsd_bits"]),
            "C_down_unitshuffle_sd": float(alt_neu["sd_jsd_bits"]),
            "cross_eval_mapping_means": {PROBE_IDS[i]: float(ce_neu["mapping_means"][i]) for i in range(4)},
            "historical_match_H": float(h_neu),
            "ancestor_hash": ancestor_hash,
            "final_hash": final_hash_neu,
            "validation_version": validation_version,
        },
    }

    for mode, run_id, pop, rows in (
        ("selected", sel_run, pop_sel, metrics["selected"]),
        ("neutral", neu_run, pop_neu, metrics["neutral"]),
    ):
        np.savez_compressed(
            outdir / "raw" / "states" / f"{run_id}_g250.npz",
            g0=pop0,
            g250=pop,
            base_seed_uint32=np.asarray(seed, dtype=np.uint32),
            scaffold_mapping=np.asarray(mapping, dtype=np.int64),
        )
        _write_metrics_csv(outdir / "raw" / "metrics" / f"{run_id}_metrics.csv", rows)
        _write_json(outdir / "raw" / "endpoints" / f"{run_id}_endpoint.json", run_endpoints[mode])

    pair_summary = {
        "paired_block_id": block_id,
        "scaffold_id": scaffold_id,
        "scaffold_mapping": list(mapping),
        "base_seed_uint32": seed,
        "selected_run_id": sel_run,
        "neutral_run_id": neu_run,
        "delta_C_down_primary": float(run_endpoints["selected"]["C_down_primary_g250"] - run_endpoints["neutral"]["C_down_primary_g250"]),
        "delta_C_down_unitshuffle": float(run_endpoints["selected"]["C_down_unitshuffle_g250"] - run_endpoints["neutral"]["C_down_unitshuffle_g250"]),
        "H_selected": float(h_sel),
        "H_neutral": float(h_neu),
        "delta_H": float(h_sel - h_neu),
        "selected_cross_eval": run_endpoints["selected"]["cross_eval_mapping_means"],
        "neutral_cross_eval": run_endpoints["neutral"]["cross_eval_mapping_means"],
        "ancestor_hash_selected": ancestor_hash,
        "ancestor_hash_neutral": ancestor_hash,
        "selected_final_hash": final_hash_sel,
        "neutral_final_hash": final_hash_neu,
        "validation_version": validation_version,
        "status": "COMPLETE",
    }
    _write_json(outdir / "raw" / "endpoints" / f"{block_id}_PAIR.json", pair_summary)
    return pair_summary
