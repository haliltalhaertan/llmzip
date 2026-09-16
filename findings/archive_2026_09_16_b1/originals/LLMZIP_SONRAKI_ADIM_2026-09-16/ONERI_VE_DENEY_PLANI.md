# LLMZIP — Son ölçümlerden sonraki geliştirme önerisi ve kaynak kaydı

16 Eylül 2026

[RESEARCH PROPOSAL] [NO NEW BENCHMARK RUN] [NOT INDEPENDENTLY AUDITED]

Bu not yeni bir deney sonucu değildir. Aynı asistanın, son gerçek 12/24/48 bayt raporunu ve birincil literatürü değerlendirmesidir. Bağımsız LLM alt ajanı başlatılmadı. GitHub/Drive veya dondurulmuş araştırma görevleri değiştirilmedi.

## Ölçülmüş başlangıç

Kaynak: LLMZIP_GERCEK_12_24_48_BAYT_RAPORU_2026-09-16.md. Ana karşılaştırma aynı exact Gram hesaplayıcısının üç boyutu; eski randomized96 ayrı kontroldür. 510 arşiv, 10.266 soru, 249.776 kayıt; RealTalk yeni merdivende yok. Aynı değerlendirme verileri önceden görülmüş, yeni gizli test değildir.

| Veri | 12 B FR@3 | 24 B FR@3 | 48 B FR@3 | BM25 FR@3 |
|---|---:|---:|---:|---:|
| LongMemEval | 52,47 | 61,48 | 61,75 | 57,14 |
| PerLTQA en_v2 | 52,98 | 54,82 | 51,87 | 60,14 |
| LoCoMo | 35,11 | 41,21 | 44,15 | 42,87 |

FR@3, gerekli kanıtların ilk üçteki payıdır; cevap doğruluğu değildir. LME'de 48−24 farkı belirsiz, PerLTQA'da 48 B daha kötü, LoCoMo'da ek fayda vardır. Veri kümesine göre sonradan kazananı seçmek önceden tanımlanmış ortak bir yöntem değildir.

PerLTQA float_std192=57,78 ve float_std384=54,49. Bu, 384-bit gerilemesini yalnız binarizasyonla açıklamayı yetersiz kılar. Zayıf koordinatların ölçeklendirmeyle fazla büyütülmesi bir HİPOTEZDİR; kök neden saptanmış değildir.

LME'de 12 B kodların toplamı 2,7793 MB iken 470 ayrı kodlayıcı/indeks durumunun pickle serileştirmesi 9.948,88 MB. İkinci sayı RAM değildir. Tek aktif arşivli servis RSS'si yaklaşık 171–205 MB; runtime/kütüphane tabanı yaklaşık 161 MB. BM25/float için bu turda eş koşullu toplam RSS/CPU deneyi yapılmamıştır.

## Karar

24 bayt, sonraki araştırma için sabit bir referans olsun; evrensel optimum veya üretim tercihi ilan edilmesin. 12 ve 48 B kontrol olarak kalsın. İki ayrı hedef: (a) kodlayıcı dahil toplam maliyet, (b) sabit baytta kanıt sıralama kalitesi.

## E0 — Önce güçlü rakibin gerçek maliyeti

Aynı ham metin, tokenizer, kayıt/gold kimlikleri ve deterministik tie sırasıyla 24 B qscale, güçlü BM25 ve float192'nin metinden sonuca CPU/duvar zamanı, RSS/USS, model dosyası, kurulum ve güncelleme maliyetlerini ölç. Sıcak servis ile soğuk yükleme ayrı; tek ve çok arşivli yerleşim ayrı. BM25'nin kalite sonuçlarını zayıf eski tokenizerlı sürümden alma. Aynı metin bütçesi ve aynı top-k kullan. Kaynak paneli ile bütün kohortun kalite ölçümünü karıştırma.

Amaç: Hangi sistemin aynı kaliteyi daha ucuza verdiğini belirlemek. Yeni bir yöntem eklemek değil, eksik güçlü maliyet kontrolünü tamamlamak.

