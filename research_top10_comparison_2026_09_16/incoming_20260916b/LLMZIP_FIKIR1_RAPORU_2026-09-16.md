# LLMZIP — Fikir 1: küçük kodla aday bul, özgün metinle yeniden sırala

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. Karar

İlk kontrollü pilot tamamlandı. Sabit qscale96 aday listesindeki 50 kaydı özgün metinden BM25 ile yeniden sıralamak, üç test kümesinde de FR@3 ortalamasını artırdı. Bu, bütün soruların iyileştiği veya yöntemin en iyi sistem olduğu anlamına gelmiyor. Aynı metin kontrolünü güçlü float/ASYM/Hamming referanslarına da verdik; tam-arşiv BM25 de kontrol olarak kullanıldı. Hız ve yardımcı durum maliyetleri ihmal edilemez. Üretime geçiş, yeni gizli-test teyidi veya özgünlük iddiası yok.

Bu pilot birinci fikrin en hafif sözcüksel sürümüdür. BM25 soru ile metindeki kelimeleri değerlendirir; mantıksal çıkarım, zamansal ilişkilerin doğrulanması veya eğitilmiş soru–metin modeli değildir.

## 2. Sonuçlardan önce sabitlenen tasarım

PLAN_BEFORE_RUN.json ve SHA-256 kaydı hesaplardan önce yazıldı; son kontrolde değişmemiş olduğu doğrulandı. Bu yerel kayıt resmî önkayıt değildir. Eski veri kümeleri zaten görülmüştür. Her kayıt kodu mevcut 96 bit olarak korundu. İlk aşama beş ayrı kontrol: Hamming, ASYM, qscale, standartlaştırılmış float32 ve ham/standartlaştırılmamış merkezli float32.

Ana aday sayısı M=50. Bütün yöntemlerde tam 50 kayıt, puan azalan ve eşitlikte doküman sıra numarası artan düzenle seçilir. Hiçbir eşitlik genişlemesi yok. Sonuç ve zamanlama yollarında aynı seçim ve yeniden sıralama fonksiyonları kullanılır. Ana ölçüt FR@3; ikincil ölçütler hit@3, hit@10 ve FR@10.

Önceden belirlenmiş birinci metin puanlayıcısı BM25: k1=1.2, b=0.75. Unicode kelime/sayı tokenları, küçük harf, tek karakterler dahil, kök bulma/stopword silme yok; özgün indeks metnindeki tarih/konuşmacı/alan etiketleri korunur. Sorgu terimleri bir kez sayılır. IDF=log(1+(N-df+0.5)/(df+0.5)); skor Σ IDF(t)·tf·2.2/[tf+1.2·(0.25+0.75·doclen/avglen)]. İstatistikler yalnız arşiv metinlerinden çıkarılır.

İkinci, sabit tanısal kol RRF60: Aynı 50 adayın ilk-aşama sırası ile BM25 sırasını 1/(60+r1)+1/(60+r2) şeklinde birleştirir. Bu yeni adayların birleşimi değildir; 50 aday dışından kayıt eklenmez. Birinci ana kol kötü çıktığında sonradan eklenmiş bir seçenek değildir. Farklı veri kümelerine göre kazananı seçip tek sistem sonucu üretmedik.

Eşik/ölçek/puanlayıcı ağırlığı gold ile eğitilmedi veya bu sonuçlara göre seçilmedi. Gold etiketleri sadece değerlendirici, erişilebilirlik tavanı ve sonradan seçilen açıklayıcı örneklerde kullanıldı.

## 3. Veri kapsamı ve kaynak kontrolü

İlk aşama kapasite tanısı: 520 arşiv, 10.971 sorgu, 258.720 kayıt. Eski 510 arşivin sayısal önbellekleri yeniden oynatıldı. LoCoMo 10 arşivinin tamamı özgün metinden, önceki sabit tarifle yeniden kuruldu (LSA tohumu5101; SVD96 tohumu5204).

