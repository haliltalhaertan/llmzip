# Google Drive inventory — llmzip research project (`LLM_TOKEN_ZIP_RESEARCH_MASTER`) and the search for the "frozen representation matrices"

- **Date:** 2026-09-12 (Europe/Istanbul)
- **Owner / account:** haliltalhaertan@gmail.com (display name: Halil Talha Ertan)
- **Access:** existing Hermes Google Workspace OAuth token (`google_token.json`), **read-only usage** (no uploads, no deletes, no trashing, no sharing, no permission changes; nothing in the project tree was modified)
- **Companion file:** `C:/Users/MDP/dev/llmzip-work/reports/drive_inventory.csv` (296 lines: header + 295 data rows; columns `folder_path,name,id,mimeType,size,modifiedTime`)
- **Local downloads (left in place for further inspection):** `C:/Users/MDP/dev/llmzip-work/drive/`

---

## 1. Coverage statement

### What was enumerated

**A. Full recursive enumeration of the llmzip project tree.** Four seed IDs were expanded by recursive folder listing (paginated `files.list`, fields incl. `size`, `md5Checksum`, `parents`, `owners`):

| Seed (given) | Resolved name | Real parent |
|---|---|---|
| `1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv` | `LLM_TOKEN_ZIP_RESEARCH_MASTER` | My Drive root (`0AE7zs2LgBcb5Uk9PVA`) |
| `1u1sYaFav17j7i5-3Nd6RrOvRpWy8juZF` | `V52_TASK_4D_LOCOMO_FROZEN_CROSS_BENCHMARK_REPLICATION_2026-08-29` | inside MASTER |
| `1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv` | `FINAL_2026-08-28_FULL_470` | inside MASTER / `V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE` |
| `17JSHz_64KvKIJwzEPshUuwgld8Smczht` | `V52_CAUSAL_SPECTRAL_BAND_HAAR_2026-09-04` | inside MASTER |

All four seeds descend from `LLM_TOKEN_ZIP_RESEARCH_MASTER`. The enumeration covers **22 folders, 216 unique files, 583,038,619 bytes** (556 MiB). Folder tree (counts = files):

```
LLM_TOKEN_ZIP_RESEARCH_MASTER                          (2)   [longmemeval_s_cleaned.json/.rar]
├── 00_PROMPTS_MASTER_ARCHIVE                         (16)
│   └── V52_TASK_4C2_AUDIT_PROMPTS                     (1)
├── 01_LITERATURE_REVIEWS                              (1)
├── LLM_Memory_Research_Checkpoint_2026-08-23_V51      (6)
├── LLM_Memory_Research_V52_T2_External_Audit          (8)
├── LLM_Memory_Research_V52_T2_RAW_EXTERNAL_AUDIT      (8)
├── RECOVERED_FROM_FILE_LIBRARY                        (2)
│   ├── 01_V51_T1_RECOVERED                            (6)
│   ├── 03_T3_T4_RECOVERED                             (1)
│   └── 04_T4C0_T4C1_RECOVERED                         (2)
├── V52_CAUSAL_SPECTRAL_BAND_HAAR_2026-09-04          (25)
├── V52_STATIC_STORAGE_INVENTORY_INDEPENDENT_AUDIT_2026-09-12 (2)
├── V52_TASK_4C2_AUDIT_PACKAGE                         (1)
├── V52_TASK_4C2_CENTERING_GEOMETRY/FINAL_2026-08-27_FULL_470 (27)
├── V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE/FINAL_2026-08-28_FULL_470 (29)
├── V52_TASK_4D_LOCOMO_FROZEN_CROSS_BENCHMARK_REPLICATION_2026-08-29 (31)
├── V52_TASK_4E0_LONGMEMEVAL_V2_ADAPTER_ESTIMAND_FREEZE (33)   [two sibling folders share this name, ids 1z_70bzjdMZ…, 10arzKV5sHDz…]
└── V52_TASK_4F0_BEAM_LARGE_SCALE_ADAPTER_EVIDENCE_FREEZE_2026-08-29 (15)
```

85 file IDs are reachable via two path strings (master-nested and seeded-root walk). The CSV normalizes every file to its **real parent chain** (single canonical `folder_path` per file ID), so no double counting: 216 unique file rows + 22 folder rows + top-level / trash / outside rows = 295 rows.

