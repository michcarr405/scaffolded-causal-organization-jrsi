# Transmission-Fidelity Validation Report v1.0.0

**Gate:** PASS
**Checks:** 33 PASS / 0 FAIL

No new confirmatory production outcome existed or was inspected before this gate decision.

## Checklist results

- [x] **A** Canonical source blob SHAs match frozen scientific commit provenance: PASS
- [x] **A** Canonical dimensions and affinity realization: PASS
- [x] **A** Frozen fixed parameters match config: PASS
- [x] **A** Exact 18-point fidelity grid preserved: PASS
- [x] **A** Archived exploratory p=0.975 selected/neutral endpoint replay exactly: PASS
- [x] **B** Same keyed seed deterministic and different root seed diverges: PASS
- [x] **B** All 18 fidelity-specific streams are distinct: PASS
- [x] **B** Parallel scheduling does not alter keyed streams: PASS
- [x] **C** All fidelities/modes reconstruct identical ancestor within block: PASS
- [x] **C** Generation-0 selected/neutral observation and fitness exactly identical: PASS
- [x] **C** Selected-neutral propagation streams are mode-paired: PASS
- [x] **C** Observation and reproduction substreams are purpose-separated: PASS
- [x] **C** Endpoint stream is fidelity-specific and mode-paired: PASS
- [x] **D** C_down relational erasure preserves motif and segment marginals: PASS
- [x] **D** C_down nonnegative and identity JSD zero: PASS
- [x] **D** C_down estimator does not modify population: PASS
- [x] **E** Specificity uses exactly 16 native/reversed CRN draws: PASS
- [x] **E** Four-draw and sixteen-draw assays use identical per-draw estimand: PASS
- [x] **E** Optimized specificity agrees with canonical core for native/reversed draw: PASS
- [x] **E** Increasing draws changes only Monte Carlo averaging precision: PASS
- [x] **F** 50,000 root-block bootstrap implemented: PASS
- [x] **F** Exact one-sided sign test counts zero nonpositive: PASS
- [x] **F** Holm hand-check: PASS
- [x] **F** Frozen contrast group definitions parse and give intended ordering: PASS
- [x] **G** Seed ledger has 30 unique new root seeds and no recorded overlap: PASS
- [x] **G** Condition manifest has exact 18 fidelities: PASS
- [x] **G** Run manifest has 1080 unique IDs: PASS
- [x] **G** Every root block has 36 runs: PASS
- [x] **G** Every fidelity has 30 selected and 30 neutral runs: PASS
- [x] **G** All production authorization flags false at frozen gate: PASS
- [x] **G** Expected output paths unique: PASS
- [x] **G** Dry manifest parses all 1080 rows: PASS
- [x] **G** No confirmatory endpoint exists before validation gate: PASS
