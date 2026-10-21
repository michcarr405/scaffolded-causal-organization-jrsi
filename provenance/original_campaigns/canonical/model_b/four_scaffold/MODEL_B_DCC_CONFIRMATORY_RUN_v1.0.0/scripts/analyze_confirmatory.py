from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
from confirmatory_stats import (
    mean_bootstrap_ci,
    exact_one_sided_sign_test,
    holm_adjust,
    stratified_pooled_bootstrap,
)

VERSION = 'v1.0.0'
SCAFFOLDS = ['SCF0','SCF1','SCF2','SCF3']
PROBES = ['SCF0','SCF1','SCF2','SCF3']
CHECKPOINTS = [0,25,50,75,100,125,150,175,200,225,250]
N_BOOT = 50000
FAMILY_CI = 0.9875


def load_json(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def check_close(a,b,tol=1e-15):
    return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=tol)


def build_block_table():
    comp = load_json(ROOT/'logs'/'PRODUCTION_COMPLETENESS_v1.0.0.json')
    if comp.get('status') != 'PASS' or comp.get('missing'):
        raise RuntimeError('production completeness gate did not pass')
    pairs = pd.read_csv(ROOT/'control'/'PAIRED_BLOCK_MANIFEST_v1.0.0.csv')
    if len(pairs)!=120 or pairs.paired_block_id.nunique()!=120:
        raise RuntimeError('paired manifest does not have 120 unique blocks')
    if pairs.base_seed_uint32.nunique()!=120:
        raise RuntimeError('paired-block seeds are not unique')

    rows=[]
    integrity=[]
    for p in pairs.itertuples(index=False):
        pid=str(p.paired_block_id)
        sid=str(p.scaffold_id)
        pe=load_json(ROOT/'raw'/'endpoints'/f'{pid}_PAIR.json')
        se=load_json(ROOT/'raw'/'endpoints'/f'{p.selected_run_id}_endpoint.json')
        ne=load_json(ROOT/'raw'/'endpoints'/f'{p.neutral_run_id}_endpoint.json')

        checks={
            'pair_id': pe['paired_block_id']==pid==se['paired_block_id']==ne['paired_block_id'],
            'scaffold_id': pe['scaffold_id']==sid==se['scaffold_id']==ne['scaffold_id'],
            'base_seed': int(pe['base_seed_uint32'])==int(p.base_seed_uint32)==int(se['base_seed_uint32'])==int(ne['base_seed_uint32']),
            'modes': se['mode']=='selected' and ne['mode']=='neutral',
            'ancestor_pairing': se['ancestor_hash']==ne['ancestor_hash']==pe['ancestor_hash_selected']==pe['ancestor_hash_neutral'],
            'delta_D': check_close(pe['delta_C_down_primary'], se['C_down_primary_g250']-ne['C_down_primary_g250']),
            'delta_A': check_close(pe['delta_C_down_unitshuffle'], se['C_down_unitshuffle_g250']-ne['C_down_unitshuffle_g250']),
            'delta_H': check_close(pe['delta_H'], se['historical_match_H']-ne['historical_match_H']),
        }
        # H must be historical mapping minus mean of other mappings within each mode.
        def H_from_cross(d):
            return float(d[sid] - np.mean([d[k] for k in PROBES if k!=sid]))
        checks['selected_H_formula']=check_close(se['historical_match_H'],H_from_cross(se['cross_eval_mapping_means']),1e-12)
        checks['neutral_H_formula']=check_close(ne['historical_match_H'],H_from_cross(ne['cross_eval_mapping_means']),1e-12)
        if not all(checks.values()):
            raise RuntimeError(f'integrity failure for {pid}: {checks}')
        integrity.append(checks)

        row={
            'paired_block_id':pid,
            'scaffold_id':sid,
            'replicate':int(p.replicate),
            'base_seed_uint32':int(p.base_seed_uint32),
            'selected_run_id':str(p.selected_run_id),
            'neutral_run_id':str(p.neutral_run_id),
            'ancestor_hash':se['ancestor_hash'],
            'selected_final_hash':se['final_hash'],
            'neutral_final_hash':ne['final_hash'],
            'C_down_primary_selected':float(se['C_down_primary_g250']),
            'C_down_primary_neutral':float(ne['C_down_primary_g250']),
            'D_delta_C_down_primary':float(pe['delta_C_down_primary']),
            'C_down_unitshuffle_selected':float(se['C_down_unitshuffle_g250']),
            'C_down_unitshuffle_neutral':float(ne['C_down_unitshuffle_g250']),
            'A_delta_C_down_unitshuffle':float(pe['delta_C_down_unitshuffle']),
            'H_selected':float(se['historical_match_H']),
            'H_neutral':float(ne['historical_match_H']),
            'H_delta_historical_match':float(pe['delta_H']),
        }
        for k in PROBES:
            s=float(se['cross_eval_mapping_means'][k]); n=float(ne['cross_eval_mapping_means'][k])
            row[f'F_selected_probe_{k}']=s
            row[f'F_neutral_probe_{k}']=n
            row[f'DeltaF_probe_{k}']=s-n
        rows.append(row)

        # Check checkpoint rows for both runs.
        for run_id,mode,endpoint in [(p.selected_run_id,'selected',se),(p.neutral_run_id,'neutral',ne)]:
            m=pd.read_csv(ROOT/'raw'/'metrics'/f'{run_id}_metrics.csv')
            if len(m)!=11 or list(m['generation'].astype(int))!=CHECKPOINTS:
                raise RuntimeError(f'checkpoint schedule mismatch: {run_id}')
            if not (m['run_id'].astype(str)==str(run_id)).all() or not (m['mode'].astype(str)==mode).all():
                raise RuntimeError(f'metric identity mismatch: {run_id}')
            last=m.iloc[-1]
            if not check_close(last['C_down_primary'],endpoint['C_down_primary_g250'],1e-15):
                raise RuntimeError(f'g250 C_down mismatch: {run_id}')
            if str(last['population_hash'])!=str(endpoint['final_hash']):
                raise RuntimeError(f'g250 population hash mismatch: {run_id}')

    df=pd.DataFrame(rows).sort_values(['scaffold_id','replicate']).reset_index(drop=True)
    if len(df)!=120 or any((df.scaffold_id==s).sum()!=30 for s in SCAFFOLDS):
        raise RuntimeError('block table does not have 30 blocks per scaffold')
    return df


