# VERSIONED_REPRODUCIBILITY_ARTIFACT_STANDARD.md

## Purpose

This document defines the default standard for building, validating, freezing, and releasing a computational research code repository as a **versioned reproducibility artifact**.

It is intended to be provided at the start of future modeling, simulation, data-analysis, and manuscript projects. The goal is not merely to make code available. The goal is to create a repository from which a scientifically meaningful result can be:

- traced to exact code, parameters, seeds, inputs, and analysis rules;
- regenerated without relying on undocumented local state;
- independently validated before production claims are frozen;
- linked unambiguously to manuscript figures, tables, and statistical statements;
- released as an immutable, citable scientific object.

The repository should be treated as part of the scientific record, not as a secondary software attachment.

---

# 1. Core principle

A reproducible computational paper should satisfy the following chain:

> **scientific specification -> audited implementation -> validated estimators and statistics -> frozen production outputs -> traceable figures and tables -> clean-room reproduction -> immutable release**

Every important scientific result should have an unbroken provenance path through this chain.

The repository should therefore answer, for any reported result:

1. What exact scientific question or contrast was prespecified?
2. What exact code produced the result?
3. What parameter configuration was used?
4. What random seeds or deterministic stream keys were used?
5. What raw or intermediate data were generated?
6. What estimator and statistical procedure were applied?
7. What script generated the table or figure?
8. What Git commit and release contain the authoritative version?
9. Can the result be reproduced from a fresh environment?

If one of these cannot be answered, the reproducibility artifact is incomplete.

---

# 2. Reproducibility must begin before production simulations

Do not wait until manuscript submission to make a repository reproducible.

The reproducibility architecture should be established before large production runs. In particular, the following should be defined before confirmatory simulations:

- scientific specification;
- inferential unit;
- model and estimator definitions;
- parameter configurations;
- seed architecture;
- output schemas;
- validation tests;
- intervention/control definitions;
- versioning and change-control rules.

Production data generated before these are controlled should be considered provisional until validated.

---

# 3. Controlling project documents

Every substantial computational project should maintain a small set of controlling documents.

Recommended files:

```text
SPECIFICATION.md
DECISIONS_LOG.md
REVIEWER_OR_REQUIREMENTS_MATRIX.md   # when applicable
VALIDATION.md
REPRODUCIBILITY.md
RESULT_FREEZE.md
RELEASE_MANIFEST.md
```

## 3.1 SPECIFICATION.md

The specification should freeze, before production where possible:

- scientific questions;
- primary outcomes;
- model definitions;
- parameter defaults and ranges;
- statistical unit;
- estimator definitions;
- intervention/control families;
- target or threshold definitions;
- censoring rules;
- primary statistical tests;
- confirmatory versus exploratory analyses;
- required robustness analyses;
- figure and table evidence requirements;
- release requirements.

## 3.2 DECISIONS_LOG.md

Any change to a frozen scientific or analytical rule should be recorded before implementation.

Each decision entry should state:

- date;
- decision ID;
- status;
- exact change;
- reason;
- alternatives considered;
- code affected;
- analyses affected;
- outputs invalidated;
- reruns required;
- verification required.

Do not silently modify a confirmatory analysis after looking at outcomes.

## 3.3 VALIDATION.md

This should record what was tested, how it was tested, what passed, what failed, and what limitations remain.

A test suite alone is not sufficient. The scientific meaning of the checks should be documented.

## 3.4 RESULT_FREEZE.md

When confirmatory production is complete, record:

- frozen scientific commit;
- production configuration hashes;
- dataset hashes;
- primary inferential results;
- figure-source data versions;
- permitted post-freeze actions;
- changes that would require reopening the scientific freeze.

---

# 4. Repository structure

Use a repository structure that separates scientific code, configuration, validation, production outputs, and manuscript-facing artifacts.

A useful default is:

```text
project/
|
|-- README.md
|-- LICENSE
|-- CITATION.cff
|-- pyproject.toml
|-- requirements.txt              # or environment lock equivalent
|-- environment.yml               # optional
|
|-- src/
|   `-- project_package/
|       |-- model.py
|       |-- simulation.py
|       |-- information.py
|       |-- statistics.py
|       |-- interventions.py
|       |-- rng.py
|       `-- io.py
|
|-- configs/
|   |-- defaults/
|   |-- pilots/
|   |-- confirmatory/
|   `-- figure_builds/
|
|-- scripts/
|   |-- run_baseline.py
|   |-- run_interventions.py
|   |-- run_statistics.py
|   |-- build_figures.py
|   |-- validate_repository.py
|   `-- clean_room_check.py
|
|-- tests/
|   |-- test_model.py
|   |-- test_rng.py
|   |-- test_estimators.py
|   |-- test_statistics.py
|   `-- test_endpoints.py
|
|-- validation/
|   |-- analytical_cases/
|   |-- deterministic_reruns/
|   |-- endpoint_checks/
|   |-- statistical_checks/
|   `-- validation_manifest.csv
|
|-- data/
|   |-- raw/
|   |-- intermediate/
|   |-- processed/
|   `-- figure_source/
|
|-- seeds/
|   |-- seed_ledger.csv
|   `-- stream_schema.md
|
|-- provenance/
|   |-- source_hashes.csv
|   |-- data_hashes.csv
|   |-- command_log.txt
|   |-- environment_record.txt
|   `-- release_manifest.csv
|
|-- figures/
|   |-- source/
|   `-- publication/
|
|-- revision/                     # when applicable
|   |-- SPECIFICATION.md
|   |-- DECISIONS_LOG.md
|   `-- REVIEWER_MATRIX.md
|
`-- docs/
    |-- VALIDATION.md
    |-- REPRODUCIBILITY.md
    |-- RESULT_FREEZE.md
    `-- RELEASE_NOTES.md
