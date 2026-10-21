# Scaffold-Strength Confirmatory Result Freeze v1.0.0

**Project:** Evolutionary appropriation of physical regularity generates downward causal constraint in a pre-genetic model  
**Campaign:** prospective scaffold-strength regime confirmation  
**Frozen decision:** **STRONG PROSPECTIVE SUPPORT**

## What was prospectively tested

Thirty new independent root-seed blocks were each evaluated at seven prespecified scaffold strengths (`beta/Theta = 0, 1.5, 2.5, 3.0, 3.5, 4.0, 4.5`), with paired selected and neutral evolution at every strength (420 evolutionary runs total). The root-seed block is the inferential unit.

The frozen families tested: (A) ancestral physical cost, (F) selection-dependent fitness recovery, (C) downward-causal-constraint regime structure, and (R) historical-specificity regime structure. The confirmatory fixed moderate probe was beta=3.0 and historical specificity used 16 CRN native/reversed draws.

## Frozen result

All 12 prespecified contrasts passed their familywise criteria. Every formal contrast had 30/30 positive block values. Holm-adjusted exact one-sided sign-test p-values were `1.86e-9` for the two-test A and F families and `3.73e-9` for the four-test C and R families. The r=4.5 endpoint satisfied the prespecified canonical fitness-floor criterion: selected and neutral mean fitness were both exactly 0.100000.

Key endpoint means show the regime clearly. Selected-minus-neutral fitness recovery rose from 3.755 at beta/Theta=1.5 to 11.304 at 3.0, remained 10.376 at 3.5, fell to 4.219 at 4.0, and was 0 at 4.5. Training-strength Delta C_down rose from 0.001226 bits at 1.5 to 0.004707 bits at 4.0 and collapsed to approximately 0 at 4.5. Under the standardized beta=3 probe, Delta C_down at training ratio 4.0 was 0.008280 bits versus 0.004707 bits under the training field, confirming latent-versus-expressed separation. Historical specificity showed the same structure: Delta R at ratio 4.0 was 4.215 under the training field but 21.485 under the standardized beta=3 probe, then fell to 0.034 at ratio 4.5 under the fixed probe.

## Validation and reproducibility

Preproduction validation passed 40/40 automated checks before any new confirmatory production outcome existed. The only pre-gate issue was diagnostic JSON serialization; it generated no production outcome and changed no scientific field. Archived exploratory beta=4 selected/neutral states replayed exactly. After production, STR_B00/R3P5 was rerun and reproduced g0/g250 state arrays and endpoint JSON exactly. Re-running the full frozen analysis reproduced all analysis file hashes exactly.

## Interpretation boundary

This campaign prospectively supports promotion of the scaffold-strength regime from exploratory evidence to **primary confirmatory evidence within the tested canonical Model B domain**. It supports progressive ancestral physical cost, selection-dependent adaptive recovery, increasing downward causal constraint and historical scaffold specificity before the viability boundary, latent organization masked by very strong training fields, and collapse of these selection-dependent effects at the canonical fitness floor.

It does **not** establish full Walker-Davies information-flow reversal, scaffold endogenization, top-down dominance, autonomous agency, or a universal optimum. The scaffold remains externally supplied and the fitness-floor boundary is a property of the tested canonical model regime.

## Primary files

- `analysis/CONFIRMATORY_RESULTS_v1.0.0.md`
- `analysis/GATE_DECISION_v1.0.0.md`
- `analysis/FORMAL_CONTRAST_RESULTS_v1.0.0.csv`
- `analysis/RATIO_SUMMARY_v1.0.0.csv`
- `analysis/BLOCK_CONTRASTS_v1.0.0.csv`
- `analysis/PAIRED_RATIO_ENDPOINTS_v1.0.0.csv`
- `validation/VALIDATION_REPORT_v1.0.0.md`
- `validation/PRODUCTION_REPLAY_AUDIT_v1.0.0.json`
- `validation/ANALYSIS_REPRODUCIBILITY_AUDIT_v1.0.0.json`
- `control/CONFIRMATORY_PLAN_v1.0.0.md`
- `control/RUN_MANIFEST_FROZEN_v1.0.0.csv`
- `control/RUN_MANIFEST_AUTHORIZED_v1.0.0.csv`
