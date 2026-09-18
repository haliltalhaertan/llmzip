# LLMZIP — bağımsız yeniden benchmark ve CPU/RAM incelemesi

15 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Sonuç

SIGN96 küçük bir indeksle rekabetçi arama kalitesi sunuyor; standartlaştırılmış float referansının kalite üstünlüğü ortadan kalkmadı. Buna karşılık “paketli kod zorunlu olarak yavaştır” sonucu yeniden ölçümde ayakta kalmadı: derlenmiş Hamming aynı kodlar ve aynı mesafelerle, optimize edilmiş standart float32 puanlamasından bu makinede 1,7–1,8 kat hızlı. Bu bir **önceden kodlanmış sorgu puanlama** sonucudur, uçtan uca metin arama hızlanması değildir. Metinden indeks kurmak ve sorguyu kodlamak çok daha pahalıdır. İndeks dizilerindeki büyük bellek kazancı, bütün sürecin RAM’ine aynı katsayıyla taşınmaz.

## 1. Ne gerçekten çalıştırıldı?

| Veri kümesi | Arşiv | Sorgu | İndekslenen kayıt |
|---|---|---|---|
| LongMemEval | 470 | 470 | 231.606 |
| PerLTQA | 30 | 8265 | 12.288 |
| RealTalk | 10 | 705 | 8.944 |

Toplam 510 arşiv, 9.440 sorgu ve 252.838 kayıt; başarı yüzdeleri veri kümeleri arasında birleştirilmedi. Kalite hesabında geçmiş rapor sayıları kopyalanmadı; hash'i doğrulanan gerçek C/qC/gold dizilerinden altı metrik yeniden hesaplandı. **Bu tam kapsamlı sayısal önbellek tekrar oynatımıdır; 510 arşivin tamamının ham metinden yeniden kurulması değildir.**

Ham metinden kontrol paneli: metin karakter sayısına göre sıralanmış 470 LME arşivinden eşit aralıklı 12 sıra, 30 PerLTQA arşivinden eşit aralıklı 6 sıra seçildi. Sonuca göre seçim yapılmadı. Her PerLTQA arşivinde 5, her LME arşivinde 1 sorgu: toplam 18 arşiv, 8.497 kayıt, 42 örnek sorgu. Randomized ve exact Gram ayrı ölçüldü; bir LME arşivinde iki ek tekrar yapıldı. Doğru ayarlı toplam 38 yeni süreç. Bu panel rastgele/popülasyon-temsili örneklem olarak sunulmuyor. RealTalk ham metinden yeniden kurulmadı.

## 2. Arama kalitesi

Hit@10, ilk on kayıtta **en az bir gold/kanıt kaydı** bulunmasıdır; LLM’nin cevabının doğruluğu değildir. Eşit puanlı sınır grubunda tek bir keyfi sıralama yerine uniform seçim altında tam beklenen hit ve fractional recall hesaplandı.

| Yöntem | LongMemEval hit@10 (%) | PerLTQA hit@10 (%) | RealTalk hit@10 (%) |
|---|---|---|---|
| Standartlaştırılmamış float64 | 82,55 | 80,81 | 36,60 |
| Standartlaştırılmış float64 | 88,30 | 83,96 | 48,51 |
| Standartlaştırılmış float32 | 88,30 | 83,96 | 48,51 |
| SIGN96 | 86,08 | 75,76 | 46,68 |
| SIGN88, en yüksek varyanslı koordinatlar | 85,80 | 74,62 | 44,99 |
| SIGN80, en yüksek varyanslı koordinatlar | 84,97 | 74,33 | 42,56 |

Standartlaştırılmış float32 ve float64, yalnız ortalamada değil, **9.440 sorgunun her birinde** hit/recall @3, @10 ve @100 sonuçlarında eşleşti. Sonraki birim-normlu float optimizasyonunda da bu altı metrikte değişen sorgu olmadı. Bu sabit veri ve metriklerdeki gözlemdir; tüm olası sorgularda matematiksel eşdeğerlik iddiası değildir.

