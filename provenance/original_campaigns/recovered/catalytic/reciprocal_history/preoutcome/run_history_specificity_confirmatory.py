import numpy as np, pandas as pd, json
from itertools import combinations_with_replacement
from pathlib import Path
from scipy.stats import binomtest

ROOT=Path('/mnt/data/CATALYTIC_COMPLEX_HISTORY_SPECIFICITY_CONFIRMATORY_v1.0.0')
OUT=ROOT/'results'
OUT.mkdir(parents=True, exist_ok=True)

M=4; R=4; PAIRS=list(combinations_with_replacement(range(M),2)); D=len(PAIRS)
N=32; POP=48; GENS=180; MU=.01; SEL=24.; K=1.; P=.975; S=2.0; ASEED=51073
UNIF=np.ones(D)/D
H1=np.array([1.,-1.,0.,0.]); H1/=np.linalg.norm(H1)
H2=np.array([1.,1.,-2.,0.]); H2/=np.linalg.norm(H2)

rng=np.random.default_rng(ASEED); A=np.exp(.9*rng.normal(size=(D,R)))
for _ in range(2000):
    A*=(R/A.sum(1))[:,None]
    A*=(D/A.sum(0))[None,:]

pi={p:i for i,p in enumerate(PAIRS)}; MUT=np.zeros((D,D))
for d,(i,j) in enumerate(PAIRS):
    MUT[d,d]=1-MU; ev=[]
    for pos in (0,1):
        old=[i,j]
        for new in range(M):
            if new==old[pos]: continue
            q=old.copy(); q[pos]=new; ev.append(pi[tuple(sorted(q))])
    for z in ev: MUT[d,z]+=MU/len(ev)

def erase(f):
    mono=np.zeros(M)
    for n,(i,j) in zip(f,PAIRS):
        if i==j: mono[i]+=2*n
        else: mono[i]+=n; mono[j]+=n
    p=mono/mono.sum(); fe=np.zeros(D)
    for k,(i,j) in enumerate(PAIRS): fe[k]=p[i]*p[j] if i==j else 2*p[i]*p[j]
    return fe/fe.sum()

def jsd(p,q):
    p=p/p.sum(); q=q/q.sum(); m=.5*(p+q)
    def kl(a,b):
        z=a>0; return np.sum(a[z]*np.log2(a[z]/b[z]))
    return .5*kl(p,m)+.5*kl(q,m)

def chem(f,b,s=S):
    cat=f@A; u=np.exp(s*np.asarray(b))*cat; v=u/(K+u); q=v/v.sum()
    fit=R/np.sum(1/np.clip(v,1e-12,None))
    return q,fit

def fitcells(st,b,s=S):
    f=st/st.sum(1,keepdims=True); cat=f@A; u=np.exp(s*np.asarray(b))[None,:]*cat; v=u/(K+u)
    return R/np.sum(1/np.clip(v,1e-12,None),axis=1)

def metrics(st,b,s=S):
    f=st.sum(0)/st.sum(); fe=erase(f); qi,fi=chem(f,b,s); qe,fer=chem(fe,b,s)
    return {'fitness':float(fitcells(st,b,s).mean()), 'R_pop':float(jsd(f,fe)), 'C_pop':float(jsd(qi,qe)), 'V_rel':float(fi-fer)}

def founder(seed):
    r=np.random.default_rng(seed); return np.stack([r.multinomial(N,UNIF) for _ in range(POP)])

def evolve(st,selected,seed,hist):
    r=np.random.default_rng(seed); st=st.copy()
    for _ in range(GENS):
        if selected:
            ft=fitcells(st,hist,S); z=SEL*(ft-ft.mean()); z-=z.max(); w=np.exp(z); w/=w.sum(); pars=r.choice(POP,POP,p=w)
        else:
            pars=r.integers(0,POP,POP)
        new=np.empty_like(st)
        for o,pa in enumerate(pars):
            pr=(P*(st[pa]/N)+(1-P)*UNIF)@MUT; pr/=pr.sum(); new[o]=r.multinomial(N,pr)
        st=new
    return st

