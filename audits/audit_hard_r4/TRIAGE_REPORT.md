[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# TypeSafe (Jev) ile denetim bulgusu triyaji — pilot raporu, 2026-09-18

## Ne yapildi
4 denetim turunun (R1-R4, 34 ajan) markdown raporlarindan 100 benzersiz bulgu satiri
MEKANIK olarak cikarildi (regex, tablo satirlari). Her bulguya 6 soru soruldu:
3 Noul (sayiyi curutuyor mu / sadece metin mi / tasarim kuralini kusur mu saniyor),
2 Score (duzeltme emegi, yayin engeli), 1 Choice (kategori).
KARAR KODDA verildi (triage_findings.py:decide) — model yalniz sinyal uretti.

Maliyet: 100 bulgu, 110.484 girdi + 16.901 cikti token, ~3 dakika.

## KALIBRASYON (zorunlu adim — atlanmadi)
Koordinatorun ELLE dogruladigi 3 bulgu altin kume olarak kullanildi:

| bulgu | beklenen | model karari | uyum |
|---|---|---|---|
| B2 gecikme tablosu (%28-40 sapma) | P1/P2 | P1_MUST_FIX | UYDU |
| B3 expected_hit = Recall | P1/P2/P3 | P2_SCOPE | UYDU |
| B1 rt_validate "%100" yanlis cumle | P3/P4 | P5_INTERNAL_ONLY | **FARK** |

**Uyum 2/3.** Yetersiz ornek — istatistiksel bir kalibrasyon iddiasi YAPILAMAZ.
B1 farkinin sebebi anlasilir: bulgu metninin kendisi "numbers unaffected" diyor,
model de ic detay saydi. Ama kayit hijyeni acisindan o cumle duzeltilmeli.
=> Kural: P5 kutusu otomatik kapatma icin KULLANILMAZ; gozden gecirilir.

## CAPRAZ TABLO — ajan etiketi vs kod karari

| ajan \ karar | P1 | P2 | P3 | P4 | P5 | REJECT |
|---|---|---|---|---|---|---|
| CRITICAL (7) | 1 | 0 | 0 | 3 | 2 | 1 |
| HIGH (20) | 2 | 4 | 0 | 5 | 7 | 2 |
| MED (29) | 1 | 3 | 1 | 6 | 18 | 0 |
| LOW (44) | 0 | 0 | 6 | 4 | 34 | 0 |

## EN DEGERLI CIKTI: ajanlarin ciddiyet etiketi guvenilmez

**Ajan CRITICAL dedi, triyaj dusurdu — 6/7 vaka.** Ornekler:
- R2/code F2 -> REJECT_MISREADS_DESIGN (misreads=0.68). Bu, koordinatorun ZATEN elle
  geri cektigi transductive-leakage yorumu. Triyaj bagimsiz olarak ayni sonuca vardi.
- R2/stats S1, S2 "CRITICAL: CI yok, veri saklanmamis" -> P5. Dogru: eksik CI bir
  raporlama zayifligi, yayinlanan sayiyi curutmuyor.
- R3/leak_perltqa F1 "CRITICAL: Hit@10 sisirilmis" -> P4. Dogru cerceve: bu bir
  sinirlama beyani, sayi curutulmesi degil.

**Ajan MED dedi, triyaj yukseltti — 4 vaka (asil kazanc bunlar):**
- R2/code F5: "C1 kapisi FR@3 tabanli, acik -7.23 pp; ama her iki okumada da 7.80
  Hit@10 acigi aktarilmis" -> YANLIS METRIK ALINTILANMIS. MED degil, yayin engeli.
- R2/data F3: "Manset tabloda hala handikapli BM25 54.18 var, adil 65.67 degil" -> P2.
- R2/code F7: "sym 'standardized' diye etiketlenmis ama sigma'ya hic bolmuyor" -> P2.
- R2/bytes F6: BM25 rakip maliyeti iki farkli serilestirmeyle raporlanmis -> P1.

Bu dordu 100 bulgu icinde gomulu kalmisti; ajan onlari MED diye isaretledigi icin
onceki turlarda one cikmamislardi.

## KATEGORI DAGILIMI (100 bulgu)
no_defect 58 | missing_evidence 11 | weak_test 9 | wrong_number 8 |
cost_accounting 7 | overclaim 5 | mislabel 2

58 "kusur degil" orani, ajanlarin raporlarinin yarisindan fazlasinin DOGRULAMA
(gecen kontroller) oldugunu gosteriyor — beklenen ve saglikli.

## SINIRLAR (durustce)
1. Kalibrasyon 3 ornekle yapildi. Savunulabilir bir esik icin 100-150 elle
   etiketlenmis bulgu gerekir. Bu pilot o isi YAPMADI.
2. Bulgu cikarma regex tabanli: yalniz markdown TABLO satirlari alindi. Duz
   paragraf halindeki bulgular kapsam disi kaldi.
3. Model bulgu metnine bakiyor, KAYNAK KODA bakmiyor. "Bu bulgu dogru mu?"
   sorusuna cevap vermez; "bu bulgu ne tur ve ne kadar acil?" sorusuna cevap verir.
4. Bir bulgunun dogrulugu hala koordinator kontrolu gerektirir (B1-B5'te yapildigi gibi).
5. Tipli cikti dogru cikti demek degildir.

## SONUC
Triyaj, 100 bulguyu 11 eyleme donusturulebilir maddeye (P1: 4, P2: 7) indirdi ve
ajanlarin ciddiyet etiketiyle ORTMEYEN 4 gercek yayin engeli buldu.
Kullanilabilir; ama kalibrasyon genisletilmeden "otomatik kapatma" icin kullanilmaz.

Dosyalar: triage_findings.py, FINDINGS_RAW.json, FINDINGS_TRIAGED.json
