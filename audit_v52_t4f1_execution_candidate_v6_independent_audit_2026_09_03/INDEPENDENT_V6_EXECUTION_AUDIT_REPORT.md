# V52 Task 4F1 — Execution Candidate V6 Cold-Start Independent Delta Audit

**Verdict: `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`**

| | |
|---|---|
| Audit date | 2026-09-03 |
| Role | cold-start independent implementation auditor |
| Instruction set | `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V6_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-03.md` (sole authority) |
| Repository commit audited | `6dee50da1452869e6049c109100f3c3fb5abb0fb` |
| Audit branch | `audit/v52-t4f1-v6-independent-2026-09-03` |
| Candidate | `task4f1_execution_candidate_v6_2026_09_03/` |
| Environment | CPython 3.12.13 built from the python.org source tarball; NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0; single-thread controls; `-B` / `PYTHONDONTWRITEBYTECODE=1` |

Every claim below is re-derived from the bytes. No prior audit, co-chair review, ledger entry,
README, preflight package or commit message was accepted as evidence. The candidate's own gate
was executed and observed, but its output was treated as a hypothesis to be tested, never as proof.

---

## 1. Headline

**The shipped V6 bytes are clean. The gate's claim about them is not established.**

Those two statements are both true and must not be collapsed. I could not find a single defect in
the *contents* of V6: no superseded literal survives, no value-shaped token is unattributed or
misplaced, every declarative payload agrees with the runner it mirrors, and the runner is
byte-identical to the accepted V4. If the question were "is this package internally consistent
today?", the answer would be yes.

But that is not what the package asserts. `NORMATIVE_SOURCE_MAP.json` states a general guarantee:

> Every load-bearing concept has one enumerated normative source; every occurrence of its value
> elsewhere is a declared typed mirror; no superseded literal survives anywhere; and no value-shaped
> token exists in the closure that no concept claims.

That guarantee is **not established**. It is **not yet falsified on these particular bytes** — which
is a much weaker statement, and is exactly the distinction V5 failed to survive. Of 36 adversarial
probes, **25 evasions succeeded** against a gate whose whole purpose is to make evasion impossible.
The most damaging of them requires no cleverness at all: writing the word `probe` in front of a
planted digest instead of the word `digest` makes it invisible.

V6 genuinely fixes what V5 got wrong. It also introduces a new defect of the same character —
a mechanism whose observable PASS is not evidence of the property it is asserted to prove.

---

## 2. Delta route — justified

All six preconditions were tested before any delta-scoped reasoning was used.

| # | Precondition | Result |
|---|---|---|
| 1 | V6 runner bytes equal accepted V4 runner bytes | **Established.** `f96cba2c…21f8` in V4, V5 and V6 |
| 2 | Runner ASTs equal, docstrings stripped | **Established.** V4↔V6 and V5↔V6 both equal |
| 3 | Retrieval-execution inputs and estimand anchors unchanged | **Established.** 30/30 declared values match the runner's own constants; BEAM corpus re-derived 205/205 blobs |
| 4 | V4 and V5 audit packages authentic | **Established.** Both commits present; V5 manifest `0b7879e3…af81` matches and is 32/32 self-consistent |
| 5 | V6 changes limited to declarative payloads, attestation semantics, package checker | **Established.** Five files changed V5→V6; the only executable one is the out-of-band checker, which the runner never imports or names |
| 6 | Inverted-burden gate passes against the complete V6 payload closure | **Passes — but see §4.** The gate returns PASS; the claim it prints is not established |

The delta route is **justified**. This audit is therefore scoped to the delta, and §7 states
exactly which conclusions rest on citation of the V4 audit rather than my own re-derivation.

---

## 3. What V6 fixed

Credit where it is due. The V5 defects are genuinely repaired, and I confirmed each by construction:

- **Line-wrapped digests** (V5 missed): caught.
- **Uppercase hex** (V5 missed): caught.
- **Both combined**: caught.
- **Burden inversion is real, not cosmetic.** The gate no longer trusts a hand-written mirror list.
  It sweeps the closure and holds discovered tokens to account. Novel digests planted in fresh
  locations are caught (probes 3.1a–3.1d, 3.1f).
