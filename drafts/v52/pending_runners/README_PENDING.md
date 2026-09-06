# Pending runners and workflows — NOT AUTHORIZED, NOT TRIGGERABLE

These files implement the candidate preregistration
`drafts/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_DRAFT_2026-09-05.md`. They exist so that the
authorization decision is made against real code rather than against a description.

## Why they are here and not in their working locations

- The runners are at `drafts/v52/pending_runners/`, **not** `research/v52/`.
- The workflows are at `drafts/v52/pending_workflows/`, **not** `.github/workflows/`.

GitHub only executes workflows under `.github/workflows/`. While the files sit here they **cannot
fire under any circumstance** — not by push, not by schedule, not by manual dispatch. Moving them
into their working locations is part of what an authorization would authorize, and is the moment
the experiment becomes runnable.

Both workflows declare no `workflow_dispatch`, no `repository_dispatch` and no `schedule`, matching
the audited boundary stage: once installed, their only trigger route is a push that creates the
named trigger file `research/v52/TRIGGER_COORDINATE_SCALE_2026-09-05.txt`, which does not exist.
Before computing anything they re-verify the pre-run seal by git blob and the exact blob of every
bound file (preregistration, pilot findings, both runners, both tests, both workflows, both frozen
bases). The seal file named in the gate does not exist either; it is written at sealing time.

## Files

| file | role |
|---|---|
| `locomo_coordinate_scale.py` | LoCoMo runner (single job) |
| `test_coordinate_scale_pure_functions.py` | LoCoMo self-test, 29 checks |
| `longmemeval_coordinate_scale_shard.py` | LongMemEval runner, deterministic 10-shard + aggregate, mirroring the audited boundary-localization shard runner |
| `test_longmemeval_coordinate_scale_shard.py` | LongMemEval self-test, 42 checks, including an end-to-end synthetic pass and a cross-runner consistency control |
| `../pending_workflows/v52-locomo-coordinate-scale.yml` | LoCoMo workflow |
| `../pending_workflows/v52-longmemeval-coordinate-scale.yml` | LongMemEval workflow (shard matrix + aggregate) |

## Revision 2026-09-07 — disclosed, not silent

Made before authorization, on the draft branch, by the Continuity Lead. Nothing sealed or frozen
was touched; the candidate preregistration document itself is byte-unchanged (`de667211…`).

1. **Invariance check narrowed to the audited scope.** `check_rotation_invariance` no longer builds
   the full archive Gram matrix `X Xᵀ` (quadratic in archive rows). It now compares archive row
   norms, query row norms and the query-to-archive dot products `XQ Xᵀ`, exactly the quantities the
   audited boundary-localization runners check. This is the narrowing L-049 recorded in advance as
   the correct fix for risk 1. `TOL = 1e-12` is unchanged; on the synthetic self-test the narrowed
   dot error is `8.9e-15` (previously `1.1e-13` with the Gram matrix), restoring the headroom the
   audited stages reported. Risk 2 is therefore closed by narrowing, not by loosening.
2. **The LongMemEval sharded runner is written.** Same pure functions as the LoCoMo runner
   (asserted equal by the cross-runner control), same seeds `59001..59010`, same arms, same output
   schema. Per-question records are persisted for every arm and seed (prereg §10.9).
3. **Both runners now report the per-seed dispersion of the measured denominators** and of
   `FULLHAAR_FRESH` (`sample_sd`, `se`, envelope), as prereg §8 requires.
4. **Non-finite values abort, they are not repaired** (prereg §5), checked on the centered
   representation and again on `C D`, with a message that names the cause rather than surfacing as
   a downstream identity failure.
5. **Workflows aligned with the audited stages:** Python 3.13 and the pinned research stack
   `numpy==2.3.5 pandas==2.2.3 scipy==1.17.0 scikit-learn==1.8.0` (the earlier draft named the Task
   4F1 environment lock, which is a different track); the seal-by-git-blob gate replaces a
   reference to a verifier script that did not exist; the LoCoMo runner takes `--out` like the
   audited runners.

## What has been validated, and what has not

The two self-tests exercise every function that does not touch the corpus, on synthetic data:

- `sign(xD) = sign(x)` holds bit-identically; a negative diagonal is **rejected**;
- degenerate and underflowing coordinates fall back to `d = 1`; the identity survives; non-finite
  input **aborts** with the non-finite message;
- rotation matrices are orthogonal at `TOL`, block-diagonal at 32, deterministic in their seed;
- the invariance check holds **within** a representation and its rotation, is **not** claimed
  between original and rescaled, and **rejects** a non-orthogonal or scaled rotation — the check has
  been shown to fail;
- `evaluate_representation` produces 10 × 6 rows per question, `NATIVE == SCALED_NATIVE` on
  distances, and aborts on a bad transform;
- `summarize` reproduces known fractions exactly (`0.75 / 0.25`), applies the preregistered bands,
  and **rejects** a missing question, a duplicated question, a native-reproduction miss, an
  invariance excursion carried in a shard, and a `SCALED_NATIVE != NATIVE` row;
- the two runners' pure functions agree numerically on the same input.

**Not validated:** anything requiring the corpus. Neither pipeline has been executed end to end,
because the corpora are not in git. The seeds/adapter/base identities are checked at run time by
the frozen bases; the native-reproduction abort (`1e-12` against the frozen anchors) is the run-time
proof that the pipeline is the audited one.

**Two things the authorization decision should know:**

- The candidate preregistration's header still says "No runner exists, no workflow exists". That
  sentence was true when v3 was written and is stale now; the document is byte-unchanged because it
  is the object under Head Researcher review. The pre-run seal binds whatever version is authorized.
- The synthetic self-tests ran on Python 3.14 / numpy 2.5 locally. The workflows pin the audited
  stack; the pure functions do not depend on the version, but that is an inference, not a run.

## Boundary

No corpus was read, no benchmark outcome computed, no Task 4F1 artifact, authorization, HMAC
material or outcome touched.
