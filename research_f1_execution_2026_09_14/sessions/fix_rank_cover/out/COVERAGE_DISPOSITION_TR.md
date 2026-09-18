[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Kapsam kararı (C1+C3)

## Supersedes
| Eski durum | Yeni durum | Kanıt |
|---|---|---|
| DOMAIN_FAIL testsiz | kapsandı | `coverage_v2.py` C1-domain |
| P derece-1 testsiz | kapsandı | C1-deg1 + deg günlüğü |
| P derece-0 testsiz | kapsandı | C1-deg0 + RAT-EARLY |
| VARIES testsiz | kapsandı | C1-varies |
| certify PT dönüşü testsiz | kapsandı | C1-pt |
| topk 524,531 PT-doğru dalı testsiz | ulaşılamaz (ispat) | aşağıda + C1-PT-* |
| sturm None dalı yorumsuz | ulaşılamaz (ispat) | aşağıda |
| L==R/L>R/L≤0 sessiz kabul | adlı ret | C3-* INPUT_ERROR |

## Dal tablosu
| Dal | Durum |
|---|---|
| certify DOMAIN_FAIL | kapsandı |
| P derece 1 (rational+sturm) | kapsandı |
| P derece 0 sabit≠0 (RAT-EARLY+sturm) | kapsandı |
| VARIES | kapsandı |
| certify PERSISTENT_TIE | kapsandı |
| topk 524,531 PT-doğru | ulaşılamaz (ispatlı) |
| sturm None (sıfır polinom) | ulaşılamaz (ispatlı) |
| hâlâ kapsanmayan | yok (bu kapsamda) |

Not: topk 524,531 satırları taban koşuda çalışır; testsiz olan PT-doğru alt dalıdır.

## İspat 1: topk üzerinden PT ulaşılamaz
`PERSISTENT_TIE` ⇒ `dirs={0}` ⇒ her alt aralıkta `is_zero` ve örnekte bağ.
`P≡0` ⇒ `|f|≡|f|`; örnekte bağ ⇒ o aralıkta işaretler eşit (işaretler kesmelerle sabit).
`P≡0` ve tanım kümesinde `D>0` iken `N1(z0)=0 ⇔ N2(z0)=0`
(`N1²D2=N2²D1` noktasal). Uçlar: sıfırsa ortak-sıfır bağ; değilse iç işarete süreklilikle eşit.
Sonuç: kapalı J'nin her noktasında bağ; 5 topk adayı bağlı.
O hâlde `topk_cert` bağ-kopisiz örnek bulamaz, `SAMPLE_TIED` erken döner; 524,531'e PT ile gidilemez.
Hesap: C1-PT-all5-tied, C1-PT-topk-sample-tied. Örnek kontrolsüz mutant PT'ye ulaşır, test onu öldürür.
Denetim iddiası doğrulandı; ulaşan girdi kurulamadı.

## İspat 2: sturm None ulaşılamaz
`sturm_open_count` None yalnız sıfır polinomda döner. `is_zero` ise sturm öncesi ayrılır:
örnekte bağ ⇒ persistent-tie; zıt işaret ⇒ continue; aynı-katı işaret ⇒ UNRESOLVED.
Sıfır polinom sturm'a gitmez.

## Girdiler (Fraction)
- domain: `(0,0,0,0)/(1,0,1,0)` [1/16,16] → DOMAIN_FAIL.
- deg1: `(−2,0,1,0)/(−2,0,1,1)` [1/4,2], P=4z → STRICT −1.
- deg0: `(1,0,1,0)/(2,0,1,0)` [1/4,2], P=−3 → STRICT −1.
- varies: S5 çifti [1/4,2] → ISOLATED_TIES VARIES, ties=[1].
- pt: S2 çifti [1/16,16] → PERSISTENT_TIE 0.
C3: `validate_interval` sırası pozitiflik→boşluk→yön; bozuk aralık sertifika üretmez.
