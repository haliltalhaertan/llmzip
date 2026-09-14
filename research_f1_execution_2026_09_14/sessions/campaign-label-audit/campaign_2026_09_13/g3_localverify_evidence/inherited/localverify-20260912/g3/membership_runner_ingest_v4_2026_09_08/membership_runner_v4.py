"""Corpus-bound runner v4 for the V52 membership-under-scaling experiment - PREPARATION ONLY.

STATUS: [IMPLEMENTATION PREPARATION - NOT AUTHORIZED TO RUN ON REAL DATA; NOT INDEPENDENTLY REVIEWED]

The lineage: v2 answered D-2, D-3, D-4, D-5 and D-6 of the independent review at
audit/v52-runner-ingest-review-2026-09-08 @ 8c8ba7aefe2622efb4fbf65230f04dbfbec25449 (report sha256
456645a61c7e44148ee454287e7db0e66adfa128539b17679ce1c94897764676, verdict FAIL). v1 is left
byte-unchanged at drafts/v52/membership_runner_v1_2026_09_08/.

WHAT CHANGED, AND WHY EACH WAS A DEFECT RATHER THAN A PREFERENCE:
  D-2  `compute_results` accepted a replicate count that contradicted the frozen seed record, so a
       result computed from 7 replicates was persisted claiming 10000. Now refused.
  D-3  the ACCEPTED seed values governed nothing - seed 999 was accepted where 52001107 is the
       accepted value. Seeds and replicate counts now resolve from `authoritative/`.
  D-4  the expected manifest hash was an arbitrary caller argument, and the on-disk bytes of a
       default Windows checkout do not match the accepted blob hash. Manifests now resolve from
       Git's original bytes through `authoritative/resolve_sources.py`.
  D-5  exception messages interpolated values verbatim and unbounded. Every message now goes
       through `safe_report`, which reports type, shape and digest and never content.
  D-6  the N-4 inheritance assertion compared caller-supplied echoes by VALUE and was connected to
       nothing. `apply_archive_transform` now stamps what it actually used, and the assertion
       checks that stamp.

This module wires the independently closed computation core to a data source. It does NOT read any
corpus. Every corpus-touching entry point calls `core.require_real_data_authorization()` first, which
refuses by default, and the only adapter shipped here is synthetic.

WHAT THIS FILE ADDS OVER THE CORE, AND WHY EACH PIECE EXISTS
------------------------------------------------------------
The core was audited against the design text. It assumes its inputs are already trustworthy: it
accepts string OR integer cluster labels, and it coerces question ids with `str()`. Two observations
from the closure check of v2 (branch audit/v52-membership-v2-closure-2026-09-07 @ 712412a5) say that
those assumptions do not survive contact with a data source:

  NEW-4 - `None` and `NaN` are rejected by the core, but the empty string, a whitespace-only string,
          and the literal strings "nan" and "None" are accepted as ORDINARY DISTINCT cluster labels.
          A label column read from CSV or JSON commonly renders a missing value as exactly one of
          these.
  NEW-5 - two labels that are distinct objects but equal under `int()` are merged into one cluster.

Neither is a defect in the core against the finding it answers, and neither was a closure blocker.
Both are defects at the INGESTION boundary, which is this file. So identity validation lives here,
BEFORE anything reaches the core, and the core is left byte-unchanged.

The failure they cause is silent. It is NOT true that a missing conversation id necessarily produces
a visible extra cluster: several missing ids collapse into ONE pseudo-conversation, a missing id that
happens to equal an existing one is absorbed into it, and an id that is merged under `int()` reduces
the count. The honest statement is that **the grouping can be corrupted silently**, with the total
cluster count unchanged, which is why a count check is not accepted as sufficient here.

THE FIVE OBLIGATIONS THIS FILE DISCHARGES
-----------------------------------------
  N-2  the bootstrap seed is FROZEN to a record before any result is computed, and real-data mode
       refuses to start without that record;
  N-3  the LongMemEval inheritance tag is carried into every output, and the conversation-cluster
       bootstrap is REFUSED for LongMemEval;
  N-4  the centering vector and the scaling matrix D are learned from the ARCHIVE ONLY and the
       identical objects are applied to the query, with nothing estimated from the query;
  NEW-4 / NEW-5 identity validation, described above;
  the output schema, the refusal to overwrite and the real-data gate are carried through the
  integration rather than left in the core where no caller reaches them.

WHAT IS NOT CLAIMED. No claim is made that any wrong ingestion is necessarily caught. What is checked
is a named input schema, a closed set of rejected identifier shapes, a six-check source-identity
contract over the ACCEPTED mapping, and the named fault variants in the negative tests.

ON CONTENT IN MESSAGES - an inventory, not a claim.

Three absolute claims have been written in this lineage and all three were falsified by independent
check. v1: content is "never printed, logged, put in an exception message, or written to disk". v2:
"no value is interpolated into any message in this module". v3: "every message here is built by
`errors.message`" and "A string cannot enter a message without first raising `UnsafeErrorField`" -
false, because the identifier validators were still on `safe_report` while the sentence described
the conversion as total. So no fourth universal sentence is written here.

What is stated instead is which interfaces were checked, and how:

  * `errors.py` is the only message builder used by the configuration, manifest, seed, cohort and
    output paths. It admits numbers, booleans, None and enum members validated against a closed set.
  * The identifier validators (`validate_identifier`, `validate_identifier_columns`) and the source
    identity contract also build through `errors.py`; `kind` is a member of `IdentifierKind`, a
    closed enumeration, not a caller string.
  * `safe_report` is still used where a value must be DESCRIBED rather than named - type, shape and
    a 12-hex digest, never the value.

Error paths exercised by the tests, on this module: the nine of F12-F20, the two the v3 closure check
found (`validate_identifier`'s kind, and the manifest `n_questions` conversion), and the identifier,
seed, mapping and result-schema refusals. The surface captured for each is the exception message, its
repr, the `__cause__`/`__context__` chain, stdout, stderr and every file written.

Untested and therefore unclaimed: anything a caller does with what it is handed, and any message
written in future without this interface.

Governing documents, the audited core and the review chain are bound by commit, path and sha256 in
`GOVERNING_AND_LINEAGE.md`. Read them from `main`, hashing RAW GIT BLOBS.
"""
from __future__ import annotations

