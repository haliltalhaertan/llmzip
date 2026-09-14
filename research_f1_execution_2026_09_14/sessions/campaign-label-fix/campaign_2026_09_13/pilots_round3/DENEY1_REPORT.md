# DENEY 1 RAPORU — Öğrenilmiş seçim priminin çok-split sağlamlaştırması

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Tarih: 2026-09-13 · Kaynak karar kuralı: Muse yol haritası Design 1 (önceden ilan edilen kill/promote kapıları)
Doğrulama durumu: BAĞIMSIZ YENİDEN-HESAP BEKLİYOR (D1V oturumu koşuyor)

## HÜKÜM (önceden ilan edilen kurallara göre): KILL

Önceden ilan edilen kural: *"KILL learned selection from (b) if mean-vs-best < +1.0 pp OR
win-rate vs best < 7/10 OR LoCoMo mirror mean-vs-best ≤ 0."*

Üç tetikleyicinin **üçü de ateşledi**:

| Kriter | Eşik | Ölçülen | Sonuç |
|---|---|---|---|
| LME drop64, ortalama vs-best | ≥ +1.0pp gerekli | **−1.25pp** | ✓ KILL |
| LME drop64, win-rate vs-best | ≥ 7/10 gerekli | **2/10** | ✓ KILL |
| LoCoMo drop64, ortalama vs-best | > 0 gerekli | **−0.15pp** | ✓ KILL |

**Sonuç: Öğrenilmiş eksen seçimi (drop64/alone64) (b) 12-byte bütçe yarışının kol tablosundan
ÇIKARILDI.** Önceden ilan edilen gating kuralı gereği (b)'nin öğrenilmiş-kol yerine
spread/random panelleri kullanacak. R2B'nin tek-split'lik "+1.62pp vs en iyi 3 seed" bulgusu
bir **split/seed şansıydı** — bu deney tam bunu test etmek için tasarlanmıştı ve sonuç negatif.

## Tasarım (donmuş altyapı, hepsi mevcut; yeni koşu)

- **10 tabakalı (%50/50) split** — question_type'a (LME) / kategoriye (LoCoMo) göre tuzlu-hash
  dağıtımı; her split disjoint+complete (470: 236/234; LoCoMo: 767/768).
- **Utility'ler yalnız eğitim tarafından** (drop/alone/var; +LME'de delta); provenance
  ayrım testi: eğitim-only top-64 ile full-data top-64 min örtüşmesi 50/64 → utility gerçekten
  eğitim-only.
- **Random paneller: split başına 10 taze seed** (formül: `91000 + 10*split + j`) — R2B'deki
  3 seed yetersizdi (3.34pp aralık).