- **Exemptions are key-path scoped, not file-scoped**, for two of the three classes — a real
  improvement, and the declaration-site exemption is implemented structurally (by deleting the
  `fields` and `deprecated_literals` keys before serialising) rather than by matching prose. An
  unattributed digest added to the map's *prose* is still caught (probe E6). The exemption
  genuinely cannot be widened by editing text around a literal.
- **Structural rules hold**: duplicate concepts, missing locators and unresolvable paths all block
  (E1–E3). A concept cannot silently deregister itself: emptying a hex concept's
  `scannable_literals` makes its own token unattributed, and the gate blocks (G4).
- **Status semantics hold**: the seal records submission status only, the inventory carries no
  status field, and a missing or disagreeing attestation blocks (F1–F4).

---

## 4. Gate 3 — the inverted-burden sweep

### 4.1 The central defect: normalisation destroys the boundaries the patterns depend on

The gate normalises before matching:

```python
def normalise(text): return re.sub(r"\s+", "", text).casefold()
```

and matches with hex-boundary lookarounds:

```python
re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
```

These two mechanisms destroy each other. Stripping **all** whitespace concatenates a token with the
words on either side of it. If the preceding word ends in `[0-9a-f]`, or the following word begins
with `[0-9a-f]`, the lookaround suppresses the match and **the token is never seen at all** — no
error, no warning, no entry in any count.

Ordinary English is full of such words. Measured over seven prefixes × five suffixes, **26 of 35
combinations (74%) make the token invisible** (`evidence/normalisation_defect.json`):

| Context | Seen? |
|---|---|
| `digest <64-hex>` + newline | seen |
| `probe <64-hex>` + newline | **missed** — `probe` ends in `e` |
| `the <64-hex>` | **missed** — `the` ends in `e` |
| `sha256 <64-hex>` | **missed** — ends in `6` |
| `V4 <64-hex>` | **missed** — ends in `4` |
| `<64-hex> and the rest` | **missed** — `and` starts with `a` |
| `<64-hex> for the cohort` | **missed** — `for` starts with `f` |

This is not a theoretical concern. Three probes exploit it against the live gate and all three pass
undetected (`evidence/probe_batch2.json`):

- **A1** — a novel unattributed 64-hex digest planted in `README.md`, preceded by the word `probe`.
- **A2** — the same digest followed by the word `and`.
- **A3** — the **live cohort digest** `9b70e16f…519a` relocated into `README.md`, a file its concept
  does not permit, hidden by ordinary prose. The identical relocation with a non-hex-adjacent word
  is caught (probe 3.1f). The only difference is one English word.

So the clause *"no value-shaped token exists in the closure that no concept claims"* is false as a
general statement, and the clause *"every occurrence of its value elsewhere is a declared typed
mirror"* is unenforced whenever prose happens to be hex-adjacent.

I re-derived the sweep independently over the shipped bytes to see whether this is already being
exploited (`evidence/independent_sweep.py`). It is not: **0 tokens are currently invisible to the
gate**. The current package is clean. The mechanism protecting it is not.

### 4.2 Further evasions

| Probe | Evasion | Result |
|---|---|---|
| B1 | Superseded literal split by a zero-width space (U+200B) | **survives** — `\s` does not match U+200B |
| B2 | Superseded literal with Cyrillic look-alike characters | caught — but only incidentally: the substitution splits the digest into a 40-hex fragment that then reads as unattributed. Not by design |
| B3 | Superseded literal interleaved with `<!---->` | **survives** — only whitespace is stripped |
| B4 | Superseded literal re-encoded as base64 | **survives** |
| B5 | Superseded literal re-encoded as a decimal integer | **survives** |
| B6 | Superseded literal split across two JSON keys | **survives** |
| B7 | Superseded literal inside a bound but non-UTF-8 payload | **survives** — `except (UnicodeDecodeError, OSError): continue` silently skips the file and does not even increment `payloads_swept` |
| B8 | Superseded literal placed in the detached attestation | **survives** — the attestation is outside the closure and is never swept |