**B. My Drive top level** — all 22 children (`q='root' in parents`); identical set returned for the drive root id `0AE7zs2LgBcb5Uk9PVA`. `drives().list` returns **no shared drives**.

**C. Trash** (`trashed = true`) — 7 items, all "Adsız doküman"/"Input :" Google Docs (≤29 KB); nothing representation-related.

**D. Shared with me** — 1 folder (`1OYVWe7hv_gihkO_D9ixJCwbChsjpyLpp`, owner sarabrain513@gmail.com). Its only child is a 7.08 GB game archive (`Stellaris Galaxy Edition.(v3.14.15).zip`) — unrelated to the project; not further enumerated.

**E. Account-wide name sweep** (45 `name contains` queries, case variants included; the operator is case-insensitive — case variants returned identical counts): `pkl, cache, cache_repr, npy, npz, matrix, tensor, emb, embedding, representation, heterogeneity, C9, codes, queries, gold, repr, sufficient, stat, frozen` + follow-ups `C96, mixed96, cache_results, Frozen_Representation, fitted, npz, locomo10, longmemeval`. 311 unique matching file IDs; 20 of them inside the project tree (all accounted for in §3B), 291 outside (classified in §3C).

**F. Ancestry resolution** of every non-project hit family (walking `parents` to root) to identify the owning program.

**G. Content inspection.** 23 files (~41 MB total; largest single download 13.5 MB) downloaded and inspected; plus pre-existing local copies of `V52_T4C3_ALL_OUTPUTS.zip`, `V52_T4D_ALL_OUTPUTS.zip`, `locomo-audit-main.zip`. Member listings of **all 20 unique project zip names** (22 zip objects) plus nested `V51_CORE_AUDIT_PACKAGE.zip` and `locomo-audit-main` internals were scanned for `*.pkl/.npy/.npz/.pt/.h5/.parquet/.bin/.mat` entries; binary NPZ bundles were opened and their array keys/shapes/dtypes dumped.

### API call count

**193 read-only Drive API calls total** (`files.list`/`files.get`/`files.export`/media downloads), well under the ~400 budget:
phases: enumeration 29, name sweep 41, ancestry/classification 56, id resolution 8, download batch 1 (14 files) 28, download batch 2 (9 files) 18, drive-root/drives 2, final searches/folder 7, id lookups 2, setup probes 2.

### What was NOT enumerated (explicit gaps)

- **Deep contents of the other top-level research folders** — `PROJECT_AUTOGENESIS` (phases B2B/B3/C0V9 and `CURRENT_RESEARCH_2026_08_25` were probed only where files matched search terms; the rest of the subtree was not walked), `Riemann Hipotezi — Araştırma Arşivi`, `Collatz Problemi — Araştırma Arşivi`, `CP20_PUBLICATION_FACTOR_PRESSURE_V1_2026-09-04`, `FUNCTION_PRESERVING_QUANTIZATION_RESEARCH_CHECKPOINT_2026-08-24` (1 level only), `autogenesis-meta`, `autogenesis-meta_guncellemeler_2026-08-24`. Name-sweep coverage (§1E) still applies to all of them.
- File **revision history** of any Drive object; Drive Activity log; Google Docs bodies other than the two audit docs noted below; comments.
- Contents **inside** the 7.08 GB shared game zip; inside non-project reproducibility zips (`C908/C909A/C910_*` bundles etc. — other programs).
- Files reachable only via another account's hierarchy (only the single shared item above exists).

---

## 2. Key findings (evidence)

### F1 — No `cache_repr/*.pkl` or equivalent serialized caches anywhere on Drive

- `name contains 'cache_repr'` → **0 hits** (both cases). `'cache_results'` → 0. `'C96'`, `'mixed96'`, `'Frozen_Representation'`, `'fitted'` → 0.
- `name contains 'pkl'` → 4 hits, all vendored NumPy test data (2026-08-20) inside `autogenesis-meta/.venv/.../numpy`: `astype_copy.pkl` (716 B), `generator_pcg64_np126.pkl.gz` (208 B), `generator_pcg64_np121.pkl.gz` (203 B), `sfc64_np126.pkl.gz` (290 B). Nothing project-related.
- `name contains 'npy'` → 35 hits, `'npz'` → 5 hits — all vendored numpy/matplotlib package files (same `.venv`), e.g. `bivariate_normal.npy`, `topobathy.npz`, `goog.npz`.
- Trash contains no archives/data — 7 empty-ish Google Docs only.
- The only array-format file inside the project tree is the 470-NPZ bundle in F2 (found by content scan, not by name); the other NPZ found on Drive (C0V9 controls, F5) lies outside the project tree.

