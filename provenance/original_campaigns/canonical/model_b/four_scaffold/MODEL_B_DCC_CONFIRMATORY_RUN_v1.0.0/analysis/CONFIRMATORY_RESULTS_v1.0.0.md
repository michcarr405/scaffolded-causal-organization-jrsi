# Confirmatory results v1.0.0

**Working paper:** *Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model*

**Frozen-decision classification:** `STRONG_PROSPECTIVE_SUPPORT`

## Gates

- Preproduction validation: **PASS (56/56 checks)**.
- Production completeness: **PASS (120 paired blocks; 240 evolutionary runs; no missing outputs)**.
- Scientific protocol changed after outcome inspection: **No**.

## Requirement A - independent canonical confirmation

SCF0 mean `Delta C_down` = **0.004679 bits**, 95% bootstrap CI **[0.004257, 0.005116]**; positive blocks **30/30**; one-sided exact sign p = **9.313e-10**.
`A-core`: **PASS**.

## Mapping-specific confirmatory families

| Family | Scaffold | Mean | 98.75% CI | Positive/30 | Raw sign p | Holm p | Pass |
|---|---|---:|---:|---:|---:|---:|:---:|
| D_primary | SCF0 | 0.004679 | [0.004144, 0.005234] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| D_primary | SCF1 | 0.003870 | [0.003220, 0.004523] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| D_primary | SCF2 | 0.004420 | [0.003845, 0.005032] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| D_primary | SCF3 | 0.003785 | [0.003274, 0.004310] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| H_historical_match | SCF0 | 12.039781 | [11.191627, 12.904068] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| H_historical_match | SCF1 | 11.814994 | [10.775359, 12.890985] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| H_historical_match | SCF2 | 11.819079 | [11.006093, 12.700514] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| H_historical_match | SCF3 | 11.963053 | [11.105160, 12.822432] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| A_unitshuffle | SCF0 | 0.004684 | [0.004146, 0.005248] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| A_unitshuffle | SCF1 | 0.003874 | [0.003234, 0.004539] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| A_unitshuffle | SCF2 | 0.004420 | [0.003834, 0.005034] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |
| A_unitshuffle | SCF3 | 0.003785 | [0.003275, 0.004321] | 30/30 | 9.313e-10 | 3.725e-09 | PASS |

`B1-strong` (primary `C_down` across all four scaffolds): **PASS**.
`B2-strong` (historical-match cross-evaluation across all four scaffolds): **PASS**.
`C-strong` (alternative unit-stratified marginal-preserving erasure across all four scaffolds): **PASS**.

## Equal-weight stratified pooled descriptive/inferential summaries

- Primary `Delta C_down`: mean **0.004189 bits**, 95% CI **[0.003961, 0.004420]**.
- Historical-match `Delta H`: mean **11.909226 fitness units**, 95% CI **[11.554064, 12.273178]**.
- Alternative-erasure `Delta C_down`: mean **0.004191 bits**, 95% CI **[0.003963, 0.004420]**.

## Selected-minus-neutral cross-evaluation matrix

Rows are the scaffold under which the population evolved; columns are the probe scaffold. Entries are mean selected-minus-neutral probe fitness differences. The final column is the predeclared diagonal historical advantage `Delta H`.

| Training | SCF0 | SCF1 | SCF2 | SCF3 | Delta H |
|---|---:|---:|---:|---:|---:|
| SCF0 | 11.4918 | 0.1897 | -1.8420 | 0.0084 | **12.0398** |
| SCF1 | 0.3694 | 11.0937 | 0.1783 | -2.7115 | **11.8150** |
| SCF2 | -1.6273 | -0.0179 | 11.3719 | 0.3035 | **11.8191** |
| SCF3 | 0.5229 | -2.7348 | 0.4685 | 11.3819 | **11.9631** |

## Frozen decision

All predeclared strong-support requirements passed. The frozen permitted claim is therefore supported within the tested canonical Model B regime:

> Within the tested canonical Model B regime, selection prospectively and reproducibly generated scaffold-history-specific inherited organization whose preservation changed lower-level chemical-state distributions; the effect generalized across four prespecified scaffold identities and survived an independently constructed marginal-preserving relational erasure.

## Claim boundary

These results do **not** establish full Walker-Davies information-flow reversal, top-down dominance, autonomous agency, or scaffold endogenization. The scaffold remains externally specified in canonical Model B.

Checkpoint trajectories are retained as descriptive outputs only; no checkpoint-wise confirmatory p-values were computed.

