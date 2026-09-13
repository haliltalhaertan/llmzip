# V52 literatür ve pre-seal tanı tanımları — 2026-09-12

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Yalnızca kaynak/yöntem incelemesi. NOT SEALED / NOT AUTHORIZED.**
Ek görev okundu; bu not kullanıcının sonraki, daha dar talimatını izler. Gerçek
temsil, corpus, gold, sorgu-belge uzaklığı, retrieval sonucu okunmadı/hesaplanmadı;
sentetik ITQ veya Faiss replay de çalıştırılmadı. Prereg, G3 ve main state değişmedi.
Bu ayrı yerel metin lead'in ileride bağlaması içindir; commit/push yapılmadı.

## 1. Doğrulanan birincil kaynaklar ve iddiaların sınırı

| Sabit sürüm | Doğrulanan başlık |
|---|---|
| [2605.17524v2](https://arxiv.org/html/2605.17524v2) | Covariance Structure and Coordinate Heterogeneity Govern Binary Quantization of Contrastive Embeddings |
| [2605.02171v3](https://arxiv.org/html/2605.02171v3) | QuIVer: Rethinking ANN Graph Topology via Training-Free Binary Quantization |
| [2405.12497v1](https://arxiv.org/html/2405.12497v1) | RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search |
| [2411.06158v4](https://arxiv.org/html/2411.06158v4) | Quantization Meets Projection: A Happy Marriage for Approximate k-Nearest Neighbor Search |

**Xiao:** Ek G/Tablo17, 12 veri kümesinde `rho(1-H_sign, delta F_rot)=0.91`,
`rho(CV(sigma), delta F_rot)=0.66` bildiriyor. Hedef F, rastgele çiftlerde BQ
skoru–gerçek iç çarpım Spearman sadakatidir; bizim evidence recall değildir.
Kuramsal çerçeve Gaussian marjinaller/thin-shell varsayımlıdır; ampirik panel
Gaussian olmayan kontrolleri de içerir. §8.4 düşük/yüksek entropi önerir; **sayısal
H<0.75 karar kuralı v2 HTML/PDF'de doğrulanmadı**. Tablo5'te H=0.747 için recall
değişimi negatiftir. Ek metindeki evrensel eşik atfı çıkarılmalıdır.
[§8.4 ve Ek G](https://arxiv.org/html/2605.17524v2#S8.SS4),
[resmî PDF](https://arxiv.org/pdf/2605.17524v2).

**QuIVer:** §3.1/Tablo1: `pos_i=1[x_i>0]`,
`strong_i=1[|x_i|>mean_j |x_j|]`. Aynı işarette ceza0; karşı işarette
zayıf/zayıf1, karışık2, güçlü/güçlü4. §3.3 sorguyu da kendi eşiğiyle kodlar;
asıl sistem graf ve float32 rerank içerir. Dolayısıyla aşağıdaki 48-D kodlayıcı
önerisi “QuIVer-style”dır, bütün QuIVer sistemi değildir.
[§3.1–3.3](https://arxiv.org/html/2605.02171v3#S3.SS1).

**RaBitQ:** Algoritma1 iki önhesaplanmış niceliği açıkça verir:
`r=||o_raw-c||` ve `a=<o_bar,o>`; Teorem3.2'nin iç-çarpım tahmincisi
`<o_bar,q>/a`, yüksek olasılıklı hatası O(D^(-1/2))'dir. Kare uzaklığa dönüşüm
norm çarpanları içerir. Rastgele kod kitabı yön tercihlerini kaldırır; bu, her
veride rotasyonun ortalama kaliteyi iyileştireceği veya iyileştiremeyeceği iddiası
değildir. Makale P matrisini saklar; bütün implementasyonlar için seed-only
çıkarımı yapılamaz. İki float32'nin somut paketlemesi için aşağıdaki Faiss kodu
gerekir. [Algoritma1, §3.1–3.2](https://arxiv.org/html/2405.12497v1#S3).

**2411.06158v4 MRQ:** PCA baş bileşenleriyle artık bileşenin istatistiklerini
birlikte kullanır. §5.3'te en az128 ve ikinin kuvveti boyutla >=%80 varyans
koruma şeklinde ampirik kural vardır; evrensel sabit bütçe bit/boyut optimumu
değildir. Bu kural 96→32 seçimimize doğrudan uygulanamaz; yalnız varyans oranı
bir karşılaştırıcıyı adil veya retrieval açısından kayıpsız ilan ettirmez.
[§3.2, §5.3](https://arxiv.org/html/2411.06158v4#S5.SS3).

**Bizim çıkarımımız:** archive-local TF-IDF/LSA/SVD ve merkezleme, InfoNCE
eğitim alanıyla aynı değildir. Merkezli sürekli simetrik bir koordinatın population
sign entropisi, varyansı ne olursa olsun1'dir. Dolayısıyla yüksek H ile yüksek
varyans heterojenliği birlikte mümkündür. Bu tanılar mekanizma kanıtı veya
literatür doğrulaması değildir. H<0.75 oranı istenirse yalnız **yerel betimsel
kesim** olarak raporlanır; bir tarafında kalmak otomatik rotasyon kararı veya
“literatürle çelişki” kararı doğurmaz. Sonradan karşılaştırma için aynı kodlayıcı,
skor, merkezleme, boyut, domain ve estimandın eşleşmesi gerekir.

## 2. Önerilen pre-seal tanı sözleşmesi — henüz uygulanmadı

Girdi `Y` mevcut merkezli N×96 dizisinin aynısıdır: yeni normalize/whiten/reorder
yok. Dtype, şekil, koordinat sırası ve kaynak/ön işleme hash'i kaydedilir.
NaN/Inf veya N<2 varsa başarısız; veri onarılmaz. İstatistiksel kovaryans için
ortalama çıkarımı, girdinin işaretlerini yeniden merkezleyerek değiştirmek
anlamına gelmez; residual ortalama ayrıca raporlanır. Tüm koordinatlar ve satırlar
tam kullanılır; şu boyutlarda örnekleme gerektiren bir yöntem zorunluluğu yoktur.

**D1 — iki sign tanımı ve sıfır kütlesi:**

```text
p_gt[j] = mean(Y[:,j] > 0)
z[j]    = mean(Y[:,j] == 0)
p_ge[j] = mean(Y[:,j] >= 0) = p_gt[j] + z[j]
h(p)    = -p log2(p) - (1-p) log2(1-p); h(0)=h(1)=0
H_gt    = mean_j h(p_gt[j])
H_ge    = mean_j h(p_ge[j])
```

Her iki H, H farkı, koordinat bazlı p/z, toplam sıfır oranı ve tümü-sıfır
koordinat sayısı raporlanır. `>0` görev/literatür uyumu, `>=0` pipeline uyumu
olarak etiketlenir; pipeline operatörü ileride kod hash'iyle bağlanmalıdır.
IEEE +0/-0 ikisi de sıfırdır; epsilon ile sessiz sıfırlama yapılmaz. H<0.75
oranı iki operatör için ayrı; tam eşitlik ayrı sayılır. Bütün koordinatları
içeren ortalama birincildir; sabitleri atıp paydayı gizlice değiştirme yoktur.

**D2 — heterojenlik:** `sigma[j]=std(Y[:,j],ddof=0)`,
`CV=std_j(sigma,ddof=0)/mean_j(sigma)`. Payda0 ise NA/DEGENERATE; CV=0 yazılmaz.
Sıfır varyans koordinat sayısı ayrıca verilir. Archive özetleri benchmark bazında
eşit archive ağırlığıyla mean, örnek sd(ddof=1), min, max ve geçerli/NA sayısıdır.
Tek archive varsa sd NA. Archive'ların bağımsız örneklem olduğu iddia edilmez.

**D3 — üç farklı nesneyi ayrı adlandır:** `v_j=sigma_j²`, `T=sum(v_j)` için
k∈{16,32,48}:

```text
ordered_first_k = sum(v[0:k]) / T
top_variance_k  = sum(k largest coordinate variances) / T
pca_spectrum_k = sum(k largest eigenvalues of Cov(Y)) / trace(Cov(Y))
```

TOP32 adayının gerçek kaybı `1-ordered_first_32` ile tanımlanır. En yüksek
varyanslı32'yi seçmek farklı bir koordinat seçicisidir; PCA ilk32 ise farklı bir
dönüşümdür. Genel olarak `ordered_first_k <= top_variance_k <= pca_spectrum_k`;
eşitlik varsayılmaz. Eski SVD sırası, sonraki satır normalizasyonu ve merkezleme
sonrasında varyansların aynı sırada veya kovaryansın diagonal olduğunu garanti
etmez. Varyans sıralaması ve ilk32 ile kesişim de raporlanabilir. T=0 ise üçü NA;
negatif özdeğerler için önceden belirlenen sayısal tolerans/kırpma kaydı gerekir.
Özdeğer hesabı yalnız tanıdır; temsili PCA ile yeniden üretme izni değildir.
Korunan varyans reconstruction enerjisidir; semantik/gold önemi değildir.

**D4 — sabit koordinatlarda korelasyonu uydurma:** aktif küme A={j:sigma_j>0}.
R yalnız A üzerinde standart Pearson korelasyonudur. |A|<2 ise off_mass ve
quantile'lar NA. Aksi halde
`off_mass=||R-diag(diag R)||F/||R||F`; median/p95 için sadece i<j tekil çiftler
kullanılır, quantile interpolation=linear sabitlenir. Sabit koordinatların
undefined korelasyonlarını0 yapma, diagonalini1 uydurma, NaN-to-zero kullanma.
Aktif/sabit sayısı ve yakın-sabit sayısı (öneri: sigma<=64*eps_float64*max(sigma),
ayrı duyarlılık etiketi) kaydedilir; yakın-sabitler birincil maskeden sessizce
çıkarılmaz. Bu normalize korelasyon proxy'sidir: Stein-ağırlıklı kovaryans sinyali
veya Xiao'nun covariance off/diagonal oranıyla özdeş değildir. Ek S0/alignment
tanısı istenirse yeni, ayrı tanım gerekir; D4 onu da tek başına doğrulamaz.

## 3. QuIVer-style 2bit×48 için önerilen tam tanım

Öneri olarak önce **mevcut sıralı ilk48** alınır; büyüklük eşiği bu48 üzerinden
hesaplanır. Sorgu da aynı archive transformundan geçer, kendi48 koordinatının
ortalama mutlak değerini kullanır. Corpus ortalaması/codebook veya query-fit yoktur.

```text
tau(x) = sum_{j=1..48}|x_j| / 48
p_j(x) = 1[x_j>0]; m_j(x)=1[|x_j|>tau(x)]
d_Q(x,q) = sum_j 1[p_j(x)!=p_j(q)] * (1+m_j(x)) * (1+m_j(q))
```

Bit sırası, son-byte maskesi ve iki düzlemin paketlenmesi açıkça sabitlenir:
iki48-bit düzlem sıkı paketlenirse6+6=12 B; iki ayrı uint64 yapılırsa16 B olur
ve sınır aşılır. Eşik kodlamadan sonra atılabilir; kalıcı per-vector float
tutulursa bütçeye eklenir. Tam-sıfır vektör için tüm bitler0 ve tau0 olur;
ayrı yok sayma/onarım yapılmaz. Bu formül sıfır uzaklığın vektör eşitliği
gerektirmediği bir sıralama uzaklığıdır; kanıtlanmış strict metric diye sunulmaz.

Xiao Eq.2'deki işaret-çarpım benzerliğini bu uzaklığa otomatik ikame etme:
`S=sum_j w_j sign(x_j)sign(q_j)` ise `d_Q=(sum_j w_j-S)/2` olur;
`sum_j w_j` adayla değişebildiğinden iki sıralama genel olarak eşdeğer değildir.
Bu cebirsel ayrım bizim yöntem kontrolümüzdür. Herhangi bir sorgu skoru burada
hesaplanmadı. Yeni ağırlıklı kol mevcut prereg'e eklenmiş değildir; ayrı lead
dispozisyonu ve sonradan yürütme izni gerektirir.

## 4. Faiss1.15: paylaşılan durum ve iki scalar için kaynak incelemesi

Resmî `facebookresearch/faiss` v1.15.0 etiketi bu incelemede `git ls-remote` ile
`20f14b31a6d54e243a3d1de6ae193fc4c3ec18ed` olarak çözüldü. Bu kaynak incelemesidir;
kurulu wheel'in aynı koddan üretildiğinin veya serializer replay'in doğrulaması
değildir.

- [IndexRaBitQ.h](https://raw.githubusercontent.com/facebookresearch/faiss/v1.15.0/faiss/IndexRaBitQ.h)
  ve [IndexRaBitQ.cpp](https://raw.githubusercontent.com/facebookresearch/faiss/v1.15.0/faiss/IndexRaBitQ.cpp):
  train, d float merkez hesaplar; kodlama merkezli girdiyi quantizer'a verir.
  **Düz sınıfta rastgele rotasyon/seed yoktur.** `qb=4` sorgu quantizasyonudur;
  `centered` de sorgu scalar-quantizer seçeneğidir, genel ön işleme izni değildir.
- [RaBitQuantizer.cpp](https://raw.githubusercontent.com/facebookresearch/faiss/v1.15.0/faiss/impl/RaBitQuantizer.cpp):
  train no-op; bir-bit kod `ceil(d/8)+sizeof(SignBitFactors)`; kod doğrudan
  `x_j-center_j>0` ile yazılır. Decode `dp_multiplier` tüketir.
- [RaBitQUtils.h](https://raw.githubusercontent.com/facebookresearch/faiss/v1.15.0/faiss/impl/RaBitQUtils.h):
  SignBitFactors iki float içerir: `or_minus_c_l2sqr` ve `dp_multiplier`.
  İlki L2'de merkezden norm karesi, IP'de ilave düzeltme içerir; ikincisi
  iç-çarpım çarpanıdır. Ayrı `f_error` yalnız multi-bit genişletmede bulunur.
  İki alanın işlevini belirlemek, plain rotasyonsuz yolun makaledeki tüm
  yüksek-olasılık koşullarını sağladığını kanıtlamaz; eski C4 kaydı değiştirilmedi.
- [index_write.cpp](https://raw.githubusercontent.com/facebookresearch/faiss/v1.15.0/faiss/impl/index_write.cpp),
  write_RaBitQuantizer ve IndexRaBitQ dalı: header, boyut/code_size/metric,
  kod dizisi, merkez dizisi, qb yazılır; gizli4-byte rotasyon seed'i yoktur.
  64-bit size_t/idx_t, 4-byte float/enum/int, 1-byte bool ABI'sinde L2, n=0,
  d32 için kaynak muhasebesi:
  `4 fourcc + 33 header + 20 quantizer fields + 8 code-length + 8 center-length
   + 128 center + 1 qb = 202 B`.
  Bu, mevcut yayımlanmış S0 ile uyumlu bir kaynak hesabıdır, yeni ölçüm değildir.
- Aynı serializer'ın `RandomRotationMatrix` dalı **A matrisini** yazar.
  [VectorTransform.cpp](https://raw.githubusercontent.com/facebookresearch/faiss/v1.15.0/faiss/VectorTransform.cpp)
  Gaussian+QR ile A üretir; ayrı32×32 float32 dönüşüm içeriği4096 B'dir.
  Seed kaydeden HadamardRotation ayrı yapıdır; plain IndexRaBitQ veya dense
  Haar dönüşümüyle özdeş sayılmaz. Dış dönüşüm varsa wrapper da ölçülmelidir.

Sonuç: “4096-byte matrix mi, 4-byte seed mi?” ikiliği eksik; üçüncü olasılık
**bu index'te rotasyon hiç yapılmıyor** ve incelenen düz Faiss yolunda durum budur.
Dolayısıyla tarihsel202-B ölçümü, rotasyonlu teorik RaBitQ32'nin toplam shared
maliyetini ölçmüş sayılmaz. Parent replay'i yinelenmez; gelecekte yöntem kimliği
ve tüm transform zincirinin serializer muhasebesi ayrıca bağlanmalıdır.

Önerilen maliyet sütunları: algorithm-specific fitted state; algorithm-specific
nonfitted state (ör. random matrix); serializer/header; common preprocessing;
per-vector code+auxiliary; toplam shared; effective B/vector; shared/(N*marginal).
SIGN96/SIGN32'nin öğrenilmiş quantizer durumu0 olabilir; BinaryFlat header33 B
ve ortak ön işleme ayrı kalır. QuIVer-style sıfır fitted state, sıfır toplam byte
demek değildir. ITQ96 float32 matris içeriği36,864 B; PQ12×8 codebook içeriği
98,304 B; bunlar headersız analitik bileşenlerdir. Tam serializer sayısı bu görevde
ölçülmedi. Oranlarda N ilgili archive'ın yetkili kaynağından gelmelidir; burada
hiçbir N sütunu açılmadı. D32 SIGN4 B, D48 iki-bit12 B, D32 RaBitQ12 B,
D96 RaBitQ20 B muhasebe açısından farklı noktalardır; eşit marjinal bütçe boyut
confound'unu kaldırmaz.

## 5. ITQ sentetik fizibilite planına gerekli düzeltme

Asıl ITQ hedefi `min_{B∈{-1,+1}^{N×d}, R^TR=I} ||B-YR||F²` ve alternating
sign/orthogonal-Procrustes güncellemeleridir. Makale tüm deneylerde50 iterasyon
kullanır; bunun yakınsama garantisi olmadığını belirtir.
[Gong–Lazebnik, CVPR2011, §2.2](https://slazebni.cs.illinois.edu/publications/cvpr11_small_code.pdf).

**Bizim lineer-cebir kontrolümüz:** iki96×96 tam-rank ortogonal R aynı R^96'yı
gerer. Principal angles hepsi0'dır; YR1/YR2'nin tam kolon uzayları da aynıdır.
Bu ölçü fit stabilitesini ölçmez. Ham Frobenius ise eşdeğer bit permütasyonu ve
işaret çevirimini gereksiz ceza sayar. Önerilen ölçü:

```text
d_SP(R1,R2) = min_{P signed permutation} ||R1-R2 P||F / sqrt(96)
```

Maliyet `|R1^T R2|` üzerinde maksimum ağırlıklı atama ile kolonlar eşleştirilir,
işaretler ilgili iç çarpımdan seçilir. Ham ve düzeltilmiş mesafe ikisi de verilir.
**Genel** ortogonal-Procrustes ile iki R'yi hizalama yapılmaz; o da mesafeyi
trivial olarak0 yapabilir. Sıfır projeksiyonlarda sign tie kuralı sabitlenir;
teorik sign/permutation eşdeğerliğinin floating/zero istisnaları ayrı kaydedilir.

Henüz çalıştırılmayan plan: n={100,250,500,1000}, d96; identity covariance,
önceden sabitlenmiş diagonal heterojenlik ve aynı spektrumun sabit ortogonal
döndürülmüş hali. Veri üretme seed'leri ile initialization seed'leri ayrı literal
paneller; aynı veri üstünde >=20 initialization ile optimizer stabilitesi,
bağımsız veri replikalarıyla örnekleme stabilitesi ayrı. Önceden seçilmiş iterasyon
limiti/tolerans (ör.1000, ardışık5 adım göreli hedef değişimi<=1e-8) yalnız bir
raporlama konvansiyonudur. Nihai hedef, ortogonallik hatası, durma nedeni, max-iter
ulaşımı ve hedefin monotonluk hataları raporlanır.

Haar–Haar null mesafeleri ve ITQ fit mesafeleri aynı d_SP ile karşılaştırılır;
eşit quantization error farklı R'lerle mümkündür. İzotropik Gaussian population'da
ayrıcalıklı yön yoktur: seed'ler arası yön farkı tek başına fit başarısızlığı
değildir. “Hangi n'de random'dan ayırt edilemez?” için null, bağımsız tekrar birimi,
test/eşdeğerlik toleransı ve güç önceden tanımlanmalıdır. Anlamsız p-değeri
eşdeğerlik değildir; tek sentetik panel evrensel minimum n vermez. Synthetic
held-out quantization loss ayrıca düşünülebilir; gerçek retrieval çıkarımı yoktur.

Lead'e öneri: önce bu tanımları ve kaynak düzeltmelerini bağla; ardından ayrı
yetkilendirilecek tanı işinin kapsamını seç. H veya variance oranı üzerinden kol
seçimi, mechanism closure, otomatik program durdurma veya prereg değişikliği yapma.

## 6. Son kaynak envanteri: CSV ile mümkün olan ve eksik kalan

Lead, Drive'da native_heterogeneity.csv'yi bulduğunu ve tam C matrisinin henüz
bulunmadığını bildirdi. Bu incelemede Drive/CSV/cache açılmadı. Yalnız indirilen
`work/representation_source_inventory_20260912/v52_t4c3_coordinate_axis_probe.py`
statik okundu; SHA256:
`8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`.
Bu yerel dosyanın hash'idir; bağımsız seal/manifest eşleşmesi burada kurulmadı.

Kaynak satır37–40: `v=np.var(C,axis=0)` (ddof=0), `occ=(C>=0).mean(axis=0)`.
Satır35 ve131–132: her96'lık vektör kendi koordinat sırasıyla `.17g` ve noktalı
virgül kullanılarak yazılır; yalnız question satırları sıralanır. Şu statik
kabiliyet haritası geçerlidir; CSV'nin bu üreticiye hash/manifest bağlanması,
96 değer/sonluluk/aralık kontrolü ve cohort doğrulaması henüz ayrı iştir:

| Tanı | CSV ile destek durumu |
|---|---|
| D1 `>=0` | occupancy_vector üzerinden sign entropy hesaplanabilir; burada hesaplanmadı. |
| D1 `>0` ve zero mass | Çıkarılamaz. `P(C>=0)` tek başına `P(C=0)` ile `P(C>0)` ayrımını vermez. Sıfır olmadığı varsayılmaz. |
| D2 | sigma=sqrt(variance_vector) ile istenen CV(sigma) hesaplanabilir. Hazır `variance_cv` **CV(variance)**'tır, D2 yerine kullanılmaz. |
| D3 sorted diagonal | En büyük16/32/48 koordinat varyansının payları hesaplanabilir. |
| D3 gerçek first-k | Bu üretici sıralamayı koruduğu için, CSV-producer kimliği doğrulanırsa mevcut ilk16/32/48 oranları da desteklenir. “Yalnız sorted” sınırından daha güçlü olan bu kabiliyet, koordinat sırası kanıtına bağlıdır. |
| D3 eigenspectrum | Diagonal varyanslardan çıkarılamaz; tam kovaryans veya C gerekir. |
| D4 istenen tanım | Çıkarılamaz. Mevcut scalar özetler tam korelasyon matrisi ve median/p95'i belirlemez. |

`normalized_variance_entropy` sign entropy değildir: normalize varyans paylarının
entropisidir. Ayrıca eski `cov_offdiag_frobenius_energy_ratio`, ikinci moment
matrisinin **kare enerji oranı**dır; istenen korelasyon Frobenius oranı değildir.
Kaynak `C.T@C/n` kullanır ve korelasyonun sıfır paydalı girişlerini0 yapar;
`mean_abs_coordinate_correlation` da istenen median/p95 veya aktif-koordinat
sözleşmesinin ikamesi değildir. Bu eski alanları değiştirme veya yeniden etiketleme
yapılmadı.

Satır109 mevcut temsilin normalize(SVD96) ardından archive-mean çıkarımıyla C
olduğunu doğrular. Satır111 cache içine C yanında qC/gold da yazıldığını;
satır225–226 arşivleme listesinin cache dosyalarını içermediğini gösterir.
Bu, cache'in hiçbir yerde mevcut olmadığının kanıtı değildir. Tam C'nin bulunması
veya izinli salt-temsil kaynağının ayrılması hâlâ açık kaynak boşluğudur; bu
not cache unpickle etmez ve temsil yeniden üretmez. T4C3 üreticisinin470 ve
LoCoMo dışlama kapsamı, bu CSV'yi LoCoMo kaynağı yapmaz; iki benchmark'ın
kapsaması ayrı doğrulanmalıdır.

**Yürütme durumu:** Bütün D1–D4 hesapları çalıştırılmadı. G3 final/park edilmeden
tanı çalışmasına başlanmaz; bu not yalnız kaynak ve yöntem uygunluğunu tamamlar.
G3'ün bitmesi tek başına corpus/cache/outcome veya seal izni değildir. Parent'ın
tarihsel Faiss replay'i ayrı devam eder; bu kaynak incelemesi onu tekrar etmez.
