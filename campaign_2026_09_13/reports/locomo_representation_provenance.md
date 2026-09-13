# LoCoMo Native Representation — Provenance, Specification, and Cross-Validation Targets
### (mechanism research track of the `llmzip` / V52 program)

Prepared: 2026-09-12 (UTC+03). Scope: read-only repository-byte and artifact analysis under
`C:/Users/MDP/dev/llmzip-work`. No pushes, no Drive writes. Work dirs: `scratch/`, `reports/`.

**Verdict (short).** The mechanism-track LoCoMo "native" representation **is** the T4D frozen
cross-benchmark construction: `mixed96 = [latent32, word TF-IDF, char_wb TF-IDF] -> archive-only
TruncatedSVD(96, random_state=5204) -> L2 normalize -> archive-mean center`, fit once per conversation
(10 independent fit units). The mechanism scripts do **not** import or read any precomputed matrix —
they contain an **inline copy** (semantic re-implementation) of the T4D `build_representation`, with
byte-pinned provenance (`FROZEN_SCRIPT_SHA256=3f7f091f…`) and an end-to-end numeric reproduction gate
(`FROZEN_NATIVE_FRAC_R3=0.23654714666441054`, error 0.0) recorded in every mechanism output. This pass
also **regenerated the matrices locally from the sealed T4D script** and matched all 10 per-conversation
count targets and the frozen native R@3 **exactly**. The missing Task1 coordinate statistics for LoCoMo
(the LongMemEval counterpartal CSV is `drive/V52_T4C3_native_heterogeneity.csv`, sha `148ae5b7…`) can
be computed from these regenerated `C96` arrays under the definitions decoded below. Remaining
uncertainty is mainly that **matrix bytes were never published** — equivalence is established by code
reading + exact metric reproduction, not by recorded matrix hashes, and cross-environment bit identity
is not asserted by any audit.

---

## 1. Evidence chain (branch / commit / path / sha256 per claim)

All repository objects were read with `git show <ref>:<path>` / `git cat-file` against
`C:/Users/MDP/dev/llmzip` (remote `github.com/haliltalhaertan/llmzip`, clone holds `main` at
`5ec3db60c03edde490374bf9cd7c3e56dd6bcd00` plus all origin branches).

**S1 — Mechanism-track branch.**
`git rev-parse origin/research/v52-sign-mechanism-locomo-2026-09-04` =
`0c9916bd7786d7ddb332f5b6da3d96d61a6223f0` ("register every coordinate-scale deviation…",
2026-09-07). Parent T4D commits exist in-repo: `canonical_parent_commit=8f52c8072f4f781ad2539c461fae154c4c52753b`,
`preregistration commit=68c4c10a6886e1076efcffd8981d53bf14fb9b6f` (both verified `git cat-file -t` = commit).

**S2 — T4D frozen script bytes.**
`drive/v52_t4d_locomo_frozen_cross_benchmark.py` (extracted from `drive/V52_T4D_ALL_OUTPUTS.zip`;
the ZIP-internal copy hashes identically):
`sha256 = 3f7f091fadc88dfcc1f68f38d6df10607d05d1e416d048fe776929a9a7b185a7` (63,381 bytes).
This equals, byte-for-byte:
- `sealed_compute_script_sha256` in `drive/t4d/V52_T4D_PRE_RUN_SEAL.json`
  (seal file sha256 = `8b1e65a99316002e4c1bf08406513d431c4bc1a53fa07352325f6573050d041d`, = manifest `pre_run_seal_sha256`),
- `"v52_t4d_locomo_frozen_cross_benchmark.py"` entry of `atomic_output_hashes` in
  `V52_T4D_POST_RUN_MANIFEST.json` (manifest raw sha256 = `a97e411c1ed24c5c93590638fcb51248936d8428a38e4d76cf0c6b74a9399b9c`),
- `SEALED SCRIPT SHA256` in `V52_T4D_HEAD_RESEARCHER_HANDOFF.txt`,
- `FROZEN_SCRIPT_SHA256` constant pinned in the mechanism script (`research/v52/locomo_sign_mechanism_replication.py`,
  blob `6700454915176854a55b0b5cf6ffe922a22e35f2`), line 26.
Upload-receipt linkage: the independent static-storage inventory audit
(`origin/audit/v52-static-storage-inventory-independent-2026-09-12`,
`audit_v52_static_storage_inventory_2026_09_12/FINDINGS.json`, finding `INV-AUD-001`) records that Drive
file `11cKt4hDPBazhrOSZxSgcT5Dw-w5kdpNi` (= `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt`, raw sha
`957e9e022f6f42ebf3e4f68eaa69cf1ec1f48367100a959a0ba9623caf5e1ddd`) is bound by the post-run manifest,
and that the manifest digest `a97e411c…` is bound by `V52_T4D_UPLOAD_RECEIPT.txt` (receipt bytes not in
the local working set; its binding is quoted in that audit, and our local copy of the manifest reproduces
the bound digest exactly). The transfer-proof `.txt` in `drive/t4d/` hashes
`957e9e02…` (manifest entry `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt`), i.e. the local download is the
exact published Drive artifact.

