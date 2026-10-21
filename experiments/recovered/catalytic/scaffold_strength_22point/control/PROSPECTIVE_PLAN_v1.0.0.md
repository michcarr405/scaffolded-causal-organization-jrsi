# Prospective confirmatory plan - catalytic-complex scaffold-strength sweep v1.0.0

## Status
Frozen before generation of any production outcome in this campaign.

## Purpose
Prospectively test the 22-point scaffold-strength geometry that was identified in a post-confirmatory diagnostic mapping of the catalytic-complex realization. This campaign is independent of the earlier single-strength catalytic confirmation and does not retroactively promote the diagnostic data.

## Microscopic realization
Use the frozen catalytic-complex model without scientific modification:
- 4 monomer types, 10 unordered dimer species;
- 32 dimers per protocell, population size 48;
- fixed catalytic matrix generated from affinity seed 51073;
- four essential reaction channels with saturating Michaelis readout K=1;
- fitness = harmonic mean of the four reaction rates;
- historical scaffold direction = [1,-1,0,0]/sqrt(2);
- transmission fidelity p=0.975;
- mutation probability 0.01;
- selection coefficient 24;
- 180 generations;
- selected and neutral treatments begin from an identical founder population within every block and strength.

Only reaction-field scaffold strength s varies.

## Frozen 22-point scaffold-strength grid
`0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.666667, 2, 2.25, 2.5, 2.75, 3, 3.333333, 3.5, 3.75, 4, 4.25, 4.5, 5, 6, 8`

## Independent block design
- 30 new root-seed blocks.
- Same founder population is used across all 22 strengths within a block.
- Selected and neutral evolutionary RNG streams are distinct and campaign-namespaced.
- Seed identities are derived from a new campaign-specific SHA256 namespace; no production seed identity is reused within this campaign or from the scalar-seed original confirmation.
- The exact inaccessible ledger of the earlier catalytic fidelity campaign cannot be file-compared; this campaign therefore records seed independence by its new derivation namespace and by comparison against every accessible catalytic ledger/source.

## Primary endpoints
For block b and strength s:
- F0(s): generation-0 ancestral/founder mean fitness under scaffold strength s.
- FS(s): selected endpoint mean fitness after 180 generations evolved at s.
- FN(s): neutral endpoint mean fitness after 180 generations evolved at s.
- DS(s)=FS(s)-F0(s): selected change from ancestral baseline.
- DN(s)=FN(s)-F0(s): neutral change from ancestral baseline.
- DREC(s)=FS(s)-FN(s)=DS(s)-DN(s): selection-dependent recovery.

Endpoint R_pop, C_pop, and V_rel are also saved as prespecified secondary outcomes at every strength.

## Primary founder-cost family
Define L={0,0.25,0.5,0.75,1.0} and H={3.0,3.333333,3.5,3.75,4.0}.

F1 - canonical founder cost:
`F0(2)-F0(0) < 0`.

F2 - integrated stronger-scaffold cost:
`mean_H F0(s) - mean_L F0(s) < 0`.

Family pass criterion for each contrast:
1. block-mean contrast has the preregistered sign;
2. the corresponding one-sided edge of a two-sided 97.5% root-block bootstrap CI excludes 0 in the preregistered direction;
3. Holm-adjusted one-sided exact sign-test p<0.05 within the two-test founder-cost family.

## Primary recovery family
Define M={1.0,1.25,1.5,1.666667,2.0,2.25,2.5,2.75,3.0,3.333333,3.5,3.75,4.0}.

R1 - canonical selection-dependent recovery:
`DREC(2) > 0`.

R2 - selected recovery above ancestral baseline over the prespecified recovery band:
`mean_M DS(s) > 0`.

R3 - integrated selection advantage over the same band:
`mean_M DREC(s) > 0`.

Family pass criterion for each contrast:
1. block-mean contrast >0;
2. lower bound of a two-sided 98.333% root-block bootstrap CI >0;
3. Holm-adjusted one-sided exact sign-test p<0.05 within the three-test recovery family.

## Prespecified secondary shape contrast
S1 - recovery is concentrated in the intermediate scaffold regime.
Let P={2.75,3.0,3.333333,3.5,3.75,4.0}; Q={0,0.25,0.5,0.75,1.0,5.0,6.0,8.0}.
Test descriptively and inferentially whether `mean_P DS(s)-mean_Q DS(s)>0` using a root-block bootstrap CI and exact sign test. S1 is not part of the promotion gate.

## Promotion rule
The campaign receives strong prospective support for the Figure 4B-C scaffold-strength story only if both founder-cost contrasts F1-F2 and all three recovery contrasts R1-R3 pass their frozen family-wise criteria.

If F1-F2 pass but any R test fails, founder-cost geometry may be promoted but selection-recovery wording must be narrowed to the tests that passed. If recovery passes but founder-cost family fails, do not claim the full cost-then-recovery sequence from this campaign.

The exact 22-point curve shapes may be described descriptively after the frozen tests are evaluated. Do not infer a universal optimum, phase transition, or critical scaffold strength from significance thresholds.

## Figure use if promoted
Figure 4B: x=scaffold strength s; y=ancestral fitness at generation 0, mean across root blocks with uncertainty.
Figure 4C: x=scaffold strength s; y=fitness change from ancestral baseline; plot DS(s) and DN(s) with uncertainty.

## Run count
22 strengths x 30 blocks x 2 evolutionary arms = 1320 evolutionary runs, plus founder evaluations.
