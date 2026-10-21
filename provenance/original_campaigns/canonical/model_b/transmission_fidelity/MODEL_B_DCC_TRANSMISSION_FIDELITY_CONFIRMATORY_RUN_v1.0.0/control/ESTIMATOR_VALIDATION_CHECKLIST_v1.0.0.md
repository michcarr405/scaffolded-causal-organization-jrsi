# Estimator and Preproduction Validation Checklist v1.0.0

**Production remains unauthorized until every required item passes.**

## Canonical model / replay
- [ ] Confirm scientific commit `2c7d78694579755402c0a1896e109b29dec4d6a0` or byte-identical source snapshot.
- [ ] Replay at least archived `beta=3, p=0.975` selected and neutral trajectories with archived seeds and verify generation-0 and generation-250 fitness/C-down against archived values to numerical tolerance.
- [ ] Verify the variable-`p` reproduction function preserves canonical draw order and matches `p=0.975` archived replay.

## Blocking and RNG
- [ ] Same block: all 18 fidelity conditions initialize to byte-identical ancestral sequence populations.
- [ ] Same block/fidelity: selected and neutral generation-0 populations and observations are identical.
- [ ] Different blocks diverge under initialization.
- [ ] Propagation streams are fidelity-specific and selected/neutral mode-paired.
- [ ] No stream key accidentally depends on selected/neutral mode where CRN pairing is required.
- [ ] Same seed/config replays exactly.

## `C_down`
- [ ] Confirm expectation-level JSD implementation uses bits.
- [ ] Confirm intact and erased distributions use identical `P(Z|M,S)`.
- [ ] Confirm erasure is exactly `P(S,M)->P(S)P(M)` with marginals preserved.
- [ ] Replay archived states and match archived `C_down` values.
- [ ] Verify `C_down=0` for a synthetic factorized `P(S,M)` case to tolerance.

## Historical specificity
- [ ] Confirm native mapping `[2,0,3,1]` and reversed mapping `[1,3,0,2]`.
- [ ] Confirm `R=F_native-F_reversed`.
- [ ] Confirm 16 common-random-number draws use identical local-state uniforms for native/reversed within each draw.
- [ ] Confirm technical draws are averaged before block-level inference.
- [ ] On archived states, compare 4-draw and 16-draw assays: estimand/orientation must agree; only technical precision is changed.

## Statistics
- [ ] Synthetic root-block bootstrap test recovers known mean/CI.
- [ ] Exact one-sided sign test counts zero as nonpositive.
- [ ] Holm correction verified on a hand-calculated three-test example.
- [ ] 98.333% two-sided interval quantiles verified.
- [ ] Contrasts are formed within block before resampling.
- [ ] No pointwise 18-fidelity significance search appears in the confirmatory analysis.

## Manifest / dry run
- [ ] Run manifest has exactly 1080 unique run IDs.
- [ ] 30 blocks x 18 fidelities x 2 modes is exact and complete.
- [ ] Every block contains the exact frozen 18-point grid.
- [ ] Every block/fidelity has exactly one selected and one neutral run.
- [ ] All rows remain `production_authorized=false` until formal authorization.
- [ ] Dry run validates expected state/metrics paths without generating scientific outcomes.

## Authorization
- [ ] Validation report is versioned and frozen.
- [ ] Decision log records PASS with no scientific amendment, or any preproduction technical amendment is documented before production.
- [ ] Authorized manifest is created only after all gates pass.
