# Scaffolded causal organization - computational reproducibility artifact

This repository contains the published computational reproducibility artifact for the manuscript **Scaffolded emergence of inherited causal organization in pre-genetic systems**, submitted to the *Journal of the Royal Society Interface*. The artifact contains three model realizations, frozen computational outputs, provenance records, publication figures and validation scripts. The manuscript and Supplementary Material remain separate submission documents and are not embedded in this repository.

## Archived release and citation

- **Archived version:** [v1.0.1 on GitHub](https://github.com/michcarr405/scaffolded-causal-organization-jrsi/releases/tag/v1.0.1), an archival-only release of the scientifically identical [v1.0.0](https://github.com/michcarr405/scaffolded-causal-organization-jrsi/releases/tag/v1.0.0).
- **Version-specific Zenodo DOI:** [10.5281/zenodo.23628232](https://doi.org/10.5281/zenodo.23628232).
- **Validated scientific commit (both tags):** `3c9baf42177287fc792ec4d7b55c575024fbef00`.
- **Clean-room evidence:** [GitHub Actions run 40138073620](https://github.com/michcarr405/scaffolded-causal-organization-jrsi/actions/runs/40138073620) — successful at that exact commit.
- **License:** MIT.

For citations to the archived software/data artifact, cite the Zenodo v1.0.1 record. The journal article's final bibliographic details will be supplied when available. This ongoing repository branch may contain subsequent documentation updates; the immutable versioned Git tags and Zenodo record preserve the exact scientifically validated release.

## Reproducibility status

**RC6 clean-room validation: PASS (24 October 2026).** A fresh GitHub-hosted Ubuntu/Python 3.13 environment installed the pinned dependencies, exported a Git-free candidate, validated repository structure, the SHA-256 manifest, published assets and builders, ran tests, rebuilt computational publication figures, validated recovered campaign packages in release form and replayed the original catalytic prospective assay.

**Five recovered original production campaigns remain Class B**, not Class A. Original production provenance was recovered and documented, and portability/release-form checks passed; the complete large-scale production runs were not all independently recomputed end-to-end. Historical original scripts may contain machine-specific paths; portable release copies normalize only non-scientific path/output plumbing. No scientific kernel, model parameter, seed, grid, inferential unit or frozen result was altered by that recovery. See `docs/CAMPAIGN_STATUS_REVISED.md` and `provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.3.0.json`.

The models do **not** establish scaffold endogenization, autonomous scaffold reconstruction or a physically complete protocell.

## Repository contents

- `publication/` — Figures 1–5 and S1–S6 in publication forms, supporting source tables, hashes and provenance maps. Recovered frozen computational builders reproduce Figures 2–5 and S1–S6; Figure 1 is the documented native-artwork exception.
- `provenance/` — archived original and recovered campaign sources, configurations, root-seed records, evidence inventories and campaign-specific status.
- `scripts/` — package, manifest, publication-asset, figure-builder, figure-reproduction and recovered-campaign validation.
- `manifests/SHA256_MANIFEST.csv` — checksum inventory for the frozen v1.0.1 artifact, validated at the tagged commit.
- `docs/` — gate closure, parameter/campaign crosswalks, audit and reproducibility documentation.

## Quick validation

Install the pinned dependencies in `requirements.txt` in a clean Python environment before running these repository-root commands:

```bash
python scripts/validate_repository.py
python scripts/validate_manifests.py
python scripts/validate_publication_figures.py
python scripts/validate_figure_builders.py
python scripts/validate_figure_reproduction.py
python -m pytest -q
python scripts/validate_recovered_campaigns.py
```

The GitHub Actions clean-room workflow is `.github/workflows/rc4-clean-room-v2.yml`. The workflow name reflects its original development gate; its successful RC6 dispatch is linked above.

## Historical validation record

- **RC1–RC3.1:** package assembly, provenance checks, initial package validation and recovery integration — PASS.
- **RC4–RC4.4:** network-enabled clean-room checks and portable figure reproduction — PASS, including [run 40089509454](https://github.com/michcarr405/scaffolded-causal-organization-jrsi/actions/runs/40089509454).
- **RC5:** Figure 3(c) release asset correction, manuscript/repository consistency, numerical traceability, 14-entry Table S2 configuration crosswalk and visual QA — PASS; see `docs/RC5_GATE_CLOSURE_2026-10-24.md`.
- **RC6:** final validated artifact, checksum lock, full clean-room workflow and public GitHub/Zenodo archiving — PASS. Scientific tag target `3c9baf42177287fc792ec4d7b55c575024fbef00`.

Documentation changes after the release do not alter the immutable scientific artifact or its DOI.