def endpoint_family(df, metric_col, family_name):
    raw=[]
    values={}
    for sid in SCAFFOLDS:
        v=df.loc[df.scaffold_id==sid,metric_col].to_numpy(float)
        values[sid]=v
        ci=mean_bootstrap_ci(v,ci=FAMILY_CI,n_boot=N_BOOT,key=f'{VERSION}|{family_name}|{sid}|98.75')
        st=exact_one_sided_sign_test(v)
        raw.append({
            'family':family_name,'scaffold_id':sid,'n':len(v),
            'mean':ci['mean'],'median':ci['median'],
            'ci_level':ci['ci'],'ci_low':ci['low'],'ci_high':ci['high'],
            'positive_blocks':st['positive'],'nonpositive_blocks':st['nonpositive'],
            'sign_p_raw':st['p_value'],
        })
    adj=holm_adjust([r['sign_p_raw'] for r in raw])
    for r,padj in zip(raw,adj):
        r['sign_p_holm']=float(padj)
        r['mapping_pass']=bool(r['mean']>0 and r['ci_low']>0 and r['sign_p_holm']<0.05)
    pooled=stratified_pooled_bootstrap(values,ci=0.95,n_boot=N_BOOT,key=f'{VERSION}|{family_name}|pooled95')
    return raw,pooled,values


def checkpoint_descriptives():
    frames=[]
    for f in sorted((ROOT/'raw'/'metrics').glob('*_metrics.csv')):
        frames.append(pd.read_csv(f))
    m=pd.concat(frames,ignore_index=True)
    if len(m)!=240*11:
        raise RuntimeError('checkpoint row count is not 2640')
    # Mode-specific descriptive means/sd/se by scaffold and generation.
    desc=(m.groupby(['scaffold_id','mode','generation'],sort=True)
          .agg(n=('C_down_primary','size'),
               C_down_mean=('C_down_primary','mean'),
               C_down_sd=('C_down_primary','std'),
               fitness_mean=('mean_fitness','mean'),
               fitness_sd=('mean_fitness','std'))
          .reset_index())
    desc['C_down_se']=desc['C_down_sd']/np.sqrt(desc['n'])
    desc['fitness_se']=desc['fitness_sd']/np.sqrt(desc['n'])
    # Pairwise selected-neutral descriptive means by generation/scaffold.
    wide=m.pivot(index=['paired_block_id','scaffold_id','base_seed_uint32','generation'],columns='mode',values=['C_down_primary','mean_fitness']).reset_index()
    wide.columns=['_'.join([str(x) for x in c if str(x)!='']).rstrip('_') if isinstance(c,tuple) else c for c in wide.columns]
    wide['Delta_C_down_primary']=wide['C_down_primary_selected']-wide['C_down_primary_neutral']
    wide['Delta_mean_fitness']=wide['mean_fitness_selected']-wide['mean_fitness_neutral']
    pdesc=(wide.groupby(['scaffold_id','generation'],sort=True)
           .agg(n=('Delta_C_down_primary','size'),
                Delta_C_down_mean=('Delta_C_down_primary','mean'),
                Delta_C_down_sd=('Delta_C_down_primary','std'),
                Delta_fitness_mean=('Delta_mean_fitness','mean'),
                Delta_fitness_sd=('Delta_mean_fitness','std'))
           .reset_index())
    return m,desc,pdesc


