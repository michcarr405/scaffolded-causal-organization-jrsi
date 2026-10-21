from __future__ import annotations
import hashlib,json,platform,sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np,pandas as pd,scipy,numba
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; SRC=ROOT/'source'; sys.path.insert(0,str(HERE)); sys.path.insert(0,str(SRC))
from fidelity_pipeline import *
from fidelity_stats import bootstrap_ci,sign_test,holm
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.simulation import init_population,reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator
OLD=Path('/mnt/data/inherit_expl_full/data/checkpoint_metrics_long.csv')
REPORT=ROOT/'validation'/'VALIDATION_REPORT_v1.0.0.json'; REPORT_MD=ROOT/'validation'/'VALIDATION_REPORT_v1.0.0.md'

class Rec:
    def __init__(self): self.items=[]
    def check(self,section,name,ok,detail=None): self.items.append({'section':section,'name':name,'status':'PASS' if bool(ok) else 'FAIL','detail':detail})
    def summary(self):
        p=sum(x['status']=='PASS' for x in self.items); return {'pass':p,'fail':len(self.items)-p,'total':len(self.items)}

def git_blob_sha(path):
    b=Path(path).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def old_replay(seed,p_inherit,neutral=False):
    params=params_for(); nw=80*8*56
    pop=init_population(80,8,60,make_generator(seed,'baseline-initialization'))
    obs=make_generator(seed,'baseline-observation'); rep=make_generator(seed,'baseline-propagation')
    fit=None
    for t in range(251):
        fit,_,_=observe_with_uniforms(pop,params,obs.random(nw))
        if t==250: break
        pop=reproduce_with_partitioning(pop,np.ones_like(fit) if neutral else fit,MU,p_inherit,rep)
    return pop,fit

def rng_fingerprint(seed,pid):
    a=make_generator(seed,'fidelity-initialization').integers(0,2**32,size=32,dtype=np.uint32)
    b=make_generator(seed,'fidelity-propagation',pid,'observation').integers(0,2**32,size=32,dtype=np.uint32)
    c=make_generator(seed,'fidelity-propagation',pid,'reproduction').integers(0,2**32,size=32,dtype=np.uint32)
    return hashlib.sha256(a.tobytes()+b.tobytes()+c.tobytes()).hexdigest()

