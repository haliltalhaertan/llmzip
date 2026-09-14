# V52 static-storage V6 — integration and portability repair

Status: **REPAIR CANDIDATE / NOT AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION.**

Repairs what the Head Researcher found by running both guards on a **Windows** machine.
Five findings, all confirmed here from the code before being accepted. V5's bytes at
`61827088b99905e25c3a40679e1c5b483f3b83a9` and the anchor guard's at
`f13969f2598bcb4a26cbfc9ffe35433851bc02c7` are not rewritten.

## The one that matters: the two guards did not know about each other

The division of labour was: V5 checks that the files are the files they claim to be; the
anchor guard stops the fraud, which is inflating the vector count so that bytes-per-vector
collapses. The V3 audit had shown that exact fraud taking a headline from 15.0 to 9e-08
with nothing noticing.

**No code called the anchor guard.** V5 said in prose that it must run, and the module
even admitted "nothing here enforces that it did". Honest, and still a hole: whoever
forgets it gets the fraud through.

This is the third time the same joint has been loose. V3: no binding at all. V4: a
binding that defaulted off. V5: two packages and a sentence between them.

**V6 makes the anchored denominators a required argument.** A caller that skips the
anchor guard cannot call `preflight` at all - it is a `TypeError` from the signature.
The mapping is then cross-checked against the plan the preflight just authenticated:
the chosen population must be bound to that copy, its count must match the plan, and it
must be positive. So a caller cannot fabricate the mapping either. `VerifiedPhysicalCopy`
now carries one `denominator`, not the menu of `denominator_states` V5 reported.

Neither module can produce a denominator alone. That is the point.

## Portability

`os.O_NOFOLLOW` was written bare while `getattr` was used for `O_CLOEXEC` on the same
line - the defensive pattern was known and applied to the wrong flag. On Windows that is
an `AttributeError`, so the module broke its own promise that every refusal is a
`PreflightError`. All four optional flags now go through `getattr`, and
`SYMLINK_FLAG_AVAILABLE` / `NONBLOCK_FLAG_AVAILABLE` expose which were compiled in.

**A first draft of this file got the reasoning wrong and the simulation caught it.** It
claimed the `S_ISREG` check on the fstat'ed handle was the portable refusal. It is not:
without `O_NONBLOCK` the `open` blocks on a FIFO before any fd exists, so the post-open
check never runs - the AUD-006 hang returning by another route, on exactly the platforms
the repair was for. Simulating a flagless platform hung the test run for two minutes.
The refusal is now a **pre-open `os.stat`**, which is portable, and the post-open `fstat`
proves the fd is the same inode, so the TOCTOU window stays closed.

## Platform matrix

V5's disposition said "31 tests, all passing on Python 3.11.15" and never said on what
operating system. On the author's Linux box that was true; on Windows 25 of the 31 could
not run at all. The claim was not false, it was unlocatable.

| Platform | Result |
|---|---|
| Linux, Python 3.11.15, both flags present | 9/9 integration tests pass |
| Flags forced to 0 in-module (Windows-like) | normal artifact accepted; FIFO refused as `PreflightError`; no hang |
| Windows, real | **NOT RUN HERE.** Needs confirmation on the Head Researcher's machine |

The third row is the honest state. This session has no Windows host and does not claim one.

## The hardcoded path

`test_archive_anchor_guard.py` line 192 runs `git -C /home/user/llmzip show ...`. That
test could only ever have executed on its author's machine, and it is the one test that
binds the guard to the real frozen table. It is superseded here by
`test_integration_v6.py::test_real_anchor_table_without_a_hardcoded_path`, which finds
the repository from `LLMZIP_REPO` or by walking up for a `.git` directory, and skips with
a stated reason rather than failing when neither works. The anchor guard MODULE is
unchanged and imported as-is; only that test case is superseded.

## Evidence

`test_integration_v6.py`, 9 tests, passing on Linux / Python 3.11.15. They cover: the two
guards working together end to end; `preflight` refusing to be called without the anchor
result; the original dilution refused by the anchor guard before the preflight runs;
three forged mappings each refused for a different reason; a missing copy in the mapping;
a 10^9 diagnostic population bound to the same copy being ignored rather than chosen; the
flags being platform-optional; the FIFO refusal not depending on them; and the real
470-row table loaded without a hardcoded path.

## What this does not mean

Not: storage measured, `<=12` proven, actual plan approved, real adapter ready, retrieval
authorized, Task4F1 authorized, V6 audited, Windows verified. V6 needs an independent
cold-start audit, and the Windows row needs a real Windows run.

Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. No
corpus, query, gold or outcome was opened; nothing was fitted, measured, scored or
sealed; `main`, the ledger and state are untouched and no merge was made.
