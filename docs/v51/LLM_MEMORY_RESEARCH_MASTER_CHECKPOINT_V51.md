# LLM Memory Research — Master Checkpoint V51
Date: 2026-08-23
Status: V1–V50 archived; V51 full-LoCoMo validation protocol prepared but not yet executed.

## 1. Project goal

The project began from a simple human-memory intuition:

> An intelligent system should not keep everything equally active. It should keep a compact route/index to what matters, preserve raw information in a cold archive, and retrieve/rehydrate detail only when needed.

A second intuition was added later:

> Repeated semantic “shapes” can be stored once and parameterized; one memory can also have several compact retrieval cues (“different senses”) that all point to the same source.

The engineering target is therefore not “compress text as much as possible.” It is:

**Minimize persistent active memory and query-time memory touching while preserving reliable evidence retrieval and exact provenance.**

The current working architecture is a two-stage memory system:

1. **Active binary router**: tiny code per memory.
2. **Shortlist**: open only a few candidate memories.
3. **Cold fine reranker**: richer lexical/character representation is consulted only for those candidates.
4. **Raw archive/provenance pointer**: exact source remains recoverable.

Current candidate:
**archive-trained 24-bit ITQ router -> shortlist M=4 -> cold 32-bit word + 32-bit char rerank**.

The main internal reference is:
**full96 = latent32 + word32 + char32 active for every memory.**

## 2. Research rules

- Counterexample/falsification first.
- Separate synthetic, hybrid, curated-real, and full-real evidence.
- Never convert numerical evidence into a theorem.
- Never use QA gold/evidence labels to fit a deployable router.
- Tie-breaking must be independent of corpus order and gold labels.
- Question, not random seed, is the main independent statistical unit.
- Major independent audit only at major thresholds, not every small task.
- Preserve raw source/provenance.
- No novelty/publication claim until literature and full benchmark validation are complete.

Labels:
[KNOWN], [EXACT], [CERTIFIED NUM], [NUM], [CONJ], [LEAD], [FAIL], [OPEN], [PARK], [RETRACT].

---

# 3. Experimental history

## Phase A — Collision-aware hierarchical routing (V1–V11)

### V1
Synthetic structured memory, 5,000 records.

Fixed index average opened records ≈ 6.13.
Adaptive collision index ≈ 3.52.
≈42.5% fewer archive records opened with similar index size.

[NUM — SYNTHETIC] Adaptive splitting can beat fixed hierarchy depth on heterogeneous structured memory.

### V2
Frozen threshold T=9 scaled from 5k to 50k.

At 50k, reads fell dramatically but active routing index exploded (~+262% vs fixed).

[FAIL] Fixed collision threshold is not scale-invariant.

### V3
Equal approximate routing-entry budget.

Adaptive routing still reduced reads, but average advantage decayed with scale:
~42.9% at 5k, ~42.7% at 10k, ~26.2% at 25k, ~8.8% at 50k.
Tail/p95 benefit remained stronger.

[NUM — SYNTHETIC] Budget matters; threshold alone is not the correct objective.

### V4
Skew stress test.

Adaptive benefit was near zero for uniform data and large under hotspot/skew:
~27% at skew 0.8, ~59% at 1.1, ~72% at 1.4–1.8.

[NUM — SYNTHETIC] Collision-aware routing is chiefly a hotspot/skew mechanism.

### V5
Replaced hand threshold with collision utility.

For uniform query demand:
G = (n^2 - sum n_j^2)/N,
priority = expected read saving / added routing nodes.

At equal budget, read reduction increased with archive size (~45% at 5k to ~68% at 50k).

[LEAD — SYNTHETIC] Utility-based budget allocation is stronger than fixed threshold.

### V6
Generalized to query demand:
G = Q_parent*n_parent - sum(Q_j*n_j).

Density-only allocation failed when future query demand differed from archive density.
Oracle query-aware allocation was much better, but demand-optimized static routing failed under shift.

[FAIL] “stored frequently = queried frequently.”
[OPEN] Need online demand adaptation.

### V7
Online exponentially-decayed demand estimator.

After hotspot -> rare-query shift, online policy initially suffered but adapted toward oracle performance.

[NUM — SYNTHETIC] Demand can be relearned after distribution shift.

### V8
Static robust mixture between predicted demand and coverage prior.

Worst-case robust solution pushed toward coverage and sacrificed hotspot gain.

