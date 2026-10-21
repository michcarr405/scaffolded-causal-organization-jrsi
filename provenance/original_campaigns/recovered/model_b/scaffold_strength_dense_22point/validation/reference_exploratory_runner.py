from __future__ import annotations

import os, time, math, json, hashlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import wilcoxon

OUT = Path('/mnt/data/modelb_ratio_sweep_extension_v2')
OLD = Path('/mnt/data/sweep_ext_work/modelb_ratio_sweep_exploratory')
THETA = 1.2
P_INHERIT = 0.975
MU = 0.001
N_GENS = 250
N_REPS = 20
RATIOS = np.array([3.5, 3.75, 4.0, 4.25, 4.5, 5.0, 6.0, 8.0], dtype=float)
BETAS = RATIOS * THETA
PROBE_BETA = 3.0
MI_PERMS = 50
SPEC_DRAWS = 4
ROOT_SEED = 2026090402
N_BOOT = 10000
N_WORKERS = 5

FAV = np.array([2, 0, 3, 1], dtype=np.int64)
FAV_REV = FAV[::-1].copy()
AFF = np.random.default_rng(123).normal(0, 1, size=(4**5, 4))
PROD = np.zeros((4,4), dtype=np.bool_)
for a,b in [(0,1),(1,2),(2,3),(3,0)]:
    PROD[a,b] = True
    PROD[b,a] = True
ANTI = np.zeros((4,4), dtype=np.bool_)
for i in range(4):
    ANTI[i,i] = True
ANTI[1,3] = True
ANTI[3,1] = True
SEG_VEC = np.tile(np.repeat(np.arange(4, dtype=np.int64), 14), 80*8)
TOTAL_WINDOWS = 80*8*56

@njit
def compute_fitnesses_and_observations(population, motif_affinity_matrix, segment_favored_met,
                                        bias_strength, productive_pairs_matrix, anti_pairs_matrix,
                                        reward_strength, penalty_strength, temperature,
                                        local_state_uniforms):
    n_cells, n_seqs, seq_len = population.shape
    n_met = motif_affinity_matrix.shape[1]
    chain_len = seq_len - 4
    n_segments = segment_favored_met.shape[0]
    seg_len = chain_len // n_segments
    total_windows = n_cells * n_seqs * chain_len
    motif_obs = np.empty(total_windows, dtype=np.int64)
    met_obs = np.empty(total_windows, dtype=np.int64)
    fitnesses = np.empty(n_cells, dtype=np.float64)
    obs_idx = 0
    for ci in range(n_cells):
        prod_sum = 0.0
        anti_sum = 0.0
        for si in range(n_seqs):
            prev_met = -1
            for pos in range(chain_len):
                motif_idx = 0
                for k in range(5):
                    motif_idx = motif_idx * 4 + int(population[ci, si, pos + k])
                motif_obs[obs_idx] = motif_idx
                logits = motif_affinity_matrix[motif_idx].copy()
                seg_idx = pos // seg_len
                if seg_idx >= n_segments:
                    seg_idx = n_segments - 1
                fav = segment_favored_met[seg_idx]
                logits[int(fav)] += bias_strength
                maxval = logits[0]
                for m in range(1, n_met):
                    if logits[m] > maxval:
                        maxval = logits[m]
                sumexp = 0.0
                for m in range(n_met):
                    val = np.exp((logits[m] - maxval) / temperature)
                    logits[m] = val
                    sumexp += val
                r = local_state_uniforms[obs_idx]
                cdf = 0.0
                chosen = n_met - 1
                for m in range(n_met):
                    cdf += logits[m] / sumexp
                    if r <= cdf:
                        chosen = m
                        break
                met_obs[obs_idx] = chosen
                obs_idx += 1
                if pos > 0:
                    if productive_pairs_matrix[prev_met, chosen]:
                        prod_sum += 1.0
                    if anti_pairs_matrix[prev_met, chosen]:
                        anti_sum += 1.0
                prev_met = chosen
        mean_prod = prod_sum / n_seqs
        mean_anti = anti_sum / n_seqs
        fit = 1.0 + reward_strength * mean_prod - penalty_strength * mean_anti
        if fit < 0.1:
            fit = 0.1
        fitnesses[ci] = fit
    return fitnesses, motif_obs, met_obs


def _stable_entropy(*parts):
    payload = '\x1f'.join(str(part) for part in parts).encode('utf-8')
    digest = hashlib.sha256(payload).digest()
    return [int.from_bytes(digest[i:i+4], 'little') for i in range(0,32,4)]