Corroboration from inside the project itself:
- The T4C3 pipeline only ever writes its caches to a **local work dir**: `v52_t4c3_coordinate_axis_probe.py` (file id `1Mvd54Y3LjSbZClrADOHHvVBDifses74o` — matches the seed ID given in the task): `a.repr=a.work/'cache_repr'; a.res=a.work/'cache_results'`, and pickles `{'question_id','C','qC','gold','hetero'}` via `p.write_bytes(pickle.dumps(...))` (lines 111, 119, 231).
- T4C2's script likewise uses a local `cachedir`: `caches=sorted(args.cachedir.glob('*.pkl'))` / `cp=args.cachedir/f'{r.question_id}.pkl'` (v52_t4c2_centering_geometry.py lines 352, 516).
- The project's own independent audit (Drive docs created today: `INDEPENDENT_INVENTORY_AUDIT_REPORT` id `1iuVHrKPcESamPS1qsz1JCH_qeRH36eRYxZf6krAsBaY`, `AUDIT_RECEIPT` id `118B7DAaUfHpKcZE1H8pyAd0FToZTRjchyyiAHRIO0dU`) states: *"No real archive-fitted TF-IDF vocabulary/IDF, source SVD, mixed96 SVD, mu96, ITQ96 rotation, PQ/OPQ codebook, or RaBitQ state package was located. Status remains SEARCHED / NOT LOCATED / UNKNOWN, never ABSENT."*

**Verdict F1: the literal `cache_repr/*.pkl` pickles and equivalent float-cache serializations are NOT on Drive.**

### F2 — FOUND: sign-packed per-question representation codes for all 470 LongMemEval questions (`V52_T4C2_BINARY_GEOMETRY.zip`)

- Drive object: id **`1ggaSk2TyhVVNil7UOk2Dai2UDcgIZY9r`**, 13,012,706 B, `application/zip`, at `LLM_TOKEN_ZIP_RESEARCH_MASTER/V52_TASK_4C2_CENTERING_GEOMETRY/FINAL_2026-08-27_FULL_470`. It is additionally nested (same bytes) inside `V52_T4C2_ALL_OUTPUTS.zip` (id `1axb1ZQpo7bdN92blVl3eHWe3nME1mwlR` in the same folder; id `1XkcdVYZTOzDXxq1RMDbnVT46_biGBGxa` in `V52_TASK_4C2_AUDIT_PACKAGE`).
- Contents: **471 entries = 470 × `codes/<question_id>.npz` + `MANIFEST.json`**. Every LongMemEval question ID carries one NPZ. Sample (`codes/001be529.npz`) exact key dump:

```
sign_doc_packed:    shape=(514, 12)      dtype=uint8     # sign bits of C (archive rows), 96 bits -> 12 bytes
sign_query_packed:  shape=(12,)          dtype=uint8     # sign bits of qC (query vector)
itq_doc_packed:     shape=(5, 514, 12)   dtype=uint8     # ITQ-rotated codes, 5 seeds
itq_query_packed:   shape=(5, 12)        dtype=uint8
itq_seeds:          shape=(5,)           dtype=int32     # [101, 202, 303, 404, 505]
gold_rows:          shape=(1,)           dtype=int32
N_archive:          shape=(1,)           dtype=int32
bitorder:           shape=(1,)           dtype=<U3       # 'big'
```

- `MANIFEST.json` records `task: "V52 Task 4C2 — Centering / Sign-Geometry Diagnostic"`, `itq_seeds`, `bitorder: "big"`, and per-question `sha256` + `N_archive` (e.g. `001be529: sha256 9f2133…, N_archive 514`).
- The project's own audit classifies this bundle as *"a nested binary diagnostic ZIP with 470 NPZ files … packed document/query codes, ITQ seeds, gold_rows, N and bitorder; they are not serialized fitted representation state and are FOUND_BUT_EXCLUDED_DIAGNOSTIC_ARTIFACT."*
- **Interpretation for the Task1 question:** this is the **sign-binarized form of the C matrices and qC vectors** (the float-valued C/qC themselves are not stored here), for 470/470 questions, with gold rows and archive sizes. It is the only surviving *per-question matrix payload* for LongMemEval found on Drive.

