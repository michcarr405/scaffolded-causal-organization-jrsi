# Confirmatory Result Freeze — Catalytic-Complex Protocell v1.0.0

## Status
Prospective plan SHA256 frozen before confirmatory outcomes:
`8088e422a9248b72f759de886c22e4fbdea20f3247ad30513e9d3f5313ddcdb3`

Microscopic realization: nonspatial catalytic-complex protocells with compositional inheritance of catalyst dimers, fixed saturating reaction kinetics, and an externally supplied reaction-rate asymmetry. There are no sequences, motifs, spatial segments, motif-position affinities, or Model B chemical softmax.

## Confirmatory design
- Independent catalytic affinity matrix seed: 51073 (not used in discovery).
- 30 entirely new paired root-seed blocks.
- 4 monomer catalyst types -> 10 unordered dimer species.
- 32 inherited dimers per protocell; population 48; 180 generations.
- Historical reaction-field strength 2.0; fidelity 0.975.
- Selected and neutral treatments began from the same founder population within block.
- Relational erasure preserved aggregate monomer marginals and randomly re-paired the same monomers, destroying inherited dimer identity while retaining the parts.

## Primary results
All six prospectively frozen primary criteria passed.

### P1 — Physical cost
The external reaction-field scaffold lowered founder fitness in 30/30 blocks.

Mean scaffold effect on founder fitness:

`-0.11310`

PASS.

### P2 — Selection-dependent fitness recovery
Selected-minus-neutral endpoint fitness was positive in 30/30 blocks.

Mean Δfitness:

`+0.05624`

One-sided exact sign p = `9.31e-10`.

PASS.

### P3 — Adaptive relational causality
Define `V_rel = fitness(intact dimer organization) - fitness(randomly re-paired counterfactual)` at fixed monomer marginals and identical reaction physics.

Selected-minus-neutral ΔV_rel was positive in 29/30 blocks.

Mean ΔV_rel:

`+0.03224`

One-sided exact sign p = `2.89e-8`.

PASS.

### P4 — Selection-generated relational organization
Selected-minus-neutral aggregate dimer relational organization (`R_pop`, JSD from random pairing at fixed monomer marginals) was positive in 28/30 blocks.

Mean ΔR_pop:

`+0.06851 bits`

One-sided exact sign p = `4.34e-7`.

PASS.

### P5 — Acquisition-expression separation
The same frozen endpoint populations were assayed at the historical training strength 2.0 and under a weaker probe strength 0.5, with no further evolution.

`ΔC_pop(probe=0.5) > ΔC_pop(train=2.0)` in 25/30 blocks.

Mean increase under weaker probing:

`+0.000339 bits`

One-sided exact sign p = `1.62e-4`.

PASS.

### P6 — Equal-distance anisotropy
Eight probe scaffolds were all located exactly the same squared Euclidean distance (`d^2=1`) from the historical scaffold.

Nevertheless, historical-match advantage differed strongly by direction:

Friedman χ² = `27.53`, p = `2.67e-4`.

Range of the eight direction means:

`0.02844 fitness units`.

PASS.

## Secondary result — raw chemical divergence
Selected-minus-neutral relational chemistry divergence at the training scaffold was positive in 24/30 blocks.

Mean ΔC_pop:

`+0.000443 bits`.

At the weaker probe strength 0.5 the mean was:

`+0.000783 bits`.

Raw divergence magnitude was deliberately secondary because discovery across six independent catalytic matrices showed it to be more microscopic-kernel-dependent than the adaptive value of relational organization.

## Post-freeze diagnostic — scaffold remains costly after adaptation
This was not a frozen primary endpoint. Re-evaluating the evolved selected populations with and without the external scaffold showed that the scaffold remained costly after adaptation in 30/30 blocks.

Mean selected fitness:
- scaffold present (strength 2.0): `0.41543`
- scaffold removed (strength 0): `0.46606`

Mean persistent scaffold cost:

`-0.05063`

Thus selection partially compensated for the scaffold without eliminating its direct cost.

## Discovery ensemble context
Before this confirmatory test, six additional independently generated catalytic matrices were examined exploratorily. Mean selected-minus-neutral fitness recovery and relation-specific fitness benefit were positive for all 6/6 matrices. Raw selected-minus-neutral chemical JSD was positive for 4/6, reinforcing the interpretation that selection robustly makes relational organization *adaptively useful* even though the magnitude of undirected chemistry divergence is more dependent on microscopic details.

## Interpretation
The core v0.3 mechanism survives in a substantially different microscopic realization:

`external reaction-field asymmetry -> selection -> inherited catalytic-complex organization -> relation-specific change in reaction dynamics and fitness`.

The result does not rely on sequence motifs, segment positions, spatial scaffolds, or the Model B readout. It also reproduces two higher-order predictions of the reduced theory: (i) acquisition and expression are separable, and (ii) historical specificity is anisotropic at fixed environmental displacement magnitude.

## Limits
- This is still an abstract computational chemistry, not a chemically calibrated protocell model.
- Dimer identity is directly compositionally inherited; the model does not explain the prebiotic origin of stable catalytic complexes.
- The external reaction-field scaffold remains supplied by the environment; no scaffold endogenization is demonstrated.
- Formal PhiID causal emergence is not tested.
