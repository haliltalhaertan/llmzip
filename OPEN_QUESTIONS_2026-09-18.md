[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LLMZIP — açık sorular ve her birinin cevabı ne işe yarar

Tarih: 2026-09-18. Kaynak: yayın paketi, dört denetim turu, süreklilik defteri (L-001…L-098),
2026-09-18 literatür taraması.

**Kapsam uyarısı.** Twelve-byte TF-IDF/SVD-işaret hattı KAPALI. Aşağıdaki sorular o kararı
yeniden açmaz. Proje geneli DUR kararı verilmemiştir; diğer hatlar açıktır.

Her madde: soru → **kaynak** (nerede açık olduğu yazılı) → cevaplanırsa ne değişir → maliyet.

---

## A. Kapatılması zorunlu olanlar (borç)

Bunlar yeni bilgi üretmez; hâlihazırda yayınlanmış sayıların geçerliliğini belirler.

### A1. LoCoMo altın otoritesi çelişkili
`FINAL_STATE.md:129-131` — n=1531 mi 1535 mi; 156 denetlenmiş düzeltme hiç uygulanmadı.
Defter, 156 düzeltmenin bağlı kohortu birebir ürettiğini doğruluyor (1535 = 1535, sıfır sapma).
**Cevaplanırsa:** LoCoMo'ya dayanan her sayı tartışılabilir olmaktan çıkar. Şu an "her LoCoMo
rakamı itiraz edilebilir" durumdayız — ki bu, çapraz-kıyaslama replikasyon iddiasının yarısı.
**Maliyet:** düşük. Düzeltme dosyası mevcut, uygulanması ve yeniden hesap.
**Getiri/maliyet: en yüksek.**

### A2. T1 ve merdiven için soru-bazlı veri saklanmıyor
`decision_tests.py:156-191` veriyi üretip atıyor; `ladder.py` yalnız arşiv toplamı saklıyor.
**Cevaplanırsa:** manşet farkların güven aralığı olur. Şu an −3,83 pp bir nokta tahmini;
arşiv düzeyinde bootstrap ile [−5,67, −2,06] elde edildi ama bu zayıf bir ikame.
**Maliyet:** düşük — tek bir yeniden koşu, kalıcılık ekleyerek.

### A3. C3'ün gerektirdiği eşit-bütçeli kontrol yok
Hakem sözleşmesi BM25 ilk-aşama + aynı yeniden sıralayıcı + aynı aday bütçesi istiyor; saklanmamış.
**Cevaplanırsa:** C3 kapısı gerçekten uygulanmış olur. Şu an "kural yazıldığı gibi
yürütülmedi" demek zorundayız.
**Maliyet:** orta.

### A4. LME kanal ablasyonu 322/470'te duruyor
`FINAL_STATE.md:127-128` — "bedeli ödendi, bitir ve dondur; kararı etkilemez."
**Cevaplanırsa:** yarım kalmış bir iş kapanır. Bilimsel getirisi düşük, hijyen değeri yüksek.
**Maliyet:** düşük (hesap zaten başlamış).

---

## B. Gerçekten açık mekanizma soruları (yeni bilgi)

2026-09-18 literatür taraması bu bölümü daralttı. İki kaynak merkezi:
Xiao 2026 (arXiv 2605.17524, *Covariance Structure and Coordinate Heterogeneity Govern Binary
Quantization of Contrastive Embeddings*) ve QuIVer (arXiv 2605.02171).

> **İki çekince — her ikisi de doğrulandı, 2026-09-18.**
> (1) Bu iki makale **bağımsız değil**: her ikisinin de birinci yazarı Wenxuan Xiao ve
> heterogeneity makalesi QuIVer'ı kendi kaynağı olarak alıntılıyor. "İki bağımsız kaynak aynı
> yöne işaret ediyor" çerçevesi geçersizdir.
> (2) Xiao'nun teorisi açıkça **InfoNCE ile eğitilmiş kontrastif gömmeler** için kurulmuş;
> QuIVer'ın sınırı "cosine-native contrastive-learning embeddings". Bizim temsilimiz
> TF-IDF → LSA → SVD: kontrastif değil, sinirsel değil. Teori bize **test edilecek hipotez ve
> ölçülecek değişken listesi** verir — kurulmuş açıklama vermez.

## B0. Birleştirici hipotez (B1–B5'in üstündeki tek soru)

B bölümündeki maddeler bağımsız değil. Altlarında tek bir daha büyük soru olabilir:

> **Bir arşivin spektral geometrisi, kompakt ikili getirimde hangi boyutun, hangi skorlayıcının
> ve hangi dönüşüm stratejisinin başarılı olacağını belirliyor mu?**

*(Formülasyon 2026-09-18 tarihli dış incelemeden alındı; kendi B1+B3+C4 maddelerimi tek çatı
altında topladığı için benimkinden iyi.)*

Doğruysa, bu hattın en değerli sonucu "12 baytlık getirim" değil, şu olur:
**arşiv spektral geometrisi → optimum kompakt getirim tasarımı.**
Bu, tek bir kodlama yönteminden çok daha genel ve savunulabilir bir sonuçtur.

**Ama önce ölçülmeli, iddia edilmemeli.** Hipotezin cazibesi kanıtı değildir; bu programın
kronik hatası tam olarak budur. B1 ve C4 bu hipotezin en ucuz iki testidir.

### B1. Sabit kodlayıcıda genişlik etkisi neden daha büyük?
R4: INDEP 96→384 **+19,86 pp**, uyarlamalıda **+8,22 pp**. Literatürde doğrudan açıklaması yok.
**Hipotez:** korpus uyarlaması ilk 96 yönü hedef arşive hizalıyor, sonraki yönlerin marjinal
değeri düşüyor; sabit kodlayıcıda ilk yönler kötü hizalı, ek boyutlar kaybı telafi ediyor.
**Test:** uyarlamalı ve sabit koşulda ilk 96 / sonraki 96 / sonraki 192 bileşenin
altın-vs-altın-olmayan ayrım katkısını ayrı ölç. Sabit durumda kuyruk bloğun katkısı büyürse
mekanizma desteklenir.
**Cevaplanırsa:** "ne kadar genişlik gerekir" sorusu taşınabilirlik rejimine bağlanır —
konuşlandırma kararı için doğrudan kullanılır. Ayrıca bu, hattın sağ çıkan tek olumlu
bulgusunun *nedenini* verir.
**Maliyet:** düşük-orta. Mevcut önbellekler yeterli, yeni veri gerekmez.
**Bu listedeki en iyi yeni deney.**

### B2. Spektral gruplama neden rastgele gruplamadan iyi?
Aynı koordinat kümesi + aynı grup boyutları + yalnız üyelik spektral vs rastgele — bu tam
müdahaleye doğrudan eş çalışma taramada çıkmadı.
**Ara değişkenler:** grup-içi özdeğer oranı, nicemleme hatası, ikili kosinüs bozulması,
altın/altın-olmayan marj korunumu, işaret entropisi.
**Cevaplanırsa:** sonucu bir ara değişken açıklarsa, retrieval koşmadan gruplama tasarlanabilir.
**Maliyet:** orta.

### B3. Yüksek-k'da düşüşün mekanizması bilinmiyor
`LADDER_REALTALK.md` geri çekme kutusu: rank overflow **değil** (T3 çürüttü), σ-bölmesi de
**değil** (`sym` σ'ya bölmüyor, yine de 53,88 → 48,71 düşüyor).
**Cevaplanırsa:** iki geri çekilmiş açıklamanın yerine doğrusu konur. Şu an literatüre
"bilmiyoruz" diyoruz — dürüst ama eksik.
**Maliyet:** orta. Xiao'nun değişken listesi (etkin rank, özdeğer sönümü, varyans CV/Gini,
anizotropi, işaret dengesi) kör taramayı gereksiz kılıyor.

### B4. Sorguyu ikilileştirmek neden veri kümesine göre değişiyor?
Defter L-097 sonu: PerLTQA'da **−4,43 pp**, RealTalk'ta faydalı; sebep bilinmiyor.
**Cevaplanırsa:** sorgu tarafı bütçesi belirlenebilir hale gelir.
**Maliyet:** düşük — ölçüm zaten var, açıklama yok.

### B5. ITQ hedefi iyileşirken getirim neden kötüleşiyor?
**Literatür bunu büyük ölçüde açıklıyor:** ITQ nicemleme hatasını minimize eder, biz sıralama
isteriz — farklı hedefler; hashing yazınında bilinen ayrışma.
**Kalan gerçek soru:** ITQ hangi sıralama-ilgili yapıyı siliyor? Xiao rotasyonun tam da
heterojenlikteki bilgi taşıyan yapıyı yok edebileceğini söylüyor.
**Test:** ITQ öncesi/sonrası koordinat heterojenliği değişimi ↔ getirim deltası korelasyonu.
**Cevaplanırsa:** "rotasyon zarar verir" gözlemi mekanizmaya bağlanır.
**Maliyet:** düşük. **Yeni ITQ taraması yapılmamalı** — literatür kalabalık.

---

## C. Sistem/konuşlandırma soruları (en yüksek pratik değer)

### C1. Gerçek Pareto sınırı nerede?
Bu turun en büyük yapısal hatası: tek bir "bayt/belge" rakamıyla sistem karşılaştırmak.
ANN-Benchmarks standardı: recall, QPS, indeks boyutu, kurulum süresi, gecikme yüzdelikleri.
**Cevaplanırsa:** "12 bayt" anlatısının yerine savunulabilir bir sistem iddiası geçer:
toplam RAM × kurulum maliyeti × gecikme × getirim kalitesi birlikte.
**Maliyet:** orta-yüksek. **Değeri en yüksek sistem sorusu.**

### C2. Kompakt kodun doğru rolü ne?
**Literatür burada net cevap veriyor.** BPR (ACL 2021, doğrulandı) ikili indeksi *aday üretimi*
için kullanıp sürekli temsili yeniden sıralamaya bırakıyor: 65 GB → 2 GB, doğruluk korunuyor.
Tencent BEBR üretimde %30–50 indeks maliyeti tasarrufu bildiriyor.
**Bunun anlamı:** ikili kodun doğal rolü **BM25'in yerine geçmek değil**, büyük vektör
indeksinin maliyetini düşürmek. Bu tur yanlış rakiple dövüşmüş olabilir.
**Cevaplanırsa:** hattın kapanma gerekçesi değişmez ama *yeniden çerçevelenir* — "kaybedilmiş
fikir" değil, "yanlış karşılaştırmaya sokulmuş fikir".
**Maliyet:** düşük (yeniden çerçeveleme) / orta (yeni deney).

### C3. Toplam bütçede bit mi, kodlayıcı durumu mu?
Kod kolu sorgu anında iki TF-IDF sözlüğü, iki SVD matrisi, `mu`, `sigma` istiyor — hiçbiri
12/24/48 B'ye dahil değil. Sabit bütçe farklı kapasite türleri arasında nasıl bölünmeli?
**Cevaplanırsa:** bütçe tahsisi ölçülebilir bir tasarım problemi olur.
**Maliyet:** orta.

### C4. Arşiv teşhisi: taramadan önce hangi temsil?
Arşiv başına yalnız etkin rank, varyans heterojenliği, özdeğer sönümü, anizotropi, sözlük
seyrekliği hesapla → `en iyi genişlik`, `en iyi skorlayıcı`, `beklenen FR@3` tahmin edilebilir mi?
**Cevaplanırsa:** projenin en pratik yeni sonucu olabilir — *"sweep yapmadan hangi kompakt
temsilin kullanılacağını öngören teşhis."* Ayrıca B1/B3'ü de besler.
**Maliyet:** orta. **Uyarı:** Xiao'nun ölçek yasası kontrastif gömmelerde kuruldu; bizim
rejime taşınması bir hipotezdir.

---

## D. Metodolojik açık

### D1. Hiçbir yerde ayrılmış sınav verisi yok
Yapılandırmalar, alt gruplar ve mekanizmalar, değerlendirildikleri veriye bakılarak seçildi.
**Negatif sonuç buna dayanıklı** (çok optimize edip yine kaybetmek anlamlıdır); pozitif ve
mekanistik bulgular dondurulup görülmemiş veride bir kez test edilene kadar keşifseldir.
**Cevaplanırsa:** B ve C bölümündeki her bulgu yayınlanabilir statüye geçer.
**Maliyet:** yüksek — ama B/C'den herhangi biri iddia edilecekse **zorunlu**.

### D2. Bu rejim literatürde ölçülmemiş
`FINAL_STATE.md:132-134`: ≤12–16 B/belge kodlardan altın Hit@10 bildiren kaynak bulunamadı.
Arşiv başına birkaç yüz belge rejimi incelenmemiş görünüyor.
**Cevaplanırsa (yani biz ölçersek):** sonuçlarımız başkasınınkiyle karşılaştırılabilir hale
gelir. Şu an kimseyle kıyaslanamıyoruz.

---

## E. Diğer hatlar (bu turda ne çalıştırıldı ne okundu)

### E1. Task 4F1 — mühürlü doğrulayıcı deney
Defter: **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**. V2–V6 adayları
bağımsız denetimlerce bloklandı; koşucu V4'ten beri bayt-özdeş ve denetim onaylı.
**Cevabı literatürden gelemez** — kendi önceden mühürlenmiş hipotezimizin testi.
**Cevaplanırsa:** projenin tek **doğrulayıcı** (keşifsel değil) sonucu olur. Bu, D1'in
yapısal çözümüdür.
**Maliyet:** yüksek; ayrıca çalıştırma yetkisi bir sahip kararıdır.

### E2. KV/inverse hattı — iki ayrı durum, karıştırılmamalı
Denetim `audit_hard_r2/ROUND_A_10roles_1114/07_kv_inverse/REPORT.md` bu hattı okudu ve iki
satırı **ayırdı** (rapor §F5, satır 92-102):

- **KV-predictor hattı:** gerçek `DynamicCache` tüketimi (install + stepwise + poison gate 8/8)
  *kodu okunarak* kanıtlanmış — ama **yeniden çalıştırılmamış** (`re-execution NOT RUN`).
- **Inverse ledger hattı:** `kv_continuation.py` tam-dizi ileri geçişle logit yeniden hesaplıyor;
  **o dosyada stepwise `DynamicCache` adımlaması yok**. "Cache" ifadesi burada fazla iddialı.
  Ayrıca generic-4bit karşılaştırıcısı 24 pozisyonun hepsini nicemlerken defter kolları yalnız
  16 önek pozisyonunu yamalıyor → **karşılaştırma eşleşmemiş, kıyas iddiası tutulmalı**.

Ve her ikisi için rapor şunu yazıyor:
> *"No resident memory savings are demonstrated anywhere; both lines disclose this honestly
> and the byte arithmetic checks out exactly."*

**Açık soru bu yüzden keskin:** düzeltilmiş matematik **gerçek stepwise `DynamicCache`** üzerinde
çalışıyor mu, ve çalıştığında **yerleşik bellekte** ölçülebilir tasarruf veriyor mu? Şu anki
kanıt "bayt aritmetiği doğru ama hiçbir yerde yerleşik tasarruf gösterilmedi" diyor.

**Cevaplanırsa:** hat ya getirimden bağımsız ikinci gerçek koldur, ya da temiz kapanır. İkisi de
değerli; belirsiz kalması değersiz.

**Devam edilecekse asgari protokol** (2026 literatürü çıtayı yükseltti — CompressKV, RocketKV,
KVComp gerçek runtime'da ölçüyor; arXiv 2607.11942 eşleşmiş-bütçe denetimi sorgu görünürlüğünün
yöntem sıralamasını değiştirdiğini gösteriyor): gerçek DynamicCache, sorgu-duyarlı **ve**
sorgu-bağımsız, eşleşmiş bellek bütçesi, önemsiz son-pencere temel çizgisi, güncel güçlü
baseline, kalite, tepe bellek, gecikme.
**Maliyet:** yüksek.

### E3. ~~B1 (kodlayıcı/projektör durum azaltma)~~ — **GERİ ÇEKİLDİ 2026-09-18**

> Bu madde, adı `B1` olan bir kodlayıcı-durum azaltma tekniği varmış gibi yazılmıştı.
> **Böyle bir teknik bu depoda yok.** `B1`, 4F1 hattındaki bir bütünlük kusurunun adı; iddianın
> sayıları (`10.13 GB`, `5.43 GB`) hiçbir dalda bulunamadı. Ayrıntı: bölüm G1.
>
> Altta yatan **meşru** soru — kodlayıcı/projektör durumu küçültülebilir mi, ve tam sistem
> Pareto'su nedir — bu belgede zaten **C1** (gerçek Pareto sınırı) ve **C3** (bit mi kodlayıcı
> durumu mu) olarak, kendi kanıtıyla kayıtlıdır. Oraya bakınız.

