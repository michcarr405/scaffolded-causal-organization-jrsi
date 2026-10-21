from pathlib import Path
import sys, hashlib, json, math, os
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd

SRCROOT=Path('/mnt/data/prospective_test_work/identity/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0')
sys.path.insert(0,str(SRCROOT/'scripts'))
from dcc_pipeline import make_params, observe, motif_tensor, probe_mapping_fitnesses_from_motifs, P_INHERIT, MU, BETA, THETA
sys.path.insert(0,str(SRCROOT/'source'))
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator

OUT=Path('/mnt/data/reduced_theory_prospective_T3T4/T4')
STATES=OUT/'states'; STATES.mkdir(exist_ok=True)
H=(2,0,3,1); N_BLOCKS=30; N_GENS=250; N_DRAWS=32; LAM=326.128666514
BOOT_N=50000; BOOT_SEED=184920177
DESIGN=pd.read_csv(OUT/'T4_PROBE_SCAFFOLDS_FROZEN.csv')
BCOLS=[f'b{s}_{z}' for s in range(4) for z in range(4)]
BIAS=DESIGN[BCOLS].to_numpy(float).reshape(-1,4,4)
TARGETS=sorted(float(x) for x in DESIGN.loc[DESIGN.distance_target>0,'distance_target'].unique())

def seed_for(bi):
    tag=f'MODEL_B_REDUCED_THEORY_T4|v1.0.0|block={bi}'
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'little')

def prior_seeds():
    files=[
      SRCROOT/'control'/'SEED_LEDGER_v1.0.0.csv',
      Path('/mnt/data/prospective_test_work/strength/MODEL_B_DCC_SCAFFOLD_STRENGTH_CONFIRMATORY_RUN_v1.0.0/control/SEED_LEDGER_v1.0.0.csv'),
      Path('/mnt/data/prospective_test_work/fidelity/MODEL_B_DCC_TRANSMISSION_FIDELITY_CONFIRMATORY_RUN_v1.0.0/control/SEED_LEDGER_v1.0.0.csv'),
      Path('/mnt/data/prospective12/reduced_theory_prospective_results/T2_mapping_level_results.csv'),
      Path('/mnt/data/reduced_theory_prospective_T3T4/T3/T3_raw_retrieval.csv')
    ]
    out=set()
    for p in files:
      if not p.exists(): continue
      d=pd.read_csv(p)
      for c in d.columns:
        if 'seed' in c.lower():
          vals=pd.to_numeric(d[c],errors='coerce').dropna().astype(np.uint64)
          out.update(int(v) for v in vals.tolist())
    return out

def evolve_one(args):
    bi,seed=args; params=make_params(H)
    pop0=init_population(params['n_cells'],params['n_seqs'],params['seq_len'],make_generator(seed,'T4-initialization'))
    ps=pop0.copy(); pn=pop0.copy()
    obs_s=make_generator(seed,'T4-observation-selected')
    rep_s=make_generator(seed,'T4-propagation-selected')
    rep_n=make_generator(seed,'T4-propagation-neutral')
    for g in range(N_GENS):
        fs,_,_=observe(ps,params,obs_s)
        ps=reproduce_with_partitioning(ps,fs,MU,P_INHERIT,rep_s)
        pn=reproduce_with_partitioning(pn,np.ones(params['n_cells'],dtype=float),MU,P_INHERIT,rep_n)
    fn=STATES/f'T4_B{bi:02d}_g250.npz'
    np.savez_compressed(fn,g0=pop0,selected_g250=ps,neutral_g250=pn,seed=np.uint32(seed),historical_mapping=np.array(H,dtype=np.int64))
    return str(fn)

def cdf_table(affinity):
    table=np.empty((len(BIAS),4,affinity.shape[0],4),float)
    for i,b in enumerate(BIAS):
        logits=affinity[None,:,:]+b[:,None,:]
        x=logits/THETA; x=x-x.max(axis=2,keepdims=True); ex=np.exp(x); p=ex/ex.sum(axis=2,keepdims=True)
        table[i]=np.cumsum(p,axis=2)
    table[:,:,:,-1]=1.0
    return table

def Rpred(d): return (1-math.exp(-float(d)/LAM))/(1-math.exp(-64.0/LAM))
def r2(y,yh):
    y=np.asarray(y,float); yh=np.asarray(yh,float); den=np.sum((y-y.mean())**2)
    return float(1-np.sum((y-yh)**2)/den)
def rmse(y,yh): return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(yh))**2)))

