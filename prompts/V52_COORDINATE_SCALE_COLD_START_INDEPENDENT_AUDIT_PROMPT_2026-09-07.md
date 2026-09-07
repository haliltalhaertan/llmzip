# V52 — Coordinate-Scale Participation: Cold-Start Independent Audit Prompt

Issued: 2026-09-07 by the Continuity Lead. Status: WRITTEN — commissioning is a Head Researcher
decision. The auditor must be a session that did NOT prepare, install, seal, trigger or record this
stage.

## Your role

You are a cold-start independent auditor. You accept nothing from chat, commit messages, ledger
prose, `ops/CURRENT_STATE.json`, or the checkpoint document as evidence. You re-derive from bytes
and from execution. You commit only under `audit_v52_coordinate_scale_independent_2026_09_07/` on
your own branch `audit/v52-coordinate-scale-independent-2026-09-07`. You do not touch the research
branch, `main`, any seal, any frozen artifact, or anything under Task 4F1.

Hard stops, non-negotiable: never invoke any Task 4F1 candidate (`--mode run`/`finalize`), never set
`V52_T4F1_AUTH_HMAC_KEY_HEX`, never read or compute a BEAM retrieval outcome. This stage is LoCoMo
and LongMemEval only.

## Object under audit

Repository `haliltalhaertan/llmzip`, branch `research/v52-sign-mechanism-locomo-2026-09-04`.

| item | anchor |
|---|---|
| package head before seal | `59ae1b53d3c4e524621d87a08b396f72a8332816` |
| pre-run seal | `research/v52/V52_COORDINATE_SCALE_PRERUN_SEAL_2026-09-05.json`, blob `52605626…`, commit `2a070062` |
| trigger | `680b10b8a3ef3dd55a5a05fe47f6fb5fa6d931d0` |
| result commits (runner-authored) | `f1bbb50` (LoCoMo), `bce57b64dd2451d4d7bc0cd2c6e61d84e35261c8` (LongMemEval) |
| checkpoint (the CLAIM you are testing) | `research/v52/V52_COORDINATE_SCALE_RESULT_CHECKPOINT_2026-09-07.md` with `.sha256` sidecar |
| preregistration (verbatim v3) | `research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md`, sha256 `de667211…` |

## Gates — each must be ESTABLISHED from bytes or execution, never from not-falsified

- **G1 Seal integrity.** Every `git_blob_sha1` in the seal matches `git hash-object` of the file at
  the trigger commit; `package_head_before_seal` is the parent chain of the seal commit; the trigger
  file carries the seal's blob. State which files are bound and which are NOT (e.g. the checkpoint).
- **G2 Single trigger.** Exactly one commit creates the trigger path; the workflows declare no
  dispatch/schedule; GitHub Actions history shows one run per workflow for this trigger. A silent
  branch is not evidence; check the Actions record.
- **G3 Preregistration freeze.** The preregistration bytes at the seal equal the draft bytes at
  `draft/v52-coordinate-scale-prereg-2026-09-05 @ bdc0db75` (sha256 `de667211…`). Report the stale
  header sentence ("No runner exists…") and judge whether it is load-bearing.
- **G4 Runner ↔ preregistration.** Every constant in both runners (seeds `59001..59010`, arms,
  `eps=1e-12`, degenerate flag threshold 4, `TOL=1e-12`, bands 0.70/0.20, scale rule `1/sigma` per
  archive on the centered representation, block boundary 32, head block drawn first) is quoted
  from the preregistration. List any value in the runners that the preregistration does not fix.
- **G5 Native reproduction.** Re-execute at least one benchmark end to end from the sealed bytes on
  the pinned stack (Python 3.13; numpy 2.3.5, pandas 2.2.3, scipy 1.17.0, scikit-learn 1.8.0) and
  reproduce `NATIVE` to `1e-12` against the frozen anchors AND reproduce the persisted per-question
  rows byte-for-byte or to stated precision. State which benchmark you re-executed and why.
- **G6 Identity.** Verify by execution, not by reading, that `sign(x D) = sign(x)` holds bit-exactly
  and that a negative diagonal is rejected. Supply your own failing case.
- **G7 Invariance scope.** The check compares row norms and query-archive dots, not a Gram matrix;
  verify it can FAIL (perturb a rotation) and that TOL was never changed between draft `c044d469`,
  draft `bdc0db75`, install `59ae1b53` and the result commits.
- **G8 Aggregates from rows.** Recompute `frac_full`, `frac_block`, per-seed values, `I_frac`, the
  denominators and their dispersions from the persisted per-question CSVs alone. Match the summaries
  and the checkpoint tables to stated precision. Note the LoCoMo summary lacks an `artifacts` block;
  hash the per-question file yourself (checkpoint states `b7abd942c13cf9ce…`).
- **G9 Bands as preregistered.** Apply §7 bands to the seed-panel means. Confirm LoCoMo `frac_full`
  ≥ 0.70 (`MOST`) and LongMemEval `frac_full` in `(0.20, 0.70)` (`PARTIAL`) with no rounding
  assistance: report the exact margins.
- **G10 Block-arm interpretability.** Independently judge the checkpoint's claim that the LoCoMo
  block fraction is not interpretable because the denominator crosses zero inside its seed envelope.
  Is this a legitimate post-hoc caveat (reporting a limitation) or an unpreregistered rule (tuning)?
  Say which and why. Check the same question on LongMemEval (all ten denominators positive?).
- **G11 No tuning.** Search the branch history between seal and checkpoint for any second trigger,
  any edit to runners, seeds, `eps`, bands or TOL, any additional arm, any replacement seed.
- **G12 Denominator by-product.** Verify the fresh `FULLHAAR_FRESH` panel statistics (LoCoMo sd
  0.0052 / se 0.00164; LongMemEval sd 0.0115 / se 0.00362) from rows, and that the checkpoint does
  NOT replace the frozen denominators in the audited boundary-localization line.
- **G13 Case against.** Build the strongest case that the result is an artifact: rescaling changes
  the query as well as the archive; the block arm's tiny loss; seed-panel size 10; question-level
  nesting in LoCoMo (1,535 questions in 10 conversations) with no clustered bootstrap yet reported.
  Adjudicate: does the case against weaken or defeat the `[LEAD]`?

## Verdict vocabulary

`AUDIT PASS`, `AUDIT PASS WITH CAVEATS`, `AUDIT FAIL`, or `BLOCKED` (with the gate). For every gate,
mark ESTABLISHED / NOT ESTABLISHED / FAIL. Deliver: `AUDIT_REPORT.md`, a gate table, a recursive
sha256 manifest of your namespace, your reproduction scripts, and a `.sha256` sidecar for the report.
Do not interpret beyond §9 of the preregistration. Do not upgrade a `[LEAD]`.
