import numpy as np, pandas as pd, json, hashlib
from itertools import combinations_with_replacement
from pathlib import Path
from scipy.stats import binomtest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'; OUT.mkdir(parents=True,exist_ok=True)
CFG=json.loads((ROOT/'control/CONFIG_v1.0.0.json').read_text())
PVALS=CFG['p_values']; NB=CFG['n_root_blocks']; ROOT0=CFG['root_seed_base']
M=4; R=4; PAIRS=list(combinations_with_replacement(range(M),2)); D=len(PAIRS)
N=CFG['n_dimers_per_cell']; POP=CFG['population']; GENS=CFG['generations']; MU=CFG['mutation_probability']; SEL=CFG['selection_coefficient']; K=CFG['michaelis_K']; S=CFG['scaffold_strength']; ASEED=CFG['affinity_seed']
UNIF=np.ones(D)/D
rng=np.random.default_rng(ASEED); A=np.exp(.9*rng.normal(size=(D,R)))
for _ in range(2000):
    A*=(R/A.sum(1))[:,None]; A*=(D/A.sum(0))[None,:]
basis=[]
for raw in [np.array([1.,-1,0,0]),np.array([1.,1.,-2,0]),np.array([1.,1.,1.,-3])]:
    v=raw.copy()
    for u in basis: v-=u*np.dot(u,v)
    v/=np.linalg.norm(v); basis.append(v)
hist=basis[0]
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
    p=np.asarray(p,float); q=np.asarray(q,float); p=p/p.sum(); q=q/q.sum(); m=.5*(p+q)
    def kl(a,b):
        z=a>0; return np.sum(a[z]*np.log2(a[z]/b[z]))
    return .5*kl(p,m)+.5*kl(q,m)

def chem(f,b,s):
    cat=f@A; u=np.exp(s*np.asarray(b))*cat; v=u/(K+u); q=v/v.sum(); fit=R/np.sum(1/np.clip(v,1e-12,None)); return q,fit

def fitcells(st,b,s):
    f=st/st.sum(1,keepdims=True); cat=f@A; u=np.exp(s*np.asarray(b))[None,:]*cat; v=u/(K+u); return R/np.sum(1/np.clip(v,1e-12,None),axis=1)

def metrics(st,b,s):
    f=st.sum(0)/st.sum(); fe=erase(f); qi,fi=chem(f,b,s); qe,fer=chem(fe,b,s)
    return {'fitness':float(fitcells(st,b,s).mean()),'R_pop':float(jsd(f,fe)),'C_pop':float(jsd(qi,qe)),'V_rel':float(fi-fer)}

def founder(seed):
    r=np.random.default_rng(seed); return np.stack([r.multinomial(N,UNIF) for _ in range(POP)])

def evolve(st,p,selected,seed):
    r=np.random.default_rng(seed); st=st.copy()
    for _ in range(GENS):
        ft=fitcells(st,hist,S)
        if selected:
            z=SEL*(ft-ft.mean()); z-=z.max(); w=np.exp(z); w/=w.sum(); pars=r.choice(POP,POP,p=w)
        else:
            pars=r.integers(0,POP,POP)
        new=np.empty_like(st)
        for o,pa in enumerate(pars):
            pr=(p*(st[pa]/N)+(1-p)*UNIF)@MUT; pr/=pr.sum(); new[o]=r.multinomial(N,pr)
        st=new
    return st

def bootstrap_ci(x,nboot=50000,seed=781245901,alpha=1/60):
    x=np.asarray(x,float); r=np.random.default_rng(seed); n=len(x)
    vals=np.empty(nboot)
    chunk=5000
    for i in range(0,nboot,chunk):
        m=min(chunk,nboot-i); idx=r.integers(0,n,size=(m,n)); vals[i:i+m]=x[idx].mean(axis=1)
    return np.quantile(vals,[alpha/2,1-alpha/2])

def holm(ps):
    ps=np.asarray(ps,float); order=np.argsort(ps); adj=np.empty_like(ps); running=0.0; m=len(ps)
    for rank,idx in enumerate(order):
        val=(m-rank)*ps[idx]; running=max(running,val); adj[idx]=min(1.0,running)
    return adj

