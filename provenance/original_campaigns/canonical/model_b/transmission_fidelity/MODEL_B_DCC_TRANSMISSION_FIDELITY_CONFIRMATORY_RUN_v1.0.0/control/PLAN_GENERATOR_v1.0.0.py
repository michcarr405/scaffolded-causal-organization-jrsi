from __future__ import annotations
import csv, hashlib, json, os, re, shutil, zipfile
from pathlib import Path
import pandas as pd

VERSION='v1.0.0'
ROOT=Path('/mnt/data/MODEL_B_DCC_TRANSMISSION_FIDELITY_CONFIRMATORY_PLAN_v1.0.0')
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

PROJECT='Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model'
COMMIT='2c7d78694579755402c0a1896e109b29dec4d6a0'
THETA=1.2; BETA=3.0; RATIO=2.5
P_VALUES=[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.75,0.8,0.825,0.85,0.875,0.9,0.925,0.95,0.975,1.0]
N_BLOCKS=30
NBOOT=50000
BOOT_SEED=2481907731
SCF='[2,0,3,1]'; REV='[1,3,0,2]'

def pid(p: float)->str:
    return f'P{int(round(p*1000)):04d}'

# Collect prior seed-like integers from accessible CSV ledgers. This is intentionally conservative.
prior=set(); sources=[]
for path in sorted(Path('/mnt/data').rglob('*.csv')):
    if ROOT in path.parents: continue
    if 'seed' not in path.name.lower() and 'manifest' not in path.name.lower():
        continue
    try:
        df=pd.read_csv(path)
    except Exception:
        continue
    seed_cols=[c for c in df.columns if 'seed' in c.lower()]
    vals=[]
    for c in seed_cols:
        for x in df[c].dropna().tolist():
            try:
                if isinstance(x,str) and not re.fullmatch(r'[+-]?\d+(?:\.0+)?',x.strip()):
                    continue
                v=int(float(x))
                if 0 <= v <= 2**32-1:
                    prior.add(v); vals.append(v)
            except Exception:
                pass
    if vals:
        sources.append({'path':str(path),'seed_columns':seed_cols,'integer_values_seen':len(vals),'unique_in_file':len(set(vals))})

# Deterministic root seeds with explicit collision/overlap avoidance.
seed_rows=[]; chosen=set()
for b in range(N_BLOCKS):
    nonce=0
    while True:
        tag=f'MODEL_B_DCC_FIDELITY_CONFIRM|{VERSION}|block{b:02d}|nonce{nonce}'
        d=hashlib.sha256(tag.encode()).digest()
        seed=int.from_bytes(d[:4],'little',signed=False)
        if seed not in prior and seed not in chosen:
            break
        nonce+=1
    chosen.add(seed)
    seed_rows.append(dict(plan_version=VERSION,block_id=f'FID_B{b:02d}',replicate=b,base_seed_uint32=seed,
                          seed_derivation_tag=tag,seed_shared_across_fidelities_within_block=True,
                          selected_neutral_share_base_seed=True,excluded_prior_seed_overlap=False,nonce=nonce))
seeds=pd.DataFrame(seed_rows)
seeds.to_csv(ROOT/'SEED_LEDGER_v1.0.0.csv',index=False)

(Path(ROOT/'SEED_EXCLUSION_AUDIT_v1.0.0.json')).write_text(json.dumps({
    'plan_version':VERSION,'prior_seed_scan_sources':sources,'prior_unique_uint32_seed_values':len(prior),
    'new_seed_count':len(chosen),'overlap_count':len(chosen & prior),
    'new_seed_values':sorted(chosen)
},indent=2))

# Conditions
roles=[]
for p in P_VALUES:
    if p<=0.6: role='low-fidelity reference region'
    elif p<0.85: role='intermediate transition-resolution region'
    elif p<0.95: role='high-fidelity transition region'
    elif p<1.0: role='very-high-fidelity region'
    else: role='perfect-transmission endpoint'
    roles.append(dict(plan_version=VERSION,p_id=pid(p),p_inherit=p,theta=THETA,beta=BETA,beta_over_theta=RATIO,
                      condition_role=role,historical_scaffold_mapping=SCF,reversed_probe_mapping=REV,
                      generation_endpoint=250,primary_figure_included=True))