def make_generator(root_seed, purpose, *keys):
    entropy = [int(root_seed) & 0xffffffff, *_stable_entropy(purpose, *keys)]
    return np.random.default_rng(np.random.SeedSequence(entropy))


def init_population(rng):
    return rng.integers(0, 4, size=(80,8,60), dtype=np.int8)


def reproduce(pop, fitnesses, rng, neutral=False):
    if neutral:
        probs = np.full(len(fitnesses), 1.0/len(fitnesses))
    else:
        fitnesses = np.maximum(np.asarray(fitnesses, dtype=float), 0)
        total = float(fitnesses.sum())
        probs = fitnesses/total if total > 0 else np.full(len(fitnesses), 1.0/len(fitnesses))
    n_cells, n_seqs, seq_len = pop.shape
    parent_uniforms = rng.random(n_cells)
    parent_indices = np.searchsorted(np.cumsum(probs), parent_uniforms, side='right')
    parent_indices = np.minimum(parent_indices, n_cells - 1)
    inherit_mask = rng.random((n_cells,n_seqs)) < P_INHERIT
    parent_sequence_indices = rng.integers(0, n_seqs, size=(n_cells,n_seqs))
    environmental = rng.integers(0,4,size=(n_cells,n_seqs,seq_len),dtype=np.int8)
    inherited = pop[parent_indices[:,None], parent_sequence_indices]
    new_pop = np.where(inherit_mask[:,:,None], inherited, environmental).astype(np.int8, copy=False)
    mutation_mask = rng.random((n_cells,n_seqs,seq_len)) < MU
    offsets = rng.integers(1,4,size=(n_cells,n_seqs,seq_len),dtype=np.int8)
    mutated = ((new_pop.astype(np.int16) + offsets.astype(np.int16)) % 4).astype(np.int8)
    return np.where(mutation_mask, mutated, new_pop).astype(np.int8, copy=False)


def observe(pop, beta, rng, fav=FAV):
    uniforms = rng.random(TOTAL_WINDOWS)
    return compute_fitnesses_and_observations(pop, AFF, fav, beta, PROD, ANTI, 2.0, 0.5, THETA, uniforms)


def run_sim(seed, beta, neutral=False):
    initialization_rng = make_generator(seed, 'baseline-initialization')
    observation_rng = make_generator(seed, 'baseline-observation')
    propagation_rng = make_generator(seed, 'baseline-propagation')
    pop = init_population(initialization_rng)
    ancestor = pop.copy()
    trajectory = []
    g0 = None
    for t in range(N_GENS):
        fit, motifs, states = observe(pop, beta, observation_rng)
        trajectory.append(float(fit.mean()))
        if t == 0:
            g0 = (fit.copy(), motifs.copy(), states.copy())
        pop = reproduce(pop, fit, propagation_rng, neutral=neutral)
    fit, motifs, states = observe(pop, beta, observation_rng)
    trajectory.append(float(fit.mean()))
    g250 = (fit.copy(), motifs.copy(), states.copy())
    return ancestor, pop, np.asarray(trajectory), g0, g250


def mi_discrete(x, y, nx, ny):
    x = np.asarray(x, dtype=np.int64).ravel()
    y = np.asarray(y, dtype=np.int64).ravel()
    counts = np.bincount(x*ny+y, minlength=nx*ny).reshape(nx,ny).astype(float)
    n = counts.sum()
    if n == 0:
        return 0.0
    pxy = counts/n
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = pxy > 0
    return float(np.sum(pxy[mask] * np.log2(pxy[mask]/expected[mask])))


def cmi_m_z_given_s(m, z, s=SEG_VEC):
    total = len(m)
    val = 0.0
    for sg in range(4):
        idx = (s == sg)
        val += (idx.sum()/total) * mi_discrete(m[idx], z[idx], 1024, 4)
    return float(val)


def info_metrics(m, z, perm_rng):
    i_s_z = mi_discrete(SEG_VEC, z, 4, 4)
    i_m_s = mi_discrete(m, SEG_VEC, 1024, 4)
    i_m_z = mi_discrete(m, z, 1024, 4)
    obs = cmi_m_z_given_s(m, z)
    null = np.empty(MI_PERMS, dtype=float)
    idxs = [np.flatnonzero(SEG_VEC == sg) for sg in range(4)]
    for j in range(MI_PERMS):
        zp = np.array(z, copy=True)
        for idx in idxs:
            zp[idx] = z[idx][perm_rng.permutation(len(idx))]
        null[j] = cmi_m_z_given_s(m, zp)
    pm = float(null.mean())
    psd = float(null.std(ddof=1)) if MI_PERMS > 1 else 0.0
    return dict(I_S_Z=i_s_z, I_M_S=i_m_s, I_M_Z=i_m_z,
                cmi_obs=obs, cmi_perm=pm, I_seq_corr=obs-pm,
                cmi_perm_sd=psd)


