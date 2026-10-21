# Scaffold-Strength Confirmatory Plan v1.0.0

**Project:** Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model  
**Campaign:** prospective confirmation of the scaffold-strength regime structure  
**Status:** **DESIGN FROZEN; VALIDATION REQUIRED; CONFIRMATORY PRODUCTION NOT AUTHORIZED**  
**Date:** 2026-09-05  
**Scientific source:** canonical Model B, commit `2c7d78694579755402c0a1896e109b29dec4d6a0`

## 1. Purpose

The exploratory scaffold-strength sweep is scientifically central enough to appear in the main manuscript figure sequence, but its regime structure must not be relabeled as prospectively confirmed without an independent campaign. This plan freezes that campaign before any new outcomes are generated.

The campaign tests four linked statements represented by the four panels of the scaffold-strength figure:

1. stronger externally imposed positional regularity lowers ancestral fitness;
2. selection, rather than neutral propagation alone, produces substantial fitness recovery over the viable intermediate/high-strength regime;
3. selection-generated downward causal constraint rises across that regime, is partly masked under very strong training fields, and disappears when the canonical fitness regime collapses;
4. selection-generated historical scaffold specificity shows the same expression-versus-latency structure.

The existing exploratory sweep and extension are design/calibration evidence only and are not pooled with this campaign for confirmatory inference.

## 2. Fixed canonical model

No model mechanism is changed. Frozen parameters are:

| Quantity | Value |
|---|---:|
| model units | 80 |
| oligomer slots per unit | 8 |
| sequence length | 60 |
| alphabet | 4 |
| motif window | 5 |
| local-state classes | 4 |
| positional segments | 4 |
| canonical scaffold mapping | `[2,0,3,1]` |
| affinity matrix | canonical 1024 x 4, seed 123 |
| `Theta` | 1.2 |
| inheritance `p` | 0.975 |
| mutation rate | 0.001 |
| reward / penalty | 2.0 / 0.5 |
| fitness floor | 0.1 |
| evolutionary duration | 250 updates |

The study does not alter the fitness floor. The high-strength collapse is therefore interpreted as a boundary of **canonical Model B's tested fitness regime**, not a universal optimum or law of physical constraint.

## 3. Frozen strength grid

Seven broad, prespecified anchors are used:

| ID | `beta/Theta` | `beta` | role |
|---|---:|---:|---|
| R0P0 | 0.0 | 0.0 | no-scaffold baseline |
| R1P5 | 1.5 | 1.8 | low-strength anchor |
| R2P5 | 2.5 | 3.0 | intermediate anchor; identical to fixed-probe beta=3 condition |
| R3P0 | 3.0 | 3.6 | strong viable anchor |
| R3P5 | 3.5 | 4.2 | high-strength transition anchor |
| R4P0 | 4.0 | 4.8 | pre-collapse latent-organization anchor |
| R4P5 | 4.5 | 5.4 | fitness-floor/collapse anchor |

The grid deliberately omits the exploratory fine-scale 3.75 point. The confirmatory question is the **broad ordered regime structure**, not whether an exact peak occurs at a previously observed numerical optimum.

## 4. Repeated-measures block design

There are **30 independent root-seed blocks**. Each block contains all seven strength conditions, and each strength contains one selected and one matched-neutral evolutionary run:

`30 blocks x 7 strengths x 2 modes = 420 evolutionary runs`.

The independent inferential unit is the **root-seed block**. Ratio conditions and selected/neutral trajectories are repeated/nested observations inside that block.

Within each block:

- all seven ratios start from the same ancestral sequence population;
- selected and neutral members at a given ratio share initialization and purpose-matched stochastic streams;
- evolutionary propagation streams are ratio-specific but mode-paired;
- cross-ratio comparisons are therefore analyzed as paired repeated-measures contrasts, not as independent samples.

This design reproduces the blocking logic of the exploratory sweep while using completely new root seeds.

## 5. New-seed requirement

The 30 root seeds are frozen in `SEED_LEDGER_v1.0.0.csv` and are deterministically derived from the namespace `MODEL_B_DCC_STRENGTH_CONFIRM|v1.0.0|...`.

They have zero overlap with the seed values found in the archived exploratory ratio-sweep ledgers and the preceding DCC confirmatory seed ledger available in the project runtime. Seed reuse across strengths **within a block** is intentional blocking; purpose-separated RNG keys ensure ratio-specific evolutionary propagation.

## 6. Panel (a): ancestral physical cost

Let `F0_b(r)` be generation-0 population mean fitness for block `b` evaluated under training scaffold strength `r`. Selected and neutral generation-0 states must be identical.

The confirmatory cost contrasts are:

- `A1 = F0(0.0) - F0(2.5) > 0`;
- `A2 = F0(2.5) - F0(4.0) > 0`.

These broad contrasts test progressive physical cost without requiring every adjacent point to differ significantly.

## 7. Panel (b): zero-centered evolutionary fitness response

The revised primary display is frozen as:

`G_selected(r) = F250_selected(r) - F0(r)`

and

`G_neutral(r) = F250_neutral(r) - F0(r)`.

The formal selection contrast is

`DeltaF(r) = G_selected(r) - G_neutral(r) = F250_selected(r) - F250_neutral(r)`.

The viable-window set is `V = {1.5, 2.5, 3.0, 3.5, 4.0}`.

Primary fitness contrasts:

- `F1 = mean_V DeltaF(r) > 0`;
- `F2 = DeltaF(3.0) - DeltaF(4.5) > 0`.

All five ratio-specific means in `V` must also be positive for strong support. `G_neutral(r)` is reported with intervals as a zero-centered reference; no post hoc equivalence margin may be introduced after results are seen.

