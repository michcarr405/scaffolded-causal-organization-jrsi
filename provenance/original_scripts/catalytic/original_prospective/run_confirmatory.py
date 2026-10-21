import numpy as np, pandas as pd, json, math
from itertools import combinations_with_replacement
from pathlib import Path
from scipy.stats import binomtest, friedmanchisquare
OUT=Path('/mnt/data/reaction_net_confirmatory')
M=4; R=4; PAIRS=list(combinations_with_replacement(range(M),2)); D=len(PAIRS)
N=32; POP=48; GENS=180; MU=.01; SEL=24.; K=1.; P=.975; S=2.0; ASEED=51073; ROOT0=2000000
UNIF=np.ones(D)/D
# matrix
rng=np.random.default_rng(ASEED); A=np.exp(.9*rng.normal(size=(D,R)))
for _ in range(2000): A*=(R/A.sum(1))[:,None]; A*=(D/A.sum(0))[None,:]
# scaffold basis
basis=[]
for raw in [np.array([1.,-1,0,0]),np.array([1.,1.,-2,0]),np.array([1.,1.,1.,-3])]:
 v=raw.copy()
 for u in basis:v-=u*np.dot(u,v)
 v/=np.linalg.norm(v);basis.append(v)
e1,e2,e3=basis; hist=e1
# mutation
pi={p:i for i,p in enumerate(PAIRS)}; MUT=np.zeros((D,D))
for d,(i,j) in enumerate(PAIRS):
 MUT[d,d]=1-MU;ev=[]
 for pos in (0,1):
  old=[i,j]
  for new in range(M):
   if new==old[pos]:continue
   q=old.copy();q[pos]=new;ev.append(pi[tuple(sorted(q))])
 for z in ev:MUT[d,z]+=MU/len(ev)

def erase(f):
 mono=np.zeros(M)
 for n,(i,j) in zip(f,PAIRS):
  if i==j:mono[i]+=2*n
  else:mono[i]+=n;mono[j]+=n
 p=mono/mono.sum();fe=np.zeros(D)
 for k,(i,j) in enumerate(PAIRS):fe[k]=p[i]*p[j] if i==j else 2*p[i]*p[j]
 return fe/fe.sum()
def jsd(p,q):
 p=p/p.sum();q=q/q.sum();m=.5*(p+q)
 def kl(a,b):
  z=a>0;return np.sum(a[z]*np.log2(a[z]/b[z]))
 return .5*kl(p,m)+.5*kl(q,m)
def chem(f,b,s):
 cat=f@A;u=np.exp(s*np.asarray(b))*cat;v=u/(K+u);q=v/v.sum();fit=R/np.sum(1/np.clip(v,1e-12,None));return q,fit
def fitcells(st,b,s):
 f=st/st.sum(1,keepdims=True);cat=f@A;u=np.exp(s*np.asarray(b))[None,:]*cat;v=u/(K+u);return R/np.sum(1/np.clip(v,1e-12,None),axis=1)
def metrics(st,b,s):
 f=st.sum(0)/st.sum();fe=erase(f);qi,fi=chem(f,b,s);qe,fer=chem(fe,b,s);return {'fitness':fitcells(st,b,s).mean(),'R_pop':jsd(f,fe),'C_pop':jsd(qi,qe),'V_rel':fi-fer}
def founder(seed):
 r=np.random.default_rng(seed);return np.stack([r.multinomial(N,UNIF) for _ in range(POP)])
def evolve(st,selected,seed):
 r=np.random.default_rng(seed);st=st.copy()
 for g in range(GENS):
  ft=fitcells(st,hist,S)
  if selected:
   z=SEL*(ft-ft.mean());z-=z.max();w=np.exp(z);w/=w.sum();pars=r.choice(POP,POP,p=w)
  else:pars=r.integers(0,POP,POP)
  new=np.empty_like(st)
  for o,pa in enumerate(pars):
   pr=(P*(st[pa]/N)+(1-P)*UNIF)@MUT;pr/=pr.sum();new[o]=r.multinomial(N,pr)
  st=new
 return st
