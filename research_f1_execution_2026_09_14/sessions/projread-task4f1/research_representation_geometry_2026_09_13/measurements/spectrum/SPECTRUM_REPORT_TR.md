[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Spektrum ölçüm raporu (Türkçe)

**Beyan edilmiş YENİDEN-UYARLAMA (declared re-fit):** bu rapor dondurulmuş
üretim yapıtının geri kazanımı değildir. Temsil hattı (`fit_archive_
representation` + SVD96, tohum 5204) gerçek derlem üzerinde yeniden
uyarlanıp yalnızca tanımlayıcı istatistikler okundu. Retrieval, recall,
altın etiket, sıralama, kıyaslama hesaplanmadı.

## 1. Kapı: GEÇTİ (15/15)

Her hücrede beklenen=ölçülen yazıldı; tamamı birebir eşleşti.

| arşiv | N | söz/kar/bir | kapı |
|---|---|---|---|
| 001be529 | 514 | 39940/59943/99915 | GEÇTİ |
| 00ca467f | 486 | 38846/54711/93589 | GEÇTİ |
| 0100672e | 486 | 41054/57162/98248 | GEÇTİ |
| 01493427 | 487 | 39327/56463/95822 | GEÇTİ |
| 031748ae | 494 | 39940/57039/97011 | GEÇTİ |
| 06878be2 | 443 | 40797/61852/102681 | GEÇTİ |
| 06db6396 | 479 | 39011/56009/95052 | GEÇTİ |
| 06f04340 | 503 | 40212/60496/100740 | GEÇTİ |
| 07741c44 | 513 | 38768/53232/92032 | GEÇTİ |
| 07741c45 | 527 | 38354/61140/99526 | GEÇTİ |
| 078150f1 | 551 | 39388/58586/98006 | GEÇTİ |
| 07b6f563 | 524 | 39414/56424/95870 | GEÇTİ |
| 0862e8bf | 490 | 37377/58769/96178 | GEÇTİ |
| 08e075c7 | 484 | 39962/57926/97920 | GEÇTİ |
| 08f4fc43 | 480 | 39853/59997/99882 | GEÇTİ |

Tam beklenen/ölçülen çiftleri `GATE.json` dosyasındadır.

## 2. (A) ham SVD spektrumu

| arşiv | p_A | R²_A | f12_A |
|---|---|---|---|
| 001be529 | 0.478 | 0.891 | 0.434 |
| 00ca467f | 0.474 | 0.866 | 0.410 |
| 0100672e | 0.478 | 0.870 | 0.416 |
| 01493427 | 0.476 | 0.857 | 0.404 |
| 031748ae | 0.477 | 0.874 | 0.416 |
| 06878be2 | 0.470 | 0.870 | 0.417 |
| 06db6396 | 0.473 | 0.870 | 0.409 |
| 06f04340 | 0.478 | 0.880 | 0.423 |
| 07741c44 | 0.478 | 0.872 | 0.417 |
| 07741c45 | 0.483 | 0.884 | 0.427 |
| 078150f1 | 0.496 | 0.919 | 0.466 |
| 07b6f563 | 0.486 | 0.884 | 0.429 |
| 0862e8bf | 0.479 | 0.888 | 0.425 |
| 08e075c7 | 0.485 | 0.870 | 0.418 |
| 08f4fc43 | 0.466 | 0.879 | 0.415 |

## 3. (B) yöntemin gördüğü varyans

| arşiv | p_B | R²_B | f12_B |
|---|---|---|---|
| 001be529 | 0.868 | 0.807 | 0.381 |
| 00ca467f | 0.830 | 0.735 | 0.346 |
| 0100672e | 0.848 | 0.758 | 0.352 |
| 01493427 | 0.850 | 0.752 | 0.341 |
| 031748ae | 0.861 | 0.784 | 0.355 |
| 06878be2 | 0.831 | 0.753 | 0.358 |
| 06db6396 | 0.846 | 0.772 | 0.348 |
| 06f04340 | 0.856 | 0.779 | 0.366 |
| 07741c44 | 0.861 | 0.785 | 0.353 |
| 07741c45 | 0.878 | 0.804 | 0.378 |
| 078150f1 | 0.875 | 0.781 | 0.403 |
| 07b6f563 | 0.866 | 0.782 | 0.370 |
| 0862e8bf | 0.866 | 0.794 | 0.373 |
| 08e075c7 | 0.869 | 0.772 | 0.357 |
| 08f4fc43 | 0.831 | 0.777 | 0.354 |

İşaret dengesi: [0.45,0.55] dışında kalan koordinat medyan 11/96
(aralık 5–14); [0.3,0.7] dışında medyan 0 (en fazla 1, tek arşivde).
Yani neredeyse hiçbir koordinat çökmüş (tek işaretli) değil.

## 4. Toplu dağılım (15 arşiv)

| ölçüt | medyan | min | maks |
|---|---|---|---|
| p_A | 0.478 | 0.466 | 0.496 |
| R²_A | 0.874 | 0.857 | 0.919 |
| f12_A | 0.417 | 0.404 | 0.466 |
| p_B | 0.861 | 0.830 | 0.878 |
| R²_B | 0.779 | 0.735 | 0.807 |
| f12_B | 0.357 | 0.341 | 0.403 |

## 5. Hüküm

- (A) için `p ∈ [1.5, 2.5]` ve "%99.7 ilk-12'de" iddiası **çürütüldü**:
  ölçülen p ≈ 0.47–0.50, ilk-12 kütlesi ≈ %40–47.
- Yavaş-azalma iddiası (p ≈ 0.25–0.55) **üs bakımından doğrulandı**
  (0.478 bu aralıkta); ancak eşlik eden "%20–30" kütle sayısı tutmadı,
  gerçek değer daha yüksek (%42). Saf üs-yasası varsayımı kütleyi
  olduğundan küçük gösterir (R²_A ≈ 0.87, tam üs yasası değil).
- (A)–(B) ayrışması: p_B − p_A ≈ 0.38; varyans biriminde 2·p_A ≈ 0.96'ya
  karşı p_B ≈ 0.86 (fark ≈ 0.09); ilk-12 kütlesi %41.7'ye karşı %35.7
  (fark ≈ 6 puan); üs yasası (A)'ya daha iyi uyar (R² 0.87'ye 0.78).
  Ana bulgu: satır-normalizasyon bileşenler-arası ölçeği yok ettiği için
  Var(C) σ'dan çıkarılamaz; doğrudan ölçülmelidir.
