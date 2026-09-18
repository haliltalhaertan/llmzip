# LLMZIP — Toplamsal koruma cezası: matematiksel risk ve deney eki

16 Eylül 2026

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

**Kapsam:** Kullanıcının aktardığı diğer-sohbet değerlendirmesini ve önceki `MATEMATIK_INCELEME.md` formüllerini kontrol eden yeni, sınırlı matematik denetimi. Yeni arama benchmarkı çalıştırılmadı. Diğer sohbetin 200 matris/2,78 fark sonuçları burada yeniden üretilmiş sayılmıyor. Aşağıdaki sentetik testler bu oturumda gerçekten çalıştırıldı. Uzak depo veya kaynak dosyalar değiştirilmedi.

## 1. Önceki bulguların doğru kapsamı

- `rho_i=sum_j U[i,j]^2`, `sum_i rho_i=k` kesin kesilmiş SVD'nin tek-kayıt özellikleri için önceki raporda tanımlanan yeniden-oluşturma göstergesine ilişkindir.
- `k/N=96/500=0,192`, tüm doküman satırları üzerindeki uniform kaldıraç ortalamasıdır. Her kayıtta bir ayrı singleton özelliği bulunan ideal durumda bu özellikler için de uniform ortalamadır. Gerçek singleton özellikler dokümanlara eşit dağılmıyorsa, sadece onların ortalamasının 0,192 olması gerekmez.
- Bu bir hit@k/FR@k sınırı veya 96-bit kodlar için evrensel bilgi-kuramsal sınır değildir. Burada 96 sürekli boyut ile sonradan alınan 96 işaret biti ayrılmalıdır.
- `48+48`: 13,20 puan kısaltma + 2,97 puan füzyon = 16,17 puan kayıp. Kısaltma oranı yaklaşık %81,63; füzyon yaklaşık %18,37. Kısaltma bu kolda baskın, tek neden değil. Bu paylar sabitlenmiş ardışık ablasyon farklarıdır; mekanizmalar için evrensel nedensel paylar değildir.

## 2. İki farklı amaç, fakat yenilik kanıtı değil

`G=Z^T Z`. Pozitif diagonal W ile `ZW` üzerinde SVD, `WGW` matrisinin yönlerini kullanır. Toplamsal kol `G+lambda D` kullanır. Genellikle aynı dönüşüm değillerdir. Ancak bir deneyde fark bulunması, literatürde özgünlüğü kanıtlamaz.

Baz matrislerini doğrudan karşılaştırmak da altuzayları karşılaştırmak değildir: `V` ile `VR` ortogonal R için aynı projektörü verir. Küçük testte baz norm farkı 2 iken projektör farkı tam 0'dır. Aynı özgün uzayda ortonormal bazlar karşılaştırılırsa uygun altuzay ölçülerinden biri `||V1V1^T-V2V2^T||_F`'dir. Büyük özellik uzayında projektörleri açıkça oluşturmak yerine çapraz küçük matris kullanılabilir:

`distance^2 = 2k - 2 ||V1^T V2||_F^2`.

Çarpımsal kolda özgün sorgunun haritası `q -> q W Vw`'dir; bu nedenle yalnız Vw ile diğer kolun V'sini karşılaştırmak, farklı koordinat ölçeklerini karıştırabilir. Etkili haritanın altuzayı ve puanlama geometrisi ayrı raporlanmalıdır. Aynı altuzay ayrıca aynı işaret kodlarını garanti etmez.

Toplamsal amaç şu artırılmış matrise SVD uygulamakla eşdeğerdir:

`Z_aug = [ Z ; sqrt(lambda) sqrt(D) ]`,

çünkü `Z_aug^T Z_aug = Z^T Z + lambda D`.

Bu cebirsel kimlik yeni bir bilimsel öncelik iddiası değildir. Yapay satırlar yalnız çözümleyici içindir; DF/IDF, doküman ortalaması, sigma, aday sayısı veya gold eşlemesine gerçek dokümanmış gibi dahil EDİLMEMELİDİR.

## 3. Yeni saptanan risk: koruma terimi boşa bir yön seçebilir

Önceki amaç:

`L(P) = ||Z(I-P)||_F^2 + lambda tr(D(I-P))`, `P=VV^T`, `V^TV=I_k`.

Türetim geçerli: optimum `G+lambda D`'nin ilk k özvektöründedir. Ancak bu amaç, gözlenen arşivin satır uzayı dışındaki yönleri de ödüllendirebilir. `Zv=0` olan bir yön bütün gerçek kayıtlarda sıfır üretir. Sonrasında merkezleme ve işaret alma onu anlamlı bir ayırt edici özelliğe dönüştürmez.

