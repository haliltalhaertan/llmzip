[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Disposition on binding-8 condition — PREPARED, NOT ACCEPTED

## Verdict: SATISFIED (on synthetic inputs only; does NOT discharge the binding)

"Condition" here means the implementation behaviour required by binding 8 as restated in
`BINDING8_READING.md` §3: exact-rational inputs, end-to-end exact arithmetic, no tolerance on
the decision path, ties decided as ties, exact §6 category boundaries, denominator
divisibility. Each element was exercised against the vendored code and held:

1. **Exact inputs** — VERIFIED: `parse_cell` (vendored module lines 215–289) reconstructs
   `fraction` as `Fraction(hits, gold_count)` from discrete retrieved/gold IDs; the runner's
   float cell is parsed only for an equality integrity check (lines 263–269) and never flows
   into `fraction`, `delta`, or any sign (T9a/b pass).
2. **End-to-end exact arithmetic** — VERIFIED: `mean_fraction` sums `Fraction` from
   `Fraction(0,1)` and divides by `len` (lines 87–91); `question_records` builds `delta` from
   exact fractions (lines 344–357); grep over the module finds `float` only in the integrity
   check and comments, and no `round(`/`isclose`/`epsilon`/`tolerance`/`threshold`/`numpy`
   anywhere on the decision path (T5a/d, T8a, T12 pass).
3. **No tolerance** — VERIFIED: `sign` (lines 94–95) is a bare `> 0 / < 0 / == 0` comparison on
   `Fraction`; `rational_payload` derives display decimals AFTER the sign and the sign does not
   depend on them (T1, T10 pass while the display reads all zeros).
4. **Ties as ties** — VERIFIED: `classify_primary` (lines 98–105) maps signs `-1/0/+1`, so an
   exact zero joins the `≤ 0` side; all-zero gives `NO_REPLICATION`, zero-plus-positive gives
   `HETEROGENEOUS` (T3a–e pass, including the Full→Heterogeneous flip).
5. **Category boundaries** — VERIFIED: Full ⟺ all four strictly positive; No ⟺ all four
   `≤ 0`; else Heterogeneous, matching §6 verbatim (T1, T2, T3b–d, T7a–d pass).
6. **Denominator divisibility** — VERIFIED: `build_report` raises
   `[BLOCKED - EXACT-RATIONAL DENOMINATOR RULE]` unless `bound % d.denominator == 0` with
   `bound = 5·n·lcmm(gold)` (lines 394–398, 432–434); tier/ceiling-free/archive denominators are
   enforced as frozen constants before any sign is reported (lines 428–451) (T8 pass).

Corroboration (VERIFIED, second route): the branch's own 10 unmodified outcome-free controls
pass against the same bytes (module sha256 `bda67f03…` confirmed at execution).

## Why this does NOT discharge binding 8

- **I am not independent.** Cold-start independent-auditor, no-self-audit, and no-self-seal
  rules (per programme governance) are not met by this run: I read the implementation I tested,
  and I authored both the inputs and the oracle. This report is a behaviour observation, not
  an audit.
- **Synthetic inputs only.** Nothing here touched real Task 4F1 outcomes, the sealed cohort,
  or the authorization gate. Real-data behaviour (including the `main()` path through
  `load_cohort`/`read_trial_rows`, fail-closed refusals excepted) is UNAVAILABLE-UNDER-SEAL in
  this session; what full authorization + real-input execution would show is a separate,
  explicitly authorized step I did not and could not perform.
- **Unfrozen, unmerged.** The implementation lives only on unmerged
  `origin/impl/t4f1-exact-rational-analysis-2026-09-04` (tip `4e13ac8`); it can still change.

## What remains before binding 8 could be discharged

1. **Freeze** the exact-rational analysis bundle byte-exact (module + tests + constants).
2. **Independent audit** by a cold-start auditor with no prior contact with the implementation,
   re-deriving the verdict from the seal and draft (not from this report), on an independent
   synthetic battery plus review of the real-data path guards.
3. **Merge** through the normal governance route (Head Researcher + co-chair), with the
   discharge recorded in the real ledger by its SOLE WRITER — a proposed ledger entry may be
   prepared as a separate file, never appended by me.
4. Only then, under a valid production authorization (which a seal is NOT), may the real-data
   run proceed — still computing every `D_t` sign exactly as tested here.

## What I could NOT do and why

- Run authorization / real-data execution: forbidden by the Task4F1 seal (would require
  `--mode run`-equivalent invocation, HMAC custody, and the absent 804MB BEAM corpus, which
  must not be fetched). Recorded as out-of-scope, not as a gap in the implementation.
- Recompute `source_section_sha256` (`09247bce…`): the extraction rule (which bytes constitute
  "section 6") lives with the seal verifier; restating a hash of my own byte range would prove
  nothing. Left as CLAIM.
