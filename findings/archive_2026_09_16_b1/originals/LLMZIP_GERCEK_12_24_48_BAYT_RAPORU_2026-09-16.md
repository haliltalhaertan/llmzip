# LLMZIP — Gerçek 12/24/48 bayt kod merdiveni: kalite, süreç RAM’i ve CPU

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. Sonuç ve kapsam

Aynı veri, sorular, kayıtlar ve kanıt kimlikleriyle 96/192/384-bit paketli doküman kodları gerçekten oluşturuldu ve bu kodlardan arama yapıldı. Sonuçlar sürekli 384-boyutlu vektörün başarısını 48 bayta mal etmiyor.

Kalite kapsamı: LongMemEval 470 arşiv / 470 soru / 231.606 kayıt; PerLTQA **en_v2** 30 / 8.265 / 12.288; LoCoMo 10 / 1.531 / 5.882. Toplam **510 arşiv, 10.266 soru, 249.776 kayıt**. Bütün veriler daha önce görüldü; kör test veya resmi önkayıt değil. Her benchmark ayrı raporlanıyor.

**Ana sonuç:** LongMemEval’de 24 ve 48 bayt 12’den daha iyi FR@3 veriyor, 48’in 24’e ilave faydası belirsiz. PerLTQA’da 24 bayt daha iyi, 48 bayt 24’ten daha kötü. LoCoMo’da 48 bayt en yüksek gözlenen değeri veriyor. Hiçbiri evrensel optimum veya bütün rakiplere üstünlük anlamına gelmiyor.

**RealTalk eksik:** 705 soruluk eski 96-boyut önbelleği mevcut, fakat daha büyük kodu üretmek için özgün doküman metni gerekiyor. 1.231.497.097 baytlık Drive yedeği, bağlantının 268.435.456 bayt indirme sınırına takıldı (413). GitHub bağlayıcısından metin görülebildi fakat bu oturumda eksiksiz ham dosyayı çalışma alanına aktarmak mümkün olmadı; yerel ağ DNS isteği de başarısız oldu. 06_review_transfer.tar yedeği hash doğrulanarak incelendi; ihtiyaç duyulan ham RealTalk arşivi çıkmadı. Bu nedenle **RealTalk 24/48 için sonuç uydurulmadı veya eski rakamlardan tahmin edilmedi**.

## 2. Önemli yöntem ayrımı: aynı EXACT hesaplayıcı, eski yöntem ayrı kontrol

Ana üç boyut aynı **tam Gram özayrışımı** hesaplayıcısını kullanıyor. Üretimdeki eski randomized SVD96 ile aynı algoritma değil. Eski 96-bit qscale kalitesi ayrıca yeniden hesaplanıp tabloda korunuyor. Boyut etkisi exact96 ile exact192/384 arasında, mevcut yönteme net fark ise original96 ile yeni kollar arasında okunmalı.

Geniş randomized384 çözümünün bir arşivdeki kapasite ölçümü 14,03 CPU saniye, exact Gram özayrışımı 0,146 CPU saniyeydi; kaliteye bakmadan ortak exact aileyle tam kohort seçildi. Bu tek-arşiv kapasite kontrolü genel hız kazancı veya yöntem üstünlüğü değildir; kaynakta CAPACITY_ONLY.json olarak ayrı durur. Ölçümlerin sonunda plan hash’i hâlâ `31b5ac3c4b0b230354ebf39f37e8ce8388b8b61094325ea281d0fd9b580824fe`.

Özellikler değişmedi: normalize word-TFIDF (1–2 gram, İngilizce stopword, sublinear TF), normalize char_wb TF-IDF (3–5 gram), word kolundan normalize LSA32 (seed5101). Z=[LSA32 | word | char]. SVD için yalnız arşiv dokümanları kullanılır; sorgu/gold fit girdisi değil. Her genişlikte projeksiyon sonrası satır normalleştirme, doküman ortalamasını çıkarma ve doküman standart sapması ayrı hesaplanır. Bu nedenle 12 baytın bitleri 24 baytın ilk 12 baytı olmak zorunda değildir; karşılaştırılan şey aynı reçetenin üç boyutu.

