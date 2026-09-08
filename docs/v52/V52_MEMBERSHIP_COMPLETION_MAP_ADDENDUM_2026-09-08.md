# Completion map — addendum, 2026-09-08

**Additive.** `V52_MEMBERSHIP_COMPLETION_MAP_2026-09-08.md`
(sha256 `2b0ed8f6d5381314c89844ef9a673efbf357df32042bd9fd1224d1aa549a5666`, `main` @ `21f5710d`) is
**not edited**, so its hash keeps resolving. This addendum tightens two of its lines and records one
decision about sequencing. It is **documentation only** and authorizes nothing.

---

## 1. G-9 — what "rerun" means, and when it happens

The map's G-9 read "a rerun of every suite under the accepted lock at seal time", which was loose in
two ways. Corrected:

**What it is.** Running the **relevant existing test suites** — the core regression suite, the runner
suite, the ingestion synthetic suite, and whatever suites the not-yet-authorized M-1/M-2/M-3 bring
with them — in the accepted environment.

**What it is NOT.** It is **not** re-executing any past experiment. No completed stage is re-run, no
prior result is recomputed, and no outcome from an earlier task is touched or reproduced. Task 4C2,
Task 4D, the LoCoMo reproduction and every other closed stage stay closed and untouched.

**When.** These checks must be **complete BEFORE the seal (G-7) and before any real run (G-8)** —
not after, and not concurrently with either. A seal that binds code whose tests were run afterwards
binds something that was not yet checked.

So the ordering inside the gate list is: the synthetic and regression checks finish in the accepted
environment → **then** the seal is made → **then**, separately authorized, the run.

## 2. G-6 — the pilot is neither planned nor authorized

The map listed G-6 as "a pilot decision, if one is wanted", which reads as though a pilot were an
expected step. It is not.

**No pilot is planned and none is authorized.** The gate exists only to mark that a pilot, if it were
ever proposed, would need its own decision.

**And it would not be an ordinary implementation decision.** A pilot that produces **real retrieval
results** is assessed as **outcome access**, under the same boundary that governs the experiment
itself — not as a testing convenience, and not as something the implementation stage may reach for
because it would be useful for debugging. Anything that yields real top-k identities, real distances or
real retrieval-quality numbers falls under that assessment regardless of what it is called or how small
it is.

## 3. The distinction the map draws, restated because it is easy to erode

Reuse of the frozen code is a reuse of **computation**, and nothing else:

| may be reused | must NOT be carried over |
|---|---|
| `fit_archive_representation`, `build_representation` — the TF-IDF, LSA and SVD computation | the **arm definitions** `FULLHAAR/BLOCK32`; this experiment's arms are `NATIVE, SCALED_NATIVE, B32_FRESH, SCALED_B32, RANDOM32_FRESH, SCALED_RANDOM32` |
| `topks_by_hamming` with its tie and priority handling, `fractional`, `stable_archive_seed` | the **rotation seeds** `59001…59010`; this experiment's panel is `60001…60010` paired with partition seeds `70001…70010` |
| the constants `SVD_SEED = 5204`, `SOURCE_LATENT_DIM = 32`, `N_NUISANCE = 20`, `TOPK = 3` | the **cohort selection** rebuilt from `audit/errors_conv_*.json`; the cohort here is **bound** and resolved id by id, never derived |
| the shape of a six-arm, ten-seed driver, as structure | the **corpus download and acquisition** path; sources here are already present and verified by hash before any parse |

Carrying any item from the right-hand column would not be reuse. It would be a design error wearing
reuse as a disguise, and it would be caught late — after results exist — if it were caught at all.

## 4. Sequencing recorded, not authorized

The Head Researcher has indicated that **after** the runner and ingestion review returns, and **if it
raises no blocker**, treating **M-1, M-2 and M-3 as a single bounded implementation package** will be
considered.

That is a statement about what may be considered, not a grant. **G-3 remains not granted.** No design
work, no code and no scaffolding for M-1, M-2 or M-3 may begin before an explicit authorization, and
the review currently in progress must return first.

---

Everything else in the completion map stands unchanged. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
