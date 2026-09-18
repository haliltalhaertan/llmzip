# V52 static-storage probe policy

Status: **PREDECLARED DESIGN CANDIDATE / NOT A RUN PLAN / NO MEASUREMENT AUTHORIZATION**.

Bu politika actual plan üretilmeden önce probe panelinin nasıl kurulacağını sabitler. Actual `MEASUREMENT_PLAN.json` bütün archive kimliklerini, `N_i` değerlerini ve her `(N,q)` çiftini literal olarak içerecektir; yalnız bu algoritmaya atıf yapmak yeterli değildir.

## 1. Her archive için zorunlu deployment probes

Her frozen archive için iki nokta:

- `DEPLOY_ADD1`: `N = N_i`, `q = 1`
- `DEPLOY_ADD8`: `N = N_i`, `q = 8`

Amaç:
- `q=1` gerçek add-one marginal farkı doğrudan sınar;
- `q=8` aynı frozen model altında küçük batch davranışını ve capacity/header basamaklarını çapraz kontrol eder.

Bu sentetik snapshot'lar gerçek archive üyeliğini değiştirmez; yalnız declared serializer/package üzerinde oluşturulur.

## 2. Sentinel staircase probes

Her benchmark roster'ında, yalnız archive kimliğine göre, **lexicographically first** ve **lexicographically last** archive sentinel seçilir. Sonuç, performans veya storage ölçümü sentinel seçimini etkileyemez.

Her iki sentinel için `q=1` ve şu sıralı N paneli literal olarak actual plana yazılır:

`0, 1, 31, 32, 33, 63, 64, 65, 255, 256, 257, 1023, 1024, 1025`

Gerekçe: sıfır/small-N ve yaygın power-of-two container/capacity geçişlerinin çevresini outcome-independent biçimde örneklemek. Bu panel evrensel bütün serializer eşiklerini kapsadığı iddiasında değildir; yalnız preregistered staircase diagnostic'tir.

Bir deployment probe aynı `(archive_id,N,q)` anahtarına denk gelirse duplicate üretilmez; actual plan tek literal request içerir ve collision notu kaydedilir.

## 3. Panel boyutu

Tek configuration ve tek format için:
- LongMemEval: en fazla `470*2 + 2*14 = 968` probe request;
- LoCoMo: en fazla `10*2 + 2*14 = 48` probe request.

Böylece contract'ın 4096 expanded-request üst sınırının altında kalır. Başka configuration veya serialization aynı plana eklenmez; ayrı plan/hash/run kullanılır.

## 4. Synthetic fixture politikası

Actual plan gerçek query/gold/outcome kullanmaz.

Her benchmark için fixture paketi measurement'tan önce literal bytes + SHA256 ile bağlanır ve en az şunları içerir:

1. `FIXED_TEXT_SENTINEL`: corpus-independent sabit UTF-8 metin; OOV davranışı dahil process-restart determinism kontrolü.
2. `VOCAB_BOUND_SENTINEL`: fitted vocabulary artifact bulunursa, outcome-independent kural ile (lexicographic ilk uygun tokenlar) oluşturulur; literal metin ve hash actual plana yazılmadan hiçbir probe çalışmaz. Vocabulary artifact çözülmezse bu fixture `UNKNOWN` kalır ve TRANSFORM readiness bloke olur.
3. `TOY_ID_PAYLOAD_TABLE`: tamamen sentetik, preassigned ID/offset/payload tablosu; gerçek retrieval ID veya corpus payload değildir.
4. `CORRUPTION_FIXTURE`: remove/restore/corrupt kontrolleri için exact byte offsets/bit flips measurement'tan önce literal olarak bağlanır.

Fixture generator, seed gerekiyorsa exact RNG algorithm/version/dtype/order ile source-bound olmalıdır. Seed tek başına fixture identity değildir; final fixture bytes + SHA256 bağlayıcıdır.

## 5. Reporting / no cherry-picking

Bütün literal probe noktaları ve başarısızlıkları raporlanır. `<=12` veren N/q noktaları seçilerek diğerleri atılamaz. Sonradan ek probe, yeni plan/hash/run ve `EXPLORATORY` etiketi gerektirir.

`delta_bytes = B(N+q)-B(N)` ve `delta_bytes_per_added_vector = delta_bytes/q` ayrı taşınır. Toplam fark doğrudan 12 B/vector ile karşılaştırılmaz. Nonlinear/capacity-rounded davranış görülürse tek batch ortalamasından genel cap uygunluğu ilan edilmez.
