# Confirmatory Plan v1.0.0

**Project:** Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model  
**Status:** DESIGN FROZEN; VALIDATION REQUIRED; CONFIRMATORY PRODUCTION NOT YET AUTHORIZED  
**Date:** 2026-09-04  
**Scientific source:** canonical Model B, commit `2c7d78694579755402c0a1896e109b29dec4d6a0`

## 1. Purpose

This plan freezes the smallest confirmatory campaign intended to test three outstanding requirements without reopening exploratory discovery:

- **A. Independent new-seed confirmation** of selected-minus-neutral `Delta C_down`.
- **B. Generalization across multiple scaffold identities**, including cross-evaluation for historical matching.
- **C. Robustness to one alternative marginal-preserving relational-erasure intervention.**

The four packages under `03_EXPLORATORY_RESULTS/` are calibration and design evidence only. They are not confirmatory results and may not be pooled with the confirmatory campaign for claim-bearing inference.

## 2. Fixed scientific scope

The campaign preserves canonical Model B. No model mechanism is added. The only new analysis object is the alternative relational-erasure estimator described in section 7.

Fixed canonical parameters:

| Quantity | Frozen value |
|---|---:|
| model units `N` | 80 |
| oligomer slots per unit | 8 |
| oligomer length `L` | 60 |
| alphabet size | 4 |
| motif window `k` | 5 |
| local-state classes | 4 |
| positional segments | 4 |
| affinity matrix | canonical 1024 x 4 matrix, affinity seed 123 |
| `Theta` | 1.2 |
| `beta` | 4.0 |
| `beta/Theta` | 3.3333333333333335 |
| compositional-transmission fidelity `p` | 0.975 |
| mutation rate `mu` | 0.001 |
| fitness reward | 2.0 |
| fitness penalty | 0.5 |
| fitness floor `F_min` | 0.1 |
| evolutionary duration | 250 population updates |

Rationale for the anchor regime: `beta=4`, `Theta=1.2`, `p=0.975` is a strong exploratory-effect condition that remains well below the later high-bias fitness-floor collapse. `p=0.975` is high but not the boundary value `p=1.0`. This choice is frozen from exploratory evidence before confirmatory outcomes are generated.

## 3. Statistical unit and pairing

The inferential unit is the **independently evolved selected-neutral paired seed block**.

For every scaffold identity and replicate:

1. selected and neutral runs use the same base seed;
2. they therefore share initialization and purpose-matched random streams;
3. the only intended mode difference is the source-selection rule;
4. the paired difference is computed before population-level inference.

Scaffold identities use different base seeds. There is **no seed reuse across scaffold identities**. Thus the campaign contains 120 independent paired blocks, not 30 blocks with four nested scaffold conditions.

Generations, motif windows, model units, local-state draws, cross-evaluation draws, and alternative-erasure shuffles are nested technical observations and never count as independent `n`.

## 4. Frozen scaffold-identity set

Four scaffold mappings are used:

| ID | segment -> favored local-state mapping |
|---|---|
| `SCF0` | `[2,0,3,1]` |
| `SCF1` | `[0,1,2,3]` |
| `SCF2` | `[1,3,0,2]` |
| `SCF3` | `[3,2,1,0]` |

`SCF0` is the canonical historical mapping. `SCF2` is the canonical reversed mapping used in earlier exploratory native-versus-reversed probes.

The set was chosen without outcome inspection by a deterministic rule: start with canonical `[2,0,3,1]`; repeatedly choose the lexicographically smallest remaining permutation that maximizes its minimum Hamming distance to the already selected set; stop at four mappings. The resulting four mappings are pairwise Hamming distance 4, so no pair shares any segment-to-state assignment.

## 5. Replicate count and run count

- 30 independent paired seed blocks per scaffold identity.
- 4 scaffold identities.
- 2 modes per block: selected and matched neutral.
- **120 independent paired blocks total.**
- **240 evolutionary runs total.**

The replicate count is a prospective 50% increase over the principal exploratory campaigns (`n=20`) and is not chosen by inspecting confirmatory outcomes. Exploratory `beta=4` results indicate that this is conservative for the canonical effect while remaining computationally compact enough to support four independent scaffold identities.

