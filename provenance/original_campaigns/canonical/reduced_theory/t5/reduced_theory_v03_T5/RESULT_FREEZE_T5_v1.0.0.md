# T5 Result Freeze v1.0.0 — Equal-Distance Anisotropy

## Status
Prospective result freeze. The T5 prospective plan, execution specification, angular predictions, and probe scaffold matrices were SHA256-frozen before any T5 evolutionary or cross-evaluation outcomes were generated.

## Primary tests
- Directional-profile correlation: r = 0.9879112; exact permutation p = 0.0002480. PASS.
- Prespecified P13 > P09 contrast: 30/30 independent root blocks; one-sided exact sign p = 9.313e-10. PASS.
- Equal-distance anisotropy: within-block direction-label permutation p = 1.99996e-5. PASS.

## Secondary
Frozen T4-derived affine absolute prediction across eight direction means:
- R2 = 0.949615
- RMSE = 0.506206 fitness units.

The predicted weakest direction P09 was observed to be weakest. The predicted strongest P13 was observed second-highest; P01 was observed highest. The full angular profile remained strongly predicted.

## Interpretation
Historical-match loss is not a scalar function of Euclidean scaffold distance. At identical displacement magnitude, direction matters reproducibly. The anisotropy is predicted by the contraction of evolved adjacent motif-context organization with the motif-dependent chemical kernel and fixed pairwise fitness map.
