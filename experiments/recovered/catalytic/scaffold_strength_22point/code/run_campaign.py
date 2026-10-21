import argparse, hashlib, json, math, os
from itertools import combinations_with_replacement
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT=Path(__file__).resolve().parents[1]
CFG=json.load(open(ROOT/'control/CONFIG_v1.0.0.json'))
STRENGTHS=np.array(CFG['scaffold_strengths'],dtype=float)
M=4; R=4; PAIRS=list(combinations_with_replacement(range(M),2)); D=len(PAIRS)
N=CFG['dimers_per_cell']; POP=CFG['population_size']; GENS=CFG['generations']; MU=CFG['mutation_probability']; SEL=CFG['selection_coefficient']; K=CFG['michaelis_K']; P=CFG['transmission_fidelity']; ASEED=CFG['affinity_seed']
UNIF=np.ones(D)/D
CAMPAIGN=CFG['campaign']

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

def seed128(tag):
    # campaign-namespaced deterministic 128-bit entropy, distinct by derivation tag
    h=hashlib.sha256((CAMPAIGN+'|'+tag).encode()).digest()
    return int.from_bytes(h[:16],'big') | (1<<127)

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

def chem(f,s):
    cat=f@A; u=np.exp(s*hist)*cat; v=u/(K+u); q=v/v.sum(); fit=R/np.sum(1/np.clip(v,1e-12,None)); return q,fit

def fitcells(st,s):
    f=st/st.sum(1,keepdims=True); cat=f@A; u=np.exp(s*hist)[None,:]*cat; v=u/(K+u); return R/np.sum(1/np.clip(v,1e-12,None),axis=1)

def metrics(st,s):
    f=st.sum(0)/st.sum(); fe=erase(f); qi,fi=chem(f,s); qe,fer=chem(fe,s)
    return {'fitness':float(fitcells(st,s).mean()),'R_pop':float(jsd(f,fe)),'C_pop':float(jsd(qi,qe)),'V_rel':float(fi-fer)}

def founder(seed):
    r=np.random.default_rng(seed); return np.stack([r.multinomial(N,UNIF) for _ in range(POP)])

def evolve(st,selected,seed,s):
    r=np.random.default_rng(seed); st=st.copy()
    for _ in range(GENS):
        ft=fitcells(st,s)
        if selected:
            z=SEL*(ft-ft.mean()); z-=z.max(); w=np.exp(z); w/=w.sum(); pars=r.choice(POP,POP,p=w)
        else:
            pars=r.integers(0,POP,POP)
        new=np.empty_like(st)
        for o,pa in enumerate(pars):
            pr=(P*(st[pa]/N)+(1-P)*UNIF)@MUT; pr/=pr.sum(); new[o]=r.multinomial(N,pr)
        st=new
    return st

def run_block(block):
    fseed=seed128(f'block{block:02d}|founder')
    f=founder(fseed)
    rows=[]; sels=[]; neus=[]
    for j,s in enumerate(STRENGTHS):
        m0=metrics(f,s)
        ss=seed128(f'block{block:02d}|strength{j:02d}|selected')
        ns=seed128(f'block{block:02d}|strength{j:02d}|neutral')
        sel=evolve(f,True,ss,float(s)); neu=evolve(f,False,ns,float(s))
        ms=metrics(sel,float(s)); mn=metrics(neu,float(s))
        row={'block':block,'strength_index':j,'scaffold_strength':float(s),'founder_seed_128':str(fseed),'selected_seed_128':str(ss),'neutral_seed_128':str(ns)}
        for k,v in m0.items(): row[f'{k}_ancestor']=v
        for k,v in ms.items(): row[f'{k}_selected']=v
        for k,v in mn.items(): row[f'{k}_neutral']=v
        row['selected_minus_ancestor']=ms['fitness']-m0['fitness']
        row['neutral_minus_ancestor']=mn['fitness']-m0['fitness']
        row['selected_minus_neutral']=ms['fitness']-mn['fitness']
        row['Delta_R_pop']=ms['R_pop']-mn['R_pop']
        row['Delta_C_pop']=ms['C_pop']-mn['C_pop']
        row['Delta_V_rel']=ms['V_rel']-mn['V_rel']
        rows.append(row); sels.append(sel); neus.append(neu)
    return block,rows,np.stack(sels),np.stack(neus),f

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--workers',type=int,default=min(12,os.cpu_count() or 1)); args=ap.parse_args()
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    allrows=[]; selected=np.empty((CFG['n_blocks'],len(STRENGTHS),POP,D),dtype=np.int16); neutral=np.empty_like(selected); founders=np.empty((CFG['n_blocks'],POP,D),dtype=np.int16)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs={ex.submit(run_block,b):b for b in range(CFG['n_blocks'])}
        for fut in as_completed(futs):
            b,rows,sels,neus,f=fut.result(); allrows.extend(rows); selected[b]=sels; neutral[b]=neus; founders[b]=f
            print(f'completed block {b}',flush=True)
    df=pd.DataFrame(allrows).sort_values(['block','strength_index']).reset_index(drop=True)
    df.to_csv(out/'BLOCK_STRENGTH_RESULTS.csv',index=False)
    np.savez_compressed(out/'ENDPOINT_STATES.npz',selected=selected,neutral=neutral,founders=founders,strengths=STRENGTHS)
    # exact seed ledger from generated rows
    df[['block','strength_index','scaffold_strength','founder_seed_128','selected_seed_128','neutral_seed_128']].to_csv(out/'EXECUTED_SEED_LEDGER.csv',index=False)
    print('production complete',len(df),'block-strength rows')
if __name__=='__main__': main()
