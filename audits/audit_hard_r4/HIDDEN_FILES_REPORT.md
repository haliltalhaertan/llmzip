[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# R4 — 113 denetlenmemis dosyanin acilmasi + bir koordinator geri cekmesi

Arac: TypeSafe Jev, surum **PINLI** `jev-1.13.0` (alias degil; her cevabin `model_used`
alani kayitli, 113/113 ayni surum). Betik: `open_hidden_files.py`.
Girdi: onceki hattin A1/A2/A3 isaretledigi 113 dosya. Bu hat dosyalarin ICERIGINI okudu
(bas+orta+son pencereler), onceki hat yalniz ilk 1500 karakteri gormustu.

Maliyet: 113 istek, 435.231 girdi + 14.456 cikti token.

## SONUC

| karar | adet |
|---|---|
| Terk edilmis, kayda gecmemis | 60 |
| Kapanmis kusur kaydi | 21 |
| Islem gerekmez | 19 |
| Acik kusur kaydi | 12 |
| Celiski adayi | 1 |

**Yayinlanan STOP sonucunu curuten gizli sonuc BULUNAMADI.** Bu, "sessizce birakilmis
celiskili sonuc var mi" sorusunu buyuk olcude kapatiyor (sinir: pencere okumasi, tam metin degil).

## KOORDINATOR GERI CEKMESI — eksen-secimi bulgusu

Tek celiski adayi `agent_out/axis-budget/evidence/axis_budget_results.json` idi.
Acildi: yayinla celiskili DEGIL (FR@3 olcuyor, Hit@10 degil). Model burada yanildi.

Ancak koordinator (ben) icindeki bir oruntuyu kullaniciya **yeni bulgu** diye sundum:
"en iyi eksenleri secmek (top), en kotuleri secmekten (bot) daha kotu sonuc veriyor;
LME'de 32 bitte fark 8 puan; ITQ bulgusuyla ayni aileden."

**Bu sunum yanlisti. Iki sebeple:**

1. **Etki isaret koduna ait degil.** Ayni dosyada saklanan `float_top`/`float_bot`
   kollari ayni etkiyi **daha buyuk** gosteriyor. `coord_audit_check.py` calistirildi:
   12 hucrenin **9'unda float etkisi sign etkisinden buyuk** (LME m=48: sign +7.75 pp,
   float +21.88 pp — oran 2.82x). Yani olay nicemlemeden (sign) degil, **eksen
   seciminden** kaynaklaniyor. ITQ ailesine baglamak yanlis atif.

2. **Yuksek butcelerdeki "ters donme" kismen mekanik.** TOP_m ve BOT_m kumeleri
   m=48'e kadar ayrik, m=64'te **32 ekseni paylasiyor**, m=96'da ayni kume
   (bot-top = 0 ozdes olarak). Benim "64 bitten sonra ters donuyor" gozlemim bu
   ortusmeyi hesaba katmiyordu.

Ayrica ayni betik projenin kendi yayinlanmis cumlesini de duzeltiyor: "dort benchmark
ayni niteliksel sekli gosteriyor" — gercekte LoCoMo ve REALTALK monoton DEGIL
(LoCoMo'da 3, REALTALK'ta 2 dususlu adim).

**Onemli olan:** bu curutmeyi ben bulmadim. Projenin kendi koordinatoru, bu denetimden
once yazmis; betik `agent_out/axis-budget/coord_audit_check.py` olarak duruyordu ve
hicbir denetim turu oraya bakmamisti. Ben de dosyayi "yeni bulgu" diye sunarken ayni
klasordeki curutmeyi okumamistim.

**Ders (skill'e yazildi):** bir dosyada oruntu gorunce, ayni dizindeki `coord_*`
betiklerini once calistir. Terk edilmis bir deneyin yaninda genellikle onu curuten
denetim de durur.

## 12 ACIK KUSUR KAYDI — ozet

En agirlari:

1. `theory_benchmark_test_v1/locomo/COORDINATOR_REVIEW.md` — **KRITIK KAPI SAPMASI**:
   plan hem native hem tarihsel float replikasyonu sartti; isci tarihsel dizileri
   bulamayip **taze bir float baseline koyup devam etmis**. Koordinator "aciklama
   takdire deger ama yeni baseline muhurlemek orijinal replikasyon sartini
   KARSILAMAZ" demis. Disposition kaydi yok.
2. `agent_out/coord-baseline/k_and_ties.py` — iki dogrulanmamis iddia:
   (a) "+10pp K uzerindeki maksimum" — LongMemEval K=20'de **-1.71 pp'ye donuyor**;
   dogruysa programin mansetı keyfi bir parametrenin tepe noktasi.
   (b) kotu-durum esitlik bozmada sign hala +7.9 onde.
   Betik yazilmis; sonucun kayda gectigi gorulmuyor.
3. `hr-consolidation/.../DEFECT_TABLE.csv` (3 kopyada ayni) — D01-D04 CONFIRMED:
   1720 mukerrer anahtar, 41 etkilenen soru, 587/1712 soruda yapisal olarak
   imkansiz ALL@3. "Dort arsivi disla" eylemi isteniyor; yapildigina dair kayit yok.
4. `agent_out/f1-audit/evidence/gate_and_mutations.json` — C3 muhur kapisi:
   sign kolu 1e-12 toleransini **gecemiyor** (LME absdiff 1.58e-4, REALTALK 7.6e-4),
   float kolu geciyor. `benchmark_gate_pass: false`.
5. `agent_out/coord-baseline/alpha_sections.py` — koordinatorun kendi acikladigi kusur:
   arsiv basina 120 sorgu sinirlamasi yuzunden mutlak FR@3 degerleri dondurulmus
   mansetler DEGIL (PerLTQA 0.6929 vs 0.4889).

Tam liste: `HIDDEN_CONTRADICTIONS.json` (verdict=H2).

## 60 TERK EDILMIS IS

Kararla celisen yok; ama programin ne kadar dagitik oldugunu gosteriyor. Bunlar
"yanlis" degil, "bitmemis ve kayda gecmemis". Envanter olarak saklanmali.

## SINIRLAR

- Dosyalar TAM okunmadi: bas+orta+son pencereler. Buyuk bir dosyanin ortasindaki
  sonuc kacmis olabilir.
- 12 acik kusur kaydinin yalnizca 1'i (axis-budget) calistirilarak dogrulandi.
  Digerlerinin **iddialari okundu, sonuclari test edilmedi**.
- Kalibrasyon yok. Bu hat bir siralama araci; H5 kutusu bir seyi kapatmaz.
