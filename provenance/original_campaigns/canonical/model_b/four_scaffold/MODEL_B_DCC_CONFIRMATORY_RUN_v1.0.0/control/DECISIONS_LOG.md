# Decisions Log

## DCC-CONF-001 - Minimal confirmatory campaign freeze

- **Date:** 2026-09-04
- **Status:** FROZEN; production blocked pending validation
- **Decision type:** methodological + scope
- **Decision:** Run one compact confirmatory campaign in canonical Model B that simultaneously covers: (A) new-seed selected-minus-neutral `Delta C_down`, (B) four independently seeded scaffold identities with full cross-evaluation, and (C) one unit-stratified exact-margin relational-erasure robustness estimator. Use `beta=4`, `Theta=1.2`, `p=0.975`, 250 generations, 30 independent paired seed blocks per scaffold identity, and preserve selected-neutral CRN pairing.
- **Primary endpoint:** `SCF0` generation-250 `Delta C_down_primary`.
- **Scaffold identities:** `SCF0=[2,0,3,1]`, `SCF1=[0,1,2,3]`, `SCF2=[1,3,0,2]`, `SCF3=[3,2,1,0]`.
- **Alternative erasure:** 128 unit-stratified within-model-unit motif-position shuffles, preserving each unit's motif multiset and segment occupancies; average JSD across shuffles.
- **Inference:** paired seed block; 50,000 block bootstraps; exact one-sided sign test; Holm adjustment within each four-mapping confirmatory family; 98.75% mapping-specific bootstrap intervals.
- **Rationale:** The handoff requires independent confirmation, mapping-identity generalization, and an independently constructed marginal-preserving erasure. The chosen anchor regime is a strong exploratory condition away from the later fitness-floor collapse. Four pairwise maximally distinct scaffold permutations provide a compact cross-mapping test. Thirty blocks per scaffold increase independent replication over the exploratory `n=20` without reopening a broad sweep.
- **Alternatives considered:**
  1. repeat only canonical mapping - rejected because it does not satisfy scaffold-identity generalization;
  2. all 24 scaffold identities - rejected as unnecessary for the smallest reviewer-resistant test;
  3. beta or inheritance sweep - rejected because discovery is already complete and would blur confirmatory scope;
  4. `p=1.0` - rejected as a boundary condition when `p=0.975` already gives strong exploratory signal;
  5. deterministic `P(S)P(M)` only - rejected because an independent erasure construction is explicitly required;
  6. reuse a common base seed across scaffold identities - rejected to preserve independent paired blocks for each scaffold.
- **Affected code:** future confirmatory wrapper and analysis scripts only; canonical Model B core must remain unchanged.
- **Affected analyses:** all new confirmatory A-C analyses.
- **Affected figures/tables:** future confirmatory portions of Figures 3-4 and supplementary alternative-erasure robustness; publication figures remain blocked until result freeze.
- **Affected manuscript sections:** future Methods, Results, Discussion limitations.
- **Outputs invalidated:** none; all existing exploratory packages remain unchanged and exploratory.
- **Verification required:** all items in `ESTIMATOR_VALIDATION_CHECKLIST_v1.0.0.md`.
- **Supersedes:** none.

## DCC-CONF-002 - Claim boundary retained

- **Date:** 2026-09-04
- **Status:** FROZEN
- **Decision type:** scope
- **Decision:** The confirmatory campaign may support intervention-defined downward causal constraint and historical scaffold appropriation within canonical Model B. It may not be used to claim full Walker-Davies reversal, top-down dominance, autonomous agency, or scaffold endogenization.
- **Rationale:** These stronger interpretations are not established by the proposed interventions and are explicitly prohibited by the controlling handoff.
- **Affected code:** none.
- **Affected analyses:** interpretation only.
- **Affected figures/tables:** captions and schematics must preserve external scaffold versus evolved organization distinction.
- **Affected manuscript sections:** title/abstract/results/discussion wording.
- **Outputs invalidated:** any future text that exceeds this boundary.
- **Verification required:** manuscript-scope and wording gate after result freeze.
- **Supersedes:** none.

## DCC-CONF-003 - Preproduction RNG and analysis-root clarification

- **Date:** 2026-09-04
- **Status:** FROZEN BEFORE CONFIRMATORY PRODUCTION
- **Decision type:** technical clarification; no scientific endpoint or model change
- **Decision:** Freeze project-level bootstrap analysis root seed as `145617781`, deterministically derived as the unsigned little-endian first four bytes of SHA-256(`MODEL_B_DCC_CONFIRM|v1.0.0|analysis-bootstrap`) = `75f3ad08df56392b57eb5e7722cbea2fd60cede57b671c93d33fe007de3dba05`.
- **Alternative-erasure stream clarification:** for each paired block, instantiate exactly one generator with `(base_seed, "confirmatory-unitshuffle")`; consume its permutations sequentially. Thus `K=128` is the exact first-128 common-prefix subset of a `K=2048` validation stream. Mode is excluded from the key, so selected and neutral use the same permutation stream positions.
- **Cross-evaluation stream clarification:** instantiate one generator with `(base_seed, "confirmatory-cross-eval")`, generate the complete 16-draw uniform matrix once, and reuse it for all four probe scaffolds and both selected and neutral members of the pair. Probe scaffold and mode are excluded from the key.
- **Rationale:** These choices make the already-frozen purpose-separated CRN policy executable without introducing an unspecified analysis seed and enforce the checklist requirement that the `K=128` convergence comparison use a common prefix stream.
- **Scientific fields changed:** none.
- **Outcome inspection:** no confirmatory production outcome existed or was inspected before this clarification.

