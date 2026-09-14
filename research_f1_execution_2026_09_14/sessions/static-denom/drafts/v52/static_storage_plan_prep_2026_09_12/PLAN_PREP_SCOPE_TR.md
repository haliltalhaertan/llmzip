# V52 statik depolama — gerçek PLAN hazırlık kapsamı

**Durum: DESIGN PREP ONLY / NOT EXECUTABLE / NOT FROZEN / NOT AUTHORIZED.**

Taban V2 envanter: `552088ae8907b13d0dcf44dfc26c0a2389503125`.
Canonical bağlam: `main@5ec3db60c03edde490374bf9cd7c3e56dd6bcd00` (L-095 gözlemi).
Task4F1: **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**.

Bu paket gerçek storage ölçümü yapmaz. Amacı, ileride üretilecek ham `v52.static-storage-plan` dosyasının seçimlerini ölçümden önce sabitlemektir. Mevcut bağımsız-incelemeli contract baytlarını değiştirmez.

## Ölçüm birimi

Bir gerçek plan = **tek benchmark + tek mevcut package configuration + tek ilan edilmiş serialization formatı**. Bir planın içinde yeni yöntem kolu seçilmez ve format değiştirilemez. Başka configuration/format ayrı plan/hash/run gerektirir.

Plan iki benchmark ailesi için ayrı üretilir:
- LongMemEval: frozen 470 archive roster, `question_id` + gerçek `N_archive` kaynağı.
- LoCoMo: frozen 10 conversation/archive roster, manifest-bound representation-transfer proof içindeki gerçek N değerleri.

Bu ayrım iki benchmark'ın arşiv-ağırlıklı özetlerini birbirine karıştırmayı engeller.

## Bütçe nesnesi

Bağlayıcı karar: `marginal_persistent_bytes_per_vector <= 12`.

Her vektör için gerçekten kalıcı saklanan code, norm, scale, correction, ID, offset, metadata veya lookup auxiliary marjinal sınıra dahildir. Shared model/projector state ayrı tutulur ve gerçek fiziksel kopya/paylaşım nüfusu ile effective cost'a tahsis edilir. `code_bytes_per_vector`, `marginal_persistent_bytes_per_vector` ve `effective_persistent_bytes_per_vector` ayrı sonuçlardır.

## Package boundary

Gerçek plan, süreç yeniden başladıktan sonra şu iki sentetik işlemi yapmaya yetecek kalıcı archive package'ını ölçer:

1. `TRANSFORM`: frozen archive temsilini **raw archive/corpus yeniden fit etmeden** aç ve hash-bound sentetik metni aynı temsil/kod uzayına taşı.
2. `ID_MAPPING`: fake, preassigned code-row/ID/offset kimliğini hash-bound oyuncak payload tablosundaki doğru kayda eşle.

Raw corpus payload'ın kendisi package byte toplamının dışındadır; fakat ona doğru geri dönüş için gereken persistent ID/offset/lookup state ücretsiz varsayılmaz. Runtime/library bağımlılıkları da archive persistent byte toplamının dışındadır fakat exact build/version/hash olarak EXTERNAL_BOUNDARY bağımlılığı şeklinde kaydedilir.

## Mevcut UNKNOWN'lar

V2 envanter fitted TF-IDF vocabulary/IDF, source ve mixed96 SVD state, `mu96`, archive-specific ITQ/PQ/OPQ/RaBitQ state, persistent ID/offset representation ve fiziksel copy/share kapsamını henüz doğrulanmış persistent artifact olarak bulmamıştır. Actual plan bunları varmış gibi dolduramaz.

Bir load-bearing artifact hâlâ çözülmemişse:
- item `UNKNOWN` kalır,
- sıfır byte yazılmaz,
- potentially-per-vector UNKNOWN `<=12` hükmünü bloke eder,
- yalnız shared UNKNOWN varsa marjinal gözlem ancak açık nitelemeyle verilebilir; toplam/effective sonuç UNKNOWN kalır.

## Serialization kuralı

Actual plan, ölçümden önce **tek** serialization kimliğini literal olarak bağlar. Öncelik mevcut/frozen artifact'ın verbatim biçimidir. Mevcut bir biçim bulunamaz ve yeni serialization tanımlanması gerekirse bu, ölçümden önce ayrı tasarım kararı ve bağımsız inceleme gerektirir; ölçüm sonucuna bakılarak format seçilemez.

## Durma kuralı

Actual planın exact roster'ı, artifact identities/hash'leri, serialization formatı, fixture hash'leri ve control expectations dış kayıtta hash-bound olmadan callback/adapter çağrısı yapılmaz. Eksik artifact gizlice raw corpustan yeniden üretilmez.
