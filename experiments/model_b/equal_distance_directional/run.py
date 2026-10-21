from pathlib import Path
import sys, hashlib, json, os, itertools, math
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np, pandas as pd
from scipy.stats import binomtest
REPO_ROOT=Path(__file__).resolve().parents[3]
SRCROOT=REPO_ROOT/'provenance/original_campaigns/canonical/model_b/four_scaffold/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0'
sys.path.insert(0,str(SRCROOT/'scripts'))
from dcc_pipeline import make_params, observe, motif_tensor, probe_mapping_fitnesses_from_motifs, P_INHERIT, MU, THETA
sys.path.insert(0,str(SRCROOT/'source'))
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator
INPUT=Path(__file__).resolve().parent/'frozen_inputs'
OUT=Path(os.environ.get('SCO_OUTPUT_DIR', REPO_ROOT/'work/model_b_equal_distance_directional'))
STATES=Path(os.environ.get('SCO_STATE_DIR', OUT/'states'))
OUT.mkdir(parents=True,exist_ok=True); STATES.mkdir(parents=True,exist_ok=True)
H=(2,0,3,1); N_BLOCKS=30; N_GENS=250; N_DRAWS=32; BETA=4.0
CAL=pd.read_csv(INPUT/'T5_FROZEN_ANGULAR_PREDICTIONS.csv')
PROBES=pd.read_csv(INPUT/'T5_PROBE_SCAFFOLDS.csv')
BCOLS=[f'b{s}_{z}' for s in range(4) for z in range(4)]
# exact historical centered bias
hist=np.zeros((4,4),float)
for s,f in enumerate(H): hist[s,:]=-BETA/4.; hist[s,f]=3*BETA/4.
BIAS=np.concatenate([hist[None,:,:],PROBES[BCOLS].to_numpy(float).reshape(-1,4,4)],axis=0)
PROBE_IDS=['HIST']+PROBES.probe_id.tolist()
AFFINE_A=-0.82392528; AFFINE_B=0.98552753
PERM_N=50000; PERM_SEED=91273411

def seed_for(bi):
    tag=f'MODEL_B_REDUCED_THEORY_T5|v1.0.0|block={bi}'
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'little')

def prior_seeds():
    files=[]
    for root in [REPO_ROOT/'provenance/original_campaigns/canonical/model_b', REPO_ROOT/'provenance/original_campaigns/canonical/reduced_theory']:
        if root.exists(): files.extend(root.rglob('*.csv'))
    out=set()
    for p in files:
        try: d=pd.read_csv(p)
        except Exception: continue
        for c in d.columns:
            if 'seed' in c.lower():
                vals=pd.to_numeric(d[c],errors='coerce').dropna().astype(np.uint64)
                out.update(int(v) for v in vals.tolist())
    return out

def evolve_one(args):
    bi,seed=args; params=make_params(H)
    pop0=init_population(params['n_cells'],params['n_seqs'],params['seq_len'],make_generator(seed,'T5-initialization'))
    ps=pop0.copy(); pn=pop0.copy()
    obs_s=make_generator(seed,'T5-observation-selected'); rep_s=make_generator(seed,'T5-propagation-selected'); rep_n=make_generator(seed,'T5-propagation-neutral')
    for g in range(N_GENS):
        fs,_,_=observe(ps,params,obs_s)
        ps=reproduce_with_partitioning(ps,fs,MU,P_INHERIT,rep_s)
        pn=reproduce_with_partitioning(pn,np.ones(params['n_cells'],dtype=float),MU,P_INHERIT,rep_n)
    fn=STATES/f'T5_B{bi:02d}_g250.npz'; np.savez_compressed(fn,g0=pop0,selected_g250=ps,neutral_g250=pn,seed=np.uint32(seed),historical_mapping=np.array(H,dtype=np.int64)); return str(fn)

def cdf_table(affinity):
    table=np.empty((len(BIAS),4,affinity.shape[0],4),float)
    for i,b in enumerate(BIAS):
        logits=affinity[None,:,:]+b[:,None,:]; x=logits/THETA; x-=x.max(axis=2,keepdims=True); ex=np.exp(x); p=ex/ex.sum(axis=2,keepdims=True); table[i]=np.cumsum(p,axis=2)
    table[:,:,:,-1]=1.0; return table

def pearson(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float); return float(np.corrcoef(x,y)[0,1])

def r2(y,yh):
    y=np.asarray(y,float); yh=np.asarray(yh,float); return float(1-np.sum((y-yh)**2)/np.sum((y-y.mean())**2))

def rmse(y,yh): return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(yh))**2)))