cond=pd.DataFrame(roles)
cond.to_csv(ROOT/'CONDITION_MANIFEST_v1.0.0.csv',index=False)

# Block manifest
blocks=[]
for r in seeds.itertuples(index=False):
    blocks.append(dict(plan_version=VERSION,block_id=r.block_id,replicate=r.replicate,base_seed_uint32=r.base_seed_uint32,
                       n_fidelity_conditions=len(P_VALUES),modes='selected;neutral',n_runs=2*len(P_VALUES),
                       shared_ancestor_across_p=True,inferential_unit=True,production_authorized=False))
pd.DataFrame(blocks).to_csv(ROOT/'BLOCK_MANIFEST_v1.0.0.csv',index=False)

# Contrast manifest, 3 tests/family -> 98.333...% intervals.
contrasts=[
('C_DOWN','C1','mean_{p=0.90,0.925,0.95,0.975,1.0}(DeltaC_down_250)-mean_{p=0,0.1,0.2,0.3,0.4,0.5,0.6}(DeltaC_down_250)','>0','downward causal constraint is concentrated in the high-fidelity regime relative to the low-fidelity regime'),
('C_DOWN','C2','mean_{p=0.95,0.975,1.0}(DeltaC_down_250)-mean_{p=0.85,0.875,0.90}(DeltaC_down_250)','>0','downward causal constraint continues to strengthen from the transition region into very high fidelity'),
('C_DOWN','C3','DeltaC_down_250(p=0.975)','>0','the manuscript-relevant p=0.975 endpoint has positive selection-generated downward causal constraint at beta=3'),
('R_SPEC','R1','mean_{p=0.90,0.925,0.95,0.975,1.0}(DeltaR_250)-mean_{p=0,0.1,0.2,0.3,0.4,0.5,0.6}(DeltaR_250)','>0','historical scaffold specificity is concentrated in the high-fidelity regime relative to the low-fidelity regime'),
('R_SPEC','R2','mean_{p=0.95,0.975,1.0}(DeltaR_250)-mean_{p=0.85,0.875,0.90}(DeltaR_250)','>0','historical scaffold specificity continues to strengthen from the transition region into very high fidelity'),
('R_SPEC','R3','DeltaR_250(p=0.975)','>0','the manuscript-relevant p=0.975 endpoint has positive selection-generated historical scaffold specificity at beta=3'),
]
rows=[]
for fam,cid,formula,direction,meaning in contrasts:
    rows.append(dict(plan_version=VERSION,family=fam,contrast_id=cid,formula=formula,direction=direction,meaning=meaning,
                     inferential_unit='root seed block',bootstrap_replicates=NBOOT,
                     sign_test='one-sided exact; zero counted nonpositive',multiplicity='Holm within family',
                     familywise_interval='98.333% two-sided root-block bootstrap'))
pd.DataFrame(rows).to_csv(ROOT/'CONTRAST_MANIFEST_v1.0.0.csv',index=False)