def motifs_from_pop(pop):
    w = np.lib.stride_tricks.sliding_window_view(pop, 5, axis=2)
    weights = np.array([256,64,16,4,1], dtype=np.int64)
    return (w*weights).sum(axis=-1).astype(np.int64).reshape(-1)


def q_by_segment(beta, fav=FAV):
    out = np.empty((4,1024,4), dtype=float)
    for sg in range(4):
        logits = AFF.copy()
        logits[:, int(fav[sg])] += beta
        x = logits/THETA
        x -= x.max(axis=1, keepdims=True)
        e = np.exp(x)
        out[sg] = e/e.sum(axis=1, keepdims=True)
    return out


def jsd_bits(p, q):
    p = np.asarray(p, dtype=float).ravel()
    q = np.asarray(q, dtype=float).ravel()
    mid = 0.5*(p+q)
    def kl(a,b):
        mask = a > 0
        return float(np.sum(a[mask]*np.log2(a[mask]/b[mask])))
    return 0.5*kl(p,mid)+0.5*kl(q,mid)


def c_down(pop, beta):
    m = motifs_from_pop(pop)
    counts = np.zeros((4,1024), dtype=float)
    np.add.at(counts, (SEG_VEC,m), 1.0)
    psm = counts/counts.sum()
    ps = psm.sum(axis=1)
    pm = psm.sum(axis=0)
    q = q_by_segment(beta)
    intact = np.einsum('sm,smz->sz', psm, q)
    erased = np.einsum('s,m,smz->sz', ps, pm, q)
    return jsd_bits(intact, erased)


def specificity(pop, beta, seed, ratio_key, phase, probe_label):
    rng = make_generator(seed, 'ratio-sweep-specificity-v2', ratio_key, phase, probe_label)
    native = []
    reversed_ = []
    for _ in range(SPEC_DRAWS):
        u = rng.random(TOTAL_WINDOWS)
        f1,_,_ = compute_fitnesses_and_observations(pop, AFF, FAV, beta, PROD, ANTI, 2.0, 0.5, THETA, u)
        f2,_,_ = compute_fitnesses_and_observations(pop, AFF, FAV_REV, beta, PROD, ANTI, 2.0, 0.5, THETA, u)
        native.append(float(f1.mean()))
        reversed_.append(float(f2.mean()))
    na = float(np.mean(native)); rv = float(np.mean(reversed_))
    return na, rv, na-rv


def ratio_tag(r):
    return f'{r:.6f}'.replace('.', 'p')


