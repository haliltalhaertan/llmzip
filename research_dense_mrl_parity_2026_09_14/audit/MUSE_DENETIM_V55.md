### HÜKÜM

- İ-1: `VALID` (gerçek girdi uzayında; egzotik sınır notuyla)
- İ-2: `VALID`
- İ-3: `VALID`
- İ-4: `VALID`
- İ-5: `VALID`
- İ-6: `FAIL-FIXABLE`
- İ-7: `VALID` (sayı tutarlılığı) / `UNVERIFIABLE` (ilan zaman sırası)
- İ-8: `VALID`
- İ-9: `VALID`
- İ-10: `VALID`
- İ-11: `VALID`
- İ-12: `FAIL-FIXABLE`
- İ-13: `VALID`
- Genel: `FAIL-FIXABLE`

### GEREKÇE

Kapanış hükmü sayısal olarak sağlam: en iyi kol %10.61, en düşük eşik %17.83, fark 7.2 puan ve bulabildiğim her yanlılık ≤0.05 puan ya da hükmü destekler yönde. Uçtan uca bağımsız yeniden üretimde iki kolun ilk arşivi JSON değerleriyle basamak basamak tuttu (xs f48 %12.007, m f48 %10.649). Buna karşılık raporda düzeltilmesi gereken gerçek kusurlar var: "hizalama" metriği sıralamayı değil spektral yassılığı ölçüyor, mxbai kapsam gerekçesindeki 0.005 sayısı tutmuyor ve %17'lik kesme asimetrisi raporda hiç anılmıyor. Bunların hiçbiri hükmü değiştirmiyor; hepsi metin/metrik düzeltmesiyle kapanır.

### BULGULAR

- **[orta]** `sonuclar/OLCUM_RAPORU_TR.md:70-71` — "hizalama nominal f / sıralı f, MRL dizilişini ölçer" tanımı yanlı
  - Kırılma: çalışmanın kendi `isotropic_null` değerlerinden boş-tabanda hizalama %87.8–90.4 çıkıyor (xs %90.4, m %88.5, mxbai %87.8; kendi simülasyonumla doğruladım); gözlenen %58.6/%79.6/%65.8'in üçü de bunun altında. Sıralamasız iki kolda hizalama farkı (mxbai %65.8 > kontrol %58.6) sıfır sıralamayla tamamen açıklanıyor: `f_nom≈k/D` iken payda `f_srt` spektral dikliğe bağlı (kontrol `p_srt=0.311` → %58.6, mxbai `p_srt=0.194` → %65.8). Yani metrik modeller arası sıralılık karşılaştırması yapamaz; yassı spektrum tek başına yüksek "hizalama" üretir.
  - Onarım: §4'teki "%100 = optimal" cümlesi ve §6'daki "hizalama %79.6 (kontrolde %58.6)" destek argümanı çıkarılsın ya da boş-taban (%~90) açıklanarak yalnızca kol-içi tanıma indirgensin; sıralılık kanıtı `p_nom`/güçlenme üzerinde dursun.
- **[düşük]** `sonuclar/OLCUM_RAPORU_TR.md:83-84` — "ilk 3 arşiv medyanı 15 arşivinkinden 0.005 puan, ilk 6 arşivinki 0.000 puan farklı" sayısı üretilemiyor
  - Kırılma: JSON'lardan arctic-m `f_48` için ilk3−med15 = +0.0418 puan, ilk6−med15 = +0.0364 puan (`f_96`: −0.0631/−0.0628; `f_384`: +0.0260/+0.0376; `p_nom`: 0.3296/0.3280'a karşı 0.3292). Hiçbir `k`'da 0.005/0.000 tutmuyor (tek tesadüfi eşleşme: ilk3−ilk6 farkı 0.0054 puan, iddia edilen karşılaştırma değil). Ayrıca yayılım kollar arası farklı varsayımı test edilmedi: mxbai'nin kendi 3 değerinde 4.891 aykırısı var (yayılım 0.186 puan).
  - Onarım: cümle gerçek farklarla (+0.04 puan mertebesi) düzeltilsin; hüküm yine de korunur çünkü mxbai marjı ~9 puan (4.72'ye karşı D=1024'te 2.85× eşiği %13.36) ve mxbai aynı ilk 3 arşivde (`001be529`, `00ca467f`, `0100672e`) koşuldu.
