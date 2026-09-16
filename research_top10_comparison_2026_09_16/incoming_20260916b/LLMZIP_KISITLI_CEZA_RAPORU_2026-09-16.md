# LLMZIP — Veri uzayıyla sınırlı koruma cezası ve gerçek sıralama kaybı ayrıştırması

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. Karar

Yeni matematiksel aday ilk defa gerçek metin arama verisinde çalıştırıldı. Küçük sentetik örnekte saptanan boş-yön riski, arşivin sayısal satır uzayıyla sınırlandırma sayesinde bu pilotta ortaya çıkmadı: bütün yeni kollar 96 etkin boyut, sıfır sabit bit sütunu ve sayısal kontrol kapılarını sağladı. Ancak güvenlikli ve doğru çözülmüş olması, arama üstünlüğü anlamına gelmiyor.

LoCoMo'da cezanın aynı exact çözümleyicinin cezasız kontrolüne göre FR@3 etkisi olumlu: düşük ceza +1,65, yüksek ceza +2,15 yüzde puan. Eski production qscale'e göre yüksek cezanın farkı +1,42 puan; bunun keşifsel aralığı sıfırı kapsıyor. PerLTQA'da fark küçük/belirsiz; 24 soruluk LME panelinde cezanın aynı çözümleyiciye göre net faydası yok. Güçlü float/BM25 karşılaştırmaları ve B8 eksikliği nedeniyle en iyi yöntem veya üretim onayı yok.

Önemli yeni tanı: gerçekten atılan bileşenin puan üstünlüğünü taşıdığı çiftler var; aynı zamanda aynı 96 sayının ölçekleri düzeltilince tekrar doğru sıralanan çiftler de var. "Bütün bilgi SVD'de kayboluyor" veya "bilgi hiç kaybolmuyor, yalnız ölçek" ikilemi yanlış. İki etki farklı örneklerde ve aynı zincirde görülebiliyor.

## 2. Gerçek kapsam ve önceden sabitlenen kurallar

Toplam 64 arşiv, 9.820 soru, 29.905 kayıt. LME: önceki, metin uzunluğuna göre eşit aralıklı 48'li panelin eşit aralıklı 24 öğesi; yalnız 24 soru. PerLTQA en_v2: 30 arşiv / 8.265 sorunun tamamı. LoCoMo: aynı 10 arşiv / 1.531 değerlendirilebilir soru. Bütün bu veriler proje tarafından daha önce görülmüştür; yeni gizli/bağımsız test değildir. LME paneli temsili rastgele örneklem değildir ve bu kez hit@10'unun %100 çıkması tüm LME'ye taşınamaz.

`PLAN_BEFORE_RUN.json` seçim, gamma değerleri, korunan özellikler, sıfır/izotropik kapılar ve metrikler yazıldıktan sonra hash'lendi. Hash: `122e54519b3291020c940a7a695eb4c3f42c40a6b07b865e58f121275205814e`. Son kontrolde değişmedi. Yerel çalışma kaydı; resmî önkayıt veya immutable üçüncü-taraf zaman damgası değil.

Ana ölçüt uniform boundary-tie beklentisi altında FR@3. İkincil: hit@3/10/100 ve FR@10/100. Her benchmark ayrı. Diğer sohbetin deterministik tie tabloları veya başka LoCoMo kohortlarıyla birleştirilmedi. BM25 de bu tabloda aynı beklenen-tie metriğiyle raporlanıyor; önceki deterministik tabloda son ondalık basamaklar farklı olabilir.

LoCoMo kaynak metni ve inherited dışlamalar korundu; görsel açıklaması/QA cevabı eklenmedi. PerLTQA özgün en_v2 metinleri yeniden oluşturulup kimlik/metin çiftleri önbellekle doğrulandı. Sadece arşiv metni ve DF bilgileri koruma yönlerini belirliyor. Query/gold, ceza matrisini veya gamma'yı belirlemek için kullanılmadı. Gold eşitlik kontrolleri ve değerlendirme, optimizasyon girdisi değil.

