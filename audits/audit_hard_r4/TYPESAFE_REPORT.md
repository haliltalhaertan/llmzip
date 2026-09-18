[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# TypeSafe (Jev) hatlari — toplu rapor, 2026-09-18

Dort hat kuruldu ve kosuldu. Ortak tasarim: KOD is akisini yonetir ve karari verir;
model yalnizca semantik yargi (Noul/Score/Choice) uretir. Model hicbir sayi hesaplamaz,
hicbir sayi uretmez — yalnizca mevcut metni siniflandirir.

Toplam maliyet: 1.129 istek, ~1.29M girdi + ~126K cikti token. Muse kotasi HARCANMADI.

| hat | girdi | cikti | dosya |
|---|---|---|---|
| 1. Bulgu triyaji | 100 denetim bulgusu | 11 eyleme donusur madde | triage_findings.py |
| 2. Iddia denetimi | 264 yayin iddiasi | 35 isaretli | audit_claims.py |
| 3. Celiski avi | 91 cumle cifti | 19 belirsiz terim | find_contradictions.py |
| 4. Denetim onceligi | 674 denetlenmemis dosya | 113 yuksek riskli | prioritize_unaudited.py |

---

## HAT 1 — Denetim bulgusu triyaji (100 bulgu)

En degerli cikti: **ajanlarin ciddiyet etiketi guvenilmez.**
- Ajan CRITICAL dedi, triyaj dusurdu: 7 vakanin 6'sinda.
  Bunlardan biri (R2/code F2) koordinatorun ZATEN elle geri cektigi transductive-leakage
  yorumuydu; triyaj bagimsiz olarak REJECT_MISREADS_DESIGN verdi.
- Ajan MED dedi, triyaj yukseltti: 4 vaka. Bunlar 100 bulgu icinde gomulu kalmisti:
  * C1 kapisi FR@3 tabanli (acik -7.23) ama her yerde 7.80 Hit@10 aktarilmis -> YANLIS METRIK
  * Manset tabloda hala handikapli BM25 54.18; adil 65.67 yalniz ekte
  * `sym` "standardized" etiketli ama sigma'ya hic bolmuyor
  * BM25 rakip maliyeti iki farkli serilestirmeyle raporlanmis

Kalibrasyon: 3 altin ornek, 2/3 uyum. YETERSIZ — bu yuzden P5 kutusu otomatik
kapatma icin kullanilmaz kurali konuldu.

## HAT 2 — Yayin iddialarinin denetimi (264 iddia)

Kod once her iddianin sayilarini 1.223 sonuc dosyasinda izledi (yil/kucuk tamsayi
elendi), kanit parcasini iddiaya iliştirdi; model kanitin iddiayi destekleyip
desteklemedigini yargiladi.

Sonuc: R7_OK 229 | R6_NEEDS_HEDGE 13 | R4_OVERGENERALIZED 12 |
R2_EVIDENCE_MISMATCH 8 | R1_REPEATS_WITHDRAWN 1 | R5_UNTRACEABLE 1

**R1 — KOORDINATOR TARAFINDAN DOGRULANDI (gercek bulgu):**
`FINAL_STATE.md:58` — "sign() ... *adds* ~10 pp over the float source (k=384: sym 54.18
vs float 43.69)". Ayni pakette `REPORT.md:25` standartlastirilmis float icin **48.51**
veriyor. Yani referans secimine gore kazanc +10 ya da -2. Duzeltme uyarisi YOK.
Bu, geri cekilmis "sign +10pp" iddiasinin yayin paketinde hala duran ornegi.

R2 grubunun cogu (C1/C3 kapi tanimlari) kanit-uyusmazligi degil: kapi METNI sayi
icermiyor, dolayisiyla sayi izleme bos donuyor. YANLIS POZITIF — hattin bilinen siniri.

## HAT 3 — Terim tutarliligi (91 cift)

C5 tutarli 42 | C4 kucuk belirsizlik 30 | **C2 okuyucu yanilir 18** | C3 nitelik gerekli 1

C2'lerin terim dagilimi: BM25 6, fair 3, qscale 3, 48 B 2, C1 1, sym 1, 12 B 1, ladder 1

**En sert (koordinator dogruladi):**
`EXTERNAL_AUDIT3_RESPONSE.md:118` "C1 survives comfortably on PerLTQA and LoCoMo" —
ama ayni sayfadaki tablo o iki satirda **-6.14 SIG ve -12.18 SIG kayip** gosteriyor.
Oradaki "C1" kapi degil, bir dis denetim elestirisi. Ayni pakette `FINAL_STATE.md:17`
C1'i **FAIL** ilan ediyor. Ayni isim, iki farkli sey, tek pakette.
=> Gercek celiski degil; ama disariya giderse kesin yanlis anlasilir. Nitelik sart.

