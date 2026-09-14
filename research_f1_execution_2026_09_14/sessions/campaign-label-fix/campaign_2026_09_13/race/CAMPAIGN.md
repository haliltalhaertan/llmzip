[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# RACE CAMPAIGN TRAcker — (b) twelve-byte budget race (2026-09-13, LOCAL ONLY)

[LOCAL] [NO PUSH] [NOTHING RUNS UNTIL SEAL] Kullanıcı talimatı: "bana bir şey sorma — muse ile
karar al ve yürüt." Kararlar Muse oturumlarıyla alınıyor; orkestratör yürütüyor.

## Dalga 1 (koşuyor)
- **RB1 — ✅ BİTTİ (2026-09-13 13:03).** Kararlar + kalibrasyon:
  - **D1 (RaBitQ eksen kuralı): spread-32 birincil / random-32 ikincil / TOP32 yalnız eğri-noktası.**
    Taze sayılarla: TOP32 farkları −13.24pp (LME) / −4.66pp (LoCoMo) vs best-of-10 RANDOM32;
    SPREAD32 −1.73/−0.79pp (seed gürültüsü içinde). HR-adı sapması kayıtlı.
  - **D2 (kalibrasyon): K=40/41 rakip look'lu tam null: LME ort −3.14 sd 1.60; LoCoMo −1.82 sd 0.93.**
    **Kill çizgileri: LME −6.4pp / LoCoMo −3.7pp** (null %2.5 dışa yuvarlı). **Promote: +2.0pp**
    (97.5. yüzdeliği >2pp aşıyor). Gereken gerçek prim: +3.1/+1.8pp (80% güç: +4.4/+2.6).
    Bağımsızlık modeli doğrulandı (K=9'da empirikle ~0.1pp); eş-korelasyon reddedildi (satırları
    yarıya çekiyordu). 16-hücre tablosu + Bonferroni + bit-identik rerun ✓.
  - Artefaktlar: `race_2026-09-13/rb1/` (memo + notebook + calib.py + literaller).
- **CERT — ✅ BİTTİ (2026-09-13 13:05).** Kayıpsızlık sertifikasyonu:
  - Karar: "kayıpsız" = **sonlu-örneklem kalite-denkliği sertifikaları** (bit-birebir ve evrensel
    imkânsızlık kanıtlanamaz — üç katmanlı gerekçe raporda).
  - **Sertifika tablosu (≥95% tek taraflı; parantezde Bonferroni aile-geçerli):** LME 10B ≤3.3/4.3pp
    (SPREAD), 8B ≤6.1/7.4 (BOT), 6B ≤10.8/12.0 (RANDavg); LoCoMo 10B ≤0.95/1.55 (BOT), 8B ≤3.0/3.7
    (BOT), 6B ≤6.8/7.7 (BOT). **ε=0 hiçbir basamakta sertifikalanamaz.**
  - Bonus: en iyi aile benchmark-yerel (LoCoMo her yerde BOT); **80/64-bit LME kolları float96'yı
    sertifikalı geçiyor (+5.2/+2.8pp); 48-bit geçemiyor.**
  - **Lemma (ispat parçalı):** P(C) sınıfında E[FR] ≤ R_free + (k/C)·R_spike — (a) retrievable-mass
    sınırları + (b) f(S,T) monotonluğu İSPATLANDI; P(C) öncülü konjektür (ampirik). Lean şekli ~50
    satır ℕ/ℚ, analiz aksiyomu yok.
  - Artefaktlar: `race_2026-09-13/cert/` (rapor + details + cert_compute.py).
- **RB3 — ✅ BİTTİ (2026-09-13 13:07).** FAISS-runner + tüm smoke'lar PASS (S1-S7, 58s).
  - **Sonuç (FR@3): SIGN native 0.5420/0.2365 — tüm üçüncü-parti kollar kaybediyor:**
    A4 spread-32: 0.294–0.312 / 0.087–0.095 · A4 random-32: 0.281–0.302 / 0.080–0.100 ·
    A5 wrapper: 0.338 / 0.084 (tek seed'siz çekiliş — descriptif) · **A6 PQ: 0.431 / 0.154**
    (SIGN +11.1pp / +8.3pp). Kalibreli null'a göre kayıplar kesin (decisive).
  - Byte replay PASS (RQ96=20B, RQ32=12B, PQ=12B, EXT2=44B); PQ maske hiç ateşlenmedi (LoCoMo
    min-N=369 dahil); determinizm bit-identik (in-process + cross-process); rotasyon-zinciri 8/8
    (IndexRaBitQ seed'siz-deterministik; wrapper `X@A.T` konvansiyonu tanılandı).
  - Artefaktlar: `race_2026-09-13/rb3/` (runner 973 satır + details + smokes + env + manifest).
- **RB2 — ✅ BİTTİ (2026-09-13 13:09).** SIGN-runner + smoke'lar PASS (S1 tamper-abort fired,
  S6 tie determinizmi, S8 kırık-inşaat assert'i tripped, S10 hardcode 0, S9-lite manifest;
  1410+30 eff_k assert). ✳ Ön tablo (FR@3; 41 kol/benchmark, per-q + model sütunu JSON'da):
  - **LME:** NATIVE .54198 · en iyi 10B: SPREAD80 .52526 / RAND80 en iyi .52445 · en iyi 8B:
    RAND64_s4 .51787 · 6B: RAND48 .4328–.4592 · TOP-kontroller: TOP48 .34949 (−9.70pp vs
    random-mean), TOP64 −5.89pp ✓
  - **LoCoMo:** NATIVE .23655 · **BOT80 .23546 (−0.11pp — fiilen parite!)** · BOT64 .21718 ·
    BOT48 .18112 · TOP48 .13183 (−2.78pp vs random-mean; 5pp marj tutmadı ama TOP kazanmadı →
    validity OK)
  - Model sütunu: r 0.9968–0.9996 (MATH-1 zarfı). Tanım-mutabakatları çözüldü (R2C stride-2 ≠
    onarılmış rank-linspace — LoCoMo SPREAD değerleri farklı, disclose; r2a stable-argsort eşleşti;
    ulp 1.1e-16 bilgilendirici). Bootstrap, analiz aşamasına devredildi (literaller kayıtlı).
  - Artefaktlar: `race_2026-09-13/rb2/` (race_sign.py + 2MB details + smoke log + manifest).

## DALGA 1 TAMAMLANDI (RB1+RB2+RB3+CERT ✅). Ön yarış tablosu:

| Kol | LME | LoCoMo |
|---|---|---|
| **NATIVE SIGN96** | **.54198** | **.23655** |
| En iyi 10B (SPREAD80 / BOT80) | .52526 (−1.67pp) | .23546 (−0.11pp) |
| PQ 12B | .43075 (−11.1pp) | .15368 (−8.3pp) |
| RaBitQ32 (en iyi rot.) | .31167 (−23.0pp) | .09550 (−14.1pp) |

**Preliminer disposition (literal kurallara göre):** kill YOK (hiçbir kol SIGN'ı ≥2pp geçmedi;
tersine hepsi geride). LME +1.67pp = "moderate"; LoCoMo +0.11pp = "parity" — promote çizgisi
+2.0'ın altında; resmi hüküm mühürlü koşu + resmi analizden gelecek.

## Dalga 2 — ✅ TAMAMLANDI (2026-09-13 ~13:25)
- **Mühür:** ✅ `PRE_RUN_SEAL_local.json` (13:10; runner hash'leri + literaller + kalibrasyon).
- **Resmi koşu:** ✅ 13:12–13:14 (RB2+RB3 exit 0). RB2 sayısal içerik bit-identik; RB3: son-ulp
  + zaman damgası + oturum-annotasyonu (hepsi kanıtlı). Kanıt: `official_run/OFFICIAL_RUN.md`.
- **RACE-V:** ✅ **26/26 EXACT, sıfır fark — resmi sayılar bağımsız doğrulandı.**
  (`racev/racev_report.md`: anchors 0.0; 12/12 FR spot 0.0; PQ retrain bit-identik; W/T/L 16/16.)
- **Resmi analiz:** ✅ bootstrap (B=5000; 94301/94302; argmax yeniden-seçimli) + 16-hücre:
  - LME: **+1.6716pp** vs SPREAD80, CI95 [−0.596, +2.122] → **MID**
  - LoCoMo: **+0.1086pp** vs BOT80, CI95 [−0.911, +1.019] (küme CI [−1.173, +1.149]) → **MID**
  - **HÜKÜM: HOLD-parity** (kill yok, promote yok; SIGN12B tahtını koruyor). Parite bile null'ın
    97.5'lik olayı; premium ihtiyacı ≈+3.1/+1.8pp (elde edilmedi).
- **Rapor:** ✅ `RACE_REPORT.md` + `analysis/ANALYSIS.md` + `analysis/analysis.py`.
- Kalan: ED4 aktarım paketi (yarış kaynakları + RACE-V + analiz) — sıradaki iş.

## BENCH-3 KAMPANYASI (kullanıcı talebi: "başka benchmarklar da kullanalım") — BAŞLATILDI
- **Amaç:** genelleme kanıtı — LME+LoCoMo'nun ötesine, farklı yapı ve dünyaya iki yeni benchmark.
- **Veriler indirildi:** `bench3/REALTALK/` (10 gerçek mesajlaşma sohbeti; 728 QA, mesaj-seviyesi
  evidence `dia_id`, kategori 1-3; repo lisansı YOK — not edilecek) ve `bench3/PerLTQA/`
  (en_v2: 32 karakter, 1905 QA, reference-memory eşleme; CC BY-NC 4.0).
- **B3A (REALTALK):** frozen hattın portu + **port-sadakati kapısı** (önce LME C96 bit-birebir
  üretim ispatı) → sonra sign96 vs float96, merdiven 80/64/48, tie teşhisi, kategori profili.
- **B3B (PerLTQA):** aynı kapı + banka itemizasyonu (profile/social/events/dialogues) +
  reference-memory eşleme; yapısal genelleme testi.
- Kaideler: read-only /mnt/c, sadece /tmp yazım, ağ yok, [LOCAL EXPLORATORY PILOT] etiketleri;
  race/prereg dosyalarına temas yok.
- Oturumlar: **B3A ✅ TAMAMLANDI (REALTALK, 13:48)** + B3B 🔄 koşuyor (PerLTQA).

### B3A SONUÇ — REALTALK portu TAMAM ✅
- **Port-sadakati kapısı: PASS 5/5** (C max|d| ≤2.3e-12, sign %100; qC aynı; gold eşit) — frozen
  producer `buildrep` doğrudan import edildi (sha256 `8dce37b1…` eşleşti); reimplementation yok.
- **Manşet: sign96 − float96 = +5.2241pp** (n=705/728; LME +10.04, LoCoMo +12.0 verili).
  W/T/L 104/558/43; %79.15 tam-eşit — "yoğunlaşma imzası" tekrarladı.
- Merdiven monoton (80>64>48 her ailede); maliyetler: 80 −0.99…−2.61pp, 64 −2.72…−4.93pp,
  48 −5.98…−6.45pp.
- **DIFF'ler:** (a) delta büyüklüğü LME'nin yarısı; (b) **BOT en iyi merdiven kolu** (80+64'te;
  LME'de BOT<RAND idi) — güçlü fark; (c) SPREAD≈RAND her genişlikte, TOP cezası 80/64'te var,
  48'de yok; (d) brief "tarih ekle" dedi ama frozen kod tarihsiz → kod esas alındı, no-date
  kullanıldı; (e) 23/728 (%3.16) çözülemez QA dışlandı (frozen denominator kuralı);
  (f) RT08: float=0.0 vs native 0.0474; (g) sign, RT03/RT04'te float'a kaybediyor — delta üniform değil.
- Determinizm: verbatim rerun **bit-identik** (details `8bae1d38…`, summary `8e725fca…`); 3/3
  independent spot-check exact; RT05 repr rebuild ~1.4e-13 (BLAS, sign-stabil).
- Kanıt: `bench3/runs/b3a_realtalk/` (report.md 202 satır, details.json 728×41 kol, port_gate.json,
  rt_repr/RT01-10.pkl, adapter+runner+port, det hash'ler). **Bağımsız doğrulamam:** tüm başlık
  sayıları ham per-QA satırlarından birebir (n/FR/W-T-L/kategori/RT08) + sha256 eşleşmesi.
- Sonraki: B3B bitince LME/LoCoMo karşılaştırma tablosu; gerekirse B3-V bağımsız doğrulama; ED4 adayı.

### B3B SONUÇ — PerLTQA negatif sonuç DOĞRULANDI ⚠️ (14:12, B3B-FIN)
- **Kurtarma:** /tmp/b3b → `bench3/runs/b3b_perltqa/` (results.json 8265 QA, port_gate PASS,
  cache'ler, step0-2 scriptleri, resolution/exclusions).
- **Ham başlık (doğrulama koşuyor): sign96 0.48894 vs float96 0.55169 → −6.28pp — TERS!**
  (LME +10.0 / LoCoMo +12.0 / REALTALK +5.2 idi.) Bölüm kırılımı: profile +20.4pp (sign kazanıyor),
  social −0.8, events −12.4 (n=4346), dialogues −1.5. Tie %29.2.
- **Birim mutabakatı (koordinatör sayımı):** genişletilmiş 8593 QA (357/897/4501/2838); çözülen 8305;
  ölçülen 8265 (Chen Zhi −40). Brief'teki "1905" üst-düzey anahtar sayım hatasıydı (koordinatör hatası).
  32→30 arşiv: Chen Zhi (döküldü) + "dragon beautiful" (bank yok). Arşiv N: 293–546 (medyan 407) —
  küçük-arşiv açıklaması geçerli değil.
- **B3B-FIN ✅ (14:12):** rerun bit-identik (sha `ec9b8b2c…`, koordinatör teyitli), 5-QA spot ≤5.6e-17,
  kod-kanıtı, tie-shift −6.256pp → **−6.275pp GERÇEK (bug değil)**. Birimler ✅ 8593→8305→8265;
  32→31→30 arşiv ("dragon beautiful" nobank; Chen Zhi N=35 döküldü). Konvansiyon: as-run = deney1
  split-0 verbatim. Yapı: 29/30 karakter negatif; events −12.41pp baskın, profile +20.44pp karşı-kazanç;
  gold=1'lerde −8.2pp; tie %29.2. Rapor: `bench3/runs/b3b_fin/`, ham: `bench3/runs/b3b_perltqa/`.

### AUDIT-1 SONUÇ ✅ (14:05) — tie-robustluk + provenans
- **Rekonstrüksiyon resmi per-q dizileriyle bit-birebir** (mc-20 diff 0.0; model diff 0.0/5.6e-17).
- **Yarış hükümleri pesimist tie'da da ayakta:** LME SIGN−SPREAD80 +1.369/+1.717/+2.188pp (pess/exp/opt),
  LoCoMo SIGN−BOT80 +0.089/+0.131/+0.193pp; farklar monotone pess<exp<opt → kural sonuçları taşımıyor;
  hepsi MID bölgesi. Task D: tüm çapalar dosya+satır izli (untraceable yok).
- Rapor: `audit_2026-09-13/audit1_cont/` (report.md + audit1_details_final.json + per-q JSON'lar).

## Sabit literaller (RB1 onaylıyor/değiştiriyor)
- Paneller: `93000+10*width_idx+j` (j=0..9; 0:48b,1:64b,2:80b) · RaBitQ rotasyon: [94101-3] ·
  random-32: [94201-3] · Bootstrap: B=5000, seed 94301.

## Kırmızı çizgiler
- Push yok; /mnt/c'ye oturumlar yazmaz (orkestratör kopyalar); ücretli API yok; A3 (öğrenilmiş
  kol) koşuya girmez; 4F1/BEAM'e temas yok.
