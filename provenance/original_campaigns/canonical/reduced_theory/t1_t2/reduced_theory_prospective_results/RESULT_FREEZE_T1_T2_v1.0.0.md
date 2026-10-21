# Reduced Theory Prospective Tests T1–T2 v1.0.0

## Status
Prospective plans were SHA256-frozen before the corresponding assays/runs. T1 used previously frozen populations but a newly prespecified dense probe assay. T2 used 30 entirely new paired evolutionary root seeds and a prespecified 24-mapping probe family.

## T1 — frozen-population probe-strength retrieval curve

### Frozen prediction
Reduced Theory v0.1 predicted that normalized causal expression would follow a fixed logistic-susceptibility curve with parameters frozen before T1 (c=-0.24648, gamma=0.57002), peaking near probe beta/theta=0.5 on the planned grid.

### Result
The strict zero-parameter quantitative prediction was only partially supported: pooled R^2=0.802, RMSE=0.142. The empirical average retrieval curve peaked at beta/theta=1.00, not 0.50.

However, the core acquisition-expression prediction was strongly supported. The same frozen populations changed causal expression substantially as only the current probe strength changed, and the maximum expression occurred at a substantially weaker scaffold than the strong training conditions. A post-test susceptibility-family refit described the average curve extremely well (R^2=0.995, peak=1.17).

Interpretation: the susceptibility/saturation mechanism remains strongly supported qualitatively, but the v0.1 small-organization approximation was too restrictive to transfer its exact susceptibility parameters across the full probe range. The retrieval peak shifts with training strength, indicating that expression depends on both current scaffold and the magnitude/composition of stored organization.

## T2 — scaffold-distance law

### Frozen prediction
For equal-strength scaffold identities, Reduced Theory v0.1 predicted historical-match advantage proportional to squared physical scaffold distance. For categorical permutation scaffolds this reduces to DeltaH(k) proportional to Hamming distance k, with predicted normalized ratios 1 : 1.5 : 2 for k=2:3:4.

### Result
Historical-match advantage increased monotonically with scaffold distance in every independent block: mean DeltaH(k=2)=6.582, k=3=9.684, k=4=11.854. Both successive distance contrasts were positive in 30/30 blocks (one-sided exact sign p=9.31e-10 and 9.31e-10). A through-origin proportional law gave R^2=0.958.

The exact linear-distance prediction was not exact. Observed ratios were k3/k2=1.471 (theory 1.5) and k4/k2=1.801 (theory 2.0), with bootstrap intervals excluding the exact theoretical values. Thus the local quadratic theory correctly predicted the ordering and much of the geometry, but finite-distance nonlinear corrections are required, especially at the largest scaffold separation.

## Overall conclusion
The prospective tests support the general reduced-theory architecture but reject its strongest first-order quantitative simplifications. Two conclusions survive especially well:

1. **Acquisition and expression are separable.** Organization acquired under a strong scaffold can be expressed more strongly under a weaker current scaffold, even with the evolved population frozen.
2. **Historical organization has geometry.** The selection-generated historical-match advantage grows systematically with physical distance from the training scaffold.

The next theoretical revision should therefore retain the acquisition-expression decomposition but replace the strictly local expression law and linear finite-distance match law with controlled nonlinear/finite-amplitude corrections. A new v0.2 theory should be derived before further confirmatory simulation.
