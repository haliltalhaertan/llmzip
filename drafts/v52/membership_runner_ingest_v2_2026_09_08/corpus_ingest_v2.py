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

What v2 does instead, stated as behaviour rather than as a promise:
  * NO value is interpolated into any message raised or printed by this module. Every message is
    built from counts, positions, field names and `safe_report` descriptions - type, shape, digest.
  * The manifest writer still applies the closed schema and the structural content policy before a
    byte is written.
  * Text IS held in memory and handed to the caller - that is what ingestion is for. A caller that
    prints what it is handed defeats all of this, and no module can prevent that. The tests check
    stdout, stderr, exception text and written files for synthetic sub-120-character fragments; they
    do not and cannot check what a caller does afterwards.
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

import membership_runner_v2 as runner                                            # noqa: E402
import membership_scaling_core as core                                           # noqa: E402
import safe_report                                                               # noqa: E402
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
    # D-1: evidence accounting. v1 published only `questions_with_empty_gold`, a count of the FULLY
    # empty case, so a question that declared two evidence ids and resolved one looked healthy in
    # the only artefact that reaches disk. All three are now published, unconditionally.
    "evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
    "questions_with_empty_gold", "questions_with_partial_evidence_loss"})

INGEST_VERSION = "corpus_ingest v2 2026-09-08"

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
    if not isinstance(mapping, dict):
        raise DesignViolation(
            f"the mapping must be the dict returned by an accepted-resolution loader, got "
            f"{safe_report.describe(mapping)}")
    if mapping.get("_accepted_manifest_sha256") != accepted.ACCEPTED_MANIFESTS[benchmark]["blob_sha256"]:
        raise DesignViolation(
            f"this mapping did not come through the accepted-resolution path for {benchmark}; only "
            f"the ACCEPTED manifest, resolved from the authoritative configuration, may be used")


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
            f"the accepted source for {benchmark} is named {bound['filename']!r}; a differently "
            f"named file is not accepted (given name digest "
            f"{safe_report.digest(path.name)}, {len(path.name)} chars)")
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
            raise ContentPolicyViolation(
                f"{_path}: a string of {len(payload)} characters may carry source content and is "
                f"refused (structural limit {_MAX_STRING}; this limit is a blunt check, NOT a "
                f"guarantee - see the module docstring)")
        return
    if payload is None or isinstance(payload, bool) or isinstance(payload, numbers.Real):
        return
    if isinstance(payload, dict):
        # D-5: v1 built the child path as f"{_path}.{k}", which interpolated the KEY verbatim and
        # echoed it when a sibling value failed - the policy leaked through its own error. Keys are
        # now reported by index and digest.
        for i, (k, v) in enumerate(payload.items()):
            assert_content_free(k, f"{_path}.<key {i}>")
            assert_content_free(v, f"{_path}.<value {i} of key digest {safe_report.digest(k)}>")
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