| Yöntem | LongMemEval fractional recall@100 (%) | PerLTQA fractional recall@100 (%) | RealTalk fractional recall@100 (%) |
|---|---|---|---|
| Float64 | 95,68 | 91,94 | 57,13 |
| Standart float32 | 95,29 | 85,37 | 65,47 |
| SIGN96 | 90,10 | 80,51 | 57,89 |

Daha fazla kanıtın toplanması istendiğinde yalnız hit@10 yeterli değildir. Örneğin PerLTQA’da standartlaştırılmamış float64, fractional recall@100’de standart float32’den daha yüksek; dolayısıyla “float_std her metrikte en iyi” denemez. Raporun sonuçları metrik-bağımlıdır. Bu oturumda yeni güven aralıkları veya anlamlılık testleri hesaplanmadı; hiçbir fark “bedelsiz” diye adlandırılmadı. LME soruları ortak oturumlar içerebildiğinden bağımsız-popülasyon çıkarımı ayrıca tasarlanmalıdır.

SIGN88/80 seçimleri varyansa göre drop-only kodlardır. Eski B8 veya B8 için ayrılmış farklı bir sign88 koluyla özdeş kabul edilmedi. B8/asym bu oturumda yeniden ölçülmedi. LME SIGN80 hit@10 kaybı 1,11 yüzde puan; RealTalk kaybı 4,12 yüzde puandır. “10 bayt ücretsiz” sonucu çıkarılamaz.

## 3. CPU ve sıcak-yol gecikmesi

Son karşılaştırmada float indeksleri ve sorguları önceden birim norma getirildi, norm vektörleri sıcak yoldan çıkarıldı; hem float hem native Hamming yeniden kullanılan çıktı tamponuyla ölçüldü. Arşiv başına 7 ısınmış tur medyanı, sorgu sayısıyla ağırlıklandırıldı. Yöntem sırası arşive göre döndürüldü. Tek iş parçacığı kullanıldı. Değerler bir sorgunun kendi arşivindeki bütün kayıtlarla puanlanması içindir.

| Yöntem | LongMemEval µs/sorgu | PerLTQA µs/sorgu | RealTalk µs/sorgu |
|---|---|---|---|
| Optimize float64 | 5,20 | 4,58 | 10,08 |
| Optimize standart float32 | 3,52 | 3,03 | 5,51 |
| Derlenmiş paketli SIGN96 | 2,02 | 1,74 | 3,00 |

| Karşılaştırma | LongMemEval | PerLTQA | RealTalk |
|---|---|---|---|
| Float64 süresi / SIGN96 süresi | 2,57× | 2,63× | 3,36× |
| Standart float32 süresi / SIGN96 süresi | 1,74× | 1,74× | 1,84× |

İlk, daha doğrudan NumPy uygulaması ölçümü ayrı dosyada korunuyor. LUT üzerinden XOR/popcount süresi LME/PerLTQA/RealTalk için sırasıyla 24,52, 20,65, 39,61 µs; modern NumPy bitwise_count için 15,38, 13,52, 24,29 µs. Aynı temsilin Python/NumPy ara dizileri nedeniyle daha yavaş, C döngüsüyle daha hızlı çıkabilmesi, eski yavaşlığın temsilin zorunlu özelliği olmadığını gösterir. Derlenmiş kod yerel bir adaydır; mevcut üretime/GitHub’a uygulanmadı.

| Yöntem | LongMemEval puanlama + ilk-10 µs | PerLTQA puanlama + ilk-10 µs | RealTalk puanlama + ilk-10 µs |
|---|---|---|---|
| Optimize float64 | 17,73 | 28,49 | 69,62 |
| Optimize standart float32 | 15,87 | 26,17 | 64,73 |
| Derlenmiş SIGN96 | 10,24 | 8,91 | 16,94 |

