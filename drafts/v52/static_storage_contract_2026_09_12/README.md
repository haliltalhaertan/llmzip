# V52 statik depolama sözleşmesi — inceleme paketi

**DRAFT / NOT APPROVED / NO MEASUREMENT / NO EXECUTION AUTHORIZATION.**

Ana belge: [Beş sorulu ölçüm sözleşmesi](MEASUREMENT_CONTRACT_TR.md).

- Ölçülen nesne: dondurulmuş, arşiv-yerel temsil/index paketinin kalıcı baytları.
- Sabitler: eğitim/model durumu, paylaşım politikası ve serileştirme; her N görüntüsünde gerçek paylaşım nüfusu ayrı.
- Muhasebe: bütün zorunlu vektör başına durum 12 B tavanına dahil; model/projektör durumu gerçek fiziksel kopyası ve `D_k` paydasıyla ayrı.
- Karar: mevcut marjinal uygunluk, kapsam ve kaynak sorunları; toplam bütçe veya yüzde eşiği eklenmiyor.
- Durma: eksiksiz olağan sonuçta doğrulama notu olarak kapanış; eksik kaynakta PARTIAL/UNKNOWN, otomatik yeni deney yok.

İlk bağımsız inceleme üç düzeltme istedi: zorunlu abort'un açık taşınması, toplam bayt ile B/vektör biriminin ayrılması, yalnız tekilleştirilmiş doğrulanmış kalemlerden alt sınır kurulması. İlk taslak ve inceleme `bc642c64b7f0d24995427e51fbea2969afca885a` commit'inde korunur. [İlk inceleme](INDEPENDENT_DESIGN_REVIEW.md) o baytlar için geçerlidir. [Delta inceleme](INDEPENDENT_DESIGN_DELTA_REVIEW.md) güncel belgenin hash'ine ve düzeltmelere ilişkin kapsamlı hükmü taşır. Hiçbiri ölçüm sonucu veya bilimsel onay değildir.

Bütçe kararının ham Git dosyası ve sidecar `source/` altında; commit/yol/digest bağları `SOURCE_BINDINGS.json` içindedir. `FILE_HASHES.json` kendisi dışındaki tüm paket dosyalarını bağlar.

Depo kökünden salt-okuma kimlik kontrolü:

```powershell
python -B drafts/v52/static_storage_contract_2026_09_12/verify_draft.py
```

Bu kontrol dosya kimliği ve kaynak bağları içindir; model açmaz, maliyet hesaplamaz, taslağa onay vermez. `--write` yalnız ilk paketleme sırasında yeni manifest üretmek içindir.

Sonraki adım belgenin incelemesidir. Projektör dosyalarının varlığı, tam envanter ve ölçüm/prob planı ayrıca doğrulanmalıdır. Bu taslak onları varmış veya çalıştırmaya hazırmış saymaz. main/ledger, mühür ve Task4F1 sınırları değişmez.
