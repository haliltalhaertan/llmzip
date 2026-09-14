[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Yeniden-üretim

İlk çalıştırmanın komut satırı kayda geçmemiş; aşağıdaki eşdeğer
komut aynı girdilerle aynı kapıyı üretir (geometri dosyası bayt-aynı
kopyalardan biri; ayırt edici kimlik sha256'dır, yola değil).

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
/home/mdp/muse-work/ml-python -B \
  /home/mdp/muse-work/spectrum/out/PACKAGE/measure_spectrum.py \
  --corpus /mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json \
  --adapter /mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py \
  --geometry <V52_T4C2_feature_geometry.csv> \
  --outdir /home/mdp/muse-work/spectrum/out/ \
  --n-archives 15
```

Girdi karmaları `HASHES.json` (`inputs` bölümü) ile doğrulanır.

## Yorumlayıcı ve kitaplıklar

- Yorumlayıcı: `/home/mdp/muse-work/ml-python -B`
  (`/usr/bin/python3` sarmalayıcısı), Python 3.14.4.
- numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1.
- Çevre: `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`,
  `PYTHONDONTWRITEBYTECODE=1`.

## Beklenen çıktı

- Çıkış kodu 0; her arşiv satırı `GECTI`; son satır
  `YAZILDI: GATE.json, SPECTRUM.json`.
- `GATE.json`: `overall_pass=true`, 15 satırın tamamı `pass=true`,
  her hücrede beklenen = ölçülen.
- `SPECTRUM.json` toplu medyanlar: p_A=0.478, f12_A=0.417,
  p_B=0.861, f12_B=0.357; işaret medyan 11/96 ve 0.
- Bunlardan sapma = DUR; rapor geçersizdir.