## 8. Panel (c): downward causal constraint

For each evolved population, the primary estimator is the already validated expectation-level quantity

`C_down = D_JS[P_intact(S,Z) || P_erased(S,Z)]`,

where `P_erased(S,M)=P(S)P(M)` and intact and erased distributions use the same `P(Z|M,S)` readout.

Two assays are frozen:

- **training-strength assay:** probe at the same `beta` under which the lineage evolved;
- **fixed moderate assay:** probe every lineage at `beta=3.0` (`beta/Theta=2.5`).

The selection-generated quantities are `DeltaC_train` and `DeltaC_probe3`, each selected minus matched neutral.

Define low `L={0.0,1.5}` and high viable `H={3.0,3.5,4.0}`.

Primary C-down contrasts:

- `C1 = mean_H DeltaC_train - mean_L DeltaC_train > 0`;
- `C2 = mean_H DeltaC_train - DeltaC_train(4.5) > 0`;
- `C3 = DeltaC_probe3(4.0) - DeltaC_train(4.0) > 0`;
- `C4 = DeltaC_probe3(4.0) - DeltaC_probe3(4.5) > 0`.

These test rise, collapse, and latent-versus-expressed separation without claiming a sharply located optimum.

## 9. Panel (d): historical scaffold specificity

Use the canonical native mapping `[2,0,3,1]` and the prespecified reversed mapping `[1,3,0,2]`.

For each mode and assay:

`R = F_native - F_reversed`,

with 16 common-random-number technical draws per native/reversed pair. The selection-generated quantity is

`DeltaR = R_selected - R_neutral`.

Training-strength and fixed-`beta=3` assays are both frozen. Primary specificity contrasts mirror panel (c):

- `R1 = mean_H DeltaR_train - mean_L DeltaR_train > 0`;
- `R2 = mean_H DeltaR_train - DeltaR_train(4.5) > 0`;
- `R3 = DeltaR_probe3(4.0) - DeltaR_train(4.0) > 0`;
- `R4 = DeltaR_probe3(4.0) - DeltaR_probe3(4.5) > 0`.

The preceding four-scaffold prospective campaign already establishes that historical matching is not unique to one mapping. This sweep uses the canonical native/reversed contrast only to test how the **magnitude and expression of historical matching vary with scaffold strength**.

## 10. Frozen inference

All claim-bearing contrasts are computed first within each root-seed block.

- bootstrap: 50,000 nonparametric root-block resamples;
- exact one-sided sign test on block-level contrast values, with zero counted as nonpositive;
- Holm adjustment within each prespecified family (`A_COST`, `F_RECOVERY`, `C_DOWN`, `R_SPEC`);
- two-test families use two-sided 97.5% bootstrap intervals for familywise 95% coverage;
- four-test families use two-sided 98.75% bootstrap intervals for familywise 95% coverage;
- no pointwise ratio-by-ratio p-value fishing;
- checkpoint trajectories are descriptive only.

The complete formulas are frozen in `CONTRAST_MANIFEST_v1.0.0.csv`.

## 11. Fitness-floor boundary rule

`r=4.5` is called a **collapse/floor anchor** only if both selected and neutral generation-250 mean fitness are `<=0.20`. If this condition is not met prospectively, the ratio remains a high-strength anchor and manuscript wording must use `turnover` or `loss of selection-dependent effect`, not `fitness-floor collapse`.

No new stronger ratio may be added after outcome inspection to rescue this wording.

## 12. Validation gates before production

Production is blocked until all items in `ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md` pass. The required gate includes:

- canonical-model replay against archived exploratory conditions;
- same-seed determinism and different-seed divergence;
- exact selected-neutral generation-0 identity;
- exact shared ancestor initialization across all seven ratios within a block;
- ratio-specific propagation and mode-paired CRN stream audit;
- replay of the validated `C_down` estimator on archived states;
- fixed-`beta=3` probe verification;
- 16-draw native/reversed CRN verification;
- synthetic bootstrap/sign-test/Holm checks;
- 420-row run-manifest completeness and dry-run schema validation.

Any scientific or estimator change requires a new plan version before confirmatory outcomes are generated.

## 13. Production outputs

Expected minimum outputs:

- 420 evolutionary run records;
- 30 independent root-seed blocks;
- 210 selected-neutral ratio pairs;
- 420 generation-250 population states;
- 30 deduplicated ancestor sequence states plus explicit linkage, or 420 g0 files if simpler;
- complete endpoint fitness, `C_down`, and historical-specificity assays for every run;
- zero missing run IDs relative to `RUN_MANIFEST_v1.0.0.csv`.

## 14. Scope and wording boundary

A successful campaign may promote the scaffold-strength regime structure from exploratory evidence to prospectively confirmed primary evidence **within the tested canonical Model B domain**.

It does not establish:

- a universal optimal physical-constraint strength;
- a continuous critical threshold;
- full Walker-Davies information-flow reversal;
- top-down dominance;
- autonomous agency;
- scaffold endogenization or self-maintenance.

The external scaffold remains externally supplied throughout evolution.

## 15. Figure consequence

If the strong-support gate passes, the current four-panel scaffold-strength figure may be rebuilt from these confirmatory source tables and presented as a primary confirmatory manuscript figure. Panel (b) is frozen to the zero-centered `selected - ancestral` and `neutral - ancestral` representation. The large `EXPLORATORY DISCOVERY SWEEP` banner must then be removed.

If strong support does not pass, the figure may remain in the main text because it is scientifically central, but its exploratory/partially confirmed status must remain explicit.
