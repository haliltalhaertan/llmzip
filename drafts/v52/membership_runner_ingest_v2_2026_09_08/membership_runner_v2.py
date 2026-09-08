"""Corpus-bound runner v2 for the V52 membership-under-scaling experiment - PREPARATION ONLY.

STATUS: [IMPLEMENTATION PREPARATION - NOT AUTHORIZED TO RUN ON REAL DATA; NOT INDEPENDENTLY REVIEWED]

v2 answers findings D-2, D-3, D-4, D-5 and D-6 of the independent review at
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

On content: no value is interpolated into any message in this module. That is a property of the code
and it is tested, but it is NOT a claim that content cannot escape by some other route - a caller
that prints a returned structure defeats it, and this module cannot prevent that.

Governing documents, the audited core and the review chain are bound by commit, path and sha256 in
`GOVERNING_AND_LINEAGE.md`. Read them from `main`, hashing RAW GIT BLOBS.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "membership_impl_v3_2026_09_07"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import membership_scaling_core as core                                           # noqa: E402
import safe_report                                                               # noqa: E402
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

RUNNER_VERSION = "membership_runner v2 2026-09-08"

# The core this runner is bound to, by RAW GIT BLOB hash. It is recorded here and carried into every
# result; the test suite checks the checked-out core against it. It is NOT verified at import time,
# because a Windows checkout hashes differently from the blob and an import-time check would either
# fail spuriously or have to be weakened - so the claim is kept to what is actually done.
BOUND_CORE = accepted.BOUND_CORE


# --------------------------------------------------------------------------------------------
# 1. Identifier validation - NEW-4 and NEW-5, at the ingestion boundary
# --------------------------------------------------------------------------------------------
# D-5: v1 had `_describe(value) -> f"{type(value).__name__}({value!r})"` here, with no length cap
# and no policy check. It was reached from the two validators whose whole purpose is to fire when
# something that is not an identifier appears in an identifier column - so the error path that
# existed to catch a malformed id column was also the path that printed it. It is replaced by
# safe_report.describe, which reports type, shape and digest and never the value.


def validate_identifier(value, kind: str, position) -> str:
    """Accept one identifier or raise a named DesignViolation. Never transform a valid one.

    Rejected, each by name: an unsupported type (NEW-5 - no int() keying is possible if no integer
    ever arrives); a designated missing-value indicator, including the empty string and the literal
    strings "nan" and "None" (NEW-4); a whitespace-only string; and a string carrying leading or
    trailing whitespace, because stripping it would silently merge " c1" with "c1" and the Head
    Researcher's instruction is that valid identifiers are not silently altered or merged.
    """
    if isinstance(value, bool) or not isinstance(value, SUPPORTED_ID_TYPES):
        raise DesignViolation(
            f"{kind} at {position} has unsupported type {safe_report.describe(value)}; this runner "
            f"supports string identifiers only, so that no int()-equal pair can merge (NEW-5). "
            f"Render non-string ids as strings in the adapter, where the choice is visible")
    probe = value.strip().casefold()
    if probe in MISSING_VALUE_TOKENS:
        raise DesignViolation(
            f"{kind} at {position} is a designated missing-value indicator "
            f"{safe_report.describe(value)}; a missing id must be fixed at the source, never "
            f"accepted as an ordinary label (NEW-4)")
    if value != value.strip():
        raise DesignViolation(
            f"{kind} at {position} has leading or trailing whitespace "
            f"({safe_report.describe(value)}); it is REJECTED rather than stripped, because "
            f"stripping would silently merge it with its neighbour")
    return value


def validate_identifier_columns(question_ids, cluster_ids) -> tuple[list[str], list[str]]:
    """Validate both id columns and their alignment. Nothing is coerced, sorted or de-duplicated."""
    q = list(question_ids)
    c = list(cluster_ids)
    if len(q) != len(c):
        raise DesignViolation(
            f"identifier columns are not aligned: {len(q)} question ids against {len(c)} cluster ids")
    if not q:
        raise DesignViolation("the cohort is empty; there is nothing to validate")
    qs = [validate_identifier(v, "question id", i) for i, v in enumerate(q)]
    cs = [validate_identifier(v, "cluster id", i) for i, v in enumerate(c)]
    seen, dupes = set(), []
    for i, v in enumerate(qs):
        if v in seen:
            dupes.append((i, v))
        seen.add(v)
    if dupes:
        raise DesignViolation(
            f"duplicate question ids in the cohort at {safe_report.positions(dupes)}")
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
    if (raw is None) == (path is None):
        raise DesignViolation("load_accepted_mapping takes exactly one of `raw` or `path`")
    if raw is None:
        raw = Path(path).read_bytes()
    try:
        resolve_sources.verify_manifest_bytes(raw, benchmark)
    except resolve_sources.SourceResolutionError as exc:
        raise DesignViolation(str(exc)) from None
    mapping = json.loads(raw.decode("utf-8"))
    extra = set(mapping) - MAPPING_FIELDS
    missing = MAPPING_FIELDS - set(mapping)
    if extra or missing:
        raise DesignViolation(
            f"expected-mapping manifest schema mismatch: missing {sorted(missing)}, unexpected {sorted(extra)}")
    if mapping["benchmark"] != benchmark:
        raise DesignViolation(
            f"the accepted {benchmark} manifest declares benchmark {mapping['benchmark']!r}")
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

    expected_map = dict(mapping["expected_question_to_cluster"])
    expected_clusters = set(mapping["expected_cluster_ids"])
    if len(mapping["expected_cluster_ids"]) != len(expected_clusters):
        raise DesignViolation("the mapping manifest lists a duplicate cluster id")
    if set(expected_map.values()) != expected_clusters:
        raise DesignViolation(
            "the mapping manifest is internally inconsistent: the clusters used by its question map "
            "are not the cluster id set it declares")
    if len(expected_map) != int(mapping["n_questions"]):
        raise DesignViolation(
            f"the mapping manifest declares n_questions={mapping['n_questions']} but maps {len(expected_map)}")

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
    if benchmark not in BENCHMARKS:
        raise DesignViolation(f"unknown benchmark {benchmark!r}")
    if scheme not in accepted.SCHEMES:
        raise DesignViolation(f"unknown resampling scheme {scheme!r}")
    try:
        return accepted.accepted_bootstrap(benchmark, scheme)
    except KeyError:
        raise DesignViolation(
            f"no accepted bootstrap configuration exists for ({benchmark}, {scheme}); its absence "
            f"from the accepted configuration is the authority for refusing it") from None


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
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise DesignViolation(f"the bootstrap seed must be an int, got {safe_report.describe(seed)}")
    if isinstance(replicates, bool) or not isinstance(replicates, int):
        raise DesignViolation(
            f"the replicate count must be an int, got {safe_report.describe(replicates)}")
    want = accepted_bootstrap_for(benchmark, scheme)
    if int(seed) != want["seed"]:
        raise DesignViolation(
            f"seed {seed} is not the accepted seed for ({benchmark}, {scheme}); the accepted value "
            f"is {want['seed']} (D-3)")
    if int(replicates) != want["replicates"]:
        raise DesignViolation(
            f"replicate count {replicates} is not the accepted count for ({benchmark}, {scheme}); "
            f"the accepted value is {want['replicates']} (D-2)")
    record = {"bootstrap_seed": int(seed), "benchmark": benchmark, "scheme": scheme,
              "replicates": int(replicates), "frozen_before_any_result": True,
              "runner_version": RUNNER_VERSION}
    core.safe_write_json(Path(path), record)
    return record


def read_bootstrap_seed(path: Path, benchmark: str, scheme: str) -> dict:
    """Load the frozen seed record and check it is the one this run is entitled to use."""
    path = Path(path)
    if not path.exists():
        raise DesignViolation(
            f"no frozen bootstrap-seed record at {path}; N-2 requires the seed to be fixed and "
            f"recorded BEFORE any result is computed")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("benchmark") != benchmark or record.get("scheme") != scheme:
        raise DesignViolation(
            f"the frozen seed record is for ({record.get('benchmark')}, {record.get('scheme')}), "
            f"not ({benchmark}, {scheme}); a record may not be reused across arms of the design")
    if not isinstance(record.get("bootstrap_seed"), int) or isinstance(record.get("bootstrap_seed"), bool):
        raise DesignViolation("the frozen seed record does not carry an integer bootstrap seed")
    want = accepted_bootstrap_for(benchmark, scheme)
    if record["bootstrap_seed"] != want["seed"] or record.get("replicates") != want["replicates"]:
        raise DesignViolation(
            f"the frozen seed record does not match the accepted configuration for ({benchmark}, "
            f"{scheme}): record has seed={record['bootstrap_seed']} "
            f"replicates={record.get('replicates')}, accepted is seed={want['seed']} "
            f"replicates={want['replicates']} (D-2, D-3)")
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
    if benchmark not in BENCHMARKS:
        raise DesignViolation(f"unknown benchmark {benchmark!r}")
    if scheme not in ("question", "cluster"):
        raise DesignViolation(f"unknown resampling scheme {scheme!r}")
    if benchmark == LONGMEMEVAL and scheme == "cluster":
        raise DesignViolation(
            "N-3: the conversation-cluster bootstrap is REFUSED for LongMemEval. Its dependency "
            "structure is a single connected component over all 470 questions, inherited from Task "
            "3A.1, so a cluster resample is ill-posed rather than merely wide. R2 line 141: 'No "
            "conversation-cluster bootstrap is defined for LongMemEval.'")
    if mapping["benchmark"] != benchmark:
        raise DesignViolation(
            f"the mapping manifest is for {mapping['benchmark']!r}, this run is {benchmark!r}")
    if mapping.get("_accepted_manifest_sha256") != accepted.ACCEPTED_MANIFESTS[benchmark]["blob_sha256"]:
        raise DesignViolation(
            "this mapping did not come through load_accepted_mapping; a run may only use the "
            "ACCEPTED manifest, resolved from the authoritative configuration")

    identity = verify_source_identity(question_ids, cluster_ids, mapping)
    seed_record = read_bootstrap_seed(seed_record_path, benchmark, scheme)
    # D-2: v1 never compared the caller's replicate count to the frozen record, so a run of 7
    # replicates was persisted claiming 10000 and write_results could not catch it - the schema was
    # satisfied. The result must state how it was actually computed.
    if isinstance(replicates, bool) or not isinstance(replicates, int):
        raise DesignViolation(
            f"the replicate count must be an int, got {safe_report.describe(replicates)}")
    if int(replicates) != int(seed_record["replicates"]):
        raise DesignViolation(
            f"replicate count {replicates} contradicts the frozen seed record, which fixes "
            f"{seed_record['replicates']}; the persisted result would misstate how it was computed (D-2)")

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
        raise DesignViolation(
            f"result schema mismatch: missing {sorted(RESULT_KEYS - set(result))}, "
            f"unexpected {sorted(set(result) - RESULT_KEYS)}")
    return result


def write_results(path: Path, result: dict) -> Path:
    """Persist through the core's refusal-to-overwrite path, after re-checking the schema."""
    if set(result) != RESULT_KEYS:
        raise DesignViolation("refusing to write a result whose schema is not the declared one")
    return core.safe_write_json(Path(path), result)


def run_on_real_corpus(*_args, **_kwargs):
    """The only entry point that would touch a corpus. It refuses, and there is nothing behind it.

    This is deliberately a stub. Writing a real ingestion path is not authorized at this stage, and a
    stub that refuses is honest where an unreachable implementation would invite a later reader to
    flip a flag and believe it had been reviewed.
    """
    core.require_real_data_authorization()
    raise DesignViolation(
        "no real-corpus ingestion path exists in this runner. Reading or downloading a corpus, real "
        "fitting, retrieval, ranking and any real-data bootstrap are NOT authorized at this stage.")