B7 deserves emphasis: a payload can be bound by the inventory, hash-verified by `main()`, and then
**silently omitted from the sweep entirely**. The gate reports success without ever having looked at it.

### 4.3 Blind spots in the token patterns

The three patterns cover 64-hex, 40-hex and `v52_t4f*` identifiers. I flattened all 24 declared
concept values into the scalar literals a reader must trust (`evidence/gate3_coverage_analysis.json`):

- **16 of 72 value atoms (22%)** are token-shaped and can be policed.
- **56 of 72 (78%)** lie outside every pattern and cannot be seen by the sweep at any position.
- **9 of 24 concepts** contribute no scannable literal at all.

Four of those nine are separately protected by bespoke equality checks elsewhere in the gate
(`candidate_submission_status`, `post_audit_acceptance_state`, `authorization_commitment_state`,
`outcome_boundary_and_stop_rule`). **Five have no enforcement of any kind:**

`arm_identifiers` · `methods_seeds_trials_topk` · `metrics_and_structural_zero_rule` ·
`aggregation_rule` · `authorization_signed_fields`

These are the numerical and semantic core of the experiment. Every drift probe against them passes
undetected (`evidence/probe_batch3.json`):

| Probe | Change | Result |
|---|---|---|
| D1 | estimand denominator `1712` → `1713` in the seal | **undetected** |
| D2 | excluded archive `1M::5` → `1M::7` in the seal | **undetected** |
| D3 | arm identifier `NATIVE_SIGN96` → `NATIVE_SIGN97` in the spec | **undetected** |
| D4 | Haar seed `43001` → `43011` in the spec | **undetected** |
| D5 | invariance tolerance `1e-12` → `1e-10` in the spec | **undetected** |
| D6 | latent seed `5101` → `5102` in the spec | **undetected** |
| D7 | canary threshold `>= 0` → `> 0` in the spec | **undetected** |

The runner would still enforce its own constants at run time, so these drifts cannot corrupt an
execution. But they corrupt the **specification a reader relies on to know what will be executed** —
which is precisely what the single-source map exists to prevent.

**Answer to the prompt's question: 24 concepts is larger, not complete.**

### 4.4 The exempt classes — all three are wider than their rationales

This is the finding that most directly repeats V5's failure mode: the declared scope and the
implemented scope differ, and the difference favours the author.

**`inventory_self_hashes`** — rationale: *"The inventory's own file digests."* Implemented scope:
the entire `files[]` subtree, any key. Probe **C1** adds a `provenance_digest` key holding an
unattributed digest inside a `files[]` entry; it is exempt and passes.

**`historical_provenance`** — rationale: *"Scoped to these key paths only."* Implemented scope uses
`kp.startswith(pre)` on dotted paths, which is string-prefix matching, not path-segment matching.
Probe **C2** adds `supersedes_candidate_addendum` — a key that no rationale covers — and it is
exempt because its name begins with `supersedes_candidate`. Probe **C3** smuggles a digest into
`payload_inventory.smuggled` for the same reason.

**`artifact_identifiers`** — rationale: *"File names, derived-output names, the environment-variable
name and container/schema wrapper labels. These are identifiers, not load-bearing values."*
Implemented scope: a **file-wide** allowlist with no key-path scoping, applying to eight of the nine
payloads. Two entries on that allowlist are not identifiers in the intended sense —
`v52_t4f0_restricted_refreeze_2026_08_31` and `v52_t4f0_codex_2026_08_31` name the **sealed 4F0
namespaces**, and the first of them is the sole authoritative source of the cohort
(`EXTERNAL:audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv`).

Probe **C4** rewrites `EXECUTION_SPEC.md` to point at the *codex* namespace instead of the
*restricted refreeze* namespace. Both strings are allowlisted, so the substitution — which changes
which sealed dataset the specification claims to draw from — passes without comment. That is a
load-bearing normative value smuggled through a class declared to contain none.

The classes can also be widened at will: probe **E5** declares a new blanket exempt class covering
all nine files and every literal, and the gate passes with a planted unattributed digest in place;
probe **G7** simply appends `EXECUTION_SPEC.md` to an existing class's `files` list.

