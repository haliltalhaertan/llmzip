# V52 — Matched Random-Partition Null Stage: Auditability Addendum

**Date:** 2026-09-05
**Track:** research (mechanism line). Canonical `main` unchanged by this document.
**Status:** `[AUDITABILITY FINDING — ADDITIVE. NO NEW EXPERIMENT. NO OUTCOME ACCESS.]`
**Applies to:** the matched random-partition null stage sealed at commit
`410bcf59e29c64096bfb988d6d95e89658f50f6e`
(`research/v52/V52_MATCHED_RANDOM_PARTITION_NULL_PROVENANCE_MANIFEST_2026-09-04.json`).

This addendum is **additive**. It rewrites nothing, retracts no number, and
supersedes no earlier artifact. It changes only how one already-recorded open
item must be stated from here on.

---

## 1. Why this document exists

Three consecutive records — the audit dispatch, the boundary-localization
auditor's carried-forward list, and the post-audit interpretation addendum —
have carried the same open item forward in the same words:

> the earlier matched random-partition null control at `410bcf5` carries an
> audit dispatch record but **no auditor branch exists** for it, so its
> LongMemEval position result has never been independently audited.

That wording says a person did not do the work. This addendum establishes that
the wording was **too weak**. The correct statement is stronger and structural,
and it was never checked before now.

## 2. What was done

No experiment was run. No corpus was read. Nothing was recomputed that depends
on retrieval outcomes. The work was confined to committed repository bytes:

1. Searched **all 57 remote branches** for a per-question output belonging to
   this stage. Result: **none exists.**
2. Confirmed the boundary-localization stage — the one that *was* audited —
   does commit per-question output
   (`locomo_boundary_per_question.csv.gz`, `longmemeval_boundary_per_question.csv.gz`).
3. Wrote `research/v52/audit_support/verify_matched_null_from_bytes.py`, which
   checks every layer of this stage that *is* checkable from bytes, and
   `research/v52/audit_support/test_verify_matched_null_from_bytes.py`, which
   proves each of those checks can fail.

## 3. The finding

**A cold-start independent audit of this stage's declared retrieval numbers is
not possible from repository bytes at all.**

The boundary-localization audit was possible because that stage committed
question-level outcomes; the auditor reconstructed the aggregates from them
(`scripts/reconstruct_from_per_question.py`). This stage committed **seed-level
aggregates only**. Its per-seed `spectral_R3` and `random_R3` therefore enter
the chain as **declarations**, and no party — independent or otherwise — can
reconstruct them without re-running the stage against the pinned corpora
(LoCoMo `79fa87e9…`, LongMemEval `d6f21ea9…`, 277,383,467 bytes).

This is the same shape as the already-recorded Full-Haar denominator gap: not a
missing reviewer, a missing artifact.

## 4. What *is* verified, and by whom

`verify_matched_null_from_bytes.py` reports **PASS on all five checkable layers
for both benchmarks**:

| Check | Covers | LoCoMo | LongMemEval |
|---|---|---|---|
| A | S32/T64 regenerated from the declared rule `sort(default_rng(seed).permutation(96)[:32])`; disjoint; union `0..95`; sizes 32/64 | PASS | PASS |
| B | per-seed `rho = (native − arm)/(native − full_haar)` and `Delta = rho_rand − rho_spec` | PASS | PASS |
| C | headline means, `L_full`, and every dispersion field (mean, sample sd, population sd, min, max) | PASS | PASS |
| D | seed CSV against summary JSON, value by value | PASS | PASS |
| E | provenance manifest against both summaries, including the regime label | PASS | PASS |

Tolerance `1e-12` throughout. Ten seeds per benchmark (`57001..57010`).

The verifier is falsifiable: **32/32 negative controls caught their mutation**,
including a trivial-leading-32 partition substitution, swapped `rho` arms, a
shifted denominator, sample sd replaced by population sd, a dropped seed, and a
manifest regime relabelled to `[NO EFFECT]`. Baseline runs on unmutated bytes
report clean, so the controls are not passing by accident.

**This is not an audit.** It was performed by the writer, not an independent
party, and by construction it cannot detect an error upstream of the seed-level
numbers — precisely the layer that is missing. A reader must not upgrade it.

## 5. Required wording from here on

Any citation of this stage's results must carry both of the following, and they
travel together:

> `[MATCHED-NULL STAGE — SEED-LEVEL DECLARATIONS, NOT INDEPENDENTLY RECONSTRUCTIBLE]`
> `[INTERNAL CONSISTENCY VERIFIED FROM BYTES; UPSTREAM RETRIEVAL LAYER UNVERIFIED]`

The earlier formulation — "no auditor branch exists" — is superseded as
**understated**, not as wrong. It remains true; it is simply not the binding
constraint.

## 6. What this does and does not change

**Does not change:**

- The boundary-localization stage's independently audited status is untouched.
  That stage reproduces matched random partitions on both benchmarks with fresh
  seeds (`58001…`) and commits the per-question output an auditor needs.
- `S_LoCoMo={32}`, `S_LongMemEval={32,48}`, `S_common={32}` and the paired
  labels `[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]` /
  `[BOUNDARY-SET HETEROGENEITY PRESENT]` are unaffected.
- No number in the `410bcf5` manifest is retracted. Nothing suggests any of them
  is wrong; they are simply not reconstructible.

**Does change:**

- The cross-benchmark claim `[CROSS-BENCHMARK SPECTRAL POSITION CAUSAL LEAD]`
  rests, on its LongMemEval side, on an unreconstructible layer. Where the
  audited boundary-localization stage covers the same ground with fresh seeds,
  **cite that stage instead** — it is the one an auditor can check.
- The remedy is now known and costed: commit per-question output, or re-run.
  Both require authorization; neither is proposed here.

## 7. Standing constraints observed

Task 4F1 untouched: SEALED (V3 `e906c6d2…`) / RUN BLOCKED / NO AUTHORIZATION /
OUTCOME ACCESS FORBIDDEN. No 4F1 payload, candidate, manifest, or audit
namespace was read or modified. No new experiment was designed, preregistered,
or triggered. No finer boundary scan, adaptive localization, or knee search was
performed or prepared.