İlk-10 ölçümü tam lexsort ve sabit tie önceliği içerir; en iyi kısmi sıralama algoritması iddiası yoktur. Hamming ve float skorlarının dağılımları farklı olduğundan sıralama maliyetleri de farklıdır. Ham metin okuma, TF-IDF dönüşümü, SVD query projection, disk/ağ, gold değerlendirmesi ve LLM üretimi bu mikro-saniye sürelerine dahil değildir. Özellikle query sign-pack/float standardizasyonu ve normlama dışarıda hazırlanmıştır. Bu nedenle “metinden uçtan uca sorgu 2 µs” veya uçtan uca aynı hızlanma denemez.

| Yöntem | LongMemEval bütün sorgular için CPU saniyesi | PerLTQA bütün sorgular için CPU saniyesi | RealTalk bütün sorgular için CPU saniyesi |
|---|---|---|---|
| Optimize standart float32 | 0,001644 | 0,025021 | 0,003873 |
| Derlenmiş SIGN96 | 0,000940 | 0,014365 | 0,002107 |

Bu CPU toplamları, tekrarlı ölçümlerdeki arşiv medyanlarının gerçek sorgu sayılarıyla ağırlıklandırılmasıyla elde edilen toplam puanlama maliyetidir; tüm benchmark betiğinin çalışma süresi değildir.

## 4. İndeks boyutu ile süreç RAM’i ayrı sonuçlar

MB = 1.000.000 bayt. Aşağıdaki tablo her veri kümesinin **bütün arşivlerinin** indeks toplamıdır; vektör başına boyut değildir. Standart float32 için arşive özgü ölçek dizisi de sayılmıştır. Ortak metin kodlayıcısı/model bu tabloda yoktur.

| İndeks düzeni | LongMemEval toplam MB | PerLTQA toplam MB | RealTalk toplam MB |
|---|---|---|---|
| Optimize float64 | 177,873 | 9,437 | 6,869 |
| Optimize standart float32 + ölçek | 89,117 | 4,730 | 3,438 |
| Paketli SIGN96 | 2,779 | 0,147 | 0,107 |

Paketli belge matrisi, float64 belge matrisinden tam 64 kat, float32 belge matrisinden tam 32 kat küçüktür. Eski 64,7 katsayısı ayrıca tutulan float norm vektörünü de sayıyordu; yeni birim-normlu düzen bunu saklamaz. Ölçek gibi yardımcı bilgiler ayrıca görünür tutuldu. Kodlayıcı TF-IDF sözlükleri ve SVD projektörü dahil edildiğinde bütün servis aynı katsayıyla küçülmez.

Ayrı RAM deneyi: yeni Python/NumPy süreci yalnız o veri kümesinin tüm indeks dizilerini yükledi, sayfalar dokunularak fiziksel belleğe getirildi. Düzen ve veri kümesi başına 3 taze süreç; tablo medyan RSS’dir. **Bu minimal indeks tutucu süreçtir; tam üretim servisi değildir.** Native kütüphane/aktif çıktı tamponu, ham metin, sözlük/SVD kodlayıcısı, sorgu önbelleği ve LLM yoktur.

| Süreçteki indeks | LongMemEval RSS MB | PerLTQA RSS MB | RealTalk RSS MB |
|---|---|---|---|
| Float64 | 274,03 | 104,91 | 102,28 |
| Standart float32 | 185,67 | 100,21 | 98,85 |
| SIGN96 | 98,96 | 95,60 | 95,54 |

Başlangıç süreci yaklaşık 95 MB tüketiyor. LME’de süreç RAM’i 2,77 kat azalıyor; 64 kat değil. Küçük PerLTQA/RealTalk indekslerinde sabit süreç yükü daha baskın. Eklenen RSS ve USS, ham sonuç dosyasında ayrı ayrı bulunur. İlk RAM denemesinin resource.ru_maxrss alanı süreç geçmişinden yüksek su izi taşıdığı için final sonuçlarda kullanılmadı; final tabloda doğrudan psutil RSS var.

