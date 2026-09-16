# LLMZIP — Kodlayıcı maliyeti ve sabit bütçeli kod tasarımı için araştırma planı

16 Eylül 2026

[LOCAL EXPLORATORY PLAN] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Statü

Bu belge yeni bir kalite, hız veya RAM benchmarkı değildir. Son 12/24/48 bayt raporu, bu oturumda kontrol edilen birincil kaynaklar ve araştırmacının önerileri birbirinden ayrılmıştır. Bu oturumda bağımsız LLM alt ajanı çalıştırılmadı; mevcut araçlarda alt ajan başlatma işlevi bulunamadı. Aşağıdaki görevler ileride gerçek bir çok-ajan ortamına verilebilecek taslaklardır. GitHub/Drive üzerinde değişiklik yapılmadı.

## 1. Karar için mevcut kanıt

Kaynak: `LLMZIP_GERCEK_12_24_48_BAYT_RAPORU_2026-09-16.md`, aynı tarihteki JSON ve ZIP.

Ana kalite: aynı exact-Gram ailesi, gerçek paketli kodlar, deterministik FR@3. LongMemEval: 52,47 / 61,48 / 61,75; PerLTQA en_v2: 52,98 / 54,82 / 51,87; LoCoMo: 35,11 / 41,21 / 44,15 (12/24/48 bayt). Bütün veriler daha önce görüldü. RealTalk'ın yeni merdiveni eksik. 24 bayt geliştirme referansı adayıdır; evrensel optimum değildir. 48 bayt LoCoMo'da güçlü alternatif olarak korunur.

Son kaynak panelinde ham metinden sonuçlara CPU yaklaşık 1,3–4,1 ms; hazır sorguyla puanlama/seçim yaklaşık 24–32 µs. Farklı ölçüm medyanlarını birbirinden çıkarıp kesin bir bileşen profili üretmiyoruz; genel olarak kodlama baskın. Dual projektör bu son ölçümde Zᵀ ve A ile zaten kullanılmıştır: yeniden keşfedilmiş bir optimizasyon olarak önerilmeyecektir.

LME'de 470 arşivin 12-bayt koluna ait serileştirilmiş model durumları yaklaşık 9,95 GB; yalnız belge kodları 2,78 MB. Bu RAM, sıkıştırılmış disk boyutu veya zorunlu teorik maliyet değildir. Tek aktif arşivlik servis RSS'si yaklaşık 204 MB; çalışma zamanı tabanı yaklaşık 161 MB. Per-arşiv modellerin toplanması, gerçek bir müşterinin 470 modeli aynı anda tuttuğu iddiası değildir. BM25/float'ın kalite kontrolü var, aynı kapsamda toplam kaynak profili henüz yok.

## 2. Temel yön değişikliği

Amaç yalnız kayıt kodunu küçültmek değil, metin -> gösterim -> tarama -> sonuç bütününün maliyetini azaltmaktır. İki ortogonal değişken ayrılmalıdır:

- Kodlayıcı: arşive özel TF-IDF/LSA/SVD yerine ortak, daha az yardımcı durum taşıyan bir dönüşüm çalışır mı?
- Kayıt kodu: aynı payload bütçesi, daha çok bir-bit koordinata mı yoksa daha az çok-bit koordinata mı ayrılmalı?

İki değişken başlangıçta aynı deney kolunda birlikte değiştirilmez. Başarısız örnekleri sonradan dışlamak, her veri kümesinin kazananını tek sistem gibi birleştirmek veya kıyaslamada rakibi optimize etmemek yasaktır.

## 3. Kısa vadeli, sınırlı deney: aynı baytta boyut-hassasiyet takası

| Payload | Bir bit/koordinat | İki bit/koordinat | Dört bit/koordinat |
|---|---|---|---|
| 24 bayt | 192 x 1 | 96 x 2 | 48 x 4 |
| 48 bayt | 384 x 1 | 192 x 2 | 96 x 4 |

Bu sadece payload aritmetiğidir. Kod kitabı, koordinat başına eşikler/temsil değerleri, norm ve düzeltme faktörleri, satır hizalaması ve kimlikler ayrı ve toplam olarak sayılmalıdır. Eski 12-bayt B8 veya nadir-kelime/SVD füzyonu bu farklı bütçelerdeki bütün aileleri elemez; ancak onlar da tarihsel negatif kontroller olarak görünür kalır.

