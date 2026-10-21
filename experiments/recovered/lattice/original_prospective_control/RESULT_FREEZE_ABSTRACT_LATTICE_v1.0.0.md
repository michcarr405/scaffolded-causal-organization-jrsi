# Result freeze — Minimal abstract lattice theoretical control v1.0.0

## Classification
**STRONG PROSPECTIVE SUPPORT** for all four preregistered qualitative properties in the intentionally abstract lattice control.

The scientific plan, config, formal contrasts, seed ledger, and discovery anisotropy template were frozen and SHA256-hashed before generation of confirmatory outcomes. Thirty entirely new root blocks were used.

## Frozen architecture
Inherited binary states X act with a fixed external field B through

`P(z_i=1|X,B)=sigmoid[1.4 b_i + 1.4 x_i + 0.5(x_{i-1}+x_{i+1})]`.

Only X evolves. The external scaffold, local interaction law, and fixed nonlinear task/fitness mapping do not evolve. Relational erasure uniformly permutes x_i within each genome, exactly preserving the number of +1/-1 components while destroying their spatial relation to scaffold and neighbors.

## P1 — Scaffold-specific acquisition: PASS
Primary contrast C1 compared, at each current probe scaffold, the selected population trained under the matching scaffold history with selected populations trained under the other three histories, then averaged the four within-probe contrasts per root block.

- mean C1 = `+0.00854079`
- 99% bootstrap CI = `[0.00734351, 0.00976737]`
- positive blocks = `30/30`
- Holm-adjusted one-sided sign p = `4.66e-9`

The effect is modest in magnitude but extremely consistent: holding current physics fixed, the matching evolutionary history has higher selected fitness than mismatched histories.

## P2 — Fidelity dependence: PASS
C2 compared high-fidelity `p={0.90,0.925,0.95,0.975,1.0}` with low-fidelity `p={0,0.1,...,0.6}` for selected-minus-neutral relational causal value DeltaV_rel.

- mean C2 = `+0.14408470`
- 99% CI = `[0.14144563, 0.14665552]`
- positive blocks = `30/30`
- Holm p = `4.66e-9`

C3 tested the operating point `p=0.975`:

- mean DeltaV_rel = `+0.17188971`
- 99% CI = `[0.16718394, 0.17658666]`
- positive blocks = `30/30`
- Holm p = `4.66e-9`

The dense mean curve rises from approximately zero at p=0 to `0.18116` at p=1.0. The frozen claim is regime-level heredity dependence, not a continuously estimated threshold.

## P3 — Acquisition/expression separation: PASS
Populations were evolved under the full training scaffold and then frozen. The same inherited populations were probed under scaled current scaffolds alpha B_H.

C4 predicted greater relational expression at alpha=0.4 than at the training condition alpha=1.0:

- mean C4 = `+0.10597441`
- 99% CI = `[0.10290756, 0.10892076]`
- positive blocks = `30/30`
- Holm p = `4.66e-9`

Mean DeltaV_rel was `0.26880` at alpha=0.4 versus `0.16282` at alpha=1.0. Descriptively, the full discovery-confirmatory control curve was largest when the scaffold was removed and declined with increasing current scaffold amplitude. Therefore acquisition under B_H and maximal expression of the acquired inherited organization are clearly distinct in this minimal control.

## P4 — Equal-distance anisotropic retrieval: PASS
All 12 probes lay at the same Euclidean distance r=0.6 from the training scaffold.

C5 predicted DeltaV_rel(phi=pi) > DeltaV_rel(phi=0):

- mean C5 = `+0.15742683`
- 99% CI = `[0.15369067, 0.16105461]`
- positive blocks = `30/30`
- Holm p = `4.66e-9`

The complete 12-angle confirmatory mean profile reproduced the frozen discovery profile with Pearson `r=0.999956` (frozen structural requirement >0.90).

Equal environmental displacement magnitude therefore does not determine retrieval magnitude in the abstract control; direction matters strongly.

## Overall interpretation
The same four qualitative phenomena now survive in a deliberately nonchemical lattice control:
1. scaffold-specific acquisition;
2. strong transmission-fidelity dependence;
3. separation of acquisition conditions from expression conditions;
4. anisotropic retrieval at equal environmental distance.

This substantially reduces the possibility that these effects require motifs, segment chemistry, catalyst dimers, saturating reaction networks, or other biochemical particulars shared by the two pre-genetic microscopic realizations.

The appropriate manuscript claim remains limited: the abstract control supports the proposed causal architecture as a mechanism-level explanation. It does not establish universality, chemical realism, scaffold endogenization, autonomous agency, or a universal critical fidelity.

## Provenance note
The production code itself was not included in the pre-outcome SHA256 set, although the scientific plan, full configuration, seed ledger, formal contrasts, and discovery template were. This limitation is recorded in `IMPLEMENTATION_AUDIT.md`; the final production code and all results are included in the archival hash manifest.
