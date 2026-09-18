# CODE AUDIT — round 2 (core experimental code, bug hunt)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Auditor role: core experimental encode/score path. Read-only on all source trees;
all scratch tests live in this directory (`audit_hard_r2/code/`).
No internet. `python3` has numpy (2.5.3, no sklearn); `~/muse-work/ml-python`
has sklearn 1.9.1 / scipy 1.18.1 and was used only where a rebuild was needed.

## (1) VERDICT in 3 lines

Two load-bearing bugs survive round 1: the "12 B/doc" storage claim omits a ~28 MB
per-archive projector (amortized ~68 KB/doc on the measured archive, 5678x the payload),
and every published code number is measured with that projector fitted on the test archive
itself — refitting it on held-out archives drops RT05 qscale Hit@10 from 60.00 to 24.29.
The STOP verdict is robust (both bugs flatter the codes, so the honest gap to BM25 is even
larger than published), but the ladder levels, the byte column, and one "genuinely ours"
finding are wrong or reference-dependent as stated.

## (2) Findings table

| ID | Severity | Claim audited | What I did | Result |
|----|----------|----------------|------------|--------|
| F1 | CRITICAL | "12 B/doc" storage; "HONEST BYTE ACCOUNTING: sign coding costs k/8 bytes per document" | Rebuilt RT05 projector exactly (ml-python/sklearn); weighed every decoder-side artifact in memory | Side info = 27,933,977 B/archive vs 4,920 B payload (5678x); amortized true cost 68,144 B/doc. PQ competitor arm discloses its codebook; own codes disclose nothing |
| F2 | CRITICAL | All RealTalk code Hit@10/FR@3 numbers (ladder, gates, T1) | Held-out experiment: same recipe, projector fit on other 9 archives (bit-exact TRANS rebuild: 0/39360 bits differ); HYBRID vocab-vs-subspace split | INDEP qscale 24.29 vs TRANS 60.00 (−35.71 pp); sym 18.57 vs 55.71 (−37.14 pp), n=70. Subspace drives ~80% of the gap. All published code numbers are transductive-regime numbers, undisclosed |
| F3 | HIGH | Bootstrap CIs / SIG claims on sym (integer-score) arms | Rescored all 705 RT queries from caches under 5 tie salts; det-vs-expected comparison | 69.8% of queries tie AT the top-10 cut; salt spread 0.71 pp; 20/705 queries flip. CIs hold the hash fixed, so tie luck (same order as the C3 +1.0 pp gate) is unmodeled |
| F4 | HIGH | REPORT "quantization costs only 1.83 pp"; FINAL_STATE "sign ADDS ~10 pp over the float source" | Recomputed raw-cosine, standardized-cosine, qscale, sym Hit@10 from caches (anchors reproduced to 4 decimals) | Both slogans are reference-shopping the same data: vs raw float, sign wins by +9.93 pp; vs standardized float, sign loses by −1.99 pp. LADDER.json (36.60) vs REPORT (48.51) differ by ~12 pp with no disclosure |
| F5 | MED | C1 gate readout ("FAIL — behind by 7.80 pp") | Arithmetic from DECISION_TESTS.json | C1 is FR@3-based (gap −7.23 pp); 7.80 is the Hit@10 gap. Wrong metric quoted in both readouts. Verdict unaffected |
| F6 | LOW | REPORT §1 evidence table Hit@10 column | Reproduced det (46.5248) and exp (46.6809) sym anchors | "sign96 46.68" is the tie-averaged (expected) number in a column of deterministic numbers (det = 46.52). 0.16 pp mix |
| F7 | MED | "The decline is specific to dividing by σ" (T3/LADDER); sym labeled "standardized" | Read t3_ladder.py scoring code (lines 186–188, 231) | sym never divides by σ, yet sym FR@3 falls 53.88→48.71 at 384. The mechanism as stated cannot explain its own table's sym row; the "standardized" label on sym is simply wrong. Sharpens (not duplicates) the known incomplete-σ-explanation issue |

## (3) Per-finding detail

### F1 — CRITICAL — the per-archive projector dwarfs the payload; "12 B/doc" is payload-only and undisclosed

**Claim.** `REPORT.md:21-27` storage column ("12 B/doc"); `coordinator/ladder.py:24`
"HONEST BYTE ACCOUNTING (the whole point): sign coding costs k/8 bytes per document";
`LADDER_REALTALK.md` byte-ladder framing ("WHAT DOES 12 BYTES COST").

