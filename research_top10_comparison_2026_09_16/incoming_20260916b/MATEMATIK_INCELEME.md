# LLMZIP — Nadir terim, SVD ve 96 bit bütçesi: matematiksel inceleme

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. Karar ve kanıt sınıfları

Diğer sohbetin RealTalk tablosu, küçük kodun BM25'e göre açığının nadir ortak terim bulunan soru grubunda toplandığını destekliyor. Ancak bu tablo SVD'nin tek başına nedensel etkisini belirlemiyor. Nadirlik, düşük spektral korunma, bit nicemleme, kod puanlama ve doğru kanıt bulma farklı olgulardır.

Bu oturumda yapılanlar:

- Kullanıcının yapıştırdığı yüzdeler üzerinden aritmetik denetim. Bu 705 soruluk yeni deneyin ham kodu ve soru çıktıları alınmadı; yeniden üretildi iddiası yok.
- Kesin SVD, ortak terim frekansı ve birim satır normlarıyla iki sentetik karşıörnek.
- 1.000 rastgele örnekte izdüşüm-puan farkı ve kosinüs ayrıştırma özdeşliklerinin sayısal kontrolü.
- 200 sentetik matriste tek-kayıt terim (singleton) korunma özdeşliğinin kontrolü; ayrıca genel sağ altuzay projektörü için sınır.
- Önceden belirtilmiş ilk üç leksikografik LongMemEval arşivinin ham metinden yeniden kurulması; 1.486 doküman, 22.037 unigram özellik-örneği; 142.656 doküman biti ve üç sorgunun 288 biti önbellekle karşılaştırıldı: sıfır bit farkı.
- Aynı 96 bit hedefine yönelik bir altuzay-ceza fonksiyonu türetildi; yalnız küçük sentetik örnekte test edildi. Yeni bir 96-bit arama yöntemi gerçek benchmarklarda çalıştırılmadı.

Bu sonuçlar yenilik, üretim onayı, genel nedensel ispat veya yeni veri üzerinde başarı değildir. Ham LME paneli RealTalk hipotezini doğrudan tekrar etmez. Koordinat/özellik korunması bilgi kuramsal bilgi miktarı veya soru-cevap başarı yüzdesi değildir.

## 2. Diğer sohbetin aritmetiği ve çıkarımları

341 / 705 = %48,3688: nadir grup en büyük tek grup olabilir, fakat salt çoğunluk değildir.

Yüzdelerin deterministik ikili hit ortalamalarının en yakın onda birine yuvarlandığını varsayarsak, uyumlu tam sayı başarı sayıları tektir:

| Grup | Soru | Kod | BM25 | BM25-kod |
|---|---:|---:|---:|---:|
| Ortak kelime yok | 24 | 5 | 4 | -1 |
| Sıradan | 224 | 47 | 35 | -12 |
| Orta | 116 | 57 | 53 | -4 |
| Nadir | 341 | 241 | 290 | +49 |
| Toplam | 705 | 350 | 382 | +32 |

Bu bir ham-kayıt doğrulaması değildir; tablonun aritmetik açıklamasıdır. Nadir gruptaki +49, diğer gruplardaki -17 farkı aşarak toplam +32 başarı verir. "Genel BM25 farkı bu grupta yoğunlaşmış" ifadesi bu anlamda doğrudur. Ancak hangi işlem nedeniyle böyle olduğu henüz belirlenmez. Ayrıca goldla ortak terime göre gruplama sonuç-bazlı tanısal bir gruplamadır; çalışma zamanında cevap bilinmeden kullanılabilecek bir yönlendirme kuralı değildir. Buna tek başına eğitim sızıntısı da denmez; problem nedensel/genellenebilir yorumun kapsamıdır.

Bit bölme deneyi:

96 bit: 49,65 → 64 bit: 40,85 → 64 SVD + 32 nadir: 34,61.

İlk geçiş -8,80, ikinci geçiş -6,24 yüzde puan. 64 SVD koordinatı ve onun puanlaması iki kolda aynıysa, ek nadir kol/fusion ayrıca zarar vermiştir. Bu eşitlik yoksa izolasyon daha da zayıftır. 80+16 için 80-only referansı gönderilmemiş. 96→64 veya 96→48 düşüşü "tek bir bit bile verilemez" veya "bütün 96-bit kodlar için bu bölme imkânsız" sonucunu ispatlamaz.

