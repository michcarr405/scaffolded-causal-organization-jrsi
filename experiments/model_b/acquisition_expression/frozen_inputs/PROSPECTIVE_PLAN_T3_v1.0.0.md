# Prospective Test T3 v1.0.0 — Finite-Amplitude Retrieval-Peak Law

Status: FROZEN PLAN, not yet executed.

## Purpose
Test the post-T1 Reduced Theory v0.2 prediction that the probe strength maximizing causal expression shifts with the magnitude of organization acquired during evolution.

## Frozen theory parameters
c=-0.149665377842
gamma=0.699255786271
alpha=0.44090926477
K=0.073893078378

## New training strengths
1.75, 2.00, 2.75, 3.25, 3.75 beta/theta. These were not used in the v0.2 fit.

## Evolutionary replication
30 entirely new paired selected-neutral root-seed blocks per training strength; canonical Model B settings otherwise unchanged.

## Retrieval assay
Freeze generation-250 populations. No additional evolution during assay. Probe each population on beta/theta = 0.00 to 3.00 in increments of 0.125, extending to 5.0 only as a secondary tail check.

## Primary prediction
For each training strength s,
q*_pred(s)=(alpha*s/2-c)/gamma.
Predicted values:
- s=1.75: q*=0.7658
- s=2.00: q*=0.8446
- s=2.75: q*=1.0810
- s=3.25: q*=1.2387
- s=3.75: q*=1.3963

Primary success criterion: the observed block-aggregated grid peak is within one probe-grid interval (0.125) of q*_pred for at least 4/5 training strengths, and the signed peak error shows no systematic monotonic bias.

## Secondary full-curve prediction
Delta C_pred(q,s)=K*JSD[Bern(sigmoid(c+gamma*q-alpha*s)) || Bern(sigmoid(c+gamma*q))].
Report pooled R2/RMSE with no parameter refitting.

## Exclusions
Do not use training strengths at or beyond the known collapse boundary for the primary test. No parameter updates are permitted before primary scoring.
