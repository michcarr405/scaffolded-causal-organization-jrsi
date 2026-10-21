# T3 Execution Spec v1.0.0

Frozen before outcome generation.

- Interpret "30 entirely new paired selected-neutral root-seed blocks per training strength" as 30 unique root seeds for each of the five training strengths (150 selected-neutral pairs; 300 evolutionary runs).
- All root seeds are deterministic SHA256-derived uint32 values keyed by training strength and block index and are collision-checked against prior strength, identity, fidelity, T2, and within-T3 seeds.
- Canonical Model B parameters are inherited from the scaffold-strength confirmatory pipeline: N=80, n_olig=8, L=60, k=5, four local states, four segments, theta=1.2, p_inherit=0.975, mutation=0.001, 250 generations, native mapping [2,0,3,1].
- Selected and neutral members of each pair share the same generation-0 population. Selected reproduction uses fitness; neutral reproduction uses unit weights.
- Generation-250 populations are frozen before retrieval assay.
- Primary probe grid is beta/theta 0.000 through 3.000 in steps of 0.125. Secondary tail is 3.125 through 5.000 in steps of 0.125.
- Retrieval is assay-only: no reproduction, mutation, or further evolution.
- Primary empirical peak for each training strength is the q_probe value maximizing block-mean DeltaC = C_down_selected - C_down_neutral on the primary grid.
- A predicted peak counts as correct when absolute grid error <= 0.125.
- Primary criterion is at least 4 of 5 training strengths correct.
- The phrase "no systematic monotonic bias" is operationalized before outcomes as a two-sided Spearman test of signed peak error versus training strength with p >= 0.05. The errors and rho are reported regardless.
- Full-curve prediction uses the frozen v0.2 parameters with no refitting and is scored by pooled R2 and RMSE over the five training strengths and primary q grid.
