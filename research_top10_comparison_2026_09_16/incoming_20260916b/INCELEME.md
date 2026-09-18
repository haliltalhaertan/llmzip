# LLMZIP — External Audit 3 yorumunun matematiksel karşı incelemesi

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Kapsam ve karar

İncelenen kaynak, kullanıcının aktardığı özet ve `haliltalhaertan/llmzip` deposunun `c31719bf26adc6f5c046db5941247d1e60b7feeb` commit'indeki `research_top10_comparison_2026_09_16/EXTERNAL_AUDIT3_RESPONSE.md` koordinatör yanıtıdır. Commit iki Markdown dosyası değiştirir. Bu commit'in araştırma alt ağacının recursive envanteri alındı (`truncated=false`). Adı `audit3_*` olan özgün denetim kodu/ham boyut merdiveni bu alt ağaçta elde edilemedi; Library aramaları da özgün paketi sağlamadı. Bu, dosyaların başka yerde bulunmadığı iddiası değildir.

Bu inceleme yeni bir LLMZIP benchmarkı veya özgün audit3'ün bağımsız yeniden üretimi değildir. Bu oturumda `verify_math.py` çalıştırıldı: tüm girdileri sentetik olan üç karşıörnek, 40 rastgele ortogonal altuzay kontrolü, kaynak tablonun aritmetik farkları ve veri-türü/bellek hesabı. Hiçbir uzak dosya değiştirilmedi.

Karar: Rastgele altuzay kontrolü ve boyut merdiveni yararlı deneylerdir. Buna karşılık “başka hiçbir 96 yön seçimi daha iyi olamaz”, “döndürme dahil tüm araştırmalar kavramsal olarak ölü” ve “384 boyut deneyi 48 baytın yeterli olduğunu kanıtlıyor” sonuçları gösterilen kanıtlardan çıkmaz. Matematiksel olarak yalnız ortalama yeniden oluşturma kısıtı vardır; bu bir arama başarısı tavanı değildir.

## 1. İz özdeşliği ne söyler?

N satır ve k ortonormal sütunlu U için H=UU^T olsun. Her i için

    rho_i = H_ii = ||U[i,:]||^2,
    0 <= rho_i <= 1,
    sum_i rho_i = tr(H) = k.

Dolayısıyla tüm N satırın eşit ağırlıklı ortalaması k/N'dir. Bu, her satırın k/N aldığı, k/N'nin tek tek satırlar için alt sınır olduğu veya hiçbir satırın bunun üstüne çıkamayacağı anlamına gelmez.

Haar-rastgele k-boyutlu bir altuzay için dönme simetrisi E[H]=cI verir; trace alınca c=k/N. Böylece sabit birim x yönünün rastgele projeksiyonda beklenen korunma göstergesi k/N olur. Bu bir beklentidir, en iyi olası seçim sınırı değildir.

### Çalıştırılan somut kontrol

N=500, k=96; ilk 96 koordinat yönünü seçen U kullanıldı. İlk 50 satır öncelikli altküme olarak tanımlandı.

- Öncelikli 50 satırın her birinin rho değeri 1.
- Geri kalan 450 satırın ortalaması 46/450 = 0,102222...
- Tüm satırların ortalaması değişmiyor: 96/500 = 0,192.
- trace tam 96; U^T U=I kontrolü geçti.

Bu, bazı yönleri daha iyi korumanın başka yönlerden bütçe alarak mümkün olduğunu gösterir. Gerçek aramada yararlı önceliklerin gold kullanılmadan bulunabildiğini veya bu örneğin iyi bir üretim yöntemi olduğunu göstermez.

### Singleton terimlerinin sayısı ile bağımsız yön sayısı aynı değildir

Aynı kayıtta tekil olarak bulunan çok sayıda özellik, a_t e_i biçiminde aynı doküman yönüne paraleldir. 95.119 singleton sütunu, 95.119 bağımsız doküman yönü demek değildir. i kaydında m_i singleton terim varsa, bu terimler üzerindeki eşit ağırlıklı ortalama

    sum_i m_i rho_i / sum_i m_i

olur; genel olarak k/N değildir. Önceki k/N singleton örneği, her satırda bir ayrı singleton bulunan özel düzeni açıkça varsayıyordu.