## 6. Primary `C_down` estimator and endpoint

For each evolved population, let `P_intact(S,M)` be the observed segment-motif distribution. Let

`P_erased(S,M) = P(S) P(M)`.

Both are passed through the same canonical local-state readout `P(Z|M,S)` for that population's historical scaffold, with the same affinity matrix, `beta`, `Theta`, and segment occupancy.

The primary estimator is

`C_down_primary = D_JS[P_intact(S,Z) || P_erased(S,Z)]`

in bits.

The primary selection-generated contrast is

`Delta C_down_primary = C_down_primary(selected) - C_down_primary(neutral)`.

### Primary A endpoint

The single primary endpoint for requirement A is:

- `SCF0`, generation 250, `Delta C_down_primary`.

### Confirmatory checkpoint schedule

`C_down_primary` and mean model fitness are recorded at generations:

`0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250`.

Only generation 250 is confirmatory for the frozen A/B pass criteria. Checkpoint trajectories are prespecified descriptive/mechanistic outputs and are not separately hypothesis-tested.

Population arrays are archived at generation 0 and 250. A SHA-256 population-state hash is recorded at every checkpoint.

## 7. Alternative marginal-preserving relational erasure

The alternative estimator is frozen as **unit-stratified exact-margin motif-position shuffling**.

For each evolved population and each of `K=128` technical shuffles:

1. parse the population into motif occurrences while retaining model-unit identity and fixed segment slots;
2. within each model unit independently, permute that unit's motif occurrences across its own fixed segment slots;
3. preserve exactly, for every shuffle:
   - each model unit's motif multiset;
   - global motif frequencies;
   - the number of slots in every segment;
   - population size, sequence inventory, scaffold identity, affinities, `beta`, `Theta`, and the local-state readout;
4. destroy the realized motif-segment relation within model units by random reassignment;
5. pass the scrambled `P_k(S,M)` through the same `P(Z|M,S)`;
6. compute `D_JS[P_intact(S,Z) || P_k(S,Z)]`;
7. average the 128 divergences.

Define

`C_down_unitshuffle = mean_k D_JS[P_intact(S,Z) || P_shuffle,k(S,Z)]`.

The confirmatory contrast is

`Delta C_down_unitshuffle = C_down_unitshuffle(selected) - C_down_unitshuffle(neutral)`.

The 128 shuffles are technical replicates and are averaged inside each evolved population before inferential analysis.

This is deliberately not the same estimand as deterministic factorization to `P(S)P(M)`: it measures expected divergence under a realizable, exact-margin, unit-stratified relational scramble. It therefore provides an intervention-definition robustness test while preserving stricter lower-order composition than the primary erasure.

## 8. Scaffold cross-evaluation

At generation 250, every selected and neutral population is probed under all four frozen scaffold identities using 16 common-random-number local-state draws per probe.

Within a paired block and draw, the same local-state uniform vector is used across all four probe mappings and across selected versus neutral. Probe identity and mode are excluded from the cross-evaluation CRN key.

For a population evolved under historical scaffold `j`, define

`H_j = F(probe=j) - mean_{k != j} F(probe=k)`.

Then define the selection-generated historical-match score

`Delta H_j = H_j(selected) - H_j(neutral)`.

A positive `Delta H_j` means selection created a fitness-relevant preference for the mapping under which that lineage evolved, beyond any corresponding neutral mapping bias.

The complete 4 x 4 cross-evaluation matrix is retained. The canonical native-versus-reversed secondary endpoint is

`Delta R_native/reversed = [F_SCF0 - F_SCF2]_selected - [F_SCF0 - F_SCF2]_neutral`

for `SCF0`-evolved populations.

## 9. Frozen inference

### Effect estimates

All claim-bearing estimates are computed from paired-block differences.

- Nonparametric percentile bootstrap: 50,000 replicates.
- Resampling unit: paired seed block.
- Mapping-specific bootstrap: resample the 30 blocks within that mapping.
- Pooled mapping summary: stratified bootstrap, resampling within each mapping and then averaging mapping means with equal weight.

