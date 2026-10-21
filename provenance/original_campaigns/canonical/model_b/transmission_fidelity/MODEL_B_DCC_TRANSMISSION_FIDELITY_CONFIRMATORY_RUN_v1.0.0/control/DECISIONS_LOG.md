# Decisions Log

## 2026-09-05 — Freeze Transmission-Fidelity Confirmatory Plan v1.0.0

**Decision:** Freeze an independent campaign to determine whether Figure 4(c,d) can be promoted from exploratory to primary prospectively confirmed evidence.

### Frozen choices
1. Preserve the **exact 18-point exploratory fidelity grid**; do not thin it.
2. Use 30 new root-seed blocks, all 18 fidelities within each block, selected-neutral pairing: 1080 runs.
3. Keep canonical Model B fixed at `beta=3`, `Theta=1.2`, SCF0, 250 generations.
4. Primary endpoint families are generation-250 `Delta C_down` and `Delta R`.
5. Keep all 18 points for descriptive figure density, but restrict inference to three preregistered contrasts per family.
6. Do not estimate or claim a continuous critical fidelity.
7. Increase specificity technical averaging from the exploratory 4 draws to 16 CRN draws, matching the later confirmatory standard; this changes technical precision only, not the `R` estimand. Validation against archived states is mandatory before production.
8. Root-seed block is the inferential unit.
9. No interim scientific outcome inspection or optional stopping.
10. Production is not authorized by this freeze.

### Evidence-status rule
Existing inheritance-sweep data remain exploratory until this campaign is completed and frozen. Existing four-scaffold and scaffold-strength prospective results are unaffected.

## 2026-09-05 — Preproduction validation and authorization
- Validation passed 33/33 checks before confirmatory outcomes existed.
- Technical propagation substream separation was documented prospectively in `PREPRODUCTION_TECHNICAL_AMENDMENT_v1.0.0.md`.
- The complete 1080-run frozen manifest was authorized as one campaign. Only the authorization flag differs between frozen and authorized copies.
- No interim scientific inference, seed replacement, grid modification, or optional stopping is permitted.

## 2026-09-05 — Confirmatory production completed and result frozen
- All 540 selected-neutral fidelity pairs / 1080 evolutionary runs completed with no missing outputs.
- Frozen analysis was executed only after complete production.
- Both predeclared endpoint families passed strong-support criteria; all six formal contrasts were positive in 30/30 root blocks.
- All five displayed high-fidelity means (`p=0.90, 0.925, 0.95, 0.975, 1.0`) were positive for both `Delta C_down` and `Delta R`.
- Deterministic analysis replay reproduced all seven analysis-file hashes exactly.
- Figure 4(c,d) are authorized for promotion from exploratory context to primary prospectively confirmed evidence, retaining the exact 18-point fidelity grid.