### Kesin karşıörnek

8 kayıt, 4 özellik, 2 boyut. Her satır birim normlu, negatif değer yok. `a=1/sqrt(2)`:

```text
Z = [ a a 0 0 ]
    [ 0 0 1 0 ]  (4 kez)
    [ 0 0 0 1 ]  (3 kez)

D = diag(1,1,0,0), lambda=5, k=2.
```

İlk iki özellik gerçekten nadirdir: yalnız ilk kayıtta birlikte geçerler. Son iki özelliğin doküman frekansı sırasıyla 4 ve 3'tür.

Dört ortonormal yön:

`v_sum=(1,1,0,0)/sqrt(2)`, `v_diff=(1,-1,0,0)/sqrt(2)`, `e3`, `e4`.

Bu bazda:

```text
G              = diag(1,0,4,3)
G + 5D         = diag(6,5,4,3)
```

Standart rank2 çözümü e3,e4'ü seçer: gerçek kayıt enerjileri 4 ve 3.

Ceza eklenince v_sum,v_diff seçilir: gerçek kayıt enerjileri 1 ve **0**. Çünkü `Z v_diff = 0` tam olarak. İki boyut ayrılmıştır fakat gerçek kodlama rankı yalnız 1'dir. Amaç gerçekten düşer (11 -> 7): sorun çözümleyicide değil, yazılan hedefin bu seçime izin vermesindedir.

Bu olasılık SymPy ile tam köklü/tamsayı cebirinde ve NumPy ile sayısal olarak doğrulandı. LLMZIP'in gerçek arşivlerinde bunun yaşandığı gösterilmedi. Her lambda için olacağı da iddia edilmiyor.

## 4. Mevcut projektör optimizasyonuyla etkileşim

Önceki küçük faktörlü projektör fikri `V=Z^T A` varsayımını gerektiriyordu. Yukarıdaki v_diff, row(Z)'ye dik olduğundan bu eşitlik yeni serbest ceza kolunda mümkün değil. Sentetik örnekte rowspace artık normu 1'dir.

Dolayısıyla "koruma cezası + eski projektör hızlandırması" iki kazancın otomatik toplamı değildir. Yeni V için:

`||V - Vr(Vr^T V)||_F`

ölçülmeli; Vr tüm sayısal satır uzayının ortonormal bazıdır.

## 5. Güvenlikli karşılaştırma adayı: gerçek veri uzayıyla sınırla

`Z = Ur Sigma_r Vr^T`, r tam sayısal rank. Yeni V'yi `V=Vr R`, `R^TR=I_k` ile sınırlandırınca çözüm:

`H = Sigma_r^2 + lambda Vr^T D Vr`,

`R = H'nin en büyük k özvektörü`.

Bu **kısıtlı farklı bir problemdir**, serbest problemin birebir aynısı değildir. Exact nullspace yönü seçemez; buna karşılık FR@3 kazancını, iyi merkezlenmiş varyansı veya iyi bit dağılımını garanti etmez.

Önemli: **Vr yalnız eski ilk96 yön değildir.** Atılan bilgiyi geri kazanma imkânı için tüm veri satır uzayı (veya açıkça tanımlanmış daha geniş bir aday altuzayı) kullanılmalıdır. Eski96 içinde dönmek, eski96'nın tamamen dışındaki bilgiyi geri getiremez.

Sentetik örnekte bu kısıtlı aday v_sum,e3 seçer: gerçek enerji 1 ve 4, kodlama rankı2, yeniden-oluşturma hatası3. Serbest kolun amaç değeri7, kısıtlı kolunki8; farklı optimumlar oldukları açıkça görünür.

Bu kısıtla tekrar `V=Z^T A` yazılabilir: `A=Ur Sigma_r^{-1} R`. Küçük tekil değerler için sayısal koşulluluk/rank toleransı kontrolü gerekir. Tam rank SVD'sini hesaplamak ve saklamak bedelsiz değildir; bu formüller hız/bellek başarısı diye sunulmaz.

200 rastgele düşük-rank/geniş matris testinde artırılmış Gram kimliği, amaç-iz kimliği, D=I negatif kontrolü, kısıtlı çözüm ve dual faktörleştirme sınandı. En büyük artık 1,91e-13'ün altında; asıl karşıörnek ayrıca tam cebirle doğrulandı.

## 6. IDF üssü, terim normu normalizasyonunun yerine geçmez

