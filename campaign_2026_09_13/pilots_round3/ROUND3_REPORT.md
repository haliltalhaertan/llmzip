# ROUND-3 RAPORU — Deney 1–5 (öğrenilmiş seçim, tie-mekanizması, transfer, adaptif öngörücü)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Tarih: 2026-09-13 · Ekip: yerel harness (Windows venv) + 2 bağımsız Muse oturumu koşu takımı
(D1V doğrulama, D5 denetim) + 4 analiz oturumu (D2/D3/D4/c2). Hiçbir şey repo'ya yazılmadı/push edilmedi.

## 0. Yönetici özeti

| Deney | Soru | Hüküm |
|---|---|---|
| **1** (Design-1) | "Öğrenilmiş bit seçimi gerçek bir prim mi?" | **KILL** — 3/3 ön-kayıtlı tetikleyici ateşledi; prim split/seed şansıydı |
| **2** (c1) | "Tie-özellikleri flip yönünü taşıyor mu?" | **GEÇTİ** (mekanizma) — AUC 0.798 vs mean-model 0.686; gold-informed, deployable değil (F1) |
| **3** (e1) | "Utility'ler benchmark'lar arası taşınır mı?" | **BENCHMARK-YEREL** — Spearman ~0.1; transfer ≈ şans (C5) |
| **4** | "Karışım sıralaması taze çekilişlerde dayanır mı?" | **DAYANIYOR (confirmatory, n=2)** — taze seed'lerde tam katı ayrım (C6) |
| **5** (c2) | "Gold-free öngörücü + adaptif yönlendirme kazandırır mı?" | **KAPANDI — şu an prereg'e hazır değil** (m3: resmi vs-random'da LME α=0.20 gürültü, LoCoMo boş; m2: gold-free öncül 0/10) |

