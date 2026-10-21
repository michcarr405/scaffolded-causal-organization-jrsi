# Prospective Test T4 v1.0.0 — Finite-Distance Historical-Match Law

Status: FROZEN PLAN, design target; requires construction of additional scaffold identities before execution.

## Purpose
Test the Reduced Theory v0.2 prediction that the v0.1 local squared-distance law is the small-distance limit of a saturating historical-match function.

## Frozen shape parameter
lambda=326.128666514 squared-distance units.

## Primary normalized law
R(d)=[1-exp(-d/lambda)]/[1-exp(-64/lambda)].

## Design requirement
Construct equal-strength scaffold variants with prespecified squared distances from one historical scaffold, prioritizing distances below 64 and intermediate between the existing 64,96,128 classes (target examples: 16,32,48,80,112,144 if the scaffold parameterization permits them without changing total strength).

## Replication
30 entirely new paired selected-neutral root-seed blocks. Evolve only under the historical scaffold; cross-evaluate frozen generation-250 populations under every prespecified probe scaffold.

## Primary analysis
For each block, normalize DeltaH(d) by DeltaH(64). Compare class means against the frozen zero-parameter R(d). No refitting of lambda.

## Key discriminating prediction
At sufficiently small d, R(d) approaches d/64. At larger d, R(d) falls below d/64 because mismatch cost saturates.
