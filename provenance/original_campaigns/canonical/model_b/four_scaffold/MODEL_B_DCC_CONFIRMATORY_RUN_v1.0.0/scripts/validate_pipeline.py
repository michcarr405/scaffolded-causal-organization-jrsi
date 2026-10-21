from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import numba

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "source"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

from dcc_pipeline import (
    BETA, CHECKPOINTS, N_GENS, N_MOTIFS, N_PROBE_DRAWS, N_SEGMENTS, N_UNIT_SHUFFLES,
    P_INHERIT, PROBE_IDS, PROBE_MAPPINGS, THETA,
    c_down_from_counts, c_down_primary, cross_evaluate, historical_match_score,
    jsd_bits, make_kernel, make_params, motif_segment_counts, motif_tensor,
    population_segment_labels, probe_mapping_fitnesses_from_motifs, run_pair_block,
    state_hash, unit_segment_labels, unitshuffle_cdown,
)
from confirmatory_stats import _seeded_rng, exact_one_sided_sign_test, holm_adjust, mean_bootstrap_ci, stratified_pooled_bootstrap
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.core import compute_fitnesses_and_observations
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning, run_single_sim
from modelb_semantic_repo.rng import make_generator

EXPL = Path('/mnt/data/ratio_exp/modelb_ratio_sweep_exploratory')
REPORT = ROOT / 'validation' / 'VALIDATION_REPORT_v1.0.0.json'
REPORT_MD = ROOT / 'validation' / 'VALIDATION_REPORT_v1.0.0.md'

EXPECTED_GIT_BLOBS = {
    'modelb_semantic_repo/rng.py':'12db759752491941b4901cdcae9ee376cd24567f',
    'modelb_semantic_repo/information.py':'a9df476f6292574bc3195273f0671799239af2d6',
    'modelb_semantic_repo/original_model/__init__.py':'fc5c4c694c05aa863d14b73716622afc34c4e0df',
    'modelb_semantic_repo/original_model/config.py':'d1b251326b88bd4049bb1e4492c309999ac840a1',
    'modelb_semantic_repo/original_model/core.py':'04f85796c61dbd46166dd24a95583c740f8fb999',
    'modelb_semantic_repo/original_model/mi.py':'0df0656ff1dcab044647228d40193fdf50f2adc9',
    'modelb_semantic_repo/original_model/simulation.py':'3c2bd7a4f8fbddc001f7fdf6fe243551cd134a4e',
    'modelb_semantic_repo/original_model/sweeps.py':'0d403b069449c68de3523c8a1990c5e47706c2f9',
}

class Recorder:
    def __init__(self):
        self.items=[]
    def check(self, section, name, condition, details=None):
        ok=bool(condition)
        self.items.append({'section':section,'name':name,'status':'PASS' if ok else 'FAIL','details':details})
        if not ok:
            raise AssertionError(f'{section}: {name}: {details}')
    def summary(self):
        return {'pass':sum(x['status']=='PASS' for x in self.items),'fail':sum(x['status']=='FAIL' for x in self.items),'total':len(self.items)}


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def file_map(path: Path):
    return {str(p.relative_to(path)):sha256_file(p) for p in sorted(path.rglob('*')) if p.is_file()}


def mi_from_joint(j):
    p=np.asarray(j,dtype=float); p=p/p.sum(); px=p.sum(1,keepdims=True); py=p.sum(0,keepdims=True); e=px@py; m=p>0
    return float(np.sum(p[m]*np.log2(p[m]/e[m])))


def exploratory_pair(rep: int):
    seeds=pd.read_csv(EXPL/'seed_ledger.csv')
    seed=int(seeds.loc[seeds.replicate==rep,'seed'].iloc[0])
    return {
        'paired_block_id':f'VAL_EXP_B{rep:02d}',
        'scaffold_id':'SCF0',
        'scaffold_mapping':'[2,0,3,1]',
        'base_seed_uint32':seed,
        'selected_run_id':f'VAL_EXP_B{rep:02d}_SELECTED',
        'neutral_run_id':f'VAL_EXP_B{rep:02d}_NEUTRAL',
    }


