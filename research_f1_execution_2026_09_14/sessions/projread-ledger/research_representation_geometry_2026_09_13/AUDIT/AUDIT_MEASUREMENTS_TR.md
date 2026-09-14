[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# BAĞIMSIZ DENETİM RAPORU: spectrum / projector / ties / roles (5 tanımlayıcı ölçüm)

## Bağımsızlık sınırlaması (açık)

Bu paketleri üreten oturumlarla aynı model ailesindenim. O çalışmaya dair
hafızam yok, akıl yürütmesine erişimim yok. Bu **kısmi bağımsızlıktır, tam
bağımsızlık değildir**. Kendimi tam bağımsız taraf olarak sunmuyorum.
Yöntemim: yeniden-okuma değil **yeniden-türetme** — kendi kodum, kendi
regresyonum, kendi tohumlarım; sayılar tutuyorsa yazar, tutmuyorsa kırarım.

## Sınırlara uyum

Task4F1 mührü: gold/evidence açılmadı, recall/doğruluk/sıralama/benchmark
yok. `build_archive` hiç çağrılmadı (etiket okuduğu için). Yalnızca temsil
yeniden-uyarlandı, tanımlayıcı istatistik okundu. Dondurulmuş arşiv ve
denetlenen paketler değiştirilmedi. Ağ yok. Yazma yalnızca
`/home/mdp/muse-work/audit_meas/out/` altına.

## MANŞET: kapı iddia edilenden zayıf, ama sayılar ayakta

Kapı (4 tamsayı: `N_archive`, `word_columns`, `char_columns`,
`combined_columns`) **boru-hattı özdeşliğini kanıtlamaz; şekil denetimidir.**
Maddi farklı hatlar aynı 4 sayıyı üretir — çalıştırarak kanıtladım
(`001be529`, `audit_gate_weakness.py`):

- `sublinear_tf=False`: kapı şekli **birebir aynı** (514, 39940, 59943,
  99915) ama `max|Δσ|=0.44` (~%5-8), `max|ΔVar|=0.0034`. **Aynı kapı,
  farklı istatistik.** KANITLANDI.
- Leksik SVD tohumu 5101→777: kapı aynı; `max|Δσ|=0.16`. KANITLANDI.
- SVD96 tohumu 5204→0/999: kapı aynı (SVD kapıdan sonra); `max|Δσ|≈0.01`,
  `max|ΔVar|≈1.5e-4`. Küçük ama sıfır değil. KANITLANDI.
- hstack sıra takası `[Xw,Xc,Xl]`: kapı aynı; `max|Δσ|=1e-14`.
  Spektrum için zararsız (sol tekil vektörler sütun permütasyonuna
  değişmez). Dürüstlük için: bu varyant bir şey kırmaz. KANITLANDI.
- Normsuz ham TF-IDF: sütunlar aynı, kapı kör. KANITLANDI.
- Karşı-kontrol — `stop_words=None`: word sütunu 39940→48536, **kapı
  yakalar**. KANITLANDI.

Kapının kısıtladığı: derlem metinlerinin birebir aynılığı, sözlüğü
değiştiren seçimler (tokenizer, n-gram, stop-word, lowercase), N, d=32.
Kapının **kısıtlamadığı**: TF-IDF değer seçenekleri (sublinear_tf, norm,
smooth_idf, use_idf), leksik SVD tohumu, SVD96 tohumu, normalizasyon
sırası/varlığı, dtype, hstack blok sırası, merkezleme. Bunlardan
sublinear_tf ve leksik tohum raporlanan istatistikleri maddi değiştirir.

Sonuç: "kapı geçti, o hâlde dondurulmuş hat yeniden üretildi" çıkarımı
**abartılı**. Gerçek güvence kapı değil kod özdeşliğidir (dondurulmuş
adapter işlevinin aynen çağrılması) — onu satır satır doğruladım (aşağıda)
ve sayıları bağımsız uyarlamayla tutturdum. Bu yüzden bulgu **P1
uyarıdır, BLOCKING değil**: her sayı "kapı + kod incelemesi + bağımsız
türetme" üçlüsüne dayanır, kapıya tek başına değil.

Kapı genelleme testi: paketin 15'i + **görülmemiş 16 arşiv** (satır
16-25, 100, 200, 300, 400, 460, 469) = **31/31 GEÇTİ**, hepsinde d_lex=32
(`audit_refit1_gate_spectrum.py`). Kapı zayıf ama tutarlı; seçilmiş 15'e
özgü bir ezber yok.

