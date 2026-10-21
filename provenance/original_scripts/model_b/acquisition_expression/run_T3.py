from pathlib import Path
import sys, hashlib, json, math, os
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SRCROOT=Path('/mnt/data/prospective_test_work/strength/MODEL_B_DCC_SCAFFOLD_STRENGTH_CONFIRMATORY_RUN_v1.0.0')
sys.path.insert(0,str(SRCROOT/'scripts'))
from strength_pipeline import params_for, c_down_primary, NATIVE, THETA, MU, P_INHERIT, observe_with_uniforms
sys.path.insert(0,str(SRCROOT/'source'))
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator

OUT=Path('/mnt/data/reduced_theory_prospective_T3T4/T3')
STATES=OUT/'states'; STATES.mkdir(exist_ok=True)
TRAIN=[1.75,2.00,2.75,3.25,3.75]
N_BLOCKS=30; N_GENS=250
Q_PRIMARY=np.round(np.arange(0.0,3.0001,0.125),3)
Q_TAIL=np.round(np.arange(3.125,5.0001,0.125),3)
Q_ALL=np.concatenate([Q_PRIMARY,Q_TAIL])
C=-0.149665377842; GAMMA=0.699255786271; ALPHA=0.44090926477; K=0.073893078378
PRED_PEAK={s:(ALPHA*s/2-C)/GAMMA for s in TRAIN}

def seed_for(s,bi):
    tag=f'MODEL_B_REDUCED_THEORY_T3|v1.0.0|train={s:.5f}|block={bi}'
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'little')

def collect_prior_seeds():
    roots=[
      SRCROOT/'control'/'SEED_LEDGER_v1.0.0.csv',
      Path('/mnt/data/prospective_test_work/identity/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0/control/SEED_LEDGER_v1.0.0.csv'),
      Path('/mnt/data/prospective_test_work/fidelity/MODEL_B_DCC_TRANSMISSION_FIDELITY_CONFIRMATORY_RUN_v1.0.0/control/SEED_LEDGER_v1.0.0.csv'),
      Path('/mnt/data/prospective12/reduced_theory_prospective_results/T2_mapping_level_results.csv')
    ]
    prior=set()
    for p in roots:
        if not p.exists(): continue
        d=pd.read_csv(p)
        for col in d.columns:
            if 'seed' in col.lower():
                vals=pd.to_numeric(d[col],errors='coerce').dropna().astype(np.uint64)
                prior.update(int(v) for v in vals.tolist())
    return prior

def evolve_one(args):
    s,bi,seed=args
    beta=float(s*THETA); params=params_for(beta)
    nw=int(params['n_cells']*params['n_seqs']*(params['seq_len']-4))
    init_rng=make_generator(seed,'T3-initialization',f'{s:.5f}')
    pop0=init_population(params['n_cells'],params['n_seqs'],params['seq_len'],init_rng)
    ps=pop0.copy(); pn=pop0.copy()
    obs_s=make_generator(seed,'T3-observation',f'{s:.5f}')
    rep_s=make_generator(seed,'T3-propagation-selected',f'{s:.5f}')
    rep_n=make_generator(seed,'T3-propagation-neutral',f'{s:.5f}')
    for g in range(N_GENS):
        u=obs_s.random(nw)
        fs,_,_=observe_with_uniforms(ps,params,u)
        ps=reproduce_with_partitioning(ps,fs,MU,P_INHERIT,rep_s)
        pn=reproduce_with_partitioning(pn,np.ones(params['n_cells'],dtype=float),MU,P_INHERIT,rep_n)
    fn=STATES/f'T3_S{s:.2f}_B{bi:02d}_g250.npz'
    np.savez_compressed(fn,g0=pop0,selected_g250=ps,neutral_g250=pn,seed=np.uint32(seed),q_train=np.float64(s),beta_train=np.float64(beta))
    return str(fn)

def sigmoid(x): return 1.0/(1.0+np.exp(-np.asarray(x,float)))
def js_bern(p,q):
    p=np.asarray(p,float); q=np.asarray(q,float); m=.5*(p+q)
    eps=1e-15
    p=np.clip(p,eps,1-eps); q=np.clip(q,eps,1-eps); m=np.clip(m,eps,1-eps)
    return .5*(p*np.log2(p/m)+(1-p)*np.log2((1-p)/(1-m))) + .5*(q*np.log2(q/m)+(1-q)*np.log2((1-q)/(1-m)))
def pred_curve(q,s):
    p0=sigmoid(C+GAMMA*np.asarray(q,float))
    p1=sigmoid(C+GAMMA*np.asarray(q,float)-ALPHA*s)
    return K*js_bern(p1,p0)

def r2(y,yh):
    y=np.asarray(y,float); yh=np.asarray(yh,float); den=np.sum((y-y.mean())**2)
    return float(1-np.sum((y-yh)**2)/den)
