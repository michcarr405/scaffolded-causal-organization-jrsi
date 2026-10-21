# Prospective confirmatory replication plan - catalytic-complex transmission fidelity v1.0.0

## Status
Frozen before generation or inspection of any production outcome in this campaign.

## Purpose
Independently replicate the previously established catalytic transmission-fidelity dependence using a new 30-block seed namespace and the exact 18-point fidelity grid. The earlier fidelity result is scientifically recorded but its exact raw archive is unavailable in the active source set. This campaign is therefore a new prospective replication, not a reconstruction or relabeling of the missing archive.

## Microscopic realization
Use the frozen catalytic-complex realization without scientific modification:
- 4 monomer catalyst types forming 10 unordered inherited dimer species;
- 32 dimers per protocell; population size 48;
- fixed 10x4 catalytic matrix generated from affinity seed 51073 and matrix-balanced exactly as in the original confirmatory implementation;
- four essential reaction channels with saturating Michaelis readout K=1;
- fitness = harmonic mean of the four essential reaction rates;
- historical reaction-field direction = [1,-1,0,0]/sqrt(2);
- scaffold strength s=2.0;
- mutation probability per dimer = 0.01;
- selection coefficient = 24;
- 180 generations;
- selected and neutral treatments begin from the identical founder population within each root-seed block and fidelity.

Only transmission fidelity p varies.

## Frozen 18-point fidelity grid
`0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975, 1.0`

## Independent block design
- 30 entirely new root-seed blocks.
- The same founder population is used across all 18 fidelity values within a block.
- Selected and neutral evolutionary RNG streams are distinct at every block x fidelity combination.
- All seed identities are deterministic 128-bit values derived from a campaign-specific SHA256 namespace.
- Seed identities will be compared against every accessible catalytic seed ledger/source. The inaccessible earlier fidelity ledger cannot be literal-file compared; this limitation is recorded rather than inferred away.

## Primary endpoints
For each block b and fidelity p:
- `Delta_R_pop(p) = R_pop_selected(p) - R_pop_neutral(p)` in bits.
- `Delta_V_rel(p) = V_rel_selected(p) - V_rel_neutral(p)` in fitness units.

Here `R_pop` is JSD between the intact aggregate dimer distribution and the random-pairing distribution at fixed monomer marginals. `V_rel` is aggregate fitness(intact) minus aggregate fitness(randomly re-paired counterfactual) under identical reaction physics.

## Primary contrast families
Define:
- LOW = {0,0.1,0.2,0.3,0.4,0.5,0.6}
- HIGH = {0.9,0.925,0.95,0.975,1.0}
- TRANSITION = {0.85,0.875,0.9}
- VERY_HIGH = {0.95,0.975,1.0}

### R_pop family
R1: `mean_HIGH Delta_R_pop - mean_LOW Delta_R_pop > 0`.
R2: `mean_VERY_HIGH Delta_R_pop - mean_TRANSITION Delta_R_pop > 0`.
R3: `Delta_R_pop(p=0.975) > 0`.

### V_rel family
V1: `mean_HIGH Delta_V_rel - mean_LOW Delta_V_rel > 0`.
V2: `mean_VERY_HIGH Delta_V_rel - mean_TRANSITION Delta_V_rel > 0`.
V3: `Delta_V_rel(p=0.975) > 0`.

## Frozen family-wise success rule
For every contrast in each three-test family:
1. the root-block mean contrast is positive;
2. the lower bound of a two-sided 98.33333333% root-block bootstrap CI is >0;
3. the Holm-adjusted one-sided exact sign-test p is <0.05 within that family.

Additional guard: the block-mean endpoint must be positive at each HIGH fidelity value for both endpoint families.

Strong prospective replication support requires all six primary contrasts and the high-fidelity positivity guard to pass. If only one family passes, wording must be restricted to that endpoint family. No significance-defined critical fidelity or strict monotonicity claim is permitted.

## Descriptive curve reporting
After the frozen tests are evaluated, report the full 18-point block means and 95% root-block bootstrap intervals for both endpoints. Curve shape can be described descriptively. The intended Figure 4 use is:
- Panel D: Delta_R_pop vs transmission fidelity p.
- Panel E: Delta_V_rel vs transmission fidelity p.

## Secondary saved quantities
At every block x fidelity endpoint save selected and neutral fitness, R_pop, C_pop, and V_rel, plus full selected and neutral endpoint states. These are not primary promotion criteria.

## Run count
18 fidelities x 30 blocks x 2 evolutionary arms = 1080 evolutionary runs.

## Interpretation boundary
A successful campaign supports high-fidelity amplification of selection-generated relational organization and its adaptive value in this catalytic realization. It does not establish a universal critical fidelity, strict monotonicity, scaffold endogenization, or universality across all inheritance systems.
