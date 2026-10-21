from __future__ import annotations
import glob,json,sys,hashlib
from pathlib import Path
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; sys.path.insert(0,str(HERE))
from strength_stats import bootstrap_ci,sign_test,holm
RIDS=['R0P0', 'R0P25', 'R0P5', 'R0P75', 'R1P0', 'R1P25', 'R1P5', 'R1P666667', 'R2P0', 'R2P25', 'R2P5', 'R2P75', 'R3P0', 'R3P333333', 'R3P5', 'R3P75', 'R4P0', 'R4P25', 'R4P5', 'R5P0', 'R6P0', 'R8P0']
RATIOS={'R0P0': 0.0, 'R0P25': 0.25, 'R0P5': 0.5, 'R0P75': 0.75, 'R1P0': 1.0, 'R1P25': 1.25, 'R1P5': 1.5, 'R1P666667': 1.666667, 'R2P0': 2.0, 'R2P25': 2.25, 'R2P5': 2.5, 'R2P75': 2.75, 'R3P0': 3.0, 'R3P333333': 3.333333, 'R3P5': 3.5, 'R3P75': 3.75, 'R4P0': 4.0, 'R4P25': 4.25, 'R4P5': 4.5, 'R5P0': 5.0, 'R6P0': 6.0, 'R8P0': 8.0}
V=['R1P5','R2P5','R3P0','R3P5','R4P0']; H=['R3P0','R3P5','R4P0']; L=['R0P0','R1P5']

def load_pairs():
    rows=[json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(ROOT/'raw'/'endpoints'/'DSTR_B*_R*_PAIR.json')))]
    df=pd.DataFrame(rows)
    if len(df)!=660 or df[['block_id','ratio_id']].drop_duplicates().shape[0]!=660: raise RuntimeError('pair table incomplete')
    return df.sort_values(['block_id','beta_over_theta']).reset_index(drop=True)

def block_contrasts(df):
    p=df.pivot(index='block_id',columns='ratio_id')
    get=lambda col,r:p[col][r].to_numpy(float)
    o={}
    o['A1']=get('F0','R0P0')-get('F0','R2P5'); o['A2']=get('F0','R2P5')-get('F0','R4P0')
    o['F1']=np.mean([get('DeltaF',r) for r in V],axis=0); o['F2']=get('DeltaF','R3P0')-get('DeltaF','R4P5')
    o['C1']=np.mean([get('DeltaC_train',r) for r in H],axis=0)-np.mean([get('DeltaC_train',r) for r in L],axis=0)
    o['C2']=np.mean([get('DeltaC_train',r) for r in H],axis=0)-get('DeltaC_train','R4P5')
    o['C3']=get('DeltaC_probe3','R4P0')-get('DeltaC_train','R4P0'); o['C4']=get('DeltaC_probe3','R4P0')-get('DeltaC_probe3','R4P5')
    o['R1']=np.mean([get('DeltaR_train',r) for r in H],axis=0)-np.mean([get('DeltaR_train',r) for r in L],axis=0)
    o['R2']=np.mean([get('DeltaR_train',r) for r in H],axis=0)-get('DeltaR_train','R4P5')
    o['R3']=get('DeltaR_probe3','R4P0')-get('DeltaR_train','R4P0'); o['R4']=get('DeltaR_probe3','R4P0')-get('DeltaR_probe3','R4P5')
    return pd.DataFrame(o,index=p.index).reset_index()

def formal_results(bc):
    fam={'A_COST':['A1','A2'],'F_RECOVERY':['F1','F2'],'C_DOWN':['C1','C2','C3','C4'],'R_SPEC':['R1','R2','R3','R4']}
    rows=[]
    for family,ids in fam.items():
        ci=.975 if len(ids)==2 else .9875
        tmp=[]
        for cid in ids:
            v=bc[cid].to_numpy(float); b=bootstrap_ci(v,ci,50000,f'{family}-{cid}'); s=sign_test(v); tmp.append((cid,b,s))
        adj=holm([x[2]['p_value'] for x in tmp])
        for (cid,b,s),pa in zip(tmp,adj):
            passed=bool(b['mean']>0 and b['low']>0 and pa<.05)
            rows.append({'family':family,'contrast_id':cid,'n_blocks':30,'mean':b['mean'],'median':b['median'],'ci_level':b['ci'],'ci_low':b['low'],'ci_high':b['high'],'positive_blocks':s['positive'],'nonpositive_blocks':s['nonpositive'],'sign_p_raw':s['p_value'],'sign_p_holm':float(pa),'pass':passed})
    return pd.DataFrame(rows)

