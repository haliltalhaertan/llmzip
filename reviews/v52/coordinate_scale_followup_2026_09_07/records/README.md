# Persisted coordinate-scale record validation

Scope: bounded post-outcome follow-up to review `4769c2a3a6e5770a3a9e9dc77a0029b4792cc34f`, not a cold-start independent audit or stage acceptance. The verifier imports Python standard-library modules only. It never imports the research runners, reads raw corpora, reranks, computes retrieval from gold labels, or touches Task 4F1.

## Result

Both existing metric panels pass the implemented checks: LoCoMo 92,100 rows (1,535 questions x 10 seeds x 6 arms), LongMemEval 28,200 rows (470 x 10 x 6). Every persisted score and native-control scalar is finite and within [0,1]. Every observed question has exactly one record in each seed/arm cell. Native and scaled-native metric values agree exactly per question/seed, and native values repeat exactly across seeds and match each row's supplied native scalar. Frozen native aggregate and published summary arm means match recomputation within absolute 1e-12. The repeated tie-identity strings agree within each question. All numeric summary values, including archive diagnostics, are finite.

Nine in-memory negative controls per benchmark are rejected: NaN score; above-one score; below-zero score; missing row; duplicate replacing one cell; paired native tamper; supplied native scalar mismatch; NaN diagnostic; cancelling paired scaled-native changes that preserve the aggregate sum. Eighteen total. Production result bytes remain unchanged.

`RESULT.json` records hashes and sizes of all four source files, question-set digests, counts, recomputed means, negative-control rejection gates, and the verifier's own SHA256. Its output is deterministic for identical input/script bytes. The frozen native constants are the previously declared values, not new estimates selected from these rows.

## Reproduction

From repository root, with a Python standard-library runtime:

```text
python -B reviews/v52/coordinate_scale_followup_2026_09_07/records/validate_records.py --output reviews/v52/coordinate_scale_followup_2026_09_07/records/RESULT.json
```

Executed here using `C:\Users\MDP\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; stdout: `PASS: both persisted panels; 18 negative controls rejected`.

## Exact limitations

- This checks internal consistency of persisted metric rows, not correct retrieval IDs, gold joins, ties, ranking, per-bit codes, or corpus identity. Equal metrics do not prove bit-identical representations or identical retrieved items.
- The question universe is inferred from the persisted rows and checked against declared counts; there is no independent question-ID manifest join. The digest records the observed set rather than certifying its external identity.
- JSON numeric finiteness does not constitute a full summary schema, diagnostic-value, or scientific interpretation validation. Ratios are not required to lie in [0,1], as they need not mathematically do so. Primary ratio aggregation, bootstrap obligations and interpretive rules remain separate unresolved review items.
- Source hashes provide an exact snapshot, not evidence of pre-execution sealing or runtime closure. The existing runner/aggregator is neither modified nor certified by these tests.
- Valid record panels narrow R4: no demonstrated malformed-record examples occur in the persisted panels under these checks. They do not close the original aggregator hardening defect or the full research audit.
