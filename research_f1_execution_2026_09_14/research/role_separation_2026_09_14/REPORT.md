[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — role separation / near-duplicate structure in memory archives

Task: test whether memory archives contain systematic near-duplicate document pairs created by
indexing BOTH speakers, and whether such pairs affect retrieval.

**Answer: adjacency structure is real and strong (AUC 0.909), but it is correlation not
duplication, it is not caused by speaker pairing, and it does not explain the SIGN96 effect —
its cross-benchmark relationship to the effect runs backwards.**

---

## Deliverables (all in `agent_out/role-separation/`)

| file | contents |
|---|---|
| `PREDICTION.md` | written before step 2, **never edited** |
| `ROLE_FACTS.md` | all measured facts, distributions, locators, bug disclosures |
| `VERDICT.md` | verdict per relayed claim, three kills, corrections, adversarial self-check |
| `roles.py` | mapping proof + FR@3 control |
| `roles_main.py` | distributions, gold adjacency, mechanism test |
| `roles_fix.py` | AUC fix, LoCoMo gold adjacency, direct adjacency test |
| `roles_fix2.py` | corrected permutation control, cross-benchmark corollary |
| `roles_confound.py` | archive-size confound |
| `roles_decomp.py` | adjacency vs cosine decomposition |
| `evidence/results.json` | every number produced (blocks A,B,C,D,E,F,G,K,L) |
| `map_probe.py`, `probe2.py` | schema/mapping probes |

Read-only discipline observed: nothing under `llmzip-work` written outside the output dir; repo
accessed only via `git show` on blobs.

---

## Key numbers

**Control (validates everything else)** — exact FR@3 tie expectation vs frozen:
LongMemEval **+10.053782505910153** (target +10.053783), PerLTQA **−6.274727836521099**
(target −6.274728), REALTALK **+5.300076925963445** (target +5.300077). LoCoMo +6.655 vs frozen
+6.828 — **0.173 pp disagreement, disclosed**, caused by gold-set assembly from `raw_evidence`.

**Mapping proven** (the mandatory adversarial check): count match 470/470; gold-index match
470/470 across 886 gold rows (order-sensitive); row-permutation control drives adjacency from
31.98 → 47.91 bits and AUC 0.914 → 0.507; role-shuffle drives asymmetry 6.90 → 0.045 bits.

**Distributions (LongMemEval, 209,187 adjacent / 57.2M total pairs):**
adjacent Hamming 31.98 (p5 16, p50 31, p95 50) vs non-adjacent 47.96; cosine +0.705 vs −0.0023;
**AUC 0.9088**. LoCoMo: 43.19 vs 47.97, cosine +0.145, AUC 0.6952.

**≤16-bit tail:** 0.1369% of all pairs, **83.56% of it non-adjacent** — both relayed figures
(0.14%, 84%) confirmed. Adjacent pairs hit the tail at 6.15%; same-session non-adjacent at 6.12%.

**Role asymmetry: 6.90 bits**, not the relayed ~1 bit. user→assistant 28.87 (n=114,870);
assistant→user 35.77 (n=94,285); shuffled control 0.045.

**Unexpected structural finding:** lag-2 pairs (SAME speaker) are **closer** (25.48 bits) than
lag-1 cross-speaker pairs (31.98). Speaker pairing is not what creates proximity.

**Gold-gold adjacency:** LME 1.33x (underpowered, 1.9 golds/archive); **LoCoMo 9.10x enrichment**
(2.85% of within-query gold pairs adjacent vs 0.313% chance).

**Mechanism test:**

| benchmark | n | median gold-dnn | close−far delta (pp) | 95% CI |
|---|---|---|---|---|
| LongMemEval | 470 | 18 | **−11.15** | [−17.79, −4.12] |
| PerLTQA | 8,265 | 27 | +0.87 | [−0.77, +2.47] |
| LoCoMo | 1,535 | 29 | −3.02 | [−6.37, +0.41] |
| REALTALK | 705 | 24 | −0.28 | [−5.10, +4.24] |

**Decisive corollary:** LongMemEval has the densest gold neighbourhoods (median 18 bits, 38.5% of
golds within 16 bits) and sign wins **+10.05 pp**; PerLTQA has sparse ones (27 bits, 3.2%) and sign
**loses −6.27 pp**. The hypothesis needs the opposite ordering.

**Decomposition of the one positive result (LME −11.15 pp):** survives archive size
(corr(dnn,N)=−0.039) and gold distinctiveness, but adjacency contributes −1.67 pp [−10.24, +6.70]
(null) and a **cosine** nearest-neighbour predictor reproduces −8.23 pp [−14.84, −2.01] of it.
So it is generic gold-neighbourhood density in the float geometry, not sign-specific speaker
duplication.

**No-role-filter claim: CONFIRMED** by reading `adapters/longmemeval_v52_adapter.py:80-103` —
`INVALID_ROLE` only appends a diagnostic and falls through to an unconditional `memories.append`;
role is also embedded in the indexed text at line 89. Corroborated by 114,902 user / 116,704
assistant rows.

---

## Bugs found in my own code (both disclosed, both corrected)

1. `roles_main.py:auc_fast()` used the wrong tail → reported AUC 0.093 instead of 0.909.
   Fixed in `roles_fix.py:F1`.
2. `roles_fix.py:F4` permutation control masked on permuted labels but indexed original rows,
   yielding a fake 33.71-bit "control". Fixed in `roles_fix2.py:G1` → 47.91 bits.

Corrections are recorded in ROLE_FACTS.md and VERDICT.md; PREDICTION.md was left untouched.

---

## Limitations

- Adjacency distributions cover LongMemEval and LoCoMo only; PerLTQA's cache exposes no turn
  ordering. The mechanism test (needs only gold-dnn) covers all four benchmarks.
- LME gold-gold adjacency is underpowered by design (single-gold questions).
- The cross-benchmark corollary is a direction over n=4 benchmarks, not a significance test.
- No causal experiment (dropping assistant rows and re-encoding) — out of scope under read-only.
- LoCoMo control differs from frozen by 0.173 pp; disclosed and isolated to gold-set assembly.
