from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
ROOT=Path(__file__).resolve().parent.parent
CFG=json.loads((ROOT/'control'/'CONFIRMATORY_CONFIG_v1.0.0.json').read_text())
ANALYSIS_ROOT_SEED=int(CFG['inference']['bootstrap_seed_uint32'])

def _rng(*keys):
    payload='\x1f'.join(str(k) for k in keys).encode(); d=hashlib.sha256(payload).digest(); ent=[ANALYSIS_ROOT_SEED]+[int.from_bytes(d[i:i+4],'little') for i in range(0,32,4)]; return np.random.default_rng(np.random.SeedSequence(ent))

def bootstrap_ci(v,ci,n_boot=50000,key='default'):
    v=np.asarray(v,float).reshape(-1); rng=_rng('root-block-bootstrap',key,len(v),n_boot,ci); idx=rng.integers(0,len(v),size=(n_boot,len(v))); b=v[idx].mean(axis=1); a=(1-ci)/2; lo,hi=np.quantile(b,[a,1-a]); return {'n':len(v),'mean':float(v.mean()),'median':float(np.median(v)),'ci':ci,'low':float(lo),'high':float(hi),'n_boot':n_boot}

def sign_test(v):
    v=np.asarray(v,float).reshape(-1); k=int(np.sum(v>0)); n=len(v); return {'n':n,'positive':k,'nonpositive':n-k,'p_value':float(binomtest(k,n,p=.5,alternative='greater').pvalue)}

def holm(ps):
    p=np.asarray(ps,float); order=np.argsort(p); out=np.empty_like(p); running=0.; m=len(p)
    for rank,idx in enumerate(order): running=max(running,(m-rank)*p[idx]); out[idx]=min(1.,running)
    return out
