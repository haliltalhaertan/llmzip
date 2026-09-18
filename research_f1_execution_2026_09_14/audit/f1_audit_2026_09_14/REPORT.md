[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — cold-start independent audit of the R2 F1 repair execution

Subject: `findings/f1-execution-2026-09-14` @ `557fc1e182729415fd9c4235934632f51b0f2782`,
namespace `research_f1_execution_2026_09_14/`.
Auditor: subagent, ~55 min budget. Output dir: `C:/Users/MDP/dev/llmzip-work/agent_out/f1-audit/`.

## VERDICT: PASS WITH OBSERVATIONS

Opinion only. I did not approve, close, seal, ratify or certify anything.

## Deliverables

| file | contents |
|---|---|
| `MY_NUMBERS.md` | my six coefficients, **frozen at step 1** before reading his code or values |
| `COMPARISON.md` | three-way comparison at full precision + diagnosis of the residual |
| `my_f1.py` | my independent implementation, written from contract/spec text only |
| `evidence/results.json` | my full machine-readable output (all three benchmarks) |
| `CODE_REVIEW.md` | adversarial review, 8 checklist items + 6 findings + 5 observations |
| `MUTATIONS.md` | 10 mutations of his own code, run end-to-end on real caches |
| `VERDICT.md` | the opinion, with remedies and the non-independence disclosure |
| `evidence/*.json`, `evidence/*.log` | receipts for every number quoted |

## What I did, in the required order

1. **Cold start.** Read the contract, the E1 spec and the frozen scorer `step2_eval.py` from git
   blobs. Wrote `my_f1.py` from that text alone. Ran it on the real caches (470 LME + 8265 PerLTQA
   + 705 REALTALK). Froze `MY_NUMBERS.md`. **I did not open any coordinator script before this point.**
2. **Compared three ways** at full precision.
3. **Then** read his scripts and attacked them against the eight specified checks.
4. **Mutation-tested** his code with 10 deliberate defects.
5. Delivered the opinion.

## Headline result: bit-for-bit agreement on all six

| benchmark | arm | mine | coordinator | diff |
|---|---|---|---|---|
| LME | strict / tie | `0.1416251737011647` / `0.14069387548880735` | identical | **0** |
| PerLTQA | strict / tie | `0.25413844391463014` / `0.27982715404990666` | identical | **0** |
| REALTALK | strict / tie | `0.09793425648573494` / `0.12307477776090332` | identical | **0** |

Headlines agree to ~1e-14: LME `+10.053782505910167` pp, PerLTQA `-6.274727836521104` pp,
REALTALK `+5.300076925963451` pp. Multi-gold rates, min-gold control and PerLTQA sections all match.
**The F1 repair's substance is reproduced.** The bug's real-data effect is confirmed, including that
its direction is *not* consistent (PerLTQA moves the other way: 0.2541 → 0.2774).

## Findings

| id | sev | finding |
|---|---|---|
| **F-1** | MED | The contract's 1e-12 acceptance test was never executed. `coord_f1_real_fr3.py:116` hardcodes **4-dp rounded** auditor values (`0.1417`, `0.1405`, …) instead of the contract's full-precision targets. Against the real targets **all six fail 1e-12** by 4.9e-06 … 2.6e-04. Mitigated: the README says "to rounding", labels the column "(4 dp)", prints every diff and keeps F1 OPEN — an incomplete test, not a misrepresentation. |
| **F-2** | MED–HIGH | Contract gate C3 (headline gates to 1e-12 *before* Claim-D; spec: "A failed gate stops that benchmark") was **never applied**. `check_headline_gates()` exists at `f1_competition.py:222-233` and is never called. I applied it: **all three benchmarks FAIL**. |
| **F-3** | MED | The exact-expectation-for-NT=20 substitution is disclosed but **under-priced**. The formula is provably correct (verified by exhaustive permutation enumeration), but the frozen estimator's own seed-to-seed spread is up to **2.7e-03** — larger than every discrepancy discussed, nine orders above the stated tolerance. The errata never states this magnitude. |
| **F-4** | LOW | Delta_q was **recomputed** where the contract says to reuse the frozen evaluation surface. Swapping only the Delta source to the frozen REALTALK surface improves the error ~1000× (2.6e-04 → **2.9e-07**). I did the same thing, so I am not privileged here. |
| **F-5** | LOW | Input inventory omits `drive/audit_layer/conv_*.json` and `regen/locomo/*.pkl` (0 grep hits in `INPUT_CACHES.sha256`) with no explicit "present, not used" line. |
| **F-6** | LOW | **An errata claim is factually wrong.** ERRATA_COORDINATOR.md attributes the `+9.677305 → +10.053783 pp` shift to its two errata jointly. I measured E1 (double centering) in isolation: **0.000000 pp change**. The entire shift is E2 (ALL@3 vs FR@3). |

**Clean on all eight checklist items:** no re-centering; tie formula correct; TOP/BOT ordering right;
average-rank Spearman correct; bootstrap resamples the right cluster level and handles a missing
cluster id sanely; **no float tolerance in any exactness-critical path** (distances are Python ints,
so a tolerance *cannot* corrupt them); the min-gold control genuinely implements the bug; manifest
and inventory are honest — he explicitly states the archive pins are **unverifiable** and that LoCoMo
was not run, rather than claiming a match.

## Mutation testing: 7/10 caught, 3 proved equivalent mutants

Caught: swap TOP/BOT; ascending axis order; gap sign flip; average-rank → ordinal ranks; min-gold →
first-gold; min-gold control aliased to primary (true no-op); bootstrap forced to query level.

Not caught — all three investigated and shown to be **equivalent mutants, not defects**:
- **M2/M3** (inject float tolerance into `==`/`<`): distances are exact Python `int`s, so the mutants
  are semantically identical. This is the *good* answer to the tolerance question.
- **M8** (re-center inside `col_mean_squares`): data is pre-centered to 1e-16, so `v_j` shifts ~1e-32
  and the axis order is unchanged. I then ran the stronger version — re-centering the **retrieval
  arms**, the actual E1 error — and got **0.000000 pp change**, which is finding F-6.

## Diagnosis of the residual (I did not stop at "doesn't match")

Ruled out by measurement: axis-ordering convention (**0 of 480** archives have tied `v_j`) and gold
de-duplication (**0** queries have duplicate gold). The cause is the **Delta_q source** — the auditor
loaded a stored per-query Delta surface as the contract instructs; the coordinator and I recomputed
it under a different tie estimator. Consequence: **exact 1e-12 reproduction is impossible for anyone
here**, because the auditor's `INDEPENDENT_QUERY_ROWS.json` is not committed to any readable branch.
The remedy is to publish that file, not to re-run anything.

## Mandatory adversarial self-check

Most damaging assumption to my own conclusion: *agreement between two implementations proves nothing
if both share a misreading of the same text.* I tested it — built a third, deliberately different
implementation (naive pure-Python triple loop) and transcribed the **auditor's own** `metrics()`
verbatim from the audit branch. All three agree at 1e-12 with **0 per-row mismatches**. Shared
misreading is ruled out.

I also caught a false positive of my own: my first tie-formula check (20 000-sample Monte Carlo)
printed "FORMULA MISMATCH" at 5.1e-03, which is merely that check's sampling error. I replaced it
with exhaustive enumeration, which vindicates the formula. Reported because an audit that hides its
own false positives is worthless.

## I am NOT truly independent

Same model family as the coordinator (correlated blind spots); **commissioned by him**; he wrote my
brief; **it quoted his six coefficients and headline values before I computed anything**. I froze
`MY_NUMBERS.md` before comparing and never tuned to match, but I was not blind to the targets. The
project's usual auditor is a separate CLI on a different subscription, rate-limited today. **This
opinion should not be treated as satisfying the project's independence requirement.**

## What I could not do
- Verify the three pinned `.tar.gz` sha256s — only extracted trees exist locally (he claims no match).
- Reproduce the auditor's values at 1e-12 — the auditor's stored Delta file is unavailable to anyone here.
- Run the LoCoMo leg — no committed per-query float surface; independently confirmed.
- Audit the sibling agent packages in the namespace — out of scope.

## Prohibitions honored
Read-only outside my output dir; no cache written/moved/renamed/deleted; **no git write of any kind**
(blobs read via `git show` only — no commit, push, checkout, branch or fetch); Task4F1 seal untouched
(no BEAM corpora, no authorization, no run/finalize, no sealed labels); no network; no installs.
