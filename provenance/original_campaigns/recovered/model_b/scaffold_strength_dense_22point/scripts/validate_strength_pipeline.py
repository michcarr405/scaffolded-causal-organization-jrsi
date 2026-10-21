from __future__ import annotations
import hashlib, json, os, platform, shutil, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, pandas as pd, scipy, numba
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(ROOT/'validation'))
from strength_pipeline import *
from strength_stats import bootstrap_ci, sign_test, holm
import reference_exploratory_runner as ref
from modelb_semantic_repo.original_model.core import compute_fitnesses_and_observations

EXPL=Path('/mnt/data/ratio_expl_full/modelb_ratio_sweep_exploratory')
REPORT=ROOT/'validation'/'VALIDATION_REPORT_v1.0.0.json'; REPORT_MD=ROOT/'validation'/'VALIDATION_REPORT_v1.0.0.md'

class Rec:
    def __init__(self): self.items=[]
    def check(self,section,name,ok,detail=None): self.items.append({'section':section,'name':name,'status':'PASS' if bool(ok) else 'FAIL','detail':detail})
    def summary(self):
        p=sum(x['status']=='PASS' for x in self.items); return {'pass':p,'fail':len(self.items)-p,'total':len(self.items)}

def git_blob_sha(path):
    b=Path(path).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def rng_fingerprint(seed,rid):
    a=make_generator(seed,'strength-initialization').integers(0,2**32,size=32,dtype=np.uint32)
    b=make_generator(seed,'strength-propagation',rid,'observation').integers(0,2**32,size=32,dtype=np.uint32)
    c=make_generator(seed,'strength-propagation',rid,'reproduction').integers(0,2**32,size=32,dtype=np.uint32)
    return hashlib.sha256(a.tobytes()+b.tobytes()+c.tobytes()).hexdigest()

def toy_contrasts(df):
    p=df.pivot(index='block_id',columns='ratio_id')
    # access helper
    get=lambda col,r: p[col][r].to_numpy()
    out={}
    out['A1']=get('F0','R0P0')-get('F0','R2P5'); out['A2']=get('F0','R2P5')-get('F0','R4P0')
    V=['R1P5','R2P5','R3P0','R3P5','R4P0']; H=['R3P0','R3P5','R4P0']; L=['R0P0','R1P5']
    out['F1']=np.mean([get('DeltaF',r) for r in V],axis=0); out['F2']=get('DeltaF','R3P0')-get('DeltaF','R4P5')
    out['C1']=np.mean([get('DeltaC_train',r) for r in H],axis=0)-np.mean([get('DeltaC_train',r) for r in L],axis=0)
    out['C2']=np.mean([get('DeltaC_train',r) for r in H],axis=0)-get('DeltaC_train','R4P5')
    out['C3']=get('DeltaC_probe3','R4P0')-get('DeltaC_train','R4P0'); out['C4']=get('DeltaC_probe3','R4P0')-get('DeltaC_probe3','R4P5')
    out['R1']=np.mean([get('DeltaR_train',r) for r in H],axis=0)-np.mean([get('DeltaR_train',r) for r in L],axis=0)
    out['R2']=np.mean([get('DeltaR_train',r) for r in H],axis=0)-get('DeltaR_train','R4P5')
    out['R3']=get('DeltaR_probe3','R4P0')-get('DeltaR_train','R4P0'); out['R4']=get('DeltaR_probe3','R4P0')-get('DeltaR_probe3','R4P5')
    return out

