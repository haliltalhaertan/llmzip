# V52 membership-under-scaling — completion map, 2026-09-08

**Documentation only.** This map records the current state. It is **not** authorization to write code,
change a design, execute anything, or seal. No component listed as missing may be started on the
strength of this document.

Every hash below is of a **raw Git blob** (`git cat-file blob <commit>:<path> | sha256sum`), never of a
checked-out file — the repository ships no `.gitattributes` and a Windows checkout hashes differently.

---

## 1. What exists, and at which commit

### Normative — the design this experiment must satisfy

| document | commit | sha256 |
|---|---|---|
| `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md` | `9b4af594` | `a99d547d525594ec6c6a12ff62f2cbb701cc05de01d7094233c90f21a0d71c71` |
| `…_DESIGN_REVISION_R2_2026-09-07.md` | `16019724` | `39cbfcea3a93307d582f9765529d6d99c09d0204706befa6470b8b932f451669` |
| `…_DESIGN_REVISION_R1_2026-09-07.md` (except §4, §5) | `2eadc41b` | `3d7a79b249e97a1bc2657a6782aec5e6a138f6a8c5e2681978ed66ad217b3391` |
| `…_PREREG_DRAFT_2026-09-07.md` (except §8) | `56c29416` | `3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399` |

### Built for this experiment

| component | branch @ commit | file sha256 | state |
|---|---|---|---|
| **computation core v3** — scaling operator, membership, rotation, Hamming distance, record validation, paired matrices, the three pp estimands, both bootstraps, safe writer | `impl/…-v3-2026-09-07` @ `dcb568d0` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` | **independently CLOSED** at `aa0ee8a9` (CLOSURE PASS) |
| **runner v1** — ingestion-boundary identity, six-check source contract, N-2 seed freezing, N-3 LongMemEval tag and cluster block, N-4 transform inheritance, result schema and writer | `impl/…-runner-v1-2026-09-08` @ `e61c414e` | `b322f85147733ead9494c33e5c78c02c2361a1986241de54c0c2aa6cc137a6d0` | prepared, **under independent review** |
| **corpus ingestion v1** — source byte identity before parse, bound-cohort resolution, archive units and gold rows, content policy | `impl/…-ingest-v1-2026-09-08` @ `22e44608` | `7dc084d8795c7e7d07270b866fdbc5e9c597508cbf331862b4075f9943fdf219` | written, **never executed on a real corpus**, **under independent review** |

### Accepted configuration — the fixed contract

| item | commit | sha256 |
|---|---|---|
| configuration identity (environment lock + seeds + sampling rules) | `e61c414e` | `33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739` |
| bootstrap seeds, machine-readable | `6911a03` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` |
| LoCoMo mapping — 1535 questions, 10 conversations | `6911a03` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` |
| LongMemEval mapping **v2** — 470-question cohort, one sentinel cluster | `e61c414e` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` |
| LongMemEval mapping v1 — **SUPERSEDED**, kept only so its hash resolves | `e61c414e` | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` |
| external acceptance record | `22e44608` | `c5d2e63956426f61f28b19856e1298ac964b3a8228b7acf72ae32128f79e1d83` |

Accepted in ledger entries **L-074** and **L-075** on `main` @ `aa42a96e`.

### Verified source identities

| source | bytes | sha256 | state |
|---|---|---|---|
| LoCoMo `locomo10.json` | 2,805,274 | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` | present locally, verified |
| LongMemEval `longmemeval_s_cleaned.json` | 277,383,467 | `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442` | present locally, verified |

### Review chain

| what | branch @ commit | report sha256 | verdict |
|---|---|---|---|
| implementation review of core v1 | `audit/…-impl-review-2026-09-07` @ `68819424` | `e245f0da2b0577f8940dfd906746f618638b45481280f93facb1774270bc3e98` | PASS WITH FINDINGS (F-1…F-12) |
| closure check of core v2 | `audit/…-v2-closure-2026-09-07` @ `712412a5` | `ec75beb4e054c4bc6e7c46aa5c2a006c749e2bd65b3d93f90543d31a1e19d0be` | CLOSURE PASS WITH FINDINGS (NEW-1…NEW-5) |
| closure check of core v3 | `audit/…-v3-closure-2026-09-07` @ `aa0ee8a9` | `aad45ff8fb6b88bda9a53b1182666ef0229a0ad2f1ff7d8baa0bf1bcca35b29a` | **CLOSURE PASS** |
| runner + ingestion review | commissioned 2026-09-08 | — | **in progress** |

---

## 2. What is missing

Three components stand between the current state and a runnable experiment. **None is authorized.**

