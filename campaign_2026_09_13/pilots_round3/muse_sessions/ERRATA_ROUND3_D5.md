# ERRATA — Round-3, D5 adversarial review sonrası (2026-09-13)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[ORCHESTRATOR ERRATA] D5 bulgularının disposition'u + uygulanan düzeltmeler + F3 recheck sonuçları.
D5 tam metni: `d5_review.md`. Bu dosya, hangi bulgunun nasıl karşılandığının kaydıdır.

## FAIL bulguları ve disposition

### F1 — D2 "provisional predictor claim" altında gold-bağımlılığı gizliyor
**Doğru:** T'nin 3 özelliğinden 2'si (+M'nin 3'ü) gold qrels gerektiriyor (dmin/dg üzerinden);
yalnız `margin` ve `top20_entropy` gold-free. Dolayısıyla T AUC=0.798 **dağıtılabilir (deployable)
bir öngörücü** kanıtı DEĞİL — mekanizma kanıtıdır. c2'nin gold-free COMBO'su (0.686/0.558) zaten
bunu göstermiştir.
**Düzeltme:** D2 raporuna banner (gold-bağımlılık açıklaması); hüküm "roadmap kill-bar'ını geçti;
tie hikâyesi c2 keşfine terfi etti" olarak yumuşatıldı. "Licenses c2" = yalnızca *keşif lisansı*.

### F2 — c2'nin LoCoMo ayağı boş; "PROMOTE" harfiyen ateşliyor ama özde başarısız
**Doğru:** LoCoMo'da random-abstention tek başına +1.135pp @α=0.20 (leg eşiği +0.5pp) — yani
kimliksiz bir "model" bile o bacağı geçerdi; COMBO AUC 0.558 ≈ şans. "≥+0.5pp same sign" eşiği
oturum-düzeyi operasyonalizasyondu ve **kendi null'unun altında** kaldı.
**Düzeltme:** D2/c2 raporlarına banner; hüküm: "gate harfiyen ateşledi; PROMOTE **koşullu** —
yeni bir prereg zorunlu vs-random üstünlük kapısı taşımalı; LoCoMo replikasyon SAYILMAZ."

### F3 — D1V'in 6 "cannot-check"inden 2'si gözden kaçırma, sınır değil
**Doğru:** (i) LoCoMo split kuralı harness'ta tam tanımlı — üyelik re-türetilebilir; (ii)
`r2c_replicate.py` `round2/session_scripts/` altında MEVCUT.
**Düzeltme + RECHECK sonuçları** (`f3_rechecks.txt`):
- B1: 10/10 split sayısı stored ile birebir (767); bakiye yapısal {1:141,2:160,3:46,4:420}.
- B2: s=0 test'inden **sıfır-olmayan FR'li 5 soru** bağımsız yeniden hesaplandı → 5/5 **EXACT**
  (0.5/1.0/1.0/1.0/1.0); üyelik hizalaması doğrulandı. (Bilgi: test FR'lerinin 561/767'si sıfır.)
- C: LME delta64 kolon seti s=0 → **recomputed==stored (64/64)**.
- D: `sha256sum -c HASHES_ROUND3.txt` → **6/6 OK** (doğru kökten; ilk deneme yol hatasıydı).
- LoCoMo bootstrap CI seed yolu (778000+s) yeniden koşulmadı — "not checked" olarak etiketli,
  kill tetikleyicisine girmediği için düşük risk.

## CAVEAT bulguları ve disposition

