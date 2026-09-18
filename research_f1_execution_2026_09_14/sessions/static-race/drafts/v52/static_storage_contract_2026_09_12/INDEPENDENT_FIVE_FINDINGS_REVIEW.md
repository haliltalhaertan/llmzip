# Beş bulgulu revizyon — bağımsız inceleme

Tarih: 2026-09-12. İnceleme türü: belge ve kaynak kod okuması, sınırlı sentetik doğrulama; uygulama geliştirme veya bilimsel deney değil.

**Güncel hüküm: PASS — yalnız hash'leri aşağıda bağlı belge revizyonu ve sentetik guard kapsamı için. FS-1'in dar düzeltmesi bağımsız kaynak okuması ve yeniden koşulan 3+16 kontrolle kapatıldı; önceki REQUEST_CHANGES ve başarısız karşı örnek kaydı aşağıda korunur. Gerçek ölçüm hazırlığı: NOT_READY. F4 guard uygulanmış ve sentetik kapsamda test edilmiştir; gerçek projektör adaptörü/runner entegrasyonu ve gerçek F2 ablation'ları OPEN kalır. Bilimsel onay ve çalıştırma yetkisi verilmedi.**

İlk incelemede worker'ın 29 sentetik testi ve worker fixture'larını kullanmadan yazılan 16 bağımsız sentetik kontrol gerçekten çalıştırıldı ve geçti. Sonraki üç hedefli kontrolden sabit ortak model büyümesini reddetmesi gereken regresyon eski guard'da başarısız oldu. Worker düzeltmesi sonrasında aynı değişmemiş hedefli 3 test ve mevcut 16 bağımsız test yeni guard üzerinde yeniden çalıştırıldı ve tamamı geçti. Worker'ın yeni 32 testlik tam paketinin başarı bildirimi ayrı bir worker beyanıdır; incelemeci bu son aşamada 32 testi yeniden koşmadı. Bu kontroller gerçek projektörün saklanabilirliğini, işlevsel zorunluluğu veya gerçek maliyetlerin doğruluğunu kanıtlamaz.

## İncelenen kimlikler ve kapsam

