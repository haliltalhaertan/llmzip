# V52 Task 4F1 — Execution Candidate V4 Cold-Start Independent Audit

- Audit date (UTC): 2026-09-01
- Role: cold-start independent implementation auditor
- Audited namespace: `task4f1_execution_candidate_v4_2026_09_01/`
- Audit namespace: `audit_v52_t4f1_execution_candidate_v4_independent_audit_2026_09_01/`

## Verdict

`PASS — V4 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER; TASK 4F1 STILL NOT PREREGISTERED OR AUTHORIZED`

This verdict concerns only whether these exact V4 bytes may later be sealed by the Head
Researcher. It does not seal, preregister, authorize, execute or interpret Task 4F1.

## Mandatory boundary statements

| Statement | Value |
| --- | --- |
| CLI `--mode run` count | `0` |
| CLI `--mode finalize` count | `0` |
| HMAC key environment set count | `0` |
| Valid production authorization constructed | `false` |
| Real retrieval ranking performed | `false` |
| Retrieval quality computed / read / reported | `false` / `false` / `false` |
| Candidate bytes modified | `false` |

The subprocess harness (`scripts/guard.py`) rejects any command containing `--mode run` or
`--mode finalize` — including the split `--mode run`, `--mode=run` and finalize forms —
before launch, and additionally refuses any launch with `V52_T4F1_AUTH_HMAC_KEY_HEX`
present in the environment. Its three self-test refusals are the first entries in
`COMMAND_LOG.txt`. Every subsequent launch in that log is a package preflight, a candidate
`--mode preflight`, or an outcome-free reconstruction.

## Anchors verified

| Anchor | Declared | Observed |
| --- | --- | --- |
| implementation SHA256 | `f96cba2c…3621f8` | matches |
| `PAYLOAD_HASHES.json` SHA256 | `fe1de9c7…1ba5e` | matches |
| `CANDIDATE_EXECUTION_SEAL.json` SHA256 | `1bf740f5…8f06e9` | matches |
| `PREFLIGHT_HASHES.json` SHA256 | `4f78b5c8…1c930f` | matches |
| V3 runner SHA256 (preserved) | `0c1c1cc2…6b07c` | matches |
| dependency lock SHA256 | `86a4db44…66655e` | matches |
| BEAM tree manifest SHA256 | `650cc145…d8318` | matches |
| BEAM pinned commit | `3e120355…4b2ef9` | matches |
| restricted cohort SHA256 | `9b70e16f…12519a` | matches |
| sealed 4F0 seal SHA256 | `596c8056…82f859c` | matches |
| restricted protocol SHA256 | `f75e6c93…493cf1` | matches |
| candidate status | `PREPARED_NOT_INDEPENDENTLY_AUDITED` | matches |
| key commitment | `PENDING_HEAD_RESEARCHER_PREREGISTRATION` | matches |
| recursive file count | exactly 8, no nesting, no `__pycache__` | matches |

Cohort structure was recomputed from the bound CSV rather than read from any declaration:
2,000 rows, 1,712 eligible, 96 archives, excluded archives exactly `1M::5`, `1M::26`,
`1M::33`, `1M::34`.

## Audit posture

Every claim in the V4 candidate and in the implementer's preflight package was treated as
a hypothesis and independently re-derived. The V3 audit's conclusions were not imported;
its Gate 3 finding was reproduced from scratch. The Gate 3 representation was rebuilt by
reimplementation from the audited specification — the candidate module was not imported
for that reconstruction — and only afterwards compared against the candidate's own output.
Carrying the B1/B2/B3 repairs forward was not treated as evidence that they survived the
edit; each was re-tested against V4 directly.

## Environment

The audited environment reproduces the dependency lock exactly: Python 3.12.13, NumPy
2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, with all five declared single-thread
controls and `-B` / `PYTHONDONTWRITEBYTECODE=1`.

