# CRITIQUE — adversarial review of the llmzip top-10 programme

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Role: adversarial partner, not cheerleader. Every claim below carries one tag:

- **[COORDINATOR]** — number re-derived by the coordinator in FINDINGS_DIGEST.md; I did not recompute it.
- **[STORED]** — number/code I read from a file on disk (cited) but did not recompute.
- **[MEASURED HERE]** — number I computed this session from files on disk. Script + output: `check_corpora.py` / `check_pools.py` / `check_decisive.py` / `check_bothmiss.py` and their `.json` outputs, all in this directory.
- **[CONJECTURE]** — my hypothesis. Falsifiable; I state what would check it. No web access was used; nothing below is cited from memory of any paper.

Headline: the central diagnosis survives my best attack, but two of the four
sub-conclusions do not, and the programme is measuring the wrong bottleneck.
Details follow. Nothing here is preregistered; treat all of it as exploratory.

---

## 1a. "The bottleneck is the representation, not the 12-byte budget" — ATTACKED, survives weakened

**The confound (real).** The headline comparison changes TWO things at once
**[STORED**, `baseline/audit_top10.py` lines 108–116**]**:

| arm | doc side | query side | scorer | RealTalk Hit@10 **[COORDINATOR]** |
|---|---|---|---|---|
| float_std | 96-dim float | whitened query, cosine norm | standardized cosine | 48.51 |
| sign96 | 96 bits | query bits | −Hamming | 46.68 |
| qscale | same 96 bits | whitened query, NO norm | unnormalized dot | 49.65 |
| BM25 | — | exact terms | BM25 | 54.18 |

float_std vs sign96 differs in quantization AND scorer. Worse for the naive
telling: qscale (quantized!) beats float_std 49.65 > 48.51 **[COORDINATOR]**.
So "quantization costs 1.83pp" is scorer-dependent — with the better scorer,
quantization costs *negative* 1.14pp. The float<BM25 gap is therefore
(representation + cosine scorer + query fold-in) vs BM25, and attributing it to
"the representation" alone is unearned. The sharpest unseparated confound is
**query folding**: queries average 9.1 tokens, median 8 **[MEASURED HERE]**,
and each query is folded through the frozen TF-IDF→SVD pipeline before scoring
ever happens. The doc vectors could be perfect and a query whose rare term died
in fold-in would still fail. Nothing in the digest separates doc-side loss from
query-side loss.

**The settler I ran — and it backfired on my own attack.** The obvious rescue
of the anti-bottleneck case is "score the floats with qscale-style weights and
they win." I ran exactly that **[MEASURED HERE**, `check_decisive.py` §A,
`s = C @ (QC/sigma)` on cached `rt_repr/RT*.pkl`, n=705**]**: **float-dot
Hit@10 = 42.70**, *below* float_std cosine (48.51) and far below BM25 (54.18).
Per-archive it is uniformly worse than cosine, collapsing worst exactly where
archives are largest (RT06 18.92, RT08 10.00). So the interaction runs the
other way: on bits, equal-energy (±1) axes let query-side 1/sigma weighting do
the ranking (qscale wins); on floats, doc-side axis magnitudes swamp the query
weighting (whitened dot loses to cosine). Scorer and representation interact;
there is no scorer-free "quantization cost."

