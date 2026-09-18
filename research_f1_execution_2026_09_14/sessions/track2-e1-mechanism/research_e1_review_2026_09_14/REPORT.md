[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — E1 review (track2-e1-mechanism)

Work is PREPARED, NOT ACCEPTED. I cannot accept, seal, ratify, or close anything.
Local commit sha: content commit `e748732eca253ff5a58228cb6ab64a010016066f`
(branch `muse/track2-e1-mechanism`); this sha-recording edit is committed separately —
see `git log` for the follow-up sha.

## What I produced (all new files in `research_e1_review_2026_09_14/`)

- `STATUS.md` — task receipt log, written first.
- `E1_MAP.md` — the 10 refs are 8 commits; v2/v2-frozen and checkpoint/lme-secondary are
  byte-identical alias pairs (empty pairwise diffs, shared shas — VERIFIED); v1→v1-frozen is a
  real 3-file step; dependency chain v1 → v1-frozen → v2 → checkpoint → recovery → r2, with the
  two audits hanging off checkpoint and recovery respectively. R2 (`d5edeb3`) is the tip, still
  pending rerun + re-audit.
- `MECHANISM_FINDINGS.md` — supported (P64 regime marker; 520/520 TOP-redundancy/BOT-effdim
  asymmetry; corrected per-gold competition direction, provisional) vs refuted/nulled (V1 low-
  variance wording, scalar heterogeneity, marginal-signal concentration, drop-loss difference,
  aggregate tie-rate causation, Q_ABS_CV×Q_EFF double-counting, duplicate collapse) vs merely
  restated (signal-vs-redundancy tradeoff, causal interaction). Carries the line's own licensed
  narrow claim verbatim with limits, and names the 520/520 + S3 bit-level legs as the most
  valuable surviving artifact.
- `NUMBERS_CROSSCHECK.md` — LME/REALTALK/PerLTQA gates and LoCoMo SIGN reproduce canon exactly
  (lead↔audit↔main all agree); P64 and 520/520 replicate three ways; R1 competition numbers
  superseded by audit-corrected per-gold table (direction unchanged). The LoCoMo +6.82838013 pp
  vs historical ~12pp discrepancy is reported without resolution: ~12pp has no frozen source and
  stays NOT_AN_ANCHOR; no frozen programme float figure contradicts +6.83.
- `WHAT_TO_DO_NEXT.md` — one frozen fifth-benchmark confirmatory test (E1-C1) with four
  predeclared falsification conditions, plus the mechanical R2-rerun prerequisite gate.

## What I verified (bytes I ran or read)

- All 10 ref→sha→date→subject rows and all 10 diff counts vs `5ec3db60` (`git for-each-ref`,
  `git diff --name-only`, `git log -1` — VERIFIED).
- Empty pairwise diffs for both twin pairs; exact 3-file v1→v1-frozen diff; 9-file v1→v2 spine;
  exact 5-file recovery→r2 addition (VERIFIED).
- Full reads: bridge report (66 lines), V1 disposition, V2 receipt, checkpoint (all 9 §§),
  LME secondary report, recovery report (142 lines), R2 report + disposition + contract
  (substance), both audit reports in full (179 + 64 lines), SPEC_V2 in full.
- Canon locators on main for LME SIGN/float and LoCoMo SIGN (`git grep` on `5ec3db60` — VERIFIED present).
- Assumption most damaging to my conclusion (docs faithfully describe code/figures): tested by
  three-way figure agreement (line↔recovery↔audit) on gates, P64, 520/520, and the audit's own
  1e-12 ten-script rerun + byte-gate checks (CLAIM, relied on second-hand where I did not
  re-execute — labeled as such). Single-source items (e.g. R2's corrected rows, which are the
  audit's rows reprinted) are labeled PROVISIONAL/PENDING, not verified.

## What I could NOT do and why

- No per-query outcomes, distances, recall, corpora, labels, or embeddings opened (Task4F1 seal;
  BEAM corpus never fetched — never attempted). All numbers are the line's published summary
  gates/coefficients, which the task permits.
- No re-execution of any E1 script or recomputation of any figure (read-only review mandate +
  30-minute budget + no-install/no-network discipline). Mechanical reproducibility rests on the
  two independent audits' testimony, which I relay as CLAIM, not as my own verification.
- No ledger/manifest/continuity writes (Head Researcher sole-writer rule); no existing file
  touched — `git status` shows only the new namespace (checked before commit).
- LoCoMo ~12pp provenance: unresolvable from committed material by the line and by me;
  recorded as UNRESOLVED rather than adjudicated.
- Never pushed, never touched main, never checked out another branch (all reads via
  `git show origin/<branch>:<path>`).

## Skeptic's pre-emption

The headline a skeptic should distrust is "P64 predicts SIGN advantage." My answer: it does
not — not per query (+0.07…+0.25 rhos, rank-method-sensitive) and not causally anywhere. What
survived adversarial audit is narrower and duller: a regime-level polarity marker plus a
sample-wide bit-redundancy asymmetry, with the causal mechanism explicitly unresolved and the
strongest quantitative leg (Claim D) awaiting its own rerun. If the fifth-benchmark test in
WHAT_TO_DO_NEXT fails any of its four frozen conditions, even that narrow structure should be
declared family-specific.