### E4. Depolama/rank sertifikası
Doğrudan eş çalışma taramada çıkmadı. **Önce matematiksel tanımı netleşmeli** — şu an
soru olarak bile tam biçimlenmemiş.

---

## F. Kaynak ayırmamayı önerdiklerim

| Hat | Neden |
|---|---|
| Yeni ITQ taraması | Literatür kalabalık; asıl soru B5'e indirgendi |
| Yeni residual-bit taraması | RBE ve Tencent BEBR olgun; bizim +0,1–0,5 pp zayıf |
| Genel "daha fazla bit iyi mi" | Bilinen; asıl soru B1 (neden rejime göre değişiyor) |
| Yeni 2-bit işaret+büyüklük algoritması | RaBitQ/QuIVer alanı doldurmuş |
| BM25'i ultra-kompakt sözlüksel kodla geçmeye çalışmak | Bu turda kaybedildi; C2 zaten rolün yanlış olduğunu söylüyor |

---

## G. Var olmayan bulgular (yanlış pozitif kaydı)

Bir dış inceleme 2026-09-18'de 47 soruluk bir liste üretti. Listenin bir kısmı **bu depoda
hiç yapılmamış deneylerin mekanizmasını** soruyordu. Aynı tuzağa tekrar düşülmemesi için
kayda geçiriliyor.

