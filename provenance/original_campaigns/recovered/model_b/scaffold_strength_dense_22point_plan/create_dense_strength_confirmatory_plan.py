from pathlib import Path
import csv, json, hashlib, glob, shutil, zipfile
from datetime import date

OUT=Path('/mnt/data/MODEL_B_DCC_SCAFFOLD_STRENGTH_DENSE_CONFIRMATORY_PLAN_v1.0.0')
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
VERSION='v1.0.0'
PROJECT='Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model'
CAMPAIGN='prospective dense-grid replication of scaffold-strength figure'
COMMIT='2c7d78694579755402c0a1896e109b29dec4d6a0'
THETA=1.2; P_INHERIT=0.975; MUT=0.001; N_BLOCKS=30; PROBE_BETA=3.0
SCF='[2,0,3,1]'; REV='[1,3,0,2]'; CHECKPOINTS='0;25;50;75;100;125;150;175;200;225;250'
# Exact 22-point x-grid used by the original exploratory+extension Figure 2 sweep.
GRID=[
('R0P0',0.0,0.0),('R0P25',0.25,0.3),('R0P5',0.5,0.6),('R0P75',0.75,0.9),
('R1P0',1.0,1.2),('R1P25',1.25,1.5),('R1P5',1.5,1.8),('R1P666667',1.666667,2.0),
('R2P0',2.0,2.4),('R2P25',2.25,2.7),('R2P5',2.5,3.0),('R2P75',2.75,3.3),
('R3P0',3.0,3.6),('R3P333333',3.333333,4.0),('R3P5',3.5,4.2),('R3P75',3.75,4.5),
('R4P0',4.0,4.8),('R4P25',4.25,5.1),('R4P5',4.5,5.4),('R5P0',5.0,6.0),
('R6P0',6.0,7.2),('R8P0',8.0,9.6)]
RIDS=[x[0] for x in GRID]

# Prior seed exclusion audit across all available ledgers, before this plan exists.
excluded=set(); seed_sources=[]
for p in sorted(set(glob.glob('/mnt/data/**/*seed*ledger*.csv',recursive=True)+glob.glob('/mnt/data/**/*SEED*LEDGER*.csv',recursive=True))):
    if str(OUT) in p: continue
    try:
        with open(p,newline='',encoding='utf-8') as f:
            rdr=csv.DictReader(f); fields=rdr.fieldnames or []; used=False
            seedcols=[c for c in fields if 'seed' in c.lower() and 'overlap' not in c.lower()]
            for row in rdr:
                for c in seedcols:
                    v=(row.get(c) or '').strip()
                    if v.isdigit(): excluded.add(int(v)); used=True
            if used: seed_sources.append(p)
    except Exception: pass

used=set(); ledger=[]
for rep in range(N_BLOCKS):
    nonce=0
    while True:
        tag=f'MODEL_B_DCC_STRENGTH_DENSE_CONFIRM|{VERSION}|block{rep:02d}|nonce{nonce}'
        seed=int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'little')
        if seed not in excluded and seed not in used: break
        nonce+=1
    used.add(seed)
    ledger.append({'plan_version':VERSION,'block_id':f'DSTR_B{rep:02d}','replicate':rep,'base_seed_uint32':seed,
                   'seed_derivation_tag':tag,'seed_shared_across_all_22_strengths_within_block':True,
                   'selected_neutral_share_base_seed':True,'excluded_prior_seed_overlap':False,'nonce':nonce})
analysis_tag=f'MODEL_B_DCC_STRENGTH_DENSE_CONFIRM|{VERSION}|analysis-bootstrap-root'
analysis_seed=int.from_bytes(hashlib.sha256(analysis_tag.encode()).digest()[:4],'little')
while analysis_seed in excluded or analysis_seed in used:
    analysis_tag+='|x'; analysis_seed=int.from_bytes(hashlib.sha256(analysis_tag.encode()).digest()[:4],'little')

def write_csv(path, rows, fields=None):
    fields=fields or list(rows[0].keys())
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

