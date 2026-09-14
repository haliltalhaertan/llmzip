# DRAFT PREREGISTRATION v2 — TWELVE-BYTE BUDGET RACE (Task 4(b)-class, LOCAL DRAFT)

**Status:** DRAFT v2 — NOT SEALED, NOT APPROVED, NOT RUN. Supersedes v1 (2026-09-13) after four
independent review sessions (PRE1 adversarial: 8 FAIL / 8 CAVEAT / 5 NOTE; PRE2 brainstorm: 12
changes; MATH-1 model validation; MATH-2 theory framing). Awaiting Head-Researcher sign-off.
Nothing runs before signature + seal. Nothing leaves this machine.

**Basis:** HR budget decision (`V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`, commit 89d3169
— operative clauses kept verbatim in §1); roadmap Design 2; rounds 1–3 pilots + errata; the four
review outputs under `prereg_race_2026-09-13/{pre1,pre2,math1,math2}/`.

**What changed vs v1 (summary):** scoring semantics now fully specified (§3); estimand + decision
rules rebuilt on the m1 null with pre-seal calibration (§4); RaBitQ32's 32-dim rule specified and
the HR-name trap (TOP32) resolved by construction choice (§5, flagged for HR); constructors/
seeds/panels/fallback policy fixed (§5); byte worksheet with shared/amortized numbers added
(§6); sealable run package defined (§8); disclosure extended incl. negative outcomes (§9);
mechanism-model annex added (§10).

## 1. Budget definition (verbatim from the HR decision — unchanged)

≤12 **marginal persistent bytes per vector** (code + any per-vector metadata: norm/scale/correction
scalars, headers). Shared state (codebooks, rotations, centroid tables) is **outside the cap** but
**reported separately** for every arm (§6). All codecs are **archive-local-fitted**; global/
cross-archive codebooks are a different deployment configuration, out of scope. Abort if
`measured_bytes != declared_bytes` — measured on the serialized per-vector payload (see §6 tie-break
rule when `code_size` and serialization disagree).

## 2. Benchmarks, protocols, gates (unchanged from v1 + precision fixes)

- LME-470; LoCoMo-1535 (Cat1-4, audit-valid). Sign codes `D=(C>=0)`, `Q=(qC>=0)`; Hamming;
  20 tie trials (`rng(5_100_000+lex*100_000+t*100+99)`; LoCoMo `stable_archive_seed(ci,t)+99`);
  top-3; fractional evidence R@3; per-question then aggregate.
- **Anchor canonicalization (C8):** LME anchor 0.5419751773049645 = the aggregate derivable from
  the frozen question-level CSV; where the frozen script constant shows the next-digit variant
  (...646), the CSV-derived value is canonical; tolerance ≤1e-12 absorbs the last digit.
  LoCoMo anchor 0.23654714666441054.
- Abort gates: both anchors recomputed in-run, ≤1e-12, before any arm. Reports per benchmark,
  never pooled.

## 3. Scoring semantics — FROZEN (closes F2/C7; PRE2 §(c) adopted verbatim where noted)

- **Task wrapper (fairness core):** every arm maps (same centered C, qC, archives, questions,
  gold) → top-3 under the same K=3 and the same 20 frozen tie draws → fractional R@3, per-question
  then aggregate. Score scales are never compared; only per-question FR@3. Fairness sentence
  (sealed): "All codecs solve the same retrieval task with per-question pairing; score-scale
  differences are absorbed by rank-based FR@3 and byte differences by the measured-bytes abort
  plus the recall-vs-measured-bytes dominance check."
- **Per-family estimators (literal):**
  - Sign subsets: Hamming on selected bits (frozen).
  - RaBitQ32 (primary): codec-native asymmetric estimator; the exact faiss call sequence
    (constructor, rotation source, scalar usage) is frozen in the run package at seal; the
    transform chain is verified by smoke S7 with an acceptance criterion (recorded, not prose).
  - PQ m=12×8bit: ADC against the archive-local codebook; no residual rerank, no float
    shortlist; LUTs are query-time compute, not persistent bytes (N3).
- **Ties on floats (the epsilon rule — pick one, frozen):** tie := **exact equality** of the
  estimated distance (Δ=0.0); near-but-unequal values order strictly; ordering =
  `lexsort((distance, trial_priority))` with the same 20 frozen draws as sign arms; per-question
  records persisted; trial-SD reported (≈0 expected under determinism pins). No jitter, no
  dither, no rerank.