# probes
theta=np.deg2rad(60); probes=[]
for k,phi in enumerate(np.deg2rad(np.arange(0,360,45))):
 perp=np.cos(phi)*e2+np.sin(phi)*e3;v=np.cos(theta)*e1+np.sin(theta)*perp;v/=np.linalg.norm(v);probes.append((k,float(np.rad2deg(phi)),v))
rows=[];dirs=[];states=[]
for b in range(30):
 f=founder(ROOT0+b); m0=metrics(f,hist,0); mb=metrics(f,hist,S)
 sel=evolve(f,True,ROOT0+10000+b);neu=evolve(f,False,ROOT0+20000+b);states.append((sel,neu))
 ms=metrics(sel,hist,S);mn=metrics(neu,hist,S)
 ms05=metrics(sel,hist,.5);mn05=metrics(neu,hist,.5)
 rec={'block':b,'founder_cost':mb['fitness']-m0['fitness']}
 for k in ['fitness','R_pop','C_pop','V_rel']:
  rec[k+'_selected']=ms[k];rec[k+'_neutral']=mn[k];rec['Delta_'+k]=ms[k]-mn[k]
 rec['DeltaC_probe05']=ms05['C_pop']-mn05['C_pop'];rec['masking_contrast']=rec['DeltaC_probe05']-rec['Delta_C_pop'];rows.append(rec)
 for k,phi,v in probes:
  fs_h=fitcells(sel,hist,S).mean(); fs_p=fitcells(sel,v,S).mean(); fn_h=fitcells(neu,hist,S).mean(); fn_p=fitcells(neu,v,S).mean();
  dirs.append({'block':b,'direction':k,'phi_deg':phi,'distance2':float(np.sum((v-hist)**2)),'DeltaH':(fs_h-fs_p)-(fn_h-fn_p)})
df=pd.DataFrame(rows);dd=pd.DataFrame(dirs);df.to_csv(OUT/'CONFIRM_BLOCK_RESULTS.csv',index=False);dd.to_csv(OUT/'CONFIRM_DIRECTION_RESULTS.csv',index=False)
dm=dd.groupby(['direction','phi_deg','distance2'],as_index=False).DeltaH.agg(['mean','sem']).reset_index();dm.to_csv(OUT/'CONFIRM_DIRECTION_SUMMARY.csv',index=False)
# stats
stats={}
# primary
stats['P1']={'negative':int((df.founder_cost<0).sum()),'n':30,'mean_cost':float(df.founder_cost.mean()),'pass':bool((df.founder_cost<0).all())}
for label,col,thr in [('P2','Delta_fitness',27),('P3','Delta_V_rel',24),('P4','Delta_R_pop',24),('P5','masking_contrast',24)]:
 pos=int((df[col]>0).sum()); stats[label]={'positive':pos,'n':30,'mean':float(df[col].mean()),'sign_p_one_sided':float(binomtest(pos,30,.5,alternative='greater').pvalue),'pass':bool(pos>=thr)}
piv=dd.pivot(index='block',columns='direction',values='DeltaH');fr=friedmanchisquare(*[piv[c].values for c in piv.columns]);rngm=float(dm['mean'].max()-dm['mean'].min());stats['P6']={'friedman_stat':float(fr.statistic),'p':float(fr.pvalue),'direction_mean_range':rngm,'pass':bool(fr.pvalue<.01 and rngm>.02)}
stats['secondary']={'Delta_C_pop_mean':float(df.Delta_C_pop.mean()),'Delta_C_pop_positive':int((df.Delta_C_pop>0).sum()),'DeltaC_probe05_mean':float(df.DeltaC_probe05.mean()),'direction_means':dm[['direction','phi_deg','distance2','mean','sem']].to_dict(orient='records')}
stats['all_primary_pass']=all(stats[k]['pass'] for k in ['P1','P2','P3','P4','P5','P6'])
with open(OUT/'CONFIRM_STATS.json','w') as fh:json.dump(stats,fh,indent=2)
pd.DataFrame(A,index=[f'{i}{j}' for i,j in PAIRS],columns=[f'R{k}' for k in range(R)]).to_csv(OUT/'CONFIRM_CATALYTIC_MATRIX.csv')
np.savez_compressed(OUT/'CONFIRM_ENDPOINT_STATES.npz',selected=np.stack([x[0] for x in states]),neutral=np.stack([x[1] for x in states]))
print(json.dumps(stats,indent=2))
