[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# C Kuyrukları ve Hubness: Tanımlayıcı Geometri Ölçümü (Türkçe Rapor)

**BEYAN EDİLMİŞ YENİDEN-UYARLAMA (declared re-fit):** bu belge dondurulmuş üretim yapıtını anlatmaz; gerçek derlem üzerinde temsil hattının yeniden uyarlanmasından okunan tanımlayıcı geometri istatistiklerini raporlar.

**Sınır beyanı (bağlayıcı):** Mühürlü "Task4F1" görevine saygı gereği altın/evidence etiketleri açılmadı, recall/dogruluk hesaplanmadı, hiçbir sıralamanın DOĞRU olup olmadığı değerlendirilmedi, benchmark çalıştırılmadı. Puanlama fonksiyonları yalnızca **birbiriyle** karşılaştırıldı; gerçekle (truth) karşılaştırma yoktur. "A sıralaması B sıralamasıyla %X uyumlu" bir geometri cümlesidir; "A doğru cevabı daha çok bulur" cümlesi bu çalışmada kurulamaz.

## Test edilen hipotez

Kanıtsız bir iddia, dondurulmuş işaret kodunun neden işe yaradığına dair bir MEKANİZMA öneriyordu: C'nin SVD koordinatları ağır kuyrukludur (basklık 9.71, çarpıklık 1.58 iddia edildi, kodsuz); birkaç aşırı koordinat değeri float iç-çarpımları domine eder ve "her şeyin komşusu" hub vektörler yaratır; `sign(C)` bu aşırılıkları ±1'e kırparak bozulmayı giderir.

Bu ölçüm o hikâyenin **öncülünü** (kuyruk istatistikleri + hub yapısı) test eder; geri-getirim kalitesi hakkındaki **sonucu** burada ölçülemez.

## Yöntem (kısa)

- 15 kapılı arşiv (geometri tablosunun ilk 15 satırı); merkezlenmiş matris C (N×96), SVD tohumu 5204, dondurulmuş propla aynı hat.
- Momentler: popülasyon momentleri (paydada N); çarpıklık=m3/m2^1.5, artı basıklık=m4/m2^2−3.
- Hubness/uyum: leave-one-out problar; üç skor (a) C'de float kosinüs, (b) ±1.5σ_i kırpılmış C'de float kosinüs (σ_i: koordinat-içi popülasyon ss), (c) sign(C)'de Hamming. Bağ-kırma: arşiv-sıralı sabit tohumlu rastgele öncelik, üç skorda aynı vektör (etiketsiz, deterministik).
- Soru/etiket alanları hiç okunmadı; yalnızca arşiv turn metinleri kullanıldı.

## ADIM 1 — C'nin kuyruk istatistikleri

Koordinat-başına (1440 koordinat, 15 arşiv) ve havuzlanmış (tüm girdiler) okumalar; iddia hangi okumayı kastettiğini söylemediği için ikisi de raporlanır (belirsizlik notu budur).

| okuma | basıklık (artı) | çarpıklık |
|---|---|---|
| iddia edilen | 9.71 | 1.58 |
| koordinat-başına medyanların medyanı (aralık) | 1.10 (0.78–1.52) | 0.09 (0.00–0.18) |
| tüm koordinatlar: medyan [p25, p75, p90, p99, maks] | 1.07 [0.47, 2.18, 4.56, 18.2, 84.9] | 0.09 [p10 −0.40, p90 0.72, maks 8.58] |
| havuzlanmış medyan (aralık) | 5.35 (4.48–8.79) | 0.22 (−0.03–0.70) |
| Gauss referansı | 0 | 0 |

**Hüküm: iddia edilen 9.71/1.58 tipik değer olarak YANLIŞLANDI.** Ne koordinat-başına ne havuzlanmış okuma iddiaya yaklaşır (yaklaşık üretim bile yok: basıklıkta ~9 kat, çarpıklıkta ~17 kat fark). Dağılım şekli: gövde ılımlı, sağ kuyrukta az sayıda aşırı koordinat (basıklık >9.71: 1440'ta 55, %3.8; çarpıklık >1.58: 42). İddia ancak küçük bir aşırı-koordinat azınlığını anlatıyor olabilir; C'nin özeti olarak geçersizdir.

**Gauss'tan uzaklık:** N≈500'de örnekleme gürültüsü ss ≈ 0.11 (çarpıklık), ≈ 0.22 (basıklık). Medyan çarpıklık 0.09 gürültü bandındadır; medyan basıklık 1.1 gerçektir ama küçüktür — **ılımlı** ağır-kuyrukluluk, iddia edilenin yanına yaklaşmaz.

**İç-çarpım yoğunlaşması** (tüm çiftler, i<j; f1=en büyük |terim|/|toplam|, f3=ilk 3 terim):

| nicelik | medyan | p90 | p99 | P(>1) |
|---|---|---|---|---|
| f1 (gerçek) | 1.43 | 7.7 | 77 | ≈0.65 |
| f1 (varyans-eşleşmeli Gauss kontrolü) | 0.80 | — | ≈42 | ≈0.40 |

f1'in büyük görünmesi **sönümlenme** (payda |S|'nin küçük olması) nedeniyledir, aşırı paylar nedeniyle değil: Gauss kontrolünde bile medyan 0.80 ve P(>1)≈0.40. Sönümlemeden arındırılmış yardımcı ölçü: en büyük terim mutlak-kütlenin medyan %13.5'ini (Gauss %11.6), ilk 3 terim %31'ini (Gauss %27) taşır. Yani: birkaç aşırı terimin iç-çarpımı domine ettiği **yoktur**; Gauss'a göre yalnızca hafif fazlalık vardır.

**İşaret dengesiyle uyum:** önceki ölçüm yeniden üretildi — [0.45,0.55] dışı medyan 11/96 koordinat, [0.30,0.70] dışı 0 (bir arşivde 1). Bununla ılımlı kuyruklar çelişmez: kuyruk **büyüklük** (|C|), denge **taraf** (işaret) hakkındadır; medyan çarpıklık ≈0.09 simetriye yakın, ılımlı-ağır-kuyruklu (t-benzeri) koordinatlarla tutarlıdır.

## ADIM 2 — Hubness (k ∈ {3, 10})

N_k(i) = i vektörünün başkalarının k-komşu listesinde görünme sayısı. Mekanizma hikâyesi (a)'da yüksek, (b) ve (c)'de düşük hubness öngörür. Bulgular (15 arşiv medyanı):

| k | ölçü | (a) ham kosinüs | (b) kırpılmış | (c) işaret Hamming |
|---|---|---|---|---|
| 3 | N_k çarpıklığı | 0.28 | 0.20 | 0.21 |
| 3 | maks N_k | 8 | 8 | 7 |
| 3 | ilk %1'in slot payı | 0.026 | 0.026 | 0.024 |
| 10 | N_k çarpıklığı | 0.05 | −0.02 | **0.33** |
| 10 | maks N_k | 20 | 19 | 20 |
| 10 | ilk %1'in slot payı | 0.021 | 0.019 | 0.020 |

(Düzgün dağılımda ilk %1'in payı 0.01 olurdu; gözlenen ~0.02 ılımlı yoğunlaşmadır. k=10'da maks 20/≈500 prob ≈ %4 — "her şeyin komşusu" hub yoktur.)

**Hüküm: mekanizma öngörüsü YANLIŞLANDI.** Hubness ılımlı ve üç skorda benzerdir; k=10'da işaret skorunun çarpıklığı ham float'tan **yüksektir** (0.33'e 0.05) — öngörünün tersidir. İki arşivde ham hubness yükselir (06f04340: çarpıklık 1.40, maks 37; 078150f1: 0.64, maks 28) ve kırpma bunları düşürür, ama örüntü sistematik değildir ve işaret skoru sistematik olarak düşük değildir.

## ADIM 3 — Kırpma ve işaret birbirine benziyor mu?

Aynı problarda ilk-10 listeleri; çiftli uyum (15 arşiv medyanı):

| çift | overlap@3 | overlap@10 | Spearman ρ |
|---|---|---|---|
| ham vs kırpılmış-1.5 | 0.93 | 0.93 | 0.85 |
| ham vs işaret | 0.76 | 0.60 | 0.23 |
| kırpılmış-1.5 vs işaret | 0.77 | 0.61 | 0.34 |

Kırpılmış sıralama işarete hamdan daha yakındır: overlap@10'da 15/15, ρ'da 15/15, overlap@3'te 11/15 arşivde. Ancak etki overlap'te küçüktür (+0.008 overlap@10).

Kırpma eşiği taraması (işaretle uyum, medyan):

| eşik | overlap@3 | overlap@10 | ρ |
|---|---|---|---|
| ±0.5σ | 0.765 | **0.622** | **0.526** |
| ±1.0σ | 0.770 | 0.611 | 0.416 |
| ±1.5σ | 0.770 | 0.607 | 0.338 |
| ±2.0σ | 0.767 | 0.608 | 0.289 |
| ±3.0σ | 0.763 | 0.603 | 0.244 |
| kırpmasız (ham) | 0.762 | 0.599 | 0.230 |

**Tepe:** overlap@10 ve ρ 15/15 arşivde en agresif eşikte (±0.5σ) tepe yapar; overlap@3 yatıktır (tepeler 4/3/2/4/2 dağılır). İşaret sıralaması, sıralama bakımından agresif bir kırpıcıya benzer — **ama** kuyruklar ılımlı olduğundan ±0.5σ kırpma "aykırı temizliği" değil, büyüklük bilgisinin toptan imhasıdır; benzerlik bilgi kaybı benzerliğidir, aykırı-kırpma mekanizması kanıtı değildir. En iyi uyumda bile ilk-10 slotlarının ~%38'i farklıdır.

**Açık beyan:** işaretle uyum, doğruluğa dair kanıt DEĞİLDİR. İki sıralama birlikte yanlış olabilir; doğruluk bu çalışmada ölçülmedi ve ölçülemedi.

## Kapanış: istenen özet

- **Kapı:** GEÇTİ — 15/15 arşivde `N_archive`, `word_columns`, `char_columns`, `combined_columns` birebir üretildi.
- **Basıklık/çarpıklık vs iddia 9.71/1.58:** YANLIŞLANDI. Koordinat-başına medyan 1.10/0.09; havuzlanmış medyan 5.35/0.22. İddia belirsizdi (hangi okuma söylenmemiş); iki okuma da raporlandı, hiçbiri tutmadı.
- **İç-çarpım yoğunlaşması:** f1 medyan 1.43, p99 77 — ama Gauss kontrolü (0.80, p99 ~42) bunun çoğunlukla sönümlenme olduğunu gösterir; mutlak-kütle payı medyan %13.5 (ilk 3: %31), Gauss'un biraz üstü. Aşırı-terim egemenliği yoktur.
- **Hubness:** üç skorda ılımlı ve benzer; k=10 çarpıklığı ham 0.05, kırpılmış −0.02, işaret 0.33; maks ~20; ilk %1 payı ~0.02. İşaret hubness'ı düşürmez.
- **Tarama tepesi:** overlap@10 ve ρ en agresif eşikte (±0.5σ) tepe yapar (15/15 arşiv); overlap@3 yatık. Kırpılmış hamdan işarete daha yakındır ama fark küçüktür.
- **Geri-getirim kalitesi ölçülmedi ve bu mühür altında ölçülemedi;** etiket açılmadı, doğruluk değerlendirilmedi.
- **Kontrol-etmedi vs yanlış ayrımı:** YANLIŞ (ölçüldü): tipik 9.71/1.58; ham float'ta hub egemenliği; işaretin hubness'ı düşürmesi; iç-çarpımda aşırı-terim egemenliği. KONTROL EDİLMEDİ: işaretin geri-getirimi iyileştirip iyileştirmediği; işaretin neden işe yaradığı; ilk 15 dışındaki arşivler; ±0.5σ altı eşikler.

**Sonuç:** mekanizma hikâyesinin öncülü temiz biçimde çöktü — kuyruklar ılımlı, hub yapısı yok, işaret hubness'ı azaltmıyor. Temiz negatif sonuçtur ve raporlanabilir en yararlı durumdur.
