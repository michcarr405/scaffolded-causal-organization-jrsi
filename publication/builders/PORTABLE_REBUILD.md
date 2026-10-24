# Portable publication-figure rebuild

The exact frozen builders under `frozen_original/` are provenance objects and are never edited in place.

Run the complete release-form rebuild with:

```bash
python scripts/build_publication_figures.py
```

The command rebuilds Figures 2--5 and Supplementary Figures S1--S6, copies the frozen Figure 1 artwork reference, and writes outputs under `work/publication_rebuild/` together with a JSON/CSV reproduction report.

## Release normalization

Some historical frozen builders contain machine-specific `/mnt/data` paths. The orchestrator verifies the exact builder SHA-256, creates a temporary execution copy, and changes only path plumbing needed to point at the staged repository support data. The frozen source file remains byte-for-byte unchanged.

The historical shared S1 builder originally continued into other obsolete supplementary builds and archive packaging. The release adapter stops immediately after the S1 figure render; the S1 plotting code is unmodified. The S5 builder likewise continues into provenance-copying and ZIP packaging after its publication figure has already been written; the temporary release execution copy stops after the figure render, leaving the plotting logic unchanged.

## S5/S6 reader-facing synchronization

The exact S5 v1.2.0 and S6 v1.2.0 builders were recovered and SHA-verified. Their later synchronization patch packages preserved the final outputs and audit records but not the tiny patch scripts. The release orchestrator therefore applies the two explicitly documented reader-facing changes to temporary execution copies:

- S5: `d^2=1` -> explicit squared scaffold norm `||B_P-B_H||^2=1`.
- S6: reader-facing probe angle `phi` -> `chi` in the equal-distance anisotropy label.

No source data, inference, geometry, estimator, or scientific value is changed. Render equivalence is checked against the synchronized frozen reference PDFs.

## Validation

`builder_support/BUILDER_SUPPORT_SHA256.csv` freezes every support input and reference PDF used by the portable rebuild. The rebuild report records builder hashes, execution normalization notes, output hashes, and rendered-pixel comparison metrics.

A clean validation run is:

```bash
python scripts/validate_figure_builders.py
python scripts/validate_figure_reproduction.py
```

Figure 1 is the sole documented exception: its freeze supplied a reader-facing artwork asset but no native computational builder.