32 bitlik taslağın az sayıda farklı skor üretmesi, o kod/puanlayıcı çiftinin kaba çözünürlüğüne işaret eder. 32 bitin sadece beş değer taşıyabileceği anlamına gelmez; 32 bit için olası kod sayısı 2^32'dir. Gruplara ayırmak tek başına rastgele sıralama değildir. Bozulma; çakışma, kodlama ve füzyon ölçeklerinden ayrıca kaynaklanabilir. Taslağın kodunu görmeden hangisi olduğu belirlenemez.

## 3. SVD'nin optimize ettiği şey

N doküman × D özellik matrisi Z olsun. Rank-k ortogonal projektör P=VVᵀ, VᵀV=I_k. İdeal kesilmiş SVD:

    min_P ||Z - ZP||_F²

amacını çözer. Bu, tüm matriste toplam kare hatayı azaltır. "Bir soru için kritik ad/tarih/sayıyı koru" hedefi bu amaçta özel olarak yer almaz. Üretimde randomized SVD kullanılıyor; bu optimumun yaklaşık çözümüdür.

Bir terim sadece m kayıtta yaklaşık a büyüklükle varsa, o ham özellik sütununun karesel enerjisi m a² civarındadır. TF-IDF nadir terimi yerel olarak artırabilir; ama m küçük, doküman uzunluğu büyük veya terimin diğer özelliklerle ilişkisi zayıfsa düşük toplam enerji kalabilir. m tek başına yeterli değildir. Gerçek tarifte satır normalleştirmesi ve LSA/kelime/karakter tekrarları da etkilidir.

TF-IDF burada nadirliğe karşı değil, nadirliği kısmen vurgulayan bir ağırlıklandırmadır. Logaritmanın ondalık üretmesi bir aritmetik hata değildir.

## 4. Daha keskin sonuç: tek kayıtta geçen terim

Kesin rank-k SVD için Z_k=U_k Σ_k V_kᵀ. H=U_k U_kᵀ olsun. Eğer t özellik sütunu sadece i kaydında a değeri taşıyorsa:

    Z[:,t] = a e_i,
    Z_k[:,t] = a H e_i.

Bundan doğrudan:

    ||Z_k[:,t]||² / ||Z[:,t]||² = H_ii,
    1 - ||Z[:,t]-Z_k[:,t]||² / ||Z[:,t]||² = H_ii,
    Z_k[i,t] / Z[i,t] = H_ii.

Diğer kayıtların üzerine yayılan yeniden-oluşturulmuş karesel enerji / a² ise H_ii(1-H_ii). Yani benzersiz terimin etkisi yalnız küçülmez; ortogonal izdüşüm onun dokümanlar üzerindeki görünümünü yayabilir.

H_ii dokümanın sol-altuzay kaldıraç değeridir. Hepsinin toplamı k:

    Σ_i H_ii = k.

Her kayıtta bir ayrı tek-kayıt özelliği bulunan ideal örnekte N=500,k=96 ise ortalama korunma göstergesi 96/500 = 0,192 olur. Bu yüzde19,2 arama başarısı değildir; tek-kayıt sütunlarının karesel enerji/yeniden oluşturma ölçüsüdür. Bazı kayıtlar çok daha iyi, bazıları daha kötü korunabilir.

Önemli koşul: a değişirken H sabit tutulmuştur. Terimin ağırlığını değiştirip SVD'yi yeniden kurmak H'yi de değiştirebilir; "IDF hiçbir zaman işe yaramaz" sonucu çıkmaz.

Genel yaklaşık altuzay: P ortogonal rank-k ve range(P)⊂row(Z) olsun; T=ZP Z⁺. Bir singleton sütunun yeniden oluşturması a T e_i'dir. T idempotent ama genellikle simetrik değildir. R_i=1-relative_SSE için:

    Σ_i R_i = 2k - ||T||_F² ≤ k.

Bu, randomized altuzaylarda eşitlik yerine üst sınır sağlar; varsayımlar kontrol edilmeden kullanılmamalı. İzdüşümden sonraki normalleştirme, merkezleme ve işaret kodlaması ayrı işlemlerdir.

## 5. "Nadir = atılır" için karşıörnek