[FAIL] One static allocation cannot simultaneously maximize hotspot gain and protect against adversarially opposite query distributions.

### V9
Greedy utility allocation audited against exact tree-knapsack / binary MILP.

Greedy was not universally optimal; worst attainable-benefit gap reached ~11%.

[FAIL] Greedy universally optimal.
[EXACT] Static additive hierarchy allocation with precedence can be solved as tree knapsack / binary MILP.

### V10
Added switching/reconfiguration cost.

Objective:
retrieval reads + lambda * routing-configuration churn.

Best tested regularization H=2 modestly improved total cost over fixed; low read count alone could be worse after switching cost.

[NUM — SYNTHETIC] Optimize total system cost, not retrieval reads alone.

### V11
Reliability-constrained routing.

A simple semantic-router error model showed naive read optimization could lose substantial evidence recall, while a reliability constraint preserved the modeled baseline recall.

[EXACT — UNDER STATED MODEL] MILP recall-risk constraint enforces modeled recall floor.
[OPEN] Real semantic router errors are not independent fixed-p events.

---

# 4. Real-data and representation branch (V12–V17)

## V12 — First real LoCoMo subset
Curated conv_0 real subset.

Flat TF-IDF top3 holdout recall ≈ .688.
Hierarchical top2 sessions ≈ .688 with ~77% candidate reduction.
Confidence-adaptive ≈ .688 with ~85% candidate reduction.

[NUM — SMALL REAL] Hierarchical routing can preserve aggregate recall while touching far fewer candidate lines.

## V13
Calibration-safe confidence guard failed on holdout.

[FAIL] Simple calibration-safe confidence threshold is not a real recall guarantee.

## V14
Unsupervised within-session semantic microclusters.

Adaptive cluster routing achieved same aggregate holdout recall (.688) with ~89.5% second-stage candidate reduction.

[NUM — SMALL REAL]

## V14c
Measured actual sparse active-index bytes.

Fewer anchors did NOT automatically mean much less memory because cluster summaries became dense.
Full-anchor CSR saving only ~4.4%, and near ~1% after pointer overhead.

[FAIL] “Fewer routes/summaries automatically means much smaller active memory.”

Top-L anchor sparsification could reduce bytes strongly, but aggressive compression threatened recall.

## V15
Compressed-anchor Pareto.

Top-L=96 retained same aggregate recall (.688) on the tiny holdout, with ~6.9% less active index and ~4.06 cold lines opened on average.

[NUM — SMALL REAL] Some anchor features are removable without observed aggregate recall loss.

## V16
Shared raw TF-IDF motif dictionary.

Exact repeated feature motifs increased size (~5–6% raw; ~9–12% worse after zlib).

[FAIL] Surface/co-occurring TF-IDF motif sharing captures the wrong kind of “shape.”

## V17
Oracle parameterized semantic shapes:
e.g. PERSON -> EVENT -> TIME -> EMOTION.

At N=5000, oracle structural templates retained roughly 12.7–16.0% additional saving even after zlib.

[LEAD — ORACLE/SYNTHETIC STRUCTURE] Parameterized relation shapes can amortize repeated structure.
[OPEN CRITICAL] Automatic shape discovery from raw language without QA leakage, while preserving negation/time/version/provenance.

Working concept: **Semantic Grammar Memory**
memory = template/shape + variables + exceptions/residuals + raw source pointer.

---

# 5. Multi-signature / “synesthesia” branch (V18–V23)

## V18–V20
Equal persistent address budget: 96 bits per memory.

Compared:
- one 96-bit word signature,
- three same-word 32-bit signatures,
- heterogeneous word32 + char32 + latent32.

Repeated random geometries showed:

[FAIL] Merely making multiple addresses from the same representation is not useful; 3x same-word addresses often underperformed one monolithic 96-bit signature.

[LEAD — SMALL REAL] Heterogeneous word+char+latent signatures were more robust, especially under query corruption.

V20 all 32 curated real questions:
- clean heterogeneous ≈ .426 vs single96 ≈ .366,
- drop50 ≈ .305 vs .243,
- drop30+typo ≈ .318 vs .255.

But the dataset remained tiny and the system-wide encoder cost was not counted.

## V21
Adaptive per-memory 96-bit split.

Raw collision-driven 48/32/16 allocation modestly beat equal 32/32/32 point estimates; “distinctiveness” allocation failed badly.
Allocation mostly collapsed to giving 48 bits to latent.

