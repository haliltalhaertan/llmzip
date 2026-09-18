# Adversarial audit brief 2 — the BM25 control and the rare-term mechanism

**Your job is to BREAK these claims, not confirm them.** The author's record in
this session: roughly fifteen claims withdrawn over two days, almost all of
them found by an auditor or an outside reviewer rather than by the author. One
bootstrap error was made, corrected, and then made again the same day. Treat
every number below as a hypothesis.

`[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]`

---

## 0. Rules

- **Re-derive with your own code**, prefixed `audit3_`. Read `run_bm25.py`,
  `run_rareterm.py`, `run_svdloss.py`, `run_where_next.py` and `run_signals.py`
  to find bugs; do not import them.
- **Do not modify** any existing `run_*.py`, `audit_*.py` or `*.json`.
- **Do not touch** the frozen venv (`llmzip-work/venv`, numpy 2.3.5); use it
  read-only, install nothing.
- **No git pushes, no `main`, no BEAM / Task 4F1 surface.**
- Everything is in `C:\Users\MDP\dev\llmzip-work\parallel_ideas_r1\hit10`.
  Frozen scorer `../b8/lib_b8.py`, frozen protocol `../b8/PROTOCOL.md`.
- Say so when a claim survives an attack you genuinely made. A clean bill of
  health is useful; a rubber stamp is not.

## 1. THE FLAW THE AUTHOR ALREADY FOUND — start here

**C2 below may be circular, and the author's attempt to rule that out
failed.** This is the most important item in the brief.

`run_rareterm.py` buckets queries by the document frequency of the **rarest
term shared between the question and its gold evidence**. BM25's score *is* the
IDF-weighted overlap between question and document. So "the gold shares a rare
term with the question" and "BM25 scores the gold highly" may be close to the
same statement, and the rare bucket may be defined by the very quantity being
compared.

A gold-free control was attempted — bucket by the question's own rarest
in-archive term — and it was **uninformative**: 1,486 of 1,535 LoCoMo queries
fell into one bucket. It does not discriminate, so it neither confirms nor
refutes anything.

`run_svdloss.py` is the author's second attempt: measure, with no query, no
gold and no BM25 anywhere, how much of each word-channel column of `Z` survives
the rank-96 truncation, and whether survival falls with document frequency.
**Check that script for bugs first** — it is the load-bearing evidence for C2
and it was written after the circularity was noticed, which is exactly when
motivated reasoning is most likely.

It has now been run, 12 LongMemEval archives, 475,051 word columns:

| df | terms | mean surviving energy |
|---|---|---|
| 1 | 376,559 | **0.182** |
| 2 | 50,117 | 0.329 |
| 3-4 | 24,195 | 0.364 |
| 5-9 | 14,330 | 0.426 |
| 10-19 | 6,644 | 0.517 |
| 20-49 | 2,499 | 0.564 |
| 50+ | 707 | **0.757** |

Spearman(df, survival) = +0.370 pooled, +0.384 mean per archive, between
+0.362 and +0.404 in every one of the 12. **So the FIRST half of C2 — the SVD
discards rare terms preferentially — now has non-circular support.**

The SECOND half does not. That the discarding is *why* BM25 wins on rare-hinge
queries still runs through the possibly-circular split. Keep those separate in
your verdict, and attack the link, not only the premise.

Specifically: is `U @ V[:, lo:hi]` the right reconstruction for
`TruncatedSVD`? Is the word-channel column range `lo:hi` correct given
`sparse.hstack([Xl, Xw, Xc])`? Does restricting to the word channel bias the
answer, given that `Xl` is itself derived from `Xw`? Is energy survival the
right quantity, or should it be per-column reconstruction error, or the
column's angle to the retained subspace?

**If you can show the rare-term mechanism is an artifact of the bucketing, that
is the single most valuable result you can return.**

## 2. Claims

**C1 — BM25 matches or beats the whole pipeline on the frozen metric.**
FR@3, `sym - bm25`, cluster bootstrap over archives:

| | n queries / archives | sym | bm25 | delta |
|---|---|---|---|---|
| LongMemEval | 470 / 470 | 54.21 | 57.00 | -2.79 [-5.89, +0.29] ns |
| PerLTQA | 8,265 / 30 | 48.89 | 56.72 | **-7.83** [-9.22, -6.45] SIG |
| LoCoMo | 1,535 / 10 | 23.79 | 37.67 | **-13.88** [-17.11, -10.58] SIG |

Even 768 B/doc `float_std` loses on LoCoMo (-11.42 SIG). BM25 is textbook
k1 = 1.2, b = 0.75, fixed before any result, per-archive statistics, untuned.

**C2 — the mechanism: the projection discards rare terms.** FR@3,
`sym - bm25`, split by the hinge term's df (cuts fixed in advance at 10 % and
2 % of the archive):

