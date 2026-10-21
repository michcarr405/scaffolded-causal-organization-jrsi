# Technical execution note v1.0.0

The first production invocation was terminated by the execution environment timeout after 12/30 worker blocks had reported completion. The frozen production script writes scientific output tables and endpoint-state archives only after all 30 blocks complete; therefore that interrupted invocation produced no scientific result table or endpoint archive.

The campaign was then rerun from the beginning using the identical pre-outcome-frozen script, configuration, seed ledger, and scientific specification. No model parameter, strength, endpoint, seed identity, contrast, or analysis rule was changed. The second invocation completed all 30 blocks and 660 block-strength rows.

This is recorded as a technical rerun under unchanged frozen specifications, not a scientific amendment.
