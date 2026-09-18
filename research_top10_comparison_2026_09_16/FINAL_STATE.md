[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# llmzip twelve-byte retrieval pilot — final state, 2026-09-16

Branch `findings/top10-comparison-2026-09-15`. `main` untouched (`59b891e`), merge is the
owner's call. Every number below was re-derived by the coordinator from stored per-query
ids; production anchors reproduce to 0.0000 pp.

## Verdict: STOP

Three gates were written down *before* the deciding tests ran (`decision_r1/cost/REFEREE.md`).
Two failed outright; the third stopped firing for a reason that retracted one of my own
explanations.

| gate | result |
|---|---|
| C1 — some arm ≤48 B beats a fairly built BM25 by ≥2 pp FR@3 on both benchmarks | **FAIL** (behind 7.80 pp at 48 B) |
| C3 — code+rerank beats BM25 alone by ≥1 pp FR@3 | **FAIL** (1 of 3, on disputed-gold LoCoMo) |
| S3 — corrected PerLTQA still declines on unstandardized arms | did not fire (`asym` rises) |

## The three facts that decided it

**1. Our BM25 baseline was handicapped by more than our entire research gain.**
The strongest honest BM25 on RealTalk scores 65.67 Hit@10 (frozen tokenizer, IDF-only
k1→0/b=0), not the 55.32 this programme always quoted — a **+10.35 pp** handicap, larger
than the whole 12→48 byte ladder gain (+8.22 pp). At 48 B/doc we trail by 7.80 pp; at the
claimed 12 B by 16.03 pp.

**2. A text reranker dissolves first-stage quality.** From 164,256 stored paired rows:
on LME, `float_raw32` starts 11.58 pp behind the leading first stage and finishes 0.29 pp
*ahead* of our flagship. Post-rerank spread is 0.58 pp across first stages spanning
11.58 pp before. Order inversions: 4/10, 3/10, 6/10 pairs. Our code's net contribution
over plain BM25 alone: −0.33 / +0.33 / +1.07 pp.

**3. Ladder shape is a scorer property, not a bit-budget law.** On RealTalk the ladder
rises monotonically (49.65 → 55.32 → 57.87). On PerLTQA the standardized arms fall at 384
dims while unstandardized `asym` keeps rising (60.79 → 61.09). Enforcing k<n removed every
constant dimension (0 in all 8 small archives) and the decline **persisted** — so the
rank-overflow cause I published was wrong. The real mechanism is dividing by the tiny σ of
genuine near-singular trailing directions.

## What is genuinely ours (nothing in the scanned literature covers these)

1. **ITQ does not beat a random rotation** here: −2.27 pp RealTalk, −0.13 PerLTQA. ITQ's
   home setting is dense image descriptors with Euclidean-neighbour ground truth; our
   regime is per-archive TF-IDF/SVD sign codes with gold retrieval.
2. **Rotation damage scales with archive size**: Pearson r = −0.78; small archives lose
   6.56 pp, large ones 23.13 pp. This alone explains the cross-benchmark difference that we
   had attributed to our axes being special.
3. **Bit balance anti-correlates with retrieval.** Rotation makes bits more balanced
   (per-bit 1-fraction range 0.309–0.658 → 0.459–0.545) and retrieval worse. The
   literature treats balance as a design goal.
4. **σ-division collapses at high k** while unstandardized scoring keeps improving —
   measured today, and visible in the incoming package's own table before anyone noticed.
5. **Fair-baseline methodology**: give the competitor your own tokenizer before claiming a
   win. Applied to ourselves, it reversed the programme's headline.
6. **`sign()` is not merely lossy here** — it acts as a per-axis normalizer and *adds*
   ~10 pp over the **raw, unstandardized** float source it quantizes
   (k=384: sym 54.18 vs raw float 43.69).
   > **CORRECTION 2026-09-18 — this gain is reference-dependent, do not quote it bare.**
   > Against *standardized* float the sign code does **not** win: `REPORT.md` §1 reports
   > `float_std` at **48.51** vs `sign96` **46.68** on the same RealTalk cohort, i.e.
   > sign is −1.83 pp *behind* that reference. The "+10 pp" holds only against raw float.
   > Already recorded on `main` as ledger L097 (`59b891e`); it had not been carried into
   > this file. Every future quotation must name the float reference it beats.

## Retractions (five, all preserved with the evidence that killed them)

1. "No better choice of 96 directions exists" — `Σρᵢ = k` fixes the *mean* at k/n and caps
   no individual ρᵢ. Counterexample verified: 96 chosen coordinate axes give ρ=1.0000 to
   those and 0.0000 to the rest, mean still 0.1920.
2. "12 bytes isn't enough, 48 is" — dimensions are not bytes, and the evidence behind it
   was defective.
3. "The SVD discards rare terms" — rare (df=1) terms survive at 0.94× a random-subspace
   null; common terms at 3.79×. The SVD lifts common terms, it does not target rare ones.
4. "CODE wins the common band" — degenerate: BM25 scores exactly zero on 97.8–100% of that
   bucket by construction, and both methods fail on ~93% of it.
5. "The PerLTQA decline is rank overflow" — disproved by my own T3 test (0 constant dims,
   decline persists).

Four were caught by external review; the fifth by my own test. All are recorded rather than
edited away.

## Honest cost accounting

| item | RealTalk |
|---|---:|
| codes + sigma (12 B/doc × 8944) | 115,008 B |
| BM25 inverted index, varint delta-gap | 670,511 B (5.83×) |
| index + raw text | 1,669,165 B |

A `pickle` dump of the same index inflates to 1,450,229 B — that number must not be quoted;
the 12.6× headline it produced was an artifact. On LME the external package measured raw
text at 76× the code and IDF dictionaries at 112×, with latency 14.9 → 17.6 ms against
0.14 ms for a plain inverted index.

## Method guards used

- **Blocking fidelity gate** before any arm was measured: PerLTQA 0 of 1,179,648 sign bits
  differed; RealTalk ladder 0 of 858,624; T3 0 of 276,480.
- **Zero-arms** (`IDF_p0`, `SHIFT_m0`) had to equal production exactly — they did, in 0 queries.
- **Mandatory controls**: random rotation for ITQ, plain BM25 for every fusion claim,
  λ=0 for the penalty arm.
- **Audit code written before workers finished**, anchors fixed in advance.
- **Gates never loosened**: one worker hit a failing gate (BM25 top-10, 704/705 match, one
  3-way tie differing by 1 ulp) and left it FAIL with an explanation rather than adjusting it.
- **The coordinator's first audit returned REJECT** — all three findings turned out to be
  defects in the audit code itself, documented rather than hidden.
- **Decision gates were written before the deciding tests ran** and were not moved afterwards.

## What remains open

- LME channel ablation, 322/470 archives at time of writing. Already paid for; finish and
  freeze. It does not gate the decision.
- LoCoMo gold authority is contradictory (n=1531 vs 1535, 156 audited corrections never
  applied). Every LoCoMo number is disputable.
- RealTalk has 10 archives; its intervals are wide and everything on it is exploratory.
- No source was found reporting gold Hit@10 at K=10 from ≤12–16 B/doc codes. The
  few-hundred-document per-archive regime appears unstudied — our results cannot be
  checked against anyone else's.

## One thing that would reopen this

Every comparison here is against BM25, which needs an inverted index and raw text at query
time. If a deployment genuinely cannot hold text or an index — bits only, sub-millisecond,
no reranker — the comparator changes and the 12-byte question becomes live again. No such
deployment has been specified in this programme, and the reranked pipeline needs the text
anyway, which is what erases the storage premise.

## Layout

```
REPORT.md                    main findings report (with inline corrections)
DECISION_TESTS.md            T1-T3, the gates, and the fifth retraction
LADDER_REALTALK.md           the RealTalk byte ladder
EXTERNAL_AUDIT3_RESPONSE.md  external audit + our retraction of the impossibility claim
PUBLICATION_VERIFY.md        clean-clone readback and the CRLF artifact
coordinator/                 every audit and analysis the coordinator ran personally
decision_r1/{keep,kill,cost}/ the three-way decision debate, with agent prompts and logs
lit_r2/{rate,quant,lexical}/ round-2 literature maps and ranked fetch queues
digest_r1/                   re-derived findings digest, round-1 lit map, adversarial review
math_r1/, ablation_r2/, ideas_r1/, baseline/, data/, pq/, audit/, inventory/
incoming_20260916b/          external package audits (ladder/ideas/chat) + prompts
FILE_MANIFEST.json           sha256 of every original file
```

Excluded: `model/` (2.4 GB HF weights; sha256 + revision in `MODEL_DOWNLOAD.json`) and
`*.npz` intermediates. Files over 3 MB are gzipped; the manifest records the sha256 of the
original uncompressed bytes.
