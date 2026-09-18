[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# SIGN96 bağ geometrisi ölçümü — Türkçe rapor

**BEYAN EDİLMİŞ YENİDEN-UYARLAMA (declared re-fit), dondurulmuş yapıt değil.**
Mühürlü Task4F1: gold/evidence açılmadı; recall/doğruluk yok; doğruluk değerlendirmesi yok;
benchmark yok. Aşağıdaki her sayı ÇÖZÜNÜRLÜK KAPASİTESİ (kod geometrisi) hakkındadır.
**Bir bağı çözmek, onu doğru çözmek demek DEĞİLDİR; doğruluk burada ölçülmedi ve ölçülemezdi.**

## Kapı (ADIM 1)

10 arşivde `N_archive`, `word_columns`, `char_columns`, `combined_columns` dondurulmuş
tabloyla birebir eşleşti: **10/10 GEÇTİ** (ayrıntı `GATE.json`).

## Dondurulmuş kodun bağ yapısı (ADIM 2, tam N; N=443–527, 4932 LOO sonda)

- Sonda→aday Hamming uzaklığı (havuzlanmış çiftler): ortalama ≈47,9; s.s. ≈5,1;
  min 0–4 (bazı arşivlerde birebir aynı kodlar var); maks 66–70.
- 3. en-yakın uzaklığı (d3) ortalaması arşivlere göre 25,5–28,1.
- **Top-3 sınırında bağ çokluğu** (d3 uzaklığını paylaşan aday sayısı, havuzlanmış):
  **medyan 1; p90 2; maks 7**; ortalama 1,31.
- Sınır bağ sayısının 1'i aşma oranı **0,258**; 3'ü aşma **0,0075**; 10'u aşma **0**.
  (Histogram: bağ=1: 3662; =2: 1073; =3: 160; =4: 31; ≥5: 6 sonda.)
- 20 en-yakın adaydaki FARKLI Hamming değeri: ortalama ≈9,7 (medyan 10). Sıralama kaba
  değil ama tam ince de değil.

## Ölçek eğilimi (ADIM 3)

**(a) Arşiv-içi alt-örnekleme** (gerçek veri, tam-arşiv uyumunun satır alt-kümesi;
küçültme uyarısı: uyumun kendisi küçültülmedi, aday havuzu küçültüldü):

| N | medyan | p90 | frac>1 | frac>3 |
|---|---:|---:|---:|---:|
| 50 | 2 | 3 | 0,542 | 0,074 |
| 100 | 2 | 3 | 0,504 | 0,050 |
| 200 | 1 | 3 | 0,363 | 0,035 |
| 400 | 1 | 2 | 0,259 | 0,012 |
| tam | 1 | 2 | 0,258 | 0,008 |

Yön: **N büyüdükçe bağ AZALIYOR** (küçük N'de top-3, yoğun kitlenin içinde kalıyor).

**(b) Arşivler-arası havuzlama** (N≈1000→4932; medyan 1, p90 2 sabit; frac>1:
0,279→0,297→0,298→0,314→0,323; frac>3: 0,009→0,025; maks 5→9):

**YÜKSEK SESLİ UYARI:** her arşiv ayrı uyarlandı; havuzlanmış vektörler ortak koordinat
sistemi paylaşmaz. Havuz figürü bu genişlik/yogunluktaki bir kodun bağ davranışına
ölçek üst-sınırı verir; **TEK bir ~5000 turluk arşivin ölçümü DEĞİLDİR.**

Yön: 5 kat N artışında yalnızca hafif kuyruk büyümesi; patlama yok. Her iki ölçüm de
"bağ sorunu büyük N'de kötüleşir" fikrini **desteklemiyor** — bu, öneriyi zayıflatan
açık bir negatif sonuçtur.

## Sürekli-sorgu yeniden-skorlama (ADIM 4; `score=sign(C)·q`, depolama aynı)

- Bağlı 1270 sondadaki 2783 bağlı slottan **2766'sı (%99,4) ayrı sürekli skor aldı**;
  **1260 sonda (%99,2) tam çözüldü**. Kalan: 17 slot, 25 çift, 10 sonda.
- Kalan tam bağların gözlenen mekanizması: **birebir aynı ±1 kodlar** (Hamming 0);
  aynı kod aynı nokta-çarpımı verir, yeniden-skorlama ayıramaz
  (en çok kalan, d3 min=0 olan 07741c45 arşivindedir).
- Sürekli skorun kendi top-3 sınır bağı: sondaların ≈%0,2'sinde (çoğu arşivde 0).
- İki-aşamalı kapsama (ilk-3 sürekli adayın Hamming ilk-M listesinde kalma oranı;
  bu bir KAPSAMA geometrisidir, doğruluk DEĞİL — havuzlanmış):
  **M=10: 0,982** (tam 3/3: 0,952); **M=50: 0,997** (0,992); **M=200: 1,000** (0,999).

## Bakmadıklarım (bilinmiyor ≠ yanlış)

- Bağlı adayların doğru cevabı içerme sıklığı — gold gerekir, bakılmadı.
- Sürekli skorun bağı DOĞRU çözme oranı — gold gerekir, bakılmadı.
- Tek bir gerçek ~5000 turluk arşivde bağ yapısı — derlemde yok, ölçülmedi.
- Farklı tohum/uyarlamalarda kararlılık — tek uyum, bakılmadı.
- Gold-bağlantılı gerçek sorguların LOO sondalardan farklı davranıp davranmadığı — bakılmadı.

## Kapanış (istenen sıra)

- Kapı: 10/10 GEÇTİ.
- Tam N'de sınır-bağ çokluğu: medyan 1, p90 2.
- Ölçek: (a) alt-örneklemede bağ N ile AZALIR (gerçek veri; uyum tam-arşiv uyumu);
  (b) havuzlamada medyan/p90 sabit, kuyruk hafif büyür — **havuz, tek büyük arşiv değildir.**
- Sürekli skor bağlı slotların %99,4'ünü ayırır; 17 slot / 25 çift tam bağlı kalır.
- Kapsama: M=10: 0,982; M=50: 0,997; M=200: 1,000 (geometri; doğruluk değil).
- Bakılmayanlar yukarıda; "bakılmadı" ile "yanlış" aynı şey değildir.
- **Bağ sorunu bu boyutlarda küçüktür ve N ile büyümez görünmektedir; bu sonuç,
  onu çözmeyi amaçlayan önerinin dayanağını zayıflatır.**
