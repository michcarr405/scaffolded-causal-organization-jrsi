# Prospective Test T5 v1.0.0 — Anisotropic Historical-Match Geometry

## Status
Frozen before any T5 evolutionary outcomes or stochastic cross-evaluation outcomes are generated.

## Motivation
T4 falsified the scalar claim that historical-match loss is a function of Euclidean scaffold distance alone. Post-T4 theory development showed that the relevant quantity is directional: the evolved selected-neutral organization is read through the motif-dependent chemical kernel and pairwise fitness map. At fixed Euclidean distance, different scaffold directions should therefore produce reproducibly different historical-match losses.

## Calibration source
The angular predictions in `T5_FROZEN_ANGULAR_PREDICTIONS.csv` were computed from the 30 already-frozen T4 root blocks using the exact pre-floor expected pair-kernel score, before any T5 population is evolved. No T5 outcome enters these predictions.

The calibration predictor is

D_raw(B|X) = F_raw,selected(B|X) - F_raw,neutral(B|X)

and

DeltaH_raw(B) = D_raw(B_hist) - D_raw(B).

The expected raw fitness contracts the frozen adjacent motif-context pair distribution with the fixed Model B chemical softmax kernel and the fixed productive/anti pair payoff matrix. It contains no stochastic chemical draws and no refitting by T5.

## Probe design
- Historical scaffold: canonical SCF0 mapping [2,0,3,1], beta=4.0, theta=1.2.
- All eight alternative probes lie at exactly the same squared Euclidean scaffold distance d=64 from the historical scaffold and retain exactly the same per-segment centered bias norm.
- T5 uses eight new angular directions midway between the four cardinal directions used in T4: phi = 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5 degrees.
- Because all probes have identical Euclidean distance, any reproducible directional ordering is incompatible with a scalar Euclidean-distance law.

## Evolutionary design
- 30 entirely new paired root-seed blocks.
- Canonical Model B.
- 250 generations.
- p_inherit=0.975.
- Selected and neutral populations start from the same root population within block.
- Both evolve under the same historical SCF0 scaffold.
- T5 root seeds must not overlap with any prior seed ledger available to the execution script.

## Cross-evaluation
- Freeze generation-250 selected and neutral populations before probing.
- Evaluate historical scaffold and all eight T5 probe scaffolds.
- 32 common-random-number chemical draws within each block, shared across all probe scaffolds and both modes.
- Define A_mode(B)=F_mode(B_hist)-F_mode(B).
- Define DeltaH(B)=A_selected(B)-A_neutral(B).

## Frozen predictions
Calibration predictions are stored verbatim in `T5_FROZEN_ANGULAR_PREDICTIONS.csv`.

Predicted strongest mismatch direction: P13, phi=292.5 degrees.
Predicted weakest mismatch direction: P09, phi=202.5 degrees.

The raw calibration range between these directions is 5.7654202055 fitness units.

For a secondary absolute-value prediction only, freeze the T4-derived affine conversion from raw expected pair-kernel mismatch to observed clipped/stochastic DeltaH:

DeltaH_obs_pred = -0.82392528 + 0.98552753 * DeltaH_raw_pred.

No coefficient may be refit using T5.

## Primary prospective tests
1. **Directional-profile test:** Pearson correlation across the eight probe-direction means between frozen `pred_raw_mean` and observed T5 mean DeltaH. PASS if r > 0.90 and the two-sided permutation p-value over all 8! direction labelings is <0.01.
2. **Extremal paired test:** DeltaH(P13) > DeltaH(P09) in at least 24/30 paired root blocks. Report exact one-sided sign-test p.
3. **Equal-distance anisotropy test:** across the eight directions, the between-direction variance of block-paired DeltaH must exceed zero by a root-block permutation test (direction labels permuted within block), p<0.01.

## Secondary tests
- Zero-refit affine absolute prediction: report R2 and RMSE of the frozen affine predictions against eight observed direction means.
- Report observed rank of all eight directions and whether P13 and P09 remain top/bottom.
- Report per-block correlation between frozen angular prediction and observed DeltaH when defined.

## Interpretation rules
- T5 can confirm anisotropy of historical-match geometry and prospective transport of a calibration-derived directional profile to entirely new evolutionary histories.
- T5 cannot establish a universal metric for arbitrary microscopic models.
- The pair-kernel predictor is mechanistically grounded in Model B and therefore supports a reduced description of Model B; generality beyond Model B requires an independent microscopic realization.
