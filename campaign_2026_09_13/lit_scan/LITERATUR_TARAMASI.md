# LİTERATÜR TARAMASI — llmzip programı için fayda haritası

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**
**Tarih:** 2026-09-13 · [LOCAL] [NOT PUSHED] · Kapsam: binary/sign kuantalama, BQ teori,
vektör sıkıştırma, LLM bellek sistemleri, bellek benchmark'ları.
Amaç: (a) bizim bulgularımızın literatürdeki yeri, (b) somut olarak faydalanabileceğimiz
yöntem/deneyler, (c) rakip/komşu işler ve farkımız.

---

## 0. EN ÖNEMLİ İKİ İSABET (özet)

1. **Teori ikizi bulundu:** "Covariance Structure and Coordinate Heterogeneity Govern Binary
   Quantization of Contrastive Embeddings" (arXiv 2605.17524, v2 2026-05). Bizim pilot serimizin
   İKİ merkezi bulgusunu birinci prensipten açıklıyor:
   - **Rotasyon hasarı** (bizim Haar: LME −15.9pp / LoCoMo −9.9pp) = onların **Corollary 3**
     (rotation drives CV(σ)→0, heterogeneity sinyalini yok eder; "universality vs exploitation"
     ödünleşimi — RaBitQ döndürür, QuIVer döndürmez).
   - **2-bit kazanç** = **Prop 5**: magnitude bit, kazancı **koordinat heterojenliği** ile ARTAN
     bilgi taşır. Bizim henüz test etmediğimiz yön (12B bütçede 96×1bit yerine 48×2bit vb.).
   - Ayrıca: off-diagonal kovaryans, sıralama sadakatinin **%30–50'sini** açıklıyor ("ilişkisel
     bilgi"); F/G ayrıştırması + sub-Gaussian sıralama hatası modeli — bizim MATH-1/MATH-2'nin
     daha genel çerçevesi.
2. **"MSE ≠ Recall" fırtınası:** TurboQuant (Google, ICLR 2026) "6× sıkıştırma, sıfır kayıp"
   iddiası → RaBitQ ekibinin simetrik karşılaştırması (arXiv 2604.19528) ve bağımsız benchmark:
   **TurboQuant'ın MSE'si %44 daha düşük ama Recall@10 %37 daha kötü** (0.245 vs 0.387).
   Meta-ders: **reconstruction iyileştirmek ≠ arama iyileştirmek; doğru metrik rank
   korelasyonu/recall.** Bizim "sign96, float96'yı geçer" anomalimiz bu dersin bizim boru
   hattındaki en çarpıcı örneği — endüstri ölçeğinde teyitli bir olgu sınıfı.

---

## 1. TEORİ: HETEROGENLİK MAKALESİ — ne veriyor, nasıl kullanırız

Kaynak: arXiv 2605.17524 (+ dayanak: "InfoNCE Induces Gaussian Distribution", arXiv 2602.24012;
Betser et al. 2026). Tam metin kopyası: `sources/coordinate_heterogeneity_2605.17524.md`.

**Verdiği araçlar:**
- **Teşhis istatistikleri:** CV(σ) (koordinat varyansı heterojenliği), sign entropy H_sign,
  per-coordinate SNR dağılımı (std(|SNR|)), log r_off. → Bunları **bizim C96/Y96 üzerinde
  hesaplayıp** bulgularımızı bu çerçeveye oturtabiliriz.
- **İki-parametreli scaling law** (F = sadakat; üç kovaryans istatistiğiyle). → Bizim LME/LoCoMo
  panellerimizde test edilebilir: F tahmini vs bizim ölçtüğümüz sıralama kalitesi.
