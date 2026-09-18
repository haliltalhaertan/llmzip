[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Çok-adımlı hafıza çağırma — mekanizma beyin fırtınası

**Soru:** *Birinci getirim turunda bulunan hafıza parçasını, ikinci tur için nasıl otomatik ve
çok ucuz bir "ipucu"na dönüştürebiliriz?*

Her mekanizma dört alanla etiketlenir: `MEASURED BASIS` (bu depoda ölçülmüş dayanak, yoksa
"yok"), `HYPOTHESIS` (ölçülmemiş varsayım), `COST`, `FAILURE MODE`.

> **Kural (L-099/L-100):** Literatür bir hipotez üretebilir; yalnız depo/ham çıktı bir proje
> bulgusu üretebilir. Aşağıdaki hiçbir madde bulgu değildir. `MEASURED BASIS` alanı boş olan
> her şey spekülasyondur.

---

## Önce: üç önkoşul ölçüldü

`evidence_path`: `audit_hard_r4/MULTISTEP_PRECONDITIONS.json`, `multistep_preconditions.py`
(sıfır model çağrısı)

### A) Birinci adım çalışıyor mu? **EVET — %93,6**

Çok-adımlı geri çağırma "önce bir kanıtı bul" varsayar. Ölçüm:

| | |
|---|---:|
| Çoklu-gold sorgu | 296 |
| **En az bir gold havuzda** | **277 (%93,6)** |
| Hiçbiri havuzda değil | 19 (%6,4) |

**Bu ailenin önkoşulu sağlanıyor.** 277 sorguda ikinci tur için bir çapa var. Kalan 19 sorgu
hiçbir çok-adımlı yöntemle çözülemez — orada sorun birinci adımda.

### B) Oracle tavan: "ilk kanıtı sorguya ekle" — **KARIŞIK, +38 net**

Oracle deneyi: bulunan gold'un **tam metnini** soruya ekle, kalan gold'ların rank'ı ne oluyor?
Bu, bu ailenin **üst sınırıdır** — gerçek sistem bundan iyi olamaz.

| | |
|---|---:|
| Test edilen kalan-gold | 379 |
| Rank'ı iyileşen | 160 (**%42,2**) |
| Kötüleşen veya aynı | 219 (%57,8) |
| Top-10'a **giren** | 61 |
| Top-10'dan **düşen** | **23** |
| **Net** | **+38** |
| Medyan rank | 4 → 4 (değişmedi) |

**İki şey birden doğru:** mekanizma çalışıyor (61 gold top-10'a giriyor), ama **kendi zararı da
var** (23 gold dışarı düşüyor). Net kazanç 379 üzerinde +38, yani **%10**.

> Bu, bugün öğrenilen "kurtardı/bozdu" kalıbının üçüncü tekrarı: Jev rerank 21/25, RRF füzyonu
> gold eliyor, şimdi sorgu genişletme 61/23. **Her müdahale çift taraflı.**

### C) Kapsam başlığı — **147 gold zaten havuzda ama top-3 dışında**

FR@3 çeşitliliği ödüllendiriyor. Havuzda ≥2 gold olan 215 sorguda:

| | |
|---|---:|
| Havuzdaki gold toplamı | 450 |
| Top-3'e giren | 303 |
| **Havuzda olup top-3 dışında** | **147** |
| Etkilenen sorgu | 114 |

**Bu, sıfır ek getirim gerektiren bir başlık.** Belgeler zaten bulunmuş, yalnız ilk üçe
seçilmemiş.

---

## Mekanizma ailesi 1 — çapadan ipucu çıkarma

### M1. Tam metin ekleme (oracle taban çizgisi)
- `MEASURED BASIS`: yukarıdaki B — net **+38/379**, 61 giren / 23 düşen
- `HYPOTHESIS`: gerçek sistem oracle'ın altında kalır (çapa seçimi hatalı olabilir)
- `COST`: sıfır model çağrısı; ikinci BM25 taraması
- `FAILURE MODE`: uzun çapa metni sorguyu boğuyor → 23 düşüş tam bu

### M2. Yalnız **yüksek-IDF** terimleri ekle
- `MEASURED BASIS`: yok. M1'in düşüş kipinden türetilmiş
- `HYPOTHESIS`: nadir terimler sinyal, sık terimler gürültü; seçici ekleme düşüşü azaltır
- `COST`: sıfır — IDF zaten indekste
- `FAILURE MODE`: nadir terim çapaya özgü olabilir (tek seferlik yazım hatası, ID)

### M3. Yalnız **adlandırılmış varlıklar** (kişi/tarih/yer)
- `MEASURED BASIS`: zayıf — bölüm dağılımı temporal-reasoning 16, multi-session 11 (L-108)
- `HYPOTHESIS`: çoklu-kanıt soruları varlık zinciriyle bağlanıyor ("Ahmet … taşındı" → "Ahmet")
- `COST`: sıfır model (regex/sözlük) veya çok küçük NER
- `FAILURE MODE`: sıfır-örtüşme vakalarında varlık adı zaten soruda var; yeni bilgi yok

### M4. **Fark terimleri**: çapada olup soruda olmayanlar
- `MEASURED BASIS`: yok
- `HYPOTHESIS`: ikinci belgeyi ilkinden ayıran şey, ilkinin **yeni** getirdiği bilgidir
- `COST`: sıfır
- `FAILURE MODE`: çapa gürültülüyse fark terimleri de gürültü

### M5. Soruyu değil, **çapayı** sorgu yap (komşu arama)
- `MEASURED BASIS`: yok
- `HYPOTHESIS`: çoklu kanıt aynı konuşmanın/oturumun parçası olabilir → çapaya benzer belgeler
- `COST`: sıfır ek kodlayıcı — `sign96` çapa vektörü zaten var
- `FAILURE MODE`: konu sürüklenmesi; çapaya benzer ama soruyla ilgisiz belgeler

### M6. **Oturum/konum komşuluğu** (temsil hiç kullanılmadan)
- `MEASURED BASIS`: yok — ama ölçmesi ucuz, `haystack_sessions` yapısı elde
- `HYPOTHESIS`: çoklu kanıt zamansal olarak yakın mesajlarda
- `COST`: **sıfır** — tarama bile yok, indeks komşuluğu
- `FAILURE MODE`: multi-session soruları tanım gereği uzak oturumları birleştiriyor

---

## Mekanizma ailesi 2 — kaç tur, ne zaman dur

### M7. **Koşullu ikinci tur**: yalnız gerektiğinde
- `MEASURED BASIS`: 174/470 sorgu tek gold (L-110) — bunlarda ikinci tur **saf maliyet**
- `HYPOTHESIS`: ucuz bir sınıflandırıcı "tek mi çok mu kanıt" ayrımını yapabilir
- `COST`: sınıflandırıcı başına ~1 çağrı, ama %37 sorguda ikinci turu tamamen atlar
- `FAILURE MODE`: yanlış sınıflandırma; çok-kanıtlıyı tek sanıp kaybetmek

### M8. **Doygunluk durdurması**: yeni tur yeni belge getirmiyorsa dur
- `MEASURED BASIS`: sign96∩BM25 ortalama 4,62/10 örtüşme (L-107) — örtüşme ölçülebilir bir sinyal
- `HYPOTHESIS`: tur çıktısı öncekiyle büyük ölçüde örtüşüyorsa daha fazla tur getirisiz
- `COST`: sıfır — küme karşılaştırması
- `FAILURE MODE`: erken durma; üçüncü belge geç gelebilir

### M9. **Gold sayısı tahmini** ile tur sayısını belirle
- `MEASURED BASIS`: dağılım biliniyor (1:174, 2:228, 3:38, 4:14, 5:10, 6:6)
- `HYPOTHESIS`: soru biçiminden kanıt sayısı kestirilebilir
- `COST`: küçük
- `FAILURE MODE`: dağılım bu veri kümesine özgü; taşınabilirlik yok

---

## Mekanizma ailesi 3 — seçim ve birleştirme (ek getirim yok)

### M10. **Çeşitlilik-farkındalı top-3** (MMR benzeri)
- `MEASURED BASIS`: **en güçlü dayanak** — 147 gold havuzda ama top-3 dışında, 114 sorgu etkileniyor
- `HYPOTHESIS`: ilk üç birbirine çok benzer belgelerle doluyor; çeşitlilik cezası kapsamı artırır
- `COST`: **sıfır ek getirim, sıfır ek model çağrısı** — yalnız seçim kuralı
- `FAILURE MODE`: çeşitlilik uğruna doğru ama benzer ikinci gold'u atmak

### M11. **Ortak-oluşum kümeleme**: aynı oturumdan gelenleri birlikte seç
- `MEASURED BASIS`: yok
- `HYPOTHESIS`: çoklu kanıt kümelenmiş geliyor
- `COST`: sıfır
- `FAILURE MODE`: multi-session'da ters etki

### M12. **Kanıt-tamamlayıcılığı skoru**: "bu belge diğerinin eksiğini kapatıyor mu"
- `MEASURED BASIS`: yok
- `HYPOTHESIS`: yargı modeli çiftleri değerlendirebilir
- `COST`: **yüksek** — çift sayısı kadar çağrı (10 aday → 45 çift)
- `FAILURE MODE`: maliyet patlaması; bugünkü ölçümlerde tek-aday yargısı 5.230 token/sorgu

---

## Mekanizma ailesi 4 — sorgu tarafı (ölçülmedi, sınırlı)

### M13. Ucuz semantik genişletme (kullanıcının 2. hattı)
- `MEASURED BASIS`: sıfır-örtüşme 20/38 kurtarılamaz vakada (L-109)
- `HYPOTHESIS`: küçük bir eşanlamlı/ilişki katmanı sözlüksel boşluğu kapatır
- `COST`: düşük, sorgu başına bir kez
- `FAILURE MODE`: **ölçülemez** — `sign96` tarafında kodlayıcı saklanmadı, yalnız `qC` var;
  sözlüksel tarafta test edilebilir ama asıl boşluk temsil tarafında

### M14. Sorgu **parçalama**: bileşik soruyu alt sorulara böl
- `MEASURED BASIS`: 30 sorgu >3 gold, 24'ü multi-session (L-110)
- `HYPOTHESIS`: "A ve B ne zaman değişti" iki ayrı getirim
- `COST`: bölme başına bir model çağrısı + n× tarama
- `FAILURE MODE`: alt sorular bağlamı kaybeder

---

## Öncelik — ölçülmüş dayanağa göre

| # | mekanizma | dayanak | maliyet | öncelik |
|---|---|---|---|---|
| **M10** | çeşitlilik-farkındalı top-3 | **147 gold, 114 sorgu** | **sıfır** | **1** |
| M2 | yüksek-IDF terim ekleme | M1'in 23 düşüşü | sıfır | 2 |
| M7 | koşullu ikinci tur | 174 tek-gold sorgu | düşük | 3 |
| M1 | tam metin ekleme | net +38/379 | düşük | 4 |
| M5/M6 | çapa-komşuluğu | yok | sıfır | 5 |
| M12 | çift yargısı | yok | **yüksek** | son |

**M10 açık ara birinci görünüyordu** — dayanağı doğrudan ölçülmüş (147 kaçırılmış gold),
maliyeti sıfır, ek getirim gerektirmiyor.

### M10 TEST EDİLDİ — **BAŞARISIZ**

Yazıldıktan hemen sonra koşuldu (MMR, λ=0,7, Jaccard çeşitlilik cezası, 470 sorgu, sıfır model
çağrısı):

| | FR@3 |
|---|---:|
| BM25 top-3 (taban) | **59,93** |
| Çeşitlilik-farkındalı top-3 | **58,74** |
| **Δ** | **−1,19 pp** |

İyileşen 4 sorgu, **kötüleşen 16**, net −12.

**Başlık kazanç değildi.** 147 gold gerçekten havuzda ve top-3 dışında, ama çeşitlilik kuralı
onları içeri almıyor — aksine, ilgili ama benzer gold'ları dışarı itiyor. Tam da uyarıda
yazdığım risk gerçekleşti, üstelik net negatif olarak.

> Bu, bugünün **dördüncü** "kurtardı/bozdu" vakası: Jev rerank 21/25, RRF gold eliyor,
> sorgu genişletme 61/23, çeşitlilik 4/16. Dört müdahalenin dördü de çift taraflı çıktı ve
> üçünde net etki ya negatif ya ayırt edilemez.

**Ders:** *"Havuzda var ama seçilmemiş" bir başlık ölçümüdür — erişilebilir kazanç değil.*
Başlığı kazanca çevirmek için seçim kuralının, kaçırılan gold'u **neden** kaçırdığını bilmesi
gerekir; körlemesine çeşitlilik bu bilgiyi taşımıyor.

Öncelik tablosu bu sonuçla güncellendi: **M10 elendi**, sıradaki M2 (yüksek-IDF terim ekleme).

---

## Ölçülmemiş olan — açıkça

| soru | durum |
|---|---|
| M10 gerçek kazancı | **ölçülmedi** |
| M2–M6 hiçbiri | **ölçülmedi** |
| `sign96` tarafında sorgu genişletme | **ölçülemez** (kodlayıcı saklanmamış) |
| Çok-adımlı mimarinin gecikme/token maliyeti | **ölçülmedi** |
| Bunların ayrılmış sınav verisinde davranışı | **ölçülmedi** — hiçbir pozitif bulgu doğrulanmadı |

`sign96` kodlayıcısının saklanmamış olması ciddi bir sınır: sorgu-tarafı mekanizmaların
(M1–M4, M13) **yalnız sözlüksel yarısı** test edilebilir. Kompakt kod tarafında aynı fikri
denemek için kodlayıcıyı yeniden kurmak gerekir.
