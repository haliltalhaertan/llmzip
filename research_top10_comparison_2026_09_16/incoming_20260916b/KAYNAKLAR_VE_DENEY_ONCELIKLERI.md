# LLMZIP — Benzer çalışmalar ve araştırma öncelikleri

Tarih: 16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Bu etiketler LLMZIP sonuçlarına ve aşağıdaki proje önerilerine aittir; atıf verilen makalelerin yayın statülerini değiştirmez. Bu dosya bir literatür incelemesi ve öneri kaydıdır. Yeni benchmark çalıştırılmadı, yöntem eğitilmedi, üretim veya dondurulmuş protokol değiştirilmedi.

## 1. Araştırma sorusu

Mevcut 96 bitlik doküman kodunun toplam depolama avantajını koruyarak, güçlü ASYM/B8 kontrollerine karşı özellikle FR@3'ü iyileştirmek; yalnızca HIT@10 veya hazırlanmış sorgu çekirdeği üzerinden genel üstünlük iddia etmemek. Hız hedefi ayrıca kodlayıcı, sorgu hazırlığı, tarama, seçim ve içerik erişimine ayrılmalı.

Proje dayanağı: kullanıcının paylaştığı “Adversarial audit of the scaled-query result — findings” belgesinin ilk iki bulgusu, §4 ve C6; son “LLMZIP_HIZ_GENELLEME_RAPORU_2026-09-16.md” içindeki kapsam ve maliyet ayrımları. Denetimdeki tüm çıkarımlar otomatik kabul edilmez: örneğin istatistiksel anlamsızlık eşdeğerlik kanıtı değildir; tek tek başarılı global ölçek/ölçek kuantizasyonu deneyleri birleşik tasarımın başarısını kanıtlamaz.

## 2. Doğrulanabilen yakın literatür

### R1 — Asymmetric Distances for Binary Embeddings

Albert Gordo, Florent Perronnin. CVPR 2011.

Birincil kaynak: https://europe.naverlabs.com/research/publications/asymmetric-distances-for-binary-embeddings/

Erişim: Yazar laboratuvarının yayın sayfası ve özeti okundu. İkili doküman ve sürekli sorgu kullanmanın tarihsel dayanağı. Bizim özel ölçekleme formülünün burada aynen yer aldığı iddia edilmiyor.

### R2 — Matryoshka Hash Representations for Model-Aware Compact Semantic Retrieval

Peichun Hua, Yunming Xiao. Eylül 2026 ön baskı; arXiv:2609.07276.

Birincil yazar kaydı: https://yunmingxiao.github.io/publication/26-matryoshka/
ArXiv: https://arxiv.org/abs/2609.07276

Erişim sınırı: Yazarın arama dizinindeki yayın özeti ve yayın listesi bulundu. Tam arXiv/PDF dosyası bu oturumda alınamadı; tablolar, kod ve hesaplar bağımsız doğrulanmadı. Eski devirdeki MHR/32 bayt/~0,65 sayısının bibliyografik kaynağı bu kayıtla belirlenebiliyor; evrensel başarı çıtası veya bizim benchmarkla doğrudan karşılaştırma değildir.

### R3 — Efficient Passage Retrieval with Hashing for Open-domain Question Answering (BPR)

Ikuya Yamada, Akari Asai, Hannaneh Hajishirzi. ACL-IJCNLP 2021, Short Papers.

Birincil kaynak: https://aclanthology.org/2021.acl-short.123/
Tam metin: https://aclanthology.org/2021.acl-short.123.pdf
Yazar kodu: https://github.com/studio-ousia/bpr

Erişim: Yayın kaydı ve tam metin okundu; §3.3–3.4 görsel sayfa da incelendi. Yeniden sıralama sürekli sorgu ile ikili doküman arasındadır; tam float doküman sakladığı varsayılmamalı. Görev eğitimi, mevcut eğitimsiz hattın değişmeden devamı değildir.

