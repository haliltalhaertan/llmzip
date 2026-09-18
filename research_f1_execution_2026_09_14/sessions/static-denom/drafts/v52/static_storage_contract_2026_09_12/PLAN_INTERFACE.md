# Frozen storage PLAN interface (schema 1)

This is a stdlib declaration, callback-boundary and coverage guard. **No actual
projector adapter or real measurement runner is integrated. F4 real adapter
integration remains OPEN.** Synthetic tests use temporary toy contracts and
declarations plus a dummy callback. They prove validation before callback I/O and
observation checks; they do not prove projector persistence, necessity ablations,
ID mapping correctness, cost completeness, or production runtime enforcement.

`MEASUREMENT_PLAN.template.json` deliberately has `NOT_READY`, `UNKNOWN` hashes
and identities, and empty inventories. It cannot run even if its exact bytes have
a matching external hash. No real archive IDs or N_i have been invented. Filling
the template requires a separately reviewed inventory and external freeze record.

## Freeze and authority

Freeze the complete ordered plan before observation. Record its exact raw-byte
SHA256, exact contract-byte SHA256, run identity, scope and authorization in an
external record. Supply the expected plan SHA256 from that record, not a digest
recomputed from an untrusted plan immediately before running it. Whitespace and
line endings are significant. A contract edit requires a new binding and freeze.
Hashes prove identity, **not authenticity, authorization, approval or freeze
chronology**. Anyone who can replace both a file and the expected digest can
replace the declaration. This module cannot verify the external freeze ceremony.
`analysis_mode` is explicitly PREDECLARED or EXPLORATORY. PREDECLARED requires
`parent_plan_sha256=null`; EXPLORATORY requires the prior plan's lowercase SHA256
and a separately frozen run. Both fields travel through requests, finalize and
the complete claim/caption. The guard verifies the hash shape and preserves the
label; it cannot establish the parent's existence, distinct run identity across
files or truthful chronology without an external registry.
No seal/HMAC, run authorization, historical namespace update, model fitting,
real corpus/query/gold read, retrieval or scientific result is created here.

## Lifecycle API

```python
from measurement_plan_guard import (
    load_plan, expected_requests, guarded_probe, finalize, make_claim,
)

# external_hash comes from the separately frozen external record.
plan = load_plan(plan_path, external_hash, contract_path)
rows = []
for request in expected_requests(plan):
    rows.append(guarded_probe(
        plan_path, external_hash, contract_path, request, trusted_dummy_callback,
    ))
coverage = finalize(plan_path, external_hash, contract_path, rows)
```

`load_plan(path, expected_sha256, contract_path)` reads at most 1 MiB + 1 byte of
the plan and checks the external lowercase SHA256 **before JSON parsing, contract
reading or any callback**. It then hashes the exact contract bytes and validates
schema and all references. It opens no path declared inside JSON. The returned
frozen `Plan` holds bytes; `.data` returns a detached dictionary. Missing/unreadable
files raise normal filesystem exceptions; declaration failures raise
`PlanValidationError`. All exceptions must stop the run; do not skip invalid rows.

`expected_requests(plan)` returns the complete ordered panel: probe order, then
configuration order, then each configuration's format order. Every configuration
and its declared formats occur at every probe for every archive. There is no
subset-selection argument. A request contains `run_id`, the full `archive` and
`format` records, `config_id`, the full `probe` and `fixture` records, and ordered
`items`, `physical_copies`, `populations`, `operations`, `controls`, plus explicit
`analysis_mode` and `parent_plan_sha256`. Physical copies
are filtered to archive/config/format, populations to probe, controls to config.
Copy records retain their complete snapshot population references.

`guarded_probe(plan_path, expected_sha256, contract_path, request, measure_callback)`
reloads and validates the files on **every call**, then requires exact request
membership, including N_i, N/q, dtype/serialization, item reasons/dispositions,
fixture, operations, control states and physical identities. JSON object key order
does not matter; array order and numeric representation do (a float is not an
integer declaration). Only then does it call trusted Python code with a detached
request. After the callback it rechecks the files and validates the returned
observation against the original request. Mutation in the callback cannot change
the expected declaration. Callback exceptions propagate. Invalid output is never
returned as accepted output. Postflight rejection cannot undo I/O already performed.

