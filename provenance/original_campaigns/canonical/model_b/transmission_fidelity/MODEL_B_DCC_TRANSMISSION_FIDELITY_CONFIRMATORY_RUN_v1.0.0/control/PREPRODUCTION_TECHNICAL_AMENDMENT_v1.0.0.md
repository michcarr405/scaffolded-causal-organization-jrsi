# Preproduction Technical Amendment v1.0.0

**Date:** 2026-09-05  
**Timing:** before validation completion and before any confirmatory production outcome existed.

The frozen manifest specifies a fidelity-specific, mode-paired `fidelity-propagation|Pxxxx` RNG namespace. Production implements two deterministic purpose substreams beneath that namespace:

- `fidelity-propagation|Pxxxx|observation`
- `fidelity-propagation|Pxxxx|reproduction`

This purpose separation prevents changes in observation draw counts from shifting reproduction randomness. Selected and neutral trajectories at a given fidelity use identical keyed observation streams and identical keyed reproduction streams; only the parent-selection probabilities differ. Fidelity conditions use distinct keyed streams. The underlying stochastic law, seeds, fidelity grid, estimators, endpoints, hypotheses, and inferential rules are unchanged.

This amendment is technical and prospective. It does not authorize outcome inspection.