### R4 — Hippocampus: An Efficient and Scalable Memory Module for Agentic AI

Yi Li, Lianjie Cao, Faraz Ahmed, Puneet Sharma, Bingzhe Li. MLSys 2026, Proceedings of Machine Learning and Systems 8.

Birincil yayın: https://proceedings.mlsys.org/paper_files/paper/2026/hash/a1d04870cf83a0f29819d66f1dfdbfcb-Abstract-Conference.html
Tam metin: https://proceedings.mlsys.org/paper_files/paper/2026/file/a1d04870cf83a0f29819d66f1dfdbfcb-Paper-Conference.pdf
Ön baskı HTML: https://arxiv.org/html/2602.13594v1

Erişim: Resmî yayın özeti ve ayrıştırılmış tam metin/ön baskı HTML incelendi. Sistem karşılaştırmasıdır; token imzaları, kayıpsız içerik ve sorgu anahtar sözcükleri çıkaran LLM adımı dahil maliyet sınırları korunmalı. Özgün uçtan uca QA ölçütü FR@3 değildir.

### R5 — Hashing as Tie-Aware Learning to Rank

Kun He, Fatih Cakir, Sarah Adel Bargal, Stan Sclaroff. CVPR 2018; arXiv ön baskı 2017, güncellenmiş sürüm v4/2018.

Birincil metin: https://arxiv.org/abs/1705.08562
PDF: https://arxiv.org/pdf/1705.08562
Yazar kodu: https://github.com/kunhe/TALR

Erişim: Özet, ayrıştırılmış tam metin ve resmî kod açıklaması incelendi. Eşit puanları dikkate alan AP/nDCG ve sıralama hedefli öğrenme için kaynak; FR@3'ün doğrudan çözümü değildir. Mevcut nDCG düzeltmesini bununla karıştırıp hit/FR sonuçlarını iptal etmemek gerekir.

### R6 — Covariance Structure and Coordinate Heterogeneity Govern Binary Quantization of Contrastive Embeddings

Wenxuan Xiao. arXiv:2605.17524v2, 29 Mayıs 2026. Ön baskı.

Birincil kaynak: https://arxiv.org/html/2605.17524v2

Erişim: Tam HTML, varsayımlar ve sınırlamalar incelendi. Sadece koordinat ölçekleri değil ortak değişim ve yakın rakipler arasındaki puan farkları için tanısal ilham sağlar. Yaklaşık Gauss/contrastive-embedding koşulları bizim TF-IDF/LSA gösterimimize doğrulanmadan taşınamaz; teoremler bağımsız denetlenmedi.

### R7 — Fast accumulation of PQ and AQ codes (FastScan)

Faiss proje belgeleri; André ve çalışma arkadaşlarının VLDB 2015 FastScan çalışmasına atıf verir.

Birincil uygulama belgesi: https://github.com/facebookresearch/faiss/wiki/Fast-accumulation-of-PQ-and-AQ-codes-(FastScan)

Erişim: Resmî uygulama açıklaması incelendi. Kısa, işlemci yazmaçlarında tutulan tablolar ve küçük tamsayı işlemleri. Mevcut 96 işaret bitini dörderli gruplamak doküman bit sayısını artırmaz; sorgu tablosunu kuantize etmek ise ayrıca hata kontrolü gerektirir.

### R8 — Constant Sequence Extension for Fast Search Using Weighted Hamming Distance

Zhenyu Weng, Huiping Zhuang, Haizhou Li, Zhiping Lin. arXiv:2306.03612, 2023.

Birincil kaynak: https://arxiv.org/abs/2306.03612

Erişim: Birincil özet okundu. Büyük koleksiyonlarda ağırlıklı Hamming ile aramaya doğrudan ilgili. Küçük arşivde indeks/tabloların kurulum ve RAM maliyetini ödeyerek SIMD taramayı geçeceği gösterilmiş değil.

### R9 — Accelerating Large-Scale Inference with Anisotropic Vector Quantization

