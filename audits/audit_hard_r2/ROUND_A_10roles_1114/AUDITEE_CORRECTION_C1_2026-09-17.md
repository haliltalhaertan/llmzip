# AUDITEE CORRECTION — the C1 "third defect" was mine, and the audit inherited it

**2026-09-17** · append-only · **no worker or coordinator file is modified**

`[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]`

This correction is written by the **auditee**, not by an auditor. It exists
because a false claim of mine entered this audit's own evidence chain and was
recorded there as `DEFECT-CONFIRMED`. Nothing in `10_governance_meta/` is
edited; a pointer notice sits beside that file so a reader of the evidence
reaches this page.

---

## 1. The false claim

I wrote, in git commit `9993f95` on branch
`findings/audit4-postcheck-2026-09-17`:

> "Two required conditions are absent as the audit says — and a third defect it
> does not name: the check is `any()` over code arms, so it passes if ANY arm
> clears the bar, which is a maximum over arms rather than a pre-specified
> one."

**That is wrong.** Existential quantification over arms is not a defect. It is
what the governing contract specifies, in two places:

```
top10_comparison_r1/coordinator/decision_tests.py:23
  C1 some arm <=48 B beats FAIR BM25 by >= +2.0 pp FR@3, CI excluding 0, on BOTH benchmarks

top10_comparison_r1/decision_r1/cost/REFEREE.md:178
  C1. Some code arm ≤48 B/doc beats fair BM25 on FR@3 by ≥ +2.0 pp with 95% CI excluding zero
      on BOTH RealTalk AND PerLTQA-corrected.
```

`REFEREE.md:180` then opens C2 with "**The same arm's** Hit@10 lower CI …",
which confirms the existential binds and is referred back to.

How I got it wrong: I read the abbreviated gate string at
`decision_tests.py:197` and did not read line 23 — fourteen lines above it, in
the same file, under the heading `PRESPECIFIED GATES`.

## 2. How it entered the audit

`audit_hard_r2/10_governance_meta/evidence.json`, check
`"C1 gate implementation matches description"`:

- `method`: `"git show decision_tests.py lines 190-191 + __main__ gates dict;`
  **`cross-read postcheck 9993f95 body`**`"`
- `result`: `"… `**`any() = max-over-arms not prespecified arm; postcheck`**
  **`confirms + names third defect`**`"`
- `verdict`: `"DEFECT-CONFIRMED (verdict FAIL unaffected: point estimates
  already fail)"`

The `method` field records the contamination path explicitly: the worker read
my commit body and adopted its reasoning. Neither the worker nor I read
`decision_tests.py:23`.

**Status of that clause: `RETRACTED / AUDITEE-INHERITED ERROR`.**

## 3. What is NOT retracted

Three things stand, and this correction must not be read as weakening them:

1. **The gate implementation is defective.** `decision_tests.py:190-191`
   computes `any(v["vs_strongest_bm25_fr3_pp"] >= 2.0 …)` — a point estimate
   only. The declared contract additionally requires a CI excluding zero and
   BOTH benchmarks. Both are absent. This was demonstrated independently by
   `01_metrics` (finding F1, with fixture `scripts/p1_fixtures.py` F4: a
   synthetic paired case with point `+2.78 pp` and CI `[-8.06, +13.63]` passes
   the code check and fails the documented check).
2. **The `DEFECT-CONFIRMED` verdict remains correct**, on those two grounds.
   Only its reasoning clause is retracted.
3. **The shipped `FAIL` is unaffected.** All six code-vs-strongest gaps are
   negative, so the point estimates already fail a necessary condition.

## 4. The correct residual question

The BATCH1 coordinator states it precisely and I adopt its wording:

> "An existential `any()` is not inherently a third defect; **the SAME eligible
> arm must satisfy every required dataset and interval condition.**
> Selection/multiplicity require a separately specified statistical treatment.
> Missing CI and second dataset are demonstrated; do not invent a ban on
> existential selection."

So the open question is one of **quantifier scope**, not of existential
selection: the contract requires
`∃ arm : (Δ ≥ 2.0 ∧ CI excludes 0 ∧ on both benchmarks)`, whereas an
implementation that evaluated each condition separately would admit
`(∃ arm : Δ ≥ 2.0) ∧ (∃ arm : CI excludes 0) ∧ …` — different arms satisfying
different conditions. The current code contains no conjunction at all, so this
is a specification requirement for any future implementation, not a third
observed defect.

Separately, and not part of this retraction: `01_metrics` F1 notes that
`strongest_bm25` is selected on **Hit@10** (`max(...hit10)`, ~line 160) while
the gate is on **FR@3**. Same winner on current data, so unobserved — that is
a real fourth observation, found by a worker, not by me.

## 5. Who caught it

The **BATCH1 coordinator** (`BATCH1_COORDINATOR_REVIEW.md`, "Corrections to
worker interpretations", item 2). I verified the refutation myself by reading
`decision_tests.py:23` and `REFEREE.md:178` before accepting it.

This makes the round internally inconsistent until now: `10_governance_meta`
recorded the clause as confirmed while the coordinator refuted it. Both files
are preserved unchanged; this page is the adjudication.

## 6. Lesson for the audit design, not for the numbers

An auditor read the auditee's commit message and adopted its reasoning without
re-deriving it from source. The `method` field is honest enough that the path
is traceable, which is why this was findable at all. Future rounds should
treat auditee commit bodies as **claims to test**, never as evidence — the same
rule the briefs already impose on prior audit reports.

---

## Propagation ledger

| where | text | status |
|---|---|---|
| `9993f95` commit body (branch `findings/audit4-postcheck-2026-09-17`) | "a third defect it does not name: the check is `any()` over code arms …" | **RETRACTED** — superseded on-branch |
| `audit_hard_r2/10_governance_meta/evidence.json`, C1 check, `result` | "`any() = max-over-arms not prespecified arm; postcheck confirms + names third defect`" | **RETRACTED clause**; file unmodified; verdict `DEFECT-CONFIRMED` stands on other grounds |
| `BATCH1_COORDINATOR_REVIEW.md` item 2 | the refutation | **UPHELD** |
| `decision_tests.py:190-191` missing CI and both-benchmarks | — | **STANDS** (demonstrated by `01_metrics` F1) |
| shipped `C1_gate_plus2pp_fr3 = false` | — | **UNAFFECTED** |
