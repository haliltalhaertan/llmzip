# Open note — the LoCoMo cohort selection rule, and what is and is not claimed

## Two claims, kept apart

**Claim 1 — the mapping is verified.** Every one of the 1535 bound question ids resolves to a real
question sitting in the conversation its id names, in the corpus whose bytes were verified first. As a
permutation problem the raw file's own structure leaves exactly one consistent assignment of the ten
cohort index sets to the ten conversations, out of 3,628,800, and it is the identity. *(L-074,
`DATA_IDENTITY_REPORT_2026-09-08.md`.)*

**Claim 2 — the cohort selection rationale is reproduced.** Different question: *why* those 1535 of the
1986 questions in the file, and not others. It was **not** established in the data-identity task; one
position was left unexplained. It is now established from **committed producer code, read only**, and
this note records that. **Claim 2 does not strengthen Claim 1 and is not a substitute for it.**

## What the earlier residual was

The data-identity task reconstructed the rule as `category != 5 AND evidence non-empty`. That
reproduces 9 of the 10 conversations exactly and left **one** unexplained exclusion: conversation 6,
raw question index 11 — a category-2 question whose single evidence id resolves to a real dialogue
turn, and which is nevertheless absent from the cohort. I did not guess a rule to cover it. A narrower
hypothesis I tried (evidence pointing only at image turns) was **wrong** and was reported as wrong.

## What the committed code says — read-only, no new corpus scan, no experiment

Source: `research/v52/locomo_sign_mechanism_replication.py` on branch
`codex/v52-locomo-reproduction-audit-2026-09-07` @ `692f599eedeb7e7a649443f24ff507e8c4d1c17d` — the
frozen base module that the LoCoMo coordinate-scale shard imports.

The rule has **three** steps, not two:

1. `EXPECTED_CATEGORY_COUNTS = {1: 282, 2: 321, 3: 96, 4: 841}` and `EXPECTED_QUESTIONS = 1540` —
   category 5 is excluded, leaving 1540. That matches the 1540 the data-identity task measured.
2. **The step that was missing.** `load_audit_corrections` reads `audit/errors_conv_*.json` —
   `EXPECTED_CORRECTIONS = 156` — and where a record carries `correct_evidence`, that value **replaces**
   the question's raw evidence.
3. `gold = [id_to_row[x] for x in q["correct_evidence"] if x in id_to_row]` and then
   **`if not gold: continue`** — a question whose corrected evidence resolves to no archive row is
   dropped. That removes 5 questions. `1540 − 5 = 1535`.

## The residual is explained

`locomo_6_qa11` has an audit correction with `error_type = "TEMPORAL_ERROR"` and a `correct_evidence`
field that is **present but empty**. So its corrected evidence is `[]`, its gold set is empty, and step
3 drops it. Its raw evidence resolving fine is exactly why the two-step reconstruction could not see it.

**Verified end to end, read-only:** applying all three steps to the verified `locomo10.json` plus the
156 corrections reproduces the bound cohort **exactly** — 1535 predicted, 1535 bound, zero on either
side of the difference. The corrections file loaded 156 records, matching the frozen constant.

No new corpus scan beyond this check was started, no representation was fitted, nothing was run, and no
question, answer or dialogue text was emitted.

## What follows for the ingestion code — and what deliberately does not

**The cohort is not changed.** It stays the bound 1535.

**The ingestion does not implement this rule.** `corpus_ingest.py` takes the bound question ids from the
manifest and resolves each one individually against the source; it refuses missing, extra, misrouted,
duplicated and position-mismatched ids rather than repairing them, and it never derives a cohort. The
test suite asserts that the category-5 question in its fake corpus is *not* ingested and is instead
reported as present-but-outside-the-cohort.

That is deliberate. A reimplementation of the selection rule inside the ingestion would be a **second**
selection rule that could drift from the bound cohort — most plausibly by omitting the audit-corrections
step, which is exactly the step a reconstruction did miss. Knowing the rule is useful for the record;
executing it again is a way to get a different answer.

**This note is documentation, not a dependency.** The ingestion does not read `audit/errors_conv_*.json`
and does not need it.
