"""v3 delta tests: the nine D-5 paths, the D-1 policy, and LongMemEval evidence accounting.

DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS. Fake files and synthetic data only. No real corpus, no
fitting, retrieval, ranking or real-data bootstrap, nothing sealed.

Every item is tested the same way: the OLD behaviour is reproduced against the **v2** modules, which
are present unchanged on this branch, and then the v3 behaviour is shown on the same input.

THE LEAK SURFACE THIS SUITE CHECKS: for each probe it captures stdout, stderr, the exception message,
AND the whole `__cause__`/`__context__` chain, plus every file written. Canaries are all shorter than
the 120-character structural limit, and they are driven in as caller-supplied values, as values read
back out of a JSON file the pipeline wrote, and as parsed corpus text.

Run: python -B test_runner_ingest_v3.py
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
V2 = HERE.parent / "membership_runner_ingest_v2_2026_09_08"
CORE = HERE.parent / "membership_impl_v3_2026_09_07"
for _p in (HERE, V2, CORE):
    sys.path.insert(0, str(_p))

import numpy as np                                                               # noqa: E402
import membership_scaling_core as core                                           # noqa: E402
import errors                                                                    # noqa: E402
import membership_runner_v3 as R3                                                # noqa: E402
import corpus_ingest_v3 as I3                                                    # noqa: E402
import membership_runner_v2 as R2                                                # noqa: E402  (unchanged)
import corpus_ingest_v2 as I2                                                    # noqa: E402  (unchanged)
from authoritative import accepted_configuration as accepted                     # noqa: E402
from authoritative import resolve_sources                                        # noqa: E402

FAILURES = []
TMP = Path(tempfile.mkdtemp(prefix="v52_v3_"))
REPO = Path(subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip())

CANARIES = {
    "question": "What did Melanie say about her sister's wedding in Lisbon last spring?",   # 70
    "answer": "She said the ceremony was moved to a vineyard outside Sintra.",             # 61
    "session": "Melanie: I finally booked the flights for the wedding weekend.",           # 60
}


def check(label, cond, detail=""):
    print((f"ok    {label}   {detail}" if cond else f"FAIL  {label}   {detail}")[:158])
    if not cond:
        FAILURES.append(label)


def surface(fn) -> str:
    """Everything a call could emit: stdout, stderr, the message, and the whole exception chain."""
    out, err = io.StringIO(), io.StringIO()
    tail = ""
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:                                                   # noqa: BLE001
        tail = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    return out.getvalue() + err.getvalue() + tail


def leaked(text) -> list:
    return [k for k, v in CANARIES.items() if v in text]


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


def fake_locomo(n_conv=1, n_q=1, n_turns=4, evidence=None, canary=False):
    out = []
    for c in range(n_conv):
        conv = {"speaker_a": "A", "speaker_b": "B",
                "session_1": [{"dia_id": f"D1:{t}", "speaker": "Melanie",
                               "text": CANARIES["session"] if canary else f"turn {t}"}
                              for t in range(n_turns)],
                "session_1_date_time": "1 Jan 2020"}
        qa = [{"question": CANARIES["question"] if canary else f"q{i}",
               "answer": CANARIES["answer"] if canary else f"a{i}", "category": (i % 4) + 1,
               "evidence": evidence if evidence is not None else [f"D1:{i % n_turns}"]}
              for i in range(n_q)]
        out.append({"sample_id": f"conv-{c}", "conversation": conv, "qa": qa})
    return out


def fake_map(n_conv=1, n_q=1):
    cohort = {f"locomo_{c}_qa{i}": f"locomo_conv_{c}" for c in range(n_conv) for i in range(n_q)}
    return {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
            "expected_cluster_ids": [f"locomo_conv_{c}" for c in range(n_conv)],
            "expected_question_to_cluster": cohort, "n_questions": len(cohort)}


print("=" * 100)
print("DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS - v3. Fake files only; no real corpus.")
print("=" * 100)

# --------------------------------------------------------------------------------------------
print("\n== D-5  the nine residual paths, and the error interface ===================================")
# --------------------------------------------------------------------------------------------
CANARY = CANARIES["question"]
seed_ok = TMP / "seeds" / "ok.json"
R3.freeze_bootstrap_seed(seed_ok, 52001107, accepted.LOCOMO, "question", 10000)

# F20: the FILE-derived one. A record whose benchmark/scheme fields carry canaries.
poisoned = TMP / "seeds" / "poisoned.json"
wj(poisoned, {"bootstrap_seed": 52001107, "benchmark": CANARY, "scheme": CANARIES["answer"],
              "replicates": 10000, "frozen_before_any_result": True, "runner_version": "x"})

m_obj = fake_map()
m_raw = mb(m_obj)
records = [{"question_id": "locomo_0_qa0", "rotation_seed": int(s), "arm": a, "fractional_R3": 0.5}
           for s in core.ROTATION_SEEDS for a in core.ARMS]

with bind_manifest(accepted.LOCOMO, m_raw):
    good_map = R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    good_map_v2 = R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    poisoned_map = dict(good_map, benchmark=CANARY)

    PATHS = {
        "F12 compute_results, mapping benchmark before the stamp check": (
            lambda M: M.compute_results(records, ["locomo_0_qa0"], ["locomo_conv_0"],
                                        {"benchmark": CANARY}, seed_ok,
                                        benchmark=accepted.LOCOMO, scheme="question", replicates=10000)),
        "F13 compute_results, unknown benchmark": (
            lambda M: M.compute_results(records, ["locomo_0_qa0"], ["locomo_conv_0"], good_map, seed_ok,
                                        benchmark=CANARY, scheme="question", replicates=10000)),
        "F14 compute_results, unknown scheme": (
            lambda M: M.compute_results(records, ["locomo_0_qa0"], ["locomo_conv_0"], good_map, seed_ok,
                                        benchmark=accepted.LOCOMO, scheme=CANARY, replicates=10000)),
        "F15 freeze_bootstrap_seed -> accepted_bootstrap_for": (
            lambda M: M.freeze_bootstrap_seed(TMP / "seeds" / f"{id(M)}.json", 1, CANARY, "question", 10)),
        "F20 read_bootstrap_seed, values read out of a JSON FILE": (
            lambda M: M.read_bootstrap_seed(poisoned, accepted.LOCOMO, "question")),
    }
    for name, fn in PATHS.items():
        old = surface(lambda f=fn: f(R2))
        new = surface(lambda f=fn: f(R3))
        check(f"D-5 NEGATIVE CONTROL: v2 leaks through {name}", bool(leaked(old)), str(leaked(old)))
        check(f"D-5 CLOSED: v3 leaks nothing through {name}", not leaked(new),
              "code + safe fields only" if not leaked(new) else new[:80])

# F17 resolve_accepted_manifest, F18/F19 verify_source_bytes
ING = {
    "F17 resolve_accepted_manifest, unknown benchmark":
        lambda: resolve_sources.resolve_accepted_manifest(REPO, CANARY),
    "F18 verify_source_bytes, unknown benchmark":
        lambda: I3.verify_source_bytes(TMP / "nope" / "locomo10.json", CANARY, enabled=True),
    "F19 verify_source_bytes, a missing PATH":
        lambda: I3.verify_source_bytes(TMP / "missing" / CANARY / "locomo10.json",
                                       accepted.LOCOMO, enabled=True),
}
for name, fn in ING.items():
    new = surface(fn)
    check(f"D-5 CLOSED: v3 leaks nothing through {name}", not leaked(new), new[:70] if leaked(new) else "")

# The v2 controls for the paths that live in `authoritative/` must run in a SUBPROCESS. In-process,
# v3's `authoritative` package shadows v2's on sys.path, so v2 would be exercised against the FIXED
# resolver and the control would silently prove nothing. That is a real hazard of testing two versions
# of one package name in a single interpreter, and it is worth naming rather than working around.
CONTROL = (
    "import sys, io, contextlib, traceback\n"
    "sys.path.insert(0, r'" + str(V2) + "'); sys.path.insert(0, r'" + str(CORE) + "')\n"
    "import membership_runner_v2 as R2, corpus_ingest_v2 as I2\n"
    "from authoritative import resolve_sources as RS\n"
    "CANARY = " + repr(CANARY) + "\n"
    "def surface(fn):\n"
    "    out, err = io.StringIO(), io.StringIO(); tail = ''\n"
    "    try:\n"
    "        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err): fn()\n"
    "    except BaseException as e:\n"
    "        tail = ''.join(traceback.format_exception(type(e), e, e.__traceback__))\n"
    "    return out.getvalue() + err.getvalue() + tail\n"
    "print('F16', CANARY in surface(lambda: R2.load_accepted_mapping(CANARY, raw=b'{}')))\n"
    "print('F17', CANARY in surface(lambda: RS.resolve_accepted_manifest(r'" + str(REPO) + "', CANARY)))\n"
    "print('F18', CANARY in surface(lambda: I2.verify_source_bytes('nope/locomo10.json', CANARY, enabled=True)))\n"
    "print('F19', CANARY in surface(lambda: I2.verify_source_bytes('m/' + CANARY + '/locomo10.json', 'LoCoMo', enabled=True)))\n"
)
ctl = subprocess.run([sys.executable, "-B", "-c", CONTROL], capture_output=True, text=True, cwd=str(V2))
seen = dict(line.split() for line in ctl.stdout.strip().splitlines() if line)
for probe in ("F16", "F17", "F18", "F19"):
    check(f"D-5 NEGATIVE CONTROL (subprocess, against v2's OWN package): v2 leaks through {probe}",
          seen.get(probe) == "True", seen.get(probe, ctl.stderr[-70:]))

check("D-5: every v3 message is a fixed code plus safe fields",
      errors.message(errors.Code.SEED_NOT_ACCEPTED, accepted_seed=52001107)
      == "E-CFG-004: the seed is not the accepted seed for this benchmark and scheme [accepted_seed=52001107]")
try:
    errors.message(errors.Code.UNKNOWN_BENCHMARK, name=CANARY)
    check("D-5: a string field is refused BEFORE a message exists", False, "no exception")
except errors.UnsafeErrorField as e:
    check("D-5: a string field is refused BEFORE a message exists", not leaked(str(e)))
check("D-5: the code set is closed and every code has a fixed sentence",
      len(list(errors.Code)) == len(errors.SENTENCES))
chain = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, raw=b"{}"))
check("D-5: a refusal carries no chained library context out with it",
      "During handling of the above exception" not in chain and "direct cause" not in chain)
runner_src = (HERE / "membership_runner_v3.py").read_text(encoding="utf-8")
ingest_src = (HERE / "corpus_ingest_v3.py").read_text(encoding="utf-8")
errors_src = (HERE / "errors.py").read_text(encoding="utf-8")
check("D-5: the absolute claim is no longer ASSERTED - it survives only as quoted, falsified v2 text",
      "the closure check falsified it with NINE paths" in runner_src
      and "Two absolute claims, two falsifications. So v3 does not make a third." in ingest_src)
# Source text wraps, so these assertions normalise whitespace first. Asserting on wrapped source is
# how two earlier claim-checks in this suite failed for the wrong reason.
flat = " ".join(errors_src.split())
check("D-5: a tested surface and a threat model are stated instead",
      "The tested surface is:" in flat and "NOT claimed: that no content can escape" in flat
      and "The threat model here is the pipeline's own error paths" in flat
      and "it is not, and cannot be, the caller's behaviour" in flat)

# --------------------------------------------------------------------------------------------
print("\n== D-1  the unauthorized exception is closed ================================================")
# --------------------------------------------------------------------------------------------
part_src = wj(TMP / "d1" / "locomo10.json", fake_locomo(evidence=["D1:0", "D9:99"]))
full_src = wj(TMP / "d1" / "none" / "locomo10.json", fake_locomo(evidence=["D9:98", "D9:99"]))
clean_src = wj(TMP / "d1" / "clean" / "locomo10.json", fake_locomo())

with gate_open(), bind_manifest(accepted.LOCOMO, m_raw):
    mp3 = R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    mp2 = R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    with bind_source(I2, accepted.LOCOMO, part_src):
        got = I2.ingest_locomo(part_src, mp2, allow_partial_evidence=True,
                               partial_evidence_citation="anything non-empty")
        check("D-1 NEGATIVE CONTROL: v2 proceeds on a free-text citation",
              got["partial_evidence_waiver"]["allowed"] is True)
        check("D-1 NEGATIVE CONTROL: and that citation reaches no written manifest",
              "partial_evidence_waiver" not in I2.summarise(got))
    with bind_source(I3, accepted.LOCOMO, part_src):
        txt = surface(lambda: I3.ingest_locomo(part_src, mp3))
        check("D-1 CLOSED: v3 stops on a partial resolution, with a fixed code",
              errors.Code.PARTIAL_EVIDENCE_RESOLUTION.value in txt, "E-COH-002")
        check("D-1: the diagnostics are safe numbers",
              "affected_questions=1" in txt and "declared_ids=2" in txt and "unresolved_ids=1" in txt)
        check("D-1: the waiver parameter no longer exists",
              "allow_partial_evidence" not in I3.ingest_locomo.__code__.co_varnames)
        check("D-1: and the policy says why, and that a new permission is not produced in code",
              "not produced in code" in I3.PARTIAL_EVIDENCE_POLICY)
    with bind_source(I3, accepted.LOCOMO, full_src):
        s = I3.summarise(I3.ingest_locomo(full_src, mp3))
        check("D-1: a FULLY unresolvable question is not a partial loss - it proceeds and is counted",
              s["questions_with_empty_gold"] == 1
              and s["evidence_accounting"]["unresolved_reference_ids"] == 2
              and s["evidence_accounting"]["resolved_reference_ids"] == 0)
    with bind_source(I3, accepted.LOCOMO, clean_src):
        s = I3.summarise(I3.ingest_locomo(clean_src, mp3))
        check("D-1: a fully resolved source proceeds with zero unresolved",
              s["evidence_accounting"]["unresolved_reference_ids"] == 0
              and s["evidence_accounting"]["declared_reference_ids"] == 1
              and s["questions_with_partial_evidence_loss"] == 0)
        check("D-1: no gold repaired, no question excluded, no cohort changed",
              s["n_questions"] == 1 and s["n_clusters"] == 1)

# --------------------------------------------------------------------------------------------
print("\n== LongMemEval  real evidence accounting ====================================================")
# --------------------------------------------------------------------------------------------
SENT = "longmemeval_single_connected_component_inherited_task3a1"
lme_map = {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LONGMEMEVAL,
           "expected_cluster_ids": [SENT], "expected_question_to_cluster": {"q0": SENT}, "n_questions": 1}
lme_raw = mb(lme_map)


def lme(has_answer=True, second=False):
    return [{"question_id": "q0", "question": "qq", "answer": "aa",
             "haystack_session_ids": ["s0", "s1"], "haystack_dates": ["d0", "d1"],
             "haystack_sessions": [[{"role": "user", "content": "hello", "has_answer": has_answer}],
                                   [{"role": "user", "content": "again",
                                     "has_answer": True if second else False}]]}]


ok_src = wj(TMP / "lme" / "ok" / "longmemeval_s_cleaned.json", lme(second=True))
bad_src = wj(TMP / "lme" / "bad" / "longmemeval_s_cleaned.json", lme(has_answer=1))

with gate_open(), bind_manifest(accepted.LONGMEMEVAL, lme_raw):
    l3 = R3.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lme_raw)
    l2 = R2.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lme_raw)
    with bind_source(I2, accepted.LONGMEMEVAL, bad_src):
        s2 = I2.summarise(I2.ingest_longmemeval(bad_src, l2))
        check("LME NEGATIVE CONTROL: v2 silently drops a has_answer of 1 and reports declared == resolved",
              s2["evidence_ids_declared"] == s2["evidence_ids_resolved"] == 0
              and s2["evidence_ids_unresolved"] == 0,
              "a gold unit vanished and the accounting called it complete")
    with bind_source(I3, accepted.LONGMEMEVAL, bad_src):
        txt = surface(lambda: I3.ingest_longmemeval(bad_src, l3))
        check("LME CLOSED: v3 REFUSES a non-boolean gold marker instead of coercing it",
              errors.Code.INVALID_GOLD_MARKER_TYPE.value in txt, "E-COH-009")
        check("LME: the refusal cites the bound adapter's own issue code",
              "INVALID_HAS_ANSWER_TYPE" in errors.SENTENCES[errors.Code.INVALID_GOLD_MARKER_TYPE])
    with bind_source(I3, accepted.LONGMEMEVAL, ok_src):
        s3 = I3.summarise(I3.ingest_longmemeval(ok_src, l3))
        ea = s3["evidence_accounting"]
        check("LME: declared is NOT derived from resolved - it is absent, because none is defined",
              ea["declared_reference_ids"] is None
              and ea["declared_reference_ids_status"] == I3.DECLARED_NOT_APPLICABLE)
        check("LME: the resolved gold units are counted under their own name",
              ea["gold_units_resolved"] == 2)
        check("LME: the model is named, and it is NOT the LoCoMo model",
              "per_turn_gold_markers" in ea["model"]
              and ea["model"] != I3.EVIDENCE_MODEL[accepted.LOCOMO])
        check("LME: what guards completeness instead is named, as tokens each backed by a real check",
              set(ea["completeness_guarded_by"]) == set(I3.COMPLETENESS_GUARDS[accepted.LONGMEMEVAL])
              and all(t in I3.COMPLETENESS_GUARD_DESCRIPTION for t in ea["completeness_guarded_by"]))
        check("LME: the model name is a short token and the prose is NOT written into the artefact",
              ea["model"] == "per_turn_gold_markers" and len(ea["model"]) < 60
              and ea["model"] in I3.EVIDENCE_MODEL_DESCRIPTION)

with gate_open(), bind_manifest(accepted.LOCOMO, m_raw), bind_source(I3, accepted.LOCOMO, clean_src):
    loc_ea = I3.summarise(I3.ingest_locomo(clean_src, R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)))["evidence_accounting"]
check("LME: the LoCoMo accounting keeps a real declared count, in its own model",
      loc_ea["declared_reference_ids"] == 1 and loc_ea["model"] == "declared_reference_ids"
      and "gold_units_resolved" not in loc_ea)
check("LME: and the two shapes are genuinely different, not the same keys with different values",
      set(loc_ea) != set(ea))

# --------------------------------------------------------------------------------------------
print("\n== regression: what v2 closed must stay closed ==============================================")
# --------------------------------------------------------------------------------------------
with bind_manifest(accepted.LOCOMO, m_raw):
    txt = surface(lambda: R3.freeze_bootstrap_seed(TMP / "r" / "a.json", 999, accepted.LOCOMO, "question", 10000))
    check("D-3 still closed: a non-accepted seed is refused", errors.Code.SEED_NOT_ACCEPTED.value in txt)
    txt = surface(lambda: R3.compute_results(records, ["locomo_0_qa0"], ["locomo_conv_0"],
                                             R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw), seed_ok,
                                             benchmark=accepted.LOCOMO, scheme="question", replicates=7))
    check("D-2 still closed: a contradicting replicate count is refused",
          errors.Code.REPLICATES_CONTRADICT_RECORD.value in txt)
    res = R3.compute_results(records, ["locomo_0_qa0"], ["locomo_conv_0"],
                             R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw), seed_ok,
                             benchmark=accepted.LOCOMO, scheme="question", replicates=10000)
    check("the accepted configuration still runs end to end", res["bootstrap_seed_record"]["replicates"] == 10000)

loc = accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]
blob = resolve_sources.git_blob(REPO, loc["commit"], loc["path"])
crlf_file = TMP / "d4" / Path(loc["path"]).name
crlf_file.parent.mkdir(parents=True, exist_ok=True)
crlf_file.write_bytes(blob.replace(b"\n", b"\r\n"))
txt = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, path=crlf_file))
check("D-4 still closed: a CRLF-translated manifest is refused", errors.Code.MANIFEST_NOT_ACCEPTED.value in txt)
check("D-4: the diagnosis survives as a SAFE FLAG rather than a sentence", "crlf_to_lf_would_match=True" in txt)
check("D-4: the accepted bytes still load",
      R3.load_accepted_mapping(accepted.LOCOMO, raw=blob)["n_questions"] == 1535)
sup = resolve_sources.git_blob(REPO, "e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf",
                               "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_longmemeval.json")
txt = surface(lambda: R3.load_accepted_mapping(accepted.LONGMEMEVAL, raw=sup))
check("source trust still closed: the superseded manifest is refused AS SUPERSEDED",
      errors.Code.MANIFEST_SUPERSEDED.value in txt, "E-SRC-002")

rng = np.random.default_rng(5204)
archive, query = rng.normal(0.3, 1.7, (48, core.DIM)), rng.normal(-1.1, .4, (9, core.DIM))
mu, D, _ = R3.fit_archive_transform(archive)
_, stamp = R3.apply_archive_transform(query, mu, D)
R3.assert_query_transform_is_inherited(mu, D, stamp)
mu_q, D_q, _ = R3.fit_archive_transform(np.vstack([query, query + 1e-9]))
_, bad = R3.apply_archive_transform(query, mu_q, D_q)
check("D-6 still closed: a query-derived transform is caught",
      "N-4 VIOLATION" in surface(lambda: R3.assert_query_transform_is_inherited(mu, D, bad)))
txt = surface(lambda: I3._longmemeval_units({"question_id": "q", "haystack_session_ids": ["a"],
                                             "haystack_dates": [], "haystack_sessions": [[]]}))
check("D-7 still closed: ragged arrays are refused", errors.Code.RAGGED_PARALLEL_ARRAYS.value in txt)
txt = surface(lambda: I3._longmemeval_units({"question_id": "q"}))
check("D-8 still closed: a missing field is a named refusal", errors.Code.ITEM_MISSING_FIELD.value in txt)
gate_txt = surface(lambda: R3.run_on_real_corpus())
check("gates still closed: the real-data gate refuses FIRST, before the stub's own refusal",
      core.REAL_DATA_EXECUTION_ENABLED is False and "not authorized" in gate_txt
      and errors.Code.NO_INGESTION_PATH.value not in gate_txt,
      "the core gate fires first; the stub code is only reachable with the gate open")
with gate_open():
    check("gates still closed: with the gate open there is still NO ingestion path behind it",
          errors.Code.NO_INGESTION_PATH.value in surface(lambda: R3.run_on_real_corpus()))
check("gates still closed: and the gate is shut again afterwards", core.REAL_DATA_EXECUTION_ENABLED is False)

# the fully canaried end-to-end path, and what actually gets written
canary_src = wj(TMP / "final" / "locomo10.json", fake_locomo(canary=True))
out = TMP / "final" / "manifest.json"
with gate_open(), bind_manifest(accepted.LOCOMO, m_raw), bind_source(I3, accepted.LOCOMO, canary_src):
    mp = R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    txt = surface(lambda: I3.write_ingest_manifest(out, I3.summarise(I3.ingest_locomo(canary_src, mp))))
    check("a fully canaried source emits no canary anywhere on the happy path", not leaked(txt))
    check("...and the written manifest carries none", not leaked(out.read_text(encoding="utf-8")))
    check("...while the in-memory structures still hold the text, which is the point of ingestion",
          CANARIES["question"] in I3.ingest_locomo(canary_src, mp)["conversations"]["locomo_conv_0"]["questions"]["locomo_0_qa0"]["text"])
    check("a second write is still refused",
          errors.Code.CONTENT_POLICY.value in surface(lambda: I3.write_ingest_manifest(out, {"x": 1}))
          or "refusing to overwrite" in surface(lambda: I3.write_ingest_manifest(out, I3.summarise(I3.ingest_locomo(canary_src, mp)))))

check("the closed core is untouched",
      hashlib.sha256((CORE / "membership_scaling_core.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
      == accepted.BOUND_CORE["blob_sha256"]
      or hashlib.sha256((CORE / "membership_scaling_core.py").read_bytes()).hexdigest()
      == accepted.BOUND_CORE["blob_sha256"])

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): {FAILURES}")
    raise SystemExit(1)
print("ALL PASS")
print("Scope: DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS for the nine D-5 paths, the D-1 partial-evidence "
      "policy and the LongMemEval evidence accounting. Fake files only. Not a seal, not run authorization.")
raise SystemExit(0)
