# LLMZIP — Hata ve bilgi kaybının yerini belirleme

16 Eylül 2026


[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]


## 1. Sonuç

İncelenen işlemlerde aritmetik/bit-paketleme hatası saptanmadı. Buna karşılık gerçek sorularda sayısal gösterimden iki taraflı işaret/Hamming puanlamasına geçerken doğru kanıtın sırasının bozulduğu doğrudan ölçüldü. Koordinat ölçekleri ve sorgu büyüklükleri bu kaybın bir kısmında etkili. Sorgunun kendisini de işaretlere indirgemek, doküman kodlarını küçük tutmak için zorunlu değildir.

Bu, bütün başarısızlıkların tek nedeni veya tüm görevler için en iyi gösterimin bulunduğu anlamına gelmez. PerLTQA'da SVD96 aşamasında ayrıca kalite kaybı var. Erken özelliklerin anlamsal yeterliliği, gold doğruluğu ve genelleme bu deneyde tamamen çözülmedi.

Yeni karşılaştırma bir kök-neden müdahalesidir: aynı arşiv, aynı soru, aynı gold ve aynı doküman bitleri; yalnız sorgu tarafındaki büyüklük bilgisi ve puanlama değişir. Eğitilmiş çözücü, öğrenilmiş eşik veya gold ile ayarlanmış parametre yoktur. Diğer yöntemlerin geçmişte benzer kullanımları bulunabilir; yenilik iddiası yoktur.


## 2. Gerçek kapsam ve doğrulama


- Sayısal önbellekler: 470 LME, 30 PerLTQA en_v2, 10 RealTalk arşivi; toplam 510 arşiv / 9.440 sorgu / 252.838 kayıt. Kalite yüzdeleri veri kümeleri arasında birleştirilmedi.
- Ham metinden yeniden kurulum: 48 LME arşivi / 48 soru ile 30 PerLTQA arşivinin tamamı / 8.265 soru. Toplam 78 arşiv / 8.313 soru / 35.652 kayıt. LME örneği toplam arşiv karakter sayısında eşit aralıklı sıralardan, etiket/başarıya bakılmadan seçildi; rastgele bağımsız örneklem değildir.
- PerLTQA metinleri en_v2 ham bellek JSON'undan yeniden oluşturuldu; kayıt kimlikleri ve metinler önbellekteki itemization ile birebir eşleşti. Gold değerlendirme protokolü değiştirilmedi; gold etiketlerinin doğruluğuna ilişkin bağımsız içerik denetimi yapılmadı.
- Üç girdi arşivinin SHA-256'ları daha önce kaydedilmiş manifestle doğrulandı. 510 C/Q dizisi önbelleğinin içerik hash'leri önceki benchmark envanteriyle eşleşti.
- Hamming, merkezlenmiş float ve standartlaştırılmış float referansları 9.440 soruda yeniden üretildi; 84.960 hit/recall çifti (3 k seviyesi) önceki sonuçlarla eşleşti. Metrik ayrıca 280 küçük durumda tüm sınır-eşitlik seçimleri sayılarak kontrol edildi.
- Ham yeniden kurulumda 78 arşivde doküman ve 8.313 soruda sorgu işaret bitleri değişmedi. Paylaşılan beş kolda 249.390 skaler kalite karşılaştırması ham yeniden kurulum ile önbellek tekrarı arasında eşleşti.
- Yeni ağırlıklı puanlama, doğrudan ±1 matrisi ve bağımsız paketli-bayt lookup hesabıyla 9.440 soruda kontrol edildi; tüm ölçülen hit/recall değerleri aynı çıktı.

RealTalk ham metinden yeniden kurulmadı. LME'nin tamamında erken TF-IDF/SVD aşamaları yeniden kurulmadı. Tam kapsamlı sonuçlar ile ham-metinden alt panel sonuçları aşağıda ayrı tutulmuştur.


## 3. Bütün önbelleklerde aşama/puanlama karşılaştırması