- **[düşük]** `sonuclar/OLCUM_RAPORU_TR.md:22-33` — raporda hiç anılmayan kesme asimetrisi: yoğun hat turların ~%17'sini 512 tokenda kesiyor, leksikal TF-IDF hattı tam metni görüyor
  - Kırılma/ölçüm: 5 arşivde tokenizer ile ölçtüm — 512 üstü tur oranı %15.76–%19.84 (max 3225 token); yani "aynı metin inşası" iddiası dize düzeyinde doğru ama modelin gördüğü girdi düzeyinde eksik. Etkiyi aynı metinlerde 512'ye karşı 256 limitle ölçtüm: xs'te Δf48 = −0.007 puan, karar kolu arctic-m'de Δf48 = +0.050 puan, Δp = +0.0014. Eşik farkı 7.2 puan olduğundan hüküm 100 kattan güvenli; yön de raporu kayırıyor (sert kesme f48'i biraz yükseltiyor).
  - Onarım: §2'ye tek cümle ("yoğun hatta ~%17 tur 512'de kesilir; tek arşiv duyarlılık deneyi etkiyi ≤0.05 puan buldu") eklensin. Not: `kod/trunc_sensitivity.py` bu deneyi tarif ediyor ama örneklemi karıştırıyor (kısa-tur alt kümesi hem seçilim hem kesmesizlik etkisi taşır) ve koşulmuş çıktısı yok; benim aynı-metin 512/256 karşılaştırmam daha temiz.
- **[bilgi]** `kod/measure_mrl_parity.py:43-59` — `archive_texts_only` dondurulmuş kopyadan `str()+concat` vs f-string ile ayrışıyor, yalnızca JSON-dışı girdide
  - Kırılma: `__format__`'ı `__str__`'den farklı tanımlı bir nesne (`date`/`role`) iki fonksiyonda farklı dizeye dönüşür; 7 `loglog_fit` diferansiyel durumunda (sıfır/negatif/tek/boş/sabit dahil hata davranışına kadar) ve gerçek derlemde 3 arşivde (N=514/486/486, metinler birebir aynı) tam eşitlik buldum. JSON'dan gelen `str/None/sayı` tiplerinde ayrışma imkânsız.
  - Onarım gerekmez; istenirse birebir aynılık için f-string'e çevrilir.

Doğrulananlar (kısa): İ-2'de `p=-slope`, `ln(var)` üzerinde bölmesiz, iki tarafta aynı (`measure_mrl_parity.py:26-39,94-112`; `measure_spectrum.py:73-87,189-191`). İ-3'ün beşi de `SPECTRUM.json` `var_C` medyanlarından basamak basamak tuttu (f_12 %35.6648, f_24 %62.4894, f_48 %84.1216, maliyet %15.8784, 2.8532×, eşik %17.8324). İ-4'te üç kolun f48 ve güçlenme oranları JSON `isotropic_null` ile tutarlı (0.967/1.697/1.006 → %97/%170/%101 değil rapordaki 0.97×/1.70×/1.01×). İ-5'i bağımsız tohum ve kodla ürettim: nominal ≈ k/D, sıralı 1/8'de ≈ %13.85, `p_srt` ≈ 0.059. İ-9'da pooling doğru: üç modelin resmî `1_Pooling/config.json`'unda CLS pooling; mxbai kartı prompt'u yalnızca sorgular için istiyor (dokümanlarda prefix yok doğru); `max_position_embeddings=512` üçünde de limit; mxbai config'inde `matryoshka_dimensions` yokken arctic-m'de `[256]` var — §7a okuması kanıtlı. İ-11'de mühür temiz: betik yalnızca `haystack_*` ve `question_id` okuyor (`measure_mrl_parity.py:43-59,142-166`); `answer`/`question` yalnızca yorumlarda geçiyor.

### DOĞRULANAMAYANLAR

- İ-7 zaman sırası: §3 eşiklerinin sonuçlardan önce ilan edildiği workspace'ten doğrulanamıyor — tüm dosya zaman damgaları paketleme anına ait, ön-kayıt yok (raporun kendi etiketi de `[NOT PREREGISTERED]`). Sayı tutarlılığı (§3 eşikleri ↔ §5 hükmü, en düşük %17.8'e karşı %10.61) doğrulandı; yalnızca "değiştirilmedi" iddiası boşluk.
- Kapsam tablosundaki süreler (21.2/55.3/75.3 dk): koşu kaydı yok, doğrulanamadı (hükme etkisiz).
- `mxbai` 15 arşive tamamlansaydı medyanın ne çıkacağı: kestirilemedi (mevcut 3 değerle marj ~9 puan olduğundan hüküm duyarsız).
- `bug_loader.py` / `det_test.py`: harici yükleyici eleştirileri, rapora sayı akıtmıyor; iddia zinciri dışında.

### KAPANMAYAN DALLAR

- Leksikal "nominal" eksenler SVD çıktısı gereği zaten varyansa göre dizili olduğundan leksikal 2.85×'in içinde bedava bir sıralama avantajı var; rapor bunu açıkça tartışmıyor — 2.85× eşiğinin yorumunu yumuşatır mı?
- Yoğun işaret dengesi boş-tabana (%~0) göre 60–100 kat, leksikale göre ~8 kat dengeli; §7c yalnızca ikinci oranı veriyor — mutlak tablo eklenmeli mi?
- mxbai'nin yassı spektrumu eğitim hedefinden mi (ikili kuantalama) yoksa veri/ mimari etkisinden mi (§7b hipotezi)? Üç gözlemle ayrıştırılamaz; kontrollü eğitim karşılaştırması gerekir.
