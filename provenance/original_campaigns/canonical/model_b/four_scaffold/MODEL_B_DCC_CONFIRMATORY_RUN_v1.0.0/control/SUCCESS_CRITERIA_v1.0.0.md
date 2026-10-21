# Strong-Support, Narrow-Support, No-Support, and Stop Criteria v1.0.0

These criteria are frozen before confirmatory production.

## Endpoint notation

For scaffold identity `j`:

- `D_j` = generation-250 `Delta C_down_primary`.
- `H_j` = generation-250 selected-minus-neutral historical-match score `Delta H`.
- `A_j` = generation-250 `Delta C_down_unitshuffle`.

Each quantity is defined first at the paired seed-block level and then summarized across the 30 independent blocks for that scaffold.

## Requirement A - independent canonical confirmation

`A-core` passes only if, for `SCF0`:

1. mean `D_0 > 0`;
2. the two-sided 95% bootstrap CI for mean `D_0` has lower bound `> 0`;
3. the one-sided exact sign-test p-value is `< 0.05`.

Failure of `A-core` blocks the full central claim regardless of any stronger result elsewhere.

## Requirement B1 - downward-causal generalization across scaffold identities

For each `j in {0,1,2,3}`, a mapping passes if:

1. mean `D_j > 0`;
2. the mapping-specific two-sided 98.75% bootstrap CI has lower bound `> 0`;
3. the Holm-adjusted one-sided sign-test p-value for the four-mapping `D` family is `< 0.05`.

`B1-strong` requires all 4 mappings to pass.

## Requirement B2 - historical matching / diagonal cross-evaluation

For each scaffold `j`, use

`H_j = [F(historical)-mean F(other 3)]_selected - [F(historical)-mean F(other 3)]_neutral`.

A mapping passes if:

1. mean `H_j > 0`;
2. its two-sided 98.75% bootstrap CI has lower bound `> 0`;
3. its Holm-adjusted one-sided sign-test p-value in the four-mapping `H` family is `< 0.05`.

`B2-strong` requires all 4 mappings to pass. The 4 x 4 mean cross-evaluation matrix must therefore show a positive diagonal advantage in every training-scaffold row after selected-neutral differencing.

## Requirement C - alternative-erasure robustness

For each scaffold `j`, a mapping passes if:

1. mean `A_j > 0`;
2. its two-sided 98.75% bootstrap CI has lower bound `> 0`;
3. its Holm-adjusted one-sided sign-test p-value in the four-mapping `A` family is `< 0.05`.

`C-strong` requires all 4 mappings to pass.

## Overall strong support

The working central claim receives **strong prospective support within the frozen Model B domain** only if all are true:

- `A-core` passes;
- `B1-strong` passes;
- `B2-strong` passes;
- `C-strong` passes;
- all validation and completeness gates pass without a scientific protocol change after outcome inspection.

Permitted claim form:

> Within the tested canonical Model B regime, selection prospectively and reproducibly generated scaffold-history-specific inherited organization whose preservation changed lower-level chemical-state distributions; the effect generalized across four prespecified scaffold identities and survived an independently constructed marginal-preserving relational erasure.

This does not license claims of full Walker-Davies reversal or scaffold endogenization.

## Narrow / model-specific support

Use **narrow support** rather than rescue analysis when `A-core` passes but one or more generality/robustness conditions fail or remain uncertain.

Predeclared narrow branches:

### N1 - partial scaffold generalization

- `A-core` passes;
- at least 3 of 4 `D_j` mapping means are positive and the stratified pooled `D` 95% bootstrap CI is entirely above zero;
- but `B1-strong` fails.

Interpretation: canonical confirmation plus evidence across most tested mappings; do not claim uniform scaffold-identity generalization.

### N2 - downward constraint generalizes, historical matching is incomplete

- `A-core` and `B1-strong` pass;
- pooled stratified mean `H` has a 95% CI above zero and at least 3 of 4 mapping means `H_j` are positive;
- but `B2-strong` fails.

Interpretation: selection-generated downward constraint generalizes, but the strongest historical-matching claim must be narrowed and the exception shown explicitly.

### N3 - primary erasure confirmed, alternative-erasure robustness incomplete

- `A-core` passes;
- canonical `A_0` mean is positive with 95% CI above zero;
- pooled stratified `A` 95% CI is above zero;
- but `C-strong` fails.

Interpretation: causal effect is confirmed under the primary intervention and supported in aggregate by the alternative intervention, but robustness is not uniform across scaffold identities.

### N4 - canonical-only support

- `A-core` passes;
- scaffold-generalization and/or alternative-erasure families do not show a stable pooled positive effect.

Interpretation: restrict the paper's core empirical claim to the canonical scaffold and the primary intervention; do not use language implying appropriation of physical regularity as a general mapping-independent phenomenon.

## No support for the central claim

Classify the central claim as **not prospectively supported** if any of the following holds:

1. `A-core` fails; or
2. the canonical mean `D_0 <= 0`; or
3. the canonical primary effect is positive only after changing a frozen endpoint, seed set, estimator, or inferential rule after outcome inspection.

If `A-core` passes but B or C fail, use one of the narrow branches above rather than declaring a fully negative study.

## Stop / reopen rules

- If the Model/Code, Estimator, or Statistical-Pipeline validation gate fails before production: **do not start confirmatory production**.
- If a scientific code or estimator defect is discovered after production: invalidate affected outputs, record a versioned decision, repair the defect, reopen the relevant gates, and rerun the affected frozen run IDs. Do not switch to a new favorable seed set.
- If `A-core` fails: do not add new beta values, inheritance values, scaffold identities, alternative erasures, or post hoc endpoints to rescue the central claim.
- Negative, null, boundary, and nonconfirming outcomes are frozen and reported alongside positive outcomes.
