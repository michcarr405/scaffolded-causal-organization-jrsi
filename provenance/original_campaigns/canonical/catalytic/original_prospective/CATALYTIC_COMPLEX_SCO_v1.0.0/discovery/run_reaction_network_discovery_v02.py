import numpy as np, pandas as pd, json
from itertools import combinations_with_replacement
from pathlib import Path

OUT=Path('/mnt/data/reaction_net_pilot/discovery_v02'); OUT.mkdir(parents=True, exist_ok=True)
MONOMERS=4; REACTIONS=4
PAIRS=list(combinations_with_replacement(range(MONOMERS),2)); D=len(PAIRS)
N_DIMER=32; POP=48; GENS=180; MU=0.01; SEL=24.0; KHALF=1.0; AFF_SEED=41721; ROOT0=930000

rng=np.random.default_rng(AFF_SEED)
A=np.exp(0.9*rng.normal(size=(D,REACTIONS)))
for _ in range(2000):
    A *= (REACTIONS/A.sum(axis=1))[:,None]
    A *= (D/A.sum(axis=0))[None,:]
# basis
basis=[]
for raw in [np.array([1.,-1,0,0]),np.array([1.,1.,-2,0]),np.array([1.,1.,1.,-3])]:
    v=raw.copy()
    for u in basis: v-=u*np.dot(u,v)
    v/=np.linalg.norm(v); basis.append(v)
e1,e2,e3=basis
PAIR_TO_IDX={p:i for i,p in enumerate(PAIRS)}
MUT=np.zeros((D,D))
for d,(i,j) in enumerate(PAIRS):
    MUT[d,d]=1-MU
    ev=[]
    for pos in (0,1):
        old=[i,j]
        for new in range(MONOMERS):
            if new==old[pos]: continue
            q=old.copy(); q[pos]=new; ev.append(PAIR_TO_IDX[tuple(sorted(q))])
    for k in ev: MUT[d,k]+=MU/len(ev)
UNIF=np.ones(D)/D

def erase_pairing_from_freq(f):
    mono=np.zeros(MONOMERS)
    for n,(i,j) in zip(f,PAIRS):
        if i==j: mono[i]+=2*n
        else: mono[i]+=n; mono[j]+=n
    p=mono/mono.sum(); fe=np.zeros(D)
    for k,(i,j) in enumerate(PAIRS): fe[k]=p[i]*p[j] if i==j else 2*p[i]*p[j]
    return fe/fe.sum()

def jsd(p,q):
    p=np.asarray(p,float); q=np.asarray(q,float); p/=p.sum(); q/=q.sum(); m=.5*(p+q)
    def kl(a,b):
        z=a>0; return np.sum(a[z]*np.log2(a[z]/b[z]))
    return .5*kl(p,m)+.5*kl(q,m)

def chem(f,b,s):
    cat=f@A; u=np.exp(s*np.asarray(b))*cat; v=u/(KHALF+u); q=v/v.sum(); fit=REACTIONS/np.sum(1/np.clip(v,1e-12,None)); return v,q,fit

def eval_cells(state,b,s):
    f=state/state.sum(1,keepdims=True); cat=f@A; u=np.exp(s*np.asarray(b))[None,:]*cat; v=u/(KHALF+u); fit=REACTIONS/np.sum(1/np.clip(v,1e-12,None),axis=1); return fit

def pop_metrics(state,b,s):
    f=state.sum(0)/state.sum()
    fe=erase_pairing_from_freq(f)
    _,qi,fi=chem(f,b,s); _,qe,fe_fit=chem(fe,b,s)
    return {
        'fitness_mean':float(eval_cells(state,b,s).mean()),
        'C_pop':float(jsd(qi,qe)),
        'R_pop':float(jsd(f,fe)),
        'V_rel':float(fi-fe_fit),
        'fit_aggregate':float(fi),
        'fit_erased':float(fe_fit),
    }

def founder(seed):
    r=np.random.default_rng(seed); return np.stack([r.multinomial(N_DIMER,UNIF) for _ in range(POP)])

