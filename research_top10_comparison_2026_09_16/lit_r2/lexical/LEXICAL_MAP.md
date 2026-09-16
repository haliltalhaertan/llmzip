[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LEXICAL MAP — why plain lexical search keeps winning, and what it means for a compressed code

Role: literature analyst. No experiments, no web access. Every paper-related
statement below is [RECALLED-FROM-MEMORY] with a confidence level, or it is
explicitly marked UNVERIFIED. Nothing here is a verified quote. Programme
numbers are [MEASURED HERE] from the coordinator's digest
(`digest_r1/FINDINGS_DIGEST.md`), the ladder audit
(`incoming_20260916b/a_ladder/LADDER_AUDIT.md`), and the ideas audit
(`incoming_20260916b/b_ideas/IDEAS_AUDIT.md`) — not from my own runs.
Derivations are [PROOF-SKETCH]; hypotheses are [CONJECTURE] with falsifiers.

Already-scanned sources (not re-reported as new): the 11 full + 13 partial
sources in `inventory/literature/DO_NOT_RESCAN.md`, plus round 1 of this job
(`digest_r1/lit/LITERATURE_MAP.md`: ITQ, all-but-the-top, RRF, Husbands
term-norm, leverage scores). [MEASURED HERE — established by reading those files.]

Our system (for reference): per archive, Z = [LSA32(word) | word-tfidf |
char-tfidf] → TruncatedSVD(96) → normalize → center → sign → 96 bits = 12 B/doc.
[MEASURED HERE — `digest_r1/FINDINGS_DIGEST.md`.]

---

## Q1. Is dense/learned retrieval KNOWN to be weak vs BM25 on tiny collections, short docs, high-singleton vocab? — verdict: PARTIALLY KNOWN mechanism classes / OPEN as a studied regime

**Verdict: the direction (BM25 strong where dense is starved of data or
lexical signal) is KNOWN folklore with one solid recalled anchor (BEIR
zero-shot); the specific regime — few-hundred-document collections, short
docs/queries, per-collection fitting, ~46% singleton vocabulary — is, to my
recall, UNSTUDIED. Confidence: medium on the folklore, medium-high that no
direct study exists (a negative claim; needs the targeted search in
FETCH_QUEUE item F1 to confirm).**

### What I recall honestly

- BEIR benchmark (Thakur et al., 2021). [RECALLED-FROM-MEMORY, medium-high
  confidence on existence and headline, low on details.] I recall a
  heterogeneous zero-shot benchmark (roughly 18 datasets) on which dense
  models trained on MS MARCO (e.g. DPR-style, ANCE, TAS-B) frequently lost to
  plain BM25 out-of-domain, and "BM25 is a strong zero-shot baseline" became
  the field's working summary. What it settles for us: dense-without-in-domain
  training losing to BM25 is an established, citable pattern — our per-archive
  SVD has no cross-archive training at all, so it is in the data-starved
  corner where BEIR says BM25 should be expected to win. What it does NOT
  settle: BEIR corpora are, to my recall, 10^3–10^6 documents (smallest I
  recall are SciFact at ~5K and NFCorpus at ~3.6K — UNVERIFIED), i.e. an order
  of magnitude above our 293–1548 docs/archive [MEASURED HERE — brief G2].
  Nobody, to my recall, ran the few-hundred-document comparison. UNVERIFIED
  until fetched (FETCH_QUEUE F1).
- DPR (Karpukhin et al., 2020) and follow-ups. [RECALLED-FROM-MEMORY, medium
  confidence.] I recall DPR beating BM25 on NQ/TriviaQA (10^6-scale Wikipedia)
  *with* large supervised training, and I recall follow-up discussion that the
  dense advantage concentrates on paraphrase / lexical-mismatch questions while
  BM25 keeps entity/rare-term questions. If true, this predicts exactly our G3
  shape (we lose the rare band by 14.37 pp [MEASURED HERE — FINDINGS_DIGEST]).
  But the DPR analysis I half-remember is post-hoc and on large corpora; it
  does not test small collections. UNVERIFIED (F2).
- LSI-era small collections. [RECALLED-FROM-MEMORY, low-medium confidence.]
  Early LSI work (Deerwester et al. 1990 and TREC-era follow-ups) routinely
  evaluated on ~10^3-document collections (MED, CISI, CRAN — venue/year/details
  UNVERIFIED), because that was the era's standard scale. So "SVD methods on
  small collections" was once the *default*, not a degraded regime — but those
  studies compared LSI against raw TF-IDF/vector-space baselines of the same
  era, not against BM25 (which postdates/postspecializes them; Robertson &
  Zaragoza 2009 BM25 overview is decades later). There is, to my recall, no
  paper that pits a per-archive LSI code against tuned BM25 at n≈400 and
  reports the small-N interaction. If the coordinator finds one, Q1 moves to
  KNOWN; I would bet against it. [CONJECTURE — falsified by any fetched
  small-N dense-vs-BM25 comparison.]
- Per-collection vs global fitting. [RECALLED-FROM-MEMORY, medium confidence
  on the structural fact; CONJECTURE on the consequence.] LSI/SVD is
  per-collection *by construction* (it diagonalizes that collection's
  term-document matrix) — that is definitional, no citation needed. Modern
  dense encoders are global (one encoder, trained on 10^5–10^7 pairs, applied
  frozen to new corpora). Our pipeline is therefore structurally closer to
  1990 LSI than to 2020 dense retrieval, and "per-collection fitting" needs no
  literature to describe — but whether per-collection fitting *helps or hurts
  at n≈400* is, to my recall, unstudied. My hypothesis: it hurts, because
  every estimated quantity (IDF, means, σ, singular vectors) is fit on ~400
  samples (see Q2's [PROOF-SKETCH]). [CONJECTURE — falsified if a fetched LSI
  study shows flat quality down to n≈200, or if our own cross-archive-shared
  encoder ever beats per-archive fitting.]
- Short documents/queries. [RECALLED-FROM-MEMORY, low confidence, near
  folklore.] I recall scattered findings that dense advantages grow with
  document length (more paraphrase surface for lexical mismatch; long-doc
  semantic matching) and shrink on short, entity-heavy, question-like text —
  e.g. discussion around SciFact/Quora (symmetric short-text) vs FiQA/HotpotQA
  in BEIR-era analysis. I cannot attribute this to a specific paper from disk.
  Mechanism sketch needing no citation: with 21–36-token docs and 8–13-token
  queries [MEASURED HERE — brief G2], there is little lexical redundancy for
  distributional smoothing to exploit and little paraphrase mass for it to
  rescue; exact-match features carry most of the information. UNVERIFIED (F1/F2).
- Singleton vocabulary (45.6% df=1, median df=2 [MEASURED HERE — brief G2]).
  That *level* of singleton dominance on short conversational text is, to my
  recall, not a studied experimental condition anywhere in dense-vs-BM25
  literature. That Zipfian skew *exists* is textbook (Zipf's law / hapax
  legomena — high confidence as folklore, no citation offered). The
  consequence for us is mathematical, not literary: singleton columns have
  average retention k/n ≈ 0.19–0.23 (see Q2), and BM25's IDF maximally rewards
  exactly the features SVD must discard. No fetch can change that arithmetic;
  a fetch can only tell us whether anyone else measured the collision.

### Bottom line for reporting

- Say: "dense losing to BM25 without in-domain training data is the BEIR-era
  expectation (to verify); our regime is an order of magnitude smaller than
  BEIR's smallest corpus, so the *magnitude* of our gap (5.67 pp before any
  compression [MEASURED HERE — FINDINGS_DIGEST]) is a NEW data point, not a
  rediscovery." That sentence is the honest (a)+(b) split the brief asks for.
