# Estimator and Pipeline Validation Checklist v1.0.0

**Gate status:** OPEN  
**Rule:** no confirmatory production may begin until every required item below is PASS and a versioned validation report is archived.

## A. Canonical model wrapper

- [ ] Confirm scientific source is commit `2c7d78694579755402c0a1896e109b29dec4d6a0` or a byte-audited transcription with no scientific changes.
- [ ] Verify canonical population shape `80 x 8 x 60`, four symbols, `k=5`, four segments, four local states.
- [ ] Verify affinity matrix is generated once with seed 123 and has shape `1024 x 4`.
- [ ] Verify local-state logits are `a_mz + beta * 1[z=f(s)]` and softmax scale is `Theta=1.2`.
- [ ] Verify fitness reward 2.0, penalty 0.5, floor 0.1, mutation 0.001.
- [ ] Verify population update samples source units by selected or uniform-neutral probabilities, then slot identities with replacement under `p=0.975`; no physical-retention/fission reinterpretation.
- [ ] Same seed + same condition reproduces identical trajectory, checkpoint hashes, and final population.
- [ ] Different seeds produce divergent final populations.
- [ ] Parallel scheduling/order leaves each run byte-identical.

## B. Selected-neutral pairing and RNG separation

- [ ] Selected and neutral members of a paired block start from identical population arrays.
- [ ] Selected and neutral baseline observation streams are identical before state divergence.
- [ ] Selected and neutral baseline propagation random variates are purpose-paired; only source-selection probabilities differ.
- [ ] Base seed is never reused across scaffold identities.
- [ ] Confirm all 120 frozen base seeds are unique.
- [ ] Confirm zero overlap with the 20 exploratory sweep seeds listed in the handoff package.
- [ ] Observation, propagation, cross-evaluation, alternative-erasure, and bootstrap streams are purpose-separated.
- [ ] No hidden global RNG state is used in claim-bearing code.

## C. Primary `C_down_primary`

- [ ] Probability tables are nonnegative and normalized to numerical tolerance `1e-12`.
- [ ] `P_intact(S,M)` reproduces direct segment-motif counts from a hand-constructed toy population/table.
- [ ] `P_erased(S,M)=P(S)P(M)` preserves `P(S)` and `P(M)` to `1e-12`.
- [ ] If `P(S,M)` is exactly factorized in a synthetic table, `C_down_primary <= 1e-12`.
- [ ] If `P(Z|M,S)` is made motif-independent in a synthetic test, erasing motif-position organization yields `C_down_primary <= 1e-12`.
- [ ] JSD is symmetric, finite, nonnegative within numerical tolerance, and bounded by 1 bit.
- [ ] Relabeling arrays without changing the represented joint distribution leaves the estimator unchanged.
- [ ] Replay archived exploratory endpoint states and reproduce archived `C_down` values to absolute tolerance `1e-12`.

## D. Alternative `C_down_unitshuffle`

- [ ] For every technical shuffle, each model unit retains exactly the same motif-count vector as before shuffling.
- [ ] For every technical shuffle, each model unit retains exactly 112 motif-window slots in each of the four segments.
- [ ] Global motif frequencies are preserved exactly.
- [ ] No motif occurrence crosses model-unit identity during the shuffle.
- [ ] Scaffold mapping, affinity matrix, `beta`, `Theta`, and `P(Z|M,S)` are unchanged.
- [ ] Same base block/shuffle key gives identical permutations and estimator value.
- [ ] Different shuffle keys generate different reassignment maps.
- [ ] Strong synthetic motif-segment association is visibly disrupted while declared marginals remain fixed.
- [ ] Synthetic nulls show no systematic selected-minus-neutral bias when selected and neutral states are identical.
- [ ] `K=128` convergence test: on the prespecified archived exploratory validation set (selected and neutral, beta=4, reps 0-3), compare the `K=128` mean to a `K=2048` reference using a common prefix stream; require maximum absolute difference `<= 1e-5` bits.
- [ ] Technical shuffle replicates are averaged within population and are never treated as inferential replicates.

## E. Cross-evaluation / historical-match score

- [ ] All four probe mappings are exactly those frozen in `CONFIRMATORY_PLAN_v1.0.0.md`.
- [ ] Each population receives 16 probe draws per mapping.
- [ ] Within each draw, the same local-state uniform vector is reused across all four probe mappings.
- [ ] The same cross-evaluation uniform vector is reused across selected and neutral members of the paired block.
- [ ] Probe mapping and mode are excluded from the CRN key.
- [ ] `H_j = F_j - mean(F_other3)` is reproduced by a hand-computable toy example.
- [ ] Canonical native-versus-reversed endpoint uses `SCF0` and `SCF2` exactly.
- [ ] Probe draws are averaged within population before any inferential calculation.

## F. Statistical pipeline

- [ ] Paired selected-neutral difference is computed before bootstrapping or sign testing.
- [ ] Bootstrap resamples paired blocks, never motif windows, generations, or technical draws.
- [ ] Mapping-specific bootstrap uses exactly 50,000 replicates.
- [ ] Pooled summaries use stratified resampling within mapping and equal weight across the four mapping means.
- [ ] Primary A interval is two-sided 95% percentile bootstrap.
- [ ] Four-mapping intervals are two-sided 98.75% percentile bootstrap.
- [ ] One-sided exact sign test counts exact zero as nonpositive.
- [ ] Holm correction implementation is verified on a published/hand-computable p-value vector.
- [ ] Synthetic all-positive, mixed-sign, and all-zero paired vectors return expected sign-test outcomes.
- [ ] Bootstrap RNG is deterministic and purpose-separated from simulation RNG.

## G. Manifest and completeness dry run

- [ ] `RUN_MANIFEST_v1.0.0.csv` contains exactly 240 unique run IDs.
- [ ] `PAIRED_BLOCK_MANIFEST_v1.0.0.csv` contains exactly 120 unique paired blocks.
- [ ] Exactly 30 paired blocks occur under each scaffold identity.
- [ ] Every paired block has one selected and one neutral run.
- [ ] Every run has one and only one frozen base seed.
- [ ] Expected output paths are unique.
- [ ] Dry-run parser can resolve every run row without starting evolution.
- [ ] Output schema includes run ID, paired block ID, scaffold, mode, base seed, generation, primary estimator, final state hash, and validation version.
- [ ] Failure/restart behavior never generates a new seed or silently changes a run ID.

## H. Gate decision

- [ ] All required items PASS.
- [ ] Validation report records code hash, environment, commands, and any non-scientific implementation notes.
- [ ] No confirmatory outcome has been inspected before the gate decision.
- [ ] Production authorization explicitly changed from `false` to `true` in a versioned decision after validation.
