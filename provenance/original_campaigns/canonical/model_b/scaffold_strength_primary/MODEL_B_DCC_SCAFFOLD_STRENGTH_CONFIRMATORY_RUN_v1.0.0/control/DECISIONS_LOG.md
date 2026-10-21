# Decisions Log

## DCC-STRENGTH-001 - Prospective scaffold-strength campaign freeze

- **Date:** 2026-09-05
- **Status:** FROZEN; production blocked pending validation
- **Decision type:** methodological + scope
- **Decision:** Prospectively confirm the scaffold-strength regime structure in canonical Model B using seven broad strength anchors `beta/Theta={0,1.5,2.5,3.0,3.5,4.0,4.5}`, 30 new independent repeated-measures root-seed blocks, selected-neutral pairing, `p=0.975`, `Theta=1.2`, and 250 updates.
- **Rationale:** The sweep is central to the paper but currently exploratory. Broad regime anchors test the discovered structure without claiming or retesting the exact exploratory peak. The fine-scale exploratory 3.75 point is deliberately omitted.
- **Affected analyses:** ancestral cost, zero-centered fitness recovery, training/fixed-probe C_down, training/fixed-probe historical specificity.
- **Outputs invalidated:** none; exploratory packages remain exploratory.
- **Verification required:** all items in `ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md`.
- **Supersedes:** none.

## DCC-STRENGTH-002 - Root-seed repeated-measures inferential design

- **Date:** 2026-09-05
- **Status:** FROZEN
- **Decision type:** statistical
- **Decision:** The independent inferential unit is the root-seed block. All seven strength conditions and selected/neutral modes are repeated/nested within block. Bootstrap and planned contrasts resample/operate on whole blocks.
- **Rationale:** Shared ancestors sharply isolate the effect of scaffold strength while preserving 30 independent evolutionary starting blocks. Ratio-specific propagation streams prevent accidental cross-ratio trajectory identity; selected/neutral streams remain paired within ratio.
- **Alternatives considered:** unique independent seeds at every ratio (rejected because it discards the scientifically useful blocking and makes regime contrasts noisier without adding independent block count for a fixed computational budget).
- **Supersedes:** none.

## DCC-STRENGTH-003 - Confirm broad regime structure, not exact numerical optimum

- **Date:** 2026-09-05
- **Status:** FROZEN
- **Decision type:** inferential + scope
- **Decision:** Primary inference uses prespecified low-versus-high, high-versus-collapse, and fixed-probe-versus-training contrasts. No exact peak-location estimator or continuous critical threshold is primary.
- **Rationale:** Exploratory results locate a plateau/turnover region rather than a sharply resolved optimum; prospectively chasing 3.75 would overfit discovery data.
- **Supersedes:** none.

## DCC-STRENGTH-004 - Figure panel (b) zero-centered representation

- **Date:** 2026-09-05
- **Status:** FROZEN production consequence
- **Decision type:** production/editorial linked to scientific endpoint
- **Decision:** When the scaffold-strength figure is rebuilt, panel (b) will plot `F250_selected-F0` and `F250_neutral-F0` rather than absolute generation-250 selected and neutral fitness. The formal selection effect remains `F250_selected-F250_neutral`.
- **Rationale:** This aligns panels (b)-(d) around excess/change relative to a baseline and visually shows the magnitude of neutral drift relative to selection-generated recovery.
- **Supersedes:** the current absolute-fitness panel (b) in the frozen figure package, but only at the next figure-version update.

## DCC-STRENGTH-005 - Figure-status gate

- **Date:** 2026-09-05
- **Status:** FROZEN
- **Decision type:** scope + production
- **Decision:** The scaffold-strength figure is important enough for the main manuscript regardless of confirmation outcome, but the sweep itself may be labeled primary confirmatory evidence only after the strong-support gate in `SUCCESS_CRITERIA_v1.0.0.md` passes. Until then it remains exploratory/partially confirmed evidence.
- **Supersedes:** none.

## DCC-STRENGTH-006 - Claim boundary retained

- **Date:** 2026-09-05
- **Status:** FROZEN
- **Decision type:** scope
- **Decision:** Even a successful sweep confirms only intervention-defined downward causal constraint and scaffold-history-specific organization within canonical Model B. It does not license claims of a universal optimal constraint, full Walker-Davies reversal, top-down dominance, autonomous agency, or scaffold endogenization.
- **Supersedes:** none.

## 2026-09-05 - Preproduction validator serialization repair

The first validation execution completed its scientific checks but failed while serializing the JSON report because a diagnostic dictionary used tuple keys from a pandas MultiIndex. No confirmatory production endpoint existed or was generated. The diagnostic-only detail field was converted to string keys (`ratio_id|mode`) and validation was restarted from the beginning. No scientific field, model code, seed, estimator, contrast, or success criterion changed.

## 2026-09-05 - Validation gate passed and production authorized

The restarted preproduction validation passed 40/40 automated checks. Archived exploratory selected/neutral beta=4 states replayed exactly; the canonical source blob audit passed; RNG/blocking, C_down, specificity, statistical, and manifest checks passed. Production was authorized by creating an authorized manifest that differs from the frozen manifest only in `production_authorized=false -> true`. No confirmatory outcome was inspected before authorization.

## 2026-09-05 - Postproduction analysis-report serialization repair

The first frozen analysis execution completed the endpoint table, block contrasts, formal contrast statistics, and ratio summary, then failed only when JSON-serializing a NumPy boolean in the result summary. The serializer was amended to convert NumPy scalar types to native JSON scalars. No endpoint, contrast formula, bootstrap seed/count, multiplicity rule, success criterion, or scientific result was changed. The analysis was then rerun deterministically from the complete raw outputs.

## 2026-09-05 - Scaffold-strength confirmatory result freeze

All 210 selected-neutral ratio pairs (420 evolutionary runs) completed. All four prespecified inferential families passed their frozen strong-support criteria, all five viable-window ratio-specific DeltaF means were positive, and the r=4.5 selected/neutral endpoint means both satisfied the <=0.20 canonical fitness-floor gate. A postproduction exact replay of STR_B00/R3P5 reproduced g0 and g250 arrays and endpoint JSON exactly, and a complete analysis rerun reproduced all frozen analysis file hashes exactly. Classification frozen as **STRONG PROSPECTIVE SUPPORT**.
