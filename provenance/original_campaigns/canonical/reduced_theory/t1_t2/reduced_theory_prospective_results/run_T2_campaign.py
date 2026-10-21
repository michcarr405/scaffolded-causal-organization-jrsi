from pathlib import Path
import sys, hashlib, json, itertools, math
import numpy as np
import pandas as pd
from scipy.stats import binomtest

SRCROOT=Path('/mnt/data/prospective_test_work/identity/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0')
sys.path.insert(0,str(SRCROOT/'scripts'))
from dcc_pipeline import (
    make_params, observe, state_hash, motif_tensor, mapping_cdf_table,
    probe_mapping_fitnesses_from_motifs, P_INHERIT, MU, BETA, THETA
)
sys.path.insert(0,str(SRCROOT/'source'))
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator

OUT=Path('/mnt/data/reduced_theory_prospective_T2')
OUT.mkdir(parents=True,exist_ok=True)
STATES=OUT/'states'; STATES.mkdir(exist_ok=True)
H=(2,0,3,1)
ALL=list(itertools.permutations(range(4)))
hidx=ALL.index(H)
N_BLOCKS=30
N_DRAWS=32
N_GENS=250
BOOT_N=50000
BOOT_SEED=390716381

# deterministic new seeds
def seed_for(i):
    tag=f'MODEL_B_REDUCED_THEORY_T2|v1.0.0|block|{i}'
    d=hashlib.sha256(tag.encode()).digest()
    return int.from_bytes(d[:4],'little',signed=False)
seeds=[seed_for(i) for i in range(N_BLOCKS)]
assert len(set(seeds))==N_BLOCKS

# light collision check against the two closest prior campaign seed ledgers
prior=set()
for p in [SRCROOT/'control'/'SEED_LEDGER_v1.0.0.csv', Path('/mnt/data/prospective_test_work/strength/MODEL_B_DCC_SCAFFOLD_STRENGTH_CONFIRMATORY_RUN_v1.0.0/control/SEED_LEDGER_v1.0.0.csv')]:
    if p.exists():
        d=pd.read_csv(p)
        for c in d.columns:
            if 'seed' in c.lower():
                vals=pd.to_numeric(d[c],errors='coerce').dropna().astype(np.uint64).tolist()
                prior.update(int(v) for v in vals)
assert not (set(seeds)&prior), 'new seed collision with checked prior campaigns'

params=make_params(H)
# all mappings equal beta/theta; cdf table across all 24
cdf=mapping_cdf_table(params['motif_affinity_matrix'], ALL, BETA, THETA)

rows=[]
for bi,seed in enumerate(seeds):
    block=f'T2_B{bi:02d}'
    init_rng=make_generator(seed,'T2-initialization')
    pop0=init_population(params['n_cells'],params['n_seqs'],params['seq_len'],init_rng)
    ps=pop0.copy(); pn=pop0.copy()
    obs_s=make_generator(seed,'T2-observation')
    obs_n=make_generator(seed,'T2-observation')
    rep_s=make_generator(seed,'T2-propagation')
    rep_n=make_generator(seed,'T2-propagation')
    for g in range(N_GENS):
        fs,_,_=observe(ps,params,obs_s)
        fn,_,_=observe(pn,params,obs_n)
        ps=reproduce_with_partitioning(ps,fs,MU,P_INHERIT,rep_s)
        pn=reproduce_with_partitioning(pn,np.ones_like(fn),MU,P_INHERIT,rep_n)
    # Endpoint cross-evaluation, common random numbers across mappings/modes.
    ms=motif_tensor(ps); mn=motif_tensor(pn)
    assert ms.size==mn.size
    u=make_generator(seed,'T2-cross-eval').random((N_DRAWS,ms.size))
    vals_s=probe_mapping_fitnesses_from_motifs(ms,cdf,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),u)
    vals_n=probe_mapping_fitnesses_from_motifs(mn,cdf,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),u)
    means_s=vals_s.mean(axis=1); means_n=vals_n.mean(axis=1)
    fh_s=means_s[hidx]; fh_n=means_n[hidx]
    for mi,m in enumerate(ALL):
        k=sum(a!=b for a,b in zip(H,m))
        As=float(fh_s-means_s[mi]); An=float(fh_n-means_n[mi]); dH=As-An
        rows.append(dict(block_id=block,block_index=bi,seed=seed,mapping_id=mi,mapping='['+','.join(map(str,m))+']',hamming=k,sq_bias_distance=float(2*(BETA**2)*k),Fhist_selected=float(fh_s),Fprobe_selected=float(means_s[mi]),A_selected=As,Fhist_neutral=float(fh_n),Fprobe_neutral=float(means_n[mi]),A_neutral=An,DeltaH=float(dH)))
    np.savez_compressed(STATES/f'{block}_g250.npz',g0=pop0,selected_g250=ps,neutral_g250=pn,seed=np.uint32(seed),historical_mapping=np.array(H,dtype=np.int64))
    print('completed',block, flush=True)

