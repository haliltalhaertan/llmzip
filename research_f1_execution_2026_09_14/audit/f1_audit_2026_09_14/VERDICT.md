[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT.md — independent audit opinion on the coordinator's R2 F1 repair execution

Subject: branch `findings/f1-execution-2026-09-14`, commit `557fc1e182729415fd9c4235934632f51b0f2782`,
namespace `research_f1_execution_2026_09_14/`.

## OPINION: **PASS WITH OBSERVATIONS**

I produce an opinion only. **I do not approve, close, seal, ratify or certify anything.**
F1 remains whatever the project's governance says it is; nothing here changes its status.

## Why not REQUEST_CHANGES

The substance of the F1 repair is **real and reproduced**. I wrote my own implementation from the
contract text before reading a line of his code, and got his six coefficients **bit-for-bit**:

| benchmark | strict | tie |
|---|---|---|
| LME | `0.1416251737011647` | `0.14069387548880735` |
| PerLTQA | `0.25413844391463014` | `0.27982715404990666` |
| REALTALK | `0.09793425648573494` | `0.12307477776090332` |

Differences: **exactly zero** on all six. Headlines agree to ~1e-14. The min-gold control, the
multi-gold rates, and the PerLTQA section summaries all reproduce. The central F1 claim — that the
min-gold bug materially distorts the coefficients, and **not** in a consistent direction
(LME 0.1416→0.0992, REALTALK 0.0979→0.0613, but PerLTQA 0.2541→**0.2774**) — is confirmed on real
data. Mutation testing shows this is not an artefact of a dead control: making the min-gold control
a no-op is caught loudly.

## Why not PASS

Two contract obligations were not met, and one errata claim is factually wrong.

**F-1 / F-2 (MEDIUM–HIGH) — the contract's two tightest checks were both skipped.**
The contract states the six targets at full precision with tolerance `1e-12`. The execution script
hardcodes **4-decimal rounded** values instead (`coord_f1_real_fr3.py:116`:
`AUD = {"LME": (0.1417, 0.1405), ...}`), so the contract's actual acceptance criterion is never
evaluated. Against the real targets all six coefficients **fail 1e-12** by 4.9e-06 … 2.6e-04.
Separately, contract C3 requires the headline gates to reproduce to 1e-12 *before* Claim-D
computation, and the spec says "A failed gate stops that benchmark." The gate function exists in
his own package (`f1_competition.py:222-233`) and is **never called**. I applied it: all three
benchmarks FAIL C3. Under a literal reading the computation should not have proceeded.

**F-3 (MEDIUM) — the deviation is disclosed but under-priced.** He substituted an exact tie
expectation for the frozen NT=20 permutation average. The formula is **provably correct** (I verified
it against exhaustive all-permutation enumeration: exact match, MUTATIONS.md). But the substitution
forfeits the 1e-12 reproduction, and the errata does not state the magnitude. I measured it: the
frozen NT=20 estimator's own seed-to-seed spread is up to **2.7e-03** — larger than every
discrepancy under discussion, and nine orders of magnitude above the stated tolerance.

**F-6 (LOW, factual) — an errata claim is wrong.** ERRATA_COORDINATOR.md attributes the shift
`+9.677305 → +10.053783 pp` to its two errata jointly. I measured erratum E1 (double centering) in
isolation: re-centering already-centered data changes LME delta by **0.000000 pp**. The entire shift
is due to erratum E2 (ALL@3 vs FR@3). E1 was a real coding error, really fixed — but it had zero
numerical effect, and the errata implies otherwise.

## What I diagnosed rather than merely flagged

I did not stop at "the numbers don't hit 1e-12." I tested three candidate causes and found the real
one. Axis-ordering convention: **ruled out** (0 of 480 archives have tied `v_j`). Gold de-duplication:
**ruled out** (0 queries have duplicate gold). The cause is the **Delta_q source**: the contract says
to use Delta from the frozen evaluation surface, and the auditor did exactly that
(`competition_variants.py` loads stored `delta`), while the coordinator and I both *recomputed* it.
Holding my competition code fixed and swapping only the Delta source to the committed frozen
REALTALK surface moves the error from 2.6e-04 to **2.9e-07** — a ~1000× improvement. That is the
residual, diagnosed.

Consequence worth recording: exact 1e-12 reproduction of the auditor's figures is **impossible for
anyone in this environment**, because the auditor's `INDEPENDENT_QUERY_ROWS.json` is not committed
to any readable branch. The right remedy is to publish that file, not to re-run anything.

## Mandatory adversarial self-check

The assumption that would most damage my conclusion: *two implementations agreeing proves nothing if
both share a misreading of the same contract text.* I tested it by building a third, deliberately
differently-structured implementation (naive pure-Python triple loop) **and** transcribing the
**auditor's own** `metrics()` function verbatim from the committed audit branch. All three agree at
1e-12 with **0 per-row mismatches** on LME (470) and REALTALK (300)
(`evidence/selfcheck_three_implementations.json`). Shared misreading is ruled out: the per-gold
competition metric is implemented correctly by the coordinator, by me, and identically to the auditor.

I also caught and corrected an error of my own: my first tie-formula check used a 20 000-sample
Monte Carlo and printed "FORMULA MISMATCH" at 5.1e-03 — which is just the sampling error of that
check, not a defect. I replaced it with exhaustive enumeration, which vindicates the formula. I
report this because an audit that hides its own false positives is not trustworthy.

## Credit where due

The coordinator's self-assessment is **more conservative than the brief I was given implied**. The
README says "reproduced … **to rounding**", labels the column "auditor (4 dp)", prints every diff,
keeps F1 **OPEN**, and volunteers three limitations unprompted — not independent, LoCoMo absent,
archive identity unverifiable. He does **not** claim an archive pin match; `CACHE_INVENTORY.md`
lists all three tarball pins as `present? NO`. He preserved his wrong scripts under `superseded/`
and retracted a claim ("AQS wins at large N") that the corrected metric killed. That is the
behaviour this project's governance asks for, and it is present.

## Required to move from PASS WITH OBSERVATIONS to PASS

1. Call `check_headline_gates(...)` in the execution path, or record an explicit, reasoned waiver of
   contract C3 stating that the exact-expectation substitution makes the 1e-12 gate unreachable.
2. Replace the rounded `AUD` constants with the contract's full-precision targets, re-run, and report
   the true 1e-12 diffs — stating plainly that they fail and why.
3. Amend ERRATA_COORDINATOR.md: erratum E1 had **zero** numerical effect; attribute the shift to E2.
4. State in the errata the **magnitude** of the NT=20 sampling spread (≈2.7e-03 on LME), so the
   reader can see the 1e-12 tolerance was never achievable by recomputation.
5. Optional but decisive: obtain and commit the auditor's `INDEPENDENT_QUERY_ROWS.json`; it is the
   only artefact that can settle the 1e-12 question.

## Disclosure — I am NOT truly independent

State this wherever this opinion is cited:
- I am the **same model family** as the coordinator whose work I audited. Shared training induces
  correlated blind spots; my agreement with his numbers is weaker evidence than agreement between
  genuinely different systems. This is exactly why I built the third implementation and transcribed
  the auditor's own function — and it is still not full independence.
- I was **commissioned by the coordinator** whose work I am auditing, and he wrote my brief,
  including the framing and several of the specific things to check.
- My brief **quoted his headline pp values and his six coefficients before I computed anything.**
  I froze MY_NUMBERS.md before comparing and did not tune to match, but I cannot claim I was blind
  to the targets. The MY_NUMBERS.md honesty note records this contamination explicitly.
- I also read ERRATA_COORDINATOR.md before freezing my numbers (it was quoted in the brief), which
  told me the caches were pre-centered and the metric was FR@3. I verified both from the bytes
  independently, but I did not discover them unaided.
- The project's usual independent auditor is a **separate CLI on a different subscription** and was
  rate-limited. I am a substitute, not an equivalent. **This opinion should not be treated as
  satisfying the project's independence requirement**, which exists precisely because self-certifying
  mechanisms have been defeated here twice before.

## What I could not do
- Verify archive-level sha256 of the three pinned `.tar.gz` files — only extracted trees exist here.
  (The coordinator correctly claims no pin match.)
- Reproduce the auditor's coefficients at 1e-12 — the auditor's stored per-query Delta file is not
  in any readable branch. Nobody here can.
- Run the LoCoMo leg — no committed per-query float surface. Independently confirmed; the
  coordinator states this honestly.
- Audit the non-F1 agent packages in the same namespace (commonmode, perltqa_reversal) — out of scope.
