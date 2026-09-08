# Expected correction identities: source-only preparation

Base: 33da318486dda749ce464fed64c35fb366f494ff. Additive; old packages unchanged.
This package extracts expected identities, not actual correction data. It grants
no ingestion, outcome, pilot, sealing, HMAC or execution permission.

`verify_inventory.py` reads one raw Git code blob, verifies its SHA256, and uses
AST literal extraction without importing/executing the historical producer.
It reconstructs the full twenty-entry identity-list hash before deriving the ten
errors_conv entries. The ten-only hash is distinct from the historical twenty-file
hash. Neither operation verifies the actual twenty or ten data files.

`EXPECTED_CORRECTION_IDENTITIES.json` contains ten filenames, sizes and hashes.
Producer Git blob: 6700454915176854a55b0b5cf6ffe922a22e35f2.
Expected subset identity: 7df45317f0cb3029fc8cb008d8480ee5c8e61ac01dd0d77bc1cfcd6a3eb7224a.

Verification: four unittest methods passed under approved Python3.13.15 using -B:
recorded inventory equals extracted source, changed source bytes rejected,
wrong full inventory rejected, wrong subset inventory rejected. These stdlib-only
checks do not replay model computations or independently audit the experiment.

Run: python -B drafts/v52/membership_source_identity_v1_2026_09_08/test_inventory.py

Raw normalization and duplicate correction-ID policy remain unapproved. Historical
silent skips, coercions and last-write-wins behavior must not be silently inherited
as a strict parser. No actual correction files were opened, parsed or downloaded.
The next proposed boundary is fail-closed parsing with explicit disposition for
unsupported values or duplicate IDs, not silent repair or cohort reselection.

## Native anchor clarification (not implementation authorization)

A fresh-context read-only subagent traced accepted sources; the parent checked the
controlling passages. Acceptance 9b4af5949c4dc0e5054f8f522f1952ec47513f8f,
docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md lines18-33,
assigns controls to draft sections1-7,10-13. Draft commit
56c294162412482ca85e77ea991a20eb22f65dac, section11, separately requires Native
reproduction at1e-12 and persistence of per-question records. It does not require
historical per-question anchors. R2 commit16019724564b5ac8db4a4d2d8bb08f98feb45c09
section6 preserves that control suite.

Historical LoCoMo code at692f599e and LME code at0c9916bd check aggregate Native
means. The v1/v2 candidate's additional historical per-question requirement is not
a preregistration mandate. This qualifies the prior README's framing as a new
granularity choice: aggregate alignment is the conservative interpretation, but
NOT evidence that any particular historical scalar is suitable for this cohort.

Before implementation, bind the exact artifact and establish matching question
coverage, corrected gold, representation, priorities and aggregation semantics.
In particular the old LoCoMo producer contains an expected1540 count; this study's
accepted cohort is1535. Do not reuse its scalar merely because that code contains
one. No historical result artifact was accessed, no anchor value was extracted
into this package, and no new anchor was manufactured. Existing synthetic v2
per-question fixtures remain unchanged, pending a separate aligned candidate.

This is a parent-authored preparation record, not independent acceptance. Main,
CURRENT_STATE and the continuity ledger remain untouched.
