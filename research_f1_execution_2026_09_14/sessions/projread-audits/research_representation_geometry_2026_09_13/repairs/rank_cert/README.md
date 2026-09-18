[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Ek düzeltme paketi — README

Bu dizin (`out/`), 1021083d4f2faebda760546e1217b4de1eef87ea Purevindeki
`rank_crossing_certificates/` arşivine EK düzeltmedir; arşiv salt-okunur
bırakıldı, yerinde değişiklik yok. Önceki oturumun kodu (`certify_v2.py`,
`fuzz_rates.py`) aynen korundu, yalnız kanıt ve belge tamamlandı.

Bağımsız denetimden geçmedi; kullanmadan önce açıklayın.

## Dosyalar

- `verify_v2.py` — yerine geçen süit: 48 korunan + 1 onarılan (S7 totolojisi)
  + 4 eklenen (S8 `cA`/`cB` statü+yön) = 53 kontrol. Varsayılan yordam
  `certify_v2`; `VERIFY_V2_PROC` ile değiştirilebilir. Çıktı: `results_v2.json`.
- `certify_v2.py` — yerine geçen yordam (önceki oturum; değiştirilmedi).
- `fuzz_rates.py`, `UNRESOLVED_RATE.json` — önce/sonra oran ölçümü.
- `verify_orig_copy.py`, `results_orig.json`, `results.json` — özgün başvuru.
- `FAILS_ON_ORIGINAL.md` — mutasyon deneyi ham çıktıları (belirleyici kanıt).
- `CERT_DISPOSITION_TR.md` — kusur karşılıkları ve kapsam cümlesi (Türkçe).

## Yeniden üretim

Ortam: `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`, `python3 -B` ile:

- `python3 -B fuzz_rates.py` → yapay 1/6→0/6; bulanık 649→0 (`eff=1759`).
- `python3 -B verify_v2.py` → `checks=53 fail=0, ALL PASS`.
- Mutasyon: `/tmp/mut_exp/mut_cA.py` özgünde `49/49 PASS` (çıkış 0),
  `VERIFY_V2_PROC=mut_cA PYTHONPATH=/tmp/mut_exp python3 -B verify_v2.py`
  4 kontrolde kalır (çıkış 1).

Kapsam: LongMemEval iddiası TEK belgeli çifttir; ilk-3 belgesi 1413 çapraz
çift ister, 1 tanesi vardır. Task4F1 kapsam dışıdır.
