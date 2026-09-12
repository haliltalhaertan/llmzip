# V52 mühür öncesi temsil tanıları — 2026-09-12

Taban commit: `ae9175676b840ae6a80a31eba9836187dc1b7491`.
Dal: `research/v52-preseal-diagnostics-2026-09-12`.
G-3 uygulaması `24d3351f068f6982148c14a9e3338c29a2769449` olarak teslim
edildikten ve bağımsız incelemeye bırakıldıktan sonra bu ayrı çalışma başladı.

**Task 1 kısmen tamamlandı; tam matris bulunmuş gibi raporlanmıyor.** Drive'dan
LongMemEval'in 470 arşivi için yayımlanmış native heterogeneity CSV'si kurtarıldı.
Metin aktarımından sonra özgün CRLF satır sonları korundu ve dosyanın 1.947.381
baytı yayımlanmış SHA256 ile birebir eşleşti:
`148ae5b727ce1aedc6c84ee9c00727f1454b0e0710d100ac8154fdf8d00924cb`.
[Drive kaynağı](https://drive.google.com/file/d/1PME-hZHxp3fRN0AYgygp1oM7v-GNYm6Z/view).

| LongMemEval, eşit arşiv ağırlığı | Ortalama | Kapsam |
|---|---:|---|
| İşaret entropisi, `>=0` | 0,997034 | Minimum 0,991037; 0,75 altında 0/470 |
| Koordinat standart sapmalarının CV'si | 0,497477 | Varyansların CV'siyle karıştırılmadı |
| En yüksek varyanslı 16 koordinatın payı | %46,9089 | Mevcut sıradaki ilk16: %45,8213 |
| En yüksek varyanslı 32 koordinatın payı | %75,9874 | Bu CSV'de ilk32 ile sayısal olarak aynı |
| En yüksek varyanslı 48 koordinatın payı | %83,9457 | Mevcut sıradaki ilk48: %83,9404 |

Bu, 96'dan mevcut ilk32 koordinata geçişte ortalama yaklaşık **%24,01 varyansın
dışarıda kaldığını** gösterir. Bu oran kalite kaybı veya bir karşılaştırıcının
adilliği değildir. Yüksek işaret entropisi ile heterojen koordinat varyansları
aynı temsilde birlikte bulunabiliyor; biri diğerinin yerine kullanılmıyor.

**Eksikler:** Task dosyasındaki `>0` entropisi için sıfır kütlesi gerekli; kaynak
CSV yalnız `>=0` oranını kaydetmiş. Bunlar sessizce eşitlenmedi. Tam korelasyon
matrisi olmadan D4'ün Frobenius oranı, medyanı ve p95'i hesaplanamaz. LoCoMo için
aynı dondurulmuş matris veya yeterli koordinat istatistikleri bulunamadı.
Bu yüzden Task1'in tam geçiş durumu OPEN kalıyor.

Üretici kaynak hash'i
`8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`
doğrulandı; kaynak yalnız statik okundu, import/execute edilmedi. Kod `C` matrisini
`cache_repr/*.pkl` içine sorgu ve gold alanlarıyla birlikte yazıyor, fakat ZIP'e
alınacak dosyaların açık listesi bu önbelleği dışarıda bırakıyor. Pickle açılmadı.
Drive ZIP aktarımları yerel olarak kullanılamayan `sediment` referansı döndürdü;
ZIP merkez dizinleri incelenmiş gibi bir iddia yok. Klasör envanteri ve sınırlar
`task1/SOURCE_INVENTORY.json` içinde. İlk geniş yerel dosya adı taraması BEAM dosya
adlarını da döndürdü; içerikleri açılmadı ve sonraki tarama yalnız üç mekanizma
klonuna daraltıldı. Bu, geniş taramanın kapsam sapmasıdır; sonuç verisi okunmadı.

Literatürün sabit sürüm ve uygulama kimliği kontrolü
`LITERATURE_ASSESSMENT_TR.md` içindedir. **0,75 evrensel bir karar eşiği olarak
doğrulanmadı**; yalnız görevde istenen yerel betimsel kesim olarak hesaplandı.
Bu sonuçtan rotasyon kararı, yayınlanmış mekanizmanın doğrulanması veya yöntem
kazananı çıkarılmadı. D1'in istenen strict-positive biçimi halen eksik olduğundan
o biçim için eşik tarafı veya literatürle çelişki ilan edilmiyor.

## Yeniden üretim ve kanıt

Python3.13.15 / NumPy2.3.5 ile:

```text
python -B research/v52/preseal_diagnostics_2026_09_12/measure_representation_diagnostics.py
```

Bu komut hash'i sabit CSV'yi okur, Task1 çıktısını yeniden yazar. Yeni bir scratch
klonda çalıştırın. Altı ayırt edici sentetik kontrol; entropi uçları, sigma/variance
ayrımı, sabit koordinat maskesi, bilinen korelasyon, `>=0` bilgisinden `>0`'ın
belirlenememesi ve dejenere durumları sınar. Tam matris fonksiyonu bu teslimde
yalnız sentetik kontrollerde kullanıldı. Gerçek matris üzerinde D4 çalıştırılmadı.

`RESULTS.json` üç görevin durumunu bir arada tutar. `ENVIRONMENT.json` her görev
için gerçek ortamı kaydeder. `HASHES.txt` kendi dışında bu namespace'in tüm
dosyalarını hash'ler; recursive self-hash yoktur. Task2 ve Task3 ayrı çalışma
sonuçları geldikçe ayrı commit/push ile eklenecek; ilk commit yalnız Task1'dir.

Hiçbir gerçek sorgu-belge uzaklığı, top-k, recall, yöntem skoru veya gerçek ITQ
fit'i hesaplanmadı. Ön-kayıt değiştirilmedi; yöntem kolları seçilmedi. Task4F1
deneyi, seal/finalize/HMAC veya production authorization yoktur.
