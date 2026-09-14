[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# F1 execution report — independent lead-regeneration of the frozen Claim-D contract

Namespace `research_e1_f1_repair_2026_09_14/`. Status of this document: PREPARED, NOT ACCEPTED.
Author is not the auditor and cannot close F1 (see `DISPOSITION.md`).

## 1. Outcome in one paragraph

The frozen contract was executed **as far as the reachable inputs allow**. My independent SPEC-derived
implementation (`f1_competition.py`, stdlib-only) is proven correct against hand-computed fixtures
(`verify_f1.py`: 27 PASS, 0 FAIL), the min-gold bug is deliberately reproduced and shown to move the numbers,
and all three reference value-sets are machine-rechecked byte-identical across branch sources. The real-data
rerun itself is **BLOCKED**: the four Drive archives the contract names are absent from every E1 branch and from
local disk, and network fetch is prohibited. Every currently-quoted Claim-D competition number therefore remains
an auditor intermediate calculation, exactly as before. No seal was crossed (Task4F1 untouched, BEAM never opened).

## 2. Requirements checklist (contract → disposition)

Contract: `origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:.../R2_COMPETITION_RERUN_CONTRACT.md`
(VERIFIED, read in full). Full box-by-box restatement: `CONTRACT_CHECKLIST.md`.

| contract box | result |
|---|---|
| C1 SHA-bound inputs verified before compute | BLOCKED — 0/4 archives present (`CACHE_INVENTORY.md`, probe E0) |
| C2 no refit/remap/re-filter | HONORED (synthetic fixtures only) |
| C3 headline gates ≤1e-12 | gate function implemented + tested (C1–C2); real application BLOCKED |
| C4 TOP64/BOT64 construction | implemented from text; proven on fixtures (A1–A3) |
| C5 per-gold metric, min-gold FORBIDDEN as metric | implemented; proven (A4/A5/A8/A9); min-gold present ONLY as labeled bug control |
| C6 non-gold sensitivity variant | implemented; proven (A4) |
| C7 average-rank Spearman summaries + sections | implemented; scipy cross-check maxdiff 5.6e-17 (B6); real targets UNREPRODUCED |
| C8 descriptive cluster bootstrap, seed 96013, B=2000, ledger | implemented; determinism + invalid-ledger proven (C3–C5); real intervals NOT generated |
| C9 persisted payloads | synthetic-schema analogues in `evidence/` (explicitly not the contract payloads) |
| C10 wording/side-conditions | honored; no R1 coefficient appears as current anywhere in this namespace |

## 3. Metric definition as implemented (from SPEC text, not from anyone's code)

Per archive: `v_j = mean_i(C_ij²)`; `order =` stable descending sort of `v`
(Python `sorted` over `range(D)` keyed by `-v_j` — stability keeps original axis order on exact ties);
TOP = first 64, BOT = last 64 (they overlap in the middle 32 by construction — independently corroborated by the
auditor's `topbot_overlap_values [32]` on all 520 archives, VERIFIED in `EXECUTION_LOG.txt`).
Bits `C≥0` / `qC≥0`; ordinary Hamming distances per arm → `d_TOP`, `d_BOT`.
Per gold row `g` (unique, range-checked; empty gold set = invalid query, excluded with reason):
`strict_all = #{i: d[i]<d[g]}`, `tie_all = #{i: d[i]==d[g]}` over ALL rows (self counts 0/1 — arm-symmetric, gaps
unaffected); `strict_ng`/`tie_ng` over non-gold competitors only. Query aggregates = arithmetic means over golds;
gaps = TOP−BOT. Min-gold control: `dmin = min_g d[g]`, counted once per query.
Spearman = average-rank (1-based, ties averaged), Pearson on ranks, `None` if <2 finite pairs or a constant rank
vector; non-finite pairs dropped (documented, counted in bootstrap ledger as `undefined_spearman`).

### Hand-computed oracle (the independence anchor — check this by hand)

Fixture `C` (5 docs × 4 axes, `k=2`), `qC=[1,-2,3,-1]`:
`v=[2.0,3.8,3.8,3.0]` → order `[1,2,3,0]` (j1 beats j2 on the tie by stability) → TOP=[1,2], BOT=[3,0].
`d_TOP=[0,2,2,0,2]`, `d_BOT=[0,2,0,2,1]` (VERIFIED A1–A3).
Q1 gold=[0,2], Δ=0.5: TOP g0: strict 0 (nothing <0), tie 2 (rows 0,3); g2: strict 2, tie 3 → (1.0, 2.5).
BOT g0: (0, 2); g2: (0, 2) → (0.0, 2.0). Gaps **(1.0, 0.5)**. Non-gold mask {1,3,4}: TOP-ng (0.5, 1.5), BOT-ng (0, 0).
Min-gold: dmin_TOP=0 → (0, 2); dmin_BOT=0 → (0, 2) → gaps **(0.0, 0.0)**. Correction demonstrated, not asserted.
Q2 gold=[4], Δ=−0.25: gaps (0.0, 2.0), min-gold identical — the single-gold case.
Q3 gold=[1,3], Δ=0.1: correct gaps **(−2.0, 0.5)** vs min-gold **(−3.0, 0.0)**.
Spearman Δ=[0.5,−0.25,0.1] vs strict gaps [1.0,0.0,−2.0]: ranks [3,1,2] vs [3,2,1] → ρ=0.5 exactly (B1).
Vs tie gaps [0.5,2.0,0.5]: ρ=−√3/2 (B2). All PASS to exact equality.

### Theorem (proven, 300 randomized 96-D trials, A9)

`gold_n == 1 ⇒ per-gold ≡ min-gold` exactly. Corollary, VERIFIED against branch bytes (D4): the auditor's
EXECUTION_LOG shows `lead == d2` to full precision in PerLTQA events/profile/social_relationship — precisely the
three sections whose recovered multi-gold count is 0 (`CORRECTED_RESULT.json` sections, VERIFIED). This is why R1's
bug survived review: it is invisible wherever every query is single-gold, and PerLTQA's headline (+0.2774/+0.2851)
is dominated by single-gold events (n=4346).

## 4. Three-reference comparison (full precision)

Lead = R1 buggy min-gold (CLAIM, live re-extracted); auditor = corrected per-gold (CLAIM, live re-extracted);
mine (real data) = UNAVAILABLE. Checks D1–D3/D5 prove the first two columns are byte-identical across
FINDINGS.json / CORRECTED_RESULT.json / contract table / EXECUTION_LOG.txt / CLAIM_MATRIX.json; D6 proves the R1
prose table rounds the lead column.

| benchmark | lead strict / tie (buggy) | auditor strict / tie (corrected) | mine, real data |
|---|---|---|---|
| LME | 0.09965709814218833 / 0.0989586520264074 | 0.14168629605302735 / 0.14045379360271315 | UNAVAILABLE-UNDER-MISSING-CACHES |
| REALTALK | 0.06118332620206951 / 0.0871527005507532 | 0.097939128891117 / 0.12281952421315011 | UNAVAILABLE-UNDER-MISSING-CACHES |
| PerLTQA | 0.27738722348615524 / 0.285059265942642 | 0.25416826537535475 / 0.2797878341571222 | UNAVAILABLE-UNDER-MISSING-CACHES |
| LoCoMo | 0.09370604039357276 / 0.09533237242284638 | 0.09491957131277647 / 0.10376015063205302 | UNAVAILABLE-UNDER-MISSING-CACHES |

Correction deltas (auditor − lead; descriptive, not mine): LME (+0.04203/+0.04150), REALTALK (+0.03676/+0.03567),
PerLTQA (−0.02322/−0.00527 — the ONLY benchmark where correction lowers the coefficient, because single-gold
events dominate and multi-gold dialogues correct downward: dialogues lead 0.09444/0.12193 → corrected
0.13054/0.11123, VERIFIED in EXECUTION_LOG), LoCoMo (+0.00121/+0.00843).
**No disagreement with the auditor exists or could be tested**: real-data agreement is UNTESTED, and any future
mismatch is a major finding by task definition. The synthetic demo (`evidence/results.json`) shows all three
variants diverging on multi-gold data, as expected.

## 5. Line-by-line comparison: mine vs the auditor's `competition_variants.py`

(Read AFTER my spec was fixed; auditor file is a post-hoc comparison target, never an oracle.)

- `topbot`: auditor `np.argsort(v, kind='stable')[::-1]` = ascending-stable-then-reversed; mine = true stable
  descending (`sorted` by `−v`). These differ ONLY on exact ties in `v_j`; with float mean-squares exact ties are
  measure-zero, and the audit reports identical axis selection under mean-square vs variance ranking. Residual risk:
  none credible, but a real-data rerun should log `order` hashes — my row schema is ready for that field.
- `metrics`: auditor `pg_all_*` (mean over golds, all rows) ≡ my primary; `pg_non_*` ≡ my sensitivity;
  `min_all_*` ≡ my bug control. Self-counting in `tie_all` (+1 per arm, cancels in gaps) identical. LoCoMo
  corrections-file handling and Delta sourcing are INPUT plumbing outside the metric — my implementation takes
  `(C, qC, gold, delta)` as inputs, so the same corrections apply unchanged at real-data time.
- `rho`: auditor `scipy rankdata average + corrcoef` ≡ mine (B6 maxdiff 5.6e-17 over 50 tied random trials).
- Bootstrap: auditor has no competition bootstrap (R1's is superseded); mine follows the contract (§C8) literally,
  including the LME-reduces-to-query-resampling behavior (singleton clusters) and the invalid ledger.
- Lead code: the actual R1 recovery competition module is on NO branch (only pilot-era min-gold snippets, e.g.
  `.../pilots_round3/muse_sessions/d2/d2.py:61-66`, predate the recovery). Lead-vs-auditor comparison rests on the
  auditor's recorded `lead_behavior` + mismatch counts (FINDINGS.json F1 evidence, VERIFIED) — second-hand (RELAYED)
  for the code itself, first-hand (VERIFIED) for the numbers.

## 6. For the skeptic: what would most damage this report, and how it was tested

Most damaging assumption: **my implementation parrots the auditor's code, so "PASS" is circular.** Defenses:
(1) the oracle is hand arithmetic (§3 — reproducible with pencil); the code was specified from contract sentences
before the auditor file was opened; (2) the single-gold theorem + D4 tie my implementation to a branch-byte fact
I did not choose (lead==d2 in exactly the zero-multi-gold sections); (3) scipy, an independent third implementation
of Spearman, agrees to 5.6e-17. A clean negative is stated where due: the headline claim — reproducing the eight
auditor coefficients — was NOT achieved and is honestly BLOCKED (§7), which is worth more than a loose "reproduced".

## 7. What was NOT done and exactly what would unblock it

- Real per-query rows, real Spearman targets, real bootstrap intervals, real headline gates, real sha256
  re-verification: all BLOCKED on the four archives in `CACHE_INVENTORY.md`. Needed: the three tarballs (+R1 ZIP
  for lead-code inspection) at the pinned shas, extracted to the auditor's layout, plus Stage-1 Delta rows —
  then `f1_competition.py` + `verify_f1.py` run unmodified (E0 probe flips from BLOCKED to live).
- No BEAM/corpora/queries/labels/embeddings were opened; no authorization constructed; no network used.

## 8. Receipts

- `python3 verify_f1.py` → 27 PASS / 0 FAIL / 1 BLOCKED (E0), exit 0. Output captured in-session 2026-09-14.
- `python3 evidence/make_evidence.py` → 27 rows (3 hand fixtures + 24 seeded 96-D SYNTH); SYNTH primary
  ρ strict 0.03402 / tie 0.44936; descriptive bootstrap (seed 96013, B=2000) strict (−0.43433, 0.55543),
  tie (0.23611, 0.59280) — synthetic numbers, valid only as machinery demonstration.
- Branch reads all via `git show origin/<branch>:<path>`; no checkout, no fetch; `main` untouched
  (`git status` shows only the new namespace untracked).
