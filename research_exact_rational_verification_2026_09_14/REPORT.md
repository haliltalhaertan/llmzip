[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Report — binding-8 exact-rational pilot (PREPARED, NOT ACCEPTED)

## What I produced (all inside `research_exact_rational_verification_2026_09_14/`)

- `STATUS.md` — plan, branch/base record, seal-compliance log.
- `BINDING8_READING.md` — binding 8 and the §6 `D_t` rule quoted verbatim with locators,
  plus a six-point restatement of what satisfies them and the frozen tier denominators
  355 / 629 / 553 / 175 with sources.
- `vendored/` — byte-exact copies (sha256-verified identical) of
  `tools/t4f1_exact_rational_outcome_analysis.py` (`bda67f03…`) and its branch test
  (`55a83165…`) from `origin/impl/t4f1-exact-rational-analysis-2026-09-04` (tip `4e13ac8`),
  plus `PROVENANCE.md` (source refs, fail-closed `main()` gate description).
- `test_exact_rational.py` + `ADVERSARIAL_TESTS.md` + `evidence/results.json` (+ `receipts.txt`) —
  31-check adversarial suite on self-authored synthetic inputs with `Fraction` oracle and a
  float-based negative control.
- `DISPOSITION.md` — verdict and what remains before discharge.
- This `REPORT.md`.

## What I verified (all VERIFIED from bytes I read/ran; see `evidence/receipts.txt`)

- The implementation decides every `D_t` sign in exact `Fraction` arithmetic with no tolerance:
  **31/31** adversarial checks pass, including tiny-positive `1/10^400` staying positive,
  exact-zero tiers classifying as ties on the `≤ 0` side (with the Full→Heterogeneous flip),
  order-invariant means, discrete-ID input reconstruction, and denominator divisibility.
- The suite is discriminating, not flattering: the deliberately float-based classifier gives
  the wrong answer on **3 cases** (suite exits nonzero unless ≥3 are exposed).
- Second route: the branch's own 10 unmodified outcome-free controls pass against the same bytes.
- `main()` is fail-closed for synthetic use (demands sealed cohort sha + 96 archive CSVs); it
  was never invoked. No seal line was crossed (receipts above).

## What I could NOT do and why

- No real-data or authorization-path execution (Task4F1 seal; BEAM corpus absent and unfetched).
- No discharge of binding 8: I am not an independent auditor, the code is unfrozen/unmerged,
  and only the Head Researcher writes the ledger. Verdict: **SATISFIED on synthetic inputs
  only** — freezing, independent audit, and merge remain (see `DISPOSITION.md`).
- `source_section_sha256` left as CLAIM (extraction rule belongs to the seal verifier).

## Commit

Namespace committed to own branch `muse/fix-exact-rational` only (no push, `main` untouched,
no existing file modified). Commit sha: recorded in the stdout summary of this session.
