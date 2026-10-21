# Seed Plan v1.0.0

- 30 independent root-seed blocks.
- Each root seed generates one ancestral sequence population shared across all 18 fidelity values and both modes.
- 36 evolutionary trajectories per block; 1080 total.
- Root seed is the clustering/inferential unit for all cross-fidelity contrasts.

## Deterministic derivation

For block `b`, hash `MODEL_B_DCC_FIDELITY_CONFIRM|v1.0.0|block<NN>|nonce<k>` with SHA-256 and interpret the first four bytes as an unsigned little-endian uint32. Increment nonce only on collision or overlap with the frozen prior-seed exclusion set.

## RNG stream policy

- `fidelity-initialization`: excludes `p` and mode, guaranteeing an identical ancestor across the complete within-block sweep.
- `fidelity-g0-observation`: excludes `p` and mode.
- `fidelity-propagation|<p_id>`: includes fidelity and excludes mode; selected/neutral are CRN-paired within fidelity, while different fidelities have independent purpose-separated propagation streams.
- `fidelity-endpoint-observation|<p_id>`: includes fidelity and excludes mode.
- `fidelity-specificity-crn|<p_id>`: excludes mode and native/reversed mapping, giving CRN pairing across native/reversed and selected/neutral assays at that fidelity.
- bootstrap uses a separate root seed `2481907731` and never shares simulation RNG state.

The frozen ledger is `SEED_LEDGER_v1.0.0.csv`; the exclusion provenance is `SEED_EXCLUSION_AUDIT_v1.0.0.json`.
