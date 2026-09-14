# EXTERNAL LLM REVIEW BUNDLE — "Axis Attack" Pilot (2026-09-12)

**Purpose:** hand an exploratory research pilot of the llmzip programme to an independent LLM
reviewer with zero prior context, together with everything needed to verify, critique, or extend it.

**EDITION 2 (2026-09-13):** this bundle now also contains the **round-2 attack** on the open
questions (per-question flip analysis, train/test-split learned selection, LoCoMo replication) —
see the new `01b_ROUND2_ADDENDUM.md` and `pilots/axis_attack_2026-09-12/round2/`. Round-2 outputs
went through their own adversarial design review (R2D) and independent recomputation (R2V); both
verdicts are appended in `ROUND2_REPORT.md` §6. All round-1 content is unchanged.

**EDITION 3 (2026-09-13, evening):** adds **round 3** — the roadmap's Design-1 robustness
experiment (the learned-selection premium was **KILLED**: 3/3 pre-declared triggers), the tie-mass
mechanism decomposition, the cross-benchmark utility-transfer matrix, the fresh-Q mixing
confirmation, and the gold-free adaptive-routing probe — each with independent recomputation
(D1V: 24/25 EXACT) and adversarial design review (D5: 3 FAIL + 9 CAVEAT, all dispositioned). See
`01c_ROUND3_ADDENDUM.md` and `pilots/axis_attack_2026-09-12/round3/`.

---

## Context in brief

- **The programme** (`haliltalhaertan/llmzip`) studies compact long-term memory retrieval for
  LLM/agent systems: can a memory system keep a very small active routing representation (e.g. the
  "native" 96-bit = 12-byte SIGN code) while preserving evidence retrieval with an auditable path
  back to the raw archive?
- Previous frozen tasks established a counter-intuitive effect: the native coordinate axes carry
  retrieval-relevant structure that rotations destroy (Task 4C3/4D: Full-Haar96 loses
  −15.9 pp LongMemEval / −9.9 pp LoCoMo vs native SIGN96).
- **This pilot attacked two open questions** on the frozen LongMemEval 470-question benchmark, using
  the frozen Task4C3 evaluation protocol verbatim:
  1. **Budget:** can the 96-bit (12-byte) code be compressed below 12 bytes, and *which bits* should
     be kept?
  2. **Mechanism:** why does axis identity matter — what do mean-distance statistics miss?
- It also ran a **mixing dose-response** experiment (same rotations, different axis pairing) as a
  variance-structure probe.

**Status of the results:** exploratory (see labels), but *independently re-verified*: a second LLM
session recomputed the headline numbers from the raw matrices (bit-exact match) and an adversarial
design review raised 2 defects + 6 caveats, **all resolved** before this bundle was assembled.

---

## Headline results (benchmark-scoped; see 01 for the full table)

| Finding | Numbers |
|---|---|
| Below-12-byte budget with *spread/random* bit selection works surprisingly well | 10 B → 51.5% (native 54.2), 8 B → 48.3, 6 B → 45.0 (−9.2 pp), 4 B → 37.2 |
| **Variance-ordered bit selection is anti-optimal** | top-48-variance 34.9% vs random-48 44.99% (−10 pp); per-question W/T/L vs random = 91/179/200 |
| Spread ≈ random ≈ best (uniform rank-stride/rank-linspace arms) | 48: 0.4503 vs 0.4499; 64: 0.4911 vs 0.4829 |
| **Separation paradox:** mean-distance stats point the wrong way | top-48 wins every mean statistic but loses FR by 10 pp — retrieval is decided by fine tie structure |
| Every axis carries some signal; no single axis is load-bearing | all 96 deltas > 0 (min 0.066); 30/96 drop-loss ≤ 0; max single drop-loss +0.011 FR |
| Mixing damage is monotone in variance disparity | matched −1.6 pp < random −3.8 pp < antimatched −5.4 pp (5 seeds) |

---

## Bundle map

```text
EXTERNAL_LLM_REVIEW_AXIS_PILOT_2026-09-12/
├── 00_READ_ME_FIRST.md              <- this file
├── 01_CANONICAL_STATUS.md           <- full numbers, verification records, limits, open questions
├── 02_INDEPENDENT_REVIEW_PROMPT.md  <- the review assignment (prompt for the reviewer LLM)
├── 03_VERIFY_COMMANDS.md            <- runnable checks (hash + consistency + optional numpy)
├── REPORT.md                        <- the pilot's own full report (read this after 01)
├── verify_pilot.py                  <- stdlib-only consistency checker (run from bundle root)
├── verify_sample_numpy.py           <- optional numpy checker against the 32 shipped matrices
├── pilots/axis_attack_2026-09-12/   <- ALL pilot scripts + result JSONs/CSVs/NPZ + review reports
│   └── HASHES_AXIS_PILOT.txt        <- manifest of the pilot directory (18 entries)
├── protocol_sources/                <- frozen protocol sources needed to recompute:
│   ├── v52_t4c3_coordinate_axis_probe.py   (the byte-frozen producer whose eval block = protocol)
│   ├── longmemeval_v52_adapter.py / _v2.py (frozen adapters; stable_archive_seed lives here)
│   ├── V52_T4C3_question_level.csv         (frozen per-question native FR references)
│   └── qids_500_sorted.json                (lex ordinals for the tie-priority protocol)
├── sample_data/cache_repr/          <- 32 of the 470 regenerated C-matrix pickles (first 32 sorted)
│                                       for spot-recomputation (full cache = 172 MB, NOT shipped)
└── muse_sessions/                   <- raw transcripts of the two independent review sessions
```

---

## Labels (must travel with any use)

- `[LOCAL EXPLORATORY PILOT]` `[NOT PREREGISTERED]` `[NOT FOR CITATION]` `[DISCLOSE-BEFORE-USE]` —
  exploratory outcomes on a frozen benchmark; they may inform a future preregistration **only if
  disclosed with it** (standard exploratory→confirmatory hygiene).
- Task 4F1 boundary untouched; no retrieval metrics outside the frozen benchmark were used; nothing
  from this bundle was pushed anywhere.

---

## What is NOT in this bundle

- The full 470-matrix cache (172 MB, `regen/lme/cache_repr/`) — needed for a complete 470-question
  recomputation; 32 matrices are shipped for spot checks, and the full cache's provenance is the
  `pkl_sha256_manifest` of the companion Task1 bundle (below).
- The 277 MB source dataset (only its sorted qid list is shipped; lex ordinals fully derivable).
- **Companion bundle:** `EXTERNAL_LLM_REVIEW_TASK1_2026-09-12.zip` — the certified regeneration that
  this pilot's matrices come from (gate: all published functionals reproduce at 0.0/≤1e-12; consumed
  sign + ITQ codes bit-identical). These two bundles are designed to be read together.

## How to verify

→ `03_VERIFY_COMMANDS.md`: two hash manifests, a stdlib consistency checker, an optional numpy
spot-recomputation against the 32 shipped matrices, and an explicit list of what cannot be checked
from here. Then the review assignment → `02_INDEPENDENT_REVIEW_PROMPT.md`.