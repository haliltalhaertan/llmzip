# V52 — Light Preregistration: the 12-byte baseline comparison

**Date:** 2026-09-09
**Prepared by:** Continuity Lead (prepares only; does not seal, does not self-approve)
**Binding when** committed with an agreeing `.sha256` sidecar and covered by a
pre-run seal on Head Researcher authorization — see the commit, the sidecar and the
seal for status.
**Repository path:** `docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md`

---

## 1. The question

At a **fixed 96-bit (12-byte) budget**, is SIGN96 competitive with standard
quantisation methods on evidence retrieval over this programme's frozen panels?

This is a **baseline characterisation**, not a test of the programme's mechanism
hypothesis. The ledger records that no such comparison has ever been made:
`RaBitQ` appears **once** across the whole ledger (L-046, a literature prediction
only); `product quantization` / `PQ` appears **zero** times.

## 2. Why it is light

No new corpus. No new gold. No new encoder. Every arm consumes the **same frozen
96-dimensional centered representation** already used by the mechanism stage:

```
Z  = hstack([LSA32(word-TFIDF), word-TFIDF, char-TFIDF])
Y  = normalize(TruncatedSVD(96).fit_transform(Z))
C  = Y - mean(Y)          # archive-fitted, archive-only
```

What this preregistration must bind is therefore only: **arms, seeds, metric,
statistics, decision bands.**

## 3. What this does NOT answer — pre-emption guard

This stage measures **methods at a matched budget on the existing panels**. It does
**not** measure how the native-versus-Haar contrast behaves as archive scale grows.
That question is the sealed Task 4F1 primary estimand (tier-wise `D_t` over
100K/500K/1M/10M) and is **not** approached here, by any corpus or proxy. No
distractor-inflated archive is constructed under this preregistration.

## 4. Arms

All arms are scored on the identical `C` / `qC` pair per question archive. All
fitting (rotations, codebooks, centroids) is **archive-only**: no query, no gold, no
answer, no question metadata enters any fit.

| # | arm | budget | notes |
|---|---|---|---|
| 1 | `SIGN96` | 96 bit | reference; `sign(C)` |
| 2 | `ITQ96` | 96 bit | learned within-96 rotation; frozen value exists |
| 3 | `SIMHASH96` | 96 bit | full-Haar `sign(RC)`; the correct name for this arm |
| 4 | `RABITQ96` | 96 bit | **primary comparator** |
| 5 | `EXT_RABITQ96` | 96 bit | extended RaBitQ at matched bits |
| 6 | `OPQ_PQ96` | 96 bit | OPQ rotation + PQ, m=12 sub-quantizers × 8 bit |
| 7 | `TRUNC12_INT8` | 96 bit | top-12 SVD coordinates at int8 — the trivially simple 12-byte baseline |
| 8 | `FLOAT96_CENTERED` | 384 byte | uncompressed ceiling, reference only, **not** at matched budget |
| 9 | `RANDOM96` | 96 bit | uniform random codes; floor |

Arm 7 stands in for the MRL/int8 baseline: this programme has no Matryoshka-trained
encoder, and SVD coordinates are already variance-ordered, so top-12-at-int8 is the
faithful analogue in this representation.

Query-side handling is **declared per arm** and is part of the preregistration:
arms 1–3 binarise both sides; arms 4–6 use each method's own published asymmetric
estimator; arm 7 keeps the query in float. Asymmetric scoring is *not* introduced as
an improvement to SIGN96 here — that would change arm 1 and is out of scope.

## 5. Seeds

- Rotation seeds where applicable: **43001–43005** (existing convention).
- ITQ seeds: **101, 202, 303, 404, 505** (existing convention).
- Codebook/centroid training seeds for arms 5–7: five seeds, declared as source
  literals in the runner before any run.
- Nuisance trials and tie-break priorities: existing frozen scheme; **one shared
  priority per (question, trial) used by every arm.**

## 6. Metric

- **Primary:** Fractional Evidence Recall@3 — chosen for comparability with every
  frozen number in the programme, not because k=3 is the operating point.
- **Secondary:** Recall@{10, 50, 100} and the full recall(k) curve.
- **Reported alongside:** distinct-code fraction, duplicate-code fraction, and
  query-exact-code-match fraction per arm. `V52_T4C2_collision_diagnostics.csv`
  already shows SIGN96 at `0.0045` and ITQ96 at `0.1059`; this stage extends that
  diagnostic to every arm.
- **LoCoMo dual reporting** per `f9951c0` Decision 1: corrected (1535) and raw
  (1540) figures always together, with their divergence.

## 7. Statistics

- Paired bootstrap over questions, 10,000 replicates, 95% CI.
- LoCoMo: conversation-level clustering (ten clusters).
  LongMemEval: question-level only — the cluster bootstrap is **ill-posed** there
  (one connected component, 470/470), per `docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md`.
- Stochastic arms report **mean ± sd over seeds**, never a single draw.
- **One primary contrast** is declared: `SIGN96 − RABITQ96`. Every other arm
  comparison is descriptive.
- Holm–Bonferroni across the descriptive arm set.

## 8. Mandatory positive controls — the run aborts if any fails

Each control names **which quantity it targets** and its tolerance. Two distinct
quantities exist in the frozen record and they are not always equal: `frozen_native`
(the panel constant) and `native_reproduction` (the same figure rebuilt from the
persisted per-question rows). Every control below targets **`frozen_native`**.