Ruiqi Guo ve çalışma arkadaşları. ICML 2020.

Birincil kaynak: https://proceedings.mlr.press/v119/guo20h.html

Erişim: Resmî bildiri kaydı/özeti. Genel yeniden oluşturma hatası yerine aramada önemli iç çarpım hatalarını hedeflemek için kavramsal dayanak. Belirli LLMZIP kazancı veya FR@3 güvencesi değildir.

## 3. Bizim puanlamanın matematiksel kimliği

b_dj ∈ {−1,+1}, sigma_j > 0 olsun. w_j = qC_j / sigma_j, t_j = sign(w_j), a_j = |w_j| tanımlayalım. Sıfır ağırlığın işaret seçimi sonucu değiştirmez.

s(d,q) = Σ_j b_dj w_j
       = Σ_j a_j − 2 Σ_j a_j · 1[b_dj ≠ t_j].

Bir sorgu için ilk toplam sabittir. Dolayısıyla en yüksek qscale puanı ile en düşük sorguya bağlı ağırlıklı Hamming uzaklığı tam olarak aynı sıralamayı verir. Bu cebirsel çıkarım için bir veri dağılımı varsayımı gerekmez; kayan noktalı farklı uygulamaların bit düzeyinde aynı sonucu üretmesi ayrıca kontrol edilir.

Bu kimlik temel yaklaşımın yenilik iddiasını daraltır, fakat uygulama maliyeti, arşiv ölçeği, kanıt metrikleri ve hata ayrıştırması üzerindeki olası araştırma katkısını tek başına geçersiz kılmaz.

## 4. Önerilen deneyler — henüz çalıştırılmadı

### A. Birinci öncelik: ilk üç sonuçta kaybın türünü ayırmak

Aynı geliştirme sorusunda, güçlü tam-sayısal kontrol, ASYM/B8 ve qscale için bütün gold kayıtların sıraları ve ilk üç yanlış rakiple puan farkları tutulmalı. Tam-sayısal yol da başarısızsa yalnız bit düzeltmesi yeterli sayılmaz. Tam-sayısal yol başarılı ve ikili yol başarısızsa hedef, ilgili ayrımı kod/puanlamada korumaktır.

Yeni bir iki-aşamalı aday için, aday kümesindeki gold sayısından ulaşılabilir en iyi FR@3 tavanı hesaplanabilir: min(3, aday kümesindeki gold sayısı)/toplam gold sayısı. Bu etiket kullanan tanısal üst sınırdır, üretim algoritması veya performans tahmini değildir. Bütün arşiv taranıyorsa aday-kaybı zaten yoktur; bunun yerine sıralama hedefi incelenir.

### B. Kalite hattı: doğrudan sıralama hedefli, sabit 96 bit

R2/R3/R5'ten alınacak ilke, orijinal sayıları yeniden oluşturmak yerine doğru kanıtı yanlış rakibin önüne koymayı hedeflemektir. Başlangıç adayı küçük sorgu-puanlama modeli; daha büyük alternatif doğrudan 96 bit üreten ortak kodlayıcıdır. Bunlar mevcut deneyi dondurulmuş gibi yeniden adlandırmak değildir: model/etiket kullanımı için ayrı izinli araştırma kolu gerekir.

Kod uzunluğu aynı olsa bile model, eğitim, yeniden indeksleme ve sorgu maliyeti ücretsiz değildir. Arşivlerin ayrı SVD tabanlarında aynı koordinat numarasının aynı anlamı taşıdığı varsayılamaz. Eğitilen ortak modelin girdileri tutarlı uzayda tanımlanmalı; aksi hâlde projeye özgü eksen bilgisi yanlış paylaşılır.

FR@3 birincil; hit@10, düzeltilmiş nDCG ve daha uzun recall listeleri ikincil. Aynı kodlayıcının güçlü float/int8 sürümleri ve eski ASYM/B8 dahil edilir. Ayarlar görülmüş benchmarklar üzerinde seçilip aynı sonuçlar bağımsız test diye sunulmaz.

