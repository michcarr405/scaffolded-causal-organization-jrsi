# Section 2 / Section 3 / Supplement synchronization fix audit v1

## Status
All synchronization issues identified in the preceding audit have been addressed in the replacement source files in this bundle. The newly supplied Supplement already contains Figure S6; no S6 insertion is required.

## Substantive fixes
1. **Lattice task-state encoding**
   - Main Methods equation (3.18) now defines `p_i(X,B)=P(z_i=1|X,B)`.
   - The lattice lower-level state is explicitly `Z_L=(p_1,...,p_nsite)`.
   - The stored task remains `y_i in {-1,+1}` and the binary target is `tilde y_i=(y_i+1)/2 in {0,1}` before equation (3.19).
   - Supplementary Methods states the same implemented mapping.

2. **Section 2 -> lattice history specificity**
   - Section 2 now states explicitly that `R_q` is a selected-minus-neutral response for a specified history/probe and that history specificity is a further cross-history contrast under common present conditions.
   - This permits realization-specific selected-lineage common-probe history contrasts without falsely identifying them algebraically with `R_F`.
   - Section 3(g) explicitly identifies `H_lattice` as such a selected-lineage history contrast.

## Mathematical / notation synchronization
3. **Model B local versus global readout kernel**
   - Equation (3.1) is now described as the motif-window-level factor of the general Section 2 kernel.
   - The full realization-specific `K_B(dz|x)` is explicitly assembled from the local motif-window draws.

4. **Probe-angle symbol**
   - `phi_{q,B_P}` is reserved for the Section 2 expected-expression functional.
   - Reader-facing probe angles use `chi` in Methods and revised Figure 5/S6 captions and labels.

5. **Distance notation**
   - Model B explicitly defines `d = ||B_P-B_H||^2` as squared scaffold displacement.
   - Catalytic equal-distance probes are written directly as `||B_P-B_H||^2=1`, avoiding a second meaning for `d`.
   - The revised Figure 5 evidence cell and Supplementary Figure S5 label/caption use the explicit norm-squared form.

## Main / Supplement synchronization
6. **Cross-document equation references**
   - Supplementary Methods no longer relies on unresolved main-document `eqref` labels.
   - It now refers explicitly to main-text equations (3.3), (3.9), (3.11), (3.16) and (3.21).

7. **Supplementary Table S1 numbering**
   - The local table counter is set to `S1`, so standalone compilation renders `Table S1`, not `Table 1`.

8. **Lattice basis typo**
   - The normalization denominators in the Supplement now use `n_site` consistently rather than the stray symbol `N`.

9. **Reader-facing internal aliases**
   - The revised S6 caption removes `C1`, `C4` and `C5` labels.
   - The revised Figure 5 evidence matrix removes `C5 30/30` and retains simply `30/30`.

## Validation
- Section 2 + Section 3 replacement blocks compile successfully together; the only undefined reference in the standalone check is the deliberately absent manuscript Figure 1 label.
- Supplementary Methods + Supplementary Table S1 compile successfully as a standalone check.
- The table renders as `Table S1`.
- Revised Figure 5, S5 and S6 PDFs were rebuilt programmatically from the frozen source-faithful figure builds. No simulation, inferential analysis or data value was changed.
- Revised figure PDFs were rendered and visually inspected; no clipping or overlap was detected.

## Integration note
The uploaded compiled manuscript and supplementary PDF still contain the pre-patch text because they are compiled artifacts. The `.tex` files and figure/caption replacements in this bundle are the synchronization-corrected sources to use for the next manuscript compile.