### F3 — FOUND: per-coordinate sufficient statistics for all 470 questions (`V52_T4C3_*heterogeneity*.csv`)

- `V52_T4C3_native_heterogeneity.csv` — id **`1PME-hZHxp3fRN0AYgygp1oM7v-GNYm6Z`**, 1,947,381 B, at `…/V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE/FINAL_2026-08-28_FULL_470` (also inside `V52_T4C3_ALL_OUTPUTS.zip`, id `1KoDZx0h88JMUfJsAgd_rUtAyeS5_3ESm`).
  - 470 data rows (one per LongMemEval question) × 13 columns: `question_id` + 9 aggregate heterogeneity stats + **`variance_vector` (96 semicolon-separated floats)** + **`occupancy_vector` (96 semicolon-separated floats)**. Exact check: `variance_vector entries: 96`, `occupancy_vector entries: 96`.
- `V52_T4C3_rotated_heterogeneity.csv` — id **`1sMbkfQvdH2yX3uKREb-gM37nIYh_83ko`**, 78,405,429 B — 18,800 rows (`question_id × family(6 rotation/control families) × seed`) with the same `variance_vector`/`occupancy_vector` columns (16 cols).
- Also in the tree: `V52_T4C3_heterogeneity_alignment.csv` (1,620 B, aggregates), `V52_T4C3_heterogeneity_quintiles.csv` (16,478 B, quintile binnings + `variance_cv`), `V52_T4C3_question_level.csv` (22 cols incl. `variance_cv`, `gold_stratum`, `N_archive`).
- **Cross-validation:** the 470 question IDs in these CSVs and the 470 NPZ basenames are **set-equal** (`ids match csv set: True`; 470 unique each, zero missing on either side). This is the same 470-question cohort.
- These vectors are exactly the "sufficient statistics (per-coordinate variance/occupancy/correlation data)" family named in the task: `variance_vector` = per-coordinate variance of C; `occupancy_vector` = per-coordinate sign occupancy; plus aggregate correlation structure (`cov_offdiag_frobenius_energy_ratio`, `mean_abs_coordinate_correlation`). Note the *full 96×96 covariance matrix is not stored* — only its Frobenius off-diagonal energy ratio and mean |corr| aggregate, plus the per-coordinate variance vectors.

### F4 — LoCoMo (T4D): NO equivalent payload — only aggregate CSVs

`V52_T4D_ALL_OUTPUTS.zip` (id `1jBgSS4A239X-5aVmYiAqvk96VP82ZYK5`, 1,451,357 B) has 26 entries, all CSV/JSON/TXT/MD/PY. Column audit of all 20 member CSVs found **no vector columns** (closest: `bit_occupancy_mean/min/max` scalars in collision_diagnostics). `V52_T4D_question_level.csv` = 1,540 rows × 29 scalar columns. No NPZ/pkl in or near the LoCoMo pipeline. The 2026-09-04 LoCoMo/LongMemEval causal+null+boundary zips (9 more bundles, all inspected) contain only scalar CSVs/JSON; their `*_per_question.csv.gz` are scalar (`fractional_R3`, `native_fractional_R3`, …). The only per-coordinate-style artifacts for LoCoMo on Drive are `audit_layer/conv_*.json` (audit notes) and the per-conversation fit *procedure proofs* (`V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt`, 4,416 B, with N per conversation locomo_0…9 = 419…568), not data.

### F5 — Other NPZ/pkl on Drive belong to other programs (excluded with evidence)

- `PHASE_C0V9_MEASUREMENT_SENSITIVITY_FINAL_CHECKPOINT_2026-08-22.zip` (id `1aFbDmVs65ZA6A-9LzcJskTNzKxJwvxKk`, 4,068,720 B, **at My Drive root**) holds 48 control NPZ from a `C0V8Q` simulation (`times`, `active`, `position(127,32,3)`, `bonds(127,496)`) — this is PROJECT_AUTOGENESIS physics/simulation control data ("partner-structure discovery panel"), definitively not LongMemEval/LoCoMo representations.
- The 4 `*.pkl`/`*.pkl.gz` and all `.npy/.npz` name hits are vendored NumPy/Matplotlib files under `autogenesis-meta/.venv/…` (provenance resolved by ancestor walk).
- `PHASE_B3_FROZEN_RUN_MATRIX.csv` (3.9 MB) etc. → `PROJECT_AUTOGENESIS/02_PHASES/…`; `C909A_THEOREM_TRANSFER_MATRIX.csv` → `Riemann Hipotezi — Araştırma Arşivi/02_COMPUTATION`; `CP20_TASK2_SHELL_MATRIX_TABLE.csv` → Collatz archive; `THREE_ENGINE_CONTRACT_MATRIX.csv` → AUTOGENESIS `ENGINE_RETENTION_SUPPORT_EQUIVALENCE_VERIFY_001`. None are llmzip artifacts.

