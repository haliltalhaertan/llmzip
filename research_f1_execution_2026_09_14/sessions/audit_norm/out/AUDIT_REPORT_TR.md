[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Denetim: norm_aware_sign_bounds (round4) — Türkçe rapor

Yöntem: Orijinaller salt-okunur bırakıldı (`1021083d` doğrulandı). `verify.py`
kopyalanıp sabit env ile koşuldu: 272/272, exit 0, `results.json` ile
BİT-BİT aynı (0 farklı kayıt). Belirleyici kontroller `fractions.Fraction`
ile tam aritmetikte yeniden yapıldı. Ağ yok, Task4F1 yok, benchmark yok.

## 1. Çekirdek sınırın ispatı (sıfırdan, denetçi ispatı)

c birim olmak üzere q·x = uρ + q⊥·x⊥, |q⊥·x⊥| ≤ ‖q⊥‖‖x⊥‖.
‖q‖=‖x‖=1 GEREKİR (c=s/√d zaten birim). Sonuç:
q·x ∈ uρ ± √((1-u²)(1-ρ²)). Evet, bu düpedüz Cauchy-Schwarz/açı
toplamıdır; yeni eşitsizlik yok (REPORT §5 bunu dürüstçe söyler).
Hipotezler: E §'da doc'lar normalize ✓, F §'da vektörler birim ✓,
taramalardaki 9 sorgunun 9'u da norm-kare=1 (tam sayı doğrulandı) ✓.
Teorem 2 metni (§5) "birim" hipotezini açıkça yazmaz; §2'den miras kalır.
Uçlar: u=±1 veya ρ=±1 → nokta-aralık uρ (top3 örneği: u=1).
ρ=0 ve ρ=-1 doc'lar için İMKÂNSIZ: x∈F(s) iken ρ=‖x‖₁/√d ∈ [1/√d,1]
(artefakt bunu hiç yazmaz; D_CASES'teki rho=-0.3 vakası imkânsız veri).
u=0 serbest. Formülde tekillik yok; aralık asla boş/ters değil (clamp)
ve asla [-1,1] dışına taşmaz (CS: |uρ|+√.. ≤ 1).

## 2. Sıfır-yüzü: bir, birkaç, tüm koordinat

0 yalnızca P-koordinatlarında olabilir (N'de <0 şart). ρ ∈ [1/√d,1]'de
kalır; aralık bozulmaz. "Tüm koordinat sıfır" doc/q için tanımsız (birim
şartı); P_K q=0 (eksen vakası) için: m<0'da tek-eksen kuralı doğru,
m=0'da YÜZ kuralı gerekir (koordinatör haklı; aşağıda tam ispatla).
verify.py eksen dalı m=0'da YANLIŞ; test seti bu vakayı içermez (B3'te
hiç attainment kontrolü yok; B2.att tutarlılık kontrolü False==False
ile geçer ve böceği yakalayamaz — gösterildi).

## A. İddia tablosu (dar; detay B ve C'de)

| ID | Hüküm | Yer | Not |
|---|---|---|---|
| T1-deger | PASS | REPORT:65-71 | sup/inf formülleri doğru |
| T1-norm | PASS | REPORT:75-77 | tek maksimizörle ispatlı |
| T1-eksen | FAIL | REPORT:78 | m=0 yüzü; kural eksik |
| T1-tablo-deger | PASS | REPORT:90-97 | 8 değer tam doğru |
| T1-tablo-uc | FAIL | REPORT:92-97 | 8 bayrağın 4'ü yanlış |
| W-bosluk | CAVEAT | REPORT:103-105 | paylaşım doğru, braket yanlış |
| W-flip | PASS | REPORT:106-110 | tam eşitsizlikle kanıtlı |
| W-tie | FAIL | REPORT:111-113 | "Exact" yanlış; yakl. doğru |
| W-ayrisma | CAVEAT | REPORT:114-116 | sonuç doğru, gerekçe yanlış |
| T2-aralik | PASS | REPORT:125 | CS; 117 tam vaka, 0 ihlal |
| T2-aci | PASS | REPORT:125 | özdeşlik |
| T2-payload | CAVEAT | REPORT:132-137 | 1e-12 sertifika değil; %75 fire |
| C-sertifika | CAVEAT | REPORT:141-146 | yeterli ✓, gerekmez (3/15) |
| C-top3 | CAVEAT | REPORT:148-153 | sayı ✓, kapsam: u=1 sentetik |
| C-fail | PASS | REPORT:155-158 | [-0.8,0.6], g=1.4, tam gerçeklenir |
| J-joint | CAVEAT | REPORT:167-173 | sınır geçerli; 1 float örnek |
| V-cevher | PASS | verify.py:33-67 | proj/üyelik/uç-değer doğru |
| V-att | FAIL | verify.py:70-86 | eksen dalı m=0'da yanlış |
| V-B2exact | FAIL | verify.py:160-165 | 30 otolojik kontrol (x==x) |
| V-B2att | CAVEAT | verify.py:171-177 | tek-eksen; böceği ıskalar |
| V-D | CAVEAT | verify.py:296-316 | t elle seçilmiş; rho=-0.3 imkânsız |
| V-E | CAVEAT | verify.py:351-399 | geçerli ama 6/6 nokta-aralık |
| V-cert | CAVEAT | verify.py:333-343 | ∓u doğru; float sertifikasız |
| V-rank | PASS | verify.py:346-348 | güvenli yön; sıkı değil |
| V-G | PASS | verify.py:431-449 | gerçek olumsuzlamalar |
| J-sonuc | PASS | results.json:8-25 | bit-bit üretildi; sayı ✓ |
| S-durum | PASS | STATUS:27 | 272/272 yeniden üretildi |
| K1-tablo | PASS | COORD:10 | 4 satır düzeltmesi tam doğru |
| K2-d4 | PASS | COORD:10 | [1/2,1] doğrulandı |
| K3-eksen | PASS | COORD:11 | karşı-örnek tam doğrulandı |
| K4-yuz | PASS | COORD:11 | m<0/m=0 ayrımı ispatlı |
| K5-iff | PASS | COORD:12 | yeterli/gerekmez doğrulandı |
| K6-float | PASS | COORD:13 | bağlam + güçlendirildi (30) |
| K7-hiza | PASS | COORD:14 | u=1, t=ρ, 15 basamak eşit |
| K8-tie | PASS | COORD:15 | yakl. ±1.1e-16; relevance yok |

Sağ kalanların kategorisi: T1-değer/T1-norm/T2: cebirsel ispat
(denetçi el-doğrulaması + tam-aritmetik vaka taraması); hiçbiri
literatür-öncelik denetimli değil, hiçbiri novel değil. W-flip:
sonlu tam örnek (benim eşitsizliğim; artefakt float). C-top3/J-joint/
W-tie: yalnızca sayısal kontrol, sentetik, sertifikasız. Gerçek-veri
faydası: YOK (artefakt da iddia etmez; Conjecture olarak dürüst).

## B. Desteklenmeyen iddia listesi

- Kapsam: 8-bit ρ'nun top-3 sertifikası SADECE u=1 sentetikte (ρ=t'yi
  ölçer); genelleme yok, gerçek-veri kapsamı yok. "Tamamen boş"
  ifadesi sıralama-için-boş demektir; [0.5,1] aralıkları nontrivial.
- Erişim: d2 tablosunda 4/8 uç bayrağı yanlış ((++):inf, (-,+):inf,
  (--): ikisi ters); (+,-) satırı doğruydu. d4 `(0.5,1]` → [0.5,1]
  olmalı (2 proza yeri + 1 detay dizesi). Eksen kuralı m=0'da yanlış;
  "ikisi de erişilmez" (W-ayrisma) yanlış (A-inf erişilir).
  C.supA detay dizesi kendiyle çelişir ("(3/5,1]" + "inf e1'de").
- Bağımsızlık: "iki bağımsız yol" YOK. Aynı yazar; 30 B2.exact
  kontrolü otoloji (fonksiyon çıktısını kendine eşitler); D.agree
  aynı formülün 3 float yazımı; D.contains t'leri elle seçilmiş.
- Yuvarlama: 1e-12 gevşekliği sertifika değil (yuvarlama analizi
  yok; aday değerlendirmeleri float). Teorem geçerliliği SADECE
  u=1 nokta-vakasında vektörden test edilmiş.
- Öncelik: yenilik iddiası yok ve olmamalı (Th2 açıkça eski; Th1
  elementer). "Exact tie" ve "equal relevance" çöpe.
- Sıralama: worst-rank güvenli üst sınırdır, erişilen gerçek sıra
  değil (doc1: worst 3, gerçek 1). L_i>U_j'nin tersi iddiası yok.
- Gizli fire: [-1,1]'de uniform 8-bit, d=4'te 256 kodun 191'ini
  (%75) hiç kullanmaz (fizibilite [0.5,1]); aynı baytın alternatif
  kullanımı karşılaştırılmadı.

## C. Yeniden hesaplanan sayılar (proza vs ham)

| Kalem | Proza | Yeniden | Durum |
|---|---|---|---|
| L1..3 | 0.9961,0.9961,0.9882 | aynı (4dp) | UYDU |
| U4..6 | 0.5020,0.7137,0.8706 | aynı (4dp) | UYDU |
| worst-rank | [3,3,3,6,5,4] | aynı | UYDU |
| true t | 1,.99751,.99015,.5,.70711,.86603 | aynı (5dp) | UYDU |
| fail aralık | [-0.8,0.6], g=1.4 | tam eşit | UYDU |
| fail cert | [-0.8010,0.6014] | aynı (4dp) | UYDU |
| joint | [-0.209877,0.777778], t=4/9 | aynı; t tam | UYDU |
| flip | 0.7939603029772521 | aynı; tam > 0.6 | UYDU |
| LME t4 | 4 sayı | 4/4 bit-eşit | UYDU |
| tie | 0.7±1e-9 | ±1.1e-16, ≠0.7 | YAKL. |
| 272/272 | geçiyor | bit-bit aynı | UYDU |

Anlaşmazlık: YOK (sayılar doğru; braket/kelime hataları prose'da).

## D. Eksik girdiler (geçersiz matematikten AYRI)

Çalıştıramadım (yasak/yok, yanlış DEĞİL): Task4F1 (kapsam-dışı, hiç
dokunulmadı); gerçek-veri top-K kapsamı (veri yok + benchmark yasak);
exec-7 orijinal probu (diskte yok — ama olgusu satır-içi yeniden
doğrulandı: member_closed True vs member_F False).
Yanlış (matematik/metodoloji): eksen erişim kuralı (m=0); 4 tablo
bayrağı; "exact tie"; 30 otolojik kontrol; "bağımsız yol" söylemi;
imkânsız rho=-0.3 test vakası. İkisi asla birleştirilmedi.

## E. Bakmadıklarım (nedeniyle)

- Literatür/öncelik: ağ yasak + artefakta dergi-taraması yok.
  "Yok" demem; "bakmadım" derim.
- Worker canlı dizini içeriği: kapsam tek-artefakt; yalnız yolun
  varlığı kontrol edildi (mevcut; komut çalışır).
- Diğer round4/round3 artefaktları: kapsam-dışı.
- d≥5 ızgaraları: yok; ispatlar boyutsuz, ızgara zaten yalnızca
  akıl-sağlığı. q=0/birim-dışı girdiler: kapsam-dışı (sessiz
  davranış not edildi, düzeltilmedi).

## F. Hüküm

Çekirdek sınır elementer ve doğrudur; teorem ispatları (eksen-erişim
hariç) sağlamdır ve sayılar bit-bit yeniden üretilir — ama d2
tablosunun uç bayrakları, eksen-erişim kuralı, "exact tie" ve "iki
bağımsız yol" iddiaları YANLIŞTIR; 1e-12 bir sertifika değildir;
8-bit ρ kazancı yalnızca u=1 sentetik hizalanmada (baytın hedefi
ölçtüğü durumda) gösterilmiştir ve gerçek-veri faydası SIFIRDIR.
"Stop" listesi: tablo bayrakları, eksen kuralının koşulsuz hali,
"exact", "bağımsız", "sertifikalı" kelimeleri. En küçük ayırt edici
test: rastgele birim (q,x) çiftlerinden hesaplanan (u,ρ,t) ile —
u∈(-1,1) genel durumunda — t∈[L,U] içermesini tam-kare eşitsizliğiyle
kontrol eden vektör-kökenli bir genel-vaka testi eklemek (şu an bu
test yok; formülün vektörden gelen tek genel kanıtı bu denetimdeki
117 tam vakadır).