- Do NOT say: "prior work shows dense fails on small collections." To my
  recall, no such paper exists, and claiming it would be exactly the
  confidently-worded fake citation the brief forbids.

---

## Q2. Minimum collection size for LSI/LSA; degradation on small collections — verdict: OPEN (no recalled study); small-N harm is PROVABLE as mechanism, CONJECTURAL as cause of G1

**Verdict: I recall NO literature on a minimum collection size for LSI/LSA or
on small-collection degradation curves. Confidence: medium (negative claim;
needs FETCH_QUEUE F3 to upgrade to a documented null). The most likely
explanation of G1 can nevertheless be grounded WITHOUT any paper, in three
checkable steps below. Q2 is therefore the question where derivation, not
fetching, does the work — fetching only rules out prior art.**

### The three-step grounding ([PROOF-SKETCH] throughout; numbers checked just now)

1. **Rank arithmetic: at n≈400, k=96 is barely a compression.**
  k/n = 96/894 ≈ 0.107 (RealTalk mean), 96/410 ≈ 0.234 (PerLTQA mean),
  96/500 = 0.192 (LME) [PROOF-SKETCH — recomputed this session from brief G2
  sizes]. On a 10^5-document TREC collection, k=96–300 keeps <0.3% of
  dimensions: SVD is a drastic denoising bottleneck and the "latent" story is
  doing real work. On our archives it keeps 11–23% of full rank: the
  bottleneck is shallow, denoising is weak, and the representation is closer
  to "a rotated, truncated TF-IDF" than to a semantic space. This does not
  need LSI literature — it is counting.
2. **Retention arithmetic: unique features cannot survive, on average.**
  The digest's verified identity (sum of retentions = k, checked to 1e-14
  [MEASURED HERE — FINDINGS_DIGEST]) implies average retention k/n ≈ 0.19 for
  singleton features, and the measured medians (df=1 ≈ 0.15–0.19 vs df>20 ≈
  0.53–0.55 [MEASURED HERE — FINDINGS_DIGEST]) match. With 45.6% of vocabulary
  at df=1 [MEASURED HERE — brief G2], roughly half the vocabulary types sit in
  the discard band. BM25, meanwhile, gives its *largest* weights to exactly
  these features. G1's 5.67 pp representation gap is therefore the expected
  sign of a head-on collision between the two methods' opposite treatments of
  singletons — derived, not cited.