import hashlib
import json
import sys
from enum import Enum
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "membership_impl_v3_2026_09_07"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import membership_scaling_core as core                                           # noqa: E402
import safe_report                                                               # noqa: E402
import errors                                                                    # noqa: E402
from authoritative import accepted_configuration as accepted                     # noqa: E402
from authoritative import resolve_sources                                        # noqa: E402

DesignViolation = core.DesignViolation

# --------------------------------------------------------------------------------------------
# Benchmarks and the LongMemEval inheritance tag (N-3)
# --------------------------------------------------------------------------------------------
LOCOMO = accepted.LOCOMO
LONGMEMEVAL = accepted.LONGMEMEVAL
BENCHMARKS = accepted.BENCHMARKS

# Carried into every output for LongMemEval. The single-component structure is INHERITED from Task
# 3A.1 and was provenance-verified, not recomputed here; a conversation-cluster bootstrap over one
# component is ill-posed, which is why it is refused rather than computed and caveated.
LONGMEMEVAL_INHERITANCE_TAG = {
    "dependency_structure": "single connected component covering all 470 questions",
    "provenance": "inherited from Task 3A.1; provenance-verified, NOT recomputed in this experiment",
    "consequence": "the conversation-cluster bootstrap is ILL-POSED for this benchmark and is refused",
    "authority": "V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R2_2026-09-07.md line 141: "
                 "'No conversation-cluster bootstrap is defined for LongMemEval.'",
}

# --------------------------------------------------------------------------------------------
# Input schema - stated, not implied (Head Researcher instruction 1)
# --------------------------------------------------------------------------------------------
# Identifiers are STRINGS ONLY. This is narrower than the core, deliberately: accepting integers is
# what makes NEW-5 reachable, because integer labels are keyed by int() and two distinct objects
# equal under int() would merge. A source whose ids are integers must render them as strings at the
# adapter, where the choice is visible, rather than here where it would be silent.
SUPPORTED_ID_TYPES = (str,)