if __name__=='__main__':
    seeds=[seed_for(i) for i in range(N_BLOCKS)]; assert len(set(seeds))==N_BLOCKS
    prior=prior_seeds(); collisions=set(seeds)&prior
    if collisions: raise RuntimeError(f'seed collisions {len(collisions)}')
    (OUT/'SEED_AUDIT_T5.json').write_text(json.dumps({'n_new_seeds':N_BLOCKS,'unique':len(set(seeds)),'prior_seed_count_checked':len(prior),'collision_count':0},indent=2)+'\n')
    jobs=[(i,seeds[i]) for i in range(N_BLOCKS) if not (STATES/f'T5_B{i:02d}_g250.npz').exists()]
    workers=min(5,os.cpu_count() or 2); print('EVOLUTION',len(jobs),'workers',workers,flush=True)
    if jobs:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs={ex.submit(evolve_one,j):j for j in jobs}
            done=0
            for fut in as_completed(futs):
                fut.result(); done+=1
                if done%5==0 or done==len(jobs): print('evolved',done,'/',len(jobs),flush=True)
    params=make_params(H); cdf=cdf_table(params['motif_affinity_matrix']); rows=[]
    for bi,seed in enumerate(seeds):
        z=np.load(STATES/f'T5_B{bi:02d}_g250.npz'); ms=motif_tensor(z['selected_g250']); mn=motif_tensor(z['neutral_g250']); assert ms.size==mn.size
        u=make_generator(seed,'T5-cross-eval').random((N_DRAWS,ms.size))
        vs=probe_mapping_fitnesses_from_motifs(ms,cdf,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),u)
        vn=probe_mapping_fitnesses_from_motifs(mn,cdf,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),u)
        means_s=vs.mean(axis=1); means_n=vn.mean(axis=1); fh_s=float(means_s[0]); fh_n=float(means_n[0])
        for i,pid in enumerate(PROBE_IDS):
            As=fh_s-float(means_s[i]); An=fh_n-float(means_n[i]); rows.append({'block_id':f'T5_B{bi:02d}','block_index':bi,'seed':seed,'probe_id':pid,'phi_deg':np.nan if i==0 else float(PROBES.iloc[i-1].phi_deg),'distance':0.0 if i==0 else 64.0,'Fhist_selected':fh_s,'Fprobe_selected':float(means_s[i]),'A_selected':As,'Fhist_neutral':fh_n,'Fprobe_neutral':float(means_n[i]),'A_neutral':An,'DeltaH':As-An})
        print('assayed',bi+1,'/',N_BLOCKS,flush=True)
    raw=pd.DataFrame(rows); raw.to_csv(OUT/'T5_probe_level_results.csv',index=False)
    alt=raw[raw.probe_id!='HIST'].copy(); summary=alt.groupby(['probe_id','phi_deg']).DeltaH.agg(['mean','std']).reset_index().rename(columns={'mean':'DeltaH_mean','std':'DeltaH_sd'})
    summary=summary.merge(CAL,on=['probe_id','phi_deg'],how='left'); summary['pred_obs_affine']=AFFINE_A+AFFINE_B*summary.pred_raw_mean
    summary.to_csv(OUT/'T5_direction_summary.csv',index=False)
    pred=summary.pred_raw_mean.to_numpy(); obs=summary.DeltaH_mean.to_numpy(); r=pearson(pred,obs)
    # exact permutation p for abs correlation all labels
    vals=[]
    for perm in itertools.permutations(obs.tolist()): vals.append(abs(pearson(pred,perm)))
    vals=np.asarray(vals); pperm=float((np.sum(vals>=abs(r)-1e-15))/len(vals))
    # extremal sign
    top='P13'; bot='P09'; piv=alt.pivot(index='block_id',columns='probe_id',values='DeltaH'); diff=(piv[top]-piv[bot]).to_numpy(); npos=int(np.sum(diff>0)); ntie=int(np.sum(diff==0)); signp=float(binomtest(npos,n=N_BLOCKS-ntie,p=.5,alternative='greater').pvalue)
    # equal-distance anisotropy permutation variance of direction means
    mat=alt.pivot(index='block_id',columns='probe_id',values='DeltaH')[CAL.probe_id.tolist()].to_numpy(); stat=float(np.var(mat.mean(axis=0),ddof=1)); rng=np.random.default_rng(PERM_SEED); cnt=0
    for k in range(PERM_N):
        pm=np.empty_like(mat)
        for i in range(mat.shape[0]): pm[i]=mat[i,rng.permutation(mat.shape[1])]
        sp=float(np.var(pm.mean(axis=0),ddof=1)); cnt += int(sp>=stat)
    paniso=(cnt+1)/(PERM_N+1)
    # affine numeric metrics
    yhat=summary.pred_obs_affine.to_numpy(); absr2=r2(obs,yhat); absrmse=rmse(obs,yhat)
    # per-block correlations
    bc=[]
    for bid,g in alt.groupby('block_id'):
        gg=g.set_index('probe_id').loc[CAL.probe_id]; bc.append(pearson(pred,gg.DeltaH.to_numpy()))
    bcs=pd.DataFrame({'block_id':sorted(alt.block_id.unique()),'profile_r':bc}); bcs.to_csv(OUT/'T5_block_profile_correlations.csv',index=False)
    observed_top=str(summary.loc[summary.DeltaH_mean.idxmax(),'probe_id']); observed_bottom=str(summary.loc[summary.DeltaH_mean.idxmin(),'probe_id'])
    res={'plan_sha256':hashlib.sha256((INPUT/'PROSPECTIVE_PLAN_T5_v1.0.0.md').read_bytes()).hexdigest(),'execution_spec_sha256':hashlib.sha256((INPUT/'EXECUTION_SPEC_T5_v1.0.0.md').read_bytes()).hexdigest(),'n_blocks':N_BLOCKS,'n_draws':N_DRAWS,'profile_r':r,'profile_exact_permutation_p':pperm,'primary_profile_pass':bool(r>0.90 and pperm<0.01),'extremal_top':top,'extremal_bottom':bot,'top_gt_bottom_blocks':npos,'ties':ntie,'extremal_sign_p':signp,'primary_extremal_pass':bool(npos>=24),'anisotropy_variance_stat':stat,'anisotropy_permutation_p':paniso,'primary_anisotropy_pass':bool(paniso<0.01),'affine_absolute_R2':absr2,'affine_absolute_RMSE':absrmse,'observed_top_direction':observed_top,'observed_bottom_direction':observed_bottom,'median_block_profile_r':float(np.median(bc)),'min_block_profile_r':float(np.min(bc)),'seed_collision_audit':'PASS'}
    (OUT/'T5_RESULT_SUMMARY.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n'); print(json.dumps(res,indent=2,sort_keys=True))