def rmse(y,yh): return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(yh))**2)))

if __name__=='__main__':
    allseeds=[seed_for(s,b) for s in TRAIN for b in range(N_BLOCKS)]
    assert len(set(allseeds))==len(allseeds)
    prior=collect_prior_seeds(); collisions=set(allseeds)&prior
    if collisions: raise RuntimeError(f'seed collision count={len(collisions)}')
    (OUT/'SEED_AUDIT_T3.json').write_text(json.dumps({'n_new_seeds':len(allseeds),'unique':len(set(allseeds)),'prior_seed_count_checked':len(prior),'collision_count':0},indent=2)+'\n')
    jobs=[(s,b,seed_for(s,b)) for s in TRAIN for b in range(N_BLOCKS) if not (STATES/f'T3_S{s:.2f}_B{b:02d}_g250.npz').exists()]
    workers=min(6,os.cpu_count() or 2)
    print('T3 EVOLUTION START jobs',len(jobs),'workers',workers,flush=True)
    if jobs:
      with ProcessPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(evolve_one,j):j for j in jobs}
        done=0
        for fut in as_completed(futs):
            fut.result(); done+=1
            if done%10==0 or done==len(jobs): print('evolved',done,'/',len(jobs),flush=True)
    rows=[]
    for s in TRAIN:
      params=params_for(float(s*THETA)); aff=params['motif_affinity_matrix']
      for bi in range(N_BLOCKS):
        z=np.load(STATES/f'T3_S{s:.2f}_B{bi:02d}_g250.npz')
        ps=z['selected_g250']; pn=z['neutral_g250']; seed=int(z['seed'])
        for q in Q_ALL:
          beta=float(q*THETA)
          cs=c_down_primary(ps,aff,NATIVE,beta,THETA)['jsd_bits']
          cn=c_down_primary(pn,aff,NATIVE,beta,THETA)['jsd_bits']
          rows.append(dict(q_train=s,block_index=bi,seed=seed,q_probe=float(q),C_selected=cs,C_neutral=cn,DeltaC=cs-cn,primary_grid=bool(q<=3.0)))
    raw=pd.DataFrame(rows); raw.to_csv(OUT/'T3_raw_retrieval.csv',index=False)
    summary=(raw.groupby(['q_train','q_probe','primary_grid']).agg(n_blocks=('DeltaC','size'),DeltaC_mean=('DeltaC','mean'),DeltaC_sd=('DeltaC','std'),C_selected_mean=('C_selected','mean'),C_neutral_mean=('C_neutral','mean')).reset_index())
    summary['DeltaC_pred']=[float(pred_curve(q,s)) for s,q in zip(summary.q_train,summary.q_probe)]
    summary.to_csv(OUT/'T3_retrieval_summary.csv',index=False)
    prim=summary[summary.primary_grid].copy()
    peaks=[]
    for s,g in prim.groupby('q_train'):
      row=g.loc[g.DeltaC_mean.idxmax()]
      pred=PRED_PEAK[float(s)]; err=float(row.q_probe-pred)
      peaks.append(dict(q_train=float(s),q_peak_pred=float(pred),q_peak_obs=float(row.q_probe),signed_error=err,abs_error=abs(err),within_one_grid=bool(abs(err)<=0.125+1e-12),peak_DeltaC=float(row.DeltaC_mean)))
    peaks=pd.DataFrame(peaks); peaks.to_csv(OUT/'T3_peak_results.csv',index=False)
    rho,pval=spearmanr(peaks.q_train,peaks.signed_error)
    pooled_r2=r2(prim.DeltaC_mean,prim.DeltaC_pred); pooled_rmse=rmse(prim.DeltaC_mean,prim.DeltaC_pred)
    res={
      'plan_sha256':hashlib.sha256((OUT/'PROSPECTIVE_PLAN_T3_v1.0.0.md').read_bytes()).hexdigest(),
      'execution_spec_sha256':hashlib.sha256((OUT/'EXECUTION_SPEC_T3_v1.0.0.md').read_bytes()).hexdigest(),
      'n_training_strengths':5,'n_blocks_per_strength':30,'n_evolution_pairs':150,'n_evolution_runs':300,
      'primary_peak_success_count':int(peaks.within_one_grid.sum()),'primary_peak_required':4,'primary_peak_pass':bool(peaks.within_one_grid.sum()>=4),
      'peak_results':peaks.to_dict(orient='records'),
      'signed_error_spearman':{'rho':float(rho),'two_sided_p':float(pval),'no_systematic_monotonic_bias_pass':bool(pval>=0.05)},
      'full_curve_no_refit':{'R2':pooled_r2,'RMSE':pooled_rmse,'n_points':int(len(prim))},
      'seed_collision_audit':'PASS'
    }
    (OUT/'T3_RESULT_SUMMARY.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print(json.dumps(res,indent=2,sort_keys=True))