Worktree: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\llmzip_storage_contract_20260912`

Namespace: `drafts/v52/static_storage_contract_2026_09_12`

Doğrulanan HEAD / önceki yayımlanmış taban: `d936455e2938a37da2b1a934f912cc2705b07ad3`. Bu rapor o commit'in değişmemiş belgesine değil, aşağıdaki çalışma ağacı baytlarına bağlıdır. Parent'ın diğer paketleme değişiklikleri bu incelemenin kapsamına alınmadı.

| İncelenen dosya | Ham dosya SHA256 |
| --- | --- |
| MEASUREMENT_CONTRACT_TR.md | `e395451d026f176b875856244abe73b54a7d54cdf2649eec272f14cfc609c510` |
| measurement_plan_guard.py | `19724919c9085e49a531e94bdb269cba96c81739f7d9449b717db982becde4c9` |
| MEASUREMENT_PLAN.template.json | `c7eefc3a53b752a814fc2b78d98b3803743bfd4d6ff7b9aa0933587f2f6e67b4` |
| PLAN_INTERFACE.md | `5af57ca10b83062b13243ebbbf4559bd5a762065dcaaa5faa60ba0a2c40b0f29` |
| test_measurement_plan_guard.py | `f2a4817f47beefaab288dab4c24c1e760862eb7bfea27d7895ac810cf3a3da06` |
| FIVE_FINDINGS_RESPONSE_TR.md | `aaac7c10917c25d5dab0efbc99baed96bbd501ebf65077469984ac3924aaad13` |
| review_checks/test_independent_guard.py | `af822b7aa52c7441427f2f818f20324f3d8b3ff8835b62f78d618e54b3277448` |
| review_checks/test_frozen_shared_review.py | `88b601a89a8e490566979b45844496f585e009474e1d5d49a06c8be4bb3d22f1` |

Başlangıçta okunan özgün bütçe kaynağı: `source/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`, SHA256 `1832f4b368024edba4a7f5d2d3f925e9c9b1c53367f1a4ed54b7586b2ec8cc26`; okuma sırasında sidecar ile eşleşti. Son aşamada bütçe kaynağı yeniden okunmadı. Kaynağın chat üzerinden aktarılmış, HR imzalı artefakt olmayan yetki statüsü yükseltilmedi. Vektör başına bütün kalıcı durumun ≤12 B sınırına girmesi, paylaşılan durumun ayrı raporlanması ve gerçek serileştirme/deklarasyon uyuşmazlığında runner'ın durması yükümlülükleri korunuyor.

Her hazır bildiriminden sonra ilgili dosyaların canlı ham hash'leri alındı. İlk inceleme ve FS-1 ön düzeltme koşusu eski `e6cea015...` guard'ına; bu raporun güncel hükmü tablodaki `19724919...` guard'ına bağlıdır. Son 3+16 bağımsız koşunun her biri tek ham guard anlık görüntüsü yükleyip yeni hash'i stdout'a yazdı. Yeni guard, arayüz, worker testleri, değişmeyen belge/şablon ve bağımsız test hash'leri koşu sonrasında yeniden doğrulandı. Önceki ara kaynak bulguları nihai sürüme otomatik taşınmadı.

## Beş bulgunun dispozisyonu

Aşağıdaki beş bulgu değerlendirmesinin olumlu kontrolleri yeni guard üzerinde de geçerlidir. F1/F4'ün sabit model boyutuna ilişkin takip bulgusu FS-1 dar düzeltme ve regresyonla kapandı; gerçek adaptör ve içerik eşitliği incelemesi bu kapanışa dahil değildir.

| Bulgu | Doğrulanan karşılık | Kapanış sınırı |
| --- | --- | --- |
| F1 — Tam paneli ölçümden önce dondurma | Sözleşme satır 31 bütün arşiv/config/N/q/tohum veya sentetik fixture/biçim/kalem/kontrol panelini dış hash kaydına bağlar. Guard tam envanter referanslarını, sıralı istek panelini ve sabit ağırlıkları denetler. `analysis_mode` ve `parent_plan_sha256` istek, tamamlanma ve claim cümlesinde taşınır. Bağımsız testte EXPLORATORY satırları ilk planın tamamlanmasında reddedildi. | Belge ve beyan bağlama düzeyinde kapalı. Gerçek tam panel, bağımsız ön kayıt, fixture/tohum kimliklerinin gerçek kaynaklara çözülmesi ve kayıt zamanının doğruluğu henüz yok/doğrulanmadı. Hash zaman sırasını veya yetkiyi kanıtlamaz. |
| F2 — Dahil/dışarıda kalemlerin işlevsel sınanması | Sözleşme satır 55–63 dönüşümü ve gerçek retrieval içermeyen sentetik ID/offset eşlemesini; çıkarma, aynı baytı geri koyma ve uygun bozma panelini açıklar. Satır 61 önceki belge açıklığını kapatır: gerekli olmayan kalemin çıkarılmasında işlev korunur ve uygulanmayan negatif kontrol gerekçesi yazılır. Guard baseline/restore çelişkilerini reddeder; NOT_REQUIRED ve EXTERNAL_BOUNDARY ayrıdır; NA yalnız gerekçeli CORRUPT olabilir. Tekil ve birleşik fallback kontrol kapsamı zorunludur. INCLUDED opsiyonel baytlar MATCH sonuçlarına rağmen kalır. | Belge ve kontrol beyanı/kapsamı düzeyinde kapalı. Gerçek ablation, bozma, geri yükleme, süreç izolasyonu, fallback yokluğu ve işlevsel karşılaştırma uygulanmış sayılmaz. Evrensel minimum temsil boyutu sonucu yoktur. |
| F3 — UNKNOWN'ın sayıyla birlikte taşınması | Sözleşme satır 104–108 ve `make_claim` margin, cap hükmü, UNKNOWN kalem/kontrol kimlikleri, tamlık ve toplam türünü aynı nesne ve cümlede tutar. Potansiyel PER_VECTOR/UNKNOWN kapsamlı eksik kesin within-cap hükmünü engeller. Yalnız SHARED eksiklikte uygun kapsamlı margin ifadesi mümkünken toplam UNKNOWN ve durum PARTIAL kalır. | Claim oluşturma düzeyinde kapalı. Sonraki dışa aktarıcı veya grafik yalnız sayı alanını seçerse bu guard onu durdurmaz; tam nesne/cümleyi korumak tüketici yükümlülüğüdür. Tam zincir hazır veya runner devam edebilir hükmü yoktur. |
| F4 — Makine PLAN guard'ı | `load_plan` dışarıdan gelen ham plan hash'ini JSON ayrıştırma ve sözleşme okumasından önce karşılaştırır. `guarded_probe` her callback öncesinde plan/sözleşmeyi yeniden doğrular ve tam istek üyeliği arar; sonrasında yeniden kontrol eder. `finalize` eksik/fazla/tekrarlı/sırası değişmiş gözlemleri reddeder. Şablon eşleşen hash ile de NOT_READY olarak reddedilir. | Sentetik guard alt kapsamı kapalı. **Gerçek projektör adaptörü ve runner entegrasyonu OPEN**; üretim ölçümünün bu kontrollerden geçtiği kanıtlanmadı. |
| F5 — Önceden sabit başlık ve tam nüfus | Belge satır 51 arşiv ağırlıklı `mean_i(C_i/N_i)` başlığı ve vektör ağırlıklı ikincil özeti sabitler. Claim tam ve sıralı arşiv listesini/N_i değerlerini ister; altküme kabul edilmez. Bağımsız oyuncak örnekte başlık 20, ikincil 28 çıkarak formüller ayrıştırıldı. UNKNOWN toplam ana başlığa sayı olarak yükseltilmez. | Belge ve claim hesaplama kapsamı kapalı. Gerçek tam nüfusun dışarıdan eksiksiz ilan edildiği henüz doğrulanmadı. |

## FS-1 — Önceki sabit ortak model boyutu açığı [P2, DÜZELTİLDİ]

**Düzeltme ve yeniden doğrulama:** Yeni guard satır 421–423, INCLUDED/SHARED kalemde `bytes_before == bytes_after` şartını `_observation` içinde uygular. Hem `guarded_probe` hem `finalize` aynı doğrulayıcıyı kullanır. Bu üç satır ham dosyadan yalnız bellek içinde çıkarılarak hesaplanan SHA256, eski guard'ın `e6cea01532a47bd4fa1711d32d5bb41535292acf5d95896493eb3aa2afa83d18` hash'iyle tam eşleşti: guard'daki delta yalnız bu üç satırdır. Worker'ın yeni eşitlik, büyüme/küçülme ve PER_VECTOR testlerinin kaynakları okundu. Arayüz satır 103–110, SHARED'ı bu şemada sabit model boyutu olarak sınırlar; N'ye bağlı kapsayıcı/başlık ek yükünü ayrı PER_VECTOR kalemi olarak ilan ettirir. Bu, tek tek kayıt yüküyle kapsayıcı farkını iki kez sayma veya parti farkından genel uygunluk çıkarma izni değildir. Sözleşmenin uzlaştırma şartı korunur.

Son koşu: değişmemiş `review_checks/test_frozen_shared_review.py`, **3/3 geçti, 0.109 saniye, exit 0**; değişmemiş `review_checks/test_independent_guard.py`, **16/16 geçti, 0.410 saniye, exit 0**. Her iki stdout yeni `19724919c9085e49a531e94bdb269cba96c81739f7d9449b717db982becde4c9` guard hash'ini bildirdi. Önceki 32→33 karşı örnek artık reddediliyor; 32→32 ortak model ve değişken PER_VECTOR pozitifleri kabul ediliyor. Eşit raporlanan uzunluklar eşit içerik veya doğru artefakt SHA'sı kanıtlamaz; bunlar gelecekteki adaptör yükümlülüğü olarak OPEN kalır.

**Aşağıdaki bölüm eski sürümün değiştirilmeden korunmuş bulgu gerekçesi ve başarısızlık kaydıdır; güncel guard davranışı olarak okunmamalıdır.**

Sınıflandırma: yerel şema/gözlem tutarlılığı açığı; gerçek kaynak dosyası hash doğrulaması veya fiziksel filesystem denetimi talebi değildir. Sözleşme satır 23 model durumu kopyalarını sabit tutar; yalnız kayıtlar, onların vektör başına durumu ve kayıt sayısına bağlı kapsayıcı ek yükü değişebilir. `_observation` (guard satır 410–420) INCLUDED kalemlerde iki bayt alanının ayrı ayrı negatif olmayan tamsayı olmasını denetler; SHARED için değişmezlik veya değişim türü kontrolü yoktur.

Yeni bağımsız fixture'da INCLUDED kalemin cost_scope'u SHARED, rolü açıkça "frozen shared model state; not a container or record-count header", gerekçesi aynı fiziksel model baytları ve sabit biçim olarak ilan edildi. Başka kimlik veya plan değişmeden callback 32→33 bayt döndürdü. Dört panel isteği de kabul edildi ve `finalize` COMPLETE verdi. 32→32 ortak model ve nüfusla büyüyen PER_VECTOR kayıt baytları pozitif kontrolleri geçti. İhlal, yanlış header sınıflandırması gerektirmeden ortaya çıkıyor; ancak serbest metin rolü makine tarafından yorumlanmadığı için mevcut şema iki durumu güvenilir biçimde ayıramıyor.

Arayüzün "yalnız zarf ve sayısal alan" sınırı mevcut kabul davranışını açıklar. Bu, söz konusu örneği geçerli dondurulmuş model gözlemine dönüştürmez. Boyut değişmezliği, gerçek artefaktları okumadan da beyan üzerinden denetlenebilecek gerekli bir tutarlılık şartıdır; eşit boyut ise tek başına eşit içerik ispatı değildir.

Dar düzeltme beklentisi: model durumu ile N'ye bağlı kapsayıcı ek yükünün makinece açık bir sınıflandırması veya eşdeğer kısıtlı şema kuralı olmalı; sabit model kaleminde `bytes_before == bytes_after` zorlanmalı. Meşru değişken kapsayıcı ek yükü ayrı önceden ilan edilmiş kalem/konfigürasyon olarak tanımlanmalı ve marjinal fark uzlaştırmasından düşürülmemeli. Bütün SHARED kalemleri körlemesine sabitlemek, meşru N'ye bağlı kapsayıcıları yanlış reddedebilir. İçerik eşitliği, kaynak SHA'larının dosyaya çözülmesi ve gerçek ölçüm kanıtı yine adaptör yükümlülüğüdür. İncelemeci worker dosyalarını değiştirmedi; düzeltme parent/worker'a bırakıldı.

**Korunacak ön düzeltme başarısızlık kaydı:** Bu karşı örneğin çalıştırıldığı eski guard SHA256'sı kesin olarak `e6cea01532a47bd4fa1711d32d5bb41535292acf5d95896493eb3aa2afa83d18`; hedefli test dosyası SHA256'sı `88b601a89a8e490566979b45844496f585e009474e1d5d49a06c8be4bb3d22f1`; belge SHA256'sı `e395451d026f176b875856244abe73b54a7d54cdf2649eec272f14cfc609c510` idi. Sonraki bir düzeltmenin hash tablosu veya başarılı koşusu bu geçmiş kaydı değiştirmez.

Çalıştırma: `python.exe -B review_checks\test_frozen_shared_review.py`, aynı g3-lock yorumlayıcısı ve namespace. Sonuç: 3 test, 0.127 saniye, 2 geçti / 1 başarısız, exit 1. Başarısız test `test_frozen_shared_model_growth_must_not_complete`; gözlenen çıktı `FROZEN_SHARED_COUNTEREXAMPLE: before=32 after=33; status=COMPLETE`. Ret beklentisi `AssertionError: 'COMPLETE' == 'COMPLETE'` ile başarısız oldu. Eski guard ve belge hash'leri takip koşusundan sonra da yukarıdaki değerlerle aynıydı. Bu sonuç gerçek model ölçümü değil, yeni sentetik beyan/gözlem zarfındaki tutarlılık karşı örneğidir.

## Önceki ara kod bulgularının kapanışı

1. **Alt sınırın FULL'a yükselmesi giderildi.** Güncel guard satır 478–550: `lower_bound_verified=True`, UNKNOWN kalem olmasa da bütün sağlanan maliyetleri, margin dahil, LOWER_BOUND tutar. `headline_full_total=None`; ≤12 alt sınır cap UNKNOWN, >12 doğrulanmış alt sınır EXCEEDS_12 olur. Bağımsız testler 0, 7, 12 ve 12.25 değerleriyle bu ayrımı sınadı. Tek bayraklı API'nin kesin margin + etkin alt sınır durumunu ayrı nitelikli claim'lerle ifade etme sınırı arayüzde açıklanmış.
2. **READY baseline/restore çelişkileri giderildi.** Guard satır 277–290 ve 307–309: baseline/restore FAILURE veya DIFFERENT reddedilir; UNKNOWN yalnız SCOPED_PARTIAL içinde mümkündür ve within-cap hükmünü engeller. NOT_REQUIRED kalemin REMOVE beklentisi MATCH olmalıdır. Bağımsız testler baseline FAILURE, restore FAILURE ve gerekli olmayan kalemde REMOVE→DIFFERENT deklarasyonlarını ayrı ayrı reddettirdi.
3. **Uygulanmayan negatif kontrol gerekçesi temsil ediliyor.** Guard satır 259–276: `applicability=NA`, yalnız CORRUPT ve NA sonucu ile birlikte, bilinen boş olmayan `na_reason` ister. NA, UNKNOWN gibi yorumlanmaz. Bağımsız kontrol geçerli NA'yı kabul etti; null, boş, yalnız boşluk ve UNKNOWN gerekçelerini reddetti.

Destekleyici yanıt metnindeki küçük ifade açıklığı da kapandı: `FIVE_FINDINGS_RESPONSE_TR.md` satır 14 artık bozulan işlev beklentisini "Zorunlu olduğu iddia edilen kalem" ile sınırlar ve NOT_REQUIRED için işlevin korunmasını açıkça yazar. Güncel yanıt hash'i tabloda bağlıdır; ana sözleşme hash'i değişmedi.

## Gerçekten çalıştırılan kontroller

Yorumlayıcı: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\.venvs\g3-lock-20260912\Scripts\python.exe`

