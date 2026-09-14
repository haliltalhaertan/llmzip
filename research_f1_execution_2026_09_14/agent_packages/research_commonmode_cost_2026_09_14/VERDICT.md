[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT — does the storage objection survive, shrink, or collapse?

PREPARED, NOT ACCEPTED.

## One-paragraph verdict

The storage objection SPLITS. As a **head-to-head claim** ("at programme
scale SIGN96+projector stores ~234× MORE than raw float32") it COLLAPSES:
the ~44 MB projector is 100% common-mode — the float96 baseline requires the
identical fitted pipeline (same Y, same mu, same five artifact classes;
T4C2 aborts unless the constructions agree to 1e-12), so the 44 MB cancels
exactly and SIGN96 is the cheapest arm at every archive size under every
valid accounting. As an **absolute-footprint claim** ("the deployed system
stores ~89 kB/vector, so '12 bytes' misleads a deployment reader") it
SURVIVES intact: common-mode status does not shrink anyone's footprint, and
the codes remain ~0.013% of persisted bytes. The damaging assumption the
adversarial session named — "what if the 88 kB is common-mode?" — tested
TRUE, and it inverts the comparison while leaving the deployment warning
untouched.

## The practical question: honest total footprint for a retrieving agent

An agent that must RETRIEVE from a stored archive needs, per archive: the
per-vector payload PLUS the fitted pipeline resident at query time (queries
must pass `wv → cv → sv → s96 → −mu`; precomputed archive vectors do not
remove this requirement). Honest totals at realistic N (P = 44,220,235 B):

- SIGN96: 12·N + P + 33. @N=500: 44,226,268 B total ≈ 88,453 B/vector.
- FLOAT96: 384·N + P. @N=500: 44,412,235 B total ≈ 88,824 B/vector.
- PQ96: 12·N + P + 98,390. @N=500: ≈ 88,649 B/vector.
- OPQ_PQ96: 12·N + P + 135,325. @N=500: ≈ 88,723 B/vector.

At what archive size does SIGN96 become a real saving? Against the
programme's float baseline: **at every N ≥ 1** (saves 372 − 33/N B/vector —
0.4% of footprint at N=500, asymptoting to the full 32× payload ratio).
Against PQ/OPQ: at every N ≥ 1, by the codebook delta (~197/271 B at N=500).
A saving that is LARGE in relative terms (≥2× vs float-full) needs
P/N ≲ 372, i.e. **N ≳ 118,872 vectors per archive** — ~190× the largest
frozen archive (616). That number is real; only its old meaning was wrong.

## Per-archive (as measured) vs shared (currently forbidden)

- Per-archive fit (prereg rule): effective ≈ 88.9 kB/vector (f32) at N≈500.
  VERIFIED against committed bytes (B1–B3).
- Shared-across-archives (ONE median-size projector serving all 231,606
  frozen vectors): effective lower bound = 12 + P/231606 ≈ **202.93 B/vector**
  (VERIFIED; independently reproduces Attack 4's 202.93 exactly — two routes
  agree). Still 17× the cap, still below float-full (586.9). This bound is
  OPTIMISTIC for sharing (a true global vocab exceeds P_med), so reality is
  worse, not better.
- The prohibition: L-088 (`docs/CONTINUITY_LEDGER.md:1881`) — "it tests
  ARCHIVE-LOCAL FITTING... a cross-archive or globally shared codebook is a
  different deployment configuration whose properties may not be presented as
  a result of this experiment"; prereg draft `:79-81` — "No reuse across
  archives... Never amortize state over all benchmark questions." Forbidding
  sharing is a CHOICE with a price tag: it locks the footprint at ~89 kB
  instead of ~0.2–0.6 kB per vector. The choice is defensible (leakage
  barrier, per-archive experimental control); its cost must be printed next
  to it, which this verdict does.

## Exact ruling the Head Researcher must make

Whether the quotable "12-byte" sentence — and the SIGN-vs-float storage
comparison — refers to (i) marginal code bytes, (ii) index-only effective
bytes/vector, or (iii) full-pipeline effective bytes/vector (per-archive
denominator). The numbers that follow from each option, at N=500:

| Option | SIGN96 | FLOAT96 | Verdict on "SIGN saves" |
|--------|-------:|--------:|-------------------------|
| (i) marginal | 12 | 384 | saves 32× at all N |
| (ii) index-only eff. | 12.07 | 384 | saves ~31.8× at all N |
| (iii) full-pipeline eff. | 88,453 | 88,824 | saves 372 B/vec (0.4%) at all N |

Under NO option does SIGN cost more than float. The "234× worse" sentence is
false under all three. The "12 bytes total" sentence is false under (iii).
Rule (i)+(iii)-mandatory-reporting (the current L-088 posture) and both
truths coexist; rule only-(i)-quotable and the deployment reader is misled.

## Skeptic's corner (assumption that would most damage this verdict)

That the float baseline could be obtained WITHOUT the pipeline — e.g. raw
encoder embeddings stored directly. I tested this against the bytes: no such
arm exists in the programme (every 96-D vector in T4C2/T4D/E1 is
pipeline-produced; the prereg's FLOAT96 row is "384 float32 payload B" OF
that same C). If a future design introduces a genuinely pipeline-free float
arm, this verdict's head-to-head section must be redone for that arm — the
absolute-footprint section would still stand.
