import numpy as np, pandas as pd, json, math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from scipy.stats import binomtest, pearsonr
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; RES.mkdir(exist_ok=True)
CFG=json.loads((ROOT/'control/CONFIG_v1.0.0.json').read_text())
N=CFG['N']; POP=CFG['population']; G=CFG['generations']; BETA=CFG['beta']; GAMMA=CFG['gamma']; KAPPA=CFG['kappa']; LAM=CFG['lambda']; MU=CFG['mu']; SSEL=CFG['selection_softmax']; AMP=CFG['scaffold_amplitude']; BASEP=CFG['base_p']; BASE=CFG['root_seed_base']
PGRID=CFG['fidelity_grid']; HANGLES=CFG['history_angles']; ALPHAS=CFG['expression_alphas']; PHIS=CFG['anisotropy_phis']; RAD=CFG['anisotropy_radius']
# fixed task and basis
idx=np.arange(N)
E1=np.cos(2*np.pi*idx/N); E1-=E1.mean(); E1/=np.sqrt(np.mean(E1**2))
E2=np.sin(2*np.pi*idx/N); E2-=E2.mean(); E2/=np.sqrt(np.mean(E2**2))
rng=np.random.default_rng(CFG['task_seed']); Y=np.r_[np.full(N//2,-1),np.full(N//2,1)]; rng.shuffle(Y)

def field(theta, amp=AMP): return amp*(np.cos(theta)*E1+np.sin(theta)*E2)
def q(X,B):
    h=BETA*B + GAMMA*X + KAPPA*(np.roll(X,1,axis=-1)+np.roll(X,-1,axis=-1))
    return 1/(1+np.exp(-h))
def fit(X,B):
    qq=q(X,B); correct=np.where(Y>0,qq,1-qq); err=1-correct.mean(axis=-1); return np.exp(-LAM*err)
def founder(seed):
    r=np.random.default_rng(seed); return r.choice([-1,1],size=(POP,N))
def evolve(X0,seed,B,p,selected):
    r=np.random.default_rng(seed); X=X0.copy()
    for _ in range(G):
        f=fit(X,B)
        if selected:
            z=np.log(f+1e-15); z=(z-z.mean())/(z.std()+1e-9); w=np.exp(SSEL*z); w/=w.sum(); inds=r.choice(POP,POP,p=w)
        else: inds=r.integers(0,POP,size=POP)
        P=X[inds]; copy=r.random((POP,N))<p; X=np.where(copy,P,r.choice([-1,1],size=(POP,N)))
        mut=r.random((POP,N))<MU; X=np.where(mut,-X,X)
    return X
def metrics(X,B,seed,n_scr=12):
    fi=float(fit(X,B).mean()); r=np.random.default_rng(seed); vals=[]
    for _ in range(n_scr):
        Xs=np.empty_like(X)
        for j,row in enumerate(X): Xs[j]=row[r.permutation(N)]
        vals.append(fit(Xs,B).mean())
    fe=float(np.mean(vals)); return fi, fi-fe

def run_block(b):
    X0=founder(BASE+b)
    hist=[]; store={}
    for h,th in enumerate(HANGLES):
        B=field(th); ss=BASE+100000+b*100+h; ns=BASE+200000+b*100+h
        XS=evolve(X0,ss,B,BASEP,True); XN=evolve(X0,ns,B,BASEP,False); store[h]=(XS,XN)
        for j,tp in enumerate(HANGLES):
            Bp=field(tp); fs,vrs=metrics(XS,Bp,BASE+500000+b*10000+h*100+j); fn,vrn=metrics(XN,Bp,BASE+600000+b*10000+h*100+j)
            hist.append([b,h,j,th,tp,fs,fn,fs-fn,vrs,vrn,vrs-vrn])
    # fidelity theta=0
    fid=[]; B0=field(0)
    for j,p in enumerate(PGRID):
        ss=BASE+300000+b*100+j; ns=BASE+400000+b*100+j
        XS=evolve(X0,ss,B0,p,True); XN=evolve(X0,ns,B0,p,False)
        fs,vrs=metrics(XS,B0,BASE+700000+b*1000+j); fn,vrn=metrics(XN,B0,BASE+800000+b*1000+j)
        fid.append([b,p,fs,fn,fs-fn,vrs,vrn,vrs-vrn])
    # expression and anisotropy reuse history-0 populations
    XS,XN=store[0]
    expr=[]
    for j,a in enumerate(ALPHAS):
        Bp=a*B0; fs,vrs=metrics(XS,Bp,BASE+900000+b*1000+j); fn,vrn=metrics(XN,Bp,BASE+910000+b*1000+j)
        expr.append([b,a,fs,fn,fs-fn,vrs,vrn,vrs-vrn])
    ani=[]
    for j,ph in enumerate(PHIS):
        Bp=B0+RAD*(np.cos(ph)*E1+np.sin(ph)*E2); fs,vrs=metrics(XS,Bp,BASE+920000+b*1000+j); fn,vrn=metrics(XN,Bp,BASE+930000+b*1000+j)
        ani.append([b,ph,RAD,fs,fn,fs-fn,vrs,vrn,vrs-vrn])
    return hist,fid,expr,ani

def boot_ci(x,alpha=.01,nboot=None,seed=0):
    if nboot is None: nboot=CFG['bootstrap_reps']
    x=np.asarray(x,float); r=np.random.default_rng(seed); n=len(x); vals=[]
    for _ in range((nboot+4999)//5000):
        m=min(5000,nboot-len(vals)*5000)
        if m<=0: break
        ii=r.integers(0,n,size=(m,n)); vals.append(x[ii].mean(axis=1))
    v=np.concatenate(vals)[:nboot]; return np.quantile(v,[alpha/2,1-alpha/2])
def holm(ps):
    ps=np.asarray(ps); order=np.argsort(ps); adj=np.empty_like(ps,float); run=0.; m=len(ps)
    for rank,i in enumerate(order): run=max(run,(m-rank)*ps[i]); adj[i]=min(1,run)
    return adj

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=8) as ex: chunks=list(ex.map(run_block,range(CFG['n_blocks'])))
    hist=[r for c in chunks for r in c[0]]; fid=[r for c in chunks for r in c[1]]; expr=[r for c in chunks for r in c[2]]; ani=[r for c in chunks for r in c[3]]
    H=pd.DataFrame(hist,columns=['block','history','probe','theta_hist','theta_probe','fit_S','fit_N','D_fitness','Vrel_S','Vrel_N','DeltaV_rel']); H.to_csv(RES/'history_cross_eval.csv',index=False)
    F=pd.DataFrame(fid,columns=['block','p','fit_S','fit_N','D_fitness','Vrel_S','Vrel_N','DeltaV_rel']); F.to_csv(RES/'fidelity.csv',index=False)
    E=pd.DataFrame(expr,columns=['block','alpha','fit_S','fit_N','D_fitness','Vrel_S','Vrel_N','DeltaV_rel']); E.to_csv(RES/'expression.csv',index=False)
    A=pd.DataFrame(ani,columns=['block','phi','radius','fit_S','fit_N','D_fitness','Vrel_S','Vrel_N','DeltaV_rel']); A.to_csv(RES/'anisotropy.csv',index=False)
    # formal contrasts
    rows=[]
    for b,g in H.groupby('block'):
        cs=[]
        for j in sorted(g.probe.unique()):
            col=g[g.probe==j]; match=float(col[col.history==j].fit_S.iloc[0]); mis=float(col[col.history!=j].fit_S.mean()); cs.append(match-mis)
        rows.append([b,np.mean(cs)])
    C=pd.DataFrame(rows,columns=['block','C1'])
    high=[.9,.925,.95,.975,1.0]; low=[0,.1,.2,.3,.4,.5,.6]
    vals=[]
    for b,g in F.groupby('block'):
        c2=g[g.p.isin(high)].DeltaV_rel.mean()-g[g.p.isin(low)].DeltaV_rel.mean(); c3=float(g[np.isclose(g.p,.975)].DeltaV_rel.iloc[0]); vals.append([b,c2,c3])
    C=C.merge(pd.DataFrame(vals,columns=['block','C2','C3']),on='block')
    vals=[]
    for b,g in E.groupby('block'):
        c4=float(g[np.isclose(g.alpha,.4)].DeltaV_rel.iloc[0]-g[np.isclose(g.alpha,1.0)].DeltaV_rel.iloc[0]); vals.append([b,c4])
    C=C.merge(pd.DataFrame(vals,columns=['block','C4']),on='block')
    vals=[]
    for b,g in A.groupby('block'):
        c5=float(g[np.isclose(g.phi,np.pi)].DeltaV_rel.iloc[0]-g[np.isclose(g.phi,0)].DeltaV_rel.iloc[0]); vals.append([b,c5])
    C=C.merge(pd.DataFrame(vals,columns=['block','C5']),on='block'); C.to_csv(RES/'block_contrasts.csv',index=False)
    raw=[]; tmp=[]
    for j,c in enumerate(['C1','C2','C3','C4','C5']):
        x=C[c].values; pos=int((x>0).sum()); p=float(binomtest(pos,len(x),.5,alternative='greater').pvalue); raw.append(p); lo,hi=boot_ci(x,.01,CFG['bootstrap_reps'],CFG['bootstrap_seed']+j)
        tmp.append({'contrast':c,'mean':float(x.mean()),'median':float(np.median(x)),'ci99_low':float(lo),'ci99_high':float(hi),'positive_blocks':pos,'sign_p_raw':p})
    adj=holm(raw)
    for r,p in zip(tmp,adj): r['sign_p_holm']=float(p); r['pass']=bool(r['mean']>0 and r['ci99_low']>0 and p<.05)
    FR=pd.DataFrame(tmp); FR.to_csv(RES/'formal_contrasts.csv',index=False)
    # profile correlation
    tmpl=pd.read_csv(ROOT/'control/DISCOVERY_ANISOTROPY_TEMPLATE.csv').sort_values('phi')
    conf=A.groupby('phi',as_index=False).DeltaV_rel.mean().sort_values('phi')
    rp=float(pearsonr(tmpl.DeltaV_rel,conf.DeltaV_rel).statistic)
    # summaries
    H.groupby(['history','probe'],as_index=False)[['fit_S','D_fitness','DeltaV_rel']].mean().to_csv(RES/'history_cross_eval_summary.csv',index=False)
    F.groupby('p',as_index=False)[['D_fitness','DeltaV_rel']].agg(['mean','sem']).to_csv(RES/'fidelity_summary.csv')
    E.groupby('alpha',as_index=False)[['D_fitness','DeltaV_rel']].agg(['mean','sem']).to_csv(RES/'expression_summary.csv')
    conf.to_csv(RES/'anisotropy_summary.csv',index=False)
    overall=bool(FR['pass'].all() and rp>0.90)
    summary={'classification':'STRONG PROSPECTIVE SUPPORT' if overall else 'PARTIAL/FAILED PROSPECTIVE SUPPORT','overall_pass':overall,'anisotropy_profile_r':rp,'profile_pass':rp>0.90,'contrasts':tmp,'n_blocks':CFG['n_blocks']}
    (RES/'result_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