```
SIGN96      LongMemEval Fractional R@3 == 0.5419751773049646   (±1e-9)
SIGN96      LoCoMo-1535 Fractional R@3 == 0.23654714666441054  (±1e-9)
SIMHASH96   LongMemEval mean over 5 seeds == 0.38271667        (±1e-6)
ITQ96       LongMemEval Fractional R@3 == 0.3761411347517731   (±1e-9)
```

**Why the tolerance is not zero.** The coordinate-scale stage records
`absolute_reproduction_error` for exactly this reason:
`research/v52/locomo_scale_outputs/locomo_scale_summary.json` reports **0.0** —
LoCoMo reproduces bit-exactly — while
`research/v52/longmemeval_scale_outputs/longmemeval_scale_summary.json` reports
**1.1102230246251565e-16**, one ULP, because `native_reproduction` there is
`0.5419751773049645` against a `frozen_native` of `0.5419751773049646`. A
bit-exact assertion on the LongMemEval control would therefore fire on a correct
run. The declared `±1e-9` clears that gap by roughly seven orders of magnitude and
is not tightened.

**The LoCoMo raw cohort is reported, not gated.** §6 requires the corrected (1535)
and raw (1540) figures to appear together. Only the corrected cohort has a frozen
constant; **no frozen raw-cohort value exists**, so no positive control can be
written for it. The raw figure is therefore computed and reported under §6 but is
**not** an abort gate, and this asymmetry is stated here so that a reader does not
expect a gate that cannot exist. If a raw-cohort constant is ever frozen, a matching
control is added by amendment.

If any assertion fails the harness cannot reproduce the frozen panel; the run stops
and **no new number is reported**. Verdict `BLOCKED`.

## 9. Decision bands — sealed before any outcome is observed

Let `Δ = SIGN96 − RABITQ96` in percentage points, on the primary metric.

Each benchmark is first classified on its own, from `Δ` and its 95% CI:

| per-benchmark state | condition |
|---|---|
| `FAVOURS_SIGN` | `Δ_b ≥ +2.0` and the 95% CI excludes 0 |
| `FAVOURS_RABITQ` | `Δ_b ≤ −2.0` and the 95% CI excludes 0 |
| `PARITY` | otherwise (includes any `Δ` whose CI contains 0) |

The two states then combine. The nine combinations are exhaustive and mutually
exclusive; no outcome falls outside a band:

| band | LoCoMo × LongMemEval | verdict |
|---|---|---|
| B1 | both `FAVOURS_SIGN` | `[SIGN96 COMPETITIVE AT MATCHED BUDGET]` |
| B2 | both `PARITY`, or one `PARITY` + one `FAVOURS_SIGN` | `[PARITY AT MATCHED BUDGET]` |
| B3 | both `FAVOURS_RABITQ` | `[SIGN96 SUPERSEDED AT MATCHED BUDGET]` |
| B4 | one `FAVOURS_SIGN` + one `FAVOURS_RABITQ` | `[NOT ESTABLISHED — BENCHMARK DISAGREEMENT]` |
| B5 | one `PARITY` + one `FAVOURS_RABITQ` | `[LEANS RABITQ — NOT A KILL, FOLLOW-UP REQUIRED]` |

B5 is not a kill. It obliges a named follow-up: the disagreeing benchmark is
re-examined for a cause before any further method work on the SIGN96 line.

**B3 is a kill criterion for the method line.** If it fires, SIGN96 is not defended
as a method contribution; the programme's publishable claim becomes the 12-byte
comparison itself, and the mechanism track is closed rather than extended.

**Negative-result commitment.** B2, B3, B4 and B5 are written up and published in
the same form as B1. No band is a reason not to report.

## 10. Leakage barrier

Fitting receives archive `memory_text` only. Gold labels, answers, evidence
annotations and question type enter no fit, no codebook and no rotation. Query
transformation happens only after archive fitting. The existing static leakage audit
is extended to the new arms, and each new arm's fit function is added to the audited
surface.

## 11. What this preregistration does not authorize

No BEAM contact. No `--mode run/finalize`. No `V52_T4F1_AUTH_HMAC_KEY_HEX`. No
modification of any sealed byte, accepted audit or frozen result. Task 4F1 remains
**SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN**.

## 12. Seal precondition — third-party implementations

Arms 4–6 require third-party implementations (RaBitQ, extended RaBitQ, OPQ/PQ). The
programme's environment lock and audit-hook policy must be extended to cover them, or
reference implementations must be vendored and hashed. The seeds for arms 5–7 (§5)
must likewise be fixed as source literals.

**This is a precondition, not an open note.** The declared primary contrast is
`SIGN96 − RABITQ96`; if this preregistration were sealed with arms 4–6 undefined and
the arm 5–7 seeds still undeclared, the primary estimand could not be computed and
the run would stop before producing anything. This preregistration is therefore
**not eligible for sealing until the dependency question is disposed of and §5 is
closed.**

Stating the precondition is not taking the decision. **Which** implementations are
adopted, and whether they are vendored or covered by an extended environment lock,
remains the Head Researcher's to decide, exactly as `f9951c0` Decision 3 names a
target for the v5 reconciliation without choosing the means.

---

*Prepared by the Continuity Lead. Not preregistered until sealed on authorization.*
