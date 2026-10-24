# RC5 Gate Closure — 2026-10-24

**Decision: PASS** (manuscript/repository consistency and publication-figure reproducibility gate).

## Evidence
- User-executed local validation on branch `rc5-figure3-label-removal` at `9613d73afb0132dcbc30d4d1909bb579c7cc1636`.
- `python scripts/rc5_validate_s2_crosswalk.py`: **PASS**; 14 Table S2 entries, 13 distinct executables.
- `python scripts/validate_repository.py`: **PASS**.
- `python scripts/validate_recovered_campaigns.py`: **PASS**; Model B dense 22-point **dry run** confirms 660 pairs / 1320 scheduled runs; recovered runner syntax compilation passed.
- `python scripts/validate_figure_reproduction.py`: **PUBLICATION FIGURE REBUILD: PASS**; Figures 2–5 and S1–S6 passed. The initial `ModuleNotFoundError: fitz` in Conda base was resolved by activating project `.venv`; PyMuPDF 1.26.7 imported successfully.
- Figure 3 v1.0.2 updated and previously verified; Figure 1 is a frozen artwork asset without a computational builder.
- Table S2 Overleaf-rendered readability was independently inspected and approved by manuscript author.
- Numerical traces compared with original archived Model B, catalytic, and lattice output records, including catalytic multiplicity-adjusted intervals and lattice AICc/bootstrap evidence.

## Limits
1. Five recovered production campaigns remain **Class B**: original production provenance complete and release-form portability validated, but full end-to-end reruns of every large campaign have **not** been performed.
2. Historical source runners may contain hardcoded machine paths; retain original frozen source and documented portability normalization.
3. Frozen design configurations may say production unauthorized; later authorized run manifests and archived completeness reports support actual execution. Do not erase this historical distinction.
4. The user's supplied final terminal output does not show the `git status --short` result (the last displayed prompt follows the rebuild); do not claim independently verified clean local tree for that command.
5. No tag, merge, DOI, or public release is asserted by this gate decision.

## RC5 decision
**PASS**, with these provenance qualifications carried into RC6 release documentation. RC6 packaging, repository finalization, tag creation, release DOI/archiving remain separate activities.
