# V52 statik depolama — mevcut kaynak envanteri

**Durum: DRAFT / PARTIAL / NOT_READY / NO MEASUREMENT / NO EXECUTION AUTHORIZATION.**

Bu belge `drafts/v52/static_storage_contract_2026_09_12/` altındaki ölçüm sözleşmesini değiştirmez ve onun bağımsız incelemesini genişletmez. Amaç yalnızca mevcut Git/Drive kaynaklarının fiziksel envanterini çıkarmaktır. Bu turda hiçbir gerçek retrieval, query/gold erişimi, korpus yeniden işleme, model yeniden fit etme, maliyet ölçümü, mühür veya Task4F1 işlemi yapılmamıştır.

## 1. Bağlayıcı muhasebe sınırı

Bağlayıcı karar nesnesi **marjinal kalıcı B/vektör <= 12** sınırıdır. Kodla birlikte vektör başına saklanması zorunlu norm, ölçek, düzeltme, kimlik, offset ve metadata bu tavana girer. Paylaşılan model/projektör durumu ayrı ölçülür ve gerçek paylaşım nüfusuna göre etkin B/vektör olarak ayrıca raporlanır. Bu envanter henüz herhangi bir kalemin bayt maliyetini ölçmez.

Kaynak yetkisi: `drafts/v52/static_storage_contract_2026_09_12/source/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`, kaynak commit `89d3169adb65a9a2ab7f289997d7c49eb8ccf25c`. Kaynağın kendi metnindeki yetki statüsü yükseltilmez.

## 2. Arşiv kimliği ve gerçek N_i kaynakları

### LongMemEval

- Birincil arşiv/N_i kaynağı: `docs/v52/task4c2/V52_T4C2_feature_geometry.csv`.
- Bu dosya 470 birincil question/archive için `question_id,N_archive,...` satırlarını taşır; tek bir sabit N kullanılmaz.
- `docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json` bu çıktıyı SHA256 `d4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32` olarak kaydeder.
- Aynı manifest veri kümesi kimliğini `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442` olarak bağlar.
- Durum: **FOUND / roster source verified by repository manifest**. 470 satırın tamamı bu envanter dosyasına tekrar kopyalanmamıştır; gerçek ölçüm adaptörü çalışmadan önce kaynak satırlarını birebir doğrulamalıdır.

### LoCoMo

- Kaynak: Drive `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt`, file id `11cKt4hDPBazhrOSZxSgcT5Dw-w5kdpNi`.
- Erişim: **AVAILABLE**.
- Dosyanın kaydettiği archive-fit nüfusları:
  - `locomo_0=419`
  - `locomo_1=369`
  - `locomo_2=663`
  - `locomo_3=629`
  - `locomo_4=680`
  - `locomo_5=675`
  - `locomo_6=689`
  - `locomo_7=681`
  - `locomo_8=509`
  - `locomo_9=568`
- Aynı kayıt bir konuşmanın bir archive-fit birimi olduğunu söyler.
- Hash durumu: **UNKNOWN IN THIS INVENTORY**. Drive kimliği ve içerik erişimi doğrulandı; bu turda bağımsız SHA256 bağlanmadı.
- Durum: **FOUND / ACCESSIBLE / HASH_NOT_BOUND_HERE**.

## 3. Dondurulmuş temsilin prosedürel kaynakları

### LongMemEval adapter ailesi

`adapters/longmemeval_v52_adapter.py` ve `adapters/longmemeval_v52_adapter_v2.py` mevcut ve Git'te adreslenebilir. V2, temsil fit fonksiyonunu V1'den devralır.

V1'in `fit_archive_representation` prosedürü şu dondurulmuş fit zincirini gösterir:

- word TF-IDF: lowercase, `(1,2)` n-gram, English stop words, sublinear TF;
- char TF-IDF: `char_wb`, `(3,5)` n-gram, sublinear TF;
- word TF-IDF üzerinde archive-local TruncatedSVD, `random_state=5101`, latent boyut en çok 32;
- normalize edilmiş word, char ve latent temsiller.

Bu kod **fitted vocabulary/IDF veya SVD bileşenlerinin fiziksel serialize edilmiş kopyası değildir**. Yalnız fit prosedürünü ve runtime'da hangi fitted nesnelerin oluştuğunu gösterir.