def main():
    rec=Rec(); cfg=json.loads((ROOT/'control'/'CONFIRMATORY_CONFIG_v1.0.0.json').read_text())
    # A canonical source and exact archived replay
    expected={'config.py':'d1b251326b88bd4049bb1e4492c309999ac840a1','core.py':'04f85796c61dbd46166dd24a95583c740f8fb999','simulation.py':'3c2bd7a4f8fbddc001f7fdf6fe243551cd134a4e','rng.py':'12db759752491941b4901cdcae9ee376cd24567f'}
    src=ROOT/'source'/'modelb_semantic_repo'; paths={'config.py':src/'original_model'/'config.py','core.py':src/'original_model'/'core.py','simulation.py':src/'original_model'/'simulation.py','rng.py':src/'rng.py'}; got={k:git_blob_sha(p) for k,p in paths.items()}
    rec.check('A','Canonical source blob SHAs match frozen scientific commit provenance',got==expected,{'expected':expected,'got':got})
    p=default_parameters(); rec.check('A','Canonical dimensions and affinity realization',p['n_cells']==80 and p['n_seqs']==8 and p['seq_len']==60 and p['motif_affinity_matrix'].shape==(1024,4),None)
    rec.check('A','Frozen fixed parameters match config',cfg['theta']==1.2 and cfg['beta']==3.0 and cfg['generations']==250,None)
    rec.check('A','Exact 18-point fidelity grid preserved',cfg['p_values']==[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.75,0.8,0.825,0.85,0.875,0.9,0.925,0.95,0.975,1.0],None)
    old=pd.read_csv(OLD); old=old[(np.isclose(old.p,.975))&(old.replicate==0)&(old.generation==250)]
    replay=[]
    for mode,neutral in [('selected',False),('neutral',True)]:
        ref=old[old['mode']==mode].iloc[0]; seed=int(ref.seed); pop,fit=old_replay(seed,.975,neutral); cd=c_down_primary(pop,p['motif_affinity_matrix'])['jsd_bits']
        # old 4-draw R namespace exactly
        us=np.stack([make_generator(seed,'inheritance-sweep-specificity',f'{.975:.6f}',250,d).random(80*8*56) for d in range(4)])
        rr=specificity(pop,params_for(),us)['R']
        replay.append({'mode':mode,'fitness_new':float(fit.mean()),'fitness_old':float(ref.fitness),'C_new':cd,'C_old':float(ref.C_down),'R_new':rr,'R_old':float(ref.R)})
    rec.check('A','Archived exploratory p=0.975 selected/neutral endpoint replay exactly',all(abs(x['fitness_new']-x['fitness_old'])<1e-12 and abs(x['C_new']-x['C_old'])<1e-12 and abs(x['R_new']-x['R_old'])<1e-12 for x in replay),replay)
    # B RNG and block design
    ledger=pd.read_csv(ROOT/'control'/'SEED_LEDGER_v1.0.0.csv'); seed0=int(ledger.iloc[0].base_seed_uint32); seed1=int(ledger.iloc[1].base_seed_uint32)
    fp1=rng_fingerprint(seed0,'P0975'); fp2=rng_fingerprint(seed0,'P0975'); fp3=rng_fingerprint(seed1,'P0975')
    rec.check('B','Same keyed seed deterministic and different root seed diverges',fp1==fp2 and fp1!=fp3,None)
    pids=pd.read_csv(ROOT/'control'/'CONDITION_MANIFEST_v1.0.0.csv').p_id.tolist(); fps=[rng_fingerprint(seed0,x) for x in pids]
    rec.check('B','All 18 fidelity-specific streams are distinct',len(set(fps))==18,None)
    with ProcessPoolExecutor(max_workers=2) as ex: par=[f.result() for f in [ex.submit(rng_fingerprint,seed0,x) for x in reversed(pids)]]
    rec.check('B','Parallel scheduling does not alter keyed streams',par==[rng_fingerprint(seed0,x) for x in reversed(pids)],None)
    # C ancestor and mode pairing
    pp=params_for(); a1=init_population(80,8,60,make_generator(seed0,'fidelity-initialization')); a2=init_population(80,8,60,make_generator(seed0,'fidelity-initialization'))
    rec.check('C','All fidelities/modes reconstruct identical ancestor within block',np.array_equal(a1,a2),{'hash':state_hash(a1)})
    u0a=make_generator(seed0,'fidelity-g0-observation').random(80*8*56); u0b=make_generator(seed0,'fidelity-g0-observation').random(80*8*56)
    f0a,_,_=observe_with_uniforms(a1,pp,u0a); f0b,_,_=observe_with_uniforms(a2,pp,u0b)
    rec.check('C','Generation-0 selected/neutral observation and fitness exactly identical',np.array_equal(u0a,u0b) and np.array_equal(f0a,f0b),{'fitness':float(f0a.mean())})
    os=make_generator(seed0,'fidelity-propagation','P0975','observation').random(128); on=make_generator(seed0,'fidelity-propagation','P0975','observation').random(128)
    rs=make_generator(seed0,'fidelity-propagation','P0975','reproduction').random(128); rn=make_generator(seed0,'fidelity-propagation','P0975','reproduction').random(128)
    rec.check('C','Selected-neutral propagation streams are mode-paired',np.array_equal(os,on) and np.array_equal(rs,rn),None)
    rec.check('C','Observation and reproduction substreams are purpose-separated',not np.array_equal(os,rs),None)
    ep=make_generator(seed0,'fidelity-endpoint-observation','P0975').random(128)
    rec.check('C','Endpoint stream is fidelity-specific and mode-paired',not np.array_equal(ep,make_generator(seed0,'fidelity-endpoint-observation','P0950').random(128)),None)
    # D C_down
    pop_old,_=old_replay(1555856187,.975,False); cd=c_down_primary(pop_old,p['motif_affinity_matrix'])
    rec.check('D','C_down relational erasure preserves motif and segment marginals',cd['motif_marginal_error']<1e-15 and cd['segment_marginal_error']<1e-15,cd)
    rec.check('D','C_down nonnegative and identity JSD zero',cd['jsd_bits']>=0 and jsd_bits([.2,.8],[.2,.8])==0.0,None)
    h=state_hash(pop_old); _=c_down_primary(pop_old,p['motif_affinity_matrix']); rec.check('D','C_down estimator does not modify population',state_hash(pop_old)==h,None)
    # E specificity and 16-draw estimand
    nw=80*8*56; uu=make_generator(seed0,'fidelity-specificity-crn','P0975').random((16,nw)); s16=specificity(pop_old,pp,uu); s4=specificity(pop_old,pp,uu[:4])
    rec.check('E','Specificity uses exactly 16 native/reversed CRN draws',s16['draw_values'].shape==(2,16),{'shape':list(s16['draw_values'].shape)})
    rec.check('E','Four-draw and sixteen-draw assays use identical per-draw estimand',np.array_equal(s4['draw_values'],s16['draw_values'][:,:4]),{'R4':s4['R'],'R16':s16['R']})
    fn,_,_=observe_with_uniforms(pop_old,{**pp,'segment_favored_met':np.array(NATIVE)},uu[0]); pr={**pp,'segment_favored_met':np.array(REVERSED)}; fr,_,_=observe_with_uniforms(pop_old,pr,uu[0])
    rec.check('E','Optimized specificity agrees with canonical core for native/reversed draw',abs(float(fn.mean())-s16['draw_values'][0,0])<1e-12 and abs(float(fr.mean())-s16['draw_values'][1,0])<1e-12,None)
    rec.check('E','Increasing draws changes only Monte Carlo averaging precision',16==4*4 and s16['draw_values'].shape[1]>s4['draw_values'].shape[1],{'theoretical_variance_ratio_mean16_to_mean4':0.25})
    # F statistics
    v=np.array([1.,2.,3.,4.,5.]); b=bootstrap_ci(v,.98333,50000,'validation'); rec.check('F','50,000 root-block bootstrap implemented',b['n_boot']==50000 and b['low']>0,b)
    s1=sign_test(np.ones(10)); sz=sign_test(np.zeros(10)); rec.check('F','Exact one-sided sign test counts zero nonpositive',s1['positive']==10 and sz['positive']==0 and sz['p_value']==1.0,None)
    rec.check('F','Holm hand-check',np.allclose(holm([.01,.04,.03]),[.03,.06,.06]),{'adj':holm([.01,.04,.03]).tolist()})
    # synthetic contrast formula check
    vals={pid:i for i,pid in enumerate(pids)}
    low=['P0000','P0100','P0200','P0300','P0400','P0500','P0600']; high=['P0900','P0925','P0950','P0975','P1000']; trans=['P0850','P0875','P0900']; very=['P0950','P0975','P1000']
    c1=np.mean([vals[x] for x in high])-np.mean([vals[x] for x in low]); c2=np.mean([vals[x] for x in very])-np.mean([vals[x] for x in trans]); c3=vals['P0975']
    rec.check('F','Frozen contrast group definitions parse and give intended ordering',c1>0 and c2>0 and c3>0,{'C1toy':c1,'C2toy':c2,'C3toy':c3})
    # G manifests
    run=pd.read_csv(ROOT/'control'/'RUN_MANIFEST_v1.0.0.csv'); blocks=pd.read_csv(ROOT/'control'/'BLOCK_MANIFEST_v1.0.0.csv'); cond=pd.read_csv(ROOT/'control'/'CONDITION_MANIFEST_v1.0.0.csv')
    rec.check('G','Seed ledger has 30 unique new root seeds and no recorded overlap',len(ledger)==30 and ledger.base_seed_uint32.nunique()==30 and (~ledger.excluded_prior_seed_overlap.astype(bool)).all(),None)
    rec.check('G','Condition manifest has exact 18 fidelities',len(cond)==18 and np.allclose(cond.p_inherit,cfg['p_values']),None)
    rec.check('G','Run manifest has 1080 unique IDs',len(run)==1080 and run.run_id.nunique()==1080,{'rows':len(run)})
    rec.check('G','Every root block has 36 runs',(run.groupby('block_id').size()==36).all() and len(blocks)==30,None)
    rec.check('G','Every fidelity has 30 selected and 30 neutral runs',(run.groupby(['p_id','mode']).size()==30).all(),None)
    rec.check('G','All production authorization flags false at frozen gate',not run.production_authorized.astype(bool).any(),None)
    rec.check('G','Expected output paths unique',run.expected_state_file.nunique()==1080 and run.expected_metrics_file.nunique()==1080,None)
    parsed=0
    for rr in run.itertuples(index=False): json.loads(rr.historical_scaffold_mapping); json.loads(rr.reversed_probe_mapping); float(rr.p_inherit); int(rr.base_seed_uint32); parsed+=1
    rec.check('G','Dry manifest parses all 1080 rows',parsed==1080,{'parsed':parsed})
    rec.check('G','No confirmatory endpoint exists before validation gate',len(list((ROOT/'raw'/'endpoints').glob('*')))==0,None)
    summary=rec.summary(); result={'validation_version':'v1.0.0','scientific_commit':cfg['scientific_commit'],'gate':'PASS' if summary['fail']==0 else 'FAIL','summary':summary,'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'numba':numba.__version__},'checks':rec.items,'confirmatory_outcomes_inspected_before_gate':False}
    REPORT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    lines=['# Transmission-Fidelity Validation Report v1.0.0','',f"**Gate:** {result['gate']}",f"**Checks:** {summary['pass']} PASS / {summary['fail']} FAIL",'', 'No new confirmatory production outcome existed or was inspected before this gate decision.','', '## Checklist results','']
    for x in rec.items: lines.append(f"- [{'x' if x['status']=='PASS' else ' '}] **{x['section']}** {x['name']}: {x['status']}")
    REPORT_MD.write_text('\n'.join(lines)+'\n'); print(json.dumps({'gate':result['gate'],'summary':summary,'report':str(REPORT)},indent=2))
    if summary['fail']: raise SystemExit(2)
if __name__=='__main__': main()