def evolve(init,b,s,p,selected,seed,checkpoints=(0,30,60,120,180)):
    r=np.random.default_rng(seed); state=init.copy(); tr=[]
    for g in range(GENS+1):
        if g in checkpoints:
            tr.append((g,pop_metrics(state,b,s)))
        if g==GENS: break
        fit=eval_cells(state,b,s)
        if selected:
            z=SEL*(fit-fit.mean()); z-=z.max(); w=np.exp(z); w/=w.sum(); parents=r.choice(POP,POP,p=w)
        else: parents=r.integers(0,POP,POP)
        new=np.empty_like(state)
        for o,par in enumerate(parents):
            probs=(p*(state[par]/N_DIMER)+(1-p)*UNIF)@MUT; probs/=probs.sum(); new[o]=r.multinomial(N_DIMER,probs)
        state=new
    return state,tr

def delta_hist(sel,neu,bh,bp,s):
    fs_h=eval_cells(sel,bh,s).mean(); fs_p=eval_cells(sel,bp,s).mean(); fn_h=eval_cells(neu,bh,s).mean(); fn_p=eval_cells(neu,bp,s).mean(); return (fs_h-fs_p)-(fn_h-fn_p)

hist=e1; primary_s=2.0; primary_p=.975
# A primary
rows=[]; ep=[]; costs=[]
for b in range(16):
    f=founder(ROOT0+b)
    m0=pop_metrics(f,hist,0); mb=pop_metrics(f,hist,primary_s); costs.append({'block':b,'no_scaffold':m0['fitness_mean'],'scaffold':mb['fitness_mean'],'cost':mb['fitness_mean']-m0['fitness_mean']})
    S,trS=evolve(f,hist,primary_s,primary_p,True,ROOT0+10000+b)
    N,trN=evolve(f,hist,primary_s,primary_p,False,ROOT0+20000+b)
    for mode,tr in [('selected',trS),('neutral',trN)]:
        for g,m in tr: rows.append({'block':b,'mode':mode,'generation':g,**m})
    for mode,st in [('selected',S),('neutral',N)]: ep.append({'block':b,'mode':mode,**pop_metrics(st,hist,primary_s)})
pd.DataFrame(rows).to_csv(OUT/'A_timecourse.csv',index=False); pd.DataFrame(ep).to_csv(OUT/'A_endpoints.csv',index=False); pd.DataFrame(costs).to_csv(OUT/'A_founder_cost.csv',index=False)
# B fidelity
fids=[.35,.55,.75,.90,.975]; fr=[]
for pi,p in enumerate(fids):
    for b in range(8):
        f=founder(ROOT0+30000+1000*pi+b); S,_=evolve(f,hist,primary_s,p,True,ROOT0+40000+1000*pi+b,checkpoints=(180,)); N,_=evolve(f,hist,primary_s,p,False,ROOT0+50000+1000*pi+b,checkpoints=(180,))
        fr += [{'p':p,'block':b,'mode':'selected',**pop_metrics(S,hist,primary_s)},{'p':p,'block':b,'mode':'neutral',**pop_metrics(N,hist,primary_s)}]
pd.DataFrame(fr).to_csv(OUT/'B_fidelity.csv',index=False)
# C retrieval
train=[1.0,1.5,2.0,2.5]; probes=np.arange(0,3.01,.25); rr=[]
for ti,ts in enumerate(train):
    for b in range(8):
        f=founder(ROOT0+60000+1000*ti+b); S,_=evolve(f,hist,ts,.975,True,ROOT0+70000+1000*ti+b,checkpoints=(180,)); N,_=evolve(f,hist,ts,.975,False,ROOT0+80000+1000*ti+b,checkpoints=(180,))
        for q in probes:
            ms=pop_metrics(S,hist,float(q)); mn=pop_metrics(N,hist,float(q)); rr.append({'train_strength':ts,'probe_strength':q,'block':b,'DeltaC':ms['C_pop']-mn['C_pop'],'DeltaV':ms['V_rel']-mn['V_rel'],'DeltaF':ms['fitness_mean']-mn['fitness_mean'],'C_selected':ms['C_pop'],'C_neutral':mn['C_pop']})