def main():
    rec=Recorder()
    raw_pairs=list((ROOT/'raw'/'endpoints').glob('*_PAIR.json'))
    rec.check('H','No confirmatory outcome exists before validation',len(raw_pairs)==0,{'existing_pair_files':len(raw_pairs)})

    # A. Canonical source and model wrapper.
    blob_audit={}
    for rel,expected in EXPECTED_GIT_BLOBS.items():
        p=SRC/rel
        got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
        blob_audit[rel]={'expected':expected,'observed':got,'match':got==expected}
    rec.check('A','Canonical source git-blob audit',all(x['match'] for x in blob_audit.values()),blob_audit)
    params=default_parameters()
    rec.check('A','Canonical population shape parameters',(params['n_cells'],params['n_seqs'],params['seq_len'])==(80,8,60),{k:params[k] for k in ['n_cells','n_seqs','seq_len']})
    rec.check('A','Four-symbol k=5 four-segment four-state architecture',params['n_metabolites']==4 and len(params['segment_favored_met'])==4 and params['motif_affinity_matrix'].shape==(1024,4),{'affinity_shape':params['motif_affinity_matrix'].shape})
    aff_ref=np.random.default_rng(123).normal(0,1,size=(1024,4))
    rec.check('A','Affinity matrix seed 123 exact',np.array_equal(params['motif_affinity_matrix'],aff_ref),None)
    p4=make_params((2,0,3,1))
    rec.check('A','Frozen beta and Theta',p4['bias_strength']==4.0 and p4['temperature']==1.2,{'beta':p4['bias_strength'],'Theta':p4['temperature']})
    rec.check('A','Frozen fitness and mutation parameters',p4['reward_strength']==2.0 and p4['penalty_strength']==0.5 and p4['mutation_rate']==0.001,{'reward':p4['reward_strength'],'penalty':p4['penalty_strength'],'mu':p4['mutation_rate']})
    ker=make_kernel(p4['motif_affinity_matrix'],(2,0,3,1),4.0,1.2)
    m=17; s=2
    logits=p4['motif_affinity_matrix'][m].copy(); logits[(2,0,3,1)[s]]+=4.0; x=logits/1.2; x-=x.max(); manual=np.exp(x); manual/=manual.sum()
    rec.check('A','Local-state logit and softmax law',np.allclose(ker[s,m],manual,rtol=0,atol=1e-15),{'kernel':ker[s,m].tolist(),'manual':manual.tolist()})
    # Same-seed deterministic short canonical trajectories and different seed divergence.
    pa=dict(p4); pa['n_gens']=4
    f1,i1=run_single_sim(pa['mutation_rate'],P_INHERIT,812345,pa['motif_affinity_matrix'],pa)
    f2,i2=run_single_sim(pa['mutation_rate'],P_INHERIT,812345,pa['motif_affinity_matrix'],pa)
    f3,i3=run_single_sim(pa['mutation_rate'],P_INHERIT,812346,pa['motif_affinity_matrix'],pa)
    rec.check('A','Same-seed determinism',np.array_equal(f1,f2) and np.array_equal(i1,i2),None)
    rec.check('A','Different-seed divergence',not np.array_equal(f1,f3),None)

    # B. Pairing and RNG separation.
    seed=123456789
    init1=make_generator(seed,'baseline-initialization'); init2=make_generator(seed,'baseline-initialization')
    pop1=init_population(80,8,60,init1); pop2=init_population(80,8,60,init2)
    rec.check('B','Selected-neutral identical ancestor arrays',np.array_equal(pop1,pop2),{'hash':state_hash(pop1)})
    u1=make_generator(seed,'baseline-observation').random(1000); u2=make_generator(seed,'baseline-observation').random(1000)
    rec.check('B','Observation CRN stream identity',np.array_equal(u1,u2),None)
    q1=make_generator(seed,'baseline-propagation').random(1000); q2=make_generator(seed,'baseline-propagation').random(1000)
    rec.check('B','Propagation CRN stream identity',np.array_equal(q1,q2),None)
    rec.check('B','Purpose-separated streams differ',not np.array_equal(u1,q1),None)
    seeds_conf=pd.read_csv(ROOT/'control'/'SEED_LEDGER_v1.0.0.csv')
    seeds_exp=set(pd.read_csv(EXPL/'seed_ledger.csv').seed.astype(int).tolist())
    conf_list=seeds_conf.base_seed_uint32.astype(int).tolist()
    rec.check('B','All 120 confirmatory base seeds unique',len(conf_list)==120 and len(set(conf_list))==120,{'n':len(conf_list),'unique':len(set(conf_list))})
    rec.check('B','No confirmatory seed overlaps exploratory 20-seed ledger',set(conf_list).isdisjoint(seeds_exp),{'overlap':sorted(set(conf_list)&seeds_exp)})
    # Hidden global RNG audit: compiled core contains no random call; simulation RNG calls require explicit generator except fixed config seed.
    core_text=(SRC/'modelb_semantic_repo/original_model/core.py').read_text()
    sim_text=(SRC/'modelb_semantic_repo/original_model/simulation.py').read_text()
    rec.check('B','No hidden global RNG in claim-bearing core','np.random' not in core_text and 'np.random.' not in sim_text,{'core_np_random':'np.random' in core_text,'simulation_np_random_dot':'np.random.' in sim_text})

    # C. Primary estimator synthetic invariants.
    toy=np.zeros((4,8),dtype=float)
    toy[0,0]=5; toy[0,1]=1; toy[1,2]=6; toy[2,3]=6; toy[3,4]=6
    toy/=toy.sum()
    ps=toy.sum(axis=1,keepdims=True); pm=toy.sum(axis=0,keepdims=True); erased=ps@pm
    rec.check('C','P(S)P(M) preserves marginals',np.max(np.abs(erased.sum(0)-pm.reshape(-1)))<=1e-12 and np.max(np.abs(erased.sum(1)-ps.reshape(-1)))<=1e-12,None)
    factor=np.full((4,1024),1.0/(4*1024))
    out=c_down_from_counts((factor*4096).astype(int),make_kernel(p4['motif_affinity_matrix'],(2,0,3,1),4.0,1.2))
    rec.check('C','Factorized P(S,M) gives zero primary C_down',out['jsd_bits']<=1e-12,{'value':out['jsd_bits']})
    # Motif-independent but segment-dependent kernel.
    base=np.array([0.1,0.2,0.3,0.4]); kin=np.empty((4,1024,4))
    for ss in range(4): kin[ss,:,:]=np.roll(base,ss)
    counts=np.zeros((4,1024),dtype=int); counts[0,0]=500; counts[1,1]=500; counts[2,2]=500; counts[3,3]=500
    out2=c_down_from_counts(counts,kin)
    rec.check('C','Motif-independent readout null',out2['jsd_bits']<=1e-12,{'value':out2['jsd_bits']})
    rec.check('C','JSD anchors and bounds',jsd_bits([1,0],[1,0])==0.0 and abs(jsd_bits([1,0],[0,1])-1.0)<1e-15 and abs(jsd_bits([.3,.7],[.6,.4])-jsd_bits([.6,.4],[.3,.7]))<1e-15,None)
    # Relabeling represented joint by a simultaneous motif permutation leaves value invariant when kernel is relabeled too.
    rng=np.random.default_rng(44); cc=rng.integers(0,20,size=(4,1024)); perm=rng.permutation(1024); kx=make_kernel(p4['motif_affinity_matrix'],(2,0,3,1),4.0,1.2)
    a=c_down_from_counts(cc,kx)['jsd_bits']; b=c_down_from_counts(cc[:,perm],kx[:,perm,:])['jsd_bits']
    rec.check('C','Joint/kernel motif relabeling invariance',abs(a-b)<1e-15,{'a':a,'b':b})
    # Replay archived exploratory C_down on eight beta=4 endpoint states.
    ep=pd.read_csv(EXPL/'endpoint_metrics.csv'); ep=ep[np.isclose(ep.beta,4.0)]
    replay=[]
    for rep in range(4):
        for mode in ('selected','neutral'):
            path=EXPL/'states'/f'{mode}_r3p333333_rep{rep:02d}.npz'
            with np.load(path) as z:
                pop=z['final']
            val=c_down_primary(pop,p4['motif_affinity_matrix'],(2,0,3,1),4.0,1.2)['jsd_bits']
            ref=float(ep[(ep.replicate==rep)&(ep['mode']==mode)].C_down_train_g250.iloc[0])
            replay.append({'rep':rep,'mode':mode,'observed':val,'reference':ref,'abs_diff':abs(val-ref)})
    maxdiff=max(x['abs_diff'] for x in replay)
    rec.check('C','Archived exploratory C_down replay to 1e-12',maxdiff<=1e-12,{'max_abs_diff':maxdiff,'rows':replay})

    # D. Unit-stratified exact-margin intervention.
    state=EXPL/'states'/'selected_r3p333333_rep00.npz'
    with np.load(state) as z: pop=z['final']; eseed=int(z['seed'])
    m3=motif_tensor(pop); unit=m3.reshape(80,-1); useg=unit_segment_labels(8,60)
    rr=make_generator(eseed,'confirmatory-unitshuffle'); sh=rr.permuted(unit,axis=1)
    per_unit_ok=all(np.array_equal(np.bincount(unit[i],minlength=1024),np.bincount(sh[i],minlength=1024)) for i in range(80))
    rec.check('D','Each unit motif multiset preserved exactly',per_unit_ok,None)
    rec.check('D','Each unit has 112 fixed slots in every segment',all(int(np.sum(useg==s))==112 for s in range(4)),[int(np.sum(useg==s)) for s in range(4)])
    rec.check('D','No motif crosses model-unit identity',per_unit_ok,None)
    r128=unitshuffle_cdown(pop,p4['motif_affinity_matrix'],(2,0,3,1),eseed,128)
    r128b=unitshuffle_cdown(pop,p4['motif_affinity_matrix'],(2,0,3,1),eseed,128)
    rec.check('D','Same base/shuffle stream deterministic',r128['mean_jsd_bits']==r128b['mean_jsd_bits'],{'value':r128['mean_jsd_bits']})
    # Different root seed should alter sampled intervention value.
    rd=unitshuffle_cdown(pop,p4['motif_affinity_matrix'],(2,0,3,1),eseed+1,128)
    rec.check('D','Different shuffle key changes reassignment',r128['mean_jsd_bits']!=rd['mean_jsd_bits'],{'a':r128['mean_jsd_bits'],'b':rd['mean_jsd_bits']})
    rec.check('D','Global motif and segment margins preserved',r128['max_global_motif_count_error']==0 and r128['max_segment_size_error']==0,r128)
    # Strong synthetic motif-segment association disruption.
    syn=np.empty((80,8,56),dtype=np.int64)
    posseg=np.repeat(np.arange(4),14)
    for ci in range(80):
        for si in range(8): syn[ci,si]=posseg
    jc=np.zeros((4,1024),int); flat_s=np.broadcast_to(posseg,syn.shape).reshape(-1); flat_m=syn.reshape(-1); np.add.at(jc,(flat_s,flat_m),1)
    before_mi=mi_from_joint(jc)
    u=syn.reshape(80,-1); srng=make_generator(777,'confirmatory-unitshuffle'); ush=srng.permuted(u,axis=1); aseg=np.broadcast_to(useg,u.shape).reshape(-1); ac=np.bincount(aseg*1024+ush.reshape(-1),minlength=4096).reshape(4,1024)
    after_mi=mi_from_joint(ac)
    rec.check('D','Strong synthetic motif-segment association is disrupted',after_mi < 0.1*before_mi,{'before_mi':before_mi,'after_mi':after_mi})
    null1=unitshuffle_cdown(pop,p4['motif_affinity_matrix'],(2,0,3,1),eseed,128)['mean_jsd_bits']; null2=unitshuffle_cdown(pop,p4['motif_affinity_matrix'],(2,0,3,1),eseed,128)['mean_jsd_bits']
    rec.check('D','Identical selected-neutral synthetic null has zero delta',null1-null2==0.0,{'delta':null1-null2})
    conv=[]
    for rep in range(4):
        for mode in ('selected','neutral'):
            path=EXPL/'states'/f'{mode}_r3p333333_rep{rep:02d}.npz'
            with np.load(path) as z: pp=z['final']; sd=int(z['seed'])
            a=unitshuffle_cdown(pp,p4['motif_affinity_matrix'],(2,0,3,1),sd,128)['mean_jsd_bits']
            b=unitshuffle_cdown(pp,p4['motif_affinity_matrix'],(2,0,3,1),sd,2048)['mean_jsd_bits']
            conv.append({'rep':rep,'mode':mode,'K128':a,'K2048':b,'abs_diff':abs(a-b)})
    convmax=max(x['abs_diff'] for x in conv)
    rec.check('D','K=128 common-prefix convergence <=1e-5 bits',convmax<=1e-5,{'max_abs_diff':convmax,'rows':conv})

    # E. Cross-evaluation.
    rec.check('E','Frozen probe mapping identities',tuple(PROBE_MAPPINGS)==((2,0,3,1),(0,1,2,3),(1,3,0,2),(3,2,1,0)),PROBE_MAPPINGS)
    rng=make_generator(eseed,'confirmatory-cross-eval'); common=rng.random((16,m3.size))
    ce1=cross_evaluate(pop,p4,eseed,PROBE_MAPPINGS,16,uniforms=common)
    ce2=cross_evaluate(pop,p4,eseed,PROBE_MAPPINGS,16,uniforms=common)
    rec.check('E','Sixteen cross-evaluation draws',ce1['draw_values'].shape==(4,16),{'shape':ce1['draw_values'].shape})
    rec.check('E','Cross-evaluation common uniforms deterministic',np.array_equal(ce1['draw_values'],ce2['draw_values']),None)
    # Canonical core agrees for SCF0 on first draw.
    fcore,_,_=compute_fitnesses_and_observations(pop,p4['motif_affinity_matrix'],np.array(PROBE_MAPPINGS[0],dtype=np.int64),4.0,p4['productive_pairs'],p4['anti_pairs'],2.0,0.5,1.2,common[0])
    rec.check('E','Optimized cross-eval agrees with canonical core',abs(float(fcore.mean())-float(ce1['draw_values'][0,0]))<1e-12,{'core':float(fcore.mean()),'probe':float(ce1['draw_values'][0,0])})
    rec.check('E','Historical-match toy formula',abs(historical_match_score(np.array([10.,4.,7.,1.]),0)-6.0)<1e-15,None)
    rec.check('E','Canonical native/reversed are SCF0 and SCF2',PROBE_MAPPINGS[0]==(2,0,3,1) and PROBE_MAPPINGS[2]==(1,3,0,2),None)

    # F. Statistical pipeline.
    v=np.array([1.,2.,3.,4.,5.]); boot=mean_bootstrap_ci(v,ci=.95,n_boot=50000,key='validation-positive')
    rec.check('F','Bootstrap resamples paired-block vector and positive CI',boot['n']==5 and boot['low']>0,boot)
    b9875=mean_bootstrap_ci(v,ci=.9875,n_boot=50000,key='validation-9875')
    rec.check('F','98.75% interval implementation',abs(b9875['ci']-.9875)<1e-15,b9875)
    s_all=exact_one_sided_sign_test(np.ones(10)); s_mix=exact_one_sided_sign_test(np.array([1,1,1,1,1,0,-1,-1,-1,-1])); s_zero=exact_one_sided_sign_test(np.zeros(10))
    rec.check('F','Exact sign test all-positive/mixed/all-zero behavior',s_all['p_value']<.01 and s_zero['p_value']==1.0 and s_mix['positive']==5,{'all':s_all,'mixed':s_mix,'zero':s_zero})
    adj=holm_adjust([.01,.04,.03])
    rec.check('F','Holm hand-computable example',np.allclose(adj,[.03,.06,.06]),{'adjusted':adj.tolist()})
    pooled=stratified_pooled_bootstrap({'SCF0':np.array([1.,2.]),'SCF1':np.array([3.,4.]),'SCF2':np.array([5.,6.]),'SCF3':np.array([7.,8.])},ci=.95,n_boot=50000,key='validation-pooled')
    rec.check('F','Stratified pooled bootstrap equal-weights mapping means',abs(pooled['mean']-4.5)<1e-15,pooled)
    # Deterministic bootstrap.
    rga=_seeded_rng('validation-purpose-a').random(64); rgb=_seeded_rng('validation-purpose-a').random(64); rgc=_seeded_rng('validation-purpose-b').random(64)
    rec.check('F','Bootstrap RNG deterministic and purpose-separated',boot==mean_bootstrap_ci(v,ci=.95,n_boot=50000,key='validation-positive') and np.array_equal(rga,rgb) and not np.array_equal(rga,rgc),None)

    # G. Manifests.
    run=pd.read_csv(ROOT/'control'/'RUN_MANIFEST_FROZEN_v1.0.0.csv')
    pairs=pd.read_csv(ROOT/'control'/'PAIRED_BLOCK_MANIFEST_v1.0.0.csv')
    rec.check('G','Run manifest has 240 unique IDs',len(run)==240 and run.run_id.nunique()==240,{'rows':len(run),'unique':run.run_id.nunique()})
    rec.check('G','Paired manifest has 120 unique blocks',len(pairs)==120 and pairs.paired_block_id.nunique()==120,{'rows':len(pairs),'unique':pairs.paired_block_id.nunique()})
    counts=pairs.groupby('scaffold_id').size().to_dict()
    rec.check('G','Exactly 30 paired blocks per scaffold',counts=={'SCF0':30,'SCF1':30,'SCF2':30,'SCF3':30},counts)
    modes=run.groupby('paired_block_id')['mode'].agg(lambda x:sorted(x.tolist()))
    rec.check('G','Every paired block has selected and neutral runs',all(x==['neutral','selected'] for x in modes),None)
    rec.check('G','Every run has one frozen base seed',run.base_seed_uint32.notna().all(),None)
    rec.check('G','Expected output paths unique',run.expected_state_file.nunique()==240 and run.expected_metrics_file.nunique()==240,None)
    # Dry parser checks all scientific fields parse without simulation.
    parsed=0
    for r in run.itertuples(index=False):
        mp=json.loads(r.scaffold_mapping); assert len(mp)==4; int(r.base_seed_uint32); float(r.beta); float(r.theta); parsed+=1
    rec.check('G','Dry-run parser resolves every run row',parsed==240,{'parsed':parsed})
    required={'run_id','paired_block_id','scaffold_id','mode','base_seed_uint32','generation','C_down_primary','population_hash','validation_version'}
    # Schema is established from runner source fields.
    source=(HERE/'dcc_pipeline.py').read_text()
    rec.check('G','Output schema contains required fields',all(f'"{x}"' in source for x in required),sorted(required))

    # Full archived exploratory replay and scheduling-order byte determinism.
    vroot=ROOT/'validation'/'replay'
    if vroot.exists(): shutil.rmtree(vroot)
    serial=vroot/'serial'; parallel=vroot/'parallel'
    for d in (serial,parallel):
        for sub in ('raw/states','raw/metrics','raw/endpoints'): (d/sub).mkdir(parents=True,exist_ok=True)
    p0=exploratory_pair(0); p1=exploratory_pair(1)
    run_pair_block(p0,serial,validation_version='v1.0.0-validation')
    run_pair_block(p1,serial,validation_version='v1.0.0-validation')
    # Reversed submission order under a process pool.
    with ProcessPoolExecutor(max_workers=2) as ex:
        fut1=ex.submit(run_pair_block,p1,parallel,'v1.0.0-validation')
        fut0=ex.submit(run_pair_block,p0,parallel,'v1.0.0-validation')
        fut1.result(); fut0.result()
    sm=file_map(serial); pm=file_map(parallel)
    rec.check('A','Parallel scheduling/order yields byte-identical run outputs',sm==pm,{'serial_files':len(sm),'parallel_files':len(pm),'mismatches':sorted(set(k for k in set(sm)|set(pm) if sm.get(k)!=pm.get(k)))[:10]})
    # Compare replay states and endpoint metrics to archived exploratory rep0/1 at beta=4.
    repdiff=[]
    for rep in (0,1):
        for mode,tag in (('selected','SELECTED'),('neutral','NEUTRAL')):
            with np.load(serial/'raw'/'states'/f'VAL_EXP_B{rep:02d}_{tag}_g250.npz') as z: got=z['g250']; anc=z['g0']
            with np.load(EXPL/'states'/f'{mode}_r3p333333_rep{rep:02d}.npz') as z: ref=z['final']; ar=z['ancestor']
            repdiff.append({'rep':rep,'mode':mode,'final_differing_sites':int(np.sum(got!=ref)),'ancestor_differing_sites':int(np.sum(anc!=ar))})
    rec.check('A','Canonical wrapper reproduces archived exploratory final states exactly',all(x['final_differing_sites']==0 and x['ancestor_differing_sites']==0 for x in repdiff),repdiff)
    # Endpoint fitness/Cdown exact replay for those four runs.
    metricdiff=[]
    for rep in (0,1):
        for mode,tag in (('selected','SELECTED'),('neutral','NEUTRAL')):
            mdf=pd.read_csv(serial/'raw'/'metrics'/f'VAL_EXP_B{rep:02d}_{tag}_metrics.csv'); row=mdf[mdf.generation==250].iloc[0]
            ref=ep[(ep.replicate==rep)&(ep['mode']==mode)].iloc[0]
            metricdiff.append({'rep':rep,'mode':mode,'fitness_abs_diff':abs(float(row.mean_fitness)-float(ref.fitness_g250)),'cdown_abs_diff':abs(float(row.C_down_primary)-float(ref.C_down_train_g250))})
    rec.check('A','Canonical wrapper reproduces archived exploratory endpoint metrics',max(max(x['fitness_abs_diff'],x['cdown_abs_diff']) for x in metricdiff)<=1e-12,metricdiff)

    # H. Gate decision and environment.
    env={
        'python':sys.version,
        'platform':platform.platform(),
        'numpy':np.__version__,
        'scipy':scipy.__version__,
        'numba':numba.__version__,
    }
    rec.check('H','Validation completed without confirmatory production outcome inspection',len(list((ROOT/'raw'/'endpoints').glob('*_PAIR.json')))==0,None)
    summary=rec.summary()
    result={
        'validation_version':'v1.0.0',
        'scientific_commit':'2c7d78694579755402c0a1896e109b29dec4d6a0',
        'gate':'PASS' if summary['fail']==0 else 'FAIL',
        'summary':summary,
        'environment':env,
        'canonical_source_blob_audit':blob_audit,
        'checks':rec.items,
        'confirmatory_outcomes_inspected_before_gate':False,
    }
    REPORT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    lines=['# Validation Report v1.0.0','',f"**Gate:** {result['gate']}",f"**Checks:** {summary['pass']} PASS / {summary['fail']} FAIL",'', 'No confirmatory production outcome existed or was inspected before this gate decision.','', '## Environment','']
    for k,v in env.items(): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Checklist results','']
    for x in rec.items: lines.append(f"- [{ 'x' if x['status']=='PASS' else ' ' }] **{x['section']}** {x['name']}: {x['status']}")
    REPORT_MD.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'gate':result['gate'],'summary':summary,'report':str(REPORT)},indent=2))

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        # Preserve a minimal failure marker without concealing the exception.
        fail={'validation_version':'v1.0.0','gate':'FAIL','error':repr(e)}
        REPORT.write_text(json.dumps(fail,indent=2)+'\n')
        raise
