# Catalytic-Complex Protocell — Model Charter v1.0.0

## Purpose
Provide a microscopic realization of Scaffolded Causal Organization that is deliberately distinct from Model B.

## What is removed relative to Model B
No sequences, motifs, segment positions, positional affinity matrix, spatial chemical bias, or motif-position softmax sampling.

## Microscopic entities
Four catalyst monomer types can form ten unordered dimers. A protocell is a multiset of 32 dimers. Dimer composition, not a template sequence, is inherited.

## Fixed microscopic physics
Each dimer has a fixed catalytic specificity across four essential reaction channels. The catalytic matrix is generated once per realization and then held fixed. It is matrix-balanced so no dimer has greater total catalytic power and a uniform dimer mixture gives equal mean catalytic capacity to all four reactions.

The environment imposes a zero-sum vector of multiplicative reaction-rate biases. Reaction rates are saturating Michaelis functions of external bias and catalyst composition. Fitness is the harmonic mean of the four reaction rates, so all channels are required.

## Evolution
Selection changes only dimer composition. At reproduction, daughter dimer slots are copied compositionally from the parent with probability p; otherwise they are drawn from the background dimer pool. Low monomer mutation changes dimer identity.

## Relational erasure
The inherited relation is which monomer types are paired into dimers. Erasure keeps the same aggregate monomer frequencies but randomly re-pairs them. Thus the parts are preserved while catalytic-complex relationships are destroyed.

## Abstract correspondence to v0.3
- external asymmetry: reaction-field vector B
- inherited organization: dimer composition / pair structure X
- fixed physical readout: dimer-specific saturating reaction kinetics K(B)
- reproductive consequence: harmonic-mean reaction fitness
- relational intervention: intact dimer pairs -> random re-pairing at fixed monomer marginals
