# REPORT 08_storage_contracts — static-storage & rank/membership contracts (HARD R2)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Scope: mathematical/cost correctness of the V7→V10 static-storage chain
(denominator accounting, copy identities, physical-vs-logical byte costs),
the rank-cert BULGU-1/BULGU-5 repair, and repair acceptance status. No
offensive testing was performed; only benign valid numeric fixtures on
isolated copies of branch files (via `git show`, read-only; nothing
checked out, no ref changed). Same-CLI partial independence applies.

Outcome: the denominator math is correct as specified; the rank-cert POC
bug reproduces exactly as audited and the v3 repair behaves as claimed on
the POC plus scale/invalid-J probes. **No obligation is genuinely closed
by acceptance**: every repair is an unmerged, unfrozen candidate; the
governance package is explicitly PREPARED / NOT ACCEPTED; 9 of 35 ledger
rows are NOT RUN live (receipt-read only). Details and limits below.

## 1. Denominator accounting — CORRECT as specified (7 live checks)

V9 rows carry `(physical_copy_id, population_id, d_k)` with no archive
identity, so summing the d-column over duplicated physical copies counts
one logical archive twice. The V10 rule (unique-by-archive logical total,
per-copy numerators never deduplicated, no byte total offered) is the
correct fix for that defect class, and the implementation matches the rule:

- Headline arithmetic verified by re-execution: 2 x 231606 = 463212, so a
  12 B/vector representation reads as 6 under the naive sum (factor 2).
  File: `drafts/v52/static_storage_integration_v10_2026_09_13/denominator_integrity_v10.py:7-13`
  (branch `9802b49`), probe `probe_denom.py` 7/7 PASS.
- `enrich_denominator_rows` + `deduplicate_logical_total` verified on a
  2-archive x2-copy fixture: naive 2400, logical 1200; conflicting
  duplicates, unknown copies, outside-roster archives, and zero/bool/empty
  inputs all reject with `V10ValidationError` (never silently merged).
- No byte-total API exists (`total_bytes`, `bytes_per_vector`, etc. absent;
  only `MAX_SOURCE_BYTES`, a source-read limit, matches "byte"), consistent
  with "V10 offers no byte total". Committed test
  `test_no_byte_total_helpers` asserts the same.
- The five pure helpers are textually IDENTICAL between the standalone
  candidate (`denominator_integrity_v10.py`) and the integrated gate
  (`static_storage_preflight_v10.py`), confirming the "inlined, superseded
  but behaviorally equivalent" claim mechanically rather than by trust.
- SHA pins verified against frozen blobs: V9 gate `a5c98065…` matches
  `b300cbf` bytes; V8 gate `68fbac5b…` matches `35b5058` bytes.

Severity: none on the math. Limit: anchor constants (470 archives,
N=231606) were read, not re-derived from the anchor blob; the 940-copy E2E
and the 18-test denominator suite were receipt-read only (NOT RUN live).

## 2. Copy identities — claim read, refusal path NOT verified (gap)

Contract note A (integration disposition) says the 940-DISTINCT-copy plan
(distinct ids/identities/bytes/digests, same coverage) is legitimate under
the guard's copy inventory, while the same-id duplicate "remains refused
(separate test)". I read the DISTINCT acceptance test
(`test_940_distinct_copies_yield_231606_unique_by_archive`) but did not
locate the same-id refusal test in the sampled files, so that half of the
identity contract is NOT RUN. Severity: LOW for cost correctness (the
denominator layer rejects unknown/conflicting copies regardless), but the
acceptance-status count below does not credit it.

## 3. Physical vs logical byte costs — correctly separated, one caveat

- Marginal vs effective is properly distinguished: the L-088 ceiling is 12
  *marginal* B/vector; the re-fit shared projector serializes to median
  88,886 *effective* B/vector (report table median row, 15-archive re-fit
  on the real corpus). The report states the re-fit is not a recovery of
  the frozen artifact, whose physical serialization was never found.
- Caveat (no severity, framing only): 88,886 is a declared re-fit number on
  15 archives, not a measurement of any frozen production artifact; quoting
  it as "the" physical cost without that qualifier would overclaim. The
  source itself carries the qualifier.

## 4. Concurrency repair — mechanism present, live rerun NOT done

The V9 race (shared `sys.modules` publication across the three-exec chain;
pinned repro: exercised rejections flip to acceptance) is plausibly
addressed by the V10 design (transaction-local scoped `__import__`, whole-
transaction `_CHAIN_LOCK`, frozen `hashlib` capture, private per-
transaction module names). Code read confirms the mechanism, including the
Python-3.14 `dataclass` self-registration refinement and empty
post-consumption `sys.modules` delta. But the 13-test concurrency suite,
the V9 2-failure repro, the 7/7 security matrix (`RECEIPT_V10.json`,
MATRIX-AS-EXPECTED), and the frozen V7/V8/V9 green reruns are all
receipt-read only — thread-timing harnesses plus full pinned-chain
materialization exceeded this slot, so they are NOT RUN, not passes.
Notably the frozen V9 entry points remain vulnerable by design (documented;
callers must migrate), which bounds the repair's effect to V10 entrants.