```

The exact structure may vary, but the conceptual separation should remain.

---

# 5. Phase 1: implementation and repository audit

Before new production results are trusted, audit the existing implementation.

## 5.1 Repository inventory

Record:

- package structure;
- executable entry points;
- notebooks;
- configuration files;
- model code;
- analysis code;
- figure-generation code;
- tests;
- dependency files;
- output directories;
- existing Git history;
- archived or submitted code versions.

Hash important imported archives and source snapshots.

## 5.2 Algorithm-to-description audit

For every scientifically meaningful operation, compare documentation/manuscript claims with the actual implementation.

Use a table such as:

| Component | Intended description | Code implementation | Match? | Required correction |
|---|---|---|---|---|

Audit at least:

- initialization;
- state representation;
- interaction rules;
- update rules;
- selection or sampling;
- inheritance or propagation;
- mutation/noise;
- intervention logic;
- stopping rules;
- summary statistics;
- inferential procedures.

The objective is not only to find programming bugs. It is to detect mismatches between the scientific description and what the code actually computes.

## 5.3 Static source audit

Search the codebase for:

- hidden global random calls;
- hard-coded parameters;
- duplicated analysis logic;
- nondeterministic ordering;
- implicit defaults;
- paths tied to one machine;
- notebook-only transformations;
- unrecorded filtering;
- manual figure edits;
- silent dropping of failed/censored cases;
- floating-point equality assumptions;
- stale output reuse.

---

# 6. Random-number architecture

Randomness must be scientifically controlled, not merely seeded once.

## 6.1 Inventory every stochastic operation

For each random draw, record:

- function;
- source file;
- purpose;
- generator used;
- seed or stream derivation;
- whether reruns are deterministic;
- whether the stream is coupled to call order.

## 6.2 Use explicit generators

Avoid hidden global random state such as uncontrolled calls to module-level RNG functions.

Prefer explicit generators passed into stochastic functions.

A function that uses randomness should normally make its random dependency visible.

## 6.3 Separate streams by purpose

At minimum, consider separate streams for:

- parameter or affinity generation;
- initial states;
- baseline evolution;
- observation/sampling;
- intervention generation;
- continuation trajectories;
- permutation nulls;
- bootstrap resampling;
- randomized controls;
- randomized topology schedules.

The purpose is to prevent one extra random draw in an unrelated step from silently changing downstream scientific outcomes.

## 6.4 Hierarchical stream keys

Prefer reproducible keys derived from meaningful identifiers, for example:

```text
root_seed
condition_id
replicate_id
analysis_stage
stream_purpose
continuation_id
permutation_id
```

The same semantic key should recover the same stream regardless of execution order.

## 6.5 Required RNG tests

At minimum verify:

- same code + same configuration + same seed -> identical output;
- same seed reproduces across fresh processes;
- different seeds produce different trajectories;
- no stochastic function works without an explicit generator when one is required;
- independent streams do not change when unrelated streams are added or reordered.

---

# 7. Minimal scientific test suite

Unit tests should target scientific invariants, not only software mechanics.

Useful categories include:

## 7.1 Encoding and state tests

- state encoding/decoding;
- motif or feature extraction;
- indexing;
- positional assignment;
- boundary handling;
- category definitions.

## 7.2 Probability and update tests

- probability normalization;
- softmax or transition rules;
- limiting cases;
- selection probabilities;
- inheritance/transmission logic;
- mutation logic;
- conservation rules where applicable.

## 7.3 Fitness or objective tests

- exact small-case values;
- neutral cases;
- positive/negative contribution rules;
- floors or clipping;
- normalization.

## 7.4 Intervention tests

- constant endpoint;
- identity endpoint;
- no-op endpoint;
- complete scrambling endpoint;
- duplicate intervention maps;
- map-label invariance;
- expected preservation/destruction properties.

## 7.5 Statistical and estimator tests

- hand-computable examples;
- known-null examples;
- known-perfect-association examples;
- permutation behavior;
- censoring behavior;
- bootstrap block structure;
- paired versus unpaired contrasts;
- missing-data handling.

---

# 8. Analytical validation before production

A scientifically strong repository should include tests where the expected answer is known independently of the implementation.

These are more informative than tests that compare one implementation against another implementation of the same idea.

Use:

- hand-computable examples;
- population-limit predictions;
- symmetry arguments;
- limiting parameter cases;
- exact endpoint identities;
- constructed null distributions;
- conservation laws;
- dimensional or normalization checks.

For every important estimator, ask:

> What result should this produce in a deliberately simple case where the answer is known?

Then encode that expectation as a permanent test.

---

# 9. Endpoint recovery

Whenever an estimator, intervention, or transformation has mathematically defined limiting cases, test them explicitly.

Examples:

- identity transformation recovers the unintervened result;
- constant grouping gives zero distinguishable information;
- zero coupling removes the corresponding causal pathway;
- full scrambling removes the targeted relational structure;
- no-op interventions leave outputs unchanged;
- neutral selection produces the expected null behavior.

Endpoint failure is a release blocker because it indicates that the pipeline may not mean what the manuscript says it means.

---

# 10. Duplicate and identity auditing for interventions

For any family of grouping maps, partitions, network rewires, masks, or transformations:

1. generate the exact transformation;
2. store it, not merely its requested parameter;
3. compute its actual effective size/resolution;
4. calculate a canonical hash;
5. identify duplicates;
6. identify constant, identity, and other endpoints;
7. verify deterministic map generation where expected.

Recommended manifest columns:

```text
method
requested_parameter
actual_parameter
map_hash
duplicate_of
endpoint_type
root_seed
map_seed
code_commit
```

Do not treat two requested settings as distinct scientific interventions if they produce the same transformation.

---

# 11. Statistical-pipeline validation

Validate statistical logic separately from the model itself.

## 11.1 Define the inferential unit

Do not infer independence from file rows or simulation output count.

Explicitly state the hierarchy, for example:

```text
independent evolved population = inferential replicate
intervention maps = repeated measurements
continuation seeds = technical Monte Carlo replicates
molecules/time points/windows = internal observations
```

## 11.2 Validate nested structure

When resampling or permuting, preserve the scientifically correct block structure.

Examples:

- bootstrap complete independent replicate blocks;
- do not bootstrap nested observations as if independent;
- use paired permutations when conditions share root seeds;
- keep technical continuations nested.

## 11.3 Censoring and target failures

If a target is not reached, record it as a censored or lower-bound result when mathematically appropriate.

Do not silently replace target failures with boundary values and analyze them as ordinary exact observations.

Test:

- exact target recovery;
- target-not-reached behavior;
- boundary interpolation;
- ties;
- numerical tolerance;
- all-censored cases;
- mixtures of reached and unreached targets.

## 11.4 Synthetic statistical tests

Before production, generate synthetic data with known structure and confirm that:

- null effects do not systematically appear significant;
- designed effects are recoverable;
- paired tests respect pairing;
- bootstrap intervals behave sensibly;
- replicate-level summaries match direct calculations.

---

# 12. Seed ledger

Every production run should be recoverable from a seed ledger.

Recommended fields:

```text
campaign_id
condition_id
root_seed
replicate_id
initialization_seed
model_seed
observation_seed
intervention_seed
continuation_seed
permutation_seed
bootstrap_seed
control_seed
config_hash
code_commit
output_path
output_hash
status
```

Not every project needs every field, but seed provenance should be explicit.

The ledger should be machine-readable and committed to the repository or archived with the release.

---

# 13. Configuration control

Do not rely on values scattered across scripts.

Use machine-readable configuration files for production campaigns.

Each production output should record:

- configuration filename;
- full resolved configuration;
- configuration hash;
- Git commit;
- seed identifiers;
- execution timestamp;
- software environment identifier.

If defaults can change between code versions, store the resolved values, not only the name of the default profile.

---

# 14. Production versus validation versus exploration

Keep these modes visibly separate.

## 14.1 Validation runs

Purpose: determine whether the implementation is correct.

They may use:

- tiny systems;
- artificial edge cases;
- hand-constructed states;
- reduced replicate counts.

They should not be interpreted as substantive scientific evidence.

## 14.2 Exploratory runs

Purpose: learn the system and develop hypotheses.

They may inform later confirmatory designs, but they must be labeled exploratory.

## 14.3 Confirmatory production runs

Purpose: produce evidence for manuscript claims.

These should use:

- frozen design;
- prespecified contrasts;
- independent seeds not used for tuning;
- frozen code/configuration;
- complete provenance.

Do not blur these categories after results are known.

---

# 15. Production archive requirements

The production archive should retain enough information to recompute reported analyses without rerunning the full simulation whenever practical.

Preserve as appropriate:

- initial states;
- evolved/final states;
- checkpoint states;
- raw observations;
- intervention assignments;
- transformation hashes;
- continuation trajectories;
- summary statistics;
- inferential records;
- seed ledgers;
- configuration files;
- figure-source tables;
- validation outputs.

For expensive simulations, storing evolved states can be critical. If states are not archived, later intervention or diagnostic analyses may require scientifically unnecessary reruns.

---

# 16. Hash-based provenance and archive integrity

Use cryptographic hashes, preferably SHA-256, for scientifically important files.

Hash:

- imported source archives;
- frozen code snapshots where useful;
- production datasets;
- evolved states;
- intervention maps;
- processed figure-source tables;
- final figure assets;
- release archives.

Maintain manifests such as:

```text
path,sha256,size_bytes,role,generated_by,code_commit
```

Hashes serve several purposes:

- detect accidental modification;
- prove that a figure source is the same object that was frozen;
- distinguish scientifically identical but render-different assets;
- verify clean-room reproduction;
- make provenance auditable.

---

# 17. Figure and table reproducibility

Publication figures should be treated as derived scientific artifacts.

For each figure, preserve:

1. frozen source data;
2. plotting script;
3. exact command;
4. relevant configuration;
5. source-data hash;
6. rendered output hash;
7. figure version;
8. manuscript panel mapping.

Avoid manual edits that cannot be regenerated.

If manual vector editing is scientifically necessary, preserve:

- editable master;
- derivative export;
- explicit statement of what was manually changed;
- confirmation that no quantitative content changed.

Distinguish **scientific reproducibility** from **render identity**. A later layout-only change may leave the quantitative science unchanged while making the submitted artwork non-identical to the archived render. Such discrepancies must be documented rather than hidden.

---

# 18. Result freeze

After the confirmatory analyses pass validation and all primary results are accepted, create a formal result freeze.

The freeze should identify:

- exact Git commit;
- exact production configurations;
- exact datasets;
- exact statistical outputs;
- exact figure-source tables;
- exact figure scripts;
- primary numerical claims;
- known limitations;
- unresolved production-only items.

After freeze:

### Allowed without reopening science

- typography corrections;
- alignment and spacing;
- non-semantic wording cleanup;
- file-format conversion;
- production layout changes that do not alter data or interpretation.

### Requires reopening or new version

- changing model rules;
- changing estimators;
- changing intervention definitions;
- changing primary contrasts;
- changing statistical unit;
- changing censoring rules;
- changing target definitions;
- adding post hoc confirmatory conditions;
- modifying frozen data.

---

# 19. Result-freeze audit

Before release, perform an audit that recomputes manuscript-facing inferential records from frozen archived data without rerunning production simulations.

The audit should verify:

- reported means/medians/effect sizes;
- confidence intervals;
- p-values or permutation results;
- target counts;
- censoring status;
- replicate counts;
- figure-source tables;
- table values;
- manuscript numerical callouts.

This is a powerful separation of concerns:

> production simulation creates the evidence; the freeze audit verifies the reported evidence.

The audit should not silently regenerate new production data.

---

# 20. Clean-room reproducibility test

A release should not be considered complete until it has been tested outside the development environment.

## 20.1 Clean-room principle

Start from the repository release candidate as if you were a new user.

Do not rely on:

- uncommitted files;
- shell history;
- local notebooks;
- developer-only data paths;
- cached objects;
- hidden environment variables;
- manually installed packages not declared by the project.

## 20.2 Recommended clean-room procedure

1. clone or unpack the release candidate into a new directory;
2. create a fresh virtual/conda environment;
3. install only documented dependencies;
4. run the test suite;
5. run analytical validation checks;
6. run deterministic same-seed checks;
7. regenerate representative simulation blocks;
8. regenerate representative statistics;
9. regenerate publication figures from archived figure-source data;
10. compare expected hashes or numerical checksums;
11. record commands, environment versions, and pass/fail status.

For extremely expensive projects, full production reruns may be unnecessary if deterministic representative blocks plus complete archived production outputs are sufficient. The scope of the clean-room check should be documented explicitly.

---

# 21. Environment capture

Record both declared and observed environments.

Preserve:

- Python/R/Julia/etc. version;
- direct dependencies;
- lock file where practical;
- operating system;
- architecture;
- compiler/runtime dependencies;
- GPU/CUDA dependencies where applicable;
- package-manager version;
- relevant environment variables.

Prefer two records:

1. **declared environment**: the dependencies users should install;
2. **execution environment**: the exact environment in which production/validation ran.

---

# 22. Exact commands

A reproducibility repository should contain exact commands for:

- environment setup;
- unit tests;
- validation suite;
- baseline simulations;
- interventions/controls;
- statistical analysis;
- figure generation;
- table generation;
- result-freeze audit;
- clean-room verification.

Avoid instructions like:

> “Run the analysis script.”

Prefer:

```bash
python scripts/run_analysis.py --config configs/confirmatory/main.yaml
```

Every manuscript figure and primary statistical result should map to at least one documented command.

---

# 23. README requirements

The top-level README should let an unfamiliar researcher understand the repository without reading the manuscript first.

It should contain:

- project purpose;
- model/analysis summary;
- repository map;
- software requirements;
- installation instructions;
- quick validation command;
- reproduction commands;
- explanation of raw versus processed data;
- seed policy;
- version/release information;
- DOI/archive link;
- expected runtimes and computational requirements;
- citation instructions;
- known limitations.

---

# 24. AI-assisted code validation

If AI-assisted tools contributed to code, do not rely on disclosure alone.

The appropriate scientific response is validation.

The repository should demonstrate that AI-assisted code was subjected to:

- human review of scientific logic;
- unit tests;
- hand-computable analytical checks;
- deterministic reruns;
- endpoint recovery;
- independent fresh-environment execution;
- source and output provenance checks.

A useful manuscript-level statement is conceptually:

> AI-assisted tools contributed to code development, but reported analyses were validated through unit tests, analytical checks, deterministic reruns, provenance-controlled production, and independent clean-environment execution.

Do not claim independent validation if it was not actually performed.

---

# 25. Versioning strategy

Use Git for scientific history and semantic versioning for public releases.

## 25.1 Commits

Commit logically distinct scientific changes separately.

Useful milestone commits include:

- source import;
- RNG repair;
- estimator validation;
- statistical-pipeline validation;
- production campaign freeze;
- figure-source freeze;
- reproducibility release candidate.

Record important commit hashes in phase handoffs and release manifests.

## 25.2 Tags

Use immutable release tags such as:

```text
project-reproducibility-v1.0.0
```

A public tag should point to exactly one immutable scientific state.

## 25.3 Do not mutate published releases

If a later change is needed, create a new version.

Do not silently replace files under an existing tag or DOI merely to make them match later manuscript production.

---

# 26. Detailed release-candidate and public-release procedure

The release process is itself part of reproducibility. Do not jump directly from a development repository to a public Git tag or DOI. Build and validate an explicit release candidate, then promote only a candidate that passes all release gates.

The sequence below should be followed for future publication-grade computational projects. The exact RC numbering can be adapted, but the order and pass/fail logic should be preserved.

## 26.1 RC0 - scientific freeze and release scope lock

RC0 is not yet a distributable package. It is the point at which the scientific state is frozen and the intended release contents are declared.

Required actions:

1. confirm that all scientific analyses intended for the manuscript have passed their relevant validation gates;
2. freeze the model, estimators, intervention definitions, statistical unit, target/censoring rules, parameter sets, and inferential procedures;
3. identify the exact scientific commit that will underlie the release;
4. freeze the production datasets and figure-source tables that support the manuscript;
5. create or update the result-freeze record;
6. declare what is in scope for the reproducibility release and what is intentionally excluded;
7. stop scientific retuning. Any later scientific change must reopen the analysis under a new version.

RC0 pass criteria:

- scientific results are frozen;
- all production inputs are identified;
- the repository has a clean scientific commit representing that state;
- no unresolved scientific ambiguity remains that could change reported results.

Required artifacts:

```text
RESULT_FREEZE.md
DECISIONS_LOG.md
RELEASE_SCOPE.md
frozen scientific commit hash
frozen production-data manifest
```

## 26.2 RC1 - assemble the candidate repository

Create the first actual release-candidate tree from the frozen scientific state. Do not use the active development working tree as the final package without this assembly step.

Required actions:

1. create a release-candidate branch, worktree, or exported directory from the frozen scientific commit;
2. remove caches, temporary notebooks, local scratch outputs, development logs, editor files, credentials, machine-specific paths, and other non-release material;
3. retain all source code needed to reproduce the reported analyses;
4. include the exact frozen configuration files used for production;
5. include the evolved states, checkpoints, or other simulation state required for downstream analyses when feasible;
6. include raw outputs or immutable archived generated datasets when practical;
7. include processed figure-source data rather than requiring figures to be reverse-engineered from image files;
8. include test and validation scripts;
9. include seed ledgers and RNG documentation;
10. include exact execution commands for all manuscript figures, tables, and statistical results;
11. add the release documentation listed below.

Minimum RC1 documentation:

```text
README.md
LICENSE
CITATION.cff
VALIDATION.md
REPRODUCIBILITY.md or equivalent
ENVIRONMENT.md
requirements.txt / lock file / pyproject.toml as appropriate
SEED_LEDGER.csv or equivalent
SOURCE_HASH_MANIFEST.csv
DATA_MANIFEST.csv
FIGURE_SOURCE_MANIFEST.csv
RELEASE_MANIFEST.md or .csv
```

README requirements:

- scientific purpose and scope;
- repository layout;
- supported operating system or platform assumptions;
- environment creation instructions;
- minimal smoke-test command;
- validation command;
- exact commands for production analyses;
- exact commands for figures and tables;
- expected output locations;
- approximate computational cost where useful;
- distinction between raw, processed, and publication outputs;
- citation instructions;
- known limitations or deliberately excluded assets.

RC1 pass criteria:

- a new user can identify the entry points without reading the source code first;
- every manuscript figure and reported statistic has a documented reproduction path;
- no required file exists only on the developer's local machine;
- repository metadata, data, seeds, and validation materials are present.

## 26.3 RC2 - provenance, hash, and package-integrity audit

RC2 verifies that the candidate contains the intended scientific objects and that those objects can be tied unambiguously to the frozen analysis.

Required actions:

1. hash all critical source, configuration, dataset, state, and figure-source files using SHA-256 or an equivalent cryptographic hash;
2. verify that manifests contain the expected files and no unexplained duplicates;
3. verify that all intervention/transformation maps, where applicable, have stable identifiers or assignment hashes;
4. verify that all stochastic production runs can be mapped to a seed-ledger entry;
5. verify that production outputs identify their source configuration, root seed, replicate identifier, and relevant software version;
6. verify that figure-source tables map explicitly to final manuscript figure panels;
7. verify that archived simulation states correspond to the populations or checkpoints used in downstream analyses;
8. verify that no release file is silently regenerated from a different scientific state;
9. record the candidate tree hash or full Git commit hash after packaging changes are committed.

Recommended release-manifest fields:

```text
artifact_id
relative_path
artifact_type
scientific_role
source_commit
configuration_id
seed_or_seed_range
sha256
created_by_command
manuscript_target
notes
```

RC2 pass criteria:

- all critical files have provenance;
- all hashes are reproducible;
- source-to-result and result-to-figure mappings are explicit;
- no unexplained file/version ambiguity remains.

## 26.4 RC3 - full validation against the packaged candidate

Run validation against RC3 as packaged, not against the development tree.

Required actions:

1. execute the complete unit and integration test suite;
2. rerun analytical or hand-computable checks;
3. rerun limiting-case and endpoint tests;
4. rerun same-seed determinism tests and different-seed divergence tests;
5. rerun estimator invariance tests such as label renaming or duplicate-map equivalence where relevant;
6. rerun statistical-pipeline validation, including censoring and replicate-level inference tests;
7. run result-freeze validators that compare the packaged outputs with the frozen inferential record;
8. check that validation scripts fail loudly if a required artifact is missing or altered;
9. save the validation transcript or machine-readable validation summary in the candidate.

Important rule:

> Validation failures are not documentation issues. A failing scientific or reproducibility check blocks promotion of the release candidate.

If the failure is caused only by packaging or documentation, correct the package, increment the candidate identifier, and rerun the affected validation. If the failure reveals a scientific difference, reopen the scientific analysis under version control rather than patching the release package silently.

RC3 pass criteria:

- all mandatory tests pass;
- expected analytical identities and endpoints are recovered exactly or within prespecified numerical tolerance;
- deterministic reruns are confirmed;
- the packaged candidate reproduces the frozen validation state.

## 26.5 RC4 - clean-room reproduction

This is the strongest pre-release reproducibility test. Treat the candidate as though it came from an external researcher.

Required actions:

1. create a new empty directory or clean machine/container/virtual environment;
2. obtain the candidate only through the intended public-facing mechanism: fresh clone, release archive, or exported package;
3. create the environment using only the packaged instructions;
4. do not rely on the developer's shell history, editable installs, environment variables, cached local data, or untracked files;
5. run the smoke test;
6. run the validation suite;
7. rerun at least one representative block from each major analysis family when full reproduction is computationally expensive;
8. regenerate representative statistical summaries and figures directly from the released data/code;
9. compare the regenerated outputs with frozen reference values, hashes, or tolerances;
10. document hardware/platform details and wall-clock/runtime information where useful;
11. save a clean-room rerun record in the repository or release archive.

The clean-room record should state:

```text
candidate identifier
source commit
platform
Python/runtime version
environment creation command
validation command
representative rerun commands
reference outputs checked
hash/tolerance comparison results
PASS/FAIL
```

RC4 pass criteria:

- installation works from the documented instructions;
- tests and validators pass without hidden local state;
- representative production outputs reproduce the frozen values within the declared criterion;
- publication figures can be regenerated from packaged source data or documented production scripts.

## 26.6 RC5 - manuscript, figure, and repository consistency audit

Before public release, compare the candidate with the actual manuscript package.

Check at minimum:

- repository name and URL;
- project/release title;
- author metadata;
- license;
- software versions;
- model and parameter descriptions;
- independent replicate counts;
- seed ranges where stated;
- figure numbers and panel mappings;
- statistical methods and permutation/bootstrap counts;
- data and figure-source filenames;
- validation procedures claimed in the manuscript;
- Data Accessibility statement;
- AI-assisted-code validation wording where applicable.

Every manuscript claim of reproducibility should correspond to a concrete artifact or recorded procedure in the candidate.

RC5 pass criteria:

- no manuscript/repository contradiction remains;
- the Data Accessibility statement can be completed once the permanent identifiers are known;
- all manuscript-facing file and figure references point to existing release artifacts.

## 26.7 RC6 - final release-candidate lock

Once RC5 passes, lock the final candidate before publication.

Required actions:

1. commit all intended release files;
2. confirm `git status` is clean;
3. record the full commit hash;
4. regenerate the final hash and release manifests from the clean tree;
5. rerun the shortest mandatory validation command one final time;
6. mark the candidate `PASS` in a release-candidate record;
7. create a byte-for-byte release archive if one will be deposited externally;
8. compute and record the release-archive SHA-256 hash.

No file should change between this lock and creation of the public Git tag except metadata that necessarily requires the final public identifiers. If such metadata changes files, commit those changes and repeat the final lock checks.

---

# 27. GitHub and Zenodo public-release workflow

The public release should promote the passed final candidate without changing its scientific contents.

## 27.1 Create the immutable Git tag

From the final clean commit:

1. record the full Git commit hash in the release record;
2. create an annotated or otherwise documented immutable tag, for example:

```text
project-reproducibility-v1.0.0
```

3. verify locally that the tag resolves to the intended commit;
4. push the release commit and tag to GitHub;
5. inspect the remote repository to confirm that the public tag resolves to the same full commit hash.

Do not move or overwrite a published scientific tag.

## 27.2 Inspect the public GitHub state

Do not assume a successful push means the public package is correct.

Inspect the repository as a public user would see it:

- README rendering;
- license detection;
- citation metadata;
- default branch state;
- release tag;
- downloadable source archives;
- expected data directories and large-file links;
- documentation links;
- no exposed secrets or local paths;
- no missing files caused by `.gitignore`, Git LFS, submodules, or packaging rules.

If the public GitHub state differs from the validated candidate, stop and correct the release before DOI publication.

## 27.3 Create the GitHub release

Create a GitHub Release from the frozen tag.

Recommended release metadata:

- release title;
- version number;
- brief scientific scope;
- frozen commit hash;
- validation status;
- known limitations;
- citation instruction;
- link to the permanent archive once available.

Attach supplemental release archives only if they are necessary and their hashes are recorded. Prefer reproducible generated archives to manually assembled zip files.

## 27.4 Prepare the Zenodo deposit

Archive the exact tagged scientific release in Zenodo or an equivalent permanent repository.

Before publishing the deposit, inspect:

- title;
- creators and affiliations;
- ORCID identifiers if used;
- description;
- version number;
- publication type/resource type;
- license;
- keywords;
- related identifiers;
- GitHub release/tag relationship;
- uploaded files and their sizes;
- whether generated data archives are included or linked correctly;
- citation metadata;
- access status.

The Zenodo deposit must correspond to the same scientific state as the Git tag. Do not upload a convenient local directory that has changed since tag creation.

## 27.5 Publish the immutable archive

After metadata and files have been reviewed:

1. publish the Zenodo record;
2. record the **version DOI** assigned to that specific release;
3. record the concept DOI separately if Zenodo provides one and if it is useful for citation/version tracking;
4. verify that the published landing page shows the intended version, authors, license, files, and related GitHub information;
5. verify that downloaded archived files correspond to the tagged release or recorded release archive hash.

For manuscript reproducibility, prefer citing the version-specific DOI when the exact scientific release matters.

## 27.6 Cross-system identity audit

After GitHub and Zenodo are public, verify that all identifiers describe the same release.

The final release record should contain:

```text
repository URL
Git tag
full Git commit hash
GitHub Release URL/version
release archive SHA-256, if applicable
Zenodo version DOI
Zenodo concept DOI, if applicable
release date
validation status
```

Verify explicitly:

```text
Git tag -> expected commit
GitHub Release -> expected tag
Zenodo record -> expected version/tag
Zenodo files -> expected release archive or repository contents
manuscript Data Accessibility statement -> same identifiers
CITATION.cff -> compatible version and citation metadata
```

A mismatch blocks final manuscript submission until it is resolved or explicitly documented.

## 27.7 Update manuscript and repository metadata only after identifiers are final

Once the permanent DOI exists:

1. insert the version DOI and release tag into the manuscript Data Accessibility statement;
2. update README and citation metadata if necessary;
3. if those metadata edits change the repository, decide whether they are release-metadata-only or require a new tag. Prefer generating metadata before tagging when possible to avoid this loop;
4. perform one final manuscript-repository-DOI consistency check;
5. archive the final release checklist.

Do not create a permanent DOI before the scientific results and release package are frozen. The controlling revision workflow explicitly treated permanent DOI creation as a post-freeze action.

## 27.8 Post-release immutability rule

After publication of the tag and DOI:

> **Never mutate the scientific contents of that release to make them match a later manuscript or production change.**

If a substantive scientific or reproducibility change is needed, issue a new version such as `v1.0.1` or `v1.1.0`, rerun the appropriate release-candidate checks, and create a new version DOI.

If the change is production-only, such as label placement, panel spacing, or a narrowed artwork layout that leaves the data and inference unchanged, document it as a production-provenance difference unless exact artwork-level regeneration is important enough to justify a new immutable release.

This distinction prevents a published DOI from becoming a moving target and preserves the scientific audit trail.

## 27.9 Release-candidate checklist summary

A compact operational checklist is:

```text
[ ] RC0 scientific state frozen
[ ] RC1 release tree assembled and documented
[ ] RC2 hashes/provenance/manifests verified
[ ] RC3 full packaged validation passed
[ ] RC4 clean-room reproduction passed
[ ] RC5 manuscript-repository consistency passed
[ ] RC6 final candidate locked; clean Git status; archive hash recorded
[ ] immutable Git tag created
[ ] tag pushed and remote commit verified
[ ] public GitHub repository inspected
[ ] GitHub Release created from frozen tag
[ ] Zenodo metadata and files inspected before publication
[ ] Zenodo version published
[ ] version DOI recorded
[ ] Git tag / commit / GitHub Release / Zenodo DOI cross-checked
[ ] manuscript Data Accessibility statement updated
[ ] final release audit archived
```

The release is complete only when this chain is closed.

---

# 28. Handling post-release production differences

Sometimes the manuscript changes after the scientific release—for example, a figure layout is narrowed, labels move, or vector artwork is adjusted.

Classify the difference.

## 28.1 Scientific change

Examples:

- changed data;
- changed statistic;
- changed panel content;
- changed estimator;
- changed result.

This requires a new scientific release version.

## 28.2 Production-only change

Examples:

- spacing;
- label placement;
- crop;
- typography;
- panel resizing without data changes.

This does not necessarily require reopening the scientific freeze.

However, if the public archive can no longer regenerate the exact submitted artwork, record the discrepancy explicitly as a **production-provenance exception**.

Never pretend exact render reproducibility when it no longer exists.

---

# 29. No-do-over rules

Unless a documented decision reopens the analysis:

1. Do not run large production sweeps before core estimators are validated.
2. Do not run intervention suites before endpoint tests pass.
3. Do not produce final publication figures before inferential results are frozen.
4. Do not create a DOI release before the scientific state is frozen.
5. Do not treat nested technical replicates as independent scientific replicates.
6. Do not introduce new confirmatory analyses after viewing results without versioning them as new work.
7. Do not preserve old numerical values merely for continuity if corrected analysis changes them.
8. Do not silently replace published release assets.
9. Do not rerun expensive production merely to recreate a figure if frozen raw/processed data are sufficient.
10. Do not allow undocumented manual steps between source data and manuscript figures.

---

# 30. Gate-based workflow

A strong default workflow is:

## Gate 0 - specification ready

Pass only if:

- scientific question is explicit;
- primary outcomes are defined;
- statistical unit is defined;
- production versus exploration is distinguished;
- change-control rules exist.

## Gate 1 - implementation validity

Pass only if:

- repository is inventoried;
- implementation matches intended model;
- stochastic calls are inventoried;
- deterministic reruns pass;
- core scientific unit tests pass;
- important transformations are hashed/inventoried.

## Gate 2 - estimator validity

Pass only if:

- analytical examples pass;
- null behavior passes;
- endpoint identities pass;
- finite-sample corrections behave properly;
- estimator provenance is recorded.

## Gate 3 - statistical-pipeline validity

Pass only if:

- inferential hierarchy is correct;
- block/pair structure is preserved;
- censoring is correct;
- bootstrap/permutation logic passes synthetic tests;
- machine-readable inferential summaries are produced.

## Gate 4 - production readiness

Pass only if:

- confirmatory configuration is frozen;
- seed ledger is frozen;
- code commit is frozen;
- expected output schema is validated;
- production commands are recorded.

## Gate 5 - core result complete

Pass only if:

- planned production completed;
- failures are accounted for;
- primary inference completed;
- no unresolved implementation issue threatens interpretation.

## Gate 6 - robustness and causal controls complete

Pass only if required robustness/control analyses are complete.

## Gate 7 - scientific result freeze

Pass only if:

- all manuscript-level claims have frozen supporting evidence;
- figures can be generated from frozen source data;
- no scientific retuning remains.

## Gate 8 - reproducibility release

Pass only if:

- README complete;
- tests pass;
- environment locked/documented;
- seed ledger archived;
- raw/processed data archived as appropriate;
- exact commands documented;
- clean-room verification passes;
- hashes/manifests complete;
- Git tag created;
- immutable archive/DOI created.

Projects may rename or combine gates, but the logical sequence should be preserved.

---

# 31. Required machine-readable manifests

For substantial projects, aim to maintain at least:

```text
SEED_LEDGER.csv
SOURCE_HASH_MANIFEST.csv
DATA_HASH_MANIFEST.csv
CONFIG_MANIFEST.csv
RUN_MANIFEST.csv
FIGURE_SOURCE_MANIFEST.csv
VALIDATION_MANIFEST.csv
RELEASE_MANIFEST.csv
```

The objective is that provenance can be inspected programmatically, not reconstructed from prose alone.

---

# 32. Recommended release manifest fields

```text
project
release_version
git_tag
git_commit
release_date
archive_doi
python_version
platform
primary_config_hash
seed_ledger_hash
raw_data_manifest_hash
processed_data_manifest_hash
figure_source_manifest_hash
test_status
validation_status
clean_room_status
known_exceptions
```

---

# 33. Minimal definition of “reproducibility validated”

Do not use the phrase loosely.

A project may describe its computational results as reproducibility-validated only if, at minimum:

- the implementation has been audited;
- stochastic behavior is controlled;
- scientific unit tests pass;
- key estimators pass analytical or known-result tests;
- mathematical endpoints recover exactly or within justified tolerance;
- statistical nesting and censoring are tested;
- production inputs and outputs have provenance;
- exact analysis/figure commands are documented;
- the release has been executed successfully from a clean environment or equivalent independent reconstruction.

For stronger claims, also require:

- hash-based archive integrity verification;
- representative deterministic production reruns;
- frozen figure-source data;
- independent regeneration of publication figures;
- permanent archival DOI.

---

# 34. Suggested manuscript Methods language

Adapt to the actual project; do not claim steps that were not performed.

> All stochastic operations used explicit, purpose-separated random-number generators, with seeds and stream identifiers recorded in a machine-readable ledger. Validation included scientific unit tests, hand-computable analytical examples, limiting-case and endpoint checks, deterministic same-seed reruns, statistical-pipeline and censoring tests, and hash-based provenance checks on archived outputs. Production analyses were frozen before manuscript figure generation. Publication figures were generated from archived figure-source data, and representative analyses were independently rerun from a clean environment using the documented dependencies and commands. The frozen code, data, validation records, release tag, commit identifier, and permanent archive are provided in the public reproducibility release.

---

# 35. Instructions to ChatGPT or another coding assistant in future projects

When this file is supplied as project guidance, follow these rules by default:

1. **Treat reproducibility as part of the scientific design from the beginning.**
2. **Do not begin large production runs until the implementation, RNG, estimators, and statistical pipeline have passed their relevant validation gates.**
3. **Prefer explicit configuration files, explicit generators, machine-readable manifests, and hashes over undocumented implicit state.**
4. **Never infer that repeated rows, continuation seeds, time points, molecules, or intervention maps are independent scientific replicates. Identify the actual inferential unit first.**
5. **Construct analytical and endpoint tests before trusting a new estimator.**
6. **Separate exploratory, validation, and confirmatory work in filenames, directories, configuration, and interpretation.**
7. **Record major scientific/analytical changes in a decision log before implementing them.**
8. **After confirmatory results are frozen, generate figures and tables from frozen source data rather than rerunning production unnecessarily.**
9. **Preserve exact commands, source/data hashes, environment information, and seed provenance.**
10. **Before public release, perform a clean-room reproduction from the release candidate rather than the development tree.**
11. **Do not mutate an immutable public release to synchronize later manuscript production changes; create a new version or document a production-provenance exception.**
12. **When AI-assisted code is used, validate it scientifically rather than treating AI disclosure as a substitute for verification.**
13. **At every phase handoff, state what is frozen, what remains provisional, what may be done next, and what is prohibited.**
14. **Prefer failure to a false pass.** If a reproducibility gate is not satisfied, record the blocker and do not silently advance.

---

# 36. Final checklist

Before declaring a repository publication-ready, verify all of the following.

## Scientific provenance

- [ ] Scientific specification frozen
- [ ] Decision log current
- [ ] Statistical unit explicit
- [ ] Confirmatory versus exploratory analyses labeled
- [ ] Production configuration frozen

## Code validity

- [ ] Implementation audited against intended model
- [ ] Core scientific unit tests pass
- [ ] No hidden uncontrolled RNG remains
- [ ] Same-seed deterministic rerun passes
- [ ] Different seeds diverge appropriately

## Estimator validity

- [ ] Hand-computable examples pass
- [ ] Known-null examples pass
- [ ] Population-limit/limiting-case checks pass where applicable
- [ ] Constant/no-op/identity endpoints pass
- [ ] Duplicate transformations produce identical results

## Statistical validity

- [ ] Inferential hierarchy documented
- [ ] Nested technical replicates handled correctly
- [ ] Pairing preserved where required
- [ ] Block bootstrap/permutation structure validated
- [ ] Target failures/censoring tested

## Provenance

- [ ] Seed ledger complete
- [ ] Config manifest complete
- [ ] Source hashes recorded
- [ ] Data hashes recorded
- [ ] Production command log retained
- [ ] Output schemas include commit/config/seed metadata

## Figures and tables

- [ ] Frozen figure-source data archived
- [ ] Figure scripts versioned
- [ ] Exact figure commands documented
- [ ] Figure source and output hashes recorded
- [ ] Manual production edits documented

## Release

- [ ] README complete
- [ ] License present
- [ ] CITATION.cff present
- [ ] Dependency lock/documentation present
- [ ] Validation record present
- [ ] Result-freeze audit passes
- [ ] Clean-room verification passes
- [ ] Git commit recorded
- [ ] Immutable tag created
- [ ] Permanent archive/DOI created
- [ ] Manuscript Data Accessibility statement matches release
- [ ] Known release exceptions explicitly documented

---

# 37. Guiding standard

The strongest practical test is simple:

> **A future researcher should be able to determine exactly what was run, why it was run, what random state and configuration produced it, how the reported statistic was calculated, which frozen data support the manuscript claim, and which immutable release preserves that evidence.**

If that can be done without reconstructing undocumented decisions from old chats, local files, or memory, the repository is functioning as a true **versioned reproducibility artifact**.
