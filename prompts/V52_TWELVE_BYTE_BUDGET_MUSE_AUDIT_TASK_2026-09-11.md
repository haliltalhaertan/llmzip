# Muse audit task — the twelve-byte budget finding

**Object under audit:** the pushed preregistration
`docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md`
on branch `draft/v52-twelve-byte-baseline-prereg-2026-09-10` at
`d2cfbaacdfc52af2ac2077ffa1d87b719a7d0779`,
and twelve claims made about it on 2026-09-11.

**Repository:** `github.com/haliltalhaertan/llmzip`, `main` at
`7e1de3af60b237766e21bf45d97018add8fe2eb1`.

---

## How to run this

Lessons from three earlier runs, two of which hung:

```bash
MUSE_TIMEOUT=1800 muse \
  --approval-mode never \
  --user-input-auto-resolve \
  --disable-write \
  --reasoning-effort xhigh \
  --task V52_TWELVE_BYTE_BUDGET_MUSE_AUDIT_TASK_2026-09-11.md
```

- `--approval-mode never --user-input-auto-resolve` is what made the third run
  stream. Without it, tool calls stall at `task.lifecycle.proposed` with nothing to
  approve them, and the run hangs until timeout.
- `--disable-write` is a **separate** flag and must stay on. Turning off the approval
  prompt does not grant write access.
- The wrapper captures only the final message. The real report is in the raw event
  stream under `run.output.delta` — extract it from the JSONL, do not trust the
  wrapper's output file.
- **Do not explore the repository.** Every claim below carries its exact
  `ref:path`. A combined 21-claim task over 85 branches and 25 worktrees blew the
  search budget and timed out. Target ~15 commands total.

## Hard stops

No writes. No commits. No pushes. No experiment, no seal, no pilot, no run. Do not
set `V52_T4F1_AUTH_HMAC_KEY_HEX`. Do not read, compute or expose any Task 4F1
retrieval outcome — Task 4F1 is SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN and
is a different corpus (BEAM) from this stage.

Installing `faiss-cpu` in a scratch virtualenv to check claims C2–C7 is expected and
permitted; it touches nothing in the repository.

---

## The claims

Grade each `VERIFIED` / `CLASS RIGHT, NUMBER NOT REPRODUCED` / `OVERSTATED` /
`FABRICATED` / `UNVERIFIABLE`. **A grade is itself a claim and must be supported from
bytes.** Two earlier reviewers each graded from where they happened to look rather
than from what was claimed; both were wrong.

### About the preregistration text

**C1.** The document's title and line 14 state a *"fixed 96-bit (12-byte) budget"*,
and the arm table at lines 52–59 gives the budget column as `96 bit` for arms 1–7.
The claim under audit: this **equates code width with stored size**, and that
equation is what the budget error rests on.
Source: `d2cfbaa:docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md`, lines 14 and 52–59.

**C8.** Section 5's third bullet requires *"Codebook/centroid training seeds for arms
5–7: five seeds, declared as source literals in the runner before any run."* The
claim: arms 5 and 7 carry **no seed-bearing randomness**, so declaring seeds for them
would announce randomness that does not exist and would falsely imply those arms are
seed-averaged. Only arm 6 needs seeds.
Source: same file, section 5.

**C9.** Arm 6 contains **two separately seeded trainings** — the OPQ rotation's own
sub-quantizer and the PQ codebook — and section 5 does not distinguish them.

**C11.** Section 8 declares positive controls
`SIGN96 LongMemEval == 0.5419751773049646` and
`SIGN96 LoCoMo-1535 == 0.23654714666441054`, both at `±1e-9`. Check that these match
the frozen values recorded in `main:docs/CONTINUITY_LEDGER.md` and that the stated
tolerance is wide enough for the known reproduction residual of about `1.11e-16`.

**C12.** The declared primary contrast is `SIGN96 − RABITQ96` (line 99). The claim:
as the document currently stands, with arms 4 and 5 outside the stated budget, this
contrast **cannot be computed at a matched budget** — which is the failure section 12
exists to prevent.

### About faiss, measured

Reproduce these in an isolated process. They were measured on `faiss-cpu 1.15.0`.

**C2.** `faiss.RaBitQuantizer(96).code_size == 20`, not 12.

**C3.** `faiss.RaBitQuantizer(96, faiss.METRIC_L2, 2).code_size == 44`.

**C4.** The overhead is **fixed at 8 bytes** independent of `d`
(`d=32 → 12`, `d=64 → 16`, `d=96 → 20`, `d=128 → 24`), and those 8 bytes are the
per-vector scalar correction terms RaBitQ's unbiased estimator and error bound
depend on — so they are **not** removable without ceasing to be RaBitQ.
The second half of C4 is an interpretation, not a measurement. **Grade the two halves
separately.**

**C5.** The largest `d` whose total fits 12 bytes at `nb_bits=1` is **`d = 32`**.

**C6.** Assigning `nb_bits` after construction is **silently ignored**:
`q = RaBitQuantizer(96); q.nb_bits = 2` leaves `code_size == 20`, i.e. a 1-bit code,
while the constructor form gives 44. Consequence claimed: a runner that assigns the
attribute would run arm 5 as a silent duplicate of arm 4.

**C7.** The second positional argument of `IndexRaBitQ` is `metric`, not `nb_bits`,
so `IndexRaBitQ(96, 2)` is read as `METRIC_L1` and aborts the process with heap
corruption rather than raising. Check the constructor signature in the installed
package.

**C10.** The minimum `faiss-cpu` version exposing multi-bit RaBitQ is **1.13.1**;
1.11.0, 1.12.0 and 1.13.0 carry RaBitQ but not the multi-bit path. Verify the
boundary if you can do it cheaply; if a full version sweep is too expensive, say so
and grade `UNVERIFIABLE` rather than guessing.

---

## The three questions that matter more than the grades

1. **Is the proposed remedy sound?** The recommendation put to the Head Researcher is:
   hold the budget at **12 bytes total including all per-vector auxiliary data**, let
   each method choose its own configuration (RaBitQ therefore at `d=32`), drop arm 5
   from the matched-budget contrast, and report a recall-versus-actual-bytes curve
   alongside. Attack this. In particular: is `d=32` RaBitQ a fair comparator for
   `d=96` SIGN96, or does it hand SIGN96 an unearned win that a reviewer would reject?

2. **What did neither session consider?** Both sessions have now looked at storage
   bytes. Neither examined query-side cost, index-structure overhead beyond the
   per-vector code, or whether any *other* arm in the table has a hidden auxiliary
   cost the same way RaBitQ does. Arm 6 `OPQ_PQ96` stores an OPQ rotation matrix and
   PQ centroids — shared, not per-vector, but not free. Say whether the budget
   definition should be per-vector or amortised, and what that does to the verdict.

3. **Is there a cheaper experiment that answers the same question?** The programme has
   spent four days on preregistration revisions and produced no new scientific result
   since 2026-09-07. If a smaller measurement would settle whether SIGN96 is
   competitive, name it.

## Report format

For each claim: the grade, the command or line that establishes it, and one sentence.
Then the three questions. Then anything you found that is not on this list.

Do not soften a finding to be agreeable, and do not invent one to look thorough. A
reviewer that produces specific numbers which do not reproduce is more dangerous than
one that stays qualitative, because numbers get quoted and hash-bound.
