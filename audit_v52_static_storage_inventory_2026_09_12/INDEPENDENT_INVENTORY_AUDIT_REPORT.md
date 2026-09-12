# V52 Static Storage Inventory — Independent Zero-Trust Audit

Date: 2026-09-12
Verdict: **REQUEST_CHANGES**
Audit branch: `audit/v52-static-storage-inventory-independent-2026-09-12`
Object under audit: `codex/v52-static-storage-contract-2026-09-12` @ `f9404f2b1e56e5a63878978c19f30283b18324fd`
Parent contract commit: `d29c7b1d668f8abf47889e132e084c4abd72615b`
Live canonical `refs/heads/main` observed at audit start: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`

## 1. Executive verdict

The parent inventory is materially conservative on the core scientific risk: it does **not** claim that fitted model/projector bytes were found, does **not** turn UNKNOWN state into zero bytes, and keeps effective persistent cost NOT_READY. LongMemEval and LoCoMo archive-size provenance and the representation procedure are substantially supported. However the inventory is not yet acceptable as the final source-resolution handoff because one provenance status is factually stale and several required state-classification dimensions are missing. Under the requested verdict rules this is **REQUEST_CHANGES**, not PASS_WITH_FINDINGS.

No result here proves `<=12` marginal persistent bytes/vector, storage measurement completeness, retrieval readiness, or scientific approval.

## 2. Exact refs verified

- Object-under-audit branch head: `f9404f2b1e56e5a63878978c19f30283b18324fd`.
- Parent contract package commit: `d29c7b1d668f8abf47889e132e084c4abd72615b`.
- Parent -> target comparison: merge base exactly `d29c7b1d668f8abf47889e132e084c4abd72615b`, target ahead by 3 commits, changes limited to the inventory namespace (`INVENTORY_IDENTITY.json`, `SOURCE_INVENTORY.json`, `SOURCE_INVENTORY_TR.md`). No contract, main, ledger, or sealed namespace mutation was observed in this delta.
- Live canonical `refs/heads/main` at audit start: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`.
- Audit branch is created from exact target; final audit commit is intentionally resolved externally after this report is committed, because a Git commit cannot contain its own hash without changing that hash.

## 3. Scope / forbidden access confirmation

Task4F1 remained SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. No Task4F1 corpus, query, gold, outcome, scoring, HMAC, seal, finalize, pilot, or production action was opened or run. No raw benchmark corpus was refit. T4C2/T4C3/T4D files were inspected only for artifact identity, provenance, schema, and physical-state evidence. Diagnostic query/gold fields encountered inside a historical T4C2 NPZ were not interpreted for retrieval quality.

## 4. Parent inventory claims checked

Supported: three distinct cost objects; <=12 applies to marginal persistent bytes/vector; per-vector norm/scale/correction/ID/offset/metadata/lookup state belongs inside the cap when physically required; shared state is separately reported; UNKNOWN is not zero; archive-local fitting does not prove one physical copy per archive.

Correction required: LoCoMo proof hash is not unbound; it is bound by the T4D post-run manifest and manifest upload receipt. Required regeneration and mapping classification dimensions are also incomplete.

Contract integrity note: `FILE_HASHES.json` raw digest was independently recomputed as `5a68093c4251343a0e485092d6ffbc064bf79ff3619fc0aabc545318cbe2a054`. The recorded hashes for `MEASUREMENT_CONTRACT_TR.md`, `measurement_plan_guard.py`, and `INDEPENDENT_FIVE_FINDINGS_REVIEW.md` are present in that manifest and the parent->target additive-only Git comparison shows those contract blobs were not changed by the inventory commits. Because the GitHub connector did not expose those three raw files as runtime-mounted bytes, this audit does **not** falsely label their SHA256 values as independently recomputed. This is an audit limitation, not evidence of a mismatch.

## 5. LongMemEval N_i provenance

Verified source: `docs/v52/task4c2/V52_T4C2_feature_geometry.csv`. Header contains `question_id,N_archive,...`. The file has 470 data rows (plus header); observed N values vary (e.g. 514, 486, 487, ...), so a universal 493 denominator is invalid. Archive identity is `question_id` and candidate denominator is row-local `N_archive`.

`docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json` binds `V52_T4C2_feature_geometry.csv` to SHA256 `d4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32`. No retrieval outcome was inferred from this table.

## 6. LoCoMo N_i provenance

Canonical Drive root was verified as `LLM_TOKEN_ZIP_RESEARCH_MASTER` id `1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv`. Source file `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt` id `11cKt4hDPBazhrOSZxSgcT5Dw-w5kdpNi` was downloaded as raw bytes.

