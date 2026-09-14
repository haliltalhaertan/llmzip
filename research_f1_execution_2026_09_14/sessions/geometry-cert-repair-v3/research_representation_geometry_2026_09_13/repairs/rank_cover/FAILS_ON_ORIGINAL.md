[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Orijinalde başarısız (her test için koşu kanıtı)

Kural: C1'de davranış değişmez; "orijinal" = kırık varyant (mutant). C3'te "orijinal" = sarmalayıcısız mantık.
Her satır koşuda gösterildi (`coverage_v2.py` 48/48 PASS).

## C1 (mutant öldürme)
| Test | Kırıkta (FAIL) | Doğruda (PASS) |
|---|---|---|
| domain | mutant STRICT dir 0 | DOMAIN_FAIL |
| deg1 (P=4z) | mutant UNRESOLVED | STRICT −1 |
| deg0 (P=−3) | mutant UNRESOLVED | STRICT −1 |
| varies | mutant STRICT dir 1 | ISOLATED_TIES VARIES |
| pt (certify) | mutant UNRESOLVED | PERSISTENT_TIE 0 |
| PT-topk | kontrolsüz mutant TIES_PRESENT (PT'ye ulaşır) | SAMPLE_TIED (ulaşılamaz) |

Ek: taban S6 tekrarı deg0/1 içermez (yalnız 2/3); yeni girdiler deg0/1'i rational+sturm günlüğüne sokar.
Taban DOMAIN_FAIL/VARIES/CERT-PT satırlarını vurmaz; yeni girdiler vurur.

## C3 (adlı retler)
Sabit çift `(1,0,1,0)/(2,0,1,0)`:
| Durum | Orijinal (FAIL: ret yok) | Düzeltme (PASS) |
|---|---|---|
| L==R (1,1) | certify STRICT dir 0 (sahte; gerçek −1) | INPUT_ERROR EMPTY_INTERVAL |
| L>R (2,1) | certify STRICT −1, [1,2] ile aynı (sessiz takas) | INPUT_ERROR INVERTED_INTERVAL |
| L=0 (0,1) | certify STRICT −1 (şartname z>0) | INPUT_ERROR NONPOSITIVE_LEFT |
| L<0 (−1,2) | certify kabul | INPUT_ERROR NONPOSITIVE_LEFT |
| topk L==R | CERTIFIED_UNSTABLE (sahte sertifika) | INPUT_ERROR EMPTY_INTERVAL |
| topk L>R | CERTIFIED_STABLE (takaslı) | INPUT_ERROR INVERTED_INTERVAL |
| topk L=0 | CERTIFIED_STABLE (kabul) | INPUT_ERROR NONPOSITIVE_LEFT |

Sıra: `L≤0` → NONPOSITIVE_LEFT; `L==R` → EMPTY; `L>R` → INVERTED. Bozuk aralık sertifika üretmez.
Geçerli aralıkta `fixed==orig` (S6 dörtlüsü aynı).

## Sadakat
`orig_verify_snapshot.py` dondurulmuş `verify.py` ile birebir (`diff` temiz).
Gömülü `*_orig` 5/5 C1 girdisinde anlık kopya ile aynı sonucu verir.
Komutlar (hepsi threads=1, bytecode kapalı):
`ml-python -B coverage_v2.py` → checks=48 fail=0 ALL PASS.
`ml-python -B realizable_tangent.py` → checks=12 fail=0 ALL PASS.