### F6 — Corpus is present on Drive (context for regeneration)

- `longmemeval_s_cleaned.json` (277,383,467 B, id `1npoK4DuxR-Gz2zXMVwKpIsfkssZFnghI`) and `longmemeval_s_cleaned.rar` (53,574,473 B, id `14nY-deHuK5wBPzQfJFyZB_Z-7X35Ywky`) sit at MASTER root.
- `locomo10.json` (2.8 MB) exists on Drive **only inside** `V52_T1_COMPUTE_INPUT_BUNDLE.zip` (`RECOVERED_FROM_FILE_LIBRARY/01_V51_T1_RECOVERED`); there is no standalone `locomo10`-named Drive file (`name contains 'locomo10'` → 0).
- The frozen representation **procedure** (TF-IDF params, SVD random_states 5101/5204, centering, query-transform rules) is fully specified in `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt` (+ T4E0/T4F0 equivalents). So the float matrices are *regenerable in principle* from corpus + procedure, but (a) the audit classifies regeneration as not verified, and (b) none of the fitted bytes themselves are on Drive.

---

## 3. CANDIDATES — every file whose name/type suggests representation data

### 3A. FOUND — representation-equivalent payloads (the answer to the core question)

| File | ID | Location (canonical) | Size | What it contains |
|---|---|---|---|---|
| `V52_T4C2_BINARY_GEOMETRY.zip` | `1ggaSk2TyhVVNil7UOk2Dai2UDcgIZY9r` | MASTER/V52_TASK_4C2_CENTERING_GEOMETRY/FINAL_2026-08-27_FULL_470 | 13.0 MB | **470/470 NPZ**: packed sign codes of C (`sign_doc_packed` N×12) and qC (`sign_query_packed` 12), 5-seed ITQ variants, `gold_rows`, `N_archive`, `bitorder`; MANIFEST with sha256s. (Also nested inside both copies of `V52_T4C2_ALL_OUTPUTS.zip`.) |
| `V52_T4C3_native_heterogeneity.csv` | `1PME-hZHxp3fRN0AYgygp1oM7v-GNYm6Z` | MASTER/…/FINAL_2026-08-28_FULL_470 | 1.9 MB | **470 rows**; `variance_vector` (96) + `occupancy_vector` (96) + 9 correlation/heterogeneity aggregates per question. |
| `V52_T4C3_rotated_heterogeneity.csv` | `1sMbkfQvdH2yX3uKREb-gM37nIYh_83ko` | same folder | 78.4 MB | 18,800 rows of the same 96-dim vectors across rotation families/seeds (incl. SIGNED_PERM_CONTROL96 controls, seed, block_size). |
| `V52_T4C3_ALL_OUTPUTS.zip` | `1KoDZx0h88JMUfJsAgd_rUtAyeS5_3ESm` | same folder | 24.8 MB | Container holding the two CSVs above + the T4C3 script; **no pkl inside** (27 entries, verified). |

### 3B. Term-matched files inside the project tree (classified; no matrix payload)