pd.DataFrame(rr).to_csv(OUT/'C_retrieval.csv',index=False)
# D anisotropy equal distance
theta=np.deg2rad(60); phis=np.deg2rad(np.arange(0,360,45)); probes2=[]
for k,phi in enumerate(phis):
    perp=np.cos(phi)*e2+np.sin(phi)*e3; v=np.cos(theta)*e1+np.sin(theta)*perp; v/=np.linalg.norm(v); probes2.append((k,np.rad2deg(phi),v))
dr=[]
for b in range(12):
    f=founder(ROOT0+90000+b); S,_=evolve(f,hist,primary_s,.975,True,ROOT0+100000+b,checkpoints=(180,)); N,_=evolve(f,hist,primary_s,.975,False,ROOT0+110000+b,checkpoints=(180,))
    for k,phi,v in probes2: dr.append({'block':b,'direction':k,'phi_deg':phi,'distance2':np.sum((v-hist)**2),'DeltaH':delta_hist(S,N,hist,v,primary_s)})
pd.DataFrame(dr).to_csv(OUT/'D_anisotropy.csv',index=False)
# summaries
summary={}
Aep=pd.DataFrame(ep).pivot(index='block',columns='mode')
summary['A']={}
for m in ['fitness_mean','C_pop','R_pop','V_rel']:
    d=Aep[m]['selected']-Aep[m]['neutral']; summary['A'][m]={'selected':float(Aep[m]['selected'].mean()),'neutral':float(Aep[m]['neutral'].mean()),'delta':float(d.mean()),'positive':int((d>0).sum()),'n':len(d)}
co=pd.DataFrame(costs); summary['A']['founder_cost']={'mean':float(co.cost.mean()),'negative':int((co.cost<0).sum()),'n':len(co)}
Bdf=pd.DataFrame(fr); bs=[]
for p,g in Bdf.groupby('p'):
    pv=g.pivot(index='block',columns='mode'); rec={'p':float(p)}
    for m in ['fitness_mean','C_pop','R_pop','V_rel']:
        d=pv[m]['selected']-pv[m]['neutral']; rec['Delta_'+m]=float(d.mean()); rec['positive_'+m]=int((d>0).sum())
    bs.append(rec)
summary['B']=bs; pd.DataFrame(bs).to_csv(OUT/'B_fidelity_summary.csv',index=False)
Cdf=pd.DataFrame(rr); cm=Cdf.groupby(['train_strength','probe_strength'],as_index=False).mean(numeric_only=True); cm.to_csv(OUT/'C_retrieval_mean.csv',index=False); peaks=[]
for ts,g in cm.groupby('train_strength'):
    j=g.DeltaC.idxmax(); row=g.loc[j]; peaks.append({'train_strength':float(ts),'peak_probe':float(row.probe_strength),'peak_DeltaC':float(row.DeltaC),'DeltaC_at_train':float(g.loc[np.isclose(g.probe_strength,ts),'DeltaC'].iloc[0])})
summary['C']=peaks; pd.DataFrame(peaks).to_csv(OUT/'C_retrieval_peaks.csv',index=False)
Ddf=pd.DataFrame(dr); dm=Ddf.groupby(['direction','phi_deg','distance2'],as_index=False).DeltaH.mean(); dm.to_csv(OUT/'D_anisotropy_mean.csv',index=False); summary['D']={'range':float(dm.DeltaH.max()-dm.DeltaH.min()),'distance2_unique':sorted(dm.distance2.round(12).unique().tolist()),'means':dm.to_dict(orient='records')}
summary['model']={'monomers':MONOMERS,'dimers':D,'reactions':REACTIONS,'N_DIMER':N_DIMER,'POP':POP,'GENS':GENS,'MU':MU,'SEL':SEL,'AFF_SEED':AFF_SEED}
with open(OUT/'SUMMARY.json','w') as fh: json.dump(summary,fh,indent=2)
pd.DataFrame(A,index=[f'{i}{j}' for i,j in PAIRS],columns=[f'R{j}' for j in range(REACTIONS)]).to_csv(OUT/'catalytic_matrix.csv')
print(json.dumps(summary,indent=2))
