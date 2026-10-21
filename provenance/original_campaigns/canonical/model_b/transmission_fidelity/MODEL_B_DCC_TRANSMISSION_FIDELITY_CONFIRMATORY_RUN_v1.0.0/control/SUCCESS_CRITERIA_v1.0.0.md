# Success, Narrow-Support, No-Support, and Stop Criteria v1.0.0

These criteria are frozen before confirmatory production.

## C_DOWN family

Each of `C1-C3` passes only if:

1. the mean block-level contrast is > 0;
2. the lower bound of its two-sided 98.333% root-block bootstrap interval is > 0;
3. the Holm-adjusted one-sided exact sign-test p-value is < 0.05 within the three-test family.

`C_DOWN-strong` requires all three tests to pass. In addition, all five displayed high-fidelity means at `p={0.90,0.925,0.95,0.975,1.0}` must be directionally positive.

## R_SPEC family

Apply the same criteria to `R1-R3`. `R_SPEC-strong` requires all three tests plus positive means at all five `p>=0.90` display points.

## Overall strong support / promotion gate

Figure 4(c,d) may be relabeled as **primary prospectively confirmed evidence** only if:

- `C_DOWN-strong` passes;
- `R_SPEC-strong` passes;
- all 1080 frozen run IDs complete or are technically rerun under identical frozen specifications;
- validation and deterministic analysis-replay gates pass;
- no scientific model, estimator, seed, endpoint, fidelity value, or contrast is changed after outcome inspection.

Permitted result form:

> Within the tested canonical Model B domain, selection-generated downward causal constraint and historical scaffold specificity were strongly concentrated in the high-transmission-fidelity regime and increased further toward very high fidelity.

The exact shape of the 18-point curves may be described descriptively. A continuously estimated critical fidelity may not be claimed.

## Narrow-support branches

### N1 - C-down confirmed, specificity incomplete
If `C_DOWN-strong` passes but `R_SPEC-strong` fails, panel (c) may be promoted; panel (d) remains exploratory/partially confirmed.

### N2 - specificity confirmed, C-down incomplete
If `R_SPEC-strong` passes but `C_DOWN-strong` fails, panel (d) may be promoted only as a specificity result; panel (c) remains exploratory/partially confirmed.

### N3 - high-vs-low confirmed but further high-fidelity strengthening not confirmed
If `C1/C3` and/or `R1/R3` pass but `C2` and/or `R2` fail, use `concentrated at high fidelity` wording but do not claim continued strengthening from transition to very-high fidelity for the affected endpoint.

### N4 - positive endpoint at p=0.975 not confirmed
If `C3` or `R3` fails, do not use the earlier exploratory `p=0.975` value as a substitute. The corresponding panel cannot receive full confirmatory status.

## No-support criterion

Do not promote the affected panel if its core high-vs-low contrast (`C1` or `R1`) fails, or if a favorable conclusion would require changing the frozen grid, seed set, estimator, or inferential rule after viewing outcomes.

Failure here does not alter the already frozen four-scaffold or scaffold-strength confirmatory results.

## Stop/reopen rules

- No production if validation fails.
- Technical failures are rerun with the same run ID, seed, and configuration.
- Scientific/estimator defects require a new version before generating/replacing affected outcomes.
- Do not thin the 18-point grid after results are seen.
- Do not add fidelities or retrospectively declare the first significant point a critical threshold.
- Null, negative, and boundary outcomes are frozen with positive outcomes.
