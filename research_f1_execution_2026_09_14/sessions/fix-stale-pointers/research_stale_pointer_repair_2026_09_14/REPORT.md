[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# REPORT — stale-pointer repair package (PREPARED, NOT ACCEPTED)

## What I produced (all inside `research_stale_pointer_repair_2026_09_14/`, additive only)

- `STATUS.md` — work plan and seal-boundary declaration.
- `STALENESS_EVIDENCE.md` — all six tasked items proven stale from bytes with
  locators + superseding locators, plus 7 further superseded statements found
  by sweeping top-level docs and `docs/` (protocol V3-pending rule, manifest
  snapshot date + V3-pending line, pre-seal RESEARCH_PROGRAM_STATUS lines,
  T4C2 "next gate", manifest's "current ledger" self-description).
- `PROPOSED_CORRECTIONS.md` — minimal before/after blocks C1–C8 (dated
  "superseded by" insertions, no history rewritten); no target carries a
  `.sha256` sidecar, so no erratum detour was needed (additive-only rule cited
  from `docs/CONTINUITY_LEDGER.md:1249`).
- `SIDECAR_AND_ANCHOR_RECHECK.md` — integrity re-verified over raw blobs:
  20/20 sidecars OK, 32/32 CURRENT_STATE anchors OK, geometry MANIFEST 73/73 OK,
  zero mismatches. (Receipts: `sidecar_recheck_receipt.txt`,
  `anchor_recheck_receipt.txt`, `geometry_manifest_receipt.txt`.)
- `CAVEAT_PROPAGATION.md` — 8 quoters tabulated: caveat travels with the audit
  report + T4C3 probe prompt (+ prompts commission it, manifest is data);
  MISSING from `docs/PROJECT_STATUS_2026-08-27.md:21`, PARTIAL in the compute
  report; exact insertion sentences proposed. Arithmetic closes: S−Fc =
  10.037944→+10.037943 and S−F0 = 10.186880→+10.1869 are different
  subtrahends, both correct (receipt `caveat_arithmetic_receipt.txt`).
- `PROPOSED_LEDGER_ENTRY.md` — draft entry for the sole writer; not appended
  to the real ledger.

## What I verified (each with locator; VERIFIED = I read/ran the bytes)

V3 verdict quote (`origin/…v3…:…REPORT.md:11`), L-003 closure
(`docs/CONTINUITY_LEDGER.md:59-73`), L-095 date 2026-09-12 (lines 2003–2027),
RESEARCH_PROGRAM_STATUS last commit 2026-09-03 (`6ed812f`), its pre-seal lines
24–25, Seal V3 2026-09-04 (`START_HERE_V52_4F1.md:39`), later state anchors
(`git branch -r`), V6 BLOCKED verdict (`origin/…v6…:…REPORT.md:3`,
commit `c88455b`), CRLF method note (handover lines 142–155), and all hash
rechecks above.

## What I could NOT do and why

- Touch the live documents, the real ledger, or any sealed/frozen artifact:
  forbidden by the task (purely additive output) — corrections are proposals only.
- Anything crossing Task4F1 SEAL: no run/finalize, no outcome metrics, no
  corpus (absent, not fetched) — stopped at the boundary by design; the
  caveat arithmetic uses only already-published frozen T4C2 percentages, not
  BEAM outcomes.
- `git branch -r` shows 137 remote branches, not 133 — noted, no action taken.
- Geometry MANIFEST verification is against `origin/findings/…` blobs (that
  namespace is not on main); main's own base is fully green.

## Commit

Branch: `muse/fix-stale-pointers` (own branch; `main` untouched, nothing
pushed, no checkout of other branches). Commit sha: <filled in after commit —
see stdout summary>.
