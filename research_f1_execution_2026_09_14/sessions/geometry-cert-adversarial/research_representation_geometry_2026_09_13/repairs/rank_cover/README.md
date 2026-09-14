[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# fix_rank_cover/out — ek düzeltmeler (C1+C2+C3)

Eklemeli paket; dondurulmuş arşive yazılmadı. Bağımsız denetimden geçmedi.

## Dosyalar
- `coverage_v2.py`: C1+C3 paketi (48 kontrol). Özgün mantık gömülü (`*_orig`), C3 adlı ret sarmalayıcıda.
- `orig_verify_snapshot.py`: dondurulmuş `verify.py` birebir kopyası (kanıt saklama).
- `realizable_tangent.py`: C2 vektör inşası + P/hüküm doğrulaması (12 kontrol).
- `REALIZABILITY_TR.md`: gerçeklenebilirlik kısıtları + örnek sınıfları.
- `COVERAGE_DISPOSITION_TR.md`: supersedes + dal tablosu + ulaşılamazlık ispatları.
- `FAILS_ON_ORIGINAL.md`: her testin orijinalde FAIL, düzeltmede PASS kanıtı.

## Koşu
```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B coverage_v2.py
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B realizable_tangent.py
```
Beklenen: `checks=48 fail=0 ALL PASS` ve `checks=12 fail=0 ALL PASS`. Stdlib-only, Fraction ile kesin.

## Kapsam özeti
DOMAIN_FAIL, deg0/1, VARIES, certify-PT kapsandı; topk-PT-doğru ve sturm-None ulaşılamaz (ispatlı).
C3: `EMPTY_INTERVAL`, `INVERTED_INTERVAL`, `NONPOSITIVE_LEFT` adlı retler; bozuk aralık sertifika üretmez.
C2: aday teğet gerçeklenebilir; açık ℚ-vektörler verildi; S4 soyut-sadece.

## Sınırlar
Çözüm mantığı değişmedi; `certify_pair` çözüm yolu ve başlık iddiaları kapsam dışı.
Sıfır-ortalama okuması incelenmedi. Bu paket tek başına sertifika sayılmaz.