- **C1 (kill belirsizliği):** Hesaplandı — LME per-split gap SD=1.35pp; naive SE=0.43pp;
  **split-bazlı bootstrap %95 CI: [−2.00, −0.41]pp**; P(ortalama > +1.0pp)=0.0000 (10K resample).
  Test-yarısı ortalama Jaccard=0.329 (rastgele yarımlar için beklenen ~0.33 — örtüşme "aşırı"
  değil ama split'ler bağımsız da değil; CI bunu yansıtır). → **Kill, örtüşme-düzeltmeli
  belirsizlik altında da sağlam** (CI üst ucu +1.0'ın altında). LoCoMo leg: nokta tahmini −0.15
  (≤0 ateşler) ama SD=0.86 → kendi başına marjinal; kill OR-kuralı zaten LME ayağından ateşli.
  İkincil vs-mean win-rate'ler artık "nominal, korelasyon-indirimsiz" dilinde (7/10 p≈0.17).
- **C2/C3 (bar asimetrisi / SPREAD çerçevesi):** ROUND3_REPORT §1'e iki-bar tablosu eklendi;
  SPREAD için "vs-mean'de ayrışır, vs-best'te ayrışmaz; fixed-vs-max yapısal dezavantaj" ifadesi.
- **C5 (D3 sonuç dili):** Lisanslı sonuç açıkça yazıldı: "utility'ler benchmark-yerel;
  transfer ≈ şans; var-satırı FAV tautolojik (src==own inşaat gereği)". d3 raporuna banner.
- **C6 (D4 n=2 + seed çakışması + subsetting):** d4 raporuna banner: "confirmatory-only (n=2)";
  seed-numeral çakışması işaretlendi (43004/05: LoCoMo için taze, LME için GATE seed'leri —
  LME taze seti 44001/44002); LME orijinal kontrastta 5-seed full'e dair bilinen: katı ayrım
  5'te de zayıf, taze 44001/02'de sağlam.
- **C7 (c2 eksikleri):** LARGE-free ablation + gain CI + formal vs-random test → **prereg öncesi
  zorunlu** olarak "sıradaki analizler"e yazıldı (aşağıda).
- **C8 (dil):** "cleared the kill-bar" ibaresi D2/§4 muadilinde uygulandı (F1 ile birlikte).
- **C9:** F3 recheck'leri ile kapatıldı (HASHES, delta64, LoCoMo üyelik).

## D5'in "sıradaki 3 analiz" listesi (uygulanacak)

1. **Kill için birleşik belirsizlik:** kısmen yapıldı (C1 sayıları); kalan: OR-kuralı
   kill-yanlılığının (selection lift nedeniyle) null-model simülasyonu — (b) prereg notuna girer.
2. **c2 LARGE-free ablation + gain CI + resmi vs-random testi** — prereg öncesi şart.
3. **D2 çok-split + tam-gold-free tie-modeli AUC** — c2-premisi olarak.

## Citation-safe / correction listeleri
D5'in (a) listesi aynen geçerli; (b) listesindeki 6 maddenin TAMAMI bu turda disposition edildi.

---

## EKSİK ANALİZLER — TAMAMLANDI (2026-09-13, akşam)

D5'in "sıradaki 3 analiz" listesi tamamlandı; üçü de `round3/missing_analyses/` altında:

1. **m1 — kill-null simülasyonu** (`m1_kill_null/`): no-edge bir kolun vs-best-of-10 farkı beklenen
   olarak LME **−1.62pp** / LoCoMo **−1.20pp** (best-of-10 selection-lift). drop64 gözlemi null'un
   **57. / 89. yüzdeliğinde** → "prim yok" bölgesinin tam içinde. Kill, bar yerleşiminden değil,
   veriden: kural **geçerli bir prim-dedektörü** (gerçek ~+2.6pp'lik bir prim barajı geçerdi).
2. **m2 — D2 çok-split + tam-gold-free** (`m2_d2multi/`): T-modeli **10/10 split'te** sağlam
   (AUC(T) 0.821, Δ(T−M) +0.162 [CI 0.126–0.199], %100 ≥0.05); **gold-free G modeli 0/10 split
   ≥0.65** (ortalama 0.555) → tie-mekanizması gold'suz operasyonalize edilemiyor;
   **c2'nin öncülü başarısız** (mekanizma gerçek, router değil).
3. **m3 — c2 ablation paketi** (`m3_c2ablation/`): LARGE-free router AUC 0.670/0.568, gain@0.20
   +1.97/+1.19pp (CI'lar 0'ı içerir); **resmi vs-random testi (200 çekiliş, Bonferroni×4)**:
   LME α=0.20 **gürültü içinde** (p_bonf 0.18 — ilk "10-draw üstü" yanılsamaydı); α=0.30/0.40
   beats-random; **LoCoMo dört α'da da gürültü içinde**. → **c2 NOT prereg-ready.** Bağlayıcı
   kapı (gelecek prereg için): gain@0.20 > 200+ random çekilişin **maksimumu**, per-benchmark,
   yalnız LARGE-free modelle; LoCoMo o kapı ateşlenmeden replikasyon sayılamaz.

**Toplu sonuç:** adaptif/router hattı şimdilik **kapandı** (m2 + m3); tie-mekanizması bilimsel
olarak sağlam kaldı (m2 Task-1: 10/10); **(b) 12-byte yarışı ana hat olarak öne çıktı.**
