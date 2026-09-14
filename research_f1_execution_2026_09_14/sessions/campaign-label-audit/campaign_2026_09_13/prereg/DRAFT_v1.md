# DRAFT PREREGISTRATION — TWELVE-BYTE BUDGET RACE (Task 4(b)-class, LOCAL DRAFT)

**Status:** DRAFT — NOT SEALED, NOT APPROVED, NOT RUN. Awaiting Head-Researcher approval before
any seal/run step. Nothing leaves this machine.
**Basis:** (i) the recorded budget decision (≤12 marginal bytes definition — frozen verbatim below);
(ii) the roadmap's Design-2 specification (strategy/roadmap_2026-09-13/muse_strategy_roadmap.md §3);
(iii) rounds 1–3 pilots + reviews (all disclosed in §7). Prepared 2026-09-13.

## 0. One-line purpose

Decide whether ANY codec whose **marginal persistent cost is ≤12 bytes per vector** can match or
beat the frozen **NATIVE SIGN96** (the 12-byte sign code) on the two frozen benchmarks under the
frozen protocols — with the question "which bits" (spread vs variance vs random) given first-class
arms, because rounds 1–3 showed bit selection dominates nominal width in this regime.

## 1. Budget definition (frozen verbatim from the decision artifact)

- Cap: **≤ 12 marginal persistent bytes per vector**, counting the code itself **plus any
  per-vector metadata** (norm/scale/correction scalars, per-vector headers).
- **Shared state** (codebooks, OPQ/rotation matrices, centroid tables) is **outside the cap** but
  its byte cost **must be reported separately** for every arm.
- All codecs are **archive-local-fitted** (as in the frozen pipeline); cross-archive/global
  codebooks constitute a **different deployment configuration** and are out of scope for this run.
- Every arm must assert `measured_bytes == declared_bytes` **before any compute**; abort otherwise
  (this is the known `nb_bits` silent-trap guard).

## 2. Benchmarks, protocols, gates (all frozen, verbatim)

- **LongMemEval-470** and **LoCoMo-1535 (Cat1-4, audit-valid)**; sign codes `D=(C>=0)`,
  `Q=(qC>=0)`; Hamming; 20 tie trials (`rng(5_100_000+lex*100_000+t*100+99)` / LoCoMo
  `stable_archive_seed(ci,t)+99`); top-3; fractional evidence R@3; per-question then aggregate.
- **Abort gates:** native reproduction = 0.5419751773049645 (LME) / 0.23654714666441054 (LoCoMo),
  tolerance ≤1e-12, both recomputed in-run before any arm.
- Reports **per benchmark, never pooled**; heterogeneity (e.g. bottom-tail nuances on LoCoMo)
  reported, not averaged away.

## 3. Arms (each with its byte-accounting worksheet; seeds frozen at seal)

| # | Arm | Marginal bytes | Notes |
|---|-----|----------------|-------|
| A0 | NATIVE SIGN96 | 12 | reference (frozen) |
| A1 | SPREAD subsets, repaired rank-linspace construction | 10 / 8 / 6 | eff_k asserts; LoCoMo-side BOT-tail arm added as benchmark-local, flagged |
| A2 | RANDOM panels at matched widths | 10 / 8 / 6 | ≥7 fresh seeds per width [literal seeds FIX AT SEAL: `93000 + 10*width_idx + j`, width_idx∈{0:48b,1:64b,2:80b}, j=0..6]; per-seed records |
| A3 | Learned-selection arm | — | **EXCLUDED** per pre-declared Design-1 kill (mean −1.25pp/2-of-10 wins LME; −0.15pp LoCoMo; null-sim places it in the no-premium zone). Gating rule executed: spread/random take its slot. |
| A4 | RaBitQ32, plain | ≤12 (measure & report) | pinned `faiss-cpu` [version+wheel hash FIX AT SEAL]; verify rotation chain empirically — do not assume wrapper semantics |
| A5 | RaBitQ32 + random-rotation wrapper | ≤12 | same pin; both namings carried |
| A6 | PQ, m=12×8bit | ≤12 marginal | report per-archive effective cost on small archives explicitly (do not hide scaling) |
| A7 | extended-RaBitQ (~44B) | 44 | **OUT of matched-budget contrast**; reported on the recall-vs-actual-bytes curve only |

