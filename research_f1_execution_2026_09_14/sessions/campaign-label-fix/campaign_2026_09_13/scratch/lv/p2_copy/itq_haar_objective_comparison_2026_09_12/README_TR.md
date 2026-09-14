[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# ITQ–Haar amaç karşılaştırması: mevcut kanıtın açılması ve dar tekrar doğrulama

İstenen Haar amaç karşılaştırması önceki `4001fc9d8ea2c932042de7823713c6efce8e56d0` teslimatında zaten vardı. `task3/RESULTS.json` içindeki `haar_null_objective` ve `haar_null_objectives_per_rotation` alanları, ayrı 20 Haar tohumu için değerleri taşıyor. Önceki kısa Markdown tablosu bu sütunu göstermediği için bulgu görünmez kalmıştı. Ayrıca `initial_objective` de ITQ'nun rastgele Haar başlangıcındaki amaç değeridir.

Bu ek, mevcut veriyi/tohumları değiştirmeden 240 başlangıç ve 240 ayrı Haar-null amaç değerini tekrar hesapladı: **480/480 değer tam eşleşti; 12 veri matrisinin ham bayt kimliği de aynı.** Yeni ITQ eğitimi yapılmadı. Tablodaki öğrenilmiş ITQ değerleri hash'e bağlı tarihsel sonuçlardan alındı; bu turda yeniden fit edilmediler. Bu, yeni bir deney veya ön-kayıt değildir; sonuçlar görülmüşken yapılmış açıkça belirtilen doğrulama ve sunum ekidir.

## Heterojen sentetik panel

Amaç, `mean((abs(Y @ R)-1)^2)`; matris elemanı başına eğitim kuantizasyon hatasıdır. Düşük değer daha iyidir. Her hücre aynı sabit veri matrisinde 20 rotasyonun ortalamasıdır.

| Vektör sayısı n | Ayrı Haar-null | Öğrenilmiş ITQ (tarihsel) | Haar ortalamasına göre hata azalması |
|---:|---:|---:|---:|
| 100 | 0,406219550 | 0,169813814 | %58,20 |
| 250 | 0,402167760 | 0,225467448 | %43,94 |
| 500 | 0,408987465 | 0,266277022 | %34,89 |
| 1000 | 0,408419700 | 0,299033856 | %26,78 |

n=500 için başlangıç-Haar ortalaması `0.4088637361`, ayrı Haar-null ortalaması `0.4089874654`, öğrenilmiş ITQ ortalaması `0.2662770224`. Yüzde, `100*(1 - mean(ITQ)/mean(Haar-null))` olarak hesaplandı; tohumlar arasında eşleştirilmiş etki tahmini değildir. Bütün 12 panelin ortalama/aralık/standart sapmaları `replay/RESULTS.json` içindedir; hiçbir dağılım veya n sonuca göre elenmedi.

## Bilimsel dispozisyon

- **Bu panelde ITQ eğitim kuantizasyon hatasına katkı sağlıyor.** Bu nedenle ITQ'yu “zaten Haar ile aynı şeyi yapıyor” gerekçesiyle dışlamak desteklenmiyor.
- İşaret/permutasyon hizalı rotasyon uzaklığının Haar–Haar uzaklığına yakın olması, aynı rotasyon dağılımını, matematiksel tanımlanamazlığı veya gereken örneklemin astronomik olduğunu kanıtlamaz. Tek bir uzaklık özeti dağılım eşitliği testi değildir.
- Eğitim amaç kazancı, retrieval kazancı değildir. Held-out hata, gerçek temsil matrisi ve arama kalitesi ölçülmedi. Bir amaç değerinin düşük/eşit çıkması tek başına “kol şart” veya “ITQ hiçbir şey katmıyor” kararını vermez. Her n için yalnız bir veri gerçekleşmesi ve koşullar arasında tekrar kullanılan tohumlar vardır.
- Gaussian panelde de n=500 eğitim hata azalması %36,85'tir. Dolayısıyla bu gözlemi yalnız heterojenliğe özgü mekanizma kanıtı olarak sunmuyoruz. Eğitimde optimize edilen amaçtaki kazancın genellenmesi ayrıca incelenmelidir.
- **Araştırma önerisi:** ITQ olasılığını açık tut; nihai kol seçimini uygunluk, dağıtım maliyeti ve önceden ilan edilen bilimsel kontrastla gerekçelendir. Bu ek bir kol kabulü veya çalışma yetkisi değildir.

## Notta düzeltilen diğer çıkarımlar

1. `RABITQ32_PLAIN` ve `RABITQ32_ROTATED` adları ayrı, ölçülmüş uygulama zincirlerine bağlandı: `CONFIGURATION_PROPOSAL.md`. Bu taslak ek, mevcut yayımlanmış ön-kayıt taslağının baytlarını değiştirmez; bilimsel kol onayı vermez.
2. Plain uygulamaya makalenin garantisi otomatik taşınamaz; rotasyon wrapper'ının varlığı da tek başına bütün teorem koşullarını doğrulamaz. “Sınır var/yok” ikili etiketi kullanılmadı. Eşlenmiş rotasyon müdahalesi bir karşılaştırma önerisidir; doğrudan Xiao mekanizması kanıtı değildir.
3. Önceki tanı `H_sign(>=0)` içindi; sıfır kütlesi bilinmediğinden istenen `>0` tanısıyla özdeşleştirilemez. 0,75 evrensel literatür karar eşiği doğrulanmış değildir. `CV(sigma)=0.4974774993` betimsel varyans heterojenliğidir, bunun yerine geçen doğrulanmış bir seçim kuralı değildir.
4. İlk32 koordinatın ortalama varyans payı `0.7598736235`, retrieval kaybının zararsızlığını veya d32 karşılaştırmasının adilliğini göstermez. Kalan varyansın görev açısından önemi ölçülmedi. Kaynak: önceki teslimatın `LITERATURE_ASSESSMENT_TR.md` ve Task1 raporunun açık sınırları.
5. Eski `fix/g3-membership-remediation-2026-09-11` dalının HEAD'i `077474013d95d6f343d31385d8a57d42fb72f721`; bu tarihsel main'dir, güncel `2d03bf83e1b39c71947b608a59df31b489a65d4d` ile aynı değildir. Dal teslimat rotası olarak DEPRECATED olarak işaretlenecek. Geçerli G3 teslimatı `7266160ac03bdd064fe75f058eae3430fbe14496`; kabul kaydı L-094. Kullanıcının özgün çalışma ağacı/index'i ve dalı korunur.
6. Arşivler arası global fit/paylaşım ayrı bir dağıtım konfigürasyonudur. Bu ek o konfigürasyonu seçmez veya maliyetini ölçmez.

## Kaynak ve tekrar üretim

`source/` altındaki üç dosya doğrudan yukarıdaki Git commit'inin ham nesnelerinden alındı. Orijinal yollar `research/v52/preseal_diagnostics_2026_09_12/itq_feasibility_synthetic.py` ve `task3/{PLAN,RESULTS}.json` idi. Betik hem SHA-256'ları hem karşılıklı kaynak/plan bağlarını kontrol eder. Kaynak modülünü import etmez; hiçbir ITQ fit veya retrieval fonksiyonu çağırmaz.

```powershell
# Depo kökünden; kilitli ortam Python3.13.15 / NumPy2.3.5 / SciPy1.17.0.
python -B research/v52/itq_haar_objective_comparison_2026_09_12/replay_objectives.py --output replay_fresh
```

Çıktı klasörü yeni olmalıdır. Sayısal tekrarı paketin ayrı bir kopyasında yapın: yeni çıktı, özgün dosya envanterine ek dosya sayılır. `python -B research/v52/itq_haar_objective_comparison_2026_09_12/verify_package.py` özgün paketin tüm dosyalarını salt-okuma ile doğrular. Aynı ham matris ve sonuç baytlarını üretmeyen ortamda replay betiği hata verir; toleransla geçirmez. Sıfır, ikili kod, skaler oracle, işaret/permutasyon değişmezliği ve yanlış-işaret negatif kontrolleri çalışır. Bu kontroller ve dar replay, bütün tarihsel ITQ optimizasyonunun yeniden denetimi sayılmaz.

Sınır: gerçek korpus/query/gold, yeni retrieval sonucu, Task4F1 run/finalize/HMAC/seal veya production authorization yoktur. Task4F1 SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN durumu değişmez.