Yöntem: her isim `main` üzerinde ve 40+ uzak dalda `git grep` ile arandı.

| İddia edilen bulgu | Gerçek durum |
|---|---|
| **Spectral grouping** (spektral vs rastgele üyelik) | **Hiçbir yerde yok** — `main`'de 0 dosya, hiçbir dalda 0 isabet. Böyle bir deney yapılmadı. Dış liste bunun üzerine **dört soru** kurmuş ve ikisini "en güçlü dar yenilik adayı" / "ana bilimsel katkıya dönüşebilir" diye etiketlemişti. **Var olmayan bir bulgunun mekanizması sorulamaz.** |
| **NanoBEIR / BRIGHT / BIRCO "karma sonuçlarımız"** | Bu isimler yalnız `research_top10_comparison_2026_09_16/inventory/literature/` altındaki **literatür envanterinde** geçiyor — başkalarının çalışmalarının listesi. Bizim ölçümümüz değil. |
| **Rank/storage certificate** | Kaynak uygulama yok; yalnız denetim metinlerinde kavram olarak anılıyor. Soru olarak bile henüz biçimlenmemiş (bkz. E4). |
| **"B1 = kodlayıcı-durum azaltma, 10,13 GB → 5,43 GB"** | **AD ÇAKIŞMASI — aşağıya bakınız.** Bu depoda `B1`, 4F1 yürütme hattındaki bir **bütünlük kusurunun** adıdır (B1/B2/B3), kodlayıcı-durum azaltma tekniğinin değil. `5.43 GB` ve `10.13 GB` dizgileri hiçbir dalda **0 isabet** veriyor. |
| KV / inverse hattı | **Gerçek** — kod ve denetim raporu mevcut (bkz. E2). |
| Dense / residual hattı | **Gerçek** — `audit_hard_r2/ROUND_A_10roles_1114/06_dense_residual/` ve `bench/sign96-micro-residual-2026-09-14` dalı. |

