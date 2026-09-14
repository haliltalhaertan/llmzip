# V52 real storage adapter interface

Status: **DESIGN PREP / NOT IMPLEMENTED / NOT EXECUTABLE**.

Bu arayüz gelecekte `measurement_plan_guard.py` ile bağlanacak gerçek storage callback/runner için hazırlanmıştır. Sentetik guard testleri bu adapter'ın çalıştığını kanıtlamaz.

## Source resolver

Her item ölçüm öncesi şu statülerden birine çözülür:
- `PERSISTED_ARTIFACT_VERIFIED`: locator + raw SHA256 + byte length + serialization doğrulanmış.
- `DETERMINISTIC_REGENERATION_VERIFIED`: küçük persisted state ve exact pinned regeneration yolu doğrulanmış; reference digest mevcut.
- `REGENERATION_CANDIDATE_NOT_VERIFIED`: run-ready değil.
- `UNKNOWN`: run-ready değil.

`NOT_LOCATED` sıfır bayt sayılmaz.

## Reopen testi

Her archive/config/format temiz süreçte yalnız declared persistent package, declared runtime dependency ve hash-bound sentetik fixture ile yeniden açılır. Eksik fitted state yeniden fit edilmez.

`TRANSFORM` baseline, önceden bağlanmış sentetik reference identity ile `MATCH` vermelidir.

## Item kontrolleri

Known INCLUDED/EXCLUDED item için:
- BASELINE: değişiklik yok.
- REMOVE: yalnız hedef physical copy çıkarılır.
- RESTORE: çıkarılmadan önceki **aynı baytlar** geri konur.
- CORRUPT: planda literal verilen byte/bit bozması uygulanır; uygulanamazsa neden planda frozen `NA` olmalıdır.

Adapter sidecar logunda copy id, before/after SHA256, byte length ve operation id taşınır. Sadece byte sayısının aynı olması içerik eşitliği kanıtı değildir.

## ID / offset mapping

Sentetik toy payload tablosu kullanılır. Ayrı alanlar:
- `logical_id_exists`
- `package_stores_id`
- `implicit_mapping_reproducible`
- `external_boundary_dependency`
- `mapping_status`

Zero-byte mapping ancak process restart sonrasında declared package ile doğru toy payload'a exact mapping gösterilirse kabul edilebilir.

## Byte accounting

Her physical copy için raw persistent byte length + raw SHA256 kaydedilir. Header, sidecar ve metadata item roster'a map edilir; açıklanamayan byte `UNACCOUNTED` olarak fail-closed kalır.

Her probe için BEFORE=`N`, AFTER=`N+q` aynı frozen shared state ile ölçülür. Runner `delta_bytes` ve `delta_bytes/q` değerlerini ayrı taşır.

SHARED item için frozen model altında byte length değişmemeli; ayrıca raw SHA256 eşitliği kontrol edilir.

## Physical copies

Her SHARED copy actual locator, artifact identity, SHA256, population ids ve `D_k` ile literal olarak planda bulunur. Hash eşitliği global paylaşım kanıtı değildir. Archive-local fit tek-copy veya `D_k=N_i` varsayımı değildir.

## Fail-closed readiness

Şunlardan biri varsa actual storage probe başlatılmaz:
- load-bearing source `UNKNOWN`;
- artifact/hash mismatch;
- undeclared persistent sidecar/header;
- plan dışı serialization;
- reopen/restore kontrolünün başarısızlığı;
- unexplained N-dependent bytes;
- potentially-per-vector UNKNOWN;
- plan veya contract hash mismatch.

Bu duruş yöntem hakkında negatif bilimsel sonuç değil, measurement-readiness başarısızlığıdır.