# Designated missing-value indicators. Detection is done on a case-folded, stripped COPY; the value
# itself is never modified, and a valid id is never stripped, re-cased or coerced.
MISSING_VALUE_TOKENS = frozenset({"", "nan", "none", "null", "na", "n/a", "nil", "-", "--", "?"})

RECORD_FIELDS = frozenset({"question_id", "rotation_seed", "arm", "fractional_R3"})

MAPPING_FIELDS = frozenset({
    "source_id", "source_sha256", "benchmark",
    "expected_cluster_ids", "expected_question_to_cluster", "n_questions"})

RESULT_KEYS = frozenset({
    "benchmark", "estimates", "uncertainty", "scheme", "n_questions", "n_clusters",
    "bootstrap_seed_record", "source_identity", "longmemeval_inheritance_tag",
    "scaling_diagnostics", "runner_version", "core_identity"})

RUNNER_VERSION = "membership_runner v4 2026-09-08"

# The core this runner is bound to, by RAW GIT BLOB hash. It is recorded here and carried into every
# result; the test suite checks the checked-out core against it. It is NOT verified at import time,
# because a Windows checkout hashes differently from the blob and an import-time check would either
# fail spuriously or have to be weakened - so the claim is kept to what is actually done.
BOUND_CORE = accepted.BOUND_CORE


# --------------------------------------------------------------------------------------------
# 0. Validate-before-you-format. N-2 / D-5.
# --------------------------------------------------------------------------------------------
def require_benchmark(value) -> str:
    """Return the CANONICAL benchmark name, or refuse without echoing the caller's value."""
    for canonical in BENCHMARKS:
        if value == canonical:
            return canonical
    errors.raise_violation(DesignViolation, errors.Code.UNKNOWN_BENCHMARK,
                           accepted_benchmarks=len(BENCHMARKS))


class IdentifierKind(Enum):
    """The declared identifier kinds. v3 took `kind` as a caller STRING and echoed it (v3 closure
    check). A closed enumeration removes the value from the caller's hands entirely."""

    QUESTION_ID = "question_id"
    CLUSTER_ID = "cluster_id"


def require_identifier_kind(value) -> IdentifierKind:
    """Accept an IdentifierKind, or refuse without echoing what was passed."""
    if isinstance(value, IdentifierKind):
        return value
    errors.raise_violation(DesignViolation, errors.Code.IDENTIFIER_KIND_UNKNOWN,
                           declared_kinds=len(IdentifierKind))


def require_scheme(value) -> str:
    """Return the CANONICAL scheme name, or refuse without echoing the caller's value."""
    for canonical in accepted.SCHEMES:
        if value == canonical:
            return canonical
    errors.raise_violation(DesignViolation, errors.Code.UNKNOWN_SCHEME,
                           accepted_schemes=len(accepted.SCHEMES))


# --------------------------------------------------------------------------------------------
# 1. Identifier validation - NEW-4 and NEW-5, at the ingestion boundary
# --------------------------------------------------------------------------------------------
# D-5: v1 had `_describe(value) -> f"{type(value).__name__}({value!r})"` here, with no length cap
# and no policy check. It was reached from the two validators whose whole purpose is to fire when
# something that is not an identifier appears in an identifier column - so the error path that
# existed to catch a malformed id column was also the path that printed it. It is replaced by
# safe_report.describe, which reports type, shape and digest and never the value.