G=ZZᵀ, özdeğerler azalan sırada; eşik max_eigenvalue×1e−12. U sütunlarının işaretleri en büyük mutlak eleman pozitif olacak şekilde belirlenir. `A=U_k/s_k`, dokümanlar `normalize(U_k*s_k)−mean`, sorgular `normalize((Zq Zᵀ) A)−mean`. Paketli kod bir koordinat için bir bit, little-endian byte-plane düzendedir.

Küçük arşivler dışlanmadı. PerLTQA’da 8 arşiv (2.217 soru) 384’ten az etkin boyuta sahip (293–381); LoCoMo’da 1 arşiv (81 soru) 369 etkin boyutlu. Eksik boyutlar sabit koordinat olarak doldurulup **gerçek 48 bayt saklama maliyeti** ödendi. Bunlar 384 bağımsız bilgi yönü taşımıyor. 96/192’de rank sınırlaması yok. Ayrıntılar SUMMARY.json/rank_caps.

## 3. Kalite: gerçek çalışan qscale sıralaması

Ana ölçüt **deterministik Fractional Evidence Recall@3**: etiketli kanıt kayıtlarının ilk üçte bulunan payı; yanıt doğruluğu veya başarılı soru oranı değil. Gerçek top10 listesi aynı puanlama çekirdeğinden ve aynı tie sırasından üretilir. Eşitlikte `SHA256(top10-r1|archive|row)` önceliği, gold kullanılmadan sabittir. Beklenen-tie FR/Hit değerleri ayrı alanlarda da saklanmıştır; iyimser/oracle eşitlik yok.

| Veri | 12 B / 96 bit | 24 B / 192 bit | 48 B / 384 bit |
|---|---|---|---|
| LongMemEval | 52,47 | 61,48 | 61,75 |
| PerLTQA en_v2 | 52,98 | 54,82 | 51,87 |
| LoCoMo | 35,11 | 41,21 | 44,15 |


Eski yöntem de görünür tutuldu (FR@3, %):

| Veri | Eski randomized96 qscale | Yeni exact96 qscale | Exact192 qscale | Exact384 qscale |
|---|---|---|---|---|
| LongMemEval | 54,27 | 52,47 | 61,48 | 61,75 |
| PerLTQA en_v2 | 53,24 | 52,98 | 54,82 | 51,87 |
| LoCoMo | 35,84 | 35,11 | 41,21 | 44,15 |


İlk-10 Hit, % (en az bir doğru kanıt):

| Veri | 12 B Hit@10 | 24 B Hit@10 | 48 B Hit@10 |
|---|---|---|---|
| LongMemEval | 88,72 | 89,15 | 86,60 |
| PerLTQA en_v2 | 79,89 | 80,71 | 79,41 |
| LoCoMo | 55,39 | 62,12 | 63,16 |


LongMemEval’de 24→48 baytta FR@3 yalnız +0,27 puan artarken Hit@10 89,15→86,60 düşüyor. PerLTQA’da 24→48 FR@3 −2,95 puan; “boyut arttıysa kalite mutlaka artar” sonucu yok. LoCoMo’da 12→48 FR@3 +9,04, eski production96’ya göre +8,30 puan.

### Güçlü kalite kontrolleri, aynı soru/kayıt/tie kuralı

| Veri | BM25 eşlenmiş | Tam Z | Float_std96 | Float_std192 | Float_std384 |
|---|---|---|---|---|---|
| LongMemEval | 57,14 | 57,47 | 54,85 | 59,89 | 63,61 |
| PerLTQA en_v2 | 60,14 | 60,15 | 56,24 | 57,78 | 54,49 |
| LoCoMo | 42,87 | 42,84 | 38,85 | 43,90 | 44,75 |


