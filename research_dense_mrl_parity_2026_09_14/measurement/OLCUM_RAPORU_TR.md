[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# V55 Cephe 1 — Yoğun (dense) MRL kanalı: spektral geometri paritesi

**Beyan edilmiş yeniden-uyarlama (declared re-fit).** Dondurulmuş üretim yapıtı geri
kazanılmadı. Gerçek LongMemEval derlemi üzerinde temsil hattı yeniden uyarlandı ve
yalnızca tanımlayıcı istatistikler okundu.

Tarih: 2026-09-14 · Betik: `measure_mrl_parity.py`

---

## 1. Soru

96 bitlik (12 bayt) bütçenin 48 biti leksikal, 48 biti yoğun bir gömme modeline
ayrılsa, yoğun tarafın ilk 48 nominal ekseni yeterli varyansı taşır mı?

Bu yalnızca MRL (Matryoshka Representation Learning) eğitimi almış modellerde
anlamlıdır: MRL, koordinatları önemliden önemsize dizmeyi öğretir; bu olmadan
"ilk 48" rastgele 48 ile aynıdır.

## 2. Yöntem — dondurulmuş ölçümle birebir parite

`measure_spectrum.py`'den **birebir kopyalanan** iki fonksiyon kullanıldı:
`loglog_fit` (satır 73-87) ve `archive_texts_only`.

- Aynı 15 arşiv, dondurulmuş `V52_T4C2_feature_geometry.csv` sırasında
  (ilk satır `001be529` doğrulandı).
- Aynı metin inşası: `"[tarih] rol: içerik"`.
- Aynı hat: satır L2 → merkezle → `np.var(C, axis=0)` (ddof=0).
- Aynı üs tanımı: `p = -slope` of `ln(var)` vs `ln(rank)`. **Bölme yok.**
- `N` kapısı: her arşivde üretilen metin sayısı dondurulmuş `N_archive` ile
  birebir eşleşmeli. Tüm kollarda **tüm arşivlerde geçti**.

**Sınır uyumu.** Yalnızca `haystack_sessions`, `haystack_dates`,
`haystack_session_ids` okundu. `answer`, `answer_session_ids`, `question`,
`question_type` alanlarına dokunulmadı. Hiçbir retrieval, recall, gold etiketi,
sıralama, benchmark ya da sonuç sayısı hesaplanmadı. Task4F1 mührü bozulmadı.

## 3. Eşikler — sonuçlardan ÖNCE ilan edildi

| ölçüt | kaynak | gereken |
|---|---|---|
| `f_48 ≤ %20 → kanal kapanır` | Gemini karar tablosu | > %20 |
| 4–5× izotropik güçlenme | Gemini hedefi | %25–30 (D=768) |
| leksikal denkliği 2.85× | bu oturum, sonuçlardan önce | %17.8 (D=768) |

Sayı çıktıktan sonra hiçbir eşik değiştirilmedi.

## 4. Sonuçlar

### Aynı eksen kesri (1/8) — elmayla elma

| kol | D | k | f nominal | izotropik taban | güçlenme |
|---|---|---|---|---|---|
| **leksikal SIGN96** (dondurulmuş) | 96 | 12 | **%35.66** | %12.50 | **2.85×** |
| arctic-m-v1.5 (MRL) | 768 | 96 | %20.65 | %12.49 | 1.65× |
| mxbai-large-v1 | 1024 | 128 | %12.60 | %12.49 | 1.01× |
| arctic-xs (negatif kontrol) | 384 | 48 | %12.10 | %12.51 | 0.97× |

### 48 bitlik bütçe sorusu

| kol | D | f_48 nominal | taban | güçlenme | p_B nominal | R² | hizalama | işaret bandı dışı |
|---|---|---|---|---|---|---|---|---|
| arctic-xs (kontrol) | 384 | %12.10 | %12.51 | 0.97× | −0.0169 | 0.003 | %58.6 | 8/384 = %2.08 |
| arctic-m-v1.5 | 768 | %10.61 | %6.25 | 1.70× | +0.3292 | 0.519 | %79.6 | 11/768 = %1.43 |
| mxbai-large-v1 | 1024 | %4.72 | %4.69 | 1.01× | +0.0061 | 0.001 | %65.8 | 15/1024 = %1.46 |
| leksikal (karşılaştırma) | 96 | %84.12 (48/96=1/2) | %50.00 | 1.68× | +0.8607 | 0.779 | — | 11/96 = %11.46 |

"hizalama" = nominal f / sıralı f. **Bu metrik modeller arası kıyas için
kullanılamaz** — bkz. §6b. İzotropik boş tabanda bile %87.8–90.4 çıkar ve
spektral yassılığa bağlıdır. Yalnızca kol-içi tanımlayıcı bir sayı olarak
bırakılmıştır.

Tüm kollarda `[0.30,0.70]` bandı dışı eksen sayısı **sıfır**.

### Kapsam

| kol | arşiv | süre | f_48 yayılımı |
|---|---|---|---|
| arctic-xs | 15/15 | 21.2 dk | 0.476 pp |
| arctic-m-v1.5 | 15/15 | 55.3 dk | 0.450 pp |
| mxbai-large-v1 | **3** | 75.3 dk | 0.186 pp |

`mxbai` 3 arşivde tutuldu.

**DÜZELTME.** Bu kararın ilk gerekçesi hatalıydı: "ilk 3 arşivin medyanı 15
arşivin medyanından 0.005 puan farklı" yazılmıştı. O sayı koşu **sürerken**,
o an biten **10** arşive karşı hesaplanmıştı (`ilk3 − ilk10 = +0.0054`), sonra
"15" diye raporlandı. Bağımsız denetim yakaladı. Tamamlanmış 15 arşive karşı
gerçek farklar:

```
        med15      ilk3 (fark)        ilk6 (fark)
f_48   10.6069   10.6487 (+0.0418)   10.6433 (+0.0364)
f_96   20.6515   20.5884 (-0.0631)   20.5887 (-0.0628)
f_384  65.6685   65.6945 (+0.0260)   65.7061 (+0.0376)
```

Doğru büyüklük 0.005 değil **~0.04–0.06 puan**. Karar yine de ayakta: mxbai'nin
kendi eşiğine marjı **8.66 puan** (ölçülen %4.715, D=1024'te 2.85× eşiği %13.37),
yani 0.06 puanlık örneklem oynaması iki büyüklük mertebesi küçük. Ayrıca mxbai
`arctic-m` ile **aynı ilk 3 arşivde** koşuldu (`001be529`, `00ca467f`, `0100672e`).

## 5. Hüküm

**Yoğun kanal, önceden ilan edilen üç ölçütün üçünü de geçemedi. Cephe kapanıyor.**

En iyi kol (`arctic-m-v1.5`) 48 bitte %10.61 taşıyor; en düşük eşik %17.8 idi.

## 6. Sebep — MRL suçlu değil

`arctic-m-v1.5`'te MRL eksen sıralaması **çalışıyor ve ölçülebilir**. İki
bağımsız kanıt:

1. `p_B nominal = +0.3292` (R² 0.519) — kontrolde `−0.0169` (R² 0.003).
   Nominal eksen sırasında gerçek bir sönümleme var.
2. `f_48` güçlenmesi **1.70×** — kontrolde **0.97×** (tabanın altında).

Üçüncü bir kanıt olarak "hizalama %79.6 vs %58.6" kullanılmıştı; **geri
çekildi**, gerekçesi §6b.

### 6b. Geri çekilen argüman: "hizalama" metriği

Bağımsız denetim (Muse) bu metriğin yanlı olduğunu gösterdi, doğrulandı:

```
kol             gozlenen   IZOTROPIK BOS TABAN   fark      p_srt
arctic-xs         %58.6          %90.4         -31.9 pp    0.311
arctic-m-v1.5     %79.6          %88.5          -8.9 pp    0.419
mxbai-large       %65.8          %87.8         -22.0 pp    0.194
```

Boş tabanda bile hizalama ~%88–90'dır, ve gözlenen üç değerin **üçü de
tabanın altındadır**. Metrik iki şeyi karıştırıyor: eksen sıralaması **ve**
spektral diklik. Düz spektrum (mxbai, `p_srt=0.194`) sıfır sıralamayla bile
dik spektrumdan (kontrol, `p_srt=0.311`) yüksek hizalama üretir — nitekim
mxbai %65.8 ile kontrolün %58.6'sının üstünde çıkmıştır, ve bu **sıralamayla
değil yassılıkla** açıklanır.

Hüküm değişmiyor: yukarıdaki iki kanıt (1) ve (2) bu metrikten bağımsızdır.

Sorun hizalamada değil, **altta yatan spektrumda**: `p_B = 0.329` (R² 0.52),
leksikalde `0.861` (R² 0.78). Leksikal spektrum yaklaşık 2.6 kat daha hızlı sönüyor.

## 7. Yan bulgular

### a) "MRL" etiketi kanıt değil

`mxbai-embed-large-v1` model kartında MRL bölümü var, ama nominal eksenleri
izotropik payın tam olarak kendisini taşıyor (1.01×, `p_B = +0.006`, R² 0.001).
Bu modeli kesmek rastgele boyut seçmekle aynı. İncelendiğinde kartın ilgili
bölümü tekniği **anlatan** genel bir açıklama; modelin matryoshka kaybıyla
eğitildiği iddiası değil.

**Sert kanıt — model `config.json` dosyaları.** Bağımsız denetim bunu buldu,
doğrulandı:

```
snowflake-arctic-embed-m-v1.5    config.json: matryoshka_dimensions = [256]
mxbai-embed-large-v1             matryoshka anahtari YOK
snowflake-arctic-embed-xs        matryoshka anahtari YOK
```

Nominal sıralama gösteren tek kol, config'inde `matryoshka_dimensions` **beyan
eden** tek koldur. Ölçüm ile beyan birebir örtüşüyor. README'deki kelime sayısı
değil, `config.json`'daki bu anahtar delildir.

**Sonuç: MRL kesme planlanıyorsa nominal eksen sıralaması ölçülmelidir**, ya da
en azından `config.json`'da `matryoshka_dimensions` aranmalıdır. Üç modelden
yalnızca biri gerçekten sıralıydı.

### b) İkili kuantalama ile MRL kesme ters yönlere çekiyor (HİPOTEZ)

Üç kolda gözlenen düzen:

| kol | p_B sıralı | işaret bandı dışı |
|---|---|---|
| arctic-m-v1.5 | 0.419 | %1.43 |
| arctic-xs | 0.311 | %2.08 |
| mxbai-large-v1 (ikili kuant. odaklı) | 0.194 | %1.46 |

İkili kuantalama için istenen şey izotropidir — her bit eşit bilgi taşısın.
MRL kesme için istenen şey anizotropidir — varyans ilk eksenlerde toplansın.
`mxbai` üç kolun en düz spektrumuna sahip.

**Bu bir hipotezdir, kanıt değildir.** Üç model üzerinde gözlenen bir düzen;
nedensellik kurmak için kontrollü eğitim karşılaştırması gerekir.

### c) İşaret dengesi yoğun tarafta belirgin olarak daha iyi

| kol | bandı dışı | oran |
|---|---|---|
| leksikal SIGN96 | 11/96 | %11.46 |
| arctic-xs | 8/384 | %2.08 |
| arctic-m-v1.5 | 11/768 | **%1.43** |
| mxbai-large-v1 | 15/1024 | %1.46 |

Yoğun eksenlerin işaret bitleri 1 bit Shannon entropisine leksikalden ~8 kat
daha yakın. Yoğunlaşma sorusundan bağımsız bir avantaj; kayda geçiyor.

### d) Leksikali yarıya indirmenin bedeli ölçüldü: %15.88

Dondurulmuş `SPECTRUM.json` içindeki `var_C` dizilerinden, daha önce
sorulmamış kesme noktaları:

```
f_12 (1/8) = %35.66     f_24 (1/4) = %62.49     f_48 (1/2) = %84.12
```

96 ekseni 48'e indirmek leksikal varyansın yalnızca %15.88'ine mal oluyor.
Hibrit önerisinin maliyet tarafı düşüktü; yoğun kanal yine de altında kaldı.

### e) İzotropik taban tabloları

N=490, 40 tekrar:

```
     D     k     k/D    nominal    sirali    sisme   p_sirali
   384    48   12.50%   12.520%   13.841%   1.106x    0.0592
   768    48    6.25%    6.252%    7.056%   1.129x    0.0584
   768    96   12.50%   12.501%   13.849%   1.108x    0.0589
  1024    48    4.69%    4.693%    5.333%   1.136x    0.0583
  1024   128   12.50%   12.482%   13.845%   1.109x    0.0586
```

Nominal taban `k/D`'yi birebir tutuyor. Sıralı taban **%12.5 değil %13.8** —
saf gürültü bile sıralandığında şişiyor, ve sıralama tek başına `p ≈ 0.059`
üretir. Sıralı sayılar 0 ile değil bu tabanla kıyaslanmalıdır.

## 8. Bu ölçümün SÖYLEMEDİĞİ

**Varyans payı getirim değildir.** Ölçülen, temsilin varyansının ne kadarının
kesmeden sağ çıktığıdır. Getirim kalitesi ayırt edici bilginin sağ kalmasına
bağlıdır ve bu ölçülmedi — Task4F1 mührünün içindedir.

Doğru kayıt: **önceden ilan edilen vekil ölçüt geçilemedi.** Hibrit mimarinin
retrieval'da işe yaramayacağı kanıtlanmadı.

## 9. Bilinen parite açığı: token kesmesi (ölçüldü, hükmü değiştirmiyor)

Yoğun hat `max_length=512` ile çalışır; leksikal hat (TF-IDF kelime+karakter)
**hiç kesmez**, tüm metni görür. Bu bir asimetridir ve raporun ilk sürümünde
açıklanmamıştı.

Büyüklüğü ölçüldü (`trunc_sensitivity.py`, ilk 3 arşiv, arctic-m-v1.5):

```
turlarin %17.03'u 512 token sinirini asiyor
token uzunlugu: medyan 118   p90 598   p99 779   max 3225
```

Etki iki bağımsız tasarımla ölçüldü.

**Tasarım 1 (bu oturum) — alt küme.** Aynı arşivlerde yalnız ≤512 token turlar:

| kol | medyan f_48 | medyan f_96 | medyan p_nom |
|---|---|---|---|
| A: tüm turlar (kesmeli) | %10.649 | %20.588 | +0.3296 |
| B: yalnız ≤512 token (kesme yok) | %10.622 | %20.603 | +0.3306 |
| fark | −0.027 pp | +0.014 pp | +0.0010 |

**Bu tasarımın kusuru var** ve bağımsız denetim işaret etti: alt küme hem
kesmesizliği hem de **seçilimi** taşır (kısa turlar farklı bir örneklemdir).
İki etki ayrışmıyor.

**Tasarım 2 (denetçiden, doğrulandı) — aynı metin, farklı limit.** Metinler
sabit tutulur, yalnız `max_length` sertleştirilir; seçilim etkisi **yok**:

```
                                f48 @512    f48 @256    fark(256-512)    dp
arctic-m-v1.5 (karar kolu)      10.6487%    10.6987%     +0.0500 pp   +0.0014
arctic-xs     (kontrol)         12.0070%    12.0003%     -0.0067 pp   -0.0004
```

Limit yarıya indirildiğinde bile etki **≤0.05 puan**. Eşiğe olan mesafe
**7.2 puan** — yani 140 kat güvenli. Üstelik yön raporu kayırıyor: sert kesme
`f_48`'i bir miktar **yükseltiyor**, yani gerçek (kesmesiz) değer daha da düşük
olurdu. **Kesme hükmü değiştirmiyor.**

Açık kalan: bu yalnızca kesmenin *bu tahmin üzerindeki* etkisini sınırlar.
Kesilen içeriğin getirim değeri taşıyıp taşımadığı ayrı bir sorudur ve
mühürlü sınırın içindedir.

## 10. Batch/padding değişmezliği (kontrol edildi)

Betik metinleri uzunluğa göre sıralayıp gruplar; bu, batch bileşimini
değiştirir. Değişmezlik doğrulandı (arctic-m-v1.5, 64 metin):

```
batch=8  vs batch=1 : mutlak max fark 6.557e-07
batch=64 vs batch=1 : mutlak max fark 6.557e-07
f_48 nominal: batch 1/8/64 -> 0.09928286 (sekiz ondalik basamak ayni)
```

## 11. En cömert çerçevede bile hüküm değişmiyor

Bağımsız denetimin açtığı dal: leksikal eksenler SVD çıktısı olduğu için
**zaten optimal sıralı**; yoğun tarafın nominal eksenleriyle kıyaslamak yoğun
tarafa haksızlık olabilir. Adil kıyas, leksikal nominal (=optimal) ile yoğun
**sıralı** (=optimal) arasında olurdu. Bu, yoğun tarafa verilebilecek en cömert
çerçevedir. Ölçüldü, aynı 1/8 eksen kesrinde:

| kol | k | f **sıralı** | sıralı taban | güçlenme |
|---|---|---|---|---|
| **leksikal f_12** (nominal = optimal) | 12 | **%35.66** | %12.50 | **2.85×** |
| arctic-m-v1.5 | 96 | %24.36 | %13.84 | 1.76× |
| arctic-xs | 48 | %20.66 | %13.84 | 1.49× |
| mxbai-large-v1 | 128 | %17.41 | %13.85 | 1.26× |

En iyi yoğun kol, mümkün olan en iyi 96 ekseni seçtiğinde bile %24.36'da
kalıyor. Leksikal üstünlüğü mutlakta 1.46×, güçlenmede 1.62×.

**Hüküm en cömert çerçevede de ayakta.**

## 12. Bağımsız denetim kaydı

Denetçi: Muse Code (`muse-spark-1.3`, `--reasoning-effort xhigh`), salt okunur,
soğuk başlangıç, düşmanca brif. Görev dosyası 13 numaralı iddia içeriyordu.
Rapor: `MUSE_DENETIM_V55.md`.

**Hüküm: `FAIL-FIXABLE`** — kapanış hükmü sağlam, üç metin/metrik kusuru var.

| denetim bulgusu | bağımsız doğrulama | bu raporda |
|---|---|---|
| "hizalama" metriği yanlı (boş taban %87.8–90.4) | **doğrulandı** | §6b, argüman geri çekildi |
| kapsam gerekçesindeki 0.005 sayısı tutmuyor | **doğrulandı** | §4, düzeltildi |
| %17 kesme asimetrisi raporda yok | **doğrulandı** | §9, eklendi |
| `str()+concat` vs f-string ayrışması (bilgi) | doğrulandı, etkisiz | onarım gerekmedi |
| `matryoshka_dimensions` config kanıtı | **doğrulandı** | §7a, rapora eklendi |

Uydurma bulgu yok; sağlam yerde icat edilmiş kusur yok. Denetçinin kaçırdığı
tek şey batch/padding değişmezliği idi — kusur bulunmadığı için (§10).

**Bağımsızlık sınırı.** Denetçi ile ölçümü yapan aynı model ailesinden.
Soğuk başlangıç ve düşmanca brif uygulandı, ama bu **kısmi bağımsızlıktır.**

## 13. Sınırlar

- 15 arşiv (mxbai'de 3), 470 arşivin alt kümesi, tek tohum.
- Güç yasası uyumları kusurlu (`arctic-m` nominal R² = 0.52). Üsler özettir, yasa değil.
- Üç model, hepsi encoder ailesinden. Genelleme kurulmadı.
- Ölçümler tek bir model ailesinin oturumunca üretildi; bağımsız denetim yapılmadı.
