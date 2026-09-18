[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Coordinator review — numbers worker (interim)

Worker reports 101/101 numerical checks within tolerance; this is not exhaustive programme validation. Persisted audit JSONs and scripts were inspected. Coordinator independently aggregated the eight T3 archive outputs: 2217 queries, 18 scalar means, maximum absolute discrepancy versus published JSON: 2.13162820728e-14 percentage points.

Important disposition: the worker correctly identifies coordinator/t3_perltqa_kltn.py as a failed producer, but its recommendation to commit the actual producer overlooks a file already present: ablation_r2/perltqa/t3_ladder.py. DECISION_TESTS.md line 11 explicitly identifies it as the producer. That script writes the matching gate/const_dims/arms schema. The defect is the ambiguous retained failed script, NOT demonstrated absence of the actual producer. Do not upgrade this to fabrication or irreproducibility of T3 data.

The sigma mechanism correction stands: sym never divides by sigma. Numeric agreement does not validate a causal explanation or whole-project STOP. The RealTalk ladder was freshly reconstructed on only 2/10 archives; other archives were reaggregated from caches. T3 covers eight small archives, not all PerLTQA. Best-of-four BM25 remains seen-data selection. Two other worker verdicts remain outstanding.

Source snapshot checked: 821 original files, zero changed/missing at this checkpoint. No source fixes applied.
