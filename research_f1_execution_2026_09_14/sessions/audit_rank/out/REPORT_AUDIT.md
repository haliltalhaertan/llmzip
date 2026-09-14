[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Denetim: rank_crossing_certificates (yalnız bu artefact)

Hedef: `.../round4/rank_crossing_certificates/` (REPORT.md,
COORDINATOR_REVIEW.md, STATUS.md, results.json, verify.py).
Dondurulmuş commit doğrulandı (salt-okunur `git log`):
`1021083 research: archive math discoveries...`.
Orijinallere yazılmadı; verify.py kopyalanıp koşuldu.
Ağ yok, Task4F1'e dokunulmadı, her şey `Fraction` ile tam aritmetik.

Özet: polinom karakterizasyonu doğru; implementasyon prose'un
söylediğinden çok daha azını sertiflıyor. En ağır bulgu: manşet
LME sertifika statüleri results.json'a yazılıyor ama 49 kontrolün
HİÇBİRİ onları assert etmiyor.

## A. İddia tablosu (dar; detay altta liste)

| ID | Sonuç | Kanıt |
|---|---|---|
| R1 skor formu | PASS | S8 float 3.3e-16; audit1 |
| R2 Thm1(i)-(iv) | PASS | audit1 + 24/24 sahte-kök filtresi |
| R2v Thm1(v) tek-sıfır | CAVEAT | imkânsız; 0/20000; koord. #1 doğru |
| R3 Thm2 sabitlik | PASS | süreklilik ispatı geçerli |
| R4 Thm3a/3b topK | PASS | ispat geçerli; 334 fuzz 0 uyuşmazlık |
| R5 "izole edilemeyince" | FAIL | izole EDİLİR; audit4 41/41 çözdü |
| R6 karmaşıklık O(..) | CAVEAT | bit-maliyet yok; koord. #4 doğru |
| R7 49/49 makine-kontrollü | CAVEAT | geçti ama F1+F2+F3 boşlukları var |
| R8 S1-S9 sayıları | PASS | hepsi tam recompute ile tuttu |
| R9 LME [1/16,1] STRICT | PASS | çift-sertifika olarak doğru |
| R9s top3 iması | CAVEAT | 1/1413 çift; koord. #2 doğru |
| R10 S4 tanjant | CAVEAT | soyut-ailede doğru, gerçekleşemez |
| R11 domain/endpoint | PASS | doğrusallık; DOMAIN_FAIL zorlanıyor |
| R12 rasyonel-vs-BLAS | PASS | kapsam doğru yazılmış; koord. #3 |
| R13 §9 limitler | CAVEAT | dürüst ama F1,F2,F3 yok |
| R15 results.json 49/0 | PASS | rerun bit-identical, 12/12 SAME |
| R16 rasyonel-kök bölme | CAVEAT | LME'de bütçe-aşımı; dürüst not var |
| R17 dual-formül | CAVEAT | uyuşuyor ama aynı-yazar; koord. #5 |
| R18 "strict unless both zero" | CAVEAT | boş parantez; kod doğru |
| R19 Thm3a gereklilik | PASS | ispat geçerli |
| R20 numpy.roots yok | PASS | grep: hiç çağrılmıyor |
| R21 S7 18048 | PASS | 16x1128 recompute tuttu |
| R22 S8 <1e-9 | PASS | ölçülen 3.3e-16 |
| R23 (1,16) UNRESOLVED | CAVEAT | dürüst çıktı, yanlış kaçınılmazlık |
| R24 SAMPLE_TIED | CAVEAT | 5 nokta; "fully tied" abartı |
| R25 prob kararsızlık | PASS | tanık geçerli: {0}->{1} |
| R26 "VARIES" statüsü | CAVEAT | kodda statü değil yön bayrağı |
| K1-K5 koord. düzeltmeleri | PASS | beşi de doğru teşhis+kapsam |

Düzeltmeler ve yeni bulgular (hem worker hem koordinatörün kaçırdıkları):

- **F1 (ağır).** Manşet LME statüleri assert'siz. `cA/cB`
  verify.py:804-812'de hesaplanıp sözlüğe yazılıyor; `check(`
  çağrılarının hiçbiri `STRICT`/`UNRESOLVED`'i doğrulamıyor
  (grep ile kanıtlı). cA `UNRESOLVED` dönse bile 49/49 geçerdi.
  Düzeltme: `check("S8-certA-strict", cA["status"]=="STRICT")`
  ve cB için beklenen statü assert'leri şart.
- **F2.** `S7-1plus1-unresolved` verify.py:734'te `check(.., True)`
  totoloji; ismi vaat ediyor, gövde hiçbir şeyi test etmiyor.
  Düzeltme: `found11 is None` assert edilmeli.
- **F3.** Ölü/testsiz dallar: `PERSISTENT_TIE` `topk_cert` üzerinden
  erişilemez (bağlantısız-örnek + kalıcı-tie çelişir; ispatla ölü
  kod, verify.py:524,531). `DOMAIN_FAIL`, derece-1/0 P, `VARIES`
  yolu hiçbir check'te yok. Düzeltme: dal başına en az 1 test.
- **F4.** LME (1,16) çözülebilirdi: Sturm=1 + uç verdictleri
  (-1@1, +1@16) farklı ⟹ tek gerçek kök KESİN geçiş (touch
  işaret değiştirmez). 2 satırlık uç-karşılaştırma yeterliydi;
  izolasyona bile gerek yok. Üstelik tam izolasyonla kök
  `z ∈ (12.313651681, 12.313653681)` içinde TEK ve geçiş
  (`cmp`: -1→+1, dışta Sturm 0). Yani `t* ≈ 3.509`.
  "Touch-or-crossing unisolated" bir implementasyon tembelliği,
  matematiksel zorunluluk değil.
- **F5.** Gerçekleşebilir tanjant VAR: `(3/2,1,2,4)` vs `(1,0,1,0)`,
  `P=(z-1/2)²`, verdict `[1,0,1]`, tam `Fraction` ile doğrulandı,
  açık 2+2 vektör inşası ile gerçekleşebilir. S4'ün
  gerçekleşemezliği seçim hatasıydı, zorunluluk değil.
- **F6 (hafif).** `L==R` → sahte `STRICT dir 0`; `L>R` sessizce
  takas; `L=0` kabul (spec `z>0` diyor). Girdi savunması yok.
- **F7.** İrrasyonel-köklü Sturm yolu sıfır assert'li (sadece
  assert'siz cB'de çalışıyor).
