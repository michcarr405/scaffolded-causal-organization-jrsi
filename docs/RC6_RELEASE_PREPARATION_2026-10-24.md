# RC6 release preparation checklist

Status: **PREPARED — NOT RELEASED** (2026-10-24)

## Established
- RC5 gate PASS: `docs/RC5_GATE_CLOSURE_2026-10-24.md`.
- Complete 14-entry Table S2 executable crosswalk: `docs/RC5_S2_EXECUTABLE_CONFIGURATION_CROSSWALK.json`.
- Portable figure rebuild PASS for Figures 2–5 and S1–S6; Figure 1 frozen artwork exception.
- RC4 network-enabled clean-room workflow passed under Ubuntu/Python 3.13.
- Five recovered production chains remain **Class B**; no assertion of complete end-to-end production replay.

## Required before immutable release
1. Confirm clean working tree and current release branch HEAD.
2. Run complete validation suite on finalized release commit (manifests, test suite, recovered campaigns, publication figures, source crosswalk).
3. Verify no secret material, unwanted large outputs, or private information in distributable tree.
4. Check LICENSE, README, dependencies, provenance and figure hashes.
5. Set a final semantic release version and immutable tag; do not presume an article publication DOI or Zenodo DOI.
6. Merge or select exact release commit according to repository policy, and create GitHub release with Class B disclosure.
7. Archive exact tagged commit at Zenodo (or other approved repository); record DOI only after minted, and cross-reference the immutable version in final manuscript Data Accessibility statement.

## Release notes / limitations
The repository contains computational and provenance artifacts for the JRSI manuscript. Historical frozen scripts may reference original absolute paths; documented release adapters normalize paths without changing scientific kernels or frozen sources. The original archive retains preauthorization design metadata alongside later authorized manifests. Five recovered campaigns have complete original production provenance and release-form portability checks, but not all production runs were independently replayed from scratch. Accordingly these campaigns remain **Class B**.

**No DOI, immutable tag, GitHub release, or journal acceptance is implied by RC5 PASS or this checklist.**
