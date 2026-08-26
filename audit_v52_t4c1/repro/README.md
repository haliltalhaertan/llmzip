# Independent reproduction scripts — V52 Task 4C1 audit

Run against the extracted `V52_T4C1_INDEPENDENT_AUDIT_PACKAGE.zip` (expects
`pkg/V52_T4C1_trial_results.csv` relative to CWD). Requires pandas, numpy, sklearn.

| Script | Purpose |
|---|---|
| `01_structural_integrity.py` | row count, balance, duplicate cells, NaN, seed replication |
| `02_independent_aggregation.py` | flat vs correctly-nested aggregation, all 7 methods, frontier |
| `03_question_level_wtl.py` | SIGN96/ITQ96/FLOAT96 win-tie-loss, gap concentration |
| `04_strata_and_seeds.py` | frozen strata breakdown, 5-seed values |
| `05_itq_orientation_probe.py` | synthetic ITQ orientation probe (AUDIT DIAGNOSTIC ONLY) |
| `06_centering_hubness_probe.py` | synthetic centering / length-heterogeneity probe (DIAGNOSTIC ONLY) |

Scripts 05 and 06 are synthetic plausibility probes used only to test whether the
reported SIGN>ITQ ordering is explicable by an orientation bug. They are **not**
methods, are **not** tuned, and no number from them enters any Task 4C1 claim.
