# ROUND-3 ÇALIŞTIRMA GÜNLÜĞÜ (kanıt)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[LOCAL EXPLORATORY] Koşular: 2026-09-13, Windows venv (Python 3.13.15 / NumPy 2.3.5),
OMP/MKL/OPENBLAS/NUMEXPR=1. Scriptler donmuş regen önbelleklerini okur; hiçbir şey repo'ya yazılmaz.

## Deney 1 — LME (harness/deney1_lme.py, 186 s, exit 0)

```
split 0..9: train=236 test=234 (tip-dengeli)
loaded 470 pkls (11s)
GATE1 native recompute: max_abs_diff=1.110e-16 mean_recomp=0.5419751773 mean_stored=0.5419751773
SPLIT 0: native=0.5233 drop64=0.4646 alone64=0.4754 rand_best64=0.4835 gap64_vs_best=-1.89pp CI90=[-5.29,-0.33]
SPLIT 1: native=0.5477 drop64=0.5121 alone64=0.4848 rand_best64=0.5306 gap64_vs_best=-1.85pp CI90=[-5.16,-0.22]
SPLIT 2: native=0.5162 drop64=0.4870 alone64=0.4655 rand_best64=0.4792 gap64_vs_best=+0.78pp CI90=[-2.05,+1.99]
SPLIT 3: native=0.5410 drop64=0.4751 alone64=0.4944 rand_best64=0.5062 gap64_vs_best=-3.11pp CI90=[-6.71,-1.50]
SPLIT 4: native=0.5534 drop64=0.4990 alone64=0.4710 rand_best64=0.5208 gap64_vs_best=-2.18pp CI90=[-5.39,+0.56]
SPLIT 5: native=0.5650 drop64=0.5252 alone64=0.4925 rand_best64=0.5138 gap64_vs_best=+1.14pp CI90=[-2.60,+2.03]
SPLIT 6: native=0.5506 drop64=0.5119 alone64=0.4646 rand_best64=0.5193 gap64_vs_best=-0.74pp CI90=[-3.76,+1.15]
SPLIT 7: native=0.5315 drop64=0.4909 alone64=0.4586 rand_best64=0.4996 gap64_vs_best=-0.87pp CI90=[-4.34,+0.16]
SPLIT 8: native=0.5523 drop64=0.4949 alone64=0.4917 rand_best64=0.5174 gap64_vs_best=-2.26pp CI90=[-6.03,-0.96]
SPLIT 9: native=0.5167 drop64=0.4826 alone64=0.4549 rand_best64=0.4974 gap64_vs_best=-1.48pp CI90=[-4.59,+0.33]
SUMMARY {"drop64_gap_vs_best_pp": {"mean": -1.2460826210826181, "median": -1.6647079772079714,
"range": [-3.107193732193725, 1.1388888888888893], "wins": "2/10"},
"alone64_gap_vs_best_pp": {"mean": -3.1452635327635305, "wins": "0/10"},
"drop48_gap_mean_pp": -2.3631054131054148, "alone48_gap_mean_pp": -3.86680911680912,
"drop32_gap_mean_pp": -3.4759971509971535, "alone32_gap_mean_pp": -2.7661680911680935,
"var_worst_all": false, "top64_overlap_min": 50}
wrote deney1_lme_details.json (831,494 bytes)
```

`var_worst_all=false` açıklaması: 30 kontrolün 29'u "var en kötü"; tek istisna s9-k64'te en kötü
kolün delta olması (delta 0.3998 < var 0.4298) — var yine dipte, "var kazandı" durumu YOK.

## Deney 1 — LoCoMo (harness/deney1_loco.py, 154 s, exit 0)

```
per-axis arrays done; GATE native: 0.23654714666441054 vs anchor diff 0.0
SPLIT 0..9 (yukarıdaki rapor tablosu)
SUMMARY {"drop64_gap_vs_best_pp": {"mean": -0.14953631584987523, "median": -0.3902,
"range": [-1.174, 1.870], "wins": "2/10"},
"alone64_gap_vs_best_pp": {"mean": -0.09175066237628539, "wins": "5/10"},
"drop48_gap_mean_pp": -0.8034913337669541, "alone48_gap_mean_pp": -0.47253661684382803,
"drop32_gap_mean_pp": -0.8352395625661359, "alone32_gap_mean_pp": -0.47777296764676774,
"var_worst_all": true, "top64_overlap_min": 50}
wrote deney1_loco_details.json (1,843,468 bytes)
```

## Ek koşular

- Bootstrap: her split, B=2000, soru-eşli; resample içinde yeniden best-of-10 (script içinde).
- `HASHES_ROUND3.txt`: script+artefakt SHA-256 listesi (6 girdi).
- Muse oturum çıktıları: `muse_sessions/{d2,d4,...}/` (toplandıkça eklenir).