def ingest_locomo(source_path, mapping, *, enabled: bool | None = None,
                  allow_partial_evidence: bool = False,
                  partial_evidence_citation: str | None = None) -> dict:
    """Resolve the BOUND LoCoMo cohort against the verified source. No cohort is derived.

    Returns in-memory structures. Nothing here is printed or written; the caller decides what to do
    with them, and only `write_ingest_manifest` may put anything on disk.
    """
    if allow_partial_evidence and not partial_evidence_citation:
        raise DesignViolation(
            "allow_partial_evidence requires partial_evidence_citation: the document or committed "
            "record that permits partial evidence resolution for this source. A waiver without a "
            "citation is a silent repair under another name (D-1)")
    identity = verify_source_bytes(source_path, runner.LOCOMO, enabled=enabled)
    _check_accepted_mapping(mapping, runner.LOCOMO)

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
                raise DesignViolation(
                    f"a question id occurs more than once in the source, at {cluster_id} position "
                    f"{position} (id digest {safe_report.digest(qid)})")
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
    problems = []
    if missing:
        problems.append(f"{len(missing)} accepted question id(s) absent from the source: "
                        f"{safe_report.describe_many(missing)}")
    if misrouted:
        problems.append(f"{len(misrouted)} question(s) in the wrong conversation: "
                        f"{safe_report.describe_many([q for q, _, _ in misrouted])}")
    if unresolved_position:
        problems.append(
            f"{len(unresolved_position)} id(s) whose positional index does not match their position "
            f"in the source: {safe_report.describe_many(unresolved_position)}")
    # D-1: an unexpected partial resolution STOPS the ingestion with a named violation. It is not a
    # flag to be read later, because the artefact that would carry the flag is the same artefact a
    # partial loss makes wrong.
    if partial_loss and not allow_partial_evidence:
        problems.append(
            f"{len(partial_loss)} question(s) have PARTIALLY unresolvable evidence - some declared "
            f"evidence ids resolve and some do not, so the gold set is silently smaller than the "
            f"source declares: "
            + safe_report.counts(questions=len(partial_loss),
                                 declared=sum(d for _, d, _ in partial_loss),
                                 unresolved=sum(u for _, _, u in partial_loss))
            + ". If this is a historically permitted state for this source, pass "
              "allow_partial_evidence=True WITH the citation that permits it; it is then recorded "
              "in the manifest rather than waived silently (D-1)")
    if problems:
        raise DesignViolation("LoCoMo cohort resolution failed: " + "; ".join(problems))

    resolved = sum(len(c["questions"]) for c in conversations.values())
    if resolved != len(bound) or resolved != mapping["n_questions"]:
        raise DesignViolation(
            f"resolved {resolved} questions against a bound cohort of {len(bound)}")

    return {"benchmark": runner.LOCOMO, "identity": identity, "mapping": mapping,
            "conversations": conversations,
            "cohort_ids": list(bound), "extra_ids_in_source": extra,
            "questions_with_empty_gold": sorted(empty_gold),
            "questions_with_partial_evidence_loss": sorted(q for q, _, _ in partial_loss),
            "evidence_tally": dict(evidence_tally),
            "partial_evidence_waiver": ({"allowed": True, "citation": partial_evidence_citation}
                                        if allow_partial_evidence else {"allowed": False, "citation": None})}


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
    for field in ("question_id", "haystack_session_ids", "haystack_dates", "haystack_sessions"):
        if field not in item:
            raise DesignViolation(
                f"a LongMemEval item is missing the required field {field!r} "
                f"({safe_report.counts(fields_present=len(item))})")
    qid = str(item["question_id"])
    # D-7: v1 zipped the three parallel arrays with no length check, and zip() stops at the
    # shortest - an item with haystack_dates=[] resolved to ZERO archive units and empty gold, with
    # only the empty-gold counter recording anything.
    lengths = {"haystack_session_ids": len(item["haystack_session_ids"]),
               "haystack_dates": len(item["haystack_dates"]),
               "haystack_sessions": len(item["haystack_sessions"])}
    if len(set(lengths.values())) != 1:
        raise DesignViolation(
            f"the parallel haystack arrays of a LongMemEval item have different lengths "
            f"({safe_report.counts(**lengths)}); zipping them would silently truncate to the "
            f"shortest (D-7)")
    if lengths["haystack_sessions"] == 0:
        raise DesignViolation("a LongMemEval item has no haystack sessions, so its archive is empty")
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


def ingest_longmemeval(source_path, mapping, *, enabled: bool | None = None) -> dict:
    """Resolve the ACCEPTED LongMemEval cohort against the verified source. No cohort is derived."""
    identity = verify_source_bytes(source_path, runner.LONGMEMEVAL, enabled=enabled)
    _check_accepted_mapping(mapping, runner.LONGMEMEVAL)

    raw = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DesignViolation("the LongMemEval source must be a list of items")

    by_id = {}
    for position, item in enumerate(raw):
        if not isinstance(item, dict) or "question_id" not in item:
            raise DesignViolation(
                f"the LongMemEval item at position {position} is not a mapping with a question_id (D-8)")
        qid = str(item["question_id"])
        if qid in by_id:
            raise DesignViolation(
                f"a question id occurs more than once in the source, at position {position} "
                f"(id digest {safe_report.digest(qid)})")
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
            f"LongMemEval cohort resolution failed: {len(missing)} accepted question id(s) absent "
            f"from the source: {safe_report.describe_many(missing)}")
    if len(questions) != mapping["n_questions"]:
        raise DesignViolation(
            f"resolved {len(questions)} questions against a bound cohort of {mapping['n_questions']}")

    return {"benchmark": runner.LONGMEMEVAL, "identity": identity, "mapping": mapping,
            "questions": questions, "cohort_ids": list(bound),
            "extra_ids_in_source": sorted(set(by_id) - set(bound)),
            "questions_with_empty_gold": sorted(empty_gold),
            "questions_with_partial_evidence_loss": [],
            "evidence_tally": {"declared": sum(len(v["gold_rows"]) for v in questions.values()),
                               "resolved": sum(len(v["gold_rows"]) for v in questions.values()),
                               "unresolved": 0},
            "partial_evidence_waiver": {"allowed": False, "citation": None}}


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
        # D-1: published unconditionally, so a partial loss of ground truth is visible in the only
        # artefact that reaches disk.
        "questions_with_partial_evidence_loss": len(ingested["questions_with_partial_evidence_loss"]),
        "evidence_ids_declared": ingested["evidence_tally"]["declared"],
        "evidence_ids_resolved": ingested["evidence_tally"]["resolved"],
        "evidence_ids_unresolved": ingested["evidence_tally"]["unresolved"],
        "ingest_version": INGEST_VERSION,
        "content_emitted": "none - counts, digests and hashes only",
    }
    assert_content_free(summary)
    return summary
