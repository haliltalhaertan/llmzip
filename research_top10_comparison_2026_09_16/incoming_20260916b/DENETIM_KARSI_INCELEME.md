# LLMZIP — Adversarial denetimin karşı incelemesi

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Kısa karar

Denetim qscale'ın Hamming üzerindeki hit@10 sayılarını doğruluyor. Buna rağmen bütün mevcut yöntemler üzerinde, bütün ana metriklerde üstünlük gösterilmiş değil. PerLTQA'da daha önceki asym kontrolü zaten aynı kazanımı sağlıyor. LME ve RealTalk'ta FR@3, Hamming'e göre artmış sayılmaz. Bu itirazlar araştırma sonucunun kapsamını daraltmalıdır.

Denetim metni `run_qscale*.py`, `run_ladder.py` ve `lib_b8.py` yollarını hedefliyor. Son hız/aktarım paketindeki `scripts/kernels.c`, `native_scorers.py`, `profile_optimized.py` ve LoCoMo ölçümlerini denetlediğini göstermiyor. Eski/different uygulamadaki rerank ve resident dense-matrix hataları son paket için otomatik kanıt değildir. Öte yandan son paketin hız sonuçları da bu denetim sayesinde bağımsız doğrulanmış sayılmaz.

## Bu oturumda gerçekten yapılan kontroller

- Son hız/aktarım paketinin manifestindeki 43 dosyanın SHA-256 değerleri yeniden doğrulandı.
- `results/quality_per_query.csv` içindeki 65.826 satır, 6 kol ve 10.971 sorgu üzerinden hit/recall ortalamaları ve eşleştirilmiş farklar yeniden hesaplandı. Yeni veri fit edilmedi ve yeni arama modeli denenmedi.
- Önceki tanı CSV'sindeki 9.440 sorgunun kol ortalamaları ayrıca karşılaştırıldı.
- Arşiv bazlı kayıtlı medyanlardan 48 performans özeti yeniden toplandı ve kayıtlı toplamlarla eşleşti. Bu, zamanlamaların yeniden koşulması değil, kayıtlı sonuçların aritmetik kontrolüdür.
- Denetimde alıntılanan nDCG tie formülü için 302 küçük vaka ve toplam 5.888 sıralama tam sayımla sınandı. Doğru formülün en büyük hatası 1,12e-16 altında; alıntılanan hatalı formül 100 vakada ayrıştı. Özgün `lib_b8.py` çalıştırılmadı.
- Son paketin C çekirdeği derlenip sentetik girdilerde 288 sorgu çağrısı / 56.800 doküman-sorgu skoru başına kontrol edildi. Scalar ve SIMD çıktıları bayt düzeyinde eşleşti; doğrudan sayısal toplamla fark en çok 8,53e-14. Hamming doğrudan bit farkı sayımıyla eşleşti. Bu bir hız ölçümü veya gerçek 10.971 sorgunun yeniden native koşusu değildir.
- Girdi raporları, ZIP'ler, uzak depolar ve dondurulmuş görevler değiştirilmedi.

Uygulayıcı ile bu karşı incelemenin yazarı aynıdır; bu belge dış bağımsız denetçi onayı değildir.

## 1. Baseline ve metrik düzeltmesi: kabul

`qscale - sym` kalite kaybını teşhis etmek için anlamlı bir kontrollü karşılaştırmadır. Ancak bir yöntem ilerlemesi iddiası için eski `asym` ve B8'i de aşmak gerekir. Denetçinin aktardığı PROTOCOL.md, ASYM-SIGN96'yı primary baseline olarak adlandırıyor. Protokolün bu dosyasını bu oturumda ayrıca açmadım; bu rol atamasının kaynağı denetim metnidir.

Soru bazlı kendi CSV'mizden tekrar hesaplanan sonuçlar:

| Veri kümesi | Hamming hit@10 | Eski asym hit@10 | qscale hit@10 | qscale − Hamming FR@3 | qscale − eski asym FR@3 |
|---|---:|---:|---:|---:|---:|
| LME | 86,08 | 85,74 | 88,51 | +0,06 | +3,62 |
| PerLTQA | 75,76 | 80,19 | 80,00 | +4,34 | −0,29 |
| RealTalk | 46,68 | 43,55 | 49,65 | −0,14 | +2,35 |
| LoCoMo | 52,64 | 56,83 | 57,22 | +4,35 | +1,58 |

Yüzdeler veri kümeleri arasında birleştirilmedi. FR@3 burada her soruda gereken kanıtların ilk üç sonuçta bulunan beklenen oranı, sonra sorgular üzerinde ortalamadır. Bu tabloda yeni anlamlılık testi yoktur; özellikle LoCoMo'nun +1,58 FR@3 farkı yalnız betimsel yeniden toplamadır. Denetim LoCoMo'yu kapsamıyor. B8 bu son pakette yeniden değerlendirilmedi; denetçinin B8'e karşı PerLTQA FR@3 farkı −0,35 iddiasını özgün B8 kodundan yeniden çalıştırmadım.

Sonuç: hit@10 kazancı gerçektir; ana eski FR@3 hedefinde bütün mevcut küçük-kod kollarına üstünlük gösterilmemiştir. Asym'e üstünlük ile mevcut en iyi eski kola üstünlük aynı şey değildir. Veri kümesine veya metriğe göre sonradan en iyiyi seçmek de uygulanabilir tek bir model seçme kuralı değildir.

## 2. Son hız paketi ile denetlenen uygulamanın ayrılması

Denetçinin W9/W10/C3 eleştirileri: kalite yolunda tie-expanded M aday, hız yolunda strict-M; yeniden sıralamada hazır dense ±1 float matrisi kullanımı. Bunlar hedeflenen betiklerde gerçekleşiyorsa gerçek ölçüm eşleştirme hatalarıdır.

Son paket ise rerank-M değil, bütün kayıtları doğrudan paketli kodlardan puanlayan bir yoldur. `weighted_soa_query` girdileri paketli byte-plane dizisi, sorgu, sigma, LUT ve skor tamponudur. Dense R matrisi bu fonksiyona verilmez. Ana ölçümde LUT her sorguda hazırlanır; Hamming'in sorgu bit paketlemesi ve float32'nin ölçeklemesi de ölçülür. Test harness'i referans karşılaştırmaları için C/float matrislerini ve alternatif düzenleri aynı anda tutar; bu harness'in RSS'si üretim RAM'i değildir. Son rapor bu ayrımı açıkça yapar.

Son pakette sigma float64 olarak sayılmıştır: 520 arşiv için 399.360 bayt; kodlar 3.104.640 bayt; iki dizi türü toplam 3.504.000 bayt. Ortalama dizileri, sözlük/SVD modeli, süreç yükü ve geçici tamponlar dahil değildir. Sorgu başına LUT 3.072 bayttır.

Bu oturumda hız tablosunun ham kayıtları toplandı, zamanlar yeniden ölçülmedi. Dolayısıyla AVX-512 hızlanması ne bu denetimle çürütüldü ne de dışarıdan bağımsız doğrulandı. Kaynak kodu/sürüm/ölçüm yolu eşleşmesi şarttır. Son paketin kalite metriği uniform-tie beklentisi; top-10 zamanlaması sabit belge-ID tie politikasıdır. Bu ayrım raporda açıklanmış olsa da belirli deployment tie politikası için ayrı kalite sonucu gerekir.

## 3. nDCG formül hatası: alıntı üzerinde doğrulandı

Tie grubunda B kayıt, G doğru kayıt, ilk k içinde kalan t konum ve bu konumların indirim toplamı D olsun. Her doğru kaydın bu konumlara dağılımı B olası yer üzerindendir; beklenen DCG katkısı `G * D / B` olmalıdır. Denetimde alıntılanan `G * mean(discounts_in_t)` ifadesi `G * D / t` hesaplar. B > t olduğunda katkıyı şişirir.

Dört eşit puanlı kayıtta tek doğru kayıt, k=1: tam sayım nDCG=0,25; alıntılanan formül 1,00. Aynı grup k=3: doğru 0,5327324384; alıntılanan formül 0,7103099179. `check_ndcg_ties.py` bağımsız tam sayım testidir.

