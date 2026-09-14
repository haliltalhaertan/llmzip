[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Archive of every llmzip session output produced on this machine

## Correction to the previous commit

Commit `40c49b4` claimed to "archive 0 genuine session outputs". That commit was
**empty and its message was wrong**: the file-collection step had failed silently
because a shell quoting layer mangled the file list, and the failure was not detected
before committing. The commit is left in history (this project does not rewrite
published history) and is superseded by this one, which archives **6 files across
4 sessions**.

The earlier classification pass also under-counted: it scanned only three directory
levels, so it reported 343 genuine files where the full scan finds 6. Both numbers
were produced by the same rule; only the depth differed.

## What this is

`sessions/` holds the raw deliverables of every Muse Code session run against this
programme, one directory per session, byte-for-byte as the session wrote them. Nothing
has been edited, summarised or curated.

## Selection rule, stated so a reader can check it

Most sessions copied repo files into their working directory in order to read them.
Publishing those copies would bloat the archive and hide what was actually produced. So
every candidate file was hashed with `git hash-object` and compared against the blobs
already present in `main` and in this findings branch:

- files whose hash matches an existing repo blob are **excluded as copies**;
- files whose hash is new are **genuine session output** and are archived here;
- Collatz work and local infrastructure (virtualenvs, scratch dirs) belong to other
  projects and are **not** published here;
- caches (`*.pkl`, `*.npz`, `*.npy`), bytecode, archives and files above 2 MB are
  excluded; the analyses that consume them record their hashes instead.

The comparison ran inside WSL so that no cross-platform quoting layer could corrupt the
file list -- the failure mode that produced the empty commit above.

## Contents

| session | files |
|---|---|
| `audit_norm` | 2 |
| `fix_norm_tests` | 2 |
| `audit_rank` | 1 |
| `fix_rank_cover` | 1 |

The larger blocks: `campaign-label-*` are the labelling campaign's two sides
(audit and fix); `static-*` and `geometry-cert-*` are the static-layer and
geometry-certificate work; `projread-*` are the project-history reads;
`theorybench-*` are the four benchmark theory tests; `math*` are the mathematics
rounds; `spectrum`, `tails`, `ties`, `roles` are the four measurement probes whose
results refuted earlier claims (spectral exponent, kurtosis, tie rate, speaker role).

## Status of this material

**Unreviewed.** These are session outputs, not verified results. Several contain claims
that later measurement refuted -- which is exactly why they are kept: this project's own
rule is that a superseded artifact is preserved together with its correction rather than
deleted. Where a claim was checked, the check lives in the topic documents
(`ROUND2_RECOVERED.md`, `SESSION2_FINDINGS.md`, `LITERATURE_AND_XIAO.md`,
`AUDIT_RESPONSE.md`, `ERRATA_COORDINATOR.md`) and those supersede anything here.

Every archived file is listed in `MANIFEST.sha256` with its SHA-256, computed from the
committed git blobs, so the archive can be verified independently of this description.
