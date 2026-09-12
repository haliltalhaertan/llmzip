# G-3 remediation delivery — scoped synthetic candidate

**Latest delta:** Independent audit `2a025ee3b85f25af80e1b939f85f23c6cf06af30`
rejected the initial `24d3351f068f6982148c14a9e3338c29a2769449` candidate for
A1: an unsorted LongMemEval cohort misbound diagnostics to questions. The current
delta corrects the bridge to use the preparation's sorted global ordinal and adds
a real two-archive synthetic regression. The regression failed against the old
bridge; the updated full suite passes **54 methods / 5,961 subtest observations**.
`A1_REMEDIATION.md` and `evidence/a1_fixed/` bind the change. Independent delta
acceptance remains pending. Earlier `evidence/final` and inherited/provenance
receipts remain unchanged evidence for the initial candidate, not reruns of this delta.

This is a **G-3 successor candidate derived from Codex v5 and execution preparation
v1**, prepared for the user's cold-start independent scoped audit. It is not an
accepted execution package. G-3 acceptance, G-4, and production readiness are not
declared by this implementation team.

The recommended working line is **this G-3 successor for synthetic development and
review**, carrying v5's reviewed fixes forward instead of reverting to v4. This is
a written implementation-owner recommendation. It does not promote historical v5
ingestion to a conforming primary LoCoMo source, rewrite the ledger, or substitute
for the Head Researcher's disposition and independent acceptance.

## Authority and sources

- Delivery base: `4f2429b257546d6899f3ed48f605cd18210aeae0`, current main at dispatch.
  Later main `1d15fdd` (L-091, PR closure) is separately coordinated by the user.
- Original checkout: `work/llmzip`, branch
  `fix/g3-membership-remediation-2026-09-11`, HEAD
  `077474013d95d6f343d31385d8a57d42fb72f721`. Its checkout and index are preserved.
- Delivery clone: `work/llmzip_g3_delivery_20260912`, branch
  `codex/g3-remediation-delivery-2026-09-12`; GitHub origin
  `https://github.com/haliltalhaertan/llmzip.git`.
- G-3 grant: `b6b06e0c7e51089aa402dcdbddf03f692d690948`,
  `docs/v52/V52_G3_REMEDIATION_GRANT_HR_DECISION_2026-09-11.md`, raw SHA-256
  `533bf10ec66fa7ab225a60d43161e129791d0f168f7e0ab520ce0afc7f23548f`.
- Coordinatewise decision: `8671128a13877c97754da182421ba615422dd2ec`,
  `docs/v52/V52_OBLIGATION_1_AND_F3_N1_DECISION_2026-09-09.md`, raw SHA-256
  `03f5fe7d7ff838936bf8bc3bc4a406836613d611fefd94f79228cb8e2cbd4970`.
- Detailed seven findings and **exact nine gaps**: `5126766cac9201bbede178ccb558efa428f9488c`,
  `audit_v52_execution_prep_v1_review_2026_09_08/EXECUTION_PREP_V1_REVIEW.md`.
- Related four findings: `2cf602090a6c4c42dba44f66d95d8dfed0e0f2e8`,
  `audit_v52_codex_v5_repair_review_2026_09_08/CODEX_V5_REVIEW.md`.
- Main ledger L-080, L-081, L-082, L-083, L-089 and L-090 were read. L-082's
  corrected-gold/dual-reporting and sorted-global-ordinal decisions remain binding.

`RECOVERY_INPUT.json` records the 11 recovered input files, their byte counts and
SHA-256, the original status, and original index SHA-256.
`provenance/pre_edit/SNAPSHOT.json` checks the preserved pre-edit bytes against that
inventory. `verify_provenance.py` compares raw Git blobs and records recovery and
current diffs separately. The source chain core → v5 → preparation is checked;
these side-branch commits are **not claimed to be ancestors of the delivery base**.
The empty `authoritative/__init__.py` is inventoried for completeness and carries
no substantive byte-identity evidence.

## What changed

The connector validates both ingestion schemas and unique question ownership before
fitting, rejects empty cohorts/archives/records, and protects immutable-core record
diagnostics with wrapper validation. LongMemEval synthetic ordinals use the sorted
global cohort. No sharded production runner is introduced.

