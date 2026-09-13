# AUDIT-1 final report — [LOCAL AUDIT] tie-convention robustness + provenance (continuation)

Scope: LOCAL only. Read-only `/mnt/c/Users/MDP/dev/llmzip-work/`; writes only `/tmp/audit1/`;
no network; system python3 (numpy). Continuation of a SIGTERM-killed session: Task B numbers
reused verbatim from `/tmp/audit1/taskB_numbers.json` (STAND); Task C-real + Task D finished here.

## Task B recap (reused, not redone)

LME n=470, fractional R@3, frozen tie protocol: floatY(uncentered) `0.4401063829787234`,
floatC(centered) `0.4415957446808511`, signC native `0.5419751773049645` (native reproduced
exactly, diff 0.0). Centering gain +0.14893617021277117pp (+0.149pp); binarization gain
+10.037943262411336pp (+10.038pp); total vs uncentered +10.186879432624107pp (+10.187pp).
W/T/L sign-vs-floatC 122/304/44; floatC-vs-floatU 7/458/5. Verdict S1: the +10pp is carried
by binarization; centering contributes only ~0.15pp. The 44.16% anchor is the CENTERED float
(`0.4415957446808511`); the uncentered complement `0.4401063829` is AUX (both in frozen
T4C2 aggregate — see Task D).

## Task C-real — method (mirrors `race_sign.py` EXACTLY)

- Arms: NATIVE96 (full 96-bit sign code); SPREAD80 / BOT80 per-archive variance subsets
  (`order_desc=argsort(var,stable)[::-1]`, SPREAD=`order_desc[round-half-up linspace(0,95,80)]`,
  `eff_k==k` asserted); RAND80_s2 = global random draw shared across archives, panel seed
  `93000+10*width_idx+j` with `width_idx={48:0,64:1,80:2}` → **RAND80_s2 seed = 93022
  (verified: recomputed from the formula AND matches `arms.RAND80_s2.seed=93022` in the
  official details); TOP48 = per-archive top-48 variance.
- Column logic: Hamming on sign bits (`C>=0`, `qC>=0`; LME per-question archive, LoCoMo
  per-conversation archive × per-question query rows). `a` = #strictly closer than gold,
  `t` = #at EXACTLY gold's distance EXCLUDING gold (group size `t+1`).
- Conventions per gold: `FR_pess=1[a+t<=2]`; `FR_exp=min(1,(3-a)/(t+1))` if `a<=2` else 0;
  `FR_opt=1[a<=2]`; question score = mean over its golds (MATH-1 identity, cf.
  `race_sign.py:model_fr`, lines 145-162). **Disclosure:** LME is 174 single-gold /
  296 multi-gold; LoCoMo gold-count mix (valid n=1535) likewise multi. The brief's
  single-gold formula is therefore applied per-gold and averaged — identical to the frozen
  `model_fr` for FR_exp.
- Tie priorities: `5_100_000+key*100_000+t*100+99`, key=LME lex rank / LoCoMo conv ordinal,
  20 trials, `lexsort((priority,distance))` top-3 — mirrored exactly.

## Task C-real — validation (recomputed vs official `race_sign_details.json` per-q arrays)

- Our remeasured mc-20 == official `fr` per-q arrays BIT-EXACTLY: max|diff| = 0.0 on all
  5 arms × both benchmarks → construction mirror confirmed exact.
- Our analytic FR_exp == official `model` per-q arrays exactly (max|diff| = 0.0 LME;
  ≤5.6e-17 LoCoMo float noise) → `a,t` extraction confirmed exact.
- FR_exp(analytic) vs official mc-20 per-q: max|diff| LME NATIVE 0.150, SPREAD80 0.133,
  RAND80_s2 0.100, BOT80 0.125, TOP48 0.200; LoCoMo NATIVE 0.300, SPREAD80 0.250,
  RAND80_s2 0.250, BOT80 0.167, TOP48 0.250. This is expected 20-draw MC noise
  (mean|diff| = official model_MAE: LME NATIVE 0.004097, LoCoMo NATIVE 0.002897), NOT a
  construction mismatch. Tie-free questions exact: LME NATIVE tie-free max|exp−mc| =
  2.22e-16. LME NATIVE gold-tie share 270/470 = 0.574 (any gold sharing its distance;
  distinct from the 0.234 top-3-boundary tie rate).

## Task C-real — DECISIVE TABLE (means; gaps = SIGN − competitor, pp)

LME n=470:

