[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Gerçeklenebilirlik (C2)

Tanım (REPORT §2): sabit grup G, belge `C=(c,g)`, sorgu `q=(qc,qg)`; `z=t²`.
`a=qc·c`, `b=qg·g`, `u=‖c‖²`, `v=‖g‖²`. Vektörler keyfi reel; katsayılar tam rasyonel okuma.
Not: dondurulmuş işlerde sıfır-ortalama şartı yok. Burada "gerçeklenebilir" = bu tanıma uygunluk.
Sıfır-ortalama kastedildiyse kapsam dışıdır (incelenmedi).

## Tekli kısıtlar (gerekli ve yeterli, ℝ)
- `u ≥ 0`, `v ≥ 0`.
- `u=0 ⇒ a=0`; `v=0 ⇒ b=0` (norm sıfır ⇒ vektör sıfır ⇒ iç çarpım sıfır).
- Yeterlilik: `u>0` ise `c=[√u]`, `qc=[a/√u]`; `u=0` ise sıfır. Grup aynı.

## Paylaşımlı sorgu (çift ve n'li aile)
Aynı tekli şartlar yeterli; ek ortak kısıt yok (ℝ üzerinde).
İnşa (tamamlayıcı blok; grup aynı): `Q ≥ max(Ai²/Ui)` seç (`Ui=0` terim atlanır, `Q=1`).
`qc=(√Q,0,…)`, `ci=(Ai/√Q, ri e_i)`, `ri=√(Ui−Ai²/Q)`, her `i` ayrı dik yönde.
O hâlde `‖ci‖²=Ui`, `qc·ci=Ai`; Gram PSD. Sorgu normu serbest olduğundan
Cauchy-Schwarz (`Ai² ≤ Q·Ui`) her zaman sağlanabilir. Boy `1+n` yeter.
ℚ-vektör daha dardır (karekökler irrasyonel olabilir); aday aşağıda ℚ ile verildi.

## Aday teğet (doğrulandı, Fraction)
Tuple: `(3/2,1,2,4)` karşı `(1,0,1,0)`.
`P=(3/2+z)²·1 − 1²·(2+4z)=1/4−z+z²=(z−1/2)²`.
Hüküm `z=1/4,1/2,1` için `[1,0,1]` (birincil + denetim uyumlu).
Sertifika `[1/4,1]` üzerinde `ISOLATED_TIES dir 1, ties=[1/2]` (teğet, dönüş yok).

Açık vektörler (ℚ, toplam boy 3; G={2}):
- `qc=[1,1/2]`, `c1=[1,1]`, `c2=[1,0]`; `qg=[1/2]`, `g1=[2]`, `g2=[0]`.
- Belge1: `1·1+1/2·1=3/2`, `1/2·2=1`, `1+1=2`, `4`. Belge2: `1`, `0`, `1`, `0`.
Koşu: `realizable_tangent.py` 12/12 PASS.

## Mevcut örnekler
| Örnek | Tuplelar | Sınıf |
|---|---|---|
| S1 | (−3,4,5,10), (−2,2,2,10) | gerçeklenebilir |
| S2 | (2,2,4,4), (1,1,1,1) | gerçeklenebilir |
| S3 | (1,1,1,10), (−1,−1,10,1) | gerçeklenebilir |
| S3b | (1,0,1,1), (−1,0,1,1) | gerçeklenebilir |
| S4 | (1,1,0,4), (1,0,1,0) | soyut-sadece (`u=0,a≠0`) |
| S5 | (−1,1,1,1), (−2,2,1,3) | gerçeklenebilir |
| S6a ek | (−50,0,1,0) | gerçeklenebilir |
| S6b ek | (−100,0,1,1) | gerçeklenebilir |
| S6c | S4 çifti | soyut-sadece |
| S7 | ızgara inşası | gerçeklenebilir (inşa gereği) |
| S8 | önbellekten türetim | gerçeklenebilir (reel vektörlerden) |
| Aday | (3/2,1,2,4), (1,0,1,0) | gerçeklenebilir (yukarıda) |

Kontrol listesi (gelecek örnek): `u,v≥0` mi; sıfır-zorlama tutuyor mu; ortak sorgu için ek test gerekmez (ℝ).