**S3 — Dataset and audit layer verified locally (2026-09-12).**

| artifact | declared | locally recomputed | result |
|---|---|---|---|
| `drive/locomo10.json` | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, 2,805,274 B | same | **MATCH** |
| `drive/audit_layer/` (20 files) | manifest sha `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06` | same (algorithm: sorted `conv_*.json`+`errors_conv_*.json`; rows `{file,bytes,sha256}`; `json.dumps(sort_keys, separators=(',',':'))`; sha256) | **MATCH** |

Every per-file size+hash in the table also matches the `AUDIT_FILE_HASHES` constant of the mechanism
script (see §3, full 20-row table).

**S4 — Function-source hashes reproduced locally: 2/2 PASS.**
The frozen script's own routine (lines 391–392, quoted verbatim):
```python
def source_function_hash(fn) -> str:
    return sha256_bytes(inspect.getsource(fn).encode("utf-8"))
```
i.e. sha256 over `inspect.getsource(fn)` (the `def` block as returned by linecache+`getblock`, then
`textwrap.dedent`), UTF-8 encoded. Reproduced by loading the extracted script as a module
(`importlib`, `main()` is guarded) with the work venv (Python 3.13.15, scikit-learn 1.8.0, NumPy 2.3.5):

| function | expected (proof/seal) | locally reproduced | verdict |
|---|---|---|---|
| `fit_archive_representation` | `48297fd495f400c02ad1a33769fd8f91d8930f6c7ff7f0e412981032d03ce564` | same | **PASS** |
| `fit_input_payload` | `4573ebdb2e5f04b414f110ab59ce256a225dd732a7a7aff064e29562fcbe25d4` | same | **PASS** |

Dedented block byte lengths: `fit_input_payload` = 163 B, `fit_archive_representation` = 951 B.
Script driver: `scratch/repro_source_hashes.py`; log: `scratch/regen_check_output.txt` (regen run).

**S5 — Adapter-family provenance (source-block family).**
`git cat-file blob 16c1349336e143d27d9cac68198cbb50a1e6340b` (`adapters/longmemeval_v52_adapter.py`)
-> sha256 `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722` = recorded;
blob `aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1` (`…_v2.py`) -> `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` = recorded.
The T4D comment `# BEGIN exact frozen source-block family implementation used by V52 adapter v1.`
(l.190) and l.198 ("matches the frozen V52 adapter source-block family") name these as the upstream
provenance of `fit_archive_representation`.

**S6 — Accepted T4C3 probe script.**
`accepted_task4c3_script_sha256=8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`
(proof l.11) equals the local `drive/v52_t4c3_coordinate_axis_probe.py` (**MATCH**). That probe is the
LongMemEval (470-archive) coordinate-axis stage; its `build_representation` is the same construction
with `SVD_SEED=5204` (probe line 18) and it produced the Task1 source CSV (§4).

**S7 — Mechanism-track representation provenance = inline copy, not import.**
No mechanism script imports the T4D script, and none reads precomputed matrices
(`grep -n 'np.load|.npy|.npz|pickle.load|read_parquet|loadmat'` over all six mechanism scripts: **NONE**).
They re-download the raw corpus + audit layer and re-fit the representation at run time:
- `research/v52/locomo_sign_mechanism_replication.py` (blob `6700454915176854a55b0b5cf6ffe922a22e35f2`,
  sha256 `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b`; last commit `adf6c45`, 2026-09-04)
  defines `fit_archive_representation` (l.190–200) and `build_representation` (l.203–221) inline — the
  exact copy quoted in §2 — and carries `DATASET_SHA256`, `AUDIT_MANIFEST_SHA256`,
  `FROZEN_NATIVE_FRAC_R3=0.23654714666441054`, `SVD_SEED=5204`, `SOURCE_LATENT_DIM=32`.
- Run source is byte-pinned by the workflow `.github/workflows/v52-locomo-mechanism.yml` (last commit `d4f4aa1`):
  `base64 -d … .gz.b64 | gzip -dc` then `sha256sum -c` against `a6ecee02…`.
  Local check: `git show origin/research/…:research/v52/locomo_sign_mechanism_replication.py.gz.b64 | base64 -d | gzip -dc | sha256sum`
  = `a6ecee02…` = sha256 of the committed `.py` (**MATCH**). Run on `ubuntu-latest`, Python 3.13,
  pip-pinned `numpy==2.3.5 pandas==2.2.3 scipy==1.17.0 scikit-learn==1.8.0`.
