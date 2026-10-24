# Draft GitHub release notes — version pending

**DRAFT ONLY — NOT A GITHUB RELEASE OR IMMUTABLE TAG**

Target commit (RC6 validated):
`3c9baf42177287fc792ec4d7b55c575024fbef00`

Clean-room validation evidence:
https://github.com/michcarr405/scaffolded-causal-organization-jrsi/actions/runs/40138073620

## Scaffolded causal organization — JRSI computational reproducibility artifact

This release candidate packages executable model implementations, original campaign provenance, frozen analysis assets, and publication figure source material supporting the Journal of the Royal Society Interface manuscript on the scaffolded emergence of inherited causal organization in pre-genetic systems.

### Included
- Model B, catalytic and lattice computational evidence and archived source campaigns.
- Frozen computational publication Figures 2–5 and S1–S6 with reproducible figure builders; Figure 1 is documented frozen artwork without a computational builder.
- Source tables, SHA-256 inventories, campaign controls, seed ledgers, intervention and bootstrap evidence, reproducibility crosswalks and audit documents.
- Table S2 configuration/source crosswalk covering 14 entries and 13 distinct executable entrypoints.
- Python dependencies pinned in `requirements.txt` and reproducibility validation scripts.

### Verified validation
At the exact target commit, GitHub Actions clean-room run `40138073620` completed successfully on GitHub-hosted Ubuntu/Python 3.13, including dependency installation, Git-free package export, repository/manifests/publication asset checks, Python tests, publication figure rebuilds, recovered-campaign release-form validation, and a replay of the original catalytic prospective assay.

### Important limits
**Five recovered original production campaigns remain Class B**, not Class A: original production provenance is complete and release-form portability/installation checks pass, but full end-to-end replay of every large production campaign was not completed. Historical source scripts may retain machine-specific paths; release-form adaptations do not modify scientific kernels, parameters, grids, inferential units or frozen result records. Frozen design files may still carry initial production-authorization false flags; later authorized run manifests document subsequent execution.

### Scope and citation
This artifact does not assert that the computational models reconstruct a fully autonomous protocell or that the external scaffold has been endogenized.

License: MIT.

Journal article bibliographic reference: **pending publication metadata**.
Archived release DOI: **pending issuance**.
Final semantic version and Git tag: **pending explicit selection**.

## Publication checklist
- [ ] Confirm the final semantic version and immutable tag.
- [ ] Confirm exact release commit remains `3c9baf42177287fc792ec4d7b55c575024fbef00`, or rerun clean-room validation after any release-source modification.
- [ ] Confirm release confidentiality/secret scan and repository visibility.
- [ ] Create annotated Git tag and GitHub release, with this disclosure.
- [ ] Archive exact tagged version, obtain DOI, and then synchronize manuscript Data Accessibility/citation text.