### Mixed96 + centering

Drive `V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt` aynı aile için şunları kaydeder:

- `[latent, word, char]` birleşimi;
- archive-only `TruncatedSVD(96, random_state=5204)`;
- L2 normalize;
- `mu96` arşiv dokümanlarından hesaplanır;
- `C96=Y96-mu96`, query aynı fitted dönüşüm ve aynı `mu96` ile dönüştürülür.

Durum: **PROCEDURE FOUND; FROZEN FITTED BYTES NOT LOCATED**.

## 4. Fitted/persisted kalem envanteri

Aşağıdaki sınıflandırma “dosya bulunamadı = yok” anlamına gelmez. `UNKNOWN` yalnızca taranan kaynaklarda fiziksel artifact henüz bağlanmadı demektir.

| Kalem | Gerekli olduğu bilinen kaynak | Fiziksel artifact durumu | Hash durumu | Şimdiki sınıf | Gerekçe |
|---|---|---|---|---|---|
| Word TF-IDF vocabulary | adapter fit prosedürü | bulunmadı | UNKNOWN | **UNKNOWN** | fitted vocabulary runtime'da gerekir; serialize dosyası henüz konumlandırılmadı |
| Word TF-IDF IDF | adapter fit prosedürü | bulunmadı | UNKNOWN | **UNKNOWN** | fitted transform durumu; serialize dosyası henüz konumlandırılmadı |
| Char TF-IDF vocabulary | adapter fit prosedürü | bulunmadı | UNKNOWN | **UNKNOWN** | fitted vocabulary runtime'da gerekir |
| Char TF-IDF IDF | adapter fit prosedürü | bulunmadı | UNKNOWN | **UNKNOWN** | fitted transform durumu |
| Source latent SVD components | adapter, `random_state=5101` | bulunmadı | UNKNOWN | **UNKNOWN** | fitted components gerekir; yeniden fit edilmedi |
| Mixed96 SVD components | T4D transfer proof / T4C2 pipeline, `random_state=5204` | bulunmadı | UNKNOWN | **UNKNOWN** | fitted 96-D projector fiziksel dosyası bağlanmadı |
| `mu96` centering vector | T4D transfer proof | bulunmadı | UNKNOWN | **UNKNOWN** | archive-specific state; fiziksel dosya bağlanmadı |
| L2 normalization rule | source code | algorithm/config present | source-bound code only | **SCOPE_UNKNOWN** | öğrenilmiş state değil; archive package sınırında ayrıca saklanıp saklanmadığı kararlaştırılmalı |
| ITQ96 fitted rotation | historical method code/results | gerçek archive fitted matrix bulunmadı | UNKNOWN | **UNKNOWN** | mevcut sonuç/algoritma, kalıcı fitted matrix dosyası yerine geçmez |
| SIMHASH/Haar rotation | seed/rule kaynakları mevcut | gerçek kalıcı representation seçimi bağlanmadı | UNKNOWN | **UNKNOWN** | matrix saklama vs deterministik regeneration politikası henüz ölçüm planında bağlanmadı |
| PQ96 codebook/centroids | Faiss maliyet kanıtı sentetik | gerçek archive fitted codebook bulunmadı | UNKNOWN | **UNKNOWN** | sentetik serializer ölçümü gerçek frozen archive state değildir |
| OPQ_PQ96 rotation + codebook | Faiss maliyet kanıtı sentetik | gerçek archive fitted state bulunmadı | UNKNOWN | **UNKNOWN** | sentetik S0 gerçek archive model paketi değildir |
| RaBitQ32 shared/index state | Faiss maliyet kanıtı sentetik | gerçek archive package bulunmadı | UNKNOWN | **UNKNOWN** | kütüphane yapısı bilinse de gerçek fiziksel paket henüz bağlanmadı |
| Kalıcı row-id / memory-id mapping | adapter runtime IDs mevcut | serialize mapping bulunmadı | UNKNOWN | **UNKNOWN** | ordinal/external lookup mı yoksa stored mapping mi olduğu storage boundary ile bağlanmalı |
| Offset/lookup metadata | tanımlı fiziksel artifact yok | bulunmadı | UNKNOWN | **UNKNOWN** | gerekli olup olmadığı gerçek retrieval package arayüzüyle sınanmalı |
| Per-vector opsiyonel metadata | tanımlı fiziksel artifact yok | bulunmadı | UNKNOWN | **UNKNOWN** | gerçekten pakette tutuluyorsa toplamdan düşülemez |

