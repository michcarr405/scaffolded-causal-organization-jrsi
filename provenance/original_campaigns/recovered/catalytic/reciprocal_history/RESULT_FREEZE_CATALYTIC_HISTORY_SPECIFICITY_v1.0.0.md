# Result Freeze - Catalytic-Complex Historical Specificity v1.0.0

## Classification
**INDEPENDENT PROSPECTIVE CONFIRMATION CAMPAIGN.** The plan, configuration, seed ledger, and production script were SHA256-frozen before any production outcomes were generated or inspected.

## Primary question
Do two distinct, equal-strength scaffold histories generate distinct inherited catalytic organization such that the selected-minus-neutral response preferentially matches the current scaffold to the evolutionary history?

## Frozen design
- Same catalytic-complex realization as the prior confirmatory work; catalytic matrix seed 51073.
- 30 entirely new root-seed blocks.
- Two zero-sum, unit-norm, orthogonal histories H1 and H2.
- Same founder within block for selected-H1, selected-H2, neutral-H1, and neutral-H2 branches.
- 180 generations; p=0.975; s=2.0; population 48; 32 dimers/cell; mutation 0.01; selection coefficient 24; Michaelis K=1.
- Frozen endpoints cross-evaluated under both H1 and H2 with no further evolution.

## Preregistered primary contrast
For history h, R_h(B)=F(S_h|B)-F(N_h|B).

H_fit = 0.5 * [(R_1(H1)-R_2(H1)) + (R_2(H2)-R_1(H2))].

Primary success required BOTH >=24/30 blocks with H_fit>0 and a two-sided 99% root-block bootstrap CI for the mean entirely above zero.

## Primary result
**PASSED.**

- mean H_fit = **0.0793963 fitness units**;
- **29/30** independent blocks positive;
- one-sided exact sign-test p = **2.8871e-08**;
- two-sided 99% bootstrap CI = **[0.0658104, 0.0918010]**.

The only non-positive block was block 3 (H_fit=-0.005375).

## Cross-evaluation matrix
Mean selected-minus-neutral fitness responses, rows = evolutionary history, columns = current probe:

| | current H1 | current H2 |
|---|---:|---:|
| history H1 | +0.052189 | +0.011288 |
| history H2 | -0.027970 | +0.089921 |

The reciprocal matching diagonal is therefore strongly favored.

## Secondary frozen outcomes
- Selected-only reciprocal match contrast: mean **0.088661**, positive in **30/30** blocks.
- Neutral reciprocal contrast: mean **0.009265**, positive in **16/30** blocks, consistent with no systematic matching signal from neutral drift.
- Relational-value historical specificity H_Vrel: mean **0.024586**, positive in **27/30** blocks.
- Algebraic identity H_fit = H_selected - H_neutral held to machine precision (maximum absolute error 0).

## Interpretation
The catalytic-complex realization now prospectively confirms historical specificity. Under the same current scaffold, lineages evolved under different scaffold histories show different selected-minus-neutral responses, and the reciprocal response preferentially matches current scaffold to evolutionary history.

This fills the previously untested catalytic history-specificity cell in the cross-realization evidence matrix. The result does not imply scaffold endogenization or autonomous scaffold reconstruction.
