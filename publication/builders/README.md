# Publication figure builders

This directory preserves the exact frozen Python builders recovered from the manuscript-current figure-freeze lineage.

## Scope

- Figure 1 is a schematic/artwork figure and its freeze explicitly records that no native computational builder was supplied. The frozen reader-facing PDF/PNG remains the controlling Figure 1 asset.
- Figures 2--5 have manuscript-current frozen builders.
- Supplementary Figures S1--S6 have frozen builders. The exact S2 and S5 builders were recovered from a deleted v1.2.1 supplementary freeze and verified against the SHA-256 values recorded in their original manifests. The exact S6 builder was likewise recovered and hash-verified.
- S5 and S6 received later reader-facing synchronization patches. The original patch packages contain the synchronized outputs and audit records but do not contain the small patch scripts. Their README/audit records are preserved under `synchronization_records/`. The frozen synchronized PDF/PNG assets under `publication/supplementary_figures/` remain controlling for those final reader-facing changes.

`FIGURE_BUILDER_INVENTORY.csv` records the SHA-256 of every preserved builder.

The frozen original scripts are retained byte-for-byte and may contain historical absolute paths. Release-form path normalization must not overwrite these provenance copies.

## Portable release build

`builder_support/` and `scripts/build_publication_figures.py` provide a single-command release-form rebuild without modifying the frozen originals. See `PORTABLE_REBUILD.md`.