## 5. Ham metinden kurulum ve gerçek RAM tepe noktaları

| Panel | Arşiv | Yöntem | Toplam kurulum s | Toplam CPU s | Tek arşiv süreç tepe RSS MB |
|---|---|---|---|---|---|
| LongMemEval | 12 | Kaynakla aynı randomized | 43,429 | 43,362 | 453,4–490,1 |
| LongMemEval | 12 | Exact Gram adayı | 10,300 | 10,249 | 233,6–240,8 |
| PerLTQA | 6 | Kaynakla aynı randomized | 3,943 | 3,929 | 226,3–251,4 |
| PerLTQA | 6 | Exact Gram adayı | 1,104 | 1,100 | 176,2–190,8 |

Kurulum süresi archive TF-IDF, LSA32, birleştirme, SVD96, merkezleme ve SIGN96 paketlemeyi içerir; interpreter/import başlangıcı ve önceden okunmuş kaynak JSON’un disk yüklemesi süreye dahil değildir. Tepe RSS ise gerçek süreç belleğidir; üst süreç 5 ms aralıklarla yalnız build zaman aralığında örnekledi. Örneklenen tepe, sürekli-zaman tepesinin alt sınırı olabilir. Paneldeki arşivlerin tepe RAM’leri **toplanmadı**: işler sıralı çalıştırıldı, tablo min–maks aralık gösterir.

CPU saniyesi ile duvar saati saniyesinin yakınlığı, kurulumun tek çekirdeği yaklaşık tam kullandığını gösteriyor. Fiziksel işlemci toplam kullanım yüzdesi olarak yorumlanmamalıdır. Donanım gücü/enerji/watt ölçülmedi.

| Panel | Kaynak randomized sorgu kodlama ms | Exact Gram sorgu kodlama ms |
|---|---|---|
| LongMemEval | 14,930 | 5,880 |
| PerLTQA | 2,634 | 1,969 |

Bunlar 42 örnek sorgu için metin → TF-IDF/LSA → SVD projection → normalize/center dönüşüm süreleridir; her sorguda 3 tekrar medyanı, panelde eşit sorgu sayılı arşivler üzerinden ortalama. Puanlama mikro-saniye, kodlama milli-saniye düzeyinde: yalnız Hamming çekirdeğini hızlandırmak sorgu kodlama maliyetini ortadan kaldırmıyor. İndeks kurulumu bir defa yapılabiliyorsa sonraki sorgulara amorti edilir; arşiv her sorguda yeniden kuruluyorsa tekrar ödenir. Panel kurulum süreleri 510 arşive körlemesine ölçeklenmedi.

Exact Gram, LME panel toplam kurulumunda 4,22×, PerLTQA’da 3,57× hızlanma verdi. LME’de yalnız son SVD aşaması 19,49× hızlandı. Fakat randomized yaklaşımın birebir aynı temsili değildir. Küçük panelde standartlaştırılmış float kalitesi bile değişti; bu yüzden “float için bedelsiz” diye otomatik geçiş onayı verilmedi. Ham soru düzeyi karşılaştırmalar build_profile.json içindedir.

Projektörün kaldırılması “toplam model belleği sıfır” anlamına gelmez. LME panelinde randomized son projektörlerin toplam dizi boyutu 890,19 MB; Gram son-projection çekirdeği için saklanan seyrek Z ve U/S toplamı 97,07 MB. TF-IDF sözlükleri ve LSA32 modeli her iki tarafta da ayrıca bulunur. Bu toplamlar dizi muhasebesidir, aynı anda resident olan servis ölçümü değildir.

## 6. Tohum düzeltmesi ve tekrarlanabilirlik

