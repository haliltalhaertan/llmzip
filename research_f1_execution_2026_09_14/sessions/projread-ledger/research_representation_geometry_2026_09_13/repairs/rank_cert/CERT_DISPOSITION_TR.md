[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# CERT_DISPOSITION_TR — kusur karşılıkları (Türkçe)

Bu paket 1021083d4f2faebda760546e1217b4de1eef87ea Purevindeki
`rank_crossing_certificates/verify.py` dosyasını ek yolla düzeltir; arşiv
salt-okunurdur, yerinde değişiklik yoktur. `verify_v2.py` yerine geçen süittir
(48 korunan + 1 onarılan + 4 eklenen = 53 kontrol).

| # | Kusur | Özgün satır | Karşılık |
|---|-------|-------------|----------|
| 1 | Başlık statüleri denetlenmiyor | `verify.py:804-805` (hesap), `:809-810` (kayıt, denetim yok) | `verify_v2.py`: `S8-cA-status`, `S8-cA-direction`, `S8-cB-status`, `S8-cB-direction` |
| 2 | `UNRESOLVED` çözülebilirken bırakılmış (S8 `cB`) | `verify.py:805` (`cB`=`UNRESOLVED`) | `certify_v2.py` (ayrıştırıcı + Sturm-biseksiyon yalıtımı); beklenti `ISOLATED_TIES/VARIES` |
| 3 | S7 totolojisi: değişmez `True` denetleniyor | `verify.py:734` (`check(..., True, ...)`); tanık dalı `:736` | `verify_v2.py`: `check("S7-1plus1-unresolved", found11 is None, ...)` koşulsuz; tanık denetimi korunur |
| 4 | Gerçek-veri iddiasının kapsamı belirsiz | S8 bölümü (`:755-823`), `results.json` `S8-lme-illustration` | Aşağıdaki kapsam cümlesi; top-3 kararlılığı ima eden hiçbir ifade kullanılmaz |

## Kusur 1 — başlık denetimi yoktu

`cA` ve `cB`, tüm gerçek-veri iddiasını taşır ama hiçbir `check` statülerine
bakmazdı. Kanıt: bozuk `cA`da özgün süit 49/49 geçti (`FAILS_ON_ORIGINAL.md`
Deney 1); `verify_v2` aynı mutasyonda 4 ek kontrolle kaldı (Deney 2).

## Kusur 2 — `UNRESOLVED` çözülebilirdi

Özgün yordam aynı-işaretli içlerdeki P-köklerinde durur; `cB` böylece
`UNRESOLVED` kaldı. v2 uç-değer ayrıştırıcısı ve kesin kök yalıtımıyla bunu
`ISOLATED_TIES` (yön `VARIES`) olarak belgeler. Ölçüm (`fuzz_rates.py`,
yeniden koşuldu): yapay 6 çağrıda özgün 1/6, v2 0/6; bulanık `n=2000`
(`eff=1759`): özgün 649, ayrıştırıcı 6, v2 0; `agree_viol=0`, `mono_viol=0`,
`valid_fail=0`. Tutuculuk korunur: çözülemeyen yine `UNRESOLVED` döner.

## Kusur 3 — S7 totolojisi

`check("S7-1plus1-unresolved", True, ...)` tanık bulunsa bile geçerdi.
Onarım gerçek koşulu (`found11 is None`) koşulsuz denetler; tanık çıkarsa kalır
(`FAILS_ON_ORIGINAL.md` Deney 3). Mevcut ızgarada sonuç değişmez (`None`).

## Kusur 4 — gerçek-veri iddiasının gerçek kapsamı

Kapsam cümlesi: LongMemEval iddiası TEK belgeli çifttir (`cA`: `STRICT`, yön
`-1`; `cB`: `ISOLATED_TIES`, yön `VARIES`); o sorgu için eksiksiz bir ilk-3
belgesi 1413 çapraz çift gerektirir (`K·(n−K)` kalıbı), bunların 1 tanesi
vardır. Bu paketteki hiçbir belge ya da statü dizgesi ilk-3 kararlılığı ima
etmez; `VARIES` açıkça kararsız parça-sürekli sıra demektir.
