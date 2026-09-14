[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Archive of every llmzip session output produced locally

## What this is

`sessions/` holds the raw deliverables of every Muse Code session run against this
programme that had not already been published, one directory per session, byte-for-byte
as the session wrote them. Nothing here has been edited, summarised or curated.

## Selection rule, stated so a reader can check it

Each session ran in its own working directory, and most sessions first copied repo
files in to read them. Publishing those copies would bloat the archive and obscure what
was actually produced. So every file was hashed with `git hash-object` and compared
against the blobs already present in `main` and in this findings branch:

- **7,134 files matched an existing repo blob** and were excluded as copies;
- **343 files did not match** and are genuine session output;
- **447 files belong to a different project** (Collatz work) or to local
  infrastructure (virtualenvs, scratch) and are deliberately NOT published here.

Caches (`*.pkl`, `*.npz`), bytecode and files above 2 MB are excluded; the analyses that
consume them record their hashes instead.

## What is in here

Sessions from earlier rounds of this programme, recovered from the local machine:

- `theorybench-*` - the four benchmark theory-test sessions (LongMemEval, PerLTQA,
  LoCoMo, REALTALK), the largest single block at 111 files.
- `math*`, `math2-*`, `math3-*`, `math4-*` - the mathematics rounds: bit allocation,
  ranking bounds, allocation optimality, sharp bounds, all-N ranking, joint gold
  bounds, norm-aware sign bounds, rank-crossing certificates.
- `theory-audit-*` - audits of the theory work: benchmark mapping, LoCoMo provenance,
  real-geometry check.
- `fix-*`, `fix_*`, `audit_*` - repair and audit sessions on the measurement layer
  (stale pointers, ledger records, exact rationals, v7 gap-fill, rank certificates,
  norm math and tests).
- `track1-*`, `track2-*` - the storage-accounting and E1-mechanism tracks.
- `deep-*`, `gap-*`, `projread-*`, `static-*`, `ultra-*`, `campaign-label-*`,
  `geometry-cert-*` - project-history reads, gap analyses, static-layer work and the
  labelling campaign.
- `spectrum`, `tails`, `ties`, `roles` - the four measurement probes whose results
  refuted earlier claims (the spectral exponent, the kurtosis claim, the tie-rate
  claim, the speaker-role claim).

## Status of this material

**Unreviewed.** These are session outputs, not verified results. Several contain claims
that later measurement refuted - that is precisely why they are kept: the programme's
own rule is that a superseded artifact is preserved with its correction rather than
deleted. Where a session's claim was checked, the check lives in the topic documents
(`ROUND2_RECOVERED.md`, `SESSION2_FINDINGS.md`, `LITERATURE_AND_XIAO.md`,
`AUDIT_RESPONSE.md`) and those supersede anything here.

Every file in this archive is listed in `MANIFEST.sha256` with its SHA-256, and the
manifest is computed from the committed git blobs, so a reader can verify the archive
independently of this description.