The callback must return exactly:

```text
{
  "request": <exact request received>,
  "items": [
    {"item_id": <id>, "disposition": <planned disposition>,
     "format_id": <planned format id>,
     "physical_copy_ids": <ordered copy ids for this item/request>,
     "bytes_before": <nonnegative integer or null>,
     "bytes_after": <nonnegative integer or null>}
  ],
  "controls": [
    {"control_id": <id>, "outcome": <planned expected_outcome>,
     "reference_identity": <planned reference_identity>}
  ]
}
```

Items and controls must occur exactly once, in declared order. Included items
require integer bytes; excluded and UNKNOWN items require `null`, never zero.
Included bytes describe logical serialized lengths in the declared boundary;
the guard checks the envelope and numeric domain, not a filesystem measurement.
For INCLUDED items with `cost_scope=SHARED`, the frozen-model contract additionally
requires `bytes_before == bytes_after` within each probe. Both growth and shrinkage
are rejected by guarded_probe and finalize. N-dependent container/header overhead
is not frozen SHARED model state: declare it separately in the count-dependent
PER_VECTOR boundary. PER_VECTOR sizes may change; acceptance is not proof of a
marginal law or budget eligibility. Equal SHARED sizes do not prove equal contents
or artifact hashes. Actual snapshot/content hash verification remains a future
adapter obligation and OPEN; this guard validates reported size equality only.
An optional component actually serialized inside this boundary remains INCLUDED
even if every removal control matches. Ablation success does not authorize byte
exclusion. Source absence is UNKNOWN, never an observed zero or an exclusion.

`finalize(plan_path, expected_sha256, contract_path, observations)` reloads the
plan/contract, validates all envelopes again and requires the exact complete
ordered probe key set `(archive_id, config_id, format_id, probe_id)`. Missing,
duplicate, extra, reordered or exploratory rows raise an exception; no partial
coverage is reported as PASS. Complete coverage returns `COMPLETE` only for a
READY declaration, or `PARTIAL` for SCOPED_PARTIAL, with UNKNOWN item/control IDs,
hashes, run identity and fixed weighting. These labels describe guard coverage,
not scientific validation. An unresolved inventory can have complete probe
coverage and still be PARTIAL. Exploration requires a separate frozen plan/run.

The per-call API is stateless: it does not schedule calls, persist a run ledger or
prevent a caller from invoking a valid request twice. Duplicate results cannot
finalize; the caller must stop on exceptions and retain every observation. A
future runner must enforce single dispatch, durable observation retention and
downstream budget checks. This guard is not a sandbox: a trusted callback could
ignore its request, fabricate observations or access data independently. No JSON
string is evaluated, imported or executed. Concurrency/OS-level file locking,
TOCTOU guarantees and authentication are not implemented.

## Schema 1 records (exact fields; no extension keys)

Top-level fields are `schema`, `version`, `status`, `contract_sha256`, `run_id`,
`analysis_mode`, `parent_plan_sha256`, `weighting`, `archives`, `formats`, `configurations`, `probes`, `items`,
`populations`, `physical_copies`, `fixtures`, `operations`, `controls`.
Schema is `v52.static-storage-plan`, version is integer `1`. Executable statuses
are `READY` and `SCOPED_PARTIAL`; any UNKNOWN item/control requires SCOPED_PARTIAL.
IDs must be nonblank, unique within their inventory and not the literal UNKNOWN.
All inventories except physical_copies are nonempty. Each array has at most 1024
records, the expanded panel at most 4096 requests, JSON depth at most 24, strings
at most 4096 characters and numeric values at most 2^63-1 in magnitude. Files are
at most 1 MiB. Duplicate JSON keys and nonfinite numbers are rejected.

