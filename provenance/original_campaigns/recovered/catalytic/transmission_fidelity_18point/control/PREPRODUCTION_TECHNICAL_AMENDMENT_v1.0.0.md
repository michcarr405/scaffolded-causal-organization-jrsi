# Preproduction Technical Amendment v1.0.0

The first production invocation was terminated by the execution environment timeout before any result file or stdout outcome was written. No scientific outcome from the new fidelity campaign was generated or inspected.

To reduce wall-clock runtime, production is authorized to use a block-parallel runner. The amendment changes only execution scheduling: each of the 30 frozen root blocks is computed in an independent worker process using the exact frozen affinity matrix, fidelity grid, model parameters, founder seeds, selected seeds, neutral seeds, endpoint definitions, contrasts, and inferential rules already hashed in the prospective plan.

Because all stochastic streams are explicitly seed-addressed and no state is shared across root blocks, parallel scheduling does not alter the scientific computation. Results are sorted by `(block, p_index)` before analysis.