### Confirmatory sign test

A one-sided exact binomial sign test is used as a distribution-light confirmatory check on the direction of paired-block effects.

- Null probability of positive effect: 0.5.
- Exact zero is counted as nonpositive, conservatively.

### Multiplicity

- Requirement A has one prespecified primary endpoint and is not multiplicity-adjusted.
- For each four-mapping confirmatory family, one-sided sign-test p-values are Holm-adjusted across the four mappings.
- Mapping-family effect-size intervals are two-sided 98.75% bootstrap intervals, giving Bonferroni familywise 95% coverage across four mapping-specific estimates.
- The canonical A effect is additionally reported with a two-sided 95% bootstrap interval.

The following are separate four-mapping families:

1. `Delta C_down_primary`;
2. `Delta H`;
3. `Delta C_down_unitshuffle`.

No checkpoint p-values will be generated.

## 10. Seed and RNG freeze

The 120 base seeds are frozen in `SEED_LEDGER_v1.0.0.csv`.

Seed derivation is deterministic and auditable: each seed is the little-endian unsigned 32-bit integer represented by the first four bytes of SHA-256 over the frozen namespace string

`MODEL_B_DCC_CONFIRM|v1.0.0|<scaffold_id>|rep<NN>|nonce<k>`.

The nonce is increased only if a collision or overlap is detected. The resulting ledger has 120 unique seeds and no overlap with the 20 exploratory sweep seeds.

Purpose-separated streams are required for:

- baseline initialization;
- baseline observation;
- baseline propagation;
- cross-evaluation observation;
- alternative-erasure permutations;
- bootstrap resampling.

Parallel job order must not alter results.

## 11. Required validation gates before production

Production remains blocked until all items in `ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md` pass and are recorded in a versioned validation report.

At minimum:

- canonical wrapper reproduces archived exploratory states/metrics under identical old conditions;
- same-seed determinism and different-seed divergence pass;
- selected-neutral CRN logic is verified;
- primary `C_down` limiting-case and replay tests pass;
- alternative-erasure exact-margin invariants and `K=128` convergence pass;
- cross-evaluation CRN reuse is verified;
- bootstrap/sign-test synthetic checks pass;
- expected run counts and output schemas pass a dry-run completeness audit.

If a scientific or estimator change is required, increment the plan version and regenerate the run and seed manifests before any confirmatory outcome is inspected.

## 12. Production completeness targets

Expected production objects:

- 240 evolutionary run records;
- 120 selected-neutral paired-block records;
- 30 paired blocks per scaffold identity;
- 240 generation-250 population state files;
- 240 generation-0 population states or one deduplicated ancestor state per pair with explicit linkage;
- 2,640 checkpoint records per mode-scaffold-replicate combination if stored long-form as 11 checkpoints x 240 runs;
- 120 primary paired `Delta C_down` endpoint records;
- 120 alternative-erasure paired endpoint records;
- 120 historical-match paired endpoint records;
- complete 4-probe cross-evaluation results for every run;
- zero missing run IDs relative to `RUN_MANIFEST_v1.0.0.csv`.

## 13. Scope and wording boundaries

Even if the confirmatory criteria are met, the paper may claim only intervention-defined **downward causal constraint within canonical Model B**.

Do not claim:

- complete Walker-Davies information-flow reversal;
- top-down dominance;
- an autonomous higher-level force independent of microscopic realization;
- agency or autonomous agency;
- a genetic code;
- scaffold endogenization or self-maintenance;
- permanent hereditary memory after scaffold removal;
- a universal optimum of physical constraint;
- biochemical realism, template replication, literal molecular retention, membrane growth, or physical fission.

## 14. Freeze statement

The scientific settings, scaffold identities, replicate count, seeds, endpoints, alternative intervention, checkpoint schedule, inferential unit, uncertainty procedure, multiplicity procedure, and success/narrow/no-support interpretation in this package are frozen as v1.0.0.

**No confirmatory production is authorized until the validation checklist is passed.**