### 4.5 Deprecated literals can be disarmed by declaration

`entry.get("must_not_appear_as_requirement", True)` defaults safely, but a deprecated entry may
declare `false`. Tokens in `deprecated` are also `continue`d out of the attribution loop. Setting
that flag to `false` therefore removes a literal from **both** the survivor check and the
unattributed check — total invisibility, by declaration, with no guard. Probe **E8** confirms it.
All six shipped entries are correctly `true`; the bypass is latent, not active.

### 4.6 The declaration-site exemption is exact, but the declaration is unverified

Probe **E6** confirms the exemption cannot be widened by editing prose — the map's prose is still
swept. This part of the design is sound.

However, the gate never checks that a concept's `scannable_literals` correspond to its declared
`value`, and never checks that a declared mirror actually contains the value. Consequences:

- **G5** — `cohort_anchor.value.eligible_questions` is changed to `9999` while its
  `scannable_literals` stay correct. Undetected. The map's own stated value can lie.
- **G2** — the cohort digest is deleted from `EXECUTION_SPEC.md`, a declared mirror. Undetected.
- **G3** — a phantom mirror is declared on a file that never held the value. Undetected.
- **G6** — the `gate_claim` prose is rewritten to claim exhaustive verification. Undetected. The
  gate does not verify its own self-description, which is why observing it print PASS establishes
  nothing about what it checked.

### 4.7 Concept resolution and duplication

Every concept resolves to an existing path and no concept is declared twice — verified in the
shipped bytes, and both rules block when violated (E1, E2). Note that path resolution checks
**existence only**, never content.

### 4.8 Missing load-bearing concepts

Two runner constants that carry experimental meaning have no concept in the map at all
(`evidence/gate3_missing_concepts.json`):

- **`REAL_CANARY_QUERY`** = `"Which project phase mentioned module 7 and a deadline?"` — the canary
  sign digests at lines 901/927 are computed *from this exact string*. The map declares the digests
  but not the input that produces them. The string also appears in `EXECUTION_SPEC.md`: a
  load-bearing value repeated in two files with no concept binding them, invisible to the sweep
  because it is not token-shaped.
- **`TIERS`** = `("100K", "500K", "1M", "10M")` — defines the archive-identifier space in which the
  four excluded archives are named. Present nowhere but the runner.

### 4.9 Verdict on the gate's claim

> **The claim is NOT ESTABLISHED. It is NOT YET FALSIFIED on the V6 bytes as shipped.**

The sweep establishes a genuine but narrow property: *within the UTF-8-decodable bound payloads, for
the three declared token shapes, at positions where whitespace-stripping does not place a hex
character adjacent to the token, and outside three exempt classes that are wider than their stated
rationales, every discovered token is attributed and correctly located.* That is worth having. It is
not what the package claims, and the gap between the two is where a future change will hide.

---

## 5. Gate 4 — attestation and submission-status semantics

The positive requirements hold: the seal records submission status only, the inventory carries no
status field, the attestation path resolves to a real file holding a real record, and missing,
unresolvable or disagreeing attestations all block (F1–F4).

Two gaps (`evidence/gate4_attestation.json`):

- **The attestation's bytes are bound by nothing.** Its SHA256 `3eed58e1…4919a` appears nowhere in
  the candidate. It is outside the payload closure, is never swept for tokens or superseded
  literals (probe B8), and the only property checked is one string equality. The "sole authority for
  post-audit acceptance state" is an unbound external file.
- **The path can be redirected into the candidate itself.** Probe **F5** creates
  `SELF_ATTESTATION.json` *inside* the candidate namespace and repoints
  `post_audit_acceptance_state.authoritative_path` at it. The gate resolves it, reads it, agrees
  with it and passes. The detachment that gives the attestation its authority is asserted by the
  map's prose, not enforced by the gate — so the package can attest to its own acceptance state.

---

## 6. Gate 5 — package-preflight behaviour

Tested with 36 fixtures of my own construction (`evidence/probe_batch1-4.json`), including a
positive control: an unmodified staged copy passes (**G1**). Every mutation ran on a throwaway copy
under `/tmp`; after each probe the real candidate was re-hashed and confirmed byte-identical.