Doğrulama: **D1V = 24/25 EXACT, 0 DIFF** (Deney 1 sayıları ham artefaktlardan rakamı rakamına).
Tasarım denetimi (D5) **TAMAMLANDI** — F1–F3 + C1–C9 disposition edildi (banner'lar + ERRATA);
kill, örtüşme-düzeltmeli belirsizlik altında da sağlam (CI [−2.00, −0.41]pp).

## 1. Deney 1 — Öğrenilmiş seçim priminin sağlamlaştırması → KILL

Tam detay: `DENEY1_REPORT.md` (+ `RUN_LOG.md`). Özet: 10 tabakalı split × 10 taze seed; birincil
ölçüt vs-en-iyi-seed. LME drop64 **−1.25pp (2/10)**, alone64 −3.15pp (0/10); LoCoMo drop64
**−0.15pp (2/10)**. Üç kill tetikleyicisi de ateşledi → öğrenilmiş kol (b) yarışından çıkarıldı
(ön-kayıtlı gating kuralı). İkincil ölçütte (vs-mean) LoCoMo'da +1.11pp (10/10) — max-of-10
yukarı-sapması hesaba katılınca prim yok. R2B'nin +1.62pp'i seed-şansıydı; R2D uyarısı doğrulandı.
Yan bulgu: onarılmış SPREAD64 — **iki-bar tablosu** (C2/C3 düzeltmesi):

| Kol | vs-best (birincil) | vs-mean (ikincil) |
|---|---|---|
| drop64 | −1.25pp, 2/10 | +0.43pp, 7/10 (nominal) |
| alone64 | −3.15pp, 0/10 | −1.47pp, 3/10 |
| SPREAD64 | −0.50pp, 3/10 | +1.17pp, 9/10 (nominal) |

SPREAD "random-panelle eşdeğer"dir çünkü **fixed-vs-max yapısal dezavantajı**: tek sabit kol,
10-çekilişli maksimumu sistematik geçemez; vs-mean'de ise ayrışır (LME). Bar seçimi iki kolu da
aynı tabloda göstermeli — "iyi bilinen kol" ifadesi yalnız vs-mean için geçerli.
**Kill belirsizliği (C1):** per-split gap SD=1.35pp; split-bazlı bootstrap %95 CI **[−2.00, −0.41]pp**;
test-yarısı ortalama Jaccard 0.329; P(ortalama>+1.0pp)=0.0000 → **kill örtüşme-düzeltmeli
belirsizlik altında da sağlam**. İkincil win-rate'ler "nominal, korelasyon-indirimsiz" okunmalı.

## 2. Deney 2 (c1) — Tie-mass ayrıştırması: mekanizma cevabı

Tam detay: `muse_sessions/d2/`. Kapılar diff 0.0 (native, TOP48, RAND48_s0, BOT48 birebir).
Held-out AUC: **T=0.798** / M=0.686 / T∪M=0.806 → ön-kayıtlı eşikler (≥0.65, Δ≥0.05) geçti.
Öz: kazanan sorularda "gold'dan kesinlikle daha yakın belge" **0.55**, kaybedenlerde **5.51**;
tie-mass 1.87 vs 4.50 — oysa ortalama-mesafe istatistikleri özdeş (23.918 vs 23.905).
**Top-variance çöküşü = tie-rekabeti çöküşü; ortalama-mesafe hikâyesi değil.** gold_bucket_size≡1
→ duplicate-code çöküşü gold düzeyinde yok. Dürüstlük: tek benchmark, tek learner, n=130.
**F1 düzeltmesi (D5):** T/M özellikleri (margin ve top20_entropy hariç) **çıkarımda gold qrels
gerektirir** → bu bir MEKANİZMA sonucudur, dağıtılabilir öngörücü DEĞİL; hüküm "roadmap
kill-bar'ını geçti; tie hikâyesi c2 keşfine terfi etti" olarak okunmalı. (c2'nin gold-free
COMBO'su 0.686/0.558 zaten bunu göstermiştir.)

## 3. Deney 3 (e1) — Cross-benchmark utility transfer

Tam detay: `muse_sessions/d3/`. Kapılar diff 0.0. Yapı: Spearman drop +0.097 / alone +0.075
(şans düzeyi; top-k kesişimleri de şans). Tek "taşınan" var (rho 0.9999) ama o gömme profili
sabiti, görev sinyali değil (var-kolu zaten her iki tarafta kötü). Transfer: **drop 48/64'te iki
yönde FAV** (kendi utility'sinden 1-2pp aşağıda, random-mean üstünde); **alone çoğunlukla FAIL**;
var hücreleri vacuous. **Lisanslı sonuç (C5):** utility'ler benchmark-yerel; **transfer ≈ şans**;
var-satırı FAV **tautolojik** (src==own inşaat gereği). Sonuç: sinyal taşıyan eksenler esasen
benchmark-yerel; taşınabilir varsayılan = spread/random (roadmap kararını destekler).

## 4. Deney 4 — Fresh-Q karışım doğrulaması

Tam detay: `muse_sessions/d4/`. Kapılar diff 0.0; orijinal seed'ler birebir yeniden türetildi.
Taze seed'lerle (43004/43005) tam katı ayrım korundu: LoCoMo min(K)=0.22966 > max(R)=0.21848 >
max(A)=0.20732; LME min(K)=0.53832 > max(R)=0.52149 > max(A)=0.49287 (orijinal LME'de zayıflayan
sıralama taze çekilişlerde daha temiz). **C6 düzeltmesi:** dil **confirmatory-only (n=2)**;
seed-numeral çakışması işaretli (43004/05: LoCoMo için taze, LME'de gate-seed numaraları; LME
taze seti 44001/44002); tam-5 LME kontrastı bilinen (katı ayrım 5'te zayıf, taze 44001/02'de
sağlam). R2D'nin pairing/eksen-atama konfoundu hâlâ açık; n=2.

## 5. Deney 5 (c2) — Gold-free öngörücü → adaptif bütçe yönlendirme

Tam detay: `muse_sessions/c2/`. Kapılar geçti; fail taban oranları LME %24.9 / LoCoMo %15.7.
Öngörücü AUC: LME 0.686 (en iyi tekil boundary_share 0.696); **LoCoMo 0.558 ≈ şans**.
Yönlendirme @α=0.20: LME **+3.09pp** (random-abstain +1.83 [0.98–2.22] → model random'ın
üstünde); LoCoMo +1.48pp (random +1.13 [0.55–2.13] → band içinde). Oracle tavanlar +10.0/+8.9pp —
boşluk var ama LoCoMo'da gold-free özellikler yakalayamıyor (muhtemel neden: LoCoMo'da
varyans/N özellikleri arşiv-sabiti, per-soru geometri zayıf).
**Disposition (F2 düzeltmesiyle):** ön-kayıtlı kapı harfiyen ateşledi **ama LoCoMo ayağı
random-abstention karşısında BOŞ** (random tek başına +1.135pp geçiyor; COMBO AUC 0.558 ≈ şans) →
"PROMOTE" **KOŞULLU**dur: herhangi bir prereg takip deneyi **bağlayıcı vs-random üstünlük kapısı**
(model gain > random-range max @α=0.20) taşımalı; **LoCoMo "replikasyon" SAYILMAZ**. LME ayağı
random'ı geçiyor (umut verici), ama prereg öncesi **LARGE-free ablation + gain CI + resmi
vs-random testi** zorunlu (C7). (Roadmap'in "iyi AUC, ucuz adaptif kazanç yok" beklentisinin
karışık hali.)

**NİHAİ ÇÖZÜM (m2+m3, aynı gün akşam):** C7'nin üç şartı koşuldu. m3: resmi 200-çekiliş testi
Bonferroni'yle **LME α=0.20'yi gürültü içine aldı** (p_bonf 0.18 — ilk okuma 10-çekiliş
yanılsamasıydı); LoCoMo dört α'da da boş. m2: mekanizma çok-split'te sağlam (T 10/10, AUC 0.821)
ama **tam-gold-free model 0/10 split'te ≥0.65** → öncül yok. **Sonuç: c2 şu an prereg'e HAZIR
DEĞİL; adaptif hat kapandı.** Gelecek bir deneme için bağlayıcı kapı: gain@0.20 > 200+ çekilişin
maksimumu (LARGE-free, per-benchmark). Detay: `missing_analyses/{m2_d2multi,m3_c2ablation}/`.

## 6. Doğrulama ve denetim durumu

- **D1V (bağımsız yeniden-hesap):** 24/25 EXACT, 0 DIFF; kill tetikleyicileri rakamı rakamına.
  F3 düzeltmesi: 2 "cannot-check" gözden kaçırmaydı → **yeniden koşuldu ve kapandı**
  (`muse_sessions/d5/f3_rechecks.txt`): LoCoMo 10/10 split sayı+bakiye ✓; 5 sıfır-olmayan-FR
  test sorusu EXACT ✓; delta64 kolonları EXACT ✓; `sha256sum -c HASHES_ROUND3.txt` **6/6 OK** ✓.
- **D5 tasarım denetimi: TAMAMLANDI** (`muse_sessions/d5/d5_review.md`): sayılar her yerde
  rakamı rakamına doğrulandı; 3 FAIL (F1/F2/F3) + 9 CAVEAT (C1–C9) — hepsi disposition edildi
  (`muse_sessions/ERRATA_ROUND3_D5.md` + oturum raporlarındaki banner'lar).
- **D5'in "sıradaki 3 analiz" listesi** (prereg öncesi zorunlu adaylar):
  1) kill OR-kuralının null-simülasyonu (selection-lift yanlılığı); 2) c2 LARGE-free ablation +
  gain CI + resmi vs-random testi; 3) D2 çok-split + tam-gold-free tie-modeli AUC.
