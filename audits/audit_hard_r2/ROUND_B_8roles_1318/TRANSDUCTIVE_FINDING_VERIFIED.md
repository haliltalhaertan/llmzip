[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# R2 KOORDINATOR BULGUSU — Transduktif iyimserlik (dogrulandi)

Tarih: 2026-09-17. Kaynak agaci READ-ONLY; 2205 dosya sha256 degismedi (0 fark).

## Iddianin kaynagi
audit_hard_r2/code (Muse ajani, xhigh) F2: "her yayinlanan RealTalk kod sayisi,
izdusum test arsivinin kendisine uydurulmus halde olculmus".

## Koordinator dogrulamasi
Ajanin tek-arsiv testi (t_inductive_rt.py, RT05) once birebir tekrarlandi,
sonra koordinator 10 arsive genisletti (t_inductive_all10.py, 705 soru,
arsiv-kumelenmis bootstrap 4000 tekrar, seed 20260917).

### Uretim-kimligi kapisi
Yeniden kurulan boru hattinin uretim onbellegiyle isaret farki:
**0 / 858,624 bit** (10 arsivin tamami). Bu, LADDER_REALTALK.md'deki
muhur sayisinin ta kendisi. Yani olculen sey projenin gercek yontemi.

### Capa eslesmesi
TRANS havuzlanmis  sym 46.52 / qscale 49.65
Yayinlanan k96     sym 46.52 / qscale 49.65   -> BIREBIR

## Sonuc (705 soru, 10 arsiv)

| kol | TRANS (yayinlanan rejim) | INDEP (durust rejim) | iyimserlik | CI95 (arsiv-boot) |
|---|---|---|---|---|
| sym    | 46.52 | 18.16 | +28.37 pp | [21.76, 35.03] |
| qscale | 49.65 | 20.00 | +29.65 pp | [23.06, 37.07] |

10 arsivin 10'unda da ayni yon; INDEP hicbirinde kazanmiyor.
Guven araligi sifiri genis farkla disliyor.

### Arsiv kirilimi (qscale)
RT01 56.47->23.53 | RT02 47.14->15.71 | RT03 73.97->15.07 | RT04 53.52->29.58
RT05 60.00->24.29 | RT06 29.73->13.51 | RT07 41.43->14.29 | RT08 30.00->5.71
RT09 53.97->28.57 | RT10 49.15->32.20

En yuksek TRANS skoru (RT03 73.97) en buyuk dususu yasiyor (-58.90).

## Anlami
Izdusum matrisi, sonradan aranacak belgelerden ogreniliyor. Gercek kullanimda
arsiv onceden elde olmaz. Dolayisiyla yayinlanan tum RealTalk kod sayilari
ulasilamaz bir avantaj iceriyor ve "transduktif rejim" olarak etiketlenmeliydi.

## Karara etkisi
DUR yonu GUCLENIYOR (kusur kodun lehineydi): durust rejimde 48B kodun
adil BM25'e (65.67 Hit@10) acigi cok daha buyuk.
ANCAK yayinlanan mutlak sayilar bu aciklama olmadan alintilanmamali.

## Sinirlar
- Yalnizca RealTalk k=96. PerLTQA/LoCoMo/LME ve k=192/384 OLCULMEDI.
- INDEP kurulumunda OOV terimler dogal olarak dusuyor; bu durust rejimin
  parcasi, ayrica ayristirilmadi.
- Tek indüktif tasarim denendi (diger 9 arsiv); alternatif (harici korpus)
  denenmedi.

## Kanitlar
- code/t_inductive_rt.py, code/t_inductive_all10.py (koordinator)
- code/INDUCTIVE_ALL10.json (per-soru sonuclar dahil)
- code/INDUCTIVE_ALL10.log
- code/CODE_AUDIT.md (ajan raporu, F2)