[FAIL] Simple archive-only “distinctiveness” is not a good bit-allocation signal.
[LEAD] Collision pressure might contain useful allocation information.

## V22
Normalized cross-view collision scores.

Normalization removed much of the raw-collision gain.

[FAIL/DIAGNOSTIC] Cross-view score scale itself was influencing V21; adaptive allocation evidence weakened.

## V23
Query-adaptive fusion was explored. Treat as mechanism exploration only; no full-benchmark claim.

---

# 6. Coarse-to-fine cascade and stopping (V24–V30)

## V24
Introduced coarse-to-fine architecture:

**latent coarse address -> shortlist -> cold word+char rerank**.

This became the central direction because only the small router stays active.

[LEAD — SMALL REAL] Two-stage retrieval can drastically reduce active/touched memory.

## V25
Scaled with synthetic hard-negative expansions.

[NUM — HYBRID] The cascade was stress-tested, but this was not a full-real benchmark.

## V26
Denoising decomposition showed a larger shortlist can improve coarse coverage yet hurt final retrieval by adding distractors to the fine stage.

[KNOWN EMPIRICALLY] More candidates is not monotonically better.

## V27
Confidence stop rule failed to beat a simple fixed shortlist robustly.

[FAIL] Simple gap/margin stop rule.

## V28
Retrieval-stability stopping was tested; useful diagnostically but not a decisive deployable rule.

## V29
Multi-view disagreement/agreement signals were investigated for adaptive stopping.
No load-bearing result; retain as diagnostics.

## V30
Measured marginal value of expanding M=4 -> M=6.
Used uncertainty features to predict whether two extra memories help.
Diagnostic only.

---

# 7. Equal-24-bit multi-view coarse address branch (V31–V42)

V31–V42 explored whether a 24-bit active router should distribute bits across latent/word/char views and whether collision/ambiguity gates could switch policies.

This branch initially produced apparently positive gate/diversity results.

## Critical correction: V43
A corpus-order tie-breaking bias was discovered.

Equal Hamming distances had been resolved in a way correlated with archive/gold ordering.

V43 reran the core claims with a random document priority independent of corpus order/gold labels.

After correction:
- real 44-line clean: full96 ≈ .4542, latent24 M4 ≈ .4521,
- probe/adaptive and theory gates were substantially worse,
- across broader hybrid settings, latent24 was generally the strongest simple cascade.

[RETRACT] Strong positive V31–V42 claims that depended on the biased tie behavior.
[FAIL] Collision-gated/probe-diversity mechanisms as previously supported.
[IMPORTANT] All future binary-router experiments must use independent randomized tie priority.

## V44
Unbiased equal-24-bit multiview allocation.

Across every tested setting, the best allocation was **24/0/0** = all 24 coarse bits to latent.

[FAIL] Splitting a tiny 24-bit coarse budget across word/char/latent views.
[LEAD] A single well-trained compact latent router is preferable at this budget.

---

# 8. Router quality and unbiased end-to-end tests (V45–V50)

## V45 — Router quality
Archive-only, no QA/gold fitting.

Methods:
- random SimHash24,
- median-threshold SimHash24,
- PCA-sign24,
- ITQ24.

Tie-breaking randomized independently of corpus/gold order.

The result was mixed across hybrid settings; no universal router dominated.
The real subset and later real-only reruns motivated deeper PCA/ITQ testing.

[NUM] Learned/archive-adapted binary codes deserve real-only testing.
[NO CLAIM] Hybrid synthetic expansions cannot establish full benchmark superiority.

## V46 — End-to-end unbiased cascade
Architecture:
24-bit router -> M=4 -> cold word32+char32 rerank.

Internal reference:
full active96.

Across the equal-weight mixture of real + hybrid settings:
- full96 recall ≈ .2171,
- PCA24 cascade ≈ .2088,
- random24 ≈ .1948,
- ITQ24 ≈ .1932,
while the cascade touched ~72.5% fewer bits on average.

[NUM — MIXED/HYBRID] Strong memory-touch saving, but not robust global recall parity.

Real 44-line setting was more promising than the hybrid expansions, which motivated V47.

## V47 — Real-only router Pareto
Data:
- curated real LoCoMo conv_0 subset only,
- 44 archive lines,
- 32 real questions,
- no synthetic hard negatives,
- 50 nuisance trials.

Example clean point estimates:
- full96: recall .48875, touched bits 4224,
- ITQ24, M=4: recall .480625, touched bits 1312,
  => only ~0.81 pp lower recall with ~68.94% fewer bits touched.