write_csv(OUT/'SEED_LEDGER_v1.0.0.csv',ledger)
conditions=[]
roles={0.0:'no-scaffold baseline',1.5:'low anchor inherited from first confirmatory campaign',2.5:'intermediate / fixed-probe-equivalent anchor',3.0:'strong viable anchor',3.5:'high transition anchor',4.0:'pre-collapse latent-organization anchor',4.5:'fitness-floor/collapse anchor'}
for rid,r,beta in GRID:
    conditions.append({'plan_version':VERSION,'ratio_id':rid,'beta_over_theta':r,'theta':THETA,'beta':beta,
                       'grid_status':'exact original 22-point exploratory+extension grid coordinate',
                       'condition_role':roles.get(r,'dense descriptive confirmatory point'),
                       'historical_scaffold_mapping':SCF,'fixed_probe_beta':PROBE_BETA,'fixed_probe_beta_over_theta':PROBE_BETA/THETA,
                       'reversed_probe_mapping':REV,'primary_figure_included':True})
write_csv(OUT/'CONDITION_MANIFEST_v1.0.0.csv',conditions)
write_csv(OUT/'GRID_PROVENANCE_v1.0.0.csv',[{'ratio_id':rid,'beta_over_theta':r,'beta':b,'source_grid':'original exploratory+extension Figure 2 x-grid; outcomes not pooled'} for rid,r,b in GRID])
blocks=[{**x,'n_strength_conditions':22,'n_modes_per_strength':2,'n_evolutionary_runs_in_block':44,'inferential_unit':True,'strengths_nested_within_block':True,'modes_paired_within_strength':True} for x in ledger]
write_csv(OUT/'BLOCK_MANIFEST_v1.0.0.csv',blocks)
runs=[]
for b in ledger:
    for rid,r,beta in GRID:
        for mode in ['selected','neutral']:
            run_id=f"{b['block_id']}_{rid}_{mode.upper()}"
            runs.append({'plan_version':VERSION,'run_id':run_id,'block_id':b['block_id'],'replicate':b['replicate'],'ratio_id':rid,'mode':mode,
              'base_seed_uint32':b['base_seed_uint32'],'scientific_commit':COMMIT,'historical_scaffold_id':'SCF0','historical_scaffold_mapping':SCF,
              'reversed_probe_mapping':REV,'N_model_units':80,'n_oligomer_slots':8,'sequence_length':60,'alphabet_size':4,'motif_window_k':5,
              'n_local_states':4,'n_segments':4,'theta':THETA,'beta':beta,'beta_over_theta':r,'fixed_probe_beta':PROBE_BETA,
              'fixed_probe_beta_over_theta':PROBE_BETA/THETA,'p_inherit':P_INHERIT,'mutation_rate':MUT,'reward_strength':2.0,'penalty_strength':0.5,
              'fitness_floor':0.1,'affinity_seed':123,'generations':250,'checkpoint_schedule':CHECKPOINTS,'archive_population_states':'g0;g250',
              'checkpoint_population_hashes':True,'primary_fitness_outputs':'F_g0;F_g250;G=F_g250-F_g0','primary_cdown_outputs':'C_down_train_g250;C_down_probe_beta3_g250',
              'primary_specificity_outputs':'R_train_g250;R_probe_beta3_g250','specificity_crn_draws':16,'cdown_estimator':'expectation-level JSD with P(S,M)->P(S)P(M)',
              'initialization_stream_key':'strength-initialization (exclude ratio and mode)','g0_observation_stream_key':'strength-g0-observation (exclude ratio and mode)',
              'propagation_stream_key':f'strength-propagation|{rid} (exclude mode)','endpoint_observation_stream_key':f'strength-endpoint-observation|{rid} (exclude mode)',
              'specificity_stream_key':f'strength-specificity-crn|{rid} (exclude mode and native/reversed mapping)',
              'expected_state_file':f'raw/states/{run_id}_g250.npz','expected_metrics_file':f'raw/metrics/{run_id}_metrics.csv','production_authorized':False})
