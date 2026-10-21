# Strong-Support, Narrow-Support, No-Support, and Stop Criteria v1.0.0

These rules are frozen before confirmatory production.

## Family A - ancestral physical cost

`A_COST` passes if both `A1` and `A2` have:

1. positive block-mean contrast;
2. lower bound of the two-sided 97.5% block-bootstrap interval > 0;
3. Holm-adjusted one-sided exact sign-test p < 0.05 within the two-test family.

## Family F - selection-dependent fitness recovery

`F_RECOVERY` passes if:

- `F1` and `F2` each satisfy the same three criteria above using 97.5% intervals and Holm correction;
- the five ratio-specific mean `DeltaF(r)` values for `r={1.5,2.5,3.0,3.5,4.0}` are all > 0.

The zero-centered `G_neutral=F250_neutral-F0` curve is reported with uncertainty but is not subjected to a post hoc equivalence margin.

## Family C - downward causal regime structure

Each of `C1-C4` passes if:

1. mean block-level contrast > 0;
2. lower bound of the two-sided 98.75% block-bootstrap interval > 0;
3. Holm-adjusted one-sided exact sign-test p < 0.05 within the four-test family.

`C_DOWN-strong` requires all four.

## Family R - historical-specificity regime structure

Apply the same criteria to `R1-R4`. `R_SPEC-strong` requires all four.

## Collapse/floor wording gate

The `r=4.5` condition may be described as a canonical fitness-floor/collapse anchor only if both selected and neutral generation-250 mean fitness are <= 0.20. Otherwise use `high-strength turnover/loss` wording and do not add a stronger ratio after inspection.

## Overall strong support for promotion of the sweep

The scaffold-strength regime structure is prospectively promoted to **primary confirmatory evidence** only if:

- `A_COST` passes;
- `F_RECOVERY` passes;
- `C_DOWN-strong` passes;
- `R_SPEC-strong` passes;
- validation, completeness, and reproducibility gates pass without a scientific protocol change after outcome inspection.

Permitted result form:

> Within the tested canonical Model B domain, increasing externally imposed scaffold strength imposed a progressively larger ancestral fitness cost, while selection generated a broad regime of adaptive recovery, downward causal constraint, and historical scaffold specificity. At high but still viable strength, standardized moderate probing revealed more latent organization than was expressed under the training field, whereas these selection-dependent effects disappeared beyond the viable canonical-fitness regime.

The wording `fitness-floor collapse` is allowed only if the separate floor gate passes.

## Narrow-support branches

### N1 - cost and adaptive recovery confirmed; causal regime shape incomplete
If `A_COST` and `F_RECOVERY` pass but `C_DOWN-strong` fails, the fitness panels may be confirmatory but the causal-strength sweep remains exploratory/partially confirmed.

### N2 - C-down regime confirmed; historical-specificity regime incomplete
If `A_COST`, `F_RECOVERY`, and `C_DOWN-strong` pass but `R_SPEC-strong` fails, promote the physical-cost/adaptive-recovery/downward-constraint story but do not claim a confirmed parallel historical-specificity strength regime.

### N3 - rise/collapse confirmed; latent-vs-expressed separation not confirmed
If `C1`, `C2`, `C4`, `R1`, `R2`, and `R4` pass but `C3` and/or `R3` fail, remove or soften `latent exceeds expression` language. Do not relabel the fixed-probe difference as confirmed.

### N4 - high-strength anchor does not satisfy the floor gate
Report `turnover` or `loss of selection-dependent effect`; do not claim fitness-floor collapse and do not add a stronger ratio post hoc.

## No support for confirmatory promotion

Do not promote the full sweep to primary confirmatory evidence if either `F_RECOVERY` or the core rise contrast `C1` fails, or if a favorable conclusion requires changing the frozen ratios, seed set, estimator, endpoint, or inferential rule after outcome inspection.

This classification does **not** invalidate the already frozen four-scaffold DCC confirmatory result; it applies only to the new scaffold-strength regime claim.

## Stop/reopen rules

- No production if validation fails.
- Scientific or estimator defects require a versioned reopen and rerun of affected frozen run IDs; do not choose new favorable seeds.
- Do not add ratios, move the fixed probe, change the collapse anchor, or introduce a new peak definition after seeing outcomes.
- Negative/null/boundary results are frozen with positive results.
