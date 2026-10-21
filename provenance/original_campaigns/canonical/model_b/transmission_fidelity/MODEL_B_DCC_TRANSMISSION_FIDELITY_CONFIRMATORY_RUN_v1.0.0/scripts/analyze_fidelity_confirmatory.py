from __future__ import annotations
import glob,json,sys,hashlib
from pathlib import Path
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; sys.path.insert(0,str(HERE))
from fidelity_stats import bootstrap_ci,sign_test,holm
PIDS=['P0000','P0100','P0200','P0300','P0400','P0500','P0600','P0700','P0750','P0800','P0825','P0850','P0875','P0900','P0925','P0950','P0975','P1000']
PVAL={'P0000':0.0,'P0100':0.1,'P0200':0.2,'P0300':0.3,'P0400':0.4,'P0500':0.5,'P0600':0.6,'P0700':0.7,'P0750':0.75,'P0800':0.8,'P0825':0.825,'P0850':0.85,'P0875':0.875,'P0900':0.9,'P0925':0.925,'P0950':0.95,'P0975':0.975,'P1000':1.0}
LOW=['P0000','P0100','P0200','P0300','P0400','P0500','P0600']; HIGH=['P0900','P0925','P0950','P0975','P1000']; TRANS=['P0850','P0875','P0900']; VERY=['P0950','P0975','P1000']

def load_pairs():
    rows=[json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(ROOT/'raw'/'endpoints'/'FID_B*_P*_PAIR.json')))]
    df=pd.DataFrame(rows)
    if len(df)!=540 or df[['block_id','p_id']].drop_duplicates().shape[0]!=540: raise RuntimeError(f'pair table incomplete {len(df)}')
    return df.sort_values(['block_id','p_inherit']).reset_index(drop=True)

def block_contrasts(df):
    p=df.pivot(index='block_id',columns='p_id'); get=lambda col,r:p[col][r].to_numpy(float)
    o={}
    o['C1']=np.mean([get('DeltaC_down',r) for r in HIGH],axis=0)-np.mean([get('DeltaC_down',r) for r in LOW],axis=0)
    o['C2']=np.mean([get('DeltaC_down',r) for r in VERY],axis=0)-np.mean([get('DeltaC_down',r) for r in TRANS],axis=0)
    o['C3']=get('DeltaC_down','P0975')
    o['R1']=np.mean([get('DeltaR',r) for r in HIGH],axis=0)-np.mean([get('DeltaR',r) for r in LOW],axis=0)
    o['R2']=np.mean([get('DeltaR',r) for r in VERY],axis=0)-np.mean([get('DeltaR',r) for r in TRANS],axis=0)
    o['R3']=get('DeltaR','P0975')
    return pd.DataFrame(o,index=p.index).reset_index()

def formal_results(bc):
    fam={'C_DOWN':['C1','C2','C3'],'R_SPEC':['R1','R2','R3']}; rows=[]
    for family,ids in fam.items():
        tmp=[]
        for cid in ids:
            v=bc[cid].to_numpy(float); b=bootstrap_ci(v,.98333,50000,f'{family}-{cid}'); s=sign_test(v); tmp.append((cid,b,s))
        adj=holm([x[2]['p_value'] for x in tmp])
        for (cid,b,s),pa in zip(tmp,adj):
            passed=bool(b['mean']>0 and b['low']>0 and pa<.05)
            rows.append({'family':family,'contrast_id':cid,'n_blocks':30,'mean':b['mean'],'median':b['median'],'ci_level':b['ci'],'ci_low':b['low'],'ci_high':b['high'],'positive_blocks':s['positive'],'nonpositive_blocks':s['nonpositive'],'sign_p_raw':s['p_value'],'sign_p_holm':float(pa),'pass':passed})
    return pd.DataFrame(rows)

def ratio_summary(df):
    metrics=['F0','F250_selected','F250_neutral','DeltaF','C_selected','C_neutral','DeltaC_down','R_selected','R_neutral','DeltaR']; rows=[]
    for pid in PIDS:
        g=df[df.p_id==pid]; row={'p_id':pid,'p_inherit':PVAL[pid],'n_blocks':len(g)}
        for m in metrics:
            b=bootstrap_ci(g[m].to_numpy(float),.95,50000,f'point-{pid}-{m}'); row[f'{m}_mean']=b['mean']; row[f'{m}_ci95_lo']=b['low']; row[f'{m}_ci95_hi']=b['high']
        rows.append(row)
    return pd.DataFrame(rows)

