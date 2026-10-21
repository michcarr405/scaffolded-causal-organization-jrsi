# Prospective Confirmatory Plan — Catalytic-Complex Protocell v1.0.0

## Status
Frozen before generation of any confirmatory evolutionary outcome for catalytic affinity matrix seed 51073.

## Purpose
Test whether the reduced Scaffolded Causal Organization mechanism reappears in a microscopically distinct, nonspatial, nonsequence system.

## Microscopic realization
- 4 catalyst monomer types form 10 unordered catalytic dimers.
- A protocell carries 32 dimers; dimer identities are compositionally inherited through growth/division with fidelity p and low monomer mutation.
- 4 essential reaction channels have fixed dimer-specific catalytic coefficients. The 10x4 catalytic matrix is drawn once from a lognormal distribution using affinity seed 51073 and matrix-balanced so every dimer has equal total catalytic capacity and uniform dimer composition gives equal mean capacity to all reaction channels.
- A zero-sum external reaction-field scaffold multiplies the four reaction propensities. It is externally supplied and does not evolve.
- Reaction rates obey a fixed saturating Michaelis form. Protocell fitness is the harmonic mean of the four essential reaction rates.
- Selection changes only inherited dimer composition.

## Relational intervention
For a frozen protocell population, aggregate dimer frequencies are converted to monomer marginals. The erased counterfactual randomly re-pairs those same monomers, preserving monomer composition while destroying dimer-pair identity. Both intact and erased states are passed through the identical reaction kinetics.

Metrics:
- R_pop: JSD between intact dimer distribution and random-pairing distribution at fixed monomer marginals.
- C_pop: JSD between normalized intact and erased reaction-state distributions.
- V_rel: aggregate fitness(intact) - aggregate fitness(erased).

## Evolutionary design
- New affinity matrix seed: 51073 (not used in discovery).
- 30 entirely new paired root-seed blocks.
- Population size 48; 32 dimers per protocell; 180 generations.
- Historical scaffold: first zero-sum orthonormal basis vector [1,-1,0,0]/sqrt(2).
- Scaffold strength s=2.0.
- Transmission fidelity p=0.975.
- Mutation probability per dimer 0.01.
- Selected and neutral treatments begin from the identical founder population within block.
- Selected parent sampling uses the frozen soft selection coefficient 24; neutral parent sampling is uniform.

## Primary prospective tests
P1. **Physical cost**: scaffolded founder fitness is lower than no-scaffold founder fitness in all 30 blocks.

P2. **Selection-dependent recovery**: endpoint selected-minus-neutral mean cell fitness is positive in at least 27/30 blocks.

P3. **Adaptive relational causality**: endpoint selected-minus-neutral V_rel is positive in at least 24/30 blocks; report one-sided exact sign-test p.

P4. **Selection-generated relational organization**: endpoint selected-minus-neutral R_pop is positive in at least 24/30 blocks; report one-sided exact sign-test p.

P5. **Acquisition-expression separation**: using the same frozen endpoints, DeltaC_pop = C_selected-C_neutral at probe strength 0.5 exceeds DeltaC_pop at the training strength 2.0 in at least 24/30 blocks. No further evolution occurs during probing.

P6. **Equal-distance anisotropy**: frozen endpoints are tested under 8 scaffold directions located 60 degrees from the historical scaffold and separated by 45-degree azimuth increments. All have squared Euclidean distance 1 from history. Direction has a significant within-block effect on DeltaH by Friedman test p<0.01 and the range of the 8 direction means exceeds 0.02 fitness units.

## Secondary outcomes
- Selected-minus-neutral C_pop at the training scaffold is reported but is not a primary pass criterion because discovery showed that raw divergence magnitude is matrix-dependent even when relation-specific adaptive value is robust.
- Endpoint selected and neutral values of R_pop, C_pop, and V_rel.
- Direction means and rankings for the anisotropy assay.

## Interpretation rules
Passing P1-P6 would support generalization of the abstract v0.3 mechanism to a nonspatial catalytic-complex reaction system: external physical asymmetry scaffolds the evolution of inherited relational organization; erasing that relation changes reaction chemistry and adaptive performance; expression depends on current scaffold strength; and historical specificity is directional rather than a scalar function of environmental distance.

Failure of P3 or P4 would count against the core generality claim. Failure of P5 would count against generality of acquisition-expression separation. Failure of P6 would count against generality of anisotropic retrieval.