Metinle yeniden sıralama: LME 470 arşiv/470 soru, PerLTQA en_v2 30/8.265, LoCoMo 10/1.531; toplam 510 arşiv/10.266 soru/249.776 kayıt. RealTalk 10 arşiv/705 soru için eldeki izinli yedeklerde yalnız sayısal önbellekler bulundu; metin-rerank sonucu üretilmedi. Bu, başka yerde ham metin olmadığı iddiası değildir.

PerLTQA kayıt metinleri en_v2 kaynağından yeniden oluşturuldu ve kayıtlı kimlik/metin çiftleriyle eşleştirildi. LoCoMo önceki 1.531 soruluk kohortu, dışlamaları ve açık birleşik kanıt kimliği düzeltmelerini aynen korur; başka bir çalışmanın 1.535 soruluk kohortuyla karıştırılmaz. Görsel açıklamaları, QA cevapları veya üretilmiş özetler indeks metnine eklenmedi.

Yedeklerin hashleri doğrulandı; önceki son paketin 43 dosyası hash kontrolünden geçti. Sayısal referanslar 10.971 sorguda önceki rapordaki dört kolun altı metriğiyle karşılaştırıldı: 263.304 skaler karşılaştırma, sıfır fark. Bu kapı tek başına her yeni kod satırının doğruluğunun ispatı değildir; ek kontroller aşağıda.

## 4. Önce erişilebilirlik: kusursuz yeniden sıralayıcı tavanı

Bu bölüm gerçek bir model başarısı değildir. Goldları bilen varsayımsal seçici, mevcut ilk M aday içinden en fazla üç doğru kayıt seçer. Her soru için tavan = min(3, adaylardaki gold sayısı)/toplam gold sayısı. Tam arşivde bile üçten fazla gold varsa FR@3 üst sınırı %100 değildir.

| Veri kümesi | qscale mevcut FR@3 | İlk50 içinde en az bir gold (%) | İlk50den kusursuz seçim FR@3 | Tam arşivden kusursuz seçim FR@3 |
|---|---:|---:|---:|---:|
| LME | 54.27 | 94.68 | 89.52 | 97.77 |
| PerLTQA | 53.24 | 91.20 | 73.80 | 83.04 |
| RealTalk | 22.41 | 67.38 | 53.70 | 93.14 |
| LoCoMo | 35.84 | 78.45 | 71.17 | 97.65 |

M=10/20/50/100 eğrileri de saklandı, fakat sonuçlara göre M değiştirilmedi. Tavanlar ilk50nin dışındaki kanıtı geri getiremez. RealTalk/LoCoMo gibi kümelerde aday kaçırma da hâlâ önemli.

## 5. Ana deney: ilk üçteki kanıt payı gerçekten değişti mi?

FR@3 = etiketli kanıt kayıtlarının ilk üçte bulunan payı; sorular üzerinden aynı veri kümesinde ortalama. Cevap doğruluğu veya soru başına en az bir kanıt oranı değildir.

| Veri | qscale | qscale → ham metin BM25 | Fark (yüzde puan) | float_std → aynı BM25 | Yalnız tam-arşiv BM25 |
|---|---:|---:|---:|---:|
| LME | 54.27 | 57.70 | +3.43 | 58.05 | 58.03 |
| PerLTQA | 53.24 | 57.46 | +4.22 | 57.42 | 57.13 |
| LoCoMo | 35.84 | 42.81 | +6.97 | 43.22 | 41.75 |

Ana yöntem kendi öncülünü geliştiriyor. Ancak LME ve PerLTQA’da yalnız BM25 ile sonuçlar çok yakın; dolayısıyla bütün iyileşmeyi küçük kodun özel bir başarısı diye yorumlayamayız. LoCoMo’da ana yöntem yalnız BM25’ten yaklaşık1.07 puan yüksek, ama aynı yeniden sıralayıcıyı kullanan float_std’den yaklaşık0.40 puan düşük.

### Önceden sabitlenen sıralama-birleştirme kolu

| Veri | qscale | qscale → RRF60 | float_std → RRF60 |
|---|---:|---:|---:|
| LME | 54.27 | 58.81 | 59.51 |
| PerLTQA | 53.24 | 57.96 | 59.70 |
| LoCoMo | 35.84 | 40.39 | 43.02 |

