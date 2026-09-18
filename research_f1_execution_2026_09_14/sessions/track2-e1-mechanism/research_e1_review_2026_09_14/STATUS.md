[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — E1 review (track2-e1-mechanism)

Work is PREPARED, NOT ACCEPTED. Nothing here is sealed, ratified, or closed.
This namespace (`research_e1_review_2026_09_14/`) contains only NEW files. No existing file has been modified.

## Task
Read the ten E1 remote branches (read-only via `git show origin/<branch>:<path>`, no checkout),
map them, extract mechanism claims, cross-check numbers, recommend one next experiment.

## Progress log (receipts — append as I go)
- [x] 00:00 — Confirmed worktree state: branch `muse/track2-e1-mechanism` at main `5ec3db60` (VERIFIED: `git log -1`). Namespace dir does not yet exist; creating it with this file.
- [x] Diffs: `git diff --name-only 5ec3db60 origin/<branch>` for all 10 refs (551/554/560/560/593/593/599/604/609/601).
- [x] Read bridge/V1-disposition/V2-receipt/checkpoint/LME-secondary/recovery/R2/audits/SPEC_V2 in full (summaries only, no sealed-outcome mining).
- [x] Deliver E1_MAP.md (10 refs = 8 commits; twin pairs byte-identical — VERIFIED).
- [x] Deliver MECHANISM_FINDINGS.md (3 supported / 7 refuted-nulled / 3 restated).
- [x] Deliver NUMBERS_CROSSCHECK.md (gates agree; LoCoMo +6.82838013pp vs ~12pp left UNRESOLVED).
- [x] Deliver WHAT_TO_DO_NEXT.md (frozen fifth-benchmark E1-C1 + 4 falsifiers; R2 rerun as gate).
- [x] Deliver REPORT.md + commit namespace to own branch.
- [x] Content commit `e748732eca253ff5a58228cb6ab64a010016066f` on `muse/track2-e1-mechanism` (VERIFIED: `git log -1`). No push, main untouched, no checkout performed (all reads via `git show origin/<branch>:<path>`).

## Constraints honored
- No push, no touching main, no checkout of another branch, no network/fetch/installs.
- Task4F1 SEAL: no run/finalize modes, no auth key, no real retrieval IDs/distances/recall/metrics mining; BEAM corpus not fetched.
- Purely additive: only new files under `research_e1_review_2026_09_14/`.
- Identity for commit (if needed): from `git log -1 --format='%an <%ae>' 5ec3db60` → `Codex <codex@openai.com>`; will pass via `-c`, never change global config.
- Every assertion carries a locator; VERIFIED / CLAIM / RELAYED labels; no invented numbers (UNAVAILABLE-UNDER-SEAL where sealed).

## Assumption that would most damage my conclusion
That the E1 branches' own summary documents faithfully describe their code and figures. I test it by
spot-checking at least one quoted figure or claim per branch against a second file in the same branch
(e.g. a contract or analysis doc), and I report where only a single source exists as single-source/UNCONFIRMED.
