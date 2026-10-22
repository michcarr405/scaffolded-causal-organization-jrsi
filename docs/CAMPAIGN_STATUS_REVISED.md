# Revised campaign reproducibility status after production-bundle recovery and RC4

RC4 network-enabled clean-room validation passed on GitHub-hosted Ubuntu/Python 3.13. The recovered campaign class remains **B** conservatively because RC4 validated release-form installation, manifests, compilation and the Model B dense-22 dry run, while not rerunning every large recovered production campaign end-to-end. The original catalytic prospective assay was replayed successfully.

| Campaign | Previous | Current | Provenance / RC4 state |
|---|---:|---:|---|
| Model B independent 22-point scaffold-strength replication | C | **B** | Original complete production/result archive recovered; 4,689-entry manifest verified; release-form 660-pair/1,320-run dry-run passed |
| Catalytic 22-point scaffold-strength campaign | C | **B** | Original complete campaign recovered; 33-entry final manifest verified; release-form runner compiled |
| Catalytic 18-point transmission-fidelity campaign | C | **B** | Original primary campaign recovered; 21-entry manifest verified; independent replication also recovered; release-form runner compiled |
| Catalytic reciprocal-history experiment | D | **B** | Original runner, config, seeds, endpoints and results recovered; 20-entry manifest verified; release-form runner compiled |
| Original prospective lattice control | D | **B** | Original prospective executable campaign recovered; 28-entry manifest verified; release-form runner compiled |

Class **A** remains reserved for an archive-complete campaign that has also been validated end-to-end in release form. The RC4 clean-room gate itself is PASS; retaining class B does not represent an RC4 failure.

See `provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.3.0.json` for the machine-readable status.
