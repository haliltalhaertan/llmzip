[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Roller Ölçüm Paketi — README

**BEYAN EDİLMİŞ YENİDEN-UYARLAMA (declared re-fit); bağımsız denetimden geçmedi (not independently audited).** Dondurulmuş yapıtın geri kazanımı değildir; gerçek derlem üzerinde temsil hattının yeniden uyarlanmasından okunan tanımlayıcı ölçümlerdir.

**Sınır:** Altın/kanıt etiketi açılmadı; recall/doğruluk/sıralama/benchmark yok; geri-getirim etkisi ölçülmedi. `build_archive` çalıştırılmadı; yalnızca statik incelendi.

## Dosyalar

- `measure_roles.py` — Ölçüm betiği. Etiket/soru/cevap alanlarını okumaz; yalnızca `question_id`, `haystack_session_ids`, `haystack_dates`, `haystack_sessions→role/content` kullanır.
- `GATE.json` — Kapı sonucu: 15/15 birebir geometri eşleşmesi.
- `ROLES.json` — Adım 1–3 ölçümleri (arşiv başına + toplu).
- `ROLES_REPORT_TR.md` — Türkçe rapor.
- `README.md` — Bu dosya.

## Çalıştırma

Ortam: `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, yorumlayıcı `/home/mdp/muse-work/ml-python -B`. Ağ yok.

```bash
/home/mdp/muse-work/ml-python -B measure_roles.py \
  --corpus /mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json \
  --adapter /mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py \
  --geometry /mnt/c/Users/MDP/dev/llmzip/docs/v52/task4c2/V52_T4C2_feature_geometry.csv \
  --outdir . --n-archives 15
```

Yöntem: kapılı gerçeklesme (`measure_spectrum.py`, kapı 15/15) ile aynı hat — arşiv başına TF-IDF (sözcük+karakter) + SVD96 (tohum 5204) + L2 + merkezleme (C) + işaret kodu (C≥0). Komşuluk eşitlik-bozma: (Hamming, arşiv-sırası) sözlük sırası, kendi-dışında.
