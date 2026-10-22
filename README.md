# Scaffolded causal organization - reproducibility artifact

This repository contains the release-candidate computational artifact for the JRSI scaffolded causal organization manuscript.

## Gate status

- RC1 assembly: PASS
- RC2 provenance/package audit: PASS
- RC3 packaged validation: PASS
- RC3.1 production-bundle recovery integration: PASS
- RC4 network-enabled clean-room validation: **PASS**
- RC4.1 publication-figure/source-table packaging: prepared; binary package application pending
- RC4.2 release-hygiene synchronization: in progress
- RC5 manuscript/repository consistency: pending final repository candidate
- RC6 final lock: pending

The successful RC4 GitHub-hosted run demonstrated network dependency installation under Python 3.13, repository/manifest validation, tests, recovered-campaign release-form validation, and catalytic prospective replay under the documented portable-equivalence rule.

## Recovery correction

Five production chains previously classified as incomplete were recovered from archived project sources: Model B independent 22-point scaffold strength, catalytic 22-point scaffold strength, catalytic 18-point fidelity, catalytic reciprocal history, and the original prospective lattice control. Their historical originals are preserved under `provenance/original_campaigns/recovered/`; release-form copies normalize only non-scientific path/output plumbing.

No scientific result, estimator, seed, parameter grid, intervention, inferential unit, or frozen output was changed by the recovery.

## Quick validation

```bash
python scripts/validate_repository.py
python scripts/validate_manifests.py
python -m pytest -q
python scripts/validate_recovered_campaigns.py
```

After the RC4.1 publication layer is applied, validation also includes:

```bash
python scripts/validate_publication_figures.py
```

## Recovered campaign status

The recovered production chains retain conservative reproducibility class **B**. RC4 established clean installation and release-form compile/dry-run validation, and the catalytic prospective assay was replayed successfully. Class A is reserved for campaigns that have also been rerun end-to-end in release form; the large recovered production campaigns were not all recomputed in full during RC4. See `docs/CAMPAIGN_STATUS_REVISED.md` and `provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.3.0.json`.

## Manuscript exclusion policy

The manuscript and Supplement are intentionally not embedded in the computational repository. They remain external publication documents. Publication figures, processed source tables, builders/source maps, and computational provenance are packaged separately in the repository, and RC5 will audit the final manuscript and Supplement against this artifact.

## Release boundary

Do not create the final immutable Git tag or DOI until RC5 and RC6 pass. The repository URL and MIT license are now fixed; the final semantic version, immutable tag, article citation, and Zenodo DOI remain intentionally pending.
