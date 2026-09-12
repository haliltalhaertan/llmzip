# Drive upload confirmation — additive to DRIVE_RECEIPT.md

`DRIVE_RECEIPT.md` was written while the Google Drive connector was unreachable and
states that nothing was uploaded. That statement was true when written and is now
superseded. Its bytes are not rewritten; this file supersedes it.

The connector became reachable later in the same session and the package was uploaded.

Folder: `V52_STATIC_STORAGE_PLAN_PREP_V3_INDEPENDENT_AUDIT_2026-09-12`
Folder id: `18dYnNl3w08QSod_R23bULF9Dx3JpcWzh`
Parent: `LLM_TOKEN_ZIP_RESEARCH_MASTER`, `1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv`

| File | Drive id | Drive fileSize | local bytes |
|---|---|---:|---:|
| INDEPENDENT_V3_AUDIT_REPORT.md | 1NFmCVffNY6orAHOOaKqfQv7J5dFLu9Ll | 9543 | 9543 |
| FINDINGS.json | 1eR3zyz66DYUhIbJ6V7oAebSU4B6YIWBb | 2634 | 2634 |
| CLOSURE_MATRIX.json | 1-m8v0SXcAlwkXnW1Q5G9JstK6cq0OD7J | 988 | 988 |
| EXECUTION_LOG.txt | 1IlFwDsgVpLEpY-fhhDeLKt2URtwlkaPa | 1328 | 1328 |
| HASHES.json | 1yYj-REcQKuBoVZtBm4PmR_hA7e0TFT_Q | 837 | 837 |
| HASHES.json.sha256 | 1KmsHEiTrHCmrbQ4BGHwBAkK3eC-sCHLZ | 78 | 78 |
| DRIVE_RECEIPT.md | 1_ZYvsPmu7KzeyS9QbH8tcykD44HLVcmu | 735 | 735 |
| EXECUTION_RAW.txt | 1fPTOyBbQyWhYbntW81GGqDIkSjJFnoQv | 2172 | 2172 |
| adversarial_probes.py | 1O1Yd0r0ihQBLaroJFUo5MEmrbVIZOw-e | 4093 | 4093 |

All nine were uploaded with conversion to Google types disabled, and the folder was
listed back after upload. Every reported Drive `fileSize` equals the local byte length.

## One upload error, recorded rather than smoothed

The first upload of `EXECUTION_RAW.txt` was sent as escaped text and arrived at 2202
bytes against a local 2172 - thirty bytes of HTML entity escaping across ten `<--`
markers. It was trashed, not overwritten, and re-uploaded from base64 at 2172 bytes.
The trashed copy's id was `1CaKGQg68KaIEKn_vtU1PKYyOr47QtnLi`. Equal size is a
necessary check and not a full digest comparison; the Drive copy remains a readable
mirror and the Git bytes on this branch remain the byte authority.

Nothing else changed. `main`, the ledger and state are untouched, no merge was made,
and Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN.
