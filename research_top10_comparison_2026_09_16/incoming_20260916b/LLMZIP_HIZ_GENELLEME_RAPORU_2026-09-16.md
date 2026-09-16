# LLMZIP — Yeni puanlama: hız ve veri aktarımı doğrulaması

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. Karar

Yeni ölçek-dengeli, sayısal-sorgulu yöntem LoCoMo aktarım testinde SIGN96/Hamming’den daha yüksek kanıt bulma başarısı verdi. İlk doğrudan C uygulaması, adil biçimde optimize edilmiş float32 referansından daha yavaştı. Aynı puanı değiştirmeyen AVX-512 uygulaması hazır sayısal sorgunun hazırlık+puanlama aşamasında float32’den 1,71–1,86 kat hızlı çıktı. Bununla birlikte eski Hamming çekirdeğinden 1,60–2,02 kat yavaştır. Metinden ilk on sonuca kadar toplam gecikme büyük ölçüde ortak TF-IDF/SVD kodlayıcısınca belirlenir; uçtan uca iki kat hızlanma gösterilmedi.

Bu çalışma bütün kullanım koşullarında üstünlük, gizli test onayı veya üretim kararı değildir. Standartlaştırılmış float, LoCoMo’da hâlâ daha yüksek kalite verir; ölçek dengelemenin eski asym üzerine ek kalite kazancı burada küçük ve belirsizdir.

## 2. Sabit tutulan yöntem ve ne değişti?

Önceki tanısal aday aynen korundu:

```text
C = normalize(SVD96(Z)) - mean(normalize(SVD96(Z)))
sigma[j] = max(std(C[:,j], ddof=0), 1e-12)
b[d,j] = +1 if C[d,j] >= 0 else -1
score(d,q) = sum_j b[d,j] * qC[j] / sigma[j]
```

İlk LSA32 tohumu 5101, son randomized SVD96 tohumu 5204. Sadece arşiv metniyle fit; sorgular fit girdisi değil. Eşik, bit sayısı, kod koordinatları ve sorgu ağırlıkları sonuçlara göre değiştirilmedi. Her arşivde sigma yalnız dokümanlardan hesaplandı. Yeni Gram/projektör dönüşümü bu deneye eklenmedi.

Doküman kodlarının bitleri korunarak bellek düzeni 12 baytlık satırlardan 12 bayt-düzlemine transpoze edildi. Toplam doküman kodu boyutu aynı kaldı; gerçek kullanımda yalnız bir düzen tutulur. Deneyde karşılaştırma için iki düzen ve bütün float kolları birlikte bellekteydi; bunun RSS’si tek yöntemin RAM’i diye sunulmadı.

Her sorgu için 24 adet 16 girişli float64 tablo, koordinat ağırlıklarından hesaplanıyor. AVX-512 permütasyonları aynı tablolardan birden çok kaydı paralel puanlıyor. Sorgu ağırlıkları birkaç bite yuvarlanmadı; bu bir başka kuantizasyon yöntemi değil. Scalar ve SIMD skorları bu verilerde bayt düzeyinde aynı. LUT hazırlığı ana hız karşılaştırmasına dahil.

## 3. Kalite — eski verilerde tekrar, ayrı veride aktarım

Hit@10 = ilk on kayıt arasında en az bir etiketli kanıt bulunması. Eşit puanlı sınırda uniform seçim altındaki tam beklenen başarı hesaplandı. Bu LLM cevap doğruluğu değildir. Veri kümeleri birleştirilmedi.

| Veri kümesi | Arşiv / soru | Eski Hamming | Eski asym | Yeni ağırlıklı | Standart float32 |
|---|---:|---:|---:|---:|---:|
| LME | 470 / 470 | %86,08 | %85,74 | %88,51 | %88,30 |
| PerLTQA | 30 / 8265 | %75,76 | %80,19 | %80,00 | %83,96 |
| RealTalk | 10 / 705 | %46,68 | %43,55 | %49,65 | %48,51 |
| LoCoMo | 10 / 1531 | %52,64 | %56,83 | %57,22 | %61,01 |

