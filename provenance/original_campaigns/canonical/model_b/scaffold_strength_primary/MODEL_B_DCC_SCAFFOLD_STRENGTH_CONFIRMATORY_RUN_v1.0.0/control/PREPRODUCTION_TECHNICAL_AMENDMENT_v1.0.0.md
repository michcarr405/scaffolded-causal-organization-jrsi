# Preproduction Technical Amendment v1.0.0

**Status:** frozen before any new confirmatory outcome exists.

The plan freezes `strength-propagation|<ratio_id>` as the ratio-specific, mode-paired evolutionary stochastic namespace but does not separately name the stochastic local-state observation stream needed during generations 1-249. To make execution scheduling-independent and prevent observation draws from shifting reproduction draws, the implementation deterministically splits that frozen namespace into two substreams:

- `strength-propagation|<ratio_id>|observation`
- `strength-propagation|<ratio_id>|reproduction`

Both include ratio identity and exclude mode. Selected and neutral therefore receive common random numbers within ratio, while different ratios receive distinct streams. This is an RNG bookkeeping clarification only: no model mechanism, parameter, seed block, endpoint, strength, estimator, contrast, or success criterion changes.

Generation 0 uses the separately frozen `strength-g0-observation` stream shared across all ratios within a block. Generation 250 confirmatory fitness uses the separately frozen `strength-endpoint-observation|<ratio_id>` stream. Checkpoint fitness at generations 25-225 is descriptive and uses the evolutionary observation substream.
