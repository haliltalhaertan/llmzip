# V52 TASK 4F1 — STATUS REPORT

To: Head Researcher / reviewing authority.
From: Continuity Lead (llmzip V52 Task 4F1).
Date: 2026-09-04.
Type: **Status report. No decision is requested.** If you want one, §6 lists the only two open asks.

Türkçe cevap verebilirsiniz.

---

## 1. Verify before you read

This is chat text. Chat text is not evidence in this project. Everything below is hash-bound.

```
repo    https://github.com/haliltalhaertan/llmzip
branch  main
commit  5f2c5b2fd7de299fab842fd82a761ed321e16d4f

git fetch origin main && git checkout 5f2c5b2
python -B tools/verify_continuity_state.py     # must print CONTINUITY_STATE: PASS
```

Note: the repository **default branch still points at `claude/itq-frontier-audit-wfrz6a`**, not `main`.
Fetch `main` by name; do not trust the default.

| Anchor | Value |
|---|---|
| Approved preregistration draft | `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` SHA256 `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` (14,688 bytes) |
| Your re-review decision | `hr/rereview-t4f1-prereg-2026-09-04` @ `19d9cbb`, file SHA256 `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f` |
| Scientific co-chair review | `cochair/review-t4f1-prereg-2026-09-03` @ `ecbf765`, file SHA256 `6493000b…` |
| Sealed 4F0 cohort | `audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv` SHA256 `9b70e16f…` |
| Ledger | `docs/CONTINUITY_LEDGER.md` L-025, L-026, L-027 |
| State anchor branches | `state/v52-t4f1-prereg-amended-2026-09-04`, `state/v52-t4f1-prereg-approved-2026-09-04` |

---

## 2. Where the project stands

Two tracks run independently. **The science track is at its first closure point. The execution track is not.**

| Item | State |
|---|---|
| Preregistration **design** | **APPROVED FOR SEALING** (your decision, 2026-09-04, bound to draft `5e618981` only) |
| Preregistration **seal** | **NOT APPLIED.** No seal artifact exists. |
| Task 4F1 preregistration | **BLOCKED** — approved is not sealed |
| Task 4F1 run | **BLOCKED** — no authorization exists, no HMAC key is set |
| Retrieval-quality outcome access | **FORBIDDEN** — nothing read, computed or inferred |
| V7 execution package | **PREPARED, NOT AUDITED** — audit still running |

---

## 3. What was verified since the last report — verification, not relay

Your decision artifact was fetched and checked rather than believed:

- Digest recomputed from the fetched blob; matches the committed `.sha256` sidecar exactly.
- The branch's merge base is `c0133fc` — the commit carrying the amended draft — so the review was
  performed on the bytes it was asked to review, not on the stale default branch.
- Diffed against that base, the branch adds **exactly two files** (decision + sidecar) and modifies
  nothing else. No candidate byte, no seal, no manifest, no draft byte was touched.
- The draft blob present on the decision branch hashes to `5e618981…`, and the 14,688-byte
  cross-check in the artifact matches an independent measurement.
- The A1–A6 discharge table was not accepted from its summary. Each cited mechanism was located in
  the approved bytes: exact-rational sign arithmetic with denominator dividing
  `5 · n_t · lcm_i(|gold_i|)` (lines 239–240); leave-one-archive-out min–max with its explicit
  not-a-CI / not-a-standard-error disclaimer (189–192); tier-local reversal and null descriptors
  (246); within-strata W/T/L with `W / (W + L)` (159).
- The decision artifact was read in full and contains **no retrieval-quality outcome**.

Recorded as L-027 at commit `5f2c5b2`. `tools/verify_continuity_state.py`: **PASS**.

---

## 4. Carried forward from your decision, so it is not lost between tracks

Your A2 implementation note — expressly not a defect in the preregistration — is now recorded as a
condition on the **execution/authorization gate**, not on the scientific draft:

> Before any run authorization, the outcome-analysis implementation must honour the exact-rational
> sign rule rather than classify the sign from a rounded or floating aggregate.

It is written into `ops/CURRENT_STATE.json` under the decision record and into L-027, so a later
session that never reads this chat still meets it.

---

## 5. Execution track — unchanged and unprejudged

The V7 independent audit (`audit/v52-t4f1-v7-independent-2026-09-03`, still at
`16dc61313acd0e9086c852eccb9100023898fd27`) has pushed Gates 1–7 evidence and scripts but **no
report, no gate table, no hash manifest**, so **no audit result is recorded** and none is assumed.
It has not advanced since the last report.

Your approval explicitly does not accept or prejudge it, and approving the preregistration does not
unblock execution. The two tracks stay separate: sealing the science does not shorten the packaging
track, and a passing package audit would not by itself authorize a run.

---

## 6. The only two open asks

1. **Sealing is authorized but not performed.** The Continuity Lead treats sealing as its own stage
   with its own preparation and ledger entry, binding draft `5e618981`, cohort anchor `9b70e16f`
   and decision anchor `8795abc7`. Say if you want it prepared now, deferred until the V7 audit
   reports, or shaped differently (e.g. additional anchors bound into the seal).
2. **Two owner-only P0 items are still open and cannot be fixed from this session:** the GitHub
   default branch still points at `claude/itq-frontier-audit-wfrz6a` rather than `main`, and this
   environment refuses every push to `refs/tags` (HTTP 403), which is why release points are pushed
   as `state/…` branches instead of tags. Both need repository-owner action.

---

## 7. Boundary declaration for this reporting period

CLI `--mode run` invocations: 0. `--mode finalize` invocations: 0. Valid production authorization
constructed: false. `V52_T4F1_AUTH_HMAC_KEY_HEX` set or inspected: false. Real BEAM retrieval
performed: false. Task 4F1 retrieval-quality outcome computed / read / reported: false / false /
false. Sealed payload, candidate, manifest, pinned corpus or historical audit namespace modified:
false. This report contains no retrieval-quality outcome.