### G1. `B1` ad çakışması — bu listenin kendi hatası

**Bu belgenin ilk sürümünde E3 maddesi "B1 (kodlayıcı/projektör durum azaltma)" diyordu.
Yanlıştı ve kaynağı gösterilmemişti.** Doğrulama:

- Depoda `B1`, **4F1 yürütme adaylarındaki bütünlük kusurlarının** adı: *"4F1 V2 audit: BLOCKED;
  synthetic B1/B2/B3 integrity defects reproduced"*, *"B1, B2 and B3 were established repaired by
  the V4 audit"* (`START_HERE_V52_4F1.md`, `docs/CONTINUITY_LEDGER.md`). Ayrıca defter, bu
  alıştırmaların **sentetik fikstürlerle** yapıldığını, gerçek BEAM verisiyle hiç yapılmadığını
  kaydediyor.
- Kodlayıcı-durum azaltma anlamındaki `B1` iddiasının sayıları (`10.13 GB`, `5.43 GB`) **hiçbir
  dalda bulunamadı**. Bu rakamlar bir dış değerlendirme metninden geldi, depodan değil.

**Sonuç:** "B1 sonrası RAM/gecikme/Pareto" soruları, *adı B1 olan gerçek bir teknik varmış gibi*
sorulamaz. Altta yatan gerçek soru — **kodlayıcı/projektör durumunun küçültülüp küçültülemeyeceği
ve tam sistem Pareto'su** — meşrudur ve bu belgede zaten **C1 ve C3** olarak, kendi kanıtıyla
kayıtlıdır. E3 maddesi bu yüzden geri çekildi.

Aynı isim iki ayrı şeye verildiğinde, iki ayrı şey tek bulgu sanılıyor. Bu, yayın paketinde
"C1" için de yaşandı (bkz. B7 düzeltmesi, `EXTERNAL_AUDIT3_RESPONSE.md`) — **bu programda
tekrarlayan bir hata sınıfı.**

**Ders:** bir soru listesi, dayandığı bulguların var olduğunu **varsayar**. Liste ne kadar
ikna edici yazılırsa yazılsın, her maddenin kaynağı önce depoda aranmalıdır. Bu belgedeki her
madde bu şekilde doğrulandı; kaynağı gösterilemeyen madde listeye alınmadı veya geri çekildi.

---

## H. Bu listeye madde ekleme kuralı (zorunlu)

Bölüm G'deki iki hata (spectral grouping, `B1` ad çakışması) aynı zincirden doğdu:
*literatürde ilginç bir fikir görüldü → projede o fikrin bulgusu varmış gibi davranıldı.*
Zinciri kesmek için bu listeye giren her madde dört alanı **zorunlu** taşır:

| Alan | Anlamı |
|---|---|
| `evidence_path` | Bu soruyu doğuran dosya/commit — depoda gösterilebilir olmalı |
| `observed_fact` | Gerçekten **ölçülmüş** olan ne |
| `open_question` | **Ölçülmemiş** kısım ne |
| `status` | `REAL` / `HYPOTHESIS` / `LITERATURE-ONLY` / `BLOCKED` |

Ve üstündeki tek ilke:

> **Literatür bir hipotez üretebilir; yalnızca depo ve ham çıktı bir proje bulgusu üretebilir.**