IDF yalnız doküman frekansına bağlıdır. Terim normu ise sayısal ağırlıklara ve uygulandığı gösterime de bağlıdır. İki terim aynı iki dokümanda `[1,1,0]` ve `[10,1,0]` değerleriyle bulunsun: IDF'leri aynı, normları sqrt(2) ve sqrt(101)'dir. `idf^p` onlara aynı ek katsayıyı verir; ters norm farklı katsayılar verir.

Husbands–Simon–Ding'in yayıncı metni özellikle LSI'deki projekte terim normlarını tartışıyor. Bu yüzden sadece IDF üssü test edilerek söz konusu yöntemin sınandığı söylenmemeli. Tam uygulama/protokol kaydı olmadan eşdeğerlik kabul edilmez.

ITQ ortogonal dönüşümü korunan sürekli uzayda geometriyi koruyabilir, fakat sonraki işaret nicemlemesi bilgi kayıplıdır. ITQ'nun quantization-loss kazanımı FR@3 kazanımını otomatik sağlamaz. Sorgu ölçeklemesi döndürmeden sonra yeniden hesaplanıyorsa geometriyi ayrıca değiştirebilir.

## 7. Diğer deneye eklenmesi önerilen kapılar

1. **Özgünlük etiketi:** "Projede farklı amaç fonksiyonu adayı"; henüz yeni algoritma veya başarı iddiası yok.
2. **Kontroller:** Aynı çözümleyicide lambda=0, D=I, eigen-gap ve solver residual; ayrıca değişmemiş üretim randomized SVD kontrolü. Baz işareti/rotasyonu ile altuzay farkını ayır. Lambda'nın ölçeğini, D ağırlıklarını, token seçimini ve uygulama sırasını sonuçlardan önce yaz.
3. **Veri taşıma kontrolü:** Seçilen yönlerin `||Zv_j||^2`, merkezlenmiş varyansı, etkin rank, rowspace artığı; işaret sonrası sabit/yinelenen bit sayıları. Serbest ve kısıtlı ceza kollarını ayrı etiketle.
4. **Sıralama tanısı:** Aynı soru/gold/rakip çiftinde tam uzay -> izdüşüm -> normalize/center -> float_std -> qscale. Gold sadece değerlendirme/tanı için; koruma ağırlığını seçim için kullanma. Sıralama farkını korunmuş/atılmış bileşene ayır; nedensellik iddiasını yalnız sınanan çifte/koşula bağla.
5. **Kalite ve maliyet:** FR@3 ana, hit@10 ikincil; her benchmark ayrı. Eski ASYM/B8, güçlü float ve BM25 kontrolleri korunur. Solver/TF-IDF, merkez/ölçek, tüm matrisler ve gerçek query yolu maliyete dahil. Ayarlar bağımsız geliştirme arşivlerinde seçilir; mevcut benchmarklar tekrar görülmüş keşif verisi olarak etiketlenir.
6. **Durdurma:** Sıfır/izotropik kontroller başarısızsa veya kodlayıcı işlevsel bilgi yerine sayısal gürültü üretiyorsa kalite başlığı yazma; hatayı kaydet. Sentetik risk görülmesi tek başına tüm yöntemi reddetme gerekçesi değil; gerçek ölçümü gerektirir.

## 8. Kaynaklar ve yeniden üretim

Önceki proje kaynağı: `LLMZIP_NADIRLIK_MATEMATIK_2026-09-16/MATEMATIK_INCELEME.md`, özellikle §§4,8,9.

Birincil dış kaynaklar (matematiksel karşıörnek ve bu oturum sonuçlarının kaynağı değiller):
- Drineas vd., Fast Approximation of Matrix Coherence and Statistical Leverage, JMLR2012: https://www.jmlr.org/papers/v13/drineas12a.html
- Husbands, Simon, Ding, Term norm distribution and its effects on Latent Semantic Indexing, IP&M2005: https://www.sciencedirect.com/science/article/pii/S0306457304000378
- Ando ve Lee, Iterative Residual Rescaling, SIGIR2001: https://www.cs.cornell.edu/home/llee/papers/ando-lee-sigir01.home.html
- Gong vd., ITQ, yazar kurumu sayfası: https://europe.naverlabs.com/research/publications/iterative-quantization-a-procrustean-approach-to-learning-binary-codes-for-large-scale-image-retrieval/

Çalıştırılan kod: `verify_penalty.py` (NumPy) ve `verify_exact.py` (SymPy).
Çıktılar: `RESULTS.json`, `EXACT_PROOF_CHECK.json`, `STDOUT.txt`.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_penalty.py
python verify_exact.py
```

Yukarıdaki testler dış bağımsız denetim değildir. Sonraki gerçek benchmark için önceden bir performans sonucu uydurulmadı.
