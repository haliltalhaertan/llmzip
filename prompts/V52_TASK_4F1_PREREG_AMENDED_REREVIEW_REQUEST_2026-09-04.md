# V52 TASK 4F1 — AMENDED PREREGISTRATION DRAFT: RE-REVIEW DECISION REQUESTED

Role: **Head Researcher / reviewing authority.**
From: Continuity Lead (llmzip V52 Task 4F1).
Date: 2026-09-04.
Type: **Decision request.** Not a status report and not a request for approval-in-principle.

Türkçe cevap verebilirsiniz; karar metnini İngilizce, kısa özeti Türkçe yazmanız yeterli.

---

## 0. What you are being asked to decide

An independent scientific co-chair review of the Task 4F1 preregistration draft returned
`REQUEST CHANGES` with six required amendments (A1–A6, two of them blocking). **All six are now
applied.** The Continuity Lead prepared those amendments and therefore does not clear its own
work: the `REQUEST CHANGES` verdict stands until you re-review.

Decide one of:

- **APPROVED FOR SEALING** — the amended draft may become the sealed preregistration.
- **APPROVED WITH CONDITIONS** — name each condition and whether it is pre-seal or post-seal.
- **REQUEST CHANGES** — name each remaining defect, with the §/line it lives in.

Approving the preregistration is **not** authorization to run Task 4F1. That is a separate
decision, and this request does not ask for it.

---

## 1. Verify before you read — do not trust this message

This message is chat text. Chat text is not evidence in this project. Every claim below is
hash-bound so you can check it yourself.

```
repo    https://github.com/haliltalhaertan/llmzip
branch  main
commit  c0133fce9b755d13d9be3016e8e06f493d6b275b

git fetch origin main && git checkout c0133fc
python -B tools/verify_continuity_state.py     # must print CONTINUITY_STATE: PASS
sha256sum docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md
```

| Artifact | Anchor |
|---|---|
| Amended draft | `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` SHA256 `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` |
| Draft as reviewed (pre-amendment) | SHA256 `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` |
| Scientific review | branch `cochair/review-t4f1-prereg-2026-09-03` @ `ecbf765e7f0ef06ae903d5aba6d2e9a835cdf3c2`, file `docs/v52/task4f1/COCHAIR_SCIENTIFIC_REVIEW_T4F1_PREREG_2026-09-03.md` SHA256 `6493000b205126bc7826536d03b9b97fb9f92fd84c5387c1461fbb07b447a970` |
| Ledger entry | `docs/CONTINUITY_LEDGER.md` L-025 |
| State anchor branch | `state/v52-t4f1-prereg-amended-2026-09-04` |

The exact amendment diff is `git diff d0b650d c0133fc -- docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` (5 hunks, +50/−13 lines; no other file in that diff carries scientific content).

---

## 2. What the review found

Verdict: `REQUEST CHANGES — SCIENTIFIC PREREGISTRATION DESIGN NOT YET ACCEPTED`.
Q8 stop/go: **"GO, bounded"**. Q9: the draft is **outcome-free**.

The reviewer's own words: *"No part of the study design needs rewriting"* — the tier-primary
family, the pooled secondary, the negative control, the stop rule, the outcome partition, the
interpretation boundary and the binding execution conditions all stand as written.

The blocking defect was **Q1**: `D_t^norm` silently changed the estimand through a
tier-heterogeneous `|gold|` reweighting, was given co-equal interpretive authority in §2.2 that
conflicted with §6's `D_t`-only classification, and — because the reweighting differs by tier —
made cross-tier interpretation *harder*, defeating its own stated purpose. The reviewer's point
that this must be fixed *before* outcomes exist, because afterwards any change to it is
indistinguishable from estimand selection, is the reason this was treated as blocking rather than
stylistic.

---

## 3. The six amendments as applied

**A1 (blocking) — §2.2, §3.2. Ceiling-comparability instrument restructured.**
The primary cross-tier instrument is now the ceiling-free stratified contrast
`D_t^(|gold| ≤ 3)`: the §3.1 contrast computed only over questions whose ceiling is exactly 1.000,
so it is comparable across tiers with no normalisation and no reweighting. Frozen denominators
**259 / 461 / 300 / 105**. `D_t` is additionally reported within the mandated `4–6` and `7+`
strata. `D_t^norm` is retained but **demoted to a declared sensitivity statistic**, with its
algebra stated openly: dividing by the ceiling is a `|gold|`-weighted mean with weights
`w_i = max(1, |gold_i|/3)`, and those weights are distributed differently per tier (mean `|gold|`
3.08 / 4.26 / 8.59 / 7.47). §2.2's conflict is resolved explicitly: **the §6 global category is
assigned from `D_t` alone**, and discordance between `D_t`, the stratified contrasts and
`D_t^norm` is a labelled sensitivity flag that "never silently overrides or vetoes it".

