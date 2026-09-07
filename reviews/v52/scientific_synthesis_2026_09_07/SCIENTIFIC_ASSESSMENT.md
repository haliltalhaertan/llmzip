# V52 — Koordinat ölçeği çalışmasının birleşik bilimsel değerlendirmesi

Tarih: 2026-09-07. **Önerilen değerlendirme; kanonik kabul veya yeni deney yetkisi değildir.**

## Ana karar önerisi

**LoCoMo'daki hesaplamasal yeniden üretimi kabul edilebilir kanıt olarak kayda alın; karşılaştırmalı mekanizma sonucunu kabul etmeyin.** Çalışmayı mevcut haliyle dar kapsamlı, sınırlılıkları açık bir müdahale gözlemi olarak raporlayın. Kanonik kararın sahibi ve tek state/ledger yazarı bu öneriyi ayrıca değerlendirmelidir. Bu dal `main` veya ledger'ı değiştirmez.

Bu iki karar çelişmez: aynı skorları güvenilir biçimde üretebilmek, seçilen ölçütün sorulan mekanizma sorusuna sağlam yanıt verdiğini göstermez.

## Kanıt düzeyleri

| Soru | Mevcut değerlendirme | Sınır |
|---|---|---|
| Mühürlü LoCoMo kodu aynı veriden aynı skorları üretiyor mu? | **EVET: hesaplamasal yeniden üretim PASS.** 1535 soru ×10 seed ×6 kol;92100 kayıtta skor farkı0. | Aynı yöntem ve benchmark; bağımsız yöntemsel replikasyon değil. Eski top-3 belge ID'leri saklanmadığından bunların eşitliği kanıtlanmadı. |
| Dosya baytları tamamen aynı mı? | CSV, yalnızca karşılaştırma belleğinde CRLF→LF eşitlendiğinde birebir aynı. | Gzip zaman damgası ve satır sonları farklı; summary tanı değerlerinde çok küçük farklar var. Ham bayt eşitliği iddiası yok. |
| Ölçekleme, tam karıştırma kolundaki skoru artırıyor mu? | Bu sabit veri/pipeline üzerinde **betimsel gözlem korunuyor**. LoCoMo ham-veri yeniden üretimi de aynı gözlemi veriyor. | Bu tek başına karşılaştırmalı mekanizma karar kuralını sağlamaz. LongMemEval bu turda ham veriden yeniden çalıştırılmadı. |
| LoCoMo MOST, LongMemEval PARTIAL ayrımı sağlam mı? | Yalnızca donmuş panelin nokta sınıflaması olarak tutulabilir. | Her iki toplama biçiminin, üç yeniden örnekleme şemasındaki tam-kol yüzdelik aralıkları0.70'i kesiyor. Popülasyon kategorisi farkı kurulmadı. |
| Ölçek tam karıştırmaya blok karıştırmadan daha fazla yardım ediyor mu? | Temiz bir karşılaştırmalı mekanizma hükmü **desteklenmiyor**. | Her iki oran tanımında bütün etkileşim yüzdelik aralıkları sıfırın iki tarafına uzanıyor; paydalar kararsız. Bu, geçerli klasik bir anlamlılık testi veya mekanizma-yok kanıtı değildir. |
| Ön-kayıt eksiksiz uygulandı mı? | **Koşulsuz PASS verilemez.** | Toplama sırası ve yorum kuralları uyuşmazlıkları, eksik/sonradan tamamlanan belirsizlik analizi, LME konuşma eşlemesi ve kontrol kapsamı açıklanmalı. |

## Birlikte taşınması gereken açıklamalar