BM25’nin tokenizerı frozen word kanalına eşlendi: English stopword çıkarma, Unicode en az iki karakter, unigram+bigrams; k1=1,2, b=0,75 önceden sabit. Bu, önceki farklı tokenizerlı BM25 sayısıyla aynı kol değil. BM25 sonucu parametre taramasından seçilmedi; fakat tüm olası BM25 ayarlarının en iyisi olduğu iddia edilmiyor.

LongMemEval’de 24/48 kodlar bu BM25 kontrolünden sayısal olarak +4,33/+4,61 FR@3 puan yüksek. LoCoMo’da 48 B − BM25 farkı +1,28; keşifsel aralık −0,21 ile +2,56, kesin üstünlük yok. PerLTQA’da 24 bayt bile BM25’nin −5,32 puan gerisinde. Yeni kolların bütün literatürü geçtiği, B8’den veya nöral rakiplerden daha iyi olduğu söylenemez. Float/BM25 **kalite** kontrolleridir; bu turda onların toplam RSS/latency profili alınmadı.

Hamming ve ölçeklemesiz asimetrik okumalar da aynı gerçek paketli kodlardan hesaplandı; tüm değerler QUALITY_LEVELS.csv içindedir. Paketli qscale çalışırken kalite/hız için hazır ±1 doküman matrisi kullanılmadı.

### Eşleştirilmiş belirsizlik

| Veri | Karşılaştırma | FR@3 farkı, puan | Keşifsel %95 aralık | İyileşen/gerileyen soru |
|---|---|---|---|---|
| LongMemEval | 24 B − 12 B | 9,01 | [6,12; 11,91] | 99/34 |
| LongMemEval | 48 B − 12 B | 9,28 | [6,03; 12,56] | 114/46 |
| LongMemEval | 48 B − 24 B | 0,27 | [-1,94; 2,45] | 44/40 |
| LongMemEval | 24 B − eski 12 B | 7,20 | [4,45; 9,96] | 88/33 |
| LongMemEval | 48 B − eski 12 B | 7,48 | [4,38; 10,62] | 106/44 |
| LoCoMo | 24 B − 12 B | 6,10 | [4,46; 7,83] | 188/83 |
| LoCoMo | 48 B − 12 B | 9,04 | [6,16; 11,84] | 262/114 |
| LoCoMo | 48 B − 24 B | 2,93 | [1,23; 4,51] | 123/81 |
| LoCoMo | 24 B − eski 12 B | 5,37 | [3,51; 7,48] | 171/84 |
| LoCoMo | 48 B − eski 12 B | 8,30 | [5,11; 11,49] | 241/112 |
| PerLTQA en_v2 | 24 B − 12 B | 1,84 | [1,00; 2,70] | 733/518 |
| PerLTQA en_v2 | 48 B − 12 B | -1,12 | [-2,29; 0,07] | 884/981 |
| PerLTQA en_v2 | 48 B − 24 B | -2,95 | [-3,87; -2,01] | 471/787 |
| PerLTQA en_v2 | 24 B − eski 12 B | 1,58 | [0,78; 2,39] | 783/587 |
| PerLTQA en_v2 | 48 B − eski 12 B | -1,37 | [-2,48; -0,27] | 894/1013 |


20.000 arşiv-cluster bootstrap, seed20260916, her tekrarın içindeki toplam-soru ağırlıklı fark. Veri kümeleri birleştirilmez. LoCoMo yalnız 10, PerLTQA 30 arşivdir; bağımsız/değiştirilebilir kümeler varsayımı ve çoklu karşılaştırma düzeltmesi yokluğu nedeniyle aralıklar keşifseldir. LME sorularının arşivleri ortak konuşma içerikleri taşıyabilir: bu aralıklar bağımsız nüfus garantisi değil, betimsel duyarlılıktır. Sonucu gördükten sonra her benchmark’a ayrı kod seçip bunları tek önceden tanımlanmış yöntemin performansıymış gibi birleştirmedik.