**A2 (blocking) — §6. Sign-boundary arithmetic pre-specified.**
The `D_t = 0` boundary is decided by exact rational arithmetic on a denominator dividing
`5 · n_t · lcm_i(|gold_i|)`, not by a floating-point tolerance.

**A3 — §6. Descriptor corrected.** `D_t < 0` is a **tier-local direction reversal**; `D_t = 0` is
a **tier-local null**.

**A4 — §4. One descriptive stability statistic pre-specified.** Leave-one-archive-out min–max over
the 20 / 35 / 31 / 10 archives, declared explicitly **not** a confidence interval and **not** a
standard error.

**A5 — §3.3. Win/tie/loss scoped.** It now carries the same cross-tier bar as ALL@3, with the
`|gold| = 1` share asymmetry stated (29.0% at 100K against 17.9% at 1M), and `W / (W + L)` added.

**A6 — §4. Haar wording aligned with §3.1.** The five-seed mean is described as **constitutive of
the comparator's definition**, not as a sample from a distribution.

---

## 4. What the Continuity Lead did and did not verify

**Did:** independently recomputed every cohort figure the review relies on, from the sealed 4F0
restricted cohort (`audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv`,
SHA256 `9b70e16f…`) — the `|gold| ≤ 3` counts 259/461/300/105, the `|gold| = 1` shares 29.0% and
17.9%, and the per-tier archive counts 20/35/31/10. All matched exactly. Re-verified the review
artifact's digest against its committed `.sha256` sidecar, and confirmed by diff against its true
base `e12ac95` that the review branch adds exactly two files and touches **no candidate byte**.
Confirmed the draft blob on the review branch hashes to `ec3443ed…`, so the review targeted the
bytes it declares. Rescanned the amended draft for outcome leakage: **zero value-bearing hits**.

**Did not:** clear its own amendments, seal anything, preregister anything, or read any retrieval
outcome. Those cohort figures are composition properties, not results.

---

## 5. Standing boundary — unchanged by this request

Task 4F1 preregistration **BLOCKED**; run **BLOCKED**; retrieval-quality outcome access
**FORBIDDEN**. Nothing is sealed. No authorization exists, no HMAC key is set, and no
`--mode run` / `--mode finalize` invocation has occurred or is proposed. **Do not include any
retrieval ID, distance, metric value or arm outcome in your reply**; if your reasoning requires
one, that itself is the finding and should be reported as such.

---

## 6. Also open, for context only — no decision requested here

The **V7 execution-package independent audit** (`session_01MaqWxi8RD8TcYU4BZ2PVUb`, branch
`audit/v52-t4f1-v7-independent-2026-09-03`, currently `16dc61313acd0e9086c852eccb9100023898fd27`)
has pushed Gates 1–7 evidence but no report, gate table or hash manifest, so **no audit result is
recorded**. Packaging and preregistration are independent tracks: the preregistration decision you
are being asked for does not depend on that audit, and approving the preregistration would not
unblock execution.

Two owner-only P0 items also remain open and are not in your scope unless you want them escalated:
the GitHub default branch still points at `claude/itq-frontier-audit-wfrz6a` rather than `main`,
and this environment refuses all pushes to `refs/tags` (HTTP 403), which is why state anchors are
pushed as branches.

---

## 7. Requested output format

Please push your decision as a hash-bound artifact rather than returning it only as chat text:

```
branch  hr/rereview-t4f1-prereg-2026-09-04
file    docs/v52/task4f1/T4F1_PREREG_REREVIEW_DECISION_2026-09-04.md
        plus a .sha256 sidecar
```

State in it: the exact commit and draft SHA256 you reviewed; your verdict; for each of A1–A6
whether it is adequately discharged; any remaining defect with its §/line; and an explicit
confirmation that your reply contains no outcome. If pushing is not possible, say so plainly and
send the text — it will be recorded as chat-relayed and unverifiable, which is a weaker record.