Bu sonuç alıntılanan formülün kusurunu kanıtlar. Eski bütün nDCG çıktılarının yeniden hesaplandığı anlamına gelmez. Hata, hit@k/FR@k fonksiyonlarına otomatik aktarılmaz; son hız ve tanı paketlerimizin altı metriği nDCG içermez. Dondurulmuş dosyalar sessizce yamalanmamalı; etkilenen nDCG sonuçları işaretlenmeli ve yeni sürümde farklarıyla düzeltilmelidir.

## 4. SVD teşhisi: daraltılmalı

Denetçi, kendi 240 LME arşivlik yeniden kurulumunda geniş Z'den 96 boyuta geçince hit@1'in 52,08'den 34,17'ye, merkezlemeden sonra 33,75'e indiğini; aynı 96 koordinatı standardize edince 47,50'ye çıktığını bildiriyor. Bu, kaybın önemli bir bölümünün saklanan koordinatların puanlama ölçeğiyle bağlantılı olduğuna dair güçlü bir müdahaledir.

Doğru çıkarım: 'SVD sonrası sıralama gerilemesinin önemli bölümü, aynı koordinatları başka ölçekle okuyarak telafi edilebiliyor.' Yanlış/geniş çıkarım: 'SVD bilgi kaybetmiyor.' Standardizasyon, atılmış koordinatları yeniden oluşturmaz; gösterilen metrik iyileşmesi bilgi-korunumu ispatı değildir. Ayrıca hit@1'de 52,08 ile 47,50 arasında artık fark vardır. Yalnız eşit ortalamaya dönmek de aynı soruların kurtarıldığını göstermez.

Bizim tanı raporumuzda S4_std karşılığı zaten vardı (tam üç küme ve 48 LME alt paneli). Dolayısıyla 'bu adım hiç denenmedi' eleştirisi `run_ladder.py` hedefi için geçerli olabilir, bütün çalışmalarımız için değil. Önceki kısa anlatımım SVD'de düşüşü doğrudan geri döndürülemez kayıp gibi duyurduysa düzeltilmelidir.

## 5. Denetimin kendi sonuçlarındaki sınırlar

### 5.1. '96 bayt global state' iki ayrı testin birleşimi değildir

Rapor, global tam-hassasiyet std ve arşiv-başına 1-byte std kollarını ayrı ölçüyor. Global ve 1-byte seçeneklerinin birlikte aynı sonucu verdiği tablo gösterilmiyor. İki ayrı ucuzlatma tek başına işe yarayınca birleşiklerinin de kaliteyi koruyacağı kanıtlanmış olmaz. Global istatistik ayrıca her benchmarkın kendi dokümanlarından toplanmış görünüyor; yeni arşive taşınan, veri kümelerinden bağımsız tek vektör ayrı bir testtir. Quantizer aralığı/kod kitabı gibi yan veriler ve değişmeyen arşiv ortalamaları ayrı sayılmalıdır. Bu yüzden 96 bayt, doğrulanmış mevcut toplam maliyet değil, ek test gerektiren adaydır. 'Free' sözcüğü ölçülen dar metriklerden bütün hedeflere genellenmemelidir.

### 5.2. Alpha hakkında aritmetik ve kronoloji

'Alpha=1 hiçbir veri kümesinde en iyi değil' cümlesi, kendi tablosunda LME için alpha=1'in en yüksek olmasıyla çelişiyor. 'Alpha var, dolayısıyla sonuçlara bakılarak seçildi' çıkarımı da tek başına geçerli değil; seçim kronolojisi gerekir. Bizim son aktarım paketinde alpha=1'e eşdeğer formül PLAN_BEFORE_RUN.json içinde LoCoMo puanlamasından önce sabitlenmiş olarak kayıtlı; bu yerel kayıt önceki tüm keşif sürecinin gizli-test/önkayıt ispatı değildir.

### 5.3. Ties ve 'şişirilmiş etki'