write_csv(OUT/'RUN_MANIFEST_v1.0.0.csv',runs)
# Inherit the exact formal contrast families from the already-prospectively-frozen seven-anchor campaign.
contrasts=[
('A_COST','A1','F0(R0P0)-F0(R2P5)','>0','broad ancestral physical cost'),
('A_COST','A2','F0(R2P5)-F0(R4P0)','>0','further ancestral cost into the pre-collapse regime'),
('F_RECOVERY','F1','mean_{R1P5,R2P5,R3P0,R3P5,R4P0}[F250_selected-F250_neutral]','>0','selection-dependent adaptive recovery across viable anchor window'),
('F_RECOVERY','F2','DeltaF(R3P0)-DeltaF(R4P5)','>0','recovery is lost at collapse anchor'),
('C_DOWN','C1','mean_{R3P0,R3P5,R4P0}(DeltaC_train)-mean_{R0P0,R1P5}(DeltaC_train)','>0','downward constraint stronger in high viable than low regime'),
('C_DOWN','C2','mean_{R3P0,R3P5,R4P0}(DeltaC_train)-DeltaC_train(R4P5)','>0','training-strength downward constraint collapses beyond viable regime'),
('C_DOWN','C3','DeltaC_probe_beta3(R4P0)-DeltaC_train(R4P0)','>0','fixed moderate probe reveals masked latent downward constraint'),
('C_DOWN','C4','DeltaC_probe_beta3(R4P0)-DeltaC_probe_beta3(R4P5)','>0','latent downward constraint present before but not after collapse'),
('R_SPEC','R1','mean_{R3P0,R3P5,R4P0}(DeltaR_train)-mean_{R0P0,R1P5}(DeltaR_train)','>0','historical specificity stronger in high viable than low regime'),
('R_SPEC','R2','mean_{R3P0,R3P5,R4P0}(DeltaR_train)-DeltaR_train(R4P5)','>0','expressed historical specificity collapses beyond viable regime'),
('R_SPEC','R3','DeltaR_probe_beta3(R4P0)-DeltaR_train(R4P0)','>0','fixed moderate probe reveals masked latent specificity'),
('R_SPEC','R4','DeltaR_probe_beta3(R4P0)-DeltaR_probe_beta3(R4P5)','>0','latent specificity present before but not after collapse')]
cr=[]
for fam,cid,formula,direction,meaning in contrasts:
    n={'A_COST':2,'F_RECOVERY':2,'C_DOWN':4,'R_SPEC':4}[fam]
    cr.append({'plan_version':VERSION,'family':fam,'contrast_id':cid,'formula':formula,'direction':direction,'meaning':meaning,
               'inferential_unit':'root seed block','bootstrap_replicates':50000,'sign_test':'one-sided exact; zero counted nonpositive',
               'multiplicity':'Holm within family','familywise_interval':'97.5% two-sided bootstrap' if n==2 else '98.75% two-sided bootstrap',
               'provenance':'unchanged from seven-anchor scaffold-strength confirmatory plan v1.0.0'})
write_csv(OUT/'CONTRAST_MANIFEST_v1.0.0.csv',cr)
config={'plan_version':VERSION,'project':PROJECT,'campaign':CAMPAIGN,'scientific_commit':COMMIT,'status':'DESIGN FROZEN; VALIDATION REQUIRED; PRODUCTION NOT AUTHORIZED',
'canonical_model':{'N':80,'n_olig':8,'L':60,'alphabet_size':4,'k':5,'n_local_states':4,'n_segments':4,'scaffold_mapping':[2,0,3,1],'theta':THETA,'p_inherit':P_INHERIT,'mutation_rate':MUT,'reward':2.0,'penalty':0.5,'fitness_floor':0.1,'affinity_seed':123,'generations':250},
'strength_grid':[{'ratio_id':rid,'beta_over_theta':r,'beta':beta} for rid,r,beta in GRID],
'fixed_probe':{'beta':PROBE_BETA,'beta_over_theta':PROBE_BETA/THETA,'reversed_mapping':[1,3,0,2],'specificity_crn_draws':16},
'design':{'n_root_seed_blocks':N_BLOCKS,'runs_per_block':44,'total_runs':len(runs),'selected_neutral_pairing':True,'strengths_repeated_within_block':True,'exact_original_22_point_grid':True},
'inference':{'formal_contrasts':'unchanged from seven-anchor confirmatory campaign','bootstrap_replicates':50000,'bootstrap_seed_uint32':analysis_seed,'bootstrap_seed_tag':analysis_tag,'resample_unit':'root seed block','sign_test':'one-sided exact','multiplicity':'Holm within prespecified families','pointwise_tests_over_22_grid':False},
'figure_policy':{'plot_all_22_points':True,'x_range':[0,8],'panel_b':'selected-minus-ancestral and neutral-minus-ancestral','no_posthoc_smoothing_or_point_removal':True},'production_authorized':False}
(OUT/'CONFIRMATORY_CONFIG_v1.0.0.json').write_text(json.dumps(config,indent=2)+'\n')

