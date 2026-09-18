[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]

# R4 ONCELIK HARITASI — hangi denetlenmemis klasor yayinlanan sayiya bagli?

Yontem (mekanik, tahmin degil):
1. Yayin belgelerinden (FINAL_STATE/REPORT/DECISION_TESTS/LADDER/EXTERNAL_AUDIT3)
   163 imza sayisi cikarildi; >=10 olan 138 tanesi arama deseni yapildi.
2. Her denetlenmemis klasorde .md/.json/.jsonl/.csv/.txt/.py/.log tarandi;
   bir dosyada 3+ farkli yayin sayisi geciyorsa "yayinla bagli" sayildi.
3. Ek olarak kod-bagimliligi: top10_comparison_r1 kodu hangi klasore atif yapiyor.

## SONUC TABLOSU

| klasor | taranan | 3+ eslesen dosya | farkli sayi | kod bagi | ONCELIK |
|---|---|---|---|---|---|
| incoming_20260916b | 3633 | 168 | 143 | - | **P1** |
| incoming_20260916 | 142 | 13 | 143 | - | **P1** |
| bench3 | 70 | 0 | 0 | **27 .py atif** | **P1 (kaynak)** |
| parallel_ideas_r1 | 1916 | 35 | 75 | - | P2 |
| scratch | 118 | 10 | 43 | - | P2 |
| hr-consolidation | 300 | 3 | 34 | - | P3 |
| chat_literature_review_20260915 | 77 | 9 | 24 | - | P3 |
| regen | 492 | 7 | 21 | - | P3 |
| agent_out | 150 | 7 | 21 | - | P3 |
| top10_literature_20260915 | 34 | 3 | 20 | - | P3 |
| review_transfer | 535 | 14 | 19 | - | P3 |
| pilots | 73 | 3 | 15 | - | P4 |
| drive | 57 | 2 | 11 | - | P4 |
| reports | 47 | 3 | 7 | - | P4 |
| residual8_pilot_r1 | 127 | 0 | 0 | - | **P5 (bagimsiz)** |
| theory_benchmark_test_v1 | 135 | 0 | 0 | - | P5 |
| math_discovery_2026_09_13 | 55 | 0 | 0 | - | P5 |
| race_2026-09-13 | 46 | 0 | 0 | - | P5 |
| next_route_round1 | 40 | 0 | 0 | - | P5 |
| harness | 15 | 0 | 0 | - | P5 |
| audit_2026-09-13 | 14 | 0 | 0 | - | P5 |
| representation_geometry_fix | 8 | 0 | 0 | - | P5 |
| prereg_race_2026-09-13 | 21 | 0 | 0 | - | P5 |

## YORUM

**P1 — bench3**: sayi icermiyor (ciktisi .pkl onbellek) AMA top10_comparison_r1'in
27 .py dosyasi ona atif yapiyor. TUM RealTalk/PerLTQA temsilleri
`runs/b3a_realtalk/`, `runs/b3b_perltqa/step2_build.py` tarafindan uretiliyor.
Bugunku iki kapi testi (0/858,624 ve 0/1,179,648 bit) bu klasorun CIKTISINI
dogruladi; KODU hic denetlenmedi. Tek nokta arizasi: burada bir hata olsa
butun sayilar birlikte kayar ve kapilar bunu yakalayamaz (kapi = "yeniden
kurulum uretimle ayni", ikisi de ayni hatayi paylasirsa sessiz kalir).

**P1 — incoming_*: ** 168 + 13 dosyada yayin sayilari birebir geciyor.
Bunlar disaridan gelen ajan paketleri. R3'te yalnizca karar ozetine giren
alt kume dogrulandi (digest_brain F7); geri kalani acilmadi.

**P5 — bagimsizlar**: yayin sayisiyla hicbir ortakligi yok. Muhtemelen terk
edilmis ayri deneyler. Denetim onceligi dusuk; ama "celiskili sonuc sessizce
birakildi mi" sorusu icin hizli tarama yeterli.

## ONERILEN R4 ROL DAGILIMI (10 ajan)

1. bench3_realtalk   — runs/b3a_realtalk/ uretici kod + adapter dogrulugu
2. bench3_perltqa    — runs/b3b_perltqa/step0..step2 zinciri + excluded arsivler
3. incoming_b_core   — incoming_20260916b, yayina giren 168 dosya
4. incoming_b_rest   — ayni paketin geri kalani + incoming_20260916
5. parallel_ideas    — parallel_ideas_r1 (111 .py, 1691 json)
6. regen_review      — regen + review_transfer (yeniden uretim iddialari)
7. scratch_agent     — scratch + agent_out + pilots + drive
8. hr_lit            — hr-consolidation + iki literatur klasoru
9. orphans           — P5 klasorlerin tamami: celiskili terk edilmis sonuc var mi
10. ladder_indep     — YARIM KALAN IS: k=192/384 + LME/LoCoMo korpus-uyarlama testi

Not: 10. rol kotadan yarim kaldi (leak_lme_locomo).