# Run manifest
runs=[]
for s in seeds.itertuples(index=False):
    for p in P_VALUES:
        p_id=pid(p)
        for mode in ['selected','neutral']:
            rid=f'{s.block_id}_{p_id}_{mode.upper()}'
            runs.append(dict(
                plan_version=VERSION,run_id=rid,block_id=s.block_id,replicate=s.replicate,p_id=p_id,mode=mode,
                base_seed_uint32=s.base_seed_uint32,scientific_commit=COMMIT,
                historical_scaffold_id='SCF0',historical_scaffold_mapping=SCF,reversed_probe_mapping=REV,
                N_model_units=80,n_oligomer_slots=8,sequence_length=60,alphabet_size=4,motif_window_k=5,
                n_local_states=4,n_segments=4,theta=THETA,beta=BETA,beta_over_theta=RATIO,p_inherit=p,
                mutation_rate=0.001,reward_strength=2.0,penalty_strength=0.5,fitness_floor=0.1,affinity_seed=123,
                generations=250,checkpoint_schedule='0;250',archive_population_states='g250',
                checkpoint_population_hashes=True,
                primary_fitness_outputs='F_g0;F_g250;DeltaF_g250(selected-neutral;secondary context)',
                primary_cdown_outputs='C_down_g250;DeltaC_down_g250(selected-neutral)',
                primary_specificity_outputs='R_g250=F_native-F_reversed;DeltaR_g250(selected-neutral)',
                specificity_crn_draws=16,
                cdown_estimator='expectation-level JSD with P(S,M)->P(S)P(M)',
                initialization_stream_key='fidelity-initialization (exclude p and mode)',
                g0_observation_stream_key='fidelity-g0-observation (exclude p and mode)',
                propagation_stream_key=f'fidelity-propagation|{p_id} (exclude mode)',
                endpoint_observation_stream_key=f'fidelity-endpoint-observation|{p_id} (exclude mode)',
                specificity_stream_key=f'fidelity-specificity-crn|{p_id} (exclude mode and native/reversed mapping)',
                expected_state_file=f'raw/states/{rid}_g250.npz',
                expected_metrics_file=f'raw/metrics/{rid}_metrics.csv',production_authorized=False
            ))
runs=pd.DataFrame(runs)
runs.to_csv(ROOT/'RUN_MANIFEST_v1.0.0.csv',index=False)

config={
 'plan_version':VERSION,'status':'DESIGN_FROZEN_VALIDATION_REQUIRED_PRODUCTION_NOT_AUTHORIZED','project':PROJECT,
 'scientific_commit':COMMIT,'theta':THETA,'beta':BETA,'beta_over_theta':RATIO,'p_values':P_VALUES,
 'n_root_blocks':N_BLOCKS,'modes':['selected','neutral'],'n_evolutionary_runs':len(runs),'generations':250,
 'historical_scaffold_mapping':[2,0,3,1],'reversed_probe_mapping':[1,3,0,2],
 'specificity_crn_draws':16,'bootstrap_replicates':NBOOT,'bootstrap_root_seed':BOOT_SEED,
 'inference':'root-block bootstrap + exact one-sided sign test + Holm within family',
 'production_authorized':False
}
(ROOT/'CONFIRMATORY_CONFIG_v1.0.0.json').write_text(json.dumps(config,indent=2))

readme=f'''# MODEL B DCC Transmission-Fidelity Confirmatory Plan {VERSION}\n\nThis package freezes the prospective campaign required to promote Figure 4 panels (c) and (d) from exploratory to primary confirmatory evidence.\n\n**Status:** design frozen; validation required; production not authorized.\n\n- Exact exploratory fidelity-grid density preserved: **18 p values**.\n- Independent root-seed blocks: **{N_BLOCKS}**.\n- Selected/neutral paired runs: **{len(runs)}**.\n- Canonical Model B unchanged: `beta=3`, `Theta=1.2`, 250 generations, SCF0 historical scaffold.\n- Primary endpoints: generation-250 selected-minus-neutral `Delta C_down` and historical specificity `Delta R`.\n- The 18-point curves are descriptive at every point; confirmatory inference is restricted to three frozen contrasts per endpoint family.\n\nNo confirmatory outcomes are present in this package.\n'''
(ROOT/'README.md').write_text(readme)