Random24 M4 was ~1 pp below full on this particular V47 protocol.

[LEAD — SMALL REAL] Compact 24-bit router + M=4 cold rerank sits close to full96 while touching far less memory.

## V48 — Statistical audit: question is the sampling unit
100 nuisance trials/question; 20,000 paired question bootstraps.

Absolute mean recall under the V48 rerun:
Clean:
- full96 .4856
- ITQ24 .5297
- PCA24 .4938
- random24 .4663

Drop50:
- full96 .3484
- ITQ24 .3609
- PCA24 .3691
- random24 .3234

Drop30+typo20:
- full96 .3688
- ITQ24 .3813
- PCA24 .3813
- random24 .3525

Paired question bootstrap:
ITQ24 - random24:
- clean +6.34 pp, 95% bootstrap ~[+0.97, +12.62], P(diff>0) ~.991
- drop50 +3.75 pp, interval crosses 0
- drop30+typo +2.88 pp, interval crosses 0

ITQ24 - full96:
- clean +4.41 pp, interval slightly crosses 0 in V48
- corrupted conditions also uncertain.

Decomposition:
fine reranking usually succeeded once the gold evidence entered the shortlist (~89–96%); the main bottleneck is **coarse shortlist coverage**.

[LEAD — SMALL REAL] ITQ improves coarse coverage over random binary hashing.
[OPEN] Full-LoCoMo generalization.

## V49 — Bit-budget curve
Real-only 44 lines / 32 questions, M=4.
Budgets: 8, 12, 16, 20, 24, 32 bits.

Point estimates sometimes showed 8-bit ITQ/PCA already near or above full96 while touching ~85.6% fewer bits.
However uncertainty intervals were wide due only 32 questions.

[LEAD] Extremely small binary routers may be viable.
[NO THEOREM] Do not claim 8 bits is sufficient globally.

## V50 — ITQ protocol sensitivity
Stress-tested ITQ across:
- latent dimensions 24, 32, 40,
- ITQ initializations 101, 202, 303, 404, 505,
- 15 protocol variants,
- clean and drop50,
- 40 nuisance trials/protocol.

ITQ24 vs full96:
Clean:
- mean advantage +3.578 pp,
- minimum across the 15 protocol variants +0.625 pp,
- maximum +10.156 pp,
- question-bootstrap over protocol family: 95% ~[+0.651, +7.136],
- P(diff>0) ≈ .994.

Drop50:
- mean advantage +2.036 pp,
- every protocol variant had positive point estimate (min +0.312 pp),
- question-bootstrap 95% ~[-0.573, +4.964],
- P(diff>0) ≈ .931.

This is the strongest current lead.

[LEAD — STRONGEST SMALL-REAL RESULT]
A 24-bit archive-trained ITQ router followed by cold fine reranking may outperform the internal full96 binary reference while touching far less memory.

But:
- only 32 questions,
- only one LoCoMo conversation,
- full96 is an internal reference, not SOTA retrieval,
- no full-LoCoMo result yet.

---

# 9. Current V51 — full LoCoMo validation

V51 is the next load-bearing experiment.

Goal:
Run the unbiased router comparison on the full real LoCoMo benchmark.

Expected data:
- 10 conversations,
- categories 1–4 only,
- 1,540 questions.
Category 5 adversarial questions are excluded from the primary retrieval test.

Audit repository provides corrected evidence/answers. V51 must report both:
1. raw LoCoMo evidence,
2. audit-clean corrected evidence.

Primary methods:
- full96
- random24
- PCA-sign24
- ITQ24 using 5 archive-only initializations
- ITQ8 as aggressive sensitivity arm

Primary architecture:
24-bit router -> shortlist M=4 -> cold word32+char32 rerank.

Sensitivity:
M=8.

Metrics:
- ANY evidence Recall@3
- ALL evidence Recall@3
- fractional evidence recall
- per-category performance
- per-conversation performance
- bits touched/query
- raw evidence vs audit-clean evidence

Statistics:
- nuisance randomness averaged within each question,
- paired question bootstrap,
- conversation-cluster bootstrap across the 10 conversations.

Hard safeguards:
- router fit uses archive only; never QA gold/evidence labels,
- random tie priority independent of corpus/gold order,
- no synthetic hard negatives in primary V51,
- image BLIP captions included,
- script aborts if it does not see exactly 10 conversations and 1,540 category-1–4 questions.