LME, PerLTQA en_v2 ve RealTalk önceki keşif verileridir; bu üçündeki kazanç yeni genelleme kanıtı değildir. LoCoMo yeni puanlayıcının geliştirildiği bu üç kümeden ayrıdır; ancak LoCoMo proje geçmişinde zaten anılmış ve önceki yöntemlerle test edilmişti. Dolayısıyla burada kamuya açık veri üzerinde yeni-yöntem aktarımı yapıldı, bütünüyle kör/gizli bir test yapılmadı. Model veya hiperparametre gold ile eğitilmedi.

### LoCoMo ayrıntısı

10 arşiv, 5.882 konuşma kaydı, 1.986 toplam sorudan 1.531 değerlendirilebilir soru. 446 adversarial kategori-5, 4 kanıtsız ve 5 geçersiz/çözülemeyen kanıt referanslı soru dışlandı. Dışlama ve kohort listesi skorlar hesaplanmadan yazıldı. Dört açık birleşik kanıt kimliği, örneğin noktalı virgülle ayrılmış D:satır etiketleri, açıkça ayrıştırıldı ve kayda geçirildi; eksik kimlikler tahmin edilmedi.

Her kayıt `[session timestamp] speaker: text` biçiminde bir konuşma turu. Görseller, BLIP açıklamaları, üretilmiş gözlemler, özetler ve QA cevapları indeks metnine eklenmedi. Bu text-only retrieval uyarlaması, LoCoMo’nun özgün uçtan uca cevap-F1 değerlendirmesiyle aynı değildir. Gold etiketlerinin içerik doğruluğu ayrıca elle denetlenmedi.

| LoCoMo karşılaştırması | Hit@10 farkı, yüzde puan | Keşifsel arşiv-bootstrap %95 aralığı | İyileşen / gerileyen / aynı soru |
|---|---:|---:|---:|
| Yeni − Hamming | 4,58 | [3,00; 6,37] | 156 / 78 / 1297 |
| Yeni − eski asym | 0,39 | [-1,66; 2,25] | 70 / 64 / 1397 |
| Yeni − standart float | -3,79 | [-4,41; -3,13] | 56 / 114 / 1361 |

20.000 eşleştirilmiş arşiv bootstrap tekrarı; yalnız 10 küme var. Aralıklar arşiv bağımsızlığı/değiştirilebilirliği varsayımına bağlıdır, bağımsız nüfus teyidi değildir. Eski asym üzerine 0,39 puan farkın aralığı sıfırı kapsıyor. Bu veride Hamming’e göre kazanımın büyük bölümü sorguyu iki işarete indirgememekten geliyor; ölçek dengelemenin ek üstünlüğü güçlü biçimde doğrulanmadı.

Fractional recall@100 sonuçları da saklandı. LoCoMo’da Hamming %75,80; yeni aday %78,75; standart float32 %84,14. Daha çok kanıt toplama açısından da float açığı kapanmadı.

## 4. Hız — eşit koşullarda yerel ölçüm

AMD EPYC 9V74, AVX-512 destekli Linux x86-64; 5 görünür vCPU, cgroup kotası 4 CPU, 4 GiB RAM sınırı. Her puanlama işi tek iş parçacıklı. Sanallaştırılmış/paylaşımlı ortam; deney işlerimiz zamanlamalar sırasında eşzamanlı yürütülmedi. Sekiz sıcak tur; yöntem sırası döndürüldü; arşiv başına medyan gerçek sorgu sayısıyla ağırlıklandırıldı. Rakamlar saniyenin milyonda biri, yani mikrosaniyedir.

Float karşılaştırması Python’da gereksiz norm hesaplaması yapan zayıf referans değildir: aynı NumPy ILP64 OpenBLAS SGEMV, C’den çağrıldı; sorgu koordinat ölçekleme aynı C çağrısına alındı. Pozitif sorgu normu sıralamayı etkilemediğinden kaldırıldı. Float32 ile float64’ün altı kalite metriği 10.971 soruda eşleşti.

### Sayısal qC hazır: sorgu hazırlığı + bütün kayıtların puanlanması