plan=f'''# Transmission-Fidelity Confirmatory Plan {VERSION}\n\n**Project:** {PROJECT}  \n**Campaign:** prospective confirmation of Figure 4(c,d) heredity dependence  \n**Status:** **DESIGN FROZEN; VALIDATION REQUIRED; CONFIRMATORY PRODUCTION NOT AUTHORIZED**  \n**Date:** 2026-09-05  \n**Scientific source:** canonical Model B, commit `{COMMIT}`\n\n## 1. Purpose\n\nFigure 4 panels (c) and (d) currently use an exploratory transmission-fidelity sweep. They are central to the manuscript because they address whether selection-generated downward causal constraint and historical scaffold specificity depend strongly on hereditary fidelity. This plan freezes an independent new-seed campaign before any new outcomes are generated.\n\nThe campaign does **not** attempt to locate a continuously estimated critical fidelity. It prospectively tests the previously observed **high-heredity regime concentration and strengthening** while preserving the full density of the original discrete sweep.\n\nExploratory data are design/calibration evidence only and will not be pooled with this campaign for confirmatory inference.\n\n## 2. Canonical Model B is unchanged\n\n| Quantity | Frozen value |\n|---|---:|\n| model units | 80 |\n| oligomer slots per unit | 8 |\n| sequence length | 60 |\n| alphabet | 4 |\n| motif window | 5 |\n| local-state classes | 4 |\n| positional segments | 4 |\n| historical scaffold | SCF0 `[2,0,3,1]` |\n| reversed probe scaffold | `[1,3,0,2]` |\n| affinity matrix | canonical 1024 x 4, seed 123 |\n| `Theta` | 1.2 |\n| `beta` | 3.0 |\n| `beta/Theta` | 2.5 |\n| mutation rate | 0.001 |\n| reward / penalty | 2.0 / 0.5 |\n| fitness floor | 0.1 |\n| duration | 250 updates |\n\nOnly transmission fidelity `p` varies.\n\n## 3. Exact 18-point fidelity grid is preserved\n\nThe prospective grid is exactly:\n\n`{P_VALUES}`\n\nThis preserves the exploratory sweep's dense resolution, especially from `p=0.70` through `1.00`. No values are thinned, shifted, inserted, or deleted. The density is retained to display regime geometry; it does not authorize 18 independent pointwise significance searches.\n\n## 4. Repeated-measures paired-block design\n\nThere are **30 independent root-seed blocks**. Every block contains all 18 fidelity values, and every fidelity contains one selected and one matched-neutral evolutionary trajectory:\n\n`30 blocks x 18 fidelities x 2 modes = 1080 evolutionary runs`.\n\nThe **root-seed block** is the inferential unit. Fidelity values and selected/neutral trajectories are repeated/nested observations within each block.\n\nWithin each block:\n\n- all fidelities and both modes begin from the same ancestral sequence population;\n- selected and neutral trajectories at a given fidelity use purpose-matched common random streams;\n- propagation streams are fidelity-specific but mode-paired;\n- cross-fidelity contrasts are therefore paired repeated-measures contrasts, not independent-sample comparisons.\n\n## 5. New-seed requirement\n\nThirty root seeds are frozen in `SEED_LEDGER_v1.0.0.csv`, derived deterministically from the namespace `MODEL_B_DCC_FIDELITY_CONFIRM|v1.0.0|...`.\n\nThe plan generator conservatively scanned accessible prior seed/manifest CSVs and excluded previously used uint32 seed values. The frozen audit is `SEED_EXCLUSION_AUDIT_v1.0.0.json`. Seed reuse **within** a block across fidelity values is intentional blocking, not pseudoreplication.\n\n## 6. Panel (c): downward causal constraint\n\nFor each generation-250 population:\n\n`C_down = D_JS[P_intact(S,Z) || P_erased(S,Z)]`,\n\nwhere relational erasure applies `P(S,M) -> P(S)P(M)` and intact and erased populations are passed through the same canonical `P(Z|M,S)` readout.\n\nThe claim-bearing paired quantity is:\n\n`DeltaC_down_250(p) = C_down_selected(p) - C_down_neutral(p)`.\n\nAll 18 means and uncertainty intervals are plotted. Formal inference is limited to:\n\n- **C1 high-vs-low:** mean over `p={{0.90,0.925,0.95,0.975,1.0}}` minus mean over `p={{0,0.1,0.2,0.3,0.4,0.5,0.6}}` > 0;\n- **C2 very-high-vs-transition:** mean over `p={{0.95,0.975,1.0}}` minus mean over `p={{0.85,0.875,0.90}}` > 0;\n- **C3 manuscript endpoint:** `DeltaC_down_250(0.975) > 0`.\n\nThese tests confirm concentration and strengthening in the high-heredity regime without retrospectively choosing a first significant fidelity.\n\n## 7. Panel (d): historical scaffold specificity\n\nHistorical specificity uses the canonical native scaffold `[2,0,3,1]` and prespecified reversed scaffold `[1,3,0,2]` at the same fixed `beta=3`. For each evolved population:\n\n`R = F_native - F_reversed`.\n\nEach native/reversed comparison averages **16 common-random-number technical draws**. Technical draws are nested measurements, not inferential replicates.\n\nThe claim-bearing paired quantity is:\n\n`DeltaR_250(p) = R_selected(p) - R_neutral(p)`.\n\nAll 18 means and intervals are plotted. Formal inference mirrors panel (c):\n\n- **R1 high-vs-low**;\n- **R2 very-high-vs-transition**;\n- **R3 `p=0.975` positive endpoint**.\n\nThe preceding four-scaffold prospective campaign already establishes that historical matching is not unique to one scaffold identity. This campaign asks how strongly that matching depends on fidelity.\n\n## 8. Dense display, sparse inference\n\nThe 18-point grid is scientifically important and is frozen unchanged for the primary figure. Every point receives a root-block mean and interval. However:\n\n- no 18-test pointwise family is performed;\n- no first-significant-`p` threshold is reported;\n- no continuous critical fidelity is estimated;\n- no smoothing or post hoc breakpoint is allowed to become claim-bearing.\n\nThe primary manuscript wording, if successful, is `concentrated in the high-heredity regime` or `increases strongly with transmission fidelity`, not `critical fidelity = x`.\n\n## 9. Frozen inference\n\nAll claim-bearing contrasts are computed **within root-seed block first**.\n\n- 50,000 nonparametric root-block bootstrap resamples;\n- exact one-sided sign test on the 30 block-level contrast values, with zero counted nonpositive;\n- Holm adjustment separately within `C_DOWN` and `R_SPEC`;\n- each three-test family uses a two-sided 98.333% root-block bootstrap interval for familywise 95% coverage;\n- bootstrap root seed `{BOOT_SEED}`;\n- exploratory outcomes are not included in confirmatory estimates.\n\n## 10. Secondary context\n\nEndpoint fitness and selected-minus-neutral `DeltaF_250(p)` are archived as non-primary context and for technical sanity checks. Corrected sequence-specific MI is **not required** for promotion of Figure 4(c,d) and is not a claim-bearing endpoint in this campaign.\n\n## 11. Validation gate before production\n\nProduction is blocked until `ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md` is completed. Required checks include:\n\n- canonical replay of archived `beta=3` inheritance-sweep conditions;\n- exact generation-0 selected/neutral identity;\n- exact shared ancestor initialization across all 18 fidelities in each block;\n- fidelity-specific propagation stream and mode-paired RNG audit;\n- deterministic `C_down` replay against archived states;\n- native/reversed specificity CRN verification;\n- explicit validation that the 16-draw assay preserves the estimand used by the exploratory 4-draw assay while increasing only technical precision;\n- synthetic block-bootstrap, exact sign-test, and Holm tests;\n- exact 1080-row manifest completeness and dry-run output-schema validation.\n\nA scientific or estimator change after outcome generation requires a versioned reopen.\n\n## 12. Production and inspection policy\n\nAfter validation, the entire 1080-run manifest is authorized as one campaign. No interim scientific inference, optional stopping, seed replacement, or selective rerunning is permitted. Technical logs may be inspected only for crashes, corruption, or invariant failures. Failed run IDs are rerun with the same frozen seed and configuration.\n\n## 13. Success boundary\n\nStrong, narrow, and no-support criteria are frozen separately in `SUCCESS_CRITERIA_v1.0.0.md`. Full promotion of both panels requires strong support in both endpoint families plus validation, completeness, and reproducibility gates.\n\n## 14. Scope boundary\n\nA successful campaign supports only the claim that, **within the tested canonical Model B domain**, selection-generated downward causal constraint and historical scaffold specificity are strongly concentrated in the high-transmission-fidelity regime.\n\nIt does not establish a continuous critical threshold, full Walker-Davies reversal, scaffold endogenization, top-down dominance, or autonomous agency.\n'''
(ROOT/'CONFIRMATORY_PLAN_v1.0.0.md').write_text(plan)

