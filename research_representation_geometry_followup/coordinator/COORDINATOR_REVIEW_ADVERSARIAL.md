# Coordinator review — adversarial soundness suite (BULGU-1 / BULGU-5 acceptance bar)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Worker: Muse session `geometry-cert-adversarial`, branch `muse/geometry-cert-adversarial`, local commit `e3f30d2` on base `75b7e05`. No push. Coordinator verification run independently on the same worktree, plus a separate stdlib script that does not import any worker module: `coord_check_adversarial.py` → `COORDINATOR_ADVERSARIAL_CHECK.json`.

## Verified by coordinator (re-executed, not taken on report)

- Published package byte-identical: `git diff 75b7e05 e3f30d2 -- research_representation_geometry_2026_09_13` is EMPTY; `sha256sum -c MANIFEST.sha256` 73/73 OK. Working tree carries only the new additive dir.
- Corpus determinism: regenerated `cases.json` with `build_corpus.py`, byte-compared against the committed file → identical. Expectations therefore cannot have been tuned after seeing outputs.
- Suite vs archived v2 reproduced by me: 41 cases, **5 safety FAIL** (`poc_K100`, `poc_K1000`, `poc_reversed_K100`, `invalidJ_empty`, `invalidJ_inverted`), runner exit 1 — matches the worker's `results_v2.json`.
- **Independent truth check (strongest evidence): I re-derived all 157 frozen truth points with my own comparator (sign-aware cross-multiplication, written from the score definition, importing no worker code). 157/157 agree, 0 mismatches.** I also re-derived the `plus`/`minus` flags that safety gate G1 depends on — no disagreement. The frozen oracle the whole suite rests on is not self-certified.
- Worker's own `test_soundness.py`: 12/12 PASS on my rerun.

## Canary probes I added (not part of the worker's tests)

| Fake target | Result | Reading |
|---|---|---|
| always `STRICT/+1` | exit 1, **32/41 safety FAIL** | confident-liar rejected |
| always `UNRESOLVED` | exit 0, safety 0 FAIL, **completeness 14 FAIL** | honest ignorance passes safety but is explicitly useless — the two bars are genuinely separated |
| v2 wrapped, status renamed `SAFE_ISOLATED` | exit 1, 15 safety FAIL | unknown status names are not silently trusted |

The third probe confirms the documented limitation from the other side: a *repaired* certifier introducing new status vocabulary will be flagged strict-unknown. That is fail-closed (safe) but it means **v3 must either reuse the known status vocabulary or the spec must be extended deliberately, in the open, before v3 is run** — not after seeing v3's score.

## Scope and limits (unchanged, restated)

- Same model family as the package authors and as the repair session. Partial independence only. **This is not the different-family independent review that remains open.**
- Finite corpus (41 cases incl. 24 seeded fuzz rows). No general safety claim follows from passing it.
- Runner loads targets in-process: no subprocess isolation or timeout.
- BULGU-2/3/4/6/7/8 and measurement findings F-01..F-07 remain **OPEN and untouched**. This suite addresses only the BULGU-1 blocker and the BULGU-5 validator hole, and additionally surfaced two invalid-J robustness faults in v2 (`L==R` certified `STRICT/0` against point truth `-1`; `L>R` silently certified) that the original audit did not list.
- `repro_bulgu1.py` exiting 0 documents that the BUG EXISTS. It is not a repair-success signal.

## Disposition

Acceptance bar ACCEPTED as the gate for the v3 candidate, with one standing condition: **`cases.json` and `validate.py` are frozen from now on.** If running v3 reveals the bar is wrong, the fix is a new, separately reviewed case set — never an edit that makes the candidate pass.

`REQUEST_CHANGES` on the published repairs package **stands**. The candidate `certify_v3.py` has not yet been run through this suite.