Probes rebind `PAYLOAD_HASHES.json` and the seal's `payload_inventory.sha256` after mutating a
payload — exactly what an implementer does when editing a declarative payload — so that probes reach
the single-source sweep instead of stopping at the closure check. This is the realistic threat model:
an author making a declarative edit and repackaging.

The implementer's fixtures were read **for coverage assessment only** and used as evidence for
nothing (`evidence/gate5_implementer_fixture_coverage.json`). All 13 cases assert behaviours the gate
implements, each written in a token-visible position. The suite is confirmatory, not adversarial: it
does not probe a single boundary of the mechanism it certifies. Thirteen boundary classes it does
not touch are enumerated in that file.

---

## 7. Gate 6 — conclusions resting on citation

The runner is byte-identical to the accepted V4 runner, verified three ways (SHA256, docstring-
stripped AST, and V5 comparison). The following therefore **rest on citation of the V4 audit
(`audit/v52-t4f1-v4-independent-2026-09-01` @ `641568d8…a26c`), not on my own re-derivation:**

- B1/B2/B3 implementation gates
- aggregation correctness
- authorization verifier behaviour beyond the fail-closed constants I checked statically
- leakage analysis of the retrieval path

What I **did** re-derive myself, and do not cite:

- byte and AST identity of the runner across V4/V5/V6
- the runner's module constants, by AST, and their agreement with every declarative payload (30/30)
- the pinned BEAM corpus: 205/205 selected blobs by git SHA-1 and size, 804,231,963 bytes, at commit
  `3e120355…2ef9`; manifest digest `650cc145…d318` matches the declared anchor
- authenticity of the V4/V5 audit packages and the V6 implementer preflight package
- the entire behaviour of the V6 gate, by construction

I did **not** invoke the runner CLI in any mode, including the permitted `--mode preflight`. The
delta route makes it unnecessary — the runner's bytes are already audited — and not invoking it is
the strictest available position with respect to the no-outcome boundary.

---

## 8. Gate 7 — active bug hunt

Each item the prompt asked me to hunt for, and what I found:

| Hunted | Found |
|---|---|
| A concept whose scannable literals omit its real value | **Yes** — 9 of 24 concepts declare none. Additionally the gate never checks `scannable_literals` against `value`, so a concept's stated value can drift freely (G5) |
| An exempt class wider than its rationale | **Yes — all three.** C1, C2, C3, C4, plus E5/G7 widening |
| A token pattern that misses a load-bearing constant | **Yes** — 56 of 72 value atoms; seeds, arms, tolerances, counts, thresholds all invisible (D1–D7) |
| An attestation satisfiable by a file the candidate itself writes | **Yes** — F5 |
| A gate that passes vacuously on an empty or malformed map | **Partly.** An emptied `fields` list blocks (E4), because the seal's own digests become unattributed. But a blanket exempt class produces a fully vacuous pass (E5), and a non-UTF-8 payload is skipped without being counted (B7) |
| *(found additionally)* Normalisation that destroys pattern boundaries | **Yes** — §4.1, the most serious finding |
| *(found additionally)* Deprecated literals disarmable by declaration | **Yes** — E8 |
| *(found additionally)* Declared mirrors never verified to contain the value | **Yes** — G2, G3 |

---

## 9. Mandatory boundary declarations

| Declaration | Value |
|---|---|
| CLI `--mode run` invocations | **0** |
| CLI `--mode finalize` invocations | **0** |
| CLI `--mode preflight` invocations | **0** (permitted; deliberately not used) |
| Runner CLI invoked in any mode | **false** |
| HMAC key environment set count | **0** |
| Valid production authorization constructed | **false** |
| Real retrieval ranking performed | **false** |
| Retrieval quality computed / read / reported | **false / false / false** |
| Candidate bytes modified | **false** |
| Pinned BEAM corpus modified | **false** |
| Sealed 4F0 namespace modified | **false** |
| Commands refused by the harness before launch | **3** (self-test of the `--mode run` / `--mode finalize` filter) |
| Delta route justified | **true** |

