[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Çok-adımlı hafıza çağırma hattı — uçtan uca ölçüm

`evidence_path`: `audit_hard_r4/MULTISTEP_PIPELINE.json`, `multistep_pipeline.py`
**Sıfır model çağrısı.** 470 sorgu, LME, saklanan artefaktlardan saf aritmetik.

Test edilen hat:

```
soru → ilk getirim → ilk kanıt → ayırt edici ipuçlarını çıkar
     → ikinci getirim → eksik kanıtları topla → birleştir
```

---

## Sonuç: hat **çalışmıyor** — ve sebebi beklenenden farklı

| kol | FR@3 | tabandan fark | CI95 |
|---|---:|---:|---|
| taban (BM25 top-3) | 59,93 | — | — |
| **oracle_M2** | **71,66** | **+11,73** | [+8,73, +14,84] SIG |
| oracle_M1 | 71,43 | +11,50 | [+8,47, +14,69] SIG |
| oracle_M2M4 | 71,30 | +11,38 | [+8,42, +14,43] SIG |
| oracle_M4 | 70,39 | +10,46 | [+7,34, +13,67] SIG |
| **real_M2** | **53,50** | **−6,43** | [−8,73, −4,18] SIG |
| real_M2M4 | 52,88 | −7,05 | [−9,47, −4,71] SIG |
| real_M1 | 52,59 | −7,34 | [−9,99, −4,73] SIG |
| real_M4 | 51,12 | −8,81 | [−11,62, −6,07] SIG |

`oracle` = çapa havuzdaki **gerçek gold** (sistem bunu bilemez).
`real` = çapa **BM25 top-1** (konuşlanabilir olan budur).

**Oracle–gerçek uçurumu: 18,2–19,3 pp.** Tüm dört ipucu yönteminde aynı.

---

## Neden başarısız: iki ayrı ölçüm

### 1. Çapa doğruluğu yetmiyor — ama sorun bu değil

BM25 top-1 gold isabeti: **255/470 = %54,3**. Yani çapa **%45,7 oranında yanlış belge**.

Doğal varsayım: "daha iyi çapa seçersek (örn. Jev, Hit@1 66,6) hat kazanır." **Yanlış.**

M2 hattı, çapa doğruluğu koşulunda:

| durum | n | hat | taban | fark |
|---|---:|---:|---:|---:|
| çapa **doğru** | 255 | 79,78 | 84,65 | **−4,87** |
| çapa **yanlış** | 215 | 22,33 | 30,60 | −8,27 |

**Çapa doğruyken bile hat tabandan kötü.** Başabaş çapa doğruluğu **%243** — matematiksel olarak
imkânsız. Yani **hiçbir çapa seçici bu hattı kurtaramaz**; Jev'in %66,6 Hit@1'i de yetmez
(tahmini sonuç −6,0 pp).

### 2. Oracle kazancı genişletmeden değil, garantili slottan geliyor

Oracle kolunu ikiye ayırdım (n=432, çapa bulunabilen sorgular):

| | FR@3 |
|---|---:|
| taban top-3 | 65,20 |
| oracle çapa + **genişletme YOK** (taban sıralamasından 2 belge) | **81,69** |
| oracle çapa + M2 genişletme | 77,96 |

| bileşen | katkı |
|---|---:|
| **Garantili gold slotu** | **+16,49 pp** |
| **Genişletmenin kendisi** | **−3,73 pp** |

**Oracle kazancının tamamı, birinci slota bir gold'un elle yerleştirilmesinden geliyor.** İpucu
çıkarma — hattın asıl fikri — **kendi başına zarar veriyor**.

> Bu, klasik bir oracle yanılsaması: `+11,5 pp` rakamı "çok-adımlı çağırma işe yarıyor" gibi
> okunuyordu, ama aslında "cevabı bilirsen cevap daha iyi" diyordu.

---

## Neden genişletme zarar veriyor

Çapa metnini sorguya eklemek, ikinci turu **çapanın konusuna** çekiyor. Kalan gold'lar çapaya
benzemiyorsa (ki çoklu-kanıt sorularında tanım gereği **farklı** bilgi taşıyorlar), genişletilmiş
sorgu onları bulmak yerine çapanın komşularını getiriyor.

Önceki M1 ölçümü (L-111, rank hareketi) bunu zaten göstermişti: 61 gold top-10'a **girmiş**,
23'ü **düşmüştü**. O zaman "net +38" pozitif görünüyordu. Uçtan uca FR@3 ölçüldüğünde net
etkinin **negatif** olduğu ortaya çıktı — çünkü rank hareketi, seçilen üç belgeye ne olduğunu
göstermiyor.

> **Ders:** Ara metrik (rank hareketi) ile nihai metrik (FR@3) zıt işaret verebilir. Bir
> mekanizmayı ara metrikle onaylamak yeterli değil.

---

## Beşinci "kurtardı/bozdu" vakası

| müdahale | sonuç |
|---|---|
| Jev rerank | 21 kurtardı / 25 bozdu |
| RRF füzyon | gold eliyor, Δ ayırt edilemez |
| Sorgu genişletme (rank) | 61 girdi / 23 düştü |
| Çeşitlilik seçimi | 4 iyi / 16 kötü, **−1,19** |
| **Çok-adımlı hat (uçtan uca)** | **−6,43 en iyi gerçek kol** |

Beş müdahalenin beşi de çift taraflı; **dördü net negatif**, biri ayırt edilemez.

---

## Ne kapandı, ne kapanmadı

**Kapandı:** *"çapa metnini sorguya ekleyerek ikinci tur yap"* ailesi — M1, M2, M4, M2M4
dördü de, hem oracle hem gerçek çapayla ölçüldü. Genişletmenin kendi katkısı **−3,73 pp**.

**Kapanmadı:**

| | durum |
|---|---|
| M5/M6 — çapa **vektörüyle** komşu arama (metin genişletme değil) | ölçülmedi |
| M7 — koşullu ikinci tur (yalnız çoklu-kanıt sorularında) | ölçülmedi |
| M14 — soruyu alt sorulara **bölme** (çapa kullanmadan) | ölçülmedi |
| Yargı modelinin ipucu **çıkarması** (kelime yerine anlam) | ölçülmedi |
| `sign96` tarafında aynı hat | **ölçülemez** — kodlayıcı saklanmamış |

**Önemli ayrım:** bu ölçüm *"çok-adımlı çağırma işe yaramaz"* demiyor. *"Çapa metnini sözlüksel
olarak sorguya eklemek işe yaramıyor"* diyor. Hattın diğer biçimleri — özellikle çapayı sorgu
yerine **filtre** olarak kullanmak, ya da soruyu bölmek — dokunulmadan duruyor.

---

## Sınırlar

- Yalnız **sözlüksel** taraf. `sign96` kodlayıcısı saklanmadığı için kompakt kod tarafında aynı
  hat kurulamıyor.
- Tek veri kümesi (LME, n=470), tek dil, tek korpus biçimi.
- Üç-belge bütçesi sabit tutuldu (çapa + 2). Daha geniş bütçede sonuç değişebilir — ölçülmedi.
- **Ayrılmış sınav verisi yok.** Bu da her bugünkü ölçüm gibi keşifseldir.