- Downstream scripts import the common source **by path via importlib** (quotes):
  - `locomo_spectral_band_haar_causal.py` (blob `7c414025…`): l.13 `COMMON_PATH = HERE / "locomo_sign_mechanism_replication.py"`; l.16 `COMMON_GIT_BLOB = "6700454915176854a55b0b5cf6ffe922a22e35f2"`; l.118 `common = load_common()`; l.124 `reps = [common.build_representation(c) for c in convs]`.
  - `locomo_boundary_localization.py` (blob `0e664314…`): l.14 `BASE_PATH = HERE / "locomo_spectral_band_haar_causal.py"`; l.86 `common = base.load_common()`; l.90 `reps = [common.build_representation(c) for c in convs]`.
  - `locomo_head_tail_two_subspace_causal.py` (blob `cb16d413…`): l.14, l.36–40 `load_base()`, l.49 same call.
  - `locomo_matched_random_partition_null.py` (blob `ebf76908…`): l.13, l.28, l.62–67 same pattern.
  - `locomo_coordinate_scale.py` (blob `13896ad9…`): l.24–25 `BASE_PATH = HERE / "locomo_spectral_band_haar_causal.py"`, `BASE_GIT_BLOB = "7c414025…"`; l.131 `reps = [common.build_representation(c) for c in convs]`.

**S8 — Cross-check of the frozen native value in both tracks.**
`0.23654714666441054` / `23.654714666441%` appears in:
- T4D: `V52_T4D_COMPUTE_REPORT.md` ("NATIVE_SIGN96 Fractional Evidence Recall@3: 23.654714666441%") and
  `V52_T4D_POST_RUN_MANIFEST.json` (`"native_fractional_R3": 0.23654714666441054`);
- mechanism outputs (branch `research/v52-sign-mechanism-locomo-2026-09-04`):
  `locomo_mechanism_outputs/locomo_mechanism_summary.json`: `"native_full96_fractional_R3_recomputed": 0.23654714666441054`, `"frozen_native_fractional_R3": 0.23654714666441054`, `"absolute_reproduction_error": 0.0`, `"frozen_native_reproduction_pass": true`;
  `locomo_causal_outputs/locomo_causal_summary.json`, `locomo_boundary_outputs/locomo_boundary_summary.json`,
  `locomo_head_tail_outputs/locomo_head_tail_summary.json`: `controls.native_reproduction = frozen_native = 0.23654714666441054`, `absolute_reproduction_error = 0.0`; same in `locomo_scale_outputs/locomo_scale_summary.json`.
All five other mechanism-stage summaries also pin `frozen_full_haar_R3 = 0.13770827054136`.

