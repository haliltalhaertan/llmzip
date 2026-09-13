# prereg_race_2026-09-13 — (b) 12-byte yarışı: taslak + dört bağımsız inceleme oturumu

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[LOCAL] [NOT PUSHED] Bu klasör, (b) 12-byte bütçe yarışı preregistration'ının hazırlık
malzemelerini toplar. Hiçbir şey mühürlenmedi, hiçbir şey koşulmadı.

## İçerik

- `DRAFT_v1.md` — ilk taslak (2026-09-13 sabah). Aynısı: `../DRAFT_PREREG_TWELVE_BYTE_RACE.md`
- `DRAFT_v2.md` — dört oturumun bulguları işlenmiş revizyon. Aynısı:
  `../DRAFT_PREREG_TWELVE_BYTE_RACE_v2.md`
- `pre1/` — **PRE1 sert eleştiri**: "NOT SEALABLE — 8 FAIL/8 CAVEAT/5 NOTE"; canlı faiss
  probe'ları (RQ96=20B, RQ32=12B, PQ=12B, PQ train küçük-N hatası, LME N istatistikleri);
  S1–S10 smoke listesi; "sağlam, dokunma" listesi.
- `pre2/` — **PRE2 beyin fırtınası**: C1–C12 değişiklik tablosu (10-seed, çift-bar, TOP negatif
  kontrol, recall-vs-bytes enstrümanı...), "sakın ekleme" listesi, değerlendirme semantiği
  reçetesi, seal öncesi 10 maddelik checklist.
- `math1/` — **MATH-1 model**: koşullu-tek-biçimli tie modeli tüm panelleri birebir yeniden
  üretiyor (r≥0.9968; TOP48 çöküşü −12.11 vs −12.34pp; bağımsızlık varsayımı işaret+seviye
  yanlış; duplicate-spike aracılığı). Scriptler: math1.py + math1b/c/d + part*.py.
- `math2/` — **MATH-2 teori çerçevesi**: T1–T7 tablosu; S1–S5 adayları; öneri S4+S2;
  "erişilemez" listesi (JL sınırları uygulanamaz uyarısı dahil).

## Bekleyen iki HR kararı (v2 §8.12)

1. **A4 32-dim kuralı:** spread-32 öneriliyor — HR karar dokümanındaki isim `TOP32_RABITQ32`
   (pilotlara göre anti-optimal). Sapma; HR onayı/resolution bekliyor.
2. **Sayısal kill/promote çizgileri:** seal öncesi kalibrasyon defteri (m1 simülasyonunun tam
   rakip setine genişletilmesi) sayıları literal olarak donduracak.

## Sıra

HR incelemesi → iki karar → kalibrasyon defteri + S1–S10 smoke'ları → HR imzası → seal → koşu.
