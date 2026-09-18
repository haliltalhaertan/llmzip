[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Ucuz kodlayıcı adayları — hız çözüldü, kalite çöktü

`evidence_path`: `audit_hard_r4/CHEAP_ENCODER.json`, `cheap_encoder.py` — **sıfır model çağrısı**

**Hedef (dış değerlendirmenin formülasyonu):** 5,1 MB / 2,85 ms kodlayıcıyı ~100 KB / ~0,2 ms'e
indirmek, **kaliteyi koruyarak**.

**Kritik tasarım kararı:** kodlayıcı değişince **belge kodları da değişir**. Bu yüzden her aday
için kalite uçtan uca yeniden ölçüldü — yalnız hız/RAM değil. Aksi hâlde "ucuz ama işe yaramaz"
bir kodlayıcı başarı sanılırdı.

---

## Sonuç: hız hedefi aşıldı, kalite hedefi tutturulamadı

60 arşiv, k=96, ham getirim (rerank yok):

| kodlayıcı | Hit@10 | FR@3 | RAM | kodlama | toplam sorgu |
|---|---:|---:|---:|---:|---:|
| **tfidf_svd** (mevcut) | **81,67** | **44,17** | 5.143 KB | 2,559 ms | 2,663 ms |
| hashing_rp_idf | 55,00 | 26,67 | 2.069 KB | 0,030 ms | **0,125 ms** |
| hashing_rp | 45,00 | 13,06 | **96 KB** | 0,028 ms | **0,124 ms** |
| shared_svd (ortak) | 58,33 | 22,50 | 310 KB | 6,572 ms | 6,672 ms |
| hash_direct (0 parametre) | 6,67 | 0,00 | **0 KB** | 0,021 ms | 0,117 ms |
| — BM25 referansı | — | — | 2.601 KB | — | 0,471 ms |

**Hız hedefi fazlasıyla tutturuldu:** `hashing_rp` 96 KB ve 0,124 ms — hedeflenen "100 KB /
0,2 ms" senaryosunun bile altında, BM25'ten **3,8× hızlı** ve **27× küçük**.

**Ama kalite çöktü:** Hit@10 81,67 → 45,00 (**−36,67 pp**). En iyi ucuz aday bile −26,67 pp.

---

## Karma boyutu sorunu değil — test edildi

İlk hipotez: 256 kova sözcük dağarcığı için çok az. Tarandı:

| karma boyutu | IDF yok | IDF 5k |
|---:|---:|---:|
| 256 | 45,00 | **55,00** |
| 1.024 | 40,00 | 51,67 |
| 4.096 | 43,33 | 51,67 |
| 16.384 | 38,33 | 48,33 |

**Boyut artırmak yardımcı olmuyor**, hatta kötüleştiriyor. Tavan ~55, `tfidf_svd`'nin 81,67'sinin
çok altında.

IDF ağırlığı **+10 pp** getiriyor (45,00 → 55,00) — yani sinyal terim ağırlıklandırmada, ama
yetmiyor.

---

## Asıl bulgu: kodlayıcının pahalılığı, değerinin kendisi

`shared_svd` kolu belirleyici. Ortak (arşivler arası) SVD, arşiv-başına RAM'i **310 KB'ye**
indiriyor ama Hit@10 **58,33**'e düşüyor — `tfidf_svd`'nin 23 puan altında.

> **Korpus-uyarlamalı SVD, `sign96`'nın kalitesini üreten şeyin ta kendisi.** Rastgele izdüşüm ve
> karma bunu taklit edemiyor; ortak SVD de edemiyor.

Bu, projenin daha önce ölçtüğü sabit-kodlayıcı çöküşüyle **tutarlı**: RealTalk k=96, korpus-uyarlamalı
49,65 → sabit 20,00 (−29,65 pp). Şimdi aynı olgu maliyet ekseninde görünüyor.

Ayrıca `shared_svd` **daha yavaş** (6,57 ms) — 20.000 kelimelik ortak sözlük, arşiv-başına küçük
sözlükten pahalı. Amortisman RAM'i düşürüyor, gecikmeyi değil.

---

## Düzeltilmiş proje resmi

Dış değerlendirmenin formülasyonu:

> *12-byte code başarılı bir veri yapısı. TF-IDF/SVD encoder başarısız maliyet yapısı.*

Ölçümden sonra **daraltılması gerekiyor**:

| | durum |
|---|---|
| 12 baytlık kodlar | **başarılı veri yapısı** — 5,7 KB, 0,103 ms, BM25'ten 4,6× hızlı |
| TF-IDF/SVD kodlayıcı | pahalı **ama kaliteyi üreten bileşen** |
| Ucuz kodlayıcı ikamesi | **ölçüldü, kalite çöküyor** (−27 ila −37 pp) |

Yani kodlayıcı "başarısız maliyet yapısı" değil — **maliyeti ile kalitesi aynı şeyin iki yüzü**.
Ucuzlatma denemesi, ucuzlatılan şeyin ta kendisini yok ediyor.

---

## Mühendislik hedefi yeniden formüle edildi

Eski hedef (dış değerlendirme): *kodlayıcıyı ~100 KB / ~0,2 ms'e indir, kaliteyi koru.*
İlk yarısı **başarıldı**, ikinci yarısı **başarısız**.

Yeni ve daha dar soru:

> **Korpus-uyarlamalı SVD'nin kalite katkısını, onun RAM/gecikme maliyeti olmadan elde etmenin
> bir yolu var mı?**

Ölçülen üç başarısız yol: rastgele izdüşüm, karma, ortak SVD. Denenmemiş yollar: seyrek/kırpılmış
SVD bileşenleri, nicelenmiş kodlayıcı (float32 → int8), artımlı/akış SVD, yalnız en bilgilendirici
terimlerle sınırlı sözlük.

**Bunların hiçbiri şu an bulgu değil — yalnız denenmemiş.**

---

## Sınırlar

- 60 arşiv (470'in tamamı değil), tek veri kümesi
- Ham getirim; rerank'lı sonuçlar farklı olabilir — ölçülmedi
- `tfidf_svd` kolu **yeniden kurulmuş** kodlayıcı; orijinal saklanmadığı için birebir aynı
  olmayabilir (Hit@10 81,67, orijinal hattın RealTalk sayılarıyla doğrudan karşılaştırılamaz)
- Rastgele izdüşüm tek tohumla; tohum varyansı ölçülmedi
- **Ayrılmış sınav verisi yok**