Ikinci: `sym` teriminin "standardized" olarak etiketlenmesi (DECISION_TESTS.md:82)
ile FINAL_STATE.md:37'deki kullanimi ayni nicelige isaret etmiyor (same_quantity 0.21).

## HAT 4 — Denetlenmemis dosyalar icin oncelik (674 dosya)

Onceki secim regex sayi-aramaydi. Bu hat her dosyanin basini okuyup riskini yargiladi.

A5_SKIP 291 | A4_WORTH_A_LOOK 270 | **A1_HIDDEN_CONTRADICTION 98** |
A3_UNVERIFIED_CLAIMS 13 | A2_FEEDS_PUBLISHED 2

Yuksek riskin klasor dagilimi:
agent_out 28 | drive 14 | pilots 13 | theory_benchmark_test_v1 10 | review_transfer 9 |
verify_top10 6 | math_discovery 6 | residual8_pilot_r1 6 | hr-consolidation 5 | incoming_b 5

**SURPRIZ:** En yuksek riskli dosyalarin cogu `agent_out/` ve `theory_benchmark_test_v1/`
icinde — ikisi de onceki oncelik haritasinda DUSUK oncelikli sayilmisti, cunku yayin
sayilariyla ortusmuyorlardi. Icerikleri okununca farkli cikti: bunlar eski KOORDINATOR
INCELEMELERI ve DEFECT_TABLE.csv gibi kusur listeleri. Yani "yayin sayisi tasimiyor"
olmalari onemsiz olduklari anlamina gelmiyor — tam tersine, kusur kayitlari olabilirler.

En yuksek 6:
  2.85 theory_benchmark_test_v1/locomo/COORDINATOR_REVIEW.md
  2.81 agent_out/f1-audit/decisive_delta_source.py
  2.78 agent_out/axis-budget/coord_audit_check.py
  2.75 hr-consolidation/audit_v52_t4f0_codex_2026_08_31/DEFECT_TABLE.csv
  2.64 agent_out/f1-audit/evidence/gate_and_mutations.json
  2.63 agent_out/coord-baseline/alpha_sections.py

Tam siralama: UNAUDITED_PRIORITY.csv (674 satir)

---

## NE YAPAMAZ (degismedi)

- Sayi hesaplamaz, ispat dogrulamaz, bug bulmaz, DUR/DEVAM karari vermez.
- Bulgu METNINE bakar, kaynak koda bakmaz: "bu bulgu dogru mu?" sorusuna cevap VERMEZ.
- Tipli cikti dogru cikti degildir.

## KALIBRASYON DURUMU — DURUST BEYAN

Hat 1: 3 altin ornek, 2/3. Hat 2: R1 bulgusu elle dogrulandi (1/1).
Hat 3: en sert C2 elle dogrulandi (1/1). Hat 4: kalibrasyon YOK.
**Hicbiri savunulabilir bir esik icin yeterli degil.** Savunulabilir kullanim icin
her hat 100-150 elle etiketlenmis ornek gerektirir. Bu yapilmadi; bu paket bir
ONCELIKLENDIRME araci olarak kullanilabilir, OTOMATIK KARAR araci olarak kullanilamaz.

## YENI DOGRULANMIS DUZELTME MADDELERI (deftere eklenecek)

B6. FINAL_STATE.md:58 — "sign adds ~10 pp over float" referans-bagimli; ayni pakette
    standartlastirilmis float 48.51 (REPORT.md:25). Uyari eklenmeli.
B7. EXTERNAL_AUDIT3_RESPONSE.md:118 — "C1 survives comfortably" cumlesindeki C1,
    FINAL_STATE.md:17'deki FAIL eden C1 kapisi DEGIL. Nitelik sart.
B8. "BM25" terimi tek pakette 4 farkli yapilandirmaya isaret ediyor
    (54.18 / 55.32 / 61.70 / 65.67). Her kullanimda yapilandirma adi yazilmali.

Dosyalar: triage_findings.py, audit_claims.py, find_contradictions.py,
prioritize_unaudited.py + FINDINGS_TRIAGED / CLAIMS_AUDITED / CONTRADICTIONS /
UNAUDITED_PRIORITY (.json/.csv)
