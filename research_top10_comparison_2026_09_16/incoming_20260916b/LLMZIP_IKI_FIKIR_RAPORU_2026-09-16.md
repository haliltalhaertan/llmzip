# LLMZIP — İki fikrin gerçek deneyi: 24 bayt hassasiyet tahsisi ve daha küçük kodlayıcı

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. Kapsam ve kararın sınırı

Bu çalışma önceki 12/24/48 bayt merdiveninin **aynı 510 arşiv / 10.266 soru / 249.776 kaydında** çalıştırıldı: LME 470/470/231.606, PerLTQA en_v2 30/8.265/12.288, LoCoMo 10/1.531/5.882. Yeni/gizli veri değil. Önceki adapter ve gold kimlikleri korundu; içerik etiketleri yeniden uzman anotasyonundan geçirilmedi. RealTalk kaynak kohortta olmadığı için çalıştırılmadı. Hiçbir soru sonuç nedeniyle dışlanmadı.

İki ana fikir ayrı tutuldu. A: aynı 24 baytı daha az koordinatı daha hassas tutarak kullanmak. B: kodlayıcı maliyetini azaltmak. B içinde iki açıkça ayrı aday var: aynı gösterimin cebirsel olarak yeniden faktörlenmesi ve daha radikal küçük ortak rastgele kodlayıcı. İkisinin kazançları toplanmadı, iki-bit ile küçük kodlayıcı tek kazanan hibritte birleştirilmedi.

Ana ölçüt gerçek deterministik FR@3: gereken kanıt kayıtlarının ilk üçte bulunan ortalama payı. Cevap doğruluğu veya başarılı soru oranı değil. Hit@10 ayrı ikincil ölçüttür. Eşitlik sırası önceki SHA256(top10-r1|archive|row) kuralıdır; gold ile eşitlik çözme yok.

## 2. Gerçek paketli kodlarla kalite (%)

| Veri | Mevcut 192×1 | 96×2 kosinüs (ana) | 96×2 iç çarpım (ikincil) | Küçültülmüş aynı kodlayıcı | Ortak rastgele kodlayıcı (ana seed) |
|---|---:|---:|---:|---:|---:|
| LongMemEval | 61,48 | 54,41 | 54,76 | 61,48 | 29,17 |
| PerLTQA en_v2 | 54,82 | 55,49 | 55,29 | 54,82 | 26,90 |
| LoCoMo | 41,21 | 37,46 | 37,39 | 41,21 | 18,59 |

Hit@10 (%):

| Veri | Mevcut 192×1 | 96×2 kosinüs (ana) | 96×2 iç çarpım (ikincil) | Küçültülmüş aynı kodlayıcı | Ortak rastgele kodlayıcı (ana seed) |
|---|---:|---:|---:|---:|---:|
| LongMemEval | 89,15 | 87,66 | 88,09 | 89,15 | 54,04 |
| PerLTQA en_v2 | 80,71 | 82,87 | 82,29 | 80,71 | 50,44 |
| LoCoMo | 62,12 | 57,61 | 58,46 | 62,12 | 32,01 |


Bu karşılaştırmada her kodlu satır gerçek **24 bayt/doküman** saklar. Hazır float/±1 doküman matrisi servis puanlamasında tutulmaz. Geniş float dizileri yalnız kalite kontrol hesabında ve ayrı süreçlerde kullanıldı. 192×1 referansı önceki exact Gram ailesidir, eski randomized96 üretiminin yeniden adlandırılması değildir.

## 3. Fikir A — 96 koordinat × 2 bit

Dokümanların exact96 merkezlenmiş koordinatları doküman standart sapmalarına bölündü. Dört seviyeli simetrik standart-normal Lloyd–Max MSE nicemleyicisi kullanıldı. Eşik ve temsil değerleri **normal dağılım integralinden**, hiçbir benchmark veya sorgu/gold görülmeden sayısal olarak çözüldü:

```
eşik: ±0.981598821567794 ve 0
seviyeler: -1.5104176084990955, -0.45278003463649225,
            0.45278003463649225,  1.5104176084990955
```

Bu bir Gauss-modeli tercihi; gerçek koordinatların Gauss olduğunu ispatlamadık. Bütün arşivlerde aynı seviyeler kullanılır, veri kümesine göre eşik seçilmez. Gerçek dört-seviye kodları byte-plane biçiminde paketlendi. Kullanıcının ilk fikrinin sınırlı bir prototipidir; bütün iki-bit nicemleyicilerin optimumu değildir.