## 4. CPU ve metinden sonuca süre: gerçekten ölçülen sistem

Donanım AMD EPYC 9V74, Linux x86-64, AVX-512; 5 görünür vCPU, 4 çekirdek kotası, 4 GiB cgroup RAM sınırı. Her zamanlama süreci CPU0’a sabitlendi ve tüm BLAS/OpenMP yolları tek iş parçacığı. Paylaşımlı/sanallaştırılmış ortam; üretim sisteminde kuyruk/SLA sonucu değil.

Kalite işlemleri iki yerel worker süreçte tamamlandı; **sonra** bütün kaynak profilleri seri alındı. Bunlar iki LLM alt ajanı veya bağımsız denetçi değil. Alt-LLM çalıştırma aracı kullanılmadı. Kalite ve zamanlama süreçleri üst üste bindirilmedi.

Kaynak paneli, sonuçlardan önce toplam metin boyutuna göre seçildi: 5 LME arşivi (min/çeyrek/medyan/üççeyrek/max), 3 PerLTQA ve 3 LoCoMo (min/medyan/max). **11 arşiv, 65 farklı soru; boyut başına üç temiz süreç; her soruya dokuz sıcak tekrar.** Toplam 99 servis süreci, 5.265 ölçülen metin→top10 çağrısı. Ek olarak 33 taze kurulum süreci.

Çağrı kapsamı: ham sorgu metni→kelime/karakter/LSA özellikleri→dual projeksiyon→normalleştirme/merkezleme→sigma düzeltmesi/LUT hazırlığı→bütün paketli kayıtları puanlama→deterministik ilk10 seçimi→özgün metin ve kimlikleri bellekte erişme. C float64 4-bit-LUT/AVX-512 çekirdeği; hız için ağırlık hassasiyeti azaltılmadı.

Tablolar önce her sorunun süreç içi dokuz tekrar medyanını, sonra aynı sorunun üç süreç medyanını, ardından paneldeki soru medyanlarının ortalamasını verir. Bir datasetin tüm sorularının latency ortalaması veya p95 SLA’sı değildir. Ham tekrarlar saklandı.

**CPU işlem zamanı, milisaniye/sorgu:**

| Veri | 12 B CPU ms | 24 B CPU ms | 48 B CPU ms |
|---|---|---|---|
| LongMemEval | 4,017 | 4,075 | 4,099 |
| PerLTQA en_v2 | 1,358 | 1,381 | 1,396 |
| LoCoMo | 1,321 | 1,417 | 1,409 |


**Duvar saati, milisaniye/sorgu:**

| Veri | 12 B duvar ms | 24 B duvar ms | 48 B duvar ms |
|---|---|---|---|
| LongMemEval | 4,022 | 4,078 | 4,101 |
| PerLTQA en_v2 | 1,359 | 1,382 | 1,397 |
| LoCoMo | 1,322 | 1,418 | 1,410 |


**Sorgunun sayısal kodu hazır: puanlama + aynı ilk10 + metin erişimi**, mikrosaniye:

| Veri | 12 B µs | 24 B µs | 48 B µs |
|---|---|---|---|
| LongMemEval | 25,93 | 27,15 | 30,62 |
| PerLTQA en_v2 | 23,92 | 25,25 | 27,53 |
| LoCoMo | 25,85 | 28,04 | 31,75 |


Tekil metin çağrısındaki zaman ölçücü ek yükü ve cache farkı nedeniyle alt-adımların ayrı medyanlarının toplamı toplam-medyana eşit olmak zorunda değildir. Hazır-sorgu kontrolü 100 çağrılık bloklarla sayaç yükünü azaltır. Bunlar AVX-512 uygulama ölçümleri; tüm CPU’larda aynı hız oranı beklenmez.

