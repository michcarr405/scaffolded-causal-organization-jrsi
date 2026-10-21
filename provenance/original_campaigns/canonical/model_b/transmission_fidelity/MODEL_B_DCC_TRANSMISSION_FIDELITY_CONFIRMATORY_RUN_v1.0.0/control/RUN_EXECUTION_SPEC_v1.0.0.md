# Run Execution Specification v1.0.0

## Frozen production size
- 30 root blocks
- 18 transmission fidelities per block
- 2 modes per fidelity
- **1080 evolutionary runs**

## Execution order
Order may be parallelized or permuted for compute efficiency; scientific identity is determined solely by frozen `run_id`, seed, fidelity, mode, and configuration.

## Required per-run outputs
- generation-0 fitness/hash linkage to the shared ancestor;
- generation-250 population state;
- generation-250 mean fitness;
- generation-250 deterministic `C_down`;
- generation-250 16-draw CRN native/reversed specificity components and averaged `R`;
- software/source hash and runtime metadata.

## Failure handling
A crashed/corrupt run is rerun using the exact same run ID and frozen inputs. No replacement seed is allowed.

## Scientific inspection
No inferential or curve-shape inspection until the frozen 1080-run campaign is complete, except technical checks needed to diagnose execution failures.