RealTalk ham metin deneyi yapılmadı. Serbest, veri uzayı dışına çıkabilen toplamsal ceza bu gerçek pilotta denenmedi; önceki sentetik risk, gerçek serbest-kol başarısızlığı diye sunulmuyor.

## 3. Test edilen amaç ve hesap

Z: LSA32 + normalize kelime TF-IDF + normalize karakter TF-IDF. İlk LSA32 tohumu 5101; eski randomized SVD96 tohumu 5204. Üretim tarifi değiştirilmeden yeniden kuruldu.

Tam sayısal satır uzayı `Z=U diag(s) Vr^T` ile tanımlanır. Gram özdeğerleri en büyüğün 1e-12 katından büyükse tutuldu; rank<96 olsaydı durulacaktı. Eski ilk96 yönle sınırlı kalınmadı.

D: yalnız kelime kanalında, uzunluğu en az2 olan unigramlar; arşiv DF=1 veya2 ise ağırlık1, diğer bütün özellikler (karakter/LSA dahil) ağırlık0. Bu, bilimsel önem veya cevap ilgililiği bildiğimiz anlamına gelmiyor; nadirlik vekiliyle tanımlanan açık bir aday.

K = Vr^T D Vr
H = diag(s^2) + lambda K
Vnew = Vr R96, R96 = H'nin öndeki96 özvektörü.

Gerçekte geniş özellik-kare matrisi oluşturulmadı. `Z_R` korunan kelime sütunları ise:

K = (U/s)^T (Z_R Z_R^T) (U/s)
A = (U/s) R96
Vnew = Z^T A
Docs_new = (U*s) R96
Queries_new = (Zq Z^T) A

