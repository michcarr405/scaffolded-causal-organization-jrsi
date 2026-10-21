# Seed Plan v1.0.0

## Design

- 30 independent root-seed blocks.
- Each root seed generates the same ancestral sequence population across all 7 scaffold-strength conditions.
- Each ratio has one selected and one matched-neutral trajectory.
- 14 evolutionary runs per block; 420 total.
- Root seed is the inferential clustering unit for all across-strength contrasts.

## Deterministic derivation

For block `b`, form:

`MODEL_B_DCC_STRENGTH_CONFIRM|v1.0.0|block<NN>|nonce<k>`.

Take SHA-256 of the UTF-8 string and interpret the first four bytes as an unsigned little-endian 32-bit integer. Increment the nonce only for collision or overlap with an excluded prior seed.

The frozen ledger is `SEED_LEDGER_v1.0.0.csv`.

## Exclusion set

At plan creation, prior integer seed values were collected from accessible project seed-ledger CSVs under `/mnt/data`, including the archived exploratory ratio-sweep ledger and the preceding DCC confirmatory ledger. All 30 new root seeds were checked for zero overlap with that set.

## RNG stream policy

- `strength-initialization`: excludes ratio and mode so all seven ratios in a block share the exact ancestor sequence population.
- `strength-g0-observation`: excludes ratio and mode to support common-random-number comparison of the physical effect of changing `beta`.
- `strength-propagation|<ratio_id>`: includes ratio but excludes mode; selected and neutral share propagation randomness within ratio, while different ratios do not share the propagation stream.
- `strength-endpoint-observation|<ratio_id>`: includes ratio but excludes mode.
- `strength-specificity-crn|<ratio_id>`: excludes mode and native/reversed mapping, so specificity assays use common random numbers.
- bootstrap uses a separate project-level analysis root and never shares simulation RNG state.

## Frozen analysis seed

- bootstrap root seed: `151092729`
- derivation tag: `MODEL_B_DCC_STRENGTH_CONFIRM|v1.0.0|analysis-bootstrap-root`
