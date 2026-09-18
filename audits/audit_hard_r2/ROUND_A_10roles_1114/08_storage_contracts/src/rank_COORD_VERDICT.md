# Coordinator verdict — certify_v3 candidate vs frozen adversarial bar

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Candidate: `certify_v3.py`, sha256 `b920737c6123622918e3931659131320f4dbe423ade5408bb21d074725dae592`, Muse branch `muse/geometry-cert-repair-v3` local commit `f46a085` on base `75b7e05`. Not pushed.
Bar: `muse/geometry-cert-adversarial` commit `e3f30d2`, frozen before the candidate was run.

## Order of events (this is the part that makes the result meaningful)

The adversarial suite was committed at `e3f30d2` and reviewed by me BEFORE `certify_v3.py` existed in runnable form. I confirmed with `git diff e3f30d2 HEAD -- .../adversarial` that the bar is EMPTY-diff after the candidate run: **no case, no expectation, and no validator line was touched to accommodate the candidate.** The two Muse sessions never read each other's worktree.

## Result on the frozen bar (coordinator-run, not worker-reported)

| Target | safety_fail | completeness_fail | exit |
|---|---:|---:|---:|
| archived `certify_v2.py` (control, same run) | **5** | 3 | 1 |
| candidate `certify_v3.py` | **0** | **0** | 0 |

The control re-run in the same command proves the suite was still capable of failing something at that moment.

## Independent coordinator check (does not import any worker module)

`coord_check_v3.py` → `COORDINATOR_V3_INDEPENDENT.json`. My own oracle: exact critical-point partition, real-root count from the exact integer discriminant of the degree-≤3 cross polynomial, roots confirmed by exact sign-change brackets. **Cells are declared root-free by exact counting, never by sampling.** Cases whose confirmed root count does not match the discriminant prediction are DISCARDED rather than assumed clean (4 of 688 discarded).

- **684 randomly generated pairs checked, 0 violations.** No stable direction on a truth that carries both signs; no non-resolving status carrying a direction; every claimed exact tie verified to be a genuine tie; every `cross(lo,hi)` bracket verified to sit inside J with an actual endpoint sign change.
- **Scale invariance: 0 violations across k ∈ {10, 10², 10³, 10⁵}** on all 684 cases — the exact defect class that produced BULGU-1 (budget skip changing the verdict under score-preserving scaling).
- **The published blocker at scales far beyond the frozen corpus** (k = 1, 10², 10⁴, 10⁶, 10⁸): `ISOLATED_TIES / VARIES` at every scale. The corpus only went to k = 1000; v3 holds two decades further out.
- Candidate source contains no POC constants except in comments (`70000`, `-200`, `10000` absent from code paths) — the fix is not a hardcoded special case for the witness.

## Structural checks

- `certify_v3.py` imports only `fractions` — it does not call the archived v2 at runtime.
- `cert_validator_v3.py` imports only `fractions` and does not import `certify_v3` — BULGU-5's "validator trusts the generator" hole is closed by construction, and it rejects the literal counterfeit certificate.
- Published package byte-identical: `git diff 75b7e05 f46a085 -- research_representation_geometry_2026_09_13` EMPTY, manifest 73/73 OK. The flawed artifact and its REQUEST_CHANGES audit remain preserved.

## Completeness, stated honestly

Worker fuzz (n=2000, seed 20260914, J=[1/16,16]): the original conservative certifier returned `UNRESOLVED` on 631/1765 effective cases; v3 returns 0. In my independent 684-case run v3 also never returned `UNRESOLVED`. **This is a real usefulness gain, but it is the direction that historically produced the bug — resolving more.** It is acceptable here only because soundness was checked first, by a bar frozen in advance, and by an independent oracle. A zero unresolved rate was never a requirement and must not become one.

## What this does NOT establish

- **No general safety proof.** 684 + 41 + 2000 finite cases, however adversarial, do not certify the algorithm. The proof argument in `FIX_DISPOSITION.md` §3 (numerator-sign constancy between cuts, Sturm-0 root-freedom per cell, neighbour-cell classification of every isolated root, endpoint deflation) is an argument I read and found coherent — I did not formally verify it.
- **Same model family throughout.** Repair session, adversarial session and my own checks are all one family. This is still NOT the different-family independent review, which remains open on your list.
- **Only BULGU-1 and BULGU-5 are addressed.** BULGU-2/3/4/6/7/8 and measurement observations F-01..F-07 remain OPEN and untouched. The two invalid-J robustness faults the adversarial suite found in v2 (`L==R` → `STRICT/0`; `L>R` silently certified) are fixed in v3 and covered.
- v3 is an **additive candidate**. Nothing in the published package was repaired in place, and the `REQUEST_CHANGES` disposition on that package is not retracted by this work.

## Disposition

Candidate **PASSES the frozen bar** and my independent check. Recommended status: **repair candidate accepted for review, blocker demonstrably addressed, package-level `REQUEST_CHANGES` still standing** until a different-family review and the remaining findings are dealt with.