Bu ana tablo yeni LUT’nin oluşturulmasını, eski yöntemde sorgunun bitlere çevrilmesini ve float tarafında sorgunun ölçeklenmesini içerir. Henüz metin kodlama ve ilk-10 seçimi dahil değildir.

| Veri | Eski Hamming µs | Yeni ilk scalar C µs | Yeni optimize SIMD µs | Optimize float32 µs | Float / yeni hız oranı |
|---|---:|---:|---:|---:|---:|
| LME | 0,89 | 3,75 | 1,76 | 3,22 | 1,83× |
| PerLTQA | 1,01 | 3,27 | 1,61 | 2,75 | 1,71× |
| RealTalk | 1,27 | 6,15 | 2,57 | 4,78 | 1,86× |
| LoCoMo | 1,08 | 4,38 | 1,98 | 3,57 | 1,80× |

İlk scalar kodda hız avantajı gerçekten kaybedildi. SIMD iyileştirmesi bu sonucu gizlemek için bir kalite ayarı yapmadı; aynı fonksiyonun uygulamasını hızlandırdı. Orijinal scalar ölçümler ve kod sürümü dosyalarda korundu. Hız kazancı bu işlemcide ölçülmüştür; AVX-512 olmayan işlemcilerde scalar fallback vardır fakat aynı hız sonucu beklenemez.

### İlk on kaydın seçimi de dahil

Aynı deterministik kısmi seçim algoritması tüm kollarda kullanıldı; eşitlikte doküman sıra kimliği önceliklidir. Kalite ölçümünde kullanılan uniform-tie beklentisiyle bu zamanlama seçiminin farkı korunmuştur. Seçim fonksiyonu tüm sorularda tam sıralamayla kontrol edildi.

| Veri | Eski Hamming µs | Yeni SIMD µs | Float32 µs |
|---|---:|---:|---:|
| LME | 15,56 | 16,13 | 17,75 |
| PerLTQA | 15,10 | 15,38 | 16,51 |
| RealTalk | 20,41 | 20,38 | 23,53 |
| LoCoMo | 17,28 | 17,71 | 19,43 |

## 5. Metinden ilk on kayda kadar toplam gecikme

19 arşiv / 51 ayrı sorgu; her yöntem ve sorgu için 9 döndürülmüş tekrar, toplam 1.377 zamanlanan çağrı. 6 LME arşivi önceki 12 boyut-kapsama panelinden; 3 PerLTQA arşivi önceki 6’lı panelden; LoCoMo’nun 10 arşivinin tamamı. PerLTQA’da 5, LoCoMo’da 3 eşit aralıklı soru sırası; sonuca göre seçim yapılmadı. Her arşiv yeni süreçte kuruldu.

İndeks bir kez kurulduktan sonra metin → TF-IDF → LSA32 → SVD96 → normalleştirme/merkezleme → puan hazırlığı → puanlama → ilk-10 ölçüldü. Disk, ağ, LLM cevabı, her soruda yeniden indeks kurma dahil değil. RealTalk ham metin gecikmesi tekrar ölçülmedi.

| Panel | Arşiv / farklı sorgu | Eski Hamming ms | Yeni SIMD ms | Float32 ms |
|---|---:|---:|---:|---:|
| LME | 6 / 6 | 15,295 | 15,261 | 15,381 |
| LoCoMo | 10 / 30 | 2,482 | 2,527 | 2,542 |
| PerLTQA | 3 / 15 | 2,573 | 2,566 | 2,607 |

Bunlar sorgu başına medyanların ortalaması. Yaklaşık aynı toplam süreler görülüyor; küçük farkları gürültü, cache/scheduler ve paylaşımlı sistem etkilerinden ayrılmış genel hız kazancı saymıyoruz. Biçimsel eşdeğerlik/non-inferiority testi yapılmadı. Sıcak p95 ve CPU ham ölçümleri end_to_end.json dosyasında; bunlar üretim yükünde kuyruk gecikmesi garantisi değildir.

## 6. Bellek ve ek kurulum maliyeti

520 arşiv / 258.720 dokümanın toplam kod boyutu 3.104.640 bayt. Toplam sigma dizileri 399.360 bayt. Kod+ölçek toplamı 3.504.000 bayt (3,504 MB); float32 doküman+aynı ölçek dizileri 99.747.840 bayt (99,748 MB). Bu iki dizi sınıfı bakımından oran yaklaşık 28,47 kattır.

