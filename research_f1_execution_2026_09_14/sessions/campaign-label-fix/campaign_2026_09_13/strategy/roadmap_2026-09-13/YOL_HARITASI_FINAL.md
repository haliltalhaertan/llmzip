# YOL HARİTASI (nihai) — Muse beyin fırtınası sentezi

**Tarih:** 2026-09-13 · **Kaynak:** iki bağımsız Muse oturumu (strateji + teknik fikir, xhigh) +
tur-1/tur-2 pilot bulguları · **Etiketler:** [YEREL STRATEJİ NOTU] [PILOT AÇIKLAMASI TAŞINACAK]
[4F1'E DOKUNULMADI]

Tam raporlar: `muse_strategy_roadmap.md` (strateji) · `muse_ideas_technical.md` (30+ fikir,
top-5 + 9 red + literatür bayrakları) — bu dizinde.

## Ana mutabakat (iki oturum nerede buluştu)

1. **Tek en önemli sonraki deney: öğrenilmiş primin çok-split sağlamlaştırması.** İki oturum da
   bunu "karar değeri en yüksek, en ucuz" ilan etti — çünkü tek-split +1.62pp'lik kazanç, 3.34pp
   seed gürültüsünün içinde; bu deney hem (b)'nin kol tablosunu belirler hem de olgunlaşmamışsa
   programı sağlam bir kolu mühürlemekten kurtarır.
2. **12-byte bütçe yarışı programın amiral kararı** — metni şimdi revize et (hesapsız), koşuyu
   Deney 1'in kapısından SONRA yap.
3. **Tie-geometrisi = "asıl bilimsel sonuç" adayı.** Ortalama-ayrım ölü; top-3'ü tie kütlesi
   belirliyor. Tie-mass ayrıştırması şimdi koşulacak (hem bilim hem öngörücü kapısı).
4. **Heterojen hassasiyet / <8B = Faz 2'ye ertelendi** (NOES-yakını, amiral karardan sonra).
5. **Disiplin:** her yerde "vs en iyi seed" birincil ölçüt; benchmark'lar asla havuzlanmaz;
   inşaat assert'leri (eff_k==k); her turda bağımsız yeniden-hesap + tasarım denetimi.

---

## FAZ 0 — bu hafta, hepsi paralel, hepsi mevcut donmuş altyapıyla (dakikalar-saatler)

### Deney 1 — Öğrenilmiş prim sağlamlaştırma (TEK EN ÖNEMLİ DENEY)
- **Tasarım:** 10 yeni train/test split (qid-sha256 tuzu döndürülmüş + tip-dengeli varyantlar);
  utility paneli {drop, alone-norm, var(kontrol), spread}; test tarafında 10 taze seed'lik RANDOM
  panelleri; k∈{32,48,64}; LME + LoCoMo aynası.
- **Birincil ölçüt:** split-başına (drop64_test − o-splitin-en-iyi-RANDOM64'ü); ortalama +
  win-rate. (vs-mean ikincil raporda kalır.)
- **Kapılar:** native yeniden-hesap ≤1e-12; split ayrık+örtü kontrolü; utility provenance
  birebir; SPREAD inşaatı onarılmış (eff_k==k — stride-2 tavanı artefaktı düzeltilecek).
- **KILL:** ortalama-vs-best < +1.0pp VEYA win-rate < 7/10 VEYA LoCoMo aynası ≤0 → öğrenilmiş kol
  (b)'ye GİRMEZ. **PROMOTE:** ≥ +1.5pp VE ≥ 8/10 VE transfer (Deney 3) negatif değil.
  Belirsiz bölge (+1.0–1.5): (b)'ye ikincil kol olarak taşınır.
- **Ek validity:** var-kolun her split'te en kötü olması kontrolü (olmazsa boru hattı şüpheli).

### Deney 2 — Tie-mass ayrıştırması (c1, mekanizma + öngörücü kapısı)
- Per-soru × kol (TOP48/RAND48/BOT48/native): d_gold tie-kütlesi, gold±1 kütlesi, gold-bucket
  boyutu, 4. sıraya marj, dup-bucket, top-20 mesafe entropisi.
- **Yarış:** 2-3 özellikli tie-modeli (train'de fit) vs mean-istatistik modeli → held-out'ta
  flip yönü AUC'si. **KILL c2:** tie-AUC < 0.65 veya tie−mean ΔAUC < 0.05 → mekanizma
  "tanımlayıcı paradoks" olarak kalır, adaptif yok.

### Deney 3 — Cross-benchmark utility transfer (e1)
- LME-train utility → LoCoMo test (ve tersi); rank-korelasyon, top-k Jaccard, transfer edilmiş
  kolun FR'ı vs within-learned vs random. Kill: transfer ≤ random ise "transfer edilmiş utility"
  asla preregister edilmez; taşınabilir varsayılan SPREAD kalır.

### Deney 4 — Fresh-Q karışım doğrulaması (R2D'nin en ucuz yükseltmesi)
- Matched/antimatched blok-2 inşaatı YENİ Q blokları + seed 43004/43005 ile; LoCoMo'da
  "min-matched > max-random > max-anti" katı ayrımı taze bloklarla hâlâ tutuyor mu?

## FAZ 1 — Hafta 2: 12-byte bütçe yarışı (preregistration + tek koşu)

- **Bütçe tanımı (mühürle):** vektör başına ≤12 **marjinal kalıcı byte** (kod + norm/ölçek/aux);
  paylaşılan durum (codebook, rotasyon) tavan dışı ama **byte'ları ayrıca raporlanır**;
  archive-local fitting beyan edilir.
- **Kollar (her biri `measured_bytes == declared` assert'i — meşhur nb_bits tuzağına karşı):**
  NATIVE SIGN96 (12B referans) · spread/random alt-kümeler 10/8/6B (≥5 seed; LoCoMo'da BOT dahil) ·
  **öğrenilmiş-64 YALNIZCA Deney 1 kapısından geçerse** (geçmezse yerine spread/random) ·
  RABITQ32 (plain + random-rotation wrapper) · PQ (m=12×8bit) · extended-RaBitQ (44B) eşleşmeli
  bütçe karşılaştırmasından ÇIKARILIR (yalnızca recall-vs-bytes eğrisinde).
- **Birincil ölçüt:** seed-panelli SIGN12B − en-iyi-12B-rakip; iki benchmark AYRI (havuz yasak);
  bantlar önceden: ≥+2.0 belirleyici / ±0.5 parite / ≤−1.0 aleyhte.
- **Disclosure boilerplate (M1 §4):** [LOCAL EXPLORATORY PILOTS axis_attack r1+r2: alternate bit
  widths, variance-ordered/matched selection, gold-informed utilities, extra seeds — tümü
  açıklanır; whitening/PCA/learned-thresholds/reranking/supervised-rotation/alternate-metrics
  pilots'ta YOKTU ve NOES kapılı kalır; R2D errata (iki-kol, SPREAD tavanı, vs-best çerçeve,
  tek-seed R2A taban) kabul edildi.]

## FAZ 2 — koşullu (Faz 0/1 sonuçlarına bağlı)

1. **(c2) Başarısızlık öngörücüsü → adaptif.** Yalnızca c1 AUC≥0.65 VE held-out selective-gain
   ≥+1.0pp @ %20 abstention VE LoCoMo replik ise prereg'e gider. *Varsayılan beklenti: iyi AUC,
   ucuz adaptif kazanç yok — bu null'un kendisi mekanizma sonucu.*
2. **(d) Heterojen hassasiyet / alt-8B.** Yalnızca (b) sonrası; M2'nin A1 tasarımı hazır:
   yayılım-tabanı + drop-güdümlü çift-bitler (S48+8×2 vb.), train-only eşikler. NOES-yakını →
   yeni prereg şart. Ayrıca M2 B5 (|q|/marj güvenilirlik eğrileri) bunun ön-kapısı olarak ucuz.
3. **(e2) Encoder genellemesi.** Yalnızca yazılı SVD-fork kararı + fiziksel fizibilite probuyla
   başlar; corpus-ölçekli retrieval yok.
4. **M2'nin diğer problarına açık kapı:** A4 dither doz-yanıt (a=0 süreklilik kapılı), B2 bit-etki
   eğrileri, B4 dup-audit, B3 katılım-oranı — hepsi ucuz, analiz-only; c1 sonuçlarına göre seçilir.

## Yayın/narratif stratejisi (M1 §2)

- **"İmzalı nulllar birinci sınıf sonuçtur":** (i) top-variance seçimi her iki benchmark'ta
  random'dan ≥X pp kötü; (ii) karışım hasarı varyans-uyumsuzluğunda monoton; (iii) ortalama-ayrım
  istatistikleri sign-kod retrieval kalitesini sıralamaz — top-3'ü tie-kütlesi belirler.
  Bir iddia daha ekleyin: "sign96 neden float96'yı +10pp geçiyor?" (hubness/centering probu,
  M1 §2.2) — programın kurucu anomalisi teorize edilmeden tam hikâye olmaz.
- Sonuç: **tie-geometrisi makalesi** (c1/c2 replike olursa) > kodlayıcı kâğıdı (b) > diğerleri.

## Disiplin kuralları (her deney, her tur)

1. vs-en-iyi-seed birincil; range W/T/L'i yanında; vs-mean ikincil.
2. Benchmark havuzlama yasak; ayrı rapor.
3. İnşaat assert'leri: eff_k==k, cols logged, code_size abort, SPREAD onarımı.
4. Her tur: froze-anchor kapıları (0.0/1e-12) + bağımsız yeniden-hesap (R2V deseni) + tasarım
   denetimi (R2D deseni) — hiçbir sayı bunlarsız alıntılanmaz.
5. NOES/4F1: whitening, PCA/learned rotations, variance reweighting, learned thresholds,
   reranking, supervised rotation, alternate metrics — prereg'siz yok; BEAM/4F1'e sıfır temas.

## Falsifier'lar (programın yanlışlanabilir kalması için)

1. Top-variance aleyhteliği ölür: taze split/seed'de TOP-k herhangi k≥32'de random-mean'i geçerse.
2. Karışım sıralaması ölür: taze-Q matched ≈ random ≈ anti çıkarsa.
3. Öğrenilmiş prim ölür: Deney 1 ort-vs-best < +1.0pp veya win-rate < 7/10 (modal beklenti: %40 ölür,
   %40 belirsiz bölge, %20 temiz promote).
4. "LoCoMo'da bottom-en-iyi" ölür: daha çok seed'de çökerse (bu, R2C'nin kırılgan yarısı; sağlam
   yarısı "top-en-kötü + monoton sıralama").
5. Tie-hikâyesi ölür: mean-model tie-model kadar iyi tahmin ederse veya gold-free öngörücü AUC≈0.5.

---

## DURUM GÜNCELLEMESİ — Round-3 tamamlandı (2026-09-13)

Faz 0'ın dört deneyi + c2 koşuldu; bağımsız yeniden-hesap (D1V: 24/25 EXACT) ve tasarım denetimi
(D5: F1–F3 + C1–C9, tümü disposition) yapıldı. Sonuçlar ve yol haritasına etkisi:

1. **Deney 1 (learned premium): KILL** — 3/3 tetikleyici; kill, örtüşme-düzeltmeli CI
   [−2.00, −0.41]pp ile sağlam. → **(b) kol tablosunda öğrenilmiş kol YOK; spread/random onun
   yerinde** (pre-declared gating gereği).
2. **Deney 2 (tie-mekanizması): mekanizma GEÇTİ** (gold-informed; AUC 0.798 vs 0.686) → c2 için
   *keşif lisansı*; "deployable öngörücü" iddiası YOK (F1; c2'nin gold-free AUC'ları 0.686/0.558).
3. **Deney 3: utility'ler benchmark-yerel; transfer ≈ şans** (var-satırı tautolojik).
4. **Deney 4: karışım katı-ayrımı taze çekilişlerde dayanıyor** (confirmatory, n=2; konfound açık).
5. **c2: KOŞULLU** — LME'de random-abstain'i yeniyor (+3.09pp vs +1.83); LoCoMo ayağı boş
   (AUC 0.558); prereg öncesi **bağlayıcı vs-random kapı + LARGE-free ablation + gain CI** şart.

**Güncellenmiş sıradaki adımlar:**
- [TAMAM] D5 eksik analizleri (m1 kill-null; m2 D2 çok-split + gold-free; m3 c2 ablation):
  **c2 prereg'e HAZIR DEĞİL; adaptif hat kapandı** (`missing_analyses/`).
- **Sıradaki: (b) 12-byte yarışı prereg taslağı** — öğrenilmiş kol dışlandı (kill); spread/random
  + RaBitQ + PQ kolları; disclosure listesi r1+r2+r3 + errata; m1 bulgusu (kural = geçerli
  prim-dedektörü) not düşülecek. HR onayı → mühür → tek koşu.
- ED3 paketi v1.1 (eksik analizlerle) — taslak sonrası tek pas.
