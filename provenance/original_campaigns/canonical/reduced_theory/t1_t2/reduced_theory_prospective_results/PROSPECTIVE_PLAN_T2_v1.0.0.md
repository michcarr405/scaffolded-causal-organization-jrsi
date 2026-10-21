# Prospective Test T2 v1.0.0 — Scaffold-distance law

Status: DESIGN FROZEN BEFORE NEW EVOLUTIONARY RUNS
Date: 2026-09-13
Theory source: REDUCED_THEORY_SCAFFOLDED_CAUSAL_ORGANIZATION_v0.1

## Question
Does the historical-match advantage of an evolved lineage scale with squared physical distance between its training scaffold and alternative equal-strength scaffold identities?

## Canonical evolution condition
Use canonical Model B parameters from the DCC confirmatory campaigns:
N=80; n_olig=8; L=60; alphabet=4; k=5; local states=4; segments=4; theta=1.2; beta=4.0; p_inherit=0.975; mutation=0.001; reward=2.0; penalty=0.5; generations=250; affinity_seed=123.

Historical/training scaffold H = [2,0,3,1].

Run 30 entirely new paired root-seed blocks. In each block SELECTED and NEUTRAL populations begin from the same initial population and share purpose-separated RNG streams as in the frozen confirmatory implementation. Neutral reproduction uses uniform weights.

## Probe scaffold family
At generation 250 freeze both populations. Probe each frozen population under all 24 permutations of [0,1,2,3], at the same beta=4.0 and theta=1.2, with no further evolution.

Use the same local-state uniform random numbers across all 24 probe mappings and across selected/neutral within each root block (common random numbers). Use 32 probe draws per mapping.

For every alternative mapping j, define k_j as Hamming distance from H. For permutations of four distinct states, k is in {2,3,4}; k=0 is the historical scaffold.

Because each differing segment replaces one beta one-hot bias with another, squared Frobenius distance between scaffold logit-bias matrices is

||b_H-b_j||^2 = 2 beta^2 k_j.

## Outcome
For each block and alternative mapping j:
A_selected(j) = F_selected(H) - F_selected(j)
A_neutral(j)  = F_neutral(H)  - F_neutral(j)
DeltaH(j) = A_selected(j) - A_neutral(j).

Average DeltaH(j) within each distance class k for each independent root block, producing DeltaH_block(k).

## Frozen theory prediction
Reduced Theory v0.1 gives, for equal-strength scaffolds,

DeltaH_ij proportional to ||b_i-b_j||^2.

Therefore, after averaging over equal-distance scaffold identities:

DeltaH(k) = lambda k, lambda > 0.

Primary shape predictions are zero-parameter after normalization to k=2:
DeltaH(3)/DeltaH(2) = 1.5
DeltaH(4)/DeltaH(2) = 2.0.

A second directional prediction is DeltaH(4) > DeltaH(3) > DeltaH(2) > 0.

## Primary evaluations
1. Report mean DeltaH(k) for k=2,3,4 using root blocks as the inferential unit.
2. Report observed normalized ratios DeltaH(3)/DeltaH(2) and DeltaH(4)/DeltaH(2), with paired-block bootstrap 95% CIs (50,000 resamples; fixed bootstrap seed 390716381).
3. Report within-block contrasts DeltaH(3)-1.5 DeltaH(2) and DeltaH(4)-2 DeltaH(2), with bootstrap 95% CIs. CIs containing zero support the predicted proportional shape; departures will be reported, not redefined.
4. Report directional within-block contrasts DeltaH(3)-DeltaH(2) and DeltaH(4)-DeltaH(3), with one-sided exact sign tests.
5. Fit a through-origin line DeltaH(k)=lambda k only as a descriptive amplitude fit; report R^2 and slope.

## Secondary diagnostics
- Individual alternative-scaffold values within each Hamming class to assess anisotropy caused by motif-affinity structure.
- Selected and neutral match advantages separately.
- C_down under each probe mapping is not a primary endpoint for T2.

## Interpretation boundary
Support for the distance law would establish a geometric prediction of scaffolded historical organization in canonical Model B. It would not establish scaffold independence, endogenization, or universality outside architectures with analogous physical and heritable degrees of freedom.
