# Validation Report v1.0.0

**Gate:** PASS
**Checks:** 56 PASS / 0 FAIL

No confirmatory production outcome existed or was inspected before this gate decision.

## Environment

- `python`: `3.13.5 (main, Jul 15 2026, 20:25:40) [GCC 14.2.0]`
- `platform`: `Linux-6.18.35-x86_64-with-glibc2.41`
- `numpy`: `2.3.5`
- `scipy`: `1.17.0`
- `numba`: `0.65.1`

## Checklist results

- [x] **H** No confirmatory outcome exists before validation: PASS
- [x] **A** Canonical source git-blob audit: PASS
- [x] **A** Canonical population shape parameters: PASS
- [x] **A** Four-symbol k=5 four-segment four-state architecture: PASS
- [x] **A** Affinity matrix seed 123 exact: PASS
- [x] **A** Frozen beta and Theta: PASS
- [x] **A** Frozen fitness and mutation parameters: PASS
- [x] **A** Local-state logit and softmax law: PASS
- [x] **A** Same-seed determinism: PASS
- [x] **A** Different-seed divergence: PASS
- [x] **B** Selected-neutral identical ancestor arrays: PASS
- [x] **B** Observation CRN stream identity: PASS
- [x] **B** Propagation CRN stream identity: PASS
- [x] **B** Purpose-separated streams differ: PASS
- [x] **B** All 120 confirmatory base seeds unique: PASS
- [x] **B** No confirmatory seed overlaps exploratory 20-seed ledger: PASS
- [x] **B** No hidden global RNG in claim-bearing core: PASS
- [x] **C** P(S)P(M) preserves marginals: PASS
- [x] **C** Factorized P(S,M) gives zero primary C_down: PASS
- [x] **C** Motif-independent readout null: PASS
- [x] **C** JSD anchors and bounds: PASS
- [x] **C** Joint/kernel motif relabeling invariance: PASS
- [x] **C** Archived exploratory C_down replay to 1e-12: PASS
- [x] **D** Each unit motif multiset preserved exactly: PASS
- [x] **D** Each unit has 112 fixed slots in every segment: PASS
- [x] **D** No motif crosses model-unit identity: PASS
- [x] **D** Same base/shuffle stream deterministic: PASS
- [x] **D** Different shuffle key changes reassignment: PASS
- [x] **D** Global motif and segment margins preserved: PASS
- [x] **D** Strong synthetic motif-segment association is disrupted: PASS
- [x] **D** Identical selected-neutral synthetic null has zero delta: PASS
- [x] **D** K=128 common-prefix convergence <=1e-5 bits: PASS
- [x] **E** Frozen probe mapping identities: PASS
- [x] **E** Sixteen cross-evaluation draws: PASS
- [x] **E** Cross-evaluation common uniforms deterministic: PASS
- [x] **E** Optimized cross-eval agrees with canonical core: PASS
- [x] **E** Historical-match toy formula: PASS
- [x] **E** Canonical native/reversed are SCF0 and SCF2: PASS
- [x] **F** Bootstrap resamples paired-block vector and positive CI: PASS
- [x] **F** 98.75% interval implementation: PASS
- [x] **F** Exact sign test all-positive/mixed/all-zero behavior: PASS
- [x] **F** Holm hand-computable example: PASS
- [x] **F** Stratified pooled bootstrap equal-weights mapping means: PASS
- [x] **F** Bootstrap RNG deterministic and purpose-separated: PASS
- [x] **G** Run manifest has 240 unique IDs: PASS
- [x] **G** Paired manifest has 120 unique blocks: PASS
- [x] **G** Exactly 30 paired blocks per scaffold: PASS
- [x] **G** Every paired block has selected and neutral runs: PASS
- [x] **G** Every run has one frozen base seed: PASS
- [x] **G** Expected output paths unique: PASS
- [x] **G** Dry-run parser resolves every run row: PASS
- [x] **G** Output schema contains required fields: PASS
- [x] **A** Parallel scheduling/order yields byte-identical run outputs: PASS
- [x] **A** Canonical wrapper reproduces archived exploratory final states exactly: PASS
- [x] **A** Canonical wrapper reproduces archived exploratory endpoint metrics: PASS
- [x] **H** Validation completed without confirmatory production outcome inspection: PASS
