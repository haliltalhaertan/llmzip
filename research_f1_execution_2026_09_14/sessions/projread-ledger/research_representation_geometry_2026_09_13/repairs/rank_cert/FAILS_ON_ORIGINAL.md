[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# FAILS_ON_ORIGINAL — özgün süitin yakalayamadığı bozulma

Mutasyon: özgün süitin kopyasında (`/tmp/mut_exp/mut_cA.py`) `certify_pair`
sarmalandı; yalnız `(L,R)=(1/16,1)` çağrısı (S8 `cA`) `UNRESOLVED` döndürür.
S6 çağrıları `J=(1/16,16)/(1/4,4)` kullandığı için etkilenmez. Doğrulandı:
mutasyonlu `cA` = `UNRESOLVED/None`, diğer yollar özgünle aynı.

## Deney 1: bozuk `cA` — özgün süit

Komut: `python3 -B mut_cA.py` (ortam: tek iş parçacığı, baytkod kapalı).
Ham çıktı:

```
checks=49 fail=0
ALL PASS
```

Çıkış kodu: 0. Bozuk başlık belgesi 49/49 GEÇTİ; hiçbir kontrol `cA`ya bakmaz.

## Deney 2: aynı mutasyon — `verify_v2.py`

Komut: `VERIFY_V2_PROC=mut_cA PYTHONPATH=/tmp/mut_exp python3 -B verify_v2.py`.
Ham çıktı:

```
FAIL S8-cA-status UNRESOLVED
FAIL S8-cA-direction None
FAIL S8-cB-status UNRESOLVED
FAIL S8-cB-direction None
checks=53 fail=4
FAILED: ['S8-cA-status', 'S8-cA-direction', 'S8-cB-status', 'S8-cB-direction']
```

Çıkış kodu: 1. Not: mutasyon yalnız `cA`yı hedefledi; `cB` kayıpları mutasyonun
değil, özgün yordamın `cB`yi gerçekten `UNRESOLVED` bırakmasınındır (ikinci
kusur). `verify_v2` v2 beklentisini (`ISOLATED_TIES/VARIES`) denetlediği için
ikisini de yakalar. Belirleyici karşıtlık: özgün, kırık `cA`da 49/49 geçer;
`verify_v2` kalır.

## Deney 3: S7 totoloji onarımı — önce/sonra

Eski ifade (`verify.py:734`): `check("S7-1plus1-unresolved", True, ...)` hiçbir
girdide kalamaz. Yeni ifade: `check("S7-1plus1-unresolved", found11 is None, ...)`.
Doğruluk tablosu (`/tmp/mut_exp/s7_tautology_probe.py` ham çıktısı):

```
tanik-yok (gercek izgara) eski=GECTI yeni=GECTI
tanik-var (zorlanmis)     eski=GECTI yeni=KALDI
```

Gerçek ızgarada `found11 is None` olduğundan iki süit de geçer; tanık çıksaydı
yalnız yenisi kalırdı.

## Eklenen her kontrol ne zaman kalır

- `S8-cA-status`: `cA["status"] != "STRICT"` ise (mutasyon, alan-dışı, çözümsüz).
- `S8-cA-direction`: `cA["direction"] != -1` ise (yön tanımsız/kayıp dahil).
- `S8-cB-status`: `cB["status"] != "ISOLATED_TIES"` ise (özgün yordam dahil).
- `S8-cB-direction`: `cB["direction"] != "VARIES"` ise.
- Onarılan `S7-1plus1-unresolved`: ızgarada tanık (`found11 is not None`) varsa.