## 4. Primary estimand and decision bands (freeze before run)

- **Primary:** per-seed difference (SIGN12B − best ≤12B competitor) on each benchmark, seed-panel
  mean + per-seed range, question-paired bootstrap CI; conversation-cluster bootstrap additionally
  for LoCoMo. Bands on the programme scale: **≥ +2.0pp decisive for SIGN; +1.0–2.0pp moderate;
  ±0.5pp parity; ≤ −1.0pp against.**
- **Kill:** the "SIGN96 competitive at 12B" line dies if SIGN loses to any ≤12B-total competitor by
  **≥2.0pp on either benchmark**, or the recall-vs-bytes curve shows SIGN dominated everywhere.
- **Promote:** to engineering if SIGN wins/parities (**≥ −0.5pp**) on both benchmarks with
  per-seed ranges not overlapping the alternate-width failure null. Benchmark-split outcomes are
  reported as heterogeneity — no averaging.

## 5. Controls

Native reproduction both benchmarks (abort); `measured_bytes==declared` (abort); construction
asserts (eff_k==k, logged cols, no sentinels); identical tie seeds across arms; third-party pins
(installed-not-vendored, wheel hash recorded); negative controls proving each check can fail;
per-question persistence for every arm/seed.

## 6. Science context to note in the sealed text (from rounds 1–3)

Sub-12B behavior on LME: 10B ≈ −2.7pp, 8B ≈ −5.9pp, 6B ≈ −9.2pp vs native (spread/random);
variance-ordered selection is anti-optimal (−10pp at 6B; worst arm on both benchmarks in every
one of 59/60 cross-checks); mixing damage is monotone in variance disparity; the kill-rule null
simulation shows the vs-best-of-10 bar behaves as a valid premium detector (expected no-edge gap
−1.6pp/−1.2pp; a true ≥3pp premium would clear it).

## 7. Disclosure boilerplate (travels with the sealed preregistration)

`[LOCAL EXPLORATORY PILOTS axis_attack r1 (2026-09-12) + r2 (2026-09-13) + r3 (2026-09-13):
alternate bit widths, variance-ordered/matched selection, gold-informed E2/E3/R2B/D2 utilities,
extra random seeds, tie-mass decomposition, cross-benchmark transfer matrix, fresh-Q mixing
confirmation, and the gold-free adaptive-routing probe (c2) — ALL DISCLOSED. The learned-selection
arm was killed by a pre-declared gate (numbers in ROUND3_REPORT.md). Whitening, PCA/learned
rotations, learned thresholds, reranking, supervised rotation, alternate distance metrics were NOT
touched by the pilots and remain NOES-gated (prereg-or-nothing). R2D and D5 errata acknowledged
and dispositioned. Kill-rule null (m1) quantified selection lift.]`

Also: frozen accepted tasks 4C1–4D untouched; **Task 4F1 / BEAM boundary untouched**; no corpus-scale
retrieval; this run consumes only the frozen LME/LoCoMo pipelines and certified matrices.

## 8. Open items to fix at seal (checklist)

1. Seed literals (A2) written as constants in the runner.
2. `faiss-cpu` pin: exact version + wheel sha256; runner asserts import version.
3. Byte-accounting worksheet per arm (per-vector vs shared-state split; row in results).
4. Negative-control artifacts for every check (one failing example recorded).
5. Runner asserts `code_size` semantics against measured serialized bytes for RaBitQ/PQ.
6. HR approval line: ______ (to be signed before seal; nothing runs before this).

*[LOCAL DRAFT — NOT PUSHED] [NO PART OF THIS RUNS UNTIL HR APPROVAL]* 
