# Bağımsız tasarım incelemesi — statik depolama sözleşmesi

Tarih: 2026-09-12. İnceleyen oturum: `01a09637-affc-7f93-a351-cfcc486c9ab2`.

**Kapsamlı hüküm: DESIGN-ONLY / DÜZELTME GEREKLİ. Bu rapor maliyet ölçümü, kaynak kullanılabilirliği kanıtı, HR onayı, mühür veya çalıştırma izni değildir.** Taslağın ana muhasebe yaklaşımı önceki bağımsız eleştiriyi karşılıyor; aşağıdaki üç dar düzeltme yapılmadan korumaların eksiksiz aktarıldığı söylenmemelidir.

İncelenen tam dosya: `drafts/v52/static_storage_contract_2026_09_12/MEASUREMENT_CONTRACT_TR.md`.

**İncelenen ham dosya baytlarının SHA256 değeri:**

`A5A69569E4F1F2C9DB1648693DC99509221EE1B8A26AE2DFDD11B79A73290951`

Bu kimlik, metnin okunması ve aynı bayt görüntüsünden SHA256/numaralı metin üretilmesiyle bağlandı. Aşağıdaki satırlar yalnız bu sürüme aittir; sonraki değişikliklere hüküm taşınmaz.

Karşılaştırılan bütçe kaynağı: doğrudan `git show 89d3169adb65a9a2ab7f289997d7c49eb8ccf25c:docs/v52/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`. Kaynağın chat üzerinden aktarılmış, HR imzalı olmayan statüsü korunur. Atanmış worktree `work/llmzip_storage_contract_20260912`; beyan edilen dal `codex/v52-static-storage-contract-2026-09-12`, taban `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`. Dal/taban Git durumu bu dar incelemede ayrıca doğrulanmadı.

Okuma sınırı taslak ve sabit bütçe nesnesidir. Gerçek model/manifest, korpus, sorgu, gold veya retrieval sonucu okunmadı; model/prob çalıştırılmadı. Yalnız belge kimliği için hash hesaplandı. Alt ajan başlatılmadı; ana belge değiştirilmedi. Parent tarafından hazırlanan ham kopya, sidecar, `SOURCE_BINDINGS.json` ve paket hash'i incelenmedi; bu rapor bunları doğrulamaz. Taslaktaki tarihsel uygulama ve maliyet referansları da bağımsız olarak doğrulanmış bulgu değildir.

## Beş sorunun tasarım kontrolü

| Soru | Metindeki karşılık | İnceleme sonucu |
|---|---|---|
| 1. Neyi ölçüyoruz? | Satır 9–19: kod, tüm marjinal kalıcı durum ve etkin toplam ayrılıyor; metin depolaması dışarıda fakat gerekli kimlik/offset içeride. | Temel sınır doğru. `a_v` açıkça 12 B kayıt yüküne dahil (39, 57). Sonlu fark ve zorunlu abort için R1/R2 gerekli. |
| 2. Eklemede ne sabit? | Satır 23–31: frozen model/OOV politikası, güncelleme dışlaması, ayrı N ve N+q görüntüleri, yeni bağımsız arşiv ayrımı. | Statik sonuç dinamik maliyet veya kalite kanıtına çevrilmiyor. Yeni kelime otomatik refit gerekçesi yapılmıyor. Paylaşım üyeliği ifadesi aşağıdaki küçük açıklamayla tutarlılaştırılmalı. |
| 3. Hangi kalem ve payda? | Satır 37–49, 55–65: gerçek kopya, pozitif gerçek D_k, arşiv satırları, iki farklı ağırlıklandırma, mantıksal dosya uzunluğu. | Heterojen arşivler ve fiziksel kopya hesabı doğru ele alınıyor; aynı hash gerçek paylaşım sayılmıyor. Alt sınırın geçerlilik koşulları R3'te. |
| 4. Hangi sonuç kararı değiştirir? | Satır 73–88: yalnız marjinal ≤12 tavanı; ortak P_i değişmezliği; kalite/fayda seçiminin belirlenmemesi. | Toplam bütçe veya yüzde eşiği icat edilmiyor. Sıra değişmezliği maddilik testi yapılmıyor. Aynı popülasyon ve ağırlık koşulu korunuyor. |
| 5. Sonuç çıkmazsa nerede durulur? | Satır 92–100: tam doğrulama şartlı olağan kapanış; eksik kaynakta PARTIAL / UNKNOWN; otomatik kapsam genişlemesi yok. | No-signal ile kaynak başarısızlığı doğru ayrılıyor. UNKNOWN sıfır veya etkisizlik sayılmıyor. Alt sınır raporlaması R3 ile daraltılmalı. |

## Gerekli düzeltmeler

### R1 — Zorunlu abort, yalnız uygunluk iddiasından vazgeçmeye indirgenmemeli

Konum: satır 77 ve sonraki plan sınırı 100–102. Bütçe kaynağının “Mandatory pre-seal assertion” bölümü, `measured_persistent_bytes_per_vector <= 12` ön kontrolünü ve gerçek `code_size`/serileştirme çıktısı deklarasyonla uyuşmadığında abort'u zorunlu tutuyor. Taslak “uygunluk iddiası kurulmaz; gerçek değer kaydedilir” diyor; bu, fail-closed çalışma davranışını açıkça taşımıyor. Mevcut taslak çalıştırma yetkisi vermediği için gerçekleşmiş bir koruma ihlali saptanmıyor, fakat gelecekteki plana aktarımda sessiz gevşeme riski var.

Önerilen ek metin:

> Sabit bütçe kararındaki ön kontrol ve abort yükümlülüğü aynen sürer: eşleşmiş karşılaştırmanın runner'ı `measured_persistent_bytes_per_vector <= 12` koşulunu ilgili hesaplamalara geçmeden doğrular; tavan aşımı veya gerçek `code_size`/serileştirme çıktısının deklarasyonla uyuşmaması halinde durur. Bulguyu kaydetmek devam izni oluşturmaz. Bu belge kontrolü çalıştırmaz veya çalıştırma yetkisi vermez; diğer mevcut korumaları ve açık yükümlülükleri kaldırmaz.

### R2 — Toplu fark ile bayt/vektör ve bütçe hükmü açıkça ayrılmalı

Konum: satır 14, 29, 39 ve 77. `B(N+q)-B(N)` toplam bayttır; q ile kaydedilmesi tek başına bunun bayt/vektör olduğunu söylemez. Satır 77'deki “farkın tavanı aşması” toplu farkı doğrudan 12 ile kıyaslamaya açık bırakıyor. Ayrıca blok/başlık basamakları varken bir parti ortalaması, tek başına tüm kayıtların bütçe uygunluğunu kanıtlamaz. Taslak lineerlik sorununu görüyor fakat karar bağlantısını tamamlamıyor.

Önerilen ek metin:

> q pozitif tamsayıdır. `delta_bytes = B(N+q)-B(N)` toplam ek bayt, `delta_bytes_per_added_vector = delta_bytes/q` o partinin vektör başına ortalama farkıdır; ikisi ayrı kaydedilir. Toplam fark doğrudan 12 B/vektör ile karşılaştırılmaz. Kayıt başına zorunlu `b_v+a_v`, N'ye bağlı serileştirme farkı ve paylaşılan durum ayrı uzlaştırılır; aynı bayt iki kez sayılmaz. Lineer olmayan farkların bütçe koşuluna nasıl bağlandığı önceden açıklanıp doğrulanmadan bir parti ortalamasından genel uygunluk hükmü çıkarılmaz. Paylaşılan model durumu bu yolla marjinal tavana taşınmaz; zorunlu vektör başına durum da paylaşılmış sayılarak dışarı çıkarılmaz.

Bu öneri yeni bir toplam bütçe, amortizasyon eşiği veya evrensel en-kötü-durum şartı koymaz; birimleri ve kanıt sınırını netleştirir.

### R3 — Çift sayımlı toplam veya bilinmeyen payda otomatik alt sınır değildir

Konum: satır 79 ve 96. Aynı satır kopya atlama, çift sayım ve belirsiz D_k için ortak olarak “bilinen alt sınır” diyor. Çift sayımlı bir sayı gerçek toplamı aşabilir. Mutlak bazı baytlar bilinse bile payda bilinmiyorsa bunların B/vektör alt sınırı olduğu ileri sürülemez.

Önerilen yerine koyma:

> Alt sınır yalnız kapsam içinde olduğu doğrulanmış, çakışmayan ve tekilleştirilmiş fiziksel kalemlerin toplamından kurulabilir; kuşkulu kalemler bu kanıtlanmış alt toplama dahil edilmez. B/vektör alt sınırı ayrıca doğru tahsis ve bilinen pozitif nüfus gerektirir. Bu koşullar yoksa ilgili toplam veya etkin değer UNKNOWN kalır; yalnız doğrulanmış mutlak baytlar ve çözülmemiş kalemler ayrı raporlanır. Yanlış veya çift sayımlı toplam alt sınır diye yayımlanmaz.

## Küçük tutarlılık açıklaması

Satır 23'te “paylaşım grupları sabittir”, satır 31'de ise N ve N+q için nüfus yeniden belirtilir. Grup üyeliği/kardinalitesi ile paylaşım politikası ayrılmalı. İlk ifadeyi “paylaşım politikası ve fiziksel durum kopyaları sabittir; G_k üyeliği ve D_k her prob anlık görüntüsü için ayrıca bağlanır” olarak netleştirmek yeterlidir. Frozen-encoder append iddiasının kendisi uygundur; refit veya kalite kanıtı eklemek gerekmez.

## Hükmün sınırı ve parent'a dönüş

R1–R3 ve küçük paylaşım açıklaması ana belgeyi hazırlayan parent'a dönen metin önerileridir; bu inceleyen ana belgeyi düzenlemedi. Yeni taslak hash'i bu rapordaki hükmün konusu değildir. Parent'ın kaynak bağları ve paket hash'i ayrı doğrulanmalıdır.

Taslağın no-signal kapanışı, UNKNOWN ayrımı, `a` dahil marjinal tavanı, fiziksel kopya/D_k muhasebesi, heterojen ağırlıkları, sabit filo/yeni arşiv ayrımı ve maddilik tautolojisinden kaçınması tasarım düzeyinde destekleniyor. R1 mevcut abort hükmünün açık aktarımındaki boşluğu kapatır; R2/R3 yanlış sayısal hükme dönüşebilecek muhasebe belirsizliklerini kapatır.

**Hiçbir gerçek maliyet, tam model kaynağı hazırlığı veya yeniden açılabilirlik doğrulanmadı. Kaynak engeli bu incelemeyle kalkmaz; bütün gerekli model artefaktlarının eksiksizliği ve kullanılabilirliğinin kanıtı açık kalır. Task4F1 SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN durumu ve diğer mevcut korumalar değişmez. Bu rapor tasarım incelemesidir; onay veya ölçüm sonucu değildir.**
