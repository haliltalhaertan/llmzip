# V52 TASK 4C2 — INDEPENDENT ADVERSARIAL AUDIT

MANDATORY FIRST STEP — CHAIN OF CUSTODY
Before interpreting any result, verify every committed frozen artifact byte-for-byte against the corresponding manifest SHA256. Treat any mismatch as a packaging/chain-of-custody defect until the canonical Drive copy is independently checked.
Run: `python3 tools/verify_frozen_artifacts.py` (exit 1 on any mismatch). See `CHAIN_OF_CUSTODY.md`.
# ZERO TRUST / MECHANISM AUDIT

ROLE
You are an independent adversarial computational auditor. Do not assume the compute report is correct. Try to falsify the result. The primary question is whether the reported SIGN96 advantage over a centered continuous control is real, correctly computed, and attributable to retrieval geometry rather than an implementation/aggregation/tie artifact.

PRIMARY ARTIFACT PACKAGE
Drive file: V52_T4C2_ALL_OUTPUTS.zip
https://drive.google.com/file/d/1XkcdVYZTOzDXxq1RMDbnVT46_biGBGxa/view?usp=drivesdk

Canonical final artifact folder:
https://drive.google.com/drive/folders/1rXeSGN0__wXTYVzvJy1wVulTY0gFTUaP

FROZEN CLAIMS UNDER AUDIT
LongMemEval cleaned-S primary cohort: 470 non-_abs questions.

FLOAT96_UNCENTERED:
ANY 61.063830%
ALL 28.936170%
Fractional 44.010638%

FLOAT96_CENTERED:
ANY 61.276596%
ALL 28.723404%
Fractional 44.159574%

SIGN96_CENTERED:
ANY 71.308511%
ALL 38.457447%
Fractional 54.197518%

ITQ96_CENTERED:
ANY 54.276596%
ALL 22.672340%
Fractional 37.614113%

Headline paired gaps:
Fc-F0 = +0.148936 pp
S-Fc = +10.037943 pp
I-Fc = -6.545461 pp
S-I = +16.583404 pp

Frozen Task 4C2 verdict:
[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]

IMPORTANT: This is a fixed-benchmark paired estimand only. All 470 primary questions belong to one shared-session connected component. No population p-values, population confidence intervals, superiority/equivalence/non-inferiority claims.

1. AUDIT LEVEL
Prefer FULL END-TO-END NUMERICAL REPRODUCTION if dataset + adapters + source are available. Otherwise perform FULL RAW-TABLE NUMERICAL REPRODUCTION plus source-level implementation audit. State the achieved level exactly.

2. CHAIN OF CUSTODY
Verify the immutable pre-run seal and post-run manifest.
Expected Task4C2 script SHA256:
3bb1126090ab619c061d10d0f1a5c20db1372c5e2cd66b5158905a65f460061b

Expected pre-run seal SHA256:
19883841cf4b2ff02df21dca56bfc1f8612ba13f03c6eeb93150c5f6ad3468a3

Verify:
- pre-run script hash == final script hash
- no method was added after seal
- exact methods are only FLOAT96_UNCENTERED, FLOAT96_CENTERED, SIGN96_CENTERED, ITQ96_CENTERED
- decision bands were sealed before new centered-float performance
- no post-result rescue methods entered the reported result

Any source mutation after seal is blocking.

3. DATASET / ADAPTER INTEGRITY
Canonical dataset SHA256 must be:
d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442
Expected byte size: 277383467
Expected total: 500
Expected primary cohort: 470 non-_abs
Expected primary zero-gold: 0

Adapter v1 expected SHA256:
0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722
Adapter v2 expected SHA256:
643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218

Verify archive fitting cannot receive query/gold/answer/type labels. Verify duplicate-memory-ID assertion is active. Reuse prior audited adapter conclusions only if exact hashes match; otherwise audit the actual source.

4. TASK 4C1 REPRODUCTION GATE
Independently verify that the Task 4C2 run reproduces frozen Task 4C1 controls exactly within deterministic tolerance. Report all 9 reproduction checks and deviations. If the gate fails, stop interpretation.

5. CLEAN SAME-INPUT ABLATION
This is load-bearing.
Prove that FLOAT96_CENTERED, SIGN96_CENTERED pre-threshold input, and ITQ96_CENTERED pre-rotation input use the exact same archive C96 and query qC96.

