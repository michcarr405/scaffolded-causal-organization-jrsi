# Result Freeze — Catalytic-Complex Transmission-Fidelity Confirmation v1.0.0

## Provenance
This campaign was frozen before outcome generation. The prospective plan SHA256 is:

`14cbe39ee6f42d4af45089eeece5e26d8824b529cbf584218c56ca5dd1b4ac40`

The first serial invocation was terminated by the execution environment before any result file or stdout outcome was produced. A pre-outcome technical amendment authorized block-parallel execution with identical frozen model, grid, seeds, endpoints, and inference. The amendment SHA256 is:

`087eeaef84cfa06ab5e09a67d191ab4e2102b77707c8a9272ae99ec7e5e70a24`

## Design
- catalytic affinity matrix seed 51073, identical to the independently confirmed catalytic realization;
- 30 entirely new root-seed blocks;
- exact 18-point transmission-fidelity grid `0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975, 1.0`;
- 540 selected-neutral fidelity pairs = 1080 evolutionary runs;
- same founder population across all fidelity conditions within each root block;
- primary endpoint families: selected-minus-neutral relational organization `DeltaR_pop` and selected-minus-neutral relation-specific adaptive value `DeltaV_rel`.

## Frozen classification
**STRONG PROSPECTIVE SUPPORT**

Both primary families passed all frozen formal contrasts and all high-fidelity directional display criteria.

### R_POP family
- R1 high-vs-low: mean `+0.0498268 bits`, 98.333% CI `[0.0364469, 0.0628952]`, positive in 27/30 blocks, Holm-adjusted one-sided sign p=`1.26e-5` — PASS.
- R2 very-high vs transition: mean `+0.0446227 bits`, 98.333% CI `[0.0194317, 0.0691095]`, positive in 24/30 blocks, Holm p=`7.15e-4` — PASS.
- R3 at p=0.975: mean `+0.0695734 bits`, 98.333% CI `[0.0451883, 0.0967369]`, positive in 27/30 blocks, Holm p=`1.26e-5` — PASS.
- Mean DeltaR_pop was positive at all five high-fidelity display points `p={0.90,0.925,0.95,0.975,1.0}` — PASS.

### V_REL family
- V1 high-vs-low: mean `+0.0271774`, 98.333% CI `[0.0233603, 0.0311060]`, positive in 30/30 blocks, Holm p=`2.79e-9` — PASS.
- V2 very-high vs transition: mean `+0.0109999`, 98.333% CI `[0.00544103, 0.0167031]`, positive in 25/30 blocks, Holm p=`1.62e-4` — PASS.
- V3 at p=0.975: mean `+0.0315869`, 98.333% CI `[0.0242537, 0.0395337]`, positive in 30/30 blocks, Holm p=`2.79e-9` — PASS.
- Mean DeltaV_rel was positive at all five high-fidelity display points — PASS.

## Shape of the prospective curves
The dense curves show a regime-like change rather than a uniform linear trend. `DeltaR_pop` remains near zero through approximately p=0.8, becomes positive at p=0.825, rises strongly through p=0.975, and is still strongly positive at p=1.0. `DeltaV_rel` begins increasing earlier but is strongly concentrated in the high-fidelity regime and continues to strengthen toward very high fidelity under the frozen contrast.

The exact curve must not be used to claim a continuously estimated critical fidelity. In particular, the lower-fidelity points were not individually preregistered threshold tests.

## Cross-realization conclusion now permitted
Because canonical Model B independently passed an analogous prospective 18-point fidelity campaign, the manuscript may now state:

> **Heredity dependence is prospectively replicated across two microscopically distinct pre-genetic realizations. In both systems, strong selection-generated relational organization and/or its causal adaptive consequence are concentrated in the high-transmission-fidelity regime and strengthen toward very high fidelity.**

For maximal symmetry, a narrower formulation is preferable:

> **Across both microscopic realizations, reliable transmission strongly amplifies the selection-generated causal contribution of inherited relational organization.**

## Boundaries
This campaign does not establish a universal critical fidelity, a continuously estimated phase transition, scaffold endogenization, autonomous agency, genetic coding, or full Walker-Davies reversal. The external scaffold remains supplied by the environment.