İki 5×3 matris kuruldu. Bütün satırlar birim uzunluklu ve negatif olmayan sayılardan oluşuyor. Her iki matriste ilk iki özellik dört kayıtta, üçüncü özellik tek kayıtta var. Her iki matris de iki boyuta indiriliyor.

Birinci matriste sık özellikler iki farklı yöne yayılıyor: özdeğerler yaklaşık 2,398 / 1,602 / 1,000. Rank2 üçüncü, nadir ekseni atıyor.

İkinci matriste sık özellikler büyük ölçüde aynı yönde: nadir eksen ilk iki bileşenden biri oluyor ve tam korunuyor. Frekanslar, doküman sayısı ve hedef boyut değişmedi.

Bu, her zaman nadir özellik atılacağı iddiasına karşı kesin bir örnektir. Rarity bir risk göstergesi olabilir; karar toplam ağırlıklı spektral yapıya bağlıdır. Gerçek matrisler ve katsayılar MATH_RESULTS.json'da.

## 6. Gerçek üç arşivde doğrudan özellik kontrolü

Sadece kelime kanalının unigram sütunlarını izledim. Karakter ve LSA kanalları orijinal kodu üretmek için korundu. Her kelime özelliği için:

    R_t = 1 - ||Z[:,t] - (Z V96 V96ᵀ)[:,t]||² / ||Z[:,t]||²

hesaplandı. Kesin SVD için enerji korunmasına eşittir; randomized uygulamada fark doğrudan hesaplandı, eşitlik varsayılmadı. R=1 tam geri oluşturma, R=0 o sütunu sıfır yazmak kadar hatalı geri oluşturma demektir; genel yaklaşık izdüşümde negatif değer de mümkündür.

Aşağıdaki değerler her arşivde terimler üzerindeki MEDYAN; arşivler tek benchmark sonucuna havuzlanmadı:

| Arşiv | Doküman | İncelenen unigram | Sadece 1 kayıtta geçenler R | 20'den fazla kayıtta geçenler R |
|---|---:|---:|---:|---:|
| 001be529 | 514 | 7575 | 0.1525 | 0.5312 |
| 00ca467f | 486 | 7071 | 0.1785 | 0.5469 |
| 0100672e | 486 | 7391 | 0.1895 | 0.5358 |

Seçim, önceden yazılan ilk-üç-leksikografik kuralına göre yapıldı; sonuçlara göre arşiv seçilmedi. Birçok kelime aynı arşivler arasında tekrar eder; 22.037 sayısı benzersiz küresel kelime sayısı değildir.

Bu panelde nadir unigram sütunları daha kötü yeniden oluşturuluyor. Bu ölçüm hipotezin spektral bölümüne doğrudan destek verir; fakat nadir terim kaynaklı gerçek kanıt-sıralaması kaybını tek başına belirlemez. Aynı kelimenin bilgisi karakter ve LSA kanallarına da dağılmıştır. Nadir grupların bağlam ve doküman uzunlukları farklı olabilir. 3 LME arşivi RealTalk'ın 705 sorusuna genellenmiş bir sonuç değildir. Yeni temsil önerisi burada denenmedi.

Dönüşümün aynı olduğuna ilişkin kontroller: toplam 142,656 doküman biti ve 288 sorgu biti önceki önbellekle eşleşti. En büyük C farkı 2.42e-12; farklar sayısal yuvarlama düzeyinde. Son altuzayın ortonormalite ve iz testleri sonuç dosyasında.

## 7. Bir yanlış sıralamanın izdüşümden geldiğini nasıl sınarız?

q sorgu, d+ doğru kanıt, d- yanlış rakip. Saf iç çarpım aşamasında:

    Δ = q·(d+ - d-)
    Δ_parallel = (qP)·((d+ - d-)P)
    Δ_perp = (q(I-P))·((d+ - d-)(I-P))
    Δ = Δ_parallel + Δ_perp.

Δ>0 iken Δ_parallel≤0 ise tam uzayda doğru kayıt önde, izdüşümde geridedir. Bunun için atılan kısmın doğruya sağladığı avantaj Δ_perp≥Δ olur. Bu, belirli bir çiftin sıralama kaybını izdüşüme yerleştirir; yine de bunun belirli bir kelimeden kaynaklandığı ayrı sınanır.

