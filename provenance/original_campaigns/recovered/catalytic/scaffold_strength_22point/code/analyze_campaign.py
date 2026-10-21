import json, math
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import binomtest
ROOT=Path('/mnt/data/CATALYTIC_COMPLEX_SCAFFOLD_STRENGTH_CONFIRMATORY_v1.0.0')
CFG=json.load(open(ROOT/'control/CONFIG_v1.0.0.json'))
BOOT=CFG['bootstrap_reps']; BRNG=np.random.default_rng(CFG['bootstrap_seed'])
df=pd.read_csv(ROOT/'results/BLOCK_STRENGTH_RESULTS.csv')
strengths=np.array(CFG['scaffold_strengths'])

def pick(block,s,col):
    z=df[(df.block==block)&np.isclose(df.scaffold_strength,s)]
    if len(z)!=1: raise ValueError((block,s,len(z)))
    return float(z.iloc[0][col])

def band(block,vals,col): return np.mean([pick(block,s,col) for s in vals])
L=[0,.25,.5,.75,1.0]; H=[3.0,3.333333,3.5,3.75,4.0]
Mband=[1.0,1.25,1.5,1.666667,2.0,2.25,2.5,2.75,3.0,3.333333,3.5,3.75,4.0]
Pband=[2.75,3.0,3.333333,3.5,3.75,4.0]; Qband=[0,.25,.5,.75,1.0,5.0,6.0,8.0]
blocks=sorted(df.block.unique())
contrasts={
'F1':np.array([pick(b,2,'fitness_ancestor')-pick(b,0,'fitness_ancestor') for b in blocks]),
'F2':np.array([band(b,H,'fitness_ancestor')-band(b,L,'fitness_ancestor') for b in blocks]),
'R1':np.array([pick(b,2,'selected_minus_neutral') for b in blocks]),
'R2':np.array([band(b,Mband,'selected_minus_ancestor') for b in blocks]),
'R3':np.array([band(b,Mband,'selected_minus_neutral') for b in blocks]),
'S1':np.array([band(b,Pband,'selected_minus_ancestor')-band(b,Qband,'selected_minus_ancestor') for b in blocks]),
}
meta={'F1':('founder_cost','negative',.975),'F2':('founder_cost','negative',.975),'R1':('recovery','positive',.98333),'R2':('recovery','positive',.98333),'R3':('recovery','positive',.98333),'S1':('secondary_shape','positive',.95)}

def bootstrap_ci(x,coverage):
    n=len(x); inds=BRNG.integers(0,n,size=(BOOT,n)); means=x[inds].mean(1); alpha=(1-coverage)/2
    return float(np.quantile(means,alpha)),float(np.quantile(means,1-alpha))

def one_sided_sign_p(x,direction):
    if direction=='positive': k=int((x>0).sum())
    else: k=int((x<0).sum())
    return k,float(binomtest(k,len(x),.5,alternative='greater').pvalue)
rows=[]
for cid,x in contrasts.items():
    fam,dirn,cov=meta[cid]; lo,hi=bootstrap_ci(x,cov); k,p=one_sided_sign_p(x,dirn)
    rows.append({'contrast_id':cid,'family':fam,'direction':dirn,'mean':x.mean(),'ci_coverage':cov,'ci_lo':lo,'ci_hi':hi,'direction_count':k,'n':len(x),'sign_p_raw':p})
res=pd.DataFrame(rows)
# Holm within promotion families only
for fam in ['founder_cost','recovery']:
    inds=list(res.index[res.family==fam]); ps=sorted([(res.loc[i,'sign_p_raw'],i) for i in inds])
    m=len(ps); running=0
    adj={}
    for rank,(p,i) in enumerate(ps,1):
        val=(m-rank+1)*p; running=max(running,val); adj[i]=min(1.0,running)
    for i,v in adj.items(): res.loc[i,'sign_p_holm']=v
res.loc[res.family=='secondary_shape','sign_p_holm']=res.loc[res.family=='secondary_shape','sign_p_raw']
# pass criteria
passes=[]
for _,r in res.iterrows():
    if r.contrast_id.startswith('F'):
        ciok=r.ci_hi<0; meanok=r['mean']<0
    else:
        ciok=r.ci_lo>0; meanok=r['mean']>0
    passes.append(bool(meanok and ciok and r.sign_p_holm<.05))
res['pass']=passes
res.to_csv(ROOT/'results/FORMAL_CONTRAST_RESULTS.csv',index=False)
# curve summaries with SEM and 95% block bootstrap intervals
summ=[]
for s,g in df.groupby('scaffold_strength',sort=True):
    row={'scaffold_strength':s,'n_blocks':g.block.nunique()}
    for col in ['fitness_ancestor','selected_minus_ancestor','neutral_minus_ancestor','selected_minus_neutral','Delta_R_pop','Delta_V_rel']:
        x=g[col].to_numpy(float); inds=BRNG.integers(0,len(x),size=(BOOT,len(x))); means=x[inds].mean(1)
        row[col+'_mean']=x.mean(); row[col+'_sem']=x.std(ddof=1)/math.sqrt(len(x)); row[col+'_ci95_lo']=np.quantile(means,.025); row[col+'_ci95_hi']=np.quantile(means,.975)
    summ.append(row)
pd.DataFrame(summ).to_csv(ROOT/'results/STRENGTH_SUMMARY.csv',index=False)
strong=bool(res[res.contrast_id.isin(['F1','F2','R1','R2','R3'])]['pass'].all())
json.dump({'strong_support':strong,'formal_contrasts':res.to_dict(orient='records')},open(ROOT/'results/RESULT_SUMMARY.json','w'),indent=2)
print(res.to_string(index=False)); print('STRONG_SUPPORT',strong)