3. **Estimation noise: everything is fit on ~400 samples.**
  IDF, column means, per-dim σ, and all 96 singular vectors are estimated
  per archive on 293–1548 documents [MEASURED HERE — brief G1/G2]. Standard
  errors on rare-feature statistics at that n are large by construction
  (a df=1 feature's archive frequency is estimated from a single occurrence —
  no theorem needed). A globally-trained dense encoder amortizes this
  estimation over 10^5+ training pairs; our encoder cannot. [CONJECTURE that
  this noise is a *large* component of the 5.67 pp — falsified if a
  shared/cross-archive encoder (fit once, applied per archive) does NOT
  recover any of the gap. Note the B2 shared-circulant prototype lost by ~25
  pp [MEASURED HERE — IDEAS_AUDIT §B2], but that prototype changed the feature
  family AND the transform together and refused single-cause attribution, so
  it does NOT falsify this conjecture — it is the wrong control.]

### What I recall about LSI sizing (all weak; none answers Q2)

- Dimensionality choice k≈100–300 as a TREC-era optimum (Dumais and
  follow-ups). [RECALLED-FROM-MEMORY, low confidence on attribution and
  numbers.] This is about k given a LARGE n, not about minimum n given k.
  Does not transfer: our k=96 is at the bottom of that range while our n is
  two orders of magnitude below theirs.
- Log-entropy weighting beating raw TF-IDF for LSI on TREC collections.
  [RECALLED-FROM-MEMORY, low confidence.] Relevant to *weighting*, not to
  collection size. (Round 1 already logged an LSI-weighting fetch as rank 9;
  keep it there, do not duplicate — see FETCH_QUEUE note.)
- Landauer & Dumais-style "how much text does LSA need to learn word meaning"
  (I recall a Psychological Review-scale paper using encyclopedia-sized
  input — details UNVERIFIED). [RECALLED-FROM-MEMORY, low confidence.] If it
  exists as I remember, it studies *training-corpus size for word knowledge*,
  not *retrieval quality vs collection size* — adjacent, not answering.
- Husbands et al. 2005 (term-norm dominance in LSI). Coordinator-VERIFIED to
  exist; round 1 covers it. It explains the *mechanism* (high-norm terms hog
  the rank budget) but, on the round-1 gloss, says nothing about collection
  size.

### Bottom line for reporting

- Grounded without literature: small-N harm follows from (1)–(3) above, all
  checkable on disk. The honest report sentence is: "At 293–1548 docs/archive
  with k=96, the SVD keeps 11–23% of full rank and discards singleton
  features at ~0.19 average retention, while BM25 maximally rewards them; the
  5.67 pp pre-compression gap is the predicted sign of that collision."
- Ruled out as an explanation: NOTHING is ruled out — quantization is ruled
  out as the *main* cause (1.83 pp [MEASURED HERE]), but among
  representation-side causes (small-N noise vs TF-IDF feature poverty vs
  channel fusion), small-N is the leading hypothesis, not a finding.
  [CONJECTURE — the discriminating test is shared-vs-per-archive fitting with
  the feature family held fixed, which has not been run.]
- Fetch value of F3 is purely defensive (confirm the null so reviewers cannot
  cite a study we missed), not explanatory.

---

## Q3. Reranking washes out first-stage quality differences — verdict: KNOWN as field practice and qualitative finding; OPEN as a stated theorem with conditions (answered most fully, as requested)

**Verdict: every practitioner knows the reranker dominates the cascade; I
recall NO paper that states the washout as a measured result with explicit
conditions (recall ceiling + candidate depth + the failure cases). Confidence:
high on the practice, medium on the qualitative finding, low-medium that any
single citable source contains both the washout AND its conditions. This is
the highest-consequence question, so it gets the full treatment: (i) what we
measured, (ii) the two-line mechanism that predicts it, (iii) what the field
knows, (iv) the exact conditions when it does NOT hold, (v) what it means for
the 12-byte premise.**

### (i) What we measured ([MEASURED HERE] throughout this subsection)

