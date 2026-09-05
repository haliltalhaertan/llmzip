# Pending runners and workflows — NOT AUTHORIZED, NOT TRIGGERABLE

These files implement the candidate preregistration
`drafts/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_DRAFT_2026-09-05.md`. They exist so that the
authorization decision is made against real code rather than against a description.

## Why they are here and not in their working locations

- The runner is at `drafts/v52/pending_runners/`, **not** `research/v52/`.
- The workflow is at `drafts/v52/pending_workflows/`, **not** `.github/workflows/`.

GitHub only executes workflows under `.github/workflows/`. While the file sits here it **cannot fire
under any circumstance** — not by push, not by schedule, not by manual dispatch. Moving these two
files into their working locations is part of what an authorization would authorize, and is the
moment the experiment becomes runnable.

The workflow additionally declares no `workflow_dispatch`, no `repository_dispatch` and no
`schedule`, matching the boundary stage: once installed, its only trigger route is a push that
creates the named trigger file, which does not exist.

## What has been validated, and what has not

`test_coordinate_scale_pure_functions.py` exercises every function that does not touch the corpus —
23 checks, all passing, on synthetic data:

- `sign(xD) = sign(x)` holds bit-identically, and a deliberately negative diagonal is **rejected**;
- degenerate coordinates fall back to `d = 1` and the identity survives that;
- rotation matrices are orthogonal, block-diagonal at 32, and deterministic in their seed;
- norm/dot invariance holds **within** a representation and its own rotation, and is demonstrably
  **not** claimed between the original and the rescaled representation;
- `frac` behaves at 0, at 1 and above 1, and is undefined on a zero denominator;
- the bands admit overshoot.

**Not validated:** anything requiring the corpus. The full pipeline has never been executed, because
the corpus is not in git. Two practical risks follow, stated rather than discovered during a run:

1. **Invariance check cost.** `check_rotation_invariance` compares the full Gram matrix `X Xᵀ`,
   which is O(n²) in the number of archive rows. The audited stages compared query-to-archive dot
   products instead, which is cheaper. On a large archive this check may dominate runtime or memory.
   If it does, the correct fix is to narrow the check to query-archive dots as the earlier stages
   did — **not** to loosen the tolerance.
2. **Dot tolerance headroom.** The synthetic self-test produced a dot error of `1.1e-13` against a
   `1e-12` tolerance — inside it, but with less headroom than the audited stages reported
   (`~1e-15`), because the Gram matrix is larger. If a real run trips this, that is information
   about the check's scale, not licence to raise `TOL`.

## Boundary

No corpus was read, no benchmark outcome computed, no Task 4F1 artifact, authorization, HMAC
material or outcome touched.
