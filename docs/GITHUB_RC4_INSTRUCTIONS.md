# GitHub RC4 clean-room instructions

Use **this exact repository tree** as the network-enabled RC4 candidate.

Candidate directory:

`JRSI_SCAFFOLDED_CAUSAL_ORGANIZATION_REPOSITORY_RC4_CANDIDATE_v0.1.3`

The working manuscript and Supplement are intentionally excluded from this computational release candidate. Do not add them before RC4. RC5 will compare the final polished manuscript externally against the frozen repository.

## Recommended procedure

1. Create a private or temporary GitHub repository, or use a dedicated `rc4-candidate` branch.
2. Copy the **contents** of this candidate directory to the repository root. Do not commit the enclosing ZIP as a substitute for the directly browsable tree.
3. Commit all files and confirm `git status` is clean.
4. Push the `rc4-candidate` branch.
5. Open **Actions -> RC4 clean-room reproducibility** and run the workflow if it did not start automatically.
6. Require the job to pass without manual edits to the runner.
7. Download and retain the `rc4-clean-room-logs` Actions artifact.
8. Record the full Git commit SHA, workflow run URL, run ID, runner OS/Python information and outcome in the RC4 closure record.

## What the workflow does

The included `.github/workflows/rc4-clean-room.yml` uses a fresh GitHub-hosted Ubuntu runner and:

- checks out only the pushed candidate;
- installs Python 3.13;
- installs dependencies from `requirements.txt` over the network;
- records the installed environment;
- validates repository structure and SHA-256 manifests;
- runs pytest;
- validates the recovered production bundles;
- reruns the original catalytic prospective assay and checks its frozen outputs.

## Pass criterion

RC4 closes only if the workflow succeeds from the untouched commit and the archived Actions log shows all required checks passing. Do not create the final immutable release tag or DOI at this stage.

After RC4 closes, proceed to RC5 manuscript-to-repository consistency auditing.