### C. Mühendislik hattı: küçük tablolar ve güvenli yeniden hesaplama

R7'den esinlenen öneri: 96 biti 24 dörtlü grupta okumak, 16 girdili sorgu tablolarını küçük tamsayılarla taramak, olası sıralama hatası taşıyan adaylarda özgün qscale puanını aynı koddan yeniden hesaplamak. Bu ikinci bir büyük doküman vektörü gerektirmez. Ama hızlanması henüz ölçülmedi.

Koşullu güvence: Bütün adaylar için |s_tahmin − s| ≤ E sınırı doğrulanıyorsa, yaklaşık k'ncı en yüksek puan tau için s_tahmin ≥ tau − 2E olan adayların tamamını tam puanlamak yeterlidir. Dışarıda kalan bir adayın gerçek puanı, yaklaşık ilk k içindeki en az k adayın alt sınırından küçük olur. E eşiklerinde eşitlikler dahil edilmeli; taşma/kırpma ve kayan nokta hataları E hesabına katılmalıdır. En kötü durumda bütün adaylar yeniden hesaplanır. Bu yöntem mevcut qscale sıralamasını korumayı hedefler, FR@3'ü kendiliğinden yükseltmez.

Zamanlama sorgu tablosu kurulumunu, transpozisyon amortismanını, yeniden hesaplamayı ve ilk-k seçimini içerir. AVX-512 dışı AVX2/ARM hedefleri kendi gerçek donanımında ölçülmelidir; yalnız derlenmesi performans kanıtı değildir.

### D. Toplam maliyet hattı: kodlayıcı mimarisi

R4'ün akış halinde gösterim üretmesi, arşiv başına pahalı yeniden faktörlemeyi azaltma açısından ayrı mimari adaydır. Bizim arşiv tabanlı TF-IDF/SVD yerine geçtiğinde gösterim değişir ve yeniden kalite deneyi gerekir. Önceden önerilen aynı-projektörü küçük faktörlerle uygulama ise farklı, eşdeğerlik hedefli mühendislik yoludur; Z dahil yardımcı diziler sayılmalıdır. Aynı optimizasyon float kontrolüne de verilmelidir.

## 5. Kabul/ret disiplini

- Yeni “başarı”: güçlü küçük-kod kontrolüne karşı önceden tanımlanmış birincil ölçütte, ayrılmış testte, toplam maliyet kabul sınırıyla birlikte değerlendirilir.
- Kalite: veri kümeleri ayrı; ortak oturum/arşiv bağımlılıkları açık; etiket/adaptör doğrulaması ve eşit-puan metrik testi zorunlu.
- Maliyet: kalıcı kodlar + tüm yardımcı istatistikler + model + sözlük + metin/kimlik + geçici tamponlar; tek-yöntem gerçek süreç tepe/yerleşik RAM; eğitim ve kurulum ayrıca.
- Gecikme: kodlama, hazırlık, tarama, ilk-k, içerik erişimi ayrı ve toplam; aynı aday seçimi ve eşitlik kuralı kalite/hızda tutarlı.
- İstatistik: istatistiksel anlamsızlık “eşit” veya “bedelsiz” demek değildir; çoklu seçenekler test etiketleriyle seçilmez.
- MHR/BEIR, BPR/Wikipedia ve Hippocampus/QA sayıları bizim FR@3 ile doğrudan karşılaştırılmaz.

## Sonuç

En yakın modern yöntem hattı MHR/BPR, en yakın bellek sistemi Hippocampus, değerlendirme/öğrenme dayanağı TALR, uygulama dayanağı FastScan'dir. Bu kaynaklar geliştirme yolları sunar; aynı 96 bit ve aynı toplam maliyetle başarı garantisi vermez. Öncelik “birkaç alpha/eşik daha denemek” değil, ilk üçteki gerçek sıralama sorununu hedeflemek ve asıl maliyet olan kodlayıcıyı ayrı incelemektir.