- D2/D3/D4/c2 iç kapıları: native anchor'lar diff 0.0 (her oturumda).
- **D5'in 3 eksik analizi TAMAMLANDI** (`missing_analyses/{m1_kill_null,m2_d2multi,m3_c2ablation}/`):
  m1 → kill kuralı geçerli prim-dedektörü, drop64 null'un 57./89. yüzdeliğinde ("prim yok" bölgesi);
  m2 → tie-mekanizması 10/10 split'te sağlam (AUC 0.821) ama gold-free G 0/10 ≥0.65;
  m3 → resmi vs-random: LME α=0.20 gürültü içinde (p_bonf 0.18), LoCoMo dört α'da boş →
  **c2 prereg'e hazır değil; adaptif hat kapandı.**

## 7. Dosyalar

- `DENEY1_REPORT.md`, `RUN_LOG.md`, `ROUND3_REPORT.md` (bu dosya), `HASHES_ROUND3.txt`
  (script+artefakt SHA-256'ları), `deney1_lme_details.json` (831KB),
  `deney1_loco_details.json` (1.8MB), `deney1_loco_peraxis.npz` — bu dizinde.
- `muse_sessions/{d1v,d2,d3,d4,c2,d5}/` — oturum raporları + JSON'lar + scriptler;
  `muse_sessions/ERRATA_ROUND3_D5.md` (tüm düzeltmelerin kaydı);
  `muse_sessions/d5/f3_rechecks.txt` (+ üretici `harness/f3_rechecks.py`).
- Promptlar: `muse_prompt_{deney2_tiemass,deney4_freshq,deney5_c2,d1v_verify,d3_transfer,d5_review}.md`
  (llmzip-work kökünde).