| Record | Exact fields and constraints |
| --- | --- |
| weighting | `primary="archive_weighted_mean_i(C_i/N_i)"`, `secondary="vector_weighted_sum_i(C_i)/sum_i(N_i)"`; never interchangeable |
| archives | `id`, positive integer `N_i`; complete ordered real roster must come from a future authorized inventory |
| formats | `id`, nonblank known `serialization`, `dtype`, `representation` = REAL / SURROGATE / EXPLICIT_CONVERSION |
| configurations | `id`, ordered nonempty unique `format_ids`, ordered nonempty unique `item_ids`; all declared items/formats must be used |
| probes | `id`, `archive_id`, nonnegative integer `N`, positive integer `q`, `fixture_id`; every archive has a probe; archive/N/q triples unique |
| items | `id`, `role`, `disposition` = INCLUDED / EXCLUDED / UNKNOWN, nonblank `reason`, `cost_scope` = PER_VECTOR / SHARED / UNKNOWN, `source_identity`, `exclusion_basis` |
| populations | `id`, `archive_id`, `probe_id`, `phase` = BEFORE / AFTER, `count`, `member_ids_sha256`; exact one per probe/phase; count equals N or N+q |
| physical_copies | `id`, `item_id`, `archive_id`, `config_id`, `format_id`, `artifact_identity`, `artifact_sha256`, `population_ids` |
| fixtures | `id`, `kind="SYNTHETIC"`, `sha256`, `generator_identity`; every fixture used by a probe |
| operations | `id`, `kind` = TRANSFORM / ID_MAPPING, `implementation_identity`; both kinds required |
| controls | `id`, `config_id`, `operation_id`, `scope`, ordered `item_ids`, `action`, `expected_outcome`, `reference_identity`, `applicability`, `na_reason` |

Dtypes: uint8/int8/uint16/int16/uint32/int32/uint64/int64/float16/float32/float64,
bytes, utf8, mixed. Serialization names are declarations, not plugins. A composite
mixed package needs its declared serialization identity to specify its layout;
this guard does not inspect dtype/shape from model files. Source and implementation
identities must resolve externally; the guard does not fetch them. Known items
require known source identity and cost scope. UNKNOWN source items may declare a
known SHARED scope for structural probes; an unknown scope is conservatively
treated as potentially per-vector for cap claims.

EXCLUDED requires `exclusion_basis=NOT_REQUIRED` or `EXTERNAL_BOUNDARY`; other
dispositions require null. NOT_REQUIRED means dispensable in the declared panel
and requires MATCH on every PER_ITEM REMOVE control. EXTERNAL_BOUNDARY means a
declared dependency outside this package, not a minimality claim; its removal
may legitimately fail. Runtime/text dependencies are never reclassified as
dispensable merely because they are outside the accounting boundary. INCLUDED
does not assert necessity: optional serialized bytes still count. The free-text
reason explains the boundary/source evidence; the guard cannot establish it.

Schema 1 deliberately models **archive-local whole-snapshot populations only**.
Population hashes identify ordered synthetic member IDs but are not recomputed
by this module. BEFORE at N=0 is legal; no amortization at zero is performed.
Original N_i remains positive and distinct from synthetic probe N. Each INCLUDED
item requires at least one physical copy per archive/config/format. Each copy
references all before/after populations of that archive. Distinct physical copies
can have equal hashes; duplicate physical artifact identities are forbidden.
`artifact_sha256` binds the declared source artifact, not both changing snapshot
files. UNKNOWN items may have no physical copy because their source is unresolved.
Partial group/global/overlapping sharing, fractional allocation and deduplication
proofs need a separately reviewed schema/adapter; do not relabel them archive-local.

For every configuration and operation, controls must include a BASELINE state
(`scope=BASELINE`, `action=BASELINE`, empty item_ids), REMOVE/RESTORE/CORRUPT for
each INCLUDED **and** EXCLUDED item (`scope=PER_ITEM`), and all three actions on
the combined ordered known-item roster (`scope=FALLBACK_COMBINED`). This freezes
combined fallback states as well as individual necessity probes. UNKNOWN items
are not silently inserted into known-item ablations. `expected_outcome` is MATCH,
DIFFERENT, FAILURE, UNKNOWN or NA. Baseline and RESTORE must MATCH in READY;
UNKNOWN is allowed only with SCOPED_PARTIAL and prevents a within-cap verdict.
FAILURE/DIFFERENT baseline or RESTORE declarations are rejected, even in partial
plans. Negative expectations remain available for REMOVE/CORRUPT as appropriate.
UNKNOWN control evidence keeps the result PARTIAL.
`applicability=APPLICABLE` requires `na_reason=null` and a non-NA outcome.
`applicability=NA` is allowed only for CORRUPT, requires `expected_outcome=NA` and
a nonblank known `na_reason`. NA is an explicit justified non-applicability
declaration, not UNKNOWN; it does not alone force PARTIAL. Baseline, REMOVE and
RESTORE cannot be NA. The observation echoes outcome NA and the frozen request
retains its reason. The guard checks presence/consistency, not the reason's truth.
`reference_identity` names the preassigned synthetic comparison/reference state.
An adapter must resolve that reference and implement the intervention faithfully.