plan=f'''# Dense Scaffold-Strength Confirmatory Plan v1.0.0

**Project:** {PROJECT}  
**Campaign:** {CAMPAIGN}  
**Status:** **DESIGN FROZEN; VALIDATION REQUIRED; CONFIRMATORY PRODUCTION NOT AUTHORIZED**  
**Date:** 2026-09-05  
**Scientific source:** canonical Model B, commit `{COMMIT}`

## 1. Purpose

A seven-anchor prospective campaign has already confirmed the scaffold-strength regime structure. This second campaign has a narrower purpose: replace the exploratory 22-point curves in the primary scaffold-strength figure with an **independent, prospectively generated dense-grid replication at the exact original x-coordinates**, without thinning the display or treating exploratory outcomes as confirmatory data.

No exploratory outcome is pooled with the new campaign. The original exploratory+extension files contribute only the frozen **22-point grid coordinates**.

## 2. Exact frozen 22-point strength grid

The full original grid is retained:

`beta/Theta = {{0, .25, .5, .75, 1, 1.25, 1.5, 1.666667, 2, 2.25, 2.5, 2.75, 3, 3.333333, 3.5, 3.75, 4, 4.25, 4.5, 5, 6, 8}}`.

`beta = {{0, .3, .6, .9, 1.2, 1.5, 1.8, 2.0, 2.4, 2.7, 3.0, 3.3, 3.6, 4.0, 4.2, 4.5, 4.8, 5.1, 5.4, 6.0, 7.2, 9.6}}` with `Theta=1.2`.

Every point is retained in the confirmatory figure. The irregular spacing is plotted on a true numeric x-axis. No point may be removed, added, or shifted after outcome inspection.

## 3. Canonical model and blocking

Canonical Model B is unchanged: `p=0.975`, `Theta=1.2`, SCF0 `[2,0,3,1]`, canonical affinity seed 123, mutation 0.001, 250 generations, and canonical fitness floor 0.1.

There are **30 new independent root-seed blocks**. Within each block all 22 strengths share the same ancestor; each strength has one selected and one matched-neutral trajectory.

`30 blocks x 22 strengths x 2 modes = 1320 evolutionary runs`.

The root-seed block is the inferential unit. Strength and mode observations are repeated/nested within block.

## 4. Figure endpoints

- **Panel (a):** ancestral `F0` across all 22 strengths.
- **Panel (b):** zero-centered `G_selected = F250_selected-F0` and `G_neutral = F250_neutral-F0` across all 22 strengths. The formal selection effect remains `DeltaF=F250_selected-F250_neutral`.
- **Panel (c):** selected-minus-neutral `DeltaC_down` at training strength and at the fixed moderate `beta=3` probe across all 22 strengths.
- **Panel (d):** selected-minus-neutral historical specificity `DeltaR` at training strength and fixed `beta=3` probe across all 22 strengths, using 16 native/reversed common-random-number draws.

All 22 means and bootstrap intervals are confirmatory descriptive estimates. There are **no 22-point significance scans** and no retrospectively defined critical strength or exact optimum.

## 5. Formal inference

The twelve formal contrasts and four families are inherited **unchanged** from the already-frozen seven-anchor scaffold-strength campaign (`A_COST`, `F_RECOVERY`, `C_DOWN`, `R_SPEC`). Their formulas are recorded verbatim in `CONTRAST_MANIFEST_v1.0.0.csv`.

Inference remains 50,000 root-block bootstrap resamples, exact one-sided sign tests, and Holm correction within each prespecified family. This dense replication does not create additional pointwise tests merely because more descriptive grid points are present.

## 6. Dense-grid promotion criterion

The full 22-point primary figure may be described as prospectively replicated if:

1. validation/completeness/reproducibility gates pass;
2. all four inherited contrast families pass their already-frozen strong-support criteria;
3. the five viable anchor `DeltaF` means at `1.5, 2.5, 3.0, 3.5, 4.0` are positive;
4. the `r=4.5` fitness-floor wording gate passes if collapse language is used;
5. all 22 prespecified points are displayed, including null/negative/unexpected values.

The campaign is not required to reproduce the exact exploratory maximum or every adjacent-point ordering.

## 7. Seed and outcome firewall

The 30 new root seeds are deterministic under the namespace `MODEL_B_DCC_STRENGTH_DENSE_CONFIRM|v1.0.0` and have zero overlap with accessible prior seed ledgers at freeze time. The seed ledger, run manifest, analysis seed, contrast manifest, and this plan are hash-frozen before production authorization.

## 8. Validation gate

Before production: canonical replay; RNG and repeated-measures blocking audit; generation-0 selected/neutral identity; shared ancestor across all 22 strengths within block; C-down replay; fixed-probe validation; 16-draw specificity CRN validation; statistical pipeline tests; 1320-row dry-manifest audit; and confirmation that no dense confirmatory endpoint exists before authorization.

Scientific or estimator changes require a new plan version before any confirmatory outcomes are generated.

## 9. Scope boundary

Success supports a dense prospective scaffold-strength map **within the tested canonical Model B domain**. It does not establish a universal optimal constraint strength, a continuously estimated critical threshold, full Walker-Davies reversal, autonomous agency, top-down dominance, or scaffold endogenization.
'''
(OUT/'CONFIRMATORY_PLAN_v1.0.0.md').write_text(plan)

