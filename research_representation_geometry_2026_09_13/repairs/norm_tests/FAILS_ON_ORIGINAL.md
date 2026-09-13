[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# FAILS_ON_ORIGINAL — her onarım/ek kontrol için yürütme kanıtı

Yöntem: `out/` değiştirilmedi. `verify_orig.py` (orijinalin kopyası) ve `verify_v2.py`
gövdesi önce `/tmp/.../evidence/` altında çalıştırıldı (v2 kopyasında yalnızca
1. satır `#` ile kapatıldı; gövde bayt-bayt aynı, `cmp` ile doğrulandı). Bu
oturumda `verify_v2.py` doğrudan çalışır yapıldı (etiket yoruma alındı,
`run_T5`/`run_T6`/`main()` eklendi) ve T5/T6 kanıtları `out/` içinde doğrudan
yürütmeyle üretildi. Karar gereken her yerde `fractions.Fraction` kullanıldı.
Ortam: `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`,
`PYTHONDONTWRITEBYTECODE=1`, Python 3.14.4, numpy 2.5.3.

Ön kayıt: orijinal davranış yerinde duruyor:

```
272/272 checks passed
```

v2 gövdesindeki önceki bölümlerin tamamı (`run_d2_kept`, `run_d3_kept`,
`run_flip_kept`, `run_cap_kept`, `run_top3_kept`, `run_query_kept`,
`run_seeded_kept`, `run_T1`..`run_T4`) — bu oturumda yeniden doğrulandı:

```
V2-TOPLAM: 340/340 passed
{'B2': 131, 'B3': 48, 'C': 10, 'D': 8, 'E': 12, 'F': 3, 'G': 3, 'H': 1,
 'T1': 15, 'T2': 51, 'T3': 51, 'T4': 7}
FAILS: []
```

T5/T6 eklendikten sonra tam çalıştırma (`python3 -B verify_v2.py`, çıkış 0):

```
GRUP B2: 131/131 GECTI ... GRUP T5: 5443/5443 GECTI GRUP T6: 8/8 GECTI
5791/5791 checks passed
```

## T1/T3 — m=0 tanığı (`driver_b.py` ham çıktısı)

`s=(1,-1,-1)`, `qsup=(-1,0,0)`, `qinf=(1,0,0)`, tanık `x=(0,-3/5,-4/5)`:

```
sup_closed(s1,qsup) = ('axis', Fraction(0, 1))
ORIJINAL sup_attained(s1,qsup) = False
DUZELTILMIS sup_attained(s1,qsup) = True
inf_closed(s1,qinf) = ('axis', Fraction(0, 1))
ORIJINAL inf_attained(s1,qinf) = False
DUZELTILMIS inf_attained(s1,qinf) = True
tanik: member_F(s1,x) = True |x|^2 = 1 qsup.x = 0 qinf.x = 0
orijinal kumede m=0 hucresi var mi: True
T3-korluk: ys = [0.0, -1.0, 0.0] member_F(s1,ys) = False eski-kontrol(member==orig-att) = True -> eski GECER (kor), yeni sup_attained = True
```

Okuma: eksen dalı `m=0`, `J={1,2}`, `N={1,2}`. Orijinal `False` der (yanlış);
düzeltilmiş kural (`N<=J`) `True` der. Tanık `x` birimdir, `F(s)` içindedir ve
`q.x=0` ile iki ucu da tam gerçekleştirir — `True` doğrudur. Eski tarz
`B2.att-consistency` (`member_F(ys)==att`, yani `False==False`) bu hücrede
geçer; kördür. Buna karşılık `T1.sup-fixed-true`, `T1.inf-fixed-true`,
`T1.witness-sup/inf`, `T1.face-orig-wrong-count`, `T3.new-catches-face`
orijinal fonksiyonda kalır, düzeltilmişte geçer.

Not: "orijinal kümede m=0 hücresi yok" ifadesi hatalıydı — D2 kümesinde 12 adet
m=0 eksen hücresi vardır (`T1.D2-agree` bunu `len(m0)==12` diye kilitler),
fakat orada `|N|<=1` olduğundan eski/yeni kural aynı sonucu verir. Ayırt edici
durum `|N|>=2`'nin sıfır yüzünü paylaşmasıdır (d>=3 gerekir).

## T2 — otuz totoloji her şeye geçer, altın tablo yakalar (`driver_c.py`)

```
bozuk varyanta karsi ESKI tarz sup karsilastirmasi: 8/8 GECTI (kor)
bozuk varyanta karsi YENI altin karsilastirma: 10 hucrede YAKALAR (sup)
hucre s=(1,1) q=(3/5,4/5): dogru sup^2 = ('norm', Fraction(1, 1)) bozuk sup^2 = ('norm', Fraction(16, 25)) altin = 1
results_orig.json: exact-sup2/inf2 sayisi = 30 , hepsi gecti = True
```

Okuma: kasten bozuk izdüşürücü (0. indisi düşürür) `sup^2=16/25` üretir;
eski tarz karşılaştırma (`ks[1]==vnorm2(proj_cone(...))`, aynı yardımcıyı iki
yanda da çağırır) 8/8 geçer. Yeni `T2.sup-val` altın karşılaştırması 10
hücrede yakalar. `results_orig.json` içinde 15 `exact-sup2` + 15 `exact-inf2`
= 30 kontrolün tamamı geçmiştir — geçmeleri yapısal olarak zorunludur
(`x==x`), bilgi taşımaz. Bu 30 kontrol v2'de silindi; yerine 48 bağımsız
kapalı-form + altın tablo hücresi (`T2.sup-val/inf-val`), `T2.old-blind`,
`T2.new-catches`, `T2.pythag-sign` geldi.

Dürüstlük notu: `T2.sup-val/inf-val` altın hücreleri orijinal koda karşı da
geçer (orijinal `sup_closed/inf_closed` doğrudur; bozuk olan erişim kuralı ve
paylaşılan-mantık riskidir). Bunlar regresyon kilidi + bağımsız şahittir;
bozuk-varyanta karşı ayırt edicilikleri yukarıda gösterildi.

## T4 — negatif rho tanımsız (`driver_d.py`)

```
vektor=999 kotu=0 en-kucuk-rho^2=1/3 (1/8=1/8)
rho=-3/10 mumkun mu? True -> hicbir birim belge uretemez (T4.neg-impossible)
```

Okuma: 999 rastgele rasyonel vektörde (d=2,3,4,5,8) `1/d<=rho^2<=1`, `rho>0`
tam `Fraction` ile doğrulandı. `rho=-0.3` hiçbir birim belge üretemez; bu
nedenle `(0.5,-0.3,0.05,"negative-rho")` gerçekleştirilebilir listeden
çıkarılıp soyut-matematik (`T4.abstract-agree/contain`, belge iddiasız)
olarak saklandı; değişiklik `T4.record-change` ile kayıtlıdır.

## T6 parantez düzeltmeleri — güçlendirme (`driver_d.py`)

```
d=4: sup_attained = True inf_attained = True -> aralik [0.5,1] (orijinal metin '(0.5,1]' YANLIS)
C: sup_attained = True inf_attained = True -> aralik [3/5,1] (orijinal metin '(3/5,1]' YANLIS)
```

Okuma: değer iddiaları (`E.signonly-vacuous`, `C.supA-infA`) önce-sonra aynı
olduğundan tek başlarına ayırt edici değildir — metin (parantez) düzeltmesidir.
Güçlendirme: iki uçta da `sup_attained/inf_attained is True` (N boş) yürütmeyle
gösterildi; kapalı parantez zorunludur. Bu yüzden "geçti" demek yerine yukarıdaki
uç-erisim kanıtı eklendi; kural gereği zayıf haliyle bırakılmadı.

## T5 — yazıldı; yanılabilirlik kırık-sınırla gösterildi

```
T5 vakalari: 2716 (d-dagilimi {2:523, 3:534, 4:549, 5:552, 8:558})
u: neg 1180, pos 1129, zero 407; u=0: 407, |u|=1: 142, u<-0.9: 252
kirik sinir (x999/1000): 592/2716 red; en siki slack 0 (592 vaka, rhs>0)
en siki katisiz bagil: 3/2212 ~ %0.1356
```

Okuma: 2716 `(q,x)` çifti tam `(d·QX−S1·Sq)²≤(d·Q2−Sq²)(d·X2−S1²)` ile
denetlendi (`E` yalnızca `u=1` noktasını kapsıyordu; `u` artık iki işaretli
genel aralıktadır). Orijinalde karşılığı yoktu (boşluk), bu yüzden
ayırt edicilik orijinal-karşı değil kırık-varyantla gösterildi: binde bir
daraltılmış sınır 592 vakada kalır. Türetme + kapsama `T5_EVIDENCE.md` içinde.

## T6 — haklı çıkarılan 8 kontrol; float sertifika açık boşluk

```
T6: 8/8 (bracket-d4, bracket-C, E-point, 3 D tanigi, nondegenerate, point-regime)
D taniklari: orthogonal-center q=(1,-1,7,-7) x=(1,0,0,0); failure-wide q=(3,-4)
x=(0,1) (alt-ucta tam esitlik); query-coded-doc F ornegi (u2=1/27, rho2=25/27)
ACIK: float nicem sertifikasi, C.tie ikiligi, aligned 0.99 tanigi (denetlenmedi)
```

Okuma: el-yazması D `t` değerlerinin 3/4'ü tam vektör tanığına bağlandı;
`[0.5,1]`/`[3/5,1]` kapalı-parantez uç-erisimle kilitlendi; E'nin nokta-aralık
olduğu (`u²=1`) kaydedilip sistematik dejenere-olmayan kapsama T5'ten sayıldı
(>1000). Float sertifika tam karara indirgenemedi — zayıf test uydurulmadı.

## Orijinalde kalıp düzeltmede geçenlerin listesi

`T1.sup-fixed-true`, `T1.inf-fixed-true`, `T1.witness-sup`, `T1.witness-inf`,
`T1.face-orig-wrong-count`, `T1.d3-cell-orig-blind`, `T2.new-catches` (+ altın
tabloda bozuk varyantı yakalayan 10 sup hücresi), `T3.new-catches-face`,
`T4.record-change` (+ `T4.neg-impossible` kaydı). `T1.sup-orig-false`,
`T1.inf-orig-false`, `T2.old-blind`, `T3.old-blind-face` körlüğü belgeleyen
(kasıtlı geçen) kontrollerdir. T5/T6 yeni testtir, orijinalde karşılığı
yoktur: T5'in ayırt ediciliği kırık-sınır deneyiyle (592 red), T6'nınki
vektör tanıklarıyla gösterildi.