def one_job(args):
    ratio, rep, seed, mode = args
    beta = ratio*THETA
    neutral = (mode == 'neutral')
    ancestor, final, traj, g0, g250 = run_sim(seed, beta, neutral=neutral)
    row = dict(ratio=ratio, beta=beta, replicate=rep, seed=seed, mode=mode)
    row['fitness_g0'] = float(g0[0].mean())
    row['fitness_g250'] = float(g250[0].mean())
    for label, obs in [('g0',g0), ('g250',g250)]:
        prng = make_generator(seed, 'ratio-sweep-mi-permutation-v2', ratio_tag(ratio), label)
        im = info_metrics(obs[1], obs[2], prng)
        for k,v in im.items(): row[f'{k}_{label}'] = v
    row['C_down_train_g0'] = c_down(ancestor, beta)
    row['C_down_train_g250'] = c_down(final, beta)
    row['C_down_probe3_g0'] = c_down(ancestor, PROBE_BETA)
    row['C_down_probe3_g250'] = c_down(final, PROBE_BETA)
    if mode == 'selected':
        a_nt = specificity(ancestor, beta, seed, ratio_tag(ratio), 'ancestor', 'train')
        a_np = specificity(ancestor, PROBE_BETA, seed, ratio_tag(ratio), 'ancestor', 'probe3')
        row['ancestor_native_train'], row['ancestor_reversed_train'], row['ancestor_specificity_train'] = a_nt
        row['ancestor_native_probe3'], row['ancestor_reversed_probe3'], row['ancestor_specificity_probe3'] = a_np
    else:
        for k in ['ancestor_native_train','ancestor_reversed_train','ancestor_specificity_train',
                  'ancestor_native_probe3','ancestor_reversed_probe3','ancestor_specificity_probe3']:
            row[k] = np.nan
    e_t = specificity(final, beta, seed, ratio_tag(ratio), 'evolved', 'train')
    e_p = specificity(final, PROBE_BETA, seed, ratio_tag(ratio), 'evolved', 'probe3')
    row['evolved_native_train'], row['evolved_reversed_train'], row['evolved_specificity_train'] = e_t
    row['evolved_native_probe3'], row['evolved_reversed_probe3'], row['evolved_specificity_probe3'] = e_p
    row['fitness_g0_traj'] = float(traj[0])
    row['fitness_g250_traj'] = float(traj[-1])
    row['fitness_initial50'] = float(traj[:50].mean())
    row['fitness_late50'] = float(traj[-50:].mean())
    row['sustained_gain_late_minus_initial50'] = row['fitness_late50'] - row['fitness_initial50']
    row['late_minus_g0'] = row['fitness_late50'] - row['fitness_g0']
    state_path = OUT/'states'/f'{mode}_r{ratio_tag(ratio)}_rep{rep:02d}.npz'
    np.savez_compressed(state_path, final=final, ancestor=ancestor, ratio=ratio, beta=beta, replicate=rep, seed=seed)
    traj_df = pd.DataFrame({'ratio':ratio,'beta':beta,'replicate':rep,'seed':seed,'mode':mode,
                            'generation':np.arange(len(traj),dtype=int),'fitness':traj})
    return row, traj_df


def bootstrap_ci(values, key, n_boot=N_BOOT):
    v = np.asarray(values, dtype=float)
    rng = make_generator(ROOT_SEED, 'extension-bootstrap', key)
    idx = rng.integers(0, len(v), size=(n_boot,len(v)))
    b = v[idx].mean(axis=1)
    return float(np.quantile(b,0.025)), float(np.quantile(b,0.975))


def exact_signflip_p_gt0(values):
    v = np.asarray(values, dtype=float)
    obs = float(v.sum())
    sums = np.array([0.0])
    for x in v:
        sums = np.concatenate((sums-x, sums+x))
    tol = 1e-14 * max(1.0, abs(obs))
    return float(np.mean(sums >= obs-tol))


def holm_adjust(ps):
    ps = np.asarray(ps, dtype=float)
    order = np.argsort(ps)
    out = np.empty_like(ps)
    running = 0.0
    m = len(ps)
    for rank, idx in enumerate(order):
        val = min(1.0, (m-rank)*ps[idx])
        running = max(running, val)
        out[idx] = running
    return out


def build_paired(endpoint):
    sel = endpoint[endpoint['mode']=='selected'].copy().drop(columns=['mode']).add_suffix('_sel')
    neu = endpoint[endpoint['mode']=='neutral'].copy().drop(columns=['mode']).add_suffix('_neu')
    paired = sel.merge(neu, left_on=['ratio_sel','beta_sel','replicate_sel'], right_on=['ratio_neu','beta_neu','replicate_neu'])
    paired = paired.rename(columns={'ratio_sel':'ratio','beta_sel':'beta','replicate_sel':'replicate'})
    paired = paired.drop(columns=['ratio_neu','beta_neu','replicate_neu'])
    paired['mode_sel']='selected'; paired['mode_neu']='neutral'
    # preserve old-style seed labels through aliases
    if 'seed_sel' not in paired.columns and 'seed_sel_sel' in paired.columns:
        paired = paired.rename(columns={'seed_sel_sel':'seed_sel'})
    paired['delta_C_down_train'] = paired.C_down_train_g250_sel - paired.C_down_train_g250_neu
    paired['delta_C_down_probe3'] = paired.C_down_probe3_g250_sel - paired.C_down_probe3_g250_neu
    paired['delta_I_seq_corr'] = paired.I_seq_corr_g250_sel - paired.I_seq_corr_g250_neu
    paired['appropriation_train_selected'] = paired.evolved_specificity_train_sel - paired.ancestor_specificity_train_sel
    paired['appropriation_probe3_selected'] = paired.evolved_specificity_probe3_sel - paired.ancestor_specificity_probe3_sel
    paired['appropriation_train_neutral'] = paired.evolved_specificity_train_neu - paired.ancestor_specificity_train_sel
    paired['appropriation_probe3_neutral'] = paired.evolved_specificity_probe3_neu - paired.ancestor_specificity_probe3_sel
    paired['selection_excess_appropriation_train'] = paired.appropriation_train_selected - paired.appropriation_train_neutral
    paired['selection_excess_appropriation_probe3'] = paired.appropriation_probe3_selected - paired.appropriation_probe3_neutral
    return paired


