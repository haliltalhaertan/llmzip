[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# COMMON-MODE CLASSIFICATION — who pays for the ~44 MB projector?

PREPARED, NOT ACCEPTED. Answers task §1–§2 from committed bytes only.
No sealed material touched (see seal record in REPORT.md).

## Q1. What the float96 baseline actually IS

VERIFIED: the programme's float96 baseline (`FLOAT96_CENTERED`) is not an
independently-encoded vector. It is the centered continuous state of the SAME
per-archive fitted lexical+SVD pipeline whose elementwise sign is SIGN96.

Decisive lines (all VERIFIED by substring match in `verify_commonmode.py` A1–A4):

- `origin/findings/representation-geometry-2026-09-13:docs/v52/task4c2/v52_t4c2_centering_geometry.py:257` —
  `wv,cv,base_svd,Xw,Xc,Xl=adapter.fit_archive_representation(texts)`: one
  archive-only fit produces the word TF-IDF vectorizer, char TF-IDF
  vectorizer, and 32-D LSA state.
- Same file `:260-263` — `svd96=TruncatedSVD(n_components=96,random_state=5204)`,
  `Y=normalize(svd96.fit_transform(Z))`, `mu=Y.mean(axis=0,keepdims=True)`.
- Same file `:265-267` — the two arms are built from ONE `Y`, ONE `mu`:
  `C_float=np.subtract(Y,mu)` / `C_sign=Y.copy(); C_sign-=mu` / `C_itq=Y+(-mu)`.
- Same file `:285,287` — `fc_scores=cosine_centered(C_float,qC_float)` vs
  `signD=C_sign>=0`: float arm scores centered cosine, SIGN arm thresholds
  the same centered matrix at zero.
- Same file `:282` — `if same_max>1e-12: raise RuntimeError(...)`: the run
  ABORTS unless the three constructions agree to 1e-12. The "same input" is
  enforced, not assumed.
- `adapters/longmemeval_v52_adapter.py:147` — `def
  fit_archive_representation(memory_texts: list[str])`: the fit API accepts
  archive strings ONLY (no query, no gold, no question metadata).
- Same file `:172-174` — query path uses the FITTED objects:
  `wv.transform`, `cv.transform`, `svd.transform(Qw)`; T4C2 `:275-277` extends
  this through `svd96.transform(Zq)` and `qC_float=np.subtract(QY,mu)`.
- Corroboration from the audit line (T4F0):
  `audit_v52_t4f0_codex_2026_08_31/audit_representation_transfer.py:96-144`
  (`fit_once`): identical pipeline — fit word+char TF-IDF, latent SVD-32,
  hstack, SVD-96, normalize, archive-mean-center — with the canary query
  transformed through the fitted state at `:137-144`.
- Corroboration from the E1 line:
  `origin/research/e1-sign-float-mechanism-frozen-2026-09-13:campaign_2026_09_13/e1_mechanism/e1_geometry_core.py:1,12`
  — "consumes already-frozen C/qC arrays" and `sign=np.where(C>=0.0,...)`:
  E1's float and sign arms are likewise two scorings of ONE C/qC pair.
- Design binding (CLAIM, proposed-not-sealed text, but the rule it states
  matches the frozen code above):
  `origin/codex/twelve-byte-prereg-revision-2026-09-12:drafts/v52/twelve_byte_prereg_revision_2026_09_12/PREREG_DRAFT.md:71`
  — "Every arm consumes the same C/qC pair, except for the explicitly
  declared coordinate truncations."

To obtain a float96 vector for a document at query time, the following fitted
artifacts for THAT archive must exist: word vocabulary + IDF weights, char
vocabulary + IDF weights, latent-SVD components (32 × word-dim), mixed-SVD
components (96 × combined-dim), and the 96-D archive mean. The query path is
`wv.transform → cv.transform → sv.transform(Qw) → hstack → s96.transform →
(−mu)` (VERIFIED: PROJECTOR_BYTES.json `config.query_path`; T4C2 `:275-277`).
`TruncatedSVD.transform` uses only `components_` (CLAIM of the projector
report, consistent with sklearn API; `singular_values_` etc. are excluded
from the inventory for this reason).

Per-archive fitting is a RULE, not an accident:
`adapters/longmemeval_v52_adapter.py:363-367` — `cross_question_fit_prohibited`:
"fit_archive_representation is invoked independently per question archive";
prereg draft `:79-81` — "Archive-local state is fitted and charged to each
archive separately. No reuse across archives is assumed... Never amortize
state over all benchmark questions."

## Q2. Component decomposition and classification

Sizes VERIFIED by recomputation (B3): median archive `078150f1` (N=551),
format (a) float32 + structured vocab; parts sum EXACTLY to 44,220,235 B.

| # | Component | Bytes (median arch.) | Share | Classification | Evidence per row |
|---|-----------|---------------------:|------:|----------------|------------------|
| 1 | word vocab (structured UTF-8) | part of 1,151,987 | — | COMMON-MODE | `wv.fit_transform`/`wv.transform` — archive fit AND every query transform; adapter :154-160, T4C2 :257,275 |
| 2 | word IDF (`idf_`, f32) | part of 391,896 | — | COMMON-MODE | same use as (1); without it neither C nor qC exists |
| 3 | char vocab (structured UTF-8) | part of 1,151,987 | — | COMMON-MODE | `cv.fit_transform`/`cv.transform`; same argument |
| 4 | char IDF (`idf_`, f32) | part of 391,896 | — | COMMON-MODE | same use as (3) |
| 5 | vocab subtotal (1)+(3) | 1,151,987 | 2.61% | COMMON-MODE | PROJECTOR_BYTES.json per-archive components (VERIFIED sum) |
| 6 | IDF subtotal (2)+(4) | 391,896 | 0.89% | COMMON-MODE | same source |
| 7 | latent SVD components (32×W) | 5,041,664 | 11.40% | COMMON-MODE | `svd.fit_transform(Xw)` archive / `svd.transform(Qw)` query; T4F0 :119-121,141 |
| 8 | mixed SVD components (96×D) | 37,634,304 | 85.11% | COMMON-MODE | `svd96.fit_transform(Z)` / `svd96.transform(Zq)`; T4C2 :260-261,275 |
| 9 | archive mean mu (96) | 384 | ~0.001% | COMMON-MODE | subtracted by BOTH arms (`C_float`, `C_sign`, `C_itq`); T4C2 :265-267 |
| 10 | stop-words list, normalize/hstack state, shapes/scalars | <100 | ~0% | COMMON-MODE-trivial | code constant / stateless (CLAIM of projector report `excluded_with_reason`; consistent with adapter source: `stop_words="english"` literal at adapter :155) |
| — | SIGN-ONLY pipeline state | 0 | 0% | (empty) | sign is a stateless threshold (`>=0`); no fitted object exists that only SIGN needs |
| — | FLOAT-ONLY pipeline state | 0 | 0% | (empty) | float arm consumes C directly; no extra fitted object |
| — | QUERY-TIME-ONLY pipeline state | 0 | 0% | (empty) | every fitted object is needed BOTH to embed archive docs AND new queries — the fit products and the query-time requirements are the same set |

Arm-specific shared state (NOT common — cancels for nobody):

| Arm | Shared state | Bytes | Pays |
|-----|--------------|------:|------|
| SIGN96 | BinaryFlat S0 (header) | 33 | SIGN arm only |
| PQ96 | codebook S0 | 98,390 | PQ arm only |
| OPQ_PQ96 | rotation+codebook S0 | 135,325 | OPQ arm only |
| ITQ96 | 96×96 rotation (analytic f32) | 36,864 | ITQ arm only |
| SIMHASH96 | full-Haar matrix or regen state | 36,864 or seed-state | SIMHASH arm only |
| TOP32_RABITQ32 | index S0 | 202 | that arm only |
| FLOAT96 | per-vector payload 384 B/vec (NOT shared) | — | FLOAT arm only, per-vector |

(S0 values VERIFIED structurally in prior session receipts and re-asserted by
exact replay CLAIM; OPQ panel mean re-verified here: C2 = 287.6889713064.)

Bottom line of the classification: 100.00% of the measured ~44 MB pipeline
inventory is COMMON-MODE across every serious arm (SIGN, FLOAT, PQ, OPQ, ITQ,
SIMHASH, TOP32, TRUNC12), because every arm consumes the same C/qC pair.
The SIGN-ONLY, FLOAT-ONLY and QUERY-TIME-ONLY columns for pipeline state are
all EMPTY. The only non-common bytes are the small arm-specific codebooks /
rotations / headers above.