- FIKIR1 applied a fixed BM25 text reranker to the top-50 qscale96 candidates:
  FR@3 gains over the first stage of +3.43 (LME) / +4.22 (PerLTQA) / +6.97
  (LoCoMo) pp — but the code's net contribution over plain full-corpus BM25
  alone is −0.33 / +0.33 / +1.07 pp. [MEASURED HERE — IDEAS_AUDIT §Package 1,
  recomputed from OZET.json; the +1.07 supersedes the brief's +1.06 by rounding.]
- The crossover: on LME the WORSE first stage (hamming96, FR@3 53.86... note:
  brief G5 prints 53.86; IDEAS_AUDIT's rerank table uses hamming96_bm25 58.23
  vs qscale96_bm25 57.70 — the ordering claim is what matters) ends up BETTER
  after reranking (58.23) than the better first stage (54.27 → 57.70).
  [MEASURED HERE — brief G5 + IDEAS_AUDIT §Package 1.] Both reranked scores sit
  within ~0.3 pp of plain BM25_full (58.03/57.13 on LME/PerLTQA).
  [MEASURED HERE — IDEAS_AUDIT §Package 1.]
- Cost: raw text for reranking costs 76× the code; the BM25 index another
  0.9–1.5× the text. [MEASURED HERE — brief G5.] FIKIR1's own accounting:
  LME 3.14 MB packed code+σ vs 64 MB BM25 JSON / 351 MB Python IDF objects /
  238 MB raw text; rerank adds +2.37 ms LME and full BM25 alone runs in
  0.10–0.14 ms end-to-end (panel timings, not SLA). [MEASURED HERE —
  IDEAS_AUDIT §§Package 1/Q4.]
- The package authors themselves refuse the system claim ("bütün iyileşmeyi
  küçük kodun özel bir başarısı diye yorumlayamayız") and the auditor confirms
  the coordinator's decisive line. [MEASURED HERE — IDEAS_AUDIT §Package 1.]
- Corroborating context: the oracle-reranker ceiling (FR@3 22.41→61.30
  RealTalk, 53.24→76.52 PerLTQA, 54.27→92.62 LME at 100 candidates
  [MEASURED HERE — FINDINGS_DIGEST]) shows pools already contain the evidence;
  and the ladder shows 192→384 dims going flat-to-negative on 2/3 benches
  [MEASURED HERE — LADDER_AUDIT §Q3], i.e. first-stage capacity is not the
  binding constraint even before reranking.

### (ii) The mechanism in two lines ([PROOF-SKETCH] — no paper needed)

A reranker can only reorder the candidate pool it is given. So, with
pool = first-stage top-M and final = reranker top-3:

- **Upper bound:** final Hit/FR ≤ pool recall (gold outside the pool can never
  surface). First-stage quality matters *only* through pool gold-content.
- **Washout:** suppose two first stages have pool gold-content p1 ≈ p2 but
  different first-stage orderings (hamming vs qscale FR@3 53.86 vs 54.27 differ
  by <0.5 pp while their *pools at depth 50* overlap heavily — the reranked
  convergence to 58.23 vs 57.70, both ≈ BM25_full 58.03, is exactly this
  signature). A reranker that promotes contained gold to top-3 with
  probability r gives finals p1·r ≈ p2·r: the ordering gap is erased by
  construction. The crossover (worse→better) needs only tiny pool-content
  noise between the two first stages — it is the expected null, not an
  anomaly. [CONJECTURE on the exact pool overlap — falsified if per-query pool
  artifacts show the two first stages' depth-50 pools differ in gold content
  by more than ~2 pp; the OZET-level numbers predict overlap, but I did not
  row-check per-query CSVs.]
- Arithmetic illustration (not our data, just the shape): p1=0.60 vs p2=0.55
  pools with r=0.9 reranker give 0.54 vs 0.5225 — a 5 pp pool gap compresses to
  1.75 pp final. The better pool still wins, but margins shrink by factor r,
  and ordering-only differences vanish entirely. [PROOF-SKETCH — recomputed
  this session.]

### (iii) What the field knows ([RECALLED-FROM-MEMORY] with confidences)

- **Retrieve-and-rerank as the dominant architecture: KNOWN, high confidence.**
  I recall the MS MARCO-era consensus (2018–2021): first-stage retrieval
  (BM25 or dense, top-100/1000) followed by a neural cross-encoder reranker
  (monoBERT — Nogueira & Cho 2019, arXiv:1901.04085; monoT5/duT5 follow-ups)
  defines the leaderboard, and the reranker supplies most of the quality gain.
  I am medium-high confident the monoBERT paper exists under approximately
  that title/date and reports large gains from reranking BM25 top-1000; I am
  low-confidence on any specific number or ablation I might half-remember. The
  Anthropic contextual-retrieval page (ALREADY SCANNED — not new) exhibits the
  same architecture (150 candidates + rerank). So "reranker dominates the
  cascade" is established practice visible in every already-scanned hybrid
  source — our FIKIR1 result *joins* that pattern rather than discovering it.
- **BM25 + neural reranker as the baseline dense struggles to beat end-to-end:
  KNOWN at folklore level, medium confidence.** I recall BEIR-era discussion
  (and I believe BEIR itself reports a BM25+rerank or dense+rerank comparison —
  UNVERIFIED) that a tuned BM25 first stage with a strong reranker matches or
  beats many dense-first-stage cascades, precisely because pool gold-content
  converges at depth 50–1000 while the reranker does the differentiating work.
  Our −0.33/+0.33/+1.07 net over plain BM25 [MEASURED HERE] is a crisp instance
  of this folklore with an unusually honest cost ledger attached.
- **The washout stated as a *measured ablation* (vary first stage, fix
  reranker, report convergence): PARTIALLY KNOWN, low-medium confidence.**
  I genuinely recall seeing "reranking BM25 vs dense first stages gives
  similar final numbers" figures in reranker papers and blog-era ablations, but
  I cannot attribute one to a specific paper/figure from disk. The closest
  citable shape I can name is the monoBERT→monoT5→duoT5 lineage plus MS MARCO
  leaderboard analyses (Nguyen et al. 2016 for the dataset; Bajaj et al. for
  the overview — author/year details UNVERIFIED). The coordinator should fetch
  F4/F5 and grade them: PASS = a figure or table fixing the reranker and
  varying the first stage with finals converging; FAIL = only first-stage or
  only reranker ablated in isolation.
- **ANN-literature framing ("first stage is a recall/cost device"):
  KNOWN, medium-high confidence.** I recall the approximate-nearest-neighbor
  literature (Faiss/IVF/PQ/HNSW line; ScaNN anisotropic loss per round 1) as
  explicitly optimizing recall@depth vs latency/bytes *under the assumption*
  that a downstream ranker consumes the shortlist. In that framing, reporting
  first-stage Hit@10 as system quality is already understood to be the wrong
  metric — recall@M and bytes/latency are the first stage's metrics. This is
  the single most useful prior-art frame for our programme, and it survives
  even if no IR paper states our exact washout.

### (iv) Exact conditions when reranking does NOT wash out first-stage differences

These follow from the pool bound in (ii) — stated as checkable conditions,
not recollections:

1. **Recall ceiling (the hard one).** If pools differ in gold *content* by Δp,
  finals differ by up to Δp·r — no reranker recovers gold outside the pool.
  First stage matters iff candidate depth × collection difficulty leaves
  headroom: at M=50 on our small archives pools may already saturate (cf. LME
  gold-in-pool = 100% at 500 candidates [MEASURED HERE — FINDINGS_DIGEST]),
  which is WHY the washout appears here and might NOT appear at M=10 or on a
  corpus where BM25 pool recall is poor. [CONJECTURE — falsified if shrinking
  M to 10–20 does not reopen a first-stage gap; directly testable on disk
  from stored per-query rows without new literature.]
2. **Reranker fallibility.** A weak/biased reranker (small cross-encoder,
  domain-mismatched, or BM25-itself-as-reranker — note ours IS BM25, i.e. the
  reranker shares the lexical inductive bias of one first stage) preserves
  more of the first-stage gap than an oracle. Our reranker being BM25 likely
  *overstates* plain-BM25-full's standing: a semantic reranker could reopen a
  code advantage. [CONJECTURE — falsified if a cross-encoder reranker (e.g.
  monoT5-class) applied symmetrically still shows convergence; FETCH F5 would
  let the coordinator check whether published cascades show reranker-identity
  interactions.]
3. **Depth–cost coupling.** Deeper M raises pool recall (good for washout) but
  costs reranker scorings linearly (bad for the system bill). The optimal M
  differs per first stage; fixing M=50 for all stages (as FIKIR1 prespecified
  [MEASURED HERE — IDEAS_AUDIT]) can mask a first stage that needs M=200 to
  fill its pool. Any "first stage doesn't matter" claim must be read as
  "at fixed M=50 with THIS reranker." [Methodological point — no fetch needed.]
4. **Complementary pools.** If first stages retrieve *different* gold (our RRF
  finding: 49 code-only + 67 BM25-only queries at depth 100 [MEASURED HERE —
  FINDINGS_DIGEST]), a reranker over the UNION pool can beat every
  single-source cascade. FIKIR1 reranked only the code's pool, never the
  union — the union+rerank cell is unmeasured. [CONJECTURE that union+rerank
  is the best cascade — falsified if measured and flat; actionable without
  literature.]

### (v) What it means for the 12-byte premise (the uncomfortable part, stated plainly)

- If the deployed system includes raw text + a reranker, the compact code's
  measured contribution is −0.33/+0.33/+1.07 pp at 76×+ text cost
  [MEASURED HERE] — and the field, to my recall, already operates cascades
  where the first stage is priced on recall-per-byte, not on standalone
  quality. Under that accounting our code is not "a worse BM25"; it is a
  first-stage candidate that must beat BM25-full or BM25-pool on
  recall@M-per-byte — a bar it has not been measured against (FIKIR1 measured
  FR@3 finals, not pool-recall@50 per byte).
- If the deployed system has NO reranker (the actual 12-byte premise: no text,
  no index, just codes), then G5 is out of scope by construction and the
  relevant comparison remains code-vs-BM25 standalone (54.18 vs 49.65
  [MEASURED HERE]) — but then the "12 bytes" framing must survive Q4's storage
  audit (per-archive σ/means/encoder state are uncharged auxiliaries;
  LADDER_AUDIT §Q1 already flags ~10 GB service-serialized state on LME
  [MEASURED HERE]).
- Either way, the programme's next honest metric is **pool recall@M per byte
  at fixed M**, not first-stage Hit@10 and not reranked FR@3 — a conclusion
  that needs no citation (it follows from the pool bound) but is, to my
  recall, exactly how the ANN literature already evaluates first stages
  (UNVERIFIED pending F6; if confirmed, cite it and stop defending Hit@10).

---

## Q4. Standard practice for reporting STORAGE — verdict: UNVERIFIED / MIXED-TO-MY-RECALL; do not quote any field-practice claim until the coordinator audits paper by paper

**Verdict: OPEN. My honest recollection is MIXED practice (low-medium
confidence in the aggregate, low confidence on any specific paper), and round
1 was right to refuse to guess. This subsection gives (a) my best recollection
with confidences, (b) why the question matters more than the answer, and
(c) exactly what to audit (FETCH_QUEUE F7). Nothing in (a) may be cited.**

### (a) Best recollection (all [RECALLED-FROM-MEMORY], none quotable)

- Dense single-vector papers (DPR-class): I recall storage reported as dims ×
  bytes (e.g. 768 × 4 B) for the vector index, with ANN structure overhead
  (IVF lists, HNSW graphs) sometimes footnoted and raw-text/passage-store cost
  essentially never charged. Confidence: low-medium. (DPR itself I recall as
  reporting index size/time via Faiss — UNVERIFIED.)
- Binary-code papers (BPR — ALREADY SCANNED, so no new fetch needed for the
  paper itself): storage as bits/doc is the headline by construction. Whether
  BPR charges query-encoder, hash-table, or rescore state in the same number
  must be read off the STORED copy (`sources/bpr_full_recovered.md`), not from
  my memory — I decline to recall it. Confidence: none offered; audit, don't ask me.
- Multi-vector papers (ColBERT-class): I recall token-vector storage stated
  explicitly (tokens × dims × bytes — thousands of bytes/doc), precisely
  because the cost is the paper's known weakness. Confidence: medium that the
  weakness is discussed, low on whether it is in a table or a footnote.
- Learned-sparse papers (SPLADE/uniCOIL/DeepImpact-class): I recall inverted
  index size (postings/MB) reported as a first-class metric alongside FLOPs —
  this family is, to my recall, the most honest about index bytes because
  sparsity IS the method. Confidence: medium-low, UNVERIFIED.
- BM25 baselines inside neural papers: I recall Lucene/Anserini/Pyserini index
  sizes essentially never reported; BM25 is costed as "free baseline."
  Confidence: low-medium. If true, it cuts BOTH ways for us: the field lets
  BM25 ride free (so our 5.8× honest accounting [MEASURED HERE —
  FINDINGS_DIGEST] is stricter than the norm — a methodological contribution),
  but it also means nobody will credit our strictness unless we force the
  comparison (report both conventions side by side).
- Reranker papers: I recall model parameters and latency reported, index/text
  cost of the first stage not re-charged. Confidence: low-medium.
- Net recollection: there is no field-wide storage-accounting standard to my
  recall — vector-bytes-only is the modal convention, full-system bytes the
  rare exception. **This paragraph is UNVERIFIED aggregate impression, not a
  finding. The coordinator must replace every clause with a per-paper audit
  (F7) before any of it constrains reporting.**

### (b) Why our position is strong regardless of what the audit finds

Our honest numbers exist and are ledger-grade: codes+σ 115,008 B vs varint
delta-gap BM25 index 670,511 B (~5.8×) vs pickle 1,450,229 B (explicitly NOT
quotable) vs index+raw-text 1,669,165 B on RealTalk/8944 docs [MEASURED HERE —
FINDINGS_DIGEST]; service-serialized state ~10 GB LME / ~150–176 MB PerLTQA
[MEASURED HERE — LADDER_AUDIT §Q1]; σ overhead ~12.9% [MEASURED HERE —
IDEAS_AUDIT §HATA]. These need no citation and survive any audit outcome:

- If the audit finds vector-bytes-only is the norm → report BOTH: "12 B/doc
  payload (field convention) | full-system bytes (honest convention)" and let
  the reader see the gap. Our 12-byte framing is then "meaningful under field
  convention, misleading as system cost" — say exactly that.
- If the audit finds full-system accounting somewhere → cite it as precedent
  and adopt it as primary.
- Either way, never quote the pickle number and never quote payload without
  the encoder caveat (both already enforced by the audits [MEASURED HERE]).

### (c) Audit instructions

Ranked per-paper audit list with pass/fail criteria is FETCH_QUEUE F7. The
rule for the coordinator: for each paper record (1) the exact storage number
quoted, (2) what scope it covers (payload / +index / +text / +model), (3) what
it omits that we charge ourselves for — then decide our reporting convention
by precedent, not by my recollection.

---

## Q5. Non-circular stratifications for the lexical-vs-dense gap — verdict: ACTIONABLE NOW; 3 concrete proposals (2 from first principles, 1 with a literature anchor)

**Verdict: G3's circularity diagnosis is correct (bucket defined by BM25's own
scoring quantity; BM25 scores ~zero on 97.8–100% of the "common" bucket by
construction so the "win" is degenerate with ~93% joint failure [MEASURED
HERE — brief G3]). The fix needs no literature: any bucketing statistic
computable WITHOUT either system's scoring function breaks the circle. I
propose three, ordered by implementability on disk today, each with definition,
non-circularity argument, predicted outcome, and falsifier. Confidence: high
that all three are non-circular (verifiable by inspection of the definitions);
predictions are [CONJECTURE].**

### S-A. Binary term-overlap split (first principles; run first — cheapest, hardest to game)

- **Definition:** after a FIXED, pre-registered tokenizer+stemmer (frozen
  BEFORE seeing outcomes; must differ from neither system's pipeline by
  tuning — pick e.g. lowercase + Porter + stopword removal and write it down
  first): bucket = OVERLAP (query ∩ gold shares ≥1 content token) vs NO-OVERLAP
  (zero shared content tokens). Optional refinement: 0 / 1 / ≥2 shared tokens.
  Report Hit@10 for CODE and BM25 per bucket plus bucket shares.
- **Why non-circular:** the bucketing statistic is a SET operation on strings.
  It uses no IDF table, no BM25 formula (no k1/b/saturation/length-norm), no
  SVD, no σ, no learned weight of any kind. Neither system's scoring function
  appears in the bucket definition — inspectable in one line of code.
  Residual caveat (honest): the tokenizer choice still affects bucket
  assignment at the margin (the digest already notes two tokenization rules
  move the rare band 341↔412 [MEASURED HERE — FINDINGS_DIGEST]), so
  pre-register the tokenizer and report both rules as robustness — do not pick
  the rule post-hoc.
- **What it would show [CONJECTURE]:** BM25's +14.37 pp rare-band edge should
  concentrate INSIDE the OVERLAP bucket (BM25 monetizes shared rare terms; the
  code cannot retain them per Q2), while any code advantage should appear ONLY
  in NO-OVERLAP (the paraphrase pocket where exact match scores zero for both
  lexical methods and distributional similarity is the sole signal). The
  digest's no_shared band (n=24, CODE 20.83 vs BM25 16.67 [MEASURED HERE —
  FINDINGS_DIGEST]) already hints at this shape but is underpowered — S-A is
  essentially that band analysis with adequate n (the OVERLAP/NO-OVERLAP split
  will be far more balanced than 24/681) and without the IDF-defined bands.
  Falsified if: BM25 also wins NO-OVERLAP (then our loss is not about rare
  terms at all — it would implicate representation quality globally), or the
  code wins inside OVERLAP (then the singleton-retention story of Q2 is wrong).
