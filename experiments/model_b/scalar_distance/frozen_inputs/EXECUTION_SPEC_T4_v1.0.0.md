# T4 Execution Spec v1.0.0

Frozen before evolutionary outcomes.

- Historical evolutionary scaffold is canonical SCF0 mapping [2,0,3,1] at beta=4.0, theta=1.2.
- 30 entirely new selected-neutral paired root-seed blocks evolve for 250 generations under that historical scaffold using canonical Model B and p_inherit=0.975.
- Probe scaffolds are continuous equal-strength logit-bias fields. Each segment's effective centered scaffold vector retains exactly the historical per-segment norm; only its direction in the three-dimensional centered four-state logit subspace changes.
- Target total squared distances from the historical scaffold are 16, 32, 48, 64, 80, 112, and 144. Four deterministic orientations are used at each distance to reduce direction-specific artifacts. The historical scaffold at distance 0 is also assayed.
- Geometry and historical-kernel equivalence are validated and frozen in T4_DESIGN_VALIDATION.json before outcomes.
- Generation-250 selected and neutral populations are frozen before cross-evaluation. Cross-evaluation uses 32 common-random-number chemical draws shared across all probe scaffolds and both modes within each root block.
- For each probe scaffold: A_mode(d)=F_mode(history)-F_mode(probe), and DeltaH(d)=A_selected(d)-A_neutral(d).
- Within each root block, DeltaH is averaged across the four orientation variants at each distance. The primary normalized response is DeltaH(d)/DeltaH(64).
- The zero-parameter frozen prediction is R(d)=[1-exp(-d/lambda)]/[1-exp(-64/lambda)] with lambda=326.128666514. No refitting is permitted for primary scoring.
- Primary outputs are class-mean normalized response, paired-block bootstrap 95% confidence intervals, zero-parameter RMSE/R2, and comparison with the local d/64 law.
