# Effect of recovery on RC4

The prior RC4 scientific clean-execution evidence remains useful evidence about the unchanged scientific core, but it cannot close the final release gate because the repository candidate has changed by adding recovered production provenance.

The corrected sequence is:

`RC3 PASS -> RC3.1 provenance recovery -> manifest/package refresh -> RC4 network-enabled clean installation on corrected candidate -> RC5 manuscript/repository consistency -> RC6 lock`.

The final RC4 run does not need to prove that historical archives were created prospectively; their own pre-outcome/final manifests already document that history. RC4 must demonstrate that the **release-form repository** installs and executes without hidden local state.