| File | Verdict |
|---|---|
| `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt/.csv` (id `11cKt4hDPBazhrOSZxSgcT5Dw-w5kdpNi` / …) | PROCEDURE ONLY — hashes + per-conversation fit parameters; no bytes. |
| `V52_T4E0_REPRESENTATION_TRANSFER_PROOF.md/.csv` ×2 copies, `V52_T4F0_REPRESENTATION_TRANSFER_PROOF.md` | PROCEDURE ONLY (estimand/adapter freeze proofs). |
| `V52_T4C3_heterogeneity_alignment.csv`, `…_quintiles.csv`, `V52_T4C2/T4C3/T4D_gold_cardinality.csv`, `V52_T2_gold_capture_decomposition.csv`, `05_V52_T2_GOLD_CAPTURE_DECOMPOSITION_CSV`, `V52_T4D_strata_gold_cardinality.csv`, `V52_T4D_ARCHIVE_SIZE_QUARTILES_FROZEN.csv` | AGGREGATES ONLY (gold counts, bins). |
| `v52_t4c3_coordinate_axis_probe.py`, `v52_t4d_locomo_frozen_cross_benchmark.py`, `v52_t4c2_centering_geometry.py` (in zips), `v52_t4e0_*`, `v52_t4f0_*` | CODE — defines `work/cache_repr`, `work/cache_results`, `cachedir/*.pkl` (local only). |
| `V52_TASK_4D_LOCOMO_FROZEN_CROSS_BENCHMARK_REPLICATION_2026-08-29` (file + folder-name matches on term "frozen") | metadata only. |
| All other `frozen`/`stat`/`C9` name matches in the tree (e.g. `V52_*_PRE_RUN_SEAL.json`, strata CSVs) | metadata/aggregates only. |

### 3C. Term-matched files outside the project tree (291 unique; grouped, all excluded with reason)

| Group | Count | Classification / evidence |
|---|---|---|
| Vendored Python env (`autogenesis-meta/.venv` — numpy, numba, matplotlib; dated 2026-08-20) | ~130 (incl. the 4 `*.pkl`, 5 `*.npz`, ~40 `*.npy`-named files; e.g. `astype_copy.pkl`, `bivariate_normal.npy`, `topobathy.npz`, `cache.py`, `repr.py`, `statisticsPen.py`) | NOT PROJECT DATA. Ancestry resolved: `autogenesis-meta/.venv/Lib/site-packages/…`. |
| `C90x–C91x` (`C907_*`…`C910_*`, incl. `C909A_THEOREM_TRANSFER_MATRIX.csv`) | 87 | Other program — `Riemann Hipotezi — Araştırma Arşivi/02_COMPUTATION` (ancestry verified) and sibling archive folders. Number-theory/theorem-transfer matrices, not embeddings. |
| `PROJECT_AUTOGENESIS` B-phase (`PHASE_B2B_PERTURBATION_MATRIX.csv`, `PHASE_B3_FROZEN_RUN_MATRIX.csv/.DRAFT`, `PHASE_B3_RUN_MATRIX_VALIDATION_DRAFT.json`), C0V9 family, `THREE_ENGINE_*`, `REPRODUCE_*` | ~40 | Other program — `PROJECT_AUTOGENESIS/02_PHASES/…` and `CURRENT_RESEARCH_2026_08_25/…` (ancestry verified). `PHASE_B3_FROZEN_RUN_MATRIX.csv` (3.9 MB, 2026-08-16) = run-configuration matrix from the B3 phase, not representations. |
| `C0V9` family (`C0V9_POSITIVE_CONTROL_FAILURE_VERIFY_*`, `C0V9_SAMPLE_REPLAY_DETAIL.csv`, `PHASE_C0V9_MEASUREMENT_SENSITIVITY_FINAL_CHECKPOINT_2026-08-22.zip` w/ 48 control NPZ) | 18 | Other program — AUTOGENESIS measurement calibration (simulation target trajectories; keys `times/active/position/bonds` verified). Canonical zip id `1aFbDmVs65ZA6A-9LzcJskTNzKxJwvxKk`; pre-interaction zip `1_lF9qwH8ShVUGqPgIdvBWV3xatLCyJA1`. |
| `CP19`/`CP20` docs and matrices (`CP20_TASK2_SHELL_MATRIX_TABLE.csv`, `CP20_TASK2_SHELL_TRANSFER_MATRIX.md`, `CP19_TASK10_MATRIX_COCYCLE.md`, Task 1–8 frozen protocol docs) | ~30 | Other program — Collatz archive (`Collatz Problemi — Araştırma Arşivi/CP20/…`, ancestry verified). |
| `cache_repr` / `C96` / `mixed96` / `sufficient` / `queries` / `tensor` | **0** | Zero name hits anywhere on Drive. |

### 3D. Container inventory — all project zips verified cache-free