- (B) için hiçbir taraf öngörüde bulunmamıştı: p_B ≈ 0.86, f12_B ≈ 0.36
  olduğu gibi raporlanır; iki kampa da sokulmaz.

## 6. Sınırlılıklar ve bakılmayanlar

- Yalnızca sözlüksel sıradaki ilk 15 arşiv ölçüldü; 470 arşivin tamamı
  çalıştırılmadı (ucuzdu ama 15 yeterli görüldü). Başka arşivlerde
  farklı çıkmayacağını **denetlemedim**; yanlış olduğunu söylemiyorum.
- Başka SVD tohumları, başka bileşen sayıları, üs-dışı uyumlar
  (üstel vb.) denenmedi.
- Koordinat düşürmenin geri-getirime etkisi **bilerek** ölçülmedi
  (mühürlü Task4F1 yasağı); bu rapor o konuda susar.
- Yöntem: `ln σ = α − p·ln i` en küçük kareler; R² aynı log-log
  doğrusal uyumundur; varyans `ddof=0` ile `np.var(C,0)`'dır.

## Kapanış

- Kapı: GEÇTİ, 15/15 birebir.
- (A) medyan: p_A = 0.478, f12_A = 0.417.
- (B) medyan: p_B = 0.861, f12_B = 0.357.
- Ayrışma: üste ≈ 0.38; ilk-12 kütlesinde ≈ 6 puan; uyumda R² ≈ 0.87/0.78.
- Hayatta kalan: yavaş-azalma öngörüsü (üs olarak); %99.7 iddiası çürütüldü.
- Bakılmayan: tam 470 arşiv, başka tohumlar, üs-dışı uyumlar, düşürmenin
  geri-getirim bedeli (yasaklı). "Bakmadım" ile "yanlış" ayrıdır.
