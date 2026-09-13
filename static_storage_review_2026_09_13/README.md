# Static-storage repair and disclosure archive

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This is a preservation/review surface, NOT an integrated release or measurement authorization. Main and frozen V7/V8/V9 artifacts are unchanged. LongMemEval-only; Task4F1 remains blocked.

## Completed integration update

The later completed integration is commit `9802b49fe7b662f873f985c39790d4f6ca16523d` on [findings/static-integrated-v10-2026-09-13](https://github.com/haliltalhaertan/llmzip/tree/findings/static-integrated-v10-2026-09-13). Public entrypoint: `drafts/v52/static_storage_integration_v10_2026_09_13/static_storage_preflight_v10.py:preflight_longmemeval_v10`.

Coordinator reran 12/12 integrated tests and 7/7 adversarial E2E tests successfully. This includes the real valid-plan path with 940 distinct copies yielding 231606 unique logical vectors. Full command/stdout/stderr receipts: `INTEGRATION_COORDINATOR_VERIFICATION.json`; worker final report: `INTEGRATION_FINAL_MUSE.log`. This remains a tested repair candidate, not independent certification or measurement authorization. The prior live snapshot below is retained as historical evidence and is superseded by this commit.

## Completed candidate commits (separate branches)

| Candidate | Commit | GitHub branch |
|---|---|---|
| Unique-by-archive denominator | `5ff0ab0368b1d1515b5214b7952757aeb03651c3` | [findings/static-denominator-v10-2026-09-13](https://github.com/haliltalhaertan/llmzip/tree/findings/static-denominator-v10-2026-09-13) |
| Scoped loader and concurrency protection | `35b50581b566ff9f5dfbcfe5d7035f6f098d192e` | [findings/static-concurrency-v10-2026-09-13](https://github.com/haliltalhaertan/llmzip/tree/findings/static-concurrency-v10-2026-09-13) |
| Adversarial E2E tests and mutation variants | `6e764b1207b565b16beb460151a4b955b69a94f0` | [findings/static-security-tests-2026-09-13](https://github.com/haliltalhaertan/llmzip/tree/findings/static-security-tests-2026-09-13) |
| Campaign label completion | `c09d6eae2c75ea11488eafd99a43d534f407f6a9` | Ancestor of this campaign branch |

Candidate commits are deliberately separate: their V10 report/manifest names overlap and they are NOT interchangeable integrated implementations.

## Coordinator verification already executed

- Denominator component: 18/18 tests passed. Distinct-copy logical aggregation works in component tests; original candidate lacked full valid-plan E2E coverage.
- Concurrency component: 13/13 tests passed; same test suite directed at V9 failed exactly two interference checks. Timing is instrumented using test hooks; do not imply an uninstrumented production reproduction.
- Security suite: intentionally retained-snapshot and unsafe-loader variants pass all seven old V9 tests, but new E2E tests catch their targeted defects. Ambient hashlib mutation is a same-process trust-model issue, not an ordinary external-file attacker.
- Coordinator initially observed an extra V9 concurrency failure; five subsequent complete suite runs did not reproduce it. Raw subsequent outputs are in `evidence/static-tests-coordinator-reruns.json`. The first aggregate observation remains a coordinator observation, not a saved full traceback.
- Disclosure completion: 63/63 in-scope narrative copies pass; 34 additive banner prefixes preserve all original trailing bytes exactly. Campaign manifest independently verified: 581/581 valid hashes, complete unique coverage.

## Evidence and in-progress integration

`evidence/` contains six worker output logs, six worker prompts, coordinator reruns, and the integration snapshot inventory. Logs are worker reports, not automatically certified claims. Partial logs can contain retries only.

`evidence/integration_work_in_progress/` is a NON-ATOMIC COPY of a live worker's two task directories, captured at the time in `evidence/SNAPSHOT_INVENTORY.json`. It includes staged/untracked work present at capture, not a completed or tested integrated release. Original embedded candidate receipts describe their original candidates; they do NOT certify the evolving snapshot. Some paths/hashes may be inconsistent across live capture. Future worker changes are not included automatically.

`MANIFEST.sha256` verifies the bytes of this archival copy only. It is not a scientific approval or claim that embedded historical manifests still match edited live files.

## Disclosure provenance caveat

Distribution banners change bytes. Five historical manifest containers reference labeled copies whose original hashes therefore no longer match. They were deliberately not rehashed to conceal this. Original campaign bytes remain accessible with `git show 84e75cc:<path>`; see `campaign_2026_09_13/disclosure_fix/DISCLOSURE_CORRECTION_REPORT.md` for affected paths.

## Earlier campaign / heavy data

The existing `campaign_2026_09_13/` review surface remains on this branch. Heavy datasets/caches/binary packages remain at the previously uploaded [Drive backup](https://drive.google.com/drive/folders/1-8DYki9uXVPIVsKBAL2xCzw_LeUJH0q4), not duplicated into Git. Their location and manifests are documented in the campaign README. This archive does not assert that virtual environments, credentials or every transient machine file belong in Git.