Raw proof SHA256: `957e9e022f6f42ebf3e4f68eaa69cf1ec1f48367100a959a0ba9623caf5e1ddd`, 4416 bytes. The proof gives: locomo_0=419, locomo_1=369, locomo_2=663, locomo_3=629, locomo_4=680, locomo_5=675, locomo_6=689, locomo_7=681, locomo_8=509, locomo_9=568.

Contrary to the parent inventory's `HASH_NOT_BOUND_HERE`/unknown wording, `V52_T4D_POST_RUN_MANIFEST.json` binds the exact proof digest under `atomic_output_hashes`. The manifest raw SHA256 is `a97e411c1ed24c5c93590638fcb51248936d8428a38e4d76cf0c6b74a9399b9c`, and `V52_T4D_UPLOAD_RECEIPT.txt` records that exact manifest digest. This is a complete artifact->manifest->receipt chain for the proof file. It is **not** proof that fitted model bytes were persisted.

## 7. Frozen representation procedure

Git source verifies V1 `fit_archive_representation` uses word TF-IDF with lowercase, `(1,2)` n-grams, English stop words and sublinear TF; char TF-IDF uses `char_wb`, `(3,5)` and sublinear TF. `use_idf` is not disabled, so sklearn default IDF is active. Both sparse blocks are normalized. Source latent SVD uses `TruncatedSVD` with up to 32 components and `random_state=5101`, followed by normalization.

V2 explicitly aliases `fit_input_payload`, `fit_archive_representation`, and `encode_sanity` to V1, so the fit procedure is inherited rather than reimplemented.

T4D proof independently records mixed96 construction as concatenate `[latent, word, char]` -> archive-only `TruncatedSVD(96, random_state=5204)` -> L2 normalize; `mu96` is computed from archive documents and queries are transformed only after archive-side fitted objects exist. This establishes **PROCEDURE FOUND**, not **FITTED BYTES FOUND**.

## 8. Fitted-state artifact search

Searched Git: canonical target tree, `research/v52-sign-mechanism-locomo-2026-09-04`, and identified twelve-byte branches/namespaces. Searched Drive: T4C2 final, T4C3 final, T4D final plus provenance/receipt material. Terms/extensions included pkl/pickle/joblib/npz/npy/faiss/index/bin/model/pt/pth/vectorizer/vocabulary/vocab/idf/svd/components/projector/projection/mu96/center/centering/rotation/itq/haar/pq/opq/rabitq/centroid/codebook/serializer/serialization/archive_model/model_state/manifest/hash/receipt.

No real archive-fitted TF-IDF vocabulary/IDF, source SVD components, mixed96 SVD components, mu96 vector, ITQ96 rotation, PQ/OPQ codebook, or RaBitQ real-archive state package was located. Correct status remains **SEARCHED / NOT LOCATED / UNKNOWN**, never ABSENT.

T4C2 contains a nested binary diagnostic ZIP with 470 NPZ files. These contain packed document/query codes, ITQ seed metadata, `gold_rows`, N and bitorder; they are not serialized fitted representation state and include fields outside the static-package boundary. They are therefore FOUND_BUT_EXCLUDED_DIAGNOSTIC_ARTIFACT, not a substitute for a model package. T4C3 and T4D output ZIPs contained CSV/JSON/report/script artifacts and no comparable serialized fitted-state files.

## 9. Deterministic regeneration analysis

- word TF-IDF vocabulary/IDF: **UNKNOWN**; cannot be reconstructed from seed alone without archive content/refit.
- char TF-IDF vocabulary/IDF: **UNKNOWN** for the same reason.
- source latent SVD: **UNKNOWN**; `random_state=5101` does not recover fitted components without fit data.
- mixed96 SVD: **UNKNOWN**; `random_state=5204` is insufficient without fitted input.
- mu96: **UNKNOWN**; archive-dependent mean.
- ITQ96 rotation: **UNKNOWN**; seed initializes the procedure but fitted rotation depends on archive representation.
- SIMHASH/Haar/random projection: **REGENERATION_CANDIDATE_NOT_VERIFIED**. Seeded NumPy RNG logic exists, but exact implementation/version/dtype/order and archive-dependent dimensions are not bound as a reopening contract.
- PQ/OPQ/RaBitQ real archive state: **UNKNOWN**; no qualifying real-archive persisted state located.

No fitted/shared item is upgraded to DETERMINISTIC_REGENERATION_VERIFIED in this audit.

## 10. ID/offset/payload mapping analysis

Logical ID existence is verified: adapters build deterministic `memory_id` values. Package storage of those IDs is **UNKNOWN**. A zero-byte implicit ordinal mapping is **not verified**. The mapping may depend on external archive order/payload state; the physical package boundary is not yet declared. Therefore persistent ID/offset/lookup bytes remain UNKNOWN and cannot be set to 0.