- **Determinism pins (C4):** threads=1 (OMP/MKL/OPENBLAS/NUMEXPR); python/numpy/faiss/BLAS/OS
  versions recorded in manifest; duplicate-code exact ties must reproduce bit-identically.

## 4. Estimand + decision rules (closes F3/F4; calibration notebook pre-seal)

- **Displays:** per-(family × width) gap table vs SIGN (per benchmark); per-question W/T/L
  matrices + tie-share for SIGN vs each competitor (tol 1e-12); per-type/Cat descriptives
  (descriptive only).
- **Primary contrast (ONE per benchmark, named):** `SIGN12B − max_aggregate(sealed competitor
  set)`, where the sealed set = the frozen arm list of §5 (per-seed aggregates; per-question-
  oracle explicitly excluded); bootstrap **re-selects the argmax inside each resample**; B and
  bootstrap seeds are literals in the run package.
- **Null calibration (F4):** the decision lines are NOT fixed a priori in this draft — a pre-seal
  notebook extends the m1 simulation (−1.62/−1.20pp no-edge baseline; observed max +1.91) to the
  FULL sealed competitor set (≈27 looks/benchmark), and freezes **numeric kill/promote lines as
  literals** before seal (structure: kill if SIGN loses beyond [null-max + margin]; promote only
  if SIGN wins beyond the calibrated lift band AND clears the null in the same direction).
  The v1 literal "≥2.0pp" is explicitly superseded (it sat 0.09pp above the observed null max).
- **Multiplicity (F4):** family-wise control; primary gating on the per-benchmark primary contrast
  only (Bonferroni across the 2 benchmarks; secondaries descriptive). Complete 16-cell
  (4 zones × 2 benchmarks) decision table published pre-seal with a point-vs-interval rule.
- **Curve (C6):** recall-vs-bytes as a DECISION INSTRUMENT: x = measured marginal bytes (dual
  axis: marginal + effective/amortized); points: native + all panels/seeds + RQ/PQ + A7-44B
  off-contrast + one k=16/24 confirmatory point per benchmark; isotonic fit per family
  (no cross-benchmark fitting); **dominance definition (literal):** pairwise-gate IRRELEVANT if
  one arm's per-seed FR range lies entirely below another's at every common byte point
  (pointwise, CIs stated) — "dominated everywhere" kills regardless of band.
- **m1 quote fixed:** a true ≈+2.6pp premium would be required to clear the vs-best-of-10 null at
  the observed scale (was misquoted as ≈3pp).

## 5. Arms (F1/F5/C1/C2 resolved; literal seeds frozen at seal)

| # | Arm | Marginal | Construction |
|---|-----|----------|--------------|
| A0 | NATIVE SIGN96 | 12B | reference |
| A1 | SPREAD subsets (repaired rank-linspace) | 10/8/6B | eff_k==k asserts; single fixed construction; **dual-bar reporting** (vs-best primary; vs-mean secondary; fixed-vs-max disadvantage stated) |
| A1b| BOT-tail (LoCoMo only: BOT80/64/48) | 10/8/6B | benchmark-local, flagged; LoCoMo bar thereby stricter (C1); LME BOT48 descriptive contrast |
| A2 | RANDOM panels | 10/8/6B | **10 seeds per width** (C2): literals `93000+10*width_idx+j`, j=0..9; width_idx {0:48b,1:64b,2:80b}; per-seed records; namespace deliberately disjoint from Deney-1's 91000s (N1) |
| A2c| **TOP-variance negative control** (k=48; k=64 LME optional) | 6B | prespecified directional expectation: loses to random-mean by ≥5pp; if it ever wins → pipeline suspect (validity gate) |
| A3 | Learned selection | — | **EXCLUDED** (Design-1 kill; numbers cited: −1.25pp/2-of-10 LME; −0.15pp LoCoMo) — disclosed record, zero runner code |
| A4 | RaBitQ32 (PRIMARY) | ≤12B measured | **32-dim rule (F1): spread-32 (repaired rank-linspace) PRIMARY; random-32 (3 frozen seeds) as SECONDARY sensitivity; TOP32 documented as a curve point with anti-optimality expectation — NOT a race member.** Same centered C; float query through the same reduction; measured bytes from pre-seal probe: RQ96=20B, RQ32=12B (must reproduce as asserts). **Deviation from HR-named `TOP32_RABITQ32` — flagged for HR decision (§8.7).** Single rotation draw prohibited: rotation panel = 3 seeds (rotations are high-variance; 4C3 −15.9pp evidence) |
| A5 | RaBitQ32 + random-rotation wrapper | ≤12B | SECONDARY (sensitivity only; caps multiplicity) — same pins |
| A6 | PQ m=12×8bit (plain; NOT OPQ — learned-rotation NOES; OPQ noted as future) | ≤12B | archive-local; **no-fallback failure policy (F5): if train fails on an archive → arm masked for that archive (counts + FR-over-available reported), never substituted; LoCoMo min-N measured pre-seal; mask-rate threshold named at seal.** Shared state reported (≈98,304 B/archive; ≈200 B/vec at LME N=490) |
| A7 | extended-RaBitQ (~44B) | 44B | curve point only; never in pairwise gates |

