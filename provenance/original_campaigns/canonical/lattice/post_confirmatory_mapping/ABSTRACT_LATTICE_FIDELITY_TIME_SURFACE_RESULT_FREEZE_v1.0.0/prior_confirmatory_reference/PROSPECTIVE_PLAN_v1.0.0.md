# Prospective confirmatory plan — Minimal abstract lattice control v1.0.0

## Status
Frozen after the v0.1.0 discovery phase and before generation or inspection of any v1.0.0 confirmatory outcomes.

## Purpose
Test whether the four qualitative properties motivating the intentionally abstract control survive on entirely new root blocks after the model and tests are frozen: (1) scaffold-specific acquisition, (2) transmission-fidelity dependence, (3) separation of acquisition from maximal expression, and (4) equal-distance anisotropic retrieval.

This is a theoretical control, not a third pre-genetic microscopic realization.

## Frozen architecture
A ring of N=24 sites has inherited binary variables x_i in {-1,+1}. The external scaffold B=(b_i) is supplied and never evolves. The microscopic readout is

P(z_i=1 | X,B) = sigmoid[ beta b_i + gamma x_i + kappa(x_{i-1}+x_{i+1}) ].

Only X is transmitted/evolved. Fitness is a fixed nonlinear function of the expected mismatch of Z to a fixed binary task pattern Y:

W(X,B) = exp[-lambda * (1/N) sum_i P(z_i != y_i | X,B)].

The task Y and the physical laws are fixed for all experiments and do not depend on evolutionary history.

### Fixed constants
- N=24 sites; ring topology.
- population=64.
- generations=200.
- beta=1.4; gamma=1.4; kappa=0.5; lambda=4.0.
- post-transmission bit mutation mu=0.003.
- selection uses softmax weights exp(1.5 * standardized(log W)).
- scaffold amplitude A=1.2.
- two zero-mean unit-RMS Fourier scaffold basis vectors e1=cos(2 pi i/N), e2=sin(2 pi i/N).
- fixed balanced task pattern Y generated once by RNG seed 1207.
- non-fidelity experiments use p=0.95, matching discovery.

Transmission: an offspring site copies the parental x_i with probability p; otherwise it is replaced by an unbiased random {-1,+1} state, followed by the fixed mutation process.

## Relational erasure
For each genome, E(X) is obtained by uniformly permuting its site labels. This exactly preserves its number of +1 and -1 inherited components while destroying their spatial relation to the scaffold, task, and neighboring positions. The physical readout and fitness law are then held unchanged.

V_rel(B) = E[W(X,B)] - E[W(E(X),B)].

DeltaV_rel is selected minus matched-neutral V_rel.

## Replication and pairing
- 30 entirely new root blocks, disjoint from discovery seeds.
- Within each block, all treatments begin from the same frozen founder population.
- Selected and neutral evolution use distinct preassigned RNG streams.
- Root block is the inferential unit.

## P1 — Scaffold-specific acquisition
Train selected and neutral populations under four cardinal scaffold histories theta_H in {0, pi/2, pi, 3pi/2} at p=0.95. Cross-evaluate every evolved population under all four current scaffolds.

Primary block contrast:
C1 = mean_j [ W_S(history=j, probe=j) - mean_{h != j} W_S(history=h, probe=j) ].

Prediction: C1 > 0. This holds current physics fixed within each probe and asks whether the evolutionary history matching that scaffold has a performance advantage over the other three histories.

## P2 — Fidelity dependence
Under history theta_H=0, use the exact 18-point grid
p={0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.75,0.8,0.825,0.85,0.875,0.9,0.925,0.95,0.975,1.0}.

Primary contrasts:
C2 = mean_{p=0.90,0.925,0.95,0.975,1.0} DeltaV_rel(p) - mean_{p=0,0.1,0.2,0.3,0.4,0.5,0.6} DeltaV_rel(p) > 0.
C3 = DeltaV_rel(p=0.975) > 0.

The claim is regime-level heredity dependence, not strict pointwise monotonicity or a continuously estimated critical threshold.

## P3 — Acquisition/expression separation
Use the p=0.95 populations trained under B_H=A e1. Freeze X and probe the same populations under alpha B_H for alpha={0,0.2,...,1.8}.

Primary contrast:
C4 = DeltaV_rel(alpha=0.4) - DeltaV_rel(alpha=1.0) > 0.

Prediction: a substantially weaker current scaffold expresses more of the selection-built relational contribution than the training scaffold itself. The full curve is descriptive and cannot replace C4.

## P4 — Equal-distance anisotropic retrieval
Using the same frozen theta_H=0 populations, probe
B_P(phi)=B_H + r[cos(phi)e1+sin(phi)e2]
with r=0.6 and 12 equally spaced angles phi in [0,2pi). Every probe is at identical Euclidean distance from B_H.

Primary contrast:
C5 = DeltaV_rel(phi=pi) - DeltaV_rel(phi=0) > 0.

Structural criterion: the 12-point confirmatory mean DeltaV_rel profile must have Pearson correlation r_profile > 0.90 with the frozen discovery profile (the discovery source files and hashes are archived with this plan).

## Frozen inference
For C1-C5:
- mean block contrast must have the predicted sign;
- lower bound of a two-sided 99% root-block bootstrap CI (50,000 resamples) must exceed zero;
- one-sided exact sign-test p values are Holm-adjusted across C1-C5 and must be <0.05.

Overall strong support requires C1-C5 all pass, r_profile>0.90, all frozen run IDs complete, and no model parameter, endpoint, contrast, or seed is altered after outcome inspection.

If any primary contrast fails, report the corresponding property as not prospectively confirmed in this control. Other passing properties may be reported individually.

## Interpretation boundary
Success would show that the four qualitative phenomena do not require the biochemical particulars of either Model B or the catalytic-complex realization. It would not establish universality, chemical realism, scaffold endogenization, autonomous agency, a phase transition, or full Walker-Davies reversal.
