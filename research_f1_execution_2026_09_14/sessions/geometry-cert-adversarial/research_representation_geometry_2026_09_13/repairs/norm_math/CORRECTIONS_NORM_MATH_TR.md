[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Ek Düzeltmeler — norm_aware_sign_bounds (matematik)

Düzeltme hedefi: commit `1021083d4f2faebda760546e1217b4de1eef87ea`,
`.../round4/norm_aware_sign_bounds/`. Özgün dosyalar değiştirilmemiştir;
bu paket EK’tir ve bağımsız denetimden geçmemiştir. Kanıtlar `proofs_exact.py`
(478/478 geçti) ile çalıştırılır; tanıklar `WITNESSES.json`’dadır.

## Yerine-geçme (supersedes) tablosu

| # | Özgün ifade (dosya:satır) | Bu belgede |
|---|---|---|
| D1 | REPORT.md:78 eksen-erisim kuralı; verify.py:76-77,85-86 | §D1 yüz kuralı onu geçersiz kılar |
| D2 | REPORT.md:94-97 tablo erişim bayrakları (4/8) | §D2 düzeltilmiş tablo onu geçersiz kılar |
| D3 | — (hiç belirtilmemiş) + REPORT.md:132, verify.py:302 | §D3 yeni destek lemması eklenir |
| D4 | REPORT.md:105, REPORT.md:153, verify.py:370 `(0.5,1]` | §D4 `[0.5,1]` onu geçersiz kılar |
| D5a | REPORT.md:111 “Exact cross-pattern tie” | §D5 geri çekildi |
| D5b | REPORT.md:20 “two independent routes” (+verify.py:6, REPORT §8) | §D5 geri çekildi |
| D5c | REPORT.md:113 “equal relevance” | §D5 geri çekildi |
| D6 | verify.py:321 K_HALF 1e-12; REPORT.md:134, §6 “certified” | §D6: kesin top-3 sertifikası + sertifikasız listesi |
| D7 | — (muhasebe yoktu; REPORT §5-6 ek-skaler iddiası yanı) | §D7 israf notu eklenir |

Simgeler: `s∈{±1}^d`, `N={i:s_i=−1}`, `F(s)={x∈S^{d−1}:x_P≥0,x_N<0}`,
`F̄(s)` kapanışı, `m_j=s_j q_j`, `m=max m_j`, `m'=min m_j`.

## D1 — Eksen-erisim kuralı m=0’da yanlış

**Özgün** (REPORT.md:78): “Axis case: attained iff some optimizing axis `s_j e_j`
has `N ⊆ {j}`.” Aynı kural verify.py:76-77 (sup) ve 85-86 (inf)’dadır.
**Neden yanlış:** `m=0` iken iyileştiriciler yalnız eksenler değildir; `m_j=0`
koordinatlarının gerdiği tüm yüz iyileştiricidir.
**Tanık:** `q=(0,0,−1)`, `s=(−,−,+)`, `N={0,1}`. `P_K q=0`, `m=max(0,0,−1)=0`.
Özgün kural: iyileştirici eksenler `(−1,0,0)`, `(0,−1,0)`; ikisi de `F(s)` dışında
(sıfır `N` koordinatı) → “erişilmez”. Oysa `x=(−3/5,−4/5,0)` birimdir,
`F(s)`’dedir (iki `N` koordinatı da negatif) ve `q·x=0=m` → erişilir. Özgün
yanlış. (inf aynası: `q=(0,0,1)`, aynı `x`, `m'=0`, skor 0.)
**Düzeltilmiş sup kuralı** (eksen durumu `P_K q=0`, yani `m≤0`):
`m<0` ise özgün tek-eksen testi doğrudur; `m=0` ise **yüz kuralı**:
erişilir ⟺ `N ⊆ J`, `J={j:q_j=0}`.
**Düzeltilmiş inf kuralı** (`m'≥0`): `m'>0` tek-eksen; `m'=0` yüz kuralı, aynı `J`.
**Kanıt:** `z_j=x_j s_j≥0`, `‖z‖=1` ile `q·x=Σ m_j z_j`. `m<0` iken
`Σm_jz_j ≤ mΣz_j ≤ m` (çünkü `m_j≤m`, `Σz≥‖z‖=1`, `m` negatif) ve eşitlik yalnız
`z=e_j` (destek tekil; çoklu destek `Σz>1` verip `mΣz<m` yapar) → yalnız
iyileştirici eksenler; erişim tek-eksen testidir. `m=0` iken `Σm_jz_j=0` ⟺
`J` dışı destek sıfır → iyileştirici kümesi `J`-yüzüdür; `F(s)`’de nokta varlığı
⟺ `N⊆J` (varsa örn. `x_j=s_j/√|J|`, `j∈J`). inf aynası işaret değiştirerek aynıdır.
**Çalıştırılabilir tanık:** `proofs_exact.py` D1 bölümü + tarama (d=2’de 4s×9q,
d=3’te 8s×7q; her hücrede bağımsız karakterizasyon ve rasyonel tanık).

## D2 — d=2 tablosu: 4 erişim bayrağı yanlış (değerler doğru)

**Özgün** REPORT.md:94-97; `q=(3/5,4/5)`. Sekiz değer doğru; `(+,+)` inf,
`(−,+)` inf bayrakları ve `(−,−)` satırının iki bayrağı yanlış; `(+,-)` doğru.
Bağımsız doğrulama (sıfırdan, norm-kare ve eksen hesabıyla) denetim özetini aynen doğruladı.
**Düzeltilmiş tablo** (bu tablo özgünün yerine geçer):

| `s` | aralık | sup | inf |
|---|---|---|---|
| `(+,+)` | `[3/5,1]` | evet, `x=q` | evet, `x=(1,0)` |
| `(+,-)` | `[-4/5,3/5)` | hayır, kapanış `(1,0)∉F` | evet, `x=(0,-1)` |
| `(-,+)` | `[-3/5,4/5)` | hayır, kapanış `(0,1)∉F` | evet, `x=(−1,0)` |
| `(-,-)` | `[-1,-3/5)` | hayır, tek iyileştirici `(−1,0)∉F` | evet, `x=−q` |

**Sekiz kanıt (özet):** `(+,+)`: `N=∅` olduğundan `F=F̄`; sup norm-durumu 1 (`x=q`);
inf eksen-durumu `m'=3/5>0`, `∅⊆{0}` → `(1,0)` erişir. `(+,-)`: sup `‖(3/5,0)‖=3/5`,
`q_1=4/5≮0` → erişilmez (maksimizör `(1,0)∉F`); inf `−‖(0,−4/5)‖=−4/5`,
`q_1>0` → `(0,−1)` erişir. `(−,+)`: sup `4/5`, `q_0≮0` → erişilmez (`(0,1)∉F`);
inf `−3/5`, `q_0>0` → `(−1,0)` erişir. `(−,−)`: sup eksen `m=−3/5<0`, tek
iyileştirici `j=0`, `N={0,1}⊈{0}` → erişilmez; inf norm `−1`, iki `q_i>0` →
`−q=(−3/5,−4/5)∈F` erişir.
**Önemli not:** verify.py’nin `sup/inf_attained` yüklemleri bu 8 hücrede
düzeltilmişle birebir uyumludur (betikte doğrulandı) — D2 kusuru yalnızca REPORT
düzyazısındadır. Kodun gerçekten yanlış olduğu yer D1’deki `m=0` durumudur.

## D3 — rho desteği: yeni lemma + imkânsız test durumu

**Özgün durum:** destek hiç belirtilmemiş; REPORT.md:132 `ρ∈[−1,1]` aralığında
düzgün kod varsayar; verify.py:302 `negative-rho` durumu `ρ=−0.3` kullanır.
**Lemma (yeni):** `x` birim, `s=sign(x)` (`sign(0)=+1`), `c=s/√d` ise
`ρ=x·c=‖x‖_1/√d` ve `ρ∈[1/√d,1]`; her zaman pozitif.
**Kanıt:** `x_i>0` ise `s_i=+1`; `x_i<0` ise `s_i=−1`; `x_i=0` ise kural gereği
`s_i=+1` ve katkı `0` — her durumda `s_i x_i=|x_i|` (sıfır-yüzü dahil), dolayısıyla
`ρ=Σ|x_i|/√d`. `‖x‖_1²=1+2Σ_{i<j}|x_i||x_j|≥1` alt sınırı, Cauchy–Schwarz
`‖x‖_1≤√d‖x‖₂=√d` üst sınırı verir. Eksen `1/√d`’yi, merkez `c` 1’i verir.
**Sonuç:** `ρ=0`, `ρ=−0.3` (verify.py:302), `ρ=−1` hiçbir `d≥1` belgesi için
gerçekleşemez (alt sınır pozitif). Aralık teoreminin kendisi soyut `(u,ρ)` için
geçerlidir — kusur kapsama şişirmesidir, geçersiz teorem değil. Geniş aralık
sesselikle varsayan yerler: REPORT.md:132 (`ρ∈[−1,1]` düzgün kod), verify.py:296-303
`D_CASES` (negative-rho satırı), §E nicemleme aralığı.
**Tanık:** betikte d=1..4 rasyonel birim vektörlerde `ρ²=‖x‖_1²/d∈[1/d,1]`
(köksüz kesin hesap) + belge alıntı kontrolleri.

## D4 — Parantez: `(0.5,1]` → `[0.5,1]`

**Özgün:** REPORT.md:105 (“one shared `(0.5, 1]`”), REPORT.md:153 (“identical
`(0.5,1]`”), verify.py:370 ayrıntı dizgisi (“share `(0.5,1]`”).
**Neden yanlış:** d=4, `q=c=(½,½,½,½)`, `s=(+,+,+,+)` durumunda `N=∅`,
`F=F̄`; `e_1=(1,0,0,0)∈F` skoru tam `1/2`, `q∈F` skoru 1. Alt uç erişilir,
aralık kapalıdır.
**Düzeltilmiş:** `[0.5,1]` (üç konumun yerine de geçer).
**Kanıt:** inf eksen-durumu `m'=min s_iq_i=1/2>0`, `∅⊆{j}` → erişilir; sup norm
`‖q‖=1`, `N` boş → erişilir. Dört eksen de `1/2`’yi verir (betikte).

## D5 — Üç geri çekme

(a) **“Exact tie” geri çekildi.** REPORT.md:111 “Exact cross-pattern tie” ifadesi
yanlış. Ölçülen: iki yanlı skor da `0.70000000000000007`, hedeften fark
`+1.1e-16` (sıfır değil); 1e-9 hoşgörülü float ikiye-bölme tam eşitlik ispatlamaz.
Doğrusu: *yaklaşık sayısal tanık*.
(b) **“Two independent paths” geri çekildi.** REPORT.md:19-20 ve §8’deki iki
“route” aynı `verify.py` dosyasında, tek yazarlıdır; bağımsız denetim değildir.
Doğrusu: *tek-yazarlı iki hesap yolu (çapraz kontrol), bağımsız doğrulama değil*.
(c) **“equal relevance” geri çekildi.** REPORT.md:113’teki ifade desteksizdir;
metinden çıkarılmıştır. Eşit kosinüs skoru eşit ilgililik göstermez.

## D6 — 1e-12 gevşekliği sertifika değildir; kesin top-3 sertifikası

**Özgün:** verify.py:321 `K_HALF=1/255+1e-12`, REPORT.md:134’teki gevşeklik ve
§6’daki “certified” sonekleri; `D.agree` 1e-12 uyumu, `worst_rank` 1e-12 hoşgörüsü.
Yuvarlama analizi yoktur; aday değerlendirmeler float’tır. “Sertifikalı” sözcüğü
float gözleme iliştirilemez.
**Kesin sertifika (bu örnek için, rasyonel):** `u=1` (`q=c`) olduğundan kesin kap
`[ρ,ρ]`’dir. Altı belge için `ρ²=S²/(4Q)` rasyonelleri:
`1, 200/201, 50/51, 1/4, 1/2, 3/4`; kutu atamaları `m=255,255,254,191,218,238`
kareli rasyonel eşitsizliklerle ispatlanır (örn. `(254/255)²<200/201≤1`,
`(252/255)²<50/51<(254/255)²`; marjların hepsi pozitif). Kesin kod-çözme aralıkları
`r₀±1/255` ile `min L_{1..3}=252/255 > max U_{4..6}=222/255`, fark `30/255` —
float’sız, hoşgörüsüz ayrışma. Marj `30/255≫1e-12` olduğundan bu örnekte 1e-12
hoşgörüsü sonucu değiştiremez.
**Sertifikasız kalan:** genel `(u,ρ)` float kap değerlendirmeleri; 1e-12’nin genel
yuvarlama iddiası; `D.agree` 1e-12 uyumu (gözlem, ispat değil); genel girdide
nicemleme-kenar yuvarlaması. “Certified top-3” sözü ancak yukarıdaki kesin
rasyonel sertifikayla birlikte okunmalıdır.

## D7 — Yük israfı muhasebesi (d=4)

d=4’te `ρ∈[0.5,1]` (D3+D4) iken `[−1,1]` üzerinde düzgün 8-bit kod
`m=round((ρ+1)·255/2)` yalnızca `m∈[191,255]`’i kullanır: `m(0.5)=191`
(191.25 aşağı), `m(1)=255`; her `k∈[191,255]` için tanık `ρ` (`k=191` için
`1/2`, diğerleri için merkez `2k/255−1∈[0.5,1]`) betikte kesin doğrulanır.
Kullanılan 65, **boş 191/256 kod (~%75)**. Ek-skaler iddiasının (REPORT §5-6)
yanına konulacak dürüst not budur. **Aynı baytın başka harcamalarıyla kıyas
yapılmadı.** Daha iyi kod tasarımı yeni iştir, kapsam dışıdır.
