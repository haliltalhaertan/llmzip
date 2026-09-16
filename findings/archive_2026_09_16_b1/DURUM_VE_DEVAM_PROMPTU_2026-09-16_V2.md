# LLMZIP — Durum ve devam promptu / 16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Bu metni yeni araştırma sohbetine başlangıç promptu olarak kullan. Projeyi baş araştırmacı/entegratör rolüyle devral. Kullanıcının hedefi düşük toplam maliyetle güçlü kanıt araması; bugünkü formülü savunmak değil, gerçekten daha iyi sistemi bulmaktır. Açıklamaları sade tut: ne yaptık, ne bulduk, ne eksik, sıradaki iş.

## Teslim güncellemesi — 16 Eylül 2026

**Drive: 12 özgün dosyanın tamamı byte-korumalı ve geri-okuma doğrulamalı saklandı. GitHub: iki ana deney raporu ve bu durum devri doğrudan kaydedildi; tam ZIP/JSON/kod aynası tamamlanamadı.** Büyük ZIP'ler Drive'da `.partNNN` parçalarıdır; diğer 10 özgün dosya `LLMZIP_SON_RAPORLAR_KOD_VE_DEVIR_2026-09-16.zip` içindeki `originals/` altında bulunur. Paketi açıp `reassemble_verify.py` ile parçaları birleştir. GitHub Actions aktarımı, yenilenmiş geçici kaynak URL'sinde de HTTP403 aldığı için durduruldu. GitHub prerelease oluşturulmadı; tam paketler için geçerli kaynak Drive arşividir. Tam kopya için Drive'ı kullan. Önce `ARCHIVE_RECEIPT.json` dosyasındaki güncel envanteri oku. Arşiv kopyası doğrulaması yeni bilimsel denetim değildir.

## 1. Önce kaynakları ve kayıt durumunu doğrula

Repo: https://github.com/haliltalhaertan/llmzip
Bu teslimin dalı: `archive/latest-findings-b1-2026-09-16`
Namespace: `findings/archive_2026_09_16_b1/`
GitHub arşivi: https://github.com/haliltalhaertan/llmzip/tree/archive/latest-findings-b1-2026-09-16/findings/archive_2026_09_16_b1
Drive: https://drive.google.com/drive/folders/1q2JVwmA_LKBmLaZtMqJTXsLWBWhT4O_m
Önceki 28 dosyanın Drive arşivi: https://drive.google.com/drive/folders/1eTS7HjgmRF5Cg4Lumlo0QYfucHG2BCbE

Bu bağlantılarla birlikte `ARCHIVE_RECEIPT.json`/`DELIVERY_RECEIPT.json` teslim kaydını kontrol et; bir bağlantının yazılmış olması yükleme ve doğrulama kanıtı değildir. `ORIGINAL_MANIFEST.json` dosya boyutlarını, SHA-256'ları ve büyük paketlerin taşıma parçalarını tanımlar. Dosyaları indirdikten sonra hash doğrula; bir parçayı tek başına ZIP gibi açma. `reassemble_verify.py` parçaları birleştirip özgün dosya hash'ini kontrol eder.

Arşivlemenin başında `main` = `59b891efda7b6c06f44da7fa0ae4fe3c13f79a2e`; eski envanter dalı = `c0df0f9d69fcb2494fb15ace6045160581a19e7a`. Bağlayıcı, repo varsayılan dalını `claude/itq-frontier-audit-wfrz6a` olarak bildirdi. Varsayılan dalı main sanma; her okumada/yazmada ref'i açıkça belirt. Canlı durum değişmiş olabilir; yeniden doğrula. Bu prompt bütün diğer dallardaki eşzamanlı çalışmaları birleştiren bir master durum iddiası değildir.

Okuma önceliği:
1. `LLMZIP_IKI_FIKIR_RAPORU_2026-09-16.md`, aynı adlı ÖZET JSON ve `FINAL_SELF_AUDIT.json`.
2. `LLMZIP_IKI_FIKIR_DENEY_PAKETI_2026-09-16.zip`: gerçek kod, soru sonuçları, kaynak ölçümleri, plan, ortam ve denetim çıktıları.
3. `LLMZIP_GERCEK_12_24_48_BAYT_RAPORU_2026-09-16.md`, ÖZET JSON ve `LLMZIP_GERCEK_12_24_48_BAYT_2026-09-16.zip`. Son paketin yeniden çalıştırma betiği bu önceki pakete ihtiyaç duyar.
4. `LLMZIP_AUDIT3_INCELEME_2026-09-16/INCELEME.md` ve karşı inceleme ZIP'i: geçersiz imkânsızlık iddialarının matematiksel kontrolü.
5. Yol haritası ve öneri belgeleri tarihsel aday listesidir; önerilmiş, denenmiş ve başarısız olmuş fikirleri ayır. Eski 28 dosya önceki araştırma ve denetim zinciridir; sonraki düzeltmeleri yok sayarak eski iddiaları canlandırma.

