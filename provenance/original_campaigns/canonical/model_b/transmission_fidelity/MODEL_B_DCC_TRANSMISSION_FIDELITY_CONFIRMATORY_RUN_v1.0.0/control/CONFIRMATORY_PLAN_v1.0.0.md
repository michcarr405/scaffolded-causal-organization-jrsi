# Transmission-Fidelity Confirmatory Plan v1.0.0

**Project:** Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model  
**Campaign:** prospective confirmation of Figure 4(c,d) heredity dependence  
**Status:** **DESIGN FROZEN; VALIDATION REQUIRED; CONFIRMATORY PRODUCTION NOT AUTHORIZED**  
**Date:** 2026-09-05  
**Scientific source:** canonical Model B, commit `2c7d78694579755402c0a1896e109b29dec4d6a0`

## 1. Purpose

Figure 4 panels (c) and (d) currently use an exploratory transmission-fidelity sweep. They are central to the manuscript because they address whether selection-generated downward causal constraint and historical scaffold specificity depend strongly on hereditary fidelity. This plan freezes an independent new-seed campaign before any new outcomes are generated.

The campaign does **not** attempt to locate a continuously estimated critical fidelity. It prospectively tests the previously observed **high-heredity regime concentration and strengthening** while preserving the full density of the original discrete sweep.

Exploratory data are design/calibration evidence only and will not be pooled with this campaign for confirmatory inference.

## 2. Canonical Model B is unchanged

| Quantity | Frozen value |
|---|---:|
| model units | 80 |
| oligomer slots per unit | 8 |
| sequence length | 60 |
| alphabet | 4 |
| motif window | 5 |
| local-state classes | 4 |
| positional segments | 4 |
| historical scaffold | SCF0 `[2,0,3,1]` |
| reversed probe scaffold | `[1,3,0,2]` |
| affinity matrix | canonical 1024 x 4, seed 123 |
| `Theta` | 1.2 |
| `beta` | 3.0 |
| `beta/Theta` | 2.5 |
| mutation rate | 0.001 |
| reward / penalty | 2.0 / 0.5 |
| fitness floor | 0.1 |
| duration | 250 updates |

Only transmission fidelity `p` varies.

## 3. Exact 18-point fidelity grid is preserved

The prospective grid is exactly:

`[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975, 1.0]`

This preserves the exploratory sweep's dense resolution, especially from `p=0.70` through `1.00`. No values are thinned, shifted, inserted, or deleted. The density is retained to display regime geometry; it does not authorize 18 independent pointwise significance searches.

## 4. Repeated-measures paired-block design

There are **30 independent root-seed blocks**. Every block contains all 18 fidelity values, and every fidelity contains one selected and one matched-neutral evolutionary trajectory:

`30 blocks x 18 fidelities x 2 modes = 1080 evolutionary runs`.

The **root-seed block** is the inferential unit. Fidelity values and selected/neutral trajectories are repeated/nested observations within each block.

Within each block:

- all fidelities and both modes begin from the same ancestral sequence population;
- selected and neutral trajectories at a given fidelity use purpose-matched common random streams;
- propagation streams are fidelity-specific but mode-paired;
- cross-fidelity contrasts are therefore paired repeated-measures contrasts, not independent-sample comparisons.

## 5. New-seed requirement

Thirty root seeds are frozen in `SEED_LEDGER_v1.0.0.csv`, derived deterministically from the namespace `MODEL_B_DCC_FIDELITY_CONFIRM|v1.0.0|...`.

The plan generator conservatively scanned accessible prior seed/manifest CSVs and excluded previously used uint32 seed values. The frozen audit is `SEED_EXCLUSION_AUDIT_v1.0.0.json`. Seed reuse **within** a block across fidelity values is intentional blocking, not pseudoreplication.

## 6. Panel (c): downward causal constraint

For each generation-250 population:

`C_down = D_JS[P_intact(S,Z) || P_erased(S,Z)]`,

where relational erasure applies `P(S,M) -> P(S)P(M)` and intact and erased populations are passed through the same canonical `P(Z|M,S)` readout.

The claim-bearing paired quantity is:

`DeltaC_down_250(p) = C_down_selected(p) - C_down_neutral(p)`.

All 18 means and uncertainty intervals are plotted. Formal inference is limited to:

