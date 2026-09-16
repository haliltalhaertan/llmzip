# LME channel ablation (stage-1 representation): does the LSA32 channel carry non-redundant signal?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Question

On RealTalk (n=705, 10 archive clusters) an ablation found dropping the LSA32
channel directionally better in 6/6 metric-scorer cells, but every 95% CI
included zero (inconclusive). The char channel was clearly valuable there.
This run re-tests the LSA-redundancy hypothesis on LongMemEval (470 archives /
470 queries, one question per archive), which has many more clusters and can
potentially settle the question. A negative result here is a useful finding:
effects have reversed between benchmarks before in this programme.

## Method (frozen)

- Archive text recipe (adapter v1 = v2 payload): memory text
  `[{haystack_date}] {role}: {content}` in flat (session, turn) order;
  query = question text only (`QUERY_DATE_DECISION = A_question_text_only`).
- Source blocks per archive: word TF-IDF(1,2; english stop words; sublinear) +
  char_wb TF-IDF(3,5; sublinear) + LSA32 TruncatedSVD on the word block
  (`random_state=5101`), each L2-normalized.
- Arms (final stage identical except the concat input; SVD96 `random_state=5204`,
  96 dims, L2-normalize, archive-mean centering, 12-byte sign coding):
  FULL = [LSA32|word|char] (production control), NO_LSA = [word|char],
  NO_CHAR = [LSA32|word], WORD_ONLY = [word]. `min(Z.shape) > 96` asserted for
  every arm x archive (no exclusions; LSA_ONLY correctly not attempted).
- Scorers: sym = -Hamming(doc bits, query bits);
  qscale = dot(doc bits as +-1, qC/sigma) with sigma = per-archive std of
  DOCUMENT C columns (ddof=0, floored at 1e-12; fit on documents only).
- Ranking: deterministic top-K (score DESC, then ascending
  SHA256("top10-r1|"+archive_id+"|"+row), then ascending row); exactly K ids,
  no duplicates, gold-unaware; archive_id = question_id.
- Metrics: Hit@10, FR@3 = |gold n top3|/|gold|, Hit@3, expected-Hit@10 under
  uniform ties (audit_baseline_lib, read-only import).
- Contrasts: each arm MINUS FULL; paired archive-clustered bootstrap, 20000
  reps, seed 20260916.

## Adapter-version determination

cache_repr carries no memory IDs, so v1 vs v2 cannot be distinguished from the
cache directly. v2's own code proves its archive payload (memory_text list and
order) is exactly identical to v1's (`payload_identical_to_v1`; the v2 patch is
identity-only: memory_id gains `s<session_position>`, excluded from text/fit).
The rebuild uses that shared payload recipe with the frozen seeds and
reproduces sign(C) bit-exactly on all 470 archives (G1), so the representation
is consistent with both adapter versions; the v2 payload-identity proof is how
this was determined.

## Fidelity gate (BLOCKING; written before any ablation number)

(TABLE PENDING)

## Results

(TABLE PENDING — per-arm means under both scorers; contrasts vs FULL with
95% bootstrap CIs; per-archive values in per_query.jsonl / RESULTS.json.)

## Verdict on the LSA-redundancy hypothesis (on THIS benchmark)

(PENDING — SUPPORTED / REFUTED / INCONCLUSIVE with CIs + RealTalk comparison.)

## Caveats

- cluster == question for LME (one question per archive), so the bootstrap
  assumes archive independence. This is NOT established: LME questions may
  share source sessions (the v2 adapter itself documents cross-question session
  reuse and a single connected dependency component on the primary cohort).
  The CIs below are therefore descriptive, NOT confirmatory.
- Deterministic sym Hit@10 exceeds expected-Hit@10 on LME (86.3830 vs
  86.0773); that ordering is real (tie-heavy Hamming arm) and was reproduced,
  not "corrected".
- No durable test collateral was added: this directory has no maintained test
  harness and the governing spec fixes the deliverable list; verification is
  the independent replay script (scratch, /tmp) plus coordinator re-derivation
  from per_query.jsonl.

## Cost

(TABLE PENDING — per-arm Z feature counts, build times, 12 B/doc payload.)
