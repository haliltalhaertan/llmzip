[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Provenance gate — performans kaydı

Bu araç artık araştırma yönünü etkiliyor, dolayısıyla **kendisinin de bir benchmark'ı olmalı.**
Kalibrasyon doğruluğu tek başına yetmez; zaman içinde precision, yanlış-pozitif oranı ve
insan-tarafından-bozulma oranı tutulur.

## Sürüm geçmişi

| sürüm | tarih | değişiklik |
|---|---|---|
| v1 | 2026-09-18 | Varlık kontrolü: `git grep` + Jev sınıflaması + kod kararı |
| v2 | 2026-09-18 | İsabetin **türü** sınıflanıyor (6 provenance sınıfı) |
| v3 | 2026-09-18 | `PRIMARY_RECOMPUTED`: ham artefakttan bağımsız yeniden hesap |

## v1 → v2 precision

Aynı 46 iddia, aynı üç kaynak belge.

| | v1 | v2 |
|---|---|---|
| PROVENANCE_FAIL | 5 | **0** |
| Bunlardan gerçek | **0** | — |
| **Precision (FAIL sınıfı)** | **0/5 = %0** | — |

v1'in beş alarmının **tamamı sahteydi**: `the fitted encoder`, `The width ladder`,
`fixed encoder`, `specific fixed-encoder`, `fixing the encoder` — hepsi İngilizce düzyazı
ifadeleri, çıkarıcı bunları teknik ad sandı. v2'de hepsi `OK_PRIMARY`.

**Kayda değer:** v1'in çıktısı koordinatör tarafından kullanıcıya *"main'deki en önemli olumlu
bulgunun kanıtı yayınlanmamış"* diye aktarıldı. Bu **yanlıştı** ve doğrulanmadan iletildi.
İnsan-tarafından-bozulma (human-overturn) oranı v1 için **1/1** — üretilen tek üst düzey
yorum geri çekildi.

## Bilinen hata modları (üçü de gerçekleşti)

| # | Mod | Belirti | Çözüm |
|---|---|---|---|
| 1 | **Meta kendini kirletme** | Bir terimin *yokluğunu* yazan belge, varlığına kanıt sayılıyor | `META` filtresi |
| 2 | **Düzyazı kirlenmesi** | Sohbet dökümündeki sayı ölçüm sanılıyor | `PROSE_ONLY` sınıfı |
| 3 | **Sözlüksel biçim uyuşmazlığı** | `19.86 pp` aranıyor, kanıt `+19.86pp` yazıyor | Varyant üretimi, birim zorunlu |

**Beklenen ama henüz görülmemiş modlar:** eşanlamlı terimler, Unicode normalizasyonu
(`−` vs `-`), `%` ile `pp` karışması, yuvarlama/kesme farkı *(v3'te görüldü — aşağıya bakınız)*,
dosya taşınması, üretilmiş tablolar.

## v3 — yeniden hesaplama sonuçları

Yedi manşet sayı, ham artefaktlardan bağımsız formülle yeniden üretildi (model kullanılmadı,
saf aritmetik):

| iddia | bildirilen | yeniden hesap | hata | sonuç |
|---|---:|---:|---:|---|
| INDEP merdiven qscale | +19,86 | 19,8582 | 0,0018 | PRIMARY_RECOMPUTED |
| INDEP merdiven sym | +16,88 | 16,8794 | 0,0006 | PRIMARY_RECOMPUTED |
| TRANS merdiven qscale | +8,22 | 8,2270 | 0,0070 | **PRIMARY_RECOMPUTED_TRUNCATED** |
| TRANS merdiven sym | +7,66 | 7,6596 | 0,0004 | PRIMARY_RECOMPUTED |
| 48B vs birincil BM25 Hit@10 | −3,83 | −3,8298 | 0,0002 | PRIMARY_RECOMPUTED |
| 48B vs birincil BM25 FR@3 | −3,26 | −3,2564 | 0,0036 | PRIMARY_RECOMPUTED |
| 48B vs en güçlü BM25 (geri çekilen manşet) | −7,80 | −7,8014 | 0,0014 | PRIMARY_RECOMPUTED |

**7/7 yeniden üretildi.**

### Dördüncü hata modu: kesme

`+8,22` uyuşmazlık verdi. Gerçek değer **8,2270** — doğru yuvarlamayla **8,23**. Rapor
yuvarlamak yerine **kesmiş**.

Bilimsel sonuca etkisi yok (0,007 pp), ama bir kayıt: aynı kesme, tolerans dar tutulursa
gelecekte sahte uyuşmazlık üretir; geniş tutulursa gerçek hatayı gizler. Çözüm iki ayrı
tolerans: doğru yuvarlama için **0,005**, kesme için **0,010** — ve kesme durumu **ayrı bir
sonuç sınıfı** olarak işaretlenir, sessizce geçirilmez.

## Metrik tanımları (sonraki koşular için)

| metrik | tanım |
|---|---|
| `precision` | Gerçek sorun / toplam alarm |
| `false_positive_rate` | Sahte alarm / toplam alarm |
| `false_negative_rate` | Kaçırılan gerçek sorun / bilinen gerçek sorun |
| `primary_vs_prose_confusion` | `PRIMARY_EVIDENCE` ↔ `PROSE_ONLY` yanlış sınıflaması |
| `human_overturn_rate` | İnsan incelemesinde bozulan araç hükmü / toplam hüküm |

## Kalibrasyon altın kümesi

| terim | beklenen | v2/v3 |
|---|---|---|
| `spectral grouping` | YOK | NONE ✓ |
| `10.13 GB` | prose-only | PROSE_ONLY ✓ |
| `5.43 GB` | prose-only | PROSE_ONLY ✓ |
| `19.86 pp` | primary | PRIMARY_EVIDENCE ✓ |
| `28.37 pp` | primary | PRIMARY_EVIDENCE ✓ |
| `DynamicCache` | primary | PRIMARY_EVIDENCE ✓ |
| `NanoBEIR` | var (literatür) | isabet ✓ |
| `residual bit` | var | isabet ✓ |
| `8.22 pp` | var | isabet ✓ |
| `3.83 pp` | var | isabet ✓ |

Sınıf kalibrasyonu: **11/11** (6 yol eşlemesi + 5 altın terim).
Altın küme küçük (10 terim). Gerçek bir kalibrasyon 100–150 öğe ister; bu sayı savunulabilir
bir eşik vermez, yalnızca bilinen hata modlarına karşı regresyon koruması sağlar.

## Yönetici kural

> **Bir iddia, ham artefakttan yeniden üretilebildiğinde grounded sayılır — dosyada göründüğünde
> değil.**

Ve aracın kendisi için:

> **`PROVENANCE_FAIL` bir inceleme kuyruğu durumudur, bilimsel hüküm değildir.**
> Aracın alarmı da bir iddiadır ve aynı zincirden geçer.
