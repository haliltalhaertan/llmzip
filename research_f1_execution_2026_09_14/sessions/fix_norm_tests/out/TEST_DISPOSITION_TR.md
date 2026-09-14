[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# TEST_DISPOSITION_TR — T1..T6 işlem kaydı

## Supersedes tablosu (dondurulmuş `verify.py`, commit `1021083` satırları)

| Kusur | Orijinal konum | Sorun | Bu paketteki karşılık |
|---|---|---|---|
| T1 | `verify.py:70-78` (`sup_attained`), `80-86` (`inf_attained`) | eksen dalı m=0'da yanlış (tekli-eksen kuralı) | `verify_v2.py:92-115` yüz kuralı (`N<=J`); `run_T1` (15 kontrol) |
| T2 | `verify.py:160-165` (`B2.exact-sup2/inf2`) | `x==x` totolojisi (15+15=30) | silindi; `run_T2` bağımsız kapalı-form + `D2_GOLD` (51 kontrol) |
| T3 | `verify.py:171-177` (`B2.att-consistency`) | `False==False` ile geçer, T1'i yakalayamaz (24 hücre) | kaldırıldı; `run_T3` altın-tablolu erişim (51 kontrol) |
| T4 | `verify.py:302` (`(0.5,-0.3,0.05,"negative-rho")`, `D_CASES` `296-304`) | rho her zaman pozitif; durum tanımsız | gerçekleştirilebilir listeden çıkarıldı, soyut saklandı; `run_T4` (7 kontrol) |
| T5 | `run_top3` (`351-400`; `u=float(q@c)` satır 373), `D_CASES` el-yazması `t` | vektör-tabanlı genel-durum aralık testi yok (`u=1` hizalı) | **kapandı**: `run_T5` 2716 vaka, tam `(*)` (5443 kontrol) |
| T6 | `C.supA-infA` (221-223), `E.signonly-vacuous` (369-370), `C.tie-*` (243-266) | el-yazması `t`; hep-nokta aralıklar; float sertifika; `(0.5,1]`/`(3/5,1]` parantezleri | parantez ikilisi + 3 D tanığı + E-nokta kaydı + dejenere-olmayan sayım (8 kontrol); float sertifika/C.tie **açık boşluk** |

## Bölüm başına durum

**T1 — eksen m=0 yüz kuralı.** Eski kural m=0'da `N`'yi tekli eksene sığdırmaya
çalışır; `N={1,2}`, `J={1,2}` iken `False` verir. Doğrusu `N<=J` (`True`;
tanık `x=(0,-3/5,-4/5)` birim, `F` içinde, `q.x=0`). D2'deki 12 m=0 hücresinde
eski/yeni aynıdır (`|N|<=1`) — hata d>=3'te gizlenir. Kanıt: `FAILS_ON_ORIGINAL.md` T1/T3.

**T2 — 30 totoloji silindi.** `ks[1]==vnorm2(proj_cone(s,q))` aynı yardımcıyı
iki yanda çağırır. Bozuk izdüşürücüye (16/25 üretir) karşı eski tarz 8/8 geçer;
altın karşılaştırma 10 hücrede yakalar. Yerine: 48 bağımsız kapalı-form +
altın tablo hücresi, `old-blind/new-catches`, Pisagor+işaret kimlikleri.

**T3 — `B2.att` kaldırıldı.** Yüz örneğinde `member_F(ys)=False`,
`orig-att=False` → eski kontrol geçer. Yeni `sup_attained=True`; tanık üstte.
48 D2 altın-tablo hücresi eski/yeni aynı sonucu verir (d=2'de erişim çakışır):
bunlar regresyon kilididir, ayırt edicilik yüz hücresindedir.

**T4 — negatif rho kaydı.** 999 rasyonel vektörde `1/d<=rho^2<=1`, `rho>0`
(`Fraction`). `(0.5,-0.3,...)` silinmedi, yeri değişti: `D_ABSTRACT` içinde
belge iddiasız soyut `(u,rho)` matematiği olarak durur; `T4.record-change`
bunu kilitler. d=4 alt uç erişilir (`rho(e1)^2=1/4`).

**T5 — KAPANDI.** `run_T5`: 2716 `(q,x)` çifti (`d∈{2,3,4,5,8}`), her vaka
tam `(*)` + rho sınırları ile denetlenir (vaka başına 2 kontrol + 11 meta =
5443). `u` iki işaretli genel aralıkta (neg 1180, pos 1129, zero 407;
u=0: 407, |u|=1: 142, u<−0.9: 252); rho her `d` için `[1/√d,1]` tam
ulaşılır; sıfır-koordinat (one 729, multi 193, face 52), karışık/tek-işaret
(2019/697) kapsanır. Kırık-sınır (`×999/1000`) 592 vakayı reddeder; en sıkı
boşluk 0 (592 vaka). Kanıt: `T5_EVIDENCE.md`.

**T6 — kısmi, haklı çıkarılan kadar.** İki parantez düzeltmesi uç-erisimle
kilitlendi (`T6.bracket-d4/C-closed`: `[0.5,1]`, `[3/5,1]`); el-yazması D
`t` değerlerinin 3/4'ü tam vektör tanığına bağlandı (orthogonal-center,
failure-wide siki alt-uç, query-coded-doc); E'nin nokta-aralık olduğu
(`u²=1`) kaydedildi; sistematik dejenere-olmayan kapsama T5'ten sayıldı
(>1000). Toplam 8 kontrol. Float nicem sertifikası (`cert_interval`),
`C.tie` ikili-arama tanıkları ve `aligned` 0.99 tanığı tam karara
indirgenemedi — **açık boşluk** (denetlenmedi, yanlış değil); zayıf test
uydurulmadı.

## Sayım ayrışımı (yürütmeyle doğrulandı)

Orijinal 272 = B2 185 (upper 24, lower 24, reach-sup 24, reach-inf 24,
exact-sup2 15, exact-inf2 15, ys-closed 24, att-consistency 24, approach 11)
+ B3 48 + C 10 + D 10 + E 12 + F 3 + G 3 + H 1.

V2 tam çalıştırma **5791**:

- Korunan: 216 = B2 131 + B3 48 + C 10 + D 8 + E 12 + F 3 + G 3 + H 1
  (içinde yerinde onarılmış 2: `C.supA-infA`, `E.signonly-vacuous` metni).
- Eklenen T1..T4: 124 = T1 15 + T2 51 + T3 51 + T4 7.
- Eklenen T5: 5443 = 2716 vaka × 2 (`T5.cap` + `T5.rho`) + 11 kapsama/meta.
- Eklenen T6: 8.
- Kaldırılan: 56 = 30 totolojik + 24 `B2.att` (kör) + 2 tanımsız-rho D.
- 272 − 56 + 124 + 5443 + 8 = 5791. Önceki gövde 340 ayrıca doğrulandı.

Kanıt referansları: sayımlar `driver_a.py` (`V2-TOPLAM: 340/340`) ve doğrudan
`python3 -B verify_v2.py` (`5791/5791`, çıkış 0); orijinal `272/272`;
ayırt edicilik `driver_b/c/d.py` + T5 kırık-sınır deneyi (592 red) — ham
çıktılar `FAILS_ON_ORIGINAL.md` içinde. Sürücüler `/tmp/.../evidence/`
altındadır, pakete kirletilmedi.
