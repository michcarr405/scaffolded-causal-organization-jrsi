# Scaffolded causal organization - reproducibility artifact

This repository contains the release-candidate computational artifact for the JRSI scaffolded causal organization manuscript.

## Gate status

- RC1 assembly: PASS
- RC2 provenance/package audit: PASS
- RC3 packaged validation: PASS
- RC3.1 production-bundle recovery integration: PASS
- RC4 network-enabled clean-room validation: PASS
- RC4.1 publication-figure/source-table packaging: PASS
- RC4.2 release-hygiene synchronization: PASS
- RC4.3 exact frozen figure-builder recovery: PASS
- RC4.4 portable one-command figure rebuild: PASS locally; final GitHub clean-room run pending
- RC5 manuscript/repository consistency: pending
- RC6 final lock: pending

The successful RC4 GitHub-hosted run demonstrated network dependency installation under Python 3.13, repository/manifest validation, tests, recovered-campaign release-form validation, and catalytic prospective replay under the documented portable-equivalence rule.

## Recovery correction

Five production chains previously classified as incomplete were recovered from archived project sources: Model B independent 22-point scaffold strength, catalytic 22-point scaffold strength, catalytic 18-point fidelity, catalytic reciprocal history, and the original prospective lattice control. Their historical originals are preserved under `provenance/original_campaigns/recovered/`; release-form copies normalize only non-scientific path/output plumbing.

No scientific result, estimator, seed, parameter grid, intervention, inferential unit, or frozen output was changed by the recovery.

## Publication layer

`publication/` contains manuscript-current Figures 1-5 and S1-S6 in PDF and PNG form, processed source tables, exact recovered frozen builders for Figures 2-5 and S1-S6, frozen builder-support inputs/reference PDFs, and SHA/provenance maps linking panels to canonical repository evidence. Figure 1 is the documented artwork exception with no native computational builder.

The manuscript and Supplement PDFs themselves remain external working publication documents and are intentionally not embedded in the computational repository.

## Quick validation

```bash
python scripts/validate_repository.py
python scripts/validate_manifests.py
python scripts/validate_publication_figures.py
python scripts/validate_figure_builders.py
python scripts/validate_figure_reproduction.py
python -m pytest -q
python scripts/validate_recovered_campaigns.py
```

## Recovered campaign status

The recovered production chains retain conservative reproducibility class B. RC4 established clean installation and release-form compile/dry-run validation, and the catalytic prospective assay was replayed successfully. Class A is reserved for campaigns that have also been rerun end-to-end in release form; the large recovered production campaigns were not all recomputed in full during RC4. See `docs/CAMPAIGN_STATUS_REVISED.md` and `provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.3.0.json`.

## Release boundary

Do not create the final immutable Git tag or DOI until RC5 and RC6 pass. The repository URL and MIT license are fixed; the final semantic version, immutable tag, article citation, and Zenodo DOI remain intentionally pending.
