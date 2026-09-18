[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Eşleşmiş sistem maliyeti — RAM / CPU / gecikme

`evidence_path`: `audit_hard_r4/SYSTEM_COST.json`, `system_cost.py` — **sıfır model çağrısı**

Gün boyu "ölçülmedi" kalan son kaldıraç. Karar artık kalite ekseninde verilemiyor
(L-107 ayırt edilemez, L-115 router erişilemez), dolayısıyla **maliyet belirleyici**.

40 arşiv, medyan ~484 belge, 5 tekrar, `perf_counter`.

---

## Sonuç: sign96 her eksende daha pahalı

| | BM25 | sign96 | oran |
|---|---:|---:|---:|
| **indeks RAM** | 2.600,7 KB | **5.141,9 KB** | **1,98×** |
| — yalnız kodlar | — | 5,7 KB | 0,002× |
| — **kodlayıcı** | — | **5.136,1 KB** | |
| **sorgu gecikmesi** | 0,471 ms | **2,943 ms** | **6,25×** |
| — yalnız tarama | — | 0,103 ms | 0,219× |
| — **sorgu kodlama** | — | **2,847 ms** | |
| **indeks kurma** | 0,033 s | **0,494 s** | **15,1×** |

---

## Kritik ayrım: "12 bayt" iddiası doğru ama yanıltıcı

**Kod matrisi gerçekten çok küçük.** 5,7 KB, BM25 indeksinin **0,002 katı** — yani 500 kat daha az.
Sırf tarama da **4,6 kat daha hızlı** (0,103 ms vs 0,471 ms).

**Ama bu, sistemin tamamı değil.** Sorgu zamanında `sign96`'nın kodlayıcıya ihtiyacı var
(TF-IDF sözlüğü → SVD bileşenleri) ve o:

| bileşen | RAM |
|---|---:|
| kodlar (12 B × 484 belge) | 5,7 KB |
| **kodlayıcı** | **5.136,1 KB** |
| | **%99,9'u kodlayıcı** |

Aynı şey gecikmede:

| bileşen | süre |
|---|---:|
| tarama | 0,103 ms |
| **sorgu kodlama** | **2,847 ms** |
| | **%96,5'i kodlama** |

> **Bu tam olarak L-098'de geri çekilen hatanın kök sebebidir.** "12 bayt" **belge yükü** için
> doğru; toplam sistem için yanlış. Kodlayıcı, kod matrisinden **900 kat büyük** ve gün boyu
> ölçülemedi çünkü **depoda saklanmamıştı** — burada yeniden kurulup açıkça sayıldı.

---

## Karar tablosu — üç kaldıraç da kapandı

| kaldıraç | sonuç |
|---|---|
| Kalite (eşleşmiş) | **ayırt edilemez** (Δ FR@3 −2,10, CI95 [−4,97, +0,70]) |
| Routing | tavan +5,49 pp **ama erişilemez** (dört model negatif) |
| **Maliyet** | **sign96 her eksende pahalı: 1,98× RAM, 6,25× gecikme, 15,1× kurma** |

Yeniden açma koşulu (1) — *"belirgin daha iyi RAM/CPU/gecikme dengesi"* — **karşılanmadı**.
Tersi ölçüldü.

---

## Yine de kapanmayan: kodlayıcı paylaşılabilir mi?

Ölçülen kurulum **arşiv başına kodlayıcı** varsayıyor (bu projenin korpus-uyarlamalı protokolü).
Ama:

- **Sabit/paylaşılan kodlayıcı** senaryosunda maliyet arşiv sayısına bölünür. 100 arşivde
  kodlayıcı RAM'i arşiv başına 51 KB'a iner ve tablo **tersine dönebilir**.
- Bunun bedeli biliniyor: sabit kodlayıcı, korpus-uyarlamalı olandan **ciddi ölçüde kötü**
  (RealTalk k=96: 49,65 → 20,00, yani −29,65 pp — L-102 kayıtlı).
- Yani "ucuz" ile "iyi" arasındaki takas **zaten ölçülmüş** ve sabit kodlayıcı tarafı çok kötü.

**Ölçülmedi:** çok-arşivli konuşlanmada paylaşılan kodlayıcının gerçek amortisman eğrisi ve
o rejimde kalitenin ne olduğu. İkisi birlikte ölçülmeden "ters dönebilir" bir hipotezdir.

---

## Sınırlar

- Tek makine (Windows, tek çekirdek Python), üretim dağıtımı değil
- BM25 saf Python; C/Rust bir implementasyon **daha da hızlı** olur — yani oran BM25 lehine
  muhafazakâr
- `sklearn` TF-IDF + TruncatedSVD kullanıldı; orijinal kodlayıcı farklı olabilir
  (saklanmadığı için doğrulanamaz)
- 40 arşiv, medyan 484 belge; çok büyük korpuslarda tarama maliyeti doğrusal artar,
  kodlayıcı sabit kalır → oran değişir
- **Ayrılmış sınav verisi yok**