12→48 ortalama CPU zamanı bu panelde LME yaklaşık %2,0; PerLTQA %2,8; LoCoMo %6,7 arttı. Ortak kodlama işi baskın olduğu için kod dört kat büyüyünce toplam CPU dört kat olmadı. 24/48 arasındaki çok küçük ters süre farkları anlamlı hız kazancı sayılmaz; cache/scheduler gürültüsü olasıdır. Eski geniş projektörlü uygulamanın eski 15 ms rakamıyla buradaki 4 ms’yi eş koşullu hızlanma diye karşılaştırmıyoruz: bu turda farklı, dual servis kodlayıcısı kullanıldı.

İndeks yüklü/sıcak; soğuk disk, ağ, LLM cevap üretimi, istek kuyruğu, concurrent kullanıcılar, doğrudan güç/enerji ölçülmedi. Kodlayıcı her sorguda yeniden eğitilmez; ayrı kurulum bir keredir.

## 5. Toplam RAM: yalnız bit dizisi değil

Her temiz servis sürecinde yalnız **bir aktif arşiv ve bir kod boyutu** yüklendi. Süreçte orijinal kayıt metinleri/kimlikleri, word/char sözlükleri ve IDF dizileri, LSA32 projektörü, seyrek `Zᵀ`, `A_k`, ortalama/sigma, paketli kodlar, sorgu/puanlama/seçim tamponları ve Python/NumPy/SciPy çalışma zamanı bulunur. Test etiketleri sıralamaya verilmez; servis ölçümünde tam query/gold nesnesi tutulmaz.

**Sıcak servis sırasında toplam resident RSS’nin panel arşivleri medyanı, MB (10^6 bayt):**

| Veri | 12 B toplam RSS MB | 24 B toplam RSS MB | 48 B toplam RSS MB |
|---|---|---|---|
| LongMemEval | 203,73 | 204,13 | 204,89 |
| PerLTQA en_v2 | 171,29 | 171,59 | 172,20 |
| LoCoMo | 171,77 | 172,32 | 173,38 |


Bu **510 arşivin aynı anda RAM’de olduğu bir servis değildir**. Her arşivin ölçümünü toplayıp gerçek çoklu-arşiv RSS’si ilan etmiyoruz. Runtime/library tabanı tek başına yaklaşık 161 MB; bu yüzden tablodaki küçük farkları bileşen maliyetinden bağımsız “bedava” sayamayız. SUMMARY.json ayrıca loaded RSS, USS, tabanın üstüne ek yük, arşiv aralığı ve peak değerlerini verir.

Tüm kaynak-panel süreçlerinde görülen tepe değerleri ve tek-geçişli kurulum CPU:

| Veri | Boyut | En yüksek servis RSS MB | En yüksek kurulum RSS MB | Kurulum CPU ortalama s |
|---|---|---|---|---|
| LongMemEval | 12 B | 204,88 | 240,98 | 0,884 |
| LongMemEval | 24 B | 205,41 | 241,09 | 0,843 |
| LongMemEval | 48 B | 206,20 | 240,69 | 0,859 |
| PerLTQA en_v2 | 12 B | 173,72 | 184,14 | 0,199 |
| PerLTQA en_v2 | 24 B | 174,06 | 185,97 | 0,179 |
| PerLTQA en_v2 | 48 B | 174,94 | 187,85 | 0,184 |
| LoCoMo | 12 B | 172,26 | 186,92 | 0,214 |
| LoCoMo | 24 B | 172,77 | 187,19 | 0,220 |
| LoCoMo | 48 B | 173,81 | 192,11 | 0,220 |