The certificate now checks **each archive and query code bit separately** against
an independent rational sign-code specification. Its 97 literal sign masks cover
96 singleton negations and all-96 negation; a nonidentity permutation is fixed as a
source literal from seed `52003107`, before any archive is observed. The seed is a
new synthetic certificate fixture choice, not an inherited scientific RNG setting.
Each member is tested directly with its own failures, including zero on either side
and jointly zero coordinates. The exact oracle does not call the numerical
transform helper. A separate test oracle independently uses rational values and
integer bit operations. This is algorithmic independence within implementation
testing, **not an independent audit of the package**.

Under this bit-transport contract, negating an exact zero deliberately fails: the
source bit should complement, but both `0.0 >= 0` and `-0.0 >= 0` are true. This
includes jointly zero coordinates, unlike the recovered mismatch-bit check. The
zero-threshold retrieval code itself is unchanged. The original reversal/alternating
aggregate canary is retained only as a regression. The adopted column-centered
96×96 N1 fixture has archive columns 0 and 2 zero and query entries +1 and -1; the
old canary accepts and the new certificate rejects it.

Matched-block checks inspect the blocks actually embedded in both rotations and
compare them with independently redrawn expected blocks. Substituting identity is
a negative control: it preserves norm/dot invariance but must fail this check.
Nuisance priorities are observed at every one of the 60 arm/seed calls.

G2's manifest-count diagnostics now require exact builtin integers at the runner
and ingestion sites. Error fields reject NumPy scalar objects and custom numeric
subclasses. **The two manifest-count fields are locally exact-type gated; this is
not a universal statement about all caller-derived values or all error surfaces.**
The old spoofed-enum mutant is required to fail the strengthened exception-type
test. `safe_report.counts` and the immutable core's path-bearing writer remain
historical limitations outside the general formatter claim; see audit triage.

## Reproduce the implementation evidence

Use the user's exact environment:

```powershell
$py = 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/.venvs/g3-lock-20260912/Scripts/python.exe'
$ns = 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/llmzip_g3_delivery_20260912/drafts/v52/membership_g3_remediation_2026_09_11'
$env:PYTHONHASHSEED = '0'
& $py -B "$ns/verify_provenance.py" --evidence-dir provenance/review-new
& $py -B "$ns/verify_delivery.py" --output evidence/review-new
& $py -B "$ns/run_inherited.py" --evidence-dir inherited/review-new
& $py -B "$ns/package_integrity.py" --ref HEAD
```

Output directories must be fresh. The launchers pin Python **3.13.15**, NumPy
**2.3.5**, SciPy **1.17.0**, scikit-learn **1.8.0**, pandas **2.2.3**, hash seed 0,
and numerical thread counts 1. They install nothing and do not alter the shared
environment. The user's separate runtime process/thread settings are untouched.
Observed test counts, exit codes and source hashes are in the JSON receipts; no
hard-coded test count supplies a pass. `TRACEABILITY.md` maps each requirement to
the implementing code, named tests, evidence, and limited disposition.

For a new Windows clone, use `git clone --no-checkout`, then set
`git config --local core.autocrlf false` **before checkout**. No global setting or
repository-wide attributes change is needed. The core hash gate is strict: CRLF
translation is refused, never accepted by normalizing a mismatch. The source
materializer uses raw Git bytes for inheritance. The core remains byte-identical
to `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72`.

## Disposition and remaining gates

Obligation 4 is implemented only as a **synthetic preparation/accepted-bootstrap
arithmetic/output bridge** with provenance and overwrite controls. Its evidence
does not prove provenance for real anchors, real corrected gold, or a production
connector. Obligation 5 is **partially addressed**: required synthetic negatives and
accepted-lock regressions are supplied. Real-ingestion-to-computation review,
independent acceptance, and pre-run sealing remain open; the latter actions are not
authorized here.

The LoCoMo v5 adapter remains raw-evidence based and non-conforming as a primary
source under L-082. Corrected 1,535/raw 1,540 dual-reporting reconciliation, actual
frozen-anchor binding and cohort identity, and production shard integration remain
outside this synthetic candidate. No corpus was accessed or scanned and no frozen
retrieval-quality result was replayed. Historical synthetic source regressions are
not frozen scientific outcome replay.

Python guards, closed schemas, hashes and refusing entry points provide the tested
checks. They are not an OS sandbox, a universal confidentiality guarantee, or a
defense against a caller with arbitrary Python execution. The direct inherited
runner/ingest mapping stamp and output APIs retain separately documented limits.

No experiment, pilot, production retrieval, finalization, seal, HMAC operation or
production authorization is performed or granted. Main, ledger/state, PR #2 and
runtime byte-cost work remain under the user's coordination.
