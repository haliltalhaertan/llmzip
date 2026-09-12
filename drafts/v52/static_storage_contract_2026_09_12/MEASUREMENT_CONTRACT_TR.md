# V52 — Statik arşiv için kalıcı maliyet ölçüm sözleşmesi

Durum: **İNCELEME TASLAĞI — ONAYLANMADI, MÜHÜRLENMEDİ.** Bu belge yeni ölçüm sonucu, deney kolu seçimi, toplam maliyet tavanı veya çalıştırma yetkisi oluşturmaz. Amaç, mevcut maliyet iddiasını doğrulamak ve kapsamını sınırlamaktır; özgün makale katkısı varsayılmaz.

Taban main: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00` (L-095). Bütçe kaynağı: `89d3169adb65a9a2ab7f289997d7c49eb8ccf25c`, `docs/v52/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`. Ham kaynak ve sidecar `source/` altında korunur. Kaynak kendi yetki durumunu chat üzerinden aktarılmış karar, imzalı HR artefaktı değil, olarak tanımlar; bu taslak o statüyü yükseltmez.

## 1. Neyi ölçüyoruz?

**Dondurulmuş, arşiv-yerel bir temsil/kodlayıcı zincirinin ilan edilen dosya biçimindeki kalıcı depolamasını.** İddia, bu sınırda vektör başına ek kalıcı bayt ile arşiv/model düzeyinde paylaşılan baytı ayrı raporlamaktır. Dinamik bir ajan hafızasının güncelleme, toplam RAM, gecikme veya bütün metin depolama maliyetini ölçmüyoruz.

Üç sonuç ayrı tutulur:

1. `code_bytes_per_vector`: yalnız kod yükü; tek başına bütçe uygunluğu değildir.
2. `marginal_persistent_bytes_per_vector`: dondurulmuş model altında ilan edilmiş kalıcı temsil/index paketine bir vektör eklemenin farkı. Kodun yanında vektör başına saklanan norm, ölçek, düzeltme, kimlik veya metadata da dahildir.
3. `effective_persistent_bytes_per_vector`: aynı paketteki toplam kalıcı baytın doğru paylaşım nüfusuna tahsisi. Ortak projektör ve yönteme özgü durum görünürdür; bu sayı 12 bayt tavanına karşı sınanmaz.

Karar ① açıkça **vektör başına saklanan her şeyi** tavana dahil eder. Bu karar "yalnız library code_size" diye daraltılamaz. Mevcut kod/index ölçümü yalnız doğrulanmış sınırı için uygunluk gösterebilir; gerçek zincirde zorunlu başka vektör başına durum bulunursa uygunluk yeniden hesaplanır. İlk sayı doğruyken ikinci sayı 12'yi aşabilir.

Bu paketin arama sonucunu gerçek metne bağlaması için gerekli kimlik/offset durumu varsa görünür kılınır ve vektör başına olanı tavana girer. Kaynak metnin kendisi bu temsil-paketi çalışmasının dışında kalır, bağımlılık olarak ilan edilir; bu nedenle sonuç "bir hatıranın tamamı 12 bayt" diye sunulamaz. Metin dışarıda diye zorunlu kimlik/metadata maliyeti de dışarı atılmaz.

## 2. Ekleme sırasında ne sabit kalıyor?

Arşivin eğitim kümesi/kimliği, TF-IDF sözlüğü ve IDF değerleri, metin işleme kuralları, SVD bileşenleri, gerekli merkez/normalizasyon durumu, kod kitabı/rotasyon, sayısal tip, tohumlar, serileştirme biçimi, paylaşım politikası ve fiziksel model durumu kopyaları sabittir. G_k üyeliği ve D_k her prob anlık görüntüsü için ayrıca bağlanır. Yalnız eklenen kodlanmış kayıt, onun zorunlu vektör başına durumu ve kayıt sayısına bağlı kapsayıcı ek yükü değişir.

Bu, **dondurulmuş modele kayıt ekleme muhasebesidir**; büyüyen bir arşivi yeniden eğitmenin ölçümü değildir. Yeni kelime görülmesi tek başına yeniden fit işlemini zorunlu kılmaz; dondurulmuş sözlüğün OOV davranışı ve yeniden eğitim politikası ayrıca belirtilir. Mevcut uygulamanın her eklemede yeniden fit yaptığı bu belgeyle iddia edilmez.

Dinamik sözlük/IDF/SVD güncellemesi, yeniden kodlama, yazma trafiği, eğitim zamanı ve tepe RAM kapsam dışıdır. Bu dışlama, bunların ücretsiz veya küçük olduğu anlamına gelmez. Genel dinamik maliyet farkı `C(N+1)-C(N)`, paylaşılan durumdaki değişimi de içerebilir; statik sonuç ona taşınmaz.

Sonlu fark ölçümünde q pozitif tamsayıdır. `delta_bytes = B(N+q)-B(N)` toplam ek bayt; `delta_bytes_per_added_vector = delta_bytes/q` o partinin vektör başına ortalama farkıdır. İkisi ayrı kaydedilir; toplam fark doğrudan 12 B/vektör ile karşılaştırılmaz. Kayıt başına zorunlu `b_v+a_v`, N'ye bağlı serileştirme farkı ve paylaşılan durum ayrı uzlaştırılır; aynı bayt iki kez sayılmaz. Birden çok ilan edilmiş N/q noktası, sabit kayıt maliyetini ve olası blok/başlık basamaklarını ayırmalıdır. Lineer olmayan farkların bütçe koşuluna nasıl bağlandığı önceden açıklanıp doğrulanmadan bir parti ortalamasından genel uygunluk hükmü çıkarılmaz; farklar ve gözlenen aralık raporlanır. Paylaşılan model durumu bu yolla marjinal tavana taşınmaz; zorunlu vektör başına durum da paylaşılmış sayılarak dışarı çıkarılmaz. Problar yalnız ayrıca izin verilen sentetik kayıtlarla yapılır; gerçek retrieval çıktısı hesaplanmaz. Bu taslak sayısal prob paneli veya çalıştırma izni tanımlamaz.

Her N ve N+q ayrı bir depolama anlık görüntüsüdür; etkin maliyetin paylaşım nüfusu her biri için yeniden belirtilir. Bu prob, gerçek arşiv üyeliğini değiştirmez. Sabit filo depolaması ile yeni bir bağımsız arşiv eklemenin maliyeti ayrı nesnelerdir; ikincisinde yeni arşiv-yerel durum da eklenir. Kapasite sınırları ve yeniden eğitim tetikleyicileri envanterde bildirilir; dondurulmuş modele eklenebilmesi kalite korunumu iddiası değildir.

## 3. Neyi sayıyoruz ve hangi paydada paylaştırıyoruz?

Bir vektör v için, kayıtların eşit payla tahsis edildiği durumda:

`effective(v) = b_v + a_v + Σ_{k: v ∈ G_k} size(s_k) / D_k`, `D_k = |G_k|`.

- `b_v`: kod baytı; `a_v`: aynı kayıt için diğer zorunlu kalıcı bayt. İkisi birlikte marjinal tavanın kayıt yükünü oluşturur; serileştiricinin N'ye bağlı ek yükü ayrıca fark ölçümünde yakalanır.
- `s_k`: gerçekten saklanan tek bir durum parçası/kopyası; `G_k`: o kopyayı paylaşan, kimliği belirtilmiş vektör grubu.
- `D_k`: gerçek grup kardinalitesi; bir performans ölçümü veya teorik paylaşılabilirlik tahmini değildir. Varsayımsal gelecek vektörlerle maliyet seyreltilmez. Amortizasyon için D_k pozitif olmalıdır; boş indeksin mutlak baytı raporlanır ama sıfıra bölünmez. Bilinmeyen payda sıfır ya da tüm korpus kabul edilmez.
- İki arşiv aynı baytları ayrı dosyalarda saklıyorsa iki kopya sayılır. Gerçekte paylaşılmayan durum, hash'leri aynı diye global sayılmaz. Çakışan paylaşım gruplarında her parça kendi kullanıcılarına tahsis edilir ve fiziksel kopya yalnız bir kez toplanır.
- Tahsis kontrolü: bütün vektörlerin tahsisleri toplamı, sınır içindeki benzersiz fiziksel parçaların ve kayıtların toplam baytına eşit olmalıdır. Atanmamış durum ayrıca görünür kalır; yuvarlama farkları saklanmaz.

Ortak terimin bilinmemesi bazı göreli sıralamaların hesaplanmasını engellemeyebilir; bunun için terimin aynı fiziksel kapsam ve tahsisle bütün yöntemlere eşit eklendiği ayrıca kanıtlanmalıdır. Toplamın bilinmediği açık kalır. Sıfır bayt yazmak, ilgili kalıcı gereksinimin bulunmadığını doğrulamayı gerektirir.

**Arşiv-yerel durumda** payda o arşivin gerçek `N_i` değeridir. 493 yalnız konuşmada kullanılan örnektir; tüm arşivler için sabit veri değildir. Yeni bağımsız arşivler eklemek mevcut arşivin paydasını büyütmez. Tek arşiv büyüdüğünde, model gerçekten sabit kalırsa paylaşılan pay azalır. Global paylaşım ayrı dağıtım konfigürasyonudur; bu çalışmada ölçülmüş sonuç olarak raporlanmaz.

Her arşivin satırı korunur. İki özet ayrı verilir: vektör ağırlıklı `Σ_i C_i / Σ_i N_i` ve arşiv ağırlıklı `mean_i(C_i/N_i)`. Bunlar karıştırılmaz; `mean(shared)/mean(N)` eşit arşiv ağırlıklı sonuç diye sunulmaz. Karşılaştırmalar aynı arşiv/popülasyon ve aynı ağırlıklandırma üzerinde yapılır. Küresel durumun arşivlere tahsis edilmesi gereken ayrı bir senaryo varsa tahsis bir kez yapılır.

### Operasyonel sınır

Sabitlenmiş yazılım ortamında, süreç yeniden başladıktan sonra, **ilan edilen model dosyalarıyla** arşivin temsilini yeniden açıp yeni bir metni aynı uzaya taşımak için hangi durum gerekir? Model durumu kaynak arşivden yeniden fit edilerek örtük biçimde geri kazanılamaz. Bu yeniden açılabilirlik koşulu yalnız dönüşüm/serileştirme içindir; ranking, retrieval ID, mesafe veya kalite değerlendirmesi içermez.

| Kalem | Nasıl ele alınır? |
|---|---|
| Kod, norm/ölçek/düzeltme, kalıcı kimlik/offset/metadata | Kayıt başına ölçülür; mevcutsa 12 B marjinal tavana dahildir |
| TF-IDF sözlüğü, IDF, gerekli işleme konfigürasyonu | Gerçek kalıcı biçim ve paylaşım grubu; veri yoksa UNKNOWN |
| SVD bileşenleri, gerekli merkez/normalizasyon durumu | Dtype/shape ve ham dizi baytı; ayrıca serileştirilmiş gerçek dosya boyutu |
| PQ/ITQ/RQ kod kitabı, rotasyon, centroid ve başlıklar | Yönteme özgü parça; gözlenen gerçek uygulama kimliğiyle bağlanır |
| Ortak paket manifesti ve gerekli başlıklar | Gerçek pakete dahilse bir kez sayılır; araştırma raporu/log/audit kopyası model paketi sayılmaz |
| Runtime/kütüphaneler | Açıkça sabitlenmiş dış ortam; model-paketi toplamına gizlice eklenmez veya bağımsız sistem maliyeti 0 sayılmaz |
| Kaynak metin/gerçek sorgu/gold, gereksiz eğitim cache'i | Bu çalışmanın ölçüm girdisi değildir; okunmaz. Gerçek uygulamanın dış bağımlılığıysa sınır kaydında gösterilir |

Her fiziksel parça için: rol, kaynak commit/yol/SHA256, gerçek ya da surrogate durumu, dtype/shape varsa, ham payload baytı, dosya uzunluğu, paylaşım grup kimliği, D_k, dahil/dışarıda/UNKNOWN gerekçesi kaydedilir. Ham dizi boyutuyla dosya boyutu birbirine eklenmez; biri diğerinin içeriğidir. Ölçüt mantıksal dosya uzunluğudur, filesystem ayrılmış blokları veya runtime RSS değildir. Seçilen sıkıştırma/serileştirme biçimi ölçüm öncesinde sabitlenir; en küçük sonuç veren biçim sonradan seçilmez.

Tarihsel ITQ float32 surrogate paket maliyeti, gerçek float64 fitted R'nin dosya maliyeti ve açık float32 dönüşümü ayrı kimliklerdir. Birbirlerinin yerine geçirilemezler. Önceki yedi sentetik maliyet konfigürasyonu yeni bilimsel deney kollarına dönüşmez; yeni yöntem eğitimi/ayar taraması yoktur.

OpenSearch formülleri yalnız vektör, segment ve paylaşılan durum terimlerinin yapısal karşılaştırması içindir. Bellek tahminini serileştirilmiş kalıcı bayt için sayısal oracle yapmayız; `24` ve `1.1` sabitlerini kendi ölçümümüze taşımayız. Bu metin yeni OpenSearch ölçümü içermez.

## 4. Hangi sonuç hangi kararı değiştirir?

Yeni bir yüzde eşiği veya toplam B/vektör tavanı icat edilmez. Karar ①'de mevcut olan tek bütçe eşiği **marjinal kalıcı ≤12 B/vektör**dür. Ortak projektörün payını o tavana ekleyerek bir kolu diskalifiye etmek kararın nesnesini değiştirir.

Sabit bütçe kararındaki ön kontrol ve abort yükümlülüğü aynen sürer: eşleşmiş karşılaştırmanın runner'ı `measured_persistent_bytes_per_vector <= 12` koşulunu ilgili hesaplamalara geçmeden doğrular; tavan aşımı veya gerçek `code_size`/serileştirme çıktısının deklarasyonla uyuşmaması halinde durur. Bulguyu kaydetmek devam izni oluşturmaz. Bu belge kontrolü çalıştırmaz veya çalıştırma yetkisi vermez; diğer mevcut korumaları ve açık yükümlülükleri kaldırmaz.

| Sınanan iddia/koşul | Çürüten veya sınırlayan gözlem | Önceden belirlenen dispozisyon |
|---|---|---|
| İlan edilen zincir marjinal ≤12 B/vektör | Zorunlu vektör başına durum dahil, yukarıdaki birim/uzlaştırma kuralıyla doğrulanmış B/vektör maliyetinin tavanı aşması veya deklarasyonla uyuşmaması | Eşleşmiş runner ön kontrolde durur; o tam konfigürasyonun uygunluk iddiası kurulmaz, gerçek değer kaydedilir. Yeni kol/ayar arayışı başlatılmaz |
| Model paketi ilan edilen ortamda yeniden açılabilir | Gerekli durum eksik, digest uyuşmuyor veya dönüşüm dışarıda kalmış model verisi gerektiriyor | Eksik bağımlılık/yeniden üretim bulgusu; eksik durum UNKNOWN. Tam maliyet ve kullanılabilirlik iddiası verilmez |
| Paylaşım ve toplam maliyet hesabı eksiksiz | Kopya atlama, çift sayım, belirsiz D_k, bilinmeyen zorunlu kalem | Tam toplam UNKNOWN; yalnız aşağıdaki koşulları sağlayan tekilleştirilmiş kalemlerden alt sınır kurulabilir. Yanlış/çift sayımlı toplam alt sınır sayılmaz |
| Kod-only maliyet eşitliği toplamda sürer | Aynı popülasyonda yönteme özgü durum farklı toplamlar oluşturur | Eşitliğin bozulması betimlenir. Önceden strict sıra yoksa "tersine dönme" denmez |
| Ortak projektör eklemek sıralamayı değiştirir | Her yönteme aynı arşivde aynı P_i ekleniyorsa sıra korunur | Bu değişmezlik cebirseldir; veriyle keşfedilmiş veya projektörün önemsizliğini gösteren sonuç sayılmaz |
| Maliyet farkı bir yöntem seçimini gerektirir | Kalite/fayda ve toplam maliyet için ilan edilmiş karar kuralı yok | "Maliyetler ölçüldü; yöntem seçimi etkisi bu sözleşmede belirlenmedi." Ucuzluk kalite üstünlüğü yerine geçmez |

### Neden önerilen "bütçe ve sıralama değişmezse maddi değil" kuralı aynen alınmadı?

Yalnız **ortak** P_i eklemek, dondurulmuş modelin marjinal maliyetini değiştirmez. Aynı yöntem seti/arşiv/ağırlıklandırmada aynı P_i eklemek toplam maliyet sırasını da değiştirmez. Bu iki sonuç birlikte, P_i çok büyükken de geçerlidir. Dolayısıyla önerilen kural bütün olası ortak maliyetleri "maddi değil" etiketleyebilir; bu bir ölçüm testi değildir.

Bu sözleşme karar temelli kapanışı korur, fakat onu şu ifadeye daraltır: **"Mevcut marjinal bütçe kararı değişmedi; toplam sistem etkisinin maddiliği için ayrıca ilan edilmiş bir karar ölçütü yok."** Projektörün mutlak baytı, efektif maliyete katkısı ve oranı yine eksiksiz raporlanır. Yüzdeyle eşik koymamak, ölçülen oranları saklamak anlamına gelmez. Toplam maliyet kararı gelecekte tanımlanacaksa yeni ve ayrı bir sözleşmeye aittir; bu sonuçlar görülmüşken seçilen ölçüt önceden ilan edilmiş gibi sunulmaz.

## 5. Önemli sonuç çıkmazsa nerede duruyoruz?

**Önceden yazılmış olağan sonuç:** Zorunlu durum eksiksiz sayılmış ve yeniden açılabilirlik doğrulanmışsa; kapsam düzeltmesi, gizli vektör başına yük veya yanlış paylaşım hesabı bulunmazsa ve mevcut bütçe uygunluğu değişmezse, çalışma bir doğrulama/sınırlandırma notu olarak kapanır. "İlan edilen statik sınırda maliyetler doğrulandı; mevcut bütçe kararında değişiklik gerektiren bulgu yok" denir. Bu, toplam maliyetin küçük veya bütün konfigürasyonların eşdeğer olduğunun iddiası değildir.

Bu sonuçta yeni kol, tohum, alt grup, N aralığı, serileştirme arayışı veya held-out ITQ otomatik başlatılmaz. Makale katkısı çıkarmak için kapsam büyütülmez. Bütün önceden ilan edilmiş arşiv satırları korunur; yalnız dikkat çekici örnek seçilmez.

Gerekli model artefaktı veya paylaşım nüfusu bulunamazsa durum **PARTIAL / UNKNOWN** olur; "etki yok" ya da "doğrulandı" diye kapanmaz. Alt sınır yalnız kapsam içinde olduğu doğrulanmış, çakışmayan ve tekilleştirilmiş fiziksel kalemlerin toplamından kurulabilir; kuşkulu kalemler bu kanıtlanmış alt toplama dahil edilmez. B/vektör alt sınırı ayrıca doğru tahsis ve bilinen pozitif nüfus gerektirir. Bu koşullar yoksa ilgili toplam veya etkin değer UNKNOWN kalır; yalnız doğrulanmış mutlak baytlar ve çözülmemiş kalemler ayrı raporlanır. Yanlış veya çift sayımlı toplam alt sınır diye yayımlanmaz. Korpusun yeniden işlenmesi veya güncelleme/kalite çalışması bu taslağın boşluk doldurma yolu değildir.

### Sonraki adımın sınırı

Önce bu taslak incelenir. Sonra yalnız doğrulanmış mevcut model/manifest kaynaklarının envanteri ve ayrı ölçüm planı hazırlanır: arşiv listesi, her N_i, yöntem/artefakt kimlikleri, kalıcı parça sınırı, dosya biçimi, sentetik yükleme/prob girdileri ve beklenen kontroller. Eksik model kaynakları bugünden varmış sayılmaz. Bu taslakta projektör boyutu, gerçek kaynak artefaktlarının hazır olduğu veya tam çalıştırma uygunluğu iddia edilmez.

Task4F1 **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN** olarak kalır. Gerçek query/gold/korpus, retrieval sonuçları, run/finalize/HMAC veya seal işlemleri bu belgeyle açılmaz. main/ledger ve önceki araştırma/HR artefaktları değişmez; bu paket yalnız inceleme taslağıdır.
