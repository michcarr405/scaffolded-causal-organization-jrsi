# Revised repository gap register after recovery

## Closed gaps

The following previous provenance gaps are **CLOSED**:

- original catalytic 22-point scaffold-strength production bundle;
- original catalytic 18-point fidelity production bundle;
- original prospective lattice production bundle;
- original catalytic reciprocal-history production bundle;
- original Model B independent dense 22-point production bundle.

## Remaining release-engineering work

1. **Portability normalization.** Preserve recovered originals unchanged and create public runner copies that replace historical absolute paths with repository-relative or CLI-configurable roots.
2. **Repository-wide manifest refresh.** The merged candidate requires new SHA-256/source/data/campaign manifests because the release tree has changed.
3. **Packaged validation.** Rerun structural validation and selected archive/result checks after merge.
4. **RC4 clean installation.** Run the network-enabled GitHub Actions clean-installation check on the corrected candidate, not the superseded pre-recovery candidate.
5. **License and public identifiers.** Select the final public license, GitHub URL/tag and permanent archive DOI before final release.

There is no longer a main-campaign reporting requirement to describe these five production packages as missing.
