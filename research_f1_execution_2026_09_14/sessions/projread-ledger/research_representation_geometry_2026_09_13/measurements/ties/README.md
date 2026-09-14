[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Ölçüm paketi: SIGN96 bağ geometrisi (Task4F1 sınırı içinde)

**BEYAN EDİLMİŞ YENİDEN-UYARLAMA (declared re-fit):** Bu dizindeki her çıktı, gerçek derlem
üzerinde temsil hattının yeniden uyarlanmasından okunan TANIMLAYICI geometri istatistikleridir;
dondurulmuş üretim yapıtının geri kazanımı DEĞİLDİR. Bağımsız denetimden geçmemiştir.

**Sınır:** Gold/evidence etiketleri açılmadı; recall/doğruluk hesaplanmadı; getirimin doğruluğu
değerlendirilmedi; benchmark çalıştırılmadı. Tüm iddialar ÇÖZÜNÜRLÜK KAPASİTESİ hakkındadır.

## Dosyalar

- `measure_ties.py` — ölçüm betiği. Yükleyici olarak kapısı 15/15 geçmiş uygulamayı
  (`spectrum/out/PACKAGE/measure_spectrum.py`: `archive_texts_only`, `load_adapter`,
  `SVD_SEED=5204`, `N_COMPONENTS=96`) modül olarak içe aktarır; kendi yükleyicisini yazmaz.
- `GATE.json` — ADIM 1 kapısı: 10 arşivde `N_archive`, `word_columns`, `char_columns`,
  `combined_columns` birebir eşleşmesi. Sonuç: 10/10 GEÇTİ.
- `TIES.json` — tüm ölçüm sonuçları (arşiv başına + havuzlanmış özetler).
- `TIES_REPORT_TR.md` — Türkçe rapor (nihai sonuç).
- `README.md` — bu dosya.

## Yöntem (kısa)

Her arşivde: TF-IDF(word+char)+LSA32 → birleşik matris → SVD96 (tohum 5204) → normalize →
merkezle (`C`) → kod `sign(C)`, 96 bit. Sondalar arşivin KENDİ merkezlenmiş vektörleridir
(leave-one-out; gold-bağlantılı sorgu yok). Aday dışı-bırakma için Hamming matrisinde
köşegen nöbetçi (999) ile kapatılır. Alt-örnekleme: tam-arşiv uyumunun satır alt-kümesidir
(tohum `9000+arşiv_sırası`); havuzlama: ayrı uyumların bit matrislerinin alt-alta eklenmesidir.

## Yeniden çalıştırma

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B measure_ties.py \
--corpus /mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json \
--adapter /mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py \
--geometry /mnt/c/Users/MDP/dev/llmzip/docs/v52/task4c2/V52_T4C2_feature_geometry.csv \
--outdir /home/mdp/muse-work/ties/out --n-archives 10
```

Ağ yok; deterministik (sabit tohumlar).
