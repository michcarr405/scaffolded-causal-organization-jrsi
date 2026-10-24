# Manuscript exclusion policy

The JRSI manuscript and Supplement are intentionally excluded from the computational repository. They remain editable publication documents until submission.

The repository does contain the frozen computational evidence required to support them: code, configurations, seed ledgers, simulation outputs/evolved states where retained, validation and provenance records, processed source tables, and reader-facing publication figure assets.

Beginning with the RC4.1 packaging correction, the repository includes the current five main figures and six supplementary figures under `publication/`, together with panel-to-source provenance maps and asset/source-table SHA-256 records. These are publication assets extracted from the compiled documents; inclusion of the figure assets does not make the manuscript or Supplement itself part of the immutable computational artifact.

RC5 is an external manuscript-to-repository consistency audit. The final polished manuscript and Supplement do not need to be embedded in the repository for that audit.

This separation prevents an editable publication draft from being mistaken for an immutable component of the reproducibility release while preserving direct auditability of every displayed figure.