success=f'''# Success, Narrow-Support, No-Support, and Stop Criteria {VERSION}\n\nThese criteria are frozen before confirmatory production.\n\n## C_DOWN family\n\nEach of `C1-C3` passes only if:\n\n1. the mean block-level contrast is > 0;\n2. the lower bound of its two-sided 98.333% root-block bootstrap interval is > 0;\n3. the Holm-adjusted one-sided exact sign-test p-value is < 0.05 within the three-test family.\n\n`C_DOWN-strong` requires all three tests to pass. In addition, all five displayed high-fidelity means at `p={{0.90,0.925,0.95,0.975,1.0}}` must be directionally positive.\n\n## R_SPEC family\n\nApply the same criteria to `R1-R3`. `R_SPEC-strong` requires all three tests plus positive means at all five `p>=0.90` display points.\n\n## Overall strong support / promotion gate\n\nFigure 4(c,d) may be relabeled as **primary prospectively confirmed evidence** only if:\n\n- `C_DOWN-strong` passes;\n- `R_SPEC-strong` passes;\n- all 1080 frozen run IDs complete or are technically rerun under identical frozen specifications;\n- validation and deterministic analysis-replay gates pass;\n- no scientific model, estimator, seed, endpoint, fidelity value, or contrast is changed after outcome inspection.\n\nPermitted result form:\n\n> Within the tested canonical Model B domain, selection-generated downward causal constraint and historical scaffold specificity were strongly concentrated in the high-transmission-fidelity regime and increased further toward very high fidelity.\n\nThe exact shape of the 18-point curves may be described descriptively. A continuously estimated critical fidelity may not be claimed.\n\n## Narrow-support branches\n\n### N1 - C-down confirmed, specificity incomplete\nIf `C_DOWN-strong` passes but `R_SPEC-strong` fails, panel (c) may be promoted; panel (d) remains exploratory/partially confirmed.\n\n### N2 - specificity confirmed, C-down incomplete\nIf `R_SPEC-strong` passes but `C_DOWN-strong` fails, panel (d) may be promoted only as a specificity result; panel (c) remains exploratory/partially confirmed.\n\n### N3 - high-vs-low confirmed but further high-fidelity strengthening not confirmed\nIf `C1/C3` and/or `R1/R3` pass but `C2` and/or `R2` fail, use `concentrated at high fidelity` wording but do not claim continued strengthening from transition to very-high fidelity for the affected endpoint.\n\n### N4 - positive endpoint at p=0.975 not confirmed\nIf `C3` or `R3` fails, do not use the earlier exploratory `p=0.975` value as a substitute. The corresponding panel cannot receive full confirmatory status.\n\n## No-support criterion\n\nDo not promote the affected panel if its core high-vs-low contrast (`C1` or `R1`) fails, or if a favorable conclusion would require changing the frozen grid, seed set, estimator, or inferential rule after viewing outcomes.\n\nFailure here does not alter the already frozen four-scaffold or scaffold-strength confirmatory results.\n\n## Stop/reopen rules\n\n- No production if validation fails.\n- Technical failures are rerun with the same run ID, seed, and configuration.\n- Scientific/estimator defects require a new version before generating/replacing affected outcomes.\n- Do not thin the 18-point grid after results are seen.\n- Do not add fidelities or retrospectively declare the first significant point a critical threshold.\n- Null, negative, and boundary outcomes are frozen with positive outcomes.\n'''
(ROOT/'SUCCESS_CRITERIA_v1.0.0.md').write_text(success)

