[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Rol Geometrisi Ölçümü — Rapor (TR)

**BEYAN EDİLMİŞ YENİDEN-UYARLAMA (declared re-fit):** Bu rapor, dondurulmuş üretim yapıtının geri kazanımı değildir; gerçek derlem üzerinde temsil hattının yeniden uyarlanmasından okunan tanımlayıcı geometri ölçümleridir. Bağımsız denetimden geçmemiştir.

**Sınır (Task4F1):** Altın/kanıt etiketi açılmadı; recall/doğruluk/sıralama/benchmark hesaplanmadı; hiçbir geri-getirimin doğru olup olmadığı değerlendirilmedi. `build_archive` çalıştırılmadı (etiket okuduğu için); yalnızca kaynak kodu statik olarak incelendi.

## Adım 0 — Kapı

15/15 arşivde özellik geometrisi (`N_archive`, `word_columns`, `char_columns`, `combined_columns`) dondurulmuş tabloyla birebir eşleşti. Ayrıntı: `GATE.json`.

## Adım 1 — Roller var mı?

Evet. Turn sözlükleri yalnızca `role` + `content` taşır; `role` değerleri tam olarak iki tanedir:

- Derlem geneli: `user` 122.416, `assistant` 124.334 (246.750 tur, 23.867 oturum).
- Ardışık tur çiftlerinin 222.851/222.883'ü rol değiştirir (neredeyse tam sıralı diyalog).
- Kapılı 15 arşivde toplam: `user` 3.706, `assistant` 3.755 (arşiv başına yaklaşık yarı yarıya).
- Adaptör `build_archive` (statik okuma): rol filtresi YOKTUR — her tur, rolü ne olursa olsun belleğe eklenir; **iki rol de dizinlenir**. Rol, `memory_text = "[date] rol: content"` öneki olarak temsil girdisine girer; yapısal `role` alanı ayrı bir özellik olarak uyarlamaya girmez.

## Adım 2 — Ölçümler (15 kapılı arşiv, C + dondurulmuş işaret kodu, 96 bit)

**Bitişik-çift benzerliği (asistan → hemen önceki kullanıcı, aynı oturum):**

- Hamming medyanı: bitişik **28** (aralık 26–29) vs tüm-diğer **48,0** (15 arşivin 15'inde de 48) ve rastgele-20 **48,0**. Medyan farkı ≈ **20 bit**; AUC (diğer > bitişik) medyan **0,955** (aralık 0,909–0,975); bitişik çiftlerin medyan **%95,9**'u rastgele medyanın altında.
- Kosinüs (C üzerinde) medyanı: bitişik **0,77** vs diğer **−0,03**; fark ≈ **0,80**.

**Komşu bileşimi (kendi-dışında, Hamming ilk-3/10, role göre):**

- Aynı-oturum payı: ilk-3'te medyan user **0,94** / assistant **0,91**; ilk-10'da user **0,59** / assistant **0,57**.
- Bitişik-eş payı: ilk-3'te user **0,23** / assistant **0,22**; ilk-10'da her ikisi de **0,12**.
- Eşin ilk-k içinde olma oranı: ilk-3'te ≈ **%57–58**, ilk-10'da ≈ **%83–85** (roller arası fark ≤2 puan).

**Rol asimetrisi (en-yakın-komşu Hamming):** medyan user **17**, assistant **16** (arşiv başına fark medyanı 1 bit, aralık 0–3). Tam-kopya komşu (d=0) oranı her iki rolde de ≈ %0,5. Bir rolün belirgin biçimde daha kalabalık olduğu **yanlıştır** — dağılımlar esasen simetriktir.

**Kopya ölçeği (15 arşivde 1.856.431 çiftin içinde):**

| Eşik | Çift sayısı | Tüm çiftlere oranı | Bitişik olan | Bitişik payı |
|---|---|---|---|---|
| ≤ 4 bit | 160 | %0,009 | 16 | %10 |
| ≤ 8 bit | 488 | %0,026 | 50 | %10 |
| ≤ 16 bit | 2.610 | %0,14 | 420 | %16 |

## Adım 3 — Ayırma ne yapar, ne yapmaz (sayım)

Arşiv başına havuz (N, user, assistant): 001be529 (514, 255, 259); 00ca467f (486, 243, 243); 0100672e (486, 241, 245); 01493427 (487, 242, 245); 031748ae (494, 246, 248); 06878be2 (443, 218, 225); 06db6396 (479, 240, 239); 06f04340 (503, 249, 254); 07741c44 (513, 254, 259); 07741c45 (527, 261, 266); 078150f1 (551, 274, 277); 07b6f563 (524, 260, 264); 0862e8bf (490, 243, 247); 08e075c7 (484, 241, 243); 08f4fc43 (480, 239, 241). Tek-role dizinleme havuzu yaklaşık **yarıya** indirir.

Elenecek yakın-kopya çifti (15 arşiv toplamı): ≤4'te user-only **107** / assistant-only **71** (160'tan); ≤8'de **318** / **224** (488'den); ≤16'da **1.651** / **1.429** (2.610'dan).

**Ölçülmedi:** Bu elemenin geri-getirime yardım mı zarar mı verdiği **ölçülmedi** ve bu veriden çıkarılamaz. Belleğin yarısını silmek, kanıt içeren bellekleri de siler; yön için altın etiket gerekir ve etiket açılmamıştır. Hiçbir yarar ima edilmemektedir.

## Sonuç

- Roller hattın tamamında vardır ve iki rol de dizinlenir.
- Bitişik asistan–kullanıcı çiftleri rastgele çiftlerden çok daha yakındır (20 bit / 0,80 kosinüs ayrımı, AUC ≈ 0,95). Önermenin göreli anlamı **doğrudur**.
- Ancak "neredeyse-kopya" mutlak anlamda **yanlıştır**: bitişik medyan 28 bittir ve küçük-eşik çiftleri nadirdir (≤16'da tüm çiftlerin %0,14'ü); bu azınlığın da çoğu (%84) bitişik çift değildir.
- Roller arası kalabalık farkı ve komşu-bileşimi farkı ihmal edilecek düzeydedir; bunu kontrol etmedim değil — ölçtüm ve **yok**.
- Geri-getirim etkisi kontrol edilmedi — bu "yanlış" değil, "bakılmadı"dır; mühürlü görev buna izin vermez.