Hit@10: ilk on sonuçta en az bir etiketli doğru kanıt; sınırda eşit puan varsa uniform rastgele seçim altındaki tam beklenti. Cevap üretme doğruluğu değildir.


| Karşılaştırma kolu | LME (470) | PerLTQA (8.265) | RealTalk (705) |
|---|---:|---:|---:|

| SVD96, merkezleme öncesi kosinüs | 82,77 | 80,48 | 36,45 |

| Merkezlenmiş, standartlaştırılmamış kosinüs | 82,55 | 80,81 | 36,60 |

| Merkezlenmiş + koordinat standartlaştırmalı kosinüs | 88,30 | 83,96 | 48,51 |

| Doküman bitleri + ham merkezli sorgu (eski asym) | 85,74 | 80,19 | 43,55 |

| Aynı doküman bitleri + standartlaştırılmış sayısal sorgu | 88,51 | 80,00 | 49,65 |

| Standartlaştırılmış sayısal doküman + sorgu bitleri | 87,66 | 79,73 | 50,35 |

| Doküman bitleri + sorgu bitleri (üretim SIGN96) | 86,08 | 75,76 | 46,68 |


Tablodaki kolların tamamı üretim zincirinde art arda çalışan aşamalar değildir. Özellikle koordinat standartlaştırması ayrı referans/karşılaştırma koludur. İki taraflı işaret kolunda pozitif koordinat ölçekleri bitleri değiştirmez.

Eski `asym` kolu da tekrar üretildi: LME 85,74 / PerLTQA 80,19 / RealTalk 43,55. Yeni tanısal karşılaştırma ham sorguyu değil koordinat standart sapmasına bölünmüş sorguyu kullanır. Bu yüzden asimetrik puanlamanın geçmişteki tüm sonuçlarının aynısı değildir.


### Merkezleme ve normalleştirme


Merkezlemenin tam önbelleklerde hit@10 net etkisi LME -0,213; PerLTQA +0,327; RealTalk +0,142 yüzde puandır. Bu küçük net değişimler, tek tek hiçbir sorunun etkilenmediği anlamına gelmez; çiftlenmiş kazanan/kaybeden sayıları JSON'dadır.

Son L2 normalleştirmesi, aynı sayısal vektörler kosinüsle karşılaştırıldığında sıralamayı değiştirmez. Ham yeniden kurulan bütün sorularda önceki/sonraki kosinüs puanları aynı çıktı. Bu sonuç diğer işlemlerle yer değiştirmeyi veya ham vektörü normalleştirmeden merkezlemeyi kapsamaz; TF-IDF içindeki farklı normalizasyonları da aynı şey saymaz.


## 4. Son aşamada iki ayrı bilgi kaybı


C = Y - mean(Y), σ_j = max(std(C[:,j]), 10^-12), b_j = +1 (C_j ≥ 0), aksi hâlde -1.

Tam standartlaştırılmış karşılaştırma: `cos(C/σ, qC/σ)`.

Dokümanlar bit, sorgu sayısal: `score(d,q) = Σ_j b_dj · qC_j/σ_j`. Pozitif, soruya özgü norm faktörü sıralamayı değiştirmez.

İki taraf da bit: `Σ_j b_dj · b_qj`, yani Hamming mesafesine tam eşdeğer sıralama.

Bu düzen, aynı standartlaştırılmış uzayda yalnız doküman büyüklüklerini atmak, yalnız sorgu büyüklüklerini atmak ve ikisini birlikte atmak için 2×2 tanısal karşılaştırma sağlar. Etkiler veri kümesi, metrik ve müdahale sırasına bağlıdır; tek evrensel nedensel pay çıkarılmadı.

PerLTQA'da: tam sayısal %83,96 → yalnız dokümanları bit yapınca %80,00 → sorguyu da bit yapınca %75,76. Son adım yaklaşık 4,24 puan ek kaybettiriyor. LME ve RealTalk'ta yalnız dokümanları bit yapmak hit@10'u hafif artırabiliyor; dolayısıyla “her kuantizasyon her soruda zarar verir” iddiası da yanlış.