Expected:
max absolute difference = 0.0 or floating roundoff only.

Verify no extra normalization, refit, whitening, SVD, centering, query-dependent transform, or block weighting occurs in only one method.

6. FLOAT96_CENTERED DEFINITION
Verify exactly:
Y96 = frozen normalized archive 96D representation
mu96 = archive mean(Y96)
C96 = Y96 - mu96
qC96 = QY96 - mu96
Ranking = global exact cosine similarity(qC96, C96)
No shortlist. No reranker. No learned metric.

7. SIGN96 DEFINITION
Verify exactly:
doc code = C96 >= 0
query code = qC96 >= 0
96 bits exactly
Ranking = global Hamming distance with the frozen independent secondary tie priority.
No corpus-order, gold-order, chronology, lexical memory-ID order, or evidence order may break ties.

8. ITQ96 DEFINITION
Verify exactly the same C96/qC96 followed by the frozen audited ITQ rotation and zero threshold. Confirm orientation and archive/query symmetry. Check R orthogonality/determinism and that no source-level difference from the previously audited ITQ implementation exists.

9. RAW TABLE INTEGRITY
Recompute the expected design row count from the code/protocol. Verify:
- 470 questions
- 20 nuisance trials
- 5 ITQ seeds where applicable
- no duplicate trial cells
- no missing questions
- no hidden methods
- no NaN/Inf
- SIGN/FLOAT replication across seed rows does not overweight them in aggregation

10. INDEPENDENT AGGREGATION
Do not trust aggregate.csv or the compute report. Reconstruct from raw trial data.
Correct nesting:
- nuisance trials averaged inside question/method/seed as applicable
- ITQ seeds are nuisance, not independent observations
- benchmark questions equal-weighted

Independently reproduce ANY R@3, ALL R@3, Fractional R@3 for all four methods and all four headline gaps.

11. PRIMARY FALSIFICATION TARGET
The central claimed residual is:
SIGN96_CENTERED - FLOAT96_CENTERED = +10.037943 pp.
Try to explain this through defects before accepting a geometry interpretation.
Explicitly test:
- wrong denominator/gold mapping
- different cohort
- row duplication/weighting
- tie priority asymmetry
- Hamming distance direction error
- cosine ranking direction error
- boolean dtype/packing error
- accidental query leakage
- accidental gold leakage
- query-dependent centering
- sign complement/inversion bug
- different continuous inputs
- nuisance/seed nesting bug
- post-selection

Quantify any defect in percentage points.

12. QUESTION-LEVEL ROBUSTNESS
Independently compute paired question-level Fractional R@3:
SIGN96 vs FLOAT96_CENTERED
FLOAT96_CENTERED vs FLOAT96_UNCENTERED
SIGN96 vs ITQ96

Expected key W/T/L:
SIGN vs centered float = 122/304/44
centered vs uncentered float = 7/458/5

Report mean win magnitude, mean loss magnitude, median paired gap, and whether the +10.04 pp result is driven by a small subset of questions.

13. FROZEN STRATA
Reconstruct only the frozen strata:
- 6 question types
- one-gold vs multi-gold
- archive-size quartiles
- reuse tertiles

Report SIGN-Fc and Fc-F0 for each. No subgroup p-values and no post-hoc thresholding.

14. BIT BALANCE
Independently verify SIGN96 and ITQ96 bit occupancy diagnostics.
Reported descriptive pattern:
- ITQ bits are extremely close to 50/50 occupancy and have 0 dead bits
- SIGN96 mean occupancy ~0.49544, min occupancy ~0.44933, max ~0.49961, 0 dead bits

Determine whether the source and exported binary codes support these values. Do not infer retrieval quality from balance alone.

15. COLLISION DIAGNOSTICS
Independently verify:
SIGN96 unique-document-code fraction ~0.995505, duplicate fraction ~0.004495, largest bucket 17, query exact-code-match fraction 0.
ITQ96 unique-code fraction ~0.894 across seeds, duplicate fraction ~0.106, largest bucket 23.

This difference is potentially important. Determine whether it is a real consequence of the frozen mappings or a packing/counting artifact. Do not claim causality from collisions alone.

16. TIE DIAGNOSTICS
Independently verify that SIGN96 has fewer Hamming ties than ITQ96.
Reported SIGN96:
mean candidates at min distance ~1.1532
mean candidates at top3-boundary distance ~1.5277
P(top3-boundary tie) ~0.2340

