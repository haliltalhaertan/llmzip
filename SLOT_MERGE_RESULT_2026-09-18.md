[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Slot-koruyan iki-tur birleşimi — sonuç

`evidence_path`: `audit_hard_r4/SLOT_MERGE.json`, `slot_merge.py` — **sıfır model çağrısı**

**Soru:** İkinci tur yeni kanıt getirirken birinci turdaki kanıtı **korursak** FR@3 yükseliyor mu?

---

## Sonuç: koruma zararı azaltıyor, ama tabanı geçmiyor

### Tüm sorgular (n=470)

| kol | FR@3 | tabandan | CI95 | |
|---|---:|---:|---|---|
| **taban** (Tur1 top-3) | **59,93** | — | — | |
| replace (L-112 real_M2) | 53,50 | −6,43 | [−8,73, −4,16] | SIG |
| merge_1_2 | 53,50 | −6,43 | [−8,75, −4,16] | SIG |
| merge_2_1 | 57,65 | −2,28 | [−4,03, −0,55] | SIG |
| **rrf_2turn** | **59,10** | −0,82 | [−2,11, +0,44] | ayırt edilemez |
| **anchor_2** | **59,10** | −0,82 | [−2,09, +0,44] | ayırt edilemez |

### Çoklu-gold altküme (n=296) — mekanizmanın hedefi

| kol | FR@3 | tabandan | |
|---|---:|---:|---|
| taban | 53,26 | — | |
| replace | 45,76 | −7,50 | SIG |
| merge_2_1 | 49,98 | −3,28 | SIG |
| rrf_2turn / anchor_2 | 52,29 | −0,97 | ayırt edilemez |

**Beklenen 62–65 gerçekleşmedi.** En iyi koruma kuralı tabanla **eşit** (−0,82, ayırt edilemez).
Koruma, M2'nin −6,43'lük zararını sıfıra yaklaştırıyor — ama **pozitife çeviremiyor**.

---

## Neden: keşif slotu, feda ettiği slottan daha kötü

| slot | gold isabeti |
|---|---:|
| Tur1 rank-3 (feda edilen) | **15,1%** |
| Tur2'nin yeni adayı (keşif slotu) | **10,4%** |

Üçüncü slotu keşfe ayırmak, o slotta **%4,7 puan daha düşük** isabetli bir belge koymak demek.
Mekanizma tam bu yüzden pozitife geçemiyor: bulduğu yeni gold'lar, yerini aldığı eski gold'lardan
daha az.

> Bu, "ikinci tur yeni kanıt buluyor" ifadesini **niceliklendiriyor**: buluyor, ama üçte birden
> az isabetle — ve bu, birinci turun üçüncü adayını feda etmeye değmiyor.

---

## Yapısal bulgu: Tur2'nin birincisi **her zaman** çapa

`merge_1_2` ile `replace` **470/470 sorguda birebir aynı** çıktı. Kontrol ettim — hata değil,
yapısal:

> **Tur2'nin 1. sırası 470/470 sorguda çapanın kendisi.**

Sebep açık: çapanın kendi kelimelerini sorguya ekliyoruz, dolayısıyla çapa kendi genişletilmiş
sorgusunda kaçınılmaz olarak birinci geliyor. Yani "1 slot Tur1 + 2 slot Tur2" kuralı, farkında
olmadan "Tur2 top-3" ile aynı şeyi yapıyor.

Bu, M2'nin neden konu kaymasına yol açtığını da açıklıyor: genişletilmiş sorgu **çapaya doğru**
çekiliyor, tanım gereği.

---

## İki darboğaz — düzeltilmiş ifade

Önceki *"darboğaz bulmada değil, birleştirmede"* ifadem **fazla güçlüydü**. Doğrusu:

| darboğaz | kanıt |
|---|---|
| **1. İkinci kanıtı bulmak** | en iyi yöntem eksik gold'u yalnız **%22,09** vakada buluyor |
| **2. Bozmadan birleştirmek** | koruma zararı sıfırlıyor ama kazanç üretmiyor (−0,82) |

İkisi birden geçerli. Ve şimdi üçüncü bir ölçüm eklendi: **bulunanın kalitesi de yetersiz**
(keşif slotu %10,4 vs feda edilen %15,1).

---

## Hat için sonuç

`Tur1 → M2 genişletme → Tur2` biçimindeki iki-tur mimarisi, **denenen altı birleştirme kuralının
hiçbiriyle** tabanı geçmiyor. Koruyucu kurallar yalnız zararı engelliyor.

**Bu, senin hipotezinin temiz bir testiydi ve olumsuz çıktı.** Öğrenilen şey de tam olarak
öngördüğün gibi: *yeni bulunan ikinci kanıtların sayısı ve kalitesi, ilk turdaki iyi adayları
değiştirmeye değmiyor.*

### Kapanan

- `Tur1 → sözlüksel genişletme → Tur2` ailesi, **altı birleştirme kuralıyla birlikte**
- "Koruyucu birleştirme M2'yi kurtarır" hipotezi

### Kapanmayan

| | durum |
|---|---|
| Üretici LLM ile **gerçek** soru parçalama | denenmedi — Jev yapamıyor (L-113) |
| Çapa **vektörüyle** komşu arama (metin genişletme değil) | ölçülmedi |
| Koşullu ikinci tur (yalnız çoklu-kanıt sorularında) | ölçülmedi |
| Daha geniş slot bütçesi (3 yerine 5) | ölçülmedi |
| `sign96` tarafı | **ölçülemez** — kodlayıcı saklanmamış |

Kritik ayrım: keşif slotunun isabeti (%10,4) **sözlüksel** ikinci tura ait. Anlamsal bir ikinci
tur daha isabetli olabilir — ama L-113 gösterdi ki Jev seçimi de kör genişletmeyi geçmiyor.

---

## Sınırlar

- Tek veri kümesi (LME, n=470), sabit 3-slot bütçe
- Yalnız sözlüksel; `sign96` kodlayıcısı yok
- **Ayrılmış sınav verisi yok** — bugünün tüm ölçümleri gibi keşifsel
- Altı kural denendi; başka birleştirme kuralları olabilir
