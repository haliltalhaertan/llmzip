# Project Status — 2026-08-27

## Current branch of research

The active question is no longer merely whether an external-memory router can be compressed. V52 Task 4C1 showed that the frozen same-family ITQ frontier degrades sharply below 96 bits on LongMemEval, while a simple centered sign/Hamming representation unexpectedly outperformed both ITQ96 and the original continuous FLOAT96 reference.

Task 4C2 was designed to falsify the leading confound: that SIGN96 only looked better because SIGN96/ITQ96 used archive-mean centering while FLOAT96 did not.

### Frozen Task 4C2 compute result

| Method | ANY R@3 | ALL R@3 | Fractional R@3 |
|---|---:|---:|---:|
| FLOAT96_UNCENTERED | 61.063830% | 28.936170% | 44.010638% |
| FLOAT96_CENTERED | 61.276596% | 28.723404% | 44.159574% |
| SIGN96_CENTERED | 71.308511% | 38.457447% | 54.197518% |
| ITQ96_CENTERED | 54.276596% | 22.672340% | 37.614113% |

Paired fixed-benchmark gaps:

- Centering effect `Fc - F0`: +0.148936 pp.
- SIGN residual `S - Fc`: +10.037943 pp.
- ITQ vs centered float `I - Fc`: -6.545461 pp.
- SIGN vs ITQ `S - I`: +16.583404 pp.

Frozen Task 4C2 decision: `[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`.

Same-input proof passed with maximum absolute difference `0.000e+00` between the centered 96D inputs used by centered FLOAT, SIGN and pre-rotation ITQ.

## Diagnostic observations

SIGN96 produced substantially fewer duplicate document codes and fewer top-3 boundary ties than ITQ96. SIGN-vs-ITQ Hamming neighborhood rank correlations were low (~0.17), showing that ITQ rotation substantially reorders neighborhoods. These are descriptive diagnostics, not yet causal explanations.

## Literature guard

The broad mechanism class is not novel. Prior work already covers sign/binary embedding retrieval, ITQ, random/orthogonal rotation, binary passage retrieval, two-stage hashing, binary agent memory, and the fact that rotation may help or hurt depending on representation geometry. The current possible contribution is therefore narrow: a preregistered evidence-level bit/quality/cost and geometry comparison in conversational long-term-memory retrieval with archive-local, no-QA/gold fitting and identical frozen evaluation rules.

## Next gate

Task 4C2 must receive independent adversarial audit before it is frozen as a checkpoint. No LoCoMo cross-benchmark extension or 4C3 mechanism experiment should be interpreted as load-bearing before that audit.
