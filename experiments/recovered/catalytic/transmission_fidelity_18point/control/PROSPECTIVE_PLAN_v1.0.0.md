# Prospective Confirmatory Plan — Catalytic-Complex Transmission Fidelity v1.0.0

## Status
Frozen before generation or inspection of any outcomes from this campaign.

## Purpose
Prospectively test whether the catalytic-complex realization reproduces the transmission-fidelity dependence already prospectively confirmed in canonical Model B, thereby placing heredity dependence on symmetric confirmatory footing across the two microscopic realizations.

## Frozen microscopic realization
The scientific model is unchanged from `CATALYTIC_COMPLEX_SCO_v1.0.0` confirmatory campaign:
- affinity matrix seed = 51073;
- 4 monomer catalyst types forming 10 unordered dimer species;
- 32 inherited dimers per protocell;
- population size 48;
- 180 generations;
- dimer mutation probability 0.01;
- soft selection coefficient 24;
- Michaelis half-saturation K = 1;
- historical zero-sum reaction-field scaffold = [1,-1,0,0]/sqrt(2);
- scaffold strength = 2.0;
- selected and neutral treatments begin from the identical founder population within each root block;
- relational erasure preserves aggregate monomer marginals while randomly re-pairing them, thereby destroying dimer-pair identity while preserving the component parts.

No model parameter other than transmission fidelity p is varied.

## Fidelity grid
Use the exact 18-point grid used in the Model B prospective fidelity campaign:

`p = {0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975, 1.0}`.

The full grid is retained regardless of outcome.

## Replication and inferential unit
- 30 entirely new root-seed blocks, not used in catalytic discovery or the prior catalytic confirmatory campaign.
- The same founder population is reused across all 18 fidelity conditions within a root block.
- Each fidelity has a selected and matched neutral evolutionary run.
- Total = 30 x 18 x 2 = 1080 evolutionary runs.
- Root-seed block is the inferential unit.

## Primary endpoints
For each fidelity and block, compute selected-minus-neutral endpoint differences:

`DeltaR_pop(p) = R_pop_selected(p) - R_pop_neutral(p)`

where `R_pop` is the JSD between intact dimer composition and the random-pairing distribution implied by the same monomer marginals.

`DeltaV_rel(p) = V_rel_selected(p) - V_rel_neutral(p)`

where `V_rel = fitness(intact) - fitness(randomly re-paired)` under identical reaction physics.

These are the two primary families because they directly measure (i) selection-generated inherited relational organization and (ii) the adaptive causal value of preserving that relation.

## Frozen formal contrasts
The contrast structure intentionally mirrors the Model B fidelity confirmation.

### R_POP family
R1. High-versus-low regime:
`mean_{p=0.90,0.925,0.95,0.975,1.0}(DeltaR_pop) - mean_{p=0,0.1,0.2,0.3,0.4,0.5,0.6}(DeltaR_pop) > 0`.

R2. Continued strengthening toward very high fidelity:
`mean_{p=0.95,0.975,1.0}(DeltaR_pop) - mean_{p=0.85,0.875,0.90}(DeltaR_pop) > 0`.

R3. Manuscript operating point:
`DeltaR_pop(p=0.975) > 0`.

### V_REL family
V1. High-versus-low regime:
`mean_{p=0.90,0.925,0.95,0.975,1.0}(DeltaV_rel) - mean_{p=0,0.1,0.2,0.3,0.4,0.5,0.6}(DeltaV_rel) > 0`.

V2. Continued strengthening toward very high fidelity:
`mean_{p=0.95,0.975,1.0}(DeltaV_rel) - mean_{p=0.85,0.875,0.90}(DeltaV_rel) > 0`.

V3. Manuscript operating point:
`DeltaV_rel(p=0.975) > 0`.

## Frozen inference and success criteria
For each of the six formal contrasts:
1. mean block-level contrast > 0;
2. lower bound of a two-sided 98.333% root-block bootstrap confidence interval > 0 (50,000 bootstrap replicates);
3. Holm-adjusted one-sided exact sign-test p < 0.05 within its three-test family; zero counts as nonpositive.

`R_POP-strong` requires R1-R3 all pass and the mean `DeltaR_pop` is positive at every displayed high-fidelity point `p={0.90,0.925,0.95,0.975,1.0}`.

`V_REL-strong` requires V1-V3 all pass and the mean `DeltaV_rel` is positive at every displayed high-fidelity point `p={0.90,0.925,0.95,0.975,1.0}`.

### Overall promotion gate
The statement

> heredity dependence is prospectively replicated across the two microscopic realizations

is permitted only if both `R_POP-strong` and `V_REL-strong` pass, all 1080 frozen run IDs complete, and no scientific model, endpoint, fidelity value, contrast, or seed is altered after outcome inspection.

If only R_POP or V_REL passes, use endpoint-specific wording. If R1 or V1 fails, do not claim strong catalytic fidelity dependence for that endpoint. If R2 or V2 fails while the corresponding high-vs-low and p=0.975 tests pass, wording is restricted to `concentrated at high fidelity`, without claiming continued strengthening into very high fidelity.

## Secondary outcomes
- selected-minus-neutral mean cell fitness (`Delta_fitness`);
- selected-minus-neutral raw chemistry divergence (`DeltaC_pop`);
- exact 18-point descriptive curves for all four quantities.

Secondary outcomes cannot rescue failure of either primary family.

## Interpretation boundary
Success supports a mechanism-level statement within the tested models: reliable inheritance is required for strong selection-generated relational organization and its relation-specific adaptive value. The discrete grid does not establish a continuously estimated critical fidelity and does not establish universality, scaffold endogenization, autonomous agency, or full Walker-Davies reversal.