success='''# Dense Scaffold-Strength Success Criteria v1.0.0

The twelve formal contrast criteria are inherited unchanged from the seven-anchor scaffold-strength confirmatory campaign v1.0.0.

- `A_COST`: A1 and A2 each require positive mean, familywise interval lower bound > 0, Holm-adjusted sign p < .05.
- `F_RECOVERY`: F1 and F2 pass the same two-test-family criteria, and mean DeltaF is positive at r={1.5,2.5,3.0,3.5,4.0}.
- `C_DOWN`: C1-C4 each require positive mean, 98.75% interval lower bound > 0, and Holm-adjusted sign p < .05.
- `R_SPEC`: R1-R4 use the same four-test-family rule.
- Fitness-floor wording at r=4.5 requires both selected and neutral mean F250 <= 0.20.

**Dense-grid strong replication:** all four families plus validation/completeness/reproducibility pass. All 22 frozen points must be shown. No exact peak location or adjacent-point monotonicity is required.

**Narrow replication:** the previously confirmed anchor-family result remains supported but one or more dense descriptive regions differ materially from the exploratory shape. Report the prospective dense curve as observed without deleting points or adding post hoc tests.

**No dense replication:** a core inherited family (especially F_RECOVERY or C1) fails, or a favorable conclusion requires changing grid, seeds, estimators, or inference after outcome inspection. This does not revoke the already-frozen seven-anchor confirmation.
'''
(OUT/'SUCCESS_CRITERIA_v1.0.0.md').write_text(success)

check='''# Dense Scaffold-Strength Estimator/Execution Validation Checklist v1.0.0

Production is blocked until every required item passes.

- [ ] canonical Model B archived replay is exact
- [ ] same seed/key deterministic; different root seeds diverge
- [ ] all 22 propagation namespaces are distinct and scheduling invariant
- [ ] selected and neutral generation-0 states/fitness are identical within each strength
- [ ] all 22 strengths reconstruct the same ancestor within each root block
- [ ] endpoint observation streams are strength-specific and mode-paired
- [ ] expectation-level C_down replays validated estimator and preserves motif/segment marginals
- [ ] training-strength and fixed-beta=3 probes use frozen beta values and do not mutate populations
- [ ] historical-specificity assay uses exactly 16 CRN draws and agrees with canonical core on test draws
- [ ] 50,000 block bootstrap, sign test, Holm, and all 12 inherited contrast formulas pass synthetic checks
- [ ] condition manifest contains exactly 22 frozen strengths and exact beta coordinates
- [ ] run manifest contains exactly 1320 unique run IDs; 44 runs per block; 30 selected + 30 neutral per strength
- [ ] seed ledger contains 30 unique new seeds with zero recorded overlap
- [ ] all output paths are unique and production flags are false at freeze
- [ ] dry-run parses all 1320 rows
- [ ] no dense confirmatory endpoint exists before validation/authorization
'''
(OUT/'ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md').write_text(check)