ledger=pd.read_csv(ROOT/'preoutcome'/'SEED_LEDGER.csv')
rows=[]; long=[]; states={k:[] for k in ['S1','S2','N1','N2']}
for rec in ledger.itertuples(index=False):
    f=founder(rec.founder_seed)
    S1=evolve(f,True,rec.selected_H1_seed,H1)
    S2=evolve(f,True,rec.selected_H2_seed,H2)
    N1=evolve(f,False,rec.neutral_H1_seed,H1)
    N2=evolve(f,False,rec.neutral_H2_seed,H2)
    for k,st in [('S1',S1),('S2',S2),('N1',N1),('N2',N2)]: states[k].append(st)
    mets={}
    for lin,st in [('S1',S1),('S2',S2),('N1',N1),('N2',N2)]:
        for probe,b in [('H1',H1),('H2',H2)]:
            m=metrics(st,b); mets[(lin,probe)]=m
            long.append({'block':rec.block,'lineage':lin,'probe':probe,**m})
    R1H1=mets[('S1','H1')]['fitness']-mets[('N1','H1')]['fitness']
    R2H1=mets[('S2','H1')]['fitness']-mets[('N2','H1')]['fitness']
    R1H2=mets[('S1','H2')]['fitness']-mets[('N1','H2')]['fitness']
    R2H2=mets[('S2','H2')]['fitness']-mets[('N2','H2')]['fitness']
    H_fit=.5*((R1H1-R2H1)+(R2H2-R1H2))
    H_selected=.5*((mets[('S1','H1')]['fitness']-mets[('S2','H1')]['fitness'])+(mets[('S2','H2')]['fitness']-mets[('S1','H2')]['fitness']))
    H_neutral=.5*((mets[('N1','H1')]['fitness']-mets[('N2','H1')]['fitness'])+(mets[('N2','H2')]['fitness']-mets[('N1','H2')]['fitness']))
    RV1H1=mets[('S1','H1')]['V_rel']-mets[('N1','H1')]['V_rel']
    RV2H1=mets[('S2','H1')]['V_rel']-mets[('N2','H1')]['V_rel']
    RV1H2=mets[('S1','H2')]['V_rel']-mets[('N1','H2')]['V_rel']
    RV2H2=mets[('S2','H2')]['V_rel']-mets[('N2','H2')]['V_rel']
    H_Vrel=.5*((RV1H1-RV2H1)+(RV2H2-RV1H2))
    row={'block':rec.block,'H_fit':H_fit,'H_selected':H_selected,'H_neutral':H_neutral,'identity_error':H_fit-(H_selected-H_neutral),'H_Vrel':H_Vrel,
         'R1_H1':R1H1,'R2_H1':R2H1,'R1_H2':R1H2,'R2_H2':R2H2,
         'RV1_H1':RV1H1,'RV2_H1':RV2H1,'RV1_H2':RV1H2,'RV2_H2':RV2H2}
    rows.append(row)

df=pd.DataFrame(rows); dl=pd.DataFrame(long)
df.to_csv(OUT/'BLOCK_HISTORY_SPECIFICITY_RESULTS.csv',index=False)
dl.to_csv(OUT/'CROSS_EVALUATION_LONG.csv',index=False)
np.savez_compressed(OUT/'ENDPOINT_STATES.npz', **{k:np.stack(v) for k,v in states.items()})
pd.DataFrame(A,index=[f'{i}{j}' for i,j in PAIRS],columns=[f'R{k}' for k in range(R)]).to_csv(OUT/'CATALYTIC_MATRIX.csv')

x=df.H_fit.to_numpy(); pos=int(np.sum(x>0)); p_sign=float(binomtest(pos,len(x),.5,alternative='greater').pvalue)
brng=np.random.default_rng(93510); means=np.empty(100000)
for i in range(100000): means[i]=brng.choice(x,size=len(x),replace=True).mean()
lo,hi=np.quantile(means,[.005,.995])
pass_primary=bool(pos>=24 and lo>0)
secondary={}
for c in ['H_selected','H_neutral','H_Vrel']:
    z=df[c].to_numpy(); secondary[c]={'mean':float(z.mean()),'positive_blocks':int(np.sum(z>0))}
res={'primary':{'endpoint':'H_fit','mean':float(x.mean()),'positive_blocks':pos,'n_blocks':len(x),'one_sided_sign_p':p_sign,'bootstrap_99_ci':[float(lo),float(hi)],'positive_block_threshold':24,'pass':pass_primary},'secondary':secondary,'max_abs_identity_error':float(np.abs(df.identity_error).max())}
with open(OUT/'FORMAL_RESULT.json','w') as f: json.dump(res,f,indent=2)
pd.DataFrame([{'endpoint':'H_fit','mean':res['primary']['mean'],'positive_blocks':pos,'n_blocks':len(x),'sign_p_one_sided':p_sign,'ci99_low':float(lo),'ci99_high':float(hi),'pass':pass_primary}]).to_csv(OUT/'FORMAL_RESULT.csv',index=False)
print(json.dumps(res,indent=2))
