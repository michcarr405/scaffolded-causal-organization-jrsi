# Result freeze - catalytic-complex 22-point scaffold-strength confirmation v1.0.0

## Status
**STRONG PROSPECTIVE SUPPORT.**

This campaign prospectively confirms the 22-point catalytic scaffold-strength story using 30 new campaign-namespaced root-seed blocks and a grid frozen before production outcomes.

## Frozen grid
`s = {0, .25, .5, .75, 1, 1.25, 1.5, 1.666667, 2, 2.25, 2.5, 2.75, 3, 3.333333, 3.5, 3.75, 4, 4.25, 4.5, 5, 6, 8}`.

## Founder-cost family
Both preregistered founder-cost contrasts passed.

- **F1 canonical cost, s=2 vs s=0:** mean `-0.113446`; 97.5% bootstrap CI `[-0.114071, -0.112819]`; 30/30 blocks negative; Holm-adjusted one-sided sign p=`1.86e-9`.
- **F2 integrated stronger-scaffold cost:** mean high-minus-low `-0.264509`; 97.5% bootstrap CI `[-0.265053, -0.263949]`; 30/30 negative; Holm-adjusted one-sided sign p=`1.86e-9`.

The prospectively generated 22-point ancestral-fitness curve declines strongly with scaffold strength. The exact curve shape is descriptive beyond the frozen contrasts.

## Selection-recovery family
All three preregistered recovery contrasts passed.

- **R1 canonical selected-neutral recovery at s=2:** mean `+0.055522`; 98.333% bootstrap CI `[0.047400, 0.063771]`; 30/30 positive; Holm-adjusted sign p=`2.79e-9`.
- **R2 selected recovery above ancestral baseline over the prespecified recovery band:** mean `+0.037738`; 98.333% CI `[0.037142, 0.038363]`; 30/30 positive; Holm-adjusted sign p=`2.79e-9`.
- **R3 integrated selection advantage over the same recovery band:** mean `+0.055211`; 98.333% CI `[0.053033, 0.057473]`; 30/30 positive; Holm-adjusted sign p=`2.79e-9`.

## Secondary prespecified shape contrast
- **S1 intermediate-strength concentration of selected recovery:** mean peak-band minus shoulder-band `+0.042970`; 95% bootstrap CI `[0.042411, 0.043554]`; 30/30 positive; one-sided sign p=`9.31e-10`.

S1 was prespecified but was not part of the promotion gate.

## Descriptive curve landmarks
At s=0, mean selected-minus-ancestor fitness is `-0.007166`; by s=0.75 it is `+0.001376`. It rises to approximately `+0.054` around s=3.5-4.0 and then declines to `+0.007834` at s=8. Neutral-minus-ancestor change is negative through most of the intermediate-strength regime and approaches zero at very high scaffold strength.

These pointwise values describe the prospectively generated curve. They are not separate multiplicity-adjusted hypothesis tests.

## Permitted manuscript-level statement
> In an independent prospective 22-point catalytic scaffold-strength campaign, stronger reaction-field scaffolding progressively reduced ancestral fitness, while selection generated compensatory recovery above the ancestral baseline over an intermediate scaffold-strength regime; matched neutral lineages did not show comparable recovery.

## Boundaries
- Do not call the recovery maximum a universal optimum.
- Do not infer a critical scaffold strength from the first positive plotted point.
- The full pointwise curve shape is prospectively generated but descriptive beyond the frozen curve-level contrasts.
- Persistent post-adaptation scaffold cost remains a separate post-freeze diagnostic from the original catalytic campaign and is not converted into a prospective result by this sweep.
