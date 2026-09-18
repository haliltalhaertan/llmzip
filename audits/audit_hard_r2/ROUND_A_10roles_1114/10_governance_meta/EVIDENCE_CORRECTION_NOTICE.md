# NOTICE — one clause in `evidence.json` is retracted

**2026-09-17** · written by the **auditee**, not by this worker or a coordinator.

`evidence.json` in this directory is **unmodified** and stays that way. This
notice exists so a reader of it reaches the adjudication.

## Affected check

`evidence.json` → check `"C1 gate implementation matches description"`.

Its `result` field contains:

> `any() = max-over-arms not prespecified arm; postcheck confirms + names third defect`

**That clause is RETRACTED.** The governing contract specifies existential
quantification over arms, so `any()` is not a defect:

```
top10_comparison_r1/coordinator/decision_tests.py:23
  C1 some arm <=48 B beats FAIR BM25 by >= +2.0 pp FR@3, CI excluding 0, on BOTH benchmarks

top10_comparison_r1/decision_r1/cost/REFEREE.md:178
  C1. Some code arm ≤48 B/doc beats fair BM25 ...
```

The clause originated in the **auditee's** git commit `9993f95`, not in this
worker's own source reading — this check's own `method` field records the path:
`"cross-read postcheck 9993f95 body"`.

## What still stands in this check

- The `DEFECT-CONFIRMED` **verdict is correct**, on the two grounds the worker
  demonstrated independently: the implementation tests a point estimate only,
  while the declared contract additionally requires a CI excluding zero and
  BOTH benchmarks.
- `verdict FAIL unaffected: point estimates already fail` — unchanged.

Only the reasoning clause is withdrawn. **This is not a finding against this
worker's verdict.**

## Full adjudication

`../AUDITEE_CORRECTION_C1_2026-09-17.md` and `../AUDITEE_CORRECTION_C1.json`.

The refutation was made by the BATCH1 coordinator
(`../BATCH1_COORDINATOR_REVIEW.md`, "Corrections to worker interpretations",
item 2) and verified from source by the auditee before acceptance.