Kosinüste paydalar önemlidir. Önce q,d+,d- birimlenmiş olsun; a_d=(qP)·(dP), r_d=q_perp·d_perp, c_d=||qP|| ||dP||. O zaman:

    full_gap - projected_cosine_gap
      = (r_plus-r_minus)
        + (a_plus-a_plus/c_plus) - (a_minus-a_minus/c_minus).

İlk terim atılan altuzay; kalanlar yeniden normalleştirme etkisidir. Sıfır projeksiyon durumları ayrı kaydedilir. Merkezleme, standartlaştırma ve bitlerin puanlanması bu özdeşliğe dahil değildir; onlar sonraki ayrı karşılaştırmalar olmalı.

Bu iki formül 1.000 rastgele matriste kontrol edildi: en büyük iç-çarpım artık hatası 2.42e-14, kosinüs hatası 9.99e-16.

Nadirlik için kesinleştirici gerçek-veri deney tasarımı: ortak nadir terim bulunan sorularda, aynı soru/kanıt/rakip kimliklerini erken sözcüksel gösterim → geniş Z → ham SVD96 → normalize/center → float_std → qscale boyunca izlemek; query-tokenizer ve OOV kontrolü; tek terim etkisini ölçmek için donmuş kodlayıcı altında silme/değiştirme ve aynı uzunluk/frekanslı ilgisiz-terim kontrolü; karakter ve LSA etkileri dahil. Sonuç-bazlı gruplama tanısaldır, üretimde kullanılacak yönlendirme değildir. FR@3 ana, hit@10 ikincil kalmalı.

## 8. Aynı 96 bit için matematiksel aday: korunma-cezalı altuzay

Bu bir araştırma önerisidir, yeni bir algoritma/öncelik iddiası veya benchmark kazanımı değildir.

P=VVᵀ, VᵀV=I96. R, sadece arşiv metninden belirlenen koruma adayları; w_t≥0. Şu amaç:

    L(P)=||Z(I-P)||_F² + λ Σ_(t∈R) w_t ||(I-P)e_t||²

standart matrisi iyi yaklaşık tutmayı ve seçilmiş sözcüksel yönleri bütünüyle kaybetmeme isteğini birleştirir. D=diag(w), seçilmeyen özelliklerde0 olsun. P²=P simetrik olduğu için:

    L(P) = tr(ZᵀZ) + λ tr(D) - tr(P (ZᵀZ+λD)).

Bu nedenle kesin optimum, ZᵀZ+λD'nin en büyük96 özdeğerine ait altuzaydır. Büyük D×D matrisi açıkça oluşturmak gerekmez; çarpım v → Zᵀ(Zv)+λDv ile matris-free eigensolver kullanılabilir. Bu algoritmik olanak çalıştırılmış performans ölçümü değildir.

Belge kodu yine96 bittir. Fakat tüm96 yeni bir gösterimden üretilir; eski96 bitin aynen korunması iddiası yok. Projektör, merkez/ölçek durumları ve ek kurulum maliyeti sayılmalı. D eğer yalnız fit sırasında kullanılıp sonra standart V saklanırsa ek kalıcı belge kodu gerekmez; yine de bütün kodlayıcı maliyeti ayrı ölçülmeli.

Basit sentetik karşıörnekte λ=1, yalnız nadir üçüncü eksene koruma eklenince aynı rank2 içinde korunma0'dan1'e çıkar. Bunun bedeli, toplam matris yeniden-oluşturma kare hatasının1,000'dan1,602'ye çıkmasıdır. Yani karşılıksız bilgi yaratılmaz; öncelik değişir. Nihai işaret kodu/FR@3 iyileşmesi bu örnekle gösterilmez.

Önemli negatif kontrol: D=I ise bütün özdeğerler aynı sabit kadar kayar; ideal altuzay değişmez. Sayısal dejenerasyon yokken bu kolda büyük bit/başarı farkı çıkması uygulama veya sayısal sorun işareti olur. Aynı solver ve seed ile λ=0 kontrolü, üretim randomized-SVD'siyle algoritma değişikliğini koruma etkisinden ayırmalı.

Nadirlik tek başına ağırlık seçme gerekçesi olamaz: yazım hataları ve alakasız kimlikler de nadir olabilir. Bir sonraki deneyin ilk işi R,w seçimini gold görmeden tanımlamak ve küçük, önceden kayıtlı bir geliştirme kuralını başka arşivlerde sınamak olmalı. Aşırı λ ortak bağlamı bozabilir. Bu aday FR@3'ü gerçek kontroller karşısında iyileştirmezse ilerletilmemeli.

