"""Fixed diagnostic codes and a closed field formatter for the preparation runner.

Messages admit declared field names, builtin numeric primitives, None and the canonical
IdentifierKind members defined here. Unknown names, foreign enums, numeric subclasses and
other values receive fixed UnsafeErrorField messages. This module does not certify all
exception paths in its callers, inspect provenance, or erase an existing __context__ chain.
The synthetic regression tests define the checked surface; no real corpus execution is
authorized by this interface.
"""
from __future__ import annotations

from enum import Enum


class UnsafeErrorField(RuntimeError):
    """Raised when something that is not a safe field is passed to an error message."""


class IdentifierKind(Enum):
    """Identifier labels admitted by the error formatter."""

    QUESTION_ID = "question_id"
    CLUSTER_ID = "cluster_id"


# Fixed labels used by the current runner, ingest and source resolver. Unknown labels are
# refused before sorting or formatting; kwargs keys are themselves untrusted input.
FIELD_NAMES = frozenset("""
accepted_benchmarks accepted_schemes declared_kinds kind position length question_ids cluster_ids
duplicates first_position missing_fields unexpected_fields field_index reason_index declared mapped
missing unexpected accepted_combinations seed_is_int replicates_is_int accepted_seed
accepted_replicates is_mapping benchmark_matches scheme_matches seed_matches replicates_matches
record_replicates requested_replicates given_name_length accepted_bytes read_bytes hash_matches
string_length structural_limit allowed_type item_position items has_dia_id_key has_id_key id_is_empty
item_is_str item_is_mapping is_none is_str is_sequence top_level_is_list conversation_index unit_row
affected_questions declared_ids unresolved_ids cohort_size missing_ids misrouted_ids
position_mismatched_ids resolved manifest_n_questions required_fields fields_present haystack_session_ids
haystack_dates haystack_sessions session_index session_is_list turn_index turn_is_mapping git_exit_code
expected_bytes wrote_bytes read_back_bytes superseded_manifests_known got_bytes
crlf_to_lf_would_match lf_to_crlf_would_match
""".split())


class Code(str, Enum):
    """Fixed error codes. Closed set; never derived from data."""

    # configuration and identity
    UNKNOWN_BENCHMARK = "E-CFG-001"
    UNKNOWN_SCHEME = "E-CFG-002"
    NO_ACCEPTED_BOOTSTRAP = "E-CFG-003"
    SEED_NOT_ACCEPTED = "E-CFG-004"
    REPLICATES_NOT_ACCEPTED = "E-CFG-005"
    SEED_RECORD_WRONG_ARM = "E-CFG-006"
    SEED_RECORD_MALFORMED = "E-CFG-007"
    SEED_RECORD_DRIFT = "E-CFG-008"
    SEED_RECORD_ABSENT = "E-CFG-009"
    REPLICATES_CONTRADICT_RECORD = "E-CFG-010"

    # manifests and sources
    MANIFEST_NOT_ACCEPTED = "E-SRC-001"
    MANIFEST_SUPERSEDED = "E-SRC-002"
    MANIFEST_ARGUMENTS = "E-SRC-003"
    MANIFEST_SCHEMA = "E-SRC-004"
    MANIFEST_BENCHMARK_MISMATCH = "E-SRC-005"
    MAPPING_NOT_FROM_ACCEPTED_PATH = "E-SRC-006"
    SOURCE_ABSENT = "E-SRC-007"
    SOURCE_NAME_MISMATCH = "E-SRC-008"
    SOURCE_IDENTITY_MISMATCH = "E-SRC-009"
    GIT_BLOB_UNREADABLE = "E-SRC-010"
    MATERIALISATION_NOT_BYTE_PRESERVING = "E-SRC-011"

    # cohort and evidence
    COHORT_RESOLUTION_FAILED = "E-COH-001"
    PARTIAL_EVIDENCE_RESOLUTION = "E-COH-002"
    DUPLICATE_QUESTION_ID = "E-COH-003"
    DUPLICATE_MEMORY_UNIT_ID = "E-COH-004"
    COHORT_SIZE_MISMATCH = "E-COH-005"
    ITEM_MISSING_FIELD = "E-COH-006"
    RAGGED_PARALLEL_ARRAYS = "E-COH-007"
    EMPTY_HAYSTACK = "E-COH-008"
    INVALID_GOLD_MARKER_TYPE = "E-COH-009"
    SESSION_SHAPE = "E-COH-010"
    EVIDENCE_ITEM_MALFORMED = "E-COH-011"
    EVIDENCE_STRUCTURE_UNSUPPORTED = "E-COH-012"
    IDENTIFIER_KIND_UNKNOWN = "E-COH-013"
    UNSUPPORTED_ID_TYPE = "E-COH-014"
    MISSING_VALUE_INDICATOR = "E-COH-015"
    IDENTIFIER_WHITESPACE = "E-COH-016"
    COLUMNS_NOT_ALIGNED = "E-COH-017"
    EMPTY_COHORT = "E-COH-018"
    MANIFEST_INTERNALLY_INCONSISTENT = "E-SRC-013"
    MANIFEST_FIELD_TYPE = "E-SRC-012"

    # output and gates
    RESULT_SCHEMA = "E-OUT-001"
    INGEST_MANIFEST_SCHEMA = "E-OUT-002"
    CONTENT_POLICY = "E-OUT-003"
    NO_INGESTION_PATH = "E-GAT-001"