- **Literature anchor:** binary overlap / lexical-match-vs-mismatch splits are,
  to my recall, standard in QA-retrieval analysis (I recall DPR-era discussion
  of lexical-overlap bias in NQ and "lexical vs semantic" BEIR commentary —
  UNVERIFIED, F2). If the coordinator confirms, cite as precedent; if not, the
  split stands on its own logic regardless.

### S-B. Query-type / paraphrase-rate split (literature-flavored; answers "what to DO about it")

- **Definition:** classify each query WITHOUT either retriever: (i) by surface
  form — ENTITY/verbatim-seeking (query contains a quoted span, proper noun,
  or rare string also present verbatim in some doc) vs DESCRIPTIVE (all other);
  or (ii) by paraphrase grade — a THIRD-PARTY judge (frozen cross-encoder or
  LLM, fixed before analysis; or cheaper: character-3-gram Jaccard between
  query and gold, threshold pre-registered) grades query–gold surface
  similarity into HIGH/MID/LOW. Buckets are the grades.
- **Why non-circular:** the grader is frozen third-party machinery (or a
  string-similarity formula), not our SVD pipeline and not BM25. Using
  char-3-gram Jaccard is especially clean: it shares no component with either
  scorer (our char-TFIDF channel uses word-adjacent TF-IDF features through
  SVD, not raw Jaccard — state this explicitly when reporting so the auditor
  can check the non-overlap).
