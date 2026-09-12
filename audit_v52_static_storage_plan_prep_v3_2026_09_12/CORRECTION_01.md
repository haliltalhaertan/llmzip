# Correction 01 — additive to INDEPENDENT_V3_AUDIT_REPORT.md

This file supersedes the parts of `INDEPENDENT_V3_AUDIT_REPORT.md` named below. That
file's bytes are NOT rewritten. Where the two disagree, this one is later and correct.

Occasion: the audit was itself reviewed cold-start by an independent agent that was
told to treat the report as a claim and re-derive from bytes. It returned SOUND WITH
CORRECTIONS. Every item below was then re-run by the lead session before being
recorded here; nothing in this file rests on the reviewer's word alone. The command
outputs are in `raw_outputs/second_round_probes.py` and `raw_outputs/fifo_hang_repro.py`.

## 1. Three errors in the original report

**1a. Probe count.** The report says "Twelve adversarial probes were then written and
executed." There are ELEVEN. `grep -c '^probe(' raw_outputs/adversarial_probes.py`
returns 11 and `EXECUTION_RAW.txt` carries 11 result lines.

**1b. Dismissal count.** The report says "Seven probes were rejected by the parent guard
rather than by preflight." There are FIVE: A1, B1, B2, D1, D2. The report's own prose in
that same paragraph enumerates exactly those five. The other six either became findings
(C1-C3 -> AUD-003, E1 -> AUD-002, F1 -> AUD-005) or were rejected by the preflight itself
(C4). The sentence contradicts its own paragraph, and it sits in the section whose stated
purpose was to keep the finding count honest.

**1c. A false absolute.** The report writes, of the PLANPREP2-AUD-001 closure, that "the
authenticated content cannot be swapped after the check." That is false as stated:

```
1. normal rebind blocked: FrozenInstanceError
2. object.__setattr__ -> b'EVIL-SWAPPED' | sha256 field still says: deadbeef
3. re-verification method present? ['byte_length', 'fixture_id', 'raw_bytes', 'sha256']
```

`frozen=True` blocks accidental rebinding and gives no integrity guarantee against
in-process code. The contrast that makes this worth recording: the parent guard's `Plan`
object IS re-authenticated on every use, by re-hashing its raw bytes; V3's `Verified*`
objects carry no equivalent method, so a tampered instance is indistinguishable from a
fresh one. The closure verdict stands, but as CLOSED WITH CAVEAT, not as an absolute.

## 2. One severity raised

**PLANPREP3-AUD-003 LOW -> MODERATE.** Its stated mitigation - "in the declared execution
order the parent guard runs first, so this is not a live hole today" - is unenforceable.
See NEW-2: `preflight` has no mechanical link to whatever the parent guard validated, so
the declared order is a sentence in a markdown file and nothing more. "Not a live hole"
was not established and is withdrawn.

## 3. One finding understated

**PLANPREP3-AUD-001.** The report frames the missing anchor around probe `N` reaching
`D_k`. There is a shorter path that does not involve a probe at all: the claim builder
computes the primary aggregate as `mean_i(C_i / N_i)` and publishes it as the headline,
so an inflated `N_i` alone deflates the published figure directly. The stated fix
direction (bind `N_i` to the frozen CSV by digest and row identity) covers both paths,
but the finding should have said the HEADLINE AGGREGATE is unanchored, not only the
amortization denominator.

Also concrete and omitted: `PLAN_PREP_SPEC_V3.md` declares the panel as "all frozen
archives: `(N_i, q=1)`". That is a checkable constraint - every archive must carry a probe
whose `N` equals its `N_i` - and no guard enforces it. That is more actionable than the
report's "simple equality cannot be the fix."

BLOCKING severity is unchanged.

## 4. Five further findings, each reproduced by this session

### PLANPREP3-AUD-006 — BLOCKING — a non-regular file hangs preflight forever

`read_bytes` calls `Path(path).open("rb")` with no regular-file check. A FIFO named in
`physical_locator` resolves inside the binding directory, so `safe_child` admits it, and
the open blocks with no reader. The digest is never reached.

```
calling preflight with physical_locator -> FIFO ...
EXIT=124  (124 = hung)
```

This is the exact window the original report examined and declared safe, reasoning that
any substitution there changes the digest and is rejected. It is not rejected, because
control never returns. `CONSUMPTION_BOUNDARY_V3.md` promises that every violation "stops
before the future adapter callback"; a hang is not a stop. Repro in
`raw_outputs/fifo_hang_repro.py`. Direction: require a regular non-symlink file before
opening, and open with `O_NOFOLLOW|O_NONBLOCK` then `fstat` the handle actually read.

