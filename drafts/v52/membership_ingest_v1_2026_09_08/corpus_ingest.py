"""Corpus ingestion for the V52 membership-under-scaling experiment - WRITTEN, NOT AUTHORIZED TO RUN.

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
  3. resolve EVERY bound question id INDIVIDUALLY against the source, refusing missing, extra and
     duplicated ids rather than repairing them;
  4. assemble the archive memory units and the query texts IN MEMORY, with their gold row indices.

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

CONTENT NEVER LEAVES MEMORY
----------------------------
Question, answer, dialogue and session text is held in memory and handed to the caller. It is never
printed, logged, put in an exception message, or written to disk. `write_ingest_manifest` is the only
writer and it refuses any payload that could carry content: every value is checked against a
conservative policy before a byte is written, and it goes through the core's refuse-to-overwrite path.
"""
from __future__ import annotations

import hashlib
import json
import numbers
import re
import sys
from pathlib import Path

_RUNNER = Path(__file__).resolve().parents[1] / "membership_runner_v1_2026_09_08"
_CORE = Path(__file__).resolve().parents[1] / "membership_impl_v3_2026_09_07"
for _p in (str(_RUNNER), str(_CORE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import membership_runner as runner                                               # noqa: E402
import membership_scaling_core as core                                           # noqa: E402

DesignViolation = core.DesignViolation


class ContentPolicyViolation(DesignViolation):
    """Raised when something that could carry source content is about to be written or logged."""


# --------------------------------------------------------------------------------------------
# Bound sources. Values only - no path is resolved and no file is opened at import time.
# --------------------------------------------------------------------------------------------
BOUND_SOURCES = {
    runner.LOCOMO: {
        "filename": "locomo10.json",
        "sha256": "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4",
        "bytes": 2805274,
        "companion": "audit/errors_conv_*.json - 156 audit corrections, needed only to REPRODUCE the "
                     "producer's selection rule, which this module does not do",
    },
    runner.LONGMEMEVAL: {
        "filename": "longmemeval_s_cleaned.json",
        "sha256": "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442",
        "bytes": 277383467,
        "companion": None,
    },
}

BOUND_MANIFESTS = {
    runner.LOCOMO: {
        "path": "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json",
        "sha256": "66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671"},
    runner.LONGMEMEVAL: {
        "path": ("drafts/v52/membership_runner_v1_2026_09_08/binding/"
                 "PROPOSED_mapping_longmemeval_v2_source_resolved.json"),
        "sha256": "d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714"},
}

INGEST_MANIFEST_KEYS = frozenset({
    "benchmark", "source_file", "source_sha256", "source_bytes", "mapping_sha256",
    "n_questions", "n_clusters", "n_archive_units_total", "per_cluster_archive_units",
    "per_cluster_questions", "questions_with_empty_gold", "ingest_version", "content_emitted"})

INGEST_VERSION = "corpus_ingest v1 2026-09-08"

LOCOMO_QID = re.compile(r"^locomo_(\d+)_qa(\d+)$")
_DIA_ID = re.compile(r"D\d+:\d+")


# --------------------------------------------------------------------------------------------
# 1. Source byte identity - checked BEFORE any parsing
# --------------------------------------------------------------------------------------------
def verify_source_bytes(path, benchmark: str, *, enabled: bool | None = None) -> dict:
    """Stream the file and compare sha256 and size against the bound values. Refuses first.

    This is the only place a corpus path is opened for hashing, and it happens before `json.loads`
    ever sees a byte: a wrong, truncated or altered file is refused without its content being parsed.
    """
    core.require_real_data_authorization(enabled)
    if benchmark not in BOUND_SOURCES:
        raise DesignViolation(f"unknown benchmark {benchmark!r}")
    bound = BOUND_SOURCES[benchmark]
    path = Path(path)
    if not path.is_file():
        raise DesignViolation(f"bound source not found at {path}")
    if path.name != bound["filename"]:
        raise DesignViolation(
            f"bound source for {benchmark} is {bound['filename']!r}, got {path.name!r}; the runner "
            f"does not accept a renamed source")
    size = path.stat().st_size
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    digest = h.hexdigest()
    if size != bound["bytes"] or digest != bound["sha256"]:
        raise DesignViolation(
            f"source identity mismatch for {benchmark}: bound {bound['sha256']} / {bound['bytes']} "
            f"bytes, read {digest} / {size} bytes")
    return {"source_file": path.name, "source_sha256": digest, "source_bytes": size}


def load_bound_mapping(manifest_path, benchmark: str) -> dict:
    """Load the bound manifest through the runner's hash-checked loader. No corpus is touched."""
    if benchmark not in BOUND_MANIFESTS:
        raise DesignViolation(f"unknown benchmark {benchmark!r}")
    return runner.load_expected_mapping(manifest_path, BOUND_MANIFESTS[benchmark]["sha256"])


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
            raise ContentPolicyViolation(
                f"{_path}: a string of {len(payload)} characters may carry source content and is "
                f"refused (limit {_MAX_STRING})")
        return
    if payload is None or isinstance(payload, bool) or isinstance(payload, numbers.Real):
        return
    if isinstance(payload, dict):
        for k, v in payload.items():
            assert_content_free(k, f"{_path}.<key>")
            assert_content_free(v, f"{_path}.{k}")
        return
    if isinstance(payload, (list, tuple)):
        for i, v in enumerate(payload):
            assert_content_free(v, f"{_path}[{i}]")
        return
    raise ContentPolicyViolation(f"{_path}: type {type(payload).__name__} is not allowed in a written manifest")


def write_ingest_manifest(path, manifest: dict):
    """The ONLY writer in this module. Schema-checked, content-checked, refuses to overwrite."""
    if set(manifest) != INGEST_MANIFEST_KEYS:
        raise DesignViolation(
            f"ingest manifest schema mismatch: missing {sorted(INGEST_MANIFEST_KEYS - set(manifest))}, "
            f"unexpected {sorted(set(manifest) - INGEST_MANIFEST_KEYS)}")
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


def ingest_locomo(source_path, manifest_path, *, enabled: bool | None = None) -> dict:
    """Resolve the BOUND LoCoMo cohort against the verified source. No cohort is derived.

    Returns in-memory structures. Nothing here is printed or written; the caller decides what to do
    with them, and only `write_ingest_manifest` may put anything on disk.
    """
    identity = verify_source_bytes(source_path, runner.LOCOMO, enabled=enabled)
    mapping = load_bound_mapping(manifest_path, runner.LOCOMO)

    raw = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DesignViolation("the LoCoMo source must be a list of conversations")

    conversations, seen_ids = {}, {}
    for index, item in enumerate(raw):
        cluster_id = f"locomo_conv_{index}"
        units = _locomo_memory_units(item.get("conversation") or {})
        id_to_row = {}
        for row, unit in enumerate(units):
            if unit["dia_id"] in id_to_row:
                raise DesignViolation(
                    f"duplicate memory unit id in {cluster_id}; the archive must be a set of units")
            id_to_row[unit["dia_id"]] = row
        conversations[cluster_id] = {"index": index, "units": units, "id_to_row": id_to_row,
                                     "questions": {}}
        for position, question in enumerate(item.get("qa") or []):
            qid = str(question.get("question_id") or f"locomo_{index}_qa{position}")
            if qid in seen_ids:
                raise DesignViolation(f"question id {qid!r} occurs more than once in the source")
            seen_ids[qid] = (cluster_id, position, question)

    # Resolve every BOUND id individually. Missing, extra and duplicated are all refused.
    bound = mapping["expected_question_to_cluster"]
    missing, misrouted, unresolved_position = [], [], []
    empty_gold = []
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
        gold_rows = list(dict.fromkeys(
            conv["id_to_row"][e] for e in _normalise_evidence(question.get("evidence"))
            if e in conv["id_to_row"]))
        if not gold_rows:
            empty_gold.append(qid)
        conv["questions"][qid] = {"position": position, "gold_rows": gold_rows,
                                  "text": str(question.get("question", ""))}

    extra = sorted(set(seen_ids) - set(bound))
    problems = []
    if missing:
        problems.append(f"{len(missing)} bound question id(s) absent from the source, e.g. {missing[:3]}")
    if misrouted:
        problems.append(f"{len(misrouted)} question(s) in the wrong conversation, e.g. {misrouted[:3]}")
    if unresolved_position:
        problems.append(
            f"{len(unresolved_position)} id(s) whose positional index does not match their position "
            f"in the source, e.g. {unresolved_position[:3]}")
    if problems:
        raise DesignViolation("LoCoMo cohort resolution failed: " + "; ".join(problems))

    resolved = sum(len(c["questions"]) for c in conversations.values())
    if resolved != len(bound) or resolved != mapping["n_questions"]:
        raise DesignViolation(
            f"resolved {resolved} questions against a bound cohort of {len(bound)}")

    return {"benchmark": runner.LOCOMO, "identity": identity, "mapping": mapping,
            "conversations": conversations,
            "cohort_ids": list(bound), "extra_ids_in_source": extra,
            "questions_with_empty_gold": sorted(empty_gold)}


# --------------------------------------------------------------------------------------------
# 4. LongMemEval ingestion
# --------------------------------------------------------------------------------------------
def _longmemeval_units(item: dict) -> tuple[list[dict], list[int]]:
    """One question's own archive: every turn of its haystack sessions, plus its gold rows.

    Unit ids follow the committed adapter's canonical form
    `<question_id>::s<session_position>::<session_id>::t<turn_index>`, which is identity only.
    """
    qid = str(item["question_id"])
    units, gold = [], []
    for si, (sid, date, session) in enumerate(zip(item["haystack_session_ids"],
                                                  item["haystack_dates"],
                                                  item["haystack_sessions"])):
        if not isinstance(session, list):
            raise DesignViolation(f"haystack session {si} of a question is not a list")
        for ti, turn in enumerate(session):
            if not isinstance(turn, dict):
                raise DesignViolation(f"turn {ti} of session {si} is not a mapping")
            role = turn.get("role")
            content = turn.get("content")
            content = "" if content is None else str(content)
            has_answer = turn.get("has_answer", False)
            row = len(units)
            units.append({"memory_id": f"{qid}::s{si}::{sid}::t{ti}", "session_position": si,
                          "turn_index": ti, "role": role,
                          "text": f"[{date}] {role}: {content}"})
            if has_answer is True:
                gold.append(row)
    return units, gold


def ingest_longmemeval(source_path, manifest_path, *, enabled: bool | None = None) -> dict:
    """Resolve the BOUND LongMemEval cohort against the verified source. No cohort is derived."""
    identity = verify_source_bytes(source_path, runner.LONGMEMEVAL, enabled=enabled)
    mapping = load_bound_mapping(manifest_path, runner.LONGMEMEVAL)

    raw = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DesignViolation("the LongMemEval source must be a list of items")

    by_id = {}
    for item in raw:
        qid = str(item["question_id"])
        if qid in by_id:
            raise DesignViolation(f"question id {qid!r} occurs more than once in the source")
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
        raise DesignViolation(
            f"LongMemEval cohort resolution failed: {len(missing)} bound question id(s) absent from "
            f"the source, e.g. {missing[:3]}")
    if len(questions) != mapping["n_questions"]:
        raise DesignViolation(
            f"resolved {len(questions)} questions against a bound cohort of {mapping['n_questions']}")

    return {"benchmark": runner.LONGMEMEVAL, "identity": identity, "mapping": mapping,
            "questions": questions, "cohort_ids": list(bound),
            "extra_ids_in_source": sorted(set(by_id) - set(bound)),
            "questions_with_empty_gold": sorted(empty_gold)}


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
        "ingest_version": INGEST_VERSION,
        "content_emitted": "none - counts, identifiers and hashes only",
    }
    assert_content_free(summary)
    return summary
