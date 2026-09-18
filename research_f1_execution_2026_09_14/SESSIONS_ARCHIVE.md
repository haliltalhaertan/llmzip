[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Archive of every llmzip session output produced on this machine

**2,265 files across 48 sessions, 58.7 MB.**

A note on the counts, because three different numbers appear in the history of this
archive. The staging scan selected **2,294** paths. Of those, **29 were `.git` pointer
files** (one per session directory that was a git worktree); git refuses to track a
file named `.git`, and it is not session output in any case. Nine directories contained
nothing except that pointer, so they carry no content and do not appear here. What
remains is **2,265 files across 48 sessions**, and a file-by-file comparison of the
working tree against the committed tree shows **zero missing and zero extra**.

## Two wrong commits this archive supersedes

Getting this archive onto the branch took several failed attempts, and two of those
failures were committed and pushed before being detected. Both are left in history --
this project does not rewrite published history -- and both are corrected here:

- **`40c49b4`** - message claims "archive 0 genuine session outputs". The commit is
  empty. The file-collection step had failed silently because a Windows-to-WSL quoting
  layer mangled the file list, and the result was committed without checking.
- **`490716c`** - archived **6 files** while claiming to archive the session corpus. A
  temporary file list had been cleared by WSL between runs, so the tar was empty and
  only a handful of stragglers were picked up.

Root cause of both: committing without verifying the staged count. The staging script
now refuses to proceed if fewer than 2000 files are staged, and the publish
script re-checks before committing.

An earlier classification pass also under-counted, reporting 343 genuine files where
the full scan finds 2294; it scanned only three directory levels. Same rule, wrong depth.

## What this is

`sessions/` holds the raw deliverables of every Muse Code session run against this
programme, one directory per session, byte-for-byte as each session wrote them. Nothing
has been edited, summarised or curated.

## Selection rule, stated so a reader can check it

Most sessions copied repo files into their working directory in order to read them.
Publishing those copies would bloat the archive and hide what was actually produced. So
every candidate file was hashed with `git hash-object` and compared against the blobs
already present in `main` and in this findings branch:

- **12,027 files scanned**, of which **2294 did not match any existing repo blob** and are
  archived here as genuine session output;
- the remaining ~9,700 matched a repo blob and were excluded as copies;
- Collatz work and local infrastructure (virtualenvs, scratch dirs) belong to other
  projects and are **not** published here;
- caches (`*.pkl`, `*.npz`, `*.npy`), bytecode, archives and files above 2 MB are
  excluded; the analyses that consume them record their hashes instead.

Selection, packing and unpacking all run **inside WSL**, writing directly onto
`/mnt/c`. Every attempt that crossed the Windows boundary corrupted something: a raw
tar piped through stdout arrived damaged, base64 likewise, a quoting layer emptied the
file list, Windows' 260-character path limit broke both `git add` and Python's
`extractall` on the deeply nested `campaign-label-*` trees (236-character paths), and
`/tmp` was cleared between runs. `core.longpaths` is now enabled for git.

## Contents

| session | files |
|---|---|
| `campaign-label-fix` | 560 |
| `campaign-label-audit` | 557 |
| `static-integrated` | 114 |
| `geometry-cert-adversarial` | 98 |
| `static-tests` | 97 |
| `static-race` | 93 |
| `static-denom` | 92 |
| `geometry-cert-repair-v3` | 91 |
| `projread-audits` | 75 |
| `projread-ledger` | 75 |
| `projread-task4f1` | 75 |
| `theorybench-perltqa` | 45 |
| `fix-v7-gapfill` | 36 |
| `theorybench-lme` | 26 |
| `theorybench-locomo` | 23 |
| `theorybench-realtalk` | 17 |
| `spectrum` | 14 |
| `fix-exact-rational` | 12 |
| `fix-ledger-record` | 12 |
| `fix-stale-pointers` | 12 |
| `fix_rank_cert` | 11 |
| `audit_rank` | 10 |
| `fix_norm_tests` | 8 |
| `track1-storage-cost` | 8 |
| `track1-storage-framing` | 8 |
| `audit_norm` | 7 |
| `fix_rank_cover` | 7 |
| `track2-e1-audit` | 7 |
| `track2-e1-mechanism` | 7 |
| `math2-sharp-bounds` | 6 |
| `math3-joint-gold-bounds` | 6 |
| `theory-audit-real-geometry` | 6 |
| `ultra-f1-exec` | 6 |
| `audit_meas` | 5 |
| `math-ranking-bounds` | 5 |
| `math2-allocation-optimality` | 5 |
| `roles` | 5 |
| `tails` | 5 |
| `ties` | 5 |
| `fix_norm_math` | 4 |
| `math-bit-allocation` | 4 |
| `math-sign-mechanism` | 4 |
| `math3-all-n-ranking` | 4 |
| `math4-norm-aware-sign-bounds` | 4 |
| `math4-rank-crossing-certificates` | 4 |
| `theory-audit-locomo-provenance` | 4 |
| `theory-audit-mapping` | 4 |
| `audit_rep` | 2 |
| `deep-branch-ledger` | 1 |
| `deep-contradictions` | 1 |
| `deep-t4f1-audits` | 1 |
| `deep-v8-lineage` | 1 |
| `gap-t4f0-evidence` | 1 |
| `gap-v1-v50-history` | 1 |
| `ultra-commonmode` | 1 |
| `ultra-f1-repair` | 1 |
| `ultra-perltqa-mechanism` | 1 |

The larger blocks: `campaign-label-*` are the two sides of the labelling campaign
(audit and fix); `static-*` and `geometry-cert-*` are the static-layer and
geometry-certificate work; `projread-*` are the project-history reads; `theorybench-*`
are the four benchmark theory tests; `math*`, `math2-*`, `math3-*`, `math4-*` are the
mathematics rounds; `spectrum`, `tails`, `ties`, `roles` are the four measurement probes
whose results refuted earlier claims (spectral exponent, kurtosis, tie rate, speaker
role); `track1-*` and `track2-*` are the storage-accounting and E1-mechanism tracks.

## Status of this material

**Unreviewed.** These are session outputs, not verified results. Several contain claims
that later measurement refuted -- which is exactly why they are kept: this project's own
rule is that a superseded artifact is preserved together with its correction rather than
deleted. Where a claim was checked, the check lives in the topic documents
(`ROUND2_RECOVERED.md`, `SESSION2_FINDINGS.md`, `LITERATURE_AND_XIAO.md`,
`AUDIT_RESPONSE.md`, `ERRATA_COORDINATOR.md`) and those supersede anything here.

Every archived file is listed in `MANIFEST.sha256` with its SHA-256, computed from the
committed git blobs, so the archive can be verified independently of this description.