## E1 — Aynı kaliteyi koruyarak kodlayıcı durumunu küçült

Önce bileşen envanteri: vocabulary/IDF, LSA, sparse ZT, A, mean/std, raw text/IDs, packed codes, geçici tamponlar ve runtime. İçeriği gerçekten birebir aynı nesneleri hash ile saptayıp paylaş; ayrı arşivlerdeki farklı istatistikleri keyfi olarak birleştirme. Ham metin veya oturum tekrarları varsa yalnız doğrulanmış tekrarları tekilleştir.

Tam eşdeğer saklama değişikliği ile float64→float32 nicemlemesini ayrı tut. İkincisi yaklaşık bir değişikliktir ve sıfıra yakın koordinatların bitlerini değiştirebilir. Sıralama/kalite kapısından geçmeden kayıpsız denmesin. Native uygulama runtime tabanını azaltabilir; model matrislerini kendiliğinden küçültmez.

Tam-eşdeğer kolun kabul şartı: aynı top-k ve metrikler, eksiksiz kaynak muhasebesi. Yaklaşık kol: önceden tanımlanmış kabul edilebilir kalite kaybı ve ayrı etiketleme. Bu not herhangi bir tasarruf miktarı vaat etmez.

## E2 — Bit sayısı mı, koordinat hassasiyeti mi?

| Çekirdek kod bütçesi | Genişlik ağırlıklı | Hassasiyet ağırlıklı |
|---|---|---|
| 24 B = 192 bit | 192 koordinat × 1 bit | 96 koordinat × 2 bit |
| 48 B = 384 bit | 384 koordinat × 1 bit | 192 × 2 bit veya 96 × 4 bit |

Bu aritmetik yalnız kod çekirdeğidir. Kayıt başına norm/düzeltme skaları gerektiren yöntemlerde bunları bütçeye ekle; katı toplam bütçe aranıyorsa kullanılabilir kod alanından düş. Ortak eşik/codebook/rotasyon/model durumları ayrıca raporlanır. Gerçek paketli kodlarla hesap yap; hazır float doküman matrisi üzerinden hızı ölçme.

İlk kontrol basit 2-bit skaler nicemleme; güçlü literatür kontrolleri çok-bitli RaBitQ (S4) ve ilgili TurboQuant iç-çarpım varyantı (S5). Her ikisinin gerçek tahmincisini uygula; rastgele döndürme + Hamming bunların yerine geçmez. TurboQuant residual düzeltmesi kayıt başına tek bit değildir; dönüşmüş residual koordinatı başına bittir. Kaynağın KV-cache başarısı bizim FR@3 sonucumuz değildir.

Bu, 12 baytta daha önce denenmiş B8 deneylerinin hiç yapılmadığı iddiası değildir. Yeni soru genişletilmiş bütçenin daha fazla yön mü yoksa yön başına daha fazla hassasiyet mi için harcanacağıdır. 2-bit kazancı varsayılmaz; daha az yönün kaybı daha iyi hassasiyetin kazancını aşabilir.

## E3 — Yeni, küçük ve paylaşılabilir kodlayıcı ailesi

Önerilen ayrı hat: metin → sabit boyutlu özellik hashing → yapılandırılmış küçük projektör → paketli kayıt kodu + sürekli sorgu. CBE (S1/S2) büyük yoğun projektör yerine circulant yapı ve FFT kullanır; mevcut arşive-özel SVD'yi aynen üretmez. Hız karmaşıklığı tek başına küçük seyrek arşivde duvar zamanı üstünlüğü garanti etmez.

HashingVectorizer (S3) sözcük sözlüğünü saklamaz ama çakışmalar getirir ve yerleşik IDF içermez. Nadirlik ağırlığını sessizce kaldırma: korunmuş IDF ile hash-bucket IDF/stateless kontrolü ayrı, maliyetleri açık olsun. Paylaşılan öğrenilmiş dönüşüm varsa fit sadece eğitim arşivleriyle; test sorguları/gold kullanılmaz. Yeni yöntem eski protokolün devamı değil, ayrı keşifsel bir adaydır.

