# Publication figure layer

This directory contains the reader-facing figure assets and compact processed source tables for the JRSI scaffolded causal organization study.

## Release boundary

The manuscript and Supplement documents are intentionally not included in this computational repository. Their current publication figures are included separately here so the computational evidence can be audited without freezing an editable manuscript draft.

- `main_figures/`: Figures 1--5 as one-page vector PDF assets plus PNG previews.
- `supplementary_figures/`: Figures S1--S6 as one-page vector PDF assets plus PNG previews.
- `source_tables/`: compact frozen or campaign-derived tables directly used to support the displayed panels. Large canonical campaign outputs are not duplicated.
- `provenance/FIGURE_PROVENANCE_MAP.csv`: panel-by-panel mapping from the reader-facing figure to processed publication tables and canonical repository evidence.
- `provenance/FIGURE_ASSET_SHA256.csv`: SHA-256 hashes of all 22 reader-facing PDF/PNG figure assets.
- `provenance/SOURCE_TABLE_SHA256.csv`: SHA-256 hashes of the compact publication source tables.
- `source_maps/`: frozen panel/source maps.
- `builders/frozen_original/`: exact manuscript-current frozen figure builders recovered from the controlling figure-freeze lineage, with SHA-256 inventory.
- `builders/builder_support/`: frozen source inputs and reference PDFs used by the portable release-form rebuild.
- `builders/synchronization_records/`: audit records for the final S5/S6 reader-facing synchronization patches.
- `builders/PORTABLE_REBUILD.md`: execution and normalization policy for the one-command rebuild.
- `historical_builders/`: older implementation provenance retained separately from the controlling builders.

## Current figure authority

The PDF assets in `main_figures/` and `supplementary_figures/` are manuscript-current vector snapshots extracted from the compiled publication documents used for the September 29 figure audit. The extraction record is in `provenance/EXTRACTION_MANIFEST.json`. The manuscript and Supplement themselves remain external.

The later canonical figure-freeze lineage is documented by project archive records as `JRSI_MAIN_AND_SUPPLEMENTARY_FIGURE_FREEZE_BUNDLE_v1.4.1`, including Figure 5 v1.1.1. Those raw Library ZIP bytes were not materializable in the RC4.1 assembly runtime. No older Figure 5 was substituted: the current Figure 5, S5 and S6 assets were taken from the compiled publication documents and mapped directly to the frozen campaign data already in this repository.

`historical_builders/` remains explicitly historical. Exact current frozen builders are retained under `builders/frozen_original/`. Figure 1 remains a documented schematic/artwork exception. For S5 and S6, the recovered exact v1.2.0 builders plus synchronization audit records establish the build lineage; the portable wrapper applies only the explicitly documented notation synchronizations to temporary execution copies and verifies render identity against the synchronized frozen references.

## Validation

Run:

```bash
python scripts/validate_publication_figures.py
python scripts/validate_figure_builders.py
python scripts/validate_figure_reproduction.py
```

The publication validator checks figure presence, one-page PDF integrity, PNG integrity, asset hashes, compact source-table hashes, panel coverage, and existence of every mapped source path in the repository.