- **What it would show [CONJECTURE]:** predicts the ACTIONABLE split — if the
  code wins LOW-similarity (true paraphrase) and loses HIGH-similarity
  (verbatim), the two systems are complementary by query type and the RRF gain
  (+5.67/+3.12 [MEASURED HERE]) is explained as routing signal: route
  verbatim queries to BM25, paraphrase queries to the code. Falsified if: the
  code wins nowhere along the grade (then there is no routable pocket and RRF
  is just variance-averaging), or BM25 wins LOW too (then BM25's win is not
  lexical at all — suspect gold-construction bias toward retrievable phrasing).
- **Literature anchor:** query-type / difficulty stratification is old IR
  practice — I recall TREC Robust (2004) hard-vs-easy topics and the query
  performance prediction (QPP) literature (pre-retrieval predictors: IDF-based
  specificity, query length, overlap statistics — Hauff et al.-era; details
  UNVERIFIED, F8). QPP is the citable precedent for "predict difficulty WITHOUT
  running the scorer," which is exactly the non-circularity principle. Note the
  trap honestly: classic QPP predictors USE IDF — so cite QPP for the
  *principle* (pre-retrieval stratification) while using IDF-FREE statistics
  (overlap counts, length, Jaccard) for the *implementation*.

### S-C. Archive-level composition split (diagnoses the cross-benchmark reversal, not just the gap)

