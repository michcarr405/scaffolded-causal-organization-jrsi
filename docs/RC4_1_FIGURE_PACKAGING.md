# RC4.1 publication-figure packaging correction

**Classification:** packaging/provenance correction only; no scientific analysis, estimator, seed, parameter, intervention, inferential unit, or frozen campaign output is changed.

## Reason

RC4 passed the network-enabled clean-room gate, but a subsequent release-content audit found that the repository did not expose a coherent reader-facing package for main Figures 1--5 and supplementary Figures S1--S6. Most underlying campaign data were present, but several processed publication source tables used by S1/S2 were only retained in historical figure-freeze packages.

## Correction

RC4.1 adds:

1. all five manuscript-current main figure assets (PDF + PNG);
2. all six manuscript-current supplementary figure assets (PDF + PNG);
3. compact publication source tables, including the exact frozen S1/S2 enrichment arrays;
4. panel-level `FIGURE_PROVENANCE_MAP.csv` linking every panel to publication source data and canonical campaign evidence;
5. SHA-256 inventories for figure assets and source tables;
6. historical source maps/builders where available, explicitly marked historical;
7. a publication-figure validator added to the clean-room workflow.

The manuscript and Supplement documents remain excluded.

## Current-asset provenance

The current figure assets were vector-clipped from the compiled manuscript and Supplement used in the figure audit. This avoids substituting the superseded September 26 Figure 5/S5/S6 layouts. The later figure-freeze lineage (`JRSI_MAIN_AND_SUPPLEMENTARY_FIGURE_FREEZE_BUNDLE_v1.4.1`, including Figure 5 v1.1.1) is recorded in project archives, but its raw Library ZIP was not materializable during this assembly. The current snapshots are therefore paired directly with the frozen campaign source data in the repository.

## Gate consequence

Because the release-form repository changes, RC4.1 must rerun the same network-enabled clean-room workflow. RC5 should begin only after RC4.1 passes.