**Code path.** `coordinator/ladder.py:111-132` (`build()`): per archive, fit word TFIDF +
char TFIDF + LSA-SVD(≤32, seed 5101) + SVD96 (seed 5204) on the archive's own documents,
then L2-normalize, subtract the doc mean `mu`, take signs. Scoring needs, per archive:
SVD96 components (96×F), LSA components, both vectorizers (vocab + IDF), `mu` (96),
`sigma` (96, in `score_arms`, `ladder.py:150-152`). None of this is counted. Same recipe in
`math_r1/quant/quant_math.py:385-400`, `ablation_r2/perltqa/ablation.py:140-168`,
`ablation_r2/lme/ablation.py:86-115`, frozen builder `drive/v52_t4d_locomo_frozen_cross_benchmark.py:196-219,646-657`.

**Test** (`t_bytes.py`, run: `~/muse-work/ml-python -u -c "import runpy;
runpy.run_path('t_bytes.py', run_name='__main__')"` in this directory): rebuilt the RT05
(smallest archive, N=410) projector with the exact recipe and weighed components in memory.

**Output (pasted).**

    archive RT05 N=410 docs
    word feats=9820 char feats=22378 latent=32 Z feats F=32230
    C shape=(410, 96) (sanity: N x 96)

    side-info bytes (per archive, shared across its 410 docs):
      SVD96 components_ 96x32230 float64: 24,752,640
      LSA32 components_: 2,513,920
      mu (96 f64): 768
      sigma (96 f64): 768
      word vectorizer pickle: 255,794
      char vectorizer pickle: 410,087
      SIDE TOTAL (no rotation): 27,933,977 B = 27279.3 KiB
      payload N*12: 4,920 B
      side/payload ratio: 5677.6x
      amortized true cost per doc: 12 + 68132 = 68144 B/doc
      ITQ rotation extra: 73,728 B f64 (36,864 B f32) = 15.0x the whole payload (f64)
      SVD96 float32 variant would be 12,376,320 B (2515.5x payload)

**Double standard (demonstrates disclosure was possible).** The PQ equal-budget arm ships
`pq/REPORT.md:50-58` (in the publication package): "Shared codebook: 98,304 bytes actual
... amortized ~10.99 bytes/doc, effective amortized ~22.99 bytes/doc" with an explicit
"no equal-total claim" disclaimer. The programme's own codes carry ~28 MB per archive
(≈285x the PQ codebook, and per-archive rather than global) with no corresponding section
anywhere in REPORT/FINAL_STATE/LADDER_REALTALK/DECISION_TESTS (verified by grep for
shared/overhead/amortiz/side-info/decoder/codebook — zero hits outside the PQ report and
the rotation paragraph). `REPORT.md:137` does disclose the *rotation* matrix cost
(3.43x/7.50x payload, float32 R vs average payload — arithmetic checks out), but the base
projector is ~300–1500x larger than the rotation and is never mentioned.

