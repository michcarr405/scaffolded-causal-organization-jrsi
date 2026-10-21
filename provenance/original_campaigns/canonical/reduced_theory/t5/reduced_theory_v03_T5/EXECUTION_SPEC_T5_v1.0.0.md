# T5 Execution Spec v1.0.0

Frozen with the prospective plan.

- Use canonical Model B code from the identity confirmatory freeze.
- Historical evolutionary scaffold mapping: [2,0,3,1], beta=4.0, theta=1.2.
- 30 new selected-neutral paired root blocks, 250 generations, p_inherit=0.975, mutation rate=0.001.
- Probe matrices are exactly those in `T5_PROBE_SCAFFOLDS.csv`; prepend the exact historical bias matrix as probe 0.
- 32 common-random-number chemical draws per block.
- Do not alter calibration predictions after outcomes are generated.
- Primary profile correlation uses direction means only, n=8.
- Exact profile permutation p-value enumerates all 8! label permutations.
- Equal-distance anisotropy permutation statistic is variance of direction means; permute the eight direction labels independently within each root block and recompute direction means and their variance. Use 50,000 Monte Carlo permutations with fixed seed 91273411.
