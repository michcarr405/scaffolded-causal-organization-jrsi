# Validation report v1.0.0

## Pre-outcome integrity
- Pre-outcome SHA256 manifest entries: 14.
- Post-run hash recheck: 14/14 exact matches.
- No frozen control/code/source-reference file changed after the pre-outcome freeze.

## Production completeness
- Required blocks: 30; observed: 30.
- Required scaffold strengths: 22; observed: 22 per block.
- Required block-strength rows: 660; observed: 660.
- Evolutionary arms per block-strength: selected and neutral, both present.
- Endpoint state archive dimensions correspond to 30 blocks x 22 strengths x 48 cells x 10 dimer species for each selected/neutral arm.

## Seed replay
- Pre-outcome seed ledger rows: 660.
- Executed seed ledger rows matched on block and strength: 660/660.
- Founder seed values exact-match pre-outcome ledger: 660/660.
- Selected evolution seed values exact-match: 660/660.
- Neutral evolution seed values exact-match: 660/660.
- Unique founder seeds: 30; unique selected seeds: 660; unique neutral seeds: 660.

## Model consistency
The production implementation is a scaffold-strength generalization of the frozen catalytic confirmatory code. The frozen scientific parameters are unchanged except that scaffold strength is varied on the prospectively frozen 22-point grid. At s=2, the new independent campaign closely replicates the original single-strength confirmation:
- founder cost: new -0.113446 vs prior -0.113103;
- selected-neutral fitness recovery: new +0.055522 vs prior +0.056244.

These are independent-root-seed replications, so numerical identity is neither expected nor required.

## Analysis replay
The frozen analysis script produced all prespecified formal contrasts and the strong-support flag without modification after outcome generation.