- **C1 high-vs-low:** mean over `p={0.90,0.925,0.95,0.975,1.0}` minus mean over `p={0,0.1,0.2,0.3,0.4,0.5,0.6}` > 0;
- **C2 very-high-vs-transition:** mean over `p={0.95,0.975,1.0}` minus mean over `p={0.85,0.875,0.90}` > 0;
- **C3 manuscript endpoint:** `DeltaC_down_250(0.975) > 0`.

These tests confirm concentration and strengthening in the high-heredity regime without retrospectively choosing a first significant fidelity.

## 7. Panel (d): historical scaffold specificity

Historical specificity uses the canonical native scaffold `[2,0,3,1]` and prespecified reversed scaffold `[1,3,0,2]` at the same fixed `beta=3`. For each evolved population:

`R = F_native - F_reversed`.

Each native/reversed comparison averages **16 common-random-number technical draws**. Technical draws are nested measurements, not inferential replicates.

The claim-bearing paired quantity is:

`DeltaR_250(p) = R_selected(p) - R_neutral(p)`.

All 18 means and intervals are plotted. Formal inference mirrors panel (c):

- **R1 high-vs-low**;
- **R2 very-high-vs-transition**;
- **R3 `p=0.975` positive endpoint**.

The preceding four-scaffold prospective campaign already establishes that historical matching is not unique to one scaffold identity. This campaign asks how strongly that matching depends on fidelity.

## 8. Dense display, sparse inference

The 18-point grid is scientifically important and is frozen unchanged for the primary figure. Every point receives a root-block mean and interval. However:

- no 18-test pointwise family is performed;
- no first-significant-`p` threshold is reported;
- no continuous critical fidelity is estimated;
- no smoothing or post hoc breakpoint is allowed to become claim-bearing.

The primary manuscript wording, if successful, is `concentrated in the high-heredity regime` or `increases strongly with transmission fidelity`, not `critical fidelity = x`.

## 9. Frozen inference

All claim-bearing contrasts are computed **within root-seed block first**.

- 50,000 nonparametric root-block bootstrap resamples;
- exact one-sided sign test on the 30 block-level contrast values, with zero counted nonpositive;
- Holm adjustment separately within `C_DOWN` and `R_SPEC`;
- each three-test family uses a two-sided 98.333% root-block bootstrap interval for familywise 95% coverage;
- bootstrap root seed `2481907731`;
- exploratory outcomes are not included in confirmatory estimates.

## 10. Secondary context

Endpoint fitness and selected-minus-neutral `DeltaF_250(p)` are archived as non-primary context and for technical sanity checks. Corrected sequence-specific MI is **not required** for promotion of Figure 4(c,d) and is not a claim-bearing endpoint in this campaign.

## 11. Validation gate before production

Production is blocked until `ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md` is completed. Required checks include:

- canonical replay of archived `beta=3` inheritance-sweep conditions;
- exact generation-0 selected/neutral identity;
- exact shared ancestor initialization across all 18 fidelities in each block;
- fidelity-specific propagation stream and mode-paired RNG audit;
- deterministic `C_down` replay against archived states;
- native/reversed specificity CRN verification;
- explicit validation that the 16-draw assay preserves the estimand used by the exploratory 4-draw assay while increasing only technical precision;
- synthetic block-bootstrap, exact sign-test, and Holm tests;
- exact 1080-row manifest completeness and dry-run output-schema validation.

A scientific or estimator change after outcome generation requires a versioned reopen.

## 12. Production and inspection policy

After validation, the entire 1080-run manifest is authorized as one campaign. No interim scientific inference, optional stopping, seed replacement, or selective rerunning is permitted. Technical logs may be inspected only for crashes, corruption, or invariant failures. Failed run IDs are rerun with the same frozen seed and configuration.

## 13. Success boundary

Strong, narrow, and no-support criteria are frozen separately in `SUCCESS_CRITERIA_v1.0.0.md`. Full promotion of both panels requires strong support in both endpoint families plus validation, completeness, and reproducibility gates.

## 14. Scope boundary

A successful campaign supports only the claim that, **within the tested canonical Model B domain**, selection-generated downward causal constraint and historical scaffold specificity are strongly concentrated in the high-transmission-fidelity regime.

It does not establish a continuous critical threshold, full Walker-Davies reversal, scaffold endogenization, top-down dominance, or autonomous agency.