**Verdict.** My attack failed where it mattered: the best-tested float scorer
still loses to BM25 by 5.67pp, so something upstream of quantization is guilty.
But the conviction is for the wrong defendant: the evidence implicates
representation-**or**-query-folding jointly, and the digest's phrasing
("the 96-dim REPRESENTATION") quietly acquits query folding without a trial.
The single measurement that would fully settle it: **untruncated TF-IDF cosine
(no LSA, no SVD) vs BM25 on RealTalk** (prescribed as NEXT_5 #1). If
untruncated cosine ≈ BM25, SVD is the villain — case closed, stop tuning bits.
If untruncated cosine ≪ BM25, the villain is at or before term weighting
(BM25's saturation + length norm, which raw cosine lacks), and the whole
SVD-quantization programme has been optimizing downstream of the real defect.

## 1b. "Unbalanced axis-aligned bits are a feature" — REJECTED as stated; a dumber theory fits better

**The competing explanation, requiring no meaningful axes.** Continuous scores
are EXACTLY invariant to orthogonal rotation (`(CR)(QR)ᵀ = CQᵀ`), so rotation
changes one thing only: where the sign grid sits. Production bits are
unbalanced (per-bit 1-rate range 0.309–0.658) **[COORDINATOR]**; rotated bits
are near-50/50 (0.459–0.545) **[COORDINATOR]**. Near-50/50 pseudo-independent
bits concentrate pairwise Hamming distances at 48±5, so the true match's margin
must survive the maximum over N−1 distractors — an extreme-value penalty that
grows with archive size N. Prediction: rotation damage scales with N, on ANY
corpus, with no axis-meaningfulness premise at all.

**The measurement the digest never ran (I ran it).** Per-archive rotation
damage on RealTalk, qscale FULL vs RAND_20260916 **[MEASURED HERE**,
`check_pools.py` §1, one seed; three seeds agree overall per **[STORED]** quant
REPORT 34.61–35.32**]**:

- Small archives (N 410–662): RT01 −4.71, RT02 −14.29, RT03 −13.70, RT04 **+7.04**, RT05 −7.14 → mean **−6.56**
- Large archives (N 1044–1548): RT06 −22.97, RT07 −22.86, RT08 −27.14, RT09 −20.63, RT10 −22.03 → mean **−23.13**

Two facts kill the "feature" story. First, **RT04 gains +7.04pp from random
rotation** — a within-benchmark sign reversal. If axis-alignment were an
intrinsic feature of our frame, a random grid cannot beat it by 7 points on 71
queries. At minimum, "meaningfulness" is archive-dependent, which is exactly
what the concentration account predicts (small N → small penalty → noise
dominates). Second, the headline "−14 to −17pp" is an average over a 34-point
spread (+7.04 to −27.14); reporting the mean as a property of "our bits" hides
that the effect lives in the large archives.

**The cross-corpus asymmetry, explained in two parts.** PerLTQA damage is ~−1pp
**[COORDINATOR]**. What differs **[MEASURED HERE**, `check_corpora.py`,
`check_decisive.py` §C**]**: (i) PerLTQA archives are ALL small (N 293–546,
median 408) — i.e., the size range where RealTalk damage is already small
(−6.56, not −23.13). Size alone closes most of the 14pp gap. (ii) The residual
(−6.6 vs −1) needs content: PerLTQA docs are LONGER (mean 36.0 / median 28
tokens vs RealTalk 21.2 / 14), templated (`[profile] Slot: value` slot lines
with heavily repeated keywords — redundancy is rotation armor), queried
~275/archive vs ~70/archive, and the benchmark sits near ceiling (80% vs 50%
base — redundant cues give multiple paths to gold). N is the skeleton key;
template redundancy is the remainder.

**One more asymmetry the digest underplays, and it splits the mechanism.**
On PerLTQA, rotation kills qscale FR@3 (−2.6 SIG) but sym Hit@10 is ≈0 (ns)
**[COORDINATOR]**. On RealTalk BOTH scorers collapse ~14pp. So on PerLTQA the
damage is PURELY qscale-miscalibration (sigma′ flattens after mixing axes; the
bits themselves are fine — sym proves it), while on RealTalk the bits
themselves get worse. Two benchmarks, two different mechanisms, one slogan.
The discriminating measurement is prescribed (NEXT_5 #5): regress per-archive
rotation damage on N across PerLTQA's 30 archives. Same-sign slope → size story
wins outright. Flat → content story wins.

## 1c. "IDF^p works via the rare-term mechanism" — PROBABLY NOISE; the defense's own exhibits convict it

**The case for noise/artifact:**

1. **Multiplicity.** Roughly 6 arms × 2 metrics × 2 scorers × 4 bands ≈ dozens
   of examined cells; exactly ONE band-contrast is 95%-SIG with lower bound
   +0.69 **[COORDINATOR/STORED**, `rare_band_decisive.json` +4.78 [+0.69,+8.43]**]**.
   One marginal SIG out of dozens is the expected false-positive yield under
   the null, not a discovery.
2. **Everything was chosen post-hoc**: the arm (p=2), the metric (FR@3, after
   Hit@10 didn't move: +0.49ns **[COORDINATOR]**), the scorer (qscale — see
   next point), the band cutoffs (2/4), the tokenization (two tried).
3. **The sym-null.** The SAME IDF_p2 codes ranked by Hamming move rare-band
   FR@3 by −0.74pp **[STORED**, `repr_fr3_mechanism.json` mechanism table:
   sym rare 33.76→33.01; qscale rare 33.23→38.01**]**. A representational
   mechanism ("rare directions now survive in the bits") must improve the BITS,
   hence both scorers. A qscale-only gain is a scorer-reweighting interaction:
   IDF_p2 reshapes the sigma spectrum, which reshapes query weighting — not
   "rare information preserved." Overall FR@3 confirms: qscale +2.61ns,
   sym −1.02ns **[STORED]**.
4. **Headroom artifact.** FULL FR@3 by band (qscale): common 1.50%, mid 12.47%,
   rare 33.23% **[STORED]**. Gains can ONLY appear where headroom exists, so
   "the gain sits where the mechanism predicted" is observationally identical
   to "the gain sits where variance permits." The common band is at floor for
   everyone — no arm could ever show a mechanism there.
5. **Sign flips inside the benchmark.** My leave-one-archive-out **[MEASURED
   HERE**, `check_decisive.py` §B, coordinator banding recipe reproduced
   exactly (overall +4.78, n=412 match to 2 decimals)**]**: dropping any single
   archive keeps the mean positive (+3.9…+6.0), so it is not ONE archive's
   quirk — but the per-archive effects are RT10 +12.76, RT05 +11.11, RT07
   +10.90, RT03 +9.22 … RT02 +0.56, RT09 −2.93, RT08 −8.43. A mechanism that
   operates at +13 in one archive and −8 in another, in the same benchmark, is
   a description of heterogeneity, not a mechanism.
6. **PerLTQA significantly reverses** (IDF_p2 FR@3 −1.76 [−2.78,−0.74] SIG
   **[COORDINATOR]**). A mechanism needs a moderator to survive a significant
   sign flip; none has been proposed, let alone measured.

**The cheapest killer (prescribed as NEXT_5 #2): a zero-CPU split-half.**
Lock NOW, before touching held-out data: tokenization-2 recipe, cutoffs 2/4,
arm IDF_p2, scorer qscale, metric FR@3, test = the same paired
archive-clustered bootstrap (seed 20260916). Split RealTalk queries odd/even
by qid within archive; the test runs ONCE on the held half. Success =
same-sign with CI excluding 0 on the held half. A preregistered version must
additionally fix: the multi-gold FR@3 definition (mean over queries of
|gold∩top3|/|gold| — the current one), the exclusion list (705 valid),
handling of the no_shared sliver (n=7 — drop or merge, decided NOW, not after
seeing which helps), and the PerLTQA boundary condition reported as-is win or
lose (no goalpost-moving: a RealTalk-only confirmation still leaves the
PerLTQA reversal unexplained). My prior, stated so it can be scored:
it fails, ~70% **[CONJECTURE]**.

## 1d. "It depends on the archive" is now evidence of overfitting — full stop

Count the reversals **[COORDINATOR]**: char channel essential-on-RT /
beneficial-to-drop-on-PQ; IDF_p2 helps-RT-rare / hurts-PQ; SHIFT_m1 helps-PQ /
hurts-RT; asym helps-PQ / hurts-LME (−3.56 FR@3); rotation −15 RT / −1 PQ.
Now add the within-benchmark reversals **[MEASURED HERE]**: rotation RT04 +7.04
vs RT08 −27.14 (34pp spread inside ONE benchmark — larger than the RT-vs-PQ
gap it supposedly explains); IDF_p2-rare RT10 +12.76 vs RT08 −8.43.

When within-benchmark archive spread EXCEEDS between-benchmark gaps,
"benchmark identity" has no predictive content left — it is the residual being
sold as a finding. The overfitting locus is precise and must be named
correctly: it is NOT the SVD weights (unsupervised, frozen seeds, docs-only —
there is no label to overfit). It is **selection over dozens of
arm×metric×scorer×band cells with 10 archive-clusters**: with 10 exchangeable
units driving the bootstrap, a post-hoc 95% CI with lower bound +0.69 is
exactly what the winner's curse produces. And note the power asymmetry the
programme keeps ignoring: NOTHING on RealTalk (10 clusters, n=705) is well
powered — every RT-first claim has CIs spanning zero — while PerLTQA's harms
(IDF_p2 −1.76 SIG, WORD_ONLY +1.37 SIG, SHIFT_m1 +1.58 SIG) are the
best-powered results in the building. The rational Bayesian
update is to trust PerLTQA's significant harms over RealTalk's exploratory
gains, i.e. to believe LESS of our own story, not more.

> **CORRECTION 2026-09-18 — "all 30 clusters" was false; the argument above is
> weaker than written.** Two of the three exhibits (IDF_p2 −1.76 and SHIFT_m1
> +1.58) were computed on **10 of 30 PerLTQA archives — 2,967 of 8,265 questions**,
> not on all 30. The stored contrasts say so themselves: `coordinator/repr_results.json`
> and `coordinator/repr_fr3_mechanism.json` both carry `"clusters": 10`, and the
> producing run died at 10/30 archives (`math_r1/repr.log` ends in SIGTERM; no
> `RESULTS.json` was ever written). The numbers are correct **as subset contrasts**.
> Only WORD_ONLY +1.37 is a separate full-cohort channel ablation (n=8265), and it
> was not re-verified here.
> Consequence: this paragraph's "only well-powered results" conclusion loses two of
> its three exhibits and the winner's-curse caveat this document raises elsewhere
> (§1d, "10 archive-clusters", "lower bound +0.69") applies to its own SHIFT_m1
> exhibit. Status of both contrasts: **SUPPORTED_ON_SUBSET**, not SUPPORTED.
> Secondary: SHIFT_m1 +1.58 is a *gain*, yet it is listed under "PerLTQA's harms".

Graduation rule (proposed, to be adopted or explicitly rejected): no arm
graduates from exploratory without (i) ONE prespecified contrast, (ii)
same-sign replication on a second benchmark or held-out archives, (iii) effect
larger than the archive-level spread (report the per-archive range next to
every CI — my LOO/rotation tables show how). Under this rule the current
graduating class is empty, which is the honest state of the programme.

---

## PART 2 — what we have not asked

### 2.1 The both-miss autopsy: half our failures are unreachable, and they cluster where nobody is looking

Oracle-over-(sym,qscale) on RealTalk FULL: sym 46.52, qscale 49.65, oracle
53.48, both-miss 328/705 (46.5%) **[MEASURED HERE**, `check_pools.py` §2**]**.
Crossed with bands and pool reachability **[MEASURED HERE**,
`check_bothmiss.py`**]**:

| band | n | both-miss | miss rate | of which: gold in CODE top-100 | gold outside top-100 |
|---|---|---|---|---|---|
| common | 133 | 124 | 93% | 41 | 83 |
| mid | 153 | 86 | 56% | 43 | 43 |
| rare | 412 | 111 | 27% | 72 | 39 |
| no_shared | 7 | 7 | 100% | 2 | 5 |

Three ignored facts. **First, the failure is the common band** (93%
both-miss; plus no_shared at 100%): queries whose gold shares only common
terms. The programme's rare-term theory aims at the band that already works
best (rare: 27% miss). Nobody works the common band — plausibly because there
is nothing to work with: if query and gold share only stopword-like terms,
lexical retrieval is ill-posed, and a 12-byte sketch cannot invent signal.
Note the irony the digest buries: in the common band CODE already BEATS BM25
(20.98 vs 15.62 Hit@10 **[COORDINATOR]**) — each method owns one band, which
is the real argument for fusion, not for fixing SVD. **Second, 170/328
(51.8%) of scorer-failures have gold OUTSIDE CODE's top-100** — unfixable by
ANY reranker at M=100, by construction. Overall: the reranking programme at
M=100 addresses at most 75.6% of queries (Hit) / 61.3% (FR@3 ceiling)
**[COORDINATOR]**, and ~24% (172/705) are dead on arrival **[MEASURED HERE**,
reproduces firststage's 172 **[STORED]**, `firststage/REPORT.md`**]**.
**Third, first-stage recall is the binding constraint, not rerank quality.**
Every reranker point should be weighed against +1pp of pool recall; the
programme currently prices rerankers and gives away recall. Even the
oracle-union of CODE∪BM25 pools still misses 105 queries @100 and 10 @500
**[STORED]**. And the FR@3 lens is harsher than Hit (61.30 vs 75.60 ceiling)
because 386/705 queries are multi-gold **[STORED]** — the metric choice alone
moves the "ceiling" by 14 points, yet arms are compared across metrics freely.

### 2.2 A realistic reranker ceiling: price the text, or stop talking about reranking

The oracle knows gold. A real reranker sees 100 raw texts + the query — and
the honest accounting the digest never quite does in one place: raw text alone
is 998,654 B (8.7× the codes) **[COORDINATOR]**; a text-reranking deployment
stores text + (index?) + model weights + 100 model forwards per query against
a Hamming scan that costs nothing. Meanwhile the FREE realistic reranker was
never run: **BM25-scores-restricted-to-CODE's-top-100** (all inputs STORED in
`firststage/per_query.jsonl`). That single recomputation (NEXT_5 #3) bounds
what dumb text signal recovers of the 22.41→61.30 gap: ≥50% recovered → text
suffices, skip learned rerankers; <20% → the gap is semantic, so price a real
model honestly or quit the direction. The deployment truth nobody states:
**any architecture that re-reads text already pays ~1MB+ before codes matter,
so the 12-byte budget is a rounding error in every reranking architecture and
binding only in the no-text edge device that also cannot run a reranker.**
The programme wants the prestige of tiny codes and the ceiling of big
rerankers simultaneously; the honest framing picks one.

### 2.3 Equal total storage: the decider nobody ran, and it cuts against the digest

**[MEASURED HERE** from `cost_audit.json` via `check_pools.py` §4**]**:
dropping the compact BM25 index frees **75.0 B/doc** (600 bits, 6.25× our
budget); dropping index+text frees **186.6 B/doc** (~1500 bits, ~15×).
Full-float-96 (384 B) is unaffordable even then — "just store floats" is off
the table at equal storage, which the digest never quite says. The unrun
decider: **600-bit codes vs CODE+BM25 fusion (55.74 Hit@10 / 31.45 FR@3
[STORED])**. Two facts point opposite ways, honestly: FOR more-bits — the
within-family dim curve 48→64→80→96 dims = 36.45→40.85→45.39→49.65
**[COORDINATOR]**, ~+4.4pp per 16 dims and NOT saturating, i.e. the 12B cap
binds at the margin and "budget is not the bottleneck" overclaims.
AGAINST — the quantization cost is only ~2pp, so extra bits must buy
*dimensions*, not precision; and k=600 at N=410 gives retention 600/410 > 1
(the rho math flips from lossy to near-exact — the regime changes, so the
curve may not extrapolate). The sharp version keeps k=96 and spends the 600
bits as ~6 bits/dim (NEXT_5 #4): it separates "k too small" from "1 bit too
coarse" at fixed SVD. At 2.56MB total (fusion's honest footprint
**[STORED]**), codes alone could be ~286 B/doc — still sub-float. So even
"spend everything on codes" cannot buy back floats on RealTalk; the programme
goal needs reframing from "12 bytes" to "pareto frontier at fixed total
bytes," where fusion is the baseline to beat, not the embarrassment to hide.

### Verdict on the stated goal

"Gold Hit@10 at K=10 from ≤12–16 byte/doc codes" has NO literature report
either way **[COORDINATOR]** — unmeasured, not refuted. Our best: 49.65 (RT)
**[COORDINATOR]**, 80.00 (PQ) **[COORDINATOR]**; uncompressed SOTA reaches only
~78 Recall@10 on hard multi-hop **[COORDINATOR]**. The rho identity (Σρᵢ = k
exactly **[COORDINATOR]**) PROVES average unique-feature retention of 96/N —
0.23 at N=410, 0.06 at N=1548 — so on large archives this FAMILY cannot keep
discriminative detail at 12 bytes no matter the quantization trick; the
co-occurrence counterexample **[COORDINATOR]** only says WHICH rare features
survive is structural, not that the average can be beaten. Plainly: **with
TF-IDF→SVD-96→sign, 12 bytes cannot reach the stated goal on RealTalk-like
archives; the overrides are fusion (not 12 honest bytes), small/redundant
archives (PerLTQA works at 80%), or a different family.** If the goal is
universal 12-byte top-10, say the programme failed and pivot to the pareto
frontier. If the goal was always "tiny codes where archives are small plus
fusion elsewhere," write that down and stop grading 12-byte arms against BM25
on 1500-doc chat archives.

---

*Checks: `check_corpora.py`, `check_pools.py`, `check_decisive.py`,
`check_bothmiss.py` (+ `.json` outputs), this directory. Caveats: float-dot
used stable-argsort top-10 (continuous scores; hash tie-break immaterial);
rotation per-archive used RAND seed 20260916 only (three seeds agree overall
[STORED]); LOO means are unweighted (directional, no bootstrap); my banding
reproduces the coordinator's overall +4.78/n=412 to 2 decimals (fidelity OK);
float-dot n=705 matches the valid-query count (cache/exclusion alignment
assumed). All CPU: minutes, read-only, no refits, no shipped-arm rescoring
except the two diagnostic scorings described.*