Çalışma dizini: yukarıdaki namespace'in mutlak dizini. Bytecode `-B` ile kapalıydı. Worker testleri için süreç yerel TEMP/TMP `review_checks` dizinine yönlendirildi; bağımsız test de geçici dizinlerini burada oluşturup temizledi.

```powershell
$env:TEMP = Join-Path (Get-Location).Path 'review_checks'
$env:TMP = $env:TEMP
& 'C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\.venvs\g3-lock-20260912\Scripts\python.exe' -B -m unittest -v test_measurement_plan_guard
& 'C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\.venvs\g3-lock-20260912\Scripts\python.exe' -B review_checks\test_independent_guard.py
```

| Çalıştırma | Gözlenen sonuç |
| --- | --- |
| Ön düzeltme worker sentetik testleri; incelemeci tarafından çalıştırıldı | Eski guard: 29 test, 3.201 saniye, OK, exit 0 |
| Ön düzeltme bağımsız sentetik testler; ayrı fixture ve ayrı beklentiler | Eski guard: 16 test, 0.891 saniye, OK, exit 0 |
| FS-1 başarısızlık koşusu; yukarıda tam receipt korundu | Eski guard: 3 test, 2 geçti / 1 başarısız, 0.127 saniye, exit 1 |
| FS-1 düzeltmesi sonrasında aynı hedefli testler | Yeni guard: 3 test, 0.109 saniye, OK, exit 0 |
| FS-1 düzeltmesi sonrasında aynı bağımsız paket | Yeni guard: 16 test, 0.410 saniye, OK, exit 0 |

