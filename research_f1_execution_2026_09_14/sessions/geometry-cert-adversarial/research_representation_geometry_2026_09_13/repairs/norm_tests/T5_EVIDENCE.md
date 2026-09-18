[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# T5_EVIDENCE — genel-durum vektör-tabanlı kap sınırı testi

## 1. Tam indirgeme (türetme + cebir denetimi)

`s_i=sign(x_i)`, `sign(0)=+1`, `c=s/√d` (birim), `rho=(x·c)/||x||`,
`u=(q·c)/||q||`, `t=(q·x)/(||q|| ||x||)`. İddia:
`t ∈ u·rho ± √((1−u²)(1−rho²))`.

- `x·c = Σx_i s_i/√d = S1/√d`, `S1=Σ|x_i|`, çünkü `x_i s_i=|x_i|`
  (`x_i=0` ise `0·1=0=|0|`).
- `q·c = Sq/√d`, `Sq=Σq_i s_i`.
- `K := u·rho·||q||·||x|| = (q·c)(x·c) = S1·Sq/d`. Görevdeki `K` ile aynı.
- `rho²=S1²/(d·X2)`, `u²=Sq²/(d·Q2)` (`Q2=||q||²`, `X2=||x||²`).
- `(t−u·rho)² ≤ (1−u²)(1−rho²)` iki yanı `Q2·X2` ile çarpılır:
  `(QX−K)² ≤ Q2·X2·(1−u²)(1−rho²)`. Görevdeki form.
- `1−u²=(d·Q2−Sq²)/(d·Q2)`, `1−rho²=(d·X2−S1²)/(d·X2)` konup `d²` ile
  çarpılır; kodun denetlediği bölmesiz tam form:
  `(d·QX−S1·Sq)² ≤ (d·Q2−Sq²)(d·X2−S1²)`. `(*)`

Kare alma yönü: `|t−u·rho| ≤ D ⟺ (…)² ≤ D²` geçerli, çünkü `D≥0`
(karekök) ve iki yan da `≥0`. `D²=(1−u²)(1−rho²)≥0`, çünkü her çarpan
`≥0`: `d·Q2−Sq² = ||q||²||s||²−(q·s)² ≥ 0` (C-S;
tam kimlik `(1/2)Σᵢⱼ(qᵢsⱼ−qⱼsᵢ)²`); `x` için aynısı. Kod her vakada
`Bq≥0`, `Bx≥0` denetler (`T5.cap`).

`rho ∈ [1/√d, 1]`: `S1>0` (`x≠0`) olduğundan `rho>0`;
`S1²≤d·X2` (C-S) verir `rho≤1`; `X2≤S1²` (çapraz terimler
`2|xᵢ||xⱼ|≥0`) verir `rho²≥1/d`. Kod her vakada ikinci iddia olarak
denetler (`T5.rho`).

**Cebir hükmü: görevdeki indirgeme DOĞRU.** Düzeltme gerekmedi.
2000 rastgele çiftte `(*)` + `Bq,Bx≥0` + rho sınırları ayrıca
doğrulandı (prototip, `/tmp`, teslimata dahil değil).

## 2. Vaka sayımı ve kapsama (yürütmeyle)

- Vaka: **2716** `(q,x)` çifti, `d ∈ {2,3,4,5,8}`,
  d-dağılımı `{2:523, 3:534, 4:549, 5:552, 8:558}`.
  Tohum `Random(20260913)`, belirlenimci. Kontrol: vaka başına 2
  (`T5.cap` + `T5.rho`) + 11 meta = **5443** T5 kontrolü, tamamı geçti.
- Kovalar: `rand 1993, par 100, orth 195, tight 194, face 44,
  onezero 50, multizero 30, dense 50, near1 50, allsign 10`
  (rastgele kovalardaki eksikler sıfır-vektör atlamalarıdır: 7+5+6).
- `u` dağılımı (tam `u²` eşikleriyle): `u=0: 407`, `0<|u|<0.1: 172`,
  `0.1–0.5: 1046`, `0.5–0.8: 452`, `0.8–0.98: 309`, `0.98–1: 188`,
  `|u|=1: 142`. İşaret: `neg 1180, pos 1129, zero 407`; `u<−0.9: 252`.
  Rastgele tarama tek başına 7 kovayı da doldurdu; `orth/par/near1`
  ile garanti altına alındı. **u≈0 ve u≈−1 kapsanır.**
- `rho` aralığı: her `d` için `min rho²=1/d`, `max rho²=1` tam ulaşıldı
  (`face` seyrekliği + `dense` kalıbı).
- Sıfır koordinat (gerçekleşen sayım): `one 729, multi 193, face 52`
  (`sign(0)=+1` işletilir; `face` = d−1 sıfır).
- `x` işareti: `mixed 2019, onesign 697`.
- `q⊥c` (`Sq=0`, tam): 407 vaka. `q∥c` (`Sq²=d·Q2`, tam): 142 vaka.
- Dejenere (`rhs=0`): 260. Dejenere-olmayan tam eşitlik (`lhs=rhs>0`): 592.

## 3. Kırık-sınır deneyi (testin yanılabilirliği)

Çarpan `(1−u²)(1−rho²)` yerine `×999/1000` kondu (tam:
`lhs·1000 > rhs·999` reddeder). Sonuç: **592/2716 vaka reddeder.**
Reddedilenlerin tamamı slack-0 vakalarıdır (`reddedilen == tam-eşitlik`,
`T5.exact-consistency` bunu kilitler). Katisiz en yakın bağıl boşluk
`3/2212 ≈ %0.1356` olduğundan `%0.1` eşiğini geçen katisiz vaka yoktur;
`%1` içinde 12, `%10` içinde 86 vaka vardır. Test sınıra değer:
sıkılaştırılmış her varyant 592 vakada yakalanır.

## 4. En sıkı vaka

En küçük boşluk `slack = rhs−lhs = 0` (`rhs>0`), 592 vakada. Örnek
`c0001-rand-d2` (rastgele kovadan): `d=2`, `q=(0,1/5)`, `x=(1/5,0)`:
`u²=rho²=1/2`, `QX=0`, `K=1/50`, `lhs=rhs=1/2500`.
En sıkı katisiz: mutlak `3/2500` (`c1046-near1-d3`); bağıl `3/2212`
(`rand` d=3, `q=(−1,2/5,1)`, `x=(4/5,−3/5,1/5)`).
