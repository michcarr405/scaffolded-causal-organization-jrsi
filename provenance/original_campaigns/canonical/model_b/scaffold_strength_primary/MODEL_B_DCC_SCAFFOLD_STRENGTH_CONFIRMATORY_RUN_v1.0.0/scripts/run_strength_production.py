from __future__ import annotations
import argparse,json,os,sys,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; sys.path.insert(0,str(HERE))
from strength_pipeline import run_ratio_pair

def load_pairs():
    f=pd.read_csv(ROOT/'control'/'RUN_MANIFEST_FROZEN_v1.0.0.csv'); a=pd.read_csv(ROOT/'control'/'RUN_MANIFEST_AUTHORIZED_v1.0.0.csv')
    cols=[c for c in f.columns if c!='production_authorized']
    if len(a)!=420 or a.run_id.nunique()!=420 or not a.production_authorized.astype(bool).all() or not f[cols].equals(a[cols]): raise RuntimeError('authorization audit failed')
    pairs=[]
    for (bid,rid),g in a.groupby(['block_id','ratio_id'],sort=True):
        if len(g)!=2 or set(g['mode'])!={'selected','neutral'}: raise RuntimeError(f'bad pair {bid} {rid}')
        s=g[g['mode']=='selected'].iloc[0]; n=g[g['mode']=='neutral'].iloc[0]
        pairs.append({'block_id':bid,'ratio_id':rid,'beta':float(s.beta),'ratio':float(s.beta_over_theta),'seed':int(s.base_seed_uint32),'selected_run_id':str(s.run_id),'neutral_run_id':str(n.run_id)})
    if len(pairs)!=210: raise RuntimeError('expected 210 ratio pairs')
    return pairs

def completeness(pairs):
    miss=[]
    for p in pairs:
        if not (ROOT/'raw'/'endpoints'/f"{p['block_id']}_{p['ratio_id']}_PAIR.json").exists(): miss.append(f"{p['block_id']}_{p['ratio_id']}_PAIR")
        for rid in (p['selected_run_id'],p['neutral_run_id']):
            for q in (ROOT/'raw'/'states'/f'{rid}_g250.npz',ROOT/'raw'/'metrics'/f'{rid}_metrics.csv',ROOT/'raw'/'endpoints'/f'{rid}_endpoint.json'):
                if not q.exists(): miss.append(str(q.relative_to(ROOT)))
    return sorted(set(miss))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--workers',type=int,default=min(6,os.cpu_count() or 2)); ap.add_argument('--dry-run',action='store_true'); args=ap.parse_args(); pairs=load_pairs()
    if args.dry_run: print(json.dumps({'status':'DRY_RUN_PASS','pairs':len(pairs),'runs':len(pairs)*2,'workers':args.workers},indent=2)); return
    jobs=[p for p in pairs if not (ROOT/'raw'/'endpoints'/f"{p['block_id']}_{p['ratio_id']}_PAIR.json").exists()]
    t0=time.time(); print('PRODUCTION_START',len(jobs),'ratio_pairs',len(jobs)*2,'runs','workers',args.workers,flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs={ex.submit(run_ratio_pair,p['block_id'],p['ratio_id'],p['beta'],p['ratio'],p['seed'],p['selected_run_id'],p['neutral_run_id'],ROOT,'v1.0.0'):p for p in jobs}
        done=0
        for fut in as_completed(futs):
            p=futs[fut]; fut.result(); done+=1
            if done%5==0 or done==len(jobs): print('COMPLETE',done,'/',len(jobs),p['block_id'],p['ratio_id'],flush=True)
    miss=completeness(pairs); report={'status':'PASS' if not miss else 'FAIL','expected_ratio_pairs':210,'expected_runs':420,'pair_endpoint_files':len(list((ROOT/'raw'/'endpoints').glob('STR_B*_R*_PAIR.json'))),'run_endpoint_files':len(list((ROOT/'raw'/'endpoints').glob('STR_B*_R*_*_endpoint.json'))),'state_files':len(list((ROOT/'raw'/'states').glob('*_g250.npz'))),'metrics_files':len(list((ROOT/'raw'/'metrics').glob('*_metrics.csv'))),'missing':miss,'runtime_seconds':time.time()-t0}
    (ROOT/'logs'/'PRODUCTION_COMPLETENESS_v1.0.0.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,indent=2,sort_keys=True),flush=True)
    if miss: raise SystemExit(2)
if __name__=='__main__': main()