Ön düzeltme 29 testlik koşunun test kaynak SHA256'sı `ece7a176832d9ea46c9fac21367350b0fb82651940a50f44a83505895f48ea12`, arayüz SHA256'sı `4df3f2f9f046f5fb6b1057640e1cf8c5a17a5328931ebe5f56b29968d30cf5cb` idi. Bu eski başarı kaydı yeni 32 testlik paketin incelemeci tarafından yeniden çalıştırıldığı anlamına gelmez. Yeni 32 test için worker'ın OK bildirimi kaynak incelemesinden ayrı tutuldu.

Bağımsız dosya worker'ın test modülünü veya toy fixture üreticisini import etmez. İki kurgusal arşiv, ayrı N/q paneli, ayrı kimlikler ve ayrı maliyet oranları kullanır. Callback yalnız beyan zarfı üretir; işlevsel çıkarma/geri koyma/bozma uyguladığını iddia etmez. Kontroller hash değiştirme sonrasında callback'in çağrılmamasını, değişmiş isteğin reddini, sıralı tam kapsamı, opsiyonel serileştirilmiş baytların tutulmasını, dış bağımlılık ayrımını, UNKNOWN aktarımını ve alt sınır/başlık kurallarını sınar. Bu 45 test sonlu sentetik kapsamdır; bütün olası girdiler veya üretim entegrasyonu için ispat değildir.

