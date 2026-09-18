[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DUZELTME DEFTERI — R1..R4 denetimleri + dis inceleme (2026-09-17)

Her satir KOORDINATOR TARAFINDAN BAGIMSIZ DOGRULANDI (ajan beyani yeterli sayilmadi).
Kaynak agaci degismedi: 2562 dosya, sha256 farki 0.

## A. ETIKET GERI CEKME (en onemli)

### A1. "Transductive leakage" -> KORPUS-UYARLAMA BAGIMLILIGI
GERI CEKILDI. Arsiv-basina fit, projenin ONCEDEN KAYITLI TASARIM KURALIDIR.
Kanit (dogrulandi):
  research_f1_execution_2026_09_14/agent_packages/research_commonmode_cost_2026_09_14/
  COMMON_MODE_CLASSIFICATION.md:61 "Per-archive fitting is a RULE, not an accident"
  prereg draft :79-81 "Archive-local state is fitted and charged to each archive
  separately. No reuse across archives is assumed."
  adapters/longmemeval_v52_adapter.py:363-367 cross_question_fit_prohibited
R4 uretici denetimi ayrica dogruladi: sorgu ve altin fit'e GIRMIYOR
(question-in-corpus leak PASS, 0/140 ortusme).

YANLIS: "yayinlanan skorlar 20-30 puan sisirilmis / dürüst skor 18.16"
DOGRU : "yayinlanan skorlar kendi rejiminde GECERLI; sabit-kodlayici rejiminde
         performans ciddi dusuyor -> tasinabilirlik/genelleme siniri"
Durum : CODE F2 = AUDITOR_INTERPRETATION_REJECTED / USEFUL OOD CONTROL (sayilar korunur)
Sorumlu: koordinator (ben) — ajan yorumunu dogrulamadan "en buyuk geri cekme" diye
         sundum; dis inceleme itirazi uzerine geri cekildi.

## B. DOGRULANMIS RAPORLAMA HATALARI (5/5 koordinator kontrolu)

| # | Hata | Dogrulama | Durum |
|---|------|-----------|-------|
| B1 | rt_validate.json "gold_resolution: 100%" | dosyada birebir bulundu; ayni dosya 23 sifir-altin + 46 kismi listeliyor, degerlendirilen 705/728 | METIN YANLIS, sayi dogru |
| B2 | firststage REPORT latency tablosu | REPORT 0.99/1.22/0.96 ms vs RESULTS.json 1.3748/1.6966/1.3317 ms (%28-40 sapma) | TABLO YANLIS, kalite sonuclari dogru |
| B3 | expected_hit_at_10 aslinda expected-Recall | 705 satir yeniden ortalandi: bm25 hit .541844 / recall .431599 / "expected_hit" .431599 (recall'a birebir esit); tfidf .529078/.419062/.419062 | ETIKET YANLIS, manset etkilenmiyor |
| B4 | "all 30 clusters" (IDF_p2 -1.76, SHIFT_m1 +1.58) | CRITIQUE.md'de cumle bulundu; repr_results.json "clusters": 10, "clusters": 30 HIC YOK; kosum 10/30 arsivde SIGTERM | SUPPORTED_ON_SUBSET (2967/8265 soru) |
| B5 | PerLTQA "30 archives, 8265 queries" turetimi belgesiz | REPORT.md basligi sayiyi veriyor, indirgeme adimlari yok: Chen Zhi (N=35) 40 soru, 11 key-miss, 277 bellek-banki-yok | ACIKLAMA EKLENMELI (yontem-notr dislama) |

## C. AYAKTA KALAN ANA SONUCLAR (degismedi)

- STOP yonu: adil BM25 (textbook frozen 61.70) > en iyi 48B kod (57.87). Fark -3.83 pp.
  NOT: yayinlanan -7.80 pp, test uzerinde 4 BM25 varyantinin EN IYISI secilerek olculdu;
  hakem sozlesmesi textbook BM25'i birincil ilan ediyor. Dogru acik -3.83 / FR@3 -3.26.
- "Kapilar onceden sabitlendi" -> GERI CEKILDI (kapilar ve sonuclar ayni commit 8bcdef5).
  Dogru ifade: kesifsel muhendislik/durdurma karari.
- Held-out ayrimi YOK. Negatif sonuc ("tune ettik, gecemedik") saglam; pozitif/mekanizma
  iddialari kesifsel.
- payload != toplam sistem durumu. 12/24/48 B belge yuku DOGRU; kodlayici durumu ayri
  raporlanmali (olculmus: ~88.9 kB/vektor N~500; paylasimli projektor alt siniri 202.93 B/vektor).

## D. R4'UN YENI POZITIF SONUCU (dogrulandi)

Genislik kazanci korpus-uyarlama artefakti DEGIL. Sabit baska-arsiv kodlayicisiyla
merdiven daha da dik yukseliyor (10 arsiv, 705 soru, arsiv-kumelenmis CI):

| k (bayt) | TRANS qscale | INDEP qscale |
|---|---|---|
| 96 (12B) | 49.65 | 20.00 |
| 192 (24B) | 55.32 | 27.09 |
| 384 (48B) | 57.87 | 39.86 |
| toplam kazanc | +8.22 | **+19.86** |

Kapilar: k=96 icin 0 bit fark; k=192/384 capalari LADDER.json ile 0.005 pp icinde.
Uyarlama bagimliligi genislikle AZALIYOR: qscale 29.65 -> 28.23 -> 18.01 pp.
Yayinlanan TRANS ikinci adimi (+2.55) %95'te anlamsiz; INDEP iki adim da anlamli.

Yayina uygun ifade: "Retrieval quality exhibits a strong width effect even when
archive-specific representation fitting is removed." — "48B BM25'i geciyor" DEGIL.

## E. URETICI (bench3) ILK KEZ DENETLENDI — TEMIZ

- Altin etiket eslemesi: 54/54 (30 RealTalk + 24 PerLTQA, ham veriden bagimsiz kurulum)
- Onbellek yeniden hesaplama: 4 arsiv bit-bit ayni
- Ortalama ekseni (axis 0), L2 sirasi: dogru
- Sorgu metni korpusa sizmis mi: 0/140
- RealTalk vs PerLTQA: matematik ayni (ayni parametreler, seed 5101/5204, ayni concat)
- Onemli sinir: kapi testleri (0/858,624 ve 0/1,179,648 bit) ureticinin CIKTISINI dogrular;
  ureticideki bir hata yeniden kurulum tarafindan da kopyalanacagi icin kapilar KOR olur.
  Bu tur o kor noktayi kapatti.

## F. HENUZ DENETLENMEYEN (durust envanter)

- LME / LoCoMo korpus-uyarlama kontrolu: OLCULMEDI (rol kotaya takildi)
- incoming_20260916b (5697 dosya) + incoming_20260916: yalnizca karar ozetine giren
  alt kume dogrulandi; 181 dosyada yayin sayilari geciyor, geri kalan acilmadi
- parallel_ideas_r1 (3183 dosya, 111 .py), regen, review_transfer, scratch, agent_out
- Yayin paketinde model agirliklari/semantic yukleri yok (PPLX kolu yeniden uretilemez;
  o kolun sayisi da mevcut degil, dolayisiyla yayinlanan hicbir sayi eksik dosyaya bagli degil)
- "Her sey denetlendi" DENMEZ. Gercek kapsama: karar veren hattin cekirdegi 4 kez;
  cevre altyapi kismen; paralel calisma alanlari hayir.

## G. YAPILMASI GEREKENLER (oncelik sirasi)

1. B1-B5'i kaynak dosyalarda duzelt (bu defter yalnizca tespit; kaynak DEGISTIRILMEDI).
2. "leakage" kelimesini tum denetim ciktilarindan cikar; A1 etiketini kullan.
3. Eski raporlarda duzeltme isaretcisi olmadan dolasan cumleleri isaretle
   (ozellikle LADDER_REALTALK.md ve CRITIQUE.md).
4. Kota yenilendikten sonra (21 Eylul 03:00): LME/LoCoMo uyarlama kontrolu + incoming paketleri.
5. Dondurulmus iddia setiyle TEK SEFERLIK held-out dogrulama — yeni optimizasyon turundan
   daha degerli.
