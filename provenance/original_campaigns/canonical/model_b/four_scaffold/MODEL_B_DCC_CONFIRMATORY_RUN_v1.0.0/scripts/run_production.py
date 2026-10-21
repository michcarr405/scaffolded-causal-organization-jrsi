from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from dcc_pipeline import run_pair_block


def load_and_audit_manifests():
    auth_path = ROOT / 'control' / 'RUN_MANIFEST_AUTHORIZED_v1.0.0.csv'
    frozen_path = ROOT / 'control' / 'RUN_MANIFEST_FROZEN_v1.0.0.csv'
    pair_path = ROOT / 'control' / 'PAIRED_BLOCK_MANIFEST_v1.0.0.csv'
    if not auth_path.exists():
        raise RuntimeError('authorized run manifest is missing')
    auth = pd.read_csv(auth_path)
    frozen = pd.read_csv(frozen_path)
    pairs = pd.read_csv(pair_path)
    if len(auth) != 240 or auth.run_id.nunique() != 240:
        raise RuntimeError('authorized run manifest does not contain 240 unique run IDs')
    if not auth.production_authorized.astype(bool).all():
        raise RuntimeError('not all runs are production-authorized')
    scientific_cols = [c for c in frozen.columns if c != 'production_authorized']
    if not frozen[scientific_cols].equals(auth[scientific_cols]):
        raise RuntimeError('authorized manifest changed frozen scientific fields')
    if len(pairs) != 120 or pairs.paired_block_id.nunique() != 120:
        raise RuntimeError('paired manifest does not contain 120 unique blocks')
    # Cross-check each pair against the authorized run rows.
    idx = auth.set_index('run_id')
    for r in pairs.itertuples(index=False):
        for run_id, mode in ((r.selected_run_id, 'selected'), (r.neutral_run_id, 'neutral')):
            rr = idx.loc[run_id]
            if rr['paired_block_id'] != r.paired_block_id or rr['scaffold_id'] != r.scaffold_id or rr['mode'] != mode or int(rr['base_seed_uint32']) != int(r.base_seed_uint32):
                raise RuntimeError(f'pair/run manifest mismatch for {run_id}')
    return auth, pairs


def pair_dict(row):
    return {
        'paired_block_id': str(row.paired_block_id),
        'scaffold_id': str(row.scaffold_id),
        'scaffold_mapping': str(row.scaffold_mapping),
        'base_seed_uint32': int(row.base_seed_uint32),
        'selected_run_id': str(row.selected_run_id),
        'neutral_run_id': str(row.neutral_run_id),
    }


def completeness(pairs):
    missing=[]
    for r in pairs.itertuples(index=False):
        pair_id=str(r.paired_block_id)
        if not (ROOT/'raw'/'endpoints'/f'{pair_id}_PAIR.json').exists():
            missing.append(pair_id)
        for run_id in (str(r.selected_run_id), str(r.neutral_run_id)):
            for path in (
                ROOT/'raw'/'states'/f'{run_id}_g250.npz',
                ROOT/'raw'/'metrics'/f'{run_id}_metrics.csv',
                ROOT/'raw'/'endpoints'/f'{run_id}_endpoint.json',
            ):
                if not path.exists():
                    missing.append(str(path.relative_to(ROOT)))
    return sorted(set(missing))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--workers',type=int,default=min(8, os.cpu_count() or 2))
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    auth,pairs=load_and_audit_manifests()
    if args.dry_run:
        print(json.dumps({'status':'DRY_RUN_PASS','n_runs':len(auth),'n_pairs':len(pairs),'workers':args.workers},indent=2))
        return
    t0=time.time()
    jobs=[]
    for r in pairs.itertuples(index=False):
        pair=pair_dict(r)
        complete=ROOT/'raw'/'endpoints'/f"{pair['paired_block_id']}_PAIR.json"
        if complete.exists():
            print(pair['paired_block_id'],'ALREADY_COMPLETE',flush=True)
            continue
        jobs.append(pair)
    print('PRODUCTION_START', 'pairs_to_run', len(jobs), 'workers', args.workers, flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs={ex.submit(run_pair_block,j,ROOT,'v1.0.0'):j['paired_block_id'] for j in jobs}
        done=0
        for fut in as_completed(futs):
            pair_id=futs[fut]
            fut.result()
            done+=1
            print('COMPLETE',pair_id,f'{done}/{len(jobs)}',flush=True)
    missing=completeness(pairs)
    report={
        'status':'PASS' if not missing else 'FAIL',
        'expected_pairs':120,
        'expected_runs':240,
        'completed_pair_files':len(list((ROOT/'raw'/'endpoints').glob('*_PAIR.json'))),
        'state_files':len(list((ROOT/'raw'/'states').glob('*_g250.npz'))),
        'metrics_files':len(list((ROOT/'raw'/'metrics').glob('*_metrics.csv'))),
        'run_endpoint_files':len([p for p in (ROOT/'raw'/'endpoints').glob('*_endpoint.json')]),
        'missing':missing,
        'runtime_seconds':time.time()-t0,
    }
    (ROOT/'logs'/'PRODUCTION_COMPLETENESS_v1.0.0.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True),flush=True)
    if missing:
        raise SystemExit(2)

if __name__=='__main__':
    main()
