# Estimator and Preproduction Validation Checklist v1.0.0

**Gate status at plan freeze:** NOT YET RUN. Production is blocked until every required item passes or a versioned amendment is approved before confirmatory outcomes exist.

## A. Canonical implementation

- [ ] Scientific commit / canonical equations match `2c7d78694579755402c0a1896e109b29dec4d6a0`.
- [ ] No model mechanism changed relative to canonical Model B.
- [ ] Fixed parameters (`Theta=1.2`, `p=0.975`, `mu=0.001`, 250 updates, fitness floor 0.1) match the run manifest.
- [ ] Canonical scaffold mapping is `[2,0,3,1]`; reversed probe is `[1,3,0,2]`.

## B. Replay and determinism

- [ ] Archived exploratory condition(s) replay exactly under old seeds/configuration before the new seed namespace is used.
- [ ] Same-seed rerun produces identical final population hashes and endpoint metrics.
- [ ] Different root seeds produce divergent population states.
- [ ] Parallel job order does not alter outputs.

## C. Repeated-measures block/RNG audit

- [ ] All seven ratios in one block share the exact generation-0 ancestor sequence array.
- [ ] Selected and neutral generation-0 state and generation-0 fitness are exactly identical within ratio.
- [ ] `strength-initialization` excludes ratio and mode.
- [ ] Propagation stream includes ratio ID and excludes mode.
- [ ] Different ratios do not accidentally consume the same propagation stream.
- [ ] Selected/neutral pair within a ratio shares intended propagation randomness.
- [ ] Endpoint observation and specificity CRN keys obey the frozen inclusion/exclusion rules.

## D. Fitness outputs

- [ ] Hand-audited `G_selected=F250_selected-F0` and `G_neutral=F250_neutral-F0` calculations match direct arithmetic.
- [ ] `DeltaF=G_selected-G_neutral` equals `F250_selected-F250_neutral` to numerical tolerance.
- [ ] Fitness floor is 0.1 and is not altered by any analysis wrapper.

## E. `C_down` estimator

- [ ] Expectation-level `C_down` matches the already validated DCC estimator on archived states.
- [ ] `P_erased(S,M)=P(S)P(M)` preserves `P(S)` and `P(M)` numerically.
- [ ] Intact and erased distributions use the identical `P(Z|M,S)` readout.
- [ ] JSD is nonnegative and zero on identity synthetic cases.
- [ ] Training-strength assay uses each run's training beta.
- [ ] Fixed-probe assay uses exactly `beta=3.0` for every lineage regardless of training beta.
- [ ] Probe does not modify/evolve the archived population state.

## F. Historical specificity estimator

- [ ] `R=F_native-F_reversed` uses mappings `[2,0,3,1]` and `[1,3,0,2]` exactly.
- [ ] 16 technical observation draws are used per assay.
- [ ] Native and reversed evaluations share common random numbers.
- [ ] Selected and neutral members share the same specificity-draw keys within a ratio/block.
- [ ] Training assay uses training beta; standardized assay uses beta=3.0.
- [ ] Technical draws are averaged within evolved population and never counted as independent n.

## G. Contrast/statistical pipeline

- [ ] Every formula in `CONTRAST_MANIFEST_v1.0.0.csv` is unit-tested on a hand-constructed 3-block toy table.
- [ ] Across-ratio contrasts are calculated within root block before aggregation.
- [ ] Bootstrap resamples 30 root blocks, retaining all nested ratios and modes in each resampled block.
- [ ] Bootstrap count is exactly 50,000.
- [ ] Analysis root seed matches `CONFIRMATORY_CONFIG_v1.0.0.json`.
- [ ] Exact one-sided sign test counts zeros as nonpositive.
- [ ] Holm adjustment is applied separately within A_COST, F_RECOVERY, C_DOWN, and R_SPEC.
- [ ] 97.5% intervals are used for two-test families; 98.75% intervals for four-test families.
- [ ] No pointwise ratio p-value family is generated for claim selection.

## H. Manifest/completeness dry run

- [ ] `SEED_LEDGER` contains 30 unique root seeds with zero overlap against the recorded prior-seed exclusion set.
- [ ] `BLOCK_MANIFEST` contains 30 blocks.
- [ ] `CONDITION_MANIFEST` contains 7 ratios with exact beta values.
- [ ] `RUN_MANIFEST` contains 420 unique run IDs = 30 x 7 x 2.
- [ ] Every block contains all 14 required runs.
- [ ] Every ratio has 30 selected + 30 neutral runs.
- [ ] Every manifest row has `production_authorized=false` at freeze.
- [ ] Expected output paths are unique.
- [ ] Dry-run creates the expected directory/schema without producing scientific outcomes.

## I. Authorization rule

- [ ] Validation report versioned and signed off.
- [ ] Scientific hashes/manifests frozen.
- [ ] Only after the preceding items pass may an authorized run manifest be created by changing the authorization field; no scientific field may change at authorization.