All 20 unique zip names in the tree were member-listed and scanned for array extensions. Array-format members exist **only** in `V52_T4C2_BINARY_GEOMETRY.zip` (470 NPZ, = 3A) and nowhere else. `V52_T4D_ALL_OUTPUTS.zip`, `V52_T4E0/T4F0_ALL_OUTPUTS.zip`, `V52_T1_COMPUTE_INPUT_BUNDLE.zip` (inputs: locomo10.json + audit jsons + V51 reference CSVs), `LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip` (198 entries, V6–V48 experiment CSVs, old V-series), `EXTERNAL_LLM_HANDOFF_BUNDLE.zip` (+ nested `V51_CORE_AUDIT_PACKAGE.zip` — `v51_question_level_results.csv` 5.5 MB scalars), `locomo-audit-main.zip` (evaluation JSONs, `answer_key.json`), the 9× 2026-09-04 causal/boundary/null zips, and the 2× small 4E0 variants contain **no representation arrays**.

---

## 4. Conclusion

## **PARTIAL**

Precise meaning of the verdict:

1. **The literal frozen caches — `cache_repr/*.pkl` (keys `question_id, C, qC, gold, hetero`) and the float-valued C/qC matrices — are NOT FOUND on Drive.** Account-wide name sweeps (`pkl, cache_repr, cache_results, npy, npz, C96, mixed96, …`), full enumeration of the project tree, trash, and content scans of every project zip found no such serialization. This matches the project's own audit status: *SEARCHED / NOT LOCATED / UNKNOWN* — with one decisive nuance: **the sign-information of every one of the 470 C matrices and query vectors survives on Drive** (F2), and per-coordinate sufficient statistics survive for all 470 questions (F3). So "not found" applies to the *float* matrices only.

2. **LongMemEval sufficient statistics: FOUND (470/470), with IDs cross-validated.** Per-coordinate `variance_vector` and `occupancy_vector` (96-dim), plus correlation aggregates — from `V52_T4C3_native_heterogeneity.csv` (also `rotated_heterogeneity.csv`, 18,800 rows), and the packed sign codes of C/qC + `gold_rows` + `N_archive` from the 470 NPZ in `V52_T4C2_BINARY_GEOMETRY.zip`. Extraction paths are listed in §3A; the CSV rows (all six binaries/CSVs appear there) give the Drive IDs.

3. **LoCoMo: NOT FOUND.** No per-coordinate vectors, no codes bundle, no pickles — only aggregate scalar CSVs (T4D question_level 1,540 rows; boundary/null/causal zips 2026-09-04) and procedure proofs. If LoCoMo per-coordinate data is required, Drive does not currently hold it; only the procedure + corpus (via V52_T1 bundle) could support regeneration.

4. Caveats: (a) the sign codes are lossy — they cannot reconstruct float C/qC; (b) variance vectors alone do not reconstruct the full covariance (only aggregate |corr|/Frobenius ratios are stored); (c) files could in principle hide in un-walked deep subtrees of the other research programs, but 45 name-sweep queries covering every required term returned nothing beyond what is classified above; (d) revision history was not searched (a deleted-and-replaced Drive file could have held caches — not checkable with the current read scopes).

### Suggested immediate next step (read-only, local)
Copy/retain from `C:/Users/MDP/dev/llmzip-work/drive/`: `V52_T4C2_BINARY_GEOMETRY.zip` (470 NPZ + MANIFEST), `V52_T4C3_native_heterogeneity.csv`, `V52_T4C3_rotated_heterogeneity.csv` — these constitute the complete set of rediscovered representation payload for LongMemEval.

---

## 5. Artifacts produced

| Path | Content |
|---|---|
| `C:/Users/MDP/dev/llmzip-work/reports/drive_inventory.csv` | 296 lines (header + 295 data rows); columns `folder_path,name,id,mimeType,size,modifiedTime`; covers 237 project-tree rows (216 files + 21 subfolder rows; the master folder itself is listed under `(My Drive root)`) + 22 My Drive top-level rows + 7 trash rows + 29 classified outside rows (21 PROJECT_AUTOGENESIS/C0V9, 2 Riemann/Collatz, 4 vendored env, 2 shared-with-me). |
| `C:/Users/MDP/dev/llmzip-work/reports/drive_inventory.md` | This report. |
| `C:/Users/MDP/dev/llmzip-work/scratch/drive_enum_raw.json`, `drive_search_raw.json`, `drive_phase3_raw.json`, `drive_phase4_raw.json`, `drive_phase5_raw.json` | Raw API replies (enumeration, sweep, ancestry, drive roots, final searches) for re-verification. |
| `C:/Users/MDP/dev/llmzip-work/drive/` | 23 downloaded files (~41 MB) incl. all inspected bundles. |