SENTENCES = {
    Code.UNKNOWN_BENCHMARK: "the benchmark is not one of the accepted benchmarks",
    Code.UNKNOWN_SCHEME: "the resampling scheme is not one of the accepted schemes",
    Code.NO_ACCEPTED_BOOTSTRAP: ("no accepted bootstrap configuration exists for this benchmark and scheme; "
                                 "its absence from the accepted configuration is the authority for refusing it"),
    Code.SEED_NOT_ACCEPTED: "the seed is not the accepted seed for this benchmark and scheme",
    Code.REPLICATES_NOT_ACCEPTED: "the replicate count is not the accepted count for this benchmark and scheme",
    Code.SEED_RECORD_WRONG_ARM: "the frozen seed record was written for a different benchmark or scheme",
    Code.SEED_RECORD_MALFORMED: "the frozen seed record is malformed",
    Code.SEED_RECORD_DRIFT: "the frozen seed record does not match the accepted configuration",
    Code.SEED_RECORD_ABSENT: "no frozen bootstrap-seed record exists; the seed must be fixed before any result",
    Code.REPLICATES_CONTRADICT_RECORD: ("the replicate count contradicts the frozen seed record; the persisted "
                                        "result would misstate how it was computed"),
    Code.MANIFEST_NOT_ACCEPTED: "these manifest bytes are not the accepted manifest",
    Code.MANIFEST_SUPERSEDED: "these manifest bytes are a SUPERSEDED manifest and must not be loaded",
    Code.MANIFEST_ARGUMENTS: "exactly one of raw bytes or a path must be given",
    Code.MANIFEST_SCHEMA: "the manifest does not carry exactly the declared field set",
    Code.MANIFEST_BENCHMARK_MISMATCH: "the manifest is for a different benchmark than this run",
    Code.MAPPING_NOT_FROM_ACCEPTED_PATH: ("this mapping did not come through the accepted-resolution path; only the "
                                          "accepted manifest may be used"),
    Code.SOURCE_ABSENT: "the accepted source file is not present at the given location",
    Code.SOURCE_NAME_MISMATCH: "the file name is not the accepted source file name",
    Code.SOURCE_IDENTITY_MISMATCH: "the source bytes do not match the accepted identity",
    Code.GIT_BLOB_UNREADABLE: "the accepted artifact could not be read from Git",
    Code.MATERIALISATION_NOT_BYTE_PRESERVING: "materialisation did not preserve the accepted bytes",
    Code.COHORT_RESOLUTION_FAILED: "the accepted cohort could not be resolved against the source",
    Code.PARTIAL_EVIDENCE_RESOLUTION: ("some declared evidence ids resolve and some do not, so the gold set would be "
                                       "silently smaller than the source declares"),
    Code.DUPLICATE_QUESTION_ID: "a question id occurs more than once in the source",
    Code.DUPLICATE_MEMORY_UNIT_ID: "a memory unit id occurs more than once; the archive must be a set of units",
    Code.COHORT_SIZE_MISMATCH: "the number of resolved questions is not the accepted cohort size",
    Code.ITEM_MISSING_FIELD: "an item is missing a required field",
    Code.RAGGED_PARALLEL_ARRAYS: ("the parallel haystack arrays have different lengths; zipping them would silently "
                                  "truncate to the shortest"),
    Code.EMPTY_HAYSTACK: "an item has no haystack sessions, so its archive would be empty",
    Code.INVALID_GOLD_MARKER_TYPE: ("a gold marker is not a boolean; the bound adapter records this as "
                                    "INVALID_HAS_ANSWER_TYPE and coerces it to False, which would drop a gold unit "
                                    "silently"),
    Code.SESSION_SHAPE: "a haystack session or turn does not have the required shape",
    Code.EVIDENCE_ITEM_MALFORMED: ("an item inside an otherwise valid evidence list cannot be turned into a "
                                   "reference id under the bound source contract"),
    Code.EVIDENCE_STRUCTURE_UNSUPPORTED: ("the evidence field is not one of the shapes the bound source "
                                          "contract defines"),
    Code.IDENTIFIER_KIND_UNKNOWN: "the identifier kind is not one of the declared identifier kinds",
    Code.UNSUPPORTED_ID_TYPE: ("the identifier is not a string; this runner supports string identifiers "
                               "only, so that no int()-equal pair can merge (NEW-5)"),
    Code.MISSING_VALUE_INDICATOR: ("the identifier is a designated missing-value indicator; a missing id "
                                   "must be fixed at the source, not accepted as a label (NEW-4)"),
    Code.IDENTIFIER_WHITESPACE: ("the identifier has leading or trailing whitespace; it is REJECTED "
                                 "rather than stripped, because stripping would merge it with its "
                                 "neighbour"),
    Code.COLUMNS_NOT_ALIGNED: "the question id and cluster id columns do not have the same length",
    Code.EMPTY_COHORT: "the cohort is empty; there is nothing to validate",
    Code.MANIFEST_INTERNALLY_INCONSISTENT: "the manifest contradicts itself",
    Code.MANIFEST_FIELD_TYPE: "a manifest field does not have the type the source contract requires",
    Code.RESULT_SCHEMA: "the result does not carry exactly the declared field set",
    Code.INGEST_MANIFEST_SCHEMA: "the ingest manifest does not carry exactly the declared field set",
    Code.CONTENT_POLICY: "a value bound for a written artefact failed the structural content policy",
    Code.NO_INGESTION_PATH: ("no real-corpus ingestion path exists; reading a corpus, real fitting, retrieval, "
                             "ranking and real-data bootstrap are not authorized"),
}


