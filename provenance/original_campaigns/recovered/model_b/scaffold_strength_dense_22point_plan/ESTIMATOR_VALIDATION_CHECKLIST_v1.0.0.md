# Dense Scaffold-Strength Estimator/Execution Validation Checklist v1.0.0

Production is blocked until every required item passes.

- [ ] canonical Model B archived replay is exact
- [ ] same seed/key deterministic; different root seeds diverge
- [ ] all 22 propagation namespaces are distinct and scheduling invariant
- [ ] selected and neutral generation-0 states/fitness are identical within each strength
- [ ] all 22 strengths reconstruct the same ancestor within each root block
- [ ] endpoint observation streams are strength-specific and mode-paired
- [ ] expectation-level C_down replays validated estimator and preserves motif/segment marginals
- [ ] training-strength and fixed-beta=3 probes use frozen beta values and do not mutate populations
- [ ] historical-specificity assay uses exactly 16 CRN draws and agrees with canonical core on test draws
- [ ] 50,000 block bootstrap, sign test, Holm, and all 12 inherited contrast formulas pass synthetic checks
- [ ] condition manifest contains exactly 22 frozen strengths and exact beta coordinates
- [ ] run manifest contains exactly 1320 unique run IDs; 44 runs per block; 30 selected + 30 neutral per strength
- [ ] seed ledger contains 30 unique new seeds with zero recorded overlap
- [ ] all output paths are unique and production flags are false at freeze
- [ ] dry-run parses all 1320 rows
- [ ] no dense confirmatory endpoint exists before validation/authorization
