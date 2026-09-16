[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# External adversarial audit 3 — what it corrected, verified by the coordinator

An external reviewer audited the programme's claims with independently written code
(`audit3_*`), reproducing every published level exactly before attacking it. This file
records what the coordinator independently verified and which of our claims must change.

## The central correction: "discard" was the wrong word. It is a dimension budget.

We reported that TruncatedSVD *discards* rare terms, implying a targeted defect that a
better choice of 96 directions could fix. The auditor supplied the control we never ran:
**a random 96-dimensional subspace null.**

| df | terms | pipeline SVD survival | random 96-dim subspace | ratio |
|---|---:|---:|---:|---:|
| 1 | 95,119 | 0.1831 | 0.1941 | **0.94×** |
| 2 | 12,719 | 0.3339 | 0.1942 | 1.72× |
| 5–9 | 3,645 | 0.4239 | 0.1943 | 2.18× |
| 20–49 | 597 | 0.5542 | 0.1943 | 2.85× |
| 50+ | 164 | 0.7513 | 0.1982 | 3.79× |

Spearman(df, survival) = +0.46 for the SVD, +0.11 pooled for the random subspace — and
per-archive the random figure is +0.038 / −0.024 / −0.009, i.e. **zero**. The pooled
value is a cross-archive artifact.

**Coordinator verification.** A random 96-dim subspace retains a generic direction at
k/n. Measured over 40 draws per size: n=410 → 0.2409 (k/n=0.2341); n=500 → 0.1875
(0.1920); n=662 → 0.1458 (0.1450); n=1548 → 0.0610 (0.0620). For a singleton column
`e_i` — which is exactly what a df=1 term is — 200 draws at n=500 give mean **0.1934**
against k/n = **0.1920**.

This is *our own leverage identity* seen from the other side: `sum_i rho_i = k` forces
mean `rho = k/n`. We derived the identity and then failed to draw the obvious
consequence — that k/n is the **baseline every direction gets**, so landing at 0.94× of
it is not evidence of targeting.

**Corrected statement.** The SVD preserves common terms **1.7–3.8× better than chance**
while rare terms survive at **essentially exactly the chance rate** for any
96-dimensional compression. Ninety-six directions cannot align with 95,119 singleton
columns, and **no other choice of 96 directions would do better on them**. The constraint
is the dimension budget, not the SVD objective.

This kills the implicit hope behind our whole representation programme: that a smarter
96-dimensional projection exists. It does not, for rare terms.

## The evidence we never produced: the dimension ladder

`run_svdloss.py` measured attenuation but never connected it to retrieval. The auditor
ran the removal experiment — same text, features, queries, gold, metric; only the
truncation changes. FR@3 in the rare-hinge bucket:

| | bm25 | svd96 | svd192 | svd384 | full Z, no projection | word channel only |
|---|---:|---:|---:|---:|---:|---:|
| LoCoMo (n=950) | 58.70 | 24.82 | 32.96 | 40.13 | 45.17 | **57.42** |
| PerLTQA (n=5,694) | 72.15 | 65.17 | 70.12 | 72.61 | **72.70** | 69.98 |

Gap to BM25: LoCoMo −33.88 → −25.74 → −18.57 → −13.53 (all SIG). PerLTQA −6.98 SIG →
−2.03 SIG → **+0.46 ns** → **+0.55 ns**.

**Monotone in the dimension budget on both benchmarks. On PerLTQA the gap to BM25 closes
completely by 384 dimensions.** The mechanism survives — on evidence we did not produce.

## A second mechanism we missed entirely

On LoCoMo, the word channel with **no projection at all** reaches 57.42 against BM25's
58.70 (gap −1.28, ns), while the full Z reaches only 45.17. **The character n-gram
channel costs 12.25 pp in the rare bucket** — comparable to the entire 96→full-rank
projection effect (20.35 pp), and absent from our account.

Decomposing the LoCoMo rare-bucket gap: projection ≈ 60%, **feature mix ≈ 36%**, BM25's
scoring function +1.28 (ns). Our claim that the projection explains the whole deficit is
wrong on the benchmark where the deficit is largest. On PerLTQA (Chinese) the char
channel helps and the projection does explain everything — another sign reversal,
consistent with our channel-ablation results.

## Our rare/common presentation is circular

The bucket is defined by the df of the rarest term shared between question and gold —
computed with **BM25's own tokenizer over BM25's own document frequencies**. In the
"common" bucket BM25 scores **exactly zero on every query** by construction (LoCoMo
100%, PerLTQA 97.8%, LME 100%). So `sym − bm25` there is not a comparison; it is the
one-sample statement `sym > 0`, and its significance is automatic.

Our framing — "the code holds its own where the hinge is common" — describes **a bucket
where nothing works.** This applies directly to a consolation we offered: CODE beating
BM25 in the common band is not an advantage when both fail on 93% of it.

The bucket also confounds rarity with sheer overlap: questions share 2–3× more terms
with gold in the rare bucket (LoCoMo 2.06 → 4.73). It is a query-difficulty stratifier.

**However:** the dimension ladder uses that same bucket definition throughout, so
comparisons *among* those arms remain internally valid. Circular presentation, sound
mechanism.

## BM25 was handicapped — our headline understates the gap

Giving BM25 the frozen word channel's own tokenization (`\b\w\w+\b`, English stopwords
removed, unigrams+bigrams) makes it **better**: +3.38 pp SIG on PerLTQA (29/30 archives),
+3.29 pp SIG on LoCoMo (9/10), +0.14 ns on LME. Stopword removal alone accounts for
almost all of it. And textbook k1=1.2/b=0.75 is not a neutral default: k1→0, b=0 gives
**42.11 on LoCoMo against 37.67**.