İlk aday sade skaler kuantizasyon olsun; sorgu sürekli kalır. Eşik ve temsil değerleri yalnız izin verilen dokümanlardan hesaplanır. Bir-bit kol, mevcut qscale sıralamasını aynen üretmek zorunda. Çok-bit puanlayıcının hedefi (iç çarpım ya da normalize kosinüs) önceden yazılmalı; değişen normları göz ardı ederek aynı hedefin ölçüldüğü söylenmemeli. Norm gerektiren yöntem bu bilgiyi depolama maliyetine ekler. Her boyutta aynı sürekli referans da raporlanır.

Güçlü harici kontroller: gerçek RaBitQ tahmincisi ve uygun SQ/PQ varyantları [4,5]. Haar+Hamming, RaBitQ yerine geçmez. Faiss'in erişilen resmi tablosunda RaBitQ bir-bit için d/8+8 bayt, çok-bit için d*b/8+20 bayt yazıyor. Örneğin 192-bit RaBitQ'nun bu uygulaması 24 değil 32 bayt/kayıttır; ortak dönüşümün maliyeti ayrıca vardır. Katı toplam bayt sınırı ve payload-eşit kıyas iki ayrı tablo olmalıdır.

## 4. Asıl sistem adayı: paylaşılan kodlayıcı

### 4A. Sinir ağı kullanmadan ortak özellik/dönüşüm

Feature Hashing, sözcük/karakter parçalarını öğrenilmiş bir kelime sözlüğü olmadan sabit özellik uzayına taşır [2]. Bu, tek başına 24-bayt arama sistemi değildir. Sonrasında ortak bir projeksiyon/kodlayıcı gerekir. İlk karşılaştırma sabit tohumlu, küçük durumlu dönüşüm; ikinci aday CBE gibi yapısal izdüşüm olabilir [3]. CBE'nin FFT ve küçük matris durumu fikri yararlıdır; makalenin yoğun matris asimptotiği, mevcut seyrek dual uygulamamıza doğrudan hız oranı vermez.

Riskler: hash çakışmaları, nadir ayrıntıların karışması, sözcüksel kanal kalitesinin kaybı. HashingVectorizer varsayılan olarak IDF içermez; IDF eklenirse yeniden istatistik durumu oluşur. Sözcük ve karakter ad uzayları ayrılmalı. Ortak öğrenilen dönüşüm yalnız geliştirme arşivlerinde fit edilmeli, değerlendirme arşivleri/gold üzerinden seçilmemeli.

### 4B. Hazır, küçük ve ortak statik anlamsal kodlayıcı

Model2Vec, bir Sentence Transformer'dan sabit token vektörleri çıkarıp çıkarımda bunları hafifçe birleştirir; Potion modelleri ilave eğitim kullanabilir [1]. `potion-retrieval-32M` aramaya yönelik somut bir adaydır [1b]. Bu aile önceden eğitilmiş modelden türetilir; eski dondurulmuş nöralsiz görevle aynı protokol değildir. Ayrı araştırma hattı gerekir. Model adındaki 32M parametre sayısıdır; 32 MB diye raporlanamaz.

Önerilen servis: bütün arşivler için tek model/tokenizer, mümkünse tek ortak projeksiyon/kod kitabı; arşive özgü sadece açıkça sayılan hafif istatistikler ve paketli kodlar. Mevcut 96/192/384 kodlar aynen korunmaz, belgeler yeniden kodlanır. Önce float gösterimin kalite tavanı, ardından 24/48-bayt kodları ölçülür. Ortak modelin boyutu, tek arşiv ve çok arşiv kullanımında ayrı amorti edilir. İsim/tarih/sayı ayrımında kötüleşme ihtimali özellikle sınanır; hız/kalite kazancı henüz gösterilmiş değildir.

## 5. Puanlama için tek, sınanabilir tanı adayı

PerLTQA'da float_std192 -> float_std384 da 57,78 -> 54,49 düşüyor; dolayısıyla gerilemenin tamamını işaret kuantizasyonuna bağlamayız. Küçük varyanslı son koordinatların standartlaştırma sırasında gereğinden fazla etkili olması bir hipotezdir, saptanmış neden değildir.