def summarize(paired):
    rows=[]
    metrics = ['delta_C_down_train','delta_C_down_probe3','delta_I_seq_corr',
               'appropriation_train_selected','appropriation_probe3_selected',
               'selection_excess_appropriation_train','selection_excess_appropriation_probe3']
    for ratio, g in paired.groupby('ratio', sort=True):
        row={'ratio':float(ratio),'beta':float(g.beta.iloc[0]),'n':len(g)}
        for metric in metrics:
            vals=g[metric].to_numpy(float)
            lo,hi=bootstrap_ci(vals,f'{metric}-{ratio}')
            row[f'{metric}_mean']=float(vals.mean())
            row[f'{metric}_ci95_lo']=lo; row[f'{metric}_ci95_hi']=hi
            row[f'{metric}_positive_reps']=int(np.sum(vals>0))
            row[f'{metric}_p_gt0']=exact_signflip_p_gt0(vals)
        for col in ['C_down_train_g250','C_down_probe3_g250','I_seq_corr_g250','I_S_Z_g250',
                    'fitness_g0','fitness_g250','fitness_late50','late_minus_g0','sustained_gain_late_minus_initial50']:
            row[f'{col}_selected_mean']=float(g[f'{col}_sel'].mean())
            row[f'{col}_neutral_mean']=float(g[f'{col}_neu'].mean())
        rows.append(row)
    s=pd.DataFrame(rows)
    for metric in metrics:
        s[f'{metric}_holm_p']=holm_adjust(s[f'{metric}_p_gt0'].values)
    return s


def combined_optimum_diagnostics(combined_paired):
    metrics=['delta_C_down_train','delta_C_down_probe3','selection_excess_appropriation_train','selection_excess_appropriation_probe3']
    out=[]
    high=float(combined_paired.ratio.max())
    pivots={m:combined_paired.pivot(index='replicate',columns='ratio',values=m).sort_index(axis=1) for m in metrics}
    for m in metrics:
        pv=pivots[m]
        means=pv.mean(axis=0)
        best=float(means.idxmax())
        diff=(pv[best]-pv[high]).to_numpy()
        dlo,dhi=bootstrap_ci(diff,f'combined-best-minus-high-{m}')
        if best==high:
            p=1.0
        else:
            try: p=float(wilcoxon(diff, alternative='greater').pvalue)
            except Exception: p=float('nan')
        rng=make_generator(ROOT_SEED,'combined-argmax-bootstrap',m)
        counts={float(r):0 for r in pv.columns}
        arr=pv.to_numpy(); cols=np.asarray(pv.columns,float)
        for _ in range(N_BOOT):
            idx=rng.integers(0,arr.shape[0],size=arr.shape[0])
            j=int(np.argmax(arr[idx].mean(axis=0)))
            counts[float(cols[j])] += 1
        dist={str(k):v/N_BOOT for k,v in counts.items() if v>0}
        mode=max(counts,key=counts.get)
        out.append(dict(metric=m,observed_best_ratio=best,observed_best_beta=best*THETA,
                        high_endpoint_ratio=high,best_minus_high_mean=float(diff.mean()),
                        best_minus_high_ci95_lo=dlo,best_minus_high_ci95_hi=dhi,p_best_gt_high=p,
                        bootstrap_argmax_at_observed_best_fraction=counts[best]/N_BOOT,
                        bootstrap_argmax_mode_ratio=mode,bootstrap_argmax_mode_fraction=counts[mode]/N_BOOT,
                        bootstrap_argmax_distribution=json.dumps(dist,sort_keys=True)))
    return pd.DataFrame(out)


