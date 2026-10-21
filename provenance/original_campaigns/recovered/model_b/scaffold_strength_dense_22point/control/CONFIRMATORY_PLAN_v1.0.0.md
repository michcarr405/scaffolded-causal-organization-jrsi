# Dense Scaffold-Strength Confirmatory Plan v1.0.0

**Project:** Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model  
**Campaign:** prospective dense-grid replication of scaffold-strength figure  
**Status:** **DESIGN FROZEN; VALIDATION REQUIRED; CONFIRMATORY PRODUCTION NOT AUTHORIZED**  
**Date:** 2026-09-05  
**Scientific source:** canonical Model B, commit `2c7d78694579755402c0a1896e109b29dec4d6a0`

## 1. Purpose

A seven-anchor prospective campaign has already confirmed the scaffold-strength regime structure. This second campaign has a narrower purpose: replace the exploratory 22-point curves in the primary scaffold-strength figure with an **independent, prospectively generated dense-grid replication at the exact original x-coordinates**, without thinning the display or treating exploratory outcomes as confirmatory data.

No exploratory outcome is pooled with the new campaign. The original exploratory+extension files contribute only the frozen **22-point grid coordinates**.

## 2. Exact frozen 22-point strength grid

The full original grid is retained:

`beta/Theta = {0, .25, .5, .75, 1, 1.25, 1.5, 1.666667, 2, 2.25, 2.5, 2.75, 3, 3.333333, 3.5, 3.75, 4, 4.25, 4.5, 5, 6, 8}`.

`beta = {0, .3, .6, .9, 1.2, 1.5, 1.8, 2.0, 2.4, 2.7, 3.0, 3.3, 3.6, 4.0, 4.2, 4.5, 4.8, 5.1, 5.4, 6.0, 7.2, 9.6}` with `Theta=1.2`.

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
