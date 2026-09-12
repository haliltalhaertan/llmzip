"""Inherited v4 regression suite adapted for the Codex v5 candidate.

DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS. Fake files and synthetic data only. No real corpus is opened,
nothing is fitted, retrieved, ranked or bootstrapped, nothing is sealed. No scan of the real corpus was
made to find out whether the malformed evidence shapes occur there - the fix does not need that, and
reading it is not authorized.

Each item is shown against the **v3** modules first, which are present unchanged on this branch, then
on the Codex candidate. This inherited helper captures displayed traceback, exception repr,
stdout and stderr. test_codex_v5.py separately traverses cause/context even if display is suppressed.
File checks here are explicit assertions, not a universal inventory of filesystem writes.

Run: python -B test_runner_ingest_v4.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent / "membership_runner_ingest_v3_2026_09_08"
CORE = HERE.parent / "membership_impl_v3_2026_09_07"
# Insertion order matters and got this wrong once: each insert goes to position 0, so the LAST one
# inserted is searched FIRST. Listing CORE, V3, HERE leaves sys.path as [HERE, V3, CORE], which is what
# is wanted - this candidate's own modules win. The particular v3 controls used here raise
# plain f-string violations or silently return; they do not exercise the changed formatter.
# Additional original-v4 controls use isolated processes in test_codex_v5.py.
for _p in (CORE, V3, HERE):
    sys.path.insert(0, str(_p))

import membership_scaling_core as core                                           # noqa: E402
import errors                                                                    # noqa: E402
import membership_runner_v4 as R4                                                # noqa: E402
import corpus_ingest_v4 as I4                                                    # noqa: E402
import membership_runner_v3 as R3                                                # noqa: E402  (unchanged)
import corpus_ingest_v3 as I3                                                    # noqa: E402  (unchanged)
from authoritative import accepted_configuration as accepted                     # noqa: E402

FAILURES = []
TMP = Path(tempfile.mkdtemp(prefix="v52_v4_"))
CANARY = "What did Melanie say about her sister's wedding in Lisbon last spring?"     # 70 chars


def check(label, cond, detail=""):
    print((f"ok    {label}   {detail}" if cond else f"FAIL  {label}   {detail}")[:158])
    if not cond:
        FAILURES.append(label)


def surface(fn) -> str:
    out, err = io.StringIO(), io.StringIO()
    tail = ""
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:                                                   # noqa: BLE001
        tail = "".join(traceback.format_exception(type(e), e, e.__traceback__)) + repr(e)
    return out.getvalue() + err.getvalue() + tail


def wj(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return path


def mb(obj) -> bytes:
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


class bind_source:
    def __init__(self, m, b, p):
        self.m, self.b, self.p = m, b, Path(p)

    def __enter__(self):
        self.s = dict(self.m.BOUND_SOURCES[self.b])
        self.m.BOUND_SOURCES[self.b] = dict(self.s, filename=self.p.name,
                                            sha256=hashlib.sha256(self.p.read_bytes()).hexdigest(),
                                            bytes=self.p.stat().st_size)

    def __exit__(self, *_):
        self.m.BOUND_SOURCES[self.b] = self.s


class bind_manifest:
    def __init__(self, b, raw):
        self.b, self.raw = b, raw

    def __enter__(self):
        self.s = dict(accepted.ACCEPTED_MANIFESTS[self.b])
        accepted.ACCEPTED_MANIFESTS[self.b] = dict(self.s, blob_sha256=hashlib.sha256(self.raw).hexdigest())

    def __exit__(self, *_):
        accepted.ACCEPTED_MANIFESTS[self.b] = self.s


class gate_open:
    def __enter__(self):
        self.s = core.REAL_DATA_EXECUTION_ENABLED
        core.REAL_DATA_EXECUTION_ENABLED = True

    def __exit__(self, *_):
        core.REAL_DATA_EXECUTION_ENABLED = self.s


def fake_locomo(evidence, n_turns=4):
    conv = {"speaker_a": "A", "speaker_b": "B",
            "session_1": [{"dia_id": f"D1:{t}", "speaker": "A", "text": f"turn {t}"} for t in range(n_turns)],
            "session_1_date_time": "1 Jan 2020"}
    return [{"sample_id": "conv-0", "conversation": conv,
             "qa": [{"question": "q", "answer": "a", "category": 1, "evidence": evidence}]}]


MAP = {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
       "expected_cluster_ids": ["locomo_conv_0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"}, "n_questions": 1}
MAP_RAW = mb(MAP)

print("=" * 100)
print("IMPLEMENTATION-TEAM SYNTHETIC TESTS - Codex v5 inherited regression. Fake files only.")
print("=" * 100)

# --------------------------------------------------------------------------------------------
print("\n== 1. evidence normalisation: the bound contract, and what is refused ======================")
# --------------------------------------------------------------------------------------------
check("VALID EMPTY: None is the contract's empty representation, and it is not a loss",
      I4._normalise_evidence(None) == ([], 0))
check("VALID EMPTY: an empty list is too", I4._normalise_evidence([]) == ([], 0)
      and I4._normalise_evidence(()) == ([], 0))
check("VALID: a list of id strings normalises unchanged",
      I4._normalise_evidence(["D1:0", "D1:2"]) == (["D1:0", "D1:2"], 2))
check("VALID: a dict carrying dia_id, and one carrying id, both normalise",
      I4._normalise_evidence([{"dia_id": "D1:0"}, {"id": "D1:1"}]) == (["D1:0", "D1:1"], 2))
check("VALID: the producer's whole-string fallback is PRESERVED, because it is the bound contract",
      I4._normalise_evidence("not-an-id-shape") == (["not-an-id-shape"], 1))
check("VALID: de-duplication of genuine repeats is unchanged - two identical ids give one reference",
      I4._normalise_evidence(["D1:0", "D1:0"]) == (["D1:0"], 2),
      "raw items 2, normalised references 1 - the two counts are deliberately different")

MALFORMED = {
    "a dict with neither dia_id nor id": [{"speaker": "A"}],
    "a dict whose id is empty": [{"dia_id": ""}],
    "a dict whose id is null": [{"dia_id": None}],
    "a non-string, non-dict list item": [7],
    "a malformed FIRST item": [{"x": 1}, "D1:0", "D1:1"],
    "a malformed MIDDLE item": ["D1:0", 7, "D1:1"],
    "a malformed LAST item": ["D1:0", "D1:1", {"x": 1}],
}
for label, value in MALFORMED.items():
    old = surface(lambda v=value: I3._normalise_evidence(v))
    new = surface(lambda v=value: I4._normalise_evidence(v))
    check(f"NEGATIVE CONTROL: v3 SILENTLY DISCARDS {label}", old == "",
          f"no exception; v3 returned {I3._normalise_evidence(value)}")
    check(f"CLOSED: v4 refuses {label} with E-COH-011",
          errors.Code.EVIDENCE_ITEM_MALFORMED.value in new)
    check(f"...and the refusal carries no content for {label}", CANARY not in new and "'x'" not in new)

for label, value in {"an int": 7, "a top-level dict": {"dia_id": "D1:0"}, "a set": {"D1:0"}}.items():
    old = surface(lambda v=value: I3._normalise_evidence(v))
    new = surface(lambda v=value: I4._normalise_evidence(v))
    check(f"NEGATIVE CONTROL: v3 silently returns [] for {label}", old == "" and I3._normalise_evidence(value) == [])
    check(f"CLOSED: v4 refuses {label} as an unsupported structure, E-COH-012",
          errors.Code.EVIDENCE_STRUCTURE_UNSUPPORTED.value in new)

check("the two faults are DIFFERENT codes, because they are different faults",
      errors.Code.EVIDENCE_ITEM_MALFORMED.value != errors.Code.EVIDENCE_STRUCTURE_UNSUPPORTED.value)
class CoercionTrap:
    calls = 0

    def __str__(self):
        self.calls += 1
        return CANARY

    def __repr__(self):
        self.calls += 1
        return CANARY


for position in range(3):
    trap = CoercionTrap()
    values = ["D1:0", "D1:1"]
    values.insert(position, trap)
    caught = None
    try:
        I4._normalise_evidence(values)
    except core.DesignViolation as exc:
        caught = exc
    check(f"malformed object at {position} is refused without coercion",
          caught is not None and errors.Code.EVIDENCE_ITEM_MALFORMED.value in str(caught)
          and trap.calls == 0 and CANARY not in str(caught))

# --------------------------------------------------------------------------------------------
print("\n== 2. 'one valid + one malformed' can no longer be reported as complete =====================")
# --------------------------------------------------------------------------------------------
mixed = wj(TMP / "mixed" / "locomo10.json", fake_locomo(["D1:0", {"speaker": "A"}]))
clean = wj(TMP / "clean" / "locomo10.json", fake_locomo(["D1:0", "D1:1"]))
dupes = wj(TMP / "dupes" / "locomo10.json", fake_locomo(["D1:0", "D1:0"]))

with gate_open(), bind_manifest(accepted.LOCOMO, MAP_RAW):
    m3 = R3.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    m4 = R4.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    with bind_source(I3, accepted.LOCOMO, mixed):
        s3 = I3.summarise(I3.ingest_locomo(mixed, m3))
        ea3 = s3["evidence_accounting"]
        check("NEGATIVE CONTROL: v3 reports the mixed source as SUCCESSFUL AND LOSSLESS",
              ea3["declared_reference_ids"] == ea3["resolved_reference_ids"] == 1
              and ea3["unresolved_reference_ids"] == 0 and s3["questions_with_empty_gold"] == 0
              and s3["questions_with_partial_evidence_loss"] == 0,
              "one of two source entries vanished and every published number says nothing was lost")
    with bind_source(I4, accepted.LOCOMO, mixed):
        txt = surface(lambda: I4.ingest_locomo(mixed, m4))
        check("CLOSED: v4 stops on the mixed source", errors.Code.EVIDENCE_ITEM_MALFORMED.value in txt)
        check("CLOSED: and it writes nothing", not list((TMP / "mixed").glob("*.out")))
    with bind_source(I4, accepted.LOCOMO, clean):
        s4 = I4.summarise(I4.ingest_locomo(clean, m4))
        ea4 = s4["evidence_accounting"]
        check("a clean source still ingests, unchanged",
              ea4["declared_reference_ids"] == 2 and ea4["resolved_reference_ids"] == 2
              and ea4["unresolved_reference_ids"] == 0)
        check("THREE COUNTS are published as three fields, not two with a third inferred",
              ea4["raw_evidence_items"] == 2 and set(ea4) >= {"raw_evidence_items", "declared_reference_ids",
                                                              "resolved_reference_ids", "unresolved_reference_ids"})
    with bind_source(I4, accepted.LOCOMO, dupes):
        ea = I4.summarise(I4.ingest_locomo(dupes, m4))["evidence_accounting"]
        check("valid repeats keep the existing set semantics, and the difference is now VISIBLE",
              ea["raw_evidence_items"] == 2 and ea["declared_reference_ids"] == 1
              and ea["resolved_reference_ids"] == 1)
    check("no question was excluded, no gold repaired, no cohort changed",
          s4["n_questions"] == 1 and s4["n_clusters"] == 1)

# --------------------------------------------------------------------------------------------
print("\n== 3. the two remaining error paths ========================================================")
# --------------------------------------------------------------------------------------------
old = surface(lambda: R3.validate_identifier(" x", CANARY, 0))
new = surface(lambda: R4.validate_identifier(" x", CANARY, 0))
check("NEGATIVE CONTROL: v3 echoes the caller's `kind` verbatim", CANARY in old)
check("CLOSED: v4 refuses an unknown identifier kind without echoing it",
      CANARY not in new and errors.Code.IDENTIFIER_KIND_UNKNOWN.value in new)
check("v4 takes `kind` from a closed enumeration",
      [k.value for k in R4.IdentifierKind] == ["question_id", "cluster_id"])
for bad, code in [(" x", errors.Code.IDENTIFIER_WHITESPACE), ("", errors.Code.MISSING_VALUE_INDICATOR),
                  (7, errors.Code.UNSUPPORTED_ID_TYPE)]:
    t = surface(lambda b=bad: R4.validate_identifier(b, R4.IdentifierKind.QUESTION_ID, 3))
    check(f"...and a genuine identifier fault still refuses by code ({code.value})",
          code.value in t and "kind=question_id" in t and "position=3" in t)

bad_map = dict(MAP, n_questions=CANARY)
old = surface(lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], bad_map))
new = surface(lambda: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], bad_map))
check("NEGATIVE CONTROL: v3 raises an uncaught ValueError carrying the value out", CANARY in old
      and "ValueError" in old)
check("CLOSED: v4 refuses the manifest field by type, with no content and no ValueError",
      CANARY not in new and errors.Code.MANIFEST_FIELD_TYPE.value in new and "ValueError" not in new)
for field, value in [("expected_question_to_cluster", CANARY), ("expected_cluster_ids", CANARY),
                     ("n_questions", 1.5), ("n_questions", True)]:
    t = surface(lambda f=field, v=value: R4.verify_source_identity(
        ["locomo_0_qa0"], ["locomo_conv_0"], dict(MAP, **{f: v})))
    check(f"...and {field}={type(value).__name__} is refused the same way, no content",
          errors.Code.MANIFEST_FIELD_TYPE.value in t and CANARY not in t)
check("a well-formed manifest still passes the identity contract",
      R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], MAP)["n_questions"] == 1)

# --------------------------------------------------------------------------------------------
print("\n== 4. candidate module identity ============================================================")
# --------------------------------------------------------------------------------------------
rsrc = (HERE / "membership_runner_v4.py").read_text(encoding="utf-8")
isrc = (HERE / "corpus_ingest_v4.py").read_text(encoding="utf-8")
check("runner module comes from this candidate", Path(R4.__file__).resolve().parent == HERE)
check("ingest module comes from this candidate", Path(I4.__file__).resolve().parent == HERE)
check("error module comes from this candidate", Path(errors.__file__).resolve().parent == HERE)
# Historical prose-string assertions are not behavioral evidence. Documentation is reviewed
# against the actual delta and the independent-audit handoff, not certified by keyword matching.

# --------------------------------------------------------------------------------------------
print("\n== 5. regression ===========================================================================")
# --------------------------------------------------------------------------------------------
with bind_manifest(accepted.LOCOMO, MAP_RAW):
    seed = TMP / "seed.json"
    R4.freeze_bootstrap_seed(seed, 52001107, accepted.LOCOMO, "question", 10000)
    check("D-3 still closed", errors.Code.SEED_NOT_ACCEPTED.value in
          surface(lambda: R4.freeze_bootstrap_seed(TMP / "s2.json", 999, accepted.LOCOMO, "question", 10000)))
    recs = [{"question_id": "locomo_0_qa0", "rotation_seed": int(s), "arm": a, "fractional_R3": 0.5}
            for s in core.ROTATION_SEEDS for a in core.ARMS]
    check("D-2 still closed", errors.Code.REPLICATES_CONTRADICT_RECORD.value in
          surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], m4, seed,
                                             benchmark=accepted.LOCOMO, scheme="question", replicates=7)))
    check("F12 ordering still closed", errors.Code.MAPPING_NOT_FROM_ACCEPTED_PATH.value in
          surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], {"benchmark": CANARY},
                                             seed, benchmark=accepted.LOCOMO, scheme="question", replicates=10000)))
    check("F20 still closed: nothing read from a seed record reaches a message",
          CANARY not in surface(lambda: R4.read_bootstrap_seed(
              wj(TMP / "poison.json", {"bootstrap_seed": 1, "benchmark": CANARY, "scheme": CANARY,
                                       "replicates": 1}), accepted.LOCOMO, "question")))
    check("the accepted configuration still runs end to end",
          R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], m4, seed,
                             benchmark=accepted.LOCOMO, scheme="question",
                             replicates=10000)["bootstrap_seed_record"]["replicates"] == 10000)

lme_map = {"source_id": "f", "source_sha256": "0" * 64, "benchmark": accepted.LONGMEMEVAL,
           "expected_cluster_ids": ["longmemeval_single_connected_component_inherited_task3a1"],
           "expected_question_to_cluster": {"q0": "longmemeval_single_connected_component_inherited_task3a1"},
           "n_questions": 1}
lme_raw = mb(lme_map)
lme_src = wj(TMP / "lme" / "longmemeval_s_cleaned.json",
             [{"question_id": "q0", "question": "q", "answer": "a", "haystack_session_ids": ["s0"],
               "haystack_dates": ["d0"], "haystack_sessions": [[{"role": "user", "content": "c", "has_answer": True}]]}])
with gate_open(), bind_manifest(accepted.LONGMEMEVAL, lme_raw), bind_source(I4, accepted.LONGMEMEVAL, lme_src):
    ea = I4.summarise(I4.ingest_longmemeval(lme_src, R4.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lme_raw)))["evidence_accounting"]
    check("LongMemEval accounting still closed", ea["declared_reference_ids"] is None
          and ea["gold_units_resolved"] == 1 and ea["model"] == "per_turn_gold_markers")
check("gates still closed", core.REAL_DATA_EXECUTION_ENABLED is False
      and "not authorized" in surface(lambda: R4.run_on_real_corpus()))
check("the closed core is untouched",
      hashlib.sha256((CORE / "membership_scaling_core.py").read_bytes()).hexdigest()
      == accepted.BOUND_CORE["blob_sha256"])
# The historical empty-iteration assertion was not an I/O observation and is removed.
# test_codex_v5.py installs and exercises a Python audit-hook guard. This inherited suite's
# corpus access is separately guarded by the launcher that runs it, not inferred from an empty list.

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): {FAILURES}")
    raise SystemExit(1)
print("ALL PASS")
print("Scope: DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS for the evidence normalisation, the two remaining "
      "error paths and the claim corrections. Fake files only. Not a seal, not run authorization.")
raise SystemExit(0)