Ana skor, standartlaştırılmış sayısal sorgu ile koddan yeniden oluşturulmuş dokümanın kosinüsüne sıralama bakımından eşdeğerdir. Doküman normu değişken olduğu için **koddan her puanlamada hesaplanır**; saklı kayıt-başına norm veya büyük sayı matrisi yoktur. Sorgunun pozitif ortak normu sıralamayı değiştirmediğinden bölünmez. Aynı kodun iç-çarpım sürümü baştan ikincil olarak tanımlandı; sonuca bakıp ana yöntem seçilmedi. 2-bit ve sign192 C çekirdekleri benzer 4-bit-LUT/AVX-512 düzeninde çalışır; CPU maliyetine gerçek norm hesabı dahildir.

Bu iki-bit kolu 192 yönün ilk yarısına yalnız sayı eklemek değildir: exact96 ve exact192 kendi normalleştirme/merkezleme/sigma değerlerini kullanır. Aynı bayt bütçesinde boyut–hassasiyet değiş tokuşu sınanır.

### Ana FR@3 farkları — A eksi mevcut 24 bayt

| Veri | Fark (yüzde puan) | Keşifsel %95 aralık | İyileşen / gerileyen soru |
|---|---:|---|---:|
| LongMemEval | -7,07 | [-9,86; -4,31] | 36 / 90 |
| PerLTQA en_v2 | 0,67 | [-0,11; 1,46] | 657 / 622 |
| LoCoMo | -3,75 | [-5,08; -2,68] | 88 / 143 |

Aynı96 koordinatı 12 bayt yerine24 baytta daha hassas tutmanın karşılığı da kontrol tablosunda görülebilir: bu, asıl eş-bütçeli karşılaştırmadan ayrı bir kontrol.

| Veri | 96×1, 12 B kontrol | 96×2, 24 B aday | 192×1, 24 B referans |
|---|---:|---:|---:|
| LongMemEval | 52,47 | 54,41 | 61,48 |
| PerLTQA en_v2 | 52,98 | 55,49 | 54,82 |
| LoCoMo | 35,11 | 37,46 | 41,21 |


20.000 eşleştirilmiş arşiv-bootstrap tekrarı, seed2026091604; tekrar içinde soru sayısıyla ağırlıklı fark. PerLTQA 30, LoCoMo yalnız 10 küme. LME arşivlerinin ortak içerikleri olabilir. Aralıklar bağımsız nüfus garantisi veya çoklu deneme düzeltmeli teyit değildir. Başarıya göre seed/kohort seçimi yapılmadı.

## 4. Fikir B1 — Aynı kodlayıcının daha küçük matematiksel yazımı

Mevcut kelime-LSA projektörü sözlük büyüklüğü ×32 float64 sayı tutuyor. W, normalize kelime-TFIDF doküman matrisi; R, mevcut öğrenilmiş LSA sağ projektörü olsun. Yeni bir LSA eğitmek yerine:

```
R = Wᵀ B
B = (WWᵀ)^+ W R
Lq = normalize((Wq Wᵀ) B)
```

özdeşliğini sayısal olarak doğruladık. Bu eşitlik ancak R'nin sütunları W'nin satır uzayındaysa geçerlidir; her arşivde geniş R yeniden oluşturularak artık kontrol edildi. Sıfıra yakın Gram özdeğerleri max×1e-12 eşiğiyle ayrıldı; gate başarısızlığında sessiz gevşetme/dışlama yoktur.

Arşiv başına büyük R kaldırılır. Wᵀ, karakter matrisi Hᵀ, doküman LSA koordinatları L ve küçük B tutulur. Final SVD'nin A192 projektör faktörü, mean/sigma ve aynı paketli kayıt kodları korunur. Sorgu çapraz puanı:

```
Zq Zᵀ = Wq Wᵀ + Hq Hᵀ + Lq Lᵀ
```

olarak hesaplanır; kelime çapraz hesabı LSA için de tekrar kullanılır. Eski Zᵀ ayrıca bellekte tutulmaz. Kelime/karakter sözlükleri hâlâ vardır. **Bu ortak/paylaşılan bir kodlayıcı değildir; aynı arşive özel kodlayıcının daha küçük bir uygulamasıdır.** Arşive özel maliyet tamamen kaldırılmış değildir.

