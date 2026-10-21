# Portability normalization

All original historical scripts are preserved unchanged under `provenance/original_campaigns/`. Public copies under `experiments/` replace only machine-specific absolute roots and output destinations with repository-relative paths or environment-variable overrides. Model algorithms, RNG logic, seeds, parameter grids, intervention definitions, statistics and frozen scientific outputs are unchanged.

Recovered Model B dense-22 production was already principally repository-relative; its public copy therefore requires no scientific-code edit. Recovered catalytic and original lattice runners had historical `/mnt/data/...` campaign roots, which were replaced only in the public copies.