Rastgele kontrolün hangi uzayda yapıldığı da yazılmalı: doküman uzayı N, tam özellik uzayı D ve satır uzayının sayısal rankı r farklı boyutlardır. k/N formülünü otomatik olarak her tür random-projection kontrolüne taşımamak gerekir. Standart kesilmiş SVD için Z_k=H Z=ZP eşitliği vardır; keyfi seçilmiş sol H ve sağ P müdahaleleri genel olarak aynı deney değildir.

## 2. Daha güçlü karşıörnek: her özelliğin korunması aynı, arama farklı

Tamamen sentetik Z=I_512 matrisi kuruldu. Her dokümanın tek ayrı özelliği var. Sorgu e_i, doğru dokümanı i; her sorgunun tek gold kaydı var. Bu birebir eşleşme görevidir, doğal dil/semantik retrieval testi değildir.

Hadamard matrisinden 96 ortonormal sütun seçilerek iki farklı rank96 harita oluşturuldu. Bütün tekil değerler 1 olduğundan ikisi de eşit Frobenius hatalı geçerli en iyi rank96 SVD çözümleridir. Bu dejenerasyon sentetik örneğin açık bir özelliğidir; evrensel imkânsızlık önermesini çürütmek için yeterlidir, gerçek arşivlerde aynı dejenerasyon veya başarı beklenmez.

Her iki kola aynı satır normalleştirmesi, ortalama çıkarma ve işaret kodlama uygulandı.

| Ölçü | Çakışan kodlu harita | Ayrı kodlu harita |
|---|---:|---:|
| Sürekli boyut | 96 | 96 |
| Her singleton için korunma | 96/512 = 0,1875 | 96/512 = 0,1875 |
| Toplam kare yeniden oluşturma hatası | 416 | 416 |
| Bütün 512 dokümanın paketli kod toplamı | 6.144 bayt | 6.144 bayt |
| Farklı kod sayısı | 128 | 512 |
| Kod çakışma grubu büyüklüğü | 4 | 1 |
| Uniform eşitlik altında hit@1 | %25 | %100 |
| Uniform eşitlik altında FR@3 | %75 | %100 |

İlk kolda her kod dört dokümanı aynı gruba koyuyor; doğru kaydın ilk üçte bulunma olasılığı 3/4. İkinci kolda doğru kaydın sıfır Hamming mesafeli kodu tekil. Her özellik için aynı korunma olmasına rağmen sıralama farklıdır.

Bu nedenle enerji/yeniden oluşturma ölçüsünden bit kodlarının veya FR@3'ün en iyi olası değerine geçilemez. Bu örnek “LLMZIP %100'e çıkar” iddiası değildir. Ortak haritaların depolama maliyeti doküman-kod tablosuna dahil değildir; iki harita aynı biçim ve boyutta tutulur.

## 3. Döndürme, mutlaka farklı altuzay seçmek değildir

q=(0,8;0,01), A=(0,8;-0,01), B=(0,01;0,8) alındı; dokümanlar A,B,-A,-B. Böylece birimleme sonrası ortalama sıfır. A, q'ya sayısal olarak çok daha yakın.

- Önce: q ile A'nın işaretleri 1 bit, B'nin 0 bit farklı; Hamming B'yi öne alıyor.
- Aynı ortogonal 45 derecelik dönüşümden sonra: A 0 bit, B 1 bit farklı; Hamming A'yı öne alıyor.
- Kosinüsler her iki durumda yaklaşık 0,99968755 ve 0,02499609; değişmiyor.

Boyut ve sürekli altuzay aynı; yalnız eksenler değişiyor. Dolayısıyla altuzay seçim kısıtı, o altuzay içindeki eksenlerin işaret kodlama üzerindeki etkisini yasaklamaz. Bu tek sentetik örnek ITQ'nun bizim verilerde kazanacağını göstermez.

## 4. Boyut merdiveninin doğru kapsamı

Koordinatör yanıtında nadir ortak-terim grubunun FR@3 değerleri şöyle:

| Veri | BM25 | 96 | 192 | 384 | Tam karışık Z | Yalnız kelime |
|---|---:|---:|---:|---:|---:|---:|
| PerLTQA (5.694 soru) | 72,15 | 65,17 | 70,12 | 72,61 | 72,70 | 69,98 |
| LoCoMo (950 soru) | 58,70 | 24,82 | 32,96 | 40,13 | 45,17 | 57,42 |