seedplan=f'''# Seed Plan {VERSION}\n\n- 30 independent root-seed blocks.\n- Each root seed generates one ancestral sequence population shared across all 18 fidelity values and both modes.\n- 36 evolutionary trajectories per block; 1080 total.\n- Root seed is the clustering/inferential unit for all cross-fidelity contrasts.\n\n## Deterministic derivation\n\nFor block `b`, hash `MODEL_B_DCC_FIDELITY_CONFIRM|v1.0.0|block<NN>|nonce<k>` with SHA-256 and interpret the first four bytes as an unsigned little-endian uint32. Increment nonce only on collision or overlap with the frozen prior-seed exclusion set.\n\n## RNG stream policy\n\n- `fidelity-initialization`: excludes `p` and mode, guaranteeing an identical ancestor across the complete within-block sweep.\n- `fidelity-g0-observation`: excludes `p` and mode.\n- `fidelity-propagation|<p_id>`: includes fidelity and excludes mode; selected/neutral are CRN-paired within fidelity, while different fidelities have independent purpose-separated propagation streams.\n- `fidelity-endpoint-observation|<p_id>`: includes fidelity and excludes mode.\n- `fidelity-specificity-crn|<p_id>`: excludes mode and native/reversed mapping, giving CRN pairing across native/reversed and selected/neutral assays at that fidelity.\n- bootstrap uses a separate root seed `{BOOT_SEED}` and never shares simulation RNG state.\n\nThe frozen ledger is `SEED_LEDGER_v1.0.0.csv`; the exclusion provenance is `SEED_EXCLUSION_AUDIT_v1.0.0.json`.\n'''
(ROOT/'SEED_PLAN_v1.0.0.md').write_text(seedplan)