Combined, the LoCoMo lexical baseline is ≥40.96, and our gap widens from −13.88 to
about **−17.2**.

## Ties: our LME row is mostly a tie artifact

`sym` carries heavy integer Hamming ties (untied on 65–77% of queries; BM25 99–100%).
Granting `sym` its **best possible** tie-break:

| | sym expected | sym friendly | bm25 | friendly − bm25 |
|---|---:|---:|---:|---:|
| LongMemEval | 54.21 | 56.55 | 57.00 | **−0.45 ns** |
| PerLTQA | 48.89 | 50.58 | 56.72 | −6.14 SIG |
| LoCoMo | 23.79 | 25.49 | 37.67 | −12.18 SIG |

Ties are worth 1.69–2.34 pp. C1 survives comfortably on PerLTQA and LoCoMo. **On
LongMemEval most of the apparent BM25 advantage is `sym`'s ties** — that must be stated
whenever the LME row is quoted.

## BM25 memory: our figure was too kind to BM25

Measured (int32 docid + float32 weight postings, plus vocabulary and idf):

| | docs | 12-byte codes | raw text | BM25 index | × codes | × the text |
|---|---:|---:|---:|---:|---:|---:|
| LongMemEval | 231,606 | 2.78 MB | 237.87 MB | **213.29 MB** | 76.7× | 0.90× |
| PerLTQA | 12,288 | 0.15 MB | 2.59 MB | 3.82 MB | 25.9× | 1.48× |
| LoCoMo | 5,882 | 0.07 MB | 0.85 MB | 1.31 MB | 18.5× | 1.54× |

213 MB on LongMemEval, not ~64 MB. The "text is stored anyway" defence only goes so far:
the index is 0.9–1.5× the text *again*, so adopting BM25 roughly doubles the text-side
footprint. Our qualitative point stands and is **stronger** than we stated.

## What the auditor could not break

- **Text alignment.** 18/18 archives reproduce cached `sign(C)` exactly (max |ΔC| ≤
  4.3e-13; LoCoMo bit-identical); shuffled-order control 0.502, so the test has power.
  Question text reproduces `qC` exactly on 1,294 PerLTQA questions (shifted-pairing
  control 0.65–0.70). Our own guard (`len(texts) != C.shape[0]`) cannot detect a
  permutation and was too weak — the result happens to hold anyway.
- **LoCoMo gold.** Applying the 156 audited corrections (92/1,534 queries change):
  −13.89 → −13.94, both SIG. The open obligation remains open but does not threaten it.
- **Thin clusters.** Cluster bootstrap, jackknife-t and an exact sign test agree;
  PerLTQA 0/30 and LoCoMo 0/10 archives favour the code.
- **Bucket cuts.** Monotone across every cut from 0.005 to 0.20; Spearman(log df, delta)
  +0.147 / +0.133 / +0.280.

## Corrections to our own published claims

1. **"The projection discards rare terms" → OVERSTATED.** Rare terms survive at 0.94× the
   random-projection null. The SVD does not target them; it lifts common terms above
   chance. The limit is the dimension budget and cannot be fixed by better directions.
2. **"The projection explains the deficit" → wrong on LoCoMo.** ~36% is the char channel.
3. **"CODE wins the common band" → degenerate.** BM25 is zero there by construction and
   both methods fail on ~93% of those queries.
4. **Our BM25 baseline was handicapped** by tokenizer and parameter choices; the honest
   gap is larger, not smaller.