RRF kolu LME/PerLTQA’da doğrudan BM25’e göre daha yüksek, LoCoMo’da daha düşük. Veri kümesine göre yöntem seçip birleşik bir kazanan üretmedik.

### Bütün kontroller, aynı deterministik eşitlik kuralı

| Yöntem | LME FR@3 | PerLTQA FR@3 | LoCoMo FR@3 |
|---|---:|---:|---:|
| BM25_full | 58.03 | 57.13 | 41.75 |
| hamming96 | 53.86 | 49.84 | 31.46 |
| hamming96_bm25 | 58.23 | 57.52 | 42.17 |
| hamming96_rrf60 | 60.26 | 56.71 | 37.93 |
| asym96 | 50.65 | 53.53 | 34.27 |
| asym96_bm25 | 57.65 | 57.51 | 42.41 |
| asym96_rrf60 | 55.95 | 58.61 | 39.00 |
| qscale96 | 54.27 | 53.24 | 35.84 |
| qscale96_bm25 | 57.70 | 57.46 | 42.81 |
| qscale96_rrf60 | 58.81 | 57.96 | 40.39 |
| float_std32 | 55.74 | 56.58 | 38.91 |
| float_std32_bm25 | 58.05 | 57.42 | 43.22 |
| float_std32_rrf60 | 59.51 | 59.70 | 43.02 |
| float_raw32 | 44.16 | 55.17 | 33.68 |
| float_raw32_bm25 | 57.76 | 58.26 | 44.06 |
| float_raw32_rrf60 | 53.56 | 59.93 | 40.54 |

Bu tablo sonuçlara bakılarak en iyi kol seçilmesini onaylamaz. Hamming’in buradaki sabit sıra numarasıyla kırılan eşitlik sonuçları, eski uniform-tie beklenti sonuçlarından farklı olabilir. Bu çalışma iki ölçümü sessizce karıştırmaz: baseline_per_query.csv ikisini de ayrı saklar; bütün ana yeni karşılaştırmalar aynı deterministik kuralı kullanır.

### Hit@10: ana ölçüt dışında da kontrol

| Veri | qscale | qscale → BM25 | qscale → RRF60 | float_std → BM25 |
|---|---:|---:|---:|---:|
| LME | 88.51 | 86.81 | 89.15 | 87.23 |
| PerLTQA | 80.00 | 82.78 | 83.23 | 83.15 |
| LoCoMo | 57.22 | 61.92 | 60.81 | 62.25 |

LME’de doğrudan BM25 yeniden sıralaması FR@3’ü artırırken hit@10’u düşürür. Bu, bütün ölçütlerde iyileşme iddiasını ayrıca engeller.

## 6. Kazanan ve kaybeden sorular; belirsizlik

| Veri | Ana FR@3 farkı | İyileşen/gerileyen/aynı soru | Keşifsel %95 arşiv-bootstrap aralığı (puan) |
|---|---:|---:|---:|
| LME | +3.43 | 78/52/340 | [0.62; 6.29] |
| PerLTQA | +4.22 | 1079/764/6422 | [3.27; 5.19] |
| LoCoMo | +6.97 | 228/113/1190 | [3.29; 10.88] |

20.000 eşleştirilmiş arşiv yeniden örneklemesi; seed9162026. PerLTQA30, LoCoMo10 küme; bağımsız/değiştirilebilir arşiv varsayımı gerektirir. LME arşivleri ortak oturumlar içerebildiğinden onun aralığı bağımsız nüfus güven aralığı olarak yorumlanamaz. Çoklu deneme düzeltmesiyle önkayıtlı hipotez teyidi yapılmadı. Tüm veriler bu araştırmada önceden görülmüştür.

## 7. Gerçek metin erişimi dahil CPU/gecikme

