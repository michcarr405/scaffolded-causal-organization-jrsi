# Post-confirmatory mechanistic mapping plan — abstract lattice fidelity × time surface v1.0.0

## Status and evidentiary role
This campaign is a **post-confirmatory mechanistic mapping study**. It does not replace or alter the frozen `ABSTRACT_LATTICE_CONFIRMATORY_v1.0.0` record. The model architecture and parameters are inherited unchanged from that confirmation. The purpose is to map emergence dynamics at much higher temporal and fidelity resolution and to determine whether the previously confirmed high-fidelity amplification is better described as a smooth storage-capacity curve, a threshold-like regime, or a combination of fidelity-dependent acquisition rate and stable amplitude.

The plan, configuration, seed ledger, and production implementation are SHA256-frozen before new outcomes are generated.

## Frozen model
Identical to the confirmed abstract lattice control:
- ring of N=24 inherited binary sites x_i in {-1,+1};
- population=64;
- beta=1.4, gamma=1.4, kappa=0.5, lambda=4.0;
- mutation mu=0.003;
- selection softmax coefficient=1.5;
- scaffold amplitude=1.2;
- fixed balanced task Y from task seed 1207;
- external scaffold and microscopic readout never evolve;
- relational erasure uniformly permutes site labels within each genome, preserving its +1/-1 composition while destroying spatial relation.

## New independent blocks
30 new root-seed blocks, disjoint from discovery and confirmation. The root-seed block is the inferential unit. All fidelity conditions within a block share the same founder population.

## Primary dense fidelity × time arm
Historical scaffold theta_H=0.

Transmission fidelity grid:

`p = 0.000, 0.025, 0.050, ..., 0.975, 1.000` (41 values).

For every p and block, evolve selected and matched-neutral populations for generations t=0..50, saving the complete inherited population X at every generation.

Core diagnostics at every generation:
- selected and neutral mean fitness F_S(t), F_N(t), and DeltaF(t);
- selected and neutral relational value V_rel^S(t), V_rel^N(t), and DeltaV_rel(t);
- nearest-neighbor correlation;
- site heterozygosity;
- projection of mean inherited state onto the fixed task Y;
- projection onto the historical scaffold basis e1;
- all 24 site means xbar_i(t).

The relational-value estimator uses 12 composition-preserving random permutations per genome and paired common-random erasure permutations for selected and neutral populations at the same block/p/t. This lowers Monte Carlo noise in DeltaV_rel. It is a mapping estimator and does not replace the estimator used in the frozen confirmatory campaign.

## Sentinel continuation arm
The same evolutionary trajectories at

`p = {0.50, 0.70, 0.80, 0.90, 0.95, 1.00}`

continue from generation 50 through generation 200. Summary diagnostics are saved every generation. Full inherited-state snapshots are saved at t={100,150,200}.

The sentinel purpose is to determine whether t=50 captures the stable regime. Define:
- `A50(p)` = mean DeltaV_rel over generations 41..50;
- `A200(p)` = mean DeltaV_rel over generations 191..200.

For p with |A200| >= 0.02, descriptive stability is considered close when both |A50-A200| < 0.01 and |A50-A200|/|A200| < 0.10. For smaller A200, only the absolute criterion is used. This is a diagnostic convention, not a confirmatory hypothesis test.

## History-specificity dynamics arm
At p=0.95, evolve under four histories theta_H={0, pi/2, pi, 3pi/2}. The theta_H=0 trajectory is reused from the dense arm; three additional histories are evolved with new preassigned RNG streams. Complete populations are saved every generation 0..50.

At t={0,5,10,15,20,30,40,50}, cross-evaluate every history under all four current scaffolds. Save matching-history fitness advantage and matching-history DeltaV_rel advantage.

## Acquisition-expression and anisotropy dynamics
Using the frozen theta_H=0, p=0.95 populations from the dense arm, at t={0,5,10,15,20,30,40,50}:
- expression probes use alpha B_H for alpha={0,0.2,...,1.8};
- anisotropy probes use B_H + 0.6[cos(phi)e1+sin(phi)e2] for the same 12 equal-distance directions as the confirmatory campaign.

This allows the emergence times of acquisition-expression separation and anisotropic retrieval to be mapped without rerunning evolution.

## Frozen mechanistic summaries
### Amplitude and rate
For every p:
- empirical plateau amplitude `A50_emp(p)` = mean DeltaV_rel(t) for t=41..50;
- empirical onset times `t10`, `t50`, `t90` are the first generations at which the block-mean trajectory reaches 10%, 50%, or 90% of its empirical plateau above the t=0 baseline and remains at or above that level for at least 3 of the next 4 generations;
- fit the descriptive model `c + A[1-exp(-k t)]` to the block-mean trajectory. Report k only when the empirical amplitude is >0.01 and fit R^2 >=0.5.

### Fidelity-response geometry
Fit `A50_emp(p)` with three prespecified descriptive models:
1. four-parameter logistic;
2. continuous two-slope segmented linear model with one breakpoint;
3. hard two-plateau step model with one breakpoint.

Compare AICc on the 41 block-mean fidelity points. Bootstrap root blocks to estimate the logistic p10, p50, p90 and the frequency with which each model has the lowest AICc. These comparisons are descriptive model mapping, not a preregistered phase-transition test.

### Relational versus fitness dynamics
Compute the same empirical t10/t50/t90 quantities for DeltaF. Compare them with DeltaV_rel at each p. No significance-threshold definition is used for onset.

## Interpretation boundaries
This study may establish the shape and timescale of the already-confirmed fidelity dependence. It does not by itself establish a universal critical fidelity, a thermodynamic phase transition, universality, chemical realism, scaffold endogenization, autonomous agency, or full Walker-Davies reversal.