Prepared files:
- `v51_full_locomo_benchmark.py`
- `v51_protocol_manifest.json`

## Current technical blocker
The GitHub connector can read the official/audit LoCoMo files, but in the previous chat the large dataset bytes could not be bridged into the Python runtime. Therefore **V51 has NOT been executed**.

Do not fabricate a full-LoCoMo result.

Preferred continuation:
1. Try to fetch/download the full dataset into the active runtime using available Drive/GitHub/file tools.
2. If the official `locomo10.json` or the 10 `audit/conv_i.json` files are available in Drive or uploaded by the user, run `v51_full_locomo_benchmark.py`.
3. Verify 10 conversations / 1,540 category1–4 questions.
4. Run V51.
5. Interpret results counterexample-first.
6. Only if V51 survives should we discuss independent audit/publication/novelty.

---

# 10. Literature / novelty constraints

General ideas already have substantial prior art:
- hierarchical memory,
- query-adaptive retrieval,
- adaptive granularity,
- historical query demand,
- switching costs,
- graph memory,
- repeated graph/motif compression,
- multi-view/distributed representations.

Relevant lines encountered:
- SwiftMem (query-aware indexing),
- HingeMem (query-adaptive retrieval),
- MemGAS,
- ARC,
- SOLAR (switching-cost semantic cache),
- MemSIF,
- RAG without Forgetting,
- Cluster with Auctions,
- TSM,
- Mnemis,
- MOSAIC,
- HDC/VSA surveys,
- grammar-based graph compression / MDL motif compression.

Therefore do NOT claim novelty for any ingredient by itself.

Possible eventual research contribution, only if full benchmarks survive:
**budgeted, archive-trained compact binary memory routing with reliability/provenance constraints and cold fine retrieval**, perhaps combined later with semantic grammar compression.

---

# 11. Current scientific status

[EXACT]
- Static hierarchy budget allocation can be formulated as precedence-constrained tree knapsack / binary MILP.
- Reliability constraint guarantees a recall floor only under the stated simplified error model.

[FAIL]
- fixed collision threshold as central solution,
- archive density = future query demand,
- one static robust allocation maximizes all demand regimes,
- greedy universally optimal,
- optimize reads alone,
- calibration-safe confidence threshold as guarantee,
- fewer summaries automatically means smaller active bytes,
- raw TF-IDF motif sharing,
- “just make multiple same-type addresses,”
- equal tiny coarse-budget multiview split,
- earlier collision/probe gates after unbiased tie correction.

[RETRACT]
- Strong V31–V42 diversity/gating conclusions that relied on corpus-order tie behavior.

[LEAD]
- semantic parameterized shapes under oracle structure,
- heterogeneous cues under equal budget on small real data,
- coarse-to-fine active-router/cold-rerank architecture,
- archive-trained PCA/ITQ binary routers,
- especially ITQ24 robustness in V48–V50.

[OPEN CRITICAL]
- Full audit-clean LoCoMo V51.
- Generalization across conversations.
- Comparison against strong modern retrievers under matched protocol.
- Whole-system byte cost including encoder/codebook parameters.
- Exact provenance/reliability under real semantic queries.
- Automatic semantic grammar discovery.
- Demand drift/reconfiguration in a real benchmark.

---

# 12. Decision rule after V51

If ITQ24 loses clearly on full LoCoMo:
- close or substantially downgrade the “ITQ24 beats full96” branch,
- keep compact-router Pareto engineering result if memory savings remain useful,
- investigate why single-conversation evidence failed to generalize.

If ITQ24 roughly matches full96 with large touch savings:
- optimize Pareto and compare against stronger compressed retrieval baselines.

If ITQ24 beats full96 robustly:
- require:
  1. conversation-cluster uncertainty,
  2. audit-clean evidence consistency,
  3. independent adversarial audit,
  4. strong literature/SOTA matched-protocol comparison,
  5. byte-level whole-system accounting,
before any publication/novelty claim.

---

# 13. User-facing explanation style

The user is intentionally exploring mathematics/computer science through intuition rather than advanced formal training.

Explain research in very simple Turkish:
- ne denedik?
- ne bulduk?
- ne anlama geliyor?
- sırada ne var?

Use formulas only when they materially help.
Never be patronizing.
The user proposes intuitive/hypothetical mechanisms; translate them into formal models, algorithms, experiments, counterexamples, and—where possible—proofs.
