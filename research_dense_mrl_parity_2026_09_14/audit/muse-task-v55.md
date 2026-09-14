# Denetçi görevi — V55 Cephe 1 yoğun MRL kanalı ölçümü

Sen bağımsız bir DENETÇİsin. Görevin bu çalışma alanındaki iddiaları **kırmaya
çalışmak**, onaylamak değil. Sana sunulan gerekçeyi doğru varsayma.

## Kapsam

`sonuclar/OLCUM_RAPORU_TR.md` içindeki ölçüm iddiaları ve bunları üreten
`kod/measure_mrl_parity.py`.

Çalışma alanı:

```
kod/measure_mrl_parity.py    ana ölçüm betiği (denetlenen)
kod/null_baseline.py         izotropik boş hipotez (D=384)
kod/null2.py                 izotropik boş hipotez (D=384/768/1024)
kod/trunc_sensitivity.py     bir duyarlılık kontrolü
kod/bug_loader.py            harici bir betiğin yükleyici hatasının gösterimi
kod/det_test.py              list(set(...)) determinizm testi
sonuclar/MRL_PARITY_*.json   üç kolun ham çıktısı (denetlenen)
sonuclar/OLCUM_RAPORU_TR.md  rapor (denetlenen)
referans/measure_spectrum.py DONDURULMUŞ leksikal ölçüm — parite kaynağı
referans/SPECTRUM.json       DONDURULMUŞ leksikal sonuç (per_archive.var_C dahil)
referans/GATE.json           dondurulmuş kapı kaydı
referans/V52_T4C2_feature_geometry.csv   dondurulmuş geometri tablosu
```

Derlem: `/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json` (277 MB).
Python: `python3` (torch 2.14 cpu, transformers 5.17, numpy 2.5.3 kurulu).
Modeller HF önbelleğinde mevcut, ağ da açık.

Bir kolu tam yeniden koşmak 20–75 dakika sürer. Nokta kontrolü tercih et
(tek arşiv, `--n-archives 1`); tam koşuya yalnız gerekiyorsa gir.

## Denetim kipi — Kip B: Matematiksel/kanıtsal geçerlilik

Odak: her adımın öncekinden gerçekten çıkıp çıkmadığı. Örtük varsayım,
niceleyici kayması, sabitlerin sessizce değişmesi. **Sayısal iddiaları fiilen
hesapla.** Karşı-örnek arayabiliyorsan ara.

## Kırmaya çalışacağın numaralı iddialar

**İ-1 (parite).** `measure_mrl_parity.py` içindeki `loglog_fit` ve
`archive_texts_only`, `referans/measure_spectrum.py` içindekilerle
**birebir aynı davranıyor**. Farklı davrandıkları bir girdi var mı?

**İ-2 (üs tanımı).** `p_B = -slope` doğrudan `ln(var)` üzerinde; bölme yok ve
bu dondurulmuş tarafla aynı konvansiyon. Doğrula.

**İ-3 (leksikal türetilmiş sayılar).** `referans/SPECTRUM.json`'daki
`per_archive[].var_C` dizilerinden 15 arşiv medyanı olarak:
`f_12 = %35.66`, `f_48 = %84.12`, "96→48 maliyeti = %15.88",
"leksikal güçlenme = 2.85×", "2.85× eşiği D=768 k=48 için %17.83".
Her birini yeniden hesapla.

**İ-4 (kol sonuçları).** JSON'lardan: arctic-xs `f_48 = %12.099` (0.97×),
arctic-m-v1.5 `f_48 = %10.607` (1.70×), mxbai-large `f_48 = %4.715` (1.01×).
Güçlenme oranları JSON'daki `isotropic_null` ile tutarlı mı?

**İ-5 (izotropik taban).** İddia: nominal taban `k/D`'ye eşittir ama **sıralı**
taban değildir (1/8 kesirde %13.8) ve sıralama tek başına `p ≈ 0.059` üretir.
Kendi simülasyonunu yaz, doğrula ya da çürüt.

**İ-6 (hizalama).** "nominal/sıralı" oranının MRL eksen sıralamasını ölçtüğü
iddiası: arctic-m %79.6, kontrol %58.6, mxbai %65.8. Bu metrik iddia edileni
ölçüyor mu, yoksa `k/D` ile mekanik olarak mı değişiyor? mxbai'nin kontrolden
yüksek çıkması iddiayla çelişiyor mu?

