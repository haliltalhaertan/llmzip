# Rank-certificate repair — blocker BULGU-1 and validator hole BULGU-5

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Additive follow-up to the published package `research_representation_geometry_2026_09_13/`, whose repairs section carries a **REQUEST_CHANGES** audit. That package is **byte-identical** here (manifest 73/73); the flaw and its audit are preserved, not silently fixed.

## Status

| Item | State |
|---|---|
| BULGU-1 (BLOCKING, false single-direction certificate) | Root cause found, repaired in an **additive candidate**; blocker no longer reproduces |
| BULGU-5 (P2, validator accepts counterfeit certificates) | Closed by construction: new validator imports neither the generator nor archived code |
| Invalid-J robustness (`L==R` → `STRICT/0`; `L>R` silently certified) | Found by the adversarial suite, **not in the original audit**; fixed in the candidate |
| BULGU-2/3/4/6/7/8, measurements F-01..F-07 | **OPEN, untouched** |
| Package-level `REQUEST_CHANGES` | **STANDS** — not retracted by this work |
| Different-family independent review | **STILL OPEN** — everything here is one model family |

## What was actually wrong

Two coupled defects in `certify_v2.py::certify_pair`:

1. **Enumeration-budget skip.** At large coordinate scaling the exact rational-root pre-cut exceeds its budget and is silently dropped. The same comparison at small scale keeps the cut and answers correctly — so a *score-preserving* rescaling changed the verdict.
2. **Exact roots never classified.** Bisection exact-hits were logged as ties but never classified crossing-vs-tangent, and the flanking cells were never sampled. With the crossing root invisible, a single midpoint sample certified the whole interval.

Witness: `p=(-100,100,0,10000)`, `q=(-200,200,70000,0)`, `J=[1,4]`. Truth is `{5/4:+1, 3/2:+1, 7/4:0, 5/2:-1, 4:-1}` — the order **changes**. v2 certified `ISOLATED_TIES` direction `-1`. The archived original certifier returned honest `UNRESOLVED`. **The "improvement" had traded soundness for resolution.**

## Method — why the PASS is worth something

The acceptance bar was authored by a **cold-start session that never read the repair worktree**, committed at `e3f30d2`, and reviewed by the coordinator **before** the candidate was runnable. After the candidate run, `git diff e3f30d2 HEAD -- adversarial/` is **empty**: no case, expectation or validator line was adjusted to let the candidate pass.

| Target | safety_fail | completeness_fail | exit |
|---|---:|---:|---:|
| archived `certify_v2.py` (control, same run) | **5** | 3 | 1 |
| candidate `certify_v3.py` | **0** | **0** | 0 |

Coordinator's own oracle (`coordinator/coord_check_v3.py`, imports no worker module; root-freedom established by **exact integer-discriminant root counting**, never by sampling; ambiguous cases discarded rather than assumed clean):

- **684 random pairs, 0 violations** (no stable direction on a both-signs truth; no non-resolving status carrying a direction; every claimed tie genuine; every crossing bracket verified inside J with a real endpoint sign change).
- **Scale invariance: 0 violations** across k ∈ {10, 10², 10³, 10⁵} — the exact defect class behind BULGU-1.
- The blocker witness holds at **k = 10⁸**, two decades beyond the frozen corpus (corpus stops at 10³).
- The candidate contains **no POC constants in code** — not a hardcoded special case.

Coordinator canaries against the bar itself: always-`STRICT` → 32/41 safety FAIL (rejected); always-`UNRESOLVED` → safety clean but 14 completeness FAIL (honest ignorance is sound and explicitly useless); v2 with a renamed status → 15 FAIL (unknown vocabulary is not trusted).

## Completeness, stated against our own interest

The candidate's `UNRESOLVED` rate is **0** where the original conservative certifier was unresolved on 631/1765 fuzz cases. That is a real gain **in exactly the direction that produced the bug**. It is acceptable only because soundness was tested first, by a bar frozen in advance, and by an independent oracle. **A zero unresolved rate was never a requirement and must not become one.**

## Not established

- **No general safety proof.** ~2,700 finite cases across three routes do not certify an algorithm. The proof argument in `candidate/FIX_DISPOSITION.md` §3 was read and found coherent by the coordinator; it was **not formally verified**.
- **Partial independence only.** Repair session, adversarial session and coordinator checks are all the same model family.
- The candidate is **additive and unmerged**. Nothing in the published package was repaired in place.

## Layout

```
candidate/     certify_v3.py, cert_validator_v3.py, tests, fuzz, FIX_DISPOSITION.md   (Muse f46a085)
adversarial/   cases.json (frozen), validate.py, run_suite.py, ADVERSARIAL_SPEC.md    (Muse e3f30d2)
coordinator/   independent checks, canaries, verdicts, session logs, task prompts
MANIFEST.sha256
```

## Reproduce

```bash
cd adversarial
python3 -B run_suite.py --target ../candidate/certify_v3.py --out /tmp/v3.json   # exit 0
python3 -B run_suite.py --target ../../research_representation_geometry_2026_09_13/repairs/rank_cert/certify_v2.py \
        --out /tmp/v2.json                                                       # exit 1, 5 unsound
python3 -B ../coordinator/coord_check_v3.py ../candidate/certify_v3.py           # 0 violations
```

Base commit `75b7e05`; `main` untouched at `5ec3db6`.
