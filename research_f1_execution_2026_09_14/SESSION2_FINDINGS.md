[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Second half of 2026-09-14: brainstorm, cross-checks, kills, and a literature hit

Everything below was produced after commit `c85ee9c`. Every measurement reproduced the
frozen headlines as a control BEFORE any new number was trusted; where a control was
skipped or broken it is stated.

## 0. A published paper already contains the main mechanism

`WHITENING_FINDING.md` (commit c85ee9c) presented per-axis variance equalisation as
this session's explanation for the sign-quantization advantage. A literature search run
afterwards found the core idea is **published and four years old**:

- **Su, Cao, Liu, Ou (2021), "Whitening Sentence Representations for Better Semantics
  and Faster Retrieval", arXiv:2103.15316** - whitening fixes the anisotropy of
  sentence embeddings, improves similarity tasks, AND reduces storage. Code at
  github.com/bojone/BERT-whitening.
- **Huang et al. (2021), "WhiteningBERT", Findings of EMNLP 2021** -
  aclanthology.org/2021.findings-emnlp.23 - "an easy whitening-based vector
  normalization strategy with less than 10 lines of code consistently boosts
  performance".
- **Jung et al. (2022), "Isotropic Representation Can Improve Dense Retrieval",
  arXiv:2209.00218** - whitening improves ColBERT/RepBERT re-ranking by 2.4-8.1% on
  NDCG@10.

**Disposition: the novelty claim in `WHITENING_FINDING.md` is withdrawn.** What this
programme did was independently rediscover a known result on its own data. That is a
sound replication and a genuine correction to the programme's headline, but it is not
new knowledge. The framing "the float baseline was under-specified" stands; the framing
"we found the mechanism" does not.

What could NOT be found published (searches recorded in the literature session): a
direct statement that **binary/sign quantization IS a crude lossy form of that same
equalisation**, capturing 44-86% of the whitening gain at 1/32 the storage. The
whitening line and the binary-quantization line appear not to have been connected.
That link, not whitening itself, is the remaining candidate contribution.

## 1. A published diagnostic does NOT replicate on this data

**Parupudi (2026), "Anisotropy Decides Cosine vs. Rank Metrics for Text Embeddings",
arXiv:2606.29571** - 19 metrics x 19 encoders x 7 datasets. Its claim (CLAIM, from the
fetched abstract): when variance concentrates into a few dominant directions, rank and
L1 metrics beat cosine; the fraction of variance in the single most dominant dimension
predicts the gain with linear correlation **0.95** and rank correlation 0.86.

Measured here (VERIFIED, `research/whitening_2026_09_14/lit_replication.py`; all four
frozen controls passed exactly first):

| benchmark | top-1 direction variance share | rank-minus-cosine gain |
|---|---|---|
| LongMemEval | 0.0469 | +11.74 pp |
| PerLTQA | 0.0475 | +1.25 pp |
| REALTALK | 0.0843 | +6.03 pp |
| LoCoMo | 0.0459 | +10.95 pp |

`r = -0.23` across the four benchmarks; `r = +0.06` across 470 LongMemEval archives.
The paper predicts +0.95. Their causal control also fails here: projecting out the
top-3 directions leaves the whitening advantage largely intact on 3 of 4 benchmarks
(LME +11.59 -> +6.96, LoCoMo +9.11 -> +7.46, REALTALK +5.66 -> +2.92) and collapses it
only on PerLTQA (+1.41 -> +0.27).

**Most likely reconciliation (not yet confirmed against the paper's full text):** these
corpora are not anisotropic - the top direction holds only 4.6-8.4% of variance - so
they sit outside the paper's regime. The paper varies the ENCODER; this programme holds
the encoder fixed and varies the CORPUS. A literature session was dispatched to fetch
the paper and check its reported concentration range; until that returns, this is a
**non-replication with a plausible scope explanation, not a refutation**.

## 2. A correction to FINDING 2, imported from an unrelated conversation

A separate thread (the V55/TF-IDF+MRL line, with a different model) measured that
ranking axes by SAMPLE variance inflates the measured top-k share even under pure
noise: sorted top-48 of Gaussian noise gives 13.8% where the isotropic truth is 12.5%,
and manufactures a fake power law. That warning applies directly to this session's axis
work, which ranked axes on the SAME documents it then retrieved from.

Tested (VERIFIED, `v55_transfer.py`): rank the axes on HALF the documents, evaluate on
all. BOT-48 minus TOP-48 FR@3, in pp:

| benchmark | in-sample | split-half | random order |
|---|---|---|---|
| LongMemEval | +7.7511 | **+8.0277** | +0.3591 |
| PerLTQA | -12.7279 | **-12.9065** | -0.0494 |
| LoCoMo | +4.8137 | **+4.9755** | -0.7167 |
| REALTALK | +0.1786 | **+0.0613** | +0.3911 |

The effect survives out-of-sample ranking on three benchmarks and is slightly stronger
there, so it is not selection bias. The random-order null is ~0, confirming axis
identity matters. **But REALTALK collapses to noise level (+0.06 vs a +0.39 null), so
the published "4/4" is corrected to 3/4.** Also imported: the concentration measure's
noise floor is 13.8%, not the isotropic 12.5%, so any "2.85x concentration" figure
computed against 12.5% should be 2.7x.

## 3. My mechanism's quantitative leg is broken (own prediction, frozen, wrong)

Prediction written into the script before running: more variance concentration should
mean a larger whitening gain, since cosine over-weights a few axes more.

| benchmark | top-12 variance share | whitening gain |
|---|---|---|
| LongMemEval | 37.47% | +11.5851 pp |
| LoCoMo | 36.99% | +8.9150 |
| REALTALK | 40.83% | +5.7365 |
| PerLTQA | 41.52% | +1.2899 |

`r(concentration, gain) = -0.90` across benchmarks - the OPPOSITE of the prediction -
and `r = -0.002` across the 30 PerLTQA archives, i.e. nothing. The mechanism explains
the effect QUALITATIVELY and fails to predict its SIZE. Stated wherever it is cited.

## 4. A preregistered kill, specified by an independent session

A brainstorm session wrote a kill criterion in its `NEXT_BRIEF.md` before the answer was
known: *"restrict both arms to top-16-only vs bot-16-only axes per archive... if
Delta(bot16) <= Delta(top16) on LME or profile, the locus hypothesis is dead."*

Result (VERIFIED, `locus_prereg.py`, PerLTQA control passed exactly):

| unit | Delta(top16) | Delta(bot16) | verdict |
|---|---|---|---|
| LongMemEval | -9.2903 | -18.3265 | KILLS |
| LoCoMo | -4.0022 | -9.9188 | KILLS |
| REALTALK | -4.7945 | -8.2592 | KILLS |
| PerLTQA | -11.9382 | -13.1238 | KILLS |
| profile | -1.3508 | -18.9690 | KILLS |
| social_relationship | -13.7964 | -17.5051 | KILLS |
| dialogues | -0.9689 | -2.1577 | KILLS |
| events | -19.3094 | -18.7438 | supports |

Fired on both named units, 7 of 8 rows. **The locus hypothesis - "sign wins when the
signal sits in low-variance axes" - is DEAD.** Isolated in a narrow band, low-variance
axes are worse for the sign arm everywhere. What dies is the "WHICH axes" story; "axis
weighting matters" survives, established by intervention elsewhere.

Residual worth recording: `r(bot-top band gap, full-96 Delta) = -0.97` across the four
sections - the band contrast predicts the outcome almost perfectly but with the
OPPOSITE sign to the hypothesis. n=4, so a lead, not evidence.

## 5. Scope: the resolution ceiling does not arrive

Hamming on 96 bits has only 97 levels while cosine is continuous, so the sign arm was
expected to degrade as N grows. Measured by subsampling inside real archives
(`resolution_limit.py`) - occupancy of the K=3 boundary bucket:

| benchmark | N/8 | N/4 | N/2 | N |
|---|---|---|---|---|
| LongMemEval | 1.73 | 1.80 | 1.88 | 1.40 |
| PerLTQA | 1.88 | 1.88 | 1.78 | 1.72 |
| REALTALK | 1.79 | 1.78 | 1.66 | 1.76 |
| LoCoMo | 1.83 | 1.84 | 1.83 | 1.81 |

Flat at ~1.8 across an 8x range of N. As N grows the 3rd-nearest document moves into
the sparse tail, so competition at the boundary does not increase.

**My own error, disclosed:** the same script printed a linear projection to N=1,000,000
(~3,000 documents in the boundary bucket). The measurement in the table above
contradicts that projection, in the same run. The projection is withdrawn.

Effective resolution is also far below 97: only ~30 levels are populated and ~16 hold
90% of the mass.

## 6. Two independent routes converge on the nonlinearity

- A brainstorm session swept a per-axis CLIP from cosine (no clip) to Hamming (hard
  clip) and found an INTERIOR optimum beating both endpoints, flagging its own
  selection bias (max over 8 thresholds on one benchmark).
- Tested honestly here (`clip_heldout.py`): select the threshold on LongMemEval ALONE,
  apply frozen to the rest. PerLTQA +5.73 [+4.59, +6.86], LoCoMo +1.86 [+0.62, +2.87],
  REALTALK +0.12 [-0.52, +0.79]. **2 of 3 held-out benchmarks - not selection bias.**
- The soft version (cosine on tanh(C/sigma)) beats the sign arm on 4/4 with CIs
  excluding zero.

**Coordinator error, disclosed:** `clip_heldout.py` caps queries per archive at 120, so
its absolute FR@3 values are NOT the frozen headlines (PerLTQA reads 0.692934 against a
frozen 0.488945). The paired differences are internally valid but the control was not
reproduced in that script. `alpha_sections.py` reruns the full query set and passes.

## 7. The within-corpus split is reproduced by one knob

`alpha_sections.py` (full 8265 PerLTQA queries, control exact). Weighted cosine with
`w = v^(-alpha/2)`, Delta against plain cosine, per section:

| section | a=0 | a=0.5 | a=1.0 | a=2.0 |
|---|---|---|---|---|
| profile | 0.00 | +9.31 | +17.12 | **+25.23** |
| social_relationship | 0.00 | +3.32 | +3.67 | -3.55 |
| dialogues | 0.00 | +0.46 | +0.48 | -0.93 |
| events | 0.00 | +1.98 | +0.35 | **-10.95** |

Profile-minus-events spread: **+36.18 pp at alpha=2**, against the sign arm's +32.75 pp
between the same sections. One axis-weighting knob, identical documents, reproduces the
split the mechanism previously could not explain.

Caveat the brainstorm session raised and this run confirms: as alpha grows the two arms
CONVERGE (events weighted-minus-sign goes +12.39 -> +14.37 -> +12.74 -> +1.44), so part
of the "weighted cosine beats sign" result is the two becoming the same thing.

## 8. Two attacks the result survived

`k_and_ties.py`, all four controls exact.

**Tie accounting** - worst case, all ties resolved AGAINST gold:

| benchmark | worst | expectation | best | share from tie accounting |
|---|---|---|---|---|
| LongMemEval | +7.9184 | +10.0538 | +12.3936 | 21.2% |
| REALTALK | +4.2556 | +5.3001 | +6.6510 | 19.7% |
| LoCoMo | +5.1543 | +6.6550 | +8.3525 | 22.6% |
| PerLTQA | -7.7987 | -6.2747 | -4.5912 | -24.3% |

About a fifth of the margin is favourable tie accounting; four fifths is real
retrieval. On PerLTQA the share is negative - tie accounting works AGAINST the sign arm
there.

**K dependence** - Delta by K:

| benchmark | K=1 | K=2 | K=3 | K=5 | K=10 | K=20 |
|---|---|---|---|---|---|---|
| LongMemEval | +5.2778 | +7.3286 | **+10.0538** | +10.0124 | +6.9281 | **-1.7052** |
| PerLTQA | -6.0339 | -6.1012 | -6.2747 | -6.4885 | -9.0461 | -12.0845 |
| REALTALK | +0.6689 | +4.0128 | +5.3001 | +6.4824 | +6.6702 | +5.5947 |
| LoCoMo | +3.5038 | +5.9916 | +6.6550 | +7.9347 | +8.7553 | +6.2152 |

The programme's headline sits at the PEAK over K and **changes sign at K=20** on the
headline benchmark. The other three hold their sign throughout. This is a real scope
limit on "+10 pp" and should accompany it.

## Standing after this session

- Dead mechanism candidates: **ten** (norm informativeness, then the locus hypothesis).
- The published mechanism (axis equalisation) is **known literature**, independently
  replicated here, qualitatively right and quantitatively unpredictive.
- The remaining candidate contribution is the **link** between that literature and
  binary quantization, plus the measured scope limits (K dependence, tie-accounting
  share, N-independence of boundary occupancy).
- Coordinator errors disclosed today: six. All retained in the record with their
  corrections.
- Nothing here is the preregistered Task4F1 experiment; all of it runs on unsealed E1
  caches; `main` remains at `5ec3db6`.
