[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Projektör Bayt Ölçümü (TR)

BEYAN EDİLMİŞ YENİDEN-UYDURMA (declared re-fit): bu belgedeki boyutlar, gerçek
derlem üzerinde hattın sadık yeniden-uydurulmasından ölçülmüştür; dondurulmuş
üretim yapıtının geri kazanımı değildir. O yapıtın fiziksel serileşmesi hiç
bulunamadı. Mühürlü görev Task4F1: retrieval sonucu, recall/doğruluk,
gold/evidence etiketi, sıralama, benchmark, sonuç sayısı hesaplanmadı; yalnızca
uydurulan yapıların serileşmiş boyutları ölçüldü.

## Soru

Defter L-088: vektör başına en çok 12 MARJİNAL KALICI BAYT. Paylaşılan model
durumu (codebook, izdüşüm, vocab, centroid) tavanın dışındadır ama bayt olarak
ayrı raporlanmalıdır. Bu rapor o ayrı sayıdır; yalnızca paylaşılan projektörü
ölçer.

Kural: 12 tavanı yalnızca `marjinal` değere uygulanır. `etkin` değer (= 12 +
paylaşılan/vektör) ayrı raporlanır ve tavana karşı test edilmez. Aşağıdaki her
cümle bu ayrıma uyar; etkin sayılarla 12 yan yana yazıldığında bu aritmetik
bilgidir, tavan testi değildir.

## Yöntem ve envanter

Hat (dondurulmuş probun sorgu yolu): `wv.transform`, `cv.transform`,
`sv.transform(Qw)`, hstack, `s96.transform`, `(.-mu)`. Sorgu için kalıcı
gerekenler: word vocab + IDF, char vocab + IDF, `sv.components_` (32 × word),
`s96.components_` (96 × birleşik), `mu` (96). `TruncatedSVD.transform` yalnızca
`components_` kullanır (kaynakta doğrulandı); SVD'de mean/offset yoktur.
`normalize`/hstack durumsuzdur; şekil/skaler yükü ihmal edilir (<100 B).

Saklama biçimleri: (a) yoğun float32 + vocab yapılı UTF-8 (indeks sırası, terim
başı uint32 uzunluk + UTF-8); (b) yoğun float16 + aynı vocab; (c) aynı
nesnelerin nesne-başı zlib seviye 6 sıkıştırılmışı (ham ve sıkıştırılmış birlikte
raporlanır). Yerel sklearn çıktısı float64'tür; float32/float16 ucuzlama
seçimidir. Ayraç alt-sınırı (UTF-8 + 1 B/terim) ayrıca denetlendi: 15 arşivde
bozucu terim sayısı 0.

Kaçınılmaz: yukarıdaki 7 kalem. Seçim: duyarlık (f64/f32/f16), vocab yapısı,
sıkıştırma açık/kapalı, fazladan SVD alanlarını saklamamak. Hariç (gerekçeli):
`singular_values_` vb. (transform kullanmaz), stop-word listesi (kod sabiti),
ITQ/rastgele izdüşümler/imza kontrolleri (yerel SIGN96 sorgu yolunda yok),
öncelik (çekirdekten üretilir, saklanmaz).

Kapsam: geometri sırasının ilk 15 arşivi. Ölçülen N aralığı 443–551, hepsinde
sözleksel d=32.

## Kapı sonucu

Kapı GEÇTİ: 15/15. Her arşivde `N_archive`, `word_columns`, `char_columns`,
`combined_columns` dondurulmuş CSV ile birebir eşleşti. Ayrıntı `GATE.json`.

## Sonuçlar (bayt; etkin = 12 + paylaşılan/vektör)

(a) ham float32 + yapılı vocab:

| Arşiv | Toplam | Pay/Vek | Etkin |
|---|---|---:|---:|
| 001be529 | 45050700 | 87647 | 87659 |
| 00ca467f | 42408234 | 87260 | 87272 |
| 0100672e | 44550385 | 91667 | 91679 |
| 01493427 | 43354654 | 89024 | 89036 |
| 031748ae | 43903935 | 88874 | 88886 |
| 06878be2 | 46272067 | 104452 | 104464 |
| 06db6396 | 43001921 | 89774 | 89786 |
| 06f04340 | 45422519 | 90303 | 90315 |
| 07741c44 | 41785637 | 81453 | 81465 |
| 07741c45 | 44677102 | 84776 | 84788 |
| 078150f1 | 44220235 | 80255 | 80267 |
| 07b6f563 | 43385335 | 82796 | 82808 |
| 0862e8bf | 43232921 | 88230 | 88242 |
| 08e075c7 | 44272052 | 91471 | 91483 |
| 08f4fc43 | 45038615 | 93830 | 93842 |
| medyan | 44220235 | 88874 | 88886 |

(b) ham float16 + yapılı vocab:

| Arşiv | Toplam | Pay/Vek | Etkin |
|---|---|---:|---:|
| 001be529 | 23110902 | 44963 | 44975 |
| 00ca467f | 21765696 | 44785 | 44797 |
| 0100672e | 22862689 | 47043 | 47055 |
| 01493427 | 22248130 | 45684 | 45696 |
| 031748ae | 22527513 | 45602 | 45614 |
| 06878be2 | 23740817 | 53591 | 53603 |
| 06db6396 | 22065001 | 46065 | 46077 |
| 06f04340 | 23305263 | 46333 | 46345 |
| 07741c44 | 21450149 | 41813 | 41825 |
| 07741c45 | 22914274 | 43481 | 43493 |
| 078150f1 | 22686111 | 41173 | 41185 |
| 07b6f563 | 22263931 | 42488 | 42500 |
| 0862e8bf | 22182133 | 45270 | 45282 |
| 08e075c7 | 22717876 | 46938 | 46950 |
| 08f4fc43 | 23110787 | 48147 | 48159 |
| medyan | 22686111 | 45602 | 45614 |

(c1) zlib (float32 kolu):

| Arşiv | Toplam | Pay/Vek | Etkin |
|---|---|---:|---:|
| 001be529 | 24182838 | 47048 | 47060 |
| 00ca467f | 23068932 | 47467 | 47479 |
| 0100672e | 24163246 | 49719 | 49731 |
| 01493427 | 23439056 | 48129 | 48141 |
| 031748ae | 23896547 | 48374 | 48386 |
| 06878be2 | 24471073 | 55239 | 55251 |
| 06db6396 | 23106616 | 48239 | 48251 |
| 06f04340 | 24264928 | 48240 | 48252 |
| 07741c44 | 22805794 | 44456 | 44468 |
| 07741c45 | 23740675 | 45049 | 45061 |
| 078150f1 | 23733327 | 43073 | 43085 |
| 07b6f563 | 23588228 | 45016 | 45028 |
| 0862e8bf | 22906059 | 46747 | 46759 |
| 08e075c7 | 23619292 | 48800 | 48812 |
| 08f4fc43 | 24016829 | 50035 | 50047 |
| medyan | 23733327 | 48129 | 48141 |

(c2) zlib (float16 kolu):

| Arşiv | Toplam | Pay/Vek | Etkin |
|---|---|---:|---:|
| 001be529 | 17286083 | 33631 | 33643 |
| 00ca467f | 16472581 | 33894 | 33906 |
| 0100672e | 17247342 | 35488 | 35500 |
| 01493427 | 16772698 | 34441 | 34453 |
| 031748ae | 17080062 | 34575 | 34587 |
| 06878be2 | 17589776 | 39706 | 39718 |
| 06db6396 | 16528338 | 34506 | 34518 |
| 06f04340 | 17390093 | 34573 | 34585 |
| 07741c44 | 16312484 | 31798 | 31810 |
| 07741c45 | 16941200 | 32146 | 32158 |
| 078150f1 | 16947003 | 30757 | 30769 |
| 07b6f563 | 16867135 | 32189 | 32201 |
| 0862e8bf | 16397588 | 33464 | 33476 |
| 08e075c7 | 16903210 | 34924 | 34936 |
| 08f4fc43 | 17187768 | 35808 | 35820 |
| medyan | 16941200 | 34441 | 34453 |

Not: tablolar tam sayıya yuvarlandı; tam duyarlık `PROJECTOR_BYTES.json` içinde.
Medyan arşivde (078150f1, a-ham) pay: s96 %85,1, sv %11,4, vocab %2,6, IDF
%0,9, mu ~%0. Yerel f64 + yapılı vocab medyanı referans olarak 87.288.483 B.

Başabaş (medyan toplamdan; tavan testi değil, aritmetik):

| Biçim | Toplam | N(→12) | N(→1) |
|---|---|---:|---:|
| a ham f32 | 44220235 | 3685020 | 44220235 |
| b ham f16 | 22686111 | 1890510 | 22686111 |
| c1 zlib f32 | 23733327 | 1977778 | 23733327 |
| c2 zlib f16 | 16941200 | 1411767 | 16941200 |

Kapsam: tasarım arşiv-yerel uydurur; paylaşılan durum yalnızca o arşivin
N≈443–551 vektörü arasında paylaşılır, küresel değil. Arşivler-arası/küresel
projektör farklı bir dağıtım biçimidir ve özellikleri bu ölçümün sonucu olarak
sunulamaz.

Bakılmayanlar (nedeniyle; "bakılmadı" ≠ "yanlış"): duyarlık düşürmenin
geri-getirime etkisi (Task4F1 yasaklar, bakılmadı); sıkıştırmanın sorgu
gecikmesine etkisi (bakılmadı); küresel projektör (farklı biçim, bakılmadı);
dondurulmuş yapıtın boyutu (yapıt bulunamadı, yalnızca re-fit ölçüldü). 15
dışı arşivlere genelleme yapılmadı.

Medyan etkin değer (a-ham) yaklaşık 88,9 kB'dir, yani 12 sayısının yaklaşık
7.400 katıdır.
