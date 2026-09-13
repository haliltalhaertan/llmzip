[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# README — ek düzeltme paketi (matematik)

Bu dizin, donmuş arşiv `.../round4/norm_aware_sign_bounds/`’a (@commit
`1021083d4f2faebda760546e1217b4de1eef87ea`) **ek** bir matematik düzeltme
paketidir. Özgün baytlar değiştirilmemiştir; düzeltmeler “yerine-geçme”
(supersedes) notlarıyla yeni dosyalarda durur.

- `CORRECTIONS_NORM_MATH_TR.md` — D1..D7 düzeltmeleri (Türkçe): özgün
  ifade + dosya:satır, hata nedeni, düzeltilmiş ifade, kanıt, tanık.
- `proofs_exact.py` — stdlib-only kesin-aritmetik kanıt/tarama betiği.
  Çalıştırma: `OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B proofs_exact.py`
  Beklenen: `478/478 checks passed`, çıkış 0. Her bölüm kendi
  başarısızlık koşulunu basar.
- `WITNESSES.json` — her düzeltilmiş iddia için makine-okunur tanıklar.

Kapsam: yalnızca matematik. Test onarımı ayrı aracın işidir; Task4F1 kapsam
dışıdır. **Bu paket bağımsız denetimden geçmemiştir; uygulayıcı kendi işinin
doğruluğunu ilan edemez.**
