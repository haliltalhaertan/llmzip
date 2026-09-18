[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]

# audit_hard_r2 — IKI AYRI DENETIM TURU (karismasin diye ayrildi)

Bu klasorde 2026-09-17 tarihinde YAPILAN IKI FARKLI tur var. Once ayni
dizine yazildilar, sonra icerik-hash dogrulamasiyla ayrildi (0 fark).

## ROUND_A_10roles_1114/   (280 dosya)  — 10 rol, saat ~11:14-11:40
Konu odakli teknik turlar. Her rolde REPORT.md:
01_metrics 02_itq 03_geometry 04_retrieval 05_f1 06_dense_residual
07_kv_inverse 08_storage_contracts 09_portability 10_governance_meta
Koordinator: BATCH1/BATCH2_COORDINATOR_REVIEW.md, CONSOLIDATED_AUDIT.md
Degismezlik: SOURCE_SHA256_BEFORE.json (879 dosya)
NOT: bu turda koordinator yanlislikla decision_tests.py'ye dokundu, geri
alindi; ayrinti BATCH2_COORDINATOR_REVIEW.md "source-change incident".

## ROUND_B_8roles_1318/    (75 dosya)  — 8 rol, saat ~13:18-16:20
"1. turun kacirdigini bul" turu. Roller ve raporlari:
meta/META_AUDIT.md          denetcileri denetle
decision/DECISION_AUDIT.md  DUR karari
stats/STATS_AUDIT.md        istatistik gecerlilik
code/CODE_AUDIT.md          cekirdek kod bug avi  <-- ana bulgu
data/DATA_AUDIT.md          veri/altin etiket
bytes/BYTES_AUDIT.md        bayt butcesi
coverage/COVERAGE_AUDIT.md  denetlenmemis koseler
novelty/NOVELTY_AUDIT.md    yenilik/onceki-sanat
Koordinator dogrulamasi: TRANSDUCTIVE_FINDING_VERIFIED.md
Ham kanit: code/INDUCTIVE_ALL10.json + .log + t_inductive_all10.py
Degismezlik: SOURCE_SHA256_R2_BEFORE.json (2205 dosya)

## Onceki tur (ayri klasor)
audit_hard_r1/  — 4 rol (numbers/integrity/claims/repro), 2026-09-16/17