Beklenen uniform tie metriği yanlı değil; denetim de bunu kabul ediyor. Hamming'e gold etiketlerini bilen en iyi tie sıralamasını vermek, daha güçlü bir oracle kontrolüdür; orijinal ölçümün yanlılığını hesaplamaz. RealTalk'ta oracle kontrole karşı aralık sıfırı kapsarsa 'bu daha güçlü karşılaştırmada üstünlük gösterilemedi' denir; 'RealTalk etkisi çürüdü/öldü' veya 'her başlık bu kadar şişmişti' denemez. İki karşılaştırmanın hedefleri farklıdır.

### 5.4. Kümelerin bağımsızlığı

29/30 pozitif arşiv etkisi yön tutarlılığıdır; her olası üst düzey kümelenmeye karşı anlamlılığın bağışık olduğu anlamına gelmez. LME'de soru başına bir arşiv olması, arşivlerin ortak kaynak oturumları paylaşmadığını kanıtlamaz. Kendi önceki raporumuz bu nedenle LME için popülasyon güven aralığı sunmamıştı. Denetçinin aralıkları kullanılan yeniden örnekleme birimi ve bağımsızlık varsayımları altında okunmalıdır.

### 5.5. Anlamlı fark bulunmaması eşitlik değildir

'float_std ile matches' veya 'nothing anywhere' ifadeleri, sayısal fark yok veya eşdeğerlik kanıtlandı şeklinde okunmamalıdır. Bazı aralıklar önemli büyüklükte pozitif/negatif etkileri de içeriyor. Buradaki operasyonel sonuç 'genel üstünlük kanıtı yok'tur.

### 5.6. Global std deneyi, tek başına leakage yokluğunu kanıtlamaz

Sorgu/gold içermeyen fit yolunu kod üzerinden izlemek doğrudan destekleyici kontroldür. Global bir istatistikle benzer performans almak, muhtemel başka bir sızıntıyı mantıken imkânsız yapmaz. Raporun bu ek çıkarımı kod denetiminin yerine geçmez.

### 5.7. Depolama etiketi belirsizliği

Denetim sign88'i diğer kollarla aynı toplam doküman bütçesinde listeliyor; eldeki eski devir notu sign88 drop-only için 11 bayt yazıyor. Sabit alan/padding veya farklı bir sign88 sürümü söz konusu olabilir. Özgün protokol, codec ve tam depolama envanteri eşleşmeden bu etiketi kesinleştirmedim.

## 6. Kaydedilecek durum

1. Hamming'e karşı hit@10 faydası korunuyor; genel yöntem üstünlüğü iddiası yok.
2. Eski asym/B8 ve ana FR@3 hedefi zorunlu karşılaştırmalar; PerLTQA kazancı yeni scaling mekanizmasına mal edilmeyecek.
3. Son AVX-512 + LoCoMo paketi bu raporla tam denetlenmiş sayılmıyor; bağımsız denetimde ZIP/manifest ve native kod hash'leri bağlanmalı.
4. nDCG tie kusuru için eski çıktılar korunarak sürümlü düzeltme ve gerçek görev tekrar hesabı gerekli; burada o dondurulmuş görev çalıştırılmadı.
5. Ucuz/global sigma ile ölçek mekanizması yeni adaylardır; ayrı önceden belirlenmiş koşular olmadan üretim onayı yok.

## Kaynak bağları

Birincil denetim: `Yapıştırılan markdown(20260916-100611).md`.
İncelenen sonuç paketi: `LLMZIP_HIZ_GENELLEME_2026-09-16.zip`.
Karşılaştırılan rapor: `LLMZIP_HATA_YERI_RAPORU_2026-09-16.md`.
İlk devir notu: `HANDOFF_2026-09-15.md`.

SHA-256 kimlikleri `SOURCE_HASHES.json`, kendi test çıktıları `package_crosschecks.json` ve `ndcg_exact_checks.json`, yeniden hesaplanan tablo `paired_metric_differences.csv` içindedir. Yeni deney zamanı veya dış kaynaklı teori iddiası eklenmedi; bu belge verilen kaynakların karşılaştırması ve açıkça ayrılmış yerel kontrollerden oluşur.