Kurulum tepe RAM’i, servis tepe RAM’inden ayrıdır. Kurulumda aynı tam Gram özayrışımı bütün genişliklerde yapılır; 96 için optimize kısmi eigensolver kullanılmadı. Yüksek boyutun bir yerde daha az kurulum süresi çıkması, az sayıda tekrarlı tek-geçiş ölçümünde hız üstünlüğü değildir. CPU fit süresine dosya okuma/pickle serileştirme dahil değil; bellekteki metinden çalışan indeks durumuna geçiş dahildir.

### Saklama muhasebesi: küçük kodun arkasında büyük kodlayıcı var

Yalnız gerçek paketli kayıt dizilerinin toplamı:

| Veri | Kayıt | 12 B kod toplamı MB | 24 B kod toplamı MB | 48 B kod toplamı MB |
|---|---|---|---|---|
| LongMemEval | 231606 | 2,7793 | 5,5585 | 11,1171 |
| PerLTQA en_v2 | 12288 | 0,1475 | 0,2949 | 0,5898 |
| LoCoMo | 5882 | 0,0706 | 0,1412 | 0,2823 |


Bütün 249.776 kayıt için kodlar 2.997.312 / 5.994.624 / 11.989.248 bayt. Fakat bu tek başına sorgu kodlayamaz.

Tüm arşivler için ortak kodlayıcı + ilgili genişlik durumunu pickle5 ile serileştirerek ölçülen toplam baytlar (bu **disk/model serileştirme boyutu**, RAM değil):

| Veri | 12 B model toplamı MB | 24 B model toplamı MB | 48 B model toplamı MB |
|---|---|---|---|
| LongMemEval | 9948,88 | 10130,25 | 10493,00 |
| PerLTQA en_v2 | 147,58 | 157,21 | 175,97 |
| LoCoMo | 51,45 | 56,05 | 65,22 |


Örneğin LME’nin 470 ayrı arşiv modeli 12 bayt kolunda toplam yaklaşık **9,95 GB serileştirilmiş durum** gerektiriyor; bunun doküman bitleri yalnız 2,78 MB. Modellerin tamamını aynı anda yüklemedik; 11 panel modeli diske kaydedildi, kalan modellerin serileştirme boyutu üretilen byte dizisinden ölçüldü.

Önemli teknik sınır: `A_k` matrisi N×k float64’tür. Bu bir doküman benzerlik indeksi değil, sorgu projektörünün faktörüdür; **büyük olması yine de gerçek maliyettir**. 12/24/48 bit dizilerine ek olarak bütün kohortta `A` toplamı 191,83 / 383,66 / 766,76 MB’dir. Bitleri küçük tutup bu yardımcı matrisi maliyetten çıkarmadık. Seyrek `Zᵀ` ve sözlük/LSA modeli de ayrıca gereklidir. Bu deney “tüm sistem 12 bayt/kayıt” veya “toplam RAM 32 kat küçük” iddiasını desteklemez. Ortak yapıları tekilleştirme/servis mimarisini küçültme bu turda test edilmedi.

## 6. Kendi doğrulamalarımız ve sınırlılıklar

- 510 input SHA-256 ve plan hash’i doğrulandı; 225.852 soru-kol satırında beklenen kapsam/tekillik mevcut.
- Eski Hamming, ASYM, qscale, float_std sonuçlarının **246.384 skaler expected metrik** karşılaştırmasında eski kayıtlarla fark 0.
- 18 arşivde production randomized96 ham metinden yeniden kuruldu. Eski bit cache’i bulunan 8 arşivde bit farkı 0, maksimum sürekli fark 1.44e-12. LoCoMo’nun 10 arşivinde eski scalar metrics ile karşılaştırma yapıldı.
- Önceki exact0 pilotunun 64 arşivindeki 235.680 karşılaştırma fark 0.
- Paketli qscale/Hamming sonuçları bütün 10.266 sorgu × üç genişlikte ayrı unpack+dot/tam-sıralama koduyla kontrol edildi. İlk-10 listesinde **0 fark**, 739.152 metric karşılaştırmasının en büyük farkı 2.22e-16.
- Servis profillerinin 585 farklı süreç/soru/genişlik top10 listesi kalite listesinin aynısı; 99 servis kod hash’i ve 33 taze-kurulum kod hash’i eşleşti.
- 1.890 küçük metric durumu 3.017 açık sınır seçimiyle kontrol edildi. 24 paketli sentetik denemede scalar/SIMD skorları birebir; gerçek veride direct dot ile en büyük skor farkı 4.55e-13, ranking/metric karşılığı değişmedi.