Zamanlama sırasında başka deney işi çalıştırılmadı. 19 yeni arşiv süreci:6LME,3PerLTQA,10LoCoMo;51 farklı soru. Boyut sırasından önceden belirlenmiş eşit aralıklı arşivler/soru sıraları; sonuca göre seçim yok. Her yolda7 döndürülmüş tekrar. Kaliteyle aynı ilk50 seçimi, aynı BM25, aynı sıralama kodu çalıştırıldı. 51 soruda yeniden oluşturulan kod ve son top10 listeleri kalite dosyalarıyla eşleşti.

Kaynak metin bir UTF-8 dosyasında tutulur. Her aday gerçek os.pread erişimiyle okunup decode/tokenize edilir. Önceden hazır bir bütün-doküman kelime matrisi, aday yeniden sıralayıcısına verilmez. Tüm-arşiv BM25 kontrolü ise gerçek ters indeks kullanır; maliyet avantajını gizlemek için ona gereksiz SVD kodlaması yaptırılmadı.

### Metinden ilk on sonuca kadar, milisaniye

| Panel | qscale | qscale → BM25 | qscale → RRF60 | float_std → BM25 | Yalnız ters-indeks BM25 |
|---|---:|---:|---:|---:|
| LME | 14.886 | 17.622 | 17.433 | 17.591 | 0.142 |
| PerLTQA | 2.743 | 3.605 | 3.580 | 3.650 | 0.103 |
| LoCoMo | 2.575 | 3.280 | 3.321 | 3.327 | 0.106 |

### Yalnız ek ilk50 metin okuma + BM25 yeniden sıralama

| Panel | Ek duvar saati ms | Ek CPU ms |
|---|---:|---:|
| LME | 2.369 | 2.368 |
| PerLTQA | 0.767 | 0.766 |
| LoCoMo | 0.591 | 0.591 |

Bu ilk prototip toplamda daha hızlı değildir. qscale→BM25 mevcut qscale’e göre panelde ek gecikme getirir. Yalnız BM25 çok daha hızlıdır fakat farklı ve daha büyük ters indeks tutar. Hız/bellek kıyasını yalnız bu sürelerle kapatamayız.

Süreler sorgu başına tekrar medyanlarının panel ortalamasıdır. Yerel, sıcak dosya-sayfası/cache koşulları; ağ, cold-disk, LLM cevap üretimi, her soruda indeks kurulumu ve yük altında kuyruk gecikmesi yok. Ortak encoder kurulur ve kullanılmaya devam eder; önceki küçük-faktör projektör önerisi bu koşuya eklenmedi. Derleyici/CPU ve tam ölçümler results/environment.json ile timing_full.json içinde. Tek yöntem RSS’si ölçülmedi; bütün karşılaştırma dizilerini içeren test sürecinin RSS’sini ürün RAM’i diye sunmadık.

## 8. Bellek: ek istatistik maliyeti büyük, gizlenmedi

MB=1.000.000 bayt. Aşağıdaki sayılar her veri kümesinin bütün arşivleri üzerinden toplamdır; arşivler ölçümde sıralı yüklendi. Kod bütçesi değişmese de toplam durum değişti.

| Veri | Paketli kod+sigma MB | Ham UTF-8 kaynak MB | Offset dosyaları MB | BM25 istatistik JSON MB | IDF Python nesneleri toplamı MB |
|---|---:|---:|---:|---:|---:|
| LME | 3.140 | 237.865 | 1.917 | 63.982 | 351.177 |
| PerLTQA | 0.170 | 2.587 | 0.102 | 1.123 | 6.000 |
| LoCoMo | 0.078 | 0.937 | 0.048 | 0.285 | 1.655 |

IDF nesne boyutu sys.getsizeof ile sözlük/anahtar/değer nesnelerinin tekrarları ayrıştırılarak hesaplandı; süreç RSS’si değildir. Tablodaki disk JSON ve çalışma zamanı sözlük boyutları birbirine eklenip RAM diye sunulmaz. Bütün arşivleri aynı anda resident tutmuş değiliz. LME’de bu ilk Python sözlük tasarımı, küçük kodun dizi tasarrufundan daha büyük bir ek yük oluşturabiliyor.