### PLANPREP3-AUD-007 — BLOCKING — no mechanical binding between the guarded plan and the preflighted plan

`preflight(plan_path, expected_plan_sha256, ...)` takes a path and a digest. It has no
parameter of the parent guard's `Plan` type and no way to learn what that guard
validated, and `VerifiedBindings` carries no `contract_sha256` and no back-reference.
`PLAN_PREP_SPEC_V3.md` requires "the same externally frozen plan SHA256" to pass both;
nothing enforces "same". A caller can validate plan A and preflight plan B. This is what
makes AUD-003's mitigation unenforceable, and it is why AUD-003 moved to MODERATE.

### PLANPREP3-AUD-008 — MODERATE — the denominator rule yields a menu, not a value

`sharing_denominator_rule = "POPULATION_COUNT"` emits one state per bound population,
with no selection rule and no phase label recoverable except by parsing an ID string.
One physical copy bound to four populations:

```
ACCEPTED copies=1 states=(('p1','EMPTY_NO_AMORTIZATION',None), ('p2','POSITIVE',1),
                          ('p3','POSITIVE',1000000000), ('p4','POSITIVE',4))
```

Four candidate `D_k` for one artifact, spanning None, 1, 10^9 and 4, ordered only by the
caller's `population_ids` order. Under the declared LongMemEval panel that is on the
order of a thousand candidates per copy. The measurement contract says `D_k` is THE real
group cardinality; the preflight hands the adapter a choice, and choosing the largest is
precisely the dilution AUD-001 warns about.

### PLANPREP3-AUD-009 — MODERATE — uncaught OSError/ValueError from the companion documents

```
relative_path = '.' (a directory)      LEAK(IsADirectoryError)
relative_path with embedded NUL        LEAK(ValueError) embedded null byte
physical_locator = '.' (a directory)   LEAK(IsADirectoryError)
```

Distinct from AUD-003 in one way that matters: the parent guard validates the PLAN and
has never seen `v52.fixture-bindings` or `v52.physical-copy-bindings`, which are V3's own
schemas. So the "parent guard catches it first" mitigation does not extend here even in
principle. A caller catching `PreflightError` crashes. Note also that `PreflightError`
subclasses `ValueError`, so a caller broad enough to catch these cannot distinguish a
genuine interpreter error from a validation refusal.

### PLANPREP3-AUD-010 — LOW — version fields accept bool and float

```
plan version = True (bool)   ACCEPTED
plan version = 1.0 (float)   ACCEPTED
plan version = 2 (control)   REJECTED  schema-1 plan required
```

`plan.get("version")==1` where the parent guard writes `type(data["version"]) is int and
... == VERSION`. Same divergence family as AUD-004, with observable behaviour. Elsewhere
the preflight does use `type(v) is int` correctly, so bool is rejected for counts and
masks; the version fields are the exception.

### PLANPREP3-AUD-011 — LOW — two physical copies may bind to one file

```
pc1 and pc2 both -> phys.bin   ACCEPTED copies=2
```

The parent guard deliberately permits equal hashes for genuinely distinct physical
copies. The preflight authenticates bytes, not the existence of two artifacts, so it
cannot distinguish two real copies from one file counted twice - the exact confusion the
contract warns against when it says equal hashes are not proof of one shared copy.

### Recorded but not reproduced here

The reviewer also reported unbounded aggregate memory: every artifact's bytes are
retained at once with only a per-artifact 64 MiB cap, so a declared worst case reaches
tens of gigabytes. This session verified only the structural half - the module defines
`MAX_ARTIFACT_BYTES`, `MAX_DECLARATION_BYTES`, `MAX_DEPTH`, `MAX_ENTITIES` and no
aggregate byte budget - and did not run the memory measurement. It is recorded as an
open concern, not as a reproduced finding.

## 5. Verdict after correction

`REQUEST_CHANGES` is unchanged and now rests on three blocking findings rather than one:
AUD-001 (no external anchor for the headline aggregate and the denominator), AUD-006
(hang on a non-regular file) and AUD-007 (no cross-guard plan binding). Each would be
frozen into the literal plan by a pass, which is why each blocks the same step.

The three inherited P2 closures stand, with AUD-001's closure now carrying the caveat in
section 1c.

Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. No
corpus, query, gold or outcome was opened; nothing was fitted, measured, scored or
sealed; `main`, the ledger and state are untouched and no merge was made.
