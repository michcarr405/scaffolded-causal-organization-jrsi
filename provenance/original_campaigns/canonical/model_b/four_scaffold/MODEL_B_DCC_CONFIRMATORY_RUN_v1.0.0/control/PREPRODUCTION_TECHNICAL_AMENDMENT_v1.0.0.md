# Preproduction Technical Amendment v1.0.0

This amendment records the technical clarifications in decision `DCC-CONF-003` before any confirmatory production run.

- Bootstrap analysis root seed: `145617781`.
- Derivation tag: `MODEL_B_DCC_CONFIRM|v1.0.0|analysis-bootstrap`.
- SHA-256: `75f3ad08df56392b57eb5e7722cbea2fd60cede57b671c93d33fe007de3dba05`.
- Unit-shuffle RNG: one sequential `confirmatory-unitshuffle` stream per base seed, shared by selected and neutral; `K=128` is a strict prefix of `K=2048`.
- Cross-evaluation RNG: one `confirmatory-cross-eval` stream per base seed; the same 16-draw uniform matrix is reused across all probe mappings and both modes.

No model mechanism, parameter, endpoint, replicate count, seed ledger, scaffold identity, estimator definition, inferential unit, success criterion, or multiplicity rule is changed.