The subprocess harness (`evidence/safe_exec.py`) refuses, before launch, any command containing a
forbidden mode or carrying `V52_T4F1_AUTH_HMAC_KEY_HEX`; its self-test refusals are logged in
`COMMAND_LOG.txt`. No retrieval-quality quantity was computed, opened, printed, summarised or
inferred at any point, and no arm comparison was formed.

---

## 10. Blocking findings

Each of the following independently requires `BLOCKED` under the prompt's stated rule.

1. **Exempt classes wider than their rationales — all three** (§4.4). `inventory_self_hashes` exempts
   the whole `files[]` subtree, not just digests. `historical_provenance` exempts by string prefix,
   admitting keys no rationale covers. `artifact_identifiers` is a file-wide allowlist that includes
   the sealed-4F0 namespace identifiers, permitting an undetected substitution of the authoritative
   cohort source (C1, C2, C3, C4).
2. **Missing load-bearing concepts** (§4.8). `REAL_CANARY_QUERY` — the input from which the canary
   digests are derived, repeated in two files — and `TIERS` have no concept in the map.
3. **The gate's claim is not established** (§4.1–4.3, §4.6). The normalisation/lookaround defect
   makes value-shaped tokens invisible in ordinary prose contexts, including a live digest relocated
   to a file its concept does not permit (A3). Eight further evasion classes survive (B1, B3–B8).
   Five concepts covering the numerical core have no enforcement of any kind (D1–D7).
4. **The detached attestation is unbound and redirectable** (§5). Its bytes are hashed nowhere, it is
   never swept, and its declared path can be pointed at a file inside the candidate namespace (F5).

**Non-blocking observations.** No superseded literal survives in the shipped bytes under an
independent search stronger than the gate's own (NFKC-normalised, format characters removed, all
non-alphanumerics stripped, applied across the closure *and* the attestation): 0 survivors. No
numerical-semantic drift exists in the shipped bytes: 30/30 declared values match the runner. No
outcome-capable execution occurred, no valid authorization was constructed, and the candidate was
not mutated.

---

## 11. Recommended remediation for a V7

1. Do not normalise away the boundaries the patterns need. Either drop the hex lookarounds and
   deduplicate matches, or match on raw text and separately match a whitespace-stripped copy, taking
   the union. Add a fixture in which a planted digest is preceded by `probe` and followed by `and`.
2. Fail closed on a bound payload that cannot be decoded as UTF-8; never `continue` past it silently.
   Count what was skipped and block on a non-zero count.
3. Narrow the exempt classes to their rationales: key-path matching on **path segments**, not string
   prefixes; scope `inventory_self_hashes` to the `sha256` key specifically; remove the sealed-4F0
   namespace identifiers from `artifact_identifiers` and give them a concept of their own.
4. Verify the declaration, not just the discovery: assert that each concept's `scannable_literals`
   contain every token-shaped atom of its `value`, and that every declared mirror actually contains
   the value at the stated locator.
5. Extend coverage beyond hex: give seeds, arm names, tolerances, counts and thresholds declared
   literals and a pattern that can find them, or state plainly in `gate_claim` that they are out of
   scope. The claim must not exceed the mechanism.
6. Bind the attestation's SHA256 inside the seal, sweep it as part of the closure, and require its
   path to resolve outside the candidate namespace.
7. Remove the `must_not_appear_as_requirement` escape, or require a co-chair-signed justification.
8. Reduce `gate_claim` to what the gate actually proves.

---

## 12. Verdict

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

The delta route was justified and the runner is untouched, so nothing here impugns the accepted V4
implementation. V6's failure is confined to the new machinery, and it is the same failure V5 had in
a new form: a gate that prints a general guarantee it does not deliver. The correct reading of its
PASS is *"no violation was found in these bytes by these narrow means"* — which is true, and is not
what it says.

For the record, and independent of this verdict: V6 was prepared under Continuity Lead authority
alone and exceeds the standing co-chair approval `4bd32782`, which covered V5 only. Even a PASS
would have left sealing conditional on co-chair ratification.
