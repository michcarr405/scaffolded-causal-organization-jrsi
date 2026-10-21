# Recovery integration report - RC3.1

## Finding

The historical reproducibility gap is resolved at the provenance level. The original production archives for the catalytic 22-point scaffold-strength campaign, catalytic 18-point fidelity campaign, catalytic reciprocal-history campaign, original prospective lattice control, and Model B independent dense 22-point scaffold-strength campaign have been recovered.

Internal archive manifests were independently checked after extraction:

| Campaign | Verified entries | Missing | Mismatches |
|---|---:|---:|---:|
| Catalytic 22-point scaffold strength | 33 | 0 | 0 |
| Catalytic 18-point fidelity, primary | 21 | 0 | 0 |
| Catalytic 18-point fidelity, independent replication | 29 | 0 | 0 |
| Original prospective lattice | 28 | 0 | 0 |
| Catalytic reciprocal history | 20 | 0 | 0 |
| Model B dense 22-point | 4689 | 0 | 0 |

The recovered Model B dense runner is principally repository-relative. Several historical planning/validation helpers retain machine-specific paths. The four other recovered primary runners use historical `/mnt/data/...` campaign roots. Those paths are packaging issues, not missing scientific provenance.

## Reporting correction

The repository and eventual Data Accessibility statement should no longer say that these five production bundles are unavailable. The correct statement is that the original archived production materials were recovered during repository reconstruction and are preserved with their original manifests; release-form copies are subjected to portability and clean-room validation separately.

## Scientific freeze

No simulation was rerun and no result was regenerated to create this recovery patch. Recovery consists of locating, verifying and preserving the original archived materials.