- **Definition:** bucket ARCHIVES (not queries) by pre-registered corpus
  statistics: singleton rate (% vocab df=1), mean doc length, query–gold
  corpus-level overlap rate (fraction of queries with ≥1 shared content token
  under the S-A tokenizer). Then plot per-archive CODE−BM25 delta against each
  statistic. Every statistic is a count, computable before either scorer runs.
- **Why non-circular:** same argument as S-A — counts and set operations, no
  scoring functions. Additionally immune to the within-archive selection
  effects that make query-level buckets suspicious.
- **What it would show [CONJECTURE]:** if Q2's mechanism is right, CODE−BM25
  should decline monotonically in singleton rate and rise in mean doc length
  (longer docs = more redundancy = more SVD-exploitable co-occurrence). This
  single plot would simultaneously explain G1 (why BM25 wins), G3 (which
  queries), AND the programme's standing regularity ("no arm has EVER won on
  both benchmarks" [MEASURED HERE — FINDINGS_DIGEST]): RealTalk vs PerLTQA
  differ in composition, so every arm's sign is composition-driven, not
  method-driven. Falsified if: the correlation is flat (then composition does
  not drive the gap and the reversal needs a different theory — e.g. gold
  construction or tokenizer interaction), or reversed.
- **Cost:** zero new retrieval runs — all statistics computable from stored
  text + stored per-query outcomes. Highest information-per-CPU of the three.