## 6. Byte worksheet (F6; primary-table columns, not a footnote)

Per arm: `[code B | scalar B | header B | declared | measured (serialization method) |
shared-state B/archive | amortized B/vec @ stated N | verdict]`. Tie-break rule when
`code_size` disagrees with measured serialization: **measured wins; disagreement = abort (C3
re-grounded: on pinned faiss 1.15.0 `IndexRaBitQ` has no `nb_bits` attribute — the silent-trap
abort is kept regardless, tied to the pinned API).** Known numbers to carry: PQ shared state
98,304 B/archive (≈200 B/vec at LME median N=490 — the "small archives" framing was dropped);
sign-mu shared 768 B/archive. Dual-axis curve (§4).

## 7. Scope guards (what is NOT in this race)

Learned-selection arm (any variant) — killed, disclosed only. Hetero-precision — future prereg
only (own width/threshold NOES). Adaptive routing — closed (m2/m3). PCA/whitening/learned
rotations/supervised rotation/reranking/alternate metrics beyond the named per-arm estimators —
NOES-gated, excluded. New-encoder generality — ill-posed until the SVD fork settles; scoping note
only. Cross-benchmark transfer arms — pilot only (transfer ≈ chance). Sub-8-bit direction —
one confirmatory point only (§4 curve). Global/cross-archive codebooks — different deployment
config. No trial-count/estimator changes mid-race (100-trial tie-mass work stays descriptive).

## 8. Sealable run package (F7) & pre-seal checklist

**Run package (must exist before signature):** run plan + runner commands with **repo-relative
paths** (no `C:/` hardcodes — deney1 harness precedent); output manifest (HASHES_ROUND3.txt-style,
`sha256sum -c` ALL-OK); frozen analysis spec (bootstrap B/seeds/strata; LoCoMo conversation-cluster
definition: clusters = conversations, counts stated); stop/fallback rules (faiss import assert;
PQ-train mask policy; cohort mismatch); provenance hashes (certified matrices list with paths+
hashes; faiss wheel sha256; installed-not-vendored); **no-reseed-after-outcome / amendment
policy**; **seal-hash binding (V52 PRE_RUN_SEAL.json pattern)**.

**Pre-seal checklist (merged PRE1 S1–S10 + PRE2 §(d); all must pass):**
1. HR approval line signed; seal commit recorded.
2. Native reproduction abort (both anchors, ≤1e-12) in the race runner.
3. Seed literals frozen in runner (panels 93000+…; 20 tie draws; B + bootstrap seeds).
4. `measured_bytes==declared` abort + worksheet populated (marginal vs shared vs amortized).
5. Construction asserts (eff_k==k, logged cols, no sentinels) incl. BOT arm; tie-seed identity.
6. Third-party pins: faiss exact version + wheel sha256 + import assert; rotation-chain
   verification (S7) executed with acceptance criterion.
7. Negative controls: one failing example recorded per abort (wrong anchor, wrong bytes, eff_k≠k,
   sentinel, mismatched tie seeds).
8. Byte replay smoke: RQ96=20, RQ32=12, PQ=12, ext=44; deliberate declaration mismatch aborts.
9. PQ min-N smoke on the min-N archive of EACH benchmark (or the mask policy fires as specified);
   LoCoMo min-N measured.