Bu ölçümler bu oturumda yeniden üretilmedi. Doğru ve aynı kohort/puanlama koşullarında üretildikleri kabul edilirse, bu yöntem ailesinde boyut artışının bu gruplarda yararlı olduğunu destekler. Başka 96-boyutlu seçimlerin veya 96-bit kodlayıcıların daha iyi olamayacağını göstermez.

384 boyutun değerlendirmede float mı, işaret kodu mu, standartlaştırılmış kosinüs mü veya sayısal-sorgu asimetrisi mi kullandığı açıkça doğrulanmalıdır. Elde edilen yanıt dosyası bunu tam belirtmiyor; özgün audit3 merdiven kodunu alamadım. Bu nedenle 72,61 değerini 48 baytlık çalışan koda atfetmiyorum.

Aynı 1.000 doküman için, yardımcı modeller hariç yalnız dizi hesabı:

- 384 paketli işaret: 48.000 bayt.
- 384 float32 koordinat: 1.536.000 bayt.
- 384 float64 koordinat: 3.072.000 bayt.

384 koordinat ancak her biri gerçekten tek işaret bitiyle saklanıp o biçimde puanlandığında 48 baytlık kod olur. Önce sürekli 384 boyutta ölçüp daha sonra işaret almanın kaliteyi koruduğunu varsaymak geçerli değildir.

PerLTQA'da 72,61-72,15=+0,46 puanın anlamsız bulunması eşdeğerlik veya minimum yeterli bütçe ispatı değildir. Üstelik tablo yalnız nadir gruba ait; bütün soruların ve diğer veri kümelerinin sonucu değildir. LoCoMo'da full Z dahi BM25'in 13,53 puan gerisindedir; tablonun kendisi “yalnız bütçe eksik” açıklamasını bütün verilere genellemez.

## 5. Diğer yorumların kapsamı

### Özellik karışımı

LoCoMo için paylaşılan sayılarda toplam fark 58,70-24,82=33,88 puan. Ardışık farklar:

- 96 -> tam Z: +20,35 (%60,06).
- Tam Z -> yalnız kelime: +12,25 (%36,16).
- Yalnız kelime -> BM25: +1,28 (%3,78).

Bu aritmetik doğru. Yüzdeler seçilen müdahale sırasındaki gözlenen fark paylarıdır, genellenebilir nedensel sorumluluk payları değil. Tam Z=[LSA32|kelime|karakter] ise doğrudan yalnız kelimeye geçmek hem LSA'yı hem karakteri hem de karışımın normalize ağırlığını değiştirir. Karakterin tek başına 12,25 puan sorumlu olduğunu söylemek için LSA sabitken karakter aç/kapat ve tercihen 2x2 etkileşim kontrolü gerekir.

### Sıradan/ortak-kelime grubu

Goldla ortak terime göre tanımlanan grup tanısaldır; çalışma zamanında gold bilinmeden uygulanabilen kural değildir. BM25 sıfır üretiyorsa sıfırın hangi kayıtlara ait olduğu (gold skoru mu, bütün arşiv skorları mı) açıkça yazılmalıdır. BM25'in işlemediği grup üzerinde başka sistemin ölçülmüş başarı göstermesi otomatik anlamsız olmaz; fakat bundan genel üstünlük, nadirlik nedenselliği veya kolay yönlendirme sonucu çıkarılamaz. “Anlamlılık otomatik” ifadesi de örneklem ve gerçek fark kontrol edilmeden doğru değildir.

### Eşit puanlar

Goldları kullanıp en iyi olası sıralamayı vermek bir oracle kontrolüdür. Tarafsız uniform-tie beklentisiyle elde edilen ölçümün hatalı veya şişirilmiş olduğunu tek başına göstermez. Eşitliklerden kaynaklanan çözünürlük kaybı yine pratik bir sorundur; oracle kazancı gerçek kullanıcının elde ettiği kazanç sayılmamalıdır.

### BM25 ve maliyet