### Reporting rule going forward (applies to all three)

Pre-register bucket definitions + tokenizer + thresholds BEFORE computing
outcomes (the IDF_p2 band analysis was exploratory-by-own-admission: subgroup
chosen after seeing results [MEASURED HERE — FINDINGS_DIGEST]); report bucket
shares alongside deltas (a win on 3% of queries is not a win); never define a
bucket with σ, IDF^p, singular vectors, BM25 scores, or code scores. S-A and
S-C are runnable this round; S-B needs a frozen grader and goes next.

---

## KNOWN vs NEW — summary table

| # | Phenomenon [MEASURED HERE] | Verdict | Basis |
|---|---|---|---|
| G1 | BM25 beats float repr by 5.67 pp; quant only 1.83 pp | Mechanism DERIVABLE (Q2 steps 1–3); regime OPEN | [PROOF-SKETCH] + [CONJECTURE]; no recalled small-N study |
| G1-sup | Frozen-tokenizer BM25 +~3 pp; k1→0/b→0 effects | UNASSESSED — artifacts not on my disk; flag, do not cite | Brief G1 only; needs coordinator verification |
| G2 | Tiny archives, short docs, 45.6% singletons | Regime OPEN as studied condition; counts textbook | Zipf folklore; no dense-vs-BM25 study recalled |
| G3 | Rare-band loss 14.37 pp; circular bucket | Circularity CONFIRMED by construction; fix ACTIONABLE (S-A/B/C) | Logic + [MEASURED HERE]; QPP cited for principle only |
| G4 | RRF +5.67/+3.12; 49/67 split | WHY known at folklore level (complementarity) | [RECALLED-FROM-MEMORY] medium; RRF paper verified R1 |
| G5 | Rerank washout; crossover; net −0.33/+0.33/+1.07 | Practice KNOWN; stated-with-conditions OPEN; mechanism DERIVED | Pool bound [PROOF-SKETCH]; monoBERT/BEIR/ANN to verify |
| Ladder | 192→384 flat-to-negative on 2/3 benches | Consistent with representation-bottleneck diagnosis | [MEASURED HERE — LADDER_AUDIT]; no lit needed |
| Storage | 5.8× index; 76× text | Practice UNVERIFIED; our ledger stands alone | Per-paper audit F7 required |

## What would change these verdicts

- F1 returning a real ≤1000-doc dense-vs-BM25 comparison → Q1 OPEN becomes
  PARTIALLY KNOWN; our magnitude stays new unless their n≈400.
- F3 returning an LSI collection-size study → Q2 mechanism gains attribution
  (or a competitor explanation); a null result (documented search, no study)
  upgrades OPEN to DOCUMENTED-OPEN.
- F4/F5 showing a fixed-reranker/varied-first-stage convergence figure → Q3
  washout becomes KNOWN with conditions; showing divergence (first stage
  preserved post-rerank) would CONTRADICT our reading and force re-analysis
  of FIKIR1's M=50/depth choice.
- F7 audit finding a full-system storage precedent → Q4 adopts it as primary
  convention; finding pure vector-bytes-only → dual-reporting (field + honest).
- S-A/S-B/S-C results (on disk, no fetch): any of the three falsifiers firing
  reopens Q1–Q2 mechanism — literature cannot substitute for these runs.
