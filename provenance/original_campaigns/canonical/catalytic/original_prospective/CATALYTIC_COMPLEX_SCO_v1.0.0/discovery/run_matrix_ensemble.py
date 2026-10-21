import numpy as np, pandas as pd, importlib.util
from pathlib import Path
# import definitions without running campaign by extracting? easier duplicate compact model
from itertools import combinations_with_replacement
OUT=Path('/mnt/data/reaction_net_pilot/discovery_v02')
M=4; R=4; PAIRS=list(combinations_with_replacement(range(M),2)); D=len(PAIRS); N=32; POP=48; GENS=180; MU=.01; SEL=24.; K=1.; UNIF=np.ones(D)/D
basis=[]
for raw in [np.array([1.,-1,0,0]),np.array([1.,1.,-2,0]),np.array([1.,1.,1.,-3])]:
 v=raw.copy()
 for u in basis:v-=u*np.dot(u,v)
 v/=np.linalg.norm(v); basis.append(v)
hist=basis[0]
PAIR_TO_IDX={p:i for i,p in enumerate(PAIRS)}
MUT=np.zeros((D,D))
for d,(i,j) in enumerate(PAIRS):
 MUT[d,d]=1-MU; ev=[]
 for pos in (0,1):
  old=[i,j]
  for new in range(M):
   if new==old[pos]:continue
   q=old.copy(); q[pos]=new; ev.append(PAIR_TO_IDX[tuple(sorted(q))])
 for z in ev:MUT[d,z]+=MU/len(ev)

def mkA(seed):
 r=np.random.default_rng(seed); A=np.exp(.9*r.normal(size=(D,R)))
 for _ in range(1000):
  A*=(R/A.sum(1))[:,None]; A*=(D/A.sum(0))[None,:]
 return A

def erase(f):
 mono=np.zeros(M)
 for n,(i,j) in zip(f,PAIRS):
  if i==j:mono[i]+=2*n
  else:mono[i]+=n;mono[j]+=n
 p=mono/mono.sum(); fe=np.zeros(D)
 for k,(i,j) in enumerate(PAIRS):fe[k]=p[i]*p[j] if i==j else 2*p[i]*p[j]
 return fe/fe.sum()
def jsd(p,q):
 p=p/p.sum();q=q/q.sum();m=.5*(p+q)
 return .5*np.sum(np.where(p>0,p*np.log2(p/m),0))+.5*np.sum(np.where(q>0,q*np.log2(q/m),0))
def chem(f,A,s=2):
 cat=f@A;u=np.exp(s*hist)*cat;v=u/(K+u);q=v/v.sum();fit=R/np.sum(1/v);return q,fit
def fitcells(st,A,s=2):
 f=st/st.sum(1,keepdims=True);cat=f@A;u=np.exp(s*hist)[None,:]*cat;v=u/(K+u);return R/np.sum(1/v,axis=1)
def metrics(st,A,s=2):
 f=st.sum(0)/st.sum();fe=erase(f);qi,fi=chem(f,A,s);qe,fer=chem(fe,A,s);return fitcells(st,A,s).mean(),jsd(qi,qe),fi-fer
def founder(seed):
 r=np.random.default_rng(seed);return np.stack([r.multinomial(N,UNIF) for _ in range(POP)])
def evolve(st,A,p,selected,seed):
 r=np.random.default_rng(seed);st=st.copy()
 for g in range(GENS):
  ft=fitcells(st,A)
  if selected:
   z=SEL*(ft-ft.mean());z-=z.max();w=np.exp(z);w/=w.sum();pars=r.choice(POP,POP,p=w)
  else:pars=r.integers(0,POP,POP)
  new=np.empty_like(st)
  for o,pa in enumerate(pars):
   pr=(p*(st[pa]/N)+(1-p)*UNIF)@MUT;pr/=pr.sum();new[o]=r.multinomial(N,pr)
  st=new
 return st
rows=[]
seeds=[41722,41723,41724,41725,41726,41727]
for ai,aseed in enumerate(seeds):
 A=mkA(aseed)
 for b in range(8):
  root=1200000+ai*10000+b;f=founder(root)
  S=evolve(f,A,.975,True,root+1000);Nn=evolve(f,A,.975,False,root+2000)
  ms=metrics(S,A);mn=metrics(Nn,A)
  # founder cost using mean cell fitness at s=0 vs 2
  f0=fitcells(f,A,0).mean(); fb=fitcells(f,A,2).mean()
  rows.append({'A_seed':aseed,'block':b,'founder_cost':fb-f0,'DeltaF':ms[0]-mn[0],'DeltaC':ms[1]-mn[1],'DeltaV':ms[2]-mn[2]})
df=pd.DataFrame(rows);df.to_csv(OUT/'E_matrix_ensemble.csv',index=False)
s=df.groupby('A_seed').agg(founder_cost=('founder_cost','mean'),DeltaF=('DeltaF','mean'),DeltaC=('DeltaC','mean'),DeltaV=('DeltaV','mean'),posF=('DeltaF',lambda x:(x>0).sum()),posC=('DeltaC',lambda x:(x>0).sum()),posV=('DeltaV',lambda x:(x>0).sum())).reset_index();s.to_csv(OUT/'E_matrix_ensemble_summary.csv',index=False);print(s.to_string(index=False));print('\nAcross matrices positive means:',(s[['DeltaF','DeltaC','DeltaV']]>0).sum().to_dict())