raw=pd.DataFrame(rows)
raw.to_csv(OUT/'T2_mapping_level_results.csv',index=False)
# exclude historical mapping k=0 for distance classes
alt=raw[raw.hamming>0].copy()
blockk=(alt.groupby(['block_id','block_index','seed','hamming']).agg(
    DeltaH=('DeltaH','mean'),A_selected=('A_selected','mean'),A_neutral=('A_neutral','mean'),n_mappings=('mapping_id','size')).reset_index())
blockk.to_csv(OUT/'T2_block_distance_results.csv',index=False)
summary=(blockk.groupby('hamming').agg(n_blocks=('DeltaH','size'),DeltaH_mean=('DeltaH','mean'),DeltaH_sd=('DeltaH','std'),A_selected_mean=('A_selected','mean'),A_neutral_mean=('A_neutral','mean'),n_mappings_per_block=('n_mappings','first')).reset_index())
summary.to_csv(OUT/'T2_distance_summary.csv',index=False)

# wide per block
w=blockk.pivot(index='block_id',columns='hamming',values='DeltaH')
w.columns=[f'k{int(c)}' for c in w.columns]
w=w.reset_index()
# bootstrap paired root blocks
rng=np.random.default_rng(BOOT_SEED)
arr=w[['k2','k3','k4']].to_numpy(float)
idx=rng.integers(0,len(arr),size=(BOOT_N,len(arr)))
bm=arr[idx].mean(axis=1)
# ratios of means
rat32=bm[:,1]/bm[:,0]; rat42=bm[:,2]/bm[:,0]
# theory-shape residual contrasts per resample mean
r3=bm[:,1]-1.5*bm[:,0]; r4=bm[:,2]-2.0*bm[:,0]
# observed
m=arr.mean(axis=0)
obs_rat32=m[1]/m[0]; obs_rat42=m[2]/m[0]
obs_r3=m[1]-1.5*m[0]; obs_r4=m[2]-2*m[0]
# monotonic directional paired contrasts
d32=arr[:,1]-arr[:,0]; d43=arr[:,2]-arr[:,1]
# exact sign test positive, zeros nonpositive
p32=binomtest(int(np.sum(d32>0)),n=len(d32),p=0.5,alternative='greater').pvalue
p43=binomtest(int(np.sum(d43>0)),n=len(d43),p=0.5,alternative='greater').pvalue

# through-origin fit on 3 class means
ks=np.array([2.,3.,4.]); lam=float(np.dot(ks,m)/np.dot(ks,ks)); pred=lam*ks
rss=float(np.sum((m-pred)**2)); tss=float(np.sum((m-m.mean())**2)); R2=float(1-rss/tss)

res={
 'plan_sha256':(OUT/'PLAN_SHA256.txt').read_text().split()[0],
 'n_blocks':N_BLOCKS,'n_probe_draws':N_DRAWS,'n_alternative_mappings':23,
 'counts_by_hamming':alt.groupby('hamming').mapping_id.nunique().astype(int).to_dict(),
 'mean_DeltaH_by_hamming':{str(int(k)):float(v) for k,v in zip(summary.hamming,summary.DeltaH_mean)},
 'ratio_k3_over_k2':{'observed':float(obs_rat32),'theory':1.5,'bootstrap95':[float(np.quantile(rat32,.025)),float(np.quantile(rat32,.975))]},
 'ratio_k4_over_k2':{'observed':float(obs_rat42),'theory':2.0,'bootstrap95':[float(np.quantile(rat42,.025)),float(np.quantile(rat42,.975))]},
 'shape_residual_k3_minus_1p5k2':{'observed':float(obs_r3),'bootstrap95':[float(np.quantile(r3,.025)),float(np.quantile(r3,.975))]},
 'shape_residual_k4_minus_2k2':{'observed':float(obs_r4),'bootstrap95':[float(np.quantile(r4,.025)),float(np.quantile(r4,.975))]},
 'directional_k3_gt_k2':{'positive_blocks':int(np.sum(d32>0)),'n':N_BLOCKS,'one_sided_sign_p':float(p32),'mean_difference':float(d32.mean())},
 'directional_k4_gt_k3':{'positive_blocks':int(np.sum(d43>0)),'n':N_BLOCKS,'one_sided_sign_p':float(p43),'mean_difference':float(d43.mean())},
 'through_origin':{'lambda':lam,'R2':R2,'predicted_means':pred.tolist()},
 'seed_collision_check_prior_strength_identity':'PASS'
}
(OUT/'T2_RESULT_SUMMARY.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print(json.dumps(res,indent=2,sort_keys=True))