## 2. Şu anki en sağlam devam adayı

`exact192 + paketli SIGN192 (24 bayt/kayıt) + qscale + B1 kompakt kodlayıcı`.

Bu üretime alınmış veya dış bağımsız denetimden geçmiş bir kazanan değildir. Yeni kalite üstünlüğü değil, mevcut 24-bayt gösterimin aynı ölçülen arama kalitesini daha küçük model durumu ve daha düşük sorgu CPU maliyetiyle üretme adayıdır. B1 hâlâ arşive özeldir; ortak/paylaşılan kodlayıcı değildir.

Kodlayıcı: normalize word TF-IDF (1–2 gram, English stopwords, sublinear TF), char_wb TF-IDF (3–5 gram), word'den normalize LSA32. LSA seed=5101. Exact Gram ailesi eski randomized SVD96 (seed5204) ile karıştırılmamalı. Fit sadece dokümanları kullanır; sorgu/gold fit girdisi değildir.

Ana ölçüt deterministik Fractional Evidence Recall@3 (FR@3): etiketli kanıtların ilk üçte bulunan payı. Bu cevap doğruluğu veya başarılı soru yüzdesi değildir. Hit@10 ayrı ikincil ölçüt. Eşitlik sırası SHA256(`top10-r1|archive|row`); beklenen-tie ve deterministik sonuçları karıştırma.

## 3. Gerçek boyut merdiveni

510 arşiv, 10.266 soru, 249.776 kayıt: LME 470/470/231.606; PerLTQA en_v2 30/8.265/12.288; LoCoMo 10/1.531/5.882. Aynı kohort bütün kollarda korundu. Bunlar daha önce görülmüş veri, gizli test değil. RealTalk bu turda eksik.

FR@3 (%), exact ailesi ve qscale:

| Veri | 12 B | 24 B | 48 B | Eşlenmiş BM25 kalite kontrolü |
|---|---:|---:|---:|---:|
| LongMemEval | 52,47 | 61,48 | 61,75 | 57,14 |
| PerLTQA en_v2 | 52,98 | 54,82 | 51,87 | 60,14 |
| LoCoMo | 35,11 | 41,21 | 44,15 | 42,87 |

24 bayt geliştirme referansıdır, evrensel optimum değildir. LME'de 48–24 farkı +0,27 puan, keşifsel aralık [-1,94;+2,45]. PerLTQA'da 48 bayt geriler; LoCoMo'da 48'in ek kazancı vardır. 48 baytı destekleyecek rankı olmayan arşivler dışlanmadı, sabit koordinatla dolduruldu ve tam 48 B ödendi. Kodlar birbirinin öneki değildir: her genişlikte normalleştirme/merkezleme/sigma yeniden hesaplanır.

## 4. Son iki fikir deneyinin sonucu

A — Aynı 24 baytta 96 koordinat ×2 bit: dokümandan standartlaştırma, tüm arşivlerde aynı standart-normal Lloyd–Max dört seviyesi, ana skor kosinüs. Veri/gold ile eşik taraması yok. FR@3 LME 54,41; PerLTQA 55,49; LoCoMo 37,46. Mevcut192×1'e fark -7,07/+0,67/-3,75 puan. PerLTQA küçük farkının aralığı [-0,11;+1,46]. Genel varsayılan olarak benimseme; bütün 2-bit yöntemlerin imkânsızlığı çıkarılamaz.

B1 — Aynı kodlayıcının cebirsel küçültülmesi: W kelime-TFIDF doküman matrisi, R eski LSA sağ projektörü. `R=WᵀB`, `B=(WWᵀ)^+WR`; `Lq=normalize((WqWᵀ)B)`. Bunun için R'nin W satır uzayında olması gerekir; her arşivde artık kontrol edildi. Büyük R kaldırılır, Wᵀ/Hᵀ/L/B tutulur. `ZqZᵀ=WqWᵀ+HqHᵀ+LqLᵀ`; kelime çapraz hesabı yeniden kullanılır. Son A192, mean/sigma ve 24-B kodlar korunur.

B1'de 10.266 sorgunun tüm ilk10 listeleri aynı: FR@3 61,48/54,82/41,21; Hit@10 89,15/80,71/62,12. En büyük projektör bağıl artığı1,320e-13; sorgu koordinatı farkı6,645e-14. Bu sonlu veride doğrulama, tüm olası sorgularda kayan-nokta bit özdeşliği teoremi değildir.

B2 — Hashing + IDF + paylaşılan rastgele circulant/FFT prototipi: ana seed FR@3 29,17/26,90/18,59. Üç sabit seed raporlandı; kazanan seçilmedi. Küçük ama kalite kaybı büyük; mevcut sistemin yerine koyma. Bu, CBE'nin eğitilmiş tam uygulaması veya bütün ortak/nöral kodlayıcıların testi değildir.

