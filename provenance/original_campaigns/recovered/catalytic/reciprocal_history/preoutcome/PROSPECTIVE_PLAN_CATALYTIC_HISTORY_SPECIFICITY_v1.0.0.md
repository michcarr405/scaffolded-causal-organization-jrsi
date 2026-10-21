# Prospective Confirmatory Plan - Catalytic-Complex Historical Specificity v1.0.0

## Status
Frozen before generation or inspection of any production outcomes from this campaign.

## Purpose
Test the remaining cross-realization signature not yet directly tested in the catalytic-complex realization: whether distinct scaffold histories generate distinct inherited organizations whose expression depends on historical match when evaluated under the same current scaffold.

This is a new prospective confirmation campaign. It does not reinterpret prior catalytic outcomes.

## Fixed microscopic realization
Use the frozen catalytic-complex realization without modification:
- 4 catalyst monomer types; 10 unordered dimers;
- 32 dimers per protocell;
- population size 48;
- 180 evolutionary generations;
- catalytic matrix seed 51073;
- mutation probability 0.01;
- transmission fidelity p=0.975;
- selection coefficient 24;
- Michaelis K=1;
- scaffold strength s=2.0;
- same matrix balancing, transmission, mutation, fitness, and relational-erasure definitions as the original catalytic confirmatory campaign.

## Historical scaffolds
Two equal-strength, zero-sum, orthonormal reaction-field directions are fixed before outcomes:

H1 = e1 = [1,-1,0,0]/sqrt(2)

H2 = e2 = [1,1,-2,0]/sqrt(6)

They have equal norm and are orthogonal. No scaffold direction will be changed after outcomes are seen.

## Block design
Use 30 entirely new root-seed blocks. Within each block:
1. generate one founder population;
2. evolve one selected lineage under H1;
3. evolve one selected lineage under H2;
4. evolve two neutral lineages from the same founder, with uniform parent sampling and otherwise identical transmission/mutation dynamics;
5. freeze all four endpoints;
6. evaluate every endpoint under both current probe scaffolds H1 and H2, with no further evolution.

The independent inferential unit is the root-seed block.

## Primary historical-specificity contrast
For history h in {1,2}, define the selected-minus-neutral historical response under current probe B as

R_h(B) = F(S_h | B) - F(N_h | B),

where F is mean cell fitness, S_h is the selected endpoint evolved under H_h, and N_h is its paired neutral endpoint.

The preregistered reciprocal matching-history contrast is

H_fit = 1/2 * [(R_1(H1) - R_2(H1)) + (R_2(H2) - R_1(H2))].

This holds current probe conditions fixed within each comparison. H_fit > 0 means that the selected-minus-neutral response is preferentially expressed when evolutionary history matches the current scaffold.

### Primary success criterion
The catalytic historical-specificity prediction is confirmed only if BOTH conditions hold:
- H_fit > 0 in at least 24 of 30 independent blocks; and
- the two-sided 99% root-block bootstrap percentile confidence interval for mean H_fit excludes zero on the positive side.

Report the one-sided exact sign-test p-value as a descriptive inferential statistic. Zeros count as non-positive.

## Secondary non-gating analyses
These are frozen before outcomes but do not determine the primary confirmation decision.

1. Selected-only reciprocal match contrast:
H_selected = 1/2 * [(F(S1|H1)-F(S2|H1)) + (F(S2|H2)-F(S1|H2))].

2. Neutral reciprocal contrast H_neutral defined analogously. The identity H_fit = H_selected - H_neutral will be checked numerically.

3. Relational-value history specificity using V_rel:
R^V_h(B) = V_rel(S_h|B) - V_rel(N_h|B),
H_Vrel = 1/2 * [(R^V_1(H1)-R^V_2(H1)) + (R^V_2(H2)-R^V_1(H2))].

4. Full 2 x 2 selected-minus-neutral cross-evaluation matrix for fitness and V_rel.

5. Endpoint R_pop and C_pop values under both probes for descriptive interpretation only.

No secondary endpoint may rescue a failed primary H_fit result.

## Randomization and seeds
Campaign namespace root starts at 9,300,000. For block b=0..29:
- founder seed = 9,300,000 + b;
- selected-H1 evolution seed = 9,310,000 + b;
- selected-H2 evolution seed = 9,320,000 + b;
- neutral-H1 evolution seed = 9,330,000 + b;
- neutral-H2 evolution seed = 9,340,000 + b.

These seeds are outside the original catalytic confirmatory namespace. The seed ledger is frozen with this plan.

## Bootstrap
Use 100,000 root-block bootstrap resamples with analysis RNG seed 93,510, sampling 30 block values with replacement. Report the 0.5th and 99.5th percentiles for the two-sided 99% interval.

## Interpretation rule
If the primary criterion passes, the catalytic realization may be described as prospectively confirming historical specificity: distinct scaffold histories generate inherited organizations with different responses under the same current physical context. This supports filling the catalytic history-specificity cell in the cross-realization evidence matrix as Confirmed.

If the primary criterion fails, the cell remains Not tested/Not confirmed as appropriate; no post hoc scaffold pair, threshold, endpoint switch, or seed extension will be used to rescue the claim.