# Production
rows=[]
for b in range(NB):
    f=founder(ROOT0+b)
    for i,p in enumerate(PVALS):
        ss=ROOT0+100000+i*1000+b; ns=ROOT0+200000+i*1000+b
        sel=evolve(f,p,True,ss); neu=evolve(f,p,False,ns)
        ms=metrics(sel,hist,S); mn=metrics(neu,hist,S)
        rec={'block':b,'p_index':i,'p':p,'founder_seed':ROOT0+b,'selected_seed':ss,'neutral_seed':ns}
        for k in ['fitness','R_pop','C_pop','V_rel']:
            rec[k+'_selected']=ms[k]; rec[k+'_neutral']=mn[k]; rec['Delta_'+k]=ms[k]-mn[k]
        rows.append(rec)
df=pd.DataFrame(rows); df.to_csv(OUT/'FIDELITY_ENDPOINTS_v1.0.0.csv',index=False)
summary=df.groupby('p',as_index=False).agg(
    Delta_R_pop_mean=('Delta_R_pop','mean'),Delta_R_pop_sem=('Delta_R_pop','sem'),
    Delta_V_rel_mean=('Delta_V_rel','mean'),Delta_V_rel_sem=('Delta_V_rel','sem'),
    Delta_fitness_mean=('Delta_fitness','mean'),Delta_fitness_sem=('Delta_fitness','sem'),
    Delta_C_pop_mean=('Delta_C_pop','mean'),Delta_C_pop_sem=('Delta_C_pop','sem'))
summary.to_csv(OUT/'FIDELITY_SUMMARY_v1.0.0.csv',index=False)

# Per-block formal contrasts
lo=[0,.1,.2,.3,.4,.5,.6]; hi=[.9,.925,.95,.975,1.0]; trans=[.85,.875,.9]; vhi=[.95,.975,1.0]
block_rows=[]
for b,g in df.groupby('block'):
    def m(col,vals): return g[g.p.isin(vals)][col].mean()
    def at(col,p): return g[np.isclose(g.p,p)][col].iloc[0]
    block_rows.append({'block':b,
      'R1':m('Delta_R_pop',hi)-m('Delta_R_pop',lo),
      'R2':m('Delta_R_pop',vhi)-m('Delta_R_pop',trans),
      'R3':at('Delta_R_pop',.975),
      'V1':m('Delta_V_rel',hi)-m('Delta_V_rel',lo),
      'V2':m('Delta_V_rel',vhi)-m('Delta_V_rel',trans),
      'V3':at('Delta_V_rel',.975)})
bc=pd.DataFrame(block_rows); bc.to_csv(OUT/'BLOCK_CONTRASTS_v1.0.0.csv',index=False)
formal=[]
for fam,ids in [('R_POP',['R1','R2','R3']),('V_REL',['V1','V2','V3'])]:
    raw=[]; temp=[]
    for j,cid in enumerate(ids):
        x=bc[cid].values; pos=int((x>0).sum()); pr=float(binomtest(pos,len(x),.5,alternative='greater').pvalue); raw.append(pr)
        lo_ci,hi_ci=bootstrap_ci(x,CFG['bootstrap_replicates'],CFG['bootstrap_seed']+100*j+(0 if fam=='R_POP' else 1000))
        temp.append({'family':fam,'contrast_id':cid,'n_blocks':len(x),'mean':float(x.mean()),'median':float(np.median(x)),'ci_level':0.9833333333333333,'ci_low':float(lo_ci),'ci_high':float(hi_ci),'positive_blocks':pos,'nonpositive_blocks':int(len(x)-pos),'sign_p_raw':pr})
    adj=holm(raw)
    for rec,pa in zip(temp,adj):
        rec['sign_p_holm']=float(pa); rec['pass']=bool(rec['mean']>0 and rec['ci_low']>0 and pa<.05); formal.append(rec)
