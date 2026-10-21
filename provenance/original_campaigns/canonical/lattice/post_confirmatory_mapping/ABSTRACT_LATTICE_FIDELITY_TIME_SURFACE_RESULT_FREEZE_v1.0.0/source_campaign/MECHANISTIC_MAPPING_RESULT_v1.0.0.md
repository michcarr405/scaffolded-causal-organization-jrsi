# Abstract lattice fidelity × time mechanistic mapping — result summary v1.0.0

## Evidentiary status
Post-confirmatory mechanistic mapping. The campaign does not replace the frozen abstract-lattice confirmation. The mapping plan, exact model/configuration, new seed ledger, and production code were SHA256-frozen before outcomes.

## Design
- 30 entirely new root-seed blocks.
- 41 fidelities from `p=0` to `1` in increments of `0.025`.
- Complete selected and neutral populations saved every generation `t=0..50`.
- Six sentinel fidelities (`0.50,0.70,0.80,0.90,0.95,1.00`) continued to generation 200.
- Full state trajectories are archived in bit-packed form and can be decoded with `scripts/decode_states.py`.
- History-specificity, acquisition-expression, and equal-distance anisotropy were additionally probed at generations `0,5,10,15,20,30,40,50`.

## 1. The fidelity × time surface is dominated by stable amplitude, not a sharp observed onset threshold
The dense surface shows relational causal value appearing rapidly at all fidelities where a nontrivial stable effect is supported, but the stable amplitude rises strongly and smoothly with transmission fidelity. Empirical `A50`, defined as mean `DeltaV_rel` over generations 41–50, increases from approximately zero at `p=0` to `0.17952` at `p=1`.

Representative empirical plateaus:
- `p=0.50`: `A50=0.02931`
- `p=0.70`: `A50=0.06114`
- `p=0.80`: `A50=0.09395`
- `p=0.90`: `A50=0.13720`
- `p=0.95`: `A50=0.15934`
- `p=0.975`: `A50=0.17255`
- `p=1.00`: `A50=0.17952`

Among the three prespecified descriptive shape models, the smooth logistic had the lowest AICc on the mean curve and won all 1000 root-block bootstrap resamples. The hard-step model was strongly disfavored (`Delta AICc ~=198.5`) and the segmented model was also worse (`Delta AICc ~=44.7`). However, the logistic midpoint hit the physical boundary at `p=1`, so its asymptotic `p50/p90` are not identifiable and must not be interpreted as a critical fidelity. The observed curve is still rising at the upper boundary.

Assumption-light observed-range landmarks are approximately:
- 10% of the observed A50 range: `p ~=0.375`
- 50%: `p ~=0.788`
- 90%: `p ~=0.954`

These are descriptive landmarks, not phase-transition points.

## 2. Fidelity affects both stable amplitude and relative acquisition timescale
The empirical trajectories reveal a nontrivial rate-amplitude tradeoff. Higher fidelity supports much larger stable causal organization, but the relative approach to that larger plateau becomes slower at high fidelity.

For example, empirical `t50` for `DeltaV_rel` is:
- `p=0.50`: generation 1
- `p=0.70`: generation 2
- `p=0.80`: generation 3
- `p=0.90`: generation 3
- `p=0.95`: generation 4
- `p=0.975`: generation 4
- `p=1.00`: generation 6

At `p=0.95`, 90% of the stable amplitude is reached by approximately generation 10. At `p=1.0`, 90% is reached around generation 21. Block-level exponential fits that were identifiable show a strong decline in fitted relative acquisition-rate parameter `k` across the high-fidelity region (for p values with >=20 identifiable block fits, Spearman rho approximately `-0.979`).

Thus the dense map supports the third candidate mechanism: **fidelity changes both the amount of inherited causal organization that can be stably maintained and the relative timescale over which that larger organization is assembled**. The dominant effect is the large increase in stable amplitude.

## 3. Fifty generations capture the stable regime over all six sentinels
Direct continuation of the exact same trajectories to generation 200 gave:

| p | A50 | A200 | relative difference |
|---:|---:|---:|---:|
| 0.50 | 0.02931 | 0.02959 | -0.96% |
| 0.70 | 0.06114 | 0.06215 | -1.62% |
| 0.80 | 0.09395 | 0.09429 | -0.36% |
| 0.90 | 0.13720 | 0.13808 | -0.64% |
| 0.95 | 0.15934 | 0.16031 | -0.60% |
| 1.00 | 0.17952 | 0.17971 | -0.10% |

All six passed the frozen descriptive closeness criterion. Therefore generation 50 is sufficient to estimate the stable fidelity-response surface across the tested sentinel range; the 200-generation runs remain useful as maintenance controls.

## 4. Relational causal value and selected-neutral fitness differentiation emerge almost together in this control
Across the dense mean surface, `DeltaV_rel` and `DeltaF` are nearly identical (`r ~=0.99999`). Their empirical relative onset times are also closely matched across the fidelity grid. This minimal lattice therefore does **not** provide evidence that relational causal organization systematically precedes measurable fitness differentiation. That question remains model-dependent and should not be generalized from this control.

## 5. Higher-order signatures emerge rapidly but with different temporal shapes
At `p=0.95`:

### Scaffold-specific history
The matching-history advantage is already clear by generation 5, peaks near generation 10 (`~0.024`), then relaxes to a smaller stable value near `0.010` by generation 40–50. This transient peak would be invisible in an endpoint-only analysis.

### Acquisition-expression separation
The frozen-signature contrast rises from zero to about `0.053` by generation 5, `0.082` by generation 10, and plateaus around `0.105` by generations 30–50.

### Equal-distance anisotropy
The anisotropy contrast rises even more rapidly in absolute magnitude: about `0.080` by generation 5, `0.126` by generation 10, and `~0.156` by generations 30–50.

Thus the higher-order properties do not all share identical temporal profiles. History specificity is strongest transiently, whereas acquisition-expression separation and anisotropy rise toward stable plateaus.

## 6. Structural organization covaries strongly with the causal surface
At generation 50 across fidelity, larger `DeltaV_rel` is associated with greater selected-neutral task projection, stronger nearest-neighbor order, lower heterozygosity, and a systematic scaffold projection. These structural correlations are descriptive because fidelity simultaneously drives all of them, but the archived full populations allow more targeted causal or decomposition analyses without rerunning evolution.

## Interpretation
The dense mapping resolves the previously ambiguous word “threshold.” In this abstract realization, the data are better described as a **smooth fidelity-dependent increase in stable storage/causal capacity** than as an abrupt critical fidelity. Reliable heredity supports progressively larger stable inherited organization, while very high fidelity also slows relative convergence to the larger plateau. Fifty generations capture the stable regime for all tested sentinels, and every-generation logging reveals transient history-specificity dynamics that endpoint assays miss.

The result does not establish a universal critical fidelity or phase transition. It provides a mechanistic map of an already-confirmed abstract control.
