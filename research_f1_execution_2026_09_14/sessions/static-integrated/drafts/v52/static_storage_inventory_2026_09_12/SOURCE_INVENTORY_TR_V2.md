# V52 statik depolama — mevcut kaynak envanteri, bağımsız denetim sonrası revizyon

**Durum: DRAFT / PARTIAL / NOT_READY / NO MEASUREMENT / NO EXECUTION AUTHORIZATION.**

Bu belge `drafts/v52/static_storage_contract_2026_09_12/` altındaki bağımsız-incelenmiş ölçüm sözleşmesini değiştirmez. Yalnız mevcut Git/Drive kaynak envanterini düzeltir. Gerçek retrieval, query/gold/outcome erişimi, korpus yeniden işleme, model yeniden fit etme, maliyet ölçümü, seal/finalize/HMAC veya Task4F1 çalıştırması yapılmamıştır.

Bağımsız audit: `audit/v52-static-storage-inventory-independent-2026-09-12` @ `22b58b609f766c028a344813eacec4abab0a7804`, verdict **REQUEST_CHANGES**. Audit paketi `audit_v52_static_storage_inventory_2026_09_12/`; `HASHES.json` sidecar SHA256 `a1ae82bb7114409aaf9fc58bb234f2ac93fa5934bbdfce47c86a57d07bf3579a`.

## 1. Denetim dispozisyonu

| Finding | Dispozisyon | Düzeltme |
|---|---|---|
| INV-AUD-001 P2 | **ACCEPTED_AND_CORRECTED** | LoCoMo proof manifest-bound provenance olarak bağlandı |
| INV-AUD-002 P2 | **ACCEPTED_AND_CORRECTED** | Her fitted/shared kaleme deterministic regeneration statüsü ve kanıt/bloker eklendi |
| INV-AUD-003 P2 | **ACCEPTED_AND_CORRECTED** | T4C2 nested NPZ bundle `FOUND_BUT_EXCLUDED_DIAGNOSTIC_ARTIFACT` olarak kataloglandı |
| INV-AUD-004 P2 | **ACCEPTED_AND_CORRECTED** | ID/offset mapping beş yönlü sınıflandırması eklendi; bytes `UNKNOWN` kaldı |
| INV-AUD-005 P3 | **ACCEPTED_AND_CORRECTED** | Ayrı `SEARCH_LOG_V2.json` tam terim/namespace/container kayıtlarıyla eklendi |

Bu düzeltmeler inventory’yi **READY yapmaz**. Yeni bir bağımsız source-resolution review gerekir.

## 2. Bağlayıcı muhasebe sınırı

Bağlayıcı karar nesnesi **marjinal kalıcı B/vektör ≤ 12** sınırıdır. Kodla birlikte gerçekten her vektör için saklanan zorunlu norm, scale, correction, kimlik, offset ve metadata bu tavana girer. Paylaşılan model/projektör durumu ayrı ölçülür ve gerçek paylaşım nüfusuna göre etkin B/vektör olarak ayrıca raporlanır. Bu envanter henüz herhangi bir kalemin bayt maliyetini ölçmez.

Kaynak yetkisi: `drafts/v52/static_storage_contract_2026_09_12/source/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`, kaynak commit `89d3169adb65a9a2ab7f289997d7c49eb8ccf25c`. Kaynağın kendi authority statüsü yükseltilmez.

## 3. Arşiv kimliği ve gerçek N_i

### LongMemEval

- Kaynak: `docs/v52/task4c2/V52_T4C2_feature_geometry.csv`.
- 470 birincil question/archive için `question_id,N_archive,...` satırları taşır.
- Tek bir 493 sabiti kullanılmaz.
- `V52_T4C2_POST_RUN_MANIFEST.json`, feature geometry’yi SHA256 `d4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32` ile bağlar.
- Durum: **FOUND_MANIFEST_BOUND_ROSTER_SOURCE**.

### LoCoMo — INV-AUD-001 düzeltmesi

Kaynak: Drive `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt`, file id `11cKt4hDPBazhrOSZxSgcT5Dw-w5kdpNi`.

Raw SHA256: `957e9e022f6f42ebf3e4f68eaa69cf1ec1f48367100a959a0ba9623caf5e1ddd`.

Bu digest `V52_T4D_POST_RUN_MANIFEST.json` (Drive id `1Lk5ZLaceKuc3OF-v0X52OfItU0PqVlmp`) tarafından bağlanır. Manifest raw SHA256: `a97e411c1ed24c5c93590638fcb51248936d8428a38e4d76cf0c6b74a9399b9c`.

`V52_T4D_UPLOAD_RECEIPT.txt` (Drive id `1BJgsMU37aw5yFnZ2g76kuNYMJkfR6HIP`) aynı manifest digest’ini external receipt olarak kaydeder.

Bu turda manifest raw byte SHA256’sı tekrar hesaplandı ve `a97e...` ile eşleşti; manifest içindeki representation-proof hash’i `957e...` olarak doğrulandı. Bu zincir **proof provenance** kanıtıdır; fitted model/projector state’in fiziksel persistence kanıtı değildir.

Archive-fit nüfusları: `locomo_0=419, 1=369, 2=663, 3=629, 4=680, 5=675, 6=689, 7=681, 8=509, 9=568`.

Durum: **FOUND_MANIFEST_BOUND_ROSTER_SOURCE**.

## 4. Dondurulmuş temsil prosedürü

Git adapter ailesi word TF-IDF, char TF-IDF, latent SVD ve normalization prosedürünü bağlar; V2 fit fonksiyonlarını V1’den alias eder. T4D representation proof `[latent, word, char] -> archive-only TruncatedSVD(96, random_state=5204) -> L2 normalize`, archive document mean `mu96` ve aynı fitted state ile query transform prosedürünü kaydeder.