Doküman kodlarının değişmemesi tasarım gereğidir; asıl sadakat sınaması bütün gerçek sorguların yeni yoldan kodlanması ve sonuç listelerinin karşılaştırılmasıdır. Sonuç: bütün sorularda ilk-10 listesi aynı. Bu gerçek verideki sayısal doğrulamadır, her olası sorguda bit-birebir kayan-nokta özdeşliği teoremi değildir. Yeni kayıt ekleme, akış güncelleme ve yeniden eğitim politikaları ayrıca sınanmadı.

### Arşiv model dosyalarının toplam boyutu (MB, RAM değildir)

| Veri | Mevcut 24 baytlı model durumu | Küçültülmüş aynı model durumu | Azalma |
|---|---:|---:|---:|
| LongMemEval | 10130,21 | 5433,87 | %46,36 |
| PerLTQA en_v2 | 157,21 | 106,66 | %32,15 |
| LoCoMo | 56,05 | 40,57 | %27,61 |

Bu değerler runtime durumlarının pickle5 serileştirmesinin gerçek byte uzunluklarıdır; tüm modellerin aynı anda RAM'e yüklendiği iddiası değildir. Kaynak metin, kimlik ve yardımcı diziler bu nesnelere dahildir. Sadece panel modelleri diskte tutuldu; diğerlerinde pickle byte dizisinin boyutu ölçülüp bırakıldı.

## 5. Fikir B2 — Çok daha küçük, arşivlerce paylaşılan rastgele dönüşüm

Ayrı, daha radikal bir aday da gerçekten çalıştırıldı: kelime1–2 ve karakter3–5 parçaları iki ayrı8192-kutulu signed hashing kanalına dönüştürülür; işaretli sublinear TF ve **yalnız dokümanlardan** hesaplanan kutu-IDF uygulanır. Sözlük yoktur; her arşivde iki8192 IDF dizisi kalır. Normalleştirilmiş16384-boyutlu gösterime ortak rastgele işaret diyagonali ve Gauss döngüsel filtre uygulanır. FFT ile hesaplanan ilk192 koordinat normalleştirilir, doküman ortalaması çıkarılır, 192bit oluşturulup aynı qscale ailesiyle okunur.

Paylaşılan rastgele ağırlıklar üç sabit seed için oluşturuldu:2026091601/02/03. İlk seed baştan ana olarak tanımlandı. Diğerleri duyarlılık kontrolleridir; en iyi seed seçilmedi. Yerel IDF/mean/sigma, metinler ve kodlar maliyete dahil. Toplam depolama hesabında ortak filtre yalnız bir kez sayılır; tek aktif servis sürecinin RSS'sinde ise gerçekten yüklü bir kopyası bulunur.

Bu **CBE'nin eğitilmiş sürümünün veya makalenin tam uygulamasının benchmarkı değildir**. CBE-random fikrinden esinlenen, bu projeye ait hashing+IDF+circulant prototipidir. Aynı anda özellik ve dönüşüm ailesi değiştiği için sonucun hangi bileşenden geldiğini tek neden olarak ilan etmiyoruz.

### Üç seed, FR@3 (%)

| Veri | Mevcut 24 B | Ana seed | Seed2 | Seed3 |
|---|---:|---:|---:|---:|
| LongMemEval | 61,48 | 29,17 | 26,47 | 29,94 |
| PerLTQA en_v2 | 54,82 | 26,90 | 26,79 | 26,23 |
| LoCoMo | 41,21 | 18,59 | 18,90 | 18,68 |

Daha küçük olmak kaliteyi korumadı. Bu başarısızlık bütün ortak kodlayıcıların, öğrenilmiş veya nöral alternatiflerin başarısızlığı değildir. İki-bit normal nicemleyici gibi, yalnız bu sabit prototip test edildi.

İzdüşüm öncesi hashed özelliklerin cosine kontrolü ayrı saklandı. O kol 24 baytlık kod değildir ve 24 bayt başarısı olarak sunulmaz:

| Veri | Hash özellikleri, sayısal ve projeksiyonsuz | 192-bit ortak rastgele prototip |
|---|---:|---:|
| LongMemEval | 64,44 | 29,17 |
| PerLTQA en_v2 | 57,93 | 26,90 |
| LoCoMo | 44,87 | 18,59 |


