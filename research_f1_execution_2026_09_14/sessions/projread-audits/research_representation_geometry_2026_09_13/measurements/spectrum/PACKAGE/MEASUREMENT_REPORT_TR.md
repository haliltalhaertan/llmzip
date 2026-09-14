[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Ölçüm raporu (Türkçe)

**Beyan edilmiş YENİDEN-UYARLAMA:** Bu dizin dondurulmuş üretim yapıtı
değildir. Temsil hattı (`fit_archive_representation` + SVD96, tohum 5204)
gerçek derlem üzerinde yeniden uyarlandı; yalnızca tanımlayıcı
istatistikler (tekil değerler, koordinat başına varyans) okundu.
Retrieval, recall/doğruluk, altın/kanıt etiketi, sıralama, kıyaslama
hesaplanmadı. Buradaki hiçbir sayı bir değerlendirme sonucu değildir.

## 1. Kapı: GEÇTİ (15/15)

Her hücrede beklenen = ölçülen; tamamı birebir eşleşti. Ayrıntı `GATE.json`.

| arşiv | N | söz / kar / bir | kapı |
|---|---|---|---|
| 001be529 | 514 | 39940 / 59943 / 99915 | GEÇTİ |
| 00ca467f | 486 | 38846 / 54711 / 93589 | GEÇTİ |
| 0100672e | 486 | 41054 / 57162 / 98248 | GEÇTİ |
| 01493427 | 487 | 39327 / 56463 / 95822 | GEÇTİ |
| 031748ae | 494 | 39940 / 57039 / 97011 | GEÇTİ |
| 06878be2 | 443 | 40797 / 61852 / 102681 | GEÇTİ |
| 06db6396 | 479 | 39011 / 56009 / 95052 | GEÇTİ |
| 06f04340 | 503 | 40212 / 60496 / 100740 | GEÇTİ |
| 07741c44 | 513 | 38768 / 53232 / 92032 | GEÇTİ |
| 07741c45 | 527 | 38354 / 61140 / 99526 | GEÇTİ |
| 078150f1 | 551 | 39388 / 58586 / 98006 | GEÇTİ |
| 07b6f563 | 524 | 39414 / 56424 / 95870 | GEÇTİ |
| 0862e8bf | 490 | 37377 / 58769 / 96178 | GEÇTİ |
| 08e075c7 | 484 | 39962 / 57926 / 97920 | GEÇTİ |
| 08f4fc43 | 480 | 39853 / 59997 / 99882 | GEÇTİ |

## 2. (A) ve (B) yan yana

(A): ham SVD spektrumu, `ln σ = α − p·ln i` uyumu; f12 = ilk 12
bileşenin `σ²` kütlesi. (B): yöntemin gördüğü varyans, aynı uyum
`Var(C)` üzerinde; f12 = ilk 12 koordinatın `Var(C)` kütlesi.
Ham sayılar `SPECTRUM.json` dosyasındadır.

| arşiv | p_A | R²_A | f12_A | p_B | R²_B | f12_B |
|---|---|---|---|---|---|---|
| 001be529 | 0.478 | 0.891 | 0.434 | 0.868 | 0.807 | 0.381 |
| 00ca467f | 0.474 | 0.866 | 0.410 | 0.830 | 0.735 | 0.346 |
| 0100672e | 0.478 | 0.870 | 0.416 | 0.848 | 0.758 | 0.352 |
| 01493427 | 0.476 | 0.857 | 0.404 | 0.850 | 0.752 | 0.341 |
| 031748ae | 0.477 | 0.874 | 0.416 | 0.861 | 0.784 | 0.355 |
| 06878be2 | 0.470 | 0.870 | 0.417 | 0.831 | 0.753 | 0.358 |
| 06db6396 | 0.473 | 0.870 | 0.409 | 0.845 | 0.772 | 0.348 |
| 06f04340 | 0.478 | 0.880 | 0.423 | 0.856 | 0.779 | 0.366 |
| 07741c44 | 0.478 | 0.872 | 0.417 | 0.861 | 0.785 | 0.353 |
| 07741c45 | 0.483 | 0.884 | 0.427 | 0.878 | 0.804 | 0.378 |
| 078150f1 | 0.496 | 0.919 | 0.466 | 0.875 | 0.781 | 0.403 |
| 07b6f563 | 0.486 | 0.884 | 0.429 | 0.866 | 0.782 | 0.370 |
| 0862e8bf | 0.479 | 0.888 | 0.425 | 0.866 | 0.794 | 0.373 |
| 08e075c7 | 0.485 | 0.870 | 0.418 | 0.869 | 0.772 | 0.357 |
| 08f4fc43 | 0.466 | 0.879 | 0.415 | 0.831 | 0.777 | 0.354 |

Toplu (15 arşiv): p_A medyan 0.478 (0.466–0.496);
f12_A medyan 0.417 (0.404–0.466); p_B medyan 0.861 (0.830–0.878);
f12_B medyan 0.357 (0.341–0.403); R²_A medyan 0.87, R²_B medyan 0.78.

## 3. İşaret dengesi

`occ` = işaretli koordinatta `C >= 0` oranı (N üzerinden).

| arşiv | [0.45,0.55] dışı | [0.30,0.70] dışı | occ min–maks |
|---|---|---|---|
| 001be529 | 6 | 0 | 0.391–0.562 |
| 00ca467f | 11 | 0 | 0.352–0.574 |
| 0100672e | 10 | 0 | 0.418–0.599 |
| 01493427 | 7 | 0 | 0.374–0.593 |
| 031748ae | 11 | 0 | 0.419–0.581 |
| 06878be2 | 14 | 0 | 0.413–0.587 |
| 06db6396 | 8 | 0 | 0.374–0.551 |
| 06f04340 | 11 | 0 | 0.388–0.581 |
| 07741c44 | 8 | 0 | 0.407–0.589 |
| 07741c45 | 14 | 0 | 0.400–0.634 |
| 078150f1 | 5 | 0 | 0.323–0.554 |
| 07b6f563 | 11 | 0 | 0.389–0.574 |
| 0862e8bf | 13 | 0 | 0.392–0.612 |
| 08e075c7 | 10 | 1 | 0.283–0.564 |
| 08f4fc43 | 13 | 0 | 0.365–0.592 |

Medyan: [0.45,0.55] dışında 11/96; [0.30,0.70] dışında 0/96
(tek arşivde 1). Neredeyse hiçbir koordinat tek işarete çökmüş değil.

## 4. İki öngörüye hüküm

- "p ∈ [1.5, 2.5], varyansın %99.7'si ilk 12'de": **ÇÜRÜTÜLDÜ.**
  Ölçülen p_A ≈ 0.478, f12_A ≈ %41.7.
- "p ≈ 0.25–0.55, ilk 12'de %20–30": üs **DOĞRULANDI** (0.478 bu
  aralıkta); eşlik eden kütle sayısı **doğrulanmadı** (gerçek ≈ %42).
  İkisi ayrı söylenir: üs tutar, kütle tutmaz.

## 5. (A)/(B) ayrışması başlı başına bulgudur

Δp ≈ 0.38. Hattın satır-normalizasyonu bileşenler-arası ölçeği yok
ettiği için Var(C), σ'dan türetilemez; doğrudan ölçülmelidir.
Bilginin "nerede yaşadığı" üzerine σ ile kurulan her sav yanlış
niceliğe bakıyordu. (B) için hiçbir taraf öngörüde bulunmamıştı:
p_B ≈ 0.861, f12_B ≈ 0.357 olduğu gibi raporlanır, iki kampa da
sokulmaz.

## 6. Budama taraması (Job 2; geometri, retrieval yok)

`SPECTRUM.json` içindeki `Var(C)` ve işaret profillerinden okundu;
yeniden-uyarlama ve geri-getirim hesaplanmadı. Ham sayılar
`TRUNCATION.json` dosyasındadır (arşiv başına + medyan/min/maks).

| k | korunan Var(C) medyan | aralık | [0.45,0.55] dışı medyan |
|---|---|---|---|
| 8 | 0.250 | 0.237–0.295 | 4 |
| 12 | 0.357 | 0.341–0.403 | 5 |
| 16 | 0.453 | 0.438–0.498 | 5 |
| 24 | 0.625 | 0.612–0.656 | 7 |
| 32 | 0.761 | 0.750–0.770 | 10 |
| 48 | 0.841 | 0.833–0.845 | 10 |
| 64 | 0.901 | 0.896–0.905 | 11 |
| 96 | 1.000 | — | 11 |

[0.30,0.70] dışı her k'de medyan 0 (en fazla 1, tek arşivde).
İşaret dengesi budamayla bozulmuyor; kuyruk koordinatları da
çökmüş değil.

Kuyruk: son 32 koordinat toplam `Var(C)`'nin medyan %9.9'unu taşır
(%9.6–%10.4). 96. koordinatın varyansı 64. koordinatınkinin
medyan ~%81'i (aralık %78–%88); kuyruk yatay değil, yavaşça
sönümlenmeye devam ediyor. Yani 96 doğal bir durma noktası değil;
dondurulmuş tasarımın durduğu yerdir. Kalan %10'un geri-getirime
maliyeti ölçülmedi (yasaklı kapsam); geometri olarak kuyruk
hâlâ ciddidir.

## Kapanış

- Kapı: GEÇTİ, 15/15 birebir.
- (A) medyan: p_A = 0.478, f12_A = 0.417.
- (B) medyan: p_B = 0.861, f12_B = 0.357.
- Ayrışma: üste ≈ 0.38; ilk-12 kütlesinde ≈ 6 puan.
- Budama: k=64 %90'ı korur; son 32 koordinat %10 taşır,
  kuyruk sönümleniyor ama düz değil.
- Bakılmayanlar `SCOPE_AND_LIMITS_TR.md` dosyasındadır.
