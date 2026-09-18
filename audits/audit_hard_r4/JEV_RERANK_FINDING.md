[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Semantik yeniden sıralama pilotu — 96-bit aday havuzu + Jev

Tarih: 2026-09-18. Veri: LME, n=470 sorgu. Model: `jev-1.13.0` (sürüm pinli).
Betikler: `jev_rerank_pilot.py` (kod kolları), `jev_rerank_bm25.py` (BM25 kolu).

## Soru

96-bit kod doğru belgeyi top-10'a sokuyor ama yanlış sıraya koyuyorsa, **semantik** bir
yeniden sıralayıcı bu hatayı düzeltebilir mi? Daha önce yalnız **sözlüksel** (BM25) yeniden
sıralama denenmişti ve hiçbir şey katmamıştı.

## Boru hattının geçerliliği

Ölçüm başlamadan önce, yayınlanmış değerlerin yeniden üretildiği doğrulandı:

| kol | bu pilotun base FR@3 | `DECISION_TESTS.json` | |
|---|---:|---:|---|
| float_raw | 44,16 | 44,16 | ✓ |
| float_std | 55,74 | 55,74 | ✓ |
| asym | 50,65 | 50,65 | ✓ |

Aynı metrik ölçülüyor.

## Sonuç

Aynı Jev yeniden sıralayıcısı **her havuza** uygulandı. LME, n=470, FR@3:

| havuz | B/belge | tavan H@10 | önce | Jev sonrası | Δ |
|---|---:|---:|---:|---:|---:|
| **sign96** | **12 B** | 86,38 | 54,60 | **70,66** | +16,06 |
| float_std | 1536 B | 88,30 | 55,74 | 70,71 | +14,97 |
| asym | 12 B | 85,74 | 50,65 | 66,04 | +15,39 |
| float_raw | 1536 B | 82,55 | 44,16 | 62,71 | +18,55 |
| **BM25** | ters indeks | 87,87 | 59,93 | **71,87** | +11,94 |

Hit@1 için eşleştirilmiş bootstrap (20.000 tekrar, seed 20260918, n=470):

| kol | Jev'in Hit@1 katkısı | CI95 |
|---|---:|---|
| sign96 | +22,98 pp | [+17,45, +28,51] **SIG** |
| float_raw | +25,53 pp | [+20,21, +30,85] **SIG** |
| asym | +24,89 pp | [+19,57, +30,21] **SIG** |
| float_std | +18,30 pp | [+12,98, +23,62] **SIG** |

600 sorgu düzeldi, 169 bozuldu, 0 hata.

## Doğrulanan: semantik ≠ sözlüksel

| yeniden sıralayıcı | LME FR@3 katkısı |
|---|---:|
| BM25 (sözlüksel) — `asym96_bm25` | **−0,38** |
| BM25 (sözlüksel) — `qscale96_bm25` | −0,33 |
| BM25 (sözlüksel) — `float_raw32_bm25` | −0,27 |
| **Jev (semantik) — sign96** | **+16,06** |

Sözlüksel yeniden sıralamanın olumsuz sonucunu semantik olana genellemek **yanlıştı**.
Mekanizma da öngörüldüğü gibi: kod belgeyi %86 oranında top-10'a sokuyor ama ilk sıraya
koyamıyor (H@1 43,83); Jev o sıralama hatasını düzeltiyor (H@1 66,81).

## Ama adil kapıda geçmiyor

İlk hesap `sign96+Jev` (70,66) ile **BM25 yalın** (58,03) karşılaştırıyordu → +12,63 pp.
Bu **yanlış karşılaştırma**: yeniden sıralanmış bir sistemi sıralanmamış birine karşı ölçüyor.
Aynı hata sınıfı bu programda daha önce yayınlanmış bir manşete yol açmıştı (−7,80 vakası).

Doğru kapı, aynı yeniden sıralayıcı her iki havuza uygulandığında:

| karşılaştırma | fark |
|---|---:|
| sign96 + Jev vs BM25 + Jev | **−1,21 pp** |
| float_std + Jev vs BM25 + Jev | −1,16 pp |
| asym + Jev vs BM25 + Jev | −5,83 pp |

**Hiçbir kod kolu geçmiyor.**

## Yine de kayda değer olan

- `sign96` **12 bayt** ile 1536 baytlık `float_std` ile aynı sonucu veriyor (70,66 vs 70,71).
- BM25'e olan açık, sözlüksel rerank rejimindeki −0,38'den farklı bir yere taşındı: şimdi
  −1,21 pp, ama **her iki taraf da yeniden sıralanmış** durumda ve kod tarafı belge başına
  12 bayt taşıyor.
- Yani bayt-başına karşılaştırmada durum bambaşka; toplam sistem durumu (kodlayıcı) hâlâ
  hesaba katılmadı.

## EK (aynı gün): eşleşmiş güven aralığı ölçüldü

`matched_ci.py`, yalnız iki karar kolunu (sign96, BM25) yeniden koştu ve soru-bazlı sonuçları
**kalıcı sakladı**. n=470, 9.400 yargı, 0 hata, 443 s.

| | tavan H@10 | Hit@1 | FR@3 |
|---|---:|---:|---:|
| sign96 + Jev | 86,38 | 66,60 | 70,37 |
| BM25 + Jev | 87,87 | 68,51 | 72,48 |

Eşleştirilmiş bootstrap, 20.000 tekrar, seed 20260918:

| ölçüt | Δ | CI95 | sonuç |
|---|---:|---|---|
| FR@3 | **−2,10 pp** | **[−4,97, +0,70]** | sıfırı içeriyor → **ayırt edilemez** |
| Hit@1 | −1,92 pp | [−5,53, +1,70] | sıfırı içeriyor → **ayırt edilemez** |

**Karar:** `BM25+Jev` üstünlüğü bu veride **desteklenmiyor**. 12 baytlık işaret yükü, ters
indeksle aynı istatistiksel kefeye giriyor — üstün değil, ölçülebilir şekilde geride de değil.

### Yan bulgu: yeniden sıralayıcı deterministik değil

Aynı girdiyle iki koşu farklı sonuç verdi. Aday havuzları **birebir aynı** olduğu (tavan H@10
86,38 ve 87,87, iki koşuda da özdeş) için fark yalnızca Jev'in skorlarından gelebilir:

| | koşu 1 | koşu 2 | fark |
|---|---:|---:|---:|
| sign96 FR@3 | 70,66 | 70,37 | −0,29 |
| BM25 FR@3 | 71,87 | 72,48 | +0,61 |
| **Δ** | **−1,21** | **−2,10** | 0,89 |

Koşu-arası oynama (0,89 pp) CI genişliğinin (5,67 pp) **içinde** — yani tutarlı, ama
tek bir koşunun nokta tahminini alıntılamanın neden yanlış olduğunun canlı kanıtı.
**Bu hattın her sayısı aralıkla birlikte verilmelidir.**

## Sınırlar — bu bulgunun neyi kanıtlamadığı

1. ~~**−1,21 pp bir NOKTA TAHMİNİ.**~~ **ÇÖZÜLDÜ** (yukarıdaki ek). Ama kusur kayda geçer:
   ilk koşu soru-bazlı sonuçları hesaplayıp **attı** — denetimlerin `decision_tests.py:156-191`
   için bulup eleştirdiği kusurun birebir tekrarı, bu kez pilot kodunda. Her iki betik
   `per_query` kalıcılığı için düzeltildi. **Yukarıdaki ana tablodaki sayılar düzeltme öncesi
   koşudandır**; karar veren sayılar ektedir.
2. **Tek veri kümesi.** Yalnız LME. RealTalk/PerLTQA'da doğrulanmadı.
3. **BM25 bu pilotta yeniden kuruldu** (textbook k1=1,2 b=0,75, frozen tokenizer) çünkü LME
   için BM25 top-10 kimlikleri saklanmamıştı. Hakem sözleşmesinin birincil yapılandırması
   kullanıldı ama bu, yayınlanmış BM25 kolunun birebir kopyası değildir.
4. **Ayrılmış sınav verisi yok.** Bu da her şey gibi keşifsel.
5. **Maliyet ölçüldü, optimize edilmedi:** kod hattı 9,84M token, BM25 hattı 2,47M
   (BM25 daha kısa belgeler seçtiği için). Sorgu başına ~20.900 token. "Ucuz" demek için erken.

## Değerlendirme

Hipotezin **mekanizması doğrulandı**, **kapısı geçilmedi**. Bu, kapatılmış twelve-byte hattını
yeniden açmaz — ama C5 kaydının statüsünü değiştirir: artık `PARTIALLY TESTED` değil,
**doğrudan test edildi, sonuç nüanslı**.

Yeniden açma koşullarından ikisi şimdi canlı:
- **(1) daha iyi toplam RAM/CPU/gecikme dengesi** — 12 B vs ters indeks, ölçülmedi;
- **(4) ters indeks tutulamayan konuşlandırma** — orada 12 B + reranker, BM25 + reranker'a
  1,21 puan farkla rakip.

Bir sonraki adım bu iki koşulu ölçmek olurdu; yeni bir getirim yöntemi aramak değil.