seedplan=f'''# Dense Scaffold-Strength Seed Plan v1.0.0

Thirty independent root seeds are deterministically derived from SHA-256 namespace `MODEL_B_DCC_STRENGTH_DENSE_CONFIRM|{VERSION}`. One root seed is shared across all 22 strengths and both modes within a block solely for repeated-measures blocking. Purpose-separated keyed RNG streams provide strength-specific propagation and mode pairing. At freeze, {len(excluded)} numeric seed values were excluded from {len(seed_sources)} accessible prior seed-ledger files; the 30 frozen roots have zero overlap.

Analysis bootstrap seed: `{analysis_seed}` from `{analysis_tag}`.
'''
(OUT/'SEED_PLAN_v1.0.0.md').write_text(seedplan)

runexec='''# Dense Scaffold-Strength Run Execution Specification v1.0.0

1. Validate the frozen plan without generating scientific outcomes.
2. Hash/freeze the control package and record environment.
3. Authorization may change only `production_authorized` from false to true; all scientific columns remain byte-equivalent.
4. Execute exactly the 660 selected-neutral strength pairs / 1320 runs in `RUN_MANIFEST_AUTHORIZED_v1.0.0.csv`.
5. Save g250 state, checkpoint metrics, and endpoint JSON for every run, plus one paired endpoint per block x strength.
6. Analyze only with the frozen twelve contrast formulas and root-block inference.
7. Produce the 22-point source table for Figure 2 without removing or smoothing points.
8. Freeze positive, null, and unexpected outcomes together.
'''
(OUT/'RUN_EXECUTION_SPEC_v1.0.0.md').write_text(runexec)

dec=f'''# Dense Scaffold-Strength Decisions Log

## 2026-09-05 — v1.0.0 design freeze

- The user requested a second prospective scaffold-strength campaign retaining the original 22-point display density and width.
- Exact original exploratory+extension x-grid frozen from beta/Theta 0 through 8; only grid coordinates are reused, not exploratory outcomes.
- N=30 new repeated-measures root blocks; 1320 runs total.
- Canonical Model B, p=0.975, Theta=1.2, 250 generations retained.
- Panel (b) remains zero-centered selected-minus-ancestral and neutral-minus-ancestral.
- Fixed moderate probe beta=3 and 16-draw native/reversed CRN specificity retained.
- Formal inference reuses the twelve already-frozen contrasts from the seven-anchor prospective campaign; the added grid density is descriptive, not an opportunity for 22-point p-value scanning.
- Exact exploratory peak reproduction is explicitly not a success criterion.
- Production is unauthorized until validation passes.
'''
(OUT/'DECISIONS_LOG.md').write_text(dec)
readme=f'''# MODEL_B_DCC_SCAFFOLD_STRENGTH_DENSE_CONFIRMATORY_PLAN_v1.0.0

Prospective preproduction freeze for the 22-point dense scaffold-strength replication. **No scientific outcomes are contained in this package.**

Key counts: 30 independent root blocks; 22 strengths; 2 modes; 1320 evolutionary runs. See `CONFIRMATORY_PLAN_v1.0.0.md` first.
'''
(OUT/'README.md').write_text(readme)
# Record seed-source audit without leaking irrelevant contents.
(OUT/'SEED_EXCLUSION_AUDIT_v1.0.0.json').write_text(json.dumps({'excluded_numeric_seed_count':len(excluded),'source_files':seed_sources,'new_root_count':30,'overlap_count':0},indent=2)+'\n')
# preserve plan-generation code
shutil.copy2('/mnt/data/create_dense_strength_confirmatory_plan.py',OUT/'create_dense_strength_confirmatory_plan.py')
# hashes excluding hash file itself
rows=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name!='SHA256_MANIFEST.csv':
        rows.append({'relative_path':str(p.relative_to(OUT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
write_csv(OUT/'SHA256_MANIFEST.csv',rows)
# zip
zip_path=Path('/mnt/data/MODEL_B_DCC_SCAFFOLD_STRENGTH_DENSE_CONFIRMATORY_PLAN_v1.0.0.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file(): z.write(p,arcname=f'{OUT.name}/{p.relative_to(OUT)}')
print(json.dumps({'out':str(OUT),'zip':str(zip_path),'n_runs':len(runs),'n_blocks':N_BLOCKS,'n_conditions':len(GRID),'excluded_prior_seeds':len(excluded),'seed_sources':len(seed_sources),'zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()},indent=2))