One provenance note, recorded because it is a deviation in *how* the interpreter was
obtained rather than in *what* was run: the container shipped CPython 3.12.3 and no
prebuilt 3.12.13 was available from the local toolchain's index, so 3.12.13 was built from
the official python.org source tarball. The pinned packages were installed from PyPI at
their exact locked versions. The BLAS backend is `scipy-openblas 0.3.30` built
`DYNAMIC_ARCH`, which is what makes `OPENBLAS_CORETYPE` a genuine kernel-dispatch switch
and therefore what makes Gate 3 testable at all.

The corpus was materialized independently: 192 files (779,151,469 bytes) covering all 96
cohort archives, each verified against the git blob SHA1 and size recorded in the accepted
pinned-tree manifest before use.

## Gate results

All gates pass. `GATE_TABLE.csv` carries the per-gate summary; the machine-readable
evidence is under `evidence/`.

### Gate 1 — recursive byte closure and bindings

The candidate is exactly eight files with no nested directory and no bytecode. Six payloads
are bound by `PAYLOAD_HASHES.json`, the inventory is bound by the seal, and the
implementation hash is bound by the seal. The candidate's own package preflight passes on
the real bytes. In temporary copies only, a nested unbound file, a mutated bound byte and
an injected `__pycache__` were each rejected. The real candidate was byte-identical before
and after every test in this audit.

### Gate 2 — V3-to-V4 change isolation

Across 38 top-level definitions: 36 AST-identical, two changed beyond schema literals
(`real_archive_canary`, `verify_environment`), two added (`sign_code_sha256`,
`describe_numerical_backend`), five changed only in a schema version string literal
(`verify_execution_seal`, `evaluate_archive`, `verify_existing_archive`,
`finalize_results`, `preflight`), none removed. Constants: the two raw-float canary
expectations removed, the two sign-code expectations and `CANARY_SIGN_MARGIN` added, and
`AUTH_SCHEMA` bumped V3→V4.

Every one of these falls inside the permitted surface, and the set of changes outside that
surface is empty. All 25 numerical and estimand core definitions — representation fitting,
query transformation, archive evaluation, Native/signed/Haar/ITQ algorithms, tie priority,
trial generation, metric definitions and the authorization verifier — are unchanged, as are
all 30 core constants including every seed, dimension, threshold, tolerance and cohort
expectation. There is no numerical or estimand drift.

Two version bumps deserve explicit note because they are load-bearing in the right
direction: `AUTH_SCHEMA` V3→V4 means a V3-shaped authorization cannot be replayed against
V4, and the archive-result metadata schema bump means V3 checkpoints cannot be substituted
into a V4 finalization. Both were confirmed by test.

### Gate 3 — canary dispatch stability

This is the gate V3 failed, and it is the one this audit weighted most heavily. All eight
required sub-findings were established independently rather than assumed.

The reconstruction yields 392 archive units with shapes `[392, 96]` and `[1, 96]` on every
dispatch, from an archive blob verified against the pinned manifest
(`bbabe6fc…bbcfa`, 964,208 bytes). The recomputed sign digests equal the candidate's two
declared constants exactly:

- archive `7365b6c4ba7753ee5431f89816c3151a2618f475415024d8932c839609ded5b5`
- query `5e40a5d1f0d33bf16c4005ed8aa172464dd1fb205da983f5373c9940f4ccad2b`

Across `SkylakeX`, `Haswell`, `Nehalem`, `Sandybridge`, `Zen` and `Barcelona` the sign
digests are identical in all six, and the candidate's own `--mode preflight` passes in all
six.

The gate is demonstrably not vacuous. The raw float digests over the same six dispatches
fall into four distinct groups — `SkylakeX`; `Haswell` = `Zen`; `Nehalem` = `Barcelona`;
`Sandybridge` — independently reproducing the four-digest spread the V3 audit reported.
The floats genuinely move; the signs do not.

The sign-stability margin was measured, not accepted:

| Quantity | Measured |
| --- | --- |
| Max cross-dispatch absolute difference | `1.2018e-13` |
| Min absolute representation value | `4.0888e-07` |
| `CANARY_SIGN_MARGIN` | `1e-09` |
| Min value ÷ required margin | `409x` |
| Min value ÷ observed noise | `3.40e6x` |
| Required margin ÷ observed noise | `8320x` |
| Entries inside the numerical noise band | `0` of 37,728 |

