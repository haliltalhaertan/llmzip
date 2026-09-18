[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — SIGN96 tie rate vs archive size N: contradiction resolved

**Output dir:** `C:/Users/MDP/dev/llmzip-work/agent_out/scale-contradiction/` (additive only;
every llmzip-work cache read-only; git repo untouched; Task4F1 seal respected — only E1/campaign
caches opened).

## Ruling in one line

**Both measurements are internally correct and they measure different processes.** Pooling
unrelated archives makes the K=3 tie rate RISE; growing/shrinking a *single real* archive makes it
FALL above N≈50. Separately, the relayed "54%→26%" is almost certainly **not a tie rate** but the
position statistic `P(d₍₃₎ ≥ t)`, which genuinely falls while the frozen tie rate rises at the very
same N.

## Control (run BEFORE any new number)

| family | sign FR@3 | float FR@3 | delta | frozen target | residual |
|---|---|---|---|---|---|
| LongMemEval | 0.5421335697399526 | 0.4415957446808511 | **+10.053783 pp** | +10.037943 | 0.016 pp |
| PerLTQA | 0.48894479616364206 | 0.551692074528853 | **−6.274728 pp** | −6.275 | 0.000 pp |
| REALTALK | 0.22553482307028402 | 0.17253405381064957 | **+5.300077 pp** | +5.2241 | 0.076 pp |

Passes. Exact tie expectation, no re-centering (col-mean absmax 7.1e-16 / 4.4e-16).

## The three independent measurements

**(a) Pooling — RISES.** 0.234 / 0.260 / 0.260 / 0.285 / 0.294 / **0.345** at N = 493 / 986 / 1971 /
4928 / 9856 / 24640, all 470 LME queries at every rung. Coordinator's six numbers reproduce (mean
abs diff 0.030; only their N≈1978 value 0.217 vs my 0.260 differs, consistent with a different pool
draw at n=120).

**(b) Subsampling within one real archive — FALLS above the peak.** LME 0.285 / 0.353 / **0.355** /
0.328 / 0.273 / **0.245** at N = 10 / 25 / 50 / 100 / 200 / 400. Same non-monotone shape in LoCoMo
and REALTALK independently. **(b) disagrees with (a) and agrees in direction with the relayed
claim.**

**(c) Natural N spread, real archives only.** r(tie, N) = +0.080 (LME, 470 arch, N 396–616),
+0.301 (PerLTQA, 30 arch, 293–546), +0.048 (LoCoMo, 10, 369–689), +0.417 (REALTALK, 10, 410–1548).
All positive but all underpowered — no family spans more than 3.8× and only LME has n>30.

## The mechanism

The K-th order statistic's **leftward drift rate** decides the sign:

| growth mode | d₍₃₎ drift | mean bc | tie rate |
|---|---|---|---|
| within-archive | **−2.869 bits/doubling** | 1.79 → 1.52 | falls |
| pooling | **−0.244 bits/doubling** | 1.53 → 1.95 | rises |

**11.8× difference.** Related rows land near the query and march d₍₃₎ into the sparse tail (fewer
collisions). Unrelated rows add only far mass (mean distance 47.88→47.97, d_min 22.08→21.59), pinning
d₍₃₎ and piling extra rows onto the same integer (more collisions).

## Where the relayed 54%→26% lives (task item 4)

48 definitions tested on two ladders (`evidence/variants.txt`, `evidence/EG.log`, `evidence/mech.txt`).

- **All 15 tie-flavour variants RISE on the pooled ladder. Zero fall.**
- Each listed candidate is dead: `gap==0` ≡ `bc>slots` (852,336 checks, **0 disagreements**);
  float arm tie rate **0.0000 at every N**; shortlist NT=20 and two-stage M=50 are **bit-identical**
  to the frozen statistic; per-archive vs per-query differs in the 4th decimal; K=1/2/5/10/20/50/100
  all rise.
- **FALLING**: `P(d₍₃₎ ≥ 30)` pooled = **0.440 / 0.440 / 0.423 / 0.379 / 0.330 / 0.204** (best L1 fit
  to 0.54→0.26, err 0.155); `P(d₍₃₎ ≥ 40)` within-archive = 0.990 → 0.000; `bc/N` = 0.056 → 0.003.