## 5. Rank certificate — bug reproduced, repair confirmed on probes (5 live)

- BULGU-1 reproduced exactly on isolated copies: POC
  `p=(-100,100,0,10000)`, `q=(-200,200,70000,0)`, J=[1,4]; exact-comparator
  samples give +1/+1/0/-1/-1 (VARIES) while archived v2 certifies
  ISOLATED_TIES/-1. Root causes as diagnosed (budget-skip drops the 7/4
  pre-cut under scaling; exact-hits never crossing/tangent-classified).
  Files: `research_representation_geometry_2026_09_13/repairs/rank_cert/certify_v2.py:263-264,372-375,469-539`.
- v3 confirmed on the same POC: ISOLATED_TIES/VARIES; identical verdicts at
  k=1/7/100/1000 (the exact defect class); L==R and L>R both UNRESOLVED
  (the two extra robustness faults). Probe `probe_rankcert.py` 5/5 PASS.
- BULGU-5 structurally closed: `certify_v3.py` and `cert_validator_v3.py`
  import only `fractions` (verified by grep); POC literals (70000/-200/
  10000) appear nowhere in v3. The literal-counterfeit rejection and the
  684-case coordinator oracle were report-read, NOT rerun.
- Sampled-vs-exhaustive: v3's evidence is finite by construction (frozen bar
  41 adversarial cases, 684 coordinator cases with 4 discarded, 2000-case
  fuzz on one seed/J, 80 vertical + 19 validator checks). The generality
  carrier is the FIX_DISPOSITION proof argument (read, coherent, not
  machine-checked). No general safety proof exists; the different-family
  review REMAINS OPEN. BULGU-2/3/4/6/7/8 and F-01..F-07 are OPEN and the
  package-level REQUEST_CHANGES STANDS per both the repair and coordinator
  documents — the repair closes BULGU-1 (+BULGU-5) only, pending review.

## 6. Obligation count — which prior obligations genuinely closed

| Obligation source | Status after this audit |
|---|---|
| V10 denominator unique-by-archive (severity: would halve B/vec) | Fixed executably per receipts + pure math verified live; NOT accepted (candidate, unmerged, unaudited, unfrozen) |
| V10 concurrency race + ambient-hashlib | Fixed executably per receipts; live rerun NOT done here; NOT accepted |
| BULGU-1 wrong certificate | Repair behaves correctly on POC/scale/robustness probes; coordinator bar passed per verdict (not rerun); NOT accepted, package REQUEST_CHANGES stands |
| BULGU-5 validator trust | Closed by construction (verified live) within the candidate; same acceptance caveat |
| BULGU-2/3/4/6/7/8, F-01..F-07 | OPEN, untouched |
| Governance repair (L-096, pointers, V7 gates, binding-8) | PREPARED, NOT ACCEPTED; L-096 still on unmerged branch; 0 accepted |
| Merge/ratification of any repair | None: rank, v10, gov branches all NOT ancestors of main `59b891e` |

Genuinely closed by acceptance: **0**. Closed executably-but-unaccepted: 5
(listed above). Incidental: the rank branch base is stale (its ledger lacks
L-097, an artifact of branching before it landed — not a deletion with
intent, but consumers of that branch inherit a stale ledger).

## 7. Limits, blockers, out-of-scope

- Counts: 35 ledger rows mechanically counted (`COVERAGE.csv`):
  21 REVIEWED-verified (live re-execution/inspection), 5 SAMPLED
  (read-only evidence, partial verification), 9 NOT RUN (presented as
  such, never as passes).
- Environment: `~/muse-work/ml-python`, `PYTHONDONTWRITEBYTECODE=1`,
  single-thread BLAS; light probes ran directly (each <10 s, well under the
  180 s cap); no heavy job needed `compute.sh`.
- NOT performed: live 940-copy E2E, concurrency/security suites, 684-case
  coordinator oracle rerun, anchor-blob re-derivation, same-id refusal path
  location, projector re-fit re-measurement, any retrieval/model/Task4F1
  work, any security exploit or deserialization probing.
- WHOLE-PROJECT parts outside this role's scope: metric/tie-contract joins
  (01), ITQ-vs-rotation (02), geometry sigma/sign-float theory (03),
  comparator/cascade fairness (04), F1 execution (05), dense-MRL/residual
  lines (06), KV/inverse-memory (07), clean-room portability (09), and
  whole-project coverage/governance adjudication (10). Within my scope, the
  items marked NOT RUN / SAMPLED above remain for a follow-up with a live
  chain environment.

## Evidence index (all under this dir)

`STATUS.md`, `COVERAGE.csv` (35 rows), `evidence.json`,
`probe_denom.py` + `outputs_probe_denom.json` (7/7, exit 0),
`probe_rankcert.py` + `outputs_probe_rankcert.json` (5/5, exit 0),
`src/` (9 branch-file copies: V10 denominator/preflight/concurrency gate +
tests, dispositions, race repro, V8 gate, rank v2/v3 certifiers and verdicts).