def validate_identifier(value, kind, position) -> str:
    """Accept one identifier or raise a named DesignViolation. Never transform a valid one.

    Rejected, each by name: an unsupported type (NEW-5 - no int() keying is possible if no integer
    ever arrives); a designated missing-value indicator, including the empty string and the literal
    strings "nan" and "None" (NEW-4); a whitespace-only string; and a string carrying leading or
    trailing whitespace, because stripping it would silently merge " c1" with "c1" and the Head
    Researcher's instruction is that valid identifiers are not silently altered or merged.
    """
    kind = require_identifier_kind(kind)
    if isinstance(value, bool) or not isinstance(value, SUPPORTED_ID_TYPES):
        errors.raise_violation(DesignViolation, errors.Code.UNSUPPORTED_ID_TYPE,
                               kind=kind, position=position)
    probe = value.strip().casefold()
    if probe in MISSING_VALUE_TOKENS:
        errors.raise_violation(DesignViolation, errors.Code.MISSING_VALUE_INDICATOR,
                               kind=kind, position=position, length=len(value))
    if value != value.strip():
        errors.raise_violation(DesignViolation, errors.Code.IDENTIFIER_WHITESPACE,
                               kind=kind, position=position, length=len(value))
    return value


def validate_identifier_columns(question_ids, cluster_ids) -> tuple[list[str], list[str]]:
    """Validate both id columns and their alignment. Nothing is coerced, sorted or de-duplicated."""
    q = list(question_ids)
    c = list(cluster_ids)
    if len(q) != len(c):
        errors.raise_violation(DesignViolation, errors.Code.COLUMNS_NOT_ALIGNED,
                               question_ids=len(q), cluster_ids=len(c))
    if not q:
        errors.raise_violation(DesignViolation, errors.Code.EMPTY_COHORT)
    qs = [validate_identifier(v, IdentifierKind.QUESTION_ID, i) for i, v in enumerate(q)]
    cs = [validate_identifier(v, IdentifierKind.CLUSTER_ID, i) for i, v in enumerate(c)]
    seen, dupes = set(), []
    for i, v in enumerate(qs):
        if v in seen:
            dupes.append((i, v))
        seen.add(v)
    if dupes:
        errors.raise_violation(DesignViolation, errors.Code.DUPLICATE_QUESTION_ID,
                               duplicates=len(dupes), first_position=dupes[0][0])
    return qs, cs


# --------------------------------------------------------------------------------------------
# 2. Source identity - the mapping contract (Head Researcher instruction 1)
# --------------------------------------------------------------------------------------------
def load_accepted_mapping(benchmark: str, *, raw: bytes | None = None, path=None) -> dict:
    """Load the ACCEPTED manifest for `benchmark`. The expected hash is NOT a caller argument.

    D-4 and the source-trust item. v1 took `expected_sha256` from the caller, so "accepted" meant
    whatever the caller said it meant, and it hashed the file ON DISK - which on a default Windows
    checkout differs from the accepted blob hash. Here the expected hash comes from
    `authoritative.accepted_configuration`, and the bytes are checked by
    `authoritative.resolve_sources`, which refuses a mismatch, names a SUPERSEDED manifest as
    superseded, and diagnoses a line-ending-translated checkout WITHOUT normalising it.

    Pass `raw` (bytes already in hand, e.g. from `git cat-file blob`) or `path` to a
    byte-preservingly materialised file. There is no third option and no override.
    """
    benchmark = require_benchmark(benchmark)                                   # N-2 / F16
    if (raw is None) == (path is None):
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_ARGUMENTS)
    if raw is None:
        raw = Path(path).read_bytes()
    try:
        resolve_sources.verify_manifest_bytes(raw, benchmark)
    except resolve_sources.SourceResolutionError as exc:
        # The message is already code-built and safe; re-raised with no chain so no library
        # context can travel with it.
        raise DesignViolation(str(exc)) from None
    mapping = json.loads(raw.decode("utf-8"))
    extra = set(mapping) - MAPPING_FIELDS
    missing = MAPPING_FIELDS - set(mapping)
    if extra or missing:
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_SCHEMA,
                               missing_fields=len(missing), unexpected_fields=len(extra))
    if mapping["benchmark"] != benchmark:
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_BENCHMARK_MISMATCH)
    # Stamped AFTER the closed-schema check, so the declared schema stays exactly what it was. This
    # is how compute_results knows a mapping came through here and not from a caller-chosen file.
    mapping["_accepted_manifest_sha256"] = accepted.ACCEPTED_MANIFESTS[benchmark]["blob_sha256"]
    return mapping