## Hat farkı: dondurulmuş prob vs `measure_spectrum.py` (satır satır)

- Metin kurma: prob `build_archive(v2)+fit_input_payload`, ölçüm
  `archive_texts_only`. İkisi de `f"[{date}] {role}: {content}"`, aynı
  atlama sırası. v2 `fit_archive_representation` = v1'in aynısıdır
  (v2 satır 53: doğrudan takma ad; v2 `memory_text` v1 ile aynı, satır 44
  vs 89). **Fark yok.**
- `fit_archive_representation(texts)` → `hstack([Xl,Xw,Xc])` →
  `TruncatedSVD(96, random_state=5204)` → `normalize` → `mean` →
  `astype(float64)`: prob satır 109-110 ile ölçüm satır 147-148/180-183
  **birebir aynı**.
- Tek sapma: prob `issues` varsa **çöker** (satır 104-105), ölçümler
  `issues`'u **yok sayar**. 31 arşivde yapısal sorun taradım
  (has_answer'a dokunmadan): **0 sorun**. has_answer-tip sorunları
  metni etkileyemez. **Maddi değil.** KANITLANDI (çalıştırma).

## Spectrum: DOĞRULANDI (kendi uyarlamam, kendi regresyonum)

3 arşivde (ilk/orta/son) bağımsız uyarlama + kapalı-form en-küçük-kareler
(polyfit DEĞİL). Hepsi 3-4 ondalıkta tuttu:

- `001be529`: benim pA=0.47806/R2A=0.89120/f12A=0.43379,
  pB=0.86786/R2B=0.80653/f12B=0.38145, dış45=6 — rapor: 0.478/0.891/
  0.434, 0.868/0.807/0.381, 6. **Tuttu.**
- `06f04340`, `08f4fc43`: aynı şekilde tuttu (pA 0.47753/0.46627,
  pB 0.85631/0.83061).
- Medyanlar (pA 0.478, f12A 0.417, pB 0.861, f12B 0.357, işaret 11/96):
  bağımsız arşiv-değeri eşleşmesi + kendi betiklerini `--n-archives 2`
  ile yeniden çalıştırıp aynı arşiv değerlerini üretmem + medyan
  aritmetiğini dizi üzerinden yeniden hesaplamamla destekleniyor.
  KANITLANDI (birleşik).

R²≈0.87/0.78 ve üs-yasası: üs burada **yasa değil tek-sayılık eğim
özetidir**. Bunu sertleştiren iki bağımsız gözetim: (a) `var_C[0] <
var_C[1]` **15/15 arşivde** (normalize sonrası ilk nokta anomalisi —
tek doğru bu kırılmayı yakalayamaz); (b) `001be529` log-log eğimi ilk-32'de
-0.28, son-64'te -0.61 (sistematik eğrisellik). Rapor bunu doğru yönetiyor:
R² açık, SCOPE madde 4 "üs bir özet, yasa değil; kütleyi üsten okumak
yanıltır" diyor. **Üs yorumu dürüst; abartı yok.**

## Truncation: SAYILAR DOĞRULANDI, sonuç DESTEKLENİYOR, köken kayıp

- 3 arşivde kumulatif varyans (k=8..96) bağımsız uyarlamadan **tuttu**
  (örn. `001be529` k64=0.899095).
- Kuyruk: `1-cumvar(64)` medyan **0.0988 → %9.9** ✓; `Var[96]/Var[64]`
  medyan **0.806, aralık 0.776-0.881** ✓ (rapor: ~0.81, %78-88).
- "96 doğal durma noktası değil, tasarımın durduğu yerdir": **geometri
  olarak destekleniyor** (kuyruk %10 taşıyor, sönümlenme sürüyor).
  Rapor geri-getirim maliyetinin ölçülmediğini açıkça yazıyor. 96-bit
  genişliğin bayt bütçesinden geldiği açıkça yazılmıyor ama "dondurulmuş
  tasarımın durduğu yerdir" bunu yanlışlamıyor — **gözlem, ihlal değil**.
- **P1: `TRUNCATION.json`'u üreten betik pakette YOK**
  (`grep TRUNCATION *.py` boş; `measure_spectrum.py` yalnızca
  GATE+SPECTRUM yazar). Sayılar doğru (bağımsız türettim) ama paket
  kendi iddiasındaki gibi yeniden-üretilemez. KANITLANDI.

## Projector: ENVANTER TAM, BAYTLAR BAYTINA TUTTU

Sorgu yolundan bağımsız envanter (prob satır 110) + sklearn kaynağı:

- `TruncatedSVD.transform` kaynağı: `safe_sparse_dot(X, components_.T)`
  — **yalnızca `components_`**, mean/offset yok. `singular_values_` vb.
  dışarıda bırakılması **doğru**. KANITLANDI (kaynak).
- `CountVectorizer.transform`: yalnızca `vocabulary_`;
  `TfidfTransformer.transform`: yalnızca `idf_` + kurucu sabitleri
  (sublinear_tf/norm bayrakları kod sabitidir, uydurma değil).
  Vektör başına kalıcı durum = vocab + IDF. **Eksik yok, fazla yok.**
  7 kalem (2 vocab + 2 IDF + sv + s96 + mu) tamdır. KANITLANDI.
- Kimlik `32 + word + char = combined`: **470/470 tutuyor** → leksik SVD
  bloğu her arşivde tam 32 sütun (N min 396 > 32 olduğundan
  `min(32,N-1,V-1)=32` hep tutar). s96 girdi genişliği de böyle sabitlenir.
- Bayt hesabı 2 arşivde **baytına eşit**: `001be529` a=45050700,
  b=23110902, a_z=24182838; `00ca467f` aynı şekilde. Manşet: medyan etkin
  **88886.36 B/vektör**, oran **7407.2×**, başabaş 3685020/44220235 —
  aritmetik tuttu. KANITLANDI.
- L-088: etkin değer tavana karşı **test edilmiyor** — iki açık feragat
  + JSON'da PASS/FAIL/cap/tavan/violation sözcüğü **yok**. Oran cümlesi
  ("12'nin ~7400 katı") aritmetik bilgi olarak çerçevelenmiş. **Uyumlu.**
  (Yanlış okunmaya davetiye çıkarır, ama feragat açık — gözlem.)

## Ties: YÖN DOĞRULANDI, mekanizma açık, disiplin temiz

- Sınır-bağ çokluğu 2 arşivde **4 ondalığa kadar eşit** (örn. `001be529`:
  med 1, p90 2.0, maks 5, f>1 0.2782, f>3 0.0097). KANITLANDI.
- Ölçek eğilimi **KENDİ tohumumla** (onlarınki 9000+ai, benimki 7777+qi):
  N=50 f>1≈0.56-0.60 → N=200 ≈0.33-0.34 → tam-N ≈0.24-0.28. **N büyüdükçe
  bağ AZALIYOR — doğrulandı.** Mekanizma: N büyüyünce 3. sıra-istatistiği
  (d3) sola, Hamming dağılımının seyrek kuyruğuna kayar; tam-eşitlik
  olasılık kütlesi incelir. Sezgiye aykırı değil, sıra-istatistiğidir.
- Havuz uyarısı: raporda "YÜKSEK SESLİ UYARI" + JSON'da `caveat`, ve havuz
  hiçbir yerde tek-büyük-arşiv gibi kullanılmıyor. **Uyuldu.**
- Reskor: 2766/2783 = **%99.389 → %99.4** ✓. Kalıntı mekanizması:
  en-kötü arşivde (`07741c45`) tam-bağlı 8 skor grubunun **8'i de birebir
  aynı kod (Hamming 0), 0 karşı-örnek**. **Doğrulandı.** KANITLANDI.
- Doğruluk dili: "doğru" geçen 10 isabetin tamamı olumsuzlama/feragat
  ("doğru çözmek DEĞİLDİR", "bakılmadı"). **Bağı doğru çözdüğünü ima eden
  tek cümle yok.** KANITLANDI (taramayla).

## Roles: AYRIM DOĞRULANDI, "48" şüpheli değil, sonuç dürüst

- Bitişik medyan 28-29 vs diğer **48.0**: 2 arşivde **tam eşit**
  (29.0/48.0, 28.5/48.0). Kopya sayımı eşit (≤16: 198, 166).
  Derlem geneli rol sayımı eşit (user 122416, assistant 124334, 246750
  tur, 23867 oturum, 222851/222883 rol-değişimi). KANITLANDI.
- "Diğer medyan 15/15'te tam 48.0": **akıl-sağlığı kontrolüdür, hile
  belirtisi değil.** Dengeli 96-bit kodlarda ikili Hamming dağılımı 48'de
  yoğunlaşır; ~120 bin çiftlik örneklemde ayrık medyanın 48'e oturması
  beklenen sağlamlıktır. Bilgi taşıyan kısım bitişiğin 28'de olmasıdır
  (20 bit ayrım, AUC≈0.95). Dağılım kaymış olsaydı 48 oynamazdı iddiası
  tersine de okunur — ama kosinüs ayrımı (0.77 vs -0.03) bağımsız
  destek verir.
- "Göreli doğru, mutlak yanlış": **dürüst okuma.** Bitişik medyan 28 bit
  (kopya değil), ≤16 çifti tüm çiftlerin %0.14'ü ve çoğulun çoğu (%84)
  bitişik değil. Rapor geri-getirim etkisinin ölçülmediğini açık yazıyor.

## Kesitsel

- **Ölçülen vs çıkarılan: temiz.** Tehlike cümlesi avı (o hâlde/recall
  düşer/doğru çöz/kazanım): 2 isabet, ikisi de YAPILMAYACAK çıkarıyı
  yasaklayan uyarı. Sınırı geçen cümle bulamadım.
- **Re-fit dürüstlüğü: 1 eksik.** Tüm MD/JSON/py beyan taşıyor, **tek
  istisna `REPRODUCE.md`** (0 beyan). P2.
- **Hashler:** spectrum 7/7 ✓, projector 5/5 ✓ (yeniden hesapla tuttu).
  **ties ve roles'ta `HASHES.json` YOK.** P1. KANITLANDI.
- **Çalıştırılabilirlik: 4/4.** Her betik `--n-archives 2` ile çıkış 0,
  kapı geçti, çıktılar yazıldı, sayılar paket değerleriyle eşleşti
  (komutlar aşağıda). Ties küçük-N'de havuz adımını 5 kez aynen
  tekrarlıyor (kozmetik israflık, sonuç doğru — gözlem).
- **Kapsam:** 15 arşiv/tek tohum dışına taşan iddia bulamadım. SCOPE'daki
  "başka arşivde farklı çıkmayacağını denetlemedim" ifadesi dürüst.
- **Kendi-kendini doğrulama:** spectrum SCOPE madde 7 "Bağımsız denetçi
  kapıyı ve medyanları aynen üretti" diyor — denetçi kimliği, kayıt,
  tarih, karma **yok**; diğer 3 paket "bağımsız denetimden geçmedi"
  diyor. **Kaynaksız öz-belgelendirme**, P2. (Bu rapor o boşluğu
  doldurur ama kimliğim gereği kısmi bağımsızlıktır.)

## Çalıştırma kanıtı (tam komutlar, hepsi çıkış 0)

Betiklerim (kendi dizinimde, etiketli): `audit_refit1_gate_spectrum.py`
(31 kapı + 3 spektrum/budama), `audit_gate_weakness.py` (6 varyant),
`audit_projector.py` (envanter + 2 bayt), `audit_ties_roles.py`
(2 bağ + 2 rol + kendi-tohum alt-örnekleme).

Paket betikleri (`--n-archives 2`, `/tmp/audit_run_*` altına):

- `measure_spectrum.py` → GECTI/GECTI, `YAZILDI: GATE.json, SPECTRUM.json`
- `measure_projector.py` → `BOYUT 001be529: a_raw=45050700 ...`,
  `YAZILDI: GATE.json, PROJECTOR_BYTES.json`
- `measure_ties.py` → `YAZILDI: GATE.json, TIES.json`
- `measure_roles.py` → `OLCUM 001be529: bitisik-H-med=29.0
  diger-H-med=48.0`, `YAZILDI: GATE.json, ROLES.json`

Ortam: `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`,
`PYTHONDONTWRITEBYTECODE=1`, `/home/mdp/muse-work/ml-python -B`
(Python 3.14.4, numpy 2.5.3, scipy 1.18.1, sklearn 1.9.1).
Yorumlayıcı+kitaplık sürümleri REPRODUCE.md ile aynı.

## Hüküm

PASS WITH OBSERVATIONS

## Bulgular

- **F-01 | P1 | `spectrum/.../MEASUREMENT_REPORT_TR.md` §1 + tüm `GATE.json`
  dosyaları | Kapı "boru-hattı özdeşliği kanıtı" gibi sunuluyor; oysa
  şekil denetimidir.** Kanıt: `sublinear_tf=False` aynı 4 tamsayıyı verip
  σ'yı 0.44 oynatıyor. Kapatma: raporlara "kapı şekil denetimidir;
  değer-seçenekleri (sublinear_tf, tohumlar, normalizasyon) kapı
  dışındadır, güvence kod özdeşliğidir" cümlesi eklensin. PROVED BY EXECUTION.
- **F-02 | P1 | `spectrum/out/PACKAGE/TRUNCATION.json` | Üreten betik
  pakette yok; yeniden-üretilemez.** Kanıt: `grep TRUNCATION *.py` boş.
  Sayılar doğru (bağımsız türettim). Kapatma: üreten betik/komut pakete
  eklensin ve hash'lensin. PROVED BY EXECUTION.
- **F-03 | P1 | `ties/out/`, `roles/out/` | `HASHES.json` yok;
  bütünlük zinciri eksik.** Kanıt: dizin listesi. Kapatma: spectrum
  biçiminde HASHES.json eklensin. PROVED BY EXECUTION.
- **F-04 | P2 | `spectrum/.../SCOPE_AND_LIMITS_TR.md` madde 7 |
  Kaynaksız "bağımsız denetçi üretti" iddiası; diğer paketlerle çelişiyor.**
  Kanıt: metin + diğer README'lerdeki "denetimden geçmedi". Kapatma:
  iddia ya kanıtıyla (denetçi kaydı) desteklensin ya da silinsin. PROVED BY EXECUTION (metin taraması).
- **F-05 | P2 | `spectrum/.../REPRODUCE.md` | Re-fit beyanı yok
  (0 isabet).** Kapatma: ilk paragrafa beyan eklensin. PROVED BY EXECUTION.
- **F-06 | P2 (gözlem) | projector raporu | "Etkin ≈ 7400×12" oranı
  feragata rağmen tavan-testi gibi okunmaya müsait.** İhlal yok (iki
  feragat + JSON'da test yok). Kapatma gerekmez; aynı çerçeve korunsun. SUSPECTED (okur etkisi, ölçülmedi).
- **F-07 | P2 (gözlem) | ties `measure_ties.py` havuz döngüsü |
  Küçük-N'de aynı havuz 5 kez hesaplanıyor (sonuç doğru).** Kapatma:
  `kk` tekilleştirilsin. PROVED BY EXECUTION.

## Bakmadıklarım (ve neden)

- 470 arşivin tamamında kapı (zaman; 31 arşiv tabakalı örneklem yeterliydi).
- 15 arşivin tamamında sıfırdan spektrum medyanı (3 bağımsız + betik
  determinizmi + medyan aritmetiğiyle kapattım; tam koşu aynı kodu
  tekrarlardı).
- Tohum duyarlılığının tam haritası (tek tohum kapsamı zaten beyanlı).
- `build_archive` çalıştırarak v1/v2 metin eşitliği (etiket sınırı;
  statik takma-ad + v2 içindeki eşitlik kanıtı yeterli).
- Sorgu-yolu uçtan-uca bayt çözme turu (envanter kaynakla kapandı).
- Gold'e dokunan her şey (yasak). "Bulamadım" ≠ "yoktur" — özellikle
  F-06 ve kapsam taraması metin aramasına dayanır.

## Bağımsızlık (tekrar, kısa)

Aynı model ailesi, sıfır hafıza, sıfır erişim: kısmi bağımsızlık. Sayıları
kendi kodumla tutturdum; kapı abartısını ve köken boşluklarını kırdım.
Raporun geri kalanı paket yazarlarına aittir, bana değil.