**S9 — Independent computational reproduction (external evidence).**
Branch `origin/codex/v52-locomo-reproduction-audit-2026-09-07`,
`audit_v52_locomo_reproduction_2026_09_07/REPORT.md` + `run_receipt.json`: one authorized invocation of
the unchanged sealed coordinate-scale runner reproduced **all 92,100 question-level scores exactly
(max numerical difference 0.0)**, NATIVE arm `0.23654714666441054`, on Windows 10, Python 3.13.15,
NumPy 2.3.5 / pandas 2.2.3 / SciPy 1.17.0 / scikit-learn 1.8.0, thread limits = 1. It explicitly does
**not** assert original OS/compiler/BLAS identity ("The original workflow used Ubuntu. Package versions
were reproduced, but original OS/compiler/BLAS identity was not asserted.") and notes that matching
scores cannot certify identical top-3 document selections ("The saved CSV contains question scores and
tie-scheme metadata, not selected document IDs.").

**S10 — Local regeneration executed in this pass (new evidence, 2026-09-12).**
Driver `scratch/regen_check.py` loads the extracted sealed script as a module and runs its own
`load_dataset` + `build_representation` + `topks_by_hamming`/`retrieval_metrics` on
`drive/locomo10.json` + `drive/audit_layer/` (work venv: Python 3.13.15, sklearn 1.8.0, NumPy 2.3.5;
`OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1`). Results (log `scratch/regen_check_output.txt`):
- per-conversation count fields: **10/10 MATCH** against `V52_T4D_REPRESENTATION_TRANSFER_PROOF.csv`;
- valid questions = **1535**; recomputed native audit fractional R@3 = **0.23654714666441054** with
  **absolute error 0.0** vs the frozen value.
Matrix fingerprints (see Appendix A) are recorded but are **not canonical** (no published matrix hash
exists; they are environment-specific sanity anchors).

**S11 — Artifact integrity of the T4D ZIP.**
All 25 files listed in `V52_T4D_POST_RUN_MANIFEST.json → atomic_output_hashes` are present in
`drive/V52_T4D_ALL_OUTPUTS.zip` and hash **exactly** as declared (25/25), including
`V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt` = `957e9e02…` and `.csv` = `cedbd908d33bba78f5ec3a9fcbf7fbda4f7905e755f4a2c3314ad5493957191c`.

**S12 — Where the outputs live.**
Mechanism outputs are committed on `research/v52-sign-mechanism-locomo-2026-09-04` (HEAD `0c9916bd…`)
under `research/v52/locomo_{mechanism,causal,boundary,head_tail,scale,random_partition}_outputs/`
(blob + content sha for the summaries are in Appendix B). The T4D publication set is Drive folder
`1u1sYaFav17j7i5-3Nd6RrOvRpWy8juZF` (per task brief; local mirror `drive/t4d/` + ZIP).

---

## 2. Exact representation specification

**Source text unit** (identical in T4D l.107–140 and mechanism l.127–150):
for each conversation, messages over `session_*` keys (excluding `*_date_time`), ordered by numeric
session index; each message must carry `dia_id`; text =
`f"{speaker}: {text}"` where `text = msg.text + " [IMAGE: {blip_caption}]"` when the caption is a
non-empty string (BLIP rule; caption appended **before** any fit). Two texts identical to the T4D script.

**Per-conversation fit unit.** One conversation = one archive = one *independent fit unit* (10 units).
`build_representation(conv)` fits: word TF-IDF, char_wb TF-IDF, latent source SVD (seed 5101),
mixed SVD-96 (seed 5204) and the centering mean — **archive memory texts only**. T4D executes the 10
units in a `ThreadPoolExecutor` and re-keys by `conv_id` (order-independent; no cross-talk).
`fit_input_payload` (T4D only, not present in the mechanism copy) is the identity function on
`list[str]` memory texts; a structural leakage barrier, semantically neutral. Forbidden fit inputs:
QA answers, gold evidence, category labels, answer/session metadata (static gate `PASS` in both).

**Feature construction** (T4D l.196–217; mechanism l.190–200 — byte-semantically identical):
1. `wv = TfidfVectorizer(lowercase=True, ngram_range=(1,2), stop_words="english", sublinear_tf=True)`;
   `Xw = normalize(wv.fit_transform(memory_texts))`
2. `cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5), sublinear_tf=True)`;
   `Xc = normalize(cv.fit_transform(memory_texts))`
3. `d = min(32, Xw.shape[0]-1, Xw.shape[1]-1)` (must be ≥ 24 else error);
   `svd = TruncatedSVD(n_components=d, random_state=5101)`; `Xl = normalize(svd.fit_transform(Xw))`
   (d = 32 for all 10 conversations).
4. `Z = sparse.hstack([csr(Xl), Xw, Xc], format="csr")` — concatenation order **[latent, word, char]**.

**Mixed96 + normalization + centering** (T4D l.646–657; mechanism l.208–219):
5. `s96 = TruncatedSVD(n_components=96, random_state=5204)`; `Y = normalize(s96.fit_transform(Z))`
   — **archive-only** fit; `random_state=5204` everywhere (cross-benchmark seed; the LongMemEval T4C3
   probe used the same 5204).
6. `mu = Y.mean(axis=0, keepdims=True)` — archive-document mean over the **normalized** 96-d vectors;
   `C = (Y - mu).astype(np.float64)`.
   So the native archive matrix per conversation is **C96 = L2-normalize(mixed SVD-96) − archive mean**,
   float64, shape (N_conv, 96).

**Query transform order** (post-fit only):
7. `Qw = normalize(wv.transform(questions))`; `Qc = normalize(cv.transform(questions))`;
   `Ql = normalize(sv.transform(Qw))`;
8. `Zq = hstack([csr(Ql), Qw, Qc])`; `QY = normalize(s96.transform(Zq))`;
   `QC = (QY - mu).astype(np.float64)` — the **same per-conversation `mu`**; queries are *not*
   re-normalized after centering. Category filter for queries: `category ∈ {1,2,3,4}`
   (282/321/96/841 = 1540).

**Retrieval semantics that the frozen native number uses** (needed only for the end-to-end check, not for
matrix regeneration): sign bits `C >= 0`, `QC >= 0`; Hamming distance; top-3 by lexsort
(distance, priority) with tie priority `priorities[t] = default_rng(stable_archive_seed(ci, t)+99).random(N)`,
`stable_archive_seed(ordinal, trial) = 5_100_000 + ordinal*100_000 + trial*100`, 20 nuisance trials;
per-question value = mean over trials of |top3 ∩ audit-corrected-gold| / |gold|; native R@3 = mean over
the **1535** audit-clean evidence-valid questions of 1540 (pre-outcome seal counts: raw-valid 1535,
audit-valid 1535, common valid 1534; unretrievable gold annotations are excluded from the metric
denominator).

---

## 3. Cross-validation targets a regeneration must match

### 3.1 Per-conversation fit block (exact; from `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt` and `.csv`, values agree)

| conv_id | N | archive_fit_docs | query_count | source_word_features | source_char_features | source_latent_dim | mixed_concat_features | mixed96_dim | no_nan |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| locomo_0 | 419 | 419 | 152 | 5704 | 14154 | 32 | 19890 | 96 | true |
| locomo_1 | 369 | 369 |  81 | 4377 | 11734 | 32 | 16143 | 96 | true |
| locomo_2 | 663 | 663 | 152 | 7636 | 16004 | 32 | 23672 | 96 | true |
| locomo_3 | 629 | 629 | 199 | 6885 | 15624 | 32 | 22541 | 96 | true |
| locomo_4 | 680 | 680 | 178 | 8121 | 17336 | 32 | 25489 | 96 | true |
| locomo_5 | 675 | 675 | 123 | 7449 | 15811 | 32 | 23292 | 96 | true |
| locomo_6 | 689 | 689 | 150 | 7672 | 17343 | 32 | 25047 | 96 | true |
| locomo_7 | 681 | 681 | 191 | 7289 | 16771 | 32 | 24092 | 96 | true |
| locomo_8 | 509 | 509 | 156 | 6107 | 15337 | 32 | 21476 | 96 | true |
| locomo_9 | 568 | 568 | 158 | 7137 | 15265 | 32 | 22434 | 96 | true |

Totals: 5,882 archive docs; 1,540 queries. Verified **10/10 locally on 2026-09-12** (S10).

### 3.2 Pinned provenance constants

| constant | value | source |
|---|---|---|
| dataset sha256 / bytes | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` / 2,805,274 | proof l.23; seal; script |
| dataset URL | `https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json` | mechanism script l.20 |
| audit-layer manifest sha256 | `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06` (20 files, sorted, `json.dumps(sort_keys, separators=(',',':'))`) | proof l.24; seal; recomputed locally MATCH |
| accepted T4C3 script sha256 | `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996` (= drive `v52_t4c3_coordinate_axis_probe.py`) | proof l.11 |
| T4D sealed script sha256 | `3f7f091fadc88dfcc1f68f38d6df10607d05d1e416d048fe776929a9a7b185a7` | seal / handoff / manifest / mechanism const |
| T4D pre-run seal sha256 | `8b1e65a99316002e4c1bf08406513d431c4bc1a53fa07352325f6573050d041d` | handoff; manifest; verified locally |
| T4D post-run manifest sha256 | `a97e411c1ed24c5c93590638fcb51248936d8428a38e4d76cf0c6b74a9399b9c` | manifest (self); receipt binding via INV-AUD-001 |
| proof `.txt` sha256 / `.csv` sha256 | `957e9e022f6f42ebf3e4f68eaa69cf1ec1f48367100a959a0ba9623caf5e1ddd` / `cedbd908d33bba78f5ec3a9fcbf7fbda4f7905e755f4a2c3314ad5493957191c` | manifest; verified locally |
| `local_fit_archive_representation_source_sha256` | `48297fd495f400c02ad1a33769fd8f91d8930f6c7ff7f0e412981032d03ce564` | proof l.12; reproduced PASS |
| `local_fit_input_payload_source_sha256` | `4573ebdb2e5f04b414f110ab59ce256a225dd732a7a7aff064e29562fcbe25d4` | proof l.13; reproduced PASS |
| adapter v1 blob / sha256 | `16c1349336e143d27d9cac68198cbb50a1e6340b` / `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722` | proof l.5–7; verified |
| adapter v2 blob / sha256 | `aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1` / `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` | proof l.8–10; verified |
| mechanism run source sha256 / blob | `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b` / `6700454915176854a55b0b5cf6ffe922a22e35f2` | workflow pin; verified from bytes |
| BLIP rule | append exact non-empty caption as `" [IMAGE: {caption}]"` to message text before archive fit | proof l.20; T4D l.107–114 |
| fit payload | archive memory text strings only; forbidden: QA answers, gold evidence, category labels, answer/session metadata | proof l.17–19 |
| LoCoMo unit transfer | one conversation = one archive fit unit; all Cat1–Cat4 queries in that conversation share the archive-only fitted representation | proof l.21 |
| tie priority | `stable_archive_seed(conversation_ordinal,trial)` = `5 100 000 + ordinal*100 000 + trial*100`; then `default_rng(seed+99).random(N_archive)` | proof l.22; T4D l.235–236, 734 |
| query transform timing | only after archive vectorizers/source SVD/mixed-96 SVD are fit | proof l.18 |
| expected cohort | 10 conversations; 1540 Cat1–4 questions (282/321/96/841); 156 audit corrections; raw-valid 1535 / audit-valid 1535 / common-valid 1534 pre-outcome | seal; script constants |
| environment | Python 3.13; `numpy==2.3.5 pandas==2.2.3 scipy==1.17.0 scikit-learn==1.8.0`; threads=1 | mechanism/scale workflow + `environment.txt`; audit receipt |

Audit-layer 20-file table (filename, bytes, sha256) — must match all 20 rows; full list lives in the
mechanism script `AUDIT_FILE_HASHES` and in the seal `audit_layer_file_hashes`; e.g.
`conv_0.json (395163,697a996d…)`, `errors_conv_9.json (15645,2c2b8791…)`; manifest recomputation MATCH
re-verified locally.

### 3.3 Metric anchors (end-to-end; a regeneration of C/QC plus the frozen metric must reproduce these)

| anchor | value | source |
|---|---|---|
| NATIVE_SIGN96 fractional R@3 | `0.23654714666441054` (= 23.654714666441%) | T4D report/manifest; all 5 mechanism summaries; **reproduced locally with abs error 0.0** |
| HAAR96 mean fractional R@3 | `0.13770827054136` (13.770827054136%); seeds 43001–43005 = 0.12991972305653088 / 0.13805874420587866 / 0.14360296073813988 / 0.13537524120298597 / 0.14158468350325026 | T4D report + manifest `haar_seed_fractional_R3` |
| ITQ96 fractional R@3 | `0.14220856478786312` | manifest |
| signed-permutation control / continuous invariance | PASS exactly / max err `1.6653345369377348e-15` | T4D report; mechanism summaries |
| scale-stage arm means (NATIVE / SCALED_NATIVE) | `0.23654714666441054` both | `locomo_scale_summary.json`; audit reproduction REPORT.md |
| causal/boundary/head-tail stage controls | `native_reproduction = frozen_native = 0.23654714666441054`, abs err 0.0 | the three summaries |

### 3.4 Task1 coordinate-statistics targets (definitions decoded and re-verified)

The L093 static-storage diagnostics (ledger `docs/CONTINUITY_LEDGER.md`, lines 1988–1989 on
`origin/audit/v52-static-storage-inventory-independent-2026-09-12`) pinned these numbers for the
**LongMemEval** 470-archive native representation, recovered from `drive/V52_T4C3_native_heterogeneity.csv`
(sha256 `148ae5b727ce1aedc6c84ee9c00727f1454b0e0710d100ac8154fdf8d00924cb` — **matches the drive copy
exactly**, 470 rows × 96-d variance_vector/occupancy_vector). Decoded definitions (all three means
reproduced from the CSV in this pass):

| statistic | definition (decoded) | ledger value | repro-verified |
|---|---|---|---|
| `CV_sigma` | per archive: `std(σ_i)/mean(σ_i)` with `σ_i = sqrt(variance_vector_i)` = per-coordinate std of the centered native matrix; then mean over archives | `0.4974774993` | `0.4974774992684583` |
| `H_ge` | per archive: mean over the 96 coordinates of binary sign-occupancy entropy `H(p_i)`, `p_i = mean(C[:,i] ≥ 0)`; then mean over archives ("zero below local 0.75" = min-archive check) | `0.9970337299` | `0.9970337299075775` |
| first32 variance share | per archive: `sum(v[:32]) / sum(v)` (v = coordinate variance vector); then mean over archives | `0.7598736235` | `0.7598736235405325` |
| `H_gt`, `D4` | requested but **not available** in published bytes; strict `>0` / zero-mass variants; definitions not pinned in the inspected working set | unavailable | — |

The full canonical coordinate-statistics function is `hetero(C)` in `drive/v52_t4c3_coordinate_axis_probe.py`
(l.37–40): variance_vector, variance_cv, normalized_variance_entropy, variance_participation_ratio,
max_median_variance_ratio, cov_offdiag_frobenius_energy_ratio, mean_abs_coordinate_correlation,
sign_occupancy mean/min/max/MAD-0.5, occupancy_vector. For LoCoMo these are undefined per the ledger
("LoCoMo frozen representation not found") and are exactly the *missing diagnostics* a local
regeneration of `C96` (per conversation) can now supply — apply `hetero()` to each conversation's `C`
and aggregate as the L093 report did (per-archive values then mean; weight/aggregate choice must be
pre-declared, mirroring the LongMemEval reporting).

---

## 4. The explicit question

> **Is the mechanism-track LoCoMo representation the same construction as the T4D frozen cross-benchmark
> representation (mixed96 = [latent32, word TF-IDF, char_wb TF-IDF] → archive-only TruncatedSVD(96,
> random_state=5204) → L2 normalize → archive-mean center)?**

**Yes — with the precision that it is a semantic re-implementation (inline copy), not a shared import or
a stored artifact.** Evidence: (i) `build_representation`/`fit_archive_representation` in
`locomo_sign_mechanism_replication.py` (blob `67004549…`) are line-for-line the same pipeline — same
vectorizer parameters, same `[latent, word, char]` order, same seeds 5101/5204, same normalize/center
order, same per-conversation fit unit, same query transform order; the only textual differences are a
removed docstring, condensed formatting, and the absence of the identity `fit_input_payload` barrier;
(ii) every mechanism stage re-checks the frozen end-to-end value `0.23654714666441054` and records
`absolute_reproduction_error = 0.0`; (iii) an independent reproduction audit re-ran the sealed pipeline
with **all 92,100 question scores identical (max diff 0.0)**; (iv) in this pass I regenerated the
matrices directly from the sealed T4D script and matched the 10 per-conversation count blocks and the
native R@3 exactly. The construction is also the cross-benchmark one in the wider sense: the same
`fit_archive_representation` family is used by the LongMemEval adapters (blob/sha verified) and the
LongMemEval T4C3 probe built its native 96-d space with `SVD_SEED=5204` the same way.

> **Is this the native representation whose coordinate statistics Task1 wants?**

**Yes for everything that is definable in the available bytes.** The open Task1 item is precisely
"Recover exact mechanism-track frozen C arrays or source-bound sufficient statistics for remaining
Task1" with the registered gap "LoCoMo frozen representation not found" (ledger, `next_single_action`
in `ops/CURRENT_STATE.json` on the 2026-09-12 branches). The arrays Task1 wants for LoCoMo are the
per-conversation `C` (centered mixed96, but note: the Task1 statistics operate on `C` — the centered
matrix, *not* re-normalized) — the same state the coordinate-scale stage uses (`scale_rule: d_i = 1/σ_i
on the centered archive representation, per archive, epsilon=1e-12`). This pass has now established a
byte-verified regeneration route for those exact arrays from the pinned corpus + sealed script, and
decoded the three L093 statistic definitions (§3.4) so the missing LoCoMo numbers can be computed and
compared. What Task1 explicitly asked but that the *published bytes* do not define (`H_gt`, `D4`,
zero-mass variant) remains unpinned — see uncertainties.

### What remains uncertain (do not overclaim)

1. **No matrix bytes were ever published.** No sha256 of any `C`/`QC`/vocabulary/`mu`/SVD component
   exists in the sealed artifacts. Equivalence rests on (a) code-level reading of a copy, (b) end-to-end
   numeric reproduction of the retrieval metric (which is a many-to-one function of the matrices), and
   (c) the 10 count blocks. Bit-identity of the mechanism-track matrices with the T4D-run matrices is
   therefore *inferred*, not directly attested. (The fingerprints in Appendix A are local, not canonical.)
2. **Environment identity is not fully asserted.** Original T4D run environment (2026-08-29) is not
   recorded in the artifacts inspected (its workflow was Ubuntu; package pins visible only from the
   later mechanism/scale runs and the reproduction audit). The independent audit reproduced everything
   on Windows with the same *package versions* but "original OS/compiler/BLAS identity was not
   asserted". Cross-platform bit-identity of TF-IDF/SVD internals is therefore unproven; same-stack
   reproduction is demonstrated (twice).
3. **Scores ≠ selections.** Matching question scores cannot certify identical top-3 *document id*
   selections under score ties (audit's own limitation statement); the frozen tie-priority rule is
   pinned, but the published score files don't contain selections.
4. **The mechanism copy's own function-source hash is nowhere recorded.** The two proof hashes hash the
   *T4D script's* functions (`48297fd4…`, `4573ebdb…` — reproduced PASS). The mechanism copy is pinned
   only by whole-file sha (`a6ecee02…`). Equivalence between the two texts is by reading + numerics, not
   by hash equality.
5. **Per-conversation spaces are independent fits.** Even with the same seed, `SVD96(5204)` is fit on
   each conversation's own `Z`; coordinates are not shared across conversations, so Task1 statistics
   must stay per-archive before aggregation, and no cross-conversation coordinate alignment should be
   assumed.
6. **Task1 scope caveat.** The L093 diagnostics scope said "no raw corpus reconstruction"; the
   regeneration established here is a *research-stage reproduction* from the pinned corpus (explicitly
   the purpose of the present session). If Task1's own acceptance wording matters, the regeneration
   route should be declared as such rather than presented as "recovery of a stored artifact".
7. **`H_gt` / `D4` / zero-mass definitions** are not pinned in the inspected bytes; computing them
   requires the L093 task definitions (not in this working set). The three decodable statistics
   (CV_sigma, H_ge, first32 share) are fully pinned and reproduced.
8. **sklearn internals sensitivity.** Regeneration is authoritative only under the pinned stack
   (`scikit-learn==1.8.0`, etc.). Changing sklearn/numpy versions may perturb TF-IDF tokenization or
   randomized SVD and break the exact `0.23654714666441054` match.

---

## Appendix A — Local regeneration recipe and fingerprints

```bash
cd C:/Users/MDP/dev/llmzip-work/scratch
C:/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe regen_check.py   # sets thread env vars to 1 internally
```
(`regen_check.py` loads `../drive/v52_t4d_locomo_frozen_cross_benchmark.py` via importlib, reads
`../drive/locomo10.json` + `../drive/audit_layer/`, prints the counts comparison, the native R@3, and
C/QC sha256 fingerprints. Output: `regen_check_output.txt`.)

Local fingerprints (float64 C-order bytes of `C` and `QC`; **non-canonical**, env-dependent, recorded
for future same-stack comparisons):

| conv | C sha256 | QC sha256 |
|---|---|---|
| locomo_0 | `565582c92a5f595c39156e4e72caa28a78cbe36337d507345ccba12f06ffc931` | `cb0b0b5236ce0ea10166b9c10a8b086d45ef8e88c7ea8949b80168b533b2f210` |
| locomo_1 | `5ac62ad91c1d5ca33a5a83beaa385c99035ac2a08dadd5b69a908ba0e1cda7c2` | `e5049a06bfdd34bbee13a95862c4c92aba2723c20ab41cc34daa0ad1718d1026` |
| locomo_2 | `2b5f4d958b9e607919b297ec737069243defcf2886df6249776fd60fbe9c5471` | `e719bdf5c829d399485ad4bbd9931ae3ea0971d40624b51711d542f76390c8db` |
| locomo_3 | `bf036ca67c7e025afc2a250820c48473eeb81f3447ec6fa7d1ab00666bad1d4a` | `354a814e08ad211b3bc326c2eb6956f9c4c4a8bd0724c5dd3913af1a18656f0b` |
| locomo_4 | `9eb03dacca67b5964224edaad3ace7450c4cd50dc0c5fc9bb96f5f51f9cec40d` | `01e94f36a98de73f32929560cb57c6e7320e62513904fe7b853ebbc3eafda01a` |
| locomo_5 | `896f3de3d7d20e9f54926d28084c7b5037b6172e82a03ea80dfdb39e5de546ec` | `b564e77dd717d133ce4c4bd7d7da93cdf4b57b5c9d7eaa5598fbda126e5ca0ea` |
| locomo_6 | `668ddeb335e9fc16c03ed5c3c59cfecf71f8d51deaefe2a9c40718e476eb45f3` | `a8a3ba5df7bf203c00a59970560fb00d8768c6808bd6459b61a9e28a10ab5920` |
| locomo_7 | `e0cf8e1fee62d5db3895c49ccee3590d221ffde0f0e82a9c8e4ba750f50e0c78` | `1167fdd403c7cd0f17dc587525409250f3b279ec5b667ddfcb92a3584fd3050f` |
| locomo_8 | `6f543e5de070a4e2cfb654638e82cddbcbe2d0edd4f34cdaed4060478d71a3c4` | `3075f779b5955b549f8e3cd0c741e2baadc36a22c219afcb719821522fcea6d8` |
| locomo_9 | `380a0ba50c52e8be0f794cd3669c7e656082f34240730c5d211db675780d8592` | `79daf0a064c142702eafad50f28521967771336319c626ac76e897fb77e3d9b9` |

Additional evidence files produced/used in this pass (under `C:/Users/MDP/dev/llmzip-work`):
`scratch/repro_source_hashes.py` (function-hash reproduction), `scratch/regen_check.py` +
`scratch/regen_check_output.txt` (counts + native R@3 + fingerprints), `scratch/mech/` (byte-exact
copies of the six mechanism scripts and four docs read via `git show`), `scratch/t4dzip/` (full T4D ZIP
extraction used for the 25/25 manifest verification).

## Appendix B — blob/content hashes of key mechanism-track files (branch `research/v52-sign-mechanism-locomo-2026-09-04`, HEAD `0c9916bd…`)

| path | git blob (sha1) | sha256 (content) |
|---|---|---|
| research/v52/locomo_sign_mechanism_replication.py | `6700454915176854a55b0b5cf6ffe922a22e35f2` | `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b` |
| research/v52/locomo_spectral_band_haar_causal.py | `7c4140252fb7f846d617189925cdf534515743f4` | `58b28c4ed0a62896710ae5ebd1c07574c29b6b5bb424de6c1bfac206ea903a15` |
| research/v52/locomo_boundary_localization.py | `0e66431449ad48b5f24049e0c05d65c917d8b893` | `2d849d32c3274fe3a4ba372245b4d4b32dc9c7520110e42df4024235e6eedb1a` |
| research/v52/locomo_head_tail_two_subspace_causal.py | `cb16d4136c6280875b7c5875ffd89f9fc01cb810` | `835669586c5f96e24f54dba7a85ebad4ff4dc6f417d169dac01cbca58af080d5` |
| research/v52/locomo_matched_random_partition_null.py | `ebf76908c73bbf266c04f6ae05537a03e70c7526` | `068b5e8b09b21ce039154220ff37068d97941fc85d292118f86612819f10d8aa` |
| research/v52/locomo_coordinate_scale.py | `13896ad93c58dbb0febeadf82d0c22b64a920915` | `df1bdded0a196ab62fc43363b5b90edba791a08ca6a3ebdb5a7c7a4d22a716a4` |
| research/v52/locomo_mechanism_outputs/locomo_mechanism_summary.json | `b2ff1b6cb4d244100da9a42e7a0c60d6eacf3162` | `e9122c0b3492888ba56c101e2bcaed5865c65fb344a2449a7e33c6de42f49fd4` |
| research/v52/locomo_causal_outputs/locomo_causal_summary.json | `5ee4b0377e8193c49f2721ac49371cc02e7a41fa` | `d1d52b2ff6277405237ee24f6e6865813d919d0d271a31b69ca59ed9b61603a1` |
| research/v52/locomo_boundary_outputs/locomo_boundary_summary.json | `89c30a2a58fd638809477ded0d41b996f051c0f1` | `5d25ed4f31bdc27e050cfd60b31687bbb384cfa4de3c72338f5c012548809761` |
| research/v52/locomo_head_tail_outputs/locomo_head_tail_summary.json | `228f756447e70c73f40b6074a44f13acabdabc08` | `71c45b615a4073c5eeeb9c38e0d4dca3c984e34989ba4f3b12d27df279cc2f8f` |
| research/v52/locomo_scale_outputs/locomo_scale_summary.json | `2664f72298569533da151b1002f006684fb82ac0` | `f878e19a091d0bccbf835231449debbb6f8299bc2dd8f81198891e322c9a9b0e` |

Per-file last-commit (branch): sign-mechanism script `adf6c45` (2026-09-04; same commit records the
mechanism outputs), spectral-band `774a125`, boundary `e14cf8a`, head-tail `90112d3`, matched-null
`e548616` (all 2026-09-04); causal outputs `91c0de3`, boundary outputs `89e38d1`, head-tail outputs
`cf5eca7`, coordinate-scale script `59ae1b5` and scale outputs `f1bbb50` (all 2026-09-07); mechanism
workflow `.github/workflows/v52-locomo-mechanism.yml` `d4f4aa1` (2026-09-04).