def verify_source_identity(question_ids, cluster_ids, mapping: dict) -> dict:
    """Prove the cohort IS the bound source, on six checks, not on the cluster count.

    A count check is explicitly not sufficient. Several distinct corruptions leave `n_clusters`
    unchanged - a missing id absorbed into an existing conversation, two ids swapped between
    conversations, a whole conversation relabelled - and every one of them changes which questions
    are resampled together, which is the only thing the cluster bootstrap depends on.
    """
    qs, cs = validate_identifier_columns(question_ids, cluster_ids)

    # v3 closure check: `int(mapping["n_questions"])` raised an uncaught ValueError here, in a public
    # entry with no stamp check, carrying the caller's value out in the library message. The manifest
    # field types the source contract requires are validated explicitly - no silent conversion, and
    # no new value accepted by coercion.
    if not isinstance(mapping.get("expected_question_to_cluster"), dict):
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_FIELD_TYPE, field_index=0)
    if not isinstance(mapping.get("expected_cluster_ids"), (list, tuple)):
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_FIELD_TYPE, field_index=1)
    n_declared = mapping.get("n_questions")
    if isinstance(n_declared, bool) or not isinstance(n_declared, int):
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_FIELD_TYPE, field_index=2)
    expected_map = dict(mapping["expected_question_to_cluster"])
    expected_clusters = set(mapping["expected_cluster_ids"])
    if len(mapping["expected_cluster_ids"]) != len(expected_clusters):
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_INTERNALLY_INCONSISTENT, reason_index=0)
    if set(expected_map.values()) != expected_clusters:
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_INTERNALLY_INCONSISTENT, reason_index=1)
    if len(expected_map) != n_declared:
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_INTERNALLY_INCONSISTENT,
                               reason_index=2, declared=n_declared, mapped=len(expected_map))

    got_map = dict(zip(qs, cs))
    missing_q = sorted(set(expected_map) - set(got_map))
    extra_q = sorted(set(got_map) - set(expected_map))
    misrouted = sorted(
        (q, got_map[q], expected_map[q]) for q in set(got_map) & set(expected_map)
        if got_map[q] != expected_map[q])
    got_clusters = set(cs)

    problems = []
    if missing_q:
        problems.append(f"{len(missing_q)} question id(s) missing against the accepted cohort: "
                        f"{safe_report.describe_many(missing_q)}")
    if extra_q:
        problems.append(f"{len(extra_q)} question id(s) not in the accepted cohort: "
                        f"{safe_report.describe_many(extra_q)}")
    if misrouted:
        problems.append(f"{len(misrouted)} question(s) mapped to the WRONG conversation: "
                        f"{safe_report.describe_many([q for q, _, _ in misrouted])}")
    if got_clusters != expected_clusters:
        problems.append(
            "conversation id SET mismatch: "
            + safe_report.counts(missing=len(expected_clusters - got_clusters),
                                 unexpected=len(got_clusters - expected_clusters)))
    if problems:
        raise DesignViolation("source identity check failed: " + "; ".join(problems))

    return {
        "source_id": mapping["source_id"], "source_sha256": mapping["source_sha256"],
        "benchmark": mapping["benchmark"], "n_questions": len(qs),
        "n_clusters": len(got_clusters),
        "cluster_id_set_matches": True, "question_to_cluster_matches": True,
        "duplicate_question_ids": 0, "missing_question_ids": 0, "extra_question_ids": 0,
        "checks_performed": ["identifier type and missing-value validation",
                             "duplicate question ids", "missing question ids", "extra question ids",
                             "per-question conversation mapping", "conversation id set equality"],
        "count_check_alone_is_not_accepted": True,
    }


# --------------------------------------------------------------------------------------------
# 3. N-2 - the bootstrap seed is frozen to a record before any result exists
# --------------------------------------------------------------------------------------------
def accepted_bootstrap_for(benchmark: str, scheme: str) -> dict:
    """The ACCEPTED seed and replicate count, or a named refusal saying why there is none."""
    benchmark, scheme = require_benchmark(benchmark), require_scheme(scheme)   # N-2 / F15
    try:
        return accepted.accepted_bootstrap(benchmark, scheme)
    except KeyError:
        errors.raise_violation(DesignViolation, errors.Code.NO_ACCEPTED_BOOTSTRAP,
                               accepted_combinations=len(accepted.ACCEPTED_BOOTSTRAP))