The guard band is well placed: observed noise sits roughly four orders of magnitude below
the required margin, which in turn sits roughly two and a half orders below the nearest
actual value. No entry is anywhere near a sign flip.

The canary remains outcome-free. Statically, its transitive call graph is exactly
`load_archive`, `fit_archive_representation`, `transform_queries`, `sign_code_sha256` and
their helpers — no ranking, metric, gold or question-loading function is reachable. By
observation under a runtime audit hook, the canary opened exactly one corpus file,
`chats/100K/12/chat.json`, and zero probing-question or cohort files.

`describe_numerical_backend` is provenance only. It records the coretype environment value,
the platform machine, and the BLAS/LAPACK name and version; it gates nothing; and its only
plausible failure source is wrapped, which was confirmed by forcing `np.show_config` to
raise and observing graceful degradation to `"unavailable: RuntimeError"` rather than a
failed run. It reads no secret.

### Gates 4–7 — B1, B2, B3 and aggregation

Re-derived against V4 with fully synthetic fixtures; 41 of 41 cases behaved as required.
The scale constants were reduced inside the test harness so the finalizer's guard logic
could be exercised end to end; the real-scale constants themselves were confirmed unchanged
by the Gate 2 AST comparison and are enforced by the cohort loader.

B1 holds: every derived destination and every corresponding `.tmp` path blocks before any
byte is changed, sentinels survive intact, a partial derived set blocks rather than being
repaired, and rerunning after a successful finalization blocks. The commit is genuinely
exclusive rather than a bare early `exists()` check — the temporary is created with
`open("x")` and the destination is claimed with `os.link`, which was confirmed to refuse an
existing destination and leave its bytes intact. Hard-link commit is used on a POSIX
filesystem here; on a filesystem without hard-link support this path would need
re-examination, which is noted as a platform classification, not a defect of these bytes.

B2 holds: all three metrics are recomputed from canonical retrieved IDs and frozen gold at
every cell, and 17 distinct tamper classes all block — including metrics altered in both
directions, structural ALL@3 zero forced to one, reordered and changed IDs, duplicate,
non-string, non-canonical and Boolean IDs, NaN, infinite and out-of-range metrics, gold
cardinality inconsistency, and unsorted, negative, oversized or Boolean distances.

One test in the first pass did not block. On inspection the fault was in my fixture, not
the candidate: the row I mutated already carried `all_at_3 = 1`, so the "tamper" was a
no-op. Corrected to a genuine ALL@3 inversion in each direction, both cases block as
required.

B3 holds: signed-permutation cells must carry exactly the Native ordered top-three IDs and
exact distances, and divergence in ID membership, ID order or any distance blocks even when
all metrics remain equal. Missing and duplicate cells block. A trial-varying payload under
fixed priority blocks. Native-versus-control question-level metric equality remains as a
redundant final guard.

Aggregation holds: 320 trial rows per eligible question, 16 question-seed rows, four
question-method rows and four aggregate rows per question set, with correct method and seed
coverage and sorted integer Hamming distances. The aggregates reproduce an independently
recomputed equal-question-weighting mean exactly, and the trials are treated as
deterministic replication identities rather than independent statistical units.

### Gate 8 — active bug hunt

The three V4-specific hypotheses were tested directly and none held.

The sign-code path cannot be used to launder a representation change. My independent
baseline reproduces the sealed canary, and every one of seven realistic perturbations —
latent seed, mixed seed, latent dimension, `sublinear_tf`, stop words, word n-gram range,
character n-gram range — changes the archive sign digest. Binding 37,728 sign bits is a
weaker constraint than binding raw float bytes, but it is the constraint that actually
governs Hamming retrieval: the runner computes `centered >= 0` for both documents and
queries, which is precisely what `sign_code_sha256` digests. Combined with the Gate 2 proof
that the numerical core is unchanged and the seal's hash binding on the script itself, a
laundered representation would have to alter the script — which breaks the seal and the
authorization binding — while preserving every one of those bits.