lambda = gamma * (ZZ^T'nin 96. büyük özdeğeri) / lambda_max(K).
İki gamma baştan sabit: 0,25 ve1,00. Benchmark başına kazanan gamma seçilmedi. Bütün kollarda aynı son normalleştirme, ortalama çıkarma ve dokümandan sigma hesabı kullanıldı. Puanlayıcılar: ham merkezli kosinüs, standartlaştırılmış kosinüs, eski asym, qscale, Hamming. Kod bütçesi hâlâ96 bit; yeni kodların eski kodlarla aynı olması beklenmiyor.

Exact0, üretim randomized SVD'den ayrı kontrol. Aynı çözümleyiciyle lambda0 ve D=I kontrolleri ayrıca çalıştırıldı. İdeal D=I kaydırması aynı altuzayı ve eksenleri korur (dejenere bazlarda ayrıca dikkat gerekir). Bu pilotta izotropik kontrolde doküman/sorgu bitleri ve qscale skorları sıfır farkla eşleşti.

Kısıtlı amaç, önceki serbest amaçla aynı problem değil. Nullspace yönü seçememesi bir güvence; iyi FR@3, iyi ölçekler veya düşük maliyet garantisi değil.

## 4. Ana FR@3 sonuçları (%): aynı bütçe, dört ayrı üretim kolu

| Veri | Eski production qscale | Exact çözümleyici, ceza0 | Kısıtlı ceza gamma0,25 | Kısıtlı ceza gamma1 |
|---|---:|---:|---:|---:|
| LME — 24 soru | 60,69 | 64,03 | 62,78 | 64,03 |
| PerLTQA — 8.265 soru | 53,24 | 52,98 | 53,38 | 53,66 |
| LoCoMo — 1.531 soru | 35,84 | 35,11 | 36,76 | 37,26 |

LME'de eskiye göre görünen +3,33 puanın tamamı exact0 kontrolünde de var. Bunu nadirlik cezasının kazancı diye yazmak yanlış olur. PerLTQA'da exact0 eskiye göre -0,25 puan, yüksek ceza exact0'a göre +0,67 puan. LoCoMo'da exact0 eskiye göre -0,73 puan; yüksek ceza exact0'a göre +2,15, eskiye göre +1,42 puan. Çözümleyici ve amaç etkileri bu nedenle ayrı raporlandı.

### Eşleştirilmiş farklar

| Veri | Karşılaştırma | FR@3 farkı (puan) | Keşifsel %95 aralık | İyileşen/gerileyen soru |
|---|---|---:|---|---:|
| LME | penalty0.25/qscale minus exact0/qscale | -1,25 | [-8,33; 5,83] | 2/2 |
| LME | penalty1/qscale minus exact0/qscale | 0,00 | [-6,25; 6,25] | 1/1 |
| LME | penalty1/qscale minus production/qscale | 3,33 | [-1,67; 10,42] | 2/1 |
| PerLTQA | penalty0.25/qscale minus exact0/qscale | 0,40 | [-0,30; 1,01] | 414/380 |
| PerLTQA | penalty1/qscale minus exact0/qscale | 0,67 | [-0,23; 1,52] | 638/606 |
| PerLTQA | penalty1/qscale minus production/qscale | 0,42 | [-0,38; 1,19] | 620/603 |
| LoCoMo | penalty0.25/qscale minus exact0/qscale | 1,65 | [0,27; 2,71] | 79/43 |
| LoCoMo | penalty1/qscale minus exact0/qscale | 2,15 | [0,57; 3,93] | 129/84 |
| LoCoMo | penalty1/qscale minus production/qscale | 1,42 | [-0,55; 3,36] | 125/96 |

20.000 arşiv bootstrap örneklemi, seed916640; her örnekte soru toplamlarıyla ağırlıklı ortalama. PerLTQA30, LoCoMo10 arşiv; değiştirilebilir/bağımsız arşiv varsayımına bağlı. LME ortak oturumlar ve seçilmiş24'lük panel nedeniyle aralığı nüfus güven aralığı değil, yalnız betimsel duyarlılık. Çoklu deneme düzeltmesi yok. İki gamma ve birçok metrik düşünüldüğü için "genel bilimsel teyit" çıkarılmaz. LoCoMo yüksek-ceza/exact0 FR@3 karşılaştırmasında arşiv yönleri8 artış/2 azalış; iki taraflı binom işaret testi p=0,1094. Dolayısıyla bootstrap aralığının sıfırı dışlamasını bütün istatistiksel yaklaşımların aynı hükmü verdiği biçiminde sunmuyoruz; bu testler farklı varsayım/hedefler kullanır. Bootstrap analizi sonuç sonrası açıklayıcı; resmi önkayıtlı doğrulama olarak sunulmuyor.

### Güçlü kontroller, aynı sorular ve aynı metrik

| Veri | Yüksek ceza qscale | Eski ASYM | Eski Hamming | Eski float_std | Exact0 float_std | BM25 |
|---|---:|---:|---:|---:|---:|---:|
| LME | 64,03 | 57,92 | 68,68 | 59,86 | 68,19 | 67,36 |
| PerLTQA | 53,66 | 53,53 | 48,89 | 56,58 | 56,24 | 57,14 |
| LoCoMo | 37,26 | 34,27 | 31,49 | 38,91 | 38,85 | 41,75 |

B8 codec'i bu turda kurulmadı. Yeni yöntemin B8'i veya bütün küçük-kod/literatür yöntemlerini geçtiği söylenemez. BM25 k1=1,2,b=0,75, Unicode kelime-sayı tokenizerı, tek karakter dahil, kök/stopword yok. Sayısal referanslara da yeni exact gösterim verilerek çözümleyici avantajı gizlenmedi. Gerçek metinle yeniden sıralama ve başka arama mimarisi bu tura eklenmedi.

Hit@10 bütün kollar için SUMMARY.json'da. LoCoMo'da production57,22 → gamma1 57,87; PerLTQA80,00 →80,23. LME küçük panel100,00 →95,83. Bir metrikteki artış tüm metriklerde artış diye sunulmuyor.

## 5. Nadirlik tanısı: asıl kazanım nerede yoğunlaşıyor?

Aşağıdaki gruplar sorgu ile **etiketli kanıt** arasındaki unigram ortaklığına göre tanısal olarak oluşturuldu. DF<=2 eşik ve unigram tanımı açıkça sabitlendi; bu diğer sohbetin RealTalk gruplarının tekrarı değildir. Gold kullanan bu gruplama çalışma zamanında bilinen yönlendirme kuralı değil. Kayıt uzunluğu/soru tipi gibi olası karıştırıcılar giderilmiş nedensel analiz değildir.

| Veri | Grup | Soru | Eski qscale FR@3 | Yüksek ceza FR@3 | Fark (puan) |
|---|---|---:|---:|---:|---:|
| PerLTQA | no_shared_unigram | 274 | 0,29 | 0,58 | 0,29 |
| PerLTQA | other_shared | 4975 | 43,93 | 43,11 | -0,82 |
| PerLTQA | rare_df_le2 | 3016 | 73,39 | 75,88 | 2,48 |
| LoCoMo | no_shared_unigram | 7 | 0,00 | 0,00 | 0,00 |
| LoCoMo | other_shared | 1086 | 25,25 | 25,55 | 0,30 |
| LoCoMo | rare_df_le2 | 438 | 62,67 | 66,88 | 4,21 |

PerLTQA nadir-ortak-terim grubunda +2,49 puan elde ederken diğer ortak-terimli grupta yaklaşık -0,82 puan kaybediyor. LoCoMo nadir grupta +4,21 puan; diğer ortak-terim grubunda yaklaşık+0,30 puan. Bunlar aynı grubun iki sabit kol karşılaştırmaları; nadirlik tek neden ilan edilemez. Altgruplara göre yöntem seçip yeni bir oracle/karma sistem başarısı hesaplanmadı.

Korunan sözcüksel yönlerin geometrik koruma toplamı `tr(R^T K R)` bütün64 arşivde arttı. Yüksek cezada exact0'a oranının arşivler üzerindeki medyanı LME2,12, PerLTQA1,97, LoCoMo3,07. Bu "bilginin3katı" veya "başarının3katı" değildir; amaç fonksiyonunun belirli parçası. Elde edilen arama kazancının bundan çok daha küçük olması, doğru surrogate'i optimize etmekle doğru kanıt bulmanın farklı olduğunu gösteriyor.

## 6. Gerçek doğru/yanlış kayıt çiftinde kaybın ayrıştırılması

Her soruda bütün etiketli doğru kayıtlar ile production qscale'in en yüksek puan verdiği üç etiketsiz kayıt eşleştirildi. Toplam105.372 çift. Yanlış sıralamaya yakın örnekleri incelemek için tanısal seçim; çiftler bağımsız örnekler değil, bir soru/kanıt birden fazla çiftte yer alıyor.

Tam birimlenmiş q,d için saf iç-çarpım farkı:

Delta_full = Delta_kept + Delta_orthogonal_residual.

Kosinüs karşılaştırmasına dönüşte ayrıca projekte vektörleri yeniden birimlemenin katkısı var:

Delta_full - Delta_projected_cos = Delta_residual + (Delta_kept - Delta_projected_cos).

Her sorunun ilk çiftinde yüksek boyutlu kalıntılar **doğrudan** oluşturularak özdeşlik bağımsız biçimde kontrol edildi; yalnız farkı farktan çıkarmakla yetinilmedi. 9.820 doğrudan kontrolün maksimum mutlak artığı 4,65e-15. Diğer bütün çiftlerin saklanan ayrıştırma bileşenleri ayrı kontrol kodunda toplandı.

| Veri | Çift sayısı | Tam uzay doğru önde, SVD-kosinüs değil | Bu kayıplardan std ile geri gelen | Std doğru önde, qscale değil |
|---|---:|---:|---:|---:|
| LME | 162 | 25 | 13 | 13 |
| PerLTQA | 98184 | 2979 | 1088 | 6967 |
| LoCoMo | 7026 | 499 | 193 | 666 |

Örneğin PerLTQA'da2.979 çiftin SVD-kosinüs sırası tam uzaydaki doğru üstünlüğünü kaybediyor; bunların1.088'inde aynı96 sayı standartlaştırıldığında üstünlük geri geliyor. Buna karşılık standart float'ın doğruyu öne koyduğu6.967 çiftte qscale bunu korumuyor. Bu sayılar ayrı hata kaynaklarının varlığını gösterir; birbirine eklenip tüm soruların kayıp yüzdesi yapılmaz. qscale'e göre yanlış rakip seçimi bazı karşılaştırmalara sistematik seçim etkisi getirir; çift sayıları yöntemlerin genel başarısını sıralamak için değil, ilgili mekanizmayı örneklemek içindir. Genel sonuç için FR@3 tablosu kullanılır.

### Örnek: LoCoMo L00_q0012

Soru: Caroline'ın18.yaş günü ne kadar önceydi? Etiketli kayıtta, bir arkadaşının on yıl önce18.yaş gününde verdiği hediyeden söz ediliyor. Başka bir kayıtta farklı bir geçmiş olay anlatılıyor. Aynı iki kayıtta:

| Aşama | Etiketli doğru kaydın rakibe karşı puan farkı |
|---|---:|
| Geniş uzay kosinüs | +0,104756 |
| Yalnız korunan iç-çarpım | -0,043817 |
| SVD sonrası kosinüs | -0,087087 |
| Merkezli kosinüs | -0,090904 |
| Aynı96 koordinat, standartlaştırılmış kosinüs | +0,039433 |
| qscale | +0,315042 |
| Hamming'e eşdeğer işaret iç-çarpımı | -2 |

Son üç satırın puan ölçekleri farklı; büyüklükler doğrudan karşılaştırılmaz, yalnız hangi kayıt önde sorusu izlenir. Aynı örnekte izdüşüm kaybı, ölçek düzeltmesiyle kısmi toparlanma ve işaret-temelli sıralamanın tekrar kaybı görülüyor. Örnek sonuç sonrası açıklama amacıyla seçildi; genel-popülasyon kanıtı değil. Bu tek rakibe karşı öne geçiş, kaydın bütün arşivde mutlaka ilk3'e girmesi demek değildir. Etiketlerin içerik doğruluğu genel olarak bu turda yeniden denetlenmedi.

## 7. Teknik kontrol sonuçları

64 input hash doğrulaması. Eski kaynakla karşılaştırılabilen LME/PerLTQA doküman+sorgu toplam3.101.952 bitinde sıfır fark. LoCoMo için bu turda eski sayısal dizi/bit cache'i paket içinde yoktu; kaynak ve soru-bazlı metrik referansı kullanıldı. Tüm9.820 sorguda production Hamming/ASYM/qscale/float_std için235.680 skaler metrik kontrolünde sıfır fark.

İzotropik D=I kontrolünde bütün64 arşivde doküman/sorgu bitleri ve qscale puanları aynen eşleşti. İki ceza kolunun her arşivde etkin rankı96, sabit bit sütunu0. Ortonormalite/eigen residual/merkezli varyans kontrolleri geçti. Her benchmark'ın ilk arşivinde geniş V=Z^T A açıkça oluşturulup dual yolla doküman ve sorgu sonuçları karşılaştırıldı. Arşiv-bazlı hata sınırları archive.json dosyalarında.

440 küçük metrik durumu815 açık sınır seçimiyle doğrulandı;24 ayrı sentetik dual faktörleme deneyi geçti. Başka betikle414 özet-metrik ortalaması CSV'den yeniden toplandı; en büyük fark2,84e-14. 105.372 çiftte gold/yanlış kimlik üyeliği ve tekillik kontrol edildi. Ayrıca ilk LME, ilk PerLTQA ve ilk LoCoMo arşivi üç ayrı taze süreçte tekrar çalıştırıldı; quality/pairs/query_groups toplam9 dosya orijinal sonuçlarla bayt-bayt eşleşti. Bunlar aynı yazarın ek kontrolleridir; dış bağımsız denetçi onayı değildir.

## 8. Maliyet ve tekrar üretim sınırları

Kod boyutu toplam29905 kayıt için358.860 bayt; doküman kodu budgetı büyümedi. Mean ve sigma dizileri her kodlayıcıya ayrıca ait. Kullanılan dual kodlayıcı, seyrek Z ve A'yı tutmak zorunda; bunlar belge bitlerine dahil değil. Tam U,s,K fit sırasında gerekir; servis tasarımı bunları kullanmayacaksa silinebilir ama burada karşılaştırmalı resident-servis uygulaması kurulmadı.

Tek-geçişli zaman sayaçları arşiv JSON'larında bulunuyor. Çözümleyici, tanı ve çoklu kollar aynı süreçte çalıştığından bunlar baştan sona latency/RSS karşılaştırması veya "daha hızlı" iddiası değildir. Karşılaştırmalı peak RAM, güncelleme, soğuk-cache ve enerji ölçülmedi. Önceki projektör fikriyle uyum cebirsel/direct-num kontrol düzeyinde; hız kazançları toplanmadı.

Ölçülen dizi toplamları, tüm arşivlerin aynı anda yüklü olduğu iddiası değildir. Kayıt başına bayt küçültme başlığı yerine sources/arrays tablosu için bütün arşiv toplamları meta sonuçlarda açıkça tutuldu.

## 9. Karar ve sonraki dar hedef

Bu amaç, nadir sözcüksel yönlere daha fazla yer ayırabiliyor; boş yön seçmeden gerçek96-bit kod üretiyor. Ancak bunu yapmak tek başına güçlü arama sistemi üretmiyor. LoCoMo cezasız exact kontrole karşı olumlu; eski production referansına karşı belirsiz; PerLTQA küçük/belirsiz; LME24'te netceza etkisi yok. Veri kümesine göre kazanan seçme yok.

Bu turdan sonra yeni gamma taraması veya daha fazla bileşeni üst üste eklemek yerine; sabit adayın güçlü referanslara karşı, ayar seçimine dahil olmayan veri üzerinde sınanması ve query/gold ortaklığına bakmadan kullanılabilir bir koruma önceliğinin tanımlanması gerekir. Salt nadirliği hedeflemek, PerLTQA diğer grubunda kaybı artırabiliyor. Mevcut sonuç üretim değişikliği için yeterli değil.

## 10. Kaynak kaydı

Önceki matematik notları: LLMZIP_NADIRLIK_MATEMATIK_2026-09-16/MATEMATIK_INCELEME.md ve LLMZIP_CEZA_KONTROL_2026-09-16/KONTROL_VE_DENEY_EKI.md. Kaynak yedekler ve SHA256: sources/receipt.json ve önceki manifest. Arşiv/soru üyeliği PLAN_BEFORE_RUN.json; karşılaştırma kaydı sources/previous_quality_per_query.csv.

Yöntem/API için birincil belgeler (deney sayılarının kaynağı değildir):
- scipy.linalg.eigh: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html
- sklearn TruncatedSVD: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html

Deney ortamı Python3.13.5, NumPy2.3.5, SciPy1.17.0, scikit-learn1.8.0; bütün BLAS/OMP yolları1thread. Güncel web belgelerinin sürümü deney ortamıyla aynı olmak zorunda değil; kullanılan API ve gerçek sürümler ayrıca kaydedildi.

Uzak GitHub/Drive dosyası değiştirilmedi. Dondurulmuş görev betikleri veya Task4F1/BEAM çıktıları çalıştırılmadı/okunmadı. İlk session-mode araç çağrısı bu ortamda desteklenmedi; hiçbir deney sonucu üretmeden reddedildi. Sonraki işler sıralı ve sınırlı komut gruplarıyla tamamlandı; yarım kohort final özete katılmadı.