def freeze_bootstrap_seed(path: Path, seed: int, benchmark: str, scheme: str, replicates: int) -> dict:
    """Write the ACCEPTED bootstrap seed to a NEW file and return the record. Refuses to overwrite.

    N-2 as before: written before any quantity is computed, and re-reading it is the only way a run
    obtains a seed, so a seed cannot be chosen after seeing a result.

    D-3 is new. v1 accepted ANY int - the review froze seed 999 where the accepted value is
    52001107 and read it straight back, so a transposed digit passed every check in the system. The
    seed and the replicate count are now checked against `authoritative.accepted_configuration`,
    which is the same file the acceptance record binds. The arguments remain, so a caller states
    what it believes it is freezing and is contradicted if it is wrong, rather than being handed a
    value silently.
    """
    benchmark, scheme = require_benchmark(benchmark), require_scheme(scheme)
    want = accepted_bootstrap_for(benchmark, scheme)
    if isinstance(seed, bool) or not isinstance(seed, int):
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_MALFORMED, seed_is_int=False)
    if isinstance(replicates, bool) or not isinstance(replicates, int):
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_MALFORMED,
                               replicates_is_int=False)
    if int(seed) != want["seed"]:
        errors.raise_violation(DesignViolation, errors.Code.SEED_NOT_ACCEPTED,
                               accepted_seed=want["seed"])
    if int(replicates) != want["replicates"]:
        errors.raise_violation(DesignViolation, errors.Code.REPLICATES_NOT_ACCEPTED,
                               accepted_replicates=want["replicates"])
    record = {"bootstrap_seed": int(seed), "benchmark": benchmark, "scheme": scheme,
              "replicates": int(replicates), "frozen_before_any_result": True,
              "runner_version": RUNNER_VERSION}
    core.safe_write_json(Path(path), record)
    return record


def read_bootstrap_seed(path: Path, benchmark: str, scheme: str) -> dict:
    """Load the frozen seed record and check it is the one this run is entitled to use."""
    path = Path(path)
    # N-2 / F20 - the ONLY file-derived leak the closure check found. v2 printed
    # record.get("benchmark") and record.get("scheme") straight out of this JSON file, uncapped. A
    # file the pipeline writes is not a trusted string source: anything that can write it can put
    # anything in it. Nothing read from the record reaches a message now.
    benchmark, scheme = require_benchmark(benchmark), require_scheme(scheme)
    if not path.exists():
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_ABSENT)
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_MALFORMED, is_mapping=False)
    if record.get("benchmark") != benchmark or record.get("scheme") != scheme:
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_WRONG_ARM,
                               benchmark_matches=record.get("benchmark") == benchmark,
                               scheme_matches=record.get("scheme") == scheme)
    if not isinstance(record.get("bootstrap_seed"), int) or isinstance(record.get("bootstrap_seed"), bool):
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_MALFORMED, seed_is_int=False)
    want = accepted_bootstrap_for(benchmark, scheme)
    if record["bootstrap_seed"] != want["seed"] or record.get("replicates") != want["replicates"]:
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_DRIFT,
                               accepted_seed=want["seed"], accepted_replicates=want["replicates"],
                               seed_matches=record["bootstrap_seed"] == want["seed"],
                               replicates_matches=record.get("replicates") == want["replicates"])
    record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return record


# --------------------------------------------------------------------------------------------
# 4. N-4 - the archive-learned transform is applied to the query, unchanged
# --------------------------------------------------------------------------------------------
def fit_archive_transform(archive_repr: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict]:
    """Learn the centering vector and D from the ARCHIVE ONLY. Returns (mu, D, diagnostics).

    N-4: nothing here sees a query. The caller receives the two objects and must pass those same
    objects to `apply_archive_transform`; `assert_query_transform_is_inherited` proves it did.
    """
    A = np.asarray(archive_repr, dtype=float)
    if A.ndim != 2 or A.shape[1] != core.DIM:
        raise DesignViolation(f"archive representation must be (n, {core.DIM}), got {A.shape}")
    mu = A.mean(axis=0)
    D, diagnostics = core.scale_matrix(A - mu)
    return mu, D, diagnostics