Kovaryans shrinkage yaklaşımı, küçük/kararsız ölçekleri düzenlemeye bir kontrol sunar [8]. Örneğin yalnız diyagonal puanlamada `sigma_tilde_j^2 = (1-alpha)*sigma_j^2 + alpha*mean(sigma^2)` denenebilir. Bu, burada önerilen bir aktarım; Ledoit-Wolf'un tam yöntemi veya onun arama garantisi diye sunulmaz. Alpha sadece dokümanlardan tanımlanan bir kuralla veya ayrı geliştirme verisinde seçilir. Geniş katsayı taramasıyla aynı testten kazanan seçilmez. İyi kovaryans tahmini iyi FR@3 garantisi değildir. Daha önceki alpha kuvveti taraması da ilgili tarihsel kontrol olarak saklanır.

## 6. Adil sistem referansı: BM25S

BM25S, BM25 katkılarını indekslemede hesaplayıp seyrek matrislerde saklayan hızlı bir uygulamadır [6]. Bu kaynak doğrudan yeni kalite iddiası değil, güçlü CPU uygulaması kontrolüdür. Önce tokenizer, stopwords, n-gramlar, IDF formülü, k1/b ve ties eski BM25 koluyla eşlenip sorgu bazlı skor/sıralama kontrolü yapılmalıdır. Kütüphane varsayılanı otomatik olarak aynı BM25 değildir.

Mevcut raporda PerLTQA'nın 24-bayt kolu 54,82 FR@3, eşlenmiş BM25 60,14. Bu fark kapanmadan genel üstünlük iddiası yok. Aynı süreçte ham metin/kimlik döndürme, build/update, sıcak ve ilk-yükleme sorgusu, toplam RSS/USS, veri-bağımlı ek RAM ve seri dosya boyutu ölçülmeli. 1, 10 ve 100 aktif arşiv koşulları kapasite elverdiği ölçüde önceden belirlenmeli; OOM veya kaynak sınırlaması sonucu da korunmalı. Runtime maliyeti arşiv sayısıyla körlemesine çarpılmamalı.

Eski RealTalk RRF aday havuzu tamamlayıcılığı, hibrit için gerekçe olabilir; bu gerçek yeniden-sıralama FR@3 artışı olarak sunulmaz. Yeni birleşime BM25 ve güçlü float kontrolünde de aynı ikinci aşama verilmeli.

## 7. Daha sonra: faydalı önekler / kademeli okuma

Matryoshka Representation Learning, kısa önekleri de yararlı olacak şekilde eğitilmiş temsillere örnek verir [7]. Mevcut üç boyut bağımsız satır normalleştirme ve merkezleme taşıdığından birbirinin hazır kod öneki değildir. Tek 48-bayt kodun ilk 24 baytıyla aday bulup yalnız adaylarda kalan kısmı okumak, ayrı tasarlanıp doğrulanabilecek bir sistemdir. Saklama 48 bayttır, 24 değildir. Paylaşılan kodlayıcı ucuzlamadan, şu anda küçük olan tarama süresini azaltmayı ana öncelik yapmayız.

Hippocampus [9], kompakt imza ile kayıpsız içerik erişimini beraber tasarlayan yakın sistem referansıdır. Bizde ölçülmüş kazanç sayılmaz. Tam uygulama maliyeti; sorgu işleme, varsa model çağrıları ve yardımcı indekslerle birlikte ele alınmalıdır.

## 8. Durdurma ve kabul kuralları

24-bayt exact-qscale, mevcut 12-bayt üretim referansı ve 48-bayt alternatif değişmeden kontrol olarak kalır. Ana ölçüt bütün sorularda FR@3; hit@10 ve FR@100 ikincildir. Alt bantlar tanısaldır, gold kullanarak çalışma-zamanı seçici kurmak yasaktır. Ayrı bir yeni/kör küme olmadan nihai genel başarı sözü yok.