Required correction: represent separately `logical_id_exists`, `package_stores_id`, `implicit_mapping_reproducible`, `external_boundary_dependency`, and `mapping_status`.

## 11. Physical copy / sharing population analysis

Archive-local fitting is verified as a procedure; persistent serialization scope is not. No fitted-state files were located from which a physical duplicate count could be established. Consequently `physical_copy_count=UNKNOWN` remains correct. `N_i` is a defensible candidate denominator only if a future package proves one archive-local copy is actually shared by exactly that archive's stored vectors. Effective cost therefore remains NOT_READY.

Identical hashes must not be treated as one global physical copy absent storage-layout proof.

## 12. Method-specific state findings

- ITQ96 rotation: real fitted rotation bytes UNKNOWN.
- SIMHASH/Haar: seeded generation procedure exists; deterministic regeneration contract not verified.
- PQ96: synthetic/library serializer evidence is not a real archive-fitted codebook. REAL_ARCHIVE_ARTIFACT_UNKNOWN.
- OPQ_PQ96: real OPQ rotation + PQ codebook not located. REAL_ARCHIVE_ARTIFACT_UNKNOWN.
- RaBitQ32: real archive state not located. REAL_ARCHIVE_ARTIFACT_UNKNOWN.

No method-specific state is assigned zero bytes.

## 13. Inventory JSON/MD consistency

`SOURCE_INVENTORY_TR.md` and `SOURCE_INVENTORY.json` are materially aligned on archive rosters, N_i sources, UNKNOWN fitted-state status, physical-copy uncertainty, NOT_READY effective cost, and forbidden shortcuts. No material MD-vs-JSON contradiction was found. The defects in this report apply to both representations: LoCoMo provenance is understated, and regeneration/mapping classifications are not explicit enough.

## 14. Findings table

| ID | Sev | Result | Required correction | Blocks next stage |
|---|---|---|---|---|
| INV-AUD-001 | P2 | LoCoMo proof digest is actually manifest-bound | upgrade provenance chain | yes |
| INV-AUD-002 | P2 | required per-item regeneration statuses missing | add C5 status/evidence fields | yes |
| INV-AUD-003 | P2 | T4C2 nested NPZ diagnostic artifacts not explicitly catalogued | list as found-but-excluded | no |
| INV-AUD-004 | P2 | ID/offset mapping taxonomy incomplete | add five-way mapping fields; retain UNKNOWN bytes | yes |
| INV-AUD-005 | P3 | parent search log not sufficiently reproducible | expand term/namespace/container search log | no |

Machine-readable details are in `FINDINGS.json`.

## 15. What remains UNKNOWN

Physical fitted TF-IDF state; source and mixed96 SVD matrices; mu96 bytes; archive-specific ITQ rotations; real archive PQ/OPQ/RaBitQ state; persistent ID/offset lookup representation; physical serialization scope; duplicate count; actual sharing populations; total shared bytes; effective persistent bytes/vector; and <=12 budget compliance.

## 16. What is safe to do next

Only repair and re-bind the source inventory: correct the LoCoMo provenance chain, add deterministic-regeneration statuses, explicitly classify the T4C2 diagnostic NPZ bundle, and add the five-way ID/offset mapping fields. After that, run a new independent source-resolution audit. Do **not** proceed to storage measurement from the current inventory.

## 17. What is still forbidden

Task4F1 outcome access; retrieval scoring; real corpus reconstruction/refit; candidate retrieval comparisons; codebook fitting on raw corpus; HMAC/seal/finalize; pilot/run/production authorization; post-hoc N/q or serialization-panel selection.

## 18. GitHub write receipt

Audit branch: `audit/v52-static-storage-inventory-independent-2026-09-12`. Base is exact target `f9404f2b1e56e5a63878978c19f30283b18324fd`. Namespace: `audit_v52_static_storage_inventory_2026_09_12/`. This package changes no target, main, ledger, sealed, or parent inventory file. Final branch-head SHA is intentionally recorded externally after commit creation (Drive `AUDIT_RECEIPT` and final chat), avoiding impossible self-referential commit hashing.

## 19. Drive write receipt

Folder: https://drive.google.com/drive/folders/1egDZALfbObWd5oum9oi9hfXUGdM56jta
Report Doc: https://docs.google.com/document/d/1iuVHrKPcESamPS1qsz1JCH_qeRH36eRYxZf6krAsBaY/edit?usp=drivesdk
Audit receipt Doc: https://docs.google.com/document/d/118B7DAaUfHpKcZE1H8pyAd0FToZTRjchyyiAHRIO0dU/edit?usp=drivesdk

The Drive documents are a readable mirror/receipt, not assumed byte-identical to Git Markdown/JSON. Git package SHA256 values are authoritative for the audit package bytes.