**PROCEDURE FOUND ≠ FITTED BYTES FOUND.**

## 5. Fitted/shared state ve deterministic regeneration — INV-AUD-002

| Kalem | Fiziksel artifact | Regeneration statüsü | Sonuç |
|---|---|---|---|
| word/char TF-IDF vocabulary + IDF | NOT_LOCATED | **UNKNOWN** | archive-dependent fitted state; corpus-free reopen kanıtı yok |
| source latent SVD (5101) | NOT_LOCATED | **UNKNOWN** | seed tek başına fitted component üretmez |
| mixed96 SVD (5204) | NOT_LOCATED | **UNKNOWN** | archive data olmadan reopen kanıtı yok |
| `mu96` | NOT_LOCATED | **UNKNOWN** | archive document state’inden türetilir |
| ITQ96 rotation | NOT_LOCATED | **UNKNOWN** | fitted optimization state |
| SIMHASH/Haar | NOT_BOUND | **REGENERATION_CANDIDATE_NOT_VERIFIED** | seeded generation var; exact RNG/version/dtype/order/dimension reopen contract yok |
| PQ96 codebooks | REAL_ARCHIVE_ARTIFACT_NOT_LOCATED | **UNKNOWN** | synthetic Faiss state gerçek archive fitted codebook değildir |
| OPQ_PQ96 rotation/codebooks | REAL_ARCHIVE_ARTIFACT_NOT_LOCATED | **UNKNOWN** | aynı sınır |
| RaBitQ32 real archive state | REAL_ARCHIVE_ARTIFACT_NOT_LOCATED | **UNKNOWN** | library structure gerçek archive package yerine geçmez |
| L2 normalization rule | SOURCE_CODE_PRESENT | **DETERMINISTIC_REGENERATION_VERIFIED** | algoritmik rule; learned archive state değildir; persistent header/config cost’unu sıfır yapmaz |

Hiçbir fitted archive-dependent item `PERSISTED_ARTIFACT_VERIFIED` veya `DETERMINISTIC_REGENERATION_VERIFIED` seviyesine yükseltilmedi.

## 6. T4C2 diagnostic NPZ bundle — INV-AUD-003

Bağımsız audit, Drive T4C2 final paketinde `V52_T4C2_ALL_OUTPUTS.zip` içinde nested `V52_T4C2_BINARY_GEOMETRY.zip` ve 470 `codes/<question_id>.npz` diagnostic artifact bulunduğunu doğruladı. Örnek şema packed doc/query codes, ITQ seeds, `gold_rows`, `N_archive`, `bitorder` alanları içeriyor.

Sınıf: **FOUND_BUT_EXCLUDED_DIAGNOSTIC_ARTIFACT**.

Gerekçe: bunlar fitted TF-IDF/SVD/`mu96`/rotation state serialization’ı değildir ve declared static-storage package değildir. Query/gold alanları retrieval-quality için yorumlanmadı.

## 7. ID / offset / payload mapping — INV-AUD-004

Beş yönlü durum:

- `logical_id_exists = VERIFIED`
- `package_stores_id = UNKNOWN`
- `implicit_mapping_reproducible = UNKNOWN`
- `external_boundary_dependency = UNKNOWN`
- `mapping_status = UNKNOWN`
- `persistent_mapping_bytes = UNKNOWN`

Adapter’ın deterministic `memory_id` üretmesi, persistent mapping’in ücretsiz olduğunu kanıtlamaz. `0 bytes` ancak declared package boundary altında code row’dan doğru payload’a dönüşün per-vector mapping baytı olmadan doğrulanması halinde yazılabilir.

## 8. Fiziksel kopya / paylaşım

Bilinen: fit scope archive-local.

Bilinmeyen: persistent serialization scope, physical copy count, gerçek sharing group ve `N_i`’nin gerçek amortization denominator olarak fiziksel doğrulanması.

Bu nedenle:
- `physical_copy_count = UNKNOWN`
- `sharing_population = N_i_CANDIDATE_NOT_PHYSICALLY_VERIFIED`
- `effective cost = NOT_READY`

## 9. Genişletilmiş arama kaydı — INV-AUD-005

Makine-okunur tam kayıt: `drafts/v52/static_storage_inventory_2026_09_12/SEARCH_LOG_V2.json`.

Aranan panel `.pkl, .pickle, .joblib, .npz, .npy, .faiss, .index, .bin, .model, .pt, .pth, vectorizer, vocabulary, vocab, idf, svd, components, projector, projection, mu96, center, centering, rotation, itq, haar, pq, opq, rabitq, centroid, codebook, serializer, serialization, archive_model, model_state, manifest, hash, receipt` terimlerini kapsar.

Doğru sonuç dili: **SEARCHED / NOT LOCATED / UNKNOWN**. Bu, yokluk kanıtı değildir.

## 10. Sonuç ve next gate

Inventory hâlâ **NOT_READY**.

Açık bloklar:
1. archive-dependent fitted model/projector physical artifact’ları bulunmuş ve bağlanmış değil;
2. ID/offset/metadata necessity gerçek package operasyon paneliyle sınanmış değil;
3. physical copy count / sharing population dosya/serializer düzeyinde doğrulanmış değil;
4. gerçek adapter + önceden hash-bound serialization/probe planı yok;
5. bu düzeltilmiş inventory henüz yeni bağımsız review’dan PASS almadı.

Eksik state’i doldurmak için raw corpustan gizli refit yapılmayacaktır.

Task4F1: **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**.