Paylaşılan kodlayıcı için karar: aynı kalite düzeyinde toplam maliyeti düşürmesi ya da aynı toplam maliyette daha yüksek kalite vermesi. Sabit-bütçeli kod için karar: aynı sözleşmeyle gerçek paketli çalışmada güçlü kontrolü iyileştirmesi. Kabul edilebilir kalite kaybı varsa eşiği sonuçlardan önce ürün hedefi olarak yazılmalı; anlamsız fark eşdeğerlik kanıtı sayılmaz.

Yeni adayın float gösterimi zaten zayıfsa, bit kuantizasyonunu parlatmadan önce kodlayıcı hattı durdurulup tanı yapılır. Temsil ve kuantizasyonun birlikte değiştiği sonuç ayrı deney ailesi olarak etiketlenir.

## 9. Bu oturumdaki tek yeni hesap: tam metin tekrarları

`count_exact_duplicates.py`, önceki deney ZIP'indeki 510 girdi JSON'unun doküman metinlerini UTF-8, sıfır normalizasyon ve SHA256 ile saydı. Sonuç `EXACT_TEXT_DUPLICATION.json` içinde. ZIP SHA256: `3848f7cb35be20eca019c9832944b1e6e90e7b94904dbc582d15658adef5d6c3`.

LME 231606 kayıt / 230904 farklı tam metin; tekrar eden ilave kayıtların oranı %0,3031. Tekilleştirmede ham UTF-8 metin baytı 237865248 -> 237727010. PerLTQA 12288 / 12121; LoCoMo 5882 / 5882. Bu ölçüm semantik/yakın tekrarları, zaman damgası çıkarıldıktan sonraki tekrarları veya modellerdeki paylaşılan kelime/karakter yapılarını ölçmez. Sonuç: yalnız birebir metin kopyalarını kaldırmak büyük model durumunun açıklanmış bir çözümü değildir. Ortak kodlayıcı fikri bundan farklıdır. Yeni arama/CPU/RAM deneyi yapılmadı.

## 10. Kaynaklar — erişim 16 Eylül 2026

[1] Minish, Model2Vec Introduction — resmi yöntem belgesi. https://minish.ai/packages/model2vec/introduction/

[1b] MinishLab, potion-retrieval-32M — yazar model kartı. https://huggingface.co/minishlab/potion-retrieval-32M

[2] scikit-learn, HashingVectorizer — resmi dokümantasyon. https://sklearn.org/stable/modules/generated/sklearn.feature_extraction.text.HashingVectorizer.html

[3] Felix Yu, Sanjiv Kumar, Yunchao Gong, Shih-Fu Chang. Circulant Binary Embedding. ICML / PMLR32(2), 2014. https://proceedings.mlr.press/v32/yub14.html

[4] RaBitQ yazar kütüphanesi — bir ve çok-bit yöntem açıklamaları. https://vectordb-ntu.github.io/RaBitQ-Library/rabitq/rabitq/

[5] Faiss, The index factory — resmi kodlama maliyet tablosu. https://github.com/facebookresearch/faiss/wiki/The-index-factory

[6] Xing Han Lù. BM25S: Orders of magnitude faster lexical search via eager sparse scoring. 2024 teknik rapor. https://arxiv.org/abs/2407.03618

[7] Aditya Kusupati ve arkadaşları. Matryoshka Representation Learning. 2022. https://arxiv.org/abs/2205.13147

[8] scikit-learn, Covariance estimation / Shrunk covariance — resmi dokümantasyon. https://scikit-learn.org/stable/modules/covariance.html#shrunk-covariance

[9] Yi Li, Lianjie Cao, Faraz Ahmed, Puneet Sharma, Bingzhe Li. Hippocampus: An Efficient and Scalable Memory Module for Agentic AI. MLSys2026. https://proceedings.mlsys.org/paper_files/paper/2026/hash/a1d04870cf83a0f29819d66f1dfdbfcb-Abstract-Conference.html

MHR önceki literatür envanterinde mevcut; bu oturumda arXiv/yazar sayfası tam erişimi sağlanamadığından yeni teknik önerinin kanıtı olarak kullanmadık. Yukarıdaki yöntemlerin LLMZIP verilerindeki yeni uygulaması bu oturumda çalıştırılmadı. Kaynakların ilan ettiği hız/başarı çarpanları bizim deneyimize taşınmadı.