`CANARY_SIGN_MARGIN` cannot be trivially satisfied by a degenerate representation. A
degenerate archive is refused upstream by the fit's own preconditions before any margin is
computed, and a constant matrix that clears the margin comfortably still fails the sign
digest. The margin is a supplementary guard, not the gate.

Backend provenance cannot leak an environment secret into an output. The backend helper
reads exactly one environment key, `OPENBLAS_CORETYPE`. `AUTH_HMAC_ENV` is read at exactly
one site, inside `verify_run_authorization`; the secret never appears in that function's
return value, no output-writing sink is called inside it, and no output writer references
the secret names at all. Provenance records only a hash of the authorization file.

Alternative checkpoint and finalization substitution was also probed: only the exact V4
checkpoint is accepted, while a V3-schema replay, a checkpoint bound to a different script,
one claiming console outcomes, one exceeding the invariance tolerance, one with a wrong
trial-row count, and a valid checkpoint verified under different provenance all block.

### Authorization boundary

With the HMAC environment absent throughout, eleven invalid fixtures were put to the
verifier and none was accepted. Because the sealed key commitment is the literal
`PENDING_HEAD_RESEARCHER_PREREGISTRATION` rather than a 64-hex digest, verification fails
at `HEAD RESEARCHER AUTHORITY KEY NOT SEALED` before any secret is read — the candidate is
cryptographically fail-closed in its current state. A temporary-copy seal carrying a
syntactically valid but non-production commitment fails at `HEAD RESEARCHER AUTHORITY KEY
MISSING`, confirming the environment-absent branch. No valid production authorization, HMAC
key, key commitment or preregistration seal was constructed at any point.

## Non-blocking observations

These do not affect the verdict and require no change before sealing. They are recorded so
the Head Researcher can decide whether to absorb them into a later revision.

1. `candidate_package_preflight.py` still carries a docstring describing it as the preflight
   "for the Task 4F1 V3 candidate", although it correctly enforces the V4 seal schema.
   Cosmetic staleness in a comment.
2. `RUN_AUTHORIZATION_TEMPLATE.json` still declares
   `V52_T4F1_RUN_AUTHORIZATION_V3_TEMPLATE_ONLY` and mentions V3 in its note. The template
   is non-authorizing by construction, and the stale schema makes it strictly more
   fail-closed rather than less, but the label no longer matches `AUTH_SCHEMA`.
3. The canary cannot distinguish a `>= 0` threshold from `> 0`, because no entry of this
   archive's representation is exactly zero (the minimum absolute value is `4.09e-07`). The
   threshold is nonetheless pinned by the Gate 2 AST equality of the ranking and evaluation
   code and by the seal's recorded interpretation, so this is a scope limit of the canary
   rather than a gap in the bindings.
4. Derived-output commit relies on `os.link`. This is correct and exclusive on POSIX
   filesystems, and was verified as such here; a filesystem without hard-link support would
   need this path re-examined.

## Conclusion

The V4 candidate preserves the sealed 1,712-question BEAM restricted-cohort protocol,
carries the B1, B2 and B3 repairs through the edit with each re-verified directly against
V4 rather than inherited from the V3 audit, and correctly remediates the V3 blocking defect
G3. The load-bearing canary is now lock-bound rather than machine-bound: it binds the sign
codes that actually drive Hamming retrieval, those codes are invariant across six BLAS
kernel dispatches whose raw float outputs demonstrably differ, and the sign-stability margin
was independently measured with several orders of magnitude of headroom on both sides.

No unresolved B1/B2/B3 behavior, canary dispatch instability, unconfirmed sign margin,
alternative load-bearing checkpoint or finalization substitution, numerical-semantic drift,
outcome-capable execution, valid authorization construction or candidate mutation was found.

`PASS — V4 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER; TASK 4F1 STILL NOT PREREGISTERED OR AUTHORIZED`
