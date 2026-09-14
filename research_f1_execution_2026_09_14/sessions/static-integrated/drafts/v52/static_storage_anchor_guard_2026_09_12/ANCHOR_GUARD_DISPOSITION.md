# V52 archive-anchor guard — disposition

Status: **REPAIR CANDIDATE / NOT AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION.**

Closes the two **scientific** findings of the independent V3 audit
(`audit/v52-static-storage-plan-prep-v3-independent-2026-09-12` @ `b06247df2124edc6953aacf0f7eb69eed99ac1e0`,
with `CORRECTION_01.md`): AUD-001 and AUD-008. The adapter-boundary and schema findings
are repaired separately on `fix/v52-static-storage-plan-prep-v4-2026-09-12`.

**Additive.** `measurement_plan_guard.py` is not modified and its bytes are not
rewritten. This module runs after it.

## The finding, restated from the exploit

The audit showed a plan whose declared archive sizes were inflated passing both existing
guards and collapsing the published headline `mean_i(C_i/N_i)` from 15.0 to 9e-08 with
identical `C_i`. The chain was internally consistent and externally unanchored: probe `N`
was validated only as an arbitrary integer, nothing tied it to the archive's `N_i`, and
nothing tied `N_i` to any frozen source.

Demonstrated closed, same shape, one artifact of 200 bytes:

```
honest                       ACCEPTED   D_k=10           effective=2.000e+01 B/vector
the audit's diluted plan     REFUSED    archive a1: declared N_i 1000000000 disagrees
                                        with the frozen anchor
```

## How it closes, without a schema change

The plan's exact-field lists are unchanged, so nothing new can be mis-declared. Every
role this guard needs is **derived** from values schema-1 already carries:

1. **`load_anchor`** authenticates a frozen archive-size table by digest and reads it. It
   takes bytes, not a path, so the caller authenticates what it read and no locator is
   reopened after hashing. Duplicate ids, non-integer, zero and negative sizes, a missing
   column and an empty table are all refusals. `ArchiveAnchor.reverify()` re-hashes on
   use, for the reason `CORRECTION_01.md` recorded about frozen containers.
2. **`verify_archive_sizes`** requires every declared `N_i` to equal the anchored value
   and refuses any archive absent from the anchor. An unanchored size cannot be used.
3. **`classify_probes`** derives the role: `FULL_SIZE` when `N` equals the anchored
   `N_i`, `DIAGNOSTIC` otherwise. The staircase points stay legal; they simply describe
   no real archive.
4. **`verify_full_size_coverage`** requires exactly one full-size probe per archive,
   which is the panel the V3 specification already declares as `(N_i, q=1)` for every
   archive and which no guard enforced.
5. **`authoritative_denominators`** returns ONE denominator per physical copy: the count
   of the full-size BEFORE population, the vectors that really share the copy in the real
   archive. Diagnostic and AFTER populations are ineligible, so the largest-candidate
   selection AUD-008 describes cannot be made. Zero, missing and duplicate candidates are
   refusals, not defaults.

## Evidence

`test_archive_anchor_guard.py`, 21 tests, all passing on Python 3.11.15. Beyond the
exploit they cover: digest mismatch and post-load swap; duplicate, non-integer, zero,
negative and blank sizes; missing column and empty table; inflated, deflated and
wrongly-typed `N_i`; an archive absent from the anchor; an archive with no full-size
probe and one with two; a copy bound to a 10^9 diagnostic population, which is ignored
rather than chosen; a copy with no eligible population and one with two; a zero
denominator; and that malformed plans raise only `AnchorValidationError` and never a
`KeyError` or `TypeError`.

The last test reads the committed metric table
`docs/v52/task4c2/V52_T4C2_feature_geometry.csv` at `origin/main`, confirms 470 archive
rows load, and shows a true size accepted and the same size multiplied by a thousand
refused. That column is archive cardinality, not a retrieval outcome.

## What this does not do

It does not verify that the frozen table is itself correct, only that the plan cannot
depart from it. Choosing which table anchors which benchmark stays a declared decision:
the LongMemEval sizes live in the table above, and the LoCoMo sizes are recorded
elsewhere in the inventory, so a LoCoMo plan needs its own digest-bound anchor and this
guard will refuse every LoCoMo archive until one is supplied. That refusal is the
intended behaviour, not a gap.

Not: storage measured, `<=12` proven, actual plan approved, real adapter ready, retrieval
authorized, Task4F1 authorized, this package audited. It needs an independent cold-start
audit before anything is frozen against it.

Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. No
corpus, query, gold or outcome was opened; nothing was fitted, measured, scored or
sealed; `main`, the ledger and state are untouched and no merge was made.
