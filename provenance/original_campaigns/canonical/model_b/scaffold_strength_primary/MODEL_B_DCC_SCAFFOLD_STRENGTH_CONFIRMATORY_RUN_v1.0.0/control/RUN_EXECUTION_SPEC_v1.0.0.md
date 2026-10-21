# Run Execution Spec v1.0.0

## Production prohibition

Do not run scientific production from this package until a validation report passes every required checklist item and an authorization manifest is created without changing any scientific field.

## Required run loop after authorization

For each row of `RUN_MANIFEST_v1.0.0.csv` in any order:

1. reconstruct the canonical Model B configuration from the manifest;
2. initialize from the block root seed using the frozen `strength-initialization` stream;
3. evolve 250 updates using the ratio-specific, mode-paired propagation stream;
4. record checkpoint fitness/state hashes;
5. archive g250 population state;
6. compute endpoint training-strength C_down;
7. compute endpoint fixed-beta=3 C_down without changing population state;
8. compute native/reversed historical specificity at training beta using 16 CRN draws;
9. compute native/reversed historical specificity at beta=3 using 16 CRN draws;
10. write exactly the expected metrics/state paths.

## Pair assembly

After both modes for a block/ratio exist, construct paired quantities `DeltaF`, `DeltaC_train`, `DeltaC_probe3`, `DeltaR_train`, `DeltaR_probe3`. Do not average across blocks before forming contrasts.

## Confirmatory analysis

Read the complete 30-block x 7-ratio paired table, evaluate only formulas in `CONTRAST_MANIFEST_v1.0.0.csv`, resample whole root blocks for 50,000 bootstraps, and apply the frozen family corrections. Ratio-specific means/intervals may be plotted descriptively; no new pointwise hypothesis family may be created after inspection.
