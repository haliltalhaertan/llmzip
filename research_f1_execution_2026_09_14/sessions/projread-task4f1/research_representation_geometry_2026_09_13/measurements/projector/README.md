[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Projektör Bayt Ölçümü — README

BEYAN EDİLMİŞ YENİDEN-UYDURMA (declared re-fit): buradaki boyutlar sadık bir
yeniden-uydurmaya aittir; dondurulmuş üretim yapıtının geri kazanımı değildir.
O yapıtın fiziksel serileşmesi hiç bulunamadı. Bağımsız denetimden geçmedi.

Task4F1 sınırı: retrieval sonucu, recall/doğruluk, gold/evidence, sıralama,
benchmark, sonuç sayısı yok; yalnızca boyut ölçümü.

## İçerik

- `measure_projector.py`: kapı + boyut ölçümü (kapısı geçmiş hattı yeniden kullanır).
- `GATE.json`: geometri kapısı (15/15).
- `PROJECTOR_BYTES.json`: bileşen dökümü, toplamlar, oranlar, başabaş.
- `PROJECTOR_REPORT_TR.md`: Türkçe rapor (nihai çıktı).
- `HASHES.json`: bu dizindeki teslimatların SHA256 dökümü.
- `README.md`: bu dosya.

## Çalıştırma

No network. Tek iş parçacığı:

`OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B measure_projector.py --corpus <json> --adapter <py> --geometry <csv> --outdir . --n-archives 15`

## Kapsam

Arşiv-yerel uydurma, ilk 15 arşiv (N 443–551, d=32). Marjinal yük 12 B
(kurgu gereği); paylaşılan toplam ayrı raporlanır; etkin değer tavana karşı
test edilmez. Küresel projektör farklı biçimdir, ölçülmedi.
