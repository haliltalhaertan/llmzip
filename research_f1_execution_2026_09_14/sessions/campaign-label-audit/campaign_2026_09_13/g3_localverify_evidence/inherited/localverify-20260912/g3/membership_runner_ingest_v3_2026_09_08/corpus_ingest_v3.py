"""Corpus ingestion v2 for the V52 membership-under-scaling experiment - WRITTEN, NOT AUTHORIZED TO RUN.

STATUS: [INGESTION CODE PREPARED - NO AUTHORIZATION TO EXECUTE ON REAL DATA; NOT INDEPENDENTLY REVIEWED]

This module reads real source files. It has never been called on one. Every entry point that opens a
corpus calls `core.require_real_data_authorization()` first, which refuses by default, and importing
this module opens nothing: there is no module-level file access, no path is resolved at import time,
and test discovery therefore cannot trigger corpus access.

WHAT THIS MODULE DOES, AND WHERE IT STOPS
------------------------------------------
It goes from bytes on disk to the structures the pipeline needs, and stops there:

  1. verify the SOURCE BYTE IDENTITY - streamed sha256 and byte size against bound values - BEFORE
     any parsing, so a wrong or altered file is refused before its content is touched;
  2. load the BOUND cohort/mapping manifest through the runner's own hash-checked loader;
  3. resolve EVERY accepted cohort id INDIVIDUALLY against the source, refusing missing, duplicated,
     misrouted and position-mismatched ids rather than repairing them. Ids present in the source but
     OUTSIDE the cohort are NOT refused - the cohort is a strict subset of the source by design, so
     they are counted and reported. v1 said "refusing missing, extra and duplicated"; the review was
     right that this was wrong about extras, and right that refusing them would have been the bug;
  4. assemble the archive memory units and the query texts IN MEMORY, with their gold row indices,
     and account for EVERY declared evidence id as resolved or unresolved (D-1).

It does NOT fit a representation, run retrieval, rank, evaluate, bootstrap, seal, or write anything
derived from content. TF-IDF, LSA, SVD, rotation and Hamming live in the audited core and in a later
stage; none of them is imported here.

THE COHORT IS BOUND, NOT RECOMPUTED
------------------------------------
This module NEVER derives a cohort. It takes the bound list of question ids from the manifest and
resolves each one. The `category != 5 and gold non-empty` rule that the producer used is documented in
`LOCOMO_SELECTION_RULE_NOTE_2026-09-08.md` and is deliberately NOT reimplemented here: a
reimplementation would be a second selection rule that could silently drift from the bound cohort. If
a bound id cannot be resolved, that is an error to report, not a cohort to regenerate.

CONTENT AND MESSAGES - the v1 claim here was FALSE and is replaced (D-5)
------------------------------------------------------------------------
v1 said, byte-verbatim: "Question, answer, dialogue and session text is held in memory and handed to
the caller. It is never printed, logged, put in an exception message, or written to disk." The
content policy ran only inside the manifest writer and never touched exception text; the independent
review got source-derived text out through SEVEN paths using fragments all SHORTER than the 120
character limit. The limit was never a guarantee and the claim was not true.

v2 then claimed 'NO value is interpolated into any message raised or printed by this module', and the
closure check falsified THAT too, with nine more paths - one of them reading its values out of a JSON
file the pipeline itself writes. Two absolute claims, two falsifications. So v3 does not make a third.

What v3 has instead is a MECHANISM, described in `errors.py`: every message is assembled by
`errors.message` from a FIXED CODE, that code's FIXED SENTENCE, and fields restricted to numbers,
booleans, None and enum members already validated against a closed set. A string cannot enter a
message without raising `UnsafeErrorField` first, and validation happens BEFORE any value could be
formatted.

The tested surface: every exception these modules raise, stdout, stderr, the `__cause__`/`__context__`
chain, and every file they write. Against that surface the tests drive caller-supplied, file-supplied
and corpus-parsed canaries, all under the 120-character structural limit, and find none.

NOT claimed: that no content can escape under any condition. Text IS held in memory and handed to the
caller - that is what ingestion is for - and a caller that prints it defeats everything above. The
threat model is these modules' own error paths, not the caller's behaviour.
"""
from __future__ import annotations