| Aynı doküman bitleri tutulurken sorgu ayrıntısı geri verilirse | LME | PerLTQA | RealTalk |
|---|---:|---:|---:|

| SIGN96 hit@10 | 86,08 | 75,76 | 46,68 |

| Sayısal, ölçeği dengelenmiş sorgu hit@10 | 88,51 | 80,00 | 49,65 |

| Fark (yüzde puan) | +2,43 | +4,24 | +2,96 |


Bu arama puanlama değişikliği Hamming ile aynı CPU maliyetine sahip sayılmadı. Doküman kodlarına bit eklenmedi, ancak arşiv başına ölçek dizisi gerekiyor. 510 arşivin toplam ölçek dizisi float64 ile 391.680 bayt; bütün doküman kodları 3.034.056 bayt. Toplam iki dizi sınıfı 3.425.736 bayt. Ortak metin kodlayıcısı, ortalama dizileri, geçici sorgu/LUT tamponları ve süreç yükü bu hesaba dahil değil. Yeni puanlayıcının uçtan uca CPU, RSS ve kuyruk gecikmesi ölçülmedi.

Daha fazla kanıtı toplama metriğinde hâlâ kalite açığı var: standartlaştırılmış float / doküman-bit-sorgu-sayısal fractional recall@100 sırasıyla LME %95,29 / %93,88; PerLTQA %85,37 / %82,39; RealTalk %65,47 / %62,37. Dolayısıyla “float'ı her açıdan geçtik” sonucu çıkmaz.


## 5. Gerçek bir sıralama tersine dönüşü


RealTalk `RT09_q000`, 1.044 kayıtlı arşiv. Soru: “At what time does Muhhamed usually come back home?” (Genellikle eve saat kaçta dönüyor?) Sabit gold etiketi kayıt 46'yı gösteriyor.

| Puanlama | Etiketli doğru kaydın sırası |
|---|---:|
| Standartlaştırılmış sayısal kosinüs | 1 |
| Doküman bitleri + eski ham sayısal sorgu | 17 |
| Aynı doküman bitleri + standartlaştırılmış sayısal sorgu | 8 |
| İki taraflı işaret/Hamming | en iyi 271 |

Doğru kaydın standartlaştırılmış kosinüsü 0,516321; Hamming uzaklığı 45. Hamming'de birinci olan kaydın uzaklığı 30. Bu, sınırdaki bir eşit-puan seçimi değil: 270 kayıt doğru kayıttan kesin daha iyi Hamming uzaklığı alıyor. Örnek sonradan tanısal olarak seçildi; temsili örneklem veya tek başına genelleme kanıtı değil. Soru metni önbellekten, doğru kaydın kimliği sabit gold eşlemesinden alındı; bu oturumda RealTalk kaynak metni üzerinden gold yeniden denetlenmedi.


## 6. Erken aşamaları ham metinden kontrol

### PerLTQA en_v2: 30 arşivin ve 8.265 sorunun tamamı

| Aşama / tanısal kol | Hit@10 (%) |
|---|---:|

| Yalnız kelime sayımları (aynı tokenizer/sözlük) | 75,09 |

| Yalnız logaritmik kelime sıklığı | 78,28 |

| Kelime TF-IDF | 82,77 |

| Kelime + karakter kanalı | 84,50 |

| Üretim geniş Z: LSA32 + kelime + karakter | 83,96 |

| SVD96 sonrası; son L2 öncesi kosinüs | 80,48 |

| Son L2 sonrası; merkezleme öncesi kosinüs | 80,48 |

| Merkezleme sonrası kosinüs | 80,81 |

| Ek standartlaştırılmış float karşılaştırması | 83,96 |

| İki taraflı bitler | 75,76 |