## DCC-CONF-004 - Validation gate passed and production authorized

- **Date:** 2026-09-04
- **Status:** PRODUCTION AUTHORIZED
- **Decision type:** validation gate + execution authorization
- **Validation result:** `validation/VALIDATION_REPORT_v1.0.0.json` reports **PASS, 56/56 checks**; SHA-256 `9d9b9f9efdecda571a72be27db0b29e16bb16b9e75f56f08a94e09b0f0a0b325`.
- **Validated scientific pipeline:** `scripts/dcc_pipeline.py`; SHA-256 `b3a218163cd8661294b8c50b3166dc14259e64aacbaef4b74ee08dd37a6215df`.
- **Production orchestration runner:** `scripts/run_production.py`; SHA-256 `072cd83f97cb40035b69de5af20e59b368a0b300e880fed9fa3d1dd8edd8482c`.
- **Preproduction dry-run:** first attempt failed before any simulation because pandas attribute access `rr.mode` resolved the Series method rather than the manifest column. The orchestration-only check was changed to bracket column access (`rr['mode']` and analogous fields). No scientific model, estimator, seed, endpoint, or inference field changed. The second dry-run passed with exactly 240 runs and 120 paired blocks.
- **Environment lock:** `control/ENVIRONMENT_LOCK_v1.0.0.json`; SHA-256 `8239dc0a40b7e5802aa75d5cc449ab20dda320e69f31b23ec31f2a8aaf8ccce7`.
- **Authorized manifest:** `control/RUN_MANIFEST_AUTHORIZED_v1.0.0.csv`; SHA-256 `16692750ff4fa5ca3ea46a01f288deacadfbc315602358bbd6845ef0fdfac321`.
- **Authorization diff audit:** `control/AUTHORIZATION_DIFF_AUDIT_v1.0.0.json`; SHA-256 `bad965675d2e4ba01f713736aa285c6be7ab63e42ad708b3173bb3bde7608329`; only `production_authorized` differs from the frozen manifest.
- **Confirmatory-output state at authorization:** 0 state files, 0 metric files, 0 paired endpoint files, 0 run endpoint files. No confirmatory outcome existed or was inspected before authorization.
- **Exact production command:** `PYTHONPATH=/mnt/data/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0/source:/mnt/data/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0/scripts python /mnt/data/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0/scripts/run_production.py --workers 8`
- **Decision:** production is authorized under the frozen v1.0.0 design. No outcome-dependent changes are permitted.

## DCC-CONF-005 - Confirmatory outcome freeze

- **Date:** 2026-09-04
- **Status:** RESULT FROZEN
- **Decision type:** confirmatory outcome classification + result freeze
- **Preproduction validation:** PASS, 56/56 checks.
- **Production completeness:** PASS, 120/120 paired blocks and 240/240 evolutionary runs; 240 state files, 240 checkpoint-metric files, 240 run endpoints, 120 paired endpoints; no missing outputs.
- **Analysis integrity:** PASS. All 120 paired identities, seeds, selected-neutral ancestors, endpoint differences, historical-match formulas, generation-250 endpoint/checkpoint consistency, and 2,640 checkpoint rows were audited.
- **Analysis reproducibility:** PASS. Frozen analysis outputs were byte-identical on an immediate deterministic rerun under analysis root seed `145617781`.
- **A-core:** PASS. For canonical `SCF0`, mean generation-250 selected-minus-neutral `Delta C_down = 0.004679253925461036` bits; 95% bootstrap CI `[0.004256931888971438, 0.005116293267841216]`; 30/30 positive blocks; one-sided exact sign p `9.313225746154785e-10`.
- **B1-strong:** PASS. All four scaffold identities passed the frozen primary `Delta C_down` mapping-specific criteria.
- **B2-strong:** PASS. All four scaffold identities passed the frozen historical-match `Delta H` criteria.
- **C-strong:** PASS. All four scaffold identities passed the frozen alternative unit-stratified exact-margin erasure criteria.
- **Pooled primary `Delta C_down`:** equal-weight stratified mean `0.0041886448856250395` bits; 95% CI `[0.003961266544366771, 0.004420395801052028]`.
- **Pooled historical-match `Delta H`:** equal-weight stratified mean `11.909226453993057`; 95% CI `[11.55406436021593, 12.273177587890626]`.
- **Pooled alternative-erasure `Delta C_down`:** equal-weight stratified mean `0.0041906337296363436` bits; 95% CI `[0.003962781822410759, 0.004419772195990226]`.
- **Frozen classification:** `STRONG_PROSPECTIVE_SUPPORT` under the preregistered v1.0.0 decision rules.
- **Permitted central claim:** Within the tested canonical Model B regime, selection prospectively and reproducibly generated scaffold-history-specific inherited organization whose preservation changed lower-level chemical-state distributions; the effect generalized across four prespecified scaffold identities and survived an independently constructed marginal-preserving relational erasure.
- **Claim boundary retained:** this does not establish full Walker-Davies information-flow reversal, top-down dominance, autonomous agency, or scaffold endogenization. The scaffold remains externally specified.
- **Outcome-dependent protocol changes:** none.
- **Post-freeze rule:** any later exploratory analyses, additional parameter values, new scaffold sets, or new interventions must be labeled secondary/exploratory and may not alter this frozen confirmatory classification.