`status` alanı olmayan veya `evidence_path`'i depoda bulunamayan madde listeye girmez.
`LITERATURE-ONLY` bir maddenin proje bulgusu olarak alıntılanması yasaktır.

**Neden bu kadar katı:** bu programın en pahalı hataları yanlış aritmetikten çıkmadı. Birbirine
yakın üç doğru şeyin birleştirilip **hiç yapılmamış dördüncü bir "bulgu"** üretilmesinden çıktı.
Spectral grouping tam olarak bunun örneğidir: ikili hashleme literatürü gerçek, spektral yöntemler
gerçek, bizim gruplama kodumuz gerçek — ama "spektral vs rastgele gruplama deneyimiz" hiç
var olmadı.

---

### C5. Aday üretimi + semantik yeniden sıralama
`status`: **PARTIALLY TESTED / CURRENTLY LOW PRIORITY**

`evidence_path`: `research_top10_comparison_2026_09_16/coordinator/DECISION_TESTS.json` (`T2_rerank`),
`coordinator/LADDER.json`, `REPORT.md:307-310`

`observed_fact`: İki aşamalı mimari **zaten sınandı** — kompakt kod aday üretir, pahalı bir
operatör yeniden sıralar. LME'de (n=470, FR@3) sınanan 96-bit aday üreticiler yeniden sıralama
sonrası **BM25'i tek başına geçemedi**: `asym96_bm25` 57,65 vs `BM25_full` 58,03 (−0,38);
`qscale96_bm25` 57,70 (−0,33); hiçbiri C3 kapısını geçmiyor, güven aralıkları sıfırı içeriyor.
RealTalk'ta aday tavanı da düşük: 96-bit qscale Hit@10 **49,65** vs hakem-birincil BM25 **61,70**.
100 aday derinliğinde havuz kalitesi CODE 75,60 | BM25 78,16 | RRF(k=60) **81,28**.
Ayrıca `REPORT.md:307-310`: iki skorlayıcının soru başına en iyisini seçen oracle RealTalk'ta
~%55'te doyuyor (ikisi birden 328/705 soruyu kaçırıyor) — açık **temsilsel**, sıralama-düzeni
sorunu değil.

`open_question`: **Semantik bir yeniden sıralayıcı 96-bit aday havuzunda hiç denenmedi.**
Doğrulandı: `T2_rerank` operatörleri yalnızca `bm25` ve `rrf60`; depoda `jev`/`typesafe`/
`LLM rerank` için sıfır isabet (`cross-encoder` geçen 5 dosyanın hepsi **literatür envanteri**,
bizim ölçümümüz değil). BM25 sözlüksel sinyal kullanır; semantik bir yeniden sıralayıcı aday
metnini doğrudan değerlendirebilir. Dolayısıyla T2'nin olumsuz sonucu, **semantik yeniden
sıralamanın değer katamayacağını kendi başına kurmaz.**

`Yeniden açma koşulları` (en az biri):
1. Kompakt aday üretici, BM25'e göre **belirgin biçimde daha iyi** toplam RAM/CPU/gecikme dengesi sunuyorsa;
2. BM25'ten **tamamlayıcı** adaylar getirip hibrit aday geri çağırmasını yükseltiyorsa;
3. Semantik yeniden sıralayıcı, sözlüksel BM25 yeniden sıralamasının **düzeltemediği** sıralama hatalarını gösterilebilir şekilde düzeltiyorsa;
4. Konuşlandırma rejimi geleneksel bir ters indeks **tutamıyorsa**.

`Yeniden açılırsa zorunlu karşılaştırma`: `96-bit → Jev`, `BM25 → Jev` ve tercihen `hibrit → Jev`,
**eşleşmiş aday derinliğinde**; raporlanacaklar: aday geri çağırma, nihai getirim kalitesi, yerel
CPU, yerleşik bellek, gecikme, Jev token sayısı, 1000 sorgu başına toplam maliyet.