Kelime-sayımları → log sıklık → TF-IDF kolları, aynı kelime sözlüğündeki ağırlıklandırmayı değiştirir; tüm üretim kanallarını aynı anda değiştiren müdahaleler değildir. Ondalık sayı üreten log ve IDF işlemleri bu veri kümesindeki kelime kolunun hit@10'unu net artırdı. Bu sonuç bütün veri kümelerinde aynı faydayı garanti etmez.

Geniş Z → SVD96: 364 soru kötüleşti, 77 soru iyileşti; net -3,472 puan. Bu, son bit adımından ayrı bir projection kaybı. Daha sonra standartlaştırma hit@10 ortalamasını bu örnekte aynı seviyeye getiriyor, fakat aynı soruları kurtardığı veya kaybı bilgi anlamında geri aldığı söylenemez.

### LME: 48 soruluk ayrı alt panel

Geniş Z %85,42 → SVD96 %85,42 → merkezleme %83,33 → standartlaştırılmış float %85,42 → SIGN96 %77,08. Bu küçük panelde SVD'nin hit@10 değeri soru bazında da değişmedi; fakat fractional recall@3 %51,28'den %38,26'ya düştü. “Projection hiçbir şeyi kaybetmiyor” denemez. Panel, 470 soruluk tam LME sonucunun yerine kullanılmadı. Sonuçlar metrik ve soru seçimine bağlıdır.


## 7. İki raporlama düzeltmesi


1. Devir notundaki `float96 (uncentered ref)` etiketi, yeniden benchmark koduyla uyuşmuyor. Önceki %82,55 / %80,81 / %36,60 değerleri `C` ve `qC` üzerinden kosinüs; yani merkezlenmiş, yalnız standartlaştırılmamış float. Gerçek merkezleme-öncesi değerler bu deneyde ayrıca bulundu: %82,77 / %80,48 / %36,45. Sayısal sonuçlar değiştirilmiyor; hangi aşamaya ait oldukları düzeltiliyor.
2. L2 normalleştirme + ortalama çıkarma koordinat varyanslarını eşitlemez. Devir notundaki “already whitened” açıklaması bu anlamda doğru değil. Arşiv içinde en büyük/en küçük koordinat standart sapması oranının arşivler üzerindeki medyanı LME 3.84, PerLTQA 4.08, RealTalk 5.30. Bu ölçek farkları bilgisayar yuvarlama gürültüsü değil. Varyans standardizasyonu da tam kovaryans whitening'i ile aynı şey değildir.

Pozitif σ'ya bölmek işaret bitlerini değiştirmez. Dolayısıyla sadece sayıları standardize edip yine iki tarafı işarete indirgemek, Hamming kodlarını tek başına iyileştirmez. Gözlenen fark, sorgunun sayısal büyüklük bilgisinin puanlamaya kadar taşınmasındadır.


## 8. Merkezleme öncesi veriyi önbellekten geri alma denetimi


Y satırları birim uzunluklu, C = Y - μ ve mean(C)=0. Böylece

`||C_i + μ||² = 1` ve `C_i · μ = -(||C_i||² - mean_i ||C_i||²)/2`.

C tam sütun-ranklıysa bu doğrusal sistem μ'yü tekil olarak belirler. Her arşivde rank, artık, belge/sorgu birim normları, ortalama kimliği ve C sütun ortalamaları kontrol edildi. Sadece rank=96 ve bütün hatalar <10^-8 ise ilgili skorlar kullanıldı; 510 arşivin tamamı geçti. Sorgular μ'yu fit etmek için kullanılmadı, yalnız sonuç doğrulamasında kullanıldı. Bu, yeni SVD çözümü hesaplamak değil, önceki normalleştirilmiş sayısal gösterimin saklı ortalamasını geri almaktır.

Ayrıca kaynak metinden yeni fit edilen 78 arşivde gerçek μ ile karşılaştırıldı. Tek-kayıt aşama dosyasındaki 001be529 ortalamasıyla da doğrulandı. Bu yöntemin geçerliliği birim-belge-normu ve tam-rank varsayımlarına bağlı; sıfır vektörlü veya rank-eksik başka girdilere otomatik genellenmez.