## 9. Kapasite hakkında ne kanıtlanır, ne kanıtlanmaz?

Sağ projektör kaldıraçları ell_t=||Vᵀ e_t||² ve Σ_t ell_t=k. Bütün D özellik yönlerini aynı96boyutta kusursuz koruyamayız. Bu genel geometri kısıtı "eski96 SVD bitinden bir tanesini bile değiştiremeyiz" anlamına gelmez.

10.000 sözcükten rastgele seçilmiş20 sözcüğün tüm olası destek kümelerini kayıpsız saklamak için en az log2 C(10000,20) ≈ 204.65 bit gerekir. Bu yalnız bütün olası kümeleri tam geri alma veya bütün üyelik sorularını hatasız cevaplama için alt sınırdır. Yaklaşık arama, dar veri dağılımı, yalnız birkaç soru ve kaynak metne erişim için doğrudan alt sınır değildir. 96-bit aramanın geliştirilemeyeceğini ispatlamaz.

## 10. Yakın matematiksel literatür

1. Husbands, Simon, Ding. Term norm distribution and its effects on Latent Semantic Indexing. Information Processing & Management41(4),777–787,2005. DOI10.1016/j.ipm.2004.03.006. Yayıncı özeti ve erişilebilir bölümlerde düşük normlu/infrequent terimlerin zayıf katkısını, terim-normalizasyonunu inceliyor. Tam deney tablosu burada indirilmedi; kendi sonuçlarını LLMZIP'e aktarmıyoruz. En doğrudan eski yöntem kontrolü bu.
2. Ando ve Lee. Iterative Residual Rescaling: An Analysis and Generalization of LSI. SIGIR2001,154–162. Yazar sayfası ve arXiv özeti kontrol edildi. Konu dağılımı eşitsizliğinin LSI'ye etkisi ve residual rescaling yaklaşımı. Ayrıntılı uygulama bu oturumda yeniden üretilmedi.
3. Drineas, Magdon-Ismail, Mahoney, Woodruff. Fast Approximation of Matrix Coherence and Statistical Leverage. JMLR13,3475–3506,2012. Kaldıraç skorları için birincil kaynak. Yukarıdaki özdeşlikler standart lineer cebirden bu oturumda türetildi; yeni teorem iddiası yok.
4. Guo vd. Accelerating Large-Scale Inference with Anisotropic Vector Quantization. ICML2020. İç çarpım açısından önemli hataları hedefler. Bizde aynı bit bütçesinde iyileşme garantisi değildir.
5. Zhang. SAKI: Score-Aware Low-Rank Key Indexing for Long-Context KV Retrieval, arXiv2608.03228v1,4 Ağustos2026. Erişilebilir ön baskıda key-reconstruction yerine score-distortion hedefi. KV attention ile bizim metin-arama protokolümüz farklı. Ön baskının bütün ispat ve sonuçlarını bağımsız denetlemedim, performans sayılarını LLMZIP sonucu diye kullanmıyorum.

## 11. Son karar

En güçlü desteklenen ifade: Bu küçük gerçek-LME panelinde tek-kayıt kelime özellikleri rank96 dönüşümünde daha kötü yeniden oluşturuluyor; diğer sohbetin RealTalk tablosu da küçük-kod açığının nadir ortak terim grubunda yoğunlaştığını raporluyor. İkisi birlikte ciddi bir araştırma hipotezi veriyor; bütün soru kaybının nedensel olarak çözüldüğünü göstermiyor.

"12 bayt bölünemez", "bir bit bile verilemez", "tek suçlu SVD kısaltma" hükümleri gönderilen tablolardan çıkmaz. İlk sonraki eylem, nadir terim koşullu gerçek sıralama kayıplarını aşamalara bağlamaktır; ardından mevcut bitleri bölmek yerine aynı96 boyutun koruma hedefini değiştiren adaylar ve normalized-LSI kontrolü ayrı test edilebilir. B8/ASYM/float/BM25 kontrolleri, toplam durum, kurulum ve uçtan uca süre korunur.

Tüm deneyler yerel. Uzak depo/dosya değişmedi. Dondurulmuş görev betiği veya Task4F1/BEAM çalıştırılmadı. Bu paketin ayrı bir dış denetimi yok.
