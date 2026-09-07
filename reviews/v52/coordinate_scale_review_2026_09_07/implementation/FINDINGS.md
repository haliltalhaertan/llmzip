# Coordinate-scale implementation review

Scope: bounded team subtask at repository HEAD `591e5d0`; source review, explicit seal Git-blob verification, existing synthetic checks and additional synthetic aggregate counterexamples. Not a cold-start certification, not a raw-corpus/retrieval rerun. Candidate code/seal/outputs unchanged. Only this review namespace written after parent integration request.

Runtime used: bundled Python 3.12.14, NumPy 2.3.5, pandas 3.0.1. This is NOT the workflow environment (Python 3.13, pandas 2.2.3, NumPy 2.3.5, SciPy 1.17.0, sklearn 1.8.0). The observed counterexamples concern deterministic validation logic, not numerical reproduction of research results.

## Positive checks

- All 10 explicit `git_blob_sha1` entries in the coordinate-scale pre-run seal match `git rev-parse HEAD:<path>`.
- Existing tests `test_coordinate_scale_pure_functions.py` and `test_longmemeval_coordinate_scale_shard.py` both exit 0 / ALL PASS in the above environment (29 and 41 named checks respectively).
- Source data-flow reviewed: LoCoMo common representation fitting uses archive texts (common module lines 190-219); queries use transform and archive-derived mean. LME base lines 122-148 uses archive payload fit, transforms query separately, constructs gold indices for scoring. Coordinate scaling uses only `C.std(axis=0)`, never query/gold. No query-fitting leak observed in inspected path; this is not an exhaustive dynamic leakage proof.
- LME shard code lines 320-326 verifies dataset and adapter-v1/v2 SHA256 before execution. The v2 adapter dynamically imports v1, already covered by this runtime verification.

## I1 — LoCoMo recursive executable closure absent from 10-file seal gate

`research/v52/locomo_spectral_band_haar_causal.py:13,34-39` dynamically imports `locomo_sign_mechanism_replication.py`. That transitive module performs archive construction, TF-IDF/SVD fitting, query transformation, and tie/scoring helpers. It is not among the seal's ten entries and the workflow's enumeration (`.github/workflows/v52-locomo-coordinate-scale.yml:51`) does not verify it. `load_common` executes without hash validation. The common module verifies downloaded corpus/audit bytes, not its own implementation bytes.

This is a reproducible closure omission, not evidence that the file changed or results were corrupted. Git history inspection finds only its original `adf6c45` addition. The checkout commit still identifies its bytes retrospectively; audit should bind and compare this dependency against the actual run commit. Do not claim the runtime seal gate covers the complete executable closure. Future packages should use a complete closure manifest rather than edit the existing seal.

## I2 — LME aggregate accepts inconsistent shard metric/control data

`research/v52/longmemeval_coordinate_scale_shard.py:203-241` validates a mean over `z['native']` against the anchor, but primary statistics come from independently provided row metrics. It compares NATIVE and SCALED_NATIVE only at the final grand-mean level. It does not enforce finite [0,1] scores or per-question/seed identity with native scalar, and uses `> TOL` checks without rejecting NaN control maxima.

Additional purely synthetic tests reproduced all four cases accepted without exception:

| Counterexample | Accepted behavior |
|---|---|
| First result `max_dot=NaN` | Aggregate invariance gate passes |
| SCALED_FULLHAAR scores of 10.0 for one of four questions | `frac_full=6.687500000000002` returned |
| SCALED_NATIVE +0.1 on question 0 and -0.1 on question 1 | Equal grand mean hides pairwise identity violations |
| All NATIVE and SCALED_NATIVE rows set to 0.8 while native scalar remains frozen 0.6 | Anchor control reports 0.6 but primary NATIVE=0.8; frac_full changes 0.75 to 0.5 |

Scoring functions in the actual producer should naturally produce bounded scores and paired native equality, so these are aggregate fail-closed shortcomings, not proof of present-output failure. Existing synthetic test only changes one scaled-native row, which the grand-mean test catches; compensating changes are untested. An independent acceptance check should reject these conditions on published rows/control summaries, without altering sealed code. Future aggregate implementations should validate finite fields, score bounds, per-question/seed equality and native scalar-row agreement before statistics.

## Other interpretation/provenance limits

- `frac` handles exactly zero denominator only; negative or nearly-zero losses still produce a band. This is the already-disclosed reason the LoCoMo block fraction cannot carry an interpretable loss-recovery claim. No proposal to select a new threshold after outcomes.
- Workflow push paths trigger on changes, not exclusively creation, of the trigger file. Comments implying a creation-only route are stronger than actual GitHub workflow semantics. Do not infer a rerun occurred; actual run history must establish that separately.
- Seal explicitly says authorization was chat-relayed and not a separate hash-bound user artifact. The seal records that provenance honestly; this review cannot certify the external conversation nor infer unauthorized execution from the absence of a separate artifact.

No Task 4F1 import/run, raw corpus acquisition, or new scientific experiment occurred.