The relayed mechanism sentence — *"the 3rd-nearest moves from the concentrated mass into the sparse
tail"* — is a **correct description of d₍₃₎'s position** and a **false description of the tie rate**.

## SIGN-minus-float delta vs N (task item 5)

Paired, all 470 LME queries, nested pools: **+10.05 → +8.98 → +8.02 → +5.72 → +4.43 → +2.67 pp**;
paired t = +7.05 at the far rung (SE 1.05 pp). Sign arm falls 0.5421→0.4588; float arm nearly flat.

**Honest power statement:** the coordinator was right that n=120 *unpaired* deltas (SE≈3.3 pp) permit
no claim — their 10.0/7.0/14.3/2.6/7.6/3.6 spread is consistent with a constant delta. Pairing on
identical queries cuts SE to 0.32–1.05 pp and **does** license the claim — **but only for the pooled
construction**, which the mechanism section shows is a wrong model of archive growth. For **real**
archives no claim is licensed at all: LME r(delta, N) = −0.012 over 470 archives.

## The fact that reframes everything

**No real archive in these caches exceeds N=1548** (LME 396–616, PerLTQA 293–546, LoCoMo 369–689,
REALTALK 410–1548). Every number either side quotes for N≥2000 describes a *synthesised* archive,
and the synthesis method determines the sign of the effect. The programme has **zero** first-hand
evidence at its 100K–1M target scale. Correct scope statement: **the N-dependence of the frozen
result is UNMEASURED and cannot be measured with the archives the programme owns.**

## Adversarial self-check

Most damaging assumption: *"the only real family with a wide natural N span agrees with pooling."*
Tested on REALTALK (10 real archives, N 410→1548, no pooling, no subsampling): r = +0.417, p≈0.23,
one high-leverage point at N=1162. **Neither confirms nor refutes** — reported as such, not
rescued. Also verified: float32 matmul Hamming ≡ popcount Hamming exactly; tie statistics never read
gold so gold-forcing cannot bias any tie ladder.

## Prediction accuracy

PREDICTION.md was written after the control and before step 2, unedited. **I was wrong on my two
central predictions**: P2 ("pooling is not an artifact; (b) will agree with (a)") — (b) falls where
(a) rises, and my stated reason was exactly the false assumption; and P4 ("sample sizes permit no
delta claim") — I under-estimated pairing. Correct on P0, P3.4, P3.5, and on P1 for pooling only.
Full table in VERDICT.md § Prediction post-mortem.

## Files produced

| file | content |
|---|---|
| `PREDICTION.md` | written before step 2, unedited |
| `SCALE_FACTS.md` | 12 fact blocks, all VERIFIED with locators |
| `VERDICT.md` | ruling, definition sweep result, scope statement, post-mortem, limitations |
| `REPORT.md` | this file |
| `scale.py` | sections A/B/C/D — pooling, subsampling, natural spread, synthetic |
| `control.py`, `analyze.py`, `sweep.py`, `pin.py`, `final.py`, `variants.py`, `mech.py`, `merge_results.py` | control, aggregation, definition sweep, self-checks, mechanism |
| `evidence/results.json` | consolidated (156 KB) |
| `evidence/*.json`, `evidence/*.txt`, `evidence/*.log` | raw per-section receipts |

## What I could NOT do

1. No real archive above N=1548 exists — nothing here speaks to 100K–1M.
2. Could not reproduce 0.54→0.26 exactly (best L1 err 0.155); the relayed session's code was
   unavailable and I did not tune toward the target.
3. The coordinator's N≈1978 rung (0.217) did not reproduce (I get 0.260); the other five do.
4. Subsampling is not a perfect model of a real *small* archive either (a real short conversation is
   coherent, not a random row sample) — the residual untestable assumption.
5. `evidence/B_subsample_rows.json` (137 MB raw per-row dump) was deleted after aggregation to keep
   the output dir reasonable; its aggregates live in `results.json` and it is regenerable with
   `scale.py B`.