Hippocampus (S8) bu mimari soruya yakındır: akış halinde random indexing ve içerik/imza indeksleri. Ancak imza birimi ve sorguda LLM kullanımı farklıdır; salt isim anarak ucuzluk rakamı aktarılamaz.

## E4 — Dar teşhis: fazla büyütülen koordinatlar mı?

PerLTQA'da float ve bit skorları birlikte düştüğü için 192/384 boyutta ölçek kaynaklı hassasiyet kontrolü yap. Örneğin yalnız sorgu ağırlığını q_j / sqrt(sigma_j^2 + tau^2) ile sınırlayan aday, aynı doküman bitleri üzerinde denenebilir. Tau=0 referansı aynı hesaplayıcıda aynı sonucu üretmeli. Tau'yu test sonuçlarına göre seçme; kalibrasyon veri ve kuralı önceden belirle. Float tarafında eşdeğer karşılaştırma ayrıca gerekir. Bu formül öneridir, doğrulanmış düzeltme değildir.

96 boyutta alpha ölçek taraması geçmişte yapılmıştır; yeniden adlandırılıp yeni bulgu diye sunulmasın. Burada yüksek boyut gerilemesine özgü bir müdahale sınanır; doküman normu/merkezlemesi ve rank-capped arşivler ayrıca incelenir.

Daha uzun vadede LeanVec-OOD (S7), veritabanı ve temsil edici eğitim sorgularını birlikte kullanarak benzerlik hatasını hedefler. Bu hazır 24 B arama çözümü değildir; kendi sistemi reranking içerir. Sorgu kullanarak öğrenilen aday, sadece dokümanla fit edilen donmuş tariften ayrı tutulmalıdır.

## Yapılmaması gerekenler

- En yüksek sonuç veren veri kümesi/boyutu sonradan seçip tek sistem başarısı yazmak.
- 48 B kodun ilk yarısını, önceki 24 B sonucuymuş gibi kullanmak. Her boyutta normalizasyon/merkezleme ayrı olduğu için prefix özdeşliği yok.
- Kaliteyi bir algoritmada, CPU/RAM'i başka algoritmada ölçmek.
- Bellek azaltımı iddiasında A, ZT, sözlük, model, norm veya ikinci indeksi görünmez kılmak.
- Tek asistanın kontrollerini bağımsız LLM alt ajanı denetimi olarak sunmak.

## Kaynaklar ve erişim kapsamı

Kaynakların hiçbirinin deneyleri bu turda yeniden çalıştırılmadı. S1/S2/S4 için yayın/ön baskı özeti, S3 için resmi API belgesi, S5/S7/S8 için HTML yöntem metinleri, S6 için yazar kurumu açıklaması incelendi. Önceki MHR sayfası bu oturumda tekrar erişilebilir olmadığından bu önerinin doğrulanmış yeni kaynağı sayılmadı.

- S1: Circulant Binary Embedding — https://proceedings.mlr.press/v32/yub14.html
  Kapsam: ICML/PMLR primary paper abstract.
- S2: On Binary Embedding using Circulant Matrices — https://arxiv.org/abs/1511.06480
  Kapsam: author preprint abstract.
- S3: HashingVectorizer — https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.HashingVectorizer.html
  Kapsam: official scikit-learn documentation.
- S4: Practical and Asymptotically Optimal Quantization of High-Dimensional Vectors in Euclidean Space for Approximate Nearest Neighbor Search — https://arxiv.org/abs/2409.09913
  Kapsam: author preprint abstract.
- S5: TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate — https://arxiv.org/html/2504.19874v1
  Kapsam: primary paper HTML v1.
- S6: TurboQuant: Redefining AI efficiency with extreme compression — https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
  Kapsam: Google Research author blog.
- S7: LeanVec: Searching vectors faster by making them fit — https://arxiv.org/html/2312.16335v2
  Kapsam: primary paper HTML v2 of 2023 preprint.
- S8: Hippocampus: An Efficient and Scalable Memory Module for Agentic AI — https://arxiv.org/html/2602.13594v1
  Kapsam: primary paper HTML v1.