check=f'''# Estimator and Preproduction Validation Checklist {VERSION}\n\n**Production remains unauthorized until every required item passes.**\n\n## Canonical model / replay\n- [ ] Confirm scientific commit `{COMMIT}` or byte-identical source snapshot.\n- [ ] Replay at least archived `beta=3, p=0.975` selected and neutral trajectories with archived seeds and verify generation-0 and generation-250 fitness/C-down against archived values to numerical tolerance.\n- [ ] Verify the variable-`p` reproduction function preserves canonical draw order and matches `p=0.975` archived replay.\n\n## Blocking and RNG\n- [ ] Same block: all 18 fidelity conditions initialize to byte-identical ancestral sequence populations.\n- [ ] Same block/fidelity: selected and neutral generation-0 populations and observations are identical.\n- [ ] Different blocks diverge under initialization.\n- [ ] Propagation streams are fidelity-specific and selected/neutral mode-paired.\n- [ ] No stream key accidentally depends on selected/neutral mode where CRN pairing is required.\n- [ ] Same seed/config replays exactly.\n\n## `C_down`\n- [ ] Confirm expectation-level JSD implementation uses bits.\n- [ ] Confirm intact and erased distributions use identical `P(Z|M,S)`.\n- [ ] Confirm erasure is exactly `P(S,M)->P(S)P(M)` with marginals preserved.\n- [ ] Replay archived states and match archived `C_down` values.\n- [ ] Verify `C_down=0` for a synthetic factorized `P(S,M)` case to tolerance.\n\n## Historical specificity\n- [ ] Confirm native mapping `[2,0,3,1]` and reversed mapping `[1,3,0,2]`.\n- [ ] Confirm `R=F_native-F_reversed`.\n- [ ] Confirm 16 common-random-number draws use identical local-state uniforms for native/reversed within each draw.\n- [ ] Confirm technical draws are averaged before block-level inference.\n- [ ] On archived states, compare 4-draw and 16-draw assays: estimand/orientation must agree; only technical precision is changed.\n\n## Statistics\n- [ ] Synthetic root-block bootstrap test recovers known mean/CI.\n- [ ] Exact one-sided sign test counts zero as nonpositive.\n- [ ] Holm correction verified on a hand-calculated three-test example.\n- [ ] 98.333% two-sided interval quantiles verified.\n- [ ] Contrasts are formed within block before resampling.\n- [ ] No pointwise 18-fidelity significance search appears in the confirmatory analysis.\n\n## Manifest / dry run\n- [ ] Run manifest has exactly 1080 unique run IDs.\n- [ ] 30 blocks x 18 fidelities x 2 modes is exact and complete.\n- [ ] Every block contains the exact frozen 18-point grid.\n- [ ] Every block/fidelity has exactly one selected and one neutral run.\n- [ ] All rows remain `production_authorized=false` until formal authorization.\n- [ ] Dry run validates expected state/metrics paths without generating scientific outcomes.\n\n## Authorization\n- [ ] Validation report is versioned and frozen.\n- [ ] Decision log records PASS with no scientific amendment, or any preproduction technical amendment is documented before production.\n- [ ] Authorized manifest is created only after all gates pass.\n'''
(ROOT/'ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md').write_text(check)