10. Determinism smoke: retrain+rerun with fixed seeds/threads ⇒ bit-identical codes and FR.
11. Dry run: 5-question end-to-end per benchmark reproducing gates + manifest shape.
12. Disclosure boilerplate (§9) travels with the sealed text; two pending HR decisions resolved
    (§8.7): (a) RaBitQ 32-dim rule (spread-32 proposed, deviates from HR-name TOP32); (b) numeric
    kill/promote lines from the calibration notebook.

## 9. Disclosure boilerplate (F8-extended; travels with the sealed text)

`[LOCAL EXPLORATORY PILOTS axis_attack r1 (2026-09-12) + r2 (2026-09-13) + r3 (2026-09-13) +
missing analyses m1/m2/m3 (2026-09-13): alternate bit widths; variance-ordered/matched selection;
gold-informed E2/E3/R2B/D2 utilities; extra random seeds; tie-mass decomposition (D2/D2X); mixing
fresh-Q confirmation (d4); cross-benchmark transfer matrix (D3); gold-free adaptive-routing probe
c2 — CLOSED, NOT prereg-ready (m3: LME α=0.20 inside 200-draw noise p_bonf=0.18; LoCoMo inside
noise at all α; m2: gold-free G 0/10 splits ≥0.65); the Design-1 kill gate that excluded A3 was
itself an EXPLORATORY (not preregistered) gate — its numbers are −1.25pp/2-of-10 (LME) and
−0.15pp (LoCoMo), with kill-null calibration m1 (no-edge ≈ −1.62/−1.20pp vs-best; observed at
57th/89th percentile); SPREAD stride-2 cap erratum disclosed and repaired (true rank-linspace,
eff_k asserts). ALL DISCLOSED.`

`[NOES LICENSES: this preregistration itself licenses the race's alternate distance metrics
(ADC, RaBitQ asymmetric estimator) by naming each arm's estimator in §3. Whitening, PCA/learned
rotations, learned thresholds, reranking, supervised rotation remain NOES-gated and are NOT
licensed here (PQ is plain — OPQ excluded; the A4 32-dim rule uses fixed spread/random axis
choices, not learned projections).]`

`[No new-encoder data; frozen accepted tasks 4C1–4D untouched; Task 4F1/BEAM boundary untouched;
no corpus-scale retrieval; all run artifacts stay local.]`

§6/curve numbers carry per-number citations into ROUND2/ROUND3 reports, DENEY1_REPORT,
missing_analyses/{m1,m2,m3}, and pilot REPORT.md.

## 10. Mechanism annex (descriptive; no decision weight)

**MATH-1 model (validated on frozen LME-470):** the exact conditional-uniform tie model — for
gold with S strictly-closer and T tied docs, P(top-3) = f(S,T) exactly, no independence
assumptions — reproduces EVERY panel arm's FR: per-question r ≥ 0.9968, MAE 0.004–0.009,
residuals at MC-noise scale; the TOP48 collapse is reproduced from distance profiles alone
(−12.11pp predicted vs −12.34pp measured). The independent-bits plug-in fails in sign and level
(+2.9pp for TOP48; +4…+26pp levels) because retrievable-regime tie mass runs 7–13× over binomial
— duplicate spikes, not smooth histograms, are the mediator. Mixing chain confirmed: pairing →
within-pair Cov (0.001/0.019/0.039 matched/random/anti) → histogram width → burial (~86% of the
width gap). **Race usage:** for every arm, also report model-predicted vs measured FR
(theory-validation column) — descriptive, in the annex only.

**MATH-2 pre-specified descriptive analyses (exploratory thresholds, no gates):** S4 —
discriminating double stratification (margin × tie-mass), 15pp gap rule with bootstrap CI;
S2 — floor calibration (predicted collapse-k proxy vs measured; ρ ≥ 0.5 prespec as exploratory).
S3 note: the selection-lift bound (sub-Gaussian max, ties to m1) is the cleanest formalization
candidate; Lean/Mathlib work deferred (Muse-only cost rule). Non-applying theory caution:
JL-style distance lower bounds do NOT transfer to top-k retrieval (category error) — not cited.

*[LOCAL DRAFT v2 — NOT PUSHED] [NOTHING RUNS UNTIL HR SIGNATURE + SEAL]*