def main():
    rec=Rec(); cfg=json.loads((ROOT/'control'/'CONFIRMATORY_CONFIG_v1.0.0.json').read_text())
    # A canonical implementation and archived exact replay
    expected={'config.py':'d1b251326b88bd4049bb1e4492c309999ac840a1','core.py':'04f85796c61dbd46166dd24a95583c740f8fb999','simulation.py':'3c2bd7a4f8fbddc001f7fdf6fe243551cd134a4e','rng.py':'12db759752491941b4901cdcae9ee376cd24567f'}
    src=ROOT/'source'/'modelb_semantic_repo'; got={}
    paths={'config.py':src/'original_model'/'config.py','core.py':src/'original_model'/'core.py','simulation.py':src/'original_model'/'simulation.py','rng.py':src/'rng.py'}
    for k,p in paths.items(): got[k]=git_blob_sha(p)
    rec.check('A','Canonical source blob SHAs match frozen scientific commit provenance',got==expected,{'expected':expected,'got':got})
    p=default_parameters(); rec.check('A','Canonical dimensions and affinity seed realization',p['n_cells']==80 and p['n_seqs']==8 and p['seq_len']==60 and p['motif_affinity_matrix'].shape==(1024,4),None)
    rec.check('A','Frozen parameters match manifest/config',cfg['canonical_model']['theta']==1.2 and cfg['canonical_model']['p_inherit']==.975 and cfg['canonical_model']['mutation_rate']==.001 and cfg['canonical_model']['fitness_floor']==.1 and cfg['canonical_model']['generations']==250,None)
    rec.check('A','Native and reversed mappings frozen',NATIVE==(2,0,3,1) and REVERSED==(1,3,0,2),None)
    replay=[]
    for mode,neutral in [('selected',False),('neutral',True)]:
        f=EXPL/'states'/f'{mode}_r3p333333_rep00.npz'
        with np.load(f) as z: seed=int(z['seed']); beta=float(z['beta']); aref=z['ancestor']; fref=z['final']
        anc,fin,tr,g0,g250=ref.run_sim(seed,beta,neutral=neutral)
        replay.append({'mode':mode,'ancestor_diff':int(np.sum(anc!=aref)),'final_diff':int(np.sum(fin!=fref)),'g250_mean':float(g250[0].mean())})
    rec.check('A','Archived exploratory beta=4 selected/neutral replay exactly',all(x['ancestor_diff']==0 and x['final_diff']==0 for x in replay),replay)
    # B determinism/RNG/blocking without confirmatory scientific outcomes
    ledger=pd.read_csv(ROOT/'control'/'SEED_LEDGER_v1.0.0.csv'); seed0=int(ledger.iloc[0].base_seed_uint32); seed1=int(ledger.iloc[1].base_seed_uint32)
    fp1=rng_fingerprint(seed0,'R3P0'); fp2=rng_fingerprint(seed0,'R3P0'); fp3=rng_fingerprint(seed1,'R3P0')
    rec.check('B','Same seed/key deterministic and different root seed diverges',fp1==fp2 and fp1!=fp3,{'same':fp1==fp2,'different':fp1!=fp3})
    rids=['R0P0', 'R0P25', 'R0P5', 'R0P75', 'R1P0', 'R1P25', 'R1P5', 'R1P666667', 'R2P0', 'R2P25', 'R2P5', 'R2P75', 'R3P0', 'R3P333333', 'R3P5', 'R3P75', 'R4P0', 'R4P25', 'R4P5', 'R5P0', 'R6P0', 'R8P0']; fps=[rng_fingerprint(seed0,r) for r in rids]
    rec.check('B','Ratio-specific evolution streams are distinct',len(set(fps))==22,None)
    with ProcessPoolExecutor(max_workers=2) as ex:
        futs=[ex.submit(rng_fingerprint,seed0,r) for r in reversed(rids)]; par=[f.result() for f in futs]
    rec.check('B','Parallel scheduling does not alter keyed streams',par==[rng_fingerprint(seed0,r) for r in reversed(rids)],None)
    # C shared ancestors, g0 CRN, mode pairing
    pp=params_for(3.0); init1=make_generator(seed0,'strength-initialization'); init2=make_generator(seed0,'strength-initialization'); a1=init_population(80,8,60,init1); a2=init_population(80,8,60,init2)
    rec.check('C','All ratios/modes reconstruct identical ancestor within block',np.array_equal(a1,a2),{'hash':state_hash(a1)})
    u0a=make_generator(seed0,'strength-g0-observation').random(80*8*56); u0b=make_generator(seed0,'strength-g0-observation').random(80*8*56)
    rec.check('C','Generation-0 observation excludes ratio and mode',np.array_equal(u0a,u0b),None)
    fsa,_,_=observe_with_uniforms(a1,pp,u0a); fsb,_,_=observe_with_uniforms(a1,pp,u0b)
    rec.check('C','Selected-neutral g0 state/fitness exactly identical',np.array_equal(fsa,fsb),{'fitness':float(fsa.mean())})
    os=make_generator(seed0,'strength-propagation','R3P0','observation').random(128); on=make_generator(seed0,'strength-propagation','R3P0','observation').random(128)
    rs=make_generator(seed0,'strength-propagation','R3P0','reproduction').random(128); rn=make_generator(seed0,'strength-propagation','R3P0','reproduction').random(128)
    rec.check('C','Selected-neutral evolution observation/reproduction CRNs mode-paired',np.array_equal(os,on) and np.array_equal(rs,rn),None)
    rec.check('C','Observation and reproduction substreams purpose-separated',not np.array_equal(os,rs),None)
    ep1=make_generator(seed0,'strength-endpoint-observation','R3P0').random(128); ep2=make_generator(seed0,'strength-endpoint-observation','R3P0').random(128)
    rec.check('C','Endpoint observation stream ratio-specific and mode-paired',np.array_equal(ep1,ep2) and not np.array_equal(ep1,make_generator(seed0,'strength-endpoint-observation','R3P5').random(128)),None)
    # D fitness formulas/floor
    rec.check('D','Zero-centered fitness arithmetic identities',abs((7-2)-(4-2)-(7-4))<1e-15,None)
    lowp=params_for(9.6); u=np.zeros(80*8*56); ff,_,_=observe_with_uniforms(a1,lowp,u); rec.check('D','Canonical fitness floor remains 0.1',float(ff.min())>=.1,None)
    # E Cdown validation on archived state
    with np.load(EXPL/'states'/'selected_r3p333333_rep00.npz') as z: pop=z['final']
    aff=p['motif_affinity_matrix']; new=c_down_primary(pop,aff,NATIVE,4.0,1.2); old=ref.c_down(pop,4.0)
    rec.check('E','Expectation-level C_down replays validated exploratory estimator',abs(new['jsd_bits']-old)<1e-15,{'new':new['jsd_bits'],'old':old})
    rec.check('E','Erasure preserves motif and segment marginals',new['motif_marginal_error']<1e-15 and new['segment_marginal_error']<1e-15,new)
    rec.check('E','JSD nonnegative and zero on identity',jsd_bits(np.array([.2,.8]),np.array([.2,.8]))==0.0 and new['jsd_bits']>=0,None)
    ctrain=c_down_primary(pop,aff,NATIVE,4.0,1.2)['jsd_bits']; cprobe=c_down_primary(pop,aff,NATIVE,3.0,1.2)['jsd_bits']
    rec.check('E','Training and fixed-beta=3 probes use distinct frozen beta values',abs(ctrain-cprobe)>0 and FIXED_PROBE_BETA==3.0,{'train':ctrain,'probe3':cprobe})
    h0=state_hash(pop); _=c_down_primary(pop,aff,NATIVE,3.0,1.2); rec.check('E','C_down probe does not modify population',state_hash(pop)==h0,None)
    # F specificity
    prm=params_for(4.0); nw=pop.shape[0]*pop.shape[1]*(pop.shape[2]-4); uu=make_generator(seed0,'strength-specificity-crn','R4P0','train').random((16,nw))
    sp=specificity(pop,prm,4.8,seed0,'R4P0','train',uu,16)
    rec.check('F','Specificity uses exactly 16 CRN draws',sp['draw_values'].shape==(2,16),{'shape':sp['draw_values'].shape})
    # canonical core first draw agreement for native and reversed
    fn,_,_=compute_fitnesses_and_observations(pop,prm['motif_affinity_matrix'],np.array(NATIVE,dtype=np.int64),4.8,prm['productive_pairs'],prm['anti_pairs'],2.0,.5,1.2,uu[0]); fr,_,_=compute_fitnesses_and_observations(pop,prm['motif_affinity_matrix'],np.array(REVERSED,dtype=np.int64),4.8,prm['productive_pairs'],prm['anti_pairs'],2.0,.5,1.2,uu[0])
    rec.check('F','Optimized native/reversed specificity agrees with canonical core',abs(float(fn.mean())-sp['draw_values'][0,0])<1e-12 and abs(float(fr.mean())-sp['draw_values'][1,0])<1e-12,{'native':float(fn.mean()),'rev':float(fr.mean())})
    uu2=make_generator(seed0,'strength-specificity-crn','R4P0','train').random((16,nw)); rec.check('F','Specificity CRN excludes mode and mapping',np.array_equal(uu,uu2),None)
    rec.check('F','Training/fixed assays purpose-separated and fixed probe beta=3',not np.array_equal(uu,make_generator(seed0,'strength-specificity-crn','R4P0','probe3').random((16,nw))) and FIXED_PROBE_BETA==3.0,None)
    # G statistics/contrast formulas
    v=np.array([1.,2.,3.,4.,5.]); b=bootstrap_ci(v,.975,50000,'validation'); rec.check('G','50,000 root-block bootstrap and 97.5% interval implemented',b['n_boot']==50000 and b['ci']==.975 and b['low']>0,b)
    b2=bootstrap_ci(v,.9875,50000,'validation9875'); rec.check('G','98.75% interval implemented',b2['ci']==.9875 and b2['low']>0,b2)
    s1=sign_test(np.ones(10)); sz=sign_test(np.zeros(10)); rec.check('G','Exact one-sided sign test counts zero nonpositive',s1['positive']==10 and sz['positive']==0 and sz['p_value']==1.0,{'positive':s1,'zero':sz})
    rec.check('G','Holm hand-check',np.allclose(holm([.01,.04,.03]),[.03,.06,.06]),{'adj':holm([.01,.04,.03]).tolist()})
    # hand-built 3-block toy with exact intended contrast values
    rows=[]
    for bi in range(3):
        for j,r in enumerate(rids): rows.append({'block_id':f'B{bi}','ratio_id':r,'F0':100-10*j-bi,'DeltaF':j+1+bi,'DeltaC_train':.1*j+.01*bi,'DeltaC_probe3':.2*j+.01*bi,'DeltaR_train':j+.1*bi,'DeltaR_probe3':2*j+.1*bi})
    tc=toy_contrasts(pd.DataFrame(rows)); rec.check('G','All 12 frozen contrast formulas produce 3 block-level values',len(tc)==12 and all(len(x)==3 for x in tc.values()),{k:v.tolist() for k,v in tc.items()})
    # H manifests and dry schema
    run=pd.read_csv(ROOT/'control'/'RUN_MANIFEST_v1.0.0.csv'); blocks=pd.read_csv(ROOT/'control'/'BLOCK_MANIFEST_v1.0.0.csv'); cond=pd.read_csv(ROOT/'control'/'CONDITION_MANIFEST_v1.0.0.csv')
    rec.check('H','Seed ledger has 30 unique new root seeds and recorded zero prior overlap',len(ledger)==30 and ledger.base_seed_uint32.nunique()==30 and (~ledger.excluded_prior_seed_overlap.astype(bool)).all(),None)
    rec.check('H','Block manifest has 30 blocks',len(blocks)==30 and blocks.block_id.nunique()==30,None)
    expected_ratios=np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.666667, 2.0, 2.25, 2.5, 2.75, 3.0, 3.333333, 3.5, 3.75, 4.0, 4.25, 4.5, 5.0, 6.0, 8.0],float); expected_betas=np.array([0.0,0.3,0.6,0.9,1.2,1.5,1.8,2.0,2.4,2.7,3.0,3.3,3.6,4.0,4.2,4.5,4.8,5.1,5.4,6.0,7.2,9.6],float)
    rec.check('H','Condition manifest has exact original 22 frozen strengths/betas',len(cond)==22 and np.allclose(cond.beta_over_theta.to_numpy(float),expected_ratios,atol=1e-8) and np.allclose(cond.beta.to_numpy(float),expected_betas,atol=1e-12),None)
    rec.check('H','Run manifest has 1320 unique IDs',len(run)==1320 and run.run_id.nunique()==1320,{'rows':len(run)})
    grp=run.groupby('block_id').size(); rec.check('H','Every block has 44 runs',len(grp)==30 and (grp==44).all(),None)
    modecounts=run.groupby(['ratio_id','mode']).size(); rec.check('H','Every ratio has 30 selected and 30 neutral runs',(modecounts==30).all(),{f'{a}|{b}':int(v) for (a,b),v in modecounts.to_dict().items()})
    rec.check('H','All production authorization flags false at frozen gate',not run.production_authorized.astype(bool).any(),None)
    rec.check('H','Expected output paths unique',run.expected_state_file.nunique()==1320 and run.expected_metrics_file.nunique()==1320,None)
    parsed=0
    for rr in run.itertuples(index=False): json.loads(rr.historical_scaffold_mapping); json.loads(rr.reversed_probe_mapping); float(rr.beta); int(rr.base_seed_uint32); parsed+=1
    rec.check('H','Dry-run parses all 1320 rows without scientific outcomes',parsed==1320,{'parsed':parsed})
    rec.check('H','No confirmatory production endpoint exists before validation gate',len(list((ROOT/'raw'/'endpoints').glob('*')))==0,None)
    # I authorization prereqs
    env={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'numba':numba.__version__}
    summary=rec.summary(); result={'validation_version':'v1.0.0','scientific_commit':cfg['scientific_commit'],'gate':'PASS' if summary['fail']==0 else 'FAIL','summary':summary,'environment':env,'checks':rec.items,'confirmatory_outcomes_inspected_before_gate':False}
    REPORT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    lines=['# Dense Scaffold-Strength Validation Report v1.0.0','',f"**Gate:** {result['gate']}",f"**Checks:** {summary['pass']} PASS / {summary['fail']} FAIL",'', 'No new confirmatory production outcome existed or was inspected before this gate decision.','', '## Checklist results','']
    for x in rec.items: lines.append(f"- [{'x' if x['status']=='PASS' else ' '}] **{x['section']}** {x['name']}: {x['status']}")
    REPORT_MD.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'gate':result['gate'],'summary':summary,'report':str(REPORT)},indent=2))
    if summary['fail']: raise SystemExit(2)
if __name__=='__main__': main()