**İ-7 (hüküm).** "Üç önceden ilan edilmiş eşiğin üçü de geçilemedi, cephe
kapanıyor." En iyi kol %10.61, en düşük eşik %17.83. Eşikler sayı görüldükten
sonra değiştirilmiş mi? Rapor §3 ile §5 tutarlı mı?

**İ-8 (MRL çalışıyor iddiası).** arctic-m için `p_nom = +0.3292` (R² 0.519)
"MRL sıralaması çalışıyor"un kanıtı sayılıyor; kontrolde `−0.0169` (R² 0.003).
R² 0.519 bir güç yasası iddiasını taşıyacak kadar iyi mi? Rapor bunu aşırı mı
yorumluyor?

**İ-9 (mxbai iddiası).** "mxbai nominal eksenlerinde hiç sıralama yok"
(1.01×, `p = +0.006`, R² 0.001). Pooling doğru mu (CLS vs mean)? Yanlış pooling
ya da eksik prefix bu sonucu üretmiş olabilir mi? Model kartını/config'i kontrol et.

**İ-10 (işaret dengesi).** "Yoğun taraf leksikalden ~8 kat daha dengeli"
(%1.43 vs %11.46). Farklı `D`'lerde bant-dışı **oranını** karşılaştırmak adil mi?
Bu oran `D` ile mekanik olarak değişir mi?

**İ-11 (mühür uyumu).** Betik `answer`, `answer_session_ids`, `question`,
`question_type` alanlarına hiç dokunmuyor; hiçbir retrieval/recall hesaplanmıyor.
Kodu okuyarak doğrula ya da ihlal göster.

**İ-12 (kapsam dürüstlüğü).** mxbai yalnız 3 arşivde koşuldu. Gerekçe:
"arctic-m'de ilk 3 arşivin medyanı 15 arşivinkinden 0.005 puan farklı."
Bu gerekçe mxbai'ye taşınabilir mi, yoksa kolların yayılımı farklı mı?

**İ-13 (hipotez etiketi).** Rapor §7b "ikili kuantalama ile MRL kesme ters
yönlere çeker" iddiasını **hipotez** olarak etiketliyor. Etiket doğru mu, yoksa
metin onu kanıtlanmış gibi mi kullanıyor? Üç gözlemden nedensellik çıkarılmış mı?

## Ayrıca özellikle şuna bak

**Leksikal hat ile yoğun hat arasında, raporun AÇIKLAMADIĞI bir parite açığı
var mı?** İki hat aynı metinleri aynı şekilde mi görüyor? Girdi işlemede,
ön işlemede, uzunluk/kapasite sınırlarında, normalizasyonda ya da örneklemede
raporun sessiz kaldığı bir asimetri ara. Bulursan büyüklüğünü **ölç** — hükmü
değiştirecek kadar büyük mü?

## Kurallar

1. **Salt okunur çalış.** Hiçbir dosyayı değiştirme, oluşturma veya silme
   (kendi geçici dosyaların `/tmp` altında olabilir). Git geçmişine dokunma.
2. Her iddiayı kaynağına kadar takip et. "Muhtemelen doğru" yeterli değil —
   ya `dosya:satır` göster, ya çürüt.
3. Doğrulayamadığın adımı **boşluk** olarak işaretle; iyimser yorumlama.
4. Gözle okumakla yetinme; **çalıştırılabilir olanı çalıştır.**
5. **Kusur icat etme.** Ekilmemiş yerde bulgu üretmek, kusuru kaçırmak kadar
   kötüdür. Bulgu yoksa "yok" yaz.
6. Rapor Türkçe, kod yorumları Türkçe. Raporunu **Türkçe** yaz.

## Çıktı formatı

Sadece şu yapıda cevap ver:

### HÜKÜM
`VALID` | `FAIL-FIXABLE` | `FAIL-FATAL` | `UNVERIFIABLE`
İ-1'den İ-13'e her iddia için ayrı satır, artı genel hüküm.

### GEREKÇE
Hükmü veren belirleyici argüman. En fazla 8 cümle.

### BULGULAR
Her biri için:
- **[ciddiyet]** `dosya:satır` — kusurun tek cümlelik ifadesi
  - Somut kırılma senaryosu (girdi/durum → beklenen vs. gerçek)
  - Onarılabilir mi, nasıl

### DOĞRULANAMAYANLAR
Kontrol edemediğin adımlar ve neden.

### KAPANMAYAN DALLAR
Denetimden sonra hâlâ açık kalan sorular.

Övgü, özet veya nezaket cümlesi ekleme.