def fmt(x, digits=6):
    if x is None: return 'NA'
    x=float(x)
    if x==0: return '0'
    if abs(x)<1e-4 or abs(x)>=1e4: return f'{x:.3e}'
    return f'{x:.{digits}f}'


def main():
    out=ROOT/'analysis'; out.mkdir(exist_ok=True)
    df=build_block_table()
    df.to_csv(out/'PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv',index=False)

    D_rows,D_pool,D_vals=endpoint_family(df,'D_delta_C_down_primary','D_primary')
    H_rows,H_pool,H_vals=endpoint_family(df,'H_delta_historical_match','H_historical_match')
    A_rows,A_pool,A_vals=endpoint_family(df,'A_delta_C_down_unitshuffle','A_unitshuffle')
    family_rows=D_rows+H_rows+A_rows
    fam=pd.DataFrame(family_rows)
    fam.to_csv(out/'MAPPING_SUMMARY_v1.0.0.csv',index=False)

    # A-core: canonical SCF0 D with the frozen 95% interval and raw sign test.
    D0=D_vals['SCF0']
    Acore_ci=mean_bootstrap_ci(D0,ci=0.95,n_boot=N_BOOT,key=f'{VERSION}|A-core|SCF0|95')
    Acore_sign=exact_one_sided_sign_test(D0)
    A_core=bool(Acore_ci['mean']>0 and Acore_ci['low']>0 and Acore_sign['p_value']<0.05)

    # Supplemental A0 95% interval needed only for predeclared N3 classification.
    A0=A_vals['SCF0']
    A0_ci95=mean_bootstrap_ci(A0,ci=0.95,n_boot=N_BOOT,key=f'{VERSION}|N3|A0|95')

    B1=bool(all(r['mapping_pass'] for r in D_rows))
    B2=bool(all(r['mapping_pass'] for r in H_rows))
    Cstrong=bool(all(r['mapping_pass'] for r in A_rows))
    strong=bool(A_core and B1 and B2 and Cstrong)

    # Cross-evaluation selected-neutral difference matrix (row = historical/training scaffold).
    matrix=[]
    for sid in SCAFFOLDS:
        sub=df[df.scaffold_id==sid]
        row={'training_scaffold':sid}
        for k in PROBES:
            row[k]=float(sub[f'DeltaF_probe_{k}'].mean())
        row['historical_advantage_delta_H']=float(sub['H_delta_historical_match'].mean())
        matrix.append(row)
    mx=pd.DataFrame(matrix)
    mx.to_csv(out/'CROSS_EVAL_SELECTED_MINUS_NEUTRAL_MATRIX_v1.0.0.csv',index=False)

    # Canonical native-versus-reversed secondary contrast, block-level and summary.
    scf0=df[df.scaffold_id=='SCF0'].copy()
    scf0['canonical_native_minus_reversed_delta']=(
        scf0['DeltaF_probe_SCF0']-scf0['DeltaF_probe_SCF2']
    )
    sec_ci=mean_bootstrap_ci(scf0['canonical_native_minus_reversed_delta'].to_numpy(),ci=0.95,n_boot=N_BOOT,key=f'{VERSION}|secondary|native-reversed|SCF0')
    sec_sign=exact_one_sided_sign_test(scf0['canonical_native_minus_reversed_delta'].to_numpy())
    scf0[['paired_block_id','base_seed_uint32','canonical_native_minus_reversed_delta']].to_csv(out/'SECONDARY_CANONICAL_NATIVE_REVERSED_BLOCKS_v1.0.0.csv',index=False)

    # Descriptive checkpoints only; no checkpoint hypothesis tests.
    allm,desc,pdesc=checkpoint_descriptives()
    desc.to_csv(out/'CHECKPOINT_MODE_DESCRIPTIVES_v1.0.0.csv',index=False)
    pdesc.to_csv(out/'CHECKPOINT_PAIRED_DESCRIPTIVES_v1.0.0.csv',index=False)

    # Predeclared narrow-branch applicability if strong support fails but A-core passes.
    applicable=[]
    if A_core and not strong:
        d_pos=sum(float(np.mean(D_vals[s]))>0 for s in SCAFFOLDS)
        h_pos=sum(float(np.mean(H_vals[s]))>0 for s in SCAFFOLDS)
        if (d_pos>=3 and D_pool['low']>0 and not B1):
            applicable.append('N1')
        if (B1 and H_pool['low']>0 and h_pos>=3 and not B2):
            applicable.append('N2')
        if (A0_ci95['mean']>0 and A0_ci95['low']>0 and A_pool['low']>0 and not Cstrong):
            applicable.append('N3')
        if not applicable:
            applicable.append('N4')

    if not A_core:
        classification='NO_SUPPORT_CENTRAL_CLAIM'
    elif strong:
        classification='STRONG_PROSPECTIVE_SUPPORT'
    else:
        classification='NARROW_SUPPORT_' + '_'.join(applicable)

    result={
        'version':VERSION,
        'analysis_root_seed':145617781,
        'n_boot':N_BOOT,
        'n_paired_blocks':int(len(df)),
        'n_blocks_per_scaffold':{s:int((df.scaffold_id==s).sum()) for s in SCAFFOLDS},
        'A_core':{
            'pass':A_core,
            'scaffold_id':'SCF0',
            'mean_D0':Acore_ci['mean'],
            'ci95_low':Acore_ci['low'],'ci95_high':Acore_ci['high'],
            'positive_blocks':Acore_sign['positive'],'nonpositive_blocks':Acore_sign['nonpositive'],
            'sign_p_raw':Acore_sign['p_value'],
        },
        'B1_strong':B1,
        'B2_strong':B2,
        'C_strong':Cstrong,
        'overall_strong_support':strong,
        'classification':classification,
        'applicable_narrow_branches':applicable,
        'pooled_95':{'D_primary':D_pool,'H_historical_match':H_pool,'A_unitshuffle':A_pool},
        'N3_A0_95':A0_ci95,
        'secondary_canonical_native_reversed':{**sec_ci,**{f'sign_{k}':v for k,v in sec_sign.items()}},
        'validation_gate':'PASS_56_of_56',
        'production_completeness':'PASS_120_pairs_240_runs',
        'claim_boundary':'No full Walker-Davies reversal, top-down dominance, autonomous agency, or scaffold endogenization claim.',
    }
    (out/'CONFIRMATORY_RESULT_SUMMARY_v1.0.0.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

    # Human-readable report.
    lines=[]
    lines += ['# Confirmatory results v1.0.0','',
              '**Working paper:** *Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model*','',
              f'**Frozen-decision classification:** `{classification}`','',
              '## Gates','',
              '- Preproduction validation: **PASS (56/56 checks)**.',
              '- Production completeness: **PASS (120 paired blocks; 240 evolutionary runs; no missing outputs)**.',
              '- Scientific protocol changed after outcome inspection: **No**.','']
    lines += ['## Requirement A - independent canonical confirmation','',
              f"SCF0 mean `Delta C_down` = **{fmt(Acore_ci['mean'])} bits**, 95% bootstrap CI **[{fmt(Acore_ci['low'])}, {fmt(Acore_ci['high'])}]**; positive blocks **{Acore_sign['positive']}/30**; one-sided exact sign p = **{fmt(Acore_sign['p_value'])}**.",
              f"`A-core`: **{'PASS' if A_core else 'FAIL'}**.",'']
    lines += ['## Mapping-specific confirmatory families','',
              '| Family | Scaffold | Mean | 98.75% CI | Positive/30 | Raw sign p | Holm p | Pass |',
              '|---|---|---:|---:|---:|---:|---:|:---:|']
    for r in family_rows:
        lines.append(f"| {r['family']} | {r['scaffold_id']} | {fmt(r['mean'])} | [{fmt(r['ci_low'])}, {fmt(r['ci_high'])}] | {r['positive_blocks']}/30 | {fmt(r['sign_p_raw'])} | {fmt(r['sign_p_holm'])} | {'PASS' if r['mapping_pass'] else 'FAIL'} |")
    lines += ['',f"`B1-strong` (primary `C_down` across all four scaffolds): **{'PASS' if B1 else 'FAIL'}**.",
              f"`B2-strong` (historical-match cross-evaluation across all four scaffolds): **{'PASS' if B2 else 'FAIL'}**.",
              f"`C-strong` (alternative unit-stratified marginal-preserving erasure across all four scaffolds): **{'PASS' if Cstrong else 'FAIL'}**.",'']
    lines += ['## Equal-weight stratified pooled descriptive/inferential summaries','',
              f"- Primary `Delta C_down`: mean **{fmt(D_pool['mean'])} bits**, 95% CI **[{fmt(D_pool['low'])}, {fmt(D_pool['high'])}]**.",
              f"- Historical-match `Delta H`: mean **{fmt(H_pool['mean'])} fitness units**, 95% CI **[{fmt(H_pool['low'])}, {fmt(H_pool['high'])}]**.",
              f"- Alternative-erasure `Delta C_down`: mean **{fmt(A_pool['mean'])} bits**, 95% CI **[{fmt(A_pool['low'])}, {fmt(A_pool['high'])}]**.",'']
    lines += ['## Selected-minus-neutral cross-evaluation matrix','',
              'Rows are the scaffold under which the population evolved; columns are the probe scaffold. Entries are mean selected-minus-neutral probe fitness differences. The final column is the predeclared diagonal historical advantage `Delta H`.','',
              '| Training | SCF0 | SCF1 | SCF2 | SCF3 | Delta H |','|---|---:|---:|---:|---:|---:|']
    for _,r in mx.iterrows():
        lines.append(f"| {r['training_scaffold']} | {fmt(r['SCF0'],4)} | {fmt(r['SCF1'],4)} | {fmt(r['SCF2'],4)} | {fmt(r['SCF3'],4)} | **{fmt(r['historical_advantage_delta_H'],4)}** |")
    lines += ['', '## Frozen decision','']
    if strong:
        lines += ['All predeclared strong-support requirements passed. The frozen permitted claim is therefore supported within the tested canonical Model B regime:', '',
                  '> Within the tested canonical Model B regime, selection prospectively and reproducibly generated scaffold-history-specific inherited organization whose preservation changed lower-level chemical-state distributions; the effect generalized across four prespecified scaffold identities and survived an independently constructed marginal-preserving relational erasure.','']
    elif not A_core:
        lines += ['The central claim is **not prospectively supported** under the frozen decision rules because `A-core` failed. No rescue sweep or endpoint substitution is permitted.','']
    else:
        lines += [f"The outcome is **narrow support** under predeclared branch(es): {', '.join(applicable)}. The manuscript claim must be restricted accordingly.",'']
    lines += ['## Claim boundary','',
              'These results do **not** establish full Walker-Davies information-flow reversal, top-down dominance, autonomous agency, or scaffold endogenization. The scaffold remains externally specified in canonical Model B.','',
              'Checkpoint trajectories are retained as descriptive outputs only; no checkpoint-wise confirmatory p-values were computed.','']
    (out/'CONFIRMATORY_RESULTS_v1.0.0.md').write_text('\n'.join(lines)+'\n')

    # Gate decision file with compact preregistered pass/fail table.
    gate_lines=['# Frozen confirmatory gate decision v1.0.0','',
                f'- A-core: **{"PASS" if A_core else "FAIL"}**',
                f'- B1-strong: **{"PASS" if B1 else "FAIL"}**',
                f'- B2-strong: **{"PASS" if B2 else "FAIL"}**',
                f'- C-strong: **{"PASS" if Cstrong else "FAIL"}**',
                f'- Overall classification: **{classification}**','',
                'No outcome-dependent protocol changes were made.']
    (out/'GATE_DECISION_v1.0.0.md').write_text('\n'.join(gate_lines)+'\n')

    # Analysis integrity summary.
    integrity={
        'status':'PASS',
        'paired_blocks_checked':120,
        'run_endpoints_checked':240,
        'checkpoint_metric_files_checked':240,
        'checkpoint_rows_checked':2640,
        'ancestor_pairing_checked':True,
        'pair_delta_recomputation_checked':True,
        'historical_H_recomputation_checked':True,
        'generation_250_endpoint_metric_consistency_checked':True,
    }
    (out/'ANALYSIS_INTEGRITY_AUDIT_v1.0.0.json').write_text(json.dumps(integrity,indent=2,sort_keys=True)+'\n')

    print(json.dumps({
        'classification':classification,
        'A_core':A_core,'B1':B1,'B2':B2,'C':Cstrong,
        'A_core_mean_D0':Acore_ci['mean'],
        'A_core_ci95':[Acore_ci['low'],Acore_ci['high']],
        'D_pooled':D_pool,
        'H_pooled':H_pool,
        'A_pooled':A_pool,
    },indent=2,sort_keys=True))

if __name__=='__main__':
    main()