| arm | pess | exp_analytic (official mc20) | opt |
|---|---|---|---|
| NATIVE96 | 0.5207801418439717 | 0.5421335697399526 (0.5419751773049645) | 0.5655319148936171 |
| SPREAD80 | 0.5070921985815603 | 0.5249645390070922 (0.5252588652482270) | 0.5436524822695035 |
| RAND80_s2 | 0.5040425531914894 | 0.5230496453900709 (0.5244539007092198) | 0.5441843971631205 |
| BOT80 | 0.5023049645390071 | 0.5231737588652482 (0.5228510638297872) | 0.5453546099290780 |
| TOP48 | 0.3022340425531915 | 0.3520567375886524 (0.3494946808510638) | 0.4061702127659574 |

LME gaps (pp): pess {SPREAD80: 1.368794, RAND80_s2: 1.673759, BOT80: 1.847518};
exp_analytic {SPREAD80: 1.716903, RAND80_s2: 1.908392, BOT80: 1.895981};
opt {SPREAD80: 2.187943, RAND80_s2: 2.134752, BOT80: 2.017730};
official-mc {SPREAD80: 1.671631, RAND80_s2: 1.752128, BOT80: 1.912411}.
Nearest competitor: SPREAD80 under pess/exp/mc (official nearest, ANALYSIS.md);
under opt the nearest is BOT80 (gap 2.017730pp) — disclosed, still positive.

LoCoMo n=1535:

| arm | pess | exp_analytic (official mc20) | opt |
|---|---|---|---|
| NATIVE96 | 0.2220304722421986 | 0.2369591212262222 (0.2365471466644105) | 0.2537041188995586 |
| SPREAD80 | 0.2103270724931963 | 0.2240353864376665 (0.2243285460467871) | 0.2408110185146016 |
| RAND80_s2 | 0.1919911539781247 | 0.2079605325004348 (0.2079832820997316) | 0.2283918054439227 |
| BOT80 | 0.2211437549059699 | 0.2356518760697448 (0.2354614220379693) | 0.2517750562864569 |
| TOP48 | 0.1155939475780441 | 0.1319846460941498 (0.1318263037126804) | 0.1544701690764155 |

LoCoMo gaps (pp): pess {SPREAD80: 1.170340, RAND80_s2: 3.003932, BOT80: 0.088672};
exp_analytic {SPREAD80: 1.292373, RAND80_s2: 2.899859, BOT80: 0.130725};
opt {SPREAD80: 1.289310, RAND80_s2: 2.531231, BOT80: 0.192906};
official-mc {SPREAD80: 1.221860, RAND80_s2: 2.856386, BOT80: 0.108572}.
Nearest competitor: BOT80 under ALL conventions (official nearest, ANALYSIS.md).

## Task C verdict (S2) — write the numbers verbatim

- LME: SIGN − SPREAD80 = +1.368794pp (pess) / +1.716903pp (exp analytic; official mc
  +1.671631pp) / +2.187943pp (opt). Official race disposition +1.67pp MID (kill −6.4 /
  promote +2.0) SURVIVES under pessimistic ties: gap stays positive at +1.37pp, same MID zone.
- LoCoMo: SIGN − BOT80 = +0.088672pp (pess) / +0.130725pp (exp analytic; official mc
  +0.108572pp) / +0.192906pp (opt). Disposition +0.11pp MID SURVIVES pessimistic ties at
  +0.089pp, same MID zone (thin but positive; CIs already include 0 per ANALYSIS.md —
  parity conclusion unchanged, not strengthened).
- S2 overall: tie convention does NOT carry either race result. Gaps are monotone
  pess < exp < opt on both benchmarks (adversarial resolution hurts SIGN least-relative:
  LME pess gap 1.37 vs opt 2.19; LoCoMo 0.089 vs 0.193).

## Task D — anchor provenance (S3)

- Native 0.5419751773049645: `drive/t4c3/V52_T4C3_aggregate.csv:2` (NATIVE_SIGN96 Fractional_R3);
  `drive/t4c3/V52_T4C3_COMPUTE_REPORT.md:7` ("NATIVE_SIGN96 Fractional R@3: 54.197517730496%");
  `drive/t4c3/V52_T4C3_sanity_checks.csv:3` (native reproduction PASS);
  `drive/t4c3/V52_T4C3_POST_RUN_MANIFEST.json:7` ("S_native"); frozen in
  `race_2026-09-13/rb2/race_sign.py:32` (LME_ANCHOR) with pre-pass gate diff 0.0.
  Definition (sign of what): `drive/v52_t4c3_coordinate_axis_probe.py:109-110`
  (Y=normalize(SVD…); mu=Y.mean; C=Y−mu; qC likewise) + retrieval lines ~149
  (D=Cr>=0 sign bits, Hamming). TRACED.