def _safe(value, field: str):
    """Admit builtin numeric primitives and canonical identifier-kind labels only."""
    if value is None or type(value) in (bool, int, float):
        return value
    if type(value) is IdentifierKind:
        if value is IdentifierKind.QUESTION_ID:
            return "question_id"
        if value is IdentifierKind.CLUSTER_ID:
            return "cluster_id"
    raise UnsafeErrorField("an error field has an unsupported value type")


def message(code: Code, **fields) -> str:
    """Build a message from the code, its fixed sentence and safe fields only."""
    if type(code) is not Code or not any(code is member for member in Code):
        raise UnsafeErrorField("an error code must be a member of the closed Code enumeration")
    if any(type(k) is not str or k not in FIELD_NAMES for k in fields):
        raise UnsafeErrorField("an error field name is not in the closed field set")
    parts = [f"{code.value}: {SENTENCES[code]}"]
    if fields:
        safe = {k: _safe(v, k) for k, v in sorted(fields.items())}
        parts.append("[" + ", ".join(f"{k}={v}" for k, v in safe.items()) + "]")
    return " ".join(parts)


def raise_violation(exc_type, code: Code, **fields):
    """Raise `exc_type` with a code-built message and suppress displayed context.

    `from None` suppresses traceback display of a prior exception. It does not erase
    `__context__`; callers inspecting exception objects can still access that chain.
    """
    raise exc_type(message(code, **fields)) from None
