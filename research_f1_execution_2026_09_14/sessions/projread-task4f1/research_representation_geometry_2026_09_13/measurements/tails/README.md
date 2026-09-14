[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# tails/out — Kuyruk ve Hubness Geometri Ölçümü

**BEYAN EDİLMİŞ YENİDEN-UYARLAMA (declared re-fit):** bu dizindeki her çıktı, dondurulmuş üretim yapıtının geri kazanımı DEĞİLDİR; gerçek derlem üzerinde temsil hattının yeniden uyarlanmasından okunan tanımlayıcı geometri istatistikleridir. **Bağımsız denetimden geçmemiştir (not independently audited).**

**Sınır:** etiket açılmadı, recall/doğruluk yok, sıralama doğruluğu değerlendirilmedi, benchmark yok. Puanlama fonksiyonları yalnızca birbiriyle karşılaştırıldı; gerçekle karşılaştırma yoktur.

## İçerik

- `measure_tails.py` — ölçüm betiği (kapı + kuyruk + hubness + sıralama uyumu). Salt-okunur girdileri okur, yalnızca bu dizine yazar.
- `GATE.json` — kapı sonucu (15/15 GEÇTİ).
- `TAILS.json` — arşiv-başına ve toplu geometri istatistikleri.
- `TAILS_REPORT_TR.md` — Türkçe rapor (nihai sonuç).
- `README.md` — bu dosya.

## Yeniden üretim

Ortam: `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, yorumlayıcı `/home/mdp/muse-work/ml-python -B`. Ağ yok.

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B measure_tails.py \
  --corpus /mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json \
  --adapter /mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py \
  --geometry /mnt/c/Users/MDP/dev/llmzip/docs/v52/task4c2/V52_T4C2_feature_geometry.csv \
  --outdir /home/mdp/muse-work/tails/out --n-archives 15
```

Kapı kalırsa betik 3 koduyla durur ve ölçüm yazmaz. Bağ-kırma tohumları sabittir (taban 77000 + arşiv sırası); sonuçlar deterministiktir.

## Girdi notu

Kapılı gerçekleme `/home/mdp/muse-work/spectrum/out/PACKAGE/measure_spectrum.py` (kapı 15/15) mantığı yeniden kullanıldı: aynı arşiv-metin kurulumu, aynı SVD hattı (96 bileşen, tohum 5204), aynı kapı alanları.