1. **A/B farkı:** A, seed başına oranların ortalamasıdır; B, seed-ortalama kazancın seed-ortalama kayba oranıdır. Mühürlü uygulamanın tarihsel ana çıktısı B'dir. A/B önkayıt uyumu bağımsız karara bağlanmadan birini sonuç görüldükten sonra tek doğru tanım ilan etmeyin. Orijinal sayıları silmeyin.
2. **Belirsizlik tamamlaması post-outcome'dur:** plan/kod bootstrap çalışmadan önce Git'e kaydedildi; fakat özgün deney sonuçları zaten biliniyordu. Bu nedenle önceden tam belirlenmiş bilimsel tasarım gibi sunulamaz. Üç şema×10000 tekrar, sabit10 rotasyon seed'ine koşulludur.
3. **Blok oranı sorunu yalnız LoCoMo değildir:** pozitif olmayan en az bir seed paydası bulunan tekrar sayıları LoCoMo-soru8910, LoCoMo-küme8410, LME-soru3306 /10000 olarak bağımsız kontrol edildi. LME'deki bir boş A etkileşim kaydı ve çok büyük sonlu uç değerler CSV'de doğrulandı. İç seed'lerin tam-sıfır/yakın-sıfır sayıları yalnız min/max/mean saklandığı için bütünüyle yeniden çıkarılamıyor; ilgili ayrıntılar üretici tanısı olarak ayrılmalı.
4. **Grup sınırı:** LoCoMo'nun10 grubu üretici archive-ordinal metadata'sından geri kazanıldı; ayrı bir ham-korpus kimlik join'i değil. LongMemEval için ortak konuşma eşlemesi kurulmadığından konuşma bootstrap'ı tamamlanmış sayılmıyor.
5. **Kontrol sınırı:** signed-permutation kontrolünün upstream kanıtı var; mühürlü scale runner bu kontrolü kendi çağrısında yeniden yürütmüyor. Aynı kodu yeniden üretmek önkayıt kapsamındaki her kontrolü ayrıca doğrulamak değildir.

## Kullanılabilecek kısa sonuç metni

> Sabit pipeline üzerinde, pozitif koordinat ölçeklemesi native işaret temsilini korurken tam ortogonal karıştırma sonrasındaki retrieval skorunu artırdı. LoCoMo'daki mühürlü hesaplama, doğrulanmış ham veri ve kilitli paket sürümleriyle92100 soru/seed/kol kaydında sayısal olarak birebir yeniden üretildi. Bununla birlikte blok-normalize karşılaştırmaların payda kararsızlığı ve önkayıt yorum/toplama uyuşmazlıkları, karşılaştırmalı mekanizma çıkarımını sınırlar. Sonradan tamamlanan duyarlılık analizleri bu sınırlılığı gidermez; görünür kılar. Sonuç aynı yöntemin genel bir mekanizma kanıtı, üretim sistemi üstünlüğü veya farklı encoder/korpuslara genelleme olarak sunulamaz.

Bu metin de kanonik kabulden önce öneridir; tam deney aşaması için koşulsuz bağımsız-audit etiketi yerine kapsamı belirtilmelidir.

## Program için önerilen sonraki karar

Yeni bir aynı-tür hesap/denetim döngüsü başlatmayın. Önce bu dar raporlama kapsamını ve açık sapmaları kanonik değerlendirmeye alın. Ardından yeni bilimsel çalışma istenecekse, sıfıra yaklaşan blok kaybına bölünmeyen ve rakip mekanizma açıklamalarını ayırabilen ayrı bir ileriye dönük tasarım için karar verin. Burada yeni ölçüt, eşik, seed, model, deney veya literatür-yenilik iddiası seçilmedi.

Tam görevlendirilmiş koordinat denetimi ve literatür taraması raporlarının hedef dalları son uzak kontrolde yoktu. Bu durum ajanların çalıştığını veya durduğunu kanıtlamaz. Mevcut onay LoCoMo'nun bir kez yeniden üretimini kapsadı ve o iş tamamlandı; yeni deney yetkisi değildir. BEAM/Task4F1 BLOCKED/FORBIDDEN olarak kalır.

## Kaynaklar ve doğrulama

`EVIDENCE_LOCK.json` tam commit/path/SHA256/boyut/Git-blob kimlikleriyle10 kaynağı bağlar. `verify_evidence.py` bunları Git objelerinden tekrar oluşturur; sayısal özetlerin bu metindeki aralık/yeniden-üretim iddialarını desteklediğini denetler. Bu araç eski deneyleri veya bootstrap'ı çalıştırmaz; yeni bağımsız bilimsel denetim yerine geçmez.

Başlıca kaynak commit'leri: özgün inceleme4769c2a; düzeltme önerisi1aa6184; bootstrap398c2ea; bağımsız sınırlı bootstrap denetimi ve düzeltmesia131341; LoCoMo ham-veri yeniden üretim denetimi692f599; kanonik duruma094452. Hepsi yayımlanmış dallarda ayrı kapsamlarıyla korunmuştur. Bu değerlendirme o kapsamları birbirine karıştırmaz.