fr=pd.DataFrame(formal); fr.to_csv(OUT/'FORMAL_CONTRAST_RESULTS_v1.0.0.csv',index=False)
means=summary.set_index('p')
high_pts=[.9,.925,.95,.975,1.0]
high_R=bool((means.loc[high_pts,'Delta_R_pop_mean']>0).all())
high_V=bool((means.loc[high_pts,'Delta_V_rel_mean']>0).all())
rpass=bool(fr[fr.family.eq('R_POP')]['pass'].all() and high_R)
vpass=bool(fr[fr.family.eq('V_REL')]['pass'].all() and high_V)
strong=bool(rpass and vpass)
res={'classification':'STRONG PROSPECTIVE SUPPORT' if strong else ('PARTIAL PROSPECTIVE SUPPORT' if rpass or vpass else 'NO STRONG PROSPECTIVE SUPPORT'),
     'R_POP_strong':rpass,'V_REL_strong':vpass,'overall_strong_support':strong,
     'high_fidelity_means_positive':{'R_POP':high_R,'V_REL':high_V},
     'integrity':{'n_pairs':int(len(df)),'n_blocks':int(df.block.nunique()),'n_runs':int(2*len(df)),'shared_founder_across_p_within_block':True},
     'formal_contrasts':fr.to_dict(orient='records')}
(OUT/'CONFIRMATORY_RESULT_SUMMARY_v1.0.0.json').write_text(json.dumps(res,indent=2))
lines=['# Catalytic-Complex Transmission-Fidelity Confirmatory Results v1.0.0','',f"**Frozen classification: {res['classification']}**",'',f"Completed {NB} independent root-seed blocks across the frozen 18-point fidelity grid ({len(df)} selected-neutral pairs; {2*len(df)} evolutionary runs). The root-seed block is the inferential unit.",'','## Formal frozen contrasts','']
for fam in ['R_POP','V_REL']:
    lines += [f'### {fam}']
    for _,r in fr[fr.family.eq(fam)].iterrows():
        lines += [f"- {r.contrast_id}: mean={r['mean']:.8g}, 98.333% CI [{r['ci_low']:.8g}, {r['ci_high']:.8g}], positive blocks={int(r['positive_blocks'])}/30, Holm p={r['sign_p_holm']:.3g}, {'PASS' if r['pass'] else 'FAIL'}"]
    lines += ['']
lines += ['## Dense endpoint means','', '| p | DeltaR_pop (bits) | DeltaV_rel | DeltaFitness | DeltaC_pop (bits) |','|---:|---:|---:|---:|---:|']
for _,r in summary.iterrows(): lines.append(f"| {r.p:.3f} | {r.Delta_R_pop_mean:.7f} | {r.Delta_V_rel_mean:.7f} | {r.Delta_fitness_mean:.7f} | {r.Delta_C_pop_mean:.7f} |")
lines += ['','## Frozen success gates','',f"- R_POP-strong: {'PASS' if rpass else 'FAIL'}",f"- V_REL-strong: {'PASS' if vpass else 'FAIL'}",f"- all five high-fidelity DeltaR_pop means positive: {'PASS' if high_R else 'FAIL'}",f"- all five high-fidelity DeltaV_rel means positive: {'PASS' if high_V else 'FAIL'}",f"- all 1080 evolutionary runs complete: {'PASS' if len(df)==540 else 'FAIL'}",'','## Interpretation boundary','']
if strong:
    lines += ['Within the tested catalytic-complex domain, selection-generated relational organization and its relation-specific adaptive value were strongly concentrated in the high-transmission-fidelity regime and strengthened further toward very high fidelity. Together with the independent Model B fidelity confirmation, heredity dependence is prospectively replicated across the two microscopic realizations.','']
else:
    lines += ['Use only the endpoint-specific or narrow-support wording permitted by the frozen prospective plan. Do not claim symmetric cross-realization confirmation unless both primary families pass.','']
lines += ['The discrete 18-point curve does not establish a continuously estimated critical fidelity, universality, scaffold endogenization, autonomous agency, or full Walker-Davies reversal.','']
(OUT/'CONFIRMATORY_RESULTS_v1.0.0.md').write_text('\n'.join(lines))
print(json.dumps(res,indent=2))
