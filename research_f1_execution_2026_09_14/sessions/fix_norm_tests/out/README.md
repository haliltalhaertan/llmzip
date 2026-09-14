[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Eklemeli düzeltme paketi — `norm_aware_sign_bounds` test onarımları

Bu dizin, dondurulmuş kaynağı düzeltmez; yalnızca ekler. Düzeltilen commit:
`1021083d4f2faebda760546e1217b4de1eef87ea` altındaki
`round4/norm_aware_sign_bounds/` (salt-okunur, bilerek; dokunulmadı).

## İçindekiler

- `verify_v2.py` — üste-gelen doğrulayıcı. **Çalışır:** etiket yorum
  satırındadır, `run_T5`/`run_T6`/`main()` mevcuttur. Çalıştırma:
  `python3 -B verify_v2.py` → `5791/5791 checks passed`, çıkış 0,
  grup özeti + `results.json` yazar.
- `verify_orig.py` — orijinalin kopyası (272/272 geçer; sorun da budur).
- `results.json` — v2 tam çalıştırmanın çıktısı (5791/5791).
  `results_orig.json` — orijinal çalışmanın çıktısıdır (272/272, korunur).
- `T5_EVIDENCE.md` — tam-indirgeme türetmesi, vaka sayımı/kapsama,
  kırık-sınır deneyi, en sıkı vaka.
- `FAILS_ON_ORIGINAL.md` — her onarım/ek kontrol için yürütme kanıtı
  (orijinalde kalır / düzeltilmişte geçer ham çıktıları).
- `TEST_DISPOSITION_TR.md` — T1..T6 işlem kaydı, `supersedes` tablosu, sayım
  ayrışımı (272 → 5791).

## Ne doğrulandı, ne doğrulanmadı

Doğrulanan (yürütmeyle): orijinal 272/272; önceki gövde 340/340; m=0 tanığı;
30 totolojinin körlüğü ve altın tablonun bozuk varyantı yakalaması; rho>0;
iki parantez düzeltmesinin uç-erisimi; T5 genel-durum vektör testi (2716
vaka, tam); T6 8 kontrol (3 D vektör tanığı dahil). Doğrulanmayan: float
nicem sertifikası, `C.tie` ikili-arama tanıkları, `aligned` 0.99 sayısına
özel vektör tanığı — açık boşluk olarak kayda geçti, uydurulmadı.

## Kullanım dışı uyarısı

BAĞIMSIZ DENETİMDEN GEÇMEDİ. Kullanmadan önce açıklayın (etiketler gereği).
Karar gereken her yerde `fractions.Fraction` kullanıldı; ağ/karşılaştırma
ölçütü çalıştırılmadı.