- **F8 (bozuk-değil).** Thm3b/prio sağlamlığı "tüm tie'lar
  listeli"ye dayanır; UNRESOLVED erken-dönüşü bunu korur.
  Kontrol edildi, açık bulunamadı.

## B. UNSUPPORTED-CLAIM listesi

- Kapsam: LME top3 stabilitesi desteklenmiyor (1/1413 çift,
  n=474 ölçüldü). "Safe-t aralığı" deyip z-aralığı vermek.
- Erişim: S4 tanjantı kosinüs-gerçekleşebilir olaylara erişmez
  (soyut-aile-geçerli). 1+1 tanığı yok (dürüstçe UNRESOLVED).
- Bağımsızlık: dual formülasyon aynı-yazar; 49 kontrol bağımsız
  denetim değil. "Machine-checked" = çalıştırılabilir assert'ler.
- Yuvarlama: rasyonel-okuma sertifikası BLAS sırasına taşınmaz
  (doğru şekilde ifşa edilmiş; taşınmış gibi KULLANILMAMALI).
- Öncelik: literatür önceliği yok; hiçbir şeye "novel" denemez.

## C. Recompute (prose vs ölçüm)

| Kalem | Prose | Ölçüm | Durum |
|---|---|---|---|
| S1 verdict/P(1) | [+,-,-,+,+,+,+]/12 | aynı | TUTTU |
| S3 P/verdict | 9(z+1)²(1-z)/[+,+,+] | aynı | TUTTU |
| S4 P/verdict | (z-1)²/[+,0,+] | aynı | TUTTU |
| S5 verdict | [+,0,-] | aynı | TUTTU |
| S6c E / 1-vs-1 | 0,1/2,0 / 1,1 | aynı | TUTTU |
| S6b tanık | probe-sets-differ | {0}->{1} | TUTTU |
| S7 evals | 18048 | 16x1128=18048 | TUTTU |
| S8 float fark | <1e-9 | 3.3e-16 | TUTTU |
| S8 uç verdict | -1,-1,+1 | aynı | TUTTU |
| toplam | 49/0 | 49/0, 12/12 SAME | TUTTU |
| UNRESOLVED oranı | (yok) | artefact 1/6=%16.7 | YENİ |
| fuzz UNRESOLVED | (yok) | 40/1705=%2.3 | YENİ |
| izolasyon kurtarma | (yok) | 41/41=%100 | YENİ |
| top3 için gereken | (yok) | 1413 çift, var 1 | YENİ |

## D. Eksik ağır girdiler (yanlış matematikten AYRI)

Yok. LME pickle + koordinatör tanığı diskte mevcuttu ve
salt-okunur yüklendi. "Çalıştıramadım" findingsi yok; tüm
"yanlış/eksik" findingsleri gerçek bulgu.

## E. Kontrol ETmediklerim

- Literatür önceliği: bakmadım (görev "novel deme" diyor).
- BLAS-sıra transferi: kapsam-dışı ve doğru ifşa edilmiş.
- Task4F1: yasak, dokunmadım.
- Diğer round artefact'ları: hedef-sınırlı.
- 1413 çiftlik tam top3 sertifikası: YAPILABİLİRDİ ama yapmadım;
  gerekçe yeteneksizlik değil: kapsam (denetim, genişletme değil)
  + dev `Fraction` maliyeti. "Yok" değil, "denemedim".
- Bit-karmaşıklığı formal analizi: eskiz olarak kabul.

## F. Hüküm

KANITLANAN: `f=(a+bz)/√(u+vz)` formu, işaret-disiplinli kübik
`P_ij` karakterizasyonu (derece ≤3, baş katsayı formülü dahil),
gerçek eşitlikler arası sabit sıkı-sıra, çapraz-çift topK
karakterizasyonu ve beklenen-recall ayrımı — hepsi sağlam ve
sayıların tamamı recompute ile tuttu. GÖZLENEN: 49/49 geçiş,
LME float uyumu (3.3e-16), tek-çift `[1/16,1]` STRICT sertifikası.
DURDURULMASI GEREKENLER: "izole edilemeyen" masalı (F4'te çözüldü),
49/49'un manşet iddiayı test ettiği izlenimi (F1: etmiyor),
S4'ün gerçekleşebilir bir şey göstermesi, top3 iması. En küçük
sonraki ayırt-edici test: LME (1,16) için uç-verdict ayrımı +
Sturm-biseksiyon izolasyonunu `certify_pair`'a ekleyip
`ISOLATED_TIES/VARIES` ve yukarıdaki kök braketini assert eden
TEK test yazmak; sonra aynı prosedürü 1413 çapraz çifte koşup
gerçek top3 sertifikasını denemek.