execution=f'''# Run Execution Specification {VERSION}\n\n## Frozen production size\n- 30 root blocks\n- 18 transmission fidelities per block\n- 2 modes per fidelity\n- **1080 evolutionary runs**\n\n## Execution order\nOrder may be parallelized or permuted for compute efficiency; scientific identity is determined solely by frozen `run_id`, seed, fidelity, mode, and configuration.\n\n## Required per-run outputs\n- generation-0 fitness/hash linkage to the shared ancestor;\n- generation-250 population state;\n- generation-250 mean fitness;\n- generation-250 deterministic `C_down`;\n- generation-250 16-draw CRN native/reversed specificity components and averaged `R`;\n- software/source hash and runtime metadata.\n\n## Failure handling\nA crashed/corrupt run is rerun using the exact same run ID and frozen inputs. No replacement seed is allowed.\n\n## Scientific inspection\nNo inferential or curve-shape inspection until the frozen 1080-run campaign is complete, except technical checks needed to diagnose execution failures.\n'''
(ROOT/'RUN_EXECUTION_SPEC_v1.0.0.md').write_text(execution)

decisions=f'''# Decisions Log\n\n## 2026-09-05 — Freeze Transmission-Fidelity Confirmatory Plan {VERSION}\n\n**Decision:** Freeze an independent campaign to determine whether Figure 4(c,d) can be promoted from exploratory to primary prospectively confirmed evidence.\n\n### Frozen choices\n1. Preserve the **exact 18-point exploratory fidelity grid**; do not thin it.\n2. Use 30 new root-seed blocks, all 18 fidelities within each block, selected-neutral pairing: 1080 runs.\n3. Keep canonical Model B fixed at `beta=3`, `Theta=1.2`, SCF0, 250 generations.\n4. Primary endpoint families are generation-250 `Delta C_down` and `Delta R`.\n5. Keep all 18 points for descriptive figure density, but restrict inference to three preregistered contrasts per family.\n6. Do not estimate or claim a continuous critical fidelity.\n7. Increase specificity technical averaging from the exploratory 4 draws to 16 CRN draws, matching the later confirmatory standard; this changes technical precision only, not the `R` estimand. Validation against archived states is mandatory before production.\n8. Root-seed block is the inferential unit.\n9. No interim scientific outcome inspection or optional stopping.\n10. Production is not authorized by this freeze.\n\n### Evidence-status rule\nExisting inheritance-sweep data remain exploratory until this campaign is completed and frozen. Existing four-scaffold and scaffold-strength prospective results are unaffected.\n'''
(ROOT/'DECISIONS_LOG.md').write_text(decisions)

# Preserve generator for repo-oriented provenance.
shutil.copy2('/mnt/data/create_fidelity_confirmatory_plan.py',ROOT/'PLAN_GENERATOR_v1.0.0.py')

# SHA manifest excluding itself, then zip.
sha_rows=[]
for f in sorted(ROOT.iterdir()):
    if f.name=='SHA256_MANIFEST.csv': continue
    if f.is_file():
        h=hashlib.sha256(f.read_bytes()).hexdigest()
        sha_rows.append({'file':f.name,'sha256':h,'bytes':f.stat().st_size})
pd.DataFrame(sha_rows).to_csv(ROOT/'SHA256_MANIFEST.csv',index=False)

zip_path=Path('/mnt/data/MODEL_B_DCC_TRANSMISSION_FIDELITY_CONFIRMATORY_PLAN_v1.0.0.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(ROOT.rglob('*')):
        if f.is_file(): z.write(f,arcname=str(Path(ROOT.name)/f.relative_to(ROOT)))

print('created',ROOT)
print('zip',zip_path,zip_path.stat().st_size)
print('runs',len(runs),'blocks',len(seeds),'p',len(P_VALUES),'prior seeds',len(prior),'overlap',len(chosen&prior))
print('zip sha256',hashlib.sha256(zip_path.read_bytes()).hexdigest())
print('seed nonce max',seeds.nonce.max())