- **Rotation yanıt cetveli (Tablo 5):** GIST degenerate: +307% (rotasyon şart!); Wolt-CLIP
  over-spread: +3.2pp; Cohere near-optimal: −0.5pp; MiniLM izotropik: ≈0. → Bizim C96'nın hangi
  rejimde olduğunu sign-entropy ile ölçebiliriz (neden −15.9pp? → "near-optimal değil, aşırı
  simetrik olmayan/norm yapısı farklı" olabilir; ölçüp göreceğiz).
- **F/G ayrıştırması:** fidelity (gürültü) × margin (sinyal) → top-K hata olasılığı üst sınırı.
  → MATH-1 modelimizin (mesafe dağılımı → panel tahmini r≥0.997) daha genel bir dil yazımı.
- **Magnitude bit teoremi (Prop 5, monotonicity):** heterojenlik ↑ ⇒ 2-bit kazancı ↑.

**Bizimle eşleşme tablosu:**
| Bizim bulgumuz | Literatür karşılığı |
|---|---|
| Haar rotasyon −15.9/−9.9pp | Corollary 3: rotasyon heterojenliği sıfırlar |
| SPREAD ≈ RANDOM > TOP-variance | heterojenliğin "implicit weighting" doğası; variance-sıralı seçim yanlış sinyali alır |
| Clone/tie kümeleri 7–13× binomial (MATH-1) | onların Gaussian-bulk varsayımına komplementer: spike bileşeni bizim özgün katkımız |
| sign96 > float96 (+10pp) | "MSE≠Recall": reconstruction ≠ ranking (BN: bizimki rank-metriğinde kazanıyor) |
| 1-bit/eksen doğal doygunluk | quantized-RP literatürü: düşük benzerlik rejiminde b=1 MLE-optimal (NeurIPS'16) |

**Aksiyonlar (öncelikli):**
- **E1:** C96 üzerinde heterojenlik teşhisi: CV(σ), H_sign, SNR dağılımı, r_off; rotasyon
  öncesi/sonrası sign-entropy değişimi → bizim −15.9pp'nin onların cetvelindeki yeri.
- **E2 (en heyecan verici):** AYNI 12B bütçede bit-dağıtımı deneyi: (a) 96×1bit (şampiyon),
  (b) 48×2bit spread-48, (c) 48×2bit top-48 variance, (d) 64×1.5bit karışık. → Magnitude bit
  bizim bellekte kazanç veriyor mu? Verirse: yeni prereg adayı ve potansiyel 12B>12B iyileşme.
- **E3:** F/G çerçevesini MATH-1'e bağla (final rapor/paper için ortak dil).

## 2. SİSTEM KOMŞULARI — kim ne yapıyor, farkımız ne

| İş | Ne | Bizden fark / aksiyon |
|---|---|---|
| **Hippocampus** (arXiv 2602.13594, MLSys'26) | Ajan belleği: **binary imzalar + kayıpsız token-ID akışı**, wavelet matrix ile Hamming-ball arama; LoCoMo+LME | **EN YAKIN SİSTEM.** Ama imzaları **random indexing** (döndürmeli!) ve axis-yapısı yok; sertifikasyon/bütçe yarışı yok. Bizim axis-preserving + sertifikalı hikâyemiz farklılaşıyor. İncelenecek: onların retrieval kalitesi vs bizim FR@3'ler. |
| **QuIVer** (arXiv 2605.02171) | BQ-native graf indeksi; 2-bit sign-magnitude; "applicability boundary" (kontrastif gömmelerde ≥88% R@10; yapısız veride <15%) | Bize teyit: BQ kontrastif gömmelerde çalışır; axis-preserving yaklaşım meşru. Sistem katmanı farklı (graf topolojisi). İleride "2-bit Sign-Magnitude" bizim E2 ile aynı aile. |
| **MHR** (arXiv 2609.07276) | "Model-aware" öğrenilmiş hash kodları; 32B'da PQ'yu geçiyor; "düşük bütçede avantaj artıyor" | Bizim "learned selection ÖLDÜ" sonucumuzdan FARKLI eksen: biz eksen SEÇİMİ öğrendik (öldü), onlar kodu sıralama kaybıyla EĞİTİYOR. Gelecek-prereg adayı; şimdilik takip. |
| **IKE** (Findings ACL 2026) | Learning-free Isolation-Kernel binary embedding; 16× bellek, ~aynı kalite; "high diversity" kriteri | Alternatif learning-free binary aile; axis-preserving değil. Karşılaştırma adayı. |
| **RaBitQ ekosistemi + LanceDB** | Multi-bit RaBitQ (SIGMOD'25); 5-bit ile 96.2% R@10, PQ'dan 2.6× düşük latency; endüstriye girmiş | Bizim RB3 sonucu: 12B'da 1-bit RaBitQ32 kaybediyor; multi-bit RaBitQ 20B+ (bütçe dışı). Bizim 12B yarışımızın hakemli çerçevesi için atıf. |
| **SimpleMem / CoreMem / LatentPress** | Bellek sistemleri: semantik sıkıştırma (token düzeyi), Fisher-rehberli, soft-token context | Farklı katman (metin/token sıkıştırma). Bizim "gösterim düzeyi 12B" katmanımız bunlarla ORTOGONAL; birlikte kullanılabilir anlatı. |

## 3. KLASİK/TEORİK ZEMİN (atıf havuzu)

- **Charikar 2002** SimHash/SRP: işaret-rastgele-projeksiyon = angular similarity tahmincisi.
- **"Beyond 'project and sign'" (ICASSP'14)**: SRP suboptimal; kuantalama+reconstruction bakışı;
  asymmetric estimator (sorgu sıkıştırılmaz) daha iyi.
- **Quantized RP MLE (NeurIPS'16)**: b-bit kuantalanmış RP'de **b=1, benzerlik <0.2 iken
  Fisher-optimal**; yüksek benzerlikte b artırmak kazanır; "sonlu-bitte J-L eşdeğeri YOK".
- **Sign-Full RP (AAAI)**: sorgu tarafını 1-bite indirmemek (y=full) tahminci varyansını düşürür
  — bizim sorgu tarafı seçimlerimiz için fikir (şu an iki taraf da işaretli).
- **Near-optimal binary embedding bounds (1512.04433)**: altuzaylar için m≈δ⁻²·d.
- **Count Sketch SRP (AISTATS'22)**: SRP varyansını düşüren sketch.

## 4. BİT TAHSİSİ / HETERO-PRECISION (bizim future-prereg'e destek)

- **"Quantization Beyond Uniform Bit Allocation"** (arXiv 2608.19388, MSR): sabit bütçede
  contiguous bucket + greedy değişken bit tahsisi → PQ'da +8%, SQ'da +18% recall; "en büyük
  kazanç düşük-bit rejiminde"; MRL özellikli gömmelerde ilk boyutlara bit yoğunlaşır.
  → Bizim "hetero-precision" fikrinin literatür kanıtı; E2'nin (d) kolu bu çerçeveden beslenmeli.
- **MRL (Matryoshka)**: bizim SVD96 koordinatları zaten azalan varyanslı — değişken bit için
  doğal eksen sırası adayı.

## 5. YENİ BENCHMARK KAYNAKLARI (BENCH-3 sonrası adaylar)

- **MemoryAgentBench** (arXiv 2507.05257): 4 yetkinlik (accurate retrieval, test-time learning,
  long-range understanding, conflict resolution); LME/LoCoMo segmentlerinden inşa edilmiş;
  Mem0/Zep/MemGPT/HippoRAG sayıları içeriyor. → BENCH-4 adayı (özellikle "accurate retrieval"
  görevleriyle veri yeniden kullanılabilir).
- **MemTrack** (arXiv 2510.01353): çok-platformlu ajan ortamları; LoCoMo/LME'nin tekil-sohbet
  sınırını aşar. → İzleme listesi.
- Not: REALTALK+PerLTQA zaten BENCH-3'te indirildi (koşuyor).

## 6. SOMUT AKSİYON LİSTESİ (öncelik sırasıyla)

1. **E1 — Heterojenlik teşhisi** (küçük, hemen): C96'da CV(σ), sign-entropy (rotation öncesi/
   sonrası), SNR dağılımı; bizim Haar hasarının oku. Çıktı: lit ile bağlanmış mini rapor.
2. **E2 — 12B'de bit-dağıtım deneyi** (orta): 96×1 / 48×2 spread / 48×2 top / 64×1.5 vs
   şampiyon; sign-magnitude bizim bellekte kazanıyor mu?
3. **E3 — F/G + scaling-law uyarlaması** (orta): MATH-1 modelimizi onların diliyle yeniden
   ifade; panel tahminlerini onların üç istatistiğiyle karşılaştır.
4. **E4 — Related-work taslağı** (yazım): §3-§5'teki atıf havuzundan 2 sayfalık ilgili işler;
   farkımız: axis-preserving + görev-kaybı sertifikası + yarış + tie-mekanizması.
5. **E5 — MemoryAgentBench değerlendirmesi** (izleme): BENCH-4 fizibilite notu.

## Kaynaklar (ana)
- 2605.17524 heterogeneity/covariance (TEORİ İKİZİ) · 2602.24012 InfoNCE-Gaussian
- 2604.19528 RaBitQ vs TurboQuant (simetrik) · MSE≠Recall bağımsız benchmark · milvus.io röportaj
- 2605.02171 QuIVer · 2602.13594 Hippocampus · 2609.07276 MHR · IKE (ACL'26 Findings)
- 2608.19388 variable bit allocation · 2405.12497 RaBitQ · QINCo2 (2501.03078) · TurboQuant (ICLR'26)
- 2507.05257 MemoryAgentBench · 2510.01353 MemTrack · 2601.02553 SimpleMem · 2606.18406 CoreMem ·
  2609.01507 LatentPress
- Klasikler: Charikar'02 · ICASSP'14 beyond-sign · NeurIPS'16 quantized-RP-MLE · AAAI sign-full-RP