TRANSFORM means a synthetic input transformation only. ID_MAPPING means a
**fake, preassigned ID→payload mapping**, never search, distance, ranking or real
retrieval ID output. These are static data declarations, not executable adapters.
The test dummy echoes identities and control outcomes; it does not demonstrate
that removal/restoration/corruption was actually executed. Independent source
inventory and real adapter verification remain necessary.

## Coupled claims and fixed headline

`make_claim(plan, config_id, format_id, marginal_bytes_per_vector,
archive_costs=None, *, lower_bound_verified=False)` returns one structured object
and a `sentence` coupling margin, cap verdict, UNKNOWN item/control IDs,
effective_total_status and lower_bound_label. Publish the complete object or its
complete sentence; extracting a cost field alone drops required qualifications.
The helper validates the frozen snapshot; use fresh `load_plan` and `finalize`
before reporting results. It can also render a declared/unresolved cost before
measurement; it is not a certificate that supplied costs were measured.

`archive_costs`, if supplied, is the exact ordered full list of
`{"archive_id": ..., "N_i": ..., "C_i": ...}` for one config/format. No omitted,
extra, duplicate or reordered archive or changed N_i is accepted. The primary
is always **mean_i(C_i/N_i)**; secondary is sum_i(C_i)/sum_i(N_i). No selector,
alternate headline or subset weighting is exposed. The toy tests use archive
ratios 10 and 20: primary 15, secondary 18, so swapping formulas cannot pass.

Shared UNKNOWN permits a declared-margin cap comparison while forcing effective
total UNKNOWN. `lower_bound_verified=True` explicitly marks **all supplied costs,
including the margin**, as caller-verified LOWER_BOUND. It is not merely a flag
that an unrelated lower bound exists. The flag keeps costs LOWER_BOUND even when
the roster is fully known; a lower bound never becomes a full total on that basis.
The caller must have verified allocation/deduplication. This intentionally small
interface uses one cost-kind flag; when a caller has an exact margin plus an
effective lower bound, separate fully qualified claims can express the two input
kinds without mislabeling either. Without that attestation, unknown total numbers
are suppressed. A potentially per-vector UNKNOWN blocks a
definitive within-12 verdict. A verified marginal lower bound already above 12
can return EXCEEDS_12. A <=12 lower bound cannot establish eligibility.
Unknown control evidence also prevents a within-cap verdict. `headline_full_total`
is null for UNKNOWN/LOWER_BOUND. No lower bound is promoted to a full total.

Costs, scope completeness, absence of omitted serialized bytes, physical-copy
truth, allocation and the lower-bound attestation are caller evidence obligations,
not established by this helper. It does not infer a general marginal law from
finite differences, calculate a projector total, prove necessity from successful
echo controls or authorize downstream matched comparisons. A future real adapter
must reconcile serialized bytes and enforce the <=12 runtime precheck before
the protected downstream operation. **That integration remains OPEN.**

## Reproduce only the synthetic tests

From this directory, use the supplied environment, with bytecode disabled:

```powershell
& 'C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\.venvs\g3-lock-20260912\Scripts\python.exe' -B -m unittest -v test_measurement_plan_guard
```

The tests read this template and use tempfile toy fixtures for plans/contracts.
They import no real model/data code, execute no JSON-provided code and read no
secret. They write nothing in the repository. Past review reports, published
namespace history, source bindings and FILE_HASHES.json are outside this work.