| | common hinge | rare hinge |
|---|---|---|
| LongMemEval | +8.47 [+1.61, +17.47] SIG (n=31) | -6.25 [-9.68, -2.88] SIG (n=356) |
| PerLTQA | +9.17 [+5.88, +12.95] SIG (n=601) | -12.44 [-14.05, -10.85] SIG (n=5,694) |
| LoCoMo | +1.22 [+0.23, +2.50] SIG (n=322) | -23.32 [-27.44, -18.94] SIG (n=950) |

**C3 — RRF fusion.** Best on LongMemEval (59.14) and PerLTQA (57.09), but its
margin over BM25 alone is ns (+2.14, +0.36); on LoCoMo it is **significantly
worse** than BM25 alone (-4.79).

**C4 — taking the sign is a per-axis normaliser.** `float` and `float_std` are
the same 96 float64 coordinates differing only by a per-axis division, worth
+11.59 pp of FR@3 on LME. `sym` captures 87 % (LME), 94 % (RealTalk), 73 %
(LoCoMo) of that gain, and on PerLTQA sits *below* raw float.

**C5 — the second-stage ceiling.** A perfect reordering of the ten candidates
the 12-byte code retrieves is worth +12.00 (PerLTQA), +24.05 (LME), +14.54
(RealTalk), +15.42 (LoCoMo) pp of FR@3, against +0.36 to +2.46 for any better
reading of the same bits.

**C6 — cheap signals do not reach it.** 470 LME queries, alpha cross-fitted on
held-out halves: IDF overlap +1.63 pp (6.8 % of the ceiling), a
shorter-document prior +1.99 pp (8.3 %), dates and proper nouns and position
nothing.

**C7 — a defect in the frozen scorer.** `lib_b8.ndcg3_expected` (lib_b8.py:63)
divides a tie bucket's expected discount by the fillable slots rather than by
the bucket size. Monte Carlo, 300 cases x 4,000 permutations: frozen mean
absolute error 0.0840 against 0.00123 corrected, 119/300 off by more than 0.02.
Zero without ties, so it inflates the Hamming arms only.

## 3. Weaknesses the author knows about

- **W1. BM25's tokeniser is not the frozen word channel's.** `[A-Za-z0-9']+`,
  no stop-word removal, no stemming, against
  `TfidfVectorizer(ngram_range=(1,2), stop_words="english")`. Which way does
  that cut? Does giving BM25 the frozen tokeniser change C1?
- **W2. The bucket cuts (10 %, 2 %) were fixed in advance but not justified.**
  Is the C2 pattern robust to other cuts, or to a continuous treatment (regress
  the per-query delta on log df)?
- **W3. LoCoMo gold is `raw_evidence`.** The 156 audited corrections are an
  open obligation; the historical anchor uses `correct_evidence`. Does C1's
  LoCoMo leg survive the audited gold? (`theory_benchmark_test_v1/locomo/
  run_locomo.py:189`.)
- **W4. LoCoMo and PerLTQA have 10 and 30 clusters.** The cluster bootstrap is
  thin there. Do distribution-free tests (sign test over archives, jackknife,
  leave-one-archive-out) agree?
- **W5. Text reconstruction.** PerLTQA question text was rebuilt by replaying
  `step2_build.py`'s qid construction (8,265/8,265 matched); LoCoMo document
  text by replaying `raw_item_to_conv` / `message_text`. Verify both against
  the cached `id_to_row` and gold rows independently. A misalignment would
  corrupt every BM25 number.
- **W6. The memory accounting for BM25 is quoted from an external run**
  (~64 MB for LME's 470 archives against 2.78 MB of codes) and was **not
  measured here**. The raw text must be stored anyway, so how much of that is
  genuinely additional is unestablished.
- **W7. C5's oracle takes ties at the M-th place in full**, so the candidate
  set is larger than nominal. Does a strict top-M change the ceiling?

## 4. What would falsify the headline

C1 and C2 are load-bearing. They fall if:

1. The text used by BM25 is not aligned with the rows the vector arms score
   (W5). Check this first; it is cheap and it would invalidate everything.
2. BM25 is being given an advantage the frozen pipeline is denied — a
   different tokeniser, different casing, access to fields the frozen
   `fit_input_payload` strips (W1).
3. The rare/common split is circular (section 1). The direct representation
   test in `run_svdloss.py` is the intended answer; audit that script hardest.
4. `exact_frac` is being applied to BM25's dense float scores and the vector
   arms' heavily tied integer scores in a way that favours one. The metric is
   an unbiased expectation over tie-breaks and a previous audit confirmed that,
   but BM25 has essentially no ties while `sym` has many — the same confound
   that cost 0.3 to 1.8 pp in the previous audit. **Quantify it here too:**
   give `sym` its best possible tie-break and re-measure C1 and C2.

Item 4 is the one the author considers most likely to shrink C1, and it has
not been tested on these contrasts.

## 5. Deliverable

For each of C1-C7 and W1-W7: **CONFIRMED / OVERSTATED / WRONG**, with your own
number and the code that produced it. Then anything not on this list. State
negative verdicts plainly.