**Effect on conclusions.** STOP is strengthened, not weakened (honest accounting only
widens BM25's lead). But every "X at 12 bytes" cell, the ladder's cost axis, and the
"WHAT DOES 12 BYTES COST" question are answered ~5000x too low as total cost. A reader
comparing against the PQ row (whose total IS disclosed as ~23 B/doc) is actively misled
about which method is cheaper.

### F2 — CRITICAL — projector fitted on the test archive inflates every code number (~36 pp on RT05)

**Claim.** All RealTalk code numbers (ladder 49.65→55.32→57.87; T1 code arms; gates).

**Code fact.** The SVD96/TFIDF/mu/sigma are fit on the same documents later retrieved
(`ladder.py:113-114,128-130`; frozen builder docstring even names it: "Archive-only
unsupervised fit", `drive/...:196-204`). Queries are transformed, never fit — so there is
no query leakage; the leak is corpus-transductive: the compressor is trained on the test
set. A deployable system (projector fixed before a new archive arrives) cannot do this.

**Test** (`t_inductive_rt.py`, ml-python): held-out RT05 (410 docs, 70 mapped queries).
TRANS = project practice (fit on RT05 docs). INDEP = identical recipe fit on the other 9
archives' 8,534 docs, RT05 encoded through it (OOV terms drop naturally).

**Output (pasted).**

    held-out RT05: N=410 nq=70
    TRANS vs cache differing bits: 0 of 39360
    TRANS sym Hit@10=55.71 qscale Hit@10=60.00
    INDEP sym Hit@10=18.57 qscale Hit@10=24.29
    transductive optimism: sym +37.14 pp, qscale +35.71 pp (one archive, 70 queries)

The 0-bit TRANS-vs-cache check proves my harness is the exact production path, so the
INDEP drop is regime, not reimplementation. Diagnostic (inline ml-python check): under
INDEP, only 1/70 queries and 0/410 docs are fully word-OOV, char rows all nonzero
(min 39), bg vocab 62,833 vs test vocab 9,820 (2,919 overlap) — the collapse is not a
trivial zero-vector artifact.

**Decomposition** (`t_hybrid.py`): HYBRID = union vocab/IDF (no dropped test terms) but
SVD96+mu fit on background only → sym 27.14 / qscale 25.71. So of the ~37 pp sym gap,
vocab explains ~8.6 pp and the test-fit subspace ~28.6 pp (~80%). The 96-dim SVD fitted
on the retrieved documents is doing most of the retrieval work attributed to "the code".

**Scope honesty.** Sampled, not exhaustive: one archive (RT05), n=70. Background = same-domain
sibling archives; a larger/diverse background could do better, a truly novel archive worse.
The synthetic mechanism demo (`t_transductive.py`, numpy-only, TRANS 100.00 vs INDEP 13.50)
is direction-only illustration and is NOT a magnitude estimate — the RT05 number above is.
STOP survives (INDEP is worse than published, so BM25's lead grows); what dies is any
reading of the ladder levels as deployable-code performance.

Related (code-evident, untested for magnitude): `semantic/score_pplx.py:56-63` fits PCA96 on
`Dall`, the concatenation of ALL RealTalk archives' document INT8 — i.e., the PCA evaluated
on each archive was fit on that archive's own test documents (plus siblings). Same
transductive class, exploratory arm only; magnitude UNVERIFIED (needs model payloads + rerun).

### F3 — HIGH — deterministic-hash tie-break hides ~0.7 pp of luck the CIs do not model

**Code.** All scorers rank with `SHA256("top10-r1|"+archive_id+"|"+row)` tie-break
(`audit/audit_baseline_lib.py:79-83`, `baseline/metrics_top10.py:74-81`,
`semantic/pplx_scorer.py:89-100`, verified-equivalent `fast_topk` in
`ablation_r2/perltqa/ablation.py:100-111` and `math_r1/quant/quant_math.py:93-103`).
No low-index favouritism anywhere — that part of the hunt is clear. The problem is
statistical, not implementational: sym scores are integers in [-96,0] (97 levels for up
to 1548 docs), so ties are structural, and every bootstrap
(`decision_tests.py:45-54`, `quant_math.py:527-544`, ablations) resamples queries while
holding the hash fixed — tie luck never enters the CI.

**Test** (`t_ties.py`, `python3`, numpy+hashlib only, scores recomputed from
`bench3/runs/b3a_realtalk/rt_repr/RT*.pkl` + `top10_comparison_r1/data/*.json`).

**Output (pasted).**

    n_queries=705
    sym det Hit@10 (salt top10-r1) = 46.5248
    sym exp Hit@10 (tie-averaged)  = 46.6809
    det - exp gap = -0.1560 pp
    sym det FR@3  = 22.8676
    sym exp FR@3  = 22.5535
    queries with tie AT the top-10 cut = 492/705 (69.8%)
    queries with tie AT the top-3 cut  = 250/705 (35.5%)
    distinct sym score levels per query: min=26, median=32, max=42
      salt top10-r1  Hit@10 = 46.5248
      salt salt-A    Hit@10 = 47.2340
      salt salt-B    Hit@10 = 47.0922
      salt salt-C    Hit@10 = 46.5248
      salt salt-D    Hit@10 = 47.2340
      salt-luck spread (max-min over 5 salts) = 0.7092 pp
      per-query disagreement: queries where 5 salts disagree = 20/705
    qscale queries with ANY tied doc pair = 705/705

det/exp reproduce the frozen G2 anchors (46.5248/46.6809) exactly — the harness is faithful.
69.8% of queries tie at the cut; re-salting moves headline Hit@10 by 0.71 pp with only
20 queries flipping. Any SIG/ns call within ~±1 pp on a sym-family arm (notably the C3
+1.0 pp gate scale, and the ±2 pp C1 scale) is being made with an unmodeled ±0.35 pp-ish
luck component. STOP (7.8 pp gap) is far outside this; borderline contrasts are not.
(The qscale "any tie" line counts exact-duplicate doc pairs anywhere in the ranking —
near-dup docs share codes; immaterial for the cut, included so nobody over-reads it.)

### F4 — HIGH — the float reference is chosen per-slogan: raw (36.60) vs standardized (48.51)

**Test** (`t_float.py`, invoked as `python3 -u -c "import t_float; t_float.main()"` —
direct `python3 t_float.py` printed nothing under this sandbox runner, so the explicit
form is the reproducible one): from cached production C/QC (k=96, n=705):

**Output (pasted).**

    n=705
    sym det     Hit@10 = 46.5248  (anchor 46.5248)
    qscale det  Hit@10 = 49.6454  (anchor 49.6454)
    raw float   Hit@10 = 36.5957  (ladder k96/float = 36.5957)
    std float   Hit@10 = 48.5106  (REPORT float_std = 48.51)
    qscale-dot vs standardized-cosine full-ranking agreement: 0/705 queries identical
    quant cost vs RAW float:  +9.93 pp (sign BEATS its float source)
    quant cost vs STD float:  -1.99 pp

**What this means.** `score_arms`' float (`ladder.py:153`) is raw cosine on centered C
(36.60); REPORT's "float_std (96 dims, uncompressed) 48.51" (`REPORT.md:24`) standardizes
axes first. Both reproduce — but they differ by ~12 pp and no doc states that LADDER.json's
float arms and REPORT's float row are different estimators. `FINAL_STATE.md:57-58`
"genuinely ours #6" ("sign ... adds ~10 pp over the float source it quantizes", sym 54.18
vs float 43.69 at k=384) uses the raw reference; against the standardized reference the
sign flips to −1.99 pp at k=96. A listed novel finding is reference-dependent. (My own
prior hypothesis that qscale-dot ≡ standardized-cosine ranking was falsified by the test:
0/705 — per-doc norms vary after centering, so the dot and the cosine rank differently.
Reported honestly; the reference-shopping point stands regardless.)

### F5 — MED — C1 readout quotes the Hit@10 gap for an FR@3 gate

C1 (per `DECISION_TESTS.md:6` and the referee rule) is FR@3-based: ≥+2.0 pp. From
`coordinator/DECISION_TESTS.json` (T1_fair_baseline): strongest BM25 frozen_idfonly
Hit@10 65.67 / FR@3 40.02; 48B qscale Hit@10 57.87 / FR@3 32.79 → Hit@10 gap −7.80 pp,
FR@3 gap −7.23 pp. Yet `FINAL_STATE.md:17` reads "FAIL (behind 7.80 pp at 48 B)" and
`DECISION_TESTS.md:102` reads "FAIL — behind by 7.80 pp at 48 B on RealTalk". Both cite
the Hit@10 number for an FR@3 gate. Verdict unaffected (both fail by ~7 pp); fix the two
cells to −7.23 (FR@3) or label the metric.

### F6 — LOW — REPORT §1 table mixes det and exp in one Hit@10 column

`REPORT.md:21-27`: "qscale 49.65" is det (49.6454); "sign96 46.68" is the tie-averaged
expected value (46.6809; det = 46.5248 — see F3 output). One column, two estimators,
0.16 pp. Immaterial to every verdict; fix by labeling or unifying (det: 46.52).

### F7 — MED — sym is labeled "standardized" but divides by nothing, and its own decline refutes the σ story

`ablation_r2/perltqa/t3_ladder.py:186-188` scores `sym` as `Dpm @ sign(QC).T` — no sigma
anywhere — yet `:231-232` labels it "standardized", as do `DECISION_TESTS.md` ("sym
(standardized)", T3 table) and `LADDER_REALTALK.md` ("hamming | yes"). Because sym never
divides by σ, the published mechanism ("with k_eff ≈ n−1 the trailing directions are
genuine but nearly singular, their σ is tiny ... dividing by it amplifies noise") cannot
explain sym's own 192→384 fall (FR@3 53.88→48.71, `DECISION_TESTS.md` T3 table; same for
the incoming package's hamming row 50.68→47.74 quoted in `LADDER_REALTALK.md`). This does
not re-report the known "σ-explanation incomplete" issue as new — it adds the crisp,
code-grounded falsifier the known issue lacked: the decline also hits the one arm the
mechanism cannot touch, so a second mechanism (e.g., noise dims accumulating Hamming
votes while signal saturates) must be operating. Fix: relabel sym/hamming as
unstandardized and amend the "That is the entire pattern" sentence in LADDER_REALTALK.md.

## (4) Checked and CLEAR (with evidence, not sampling claims)

- **Query/doc normalization symmetry.** Every stage treats docs/queries identically
(L2-normalize after each transform; shared doc-fit mu/sigma): `ladder.py:117-132`,
frozen `drive/...:652-657`, `ablation_r2/*` equivalents. The only asymmetry is qscale's
by-design query-only σ-division (`ladder.py:150-152`), which is disclosed in-code. No bug.
- **Tie-break implementation.** Hash-salt everywhere (refs in F3); `fast_topk` carries an
inline equivalence proof executed at import (`ablation.py:115-127`, `quant_math.py:106-118`);
my independent reimplementation hit all four G2 anchors to 4 decimals. No low-index bias.
- **Hit@k off-by-one.** `det_top10` returns exactly k (`audit_baseline_lib.py:79-83`);
`metrics` (`ladder.py:134-142`) uses `top[:3]` of the same ordering as a separate top-3
call would — identical by construction. Data→evaluated accounting: 705/705 RealTalk
queries (summed `data/RT*.json` vs `LADDER.json` n). No drops, no off-by-one.
- **dtypes/packing.** Signs via `>=0` booleans throughout; zero→+1 convention identical in
`metrics_top10.py:22-31`, `pplx_scorer.py:33-47`, all ablation scorers. INT8 via torch
half-even round per documented official semantics (`pplx_scorer.py:27-30`). 96/192/384 all
divide 8 evenly. No overflow, no endianness mismatch (big-endian pack/unpack paired).
- **MED thresholds / ITQ queries.** MED doc medians applied to query sym-bits
(`quant_math.py:505-513,589-590`); ITQ rotates queries with the same R
(`quant_math.py:480-490`); sigma recomputed in the rotated frame (`:486`). Correct.
- **BM25 k1→0 branch.** `decision_tests.py:151` (`s[i] += idf`) equals the k1→0 limit of
the BM25 formula (tf·1/(tf+0) = 1); `ladder.py:99-109` reaches the same value
arithmetically. Equivalent; not a bug.
- **FR@3 definition split (flagged, not counted twice).** `run_top10.py:233-234` scores
FR@3 as tie-expected recall while ladder/ablations/T1 use deterministic top3. Within T1
(code vs BM25) both sides are det — consistent where the verdict is decided. Cross-table
FR@3 comparisons against baseline-expected numbers inherit the F3-scale (±0.3 pp) wobble.

## (5) What I could NOT check and why

- **Second-archive replication of F2 / full-ladder INDEP rerun.** One held-out archive
(RT05, n=70) by design; a 10-archive INDEP ladder costs ~10 more projector fits and was
out of budget. The single point is bit-exact-validated, but the −36 pp magnitude is an
RT05 measurement, not a RealTalk average — treat it as existence + scale, not a new headline.
- **LoCoMo rerank rows (T2 input).** 164,256 stored paired rows are taken as data; the
reranker that produced them needs model weights + internet (unavailable). T2 arithmetic was
not re-derived.
- **Semantic PPLX arms.** Need model payloads/GPU; the PCA-transduction note (F2, related)
is code-evident but its magnitude is UNVERIFIED.
- **ITQ-vs-random re-derivation.** Accepted from the prior round; my conclusions do not
depend on it.
- **PerLTQA/LoCoMo byte audits.** Same code recipe as F1 (per-archive SVD96+TFIDF), so the
omission generalizes structurally (PerLTQA median N≈407 ⇒ similar ~60–70 KB/doc scale),
but I weighed only RT05 — stated, not extrapolated as fact.
- **Round-1 scope.** Deliberately not repeated: BM25/ladder/PerLTQA number reproduction,
LoCoMo gold discrepancy, hardcoded-paths portability, rerank-overgeneralization and
RealTalk-only-correction issues (all listed as already-known; no new evidence found on any).

## Appendix — exact reproduction commands (all run from `audit_hard_r2/code/`)

- `python3 -u -c "import runpy; runpy.run_path('t_ties.py', run_name='x')"` → F3 (numpy only)
- `python3 -u -c "import t_float; t_float.main()"` → F4/F6 (numpy only)
- `~/muse-work/ml-python -u -c "import runpy; runpy.run_path('t_bytes.py', run_name='__main__')"` → F1
- `~/muse-work/ml-python -u -c "import runpy; runpy.run_path('t_inductive_rt.py', run_name='__main__')"` → F2
- `~/muse-work/ml-python -u -c "import runpy; runpy.run_path('t_hybrid.py', run_name='__main__')"` → F2 decomposition
- `python3 t_transductive.py` (explicit-runner form if silent) → mechanism illustration only
- JSON arithmetic (F5/F6/query counts): inline `python3 -u -c` against
`top10_comparison_r1/coordinator/{LADDER,DECISION_TESTS}.json` (see report body)

Nothing outside this directory was written. No citations, numbers, paths, or results above
are invented: every number is either pasted tool output or byte-identical JSON arithmetic,
and every file:line reference was read in-session. Where a magnitude rests on one archive
or a toy demo, it is labeled as such.

