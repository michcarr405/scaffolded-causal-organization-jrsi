# RC4.4 publication-figure rebuild validation

**Status: PASS (local release-form validation)**

Across targeted release-form validation runs, all ten computational publication figures were rebuilt from the frozen repository support inputs using the exact recovered builders plus temporary release-form path normalization where required. Figure 1 remains the documented artwork exception.

The two later reader-facing synchronization edits were applied only to temporary execution copies: S5 explicit squared scaffold-norm notation and S6 probe-angle `phi` -> `chi`.

## Render-equivalence results

| Figure | Builder SHA-256 | Mean absolute pixel difference | Changed-pixel fraction | Status |
|---|---|---:|---:|---|
| Figure_2 | `cc55aa9d468d0c4af7b506d375716fa1dd696f68c821709adc5ac50708f2315c` | 0.0 | 0.0 | PASS |
| Figure_3 | `460da96d0c478d45e9bff963dea089a9394944f65093f1b1d3a63198b7a2a2f6` | 0.0 | 0.0 | PASS |
| Figure_4 | `00f80baf66d72f44e1ce9c1cfccd3b41e6cbcad221ac82e222b738e467e14075` | 0.0 | 0.0 | PASS |
| Figure_5 | `eae9ce1ec7a4c51eabca28e540c965ce34f6f34b8420f5b16bd0693fb9d32d87` | 0.0 | 0.0 | PASS |
| Figure_S1 | `ab639892f3cb1592bb6af68caeba99d46698567cad00ece93de5ca730cf5da60` | 0.0 | 0.0 | PASS |
| Figure_S2 | `57feb78bfed10f11fbfcf0e0fe199a4784a6d872b29847ee7ca35b39d71fa8de` | 0.0 | 0.0 | PASS |
| Figure_S3 | `16ea96b6fe0602fb11a2ac4e5c2ac578121dfa27079c75dde991f7b9f9b6f126` | 0.0 | 0.0 | PASS |
| Figure_S4 | `9d894b9f090a96f681ce3f54437e1076763e8d479d3f897a59cb15ca947dc84f` | 0.0 | 0.0 | PASS |
| Figure_S5 | `56bcfe210077f6321047237f250fc6b2ec51dfe0173849b93fcf89d445addb22` | 0.0 | 0.0 | PASS |
| Figure_S6 | `1b74bf8bd5768238a719bcff5a24485d370b6e250d96e8a93171ff62bc3ed4f2` | 0.0 | 0.0 | PASS |

All ten comparisons had zero rendered-pixel difference in this validation environment.

The GitHub RC4.4 clean-room workflow runs the complete single-command release-form rebuild after dependency installation on a fresh hosted runner.
