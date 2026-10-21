# Analysis and provenance audit v1.0.0

## Audit conclusion
**PASS for promotion to a frozen post-confirmatory mechanistic mapping result**, with one limited provenance qualification concerning independent reconstruction of discovery-seed disjointness from the surviving discovery CSV snapshot.

## 1. Pre-outcome scientific freeze
The original `control/PREOUTCOME_HASHES.txt` verifies exactly against the current source campaign for:

- `MECHANISTIC_MAPPING_PLAN_v1.0.0.md`;
- `CONFIG_v1.0.0.json`;
- `SEED_LEDGER.csv`;
- `scripts/run_mapping.py`;
- `scripts/decode_states.py`.

Unlike the earlier abstract-lattice confirmatory campaign, the exact production implementation itself was included in the pre-outcome SHA256 set.

## 2. Campaign validation
The archived validation report passes all listed integrity checks:

- pre-outcome hashes verify;
- expected dense row count;
- 30 root blocks;
- 41 fidelity values per block;
- 51 generations per block/fidelity;
- expected site-mean rows;
- expected sentinel continuation rows;
- expected history/expression/anisotropy probe rows;
- exactly 30 state archives;
- finite primary surface;
- all six sentinel closeness checks;
- state shapes correct;
- state decoder returns binary arrays of the expected shape.

## 3. Seed independence
The mapping seed ledger contains 2,670 unique founder/selected/neutral RNG seeds. Comparison with the prior confirmatory seed ledger gives **zero seed overlap**. Mapping founder seeds are `12000000..12000029`; confirmatory founder seeds are `9000000..9000029`.

The frozen mapping plan explicitly states that the 30 mapping blocks are disjoint from both discovery and confirmation. The surviving discovery archive contains result CSVs but no seed ledger or executable provenance, so disjointness from discovery cannot be independently recomputed from those CSVs alone. This does not affect the exact zero-overlap verification against the prior confirmatory campaign, but the distinction is recorded rather than silently overstated.

## 4. Claim-to-plan audit

### M1 fidelity-response geometry
**Status:** analysis family prespecified; exact observed outcome mapped post-confirmation.

The plan prespecified three candidate shape models (logistic, continuous segmented linear, hard two-plateau step), AICc comparison, and block bootstrap model-winning frequency. Therefore the statement that the smooth logistic outperformed the two prespecified alternatives is within the frozen analysis plan.

The later observed-range `p10/p50/p90` landmarks are not the preregistered asymptotic logistic landmarks; they were added as assumption-light descriptive summaries after the fitted logistic midpoint hit the physical boundary. They remain post-outcome descriptive quantities.

### M2 amplitude/rate decomposition
**Status:** analysis family prespecified; rate-amplitude tradeoff is a mapped outcome.

The plan prespecified empirical `A50`, `t10/t50/t90`, and a descriptive exponential acquisition model. The specific finding that high fidelity increases stable amplitude while slowing relative convergence to the larger plateau is therefore a frozen mapping result, not a previously confirmed prediction.

### M3 generation-50 sentinel stability
**Status:** criterion prespecified.

The sentinel fidelities, `A50`, `A200`, and closeness criteria were frozen before outcomes. All six pass exactly as specified.

### M4 `DeltaV_rel` versus `DeltaF`
**Status:** comparison prespecified; near-identity is mapped outcome.

The plan prespecified the same onset summaries for `DeltaF` and comparison with `DeltaV_rel`. The near-perfect block-mean surface correlation is a legitimate frozen mechanistic finding, but was not a prior qualitative prediction.

### M5 higher-order temporal signatures
**Status:** probe schedule prespecified; exact temporal shapes are mapped outcomes.

History cross-evaluation, expression probes, anisotropy probes, and probe generations were all fixed before outcomes. The exact transient versus plateau shapes were learned from the mapping data and are therefore frozen descriptive-mechanistic outcomes, not independent new confirmation tests.

### Structural correlations
**Status:** secondary descriptive.

The component diagnostics were prespecified for collection, but the particular cross-fidelity correlational interpretation was not an independent causal test. These correlations cannot rescue or redefine any primary mechanistic finding.

## 5. Evidentiary separation from the original confirmation
The source plan states explicitly that this campaign “does not replace or alter the frozen `ABSTRACT_LATTICE_CONFIRMATORY_v1.0.0` record.” This freeze preserves that boundary.

The older campaign remains the canonical prospective confirmation of existence. The mapping campaign controls the higher-resolution estimates of fidelity-response geometry and temporal dynamics.

## 6. Freeze boundary
No result derived after this freeze may be retroactively inserted into v1.0.0. The complete inherited-state archive is intentionally retained so later analyses can be performed without rerunning evolution, but such analyses must receive a new version and an explicit post-freeze evidentiary label.