## 5. Fiziksel kopya ve paylaşım nüfusu

**Bilinen:** fit kapsamı archive-local. LongMemEval prosedürü question/archive başına fit eder; LoCoMo transfer kaydı konuşma başına bir fit birimi tanımlar.

**Bilinmeyen:** fitted nesnelerin gerçekten kalıcı olarak kaç fiziksel kopya halinde saklandığı. “Archive-local fit” tek başına “diskte bir kopya vardır” veya “bütün state N_i vektöre tam olarak bir kez paylaşılır” kanıtı değildir.

Bu yüzden fitted state için şimdilik:

- physical_copy_count = `UNKNOWN`
- sharing_population = `N_i candidate, NOT YET PHYSICALLY VERIFIED`
- effective-byte hesabı = **NOT READY**

Gerçek adapter, serializer ve fiziksel dosya roster'ı olmadan `C_i/N_i` hesabı yapılmayacaktır.

## 6. Yapılan kaynak taraması

Drive ana kökü: `LLM_TOKEN_ZIP_RESEARCH_MASTER`, folder id `1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv`.

İncelenen ilgili namespace'ler:

- Drive `V52_TASK_4C2_CENTERING_GEOMETRY` ve `FINAL_2026-08-27_FULL_470`;
- Drive `V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE` final klasörü;
- Drive `V52_TASK_4D_LOCOMO_FROZEN_CROSS_BENCHMARK_REPLICATION_2026-08-29`;
- canonical Git `main` tree;
- `research/v52-sign-mechanism-locomo-2026-09-04` tree;
- twelve-byte prereg revision/source-evidence namespaces.

Aranan ad/uzantılar arasında `pkl`, `npz`, `joblib`, `model`, `svd`, `vectorizer`, `idf`, `OPQ`, `RaBitQ`, `codebook`, `centroid`, `faiss` bulunur. T4C2/T4D stage klasörlerinde ve incelenen Git ağaçlarında fitted model serialization dosyası olarak açıkça tanımlanabilen bir artifact **konumlandırılmadı**. Drive genel aramalarında OPQ/RaBitQ/codebook terimleri çoğunlukla rapor, prompt ve literatür belgelerine isabet etti.

Bu cümle bir yokluk kanıtı değildir. Doğru statü: **SEARCHED / NOT LOCATED / UNKNOWN**.

## 7. Şimdilik dahil / dışarıda / UNKNOWN

**Dahil edilen kaynak referansları:** archive roster/N_i kaynakları, adapter kaynak kodu, T4D representation-transfer proof ve hash/provenance manifestleri. Bunlar ölçüm sayısı değildir; envanter dayanaklarıdır.

**Dışarıda:** query-side geçici RAM, retrieval kalite sonuçları, dynamic retraining/recoding/write traffic, bütün corpus payload'ı. Bunlar mevcut sözleşmenin ölçüm nesnesi değildir.

**UNKNOWN:** fiziksel fitted projector/vectorizer state, method-specific gerçek archive codebooks/rotations, kalıcı ID/offset metadata, fiziksel copy count ve kesin sharing population.

## 8. Sonuç ve sonraki gate

Bu envanter **NOT_READY** durumundadır. Bir `READY` gerçek ölçüm planı üretmek için en az şu dört şey gerekir:

1. fiziksel fitted model/projector artifact'larının kaynak kimliği veya açıkça `UNKNOWN` kalacaklarının ölçüm kapsamına bağlanması;
2. gerçek package storage boundary içinde ID/offset/metadata gerekliliğinin operation/remove/restore/corrupt kontrolleriyle bağlanması;
3. fiziksel kopya ve paylaşım nüfusunun dosya/serializer seviyesinde doğrulanması;
4. bundan sonra ayrı bir gerçek adapter + serialization/probe planının ölçümden önce hash-bound olarak hazırlanması.

Kaynaklar eksik kalırsa gerçek korpustan gizlice yeniden fit edilmeyecek; sonuç `UNKNOWN/PARTIAL` olarak kalacaktır.