ITQ96 reported top3-boundary tie probability is roughly 0.37–0.42 depending on seed.

Verify identical tie priority semantics. Determine whether tie-handling could plausibly explain a meaningful fraction of the quality gap.

17. DISTANCE / RANK GEOMETRY
Use only the exported diagnostics / frozen codes. No new optimized method.
Verify gold-vs-nongold Hamming separation and continuous cosine separation.
Verify SIGN-vs-ITQ Hamming rank/distance Spearman diagnostics; reported mean correlations are low (~0.17).

Interpretation ceiling:
Low correlation supports that ITQ rotation substantially reorders binary neighborhoods, but does not prove why SIGN retrieves evidence better.

18. MECHANISM CLAIM CEILING
If all checks pass, the strongest allowed statement is:
"On the frozen LongMemEval representation and protocol, zero-threshold SIGN/Hamming retrieval on the centered 96D representation substantially outperforms both centered continuous cosine retrieval and archive-fitted ITQ96/Hamming retrieval. Mean-centering alone explains almost none of the SIGN-vs-uncentered-FLOAT gap."

Do NOT claim:
- sign hashing is novel
- sign hashing is generally superior to ITQ
- binary retrieval is intrinsically superior to continuous retrieval
- this generalizes to LoCoMo
- this is a population-level statistical superiority result
- collisions/ties are the proven causal mechanism

19. PRIOR-ART GUARD
Simple sign/binary quantization, binary semantic hashing, ITQ, shortlist+richer reranking, binary retrieval, multi-view hashing and binary agent-memory retrieval are known prior art. A positive 4C2 result is a benchmark-specific geometry phenomenon / candidate contribution, not algorithmic novelty by itself.

20. NO NEW EXPERIMENTS IN THE AUDIT
Do not run:
- uncentered SIGN
- alternate threshold
- alternate cosine/Euclidean metric
- whitening
- new rotation
- new bit width
- LoCoMo
- rescue methods

If a new experiment is scientifically warranted, recommend it after the audit; do not mix it into the frozen 4C2 verdict.

21. REQUIRED VERDICT
Return exactly one:
PASS
PASS WITH CONDITIONS
FAIL

22. BRANCH DECISIONS
Answer explicitly:
1. Does FLOAT96_CENTERED 44.159574% reproduce?
2. Does SIGN96_CENTERED 54.197518% reproduce?
3. Does ITQ96_CENTERED 37.614113% reproduce?
4. Does S-Fc = +10.037943 pp reproduce?
5. Is centering effect really only +0.148936 pp?
6. Are SIGN/FLOAT-centered/ITQ pre-binary inputs identical?
7. Are aggregation and seed/nuisance nesting correct?
8. Are tie rules symmetric and independent?
9. Are SIGN collision/tie advantages real in the exported codes?
10. Is any discovered defect large enough to explain the +10.04 pp residual?
11. Can Task 4C2 be frozen as an audited numerical checkpoint?
12. Can the project proceed to a single mechanism-focused Task 4C3?
13. What is the strongest remaining falsification risk?

23. REQUIRED HEAD RESEARCHER HANDOFF

TASK:
V52 Task 4C2 Independent Adversarial Audit

VERDICT:
...

AUDIT LEVEL:
...

CHAIN OF CUSTODY:
...

DATASET / ADAPTER:
...

TASK4C1 REPRODUCTION:
...

RAW TABLE:
...

FLOAT96_UNCENTERED:
ANY=
ALL=
Fractional=

FLOAT96_CENTERED:
ANY=
ALL=
Fractional=

SIGN96_CENTERED:
ANY=
ALL=
Fractional=

ITQ96_CENTERED:
ANY=
ALL=
Fractional=

CENTERING EFFECT Fc-F0:
...

SIGN RESIDUAL S-Fc:
...

SIGN-ITQ:
...

SAME INPUT PROOF:
...

W/T/L:
...

BIT BALANCE:
...

COLLISIONS:
...

TIES:
...

DISTANCE/RANK GEOMETRY:
...

STRATA:
...

BUGS:
...

QUANTIFIED DEFECT:
...

OVERCLAIMS:
...

STRONGEST FALSIFICATION RISK:
...

TASK 4C2 FREEZE:
YES / NO

TASK 4C3 MECHANISM BRANCH:
YES / NO

RECOMMENDED NEXT COMPUTE:
One technical recommendation only.