def ratio_summary(df):
    metrics=['F0','F250_selected','F250_neutral','G_selected','G_neutral','DeltaF','C_train_selected','C_train_neutral','DeltaC_train','C_probe3_selected','C_probe3_neutral','DeltaC_probe3','R_train_selected','R_train_neutral','DeltaR_train','R_probe3_selected','R_probe3_neutral','DeltaR_probe3']
    rows=[]
    for rid in RIDS:
        g=df[df.ratio_id==rid]; row={'ratio_id':rid,'beta_over_theta':RATIOS[rid],'beta':float(g.beta.iloc[0]),'n_blocks':len(g)}
        for m in metrics:
            b=bootstrap_ci(g[m].to_numpy(float),.95,50000,f'ratio-{rid}-{m}'); row[f'{m}_mean']=b['mean']; row[f'{m}_ci95_lo']=b['low']; row[f'{m}_ci95_hi']=b['high']
        rows.append(row)
    return pd.DataFrame(rows)

def main():
    out=ROOT/'analysis'; out.mkdir(exist_ok=True)
    df=load_pairs(); df.to_csv(out/'PAIRED_RATIO_ENDPOINTS_v1.0.0.csv',index=False)
    # integrity checks
    f0_ident=np.max(np.abs(df['F0']-(df['F250_selected']-df['G_selected'])))<1e-12 and np.max(np.abs(df['F0']-(df['F250_neutral']-df['G_neutral'])))<1e-12
    delta_ident=np.max(np.abs(df['DeltaF']-(df['G_selected']-df['G_neutral'])))<1e-12
    block_anc=df.groupby('block_id').ancestor_hash.nunique(); ancestors_ok=bool((block_anc==1).all())
    bc=block_contrasts(df); bc.to_csv(out/'BLOCK_CONTRASTS_v1.0.0.csv',index=False)
    fr=formal_results(bc); fr.to_csv(out/'FORMAL_CONTRAST_RESULTS_v1.0.0.csv',index=False)
    rs=ratio_summary(df); rs.to_csv(out/'RATIO_SUMMARY_v1.0.0.csv',index=False)
    family_pass={fam:bool(g['pass'].all()) for fam,g in fr.groupby('family')}
    viable_positive=bool((rs[rs.ratio_id.isin(V)]['DeltaF_mean']>0).all())
    family_pass['F_RECOVERY']=family_pass['F_RECOVERY'] and viable_positive
    collapse_row=rs[rs.ratio_id=='R4P5'].iloc[0]; floor_gate=bool(collapse_row.F250_selected_mean<=.20 and collapse_row.F250_neutral_mean<=.20)
    strong=bool(all(family_pass.get(k,False) for k in ['A_COST','F_RECOVERY','C_DOWN','R_SPEC']))
    if strong: classification='STRONG PROSPECTIVE SUPPORT'
    elif family_pass['A_COST'] and family_pass['F_RECOVERY'] and not family_pass['C_DOWN']: classification='N1 NARROW SUPPORT'
    elif family_pass['A_COST'] and family_pass['F_RECOVERY'] and family_pass['C_DOWN'] and not family_pass['R_SPEC']: classification='N2 NARROW SUPPORT'
    else: classification='NO FULL SUPPORT'
    cpass={r.contrast_id:bool(r['pass']) for _,r in fr.iterrows()}
    latent_sep=bool(cpass.get('C3',False) and cpass.get('R3',False)); rise_collapse=bool(all(cpass.get(x,False) for x in ['C1','C2','C4','R1','R2','R4']))
    summary={'classification':classification,'overall_strong_support':strong,'family_pass':family_pass,'all_viable_ratio_DeltaF_means_positive':viable_positive,'collapse_floor_gate_pass':floor_gate,'latent_exceeds_expression_confirmed':latent_sep,'rise_collapse_core_confirmed':rise_collapse,'integrity':{'f0_arithmetic':f0_ident,'deltaF_identity':delta_ident,'shared_ancestor_within_block':ancestors_ok,'n_pairs':len(df),'n_strengths':df.ratio_id.nunique(),'n_blocks':df.block_id.nunique()},'formal_contrasts':fr.to_dict(orient='records')}
    (out/'CONFIRMATORY_RESULT_SUMMARY_v1.0.0.json').write_text(json.dumps(summary,indent=2,sort_keys=True,default=lambda o: o.item() if hasattr(o,'item') else str(o))+'\n')
    # concise report
    def fmt(cid):
        r=fr[fr.contrast_id==cid].iloc[0]; return f"{cid}: mean={r['mean']:.6g}, {100*r['ci_level']:.2f}% CI [{r['ci_low']:.6g}, {r['ci_high']:.6g}], positive blocks={int(r['positive_blocks'])}/30, Holm p={r['sign_p_holm']:.3g}, {'PASS' if r['pass'] else 'FAIL'}"
    lines=['# Dense Scaffold-Strength Confirmatory Results v1.0.0','',f'**Frozen classification: {classification}**','',f'Completed 30 independent root-seed blocks across the exact 22-point grid (660 selected-neutral pairs; 1320 evolutionary runs). The root-seed block is the inferential unit.','', '## Formal frozen contrasts','']
    for fam,ids in [('A_COST',['A1','A2']),('F_RECOVERY',['F1','F2']),('C_DOWN',['C1','C2','C3','C4']),('R_SPEC',['R1','R2','R3','R4'])]:
        lines += [f'### {fam}',*['- '+fmt(x) for x in ids],'']
    lines += ['## Endpoint means by scaffold strength','', '| beta/Theta | F0 | G selected | G neutral | DeltaF | DeltaC train | DeltaC beta=3 | DeltaR train | DeltaR beta=3 |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in rs.iterrows(): lines.append(f"| {r.beta_over_theta:.1f} | {r.F0_mean:.3f} | {r.G_selected_mean:.3f} | {r.G_neutral_mean:.3f} | {r.DeltaF_mean:.3f} | {r.DeltaC_train_mean:.6f} | {r.DeltaC_probe3_mean:.6f} | {r.DeltaR_train_mean:.3f} | {r.DeltaR_probe3_mean:.3f} |")
    lines += ['', '## Frozen success gates','',f"- A_COST: {'PASS' if family_pass['A_COST'] else 'FAIL'}",f"- F_RECOVERY: {'PASS' if family_pass['F_RECOVERY'] else 'FAIL'}",f"- C_DOWN-strong: {'PASS' if family_pass['C_DOWN'] else 'FAIL'}",f"- R_SPEC-strong: {'PASS' if family_pass['R_SPEC'] else 'FAIL'}",f"- all five viable-window DeltaF means positive: {'PASS' if viable_positive else 'FAIL'}",f"- r=4.5 canonical fitness-floor gate: {'PASS' if floor_gate else 'FAIL'} (selected mean={collapse_row.F250_selected_mean:.6f}; neutral mean={collapse_row.F250_neutral_mean:.6f})",'', '## Interpretation boundary','']
    if strong:
        wording='Within the tested canonical Model B domain, increasing externally imposed scaffold strength imposed a progressively larger ancestral fitness cost, while selection generated a broad regime of adaptive recovery, downward causal constraint, and historical scaffold specificity. At high but still viable strength, standardized moderate probing revealed more latent organization than was expressed under the training field, whereas these selection-dependent effects disappeared beyond the viable canonical-fitness regime.'
        if floor_gate: wording += ' The prespecified r=4.5 anchor satisfied the canonical fitness-floor criterion.'
        lines += [wording,'']
    lines += ['This result does not establish full Walker-Davies information-flow reversal, scaffold endogenization, top-down dominance, or autonomous agency. The scaffold remains externally supplied.']
    (out/'CONFIRMATORY_RESULTS_v1.0.0.md').write_text('\n'.join(lines)+'\n')
    (out/'GATE_DECISION_v1.0.0.md').write_text(f"# Dense Scaffold-Strength Gate Decision v1.0.0\n\n**Decision: {classification}**\n\nAll frozen family gates: {json.dumps(family_pass,sort_keys=True)}\n\nFitness-floor wording gate: {'PASS' if floor_gate else 'FAIL'}.\n")
    print(json.dumps({'classification':classification,'family_pass':family_pass,'floor_gate':floor_gate,'viable_positive':viable_positive},indent=2))
if __name__=='__main__': main()
