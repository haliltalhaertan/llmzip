[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — LoCoMo baseline provenance audit: where the +12pp inference failed

## Plain-English summary

The programme repeatedly quoted a LoCoMo "SIGN minus float ≈ +12pp" gap as if it
were an established measurement. It was not. No frozen artifact ever contained a
historical LoCoMo float baseline, and no source file computes +12 from data:

- The shared plan required reproducing BOTH the historical native SIGN score AND
  the historical centered-float score before running any new intervention, and
  aborting if either gate failed.
- The worker reproduced the native SIGN score exactly
  (0.23654714666441054) but found no historical float arrays, substituted a
  freshly computed float score (0.16826334541318252), and continued anyway.
  Current gap: +6.82838pp, not +12pp.
- The +12pp figure traces back to user prompt briefs that asserted it "as given",
  never to a recomputation. The one report that repeats it says so explicitly:
  "programme-reported; not recomputed here — stated as given."
- An earlier certificate states outright that "no LoCoMo float anchor exists in
  the frozen artefacts." The only historical LoCoMo gap with a primary source is
  a different comparison entirely: Haar − Native = −9.8839pp.
- A fresh independent recompute from the original cache confirms the CURRENT
  numbers bitwise, but that cannot retroactively satisfy the missing historical
  gate. Verdict: **+12pp is UNSUPPORTED — retract pending a primary source.**
  The LoCoMo transfer result stays CONDITIONAL / PROTOCOL-DEVIATION.

Nothing below is a new theory, a tuned proxy, or a compression claim. All further
diagnosis is post-hoc, not preregistered and not a held-out prediction.

## 1. Provenance chain (claim -> exact source line)

| # | Claim | Exact source (file:line) | Status |
|---|-------|--------------------------|--------|
| P1 | Gate requires native AND float replication; abort if unreproducible | `theory_benchmark_test_v1/PLAN.md:15,17` ("Recompute ORIGINAL native SIGN96 and centered-float96 ... Abort new experiments if gate cannot be reproduced") | Binding plan; violated (see P2) |
| P2 | Worker: no frozen centered-float96 arrays; float is a fresh measurement; gate marked PASS on native only | `theory_benchmark_test_v1/locomo/REPORT.md:19-35` ("No frozen LoCoMo centered-float96 arrays exist in scope ... so the float baseline is a sealed FRESH measurement, not a gated anchor") | Self-disclosed deviation |
| P3 | Coordinator: substitution does NOT satisfy replication; status must be CONDITIONAL/PROTOCOL-DEVIATION | `theory_benchmark_test_v1/locomo/COORDINATOR_REVIEW.md:7` | Governing correction; supersedes worker's "PASS" framing |
| P4 | "+12pp" with explicit disclaimer of no recomputation | `bench3/runs/b3a_realtalk/report.md:28-30` ("LoCoMo +12.0pp (programme-reported; not recomputed here — stated as given)") | NOT a primary source by its own text |
| P5 | No LoCoMo float anchor ever existed in frozen artefacts | `race_2026-09-13/cert/cert_report.md:213` ("no LoCoMo float anchor exists in the frozen artefacts, so C3 is LME-only") | Predates theory wave; primary negative evidence |
| P6 | The only sourced historical LoCoMo gap is Haar-based, and it is negative | `drive/t4d/V52_T4D_COMPUTE_REPORT.md:7-9` (NATIVE 23.654714666441%, HAAR96 13.770827054136%, D = −9.883887612 pp); traced at `audit_2026-09-13/audit1_cont/report.md:132-136` | Different estimand (Haar codec vs native), opposite sign |
| P7 | +12pp asserted "as given" in tasking briefs | `muse_prompt_b3b_finish.md:30`, `muse_prompt_bench3_perltqa.md:58`, `muse_prompt_bench3_realtalk.md:58` (each "+12.0" as input premise); repeated downstream at `bench3/runs/b3b_fin/report.md:195`, `race_2026-09-13/CAMPAIGN.md:95` ("LoCoMo +12.0 verili" = "given"), `math_discovery_2026_09_13/bit_allocation/REPORT.md:51`, `math_discovery_2026_09_13/sign_mechanism/REPORT.md:230` | Transmission chain of an unsourced premise, not independent corroboration |
| P8 | Current exact-cache gap is +6.82838pp | `theory_benchmark_test_v1/locomo/COORDINATOR_AGGREGATE.json:8` (`current_native_minus_float_mc_pp: 6.828380125122796`); worker `gate.json:20,29` | Current measurement, not history |

Negative search scope (stated, not "does not exist"): content greps over
`bench3/`, `review_transfer/`, `reports/`, `pilots/`, `scratch/`, `drive/`,
`math_discovery_2026_09_13/`, `theory_benchmark_test_v1/`, `audit_2026-09-13/`,
`race_2026-09-13/cert/` for `+12/12.0pp/12pp/programme-reported` and for
LoCoMo float anchors; plus `git log -S 'LoCoMo +12'` in `/mnt/c/Users/MDP/dev/llmzip`
(empty). Found: only P4/P7 repeats (all disclaimed or premise-level) and one
base64-image false positive. No primary computation of +12 found in scope.

## 2. Original vs current metric definitions

- Historical native SIGN96 (unchanged across eras): Hamming distance on
  `sign(C), sign(qC)` with `sign(x)=+1 iff x>=0`; top-3 fractional recall under
  the frozen 20-seed priorities `default_rng(5_100_000 + ci*100_000 + t*100 + 99)`
  (`run_locomo.py:27-28,92-101`); anchor 0.23654714666441054 over 1535 valid QAs
  (1540 cat1-4 minus 5 with no retrievable evidence).
- Historical centered float96 for LoCoMo: NEVER FROZEN (P5). No per-QA array, no
  mean anchor, no tie-convention record specific to LoCoMo exists in scope.
  (`taskC_LoCoMo_perq.json` arms: NATIVE96, SPREAD80, RAND80_s2, BOT80, TOP48 —
  no float arm; verified programmatically, `perq_has_float_arm: false`.)
- Current float (worker + this audit): cosine distances on the regen cache
  (`regen/locomo/locomo_{ci}.pkl`: C column-centered to ~2e-16, QC = queries in
  the same centered frame), exact tie-expectation + 20-seed MC with the same
  frozen priorities. Effectively zero float ties
  (`float_mc_minus_exp_maxabs` 2.2e-16), so MC == exact throughout.

## 3. Exact independent current baseline (this audit, `verify.py` + `results.json`)

Independently implemented (own parsing, unit-vector cosine formulation, own
tie-law/MC code; run with threads=1, `PYTHONDONTWRITEBYTECODE=1`, ml-python -B):

- ncat14 = 1540, valid = 1535, excluded = 5; single-gold 1103 / multi-gold 432.
- sign MC 0.23654714666441054 (anchor diff 0.0), sign exact 0.2369591212262222.
- float MC = float exact = 0.16826334541318252.
- sign−float: MC +6.828380125122796pp; exact +6.869577581303966pp.
- Agreement with worker arrays: per-QA maxabs 0.0 (sign and float);
  vs `deney1_loco_peraxis.npz` native 1.11e-16 (fp noise only).
- Diagnostics only (NOT alternative claims): archive-macro gap +6.4529pp
  (macro sign 0.24057085 / float 0.17604133) vs question-micro +6.8284pp;
  any-hit rates sign 0.2964 / float 0.1993.
- Exact rational synthetics (Fractions, root-free): positive diagonal rescaling
  leaves all Hamming distances invariant (`synthetic_sign_invariant_under_pos_scale:
  true`) while cosine order can flip; E1 exhibit (ham 0 vs 1, both dots
  positive, cross-multiplied cosine inequality holds).
- Source bytes read (24 files incl. all pkls/npzs/jsons) hashed before and
  re-verified after: STABLE. Cited markdown sources hashed before/after: all
  identical (see §5).

This recompute CONFIRMS current arithmetic only. It uses the same regen cache
as the worker, so agreement is expected and is NOT an independent review, NOT a
historical replication, and does NOT cure the P1 gate bypass: a successful
current recompute cannot retroactively satisfy a missing historical anchor.

## 4. Error taxonomy (separated as required)

- **Algebra error:** NONE found in the LoCoMo worker arithmetic. Invariance
  identities (sign invariance under positive scale; LOW48(t)=HIGH48(1/t) up to a
  global positive scale) are correct and correctly flagged as construction, not
  evidence (`REPORT.md:43,45-49,55-58`).
- **Wrong assumptions:** the +12pp premise (P7) was consumed as background fact
  by downstream prose (P4-disclaimed once, undisclaimed in bit_allocation:51 and
  sign_mechanism:230). Assumption, not derivation.
- **Unidentifiable mapping:** Model-H theoretical `t` (true nuisance scale) is
  unidentified on real vectors; LOW48 query-magnitude grouping is a proxy, and
  both worker and coordinator state this (`REPORT.md:15-17`; PLAN.md:9,21).
- **Metric mismatch (the load-bearing one):** historical LoCoMo "gap" in
  programme memory (+12pp, sign−float, positive) vs the only sourced historical
  LoCoMo gap (−9.8839pp, Haar−native, negative, P6) vs the current measurement
  (+6.83pp, fresh float). Three different estimands; quoting them interchangeably
  is the provenance error. Also MC-vs-exact: sign MC 0.23655 vs exact 0.23696
  must not be mixed across eras.
- **Numerical bugs:** NONE in the current pipeline (bitwise/1e-16 agreement;
  FULL96 bitwise invariance; t=1 bitwise identity). Not the failure site.
- **Inference overreach:** (a) worker "GATE: PASS" framing while the float half
  of the gate was replaced by a fresh baseline (corrected by P3); (b) treating
  the HIGH48 contrast as a second look at the same algebraic coin rather than
  independent evidence is correctly handled, but anyonul reading it as
  confirmation would overreach; (c) any causal Model-H reading of the negative
  LOW48 contrast (−2.58291pp, CI [−3.77676,−1.31321], 10 clusters, nominal,
  unadjusted 1-of-4) beyond "this proxy transfer fails here."

No 'proven cause' is claimed from correlation anywhere above; the +12 verdict
rests on documentary absence + explicit disclaimers, not on a statistical fit.

## 5. Ranked error ledger

| Rank | Claim | Evidence | Correction | Still valid | Minimal discriminating next test |
|------|-------|----------|------------|-------------|----------------------------------|
| 1 | LoCoMo SIGN−float ≈ +12pp is an established historical result | P4 (disclaimed repeat), P5 (no anchor ever frozen), P8 (+6.83 current), negative search §1 | Mark UNSUPPORTED; retract pending primary source; stop quoting in prose | Nothing about +12 | Produce a frozen per-QA float array + mean from a pre-theory artifact, or keep retracted |
| 2 | LoCoMo transfer pilot was fully gated ("PASS") | P1 vs P2; P3 correction | Status = CONDITIONAL / PROTOCOL-DEVIATION; gate bypass explicit | Native SIGN reproduction (bitwise); all current arithmetic | None needed for arithmetic; fresh pre-registered replication if a historical float source ever surfaces |
| 3 | +12 might be the Haar gap misremembered | P6: Haar−Native = −9.8839pp (wrong sign, wrong estimand, 13.77% Haar vs needed ~11.65% float) | Reject this rescue: numbers do not match | Haar/Native anchors themselves | Exact-line check of any newly proposed source before acceptance |
| 4 | Current +6.83pp reproduces history | §3: same-cache recompute; no historical float array exists (P5, perq arms) | Current baseline only; diagnostic macro/micro + any-hit recorded, not selected | Current numbers | Same as #1 |
| 5 | Downstream theory prose citing "+12pp" as empirical motivation | bit_allocation:51, sign_mechanism:230 (coordinator review of the latter corrects math, not the +12 citation) | Annotate both as premise-level, non-evidentiary | Their synthetic theorems (with the shared-gold correction) | Text correction pass; no rerun |

## 6. Exact executed commands and counts

- `ls` workspace + source roots: 1 run.
- sha256/wc of 11 key files (before): 1 run; after-hashes of 15 files: 1 run —
  all overlapping hashes identical; `verify.py` re-hashed its 24 read files
  after running: STABLE.
- Content greps: `+12pp` in bench3/math_discovery/theory (3 hits + coordinator
  note); `12`-context in b3a report; `programme-reported|+12|12.0pp|12pp` across
  review_transfer/reports/pilots/scratch/drive/bench3 (only P4 + base64 false
  positive); LoCoMo-float grep in audit/cert (P5, P6); `locomo.{0,60}12` live
  excluding static copies (12 files, §1 table); `git log -S 'LoCoMo +12'`
  in llmzip (empty).
- `/home/mdp/muse-work/ml-python -B` probes: numpy import ok; perq arms list;
  regen cache shapes/centering (`C (419,96)`, colmean ~2e-16); npz native mean
  0.23654714666441054.
- `verify.py --write` (threads=1, no-bytecode): exit 0; 1535 QAs recomputed
  (sign+float, MC+exact); wrote `results.json`. Two self-bugs fixed en route
  (label-line SyntaxError; filtered-index IndexError) — both in audit-only code,
  sources untouched.
- Counts: 24 source files hashed; 1535/1535 QAs recomputed; per-QA maxabs vs
  worker 0.0 (both arms); 0 float ties (2.2e-16); 10 archive clusters noted.

Frozen files untouched; all outputs in this audit workspace only. No installs,
network, pushes, or main-branch changes.
