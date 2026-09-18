[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Router pilotu — önce tavan, sonra tahmin

`evidence_path`: `audit_hard_r4/ROUTER_PILOT.json`, `router_pilot.py` — **sıfır model çağrısı**

Dış değerlendirmenin dayattığı sıra izlendi: **önce oracle tavanı, sonra gerçek tahmin.**

---

## Adım 1 — Oracle tavanı: +5,49 pp (gürültüden arındırılmış)

Her sorguda `sign96+Jev` ile `BM25+Jev` arasından **doğru olanı** seçebilseydik:

| | FR@3 |
|---|---:|
| hep sign96 | 70,37 |
| hep BM25 | 72,48 |
| **ORACLE** | **78,43** |
| anti-oracle (hep yanlışı seç) | 64,42 |

Ham oracle kazancı **+5,95 pp**. Yöntemler 112/470 sorguda (%23,8) farklı sonuç veriyor;
50'sinde sign96, 62'sinde BM25 kazanıyor.

### Ama ham oracle şişirilmiş — gürültü tabanı ölçüldü

`max(a, b)` yalnız gerçek farkı değil, **model kararsızlığını da** toplar. Bunu niceliklendirmek
için **aynı sistemin iki bağımsız koşusunu** oracle'ladım (`BM25+Jev`, L-103 ve L-107):

| | FR@3 |
|---|---:|
| koşu 1 | 72,48 |
| koşu 2 | 72,09 |
| "oracle" (max) | 72,94 |
| **sahte kazanç** | **+0,46 pp** |

Aynı sistem, 14/470 sorguda farklı sonuç veriyor. Yani oracle'ın **+0,46 puanı saf gürültü**.

> **Gerçek tavan: +5,95 − 0,46 = +5,49 pp.**

Senin eşiğine göre (+0,5 değersiz, +5–10 değerli) bu **araştırmaya değer** bir tavan.

---

## Adım 2 — Tahmin edilebilir mi? **HAYIR**

13 ucuz runtime özelliği: sorgu uzunluğu, sayı/tarih içeriyor mu, zamansal kelime, BM25 top-1
skoru ve marjı, sign96 top-1 skoru ve marjı, iki yöntem aynı belgeyi mi buldu, top-10 örtüşmesi,
arşiv boyutu, skor dağılımı istatistikleri.

**Dürüstlük kuralları:** train/test ayrıldı, router yalnız train'den öğrendi, **200 rastgele
bölünme** (tek bölünme post-selection riski taşır), gürültü tabanı ayrıca ölçüldü.

| model | kazanç | SD | %95 aralık | pozitif çıkan |
|---|---:|---:|---|---:|
| logistic regression | −0,21 | 0,62 | [−2,12, +0,00] | 1/200 |
| logreg (dengeli) | −2,43 | 1,43 | [−5,31, −0,03] | 5/200 |
| karar ağacı (d=3) | −1,49 | 1,48 | [−4,47, +1,07] | 29/200 |
| random forest | −0,80 | 1,02 | [−2,65, +1,13] | 42/200 |
| — test oracle tavanı | **+5,92** | | | |

**Dört modelin dördü de negatif.** Hiçbiri tavanın hiçbir kısmını yakalayamıyor.

### Doğruluk metriği yanıltıcı — kaydedildi

İlk model %88,9 doğruluk verdi, kulağa iyi geliyor. Ama:

- Etiket dağılımı: sign96 yalnız **50/470** sorguda kazanıyor (%10,6)
- Çoğunluk tabanı (**hep BM25 de**) = %89,4
- Yani router, **hiçbir şey yapmayandan da kötü**

Üstelik doğruluk zaten yanlış metrik: 358 sorguda iki yöntem **aynı** sonucu veriyor, orada seçim
önemsiz. Karar metriği FR@3 kazancıdır — o da negatif.

---

## Sonuç: seçim tahmin edilebilir değil (bu özelliklerle)

> **Tavan gerçek (+5,49 pp) ama erişilemiyor.** Denenen 13 ucuz sinyalin hiçbiri, hangi yöntemin
> kazanacağını önceden söylemiyor.

Bu, projenin daha önce ölçtüğü bir bulguyla **tutarlı**: L-109'da sözlüksel örtüşme ile yöntem
farkı arasındaki korelasyon **r ≈ 0,02** çıkmıştı. Senin uyarın da aynı yöndeydi: *"insan gözüyle
'bu lexical soru, BM25 kullan' demek güvenilir olmayabilir."* Şimdi 13 özellikli bir öğrenici de
aynı sonucu veriyor.

### Yöntem anlaşmazlığı sinyali de işe yaramadı

Önerdiğin en umut verici sinyal — iki yöntemin top-1'i aynı mı, top-10 örtüşmesi ne — özellik
kümesinde vardı ve **yetmedi**. Anlaşmazlık "belirsizlik" gösteriyor olabilir, ama **hangi tarafın
haklı olduğunu** göstermiyor.

---

## Bu ne kapatır, ne kapatmaz

**Kapandı:** ucuz runtime özellikleriyle ikili router (sign96 vs BM25), dört model ailesiyle.

**Kapanmadı:**

| | durum |
|---|---|
| Dört çıkışlı router (BM25 / sign96 / ikisi / zor) | ölçülmedi |
| Jev'in kendisinin router olması (sorgu başına bir yargı) | ölçülmedi — **maliyetli** |
| Daha zengin özellikler (varlık türleri, soru tipi sınıflandırması) | ölçülmedi |
| Başka veri kümesinde aynı tavan | ölçülmedi |

**Önemli sınır:** bu, "routing imkânsız" demek değil. *"Bu 13 ucuz sinyalle, bu veri kümesinde,
bu iki yöntem arasında"* demek. Tavan hâlâ orada duruyor — yalnız anahtarı bulunamadı.

---

## Sınırlar

- n=470, tek veri kümesi, **ayrılmış sınav verisi yok** (200 bölünme iç doğrulama, dış değil)
- Etiketler Jev'in tek koşusundan; koşu kararsızlığı 14/470 sorguda etiketi çevirebilir
- `sign96` kodlayıcısı yok, sorgu-tarafı özellikler sınırlı
