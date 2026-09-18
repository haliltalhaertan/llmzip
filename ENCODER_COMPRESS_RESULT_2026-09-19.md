[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Kodlayıcı sıkıştırma — üç yol, üçü de kriteri geçemedi

`evidence_path`: `audit_hard_r4/ENCODER_COMPRESS.json`, `encoder_compress.py`
**Sıfır model çağrısı.** 25 arşiv, k=96.

## Başarı kriteri — deney öncesi donduruldu

Dış değerlendirmenin formülasyonu, koşu başlamadan betiğe yazıldı:

1. Hit@10, aynı kohortta tabanın **en fazla 3 puan altında**
2. Kodlayıcı RAM **≤ 100 KB**
3. Sorgu kodlama **≤ 0,25 ms**

**Üçü birden** sağlanmazsa yöntem hedefi çözmüyor.

---

## Sonuç: 11 koldan hiçbiri üç kriteri geçemedi

| kol | Hit@10 | fark | RAM KB | ms | bit-flip % | 3/3 |
|---|---:|---:|---:|---:|---:|:--:|
| **taban** tfidf_svd | 80,00 | — | 2.916 | 2,809 | — | — |
| A_int8 | 72,00 | −8,00 | 2.916 | 1,209 | 0,95 | — |
| A_int8_prune50 | 72,00 | −8,00 | 2.260 | 1,188 | 0,95 | — |
| A_int8_prune90 | 72,00 | −8,00 | 1.052 | 1,043 | 5,28 | — |
| A_int8_prune95 | 64,00 | −16,00 | 856 | 1,006 | 10,92 | — |
| B_sparse32 | 12,00 | −68,00 | 706 | 1,016 | 33,09 | — |
| B_sparse64 | 24,00 | −56,00 | 721 | 0,979 | 26,66 | — |
| B_sparse128 | 44,00 | −36,00 | 751 | 0,947 | 19,92 | — |
| C_codebook256 | 64,00 | −16,00 | 720 | 0,795 | 8,52 | — |
| **C_codebook512** | **72,00** | −8,00 | 750 | 0,763 | 4,15 | — |
| **BC_hybrid** | **72,00** | −8,00 | 735 | **0,359** | 7,15 | — |

---

## Asıl bulgu: RAM kriteri **yapısal olarak** geçilemez

Hiçbir kol 100 KB'ye yaklaşamadı. Sebep sıkıştırmanın zayıflığı değil — ayrıştırdım:

| bileşen | RAM | sıkıştırılabilir mi |
|---|---:|---|
| **Sözlük** (kelime→indeks) | **691 KB** | **hayır — hiçbir kol dokunmuyor** |
| SVD matrisi (float32) | 4.452 KB | evet, tüm çalışma burada |
| toplam | 5.143 KB | |

Medyan 5.936 kelimelik sözlük tek başına **691 KB**.

> **SVD matrisi sıfıra inse bile 100 KB kriteri geçilemez.** Darboğaz projeksiyon matrisi değil,
> **sözlüğün kendisi**. Üç yolun üçü de yanlış bileşeni hedefliyordu.

Bu, sıkıştırma yollarının kalitesinden bağımsız bir **yapısal sınır**. Senin önerdiğin
44 KB'lik hesap (20k kelime → prototip 1 bayt + 256×96 int8) yalnız **prototip tablosunu**
sayıyordu; kelime→prototip eşlemesinin kendisi Python sözlüğü olarak 691 KB tutuyor.

---

## Yine de sıralama bilgilendirici

Senin öncelik sıran kısmen doğrulandı:

**En iyi iki kol `C_codebook512` ve `BC_hybrid`** — ikisi de öğrenilmiş kod kitabı tabanlı,
ikisi de −8,00 pp'de ve bit-flip oranları en düşükler arasında (%4,15 ve %7,15).

**`BC_hybrid` en hızlı: 0,359 ms** — tabandan **7,8× hızlı**, senin 0,25 ms hedefine en yakın kol.

**B (seyrek hiperdüzlem) tek başına felaket:** 32 terim %12, 64 terim %24, 128 terim %44.
Bit-flip %33'e çıkıyor. Yani *"aynı biti üretmek için binlerce kelime gerekli mi?"* sorusunun
cevabı bu veride **evet** — en azından bit-başına-bağımsız seyrekleştirmeyle.

**A (int8) neredeyse bedava:** bit-flip yalnız %0,95 ama Hit@10 yine de −8 puan düşüyor.
Bu ilginç: **%1 bit değişimi 8 puan kaybettiriyor** — sistem bit-flip'e beklenenden hassas.

---

## Ara metrik yine yanıltıcı

`A_int8` bit-flip %0,95 ile en "sadık" kol, ama Hit@10 kaybı `C_codebook512` ile **aynı** (−8,00)
ve FR@3'te `A_int8` daha iyi (43,33 vs 37,33).

Buna karşılık `A_int8_prune90` %5,28 flip ile FR@3'te 27,33'e çöküyor, `C_codebook512` %4,15 flip
ile 37,33'te kalıyor. **Flip oranı tek başına kaliteyi öngörmüyor.**

Bu, L-112'de kaydedilen dersin üçüncü tekrarı: ara metrik (bit-flip) nihai metrikle (Hit@10/FR@3)
güvenilir biçimde hizalanmıyor.

---

## Ne öğrenildi, ne öğrenilmedi

**Öğrenildi:**
- 100 KB hedefi **sözlük yüzünden** bu mimaride ulaşılamaz — yapısal sınır
- Öğrenilmiş kod kitabı (C) rastgele yöntemlerden (L-117: hashing 45,00) **belirgin üstün** (72,00)
- int8 kuantizasyonu bit-flip'i %1'de tutuyor ama yine 8 puan kaybettiriyor
- Bit-başına seyrekleştirme (B) tek başına çalışmıyor

**Öğrenilmedi / denenmedi:**
- **Sözlüksüz** bir mimari (karma tabanlı indeksleme + öğrenilmiş kod kitabı birleşimi) — bu,
  sözlük darboğazını aşabilecek tek yol ve **denenmedi**
- Kelime sözlüğünü kırpma (en bilgilendirici 1.000 terim) ve kalite bedeli
- `BC_hybrid`'in daha agresif varyantları
- n=25 çok küçük: Hit@10'da 4 puan = 1 arşiv. Sıralama gösterge, **kesin değil**

---

## Sınırlar

- **n=25 arşiv** — tek arşiv Hit@10'u 4 puan oynatır; bu tablo yön gösterir, hüküm vermez
- Ham getirim, rerank yok
- Taban **yeniden kurulmuş** kodlayıcı (orijinal saklanmamış)
- RAM ölçümü Python nesnelerinin gerçek boyutu; C/Rust uygulamasında sözlük çok daha küçük olurdu
  — bu, ölçümün **uygulama-bağımlı** olduğu anlamına gelir ve kriterin kendisi de öyle
- **Ayrılmış sınav verisi yok**

---

## ⚠ Kapsam sınırı — 691 KB bir alt sınır DEĞİL

> **691 KB sözlük maliyeti bir "bilgi-teorik minimum" değildir.** Bu, **Python/sklearn nesne
> temsilinin** ölçülen maliyetidir. C/Rust, minimal perfect hash, succinct dictionary, FST gibi
> yapılarla ciddi biçimde küçülebilir.

| ❌ yanlış | ✅ doğru |
|---|---|
| "100 KB imkânsız" | **"Mevcut Python/sklearn temsili altında 100 KB mümkün değil."** |

Bu ayrım açıkça kaydedilmiştir; aksi hâlde bu projenin L-098 (`−7,80` manşeti) ve L-105
(`closure_scope`) düzeltmelerindeki **kapsam şişmesi** hatası tekrarlanır.

## Bu turda AÇILMAYAN yeni soru

> SVD matrisini değil, **sözlük + projeksiyonu birlikte** nasıl kompaktlaştırırız ve
> korpus-uyarlamalı kaliteyi koruruz?

Kayda geçirildi, **koşulmadı**.