İlk geçici test girişimi, guard hash'inin okunmuş ara sürümden değiştiği görülünce Python çağrılmadan durduruldu. O eski şemaya ait test sonucu raporlanmadı. Sonraki gerçek koşuların eski/yeni guard ayrımı yukarıdaki kayıtlarla korunmuştur.

## Açık kalan hazırlık ve güven sınırları

- **Kaynak hazırlığı PENDING:** gerçek arşiv listesi/N_i, projektör ve diğer mevcut kaynak artefaktlarının kimlikleri, fiziksel kopyalar, serileştirme biçimleri ve gerekli kalemlerin eksiksiz envanteri doğrulanmadı. JSON içindeki kaynak, fixture ve üyelik digest'leri dosya içeriklerine karşı çözülmüyor.
- **İşlevsel ablation hazırlığı PENDING:** yeni/temiz süreçte gerçek yükleme ve dönüşüm, sentetik ID/offset işlevi, çıkarma–geri koyma–bozma varyantları ve maskelenmeyen fallback koşulları gösterilmedi. Gerekçe ve expected_outcome beyanları deney kanıtı değildir.
- **Runtime/adapter hazırlığı PENDING; F4 OPEN:** gerçek projektör ölçüm adaptörü yok. Callback'in gerçekten dondurulmuş isteği işlemesi, fiziksel baytları ölçmesi, bunları sonlu farklarla uzlaştırması ve gerçek downstream işlem öncesi ≤12/serileştirme uyuşmazlığı abort'unu uygulaması ayrıca doğrulanmalıdır.
- **Dış kayıt ve çalıştırma yaşam döngüsü PENDING:** guard stateless'tir. Tek dispatch, her başarısızlığın kalıcı kaydı, sonuçların seçilmeden tutulması, parent planın varlığı, farklı run kimliği ve ölçüm öncesi zaman sırası dış kayıt/runner sorumluluğudur. `finalize` eksik kapsamı reddeder; başarısız gözlem günlüğü oluşturmaz.
- **Muhasebe/claim sınırı:** guard sağlanan maliyetlerin gerçekten ölçüldüğünü, tahsis ve tekilleştirmenin doğru olduğunu veya serileştirilmiş kalem atlanmadığını kanıtlamaz. Schema 1 yalnız arşiv-yerel tam snapshot nüfuslarını modeller; örtüşen/kısmi/global paylaşım için ek şema/adaptör incelemesi gerekir. Güvenilir Python callback bir sandbox içinde çalışmaz; postflight kontrol gerçekleşmiş I/O'yu geri alamaz.
- **Bilimsel/yetki durumu değişmedi:** gerçek korpus/query/gold/model veya ayrı retrieval outcome artefaktı okunmadı; deney, eğitim, retrieval, run/finalize/HMAC/seal işlemi yapılmadı. Buradaki `finalize` çağrıları yalnız yeni sentetik guard'ın geçici oyuncak gözlemleri içindir; araştırma hattının finalize işlemi değildir. Task4F1 SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN olarak kalır.

İncelemecinin kalıcı yazıları yalnız bu rapor, `review_checks/test_independent_guard.py` ve takip kontrolü `review_checks/test_frozen_shared_review.py` dosyalarıdır. Son dar yeniden incelemede iki bağımsız test dosyası da değiştirilmedi; yalnız rapor güncellendi. Parent belgesi, worker kodu/testleri/arayüzü/şablonu ve paketleme dosyaları değiştirilmedi; commit, push veya yeni worker başlatılmadı. FS-1'in dar düzeltmesi ve regresyonu tamamlandı. Mevcut kaynak envanteri, gerçek F2 ablation'ları ve F4 gerçek adaptör entegrasyonu açık kalır; bu rapor onların hazır veya onaylanmış olduğunu varsaymaz.
