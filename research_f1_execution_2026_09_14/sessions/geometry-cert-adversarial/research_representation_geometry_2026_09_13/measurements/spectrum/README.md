[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Benioku — tanımlayıcı spektrum ölçümü

Bu dizin **beyan edilmiş bir YENİDEN-UYARLAMA (declared re-fit)** ürünüdür:
dondurulmuş üretim yapıtı geri kazanılmadı; temsil hattı gerçek derlem
üzerinde yeniden uyarlanıp yalnızca temsilin **tanımlayıcı istatistikleri**
(tekil değerler, koordinat başına varyans) okundu.

- Derlem: `/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json`
- İzlenen prob: `/mnt/c/Users/MDP/dev/llmzip-work/drive/v52_t4c3_coordinate_axis_probe.py` (SVD_SEED=5204)
- Adaptör: `/mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py`
  (yalnızca `fit_archive_representation` çağrıldı; etikete dokunan
  `build_archive` çağrılmadı, metinler etiketsiz kuruldu)
- Dondurulmuş geometri: `V52_T4C2_feature_geometry.csv` (yalnızca kapı karşılaştırması)

**Hesaplanmayanlar:** geri-getirim (retrieval), geri-çağırma/dogruluk
(recall/accuracy), altın/kanıt etiketi kullanımı, belge sıralama, kıyaslama
(benchmark), sonuç sayısı, HMAC/mühürleme. Bu dizindeki hiçbir sayı bir
değerlendirme sonucu değildir.

Dosyalar: `measure_spectrum.py` (ölçüm; kapı kalırsa durur),
`GATE.json` (kapı), `SPECTRUM.json` (spektrum), `SPECTRUM_REPORT_TR.md` (rapor).