## 6. Gerçek CPU ve süreç RAM'i

Önce kalite tamamlandı, sonra kaynak deneyleri seri yürütüldü. Aynı önceki11 arşivlik panel:5 LME,3 PerLTQA,3 LoCoMo; 65 farklı sorgu. Her arşiv/yöntem üç temiz süreçte; sorgu başına7 sıcak tekrar. Toplam132 servis süreci,5.460 zamanlanan uçtan uca çağrı. Ayrıca44 taze indeks-kurulum süreci. Alt-LLM ajanı yok; kalite için iki yerel CPU worker kullanıldı. Kaynak profilleri sırasında bu worker'lar çalışmıyordu.

CPU0'a sabitleme, tek BLAS/OpenMP thread, AMD EPYC9V74/AVX-512, Linux ve4GiB sınırı. Paylaşımlı/sanallaştırılmış ortam. Kapsam: ham sorgu→özellikler→sorgu kodu→LUT/puanlama→aynı ilk10→özgün metin/kimliklerine bellek erişimi. Sorgu tablosu, 2-bit norm hesabı ve hash/FFT dahil. Ağ, soğuk disk, LLM yanıtı, eşzamanlı istek kuyruğu/enerji yok. Kodlayıcı sorgu başına tekrar fit edilmez.

Aşağıdaki CPU değerleri: önce sorgunun7 tekrar medyanı, sonra üç süreç medyanı, sonra sabit paneldeki sorguların ortalaması. Bütün benchmark'ın latency ortalaması veya p95 SLA garantisi değildir.

### CPU milisaniye / sorgu

| Veri | Mevcut192×1 | 96×2 | Küçük aynı kodlayıcı | Ortak rastgele prototip |
|---|---:|---:|---:|---:|
| LongMemEval | 2,60 | 2,78 | 1,34 | 1,64 |
| PerLTQA en_v2 | 1,79 | 1,79 | 1,25 | 1,48 |
| LoCoMo | 1,70 | 1,74 | 1,20 | 1,42 |

### Toplam sıcak süreç RSS, MB

| Veri | Mevcut192×1 | 96×2 | Küçük aynı kodlayıcı | Ortak rastgele prototip |
|---|---:|---:|---:|---:|
| LongMemEval | 204,14 | 203,78 | 183,52 | 163,77 |
| PerLTQA en_v2 | 171,36 | 171,06 | 167,74 | 163,40 |
| LoCoMo | 172,06 | 171,54 | 168,62 | 163,40 |

Bir süreçte bir aktif arşiv ve bir yöntem var. Runtime/kütüphaneler, sözlükler, kaynak metinler, projektörler, kodlar ve tamponlar dahildir. Model dosyasındaki yüzde azalmayı toplam süreç RAM'inin aynı oranda azalması diye okumayın. RSS arşiv panel medyanıdır; kodların payload byte sayısı veya bütün arşivlerin birleşik RSS'si değildir. USS, çalışma zamanı tabanı üstündeki ek bellek, yükleme süresi, sorgu ara aşamaları ve ham tekrarlar JSON/CSV dosyalarındadır.

Kurulum yolları karşılaştırılan her yöntem için kendi gerçek builder'ıyla çalıştırıldı. B1 eski fit işlemini koruyup ek faktörleme yapar; kalıcı boyut azalması kurulumun bedelsiz veya daha ucuz olduğu anlamına gelmez. Tepe fit RSS servis RSS'sinden ayrı raporlanır.

## 7. Doğrulamalar

- 510 kaynak input SHA256 ve plan SHA256 kontrolü; değişmeyen plan: `8192eff3df15c1c8d6e6878b834bc5b68331c20f34b06c1b7f420934466a3eec`.
- Önceki exact96/exact192 referanslarıyla 246,384 skaler metrik kontrolü, en büyük fark 0.0; baseline kayıt kodları aynı.
- B1 için en büyük LSA projektör bağıl artığı 1.320e-13; sorgu koordinatı mutlak farkı 6.645e-14; bütün 10,266 sorguda ilk10 farkı 0.
- Ayrı betikte paketli dosyalar geri okunarak 82,128 sonuç listesi ve 492,768 metrik yeniden hesaplandı; hata 0.0.
- 2550 24-bayt payload kontrolü. 160 sentetik2-bit testinde scalar/SIMD puanları birebir; direkt matris skoruyla maksimum fark test JSON'unda. Metrikler ayrıca1890 küçük durumda3017 sınır kombinasyonuyla kontrol edildi.
- 780 servis sonuç listesi kalite listesiyle aynı; 132 servis ve 44 taze kurulum kod hash'i eşleşti.