- **SPREAD onarımı:** eski stride-2 çatısı (k=64'te 48'e kırpılıyordu) yerine **gerçek
  rank-linspace** (round(linspace(0,95,k)) ayrık pozisyonlar; eff_k==k assert'li).
- **Birincil ölçüt:** split-başına (drop64_test − o-splitin-en-iyi-random-seed'i); ikincil:
  vs panel ortalaması. Bootstrap: soru-eşli, B=2000, %90 CI, resample içinde yeniden best-of-10
  (adil "en iyi seçimi").
- Protokol aynen: sign-Hamming top-3, 20 tie trial, per-question lex-ordinal priority rng —
  LME'de R2B ile, LoCoMo'da T4D/R2C ile bit-uyumlu.

## KAPILAR (hepsi geçti)

| Kapı | Sonuç |
|---|---|
| LME native yeniden-hesap | max abs diff **1.11e-16**; ortalama 0.5419751773049645 birebir |
| LoCoMo native yeniden-hesap | diff **0.0** vs anchor 0.23654714666441054 |
| Split bütünlüğü | 10/10 disjoint+complete, tip-dengeli |
| Utility provenance | train-vs-full top-64 örtüşme min 50/64 (ikisi farklı ✓) |
| SPREAD eff_k assert | 6/6 kolon kümesi distinct (LME+LoCoMo, k∈{32,48,64}) |
| **Varyans-kontrol validity** | LME 29/30 kontrol "var en kötü"; tek istisna: s9-k64'te delta (0.3998) var'dan (0.4298) da kötüydü — **var "kazanmadı"**. LoCoMo 30/30 temiz. |

## LME sonuçları (470 soru; split-başına ~234 test)

| s | native | drop64 | alone64 | RAND64 best | RAND64 mean | gap vs best | gap vs mean |
|---|---|---|---|---|---|---|---|
| 0 | .5233 | .4646 | .4754 | .4835 | .4652 | −1.89 | −0.05 |
| 1 | .5477 | .5121 | .4848 | .5306 | .5095 | −1.85 | +0.26 |
| 2 | .5162 | .4870 | .4655 | .4792 | .4636 | +0.78 | +2.35 |
| 3 | .5410 | .4751 | .4944 | .5062 | .4896 | −3.11 | −1.45 |
| 4 | .5534 | .4990 | .4710 | .5208 | .4927 | −2.18 | +0.63 |
| 5 | .5650 | .5252 | .4925 | .5138 | .5074 | +1.14 | +1.77 |
| 6 | .5506 | .5119 | .4646 | .5193 | .4957 | −0.74 | +1.62 |
| 7 | .5315 | .4909 | .4586 | .4996 | .4886 | −0.87 | +0.23 |
| 8 | .5523 | .4949 | .4917 | .5174 | .5078 | −2.26 | −1.29 |
| 9 | .5167 | .4826 | .4549 | .4974 | .4803 | −1.48 | +0.23 |

**Özet (birincil):** drop64 ortalama **−1.25pp** [−3.11, +1.14], wins **2/10**.
alone64 ortalama **−3.15pp** [−5.47, −0.82], wins **0/10**.
**İkincil (vs ortalama):** drop64 **+0.43pp** (7/10) — yani panel ortalaması düzeyinde, prim yok;
alone64 −1.47pp.

## LoCoMo sonuçları (1535 geçerli soru; ~153 test/split)

Gate: native diff **0.0**. Aynı tablo (tam sayılar JSON'da):

| s | native | drop64 | alone64 | best64 | mean64 | gap vs best |
|---|---|---|---|---|---|---|
| 0 | .2417 | .2120 | .2090 | .2162 | .2051 | −0.42 |
| 1 | .2407 | .2067 | .2148 | .2103 | .1982 | −0.36 |
| 2 | .2260 | .1979 | .1906 | .1997 | .1860 | −0.18 |
| 3 | .2274 | .1906 | .1902 | .1953 | .1850 | −0.47 |
| 4 | .2446 | .2143 | .2176 | .2222 | .2033 | −0.79 |
| 5 | .2362 | .2151 | .1930 | .2078 | .1953 | +0.73 |
| 6 | .2448 | .2061 | .2101 | .2085 | .2023 | −0.25 |
| 7 | .2365 | .2071 | .2237 | .2188 | .2007 | −1.17 |
| 8 | .2345 | .2101 | .2118 | .1914 | .1849 | +1.87 |
| 9 | .2357 | .2059 | .2108 | .2106 | .1945 | −0.47 |

**Birincil:** drop64 **−0.15pp** [−1.17, +1.87], wins **2/10**; alone64 −0.09pp, 5/10.
**İkincil (vs ortalama):** drop64 **+1.11pp (10/10)**, alone64 +1.16pp (9/10) — dikkat çekici ama
karar kriteri DEĞİL. Yorum: "en iyi seed" seçici maksimum istatistiği ~+1.2pp yukarı sapıyor;
öğrenilmiş kol panel ortalaması düzeyinde (hatta az üstünde) ama **en iyi rastgele çekilişi
sistematik olarak geçemiyor**. Pratik anlamı aynı: mühürlenecek bir prim yok.

## Yan bulgular

1. **Onarılmış SPREAD64:** LME'de panel ortalamasını 9/10 split'te geçiyor (+1.17pp ortalama)
   ama vs-best 3/10 (−0.50pp); LoCoMo'da vs-mean −0.33pp. → Random panellerle istatistiksel
   olarak ayrışmıyor; (b) için geçerli bir "iyi bilinen" kol, "öğrenilmiş" değil.
2. **Kill, R2D'nin uyardığı "seed-noise laundering"in ölçülmüş halidir:** R2B'nin +3.39pp
   (3-seed ortalaması) → 10-seed ortalamasına karşı +0.4…+1.1pp → en iyi seed'e karşı negatif.
   Seed sayısı arttıkça "prim" kayboldu → prim seed-şansıydı.
3. **var-en-kötü validity'si 59/60 kontrolde tuttu** (tek istisna zararsız: başka bir kol daha
   kötüydü). Bu, boru hattının ve tur-1/2'top-variance-aşırı-kötü bulgusunun sağlamlığını
   bağımsız olarak yeniden doğruladı.
4. LME'de utility'lerin top-5'i split'ten split'e değişiyor (s0 [83,61,92,94,63] vs s1
   [94,45,92,84,95]) — tek-split utility seçiminin neden kırılgan olduğunun ek kanıtı.

## Sonuçların yol haritasına etkisi

- **(b) 12-byte yarışı kol tablosu güncellendi:** öğrenilmiş kol GİRDİ DEĞİL (pre-declared
  kural); spread/random panelleri onun yerinde; RaBitQ/PQ kolları değişmedi.
- **Deney 3 (transfer)** yine de koşuyor (bilgilendirici; "utility evrensel mi" sorusu) ama
  artık bir (b) kapısı değil.
- **Deney 2 (tie-mass) etkilenmedi**; mekanizma hattı aynen sürüyor.
- Muse §2.5 gereği: bu **imzalı null** ("öğrenilmiş seçim primsiz; en iyi seed'e karşı negatif")
  yayın/narratif envanterine girer.

## Dosyalar + hash'ler

- `harness/deney1_lme.py` sha256 `556b67136965c607…` (tam: 556b67136965c607b71d764261ac1b9c204000bc1b0d3b7efc7dbc143377999c)
- `harness/deney1_loco.py` sha256 `c2d3c0e7b3a6676539df7216e49bf3f20c506f1124df2b940e0d55b80fbad1af`
- `round3/deney1_lme_details.json` (831,494 B) sha256 `2dabcb26229d83bd…`
- `round3/deney1_loco_details.json` (1,843,468 B) sha256 `7ffa7c192cb60e84…`
- `round3/deney1_loco_peraxis.npz` (110,608 B) sha256 `90cae3fc1e01fb91…` — LoCoMo per-eksen
  drop/alone/native/pool/var_rank dizileri (transfer deneyi ve bağımsız doğrulama için)

**Not:** Tam hash'ler `HASHES_ROUND3.txt`'te; bağımsız yeniden-hesap (D1V) ve tasarım denetimi
tamamlanınca bu rapora eklenti düşülecek; hiçbir sayı doğrulanmadan alıntılanmamalı.