> **Terminoloji uyarısı:** PerLTQA'daki %75,68 gibi değerler için "her arşive özel uydurma"
> denmez. Arşiv-başına uyarlama, **indekslenmiş-korpus protokolünün parçasıdır** (sorgu ve altın
> etiketler fit'e girmez). Sabit kodlayıcıda düşmesi **taşınabilirlik/genelleme** sınırını ölçer,
> sızıntıyı değil. Bkz. B bölümü başındaki çekinceler.

---

### C5. Aday üretimi + semantik yeniden sıralama
`status`: **DIRECTLY TESTED — SEMANTIC RERANK BENEFIT CONFIRMED (SIG);
MATCHED BM25+JEV COMPARISON STATISTICALLY INDISTINGUISHABLE (CI95 spans zero)**

`evidence_path`: `audit_hard_r4/JEV_RERANK_FINDING.md`, `JEV_RERANK_PILOT.json`,
`JEV_RERANK_BM25.json`, `jev_rerank_pilot.py`, `jev_rerank_bm25.py` (denetim dalı);
önceki sözlüksel sonuç: `coordinator/DECISION_TESTS.json` (`T2_rerank`)

İki ayrı sonuç, karıştırılmamalı:

#### (a) Semantik yeniden sıralama mekanizması — **SUPPORTED**

`observed_fact`: LME, n=470, aynı `jev-1.13.0`. Kod havuzuna semantik yeniden sıralama
**+16,06 pp FR@3** katıyor; Hit@1 **+22,98 pp**, eşleştirilmiş bootstrap **CI95
[+17,45, +28,51]** (20.000 tekrar, seed 20260918), sıfırı dışlıyor. `sign96` kolunda
**152 sorgu düzeldi, 44 bozuldu** (net +108).

> *Not: daha önce raporladığım "600 düzeltti / 169 bozdu" **dört kod kolunun toplamıdır**
> (470 sorgu × 4 kol = 1880 satır), tek kola ait değildir. Kol başına: sign96 152/44,
> float_raw 158/38, asym 155/38, float_std 135/49.*

Mekanizma öngörüldüğü gibi: kod doğru belgeyi %86,4 oranında top-10'a sokuyor ama ilk sıraya
koyamıyor (H@1 43,83 → **66,81**).

**Sözlükselden farkı belirleyici:** BM25 yeniden sıralaması aynı havuzlara hiçbir şey katmamıştı
(`asym96_bm25` −0,38; `qscale96_bm25` −0,33; `float_raw32_bm25` −0,27). Sözlüksel sonucu
semantik olana genellemek **yanlıştı** ve bu genelleme geri çekildi.

#### (b) Eşleşmiş sistem karşılaştırması — **SUPERIORITY NOT ESTABLISHED; EQUIVALENCE ALSO NOT ESTABLISHED**

`evidence_path`: `audit_hard_r4/MATCHED_CI.json`, `matched_ci.py` (denetim dalı)

`observed_fact`: Aynı Jev her iki havuza uygulandı; yalnız iki karar kolu yeniden koşuldu ve
soru-bazlı sonuçlar **kalıcı saklandı** (n=470, 9.400 yargı, 0 hata).

| | tavan H@10 | Hit@1 | FR@3 |
|---|---:|---:|---:|
| sign96 + Jev | 86,38 | 66,60 | 70,37 |
| BM25 + Jev | 87,87 | 68,51 | 72,48 |

Eşleştirilmiş bootstrap (20.000 tekrar, seed 20260918):

| ölçüt | Δ | CI95 |
|---|---:|---|
| FR@3 | **−2,10 pp** | **[−4,97, +0,70]** |
| Hit@1 | −1,92 pp | [−5,53, +1,70] |

**İki ayrı olumsuz sonuç — karıştırılmamalı:**

1. **`BM25+Jev` üstünlüğü GÖSTERİLEMEDİ.** Aralık sıfırı kapsıyor.
2. **Eşdeğerlik de GÖSTERİLEMEDİ.** Bu, önceden belirlenmiş bir eşdeğerlik marjı gerektirir.
   Mevcut veriyle hesaplandı (`per_query`'den, ek API çağrısı olmadan):

   | marj | eşdeğerlik |
   |---|---|
   | ±1 pp | gösterilemez |
   | ±2 pp | **gösterilemez** |
   | ±3 pp | gösterilemez |
   | ±5 pp | gösterilir |

   Eşdeğerlik iddiası için gereken minimum marj **±4,97 pp** — makul bir getirim marjından
   çok geniş. Bootstrap dağılımının **%92,9'u sıfırın altında**, yani eğilim BM25 lehine.

> **Dil uyarısı:** Bu sonuç için "aynı kefede" / "eşdeğer" denmez. Doğru ifade:
> *"bu deneyde BM25+Jev'in ölçülebilir üstünlüğü gösterilemedi; eşdeğerlik de gösterilmedi."*
> Koordinatör bir kez "aynı istatistiksel kefeye giriyor" yazdı; bu **geri çekildi**.

`open_question`: Kalite ekseninde karar verilemiyor → soru **sistem maliyetine** kayıyor:
aynı getirim kalitesi civarında, sign96 sistemi BM25'e kıyasla ne kadar RAM/CPU/gecikme
tasarrufu sağlıyor? Bu, yeniden açma koşulu (1) ve **ölçülmedi**.

#### Yeniden sıralayıcı deterministik değil

Aynı girdiyle iki koşu farklı sonuç verdi. Aday havuzları **birebir aynı** (tavan 86,38 / 87,87
her iki koşuda özdeş), dolayısıyla fark yalnız Jev skorlarından:

| | koşu 1 | koşu 2 |
|---|---:|---:|
| sign96 FR@3 | 70,66 | 70,37 |
| BM25 FR@3 | 71,87 | 72,48 |
| **Δ** | **−1,21** | **−2,10** |

**Metodolojik sonuç:** Mevcut bootstrap yalnız **sorgu örnekleme** belirsizliğini ölçüyor;
Jev'in koşudan koşuya stokastikliğini içermiyor. Yayın düzeyi bir sonuç için:

> toplam belirsizlik = sorgu varyasyonu + model koşu varyasyonu

#### Koşu varyansı ölçüldü — `run_variance.py`, sabit 120 soru, 4 bağımsız tekrar

`evidence_path`: `audit_hard_r4/RUN_VARIANCE.json`

| tekrar | sign96 FR@3 | BM25 FR@3 | Δ |
|---|---:|---:|---:|
| 1 | 73,32 | 68,25 | +5,07 |
| 2 | 73,32 | 68,53 | +4,79 |
| 3 | 73,32 | 67,56 | +5,76 |
| 4 | 73,04 | 67,94 | +5,10 |

**Koşu-arası SD = 0,413 pp.** Kollar eşit kararsız değil: `sign96` SD 0,139 — `BM25` SD 0,417,
yani **üç kat daha oynak**. Sebebi mekanik: sign96 havuzu saklanmış ve sabit; BM25 havuzu her
koşuda yeniden kuruluyor, dolayısıyla sıralama bağları farklı çözülebiliyor.

Toplam belirsizlik:

| bileşen | SD |
|---|---:|
| sorgu örnekleme (n=470 bootstrap) | 1,441 pp |
| model koşu varyasyonu | 0,413 pp |
| **toplam** √(q²+r²) | **1,499 pp** |

Koşu varyansı aralığı yalnız **%4** genişletiyor: düzeltilmiş CI95 ≈ **[−5,04, +0,83]**
(ham [−4,97, +0,70]). **Sonuç değişmiyor** — üstünlük de eşdeğerlik de gösterilemiyor.

#### Önemli: sonuç veri altkümesine güçlü biçimde bağlı

Varyans koşusu ilk 120 soruda **Δ = +5,18 pp** verdi — tam koşudaki **−2,10**'un **tersi işaret**.

Bu model kararsızlığı **değil**: aynı 120 soru tam koşunun kendi verisinden çekildiğinde de
**+4,38 pp** çıkıyor.

**Dosya sırasında dilimler** (her biri n=120):

| dilim | Δ |
|---|---:|
| 0–119 | **+4,38** |
| 120–239 | −5,29 |
| 240–359 | −2,96 |
| 360–469 | −4,76 |

Rastgele 120'lik örnekler (2000 tekrar) ortalama −2,03, %95 aralığı **[−6,60, +2,72]**.
İlk-120'nin +4,38 değeri bu aralığın **dışında** → gerçek bir sıra etkisi, rastgele örnekleme
dalgalanması değil.

#### H1/H2/H3 — 13,7 pp heterojenlik parçalandı (sıfır yeni model çağrısı)

`evidence_path`: `audit_hard_r4/H123_RESULTS.json`, `h123_decompose.py`

**Hipotezler analizden ÖNCE donduruldu** (dış değerlendirme, 2026-09-18) — post-hoc tarama
koruması. Yalnız bu üçü test edildi.

##### H1 — bölüm etkisi aday havuzu farkıyla açıklanıyor: **GÜÇLÜ DESTEK**

| bölüm | n | Δ FR@3 | sign H@10 | BM25 H@10 | havuz farkı |
|---|---:|---:|---:|---:|---:|
| single-session-preference | 30 | −8,33 | 50,00 | 56,67 | −6,67 |
| temporal-reasoning | 127 | −5,49 | 81,89 | 85,04 | −3,15 |
| single-session-user | 64 | −4,69 | 90,62 | 95,31 | −4,69 |
| multi-session | 121 | −1,58 | 85,95 | 86,78 | −0,83 |
| knowledge-update | 72 | +2,08 | 98,61 | 97,22 | +1,39 |
| single-session-assistant | 56 | +5,36 | 96,43 | 92,86 | +3,57 |

Korelasyon: bölüm düzeyi **r = +0,982** (r²=0,96), sorgu düzeyi **r = +0,720** (r²=0,52).
Sıralama birebir aynı — **Δ tamamen havuz farkını takip ediyor.**

##### H2 — sözlüksel örtüşme farkı açıklıyor: **REDDEDİLDİ**

| ölçüm | r |
|---|---:|
| ham kelime örtüşmesi ↔ Δ | **+0,021** |
| IDF-ağırlıklı örtüşme ↔ Δ | **−0,003** |

Dörtlük dilimlerde de örüntü yok (Δ: −1,99 / −5,03 / −0,71 / −0,70).

> **Koordinatörün hipotezi çürütüldü.** *"Sözlüksel eşleşmenin güçlü olduğu yerde BM25, olmadığı
> yerde kompakt kod kazanıyor"* yazmıştım — **veri bunu desteklemiyor**, korelasyon sıfır.
> Geri çekildi.

##### H3 — her iki havuzda gold varken fark kayboluyor: **GÜÇLÜ DESTEK**

| grup | n | % | Δ FR@3 |
|---|---:|---:|---:|
| her ikisinde | 387 | 82,3 | **−0,08** |
| yalnız sign96'da | 19 | 4,0 | +61,40 |
| yalnız BM25'te | 26 | 5,5 | −81,73 |
| hiçbirinde | 38 | 8,1 | 0,00 |

Tavan eşitlendiğinde: sign+Jev **82,45** vs BM25+Jev **82,53** → **Δ = −0,08 pp**.

**Farkın %96'sı aday üretiminden geliyor, yeniden sıralamadan değil.** İki havuzun aynı belgeyi
içerdiği 387 sorguda Jev her iki havuzda **aynı** performansı gösteriyor. Sorun Jev değil.

##### Yan bulgu: gerçek tamamlayıcılık

| havuz | tavan H@10 |
|---|---:|
| sign96 | 86,38 |
| BM25 | 87,87 |
| **birleşim (hibrit)** | **91,91** |

19 sorguda gold **yalnız sign96'da**, 26 sorguda **yalnız BM25'te**. Hibrit havuz BM25 üzerine
**+4,04 pp** tavan kazandırıyor.

**Bu, yeniden açma koşulu (2)'nin doğrudan karşılanmasıdır:** kompakt kod BM25'in kaçırdığı
tamamlayıcı adaylar getiriyor.

##### Ama sabit bütçede füzyon işe yaramıyor — **ÖLÇÜLDÜ, OLUMSUZ**

`evidence_path`: `audit_hard_r4/FUSION_DEPTH.json`, `fusion_depth.py` (sıfır model çağrısı)

Union tavanı 91,91 ama **ortalama 15,4 aday** demek — Jev maliyeti ~%50 artar. Asıl soru:
`a+b=10` bütçesinde (tekrarsız, en fazla 10 aday) tavanın ne kadarı korunur?

| sign96 | BM25 | ort. havuz | kapsam | union'dan |
|---:|---:|---:|---:|---:|
| 0 | 10 | 10,00 | 87,87 | −4,04 |
| **1** | **9** | **9,15** | **88,30** | **−3,61** |
| 2 | 8 | 8,42 | 88,30 | −3,61 |
| 5 | 5 | 7,39 | 87,23 | −4,68 |
| 10 | 0 | 10,00 | 86,38 | −5,53 |

**En iyi sabit-bütçe füzyonu (sign1+bm25₉) yalnız +0,43 pp getiriyor** — tek başına BM25'in
87,87'sine karşı 88,30. Union'ın +4,04 puanlık kazancının **yalnız %11'i** korunuyor.

Sebep mekanik: tekrarsız birleştirme havuzu **küçültüyor** (ortalama 7,4–9,2 aday), çünkü iki
yöntem büyük ölçüde aynı belgeleri buluyor. Derinlik kırpıldığında tamamlayıcı belgeler zaten
listenin altında kalıyor.

Daha geniş havuzlar kazancı geri getiriyor ama maliyetle birlikte:

| yapılandırma | ort. havuz | kapsam |
|---|---:|---:|
| sign7+bm25₇ (cap 14) | 10,5 | 90,00 |
| sign5+bm25₁₀ (cap 15) | 11,7 | 90,43 |
| sign10+bm25₁₀ (cap 20) | 15,4 | **91,91** |

**Sonuç:** tamamlayıcılık gerçek ama **ucuz değil**. +4 puanlık tavan kazancı için aday sayısını
~%50 artırmak gerekiyor; sabit bütçede kazanç %11'e iniyor. Hibrit havuz + Jev ölçülmedi ve
bu tabloya göre **öncelikli değil**.

> **Metodolojik not:** İlk füzyon koşusu BM25 tavanını 87,23 verdi (diğer koşularda 87,87).
> Sebep: `text_of` bu betikte metni 1200 karakterde **kesmiyordu**. Aynı deneyin iki farklı
> sayısı — düzeltildi ve kaynağa not düşüldü. Paylaşılan yardımcı fonksiyonlar betikler arası
> birebir aynı olmalı.

Ulaşılamaz: 38 sorgu (%8,1) hiçbir havuzda gold içermiyor; hiçbir yeniden sıralayıcı bunları
kurtaramaz.

> **Ama sıra etkisini bölüm karışımı AÇIKLAMIYOR.** Tam-veri bölüm Δ'ları ilk-120'nin bölüm
> ağırlıklarıyla birleştirildiğinde tahmin **−1,45 pp**; gerçek değer **+4,38 pp**. Yani
> 6,48 puanlık farkın yalnız ~0,65'i kompozisyondan geliyor, **+5,83 puanı bölüm-içi** ve
> **sebebi bilinmiyor**. Koordinatör bir kez "işaret dönmesinin büyük kısmı bölüm karışımı"
> yazdı; bu **doğrulanmadı ve geri çekildi**.

**Sonuçları:**
- `−2,10 pp` yalnızca **LME'nin tamamı** için geçerlidir;
- Alt-küme seçilerek raporlanan herhangi bir sayı, bu programın daha önce düzelttiği
  "10/30 arşiv sonucunu tüm veri kümesi gibi sunmak" hatasının aynısı olur;
- Açık soru: bölüm-içi sıra etkisinin kaynağı nedir (arşiv boyutu? kaynak dosya?).

#### Ölçülen maliyet (kol başına, düzeltilmiş)

| hat | token / sorgu / kol |
|---|---:|
| `sign96 → Jev` | **~5.234** |
| `BM25 → Jev` | **~5.245** |

> *Not: daha önce verdiğim "~20.900 token/sorgu" **dört kolun toplamıdır**; tek kolun maliyeti
> gibi sunmak yanlış olurdu.*

#### Kayda değer ama fazla okunmamalı

`sign96` **12 baytlık işaret yükü** ile, `float_std`'nin **1536 baytlık float yükü** ile aynı
sonucu veriyor (70,66 vs 70,71).

> **Bu yalnızca belge yükü karşılaştırmasıdır.** Toplam kodlayıcı/indeks RAM'i eşitlenmiş
> **değildir**. Eski 12-bayt hatasını yeniden üretmemek için bu ayrım her alıntıda korunur.

#### Yeniden açma koşullarından ikisi artık canlı

- **(1)** daha iyi toplam RAM/CPU/gecikme dengesi — 12 B yük vs ters indeks, **ölçülmedi**;
- **(4)** ters indeks tutulamayan konuşlandırma — orada 12 B + reranker, BM25 + reranker'a
  1,21 puan farkla rakip (aralık beklemede).

Sonraki adım bu iki koşulu ölçmek; yeni bir getirim yöntemi aramak değil.

#### Bu bulgunun kanıtlamadıkları

Tek veri kümesi (yalnız LME); BM25 bu pilotta yeniden kuruldu (hakem birincil yapılandırması,
textbook k1=1,2 b=0,75, frozen tokenizer) çünkü LME için BM25 top-10 saklanmamıştı — yayınlanmış
BM25 kolunun birebir kopyası değildir; ayrılmış sınav verisi yok, dolayısıyla keşifseldir.

> **Terminoloji uyarısı:** PerLTQA'daki %75,68 gibi değerler için "her arşive özel uydurma"
> denmez. Arşiv-başına uyarlama, **indekslenmiş-korpus protokolünün parçasıdır** (sorgu ve altın
> etiketler fit'e girmez). Sabit kodlayıcıda düşmesi **taşınabilirlik/genelleme** sınırını ölçer,
> sızıntıyı değil.

---

## Öncelik sırası

| # | Madde | Neden burada |
|---|---|---|
| 1 | **A1** LoCoMo altın | Ucuz; yayınlanmış sayıların yarısını kurtarır |
| 2 | **B1** sabit-vs-uyarlamalı genişlik | Literatürde açıklaması yok; mevcut veriyle test edilir |
| 3 | **C4** arşiv teşhisi | En pratik yeni sonuç adayı; B1/B3'ü besler |
| 4 | **A2** soru-bazlı kalıcılık | Ucuz; her manşete aralık kazandırır |
| 5 | **C1** tam Pareto | En değerli sistem sorusu; "12 bayt" anlatısının yerine geçer |
| 6 | **D1** ayrılmış sınav | 2/3/5'ten biri iddia edilecekse zorunlu |
| 7 | **E1** 4F1 | Tek doğrulayıcı sonuç; sahip kararı |

**Not:** 1–4 mevcut veriyle, yeni veri toplamadan yapılabilir. 5–7 gerçek yatırımdır.

---

*Bu liste kaynaklardan grep ile çıkarıldı, hafızadan yazılmadı. Her maddenin nerede açık
olduğu yazılıdır. Literatür iddiaları 2026-09-18'de arXiv/ACL üzerinde doğrulandı; iki
çekince (aynı yazar, alan uyuşmazlığı) B bölümünün başında kayıtlıdır.*