- float96 CENTERED 0.4415957447 (44.159574%): repo-frozen
  `docs/v52/task4c2/V52_T4C2_aggregate.csv:4` (FLOAT96_CENTERED …0.44159574468085105;
  1-ulp vs recomputed …111 — disclosed); `docs/v52/task4c2/V52_T4C2_COMPUTE_REPORT.md:12`
  (| FLOAT96_CENTERED | … | 44.159574% |); centering split
  `docs/v52/task4c2/V52_T4C2_centering_effect.csv:2`. Metric/code:
  `docs/v52/task4c2/v52_t4c2_centering_geometry.py:69/74/75` (rank_float/cosine top-3 +
  stable_archive_seed tie rule per Task C synthetic header). TRACED (to T4C2; T4C3 seal
  lists it as FLOAT96_CENTERED_INVARIANCE_REFERENCE method,
  `drive/t4c3/V52_T4C3_PRE_RUN_SEAL.json:23`).
- Uncentered complement 0.4401063829 (AUX): same T4C2 aggregate.csv:3 + report:11
  (44.010638%). TRACED as AUX.
- ITQ96 37.61% (LME): `drive/t4c3/V52_T4C3_aggregate.csv:3`
  (ITQ96_CENTERED …0.376141134751773); envelope
  `drive/t4c3/V52_T4C3_ITQ_HAAR_ENVELOPE.csv:2`; report:17 ([ITQ WITHIN FULL-HAAR ENVELOPE]).
  Task-B recompute mean_itq 0.3761411347517731 matches to 1e-16. TRACED.
- Haar96 38.27% (LME): full-block-96 row `drive/t4c3/V52_T4C3_aggregate.csv:9`
  (BLOCK_ORTHO_SIGN96,96.0 …0.3827166666666667); report:8
  ("Full-Haar96 mean Fractional R@3: 38.271666666667%"); seeds report:10. TRACED.
- D96 −15.9258 (LME): report:9 ("D96: -15.925851 pp"); recompute from constants
  0.3827166666666667−0.5419751773049645 = −15.925851063829777pp (taskB_numbers.json).
  Cross-check vs `drive/t4d/…`: T4D is the LoCoMo report (different D, −9.8839); the LME
  D96 cross-check against the T4C3 report PASSES; t4d carries no LME D96 (correctly —
  flagging only to avoid misreading). TRACED.
- Haar96 13.77% (LoCoMo): `drive/t4d/V52_T4D_COMPUTE_REPORT.md:8`
  ("HAAR96 mean Fractional Evidence Recall@3: 13.770827054136%"); seeds :10. TRACED.
- LoCoMo −9.8839pp: same report:9 ("D_LoCoMo = Haar − Native: −9.883887612 pp");
  native 23.654714666441% (:7) reproduces the LoCoMo anchor 0.23654714666441054. TRACED.
- LoCoMo native anchor code: `race_sign.py:33` (LOCOMO_ANCHOR) + pre-pass gate diff 0.0.
- Flagged untraceable: NONE among the listed anchors. Nearest-miss disclosed: float96's
  frozen *definition* (cosine float ranking) lives in T4C2 geometry code, not in any T4C3
  file — T4C3 only names it as a reference method; and the T4C2 CSVs cited are the
  repo-frozen copies (`llmzip-audit/docs/v52/task4c2/`), whose `/mnt/c` counterparts were
  not separately re-verified this run (read-only spot check only).

## NOT checkable / limits

- Per-question arrays for float/ITQ/Haar (Task D anchors) were not re-derived per-q here
  beyond Task-B means; provenance is file+line, not an independent rerun (except ITQ mean
  cross-check).
- LoCoMo per-archive builder re-run not needed: reuse of frozen `locomo_{ci}.pkl`
  (sha `3f7f091f…` per brief) with order-assert passed; no rebuild, no subset cap triggered.
- `audit1_details_final.json` carries per-q exp/pess/opt/mc + official fr/model for the
  5 race arms × both benchmarks (this run's exact reconstruction, mc bit-identical).

## Files written

- `/tmp/audit1/taskC_real.py`, `/tmp/audit1/taskC_real_locomo.py`, `/tmp/audit1/taskC_tiefree.py`
- `/tmp/audit1/taskC_LME_perq.json`, `/tmp/audit1/taskC_LoCoMo_perq.json`
- `/tmp/audit1/report.md` (this file), `/tmp/audit1/audit1_details_final.json`