Bu, toplam servis RSS’si değil. TF-IDF/SVD kodlayıcısı, metinler, kimlikler, arşiv ortalamaları, Python/runtime, geçici tamponlar hariçtir. Yeni LUT eşzamanlı sorgu başına 3.072 bayt; aday skor tamponu arşivdeki kayıt sayısının 8 katı bayt, float32 skor tamponu 4 katı. İlk-10 geçici dizileri ayrıca vardır. Tekrar kullanılan eski byte düzeni yeni düzene aktarılırken geçici olarak iki kopya oluşabilir; kalıcı depoda iki kod düzeni birlikte gerekmiyor.

Eşik öğrenme veya model eğitimi yok. Sigma hesabı ve byte transpozisyonunun ek kurulum süreleri arşiv bazında optimized_speed.json içinde ölçüldü; ortak pahalı arşiv kodlayıcısının maliyetini azaltan bir değişiklik yapılmadı. Yeni yöntem için karşılaştırmalı toplam süreç RSS deneyi bu oturumda yapılmadı.

## 7. Son doğrulama ve sınırlar

- 280 küçük tie senaryosunda metrik açık kombinasyon sayımıyla eşleşti.
- 10971 sorunun scalar/SIMD skorları sayısal olarak, ayrıca 10971 soruda float64 skor dizileri bayt olarak aynı.
- 258720 dokümanın transpoze edilmiş kodu eski bit dizisiyle tam aynı; ek doküman biti yok.
- 9.440 eski sorgudaki Hamming, weighted, float ve eski asym referansları yeniden üretildi. LoCoMo’da 1.531 ek sorgu aynı donmuş yöntemle işlendi.
- 10.971 sorguda float32/full64 altı hit/recall metriği eşit. Native ağırlıklı puanlama, doğrudan ±1 matris hesabıyla aynı metrikleri verdi.
- Uygulayıcı bu raporun yazarıdır; dış bağımsız denetçi onayı yoktur. Kamuya açık yeni-yöntem aktarımıdır, önkayıtlı veya gizli-test teyidi değildir.
- PerLTQA en_v1/zh ve başka yeni veri kümeleri bu oturumda test edilmedi. Başka sohbetlerden aktarılan değerler yeni ölçüm diye kullanılmadı.
- GitHub/Drive’a yazılmadı; main değişmedi; Task4F1/BEAM ve dondurulmuş görev betikleri çalıştırılmadı. LoCoMo’nun ham metni ve sabit etiketleri ayrı keşifsel uyarlamada kullanıldı.

## 8. Kaynak ve yeniden üretim

Eski büyük girdiler, kullanıcının hash-doğrulanan yedeklerinden seçilerek geri alındı. Yerel ağdan yeni veri indirme denemesi başarısız oldu; LoCoMo ham dosyası mevcut yedekten alındı ve resmî GitHub blob SHA ile karşılaştırıldı. Eşleşme tam:

```text
Official file: https://github.com/snap-research/locomo/blob/main/data/locomo10.json
Official schema: https://github.com/snap-research/locomo
Git blob SHA-1: d95b872480b413d935821fdc3c84f8a8f5f29e73
SHA-256: 79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4
Backup: 07_drive_frozen.tar.gz.tar::drive/locomo10.json
```

Yeni puanlama, ölçüm kapsamı ve veri seçim kuralı PLAN_BEFORE_RUN.json içine skorlar görülmeden yazıldı; bu yerel kayıt resmî önkayıt değildir. CPU optimizasyonu sonuçlardan sonra, kalite fonksiyonu değiştirilmeden yapıldı. Kaynak sürümleri ve ham ölçümler korunmuştur.

Dosyalar: results/FINAL_SUMMARY.json, quality_per_query.csv, optimized_speed_per_archive.json, end_to_end.json, locomo_adapter_before_scores.json, locomo_paired_comparisons.json, final_checks.json, final_environment.json. Betikler ve yeniden çalıştırma adımları paketin README.md dosyasında.