İki iç denetim düzeltmesi kayda geçirildi. İlk ölçüm betiğinin eski referans isim eşlemesi sadece Hamming/qscale’yi kontrol ediyor, ASYM/float isimleri uyuşmadığından atlanıyordu; sonuç-sonrası ayrı denetçi betik doğru `asym_raw/float_std64` isimleriyle dört kolu da tamamladı. Ayrı denetçinin iki kapsam sayacı DONE.gates yerine üst seviyeye baktığından ilk yazımda 0 raporladı; yalnız bu metadata sayaçları 18/64 olarak düzeltildi. **Soru sonuçları, eşikler, genişlikler ve asıl ölçümler değiştirilmedi.**

Uygulayıcı ve bu ek kontrollerin yazarı aynı asistandır. Ayrı kontrol implementasyonu kullanılması dış bağımsız denetim değildir. Hiçbir yeni sonuç GitHub/Drive’a bu turda yazılmadı; `main`, dondurulmuş dosyalar ve Task4F1/BEAM sınırı değişmedi.

## 7. Karar

Mevcut veride 24 bayt, LongMemEval için 48’e yakın FR@3 ve daha iyi Hit@10 ile güçlü bir maliyet/kalite adayı; PerLTQA’da denenmiş üç genişlik içinde en iyi fakat güçlü BM25’nin gerisinde. LoCoMo’da 48 baytın 24’e ek FR@3 kazancı var; yine de yalnız 10 arşiv ve görülen veriler, BM25’ye kesin üstünlük yok. Bu seçimler sonuç sonrası araştırma önerisidir, doğrulanmış üretim yönlendirme kuralı değildir.

**Artık “12 bayt mı 48 bayt mı?” sorusunun üç veri kümesi için gerçek cevabı var: tek bir ortak kazanan yok.** Daha büyük kod bazen faydalı, bazen zararlı; toplam maliyetin büyük kısmını küçük bit dizisinin dışındaki kodlayıcı taşıyor. Yöntemi daha ucuz hâle getirme hedefinde kodlayıcı durumu ve toplam servis mimarisi de ele alınmalı. RealTalk ölçümü tamamlanmadı.

## 8. Dosyalar ve kaynaklar

PLAN_BEFORE_RUN.json ve SHA256; results/SUMMARY.json, SELF_AUDIT.json, ENVIRONMENT.json; QUALITY_LEVELS.csv ve RESOURCE_LEVELS.csv; 510 quality.jsonl.gz, packed_inputs.npz, groups.json ve DONE.json; 99 servis/33 kurulum ham JSON; scripts/core.py, packed.c, run_quality.py, profile_worker.py, audit_and_summarize.py. Kaynak girdiler inputs/ altında kendi plan hash’leriyle.

Önceki kaynak: LLMZIP_KISITLI_CEZA_PILOT_2026-09-16 (e8e2b0f0e3e7ba624d23b5d52ff5d912b6f9cc454ac309eda1180d7c943e0238); LLMZIP_BENCHMARK_2026-09-15 ve hash-doğrulanmış 03_regen/04_bench3/02_dataset yedekleri. Daha önceki seed/tie/BM25 düzeltmeleri korunmuştur. Kaynaklar yeniden araştırma sonucu olarak sunulmadı.

Ortam: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0; gcc (Debian 14.2.0-19) 14.2.0. Tam versiyon ve donanım ENVIRONMENT.json.