Devir notu son SVD için 5101 yazıyordu. Kurtarılan üretici buildrep fonksiyonunun SVD_SEED sabiti **5204**; PerLTQA step2_build.py de 5204 kullanıyor. **İlk LSA32’nin tohumu 5101, son SVD96’nın tohumu 5204.** Başlangıçta nottaki 5101 kullanılarak yapılan LME denemesi bundan dolayı final source-matched koşu sayılmadı; ayrı superseded_seed5101_diagnostic klasöründe korundu.

Doğru ayarda yeniden kurulan 18 arşivin doküman işaret bitleri ve 42 örnek sorgunun işaret bitleri önbellekle eşleşti; kontrol edilen hit@10/recall@10 sonuçları da aynı kaldı. Bir LME arşivi aynı ortamda üç taze süreçte yeniden kuruldu; C/Q/packed-C hash makbuzları üçünde aynı. Bu, bu panelde iyi bir tekrar üretim bulgusudur; bütün donanım ve BLAS sürümlerinde genel bit-exact determinism ispatı değildir. Önceki oturumun 0,53 puan farkının nedeni ayrıca kanıtlanmış sayılmadı.

## 7. Doğrulama kapıları ve sınırlar

- 270 küçük sınır-tie senaryosunda analitik metrik, tüm ilgili altküme seçimlerinin açık sayımıyla karşılaştırıldı.
- 9.440 gerçek sorguda naive Hamming, paketli NumPy ve derlenmiş SIGN96 mesafeleri bütün dokümanlar için aynı. Optimize ham-pointer bağlama ayrıca aynı sorgularda kontrol edildi.
- 9.440 sorguda derlenmiş SIGN80, aynı seçili koordinatlar üzerindeki doğrudan Hamming ile aynı.
- 9.440 sorguda standart float32/64 altı kalite metriği birebir aynı; birim-normlu optimize float yollarında da değişen sorgu yok.
- Dört girdi arşivinin SHA-256 değeri Drive manifestiyle eşleşti. Kimlikler ve hash’ler source_provenance.json içinde.

Sınırlar: yeni keşifsel harness dış denetçi tarafından denetlenmedi; eski Sept15 HIT10/lib_b8 betiklerinin tamamı bulunamadığı için kaynakla uyumlu yeniden uygulama kullanıldı. B8/asym kolları, ham RealTalk kurulum, tüm 510 arşivden ham yeniden fit, LLM cevap kalitesi, dağıtık servis, eşzamanlı yük, cold-cache tail latency ve enerji ölçülmedi. Gram alternatifinin kalite değerlendirmesi yalnız küçük paneldir. Donanım/BLAS ve veri ölçeği değiştikçe zamanlama değişebilir. Hiçbir pilot sonucu üretim onayı veya önkayıtlı bilimsel doğrulama olarak sunulmadı.

## 8. Ortam ve dosya haritası

Linux x86-64 / Python 3.13.5. Görünen CPU modeli AMD EPYC 9V74; 5 görünür vCPU, cgroup kotası 4 CPU; 4 GiB RAM sınırı. Bütün BLAS/OMP yolları 1 thread ile çalıştırıldı. NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, psutil 7.2.2. Derleyici GCC 14.2, `-O3 -march=native`. Sanallaştırılmış/paylaşımlı ortam; çalışma sırasında başka deney işleri sıralı yürütüldü. Ölçüm dosyaları metadata işlemlerinin ve sistem zamanlayıcısının etkilerinden tamamen bağışık değildir.

Kaynak GitHub main: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`. Hiçbir uzak dosya değiştirilmedi; main, eski görevler ve Task4F1/BEAM sonuç sınırı korunmuştur. Yeni C çekirdeği yalnız bu yerel test paketindedir.

Rapor tablolarının makine-okunur özeti `results/SUMMARY.json`; tam ölçümler `quality.json`, `optimized_comparison.json`, `memory_optimized.json`, `build_profile.json`; soru ve arşiv düzeyi kanıtlar ilgili CSV/JSON dosyalarıdır. README yeniden çalıştırma komutlarını ve veri geri alma sınırlarını içerir.