def main():
    out=ROOT/'analysis'; out.mkdir(exist_ok=True)
    df=load_pairs(); df.to_csv(out/'PAIRED_FIDELITY_ENDPOINTS_v1.0.0.csv',index=False)
    # integrity
    f0_spread=df.groupby('block_id').F0.agg(lambda x: float(np.max(x)-np.min(x))); ancestor_n=df.groupby('block_id').ancestor_hash.nunique()
    shared_f0=bool((f0_spread<1e-12).all()); shared_anc=bool((ancestor_n==1).all())
    bc=block_contrasts(df); bc.to_csv(out/'BLOCK_CONTRASTS_v1.0.0.csv',index=False)
    fr=formal_results(bc); fr.to_csv(out/'FORMAL_CONTRAST_RESULTS_v1.0.0.csv',index=False)
    rs=ratio_summary(df); rs.to_csv(out/'FIDELITY_SUMMARY_v1.0.0.csv',index=False)
    fam_pass={fam:bool(g['pass'].all()) for fam,g in fr.groupby('family')}
    high_c=bool((rs[rs.p_id.isin(HIGH)]['DeltaC_down_mean']>0).all()); high_r=bool((rs[rs.p_id.isin(HIGH)]['DeltaR_mean']>0).all())
    fam_pass['C_DOWN']=fam_pass.get('C_DOWN',False) and high_c; fam_pass['R_SPEC']=fam_pass.get('R_SPEC',False) and high_r
    strong=bool(fam_pass['C_DOWN'] and fam_pass['R_SPEC'])
    cp={r.contrast_id:bool(r['pass']) for _,r in fr.iterrows()}
    if strong: classification='STRONG PROSPECTIVE SUPPORT'
    elif fam_pass['C_DOWN'] and not fam_pass['R_SPEC']: classification='N1 NARROW SUPPORT — C_DOWN ONLY'
    elif fam_pass['R_SPEC'] and not fam_pass['C_DOWN']: classification='N2 NARROW SUPPORT — R_SPEC ONLY'
    elif (cp.get('C1') and cp.get('C3')) or (cp.get('R1') and cp.get('R3')): classification='N3 NARROW SUPPORT — HIGH-FIDELITY CONCENTRATION WITHOUT FULL STRENGTHENING'
    else: classification='NO FULL SUPPORT'
    summary={'classification':classification,'overall_strong_support':strong,'family_pass':fam_pass,'high_fidelity_display_means_positive':{'C_DOWN':high_c,'R_SPEC':high_r},'integrity':{'n_pairs':len(df),'n_blocks':df.block_id.nunique(),'shared_ancestor_within_block':shared_anc,'identical_F0_across_fidelities_within_block':shared_f0},'formal_contrasts':fr.to_dict(orient='records')}
    (out/'CONFIRMATORY_RESULT_SUMMARY_v1.0.0.json').write_text(json.dumps(summary,indent=2,sort_keys=True,default=lambda o:o.item() if hasattr(o,'item') else str(o))+'\n')
    def fmt(cid):
        r=fr[fr.contrast_id==cid].iloc[0]; return f"{cid}: mean={r['mean']:.6g}, {100*r['ci_level']:.3f}% CI [{r['ci_low']:.6g}, {r['ci_high']:.6g}], positive blocks={int(r['positive_blocks'])}/30, Holm p={r['sign_p_holm']:.3g}, {'PASS' if r['pass'] else 'FAIL'}"
    lines=['# Transmission-Fidelity Confirmatory Results v1.0.0','',f'**Frozen classification: {classification}**','', 'Completed 30 independent root-seed blocks across the exact frozen 18-point transmission-fidelity grid (540 selected-neutral pairs; 1080 evolutionary runs). The root-seed block is the inferential unit.','', '## Formal frozen contrasts','', '### C_DOWN', *['- '+fmt(x) for x in ['C1','C2','C3']], '', '### R_SPEC', *['- '+fmt(x) for x in ['R1','R2','R3']], '', '## Dense endpoint means', '', '| p | DeltaC_down (bits) | DeltaR (fitness units) | DeltaF (fitness units) |','|---:|---:|---:|---:|']
    for _,r in rs.iterrows(): lines.append(f"| {r.p_inherit:.3f} | {r.DeltaC_down_mean:.7f} | {r.DeltaR_mean:.4f} | {r.DeltaF_mean:.4f} |")
    lines += ['', '## Frozen success gates','',f"- C_DOWN-strong: {'PASS' if fam_pass['C_DOWN'] else 'FAIL'}",f"- R_SPEC-strong: {'PASS' if fam_pass['R_SPEC'] else 'FAIL'}",f"- all five high-fidelity DeltaC means positive: {'PASS' if high_c else 'FAIL'}",f"- all five high-fidelity DeltaR means positive: {'PASS' if high_r else 'FAIL'}",f"- shared ancestor within root block: {'PASS' if shared_anc else 'FAIL'}",f"- identical F0 across fidelity conditions within root block: {'PASS' if shared_f0 else 'FAIL'}",'', '## Interpretation boundary','']
    if strong:
        lines += ['Within the tested canonical Model B domain, selection-generated downward causal constraint and historical scaffold specificity were strongly concentrated in the high-transmission-fidelity regime and increased further toward very high fidelity. The dense 18-point curves describe the discrete regime geometry; they do not establish a continuously estimated critical fidelity.','']
    lines += ['This result does not establish full Walker-Davies information-flow reversal, scaffold endogenization, top-down dominance, or autonomous agency. The scaffold remains externally supplied.']
    (out/'CONFIRMATORY_RESULTS_v1.0.0.md').write_text('\n'.join(lines)+'\n')
    (out/'GATE_DECISION_v1.0.0.md').write_text(f"# Transmission-Fidelity Gate Decision v1.0.0\n\n**Decision: {classification}**\n\nC_DOWN-strong: {'PASS' if fam_pass['C_DOWN'] else 'FAIL'}  \nR_SPEC-strong: {'PASS' if fam_pass['R_SPEC'] else 'FAIL'}  \n\nFull promotion of Figure 4(c,d): {'AUTHORIZED' if strong else 'NOT AUTHORIZED'}.\n")
    print(json.dumps({'classification':classification,'family_pass':fam_pass,'high_c':high_c,'high_r':high_r},indent=2))
if __name__=='__main__': main()