## 9. Kapsam sınırları ve karar


Bu çalışma mevcut sabit kohort üzerindeki açıklayıcı/keşifsel bir denetimdir; yeni dokunulmamış test veya önkayıtlı teyit deneyi değil. Hiçbir model/hiperparametre gold etiketleriyle eğitilmedi; goldlar yalnız puanlama ve tanısal örnek seçimi için kullanıldı. Bir veri kümesindeki ortalama üstünlük her arşiv veya her soru için üstünlük değildir. Arşivler arasında bağımsızlık ayrıca denetlenmedi; LME soruları ortak oturumlar içerebilir.

Arşiv-kümeli, eşleştirilmiş 20.000 bootstrap tekrarına dayanan keşifsel aralıklar ayrı dosyada: PerLTQA +4,24 puan [3,39; 5,05]; RealTalk +2,96 [0,82; 4,98]. Bunlar arşivlerin bağımsız/değiştirilebilir olduğu varsayımına bağlı; RealTalk yalnız 10 küme. Yeni genel-popülasyon veya istatistiksel teyit iddiası olarak kullanılmamalı. LME için popülasyon güven aralığı sunulmadı.

Üretime geçiş kararı verilmedi. GitHub/Drive'a yazılmadı, main değiştirilmedi, Task4F1/BEAM veya başka kapalı görev çalıştırılmadı. Önceki benchmark paketindeki çıkarılmış temsil tarifi yeniden uygulandı; dondurulmuş görev scriptleri yürütülmedi. Deney için iki süreç paralel kullanıldı; bu nedenle yeni ham çalışma süreleri performans karşılaştırması diye sunulmadı.

Karar: Ondalıkları veya son L2 işlemini kaldırmak için gerekçe yok. Yeni eşik aramaya dönmeden, aynı doküman bitlerini sayısal/ölçek-dengelenmiş sorguyla okuyan aday ayrı maliyet ve bağımsız-genelleme denetimine alınabilir. PerLTQA'daki ek SVD kaybı ayrı tutulmalı. Bütün sistem hatalarının veya anlamsal kanıt bulma sorununun çözüldüğü iddia edilmiyor.


## 10. Dosyalar ve dış yöntem kaynakları


- `readout_diagnostic.py`: tam önbellek tekrar oynatımı, bağımsız metrik ve 2×2 ayrıştırma.
- `stage_diagnostic.py`: 48 LME + 30 PerLTQA kaynak metinden aşama karşılaştırması.
- `check_weighted_packed.py`: aynı kodlar üzerinden bağımsız LUT puanlama kontrolü.
- `results/readout_per_query.csv` ve `results/raw_stage_per_query.csv`: bütün soru/aşama puanları ve en iyi gold sıra sınırları.
- `results/rank_inversion_examples.json` ve `results/raw_stage_examples.json`: sonradan seçilmiş tanısal örnekler; temsili örneklem değildir.
- `results/mean_recovery_validation.json`, `weighted_packed_validation.json`, `raw_vs_cache_final_checks.json`: gerçek kontrol kayıtları.
- `results/DIAGNOSIS_SUMMARY.json`: küçük makine-okunur özet.

Kaynak dosya: HANDOFF_2026-09-15.md §1, §3e ve §6a; eski benchmark paketinin scripts/common.py, scripts/quality.py, scripts/build_profile.py ve kaynak çıkarımı. Tohumlar ilk LSA32=5101, son SVD96=5204; devir notundaki son tohum yazım hatası tekrar edilmedi.

Genel yöntem tanımlarının resmî kaynakları (yeni deney sayıları bu sayfalardan alınmadı):
- scikit-learn TruncatedSVD: https://scikit-learn.org/1.6/modules/generated/sklearn.decomposition.TruncatedSVD.html
- scikit-learn cosine similarity: https://scikit-learn.org/1.5/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html

Bu raporun yorumları bu oturumda yazıldı; harici bağımsız denetçi onayı yoktur.
