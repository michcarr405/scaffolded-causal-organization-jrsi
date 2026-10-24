# RC4 clean-room status

**Status: PASS**

The network-enabled RC4 clean-room workflow completed successfully on the `rc4-candidate` branch using a GitHub-hosted Ubuntu runner and Python 3.13.

Validated components included:

- installation from declared Python dependencies, including Numba required by the recovered Model B dense-22 runner;
- repository structure and full SHA manifest;
- pytest suite;
- recovered production-bundle release-form validation;
- Model B dense-22 dry-run counts (660 selected-neutral pairs / 1,320 runs);
- original catalytic prospective replay.

The catalytic replay requires byte identity for `CONFIRM_ENDPOINT_STATES.npz` and `CONFIRM_CATALYTIC_MATRIX.csv`, requires `all_primary_pass=true`, and permits only tightly bounded numerical equivalence (rtol=atol=1e-12) for derived floating-point CSV/JSON outputs across platforms.

RC4 does not claim that every computationally expensive recovered production campaign was rerun end-to-end. Campaign-specific reproducibility class B is therefore retained conservatively where appropriate.
