import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest

ROOT=Path(__file__).resolve().parents[1]
CFG=json.load(open(ROOT/'control/CONFIG_v1.0.0.json'))
df=pd.read_csv(ROOT/'results/BLOCK_FIDELITY_RESULTS.csv')
B=CFG['n_blocks']; BREPS=CFG['bootstrap_reps']; BRNG=np.random.default_rng(CFG['bootstrap_seed'])
LOW=[0,.1,.2,.3,.4,.5,.6]; HIGH=[.9,.925,.95,.975,1.0]; TRANS=[.85,.875,.9]; VHIGH=[.95,.975,1.0]

def vals(endpoint, ps):
    q=df[df.transmission_fidelity.round(6).isin([round(x,6) for x in ps])]
    return q.groupby('block')[endpoint].mean().reindex(range(B)).values

def at(endpoint,p):
    q=df[np.isclose(df.transmission_fidelity,p)]
    return q.set_index('block')[endpoint].reindex(range(B)).values

def boot_ci(x, level):
    x=np.asarray(x,float); n=len(x); means=np.empty(BREPS)
    for i in range(BREPS): means[i]=x[BRNG.integers(0,n,n)].mean()
    a=(1-level)/2
    return float(np.quantile(means,a)),float(np.quantile(means,1-a))

def holm(ps):
    m=len(ps); order=np.argsort(ps); adj=np.empty(m); running=0.0
    for rank,idx in enumerate(order):
        val=(m-rank)*ps[idx]; running=max(running,val); adj[idx]=min(1.0,running)
    return adj

rows=[]; fam_raw={}
for fam,endpoint,prefix in [('R_pop','Delta_R_pop','R'),('V_rel','Delta_V_rel','V')]:
    contrasts=[
        (prefix+'1', vals(endpoint,HIGH)-vals(endpoint,LOW), 'high_minus_low'),
        (prefix+'2', vals(endpoint,VHIGH)-vals(endpoint,TRANS), 'veryhigh_minus_transition'),
        (prefix+'3', at(endpoint,.975), 'p0975_positive')]
    pvals=[]
    temp=[]
    for cid,x,definition in contrasts:
        mean=float(np.mean(x)); lo,hi=boot_ci(x,0.9833333333); pos=int(np.sum(x>0)); p=float(binomtest(pos,B,.5,alternative='greater').pvalue)
        pvals.append(p); temp.append((cid,definition,mean,lo,hi,pos,p))
    adj=holm(pvals)
    for k,t in enumerate(temp):
        cid,definition,mean,lo,hi,pos,p=t
        passed=bool(mean>0 and lo>0 and adj[k]<.05)
        rows.append({'family':fam,'contrast_id':cid,'endpoint':endpoint,'definition':definition,'mean_contrast':mean,'ci_level':0.9833333333,'ci_low':lo,'ci_high':hi,'positive_blocks':pos,'n_blocks':B,'sign_p_one_sided':p,'holm_adjusted_p':float(adj[k]),'pass':passed})

formal=pd.DataFrame(rows); formal.to_csv(ROOT/'results/FORMAL_CONTRAST_RESULTS.csv',index=False)

# curve summary with 95% block bootstrap intervals
srows=[]
for endpoint in ['Delta_R_pop','Delta_V_rel','Delta_fitness','Delta_C_pop']:
    for p,g in df.groupby('transmission_fidelity'):
        x=g.set_index('block')[endpoint].reindex(range(B)).values
        lo,hi=boot_ci(x,.95)
        srows.append({'endpoint':endpoint,'transmission_fidelity':p,'mean':float(np.mean(x)),'sem':float(np.std(x,ddof=1)/math.sqrt(B)),'ci95_low':lo,'ci95_high':hi,'positive_blocks':int(np.sum(x>0))})
summary=pd.DataFrame(srows); summary.to_csv(ROOT/'results/FIDELITY_SUMMARY.csv',index=False)

high_guard={}
for endpoint in ['Delta_R_pop','Delta_V_rel']:
    mm=summary[(summary.endpoint==endpoint)&(summary.transmission_fidelity.round(6).isin([round(x,6) for x in HIGH]))]
    high_guard[endpoint]=bool((mm['mean']>0).all())
all_pass=bool(formal['pass'].all() and all(high_guard.values()))
result={'all_six_primary_pass':bool(formal['pass'].all()),'high_fidelity_positivity_guard':high_guard,'strong_prospective_replication_support':all_pass,'formal_contrasts':formal.to_dict(orient='records')}
with open(ROOT/'results/RESULT_SUMMARY.json','w') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