5. **BM25 index memory understated** (213 MB vs ~64 MB quoted on LongMemEval).
6. **`ndcg3_expected` defect confirmed** (frozen MAE 0.1292; corrected 0.00099) — but the
   MAE is a property of the synthetic generator, not of the benchmarks; on real data the
   bias is +0.88 to +1.36 nDCG points on tied arms only, and exactly zero on float arms.

## What this changes about the programme's direction

The dimension ladder is the most decision-relevant result anyone has produced this round,
and it points away from everything we were doing:

- Tuning **which** 96 directions (IDF^p, component shift, rotation) cannot recover rare
  terms — they are already at the chance rate and no 96-dim choice beats chance on them.
- Raising the **budget** does work, monotonically, and on PerLTQA fully closes the gap to
  BM25 at 384 dimensions.
- On LoCoMo, a third of the gap is the **feature mix**, which no extra dimension fixes.

The honest question is therefore no longer "how do we make 96 bits smarter" but "what is
the right operating point on the bits-vs-quality curve, and is 12 bytes anywhere near
it". That reframes the programme's premise rather than advancing it.


---

# RETRACTION (same day) — the impossibility claim was wrong

A further external review challenged two conclusions in this file. **On the first it is
right and the claim is retracted.**

## Retracted: "no other choice of 96 directions would do better on rare terms"

We wrote that the dimension budget makes rare-term loss unavoidable, so no better
96-dimensional projection exists. That does not follow from `sum_i rho_i = k`.

The identity fixes the **mean** at k/n. It places no cap on any individual `rho_i`.

**Coordinator-verified counterexample.** A 96-dim subspace spanned by 96 chosen
coordinate axes:

    chosen 96 directions  rho = 1.0000
    all other directions  rho = 0.0000
    sum = 96.0000 = k,  mean = 0.1920 = k/n

Their 50-direction version reproduces exactly: preserved 1.000, rest 0.102, mean 0.192.
Some directions can be protected in full; the cost is paid by others. Whether the
*retrieval-useful* directions can be identified from documents alone is an **open
empirical question**, not a settled impossibility.

Consequence for the programme: our failed 96-bit arms (IDF^p, component shift, ITQ,
median threshold) stay shelved **because they failed in experiments**, not because of an
impossibility proof. The reviewer's formulation is the correct one.

They also note that 95,119 singleton columns are not 95,119 independent directions —
several unique terms in the same record can share a direction over documents. Correct;
the "96 directions vs 95,119 details" phrasing was loose.

## Also retracted: "12 bytes isn't enough, 48 bytes is"

Two conflations, both real:

1. **Dimensions are not bytes.** 384 *coordinates* equal 48 bytes only if they are stored
   as 384 **sign bits** and scored as such. At float32 the same 384 coordinates are
   1,536 B/doc — 32× more. The audit's ladder does not state which scorer produced each
   row, so "384 dims closes the gap" cannot be rewritten as "48 bytes closes the gap"
   without the sign-coded arm.
2. **Scope.** The PerLTQA row is the **rare-term bucket only**, not all queries. And
   +0.46 ns is a failure to detect a difference, not a demonstration of equivalence, and
   certainly not proof that 48 B is the minimum sufficient budget.

Their third point stands too: on LoCoMo the **unprojected** mixed representation still
scores 45.17 against BM25's 58.70, so the deficit there cannot be attributed to the
dimension budget alone.

## One correction we do not accept

The reviewer objects to reading the friendly-tie result as evidence that the LME row is
an artifact. They are right that an expectation-over-ties metric is unbiased and that a
gold-aware tie-break is an oracle control — we should not call the expectation "wrong".
What the friendly-tie number legitimately shows is **sensitivity**: on LME the gap moves
from −2.79 to −0.45 under the most favourable tie-break, i.e. the LME conclusion is not
robust to tie convention. That is how it will be stated. PerLTQA (−6.14) and LoCoMo
(−12.18) survive even the friendliest ties.

On memory, the scope difference is noted: our earlier ~64 MB was the BM25 statistics
JSON total, while the 213 MB figure counts full postings (int32 docid + float32 weight)
plus vocabulary and idf. Both should be labelled by scope rather than compared directly.

## What this changes in the running experiment

The coordinator's dimension ladder (`coordinator/ladder.py`, running on RealTalk at the
time of this retraction) was already designed to separate exactly what the reviewer asks
for, and this is preserved:

    k in {96, 192, 384, 768}  x  { sym (sign bits, Hamming)
                                   qscale (same sign bits, numeric query)
                                   float (no quantization) }

with bytes/doc charged honestly per arm (sign = k/8 B; float = 4k B), plus unprojected
word-only and full-Z controls and BM25 under **both** the coarse and the frozen
tokenizer. Headline decisions will be taken on **all queries**, with the rare-term band
reported as diagnosis only.
