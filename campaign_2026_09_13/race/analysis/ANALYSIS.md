# RACE — official analysis (post-RACE-V)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[LOCAL] [NOT PUSHED]. Runs on the official-run outputs; frozen literals from
`rb1/frozen_literals.json`; rules from RB1 d2 notebook §3–§4. Script: `analysis.py`
(this folder). B=5000, seeds 94301 (LME) / 94302 (LoCoMo); fixed-argmax secondary +10;
LoCoMo conversation-cluster CI additionally (descriptive).

## Primary contrast: SIGN12B − max(sealed competitor set)

| | LME (K=40) | LoCoMo (K=41) |
|---|---|---|
| SIGN96 | 0.5419751773049645 | 0.23654714666441054 |
| Best competitor | SPREAD80 = 0.525258865248227 | BOT80 = 0.23546142203796927 |
| **Observed gap** | **+1.6716pp** | **+0.1086pp** |
| Zone (kill −6.4 / −3.7; promote +2.0) | **MID** | **MID** |
| Bootstrap 95% CI (argmax re-selected) | [−0.596, +2.122] | [−0.911, +1.019] |
| Fixed-argmax 95% CI (secondary) | [−0.257, +3.603] | [−0.890, +1.090] |
| Cluster CI (LoCoMo, descriptive) | — | [−1.173, +1.149] |
| Argmax wins / 5000 resamples | SPREAD80 1011, RAND80_s2 932, RAND80_s8 866, … | BOT80 4518, SPREAD80 163, RAND80_s3 159, … |

## 16-cell disposition

(LME zone, LoCoMo zone) = (MID, MID) → **HOLD-parity**.
Action: **retain SIGN12B — no kill, no promote.** All CIs include 0; the result is a
statistical parity with a positive point estimate (+1.67pp LME “moderate”, +0.11pp LoCoMo).

## Reading (frozen-frame numbers)

Under the pre-seal no-edge null (K=40/41 looks), the expected contrast is −3.14pp (LME) /
−1.82pp (LoCoMo); its 97.5th percentile sits at ≈−0.07 / −0.03. The observed +1.67 / +0.11
therefore exceeds the null's 97.5th on both benchmarks — i.e. **parity is itself a
97.5th-percentile event**, and LME lands in the descriptive “moderate” band; but the frozen
promote line (+2.0pp, set above the null edge with >2pp daylight) is NOT cleared by the
point estimate, and no CI condition for promote would pass anyway (CIs include 0).
A true premium of ≈+3.1pp (LME) / ≈+1.8pp (LoCoMo) would be needed for the expected gap to
reach the null's upper edge (≈+4.4 / +2.6pp for 80% power). Not achieved this race.

## Dominance check (descriptive)

No arm dominates SIGN recall-vs-bytes across rungs: SIGN at 12B (96b) has the highest
aggregate on both benchmarks; the best ≤10B arms sit below it (SPREAD80 −1.67pp LME;
BOT80 −0.11pp LoCoMo), and all third-party codecs at ≤12B are far below (PQ −11.1/−8.3pp;
RaBitQ32 −23…26/−14…16pp). Nothing to kill on dominance grounds.

## Not-checkable / caveats (carried)

- Per-archive code bytes vs runner runs: only aggregate `codes_sha256` persisted (covered
  functionally: bit-identical retrains + exact FRs, RACE-V §3b).
- Bootstrap phase is local/exploratory; interval construction as frozen, no external seal.
- R@3 (fractional) is the measured quantity; end-to-end answer quality is out of scope.
- Two benchmarks, one representation family; A5 wrapper single-draw excluded from K per
  sealed rules (C10 cap).
