# Prospective Test T1 v1.0.0 — Frozen-population probe-strength retrieval curve

Status: DESIGN FROZEN BEFORE T1 ASSAY
Date: 2026-09-13
Theory source: REDUCED_THEORY_SCAFFOLDED_CAUSAL_ORGANIZATION_v0.1

## Question
Does the causal expression of a fixed evolved organization depend on current scaffold strength according to the susceptibility curve predicted before this assay?

## Frozen source populations
Use generation-250 frozen states from the independent 7-point scaffold-strength confirmatory campaign MODEL_B_DCC_SCAFFOLD_STRENGTH_CONFIRMATORY_RUN_v1.0.0. No further evolution is permitted. Use all 30 root-seed blocks and both SELECTED and NEUTRAL states.

Primary training-strength set (pre-collapse): beta/theta = {1.5, 2.5, 3.0, 3.5, 4.0}.
Secondary descriptive conditions: beta/theta = {0.0, 4.5}.

## Probe grid
Theta remains fixed at 1.2. Assay each identical frozen population under the native scaffold mapping at probe beta/theta q in:

{0.00, 0.25, 0.50, ..., 5.00}

so beta_probe = 1.2 q.

No reproduction, mutation, selection, or state updating occurs during probe assays.

## Outcome
For every block, training strength, mode, and probe q, compute deterministic C_down using the already-frozen primary relational-erasure estimator.

Primary evolutionary quantity:
DeltaC(train,q) = C_down_selected(train,q) - C_down_neutral(train,q).

For each training condition, normalize the condition-level mean retrieval curve to q0 = 2.5:
R(train,q) = mean_block DeltaC(train,q) / mean_block DeltaC(train,2.5).

Blockwise normalized ratios will also be retained as a secondary uncertainty diagnostic.

## Frozen theory prediction (no refitting in primary test)
Use the v0.1 normalized logistic-susceptibility parameters estimated before T1 from the earlier train-vs-fixed-probe analysis:

c = -0.24648168999601677
gamma = 0.5700229862715289
q0 = 2.5

F(q) = sigmoid(c + gamma q) [1 - sigmoid(c + gamma q)]
R_pred(q) = F(q) / F(q0).

This prediction has zero free parameters in T1.

The continuous predicted maximum occurs at q* = -c/gamma ~= 0.4324; on the prespecified 0.25 grid the predicted maximum is q = 0.50.

## Primary evaluations
1. Compare all normalized primary-condition curves to the fixed zero-parameter prediction R_pred(q), reporting pooled R^2 and RMSE across the 5 x 21 condition-probe points.
2. Report R^2 and RMSE separately for each of the five primary training strengths.
3. Average the five normalized primary curves at each q and report the empirical peak q. The directional prediction is an intermediate/weak probe maximum near q=0.5, not at the training strengths.
4. Report how well normalized curves collapse onto one common curve (between-training SD at each q).

No pass/fail threshold is introduced after inspecting T1. Interpretation will use effect size and prediction error transparently.

## Secondary analyses
- Free two-parameter susceptibility refit to T1, clearly labeled post-confirmatory diagnostic.
- Linear and quadratic probe-response comparisons.
- Descriptive retrieval curves for q_train=0 and 4.5.
- Selected and neutral curves separately.

## Interpretation boundary
A successful T1 supports acquisition-expression separation and context-dependent causal expression of frozen inherited organization. It does not establish autonomous memory, scaffold endogenization, or formal PhiID causal emergence.