Aynı tokenizerla ve kuvvetli BM25 kontrolleriyle kıyaslama faydalıdır. Sonradan seçilmiş en iyi parametreler ayrı doğrulama gerektirir. 213 MB ile 64 MB ancak aynı nesneleri sayıyorlarsa doğrudan düzeltme çifti olur. Bizim önceki Fikir1 raporumuzdaki 63,982 MB, BM25 istatistik JSON'udur; tam ters indeks/RSS değildir. Posting, sözlük, ham metin, kodlayıcı, geçici tampon ve kalıcı/çalışma zamanı ayrımı korunmalıdır.

## 6. Sonraki deneye uygun karar

Boyut merdiveni yapılmaya değer. Ancak sonucu baştan “48 bayt gerekli” diye etiketlememek gerekir. 96/192/384 için aynı arşiv ve sorularda üç ayrı puanlama dalı ölçülmeli:

1. Sürekli koordinatların açıkça tanımlanmış float puanlaması.
2. Paketli işaret kodu + Hamming.
3. Aynı paketli kod + sayısal sorgu/qscale.

Böylece boyut indirgeme kaybı ile işaret kuantizasyonu ayrılır. Sabit tokenizer, aynı doğru kanıt kimlikleri, ortak soru kümesi, çözümleyici/tohum kontrolü, sıfır-rank/düşük-rank kayıtları ve tek eşitlik kuralı gerekir. N<384 durumunda soru dışlayıp kohortu değiştirmek yerine gerçekleşen rankı/kodu açıkça raporlamak veya baştan belirlenmiş ortak panel kullanmak gerekir.

Nadir grup ikincil tanı olsun; ana karar bütün soruların FR@3'üyle verilsin. Düşük bütçeli mevcut yöntemler, kuvvetli BM25 ve aynı temsilin float kontrolü korunsun. Kodlayıcı dahil toplam saklama, tepe/yerleşik RAM, kurulum ve metinden sonuca CPU/gecikme ayrı ölçülsün. Yeni ayarlar yalnız bu zaten görülmüş benchmarklara göre seçilirse keşifsel statü değişmez.

Son durum: Mevcut 96-bit yöntemin bazı koşullarda yetersizliği ciddi bir deney bulgusudur. “96-bit yöntemler geliştirilemez” matematiksel olarak gösterilmiş değildir. Aynı şekilde elde edilen belge, 48 baytlık kodun hedef kaliteyi verdiğini veya gerekli minimum bütçenin 48 bayt olduğunu ispatlamaz.

## Kaynak ve yeniden üretim

Proje kaynakları:

- https://github.com/haliltalhaertan/llmzip/commit/c31719bf26adc6f5c046db5941247d1e60b7feeb
- https://github.com/haliltalhaertan/llmzip/blob/c31719bf26adc6f5c046db5941247d1e60b7feeb/research_top10_comparison_2026_09_16/EXTERNAL_AUDIT3_RESPONSE.md
- Önceki MATEMATIK_INCELEME.md §§4,9 ve KONTROL_VE_DENEY_EKI.md §1: k/N'nin satır ortalaması olduğu, singleton kelime ortalamasının özel koşulu ve 96 sürekli boyutun 96 bitten ayrılması zaten kayıtlı.
- Önceki LLMZIP_FIKIR1_RAPORU_2026-09-16.md §8: 63,982 MB istatistik JSON, tam servis RAM'i değil.

Yöntem tanımlarının birincil kaynakları; yeni sentetik sonuçlar bu yayınlardan alınmadı:

- Drineas vd. (2012), Fast Approximation of Matrix Coherence and Statistical Leverage: https://www.jmlr.org/papers/v13/drineas12a.html
- Manning, Raghavan, Schütze, Low-rank approximations: https://nlp.stanford.edu/IR-book/html/htmledition/low-rank-approximations-1.html (yalnız SVD'nin Frobenius minimizasyon amacı için).
- NumPy veri türleri: https://numpy.org/doc/stable/user/basics.types.html

Çalıştırma:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_math.py

Sonuç: MATH_RESULTS.json; günlük: STDOUT.txt. Scriptte tüm sentetik girdiler, seed ve kontroller açık. Matematiksel counterexample yeni bir yöntem/öncelik iddiası değildir. Bu inceleme dış bağımsız denetçi onayı değildir.