## 5. Maliyet: yalnız aynı son deneyin eş-koşullu satırlarını karşılaştır

11 arşiv /65 farklı sorgu; üç temiz servis süreci ve sorgu başına7 sıcak tekrar. 132 servis,5.460 uçtan uca çağrı,44 taze kurulum. Tek BLAS/OpenMP thread, CPU0, AMD EPYC9V74/AVX-512, Linux,4GiB sınırı. Tek süreçte tek arşiv/tek yöntem. Kalite CPU worker'ları profil sırasında çalışmadı; bunlar LLM alt ajanı değildi.

| Veri | Base192 CPU ms | B1 CPU ms | Base RSS MB | B1 RSS MB |
|---|---:|---:|---:|---:|
| LME | 2,60 | 1,34 | 204,14 | 183,52 |
| PerLTQA | 1,79 | 1,25 | 171,36 | 167,74 |
| LoCoMo | 1,70 | 1,20 | 172,06 | 168,62 |

Kapsam ham sorgudan metin/kimlik erişimli ilk10'a kadardır. Ağ, soğuk disk, LLM cevap üretimi, istek kuyruğu ve enerji dahil değildir. Bu panelin CPU/RSS'sini tüm datasetin latency/p95 SLA'sı sayma. Eski merdiven raporunun farklı oturum süreleriyle çarpan hesaplama.

Model serileştirme toplamı (RAM değil): LME10.130,21→5.433,87MB (%46,36 azalma); PerLTQA157,21→106,66MB; LoCoMo56,05→40,57MB. Kaynak metin ve yardımcı yapılar dahil. Aynı anda bütün arşivler RAM'de tutulmadı. Sorgu maliyeti düşerken kurulum tepe RAM'i artabilir: LME panel maksimumu240,00→262,71MB. B1 ek faktörleme gerektirir.

## 6. Kanıt durumu ve kesinlikle söylenmeyecekler

Son rapor aynı yazara ait ayrı doğrulama kodu kullanır: 82.128 liste,492.768 metrik yeniden hesaplanmış; fark0; 2.550 payload kontrolü. Dış bağımsız denetim DEĞİL. Bu arşivleme oturumundaki SHA kontrolü de bilimsel yeniden çalıştırma DEĞİL.

“En iyi sistem”, “bütün RAM24bayt/kayıt”, “her veride float/BM25'yi geçtik”, “48bayt her yerde yeter”, “96bit matematiksel olarak geliştirilemez”, “model küçültmek yeni arama kalitesi kazancı” deme. Ortalama kaldıraç k/N, her yön için üst sınır veya arama başarısı tavanı değildir. Oracle üst sınırı gerçek çalışan seçici değildir. Ortak kodlayıcının başarısız tek prototipini bütün ailelere genelleme.

## 7. Sıradaki önerilen işler (henüz yapılmış değil)

Önce B1'i farklı uygulayıcıya kaynak, plan ve hash'lerle bağımsız denetlet: denklem koşulları, bütün sorguların yeni yoldan kodlanması, paketli liste eşitliği, kalıcı/kurulum/sıcak RAM muhasebesi. Fark çıkarsa dur, kuralı gevşetme.

Ardından aynı pipeline/panelde güçlü BM25 ve float referanslarının toplam RSS/CPU/kurulum maliyetini ölç. Onların son turdaki yalnız kalite referansları tam sistem maliyeti karşılaştırması değildir. B1'i 48bayt LoCoMo'ya henüz uygulanmış sayma; ayrı test gerekir.

Ayrı veride ve RealTalk kaynakları eksiksiz geri alındığında sabit yöntem genellemesini değerlendir. Rastgele yeni katsayı taraması ve sonuç-sonrası dataset başına kazanan seçme yerine, önce sabit hipotez/plan/kohort/metrik yaz. Model2Vec/Potion, eğitilmiş ortak kodlayıcı, gerçek RaBitQ/PQ/OPQ/TurboQuant kontrolü bu son deneyde çalıştırılmadı.

## 8. Çalışma sınırı

`main`e yazma/merge yapma; varsayılan dalı değiştirme. Mevcut rapor/ham dosyaları sessizce düzeltme, yeni sürüm ve değişiklik kaydı ekle. Task4F1/BEAM ve dondurulmuş görevleri açık yeni kullanıcı yetkisi olmadan çalıştırma/okuma. Arşiv kopyalama için eklenen workflow araştırma deneyi değildir; yeni bilimsel çalışma izni yerine geçmez. Hassas kaynak veya tokenları prompta/loga taşıma.

Alt ajan varsa gerçek araçla başlat; yoksa açıkça söyle. Aynı modelin farklı rol metinlerini bağımsız denetçi sayma. Veri aktarımında doğru dosya SHA'sını ve depo ref'ini doğrula. İlk yanıtında doğruladığın kaynakları, mevcut adayı ve en dar sonraki işi sade Türkçeyle bildir.