def main():
    t0=time.time()
    seeds=pd.read_csv(OLD/'seed_ledger.csv')
    seeds.to_csv(OUT/'seed_ledger.csv',index=False)
    config=dict(status='EXPLORATORY_EXTENSION',theta=THETA,p_inherit=P_INHERIT,mutation_rate=MU,
                n_generations=N_GENS,n_replicates=N_REPS,ratios=RATIOS.tolist(),betas=BETAS.tolist(),
                probe_beta=PROBE_BETA,probe_ratio=PROBE_BETA/THETA,mi_permutations=MI_PERMS,
                specificity_assay_draws=SPEC_DRAWS,root_seed=ROOT_SEED,
                scientific_source_commit='2c7d78694579755402c0a1896e109b29dec4d6a0',
                original_sweep=str(OLD))
    with open(OUT/'experiment_config.json','w') as f: json.dump(config,f,indent=2)
    jobs=[]
    for ratio in RATIOS:
        for mode in ['neutral','selected']:
            for _,r in seeds.iterrows():
                jobs.append((float(ratio),int(r.replicate),int(r.seed),mode))
    print('jobs',len(jobs),'workers',N_WORKERS,flush=True)
    rows=[]; trajs=[]
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs=[ex.submit(one_job,j) for j in jobs]
        for i,fut in enumerate(as_completed(futs),1):
            row,tr=fut.result(); rows.append(row); trajs.append(tr)
            if i%20==0: print('done',i,'/',len(jobs),'elapsed',round(time.time()-t0,1),flush=True)
    endpoint=pd.DataFrame(rows).sort_values(['ratio','mode','replicate']).reset_index(drop=True)
    traj=pd.concat(trajs,ignore_index=True).sort_values(['ratio','mode','replicate','generation']).reset_index(drop=True)
    endpoint.to_csv(OUT/'endpoint_metrics_extension.csv',index=False)
    traj.to_csv(OUT/'fitness_trajectories_extension.csv',index=False)
    paired=build_paired(endpoint).sort_values(['ratio','replicate']).reset_index(drop=True)
    paired.to_csv(OUT/'paired_selected_neutral_metrics_extension.csv',index=False)
    summary=summarize(paired)
    summary.to_csv(OUT/'ratio_summary_extension.csv',index=False)

    old_ep=pd.read_csv(OLD/'endpoint_metrics.csv')
    old_pair=pd.read_csv(OLD/'paired_selected_neutral_metrics.csv')
    # Normalize old paired replicate/ratio columns are already unsuffixed.
    common=[c for c in paired.columns if c in old_pair.columns]
    combined_pair=pd.concat([old_pair[common],paired[common]],ignore_index=True).sort_values(['ratio','replicate']).reset_index(drop=True)
    combined_pair.to_csv(OUT/'combined_paired_selected_neutral_metrics.csv',index=False)
    old_summary=pd.read_csv(OLD/'ratio_summary.csv')
    # Make extension summary column-compatible; fill missing old columns if needed.
    cols=list(old_summary.columns)
    for c in cols:
        if c not in summary.columns: summary[c]=np.nan
    for c in summary.columns:
        if c not in old_summary.columns: old_summary[c]=np.nan
    combined_summary=pd.concat([old_summary[summary.columns],summary],ignore_index=True).sort_values('ratio').reset_index(drop=True)
    # Recompute Holm across the full combined tested grid from raw p values.
    metrics=['delta_C_down_train','delta_C_down_probe3','delta_I_seq_corr','appropriation_train_selected',
             'appropriation_probe3_selected','selection_excess_appropriation_train','selection_excess_appropriation_probe3']
    for m in metrics:
        combined_summary[f'{m}_holm_p']=holm_adjust(combined_summary[f'{m}_p_gt0'].values)
    combined_summary.to_csv(OUT/'combined_ratio_summary.csv',index=False)
    opt=combined_optimum_diagnostics(combined_pair)
    opt.to_csv(OUT/'combined_optimum_diagnostics.csv',index=False)
    runtime=time.time()-t0
    prov=config | dict(classification='exploratory extension/regime-finding',runtime_seconds=runtime,
                       notes=['extension grid frozen in EXTENSION_FREEZE.md before execution',
                              'same 20 seed blocks as preceding exploratory sweep',
                              'canonical simulation law validated by exact replay of archived old states',
                              'C_down definition exactly reproduces archived old endpoint values',
                              'combined files are derived views; original sweep files are not modified'])
    with open(OUT/'provenance.json','w') as f: json.dump(prov,f,indent=2)
    print('DONE runtime',round(runtime,1),flush=True)
    print(summary[['ratio','beta','delta_C_down_train_mean','delta_C_down_probe3_mean',
                   'selection_excess_appropriation_train_mean','selection_excess_appropriation_probe3_mean','fitness_g250_selected_mean']].to_string(index=False),flush=True)
    print('\nOPTIMA\n',opt.to_string(index=False),flush=True)

if __name__=='__main__':
    main()