| # | missing component | what it must do | why it is not covered by anything above |
|---|---|---|---|
| **M-1** | **representation stage** | word TF-IDF + char TF-IDF + LSA on the archive's memory units only, hstack, `TruncatedSVD(96, random_state=5204)`, normalize, archive-mean centring — and the query put through the **identical fitted objects** | the core's `scale_matrix` operates on an already-built 96-dimensional representation; nothing in the new lineage builds one. The runner's `fit_archive_transform` covers only the centring and `D`, not the vectorizers or the SVD |
| **M-2** | **scoring stage** | sign quantization at 0, Hamming distance, **top-3 with the audited tie and priority handling**, fractional R@3 against the gold rows, **20 nuisance trials**, over the **six arms** `NATIVE, SCALED_NATIVE, B32_FRESH, SCALED_B32, RANDOM32_FRESH, SCALED_RANDOM32` at all ten rotation seeds | the core has `hamming_dist` and the sign comparison, but no top-k, no tie handling, no fractional R@3 and no nuisance-trial loop. The runner consumes per-question records; nothing produces them |
| **M-3** | **orchestration** | drive ingestion → M-1 → M-2 per conversation and per benchmark, emit the per-question records the runner validates, and carry the diagnostics R1 §1 requires | no driver exists at any layer |

Also absent, by design and by instruction: a **pre-run seal**, and any HMAC material.

---

## 3. What would be reused from frozen code, rather than rewritten

These already exist, audited, in the earlier LoCoMo lineage. Reuse is the **expectation**, not a
foregone decision — how they are reused is part of the design work that has not been authorized.

| frozen artifact | commit | sha256 | what it supplies |
|---|---|---|---|
| `research/v52/locomo_sign_mechanism_replication.py` | `692f599e` | `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b` | `fit_archive_representation` and `build_representation` (**M-1**); `topks_by_hamming` with tie and priority handling, `fractional`, `stable_archive_seed` (**M-2**); the constants `SVD_SEED = 5204`, `SOURCE_LATENT_DIM = 32`, `N_NUISANCE = 20`, `TOPK = 3` |
| `research/v52/locomo_coordinate_scale.py` | `692f599e` | `df1bdded0a196ab62fc43363b5b90edba791a08ca6a3ebdb5a7c7a4d22a716a4` | the **shape** of a six-arm, ten-seed driver (**M-3**) — for its structure only; its arms are `FULLHAAR/BLOCK32` and its seeds `59001…59010`, so it is not this experiment |
| `adapters/longmemeval_v52_adapter.py` | `origin/main` | `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722` | LongMemEval acquisition path and the v1 archive construction |
| `adapters/longmemeval_v52_adapter_v2.py` | `origin/main` | `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` | the canonical memory-id form the ingestion already follows |

**Two cautions that belong with this table.**

1. The frozen replication is the **earlier** experiment. Its arms and rotation seeds differ from this
   one's. Reusing its representation and scoring machinery is reasonable; reusing its arm definitions
   or seeds would be a design error.
2. It **downloads and hashes the corpus itself** and reads `audit/errors_conv_*.json` to rebuild the
   cohort. The new lineage deliberately does neither: ingestion resolves the **bound** cohort and never
   derives one. Any reuse must take the computation and leave the acquisition and selection behind.

---

## 4. Mandatory gates remaining before a real run

In order. Each is a separate decision.

| gate | state |
|---|---|
| **G-1** independent review of runner + ingestion | **in progress** — commissioned 2026-09-08 |
| **G-2** disposition of whatever G-1 finds | not reached |
| **G-3** authorization to write **M-1**, **M-2**, **M-3** | **not granted**; no design or code authority exists for them |
| **G-4** independent review of those components once written | not reached |
| **G-5** authorization to execute the ingestion on a **real corpus** | **not granted** — the ingestion has never opened one |
| **G-6** a pilot decision, if one is wanted | not reached; no pilot is authorized |
| **G-7** a **pre-run seal** binding design, configuration, cohort, seeds, environment and code by hash | **not made** |
| **G-8** authorization for the run itself, and only then `finalize` | **not granted** |
| **G-9** a rerun of every suite under the accepted lock at seal time | not reached |

**Outcome boundary, unchanged.** Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME
ACCESS FORBIDDEN`. Nothing in this map alters it.

---

## 5. What is settled and must not be reopened

- **Core findings F-1 … F-12, NEW-1, NEW-2, NEW-3** — independently closed. Reopening them is a new
  round and needs its own authority.
- **The fixed cohort, the two mapping manifests, the three seed values and the environment lock** —
  accepted, and bound by the records in §1. They are preserved as they stand.
- **Still open and deliberately untouched:** NEW-4 and NEW-5 against the core (answered at the runner's
  ingestion boundary only); O-1, W-1, W-2 as backlog.