if __name__=='__main__':
    seeds=[seed_for(i) for i in range(N_BLOCKS)]; assert len(set(seeds))==N_BLOCKS
    prior=prior_seeds(); col=set(seeds)&prior
    if col: raise RuntimeError(f'seed collisions {len(col)}')
    (OUT/'SEED_AUDIT_T4.json').write_text(json.dumps({'n_new_seeds':N_BLOCKS,'unique':len(set(seeds)),'prior_seed_count_checked':len(prior),'collision_count':0},indent=2)+'\n')
    jobs=[(i,seeds[i]) for i in range(N_BLOCKS) if not (STATES/f'T4_B{i:02d}_g250.npz').exists()]
    workers=min(5,os.cpu_count() or 2)
    print('T4 EVOLUTION START jobs',len(jobs),'workers',workers,flush=True)
    if jobs:
      with ProcessPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(evolve_one,j):j for j in jobs}
        done=0
        for fut in as_completed(futs):
          fut.result(); done+=1
          if done%5==0 or done==len(jobs): print('evolved',done,'/',len(jobs),flush=True)
    params=make_params(H); cdf=cdf_table(params['motif_affinity_matrix'])
    rows=[]
    for bi,seed in enumerate(seeds):
      z=np.load(STATES/f'T4_B{bi:02d}_g250.npz'); ps=z['selected_g250']; pn=z['neutral_g250']
      ms=motif_tensor(ps); mn=motif_tensor(pn); assert ms.size==mn.size
      u=make_generator(seed,'T4-cross-eval').random((N_DRAWS,ms.size))
      vs=probe_mapping_fitnesses_from_motifs(ms,cdf,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),u)
      vn=probe_mapping_fitnesses_from_motifs(mn,cdf,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),u)
      means_s=vs.mean(axis=1); means_n=vn.mean(axis=1); fh_s=float(means_s[0]); fh_n=float(means_n[0])
      for i,row in DESIGN.iterrows():
        As=fh_s-float(means_s[i]); An=fh_n-float(means_n[i])
        rows.append(dict(block_id=f'T4_B{bi:02d}',block_index=bi,seed=seed,scaffold_id=row.scaffold_id,distance=float(row.distance_target),phi_index=int(row.phi_index),Fhist_selected=fh_s,Fprobe_selected=float(means_s[i]),A_selected=As,Fhist_neutral=fh_n,Fprobe_neutral=float(means_n[i]),A_neutral=An,DeltaH=As-An))
      print('assayed',bi+1,'/',N_BLOCKS,flush=True)
    raw=pd.DataFrame(rows); raw.to_csv(OUT/'T4_probe_level_results.csv',index=False)
    alt=raw[raw.distance>0].copy()
    blockd=(alt.groupby(['block_id','block_index','seed','distance']).agg(DeltaH=('DeltaH','mean'),DeltaH_sd_orientation=('DeltaH','std'),A_selected=('A_selected','mean'),A_neutral=('A_neutral','mean'),n_orientations=('scaffold_id','size')).reset_index())
    b64=blockd.loc[np.isclose(blockd.distance,64.0),['block_id','DeltaH']].rename(columns={'DeltaH':'DeltaH64'})
    blockd=blockd.merge(b64,on='block_id',how='left'); blockd['R_obs']=blockd.DeltaH/blockd.DeltaH64
    blockd['R_pred']=blockd.distance.map(Rpred); blockd['R_local']=blockd.distance/64.0
    blockd.to_csv(OUT/'T4_block_distance_results.csv',index=False)
    # paired-block bootstrap means of normalized response
    rng=np.random.default_rng(BOOT_SEED)
    blocks=sorted(blockd.block_id.unique()); n=len(blocks)
    arr=np.stack([blockd[blockd.distance==d].set_index('block_id').loc[blocks,'R_obs'].to_numpy(float) for d in TARGETS],axis=1)
    idx=rng.integers(0,n,size=(BOOT_N,n)); bmeans=arr[idx].mean(axis=1)
    means=arr.mean(axis=0); sds=arr.std(axis=0,ddof=1)
    lo=np.quantile(bmeans,.025,axis=0); hi=np.quantile(bmeans,.975,axis=0)
    pred=np.array([Rpred(d) for d in TARGETS]); local=np.array(TARGETS)/64.0
    summary=pd.DataFrame({'distance':TARGETS,'R_obs_mean':means,'R_obs_sd':sds,'bootstrap95_lo':lo,'bootstrap95_hi':hi,'R_pred':pred,'R_local':local})
    summary.to_csv(OUT/'T4_distance_summary.csv',index=False)
    class_r2=r2(means,pred); class_rmse=rmse(means,pred); local_r2=r2(means,local); local_rmse=rmse(means,local)
    pooled_pred=np.tile(pred,(n,1)).reshape(-1); pooled_local=np.tile(local,(n,1)).reshape(-1); pooled_obs=arr.reshape(-1)
    res={
      'plan_sha256':hashlib.sha256((OUT/'PROSPECTIVE_PLAN_T4_v1.0.0.md').read_bytes()).hexdigest(),
      'execution_spec_sha256':hashlib.sha256((OUT/'EXECUTION_SPEC_T4_v1.0.0.md').read_bytes()).hexdigest(),
      'design_csv_sha256':hashlib.sha256((OUT/'T4_PROBE_SCAFFOLDS_FROZEN.csv').read_bytes()).hexdigest(),
      'n_blocks':N_BLOCKS,'n_probe_draws':N_DRAWS,'target_distances':TARGETS,'orientations_per_distance':4,
      'zero_parameter_finite_distance':{'lambda':LAM,'class_mean_R2':class_r2,'class_mean_RMSE':class_rmse,'pooled_block_R2':r2(pooled_obs,pooled_pred),'pooled_block_RMSE':rmse(pooled_obs,pooled_pred)},
      'local_distance_law':{'class_mean_R2':local_r2,'class_mean_RMSE':local_rmse,'pooled_block_R2':r2(pooled_obs,pooled_local),'pooled_block_RMSE':rmse(pooled_obs,pooled_local)},
      'finite_distance_better_RMSE':bool(class_rmse<local_rmse),
      'mean_normalized_response':{str(int(d)):float(v) for d,v in zip(TARGETS,means)},
      'prediction':{str(int(d)):float(v) for d,v in zip(TARGETS,pred)},
      'seed_collision_audit':'PASS'
    }
    (OUT/'T4_RESULT_SUMMARY.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print(json.dumps(res,indent=2,sort_keys=True))