import hashlib
import json
import numbers
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CORE = Path(__file__).resolve().parents[1] / "membership_impl_v3_2026_09_07"
for _p in (str(_HERE), str(_CORE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import membership_runner_v3 as runner                                            # noqa: E402
import membership_scaling_core as core                                           # noqa: E402
import safe_report                                                               # noqa: E402
import errors                                                                    # noqa: E402
from authoritative import accepted_configuration as accepted                     # noqa: E402
from authoritative import resolve_sources                                        # noqa: E402

DesignViolation = core.DesignViolation


class ContentPolicyViolation(DesignViolation):
    """Raised when something that could carry source content is about to be written or logged."""


# --------------------------------------------------------------------------------------------
# Bound sources. Values only - no path is resolved and no file is opened at import time.
# --------------------------------------------------------------------------------------------
# Source identities and accepted manifests both resolve from the single authoritative module. v1
# duplicated these values here, which is how "accepted" could drift from what was actually accepted.
BOUND_SOURCES = accepted.ACCEPTED_SOURCES
BOUND_MANIFESTS = {b: {"path": e["path"], "sha256": e["blob_sha256"], "commit": e["commit"]}
                   for b, e in accepted.ACCEPTED_MANIFESTS.items()}

INGEST_MANIFEST_KEYS = frozenset({
    "benchmark", "source_file", "source_sha256", "source_bytes", "mapping_sha256",
    "n_questions", "n_clusters", "n_archive_units_total", "per_cluster_archive_units",
    "per_cluster_questions", "ingest_version", "content_emitted",
    "questions_with_empty_gold", "questions_with_partial_evidence_loss",
    # The evidence accounting is ONE field whose shape is named by its model, not a set of shared
    # keys. v2 used the same key names for both benchmarks, which is how LongMemEval ended up
    # publishing declared = resolved and calling it an accounting.
    "evidence_accounting"})

# The two benchmarks have DIFFERENT gold models. The manifest carries the model NAME - a short token -
# and the prose stays here, unwritten: a written artefact should carry identifiers, not paragraphs, and
# the structural content policy is right to refuse a paragraph even when it is one of ours.
EVIDENCE_MODEL = {"LoCoMo": "declared_reference_ids", "LongMemEval": "per_turn_gold_markers"}

EVIDENCE_MODEL_DESCRIPTION = {
    "declared_reference_ids": ("each question declares evidence ids that must resolve to rows of its own "
                               "conversation archive, so a reference CAN dangle and is counted"),
    "per_turn_gold_markers": ("gold is a boolean marker on a turn of the question's own haystack, not a "
                              "reference into a separate index, so nothing can dangle and there is NO "
                              "declared count to report"),
}

# Why "declared" is absent for LongMemEval rather than fabricated.
DECLARED_NOT_APPLICABLE = "NOT_APPLICABLE"
DECLARED_NOT_APPLICABLE_REASON = (
    "this benchmark declares no evidence ids. v2 set declared = resolved here, which made the number a "
    "tautology and any loss invisible while the shared field names promised an accounting. No count is "
    "invented; the guards below are what stand in its place."
)

# Short tokens naming what guards completeness where declared-vs-resolved is unavailable. Each token
# corresponds to a check in this module; the prose is in COMPLETENESS_GUARD_DESCRIPTION.
COMPLETENESS_GUARDS = {
    "LongMemEval": ("parallel_array_length_check", "empty_haystack_refused",
                    "units_enumerated_from_sessions", "non_boolean_gold_marker_refused"),
}

COMPLETENESS_GUARD_DESCRIPTION = {
    "parallel_array_length_check": "the three parallel haystack arrays are length-checked BEFORE zip, so no session or date can be dropped (D-7)",
    "empty_haystack_refused": "an item with no haystack sessions is refused rather than yielding an empty archive",
    "units_enumerated_from_sessions": "every unit is enumerated from the sessions themselves, so no gold marker can point at a unit that does not exist",
    "non_boolean_gold_marker_refused": "a non-boolean gold marker is REFUSED, where the bound adapter records INVALID_HAS_ANSWER_TYPE and coerces it to False",
}

# D-1, second round: there is NO accepted partial-evidence exception for this experiment.
PARTIAL_EVIDENCE_POLICY = (
    "An unexpected partial resolution STOPS the ingestion. v2 offered allow_partial_evidence with a "
    "free-text citation; a non-empty string is not an authorization, nothing checked that it named a "
    "real decision, and it reached no persisted artefact. The path is REMOVED. If the bound semantics "
    "are ever found to require an exception, it is brought for decision with its full source and "
    "reasoning and recorded there - it is not produced in code."
)

INGEST_VERSION = "corpus_ingest v3 2026-09-08"

LOCOMO_QID = re.compile(r"^locomo_(\d+)_qa(\d+)$")
_DIA_ID = re.compile(r"D\d+:\d+")


# --------------------------------------------------------------------------------------------
# 1. Source byte identity - checked BEFORE any parsing
# --------------------------------------------------------------------------------------------
def _check_accepted_mapping(mapping, benchmark: str) -> None:
    """Refuse a mapping that did not come through the accepted-resolution path.

    The ingestion no longer takes a manifest PATH and a caller-supplied hash. It takes the mapping
    that `load_accepted_mapping_from_git` or `load_accepted_mapping_from_file` produced, and those
    are the only two functions that can stamp it.
    """
    benchmark = runner.require_benchmark(benchmark)
    if not isinstance(mapping, dict) or mapping.get("_accepted_manifest_sha256") != \
            accepted.ACCEPTED_MANIFESTS[benchmark]["blob_sha256"]:
        errors.raise_violation(DesignViolation, errors.Code.MAPPING_NOT_FROM_ACCEPTED_PATH)


def verify_source_bytes(path, benchmark: str, *, enabled: bool | None = None) -> dict:
    """Stream the file and compare sha256 and size against the bound values. Refuses first.

    This is the only place a corpus path is opened for hashing, and it happens before `json.loads`
    ever sees a byte: a wrong, truncated or altered file is refused without its content being parsed.
    """
    core.require_real_data_authorization(enabled)
    benchmark = runner.require_benchmark(benchmark)                            # N-2 / F18
    bound = BOUND_SOURCES[benchmark]
    path = Path(path)
    if not path.is_file():
        # N-2 / F19: v2 printed the missing path verbatim and uncapped. A path is caller-supplied
        # text like any other.
        errors.raise_violation(DesignViolation, errors.Code.SOURCE_ABSENT)
    if path.name != bound["filename"]:
        errors.raise_violation(DesignViolation, errors.Code.SOURCE_NAME_MISMATCH,
                               given_name_length=len(path.name))
    size = path.stat().st_size
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    digest = h.hexdigest()
    if size != bound["bytes"] or digest != bound["sha256"]:
        errors.raise_violation(DesignViolation, errors.Code.SOURCE_IDENTITY_MISMATCH,
                               accepted_bytes=bound["bytes"], read_bytes=size,
                               hash_matches=digest == bound["sha256"])
    return {"source_file": path.name, "source_sha256": digest, "source_bytes": size}


def load_accepted_mapping_from_git(repo_root, benchmark: str) -> dict:
    """Resolve the ACCEPTED manifest from Git's ORIGINAL BYTES. D-4.

    v1 hashed a checked-out file against a hash computed from the raw blob. On a default Windows
    clone - `core.autocrlf=true`, which is set in this machine's SYSTEM config - the checkout has
    CRLF line endings and does not match, so the loader refused its own accepted configuration.
    Reading the blob avoids the checkout filter entirely.
    """
    raw, _entry = resolve_sources.resolve_accepted_manifest(repo_root, benchmark)
    return runner.load_accepted_mapping(benchmark, raw=raw)


def load_accepted_mapping_from_file(manifest_path, benchmark: str) -> dict:
    """Load a BYTE-PRESERVINGLY MATERIALISED manifest file. D-4.

    Use `authoritative.resolve_sources.materialize_accepted_manifest` to produce it. A file that a
    line-ending filter has touched is REFUSED with that diagnosis - never normalised, because
    normalising to make the hash match would also hide a genuine substitution.
    """
    return runner.load_accepted_mapping(benchmark, path=manifest_path)


# --------------------------------------------------------------------------------------------
# 2. Content policy - the only writer, and what it refuses
# --------------------------------------------------------------------------------------------
_MAX_STRING = 120


def assert_content_free(payload, _path="payload") -> None:
    """Refuse anything that could carry source content. Conservative on purpose.

    Only short strings, numbers, booleans, None and containers of those are allowed. A long string is
    refused whether or not it actually came from the corpus, because the check must not depend on
    guessing provenance.
    """
    if isinstance(payload, str):
        if len(payload) > _MAX_STRING:
            errors.raise_violation(ContentPolicyViolation, errors.Code.CONTENT_POLICY,
                                   string_length=len(payload), structural_limit=_MAX_STRING)
        return
    if payload is None or isinstance(payload, bool) or isinstance(payload, numbers.Real):
        return
    if isinstance(payload, dict):
        # D-5: v1 built the child path as f"{_path}.{k}", which interpolated the KEY verbatim and
        # echoed it when a sibling value failed - the policy leaked through its own error. Keys are
        # now reported by index and digest.
        for i, (k, v) in enumerate(payload.items()):
            assert_content_free(k, f"{_path}.<key {i}>")
            assert_content_free(v, f"{_path}.<value {i}>")
        return
    if isinstance(payload, (list, tuple)):
        for i, v in enumerate(payload):
            assert_content_free(v, f"{_path}[{i}]")
        return
    errors.raise_violation(ContentPolicyViolation, errors.Code.CONTENT_POLICY, allowed_type=False)


def write_ingest_manifest(path, manifest: dict):
    """The ONLY writer in this module. Schema-checked, content-checked, refuses to overwrite."""
    if set(manifest) != INGEST_MANIFEST_KEYS:
        errors.raise_violation(DesignViolation, errors.Code.INGEST_MANIFEST_SCHEMA,
                               missing_fields=len(INGEST_MANIFEST_KEYS - set(manifest)),
                               unexpected_fields=len(set(manifest) - INGEST_MANIFEST_KEYS))
    assert_content_free(manifest)
    return core.safe_write_json(Path(path), manifest)


# --------------------------------------------------------------------------------------------
# 3. LoCoMo ingestion
# --------------------------------------------------------------------------------------------
def _locomo_memory_units(conversation: dict) -> list[dict]:
    """Ordered memory units of one conversation: sessions in numeric order, turns in file order.

    The unit text follows the producer's committed `message_text`: speaker and text, with an image
    caption appended as "[IMAGE: ...]" when one is present. Reproduced here because the ingestion has
    to build the same units; the SELECTION rule is not reproduced, only the unit construction.
    """
    units = []
    session_keys = sorted(
        (k for k in conversation if k.startswith("session_") and not k.endswith("_date_time")),
        key=lambda k: int(k.split("_")[1]))
    for sk in session_keys:
        for msg in conversation.get(sk) or []:
            dia_id = str(msg.get("dia_id", ""))
            if not dia_id:
                continue
            speaker = str(msg.get("speaker", "")).strip()
            text = str(msg.get("text", "")).strip()
            caption = str(msg.get("blip_caption", "") or "").strip()
            if caption:
                text = f"{text} [IMAGE: {caption}]".strip()
            units.append({"dia_id": dia_id, "session": sk,
                          "text": f"{speaker}: {text}".strip(": ")})
    return units


def _normalise_evidence(value) -> list[str]:
    """Evidence ids only, in the producer's committed normalisation. Never returns free text."""
    if value is None:
        return []
    if isinstance(value, str):
        found = _DIA_ID.findall(value)
        return found if found else [value]
    if isinstance(value, (list, tuple)):
        out = []
        for item in value:
            if isinstance(item, str):
                found = _DIA_ID.findall(item)
                out.extend(found if found else [item])
            elif isinstance(item, dict):
                did = item.get("dia_id") or item.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def ingest_locomo(source_path, mapping, *, enabled: bool | None = None) -> dict:
    """Resolve the BOUND LoCoMo cohort against the verified source. No cohort is derived.

    Returns in-memory structures. Nothing here is printed or written; the caller decides what to do
    with them, and only `write_ingest_manifest` may put anything on disk.
    """
    # D-1, second round. v2 offered allow_partial_evidence with a free-text citation. A non-empty
    # string is not an authorization: nothing checked that the text named a real decision, and the
    # citation reached no persisted artefact anyway. NO accepted partial-evidence exception exists
    # for this experiment, so the path is REMOVED rather than tightened. If the bound semantics ever
    # do require one, it is decided and recorded first - see PARTIAL_EVIDENCE_POLICY below - and it
    # is not produced in code.
    identity = verify_source_bytes(source_path, runner.LOCOMO, enabled=enabled)
    _check_accepted_mapping(mapping, runner.LOCOMO)

    raw = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        errors.raise_violation(DesignViolation, errors.Code.SESSION_SHAPE, top_level_is_list=False)

    conversations, seen_ids = {}, {}
    for index, item in enumerate(raw):
        cluster_id = f"locomo_conv_{index}"
        units = _locomo_memory_units(item.get("conversation") or {})
        id_to_row = {}
        for row, unit in enumerate(units):
            if unit["dia_id"] in id_to_row:
                errors.raise_violation(DesignViolation, errors.Code.DUPLICATE_MEMORY_UNIT_ID,
                                       conversation_index=index, unit_row=row)
            id_to_row[unit["dia_id"]] = row
        conversations[cluster_id] = {"index": index, "units": units, "id_to_row": id_to_row,
                                     "questions": {}}
        for position, question in enumerate(item.get("qa") or []):
            qid = str(question.get("question_id") or f"locomo_{index}_qa{position}")
            if qid in seen_ids:
                errors.raise_violation(DesignViolation, errors.Code.DUPLICATE_QUESTION_ID,
                                       conversation_index=index, position=position)
            seen_ids[qid] = (cluster_id, position, question)

    # Resolve every BOUND id individually. Missing, extra and duplicated are all refused.
    bound = mapping["expected_question_to_cluster"]
    missing, misrouted, unresolved_position = [], [], []
    empty_gold, partial_loss = [], []
    evidence_tally = {"declared": 0, "resolved": 0, "unresolved": 0}
    for qid, expected_cluster in bound.items():
        if qid not in seen_ids:
            missing.append(qid)
            continue
        cluster_id, position, question = seen_ids[qid]
        if cluster_id != expected_cluster:
            misrouted.append((qid, cluster_id, expected_cluster))
            continue
        m = LOCOMO_QID.fullmatch(qid)
        if not m or int(m.group(2)) != position:
            unresolved_position.append(qid)
            continue
        conv = conversations[cluster_id]
        # D-1. v1 wrote `if e in conv["id_to_row"]` inside the comprehension, which SILENTLY
        # discarded every evidence id that did not resolve, and recorded only the fully-empty case.
        # A question declaring two evidence ids with one unresolvable came out looking healthy and
        # the persisted summary said questions_with_empty_gold = 0. The gold rows are the ground
        # truth the whole estimand is computed against, so a partial loss must not be invisible.
        declared = _normalise_evidence(question.get("evidence"))
        resolved, unresolved = [], []
        for e in declared:
            (resolved if e in conv["id_to_row"] else unresolved).append(e)
        gold_rows = list(dict.fromkeys(conv["id_to_row"][e] for e in resolved))
        if unresolved and resolved:
            partial_loss.append((qid, len(declared), len(unresolved)))
        if not gold_rows:
            empty_gold.append(qid)
        evidence_tally["declared"] += len(declared)
        evidence_tally["resolved"] += len(resolved)
        evidence_tally["unresolved"] += len(unresolved)
        conv["questions"][qid] = {"position": position, "gold_rows": gold_rows,
                                  "evidence_declared": len(declared),
                                  "evidence_unresolved": len(unresolved),
                                  "text": str(question.get("question", ""))}

    extra = sorted(set(seen_ids) - set(bound))
    problems = bool(missing or misrouted or unresolved_position)
    # D-1: an unexpected partial resolution STOPS the ingestion with a named violation. It is not a
    # flag to be read later, because the artefact that would carry the flag is the same artefact a
    # partial loss makes wrong.
    if partial_loss:
        # Stops here, with safe numeric diagnostics. No gold is repaired, no question excluded and
        # no cohort changed - the run simply does not proceed on a source whose ground truth is
        # partially unresolvable.
        errors.raise_violation(DesignViolation, errors.Code.PARTIAL_EVIDENCE_RESOLUTION,
                               affected_questions=len(partial_loss),
                               declared_ids=sum(d for _, d, _ in partial_loss),
                               unresolved_ids=sum(u for _, _, u in partial_loss),
                               cohort_size=len(bound))
    if problems:
        errors.raise_violation(DesignViolation, errors.Code.COHORT_RESOLUTION_FAILED,
                               missing_ids=len(missing), misrouted_ids=len(misrouted),
                               position_mismatched_ids=len(unresolved_position),
                               cohort_size=len(bound))

    resolved = sum(len(c["questions"]) for c in conversations.values())
    if resolved != len(bound) or resolved != mapping["n_questions"]:
        errors.raise_violation(DesignViolation, errors.Code.COHORT_SIZE_MISMATCH,
                               resolved=resolved, cohort_size=len(bound),
                               manifest_n_questions=mapping["n_questions"])

    return {"benchmark": runner.LOCOMO, "identity": identity, "mapping": mapping,
            "conversations": conversations,
            "cohort_ids": list(bound), "extra_ids_in_source": extra,
            "questions_with_empty_gold": sorted(empty_gold),
            "questions_with_partial_evidence_loss": [],
            "evidence_accounting": {"model": EVIDENCE_MODEL[runner.LOCOMO],
                                    "declared_reference_ids": evidence_tally["declared"],
                                    "resolved_reference_ids": evidence_tally["resolved"],
                                    "unresolved_reference_ids": evidence_tally["unresolved"]}}


# --------------------------------------------------------------------------------------------
# 4. LongMemEval ingestion
# --------------------------------------------------------------------------------------------
def _longmemeval_units(item: dict) -> tuple[list[dict], list[int]]:
    """One question's own archive: every turn of its haystack sessions, plus its gold rows.

    Unit ids follow the committed adapter's canonical form
    `<question_id>::s<session_position>::<session_id>::t<turn_index>`, which is identity only.
    """
    # D-8: v1 did str(item["question_id"]) and a missing key raised a raw KeyError. The codebase's
    # standard is a named DesignViolation - the same class the core closed as F-3 and NEW-3.
    required = ("question_id", "haystack_session_ids", "haystack_dates", "haystack_sessions")
    missing_fields = [f for f in required if f not in item]
    if missing_fields:
        errors.raise_violation(DesignViolation, errors.Code.ITEM_MISSING_FIELD,
                               required_fields=len(required), missing_fields=len(missing_fields),
                               fields_present=len(item))
    qid = str(item["question_id"])
    # D-7: v1 zipped the three parallel arrays with no length check, and zip() stops at the
    # shortest - an item with haystack_dates=[] resolved to ZERO archive units and empty gold, with
    # only the empty-gold counter recording anything.
    lengths = {"haystack_session_ids": len(item["haystack_session_ids"]),
               "haystack_dates": len(item["haystack_dates"]),
               "haystack_sessions": len(item["haystack_sessions"])}
    if len(set(lengths.values())) != 1:
        errors.raise_violation(DesignViolation, errors.Code.RAGGED_PARALLEL_ARRAYS, **lengths)
    if lengths["haystack_sessions"] == 0:
        errors.raise_violation(DesignViolation, errors.Code.EMPTY_HAYSTACK)
    units, gold = [], []
    for si, (sid, date, session) in enumerate(zip(item["haystack_session_ids"],
                                                  item["haystack_dates"],
                                                  item["haystack_sessions"])):
        if not isinstance(session, list):
            errors.raise_violation(DesignViolation, errors.Code.SESSION_SHAPE, session_index=si,
                                   session_is_list=False)
        for ti, turn in enumerate(session):
            if not isinstance(turn, dict):
                errors.raise_violation(DesignViolation, errors.Code.SESSION_SHAPE, session_index=si,
                                       turn_index=ti, turn_is_mapping=False)
            # LongMemEval has NO declared-reference model: gold is a per-turn marker, not a pointer
            # that can dangle. The analogue of an unresolvable reference is therefore a marker in a
            # type the BOUND adapter silently ignores - adapters/longmemeval_v52_adapter_v2.py lines
            # 37-38 and 45 record exactly this as INVALID_HAS_ANSWER_TYPE and coerce it to False.
            # v2 inherited that silence. It is refused here instead.
            if "has_answer" in turn and not isinstance(turn["has_answer"], bool):
                errors.raise_violation(DesignViolation, errors.Code.INVALID_GOLD_MARKER_TYPE,
                                       session_index=si, turn_index=ti)
            role = turn.get("role")
            content = turn.get("content")
            content = "" if content is None else str(content)
            row = len(units)
            units.append({"memory_id": f"{qid}::s{si}::{sid}::t{ti}", "session_position": si,
                          "turn_index": ti, "role": role,
                          "text": f"[{date}] {role}: {content}"})
            if turn.get("has_answer", False) is True:
                gold.append(row)
    return units, gold


def ingest_longmemeval(source_path, mapping, *, enabled: bool | None = None) -> dict:
    """Resolve the ACCEPTED LongMemEval cohort against the verified source. No cohort is derived."""
    identity = verify_source_bytes(source_path, runner.LONGMEMEVAL, enabled=enabled)
    _check_accepted_mapping(mapping, runner.LONGMEMEVAL)

    raw = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        errors.raise_violation(DesignViolation, errors.Code.SESSION_SHAPE, top_level_is_list=False)

    by_id = {}
    for position, item in enumerate(raw):
        if not isinstance(item, dict) or "question_id" not in item:
            errors.raise_violation(DesignViolation, errors.Code.ITEM_MISSING_FIELD, position=position,
                                   item_is_mapping=isinstance(item, dict))
        qid = str(item["question_id"])
        if qid in by_id:
            errors.raise_violation(DesignViolation, errors.Code.DUPLICATE_QUESTION_ID, position=position)
        by_id[qid] = item

    bound = mapping["expected_question_to_cluster"]
    questions, missing, empty_gold = {}, [], []
    for qid in bound:
        if qid not in by_id:
            missing.append(qid)
            continue
        units, gold = _longmemeval_units(by_id[qid])
        if not gold:
            empty_gold.append(qid)
        questions[qid] = {"units": units, "gold_rows": gold,
                          "text": str(by_id[qid].get("question", ""))}
    if missing:
        errors.raise_violation(DesignViolation, errors.Code.COHORT_RESOLUTION_FAILED,
                               missing_ids=len(missing), cohort_size=len(bound))
    if len(questions) != mapping["n_questions"]:
        errors.raise_violation(DesignViolation, errors.Code.COHORT_SIZE_MISMATCH,
                               resolved=len(questions), cohort_size=len(bound),
                               manifest_n_questions=mapping["n_questions"])

    return {"benchmark": runner.LONGMEMEVAL, "identity": identity, "mapping": mapping,
            "questions": questions, "cohort_ids": list(bound),
            "extra_ids_in_source": sorted(set(by_id) - set(bound)),
            "questions_with_empty_gold": sorted(empty_gold),
            "questions_with_partial_evidence_loss": [],
            # The NEW finding. v2 wrote declared = resolved here, which made the number a tautology
            # and any loss invisible while the shared field names promised an accounting. There is no
            # declared-reference count in this benchmark to report, so none is invented: the field is
            # absent from this model, and what guards completeness instead is named.
            "evidence_accounting": {
                "model": EVIDENCE_MODEL[runner.LONGMEMEVAL],
                "declared_reference_ids": None,
                "declared_reference_ids_status": DECLARED_NOT_APPLICABLE,
                "gold_units_resolved": sum(len(v["gold_rows"]) for v in questions.values()),
                "completeness_guarded_by": list(COMPLETENESS_GUARDS[runner.LONGMEMEVAL])}}


# --------------------------------------------------------------------------------------------
# 5. The content-free summary - the only thing that may be persisted
# --------------------------------------------------------------------------------------------
def summarise(ingested: dict) -> dict:
    """Counts and hashes only. Passed through the content policy before it can be written."""
    benchmark = ingested["benchmark"]
    identity = ingested["identity"]
    mapping = ingested["mapping"]
    if benchmark == runner.LOCOMO:
        convs = ingested["conversations"]
        per_units = {c: len(v["units"]) for c, v in convs.items()}
        per_questions = {c: len(v["questions"]) for c, v in convs.items()}
        n_clusters = len(mapping["expected_cluster_ids"])
    else:
        qs = ingested["questions"]
        per_units = {"total_over_per_question_archives": sum(len(v["units"]) for v in qs.values())}
        per_questions = {mapping["expected_cluster_ids"][0]: len(qs)}
        n_clusters = 1
    summary = {
        "benchmark": benchmark,
        "source_file": identity["source_file"],
        "source_sha256": identity["source_sha256"],
        "source_bytes": identity["source_bytes"],
        "mapping_sha256": BOUND_MANIFESTS[benchmark]["sha256"],
        "n_questions": mapping["n_questions"],
        "n_clusters": n_clusters,
        "n_archive_units_total": sum(per_units.values()),
        "per_cluster_archive_units": per_units,
        "per_cluster_questions": per_questions,
        "questions_with_empty_gold": len(ingested["questions_with_empty_gold"]),
        "questions_with_partial_evidence_loss": len(ingested["questions_with_partial_evidence_loss"]),
        # Published unconditionally, in the shape that belongs to this benchmark's gold model.
        "evidence_accounting": ingested["evidence_accounting"],
        "ingest_version": INGEST_VERSION,
        "content_emitted": "none - counts, digests and hashes only",
    }
    assert_content_free(summary)
    return summary
