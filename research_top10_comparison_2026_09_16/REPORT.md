[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Twelve-byte retrieval codes: where they work, where they fail, and what it honestly costs

Round of 2026-09-16. Branch `findings/top10-comparison-2026-09-15`; `main` untouched.

Every number here was **re-derived by the coordinator** from stored per-query top-10 ids,
not copied from a worker's summary. Production anchors reproduce to 0.0000 pp. All
contrasts use a paired archive-clustered bootstrap, 20000 reps, seed 20260916.
"SIG" = the 95% interval excludes zero.

---

## 1. What was being claimed, and what survived

The programme's working claim was: *a 12-byte-per-document code gives competitive
retrieval*. This round tested that claim hard enough to break parts of it.

**The claim did not survive in its strong form.** The evidence:

| RealTalk (n=705, Hit@10) | value | storage |
|---|---:|---|
| BM25 (plain lexical, no learning) | **54.18** | inverted index |
| qscale (our 12-byte code) | 49.65 | 12 B/doc |
| float_std (96 dims, **uncompressed**) | 48.51 | 384 B/doc |
| sign96 | 46.68 | 12 B/doc |
| PQ (equal budget control) | 33.05 | 12 B/doc |

Quantization costs only **1.83 pp** (48.51 → 46.68). But BM25 beats the *uncompressed*
representation by **5.67 pp**. So the bottleneck was never the 12-byte budget: it is the
96-dimensional representation itself. Tuning bits cannot fix this, and this round
confirmed that by trying and failing.

---

## 2. The mechanism: what the projection throws away

Stratifying the 705 RealTalk queries by the IDF of the term shared between query and its
gold document:

| band | n | CODE | BM25 | gap |
|---|---:|---:|---:|---:|
| no_shared | 24 | 20.83 | 16.67 | −4.17 |
| common (idf<2) | 224 | 20.98 | 15.62 | −5.36 |
| mid (2–4) | 116 | 49.14 | 45.69 | −3.45 |
| **rare (≥4)** | **341** | **70.67** | **85.04** | **+14.37** |

The entire deficit lives in the rare-term band (341/705 = 48.37%, the largest band but
**not** a majority — an earlier draft wrongly called it one).

**Why this happens, mathematically.** TruncatedSVD minimizes Frobenius reconstruction
error, which rewards high-variance directions. Rare terms are low-variance by
construction, so they are discarded first — while IDF says those are exactly the
discriminative ones. The two objectives point in opposite directions.

For a feature present in exactly one record `i`, the energy retained by a rank-k
projection is the leverage score

    rho_i = sum_{j<=k} U_ij^2,   and   sum_i rho_i = k   exactly.

Verified numerically over 200 random matrices: max deviation **1.07e-14**. In a
500-record archive at k=96, the *average* retention for such unique features is
96/500 = 0.192. Keeping every unique detail at full strength is arithmetically
impossible, not an implementation defect.

**Limit on that claim (important).** This does *not* prove "rare is always discarded."
A counterexample exists in which, holding term frequencies and k fixed and changing only
the co-occurrence structure, a rare feature flips from fully dropped to fully preserved.
Co-occurrence structure matters, not rarity alone. Measured on 3 LME archives rebuilt
bit-exactly (1486 records), median word-feature reconstruction quality (1 = perfect,
0 = as bad as zeroing the column): df=1 features 0.153/0.179/0.189 versus df>20
features 0.531/0.547/0.536.

---

## 3. What we tried. Every arm kept exactly 96 bits / 12 bytes.

### 3.1 Quantization layer — 4 of 4 failed, and the failure is the finding

| RealTalk Hit@10 (qscale) | | PerLTQA Hit@10 (qscale) | |
|---|---:|---|---:|
| FULL | 49.65 | FULL | 80.00 |
| ITQ (50 iters) | 32.77 | ITQ | 78.91 |
| random rotation (3 seeds) | 35.04 (34.61–35.32) | random rotation | 79.04 |
| median threshold | 49.22 | median threshold | 79.47 |

**ITQ minus random rotation = −2.27 pp (RealTalk), −0.13 pp (PerLTQA).** ITQ's
optimization bought nothing; *any* rotation does this damage. Without the random-rotation
control we would have concluded "ITQ doesn't work here"; with it we learned something
stronger and more general.

Verified on real data: `sign(C_ij / sigma_j) == sign(C_ij)` — 0 of 63,552 document bits
and 0 of 8,160 query bits changed by per-axis rescaling. Only a rotation or a shifted
threshold can move a bit in this pipeline.

**Why rotation hurts — the honest answer.** An earlier draft of this report claimed our
unbalanced axis-aligned bits are "a feature." An adversarial review killed that
explanation with a simpler one, and the coordinator verified it:

| RealTalk archives | mean rotation damage |
|---|---:|
| small (N<700), 5 archives | −6.56 pp |
| large (N≥1000), 5 archives | **−23.13 pp** |

Pearson r(archive size, damage) = **−0.78**. PerLTQA has *no* large archives (median 408
docs, max 546); RealTalk has five (1044–1548). The −17 pp vs −1 pp split between the two
benchmarks is explained by **archive size distribution**, with no appeal to our axes
being special. The simpler explanation wins.

Bit balance, for the record: production mean fraction-of-1s 0.492 with per-bit range
0.309–0.658; rotated arms 0.499 with range 0.459–0.545. Rotation makes bits *more*
balanced — textbook "better" — while retrieval collapses.

**Cost.** The rotation matrix R is 96×96 floats per archive: **3.43×** (RealTalk) and
**7.50×** (PerLTQA) the entire document payload it fails to improve.

**Scope, verified against the source.** The ITQ paper (Gong & Lazebnik, "Iterative
Quantization: A Procrustean Approach to Learning Binary Codes for Large-scale **Image**
Retrieval") evaluates dense visual descriptors with Euclidean neighbours as ground truth.
Our inputs are per-archive TF-IDF/SVD and our target is gold retrieval. This is a scope
mismatch, not a refutation of ITQ. The paper defines the random-orthogonal baseline we
used as our control.

### 3.2 Representation layer — real signals, and they reverse across benchmarks

Zero-arm identity verified first: `IDF_p0` and `SHIFT_m0` differ from production in
**0 queries**. Without that check, every other arm would measure a reimplementation.

**A. IDF^p reweighting of the word block.** RealTalk Hit@10: all arms ns. RealTalk FR@3
overall for IDF_p2: +2.61 pp, CI [−0.12, +5.30] — **not significant**. But the mechanism
check, by band:

| band | n | diff |
|---|---:|---:|
| common | 133 | −0.75 ns |
| mid | 153 | −0.20 ns |
| **rare** | **412** | **+4.78 pp, CI [+0.69, +8.43] SIG** |

The gain sits **only** in the band the stated mechanism predicted, and replicates under a
second tokenization rule (n=408: +4.83, CI [+0.70, +8.50]). In-band Hit@10 is +0.49 ns —
so ordering improves inside an unchanged pool.

**Three caveats that must travel with this number.** (i) It is a subgroup contrast chosen
*after* seeing results — the weakest form of evidence. (ii) The same arm **significantly
hurts** PerLTQA: FR@3 −1.76, CI [−2.78, −0.74]; IDF_p1 −1.17 SIG. (iii) Leave-one-archive-out
shows per-archive effects ranging −8.43 to +12.76 pp.

**B. Component shift (use components m+1..m+96 — a window shift, not truncation).**
PerLTQA SHIFT_m1 Hit@10 **+1.58, CI [+0.69, +2.47] SIG** (sym +1.35 SIG). RealTalk
SHIFT_m1 Hit@10 −0.28 ns, and sym FR@3 **−1.06 SIG (harmful)**. Opposite signs again.

### 3.3 Channel ablation — the sign reverses here too

| arm | RealTalk Hit@10 (qscale) | PerLTQA Hit@10 (qscale) |
|---|---:|---:|
| FULL | 49.65 | 80.00 |
| NO_LSA | 52.06 (+2.41 ns) | 79.53 (FR@3 −1.23 **SIG harmful**) |
| NO_CHAR | 43.83 (−5.82 **SIG harmful**) | 80.83 |
| WORD_ONLY | 46.24 (−3.40 **SIG harmful**) | **81.37 (+1.37 SIG, FR@3 +2.09 SIG)** |

The char channel is significantly essential on RealTalk and significantly droppable on
PerLTQA. WORD_ONLY — the *simplest* arm — wins on PerLTQA and is 5.6× faster to build
(28.1 s → 5.0 s per archive). LSA_ONLY was not run: Z would have only 32 columns and the
fixed SVD96 protocol requires 96. The worker declared this a blocker instead of
inventing numbers. Correct behaviour; the prompt was at fault.

### 3.4 Budget splitting — failed, and the failure decomposes

Splitting 96 bits between SVD dims and a rare-term Bloom sketch:
96+0 = 49.65 | 80+16 = 33.33 | 64+32 = 34.61 | 48+48 = 33.48.
SVD-only truncation: 96 → 45.39 (80) → 40.85 (64) → 36.45 (48).

| split | truncation cost | extra fusion cost | truncation's share |
|---|---:|---:|---:|
| 80/16 | 4.26 | 12.06 | **26%** |
| 64/32 | 8.80 | 6.24 | 59% |
| 48/48 | 13.20 | 2.97 | 82% |

**Retraction.** An earlier claim that "truncation is the sole cause" was wrong. At 80/16
truncation explains only 26% of the damage; the rest was the fusion design. Also, a
32-bit Bloom score yields ~5 distinct values per query, so it ranks almost entirely by
tie-break — a bad sketch, not only a truncation problem.

---

## 4. First-stage retrieval: the largest measured gain, and it is not ours

RealTalk pool quality at 100 candidates: CODE 75.60 | BM25 78.16 | **RRF(k=60) 81.28**.
RRF − CODE = +5.67 pp, CI [+3.23, +8.20] SIG. RRF − BM25 = +3.12 SIG.

Complementarity is real: at 100 candidates CODE alone finds 49 queries BM25 misses;
BM25 alone finds 67 queries CODE misses.

**Honest storage (RealTalk, 8944 docs).** Codes + sigma 115,008 B. BM25 inverted index
**670,511 B** under varint delta-gap encoding. A `pickle` dump inflates the same index to
1,450,229 B — **that number must not be quoted**; the earlier 12.6× headline was a
pickle artifact, the honest ratio is **5.83×**. Index + raw text: 1,669,165 B.

---

## 5. The reranking ceiling is smaller than it looks

Oracle reranker over the pool we already retrieve (FR@3): PerLTQA 53.24 → 76.52 @100
(+23.3); LME 54.27 → 92.62 (+38.4); RealTalk 22.41 → 61.30 (+38.9).

That looked like the biggest opportunity in the programme. It is not, and the
adversarial review is why. Decomposing the 705 RealTalk queries:

- 350 queries: CODE already hits @10.
- 183: gold is inside the top-100 pool but not the top-10 — **reachable by a reranker**.
- 172: gold is **outside the top-100 entirely** — unreachable by *any* reranker.

Of the **328 queries both our scorers miss**, 170 (51.8%) have gold outside the top-100.
So roughly half the headline ceiling is unreachable in principle. Reranking addresses
the reachable portion only.

Per band, the fraction both scorers miss: common 93.2% (n=133), mid 56.2% (n=153),
rare 26.9% (n=412). Note what this does to a tempting consolation: CODE does beat BM25
in the common band (20.98 vs 15.62), but **both methods fail on 93% of those queries** —
being ahead where both are broken is not an advantage worth claiming.

**Independent corroboration.** A separate effort (gpt-6-pro, 2026-09-16) ran the actual
text-rerank experiment whose anchors match ours to 0.0000 (qscale FR@3: LME 54.27,
PerLTQA 53.24, RealTalk 22.41), with ceiling values consistent with ours under fewer
candidates. Their result, FR@3:

| data | qscale | code → BM25 rerank | **BM25 alone** | code's net contribution |
|---|---:|---:|---:|---:|
| LME | 54.27 | 57.70 | 58.03 | **−0.33** |
| PerLTQA | 53.24 | 57.46 | 57.13 | +0.33 |
| LoCoMo | 35.84 | 42.81 | 41.75 | +1.06 |

On two of three datasets, the 12-byte code contributes nothing measurable once text
reranking is available. Their memory accounting on LME (MB): packed codes + sigma 3.14;
raw UTF-8 source 237.87 (**76×**); IDF dictionary objects 351.18 (**112×**). And latency
rose: 14.9 ms → 17.6 ms, against 0.14 ms for a plain inverted index.

---

## 6. Known negative results — do not rediscover

- Arbitrary quantile thresholds hurt badly (PerLTQA zero-threshold .76 vs q0.1 .31).
- The old `asym` arm helps PerLTQA but **loses** on LME (−3.56 pp FR@3).
- `qscale` is not new: identical results exist in `hit10/QSCALE.json`, in an external
  gpt-6-pro package, and in a fresh rerun — all to 0.000 deviation. Verification is
  valuable; rediscovery is not.
- The PPLX-0.6B semantic arm was abandoned: the encoder ran at ~4.3 texts/s (73 tok/s)
  and the cause was never diagnosed. Weights verified (sha256 matches server, revision
  `2c4d510dd4a732063c31a0f70193e35067b51fd8`) but no retrieval numbers were produced.
- **No arm has ever won on both benchmarks simultaneously.** This is now a
  programme-level regularity across channel ablation, IDF power, component shift, and
  the old asym arm — and it is unexplained. It is currently a better predictor of any
  new result than any mechanism we have proposed.

## 7. Open, unresolved

- LoCoMo gold authority is contradictory (n=1531 vs 1535; 156 audited corrections never
  applied). Every LoCoMo number is disputable.
- RealTalk has only 10 archives; its intervals are wide and everything on it is exploratory.
- Literature search found **no source** reporting gold Hit@10 at K=10 from ≤12–16 B/doc
  codes. The target is unmeasured in the literature — neither confirmed nor refuted.
- A 2^96 counting bound is vacuous here (~900 docs/archive). The constraint is query-side
  generalization through the same lossy 96-dim bottleneck, and we know of no applicable
  theorem. Estimating I(code; gold) would be a research project, not a citation.
- An oracle that picks the better of our own two scorers per query saturates at ~55% on
  RealTalk (both miss 328/705) — the gap is representational, not a ranking-order problem.

## 8. What this round is worth

The strong claim ("12 bytes, competitive retrieval") is not defensible on this evidence
and should not be published in that form. What is defensible, and what this directory
contains:

1. A **measured map** of where extremely-low-bit spectral codes work and fail, with the
   mechanism named (variance vs. discrimination), derived mathematically and confirmed
   by band-stratified measurement.
2. A **replicated negative result** on the quantization layer, including the control
   (random rotation) that turns "ITQ failed" into the stronger "rotation itself is the
   problem, and its damage scales with archive size."
3. An **honest cost methodology**: varint vs pickle, auxiliary state charged at 76–112×,
   latency measured rather than assumed. Applied to ourselves first.
4. A set of **retracted claims** (rare-band majority, truncation as sole cause, "our axes
   are a feature") with the evidence that killed each — preserved rather than quietly
   edited away.

## 9. Methodological guards used this round

- **Blocking fidelity gate.** No arm was measured until the production representation was
  rebuilt bit-exactly from raw text. PerLTQA: 0 of 1,179,648 sign bits differed. LME:
  0 differing bits across 92+ archives verified. A near-miss rebuild is not a licence to
  report new arms — they would measure the reimplementation.
- **Zero-arms.** `IDF_p0`, `SHIFT_m0` must equal production exactly. They did (0 queries).
- **Mandatory controls.** Random rotation for ITQ; plain BM25 for every fusion claim.
- **Audit code written before workers finished**, with anchors fixed in advance.
- **Seeds pinned in the prompt** (LSA32=5101, SVD96=5204) after a prior run was
  invalidated by a wrong seed (`BOTTLENECK.json` INVALID_SEED_DEFECT).
- **No gate loosening.** Workers were instructed to STOP and report rather than adjust a
  failing gate. One did exactly that (G6, BM25 top-10: 704/705 match, one 3-way tie
  differing by 1 ulp) and left it as FAIL with an explanation.
- **Coordinator audits are adversarial to the coordinator too.** The first audit run
  returned REJECT with 3 findings; all three turned out to be defects in the audit code,
  not the workers'. The corrected audit re-derives every metric from raw stored ids
  (RealTalk+PerLTQA: 107,640 rows, 0 mismatches; RRF rebuilt from scratch, 705/705 identical).

## 10. Where things are

```
coordinator/     audit + analysis written and run by the coordinator, not by workers
digest_r1/       FINDINGS_DIGEST.md (re-derived), lit/ (literature map), brain/ (adversarial review)
math_r1/         repr/ (IDF^p, component shift), quant/ (ITQ, random, median)
ablation_r2/     perltqa/ (complete), lme/ (in progress at publication time)
ideas_r1/        ablation/ (RealTalk channels), firststage/ (CODE vs BM25 vs RRF)
baseline/ data/ pq/ audit/     first-round producer arms
inventory/       MASTER_LEDGER.md, DO_NOT_REPEAT.md, GAP_TO_100.md, DO_NOT_RESCAN.md
incoming_20260916/   external gpt-6-pro package + our verification
FILE_MANIFEST.json   sha256 of every original file (pre-gzip)
```

Excluded from publication: `model/` (2.4 GB HF weights; sha256 + revision recorded in
`MODEL_DOWNLOAD.json`) and `*.npz` intermediates. Files over 3 MB are gzipped; the
manifest records the sha256 of the original uncompressed bytes.