Ters-indeks BM25 kontrolünün posting dizileri, sözlüğü ve Python nesne boyutları memory_accounting.json içinde ayrıca sayıldı. Ham kaynak, kimlik/offset erişimi ve ortak TF-IDF/SVD kodlayıcısı her sistemin ihtiyacına göre maliyete dahil edilmelidir. Bu deney tüm servisin daha küçük olduğunu göstermedi. Üretim adayında istatistiklerin daha kompakt veya yeniden kullanılan bir saklama biçimi ayrı kalite-eşdeğerlik ve maliyet denetimi gerektirir.

## 9. Doğrulama, kapsam sınırları ve sonraki karar

-120 küçük eşitlik senaryosunda 2.249 açık sıralama sayımı, analitik hit/FR ile eşleşti; küçük oracle durumları brute-force kontrol edildi.
-10.971 sorguda263.304 önceki metrik karşılaştırması aynı; yerel native ağırlıklı skorun bağımsız ±1 doğrusal hesabıyla en büyük farkı2.85e-14 altında.
-2.566.500 aday metni gerçek dosyadan okunup yeniden tokenize edildi;51.330 aday-grup skoru bağımsız ters indeks puanlarıyla kontrol edildi; en büyük fark2.85e-14 altında.
-153.990 sonuç satırında oracle tavanı aşılmadı. 54.855 soru/ilk-aşama kolunda M büyüdükçe oracle kapasitesi azalmadı.
-205.320 deterministik baseline metriği iki aşama arasında aynı;520 aday dosyasıhashkontrolü.
-51zamanlama sorusunun aynı algoritmayla ürettiği top10kalite dosyasına aynen uydu.

Yukarıdaki kontroller kod yazarı tarafından yapıldı; bağımsız dış denetçi onayı değildir. B8 codec’i bu pilotta yeniden uygulanmadı ve BM25/RRF ile tekrar sıralanmadı. B8’i ve bütün literatür yöntemlerini geçtiğimiz söylenemez. Gold etiketleri içerik bazında yeniden denetlenmedi. Yeni dokunulmamış test yapılmadı.

Bir ilk çalışma araç süre sınırında kesildi; kısmî CSV/log results/partial_timeout_stage2.* olarak saklandı ve nihai hesaplara katılmadı. Tam çalışma 510 metin arşiviyle yeniden tamamlandı. PLAN ayarları değiştirilmedi. Kaynak dosyalar, GitHub main/Drive ve kapalı Task4F1/BEAM sınırları değiştirilmedi.

Karar: Aday bulma + özgün metin sıralaması araştırmaya değer; ilk-üçte gerçek gözlenen kazanç var. Ancak bu hafif sözcüksel pilot, en iyi kalite/hız/bellek sistemini göstermiyor. Bir sonraki ayrıştırmada özellikle yalnız BM25 ve aynı metin kontrolünü alan float/ASYM karşılaştırmaları korunmalı. Daha karmaşık anlamsal kontrolü eklemeden önce mevcut büyük yardımcı durum maliyeti çözülmeli; hiçbir sonraki adım bu oturumda yapılmış gibi raporlanmıyor.

## 10. Birincil yöntem kaynakları ve dosyalar

BM25 parametre dayanağı: https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity
RRF sabiti dayanağı: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
Bu sayfalardan yeni deney sayısı alınmadı. Kullanılan BM25 tokenizer/puanlayıcı bize ait açık uygulamadır; Elasticsearch’ün byte-identical replikası değildir. RRF burada aynı50aday üzerinde uygulanır; ayrı getiricilerin tüm-listesi birleşimiyle aynı deney değildir.

Özet: OZET.json. Gerçek soru sonuçları: results/text_rerank_per_query.csv. Bütün aday tavanları: results/capacity_per_query.csv. Başarı/başarısızlık örnekleri: results/illustrative_examples.json (sonradan tanısal seçim). Zamanlama/CPU: results/timing_full.json. Bellek muhasebesi: results/memory_accounting.json. Kaynak kimlik/hash zinciri: sources/input_manifest.json ve source_register.json. Yeniden üretim adımları README.md.