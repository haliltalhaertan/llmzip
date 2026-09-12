# V52 statik depolama sözleşmesi — inceleme paketi

**DRAFT / NOT APPROVED / NO MEASUREMENT / NO EXECUTION AUTHORIZATION.**

Ana belge: [Beş sorulu ölçüm sözleşmesi](MEASUREMENT_CONTRACT_TR.md).

- Ölçülen nesne: dondurulmuş, arşiv-yerel temsil/index paketinin kalıcı baytları.
- Sabitler: eğitim/model durumu, paylaşım politikası ve serileştirme; her N görüntüsünde gerçek paylaşım nüfusu ayrı.
- Muhasebe: bütün zorunlu vektör başına durum 12 B tavanına dahil; model/projektör durumu gerçek fiziksel kopyası ve `D_k` paydasıyla ayrı.
- Karar: mevcut marjinal uygunluk, kapsam ve kaynak sorunları; toplam bütçe veya yüzde eşiği eklenmiyor.
- Durma: eksiksiz olağan sonuçta doğrulama notu olarak kapanış; eksik kaynakta PARTIAL/UNKNOWN, otomatik yeni deney yok.

İlk bağımsız inceleme üç düzeltme istedi: zorunlu abort'un açık taşınması, toplam bayt ile B/vektör biriminin ayrılması, yalnız tekilleştirilmiş doğrulanmış kalemlerden alt sınır kurulması. İlk taslak ve inceleme `bc642c64b7f0d24995427e51fbea2969afca885a` commit'inde korunur. [İlk inceleme](INDEPENDENT_DESIGN_REVIEW.md) o baytlar için geçerlidir. [İlk delta inceleme](INDEPENDENT_DESIGN_DELTA_REVIEW.md), `d936455e2938a37da2b1a934f912cc2705b07ad3` sürümünü kapatır; sonraki revizyona hükmü taşınmaz.

Beş bulgulu takip revizyonu: (1) tam prob/arşiv panelinin ölçüm öncesi hash'le bağlanması, (2) çıkarma/geri koyma ve sentetik kimlik/offset kontrolleri, (3) UNKNOWN'ın sayıyla aynı cümle/nesnede taşınması, (4) makine planı ve guard, (5) arşiv-ağırlıklı başlık seçimi. Alt sınır etiketi de başlıkla birlikte taşınır. [Güncel bağımsız inceleme](INDEPENDENT_FIVE_FINDINGS_REVIEW.md) tam belge ve guard hash'lerine bağlanır. Hiçbir inceleme gerçek maliyet ölçümü veya bilimsel onay değildir.

Makine tarafı: [plan arayüzü](PLAN_INTERFACE.md), `MEASUREMENT_PLAN.template.json`, `measurement_plan_guard.py` ve sentetik guard testleri. Şablon gerçek envanter içermez ve NOT_READY durumunda ölçüm için reddedilir. Gerçek projektör adaptörü henüz yoktur; onun guard'a bağlandığı ve işlevsel çıkarma kontrollerini uyguladığı ayrıca doğrulanmalıdır. Bu eksik, sentetik testlerin geçmesiyle kapanmaz.

Bütçe kararının ham Git dosyası ve sidecar `source/` altında; commit/yol/digest bağları `SOURCE_BINDINGS.json` içindedir. `FILE_HASHES.json` kendisi dışındaki tüm paket dosyalarını bağlar.

Depo kökünden salt-okuma kimlik kontrolü:

```powershell
python -B drafts/v52/static_storage_contract_2026_09_12/verify_draft.py
```

Bu kontrol dosya kimliği ve kaynak bağları içindir; model açmaz, maliyet hesaplamaz, taslağa onay vermez. `--write` paketleme sırasında mevcut dosyalardan manifesti yeniden üretir; eski manifestler Git geçmişinde kalır. Kaynak/inceleme kimlik kontrolleri manifest yazılmadan da uygulanır.

Sonraki adım belgenin incelemesidir. Projektör dosyalarının varlığı, tam envanter ve ölçüm/prob planı ayrıca doğrulanmalıdır. Bu taslak onları varmış veya çalıştırmaya hazırmış saymaz. main/ledger, mühür ve Task4F1 sınırları değişmez.
