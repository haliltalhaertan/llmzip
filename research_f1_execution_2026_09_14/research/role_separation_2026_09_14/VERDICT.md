[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT.md — near-duplicate role structure as a mechanism for the SIGN96 effect

## Bottom line

**The hypothesis is REFUTED as a mechanism.** Archives do contain systematic adjacency structure
from indexing both speakers, but it is *correlation, not duplication*; it is not driven by speaker
pairing; and its relationship to the sign-vs-float effect runs **opposite** to what the hypothesis
requires across benchmarks.

Candidate explanation #6 (archive-internal near-duplicate structure) joins the five already dead.

---

## Verdict on each relayed claim

| # | relayed claim | verdict | measured |
|---|---|---|---|
| 1 | adjacent pairs Hamming 28 vs 48 random | **PARTLY CONFIRMED** | 31.98 vs 47.96 (LME). LoCoMo 43.19 vs 47.97 — relayed number does not generalise |
| 2 | AUC 0.955 | **OVERSTATED** | **0.9088** (LME), 0.6952 (LoCoMo) |
| 3 | cosine 0.77 vs −0.03 | **PARTLY CONFIRMED** | **0.705** vs −0.0023 |
| 4 | "near-copy is FALSE"; ≤16 bits = 0.14% of pairs | **CONFIRMED** | **0.1369%** |
| 5 | 84% of the ≤16 tail is not adjacent | **CONFIRMED** | **83.56%** |
| 6 | role asymmetry ≈ 1 bit | **REFUTED** | **6.90 bits** (u→a 28.87, a→u 35.77); shuffle control 0.045 |
| 7 | `build_archive` applies no role filter | **CONFIRMED** | read at `adapters/longmemeval_v52_adapter.py:80-103` |

The external model was right about the negative result (claims 4, 5) and about the no-filter fact,
overstated the separation statistics, and was wrong by ~7x on role asymmetry.

---

## Why the hypothesis dies — three independent kills

**Kill 1 — the tail is not made of speaker pairs.**
Only 6.15% of adjacent pairs fall within 16 bits, and same-session *non*-adjacent pairs hit that
tail at an indistinguishable rate (6.12%). 83.56% of the ≤16-bit tail is non-adjacent. Adjacency
buys no special near-duplicate status.

**Kill 2 — the proximity is not caused by speaker pairing.**
Lag-2 pairs, which are the **same speaker**, are **closer** (25.48 bits) than lag-1 cross-speaker
pairs (31.98 bits). If indexing both speakers created the duplicates, cross-speaker lag-1 would be
the tightest relation. It is not. The driver is topic continuity and same-speaker register — and
because roles alternate, indexing both speakers *interleaves dissimilar rows*, working against
duplication rather than for it.

**Kill 3 — the cross-benchmark sign is backwards.**
The hypothesis requires the sign-losing benchmark to be the near-duplicate-rich one.

| | sign − float | median gold-dnn | % gold-dnn ≤ 16 |
|---|---|---|---|
| LongMemEval | **+10.05 pp** | **18 bits** (densest) | **38.5%** |
| PerLTQA | **−6.27 pp** | 27 bits | 3.2% |

LongMemEval has ~12x more near-duplicate gold neighbourhoods than PerLTQA and is where sign wins
*most*. Near-duplicate density cannot explain a reversal whose sign it predicts wrongly.

---

## The one real finding, correctly characterised

There **is** a significant within-LongMemEval moderator: queries whose gold row has a close non-gold
neighbour show **delta = −11.15 pp** relative to far-neighbour queries (CI [−17.79, −4.12]),
decomposing into sign −8.37 pp [−15.63, −0.88] and float +2.78 pp [−4.94, +10.20]. It survives:

- archive size (corr(dnn, N) = −0.039; within-quartile effects −19.2/−14.3/−20.3/+6.1 pp);
- gold distinctiveness (residualising on gold-query distance raises r from 0.174 to 0.188).

But it is **not a role effect and not a quantization-specific effect**:

- adjacency within the close group contributes **−1.67 pp, CI [−10.24, +6.70]** (null);
- the nearest neighbour being an adjacent turn is associated with **+0.58 pp**, CI [−6.27, +7.67];
- substituting a *cosine* nearest-neighbour predictor reproduces **−8.23 pp** of it, so the
  predictor lives in the float geometry, not in the sign code.

Correct name for it: **generic gold-neighbourhood density**, a per-query difficulty moderator.
It does not survive as a cross-benchmark mechanism (PerLTQA +0.87 pp, LoCoMo −3.02 pp, REALTALK
−0.28 pp; all CIs cross zero) and, controlled for archive and section, the slopes are
+0.223 / +0.422 / −0.045 pp per bit — i.e. inconsistent in sign and negligible in size.

---

## Corrections to PREDICTION.md (PREDICTION.md itself was NOT edited)

| prediction | outcome |
|---|---|
| P1 Hamming 30–40, AUC 0.75–0.93 | **HIT** (31.98, 0.9088) |
| P1 cosine 0.35–0.65, relayed 0.77 too extreme | **MISS** — 0.705; the relayed figure was closer than mine |
| P2 ≤16 tail <1%, mostly non-adjacent | **HIT** (0.1369%, 83.56% non-adjacent) |
| P3 asymmetry 1–4 bits, user→assistant closer | **HALF-HIT** — direction correct, magnitude 6.90 bits, above my band |
| P4 gold-gold adjacency >5x enriched | **MISS on LME** (1.33x, no power); **HIT on LoCoMo** (9.10x) |
| P5 no sign-specific near-duplicate penalty | **HIT on the conclusion, MISS on the route** — I predicted no within-benchmark effect; LME shows a real −11.15 pp one. It dies as a *mechanism* for the reason I predicted (cross-benchmark sign backwards), plus one I did not anticipate (cosine reproduces it) |
| P6 reproduce a frozen headline | **HIT** — three headlines to ≤7e-7 pp |

Two self-inflicted bugs found and corrected mid-run, both disclosed in ROLE_FACTS.md:
1. `roles_main.py:auc_fast()` inverted the AUC tail (reported 0.093 instead of 0.909).
2. `roles_fix.py:F4` permutation control masked on permuted labels but indexed original rows,
   producing a fake "half-surviving" control (33.71 bits). Corrected in `roles_fix2.py:G1`
   → 47.91 bits, which is the proper null.

---

## Adversarial self-check (mandatory)

**Most damaging assumption: the row↔turn mapping.** If wrong, every number is meaningless.

Tested four ways, all passed:
1. Count match 470/470.
2. **Gold-index match 470/470 (886 rows)** — an order-sensitive check, not a length check.
3. Row-permutation control: true adjacency 31.98 bits vs permuted 47.91 bits (= cross-session
   baseline 48.19); AUC vs cross-session 0.914 → 0.507 (chance).
4. Role-shuffle control: asymmetry 6.90 → 0.045 bits.

**Second-most damaging assumption: that my per-query FR@3 matches the frozen pipeline.**
Three of four benchmark deltas reproduce to ≤7e-7 pp. LoCoMo is off by 0.173 pp due to a gold-set
assembly difference (evidence IDs missing from `id_to_row`); disclosed, and it affects no
conclusion since LoCoMo enters only through structure measurements.

**Third: that I would have accepted the LME effect uncritically.** I did not — it is the one
result favouring the hypothesis, and I ran the size confound, the distinctiveness confound, the
adjacency decomposition, and the cosine substitution specifically to try to keep it alive as a
role effect. It failed the last two.

---

## What I could NOT do

- **No significance test on the cross-benchmark corollary** (n=4 benchmarks; the pattern is
  reported as a direction, not a test).
- **LME gold-gold adjacency is underpowered** (1.9 gold rows per archive). The LoCoMo measurement
  (9.10x) is the informative one.
- **REALTALK/PerLTQA adjacency structure not measured** — neither cache exposes turn ordering
  (`rt_repr` has `id_to_row` but PerLTQA's `cache_arch_eval.pkl` carries only `C`/`N`). Adjacency
  distributions are therefore LME + LoCoMo only; the mechanism test (which needs only gold-dnn)
  covers all four.
- **No causal test.** Nothing here removes assistant rows and re-runs retrieval; that would be the
  direct experiment and it requires re-encoding, which is out of scope read-only.
