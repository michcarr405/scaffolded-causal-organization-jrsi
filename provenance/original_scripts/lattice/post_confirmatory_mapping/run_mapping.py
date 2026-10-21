import json, math, warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize_scalar

ROOT=Path('/mnt/data/ABSTRACT_LATTICE_FIDELITY_TIME_SURFACE_DIAGNOSTIC_v1.0.0')
RES=ROOT/'results'; STATES=ROOT/'states'
CFG=json.loads((ROOT/'control/CONFIG_v1.0.0.json').read_text())
N=CFG['N']; POP=CFG['population']; G=CFG['dense_generations']; GS=CFG['sentinel_generations']
BETA=CFG['beta']; GAMMA=CFG['gamma']; KAPPA=CFG['kappa']; LAM=CFG['lambda']; MU=CFG['mu']; SSEL=CFG['selection_softmax']; AMP=CFG['scaffold_amplitude']; BASE=CFG['root_seed_base']
PGRID=np.array(CFG['fidelity_grid'],float); SENT=np.array(CFG['sentinel_p'],float); BASEP=CFG['base_p']; HANGLES=np.array(CFG['history_angles'],float); TPROBE=CFG['probe_generations']; ALPHAS=CFG['expression_alphas']; PHIS=CFG['anisotropy_phis']; RAD=CFG['anisotropy_radius']; NSCR=CFG['n_erasure_scrambles']
idx=np.arange(N)
E1=np.cos(2*np.pi*idx/N); E1-=E1.mean(); E1/=np.sqrt(np.mean(E1**2))
E2=np.sin(2*np.pi*idx/N); E2-=E2.mean(); E2/=np.sqrt(np.mean(E2**2))
rng=np.random.default_rng(CFG['task_seed']); Y=np.r_[np.full(N//2,-1),np.full(N//2,1)]; rng.shuffle(Y)

def field(theta,amp=AMP): return amp*(np.cos(theta)*E1+np.sin(theta)*E2)
B0=field(0.0)

def q(X,B):
    h=BETA*B + GAMMA*X + KAPPA*(np.roll(X,1,axis=-1)+np.roll(X,-1,axis=-1))
    return 1/(1+np.exp(-h))

def fit(X,B):
    qq=q(X,B); correct=np.where(Y>0,qq,1-qq); err=1-correct.mean(axis=-1); return np.exp(-LAM*err)

def founder(seed):
    r=np.random.default_rng(seed); return r.choice(np.array([-1,1],dtype=np.int8),size=(POP,N))

def reproduce(X,r,B,p,selected):
    f=fit(X,B)
    if selected:
        z=np.log(f+1e-15); z=(z-z.mean())/(z.std()+1e-9); w=np.exp(SSEL*z); w/=w.sum(); inds=r.choice(POP,POP,p=w)
    else:
        inds=r.integers(0,POP,size=POP)
    P=X[inds]; copy=r.random((POP,N))<p; repl=r.choice(np.array([-1,1],dtype=np.int8),size=(POP,N)); X=np.where(copy,P,repl).astype(np.int8)
    mut=r.random((POP,N))<MU; return np.where(mut,-X,X).astype(np.int8)

def paired_metrics(XS,XN,B,seed):
    fs=float(fit(XS,B).mean()); fn=float(fit(XN,B).mean())
    r=np.random.default_rng(seed)
    base=np.broadcast_to(np.arange(N,dtype=np.int16),(NSCR,POP,N)).copy()
    perms=r.permuted(base,axis=-1)
    def erased_mean(X):
        Xb=np.broadcast_to(X,(NSCR,POP,N)); Xe=np.take_along_axis(Xb,perms,axis=-1)
        return float(fit(Xe.reshape(NSCR*POP,N),B).mean())
    fes=erased_mean(XS); fen=erased_mean(XN)
    vrs=fs-fes; vrn=fn-fen
    return fs,fn,fs-fn,vrs,vrn,vrs-vrn

def structural(X):
    xb=X.mean(axis=0)
    neighbor=float(np.mean(X*np.roll(X,1,axis=-1)))
    fplus=(xb+1)/2
    hetero=float(np.mean(2*fplus*(1-fplus)))
    task=float(np.mean(xb*Y))
    scaff=float(np.mean(xb*E1))
    return neighbor,hetero,task,scaff,xb

def pack(X): return np.packbits((X>0).astype(np.uint8),axis=-1,bitorder='little')

def evolve_condition(block,p,pidx,X0,selected_seed,neutral_seed):
    rs=np.random.default_rng(selected_seed); rn=np.random.default_rng(neutral_seed)
    XS=X0.copy(); XN=X0.copy()
    statesS=np.empty((G+1,POP,(N+7)//8),dtype=np.uint8); statesN=np.empty_like(statesS)
    dense=[]; sites=[]; sentinel=[]; snaps={}
    is_sent=bool(np.any(np.isclose(SENT,p)))
    for t in range(G+1):
        statesS[t]=pack(XS); statesN[t]=pack(XN)
        seed=BASE+5000000+block*100000+pidx*1000+t
        fs,fn,df,vrs,vrn,dv=paired_metrics(XS,XN,B0,seed)
        sS=structural(XS); sN=structural(XN)
        dense.append([block,p,t,fs,fn,df,vrs,vrn,dv,*sS[:4],*sN[:4]])
        for tr,xb in [('S',sS[4]),('N',sN[4])]:
            sites.extend([[block,p,t,tr,i,float(xb[i])] for i in range(N)])
        if t<G:
            XS=reproduce(XS,rs,B0,p,True); XN=reproduce(XN,rn,B0,p,False)
    if is_sent:
        for t in range(G+1,GS+1):
            XS=reproduce(XS,rs,B0,p,True); XN=reproduce(XN,rn,B0,p,False)
            seed=BASE+6000000+block*100000+pidx*1000+t
            fs,fn,df,vrs,vrn,dv=paired_metrics(XS,XN,B0,seed)
            sS=structural(XS); sN=structural(XN)
            sentinel.append([block,p,t,fs,fn,df,vrs,vrn,dv,*sS[:4],*sN[:4]])
            if t in (100,150,200): snaps[t]=(pack(XS),pack(XN))
    return dense,sites,statesS,statesN,sentinel,snaps

def evolve_history(block,h,theta,X0,ss,ns):
    B=field(theta); rs=np.random.default_rng(ss); rn=np.random.default_rng(ns); XS=X0.copy(); XN=X0.copy()
    sS=np.empty((G+1,POP,(N+7)//8),dtype=np.uint8); sN=np.empty_like(sS); checkpoints={}
    for t in range(G+1):
        sS[t]=pack(XS); sN[t]=pack(XN)
        if t in TPROBE: checkpoints[t]=(XS.copy(),XN.copy())
        if t<G:
            XS=reproduce(XS,rs,B,BASEP,True); XN=reproduce(XN,rn,B,BASEP,False)
    return sS,sN,checkpoints

def unpack_arr(A):
    return np.where(np.unpackbits(A,axis=-1,count=N,bitorder='little')>0,1,-1).astype(np.int8)

def run_block(block):
    X0=founder(BASE+block)
    dense_rows=[]; site_rows=[]; sentinel_rows=[]
    packedS=np.empty((len(PGRID),G+1,POP,(N+7)//8),dtype=np.uint8); packedN=np.empty_like(packedS)
    sentinel_snaps={}
    # store p=.95 raw checkpoints for expression/anisotropy/history reuse
    p95_idx=int(np.where(np.isclose(PGRID,BASEP))[0][0]); p95_cp={}
    for j,p in enumerate(PGRID):
        ss=BASE+100000+block*1000+j; ns=BASE+200000+block*1000+j
        dr,sr,ps,pn,sen,snaps=evolve_condition(block,float(p),j,X0,ss,ns)
        dense_rows.extend(dr); site_rows.extend(sr); sentinel_rows.extend(sen); packedS[j]=ps; packedN[j]=pn
        if j==p95_idx:
            for t in TPROBE: p95_cp[t]=(unpack_arr(ps[t]),unpack_arr(pn[t]))
        for t,(a,b) in snaps.items(): sentinel_snaps[(j,t,'S')]=a; sentinel_snaps[(j,t,'N')]=b
    # History arms: h=0 reuses p=.95 dense trajectory; evolve h=1..3
    histS=np.empty((len(HANGLES),G+1,POP,(N+7)//8),dtype=np.uint8); histN=np.empty_like(histS); hist_cp={0:p95_cp}
    histS[0]=packedS[p95_idx]; histN[0]=packedN[p95_idx]
    for h,th in enumerate(HANGLES[1:],start=1):
        ss=BASE+300000+block*100+h; ns=BASE+400000+block*100+h
        a,b,cp=evolve_history(block,h,float(th),X0,ss,ns); histS[h]=a; histN[h]=b; hist_cp[h]=cp
    # Cross-history probes
    hx=[]; hs=[]
    for t in TPROBE:
        for h,th in enumerate(HANGLES):
            XS,XN=hist_cp[h][t]
            for j,tp in enumerate(HANGLES):
                Bp=field(float(tp)); seed=BASE+7000000+block*100000+t*1000+h*100+j
                fs,fn,df,vrs,vrn,dv=paired_metrics(XS,XN,Bp,seed)
                hx.append([block,t,h,j,float(th),float(tp),fs,fn,df,vrs,vrn,dv])
        # block-level matching advantages at this t
        arr=pd.DataFrame([r for r in hx if r[1]==t],columns=['block','t','history','probe','th','tp','fitS','fitN','dF','vS','vN','dV'])
        fit_adv=[]; v_adv=[]
        for j in range(len(HANGLES)):
            col=arr[arr.probe==j]; fit_adv.append(float(col[col.history==j].fitS.iloc[0]-col[col.history!=j].fitS.mean())); v_adv.append(float(col[col.history==j].dV.iloc[0]-col[col.history!=j].dV.mean()))
        hs.append([block,t,float(np.mean(fit_adv)),float(np.mean(v_adv))])
    # Expression and anisotropy dynamics from p=.95 theta=0 states
    expr=[]; ani=[]
    for t in TPROBE:
        XS,XN=p95_cp[t]
        for j,a in enumerate(ALPHAS):
            Bp=float(a)*B0; seed=BASE+8000000+block*100000+t*1000+j
            expr.append([block,t,float(a),*paired_metrics(XS,XN,Bp,seed)])
        for j,ph in enumerate(PHIS):
            Bp=B0+RAD*(np.cos(ph)*E1+np.sin(ph)*E2); seed=BASE+9000000+block*100000+t*1000+j
            ani.append([block,t,float(ph),RAD,*paired_metrics(XS,XN,Bp,seed)])
    # Save bit-packed full states per block
    snap_arrays={}
    for (j,t,tr),arr in sentinel_snaps.items(): snap_arrays[f'sentinel_{tr}_pidx{j}_t{t}']=arr
    np.savez_compressed(STATES/f'block_{block:02d}.npz',dense_selected=packedS,dense_neutral=packedN,history_selected=histS,history_neutral=histN,**snap_arrays)
    return dense_rows,site_rows,sentinel_rows,hx,hs,expr,ani

def stable_time(t,y,plateau,frac):
    t=np.asarray(t); y=np.asarray(y); baseline=float(y[t==0][0]); target=baseline+frac*(plateau-baseline)
    if plateau<=baseline+1e-6: return np.nan
    for i in range(len(t)):
        if y[i]>=target:
            j=min(len(t),i+4)
            if np.sum(y[i:j]>=target)>=min(3,j-i): return float(t[i])
    return np.nan

def expfun(t,c,A,k): return c+A*(1-np.exp(-k*t))
def logistic(p,c,A,s,p50): return c+A/(1+np.exp(-s*(p-p50)))
def stepfit(p,y):
    best=None
    for k in range(2,len(p)-2):
        pred=np.r_[np.repeat(y[:k].mean(),k),np.repeat(y[k:].mean(),len(p)-k)]; rss=float(np.sum((y-pred)**2))
        if best is None or rss<best[0]: best=(rss,p[k],pred)
    return best
def segmented_fit(p,y):
    def rss_for(bp):
        X=np.column_stack([np.ones_like(p),p,np.maximum(0,p-bp)])
        coef=np.linalg.lstsq(X,y,rcond=None)[0]; r=y-X@coef; return float(r@r),coef
    opt=minimize_scalar(lambda bp:rss_for(bp)[0],bounds=(0.05,0.95),method='bounded')
    rss,coef=rss_for(opt.x); pred=np.column_stack([np.ones_like(p),p,np.maximum(0,p-opt.x)])@coef
    return rss,float(opt.x),coef,pred
def aicc(rss,n,k):
    rss=max(rss,1e-15); a=n*np.log(rss/n)+2*k
    return a + 2*k*(k+1)/(n-k-1)

def analyze():
    D=pd.read_csv(RES/'dense_time_surface.csv'); S=pd.read_csv(RES/'sentinel_time_series.csv'); H=pd.read_csv(RES/'history_specificity_by_time.csv'); E=pd.read_csv(RES/'expression_by_time.csv'); A=pd.read_csv(RES/'anisotropy_by_time.csv')
    # mean surfaces
    mean=D.groupby(['p','t'],as_index=False).agg(DeltaV_rel=('DeltaV_rel','mean'),DeltaF=('DeltaF','mean'),Vrel_sem=('DeltaV_rel','sem'),DeltaF_sem=('DeltaF','sem'))
    mean.to_csv(RES/'dense_time_surface_summary.csv',index=False)
    # empirical amplitude and onset; descriptive exponential fit
    rows=[]
    for p,g in mean.groupby('p'):
        g=g.sort_values('t'); A50=float(g[g.t.between(41,50)].DeltaV_rel.mean()); F50=float(g[g.t.between(41,50)].DeltaF.mean())
        rec={'p':p,'A50_emp':A50,'DeltaF50_emp':F50}
        for name,col,pl in [('Vrel','DeltaV_rel',A50),('Fit','DeltaF',F50)]:
            for frac in (.1,.5,.9): rec[f't{int(frac*100)}_{name}']=stable_time(g.t.values,g[col].values,pl,frac)
        try:
            popt,_=curve_fit(expfun,g.t.values,g.DeltaV_rel.values,p0=[g.DeltaV_rel.iloc[0],max(A50-g.DeltaV_rel.iloc[0],1e-4),.1],bounds=([-0.05,-0.1,.001],[0.05,.5,2.0]),maxfev=20000)
            pred=expfun(g.t.values,*popt); ssr=np.sum((g.DeltaV_rel.values-pred)**2); sst=np.sum((g.DeltaV_rel.values-g.DeltaV_rel.mean())**2); r2=1-ssr/sst if sst>0 else np.nan
            rec.update(exp_c=popt[0],exp_A=popt[1],exp_k=popt[2] if A50>0.01 and r2>=.5 else np.nan,exp_r2=r2)
        except Exception: rec.update(exp_c=np.nan,exp_A=np.nan,exp_k=np.nan,exp_r2=np.nan)
        rows.append(rec)
    P=pd.DataFrame(rows); P.to_csv(RES/'fidelity_dynamic_parameters.csv',index=False)
    # fidelity response model comparison on A50
    p=P.p.values; y=P.A50_emp.values; n=len(p)
    model=[]
    try:
        popt,_=curve_fit(logistic,p,y,p0=[y.min(),y.max()-y.min(),10,.75],bounds=([-0.1,0,.1,0],[.1,.5,100,1]),maxfev=50000); pred=logistic(p,*popt); rss=float(np.sum((y-pred)**2)); model.append(['logistic',aicc(rss,n,4),rss,*popt])
    except Exception: popt=[np.nan]*4
    rss,bp,coef,pred=segmented_fit(p,y); model.append(['segmented',aicc(rss,n,4),rss,coef[0],coef[1],coef[2],bp])
    rss,bp,pred=stepfit(p,y); model.append(['hard_step',aicc(rss,n,3),rss,np.nan,np.nan,np.nan,bp])
    M=pd.DataFrame(model,columns=['model','AICc','RSS','param1','param2','param3','break_or_p50']); M['delta_AICc']=M.AICc-M.AICc.min(); M.to_csv(RES/'fidelity_shape_model_comparison.csv',index=False)
    # root-block bootstrap of logistic p10/p50/p90 + model winner
    rng=np.random.default_rng(CFG['bootstrap_seed']); boots=[]; winners=[]; blocks=np.sort(D.block.unique())
    for bi in range(CFG['bootstrap_reps']):
        samp=rng.choice(blocks,len(blocks),replace=True); parts=[]
        for newb,oldb in enumerate(samp):
            z=D[D.block==oldb].copy(); z['boot']=newb; parts.append(z)
        bd=pd.concat(parts,ignore_index=True); by=bd[bd.t.between(41,50)].groupby('p').DeltaV_rel.mean().reindex(p).values
        vals={}
        try:
            po,_=curve_fit(logistic,p,by,p0=[by.min(),by.max()-by.min(),10,.75],bounds=([-0.1,0,.1,0],[.1,.5,100,1]),maxfev=20000)
            rr=float(np.sum((by-logistic(p,*po))**2)); vals['logistic']=aicc(rr,n,4); c,aa,slope,p50=po; q=np.log(9)/slope; boots.append([p50-q,p50,p50+q,slope,aa])
        except Exception: vals['logistic']=np.inf
        rr,bb,cc,pr=segmented_fit(p,by); vals['segmented']=aicc(rr,n,4)
        rr,bb,pr=stepfit(p,by); vals['hard_step']=aicc(rr,n,3)
        winners.append(min(vals,key=vals.get))
    B=pd.DataFrame(boots,columns=['p10','p50','p90','slope','amplitude']); B.to_csv(RES/'fidelity_logistic_bootstrap.csv',index=False)
    from collections import Counter
    win=Counter(winners); (RES/'fidelity_shape_bootstrap_winners.json').write_text(json.dumps({k:int(v) for k,v in win.items()},indent=2))
    # sentinel A50 vs A200 per block and p
    d50=D[D.t.between(41,50)].groupby(['block','p']).DeltaV_rel.mean().rename('A50').reset_index(); d200=S[S.t.between(191,200)].groupby(['block','p']).DeltaV_rel.mean().rename('A200').reset_index(); Z=d50.merge(d200,on=['block','p']); Z['diff']=Z.A50-Z.A200; Z['rel_diff']=Z['diff']/Z.A200.replace(0,np.nan); Z.to_csv(RES/'sentinel_A50_A200_blocks.csv',index=False)
    ss=[]
    for p0,g in Z.groupby('p'):
        a50=g.A50.mean(); a200=g.A200.mean(); diff=g['diff'].mean(); rel=diff/a200 if abs(a200)>=.02 else np.nan; close=(abs(diff)<.01 and (abs(a200)<.02 or abs(rel)<.10)); ss.append([p0,a50,a200,diff,rel,close])
    pd.DataFrame(ss,columns=['p','A50_mean','A200_mean','difference','relative_difference','diagnostic_close']).to_csv(RES/'sentinel_stability_summary.csv',index=False)
    # higher-order contrasts by time
    ex=[]
    for (b,t),g in E.groupby(['block','t']):
        c=float(g[np.isclose(g.alpha,.4)].DeltaV_rel.iloc[0]-g[np.isclose(g.alpha,1.0)].DeltaV_rel.iloc[0]); ex.append([b,t,c])
    pd.DataFrame(ex,columns=['block','t','expression_C4']).to_csv(RES/'expression_separation_contrast_by_time.csv',index=False)
    an=[]
    for (b,t),g in A.groupby(['block','t']):
        c=float(g[np.isclose(g.phi,np.pi)].DeltaV_rel.iloc[0]-g[np.isclose(g.phi,0)].DeltaV_rel.iloc[0]); an.append([b,t,c])
    pd.DataFrame(an,columns=['block','t','anisotropy_C5']).to_csv(RES/'anisotropy_contrast_by_time.csv',index=False)
    # write summary json
    qB=B.quantile([.025,.5,.975]).to_dict(); summary={'logistic_bootstrap_quantiles':qB,'shape_model_bootstrap_winners':{k:int(v) for k,v in win.items()},'best_mean_curve_model':str(M.sort_values('AICc').iloc[0].model),'sentinel_all_close':bool(pd.read_csv(RES/'sentinel_stability_summary.csv').diagnostic_close.all())}
    (RES/'MECHANISTIC_MAPPING_SUMMARY.json').write_text(json.dumps(summary,indent=2))

def make_plots():
    import matplotlib.pyplot as plt
    D=pd.read_csv(RES/'dense_time_surface_summary.csv'); P=pd.read_csv(RES/'fidelity_dynamic_parameters.csv'); M=pd.read_csv(RES/'fidelity_shape_model_comparison.csv'); S=pd.read_csv(RES/'sentinel_stability_summary.csv')
    # heatmap
    piv=D.pivot(index='p',columns='t',values='DeltaV_rel')
    fig,ax=plt.subplots(figsize=(7.2,5.0)); im=ax.imshow(piv.values,aspect='auto',origin='lower',extent=[piv.columns.min(),piv.columns.max(),piv.index.min(),piv.index.max()]); ax.set_xlabel('Generation'); ax.set_ylabel('Transmission fidelity p'); cb=fig.colorbar(im,ax=ax); cb.set_label(r'$\Delta V_{rel}$'); fig.tight_layout(); fig.savefig(RES/'figures/fig_fidelity_time_surface.png',dpi=220); plt.close(fig)
    # plateau curve
    fig,ax=plt.subplots(figsize=(6.2,4.2)); ax.plot(P.p,P.A50_emp,marker='o'); ax.set_xlabel('Transmission fidelity p'); ax.set_ylabel(r'Empirical plateau $A_{50}$'); ax.axhline(0,linestyle='--',linewidth=.8); fig.tight_layout(); fig.savefig(RES/'figures/fig_plateau_vs_fidelity.png',dpi=220); plt.close(fig)
    # rate
    fig,ax=plt.subplots(figsize=(6.2,4.2)); ax.plot(P.p,P.exp_k,marker='o'); ax.set_xlabel('Transmission fidelity p'); ax.set_ylabel('Acquisition rate k (identifiable fits only)'); fig.tight_layout(); fig.savefig(RES/'figures/fig_rate_vs_fidelity.png',dpi=220); plt.close(fig)
    # onset
    fig,ax=plt.subplots(figsize=(6.4,4.3)); ax.plot(P.p,P.t50_Vrel,marker='o',label='Relational causal value'); ax.plot(P.p,P.t50_Fit,marker='o',label='Fitness difference'); ax.set_xlabel('Transmission fidelity p'); ax.set_ylabel('Empirical t50 (generation)'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(RES/'figures/fig_t50_rel_vs_fitness.png',dpi=220); plt.close(fig)
    # sentinel
    fig,ax=plt.subplots(figsize=(6.2,4.2)); ax.plot(S.p,S.A50_mean,marker='o',label='A50'); ax.plot(S.p,S.A200_mean,marker='o',label='A200'); ax.set_xlabel('Transmission fidelity p'); ax.set_ylabel(r'$\Delta V_{rel}$ plateau'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(RES/'figures/fig_sentinel_50_vs_200.png',dpi=220); plt.close(fig)
    # history dynamics
    H=pd.read_csv(RES/'history_specificity_by_time.csv').groupby('t',as_index=False)[['match_fit_adv','match_DeltaV_adv']].mean(); fig,ax=plt.subplots(figsize=(6.2,4.2)); ax.plot(H.t,H.match_fit_adv,marker='o',label='Matching-history fitness advantage'); ax.plot(H.t,H.match_DeltaV_adv,marker='o',label='Matching-history relational advantage'); ax.axhline(0,linestyle='--',linewidth=.8); ax.set_xlabel('Generation'); ax.set_ylabel('Matching-history advantage'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(RES/'figures/fig_history_specificity_dynamics.png',dpi=220); plt.close(fig)
    # expression and anisotropy contrast dynamics
    E=pd.read_csv(RES/'expression_separation_contrast_by_time.csv').groupby('t',as_index=False).expression_C4.mean(); A=pd.read_csv(RES/'anisotropy_contrast_by_time.csv').groupby('t',as_index=False).anisotropy_C5.mean(); fig,ax=plt.subplots(figsize=(6.2,4.2)); ax.plot(E.t,E.expression_C4,marker='o',label='Acquisition-expression separation'); ax.plot(A.t,A.anisotropy_C5,marker='o',label='Equal-distance anisotropy'); ax.axhline(0,linestyle='--',linewidth=.8); ax.set_xlabel('Generation'); ax.set_ylabel('Frozen-signature contrast'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(RES/'figures/fig_higher_order_signature_dynamics.png',dpi=220); plt.close(fig)

if __name__=='__main__':
    RES.mkdir(exist_ok=True); STATES.mkdir(exist_ok=True)
    with ProcessPoolExecutor(max_workers=8) as ex: chunks=list(ex.map(run_block,range(CFG['n_blocks'])))
    dense=[r for c in chunks for r in c[0]]; sites=[r for c in chunks for r in c[1]]; sent=[r for c in chunks for r in c[2]]; hx=[r for c in chunks for r in c[3]]; hs=[r for c in chunks for r in c[4]]; expr=[r for c in chunks for r in c[5]]; ani=[r for c in chunks for r in c[6]]
    cols=['block','p','t','fit_S','fit_N','DeltaF','Vrel_S','Vrel_N','DeltaV_rel','neighbor_S','heterozygosity_S','task_projection_S','scaffold_projection_S','neighbor_N','heterozygosity_N','task_projection_N','scaffold_projection_N']
    pd.DataFrame(dense,columns=cols).to_csv(RES/'dense_time_surface.csv',index=False)
    pd.DataFrame(sites,columns=['block','p','t','treatment','site','xbar']).to_csv(RES/'site_means.csv',index=False)
    pd.DataFrame(sent,columns=cols).to_csv(RES/'sentinel_time_series.csv',index=False)
    pd.DataFrame(hx,columns=['block','t','history','probe','theta_hist','theta_probe','fit_S','fit_N','DeltaF','Vrel_S','Vrel_N','DeltaV_rel']).to_csv(RES/'history_cross_eval_by_time.csv',index=False)
    pd.DataFrame(hs,columns=['block','t','match_fit_adv','match_DeltaV_adv']).to_csv(RES/'history_specificity_by_time.csv',index=False)
    pd.DataFrame(expr,columns=['block','t','alpha','fit_S','fit_N','DeltaF','Vrel_S','Vrel_N','DeltaV_rel']).to_csv(RES/'expression_by_time.csv',index=False)
    pd.DataFrame(ani,columns=['block','t','phi','radius','fit_S','fit_N','DeltaF','Vrel_S','Vrel_N','DeltaV_rel']).to_csv(RES/'anisotropy_by_time.csv',index=False)
    analyze(); make_plots()
    print((RES/'MECHANISTIC_MAPPING_SUMMARY.json').read_text())