Uygulayıcı ve ayrı doğrulama kodunun yazarı aynıdır. Bu dış bağımsız denetçi onayı değildir. Bilimsel iddia/üretim değişikliği yapılmadı; GitHub/Drive/main/dondurulmuş görevlerde değişiklik yok. Karşılaştırılan algoritmalar sonuca göre değiştirilmedi.

## 8. Karar

Dört seviyeli96×2 prototipini genel varsayılan yapmayın: PerLTQA'da küçük/belirsiz iyileşme olsa bile bu boyut–hassasiyet değiş tokuşu diğer verilerde kayıp veriyor. Bu, iki-bit fikrinin matematiksel olarak imkânsız olduğunu değil, bu sabit adayın genel kazanmadığını gösterir.

En somut devam adayı **B1 cebirsel kodlayıcı küçültmesi**. Gösterim ve mevcut24-bayt kodlar korunurken model durumunu küçültüyor; bütün mevcut sorularda ilk10 eşleşiyor. Kaynak maliyetleri gerçek süreçte ölçülmüştür, fakat bu dış denetim veya üretim yükü garantisi değildir. B2 ortak rastgele prototip, küçük olmasına rağmen kalite kaybı nedeniyle mevcut yöntemin yerine konmamalı.

Eski BM25/float referanslarını bu turda tekrar eğitip toplam maliyet profiline sokmadık; bütün rakipleri geçme iddiası yok. İki deneyin sonuçlarını birleştiren hibrit ve ayrı/gizli veri doğrulaması yapılmadı.

## 9. Kaynaklar ve tekrar üretim

Sayısal sonuçların kaynağı bu paketin `results/` dosyalarıdır. Önceki byte-merdiveni arşivi, plan içindeki SHA256 ile tanımlıdır. Araştırma bağlamı için birincil kaynaklar:

- CBE, Yu–Kumar–Gong–Chang, ICML2014: https://proceedings.mlr.press/v32/yub14.html — yapılandırılmış circulant dönüşümün mimari öncülü; bu prototip makale sonucunun tekrarı değil.
- HashingVectorizer resmi API: https://scikit-learn.org/1.9/modules/generated/sklearn.feature_extraction.text.HashingVectorizer.html — feature hashing, alternate_sign, norm. Çalıştırılan sürüm sklearn1.8.0'dır; web sürümü farklıdır. Bin-IDF ve sublinear signed TF bize ait açık eklerdir.

Kod, PLAN_BEFORE_RUN, doğrulamalar, ortam sürümleri ve bütün soru çıktıları pakette. `scripts/replay.py` önceki arşivi hash'leyerek yeni dizinde tekrarı kurar. Kendi bilgisayarınızdaki CPU/RSS rakamlarının aynı olması beklenmez. Python3.13.5, NumPy2.3.5, SciPy1.17.0, sklearn1.8.0, gcc14.2.0.

## Ek: Kurulum tepe RAM ve CPU (tek-geçiş, küçük panel)

| Veri | Kol | Kurulum CPU ort. s | En yüksek kurulum RSS MB |
|---|---|---:|---:|
| LongMemEval | base192 | 1,07 | 240,00 |
| LongMemEval | compact192 | 1,02 | 262,71 |
| LoCoMo | base192 | 0,24 | 187,07 |
| LoCoMo | compact192 | 0,30 | 198,96 |
| PerLTQA en_v2 | base192 | 0,21 | 185,88 |
| PerLTQA en_v2 | compact192 | 0,24 | 198,68 |

Kalıcı/sorgu RAM azalmasına rağmen kompaktlaştırma sırasında geçici tepe RAM daha yüksek olabilir. Tek-geçiş fit sürelerinden genel hız üstünlüğü çıkarılmaz.

İç metaveri kontrolü: Kurulum sonrası RSS özeti için MB adlı alanın başlangıçta byte içerdiği fark edildi ve yayın öncesi 10^6'ya bölünerek düzeltildi. Ham ölçümler, kodlar, sorgu sonuçları ve deney kuralları değiştirilmedi; ayrıntı METADATA_CORRECTIONS.json.
