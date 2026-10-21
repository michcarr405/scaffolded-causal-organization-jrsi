# Reduced Theory Prospective Tests T3-T4 - Result Freeze v1.0.0

Status: FROZEN RESULTS.

## T3 - finite-amplitude retrieval-peak law

The T3 plan and execution specification were frozen and hashed before outcome generation. Five previously unused training strengths were evolved with 30 entirely new selected-neutral root-seed pairs per strength (150 pairs; 300 evolutionary runs). Generation-250 populations were frozen before assay.

Primary result: **PASS**. The observed block-mean retrieval peak fell within one 0.125 probe-grid interval of the frozen v0.2 prediction for **5/5** training strengths (required >=4/5).

Predicted versus observed peaks:
- training 1.75: predicted 0.7658, observed 0.750, error -0.0158.
- training 2.00: predicted 0.8446, observed 0.750, error -0.0946.
- training 2.75: predicted 1.0810, observed 1.000, error -0.0810.
- training 3.25: predicted 1.2387, observed 1.125, error -0.1137.
- training 3.75: predicted 1.3963, observed 1.375, error -0.0213.

Signed peak error showed no monotonic trend by the predeclared operational test (Spearman rho=-0.300, two-sided p=0.624).

The full frozen finite-amplitude curve, with **no parameter refitting**, achieved pooled R2=0.9663 and RMSE=0.00048753 bits across 125 primary grid points.

Interpretation: the post-T1 v0.2 prediction that the probe strength maximizing expression shifts systematically with the magnitude of organization acquired during evolution received strong prospective support.

## T4 - finite-distance historical-match law

The T4 design was frozen before evolutionary outcomes. Thirty entirely new selected-neutral root-seed pairs evolved under the canonical historical scaffold. Frozen endpoint populations were probed under 28 continuous equal-strength scaffold variants: four orientations at each total squared distance 16, 32, 48, 64, 80, 112, and 144. The construction preserved per-segment scaffold norm exactly and reproduced the historical categorical kernel to numerical precision.

Primary zero-parameter v0.2 result: **NOT SUPPORTED**. The frozen saturating scalar-distance law gave class-mean R2=-0.5756, RMSE=0.4704; the local d/64 law was worse (R2=-1.3114, RMSE=0.5697) but neither described the new continuous-scaffold data adequately.

Observed normalized mean response:
- d=112: 1.0216.
- d=144: 0.9695.
- d=16: 0.0081.
- d=32: 0.3790.
- d=48: 0.7648.
- d=64: 1.0000.
- d=80: 1.0822.

Observed raw DeltaH means were:
- d=16: 0.1710.
- d=32: 5.1139.
- d=48: 10.2313.
- d=64: 13.3415.
- d=80: 14.4234.
- d=112: 13.6060.
- d=144: 12.9118.

The response rose from near zero at d=16, reached its maximum near d=80, and then declined at d=112 and d=144. Orientation-level effects were substantial at small and intermediate distances. Thus raw Euclidean scaffold distance is not a sufficient state variable for historical mismatch outside the restricted categorical-permutation family used in T2.

## Combined inference

T3 strengthens the acquisition-storage-retrieval part of Reduced Theory v0.2: training history quantitatively predicts the physical context in which frozen inherited organization is maximally expressed.

T4 falsifies the proposed one-dimensional finite-distance extension. The earlier T2 monotonic distance result is real within the categorical permutation family, but it does not generalize to arbitrary equal-strength directions in scaffold-logit space. The next theory should therefore be anisotropic/state-dependent rather than a scalar function of Euclidean scaffold distance. A natural local form is DeltaH approximately delta_b^T G(x*, chemistry) delta_b, where G is an effective metric induced by the chemical kernel and evolved organization.

No v0.2 parameters were refit for these prospective scores.
