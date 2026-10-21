# Confirmatory result freeze - catalytic-complex transmission-fidelity replication v1.0.0

## Status
Independent prospective replication. All scientific design files and executable code were SHA256-frozen before production outcomes. The earlier catalytic 18-point campaign remains historically relevant but its exact raw archive was unavailable; this campaign is new evidence, not a reconstruction.

## Design
- 30 new root-seed blocks.
- Exact 18-point fidelity grid: `0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975, 1.0`.
- 1080 evolutionary runs: selected and neutral at every block x fidelity.
- Same founder across all fidelities within a block.
- Fixed catalytic matrix seed 51073, scaffold strength s=2, population 48, 32 dimers/cell, 180 generations, mutation 0.01, selection coefficient 24, Michaelis K=1.

## Promotion result
**STRONG PROSPECTIVE REPLICATION SUPPORT.** All six frozen primary contrasts passed, and all HIGH-fidelity endpoint means were positive for both families.

### Relational organization: Delta R_pop
- R1 high minus low: `0.05564559` bits; 98.333% CI `[0.04091773, 0.06963733]`; 28/30 positive; Holm-adjusted one-sided sign p = `1.3e-06`.
- R2 very-high minus transition: `0.05514860` bits; CI `[0.02976665, 0.07996532]`; 25/30 positive; adjusted p = `0.000162`.
- R3 at p=0.975: `0.08894572` bits; CI `[0.06031464, 0.11605388]`; 26/30 positive; adjusted p = `5.95e-05`.

### Adaptive relational value: Delta V_rel
- V1 high minus low: `0.02641961` fitness units; 98.333% CI `[0.02316987, 0.02955325]`; 30/30 positive; adjusted p = `2.79e-09`.
- V2 very-high minus transition: `0.01293189`; CI `[0.00800689, 0.01771580]`; 27/30 positive; adjusted p = `4.22e-06`.
- V3 at p=0.975: `0.03428881`; CI `[0.02739109, 0.04088767]`; 30/30 positive; adjusted p = `2.79e-09`.

## Curve-level interpretation
The full 18-point curves support strong high-fidelity amplification. Delta R_pop is near zero or slightly negative through much of the low-to-intermediate region, becomes positive around p~0.8, and rises strongly at high fidelity, with a non-monotonic drop from p=0.975 to p=1. Delta V_rel rises more smoothly across fidelity and is strongest at the highest fidelities. These shapes do **not** justify a universal critical fidelity or strict monotonicity claim.

## Figure 4 use
- Panel D: Delta R_pop versus transmission fidelity p.
- Panel E: Delta V_rel versus transmission fidelity p.
Use full 18-point means with 95% root-block bootstrap intervals.

## Interpretation boundary
This campaign independently supports heredity-dependent amplification of selection-generated relational organization and its adaptive value in the catalytic realization. It does not establish scaffold endogenization, a universal phase transition, or universality across all inheritance architectures.