def transform_stamp(mu, D) -> str:
    """A digest of the exact bytes of the parameters a transform used. D-6.

    Not object identity - `id()` is reused after garbage collection and says nothing across
    processes - but a fingerprint of the VALUES ACTUALLY CONSUMED, recorded by the function that
    consumed them rather than reported by the caller.
    """
    h = hashlib.sha256()
    for arr in (np.ascontiguousarray(np.asarray(mu, dtype=float)),
                np.ascontiguousarray(np.asarray(D, dtype=float))):
        h.update(str(arr.shape).encode("ascii"))
        h.update(arr.tobytes())
    return h.hexdigest()


def apply_archive_transform(X: np.ndarray, mu: np.ndarray, D: np.ndarray):
    """Centre by the ARCHIVE mean, rescale by the ARCHIVE D, and STAMP what was used.

    Returns (transformed, stamp). D-6: v1 returned only the array and recorded nothing, so the
    inheritance assertion could only compare echoes the caller handed it - a caller that
    transformed the query with a query-derived mu and then passed the archive mu to the assertion
    passed cleanly. The stamp is produced HERE, by the code that actually did the arithmetic.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != core.DIM:
        raise DesignViolation(f"representation must be (n, {core.DIM}), got {X.shape}")
    return (X - mu) @ D, transform_stamp(mu, D)


def assert_query_transform_is_inherited(mu_archive, D_archive, query_stamp: str) -> None:
    """N-4: the query must have been transformed by the ARCHIVE-learned parameters.

    D-6. v1 took `mu_used` and `D_used` from the caller and compared them to the archive pair with
    `np.array_equal`. Two problems, both demonstrated by the review: `np.array_equal` is VALUE
    equality, so passing `mu.copy()` and `D.copy()` passed while the docstring claimed "IDENTICAL
    objects"; and the assertion was connected to nothing, so a caller could transform the query one
    way and report another.

    Now the caller cannot report anything. It passes the STAMP that `apply_archive_transform`
    returned when it transformed the query, and that stamp is a digest of the parameter bytes the
    arithmetic actually consumed. Bytes, not tolerance, is right here: this asserts the same numbers
    were reused, not that two summation orders agree.
    """
    expected = transform_stamp(mu_archive, D_archive)
    if not isinstance(query_stamp, str):
        raise DesignViolation(
            f"the query transform stamp must be the string returned by apply_archive_transform, got "
            f"{safe_report.describe(query_stamp)}")
    if query_stamp != expected:
        raise DesignViolation(
            "N-4 VIOLATION: the query was NOT transformed by the archive-learned centering vector "
            "and D - the stamp recorded by apply_archive_transform does not match the archive "
            "parameters, so something was estimated from the query")


# --------------------------------------------------------------------------------------------
# 5. The integration entry points
# --------------------------------------------------------------------------------------------
def compute_results(records, question_ids, cluster_ids, mapping, seed_record_path, *,
                    benchmark: str, scheme: str, replicates: int = core.BOOTSTRAP_REPLICATES,
                    scaling_diagnostics: dict | None = None) -> dict:
    """The whole chain: identity, mapping, frozen seed, core estimates, core bootstrap, output.

    Reads no corpus. `records` are already-computed per-question scores, whoever produced them.
    """
    # N-2 / F13, F14: canonicalised before anything else, so no caller string reaches a message.
    benchmark, scheme = require_benchmark(benchmark), require_scheme(scheme)
    # N-2 / F12 - the ORDERING defect. v2 compared mapping["benchmark"] and printed it one line
    # BEFORE this stamp check, so an arbitrary caller dict reached a message. The stamp check now
    # runs FIRST: nothing from the mapping is read, compared or formatted until the mapping has
    # been shown to be the accepted one.
    if not isinstance(mapping, dict) or mapping.get("_accepted_manifest_sha256") != \
            accepted.ACCEPTED_MANIFESTS[benchmark]["blob_sha256"]:
        errors.raise_violation(DesignViolation, errors.Code.MAPPING_NOT_FROM_ACCEPTED_PATH)
    if benchmark == LONGMEMEVAL and scheme == "cluster":
        raise DesignViolation(
            "N-3: the conversation-cluster bootstrap is REFUSED for LongMemEval. Its dependency "
            "structure is a single connected component over all 470 questions, inherited from Task "
            "3A.1, so a cluster resample is ill-posed rather than merely wide. R2 line 141: 'No "
            "conversation-cluster bootstrap is defined for LongMemEval.'")
    if mapping["benchmark"] != benchmark:
        errors.raise_violation(DesignViolation, errors.Code.MANIFEST_BENCHMARK_MISMATCH)

    identity = verify_source_identity(question_ids, cluster_ids, mapping)
    seed_record = read_bootstrap_seed(seed_record_path, benchmark, scheme)
    # D-2: v1 never compared the caller's replicate count to the frozen record, so a run of 7
    # replicates was persisted claiming 10000 and write_results could not catch it - the schema was
    # satisfied. The result must state how it was actually computed.
    if isinstance(replicates, bool) or not isinstance(replicates, int):
        errors.raise_violation(DesignViolation, errors.Code.SEED_RECORD_MALFORMED,
                               replicates_is_int=False)
    if int(replicates) != int(seed_record["replicates"]):
        errors.raise_violation(DesignViolation, errors.Code.REPLICATES_CONTRADICT_RECORD,
                               record_replicates=int(seed_record["replicates"]),
                               requested_replicates=int(replicates))

    qs = list(question_ids)
    g, gs = core.paired_matrices(records, qs)
    estimates = core.aggregate(g, gs)

    if scheme == "question":
        uncertainty = core.question_bootstrap(g, gs, seed_record["bootstrap_seed"], replicates)
        n_clusters = identity["n_clusters"]
    else:
        uncertainty = core.cluster_bootstrap(
            g, gs, list(cluster_ids), seed_record["bootstrap_seed"], replicates)
        n_clusters = uncertainty["n_clusters"]

    result = {
        "benchmark": benchmark, "estimates": estimates, "uncertainty": uncertainty,
        "scheme": scheme, "n_questions": len(qs), "n_clusters": n_clusters,
        "bootstrap_seed_record": seed_record, "source_identity": identity,
        "longmemeval_inheritance_tag": LONGMEMEVAL_INHERITANCE_TAG if benchmark == LONGMEMEVAL else None,
        "scaling_diagnostics": scaling_diagnostics, "runner_version": RUNNER_VERSION,
        "core_identity": BOUND_CORE,
    }
    if set(result) != RESULT_KEYS:
        errors.raise_violation(DesignViolation, errors.Code.RESULT_SCHEMA,
                               missing_fields=len(RESULT_KEYS - set(result)),
                               unexpected_fields=len(set(result) - RESULT_KEYS))
    return result


def write_results(path: Path, result: dict) -> Path:
    """Persist through the core's refusal-to-overwrite path, after re-checking the schema."""
    if set(result) != RESULT_KEYS:
        errors.raise_violation(DesignViolation, errors.Code.RESULT_SCHEMA,
                               missing_fields=len(RESULT_KEYS - set(result)),
                               unexpected_fields=len(set(result) - RESULT_KEYS))
    return core.safe_write_json(Path(path), result)


def run_on_real_corpus(*_args, **_kwargs):
    """The only entry point that would touch a corpus. It refuses, and there is nothing behind it.

    This is deliberately a stub. Writing a real ingestion path is not authorized at this stage, and a
    stub that refuses is honest where an unreachable implementation would invite a later reader to
    flip a flag and believe it had been reviewed.
    """
    core.require_real_data_authorization()
    errors.raise_violation(DesignViolation, errors.Code.NO_INGESTION_PATH)
