# Scaffolded causal organization - reproducibility artifact RC4 candidate

This is the corrected **RC4 candidate v0.1.3** for the JRSI scaffolded causal organization manuscript. It incorporates the original production bundles recovered after the initial reproducibility audit and is intended to be the exact candidate tested by the final network-enabled RC4 clean-installation workflow.

## Recovery correction

Five production chains previously classified as incomplete were subsequently recovered from archived project sources: Model B independent 22-point scaffold strength, catalytic 22-point scaffold strength, catalytic 18-point fidelity, catalytic reciprocal history, and the original prospective lattice control. Their historical originals are preserved byte-for-byte under `provenance/original_campaigns/recovered/`; public copies normalize only machine-specific path/output plumbing.

No scientific result, estimator, seed, parameter grid, intervention, inferential unit, or frozen output is changed by RC3.1.

## Current gate status

- RC1 assembly: PASS
- RC2 provenance/package audit: PASS for the pre-recovery candidate
- RC3 packaged validation: PASS for the pre-recovery candidate
- RC3.1 recovery integration: PASS
- RC4 network-enabled clean installation: **pending GitHub Actions run on this exact candidate**

The supplied GitHub Actions workflow `.github/workflows/rc4-clean-room.yml` is designed to close the remaining networked installation subcheck on a fresh GitHub-hosted Linux runner.

## Quick validation

```bash
python scripts/validate_repository.py
python scripts/validate_manifests.py
python -m pytest -q
python scripts/validate_recovered_campaigns.py
```

## Recovered campaign status

All five formerly missing production chains now have complete historical provenance and are classified **B** pending release-form portability/clean-room validation. See `docs/CAMPAIGN_STATUS_REVISED.md` and `provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.2.0.json`.

## Release boundary

Do not create a final immutable Git tag or DOI until RC4, RC5 and RC6 pass. The `LICENSE` remains an explicit placeholder until the author selects the public license.

## Manuscript exclusion policy

The manuscript and Supplement are intentionally **not included** in this computational repository. They remain separate working publication documents and may receive editorial polishing before submission. RC5 will compare the final manuscript externally against this frozen computational artifact. Publication figures and their source-faithful build materials remain in the repository because they are computational outputs of the analyses.
