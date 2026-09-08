"""INDEPENDENT probe suite, part 4: regression over everything earlier checks closed.

Synthetic only. No real corpus opened, read, downloaded, hashed or scanned. Accepted MANIFEST json is
read as a RAW GIT BLOB (a cohort id list, not corpus) only to build a synthetic source of its SHAPE.

Usage:  python -B probe_v4_part4.py <checkout-of-86a8fd7a> <repo-root-with-.git>
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

ROOT = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
PKG4 = ROOT / "drafts/v52/membership_runner_ingest_v4_2026_09_08"
PKG3 = ROOT / "drafts/v52/membership_runner_ingest_v3_2026_09_08"
CORE = ROOT / "drafts/v52/membership_impl_v3_2026_09_07"
for _p in (CORE, PKG3, PKG4):
    sys.path.insert(0, str(_p))

import membership_scaling_core as core          # noqa: E402
import errors                                   # noqa: E402
import membership_runner_v4 as R4               # noqa: E402
import corpus_ingest_v4 as I4                   # noqa: E402
from authoritative import accepted_configuration as accepted   # noqa: E402
from authoritative import resolve_sources                      # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="audit_v4d_"))
CANARY = "Where did Rashid park the blue van on the night of the storm?"
TALLY = {}


def say(kind, label, detail=""):
    TALLY[kind] = TALLY.get(kind, 0) + 1
    print((f"{kind:<8} {label}" + (f"   |  {detail}" if detail else ""))[:400])


def ck(label, cond, detail="", failkind="FINDING"):
    say("PASS" if cond else failkind, label, detail)
    return cond


def surface(fn):
    out, err = io.StringIO(), io.StringIO()
    parts = []
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:                                                     # noqa: BLE001
        parts.append("".join(traceback.format_exception(type(e), e, e.__traceback__)))
        parts.append(repr(e))
        cur, seen = e, set()
        while cur is not None and id(cur) not in seen:
            seen.add(id(cur))
            parts.append(f"[chain {type(cur).__name__}] {cur!r}")
            cur = cur.__cause__ or cur.__context__
    return out.getvalue() + err.getvalue() + "\n".join(parts)


def blob(commit, path) -> bytes:
    return subprocess.run(["git", "cat-file", "blob", f"{commit}:{path}"], cwd=REPO,
                          capture_output=True, check=True).stdout


def wj(p: Path, obj) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return p


def mb(o):
    return (json.dumps(o, indent=2) + "\n").encode("utf-8")


print("=" * 110)
print("INDEPENDENT AUDIT PROBES part 4 - regression. SYNTHETIC ONLY. No real corpus opened or scanned.")
print("=" * 110)

COMMIT = "86a8fd7a73a0d4e045666e692cd7e2016f134885"
BIND = "drafts/v52/membership_runner_v1_2026_09_08/binding"
loco_raw = blob(COMMIT, f"{BIND}/PROPOSED_mapping_locomo.json")
lme_raw = blob(COMMIT, f"{BIND}/PROPOSED_mapping_longmemeval_v2_source_resolved.json")
superseded_raw = blob(COMMIT, f"{BIND}/PROPOSED_mapping_longmemeval.json")
say("INFO", "accepted manifests read as RAW GIT BLOBS (not from a checkout)",
    f"locomo {len(loco_raw)} B sha256={hashlib.sha256(loco_raw).hexdigest()[:16]}…; "
    f"lme {len(lme_raw)} B sha256={hashlib.sha256(lme_raw).hexdigest()[:16]}…")

# ==========================================================================================
print("\n== P. source trust, D-4 and the manifest resolution ========================================")
# ==========================================================================================
ck("P1  the ACCEPTED locomo manifest resolves from its raw Git bytes",
   R4.load_accepted_mapping(accepted.LOCOMO, raw=loco_raw)["n_questions"] == 1535)
ck("P2  the ACCEPTED longmemeval manifest resolves from its raw Git bytes",
   R4.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lme_raw)["n_questions"] == 470)
t = surface(lambda: R4.load_accepted_mapping(accepted.LONGMEMEVAL, raw=superseded_raw))
ck("P3  D-4/source-trust: the SUPERSEDED manifest is refused AS SUPERSEDED",
   errors.Code.MANIFEST_SUPERSEDED.value in t, t.strip().splitlines()[-1][:150])
t = surface(lambda: R4.load_accepted_mapping(accepted.LOCOMO, raw=superseded_raw))
ck("P3b and refused under the other benchmark too", errors.Code.MANIFEST_SUPERSEDED.value in t
   or errors.Code.MANIFEST_NOT_ACCEPTED.value in t, t.strip().splitlines()[-1][:150])
crlf = loco_raw.replace(b"\n", b"\r\n")
t = surface(lambda: R4.load_accepted_mapping(accepted.LOCOMO, raw=crlf))
ck("P4  D-4: a CRLF-translated copy of the accepted manifest is REFUSED, not normalised",
   errors.Code.MANIFEST_NOT_ACCEPTED.value in t and "crlf" in t.lower(),
   t.strip().splitlines()[-1][:220])
print("P4b BYTE-VERBATIM CRLF refusal:")
print("   >>> " + [l for l in t.splitlines() if "crlf_to_lf" in l][0].strip())
t = surface(lambda: R4.load_accepted_mapping(accepted.LOCOMO, raw=loco_raw[:-1]))
ck("P5  a one-byte-truncated manifest is refused", errors.Code.MANIFEST_NOT_ACCEPTED.value in t)
t = surface(lambda: R4.load_accepted_mapping(accepted.LOCOMO, raw=loco_raw, path=TMP / "x.json"))
ck("P6  giving both raw and path is refused (no override)", errors.Code.MANIFEST_ARGUMENTS.value in t)
t = surface(lambda: R4.load_accepted_mapping(CANARY, raw=loco_raw))
ck("P7  an unknown benchmark is refused BEFORE any manifest byte is looked at, no echo",
   errors.Code.UNKNOWN_BENCHMARK.value in t and CANARY not in t)
import inspect as _insp
ck("P8  there is still no caller-supplied expected-hash argument in the signature",
   "expected_sha256" not in _insp.signature(R4.load_accepted_mapping).parameters,
   str(_insp.signature(R4.load_accepted_mapping)))

# ==========================================================================================
print("\n== Q. D-2, D-3, D-6, seeds, gates, writers =================================================")
# ==========================================================================================
m4 = R4.load_accepted_mapping(accepted.LOCOMO, raw=loco_raw)
seed = TMP / "seed.json"
R4.freeze_bootstrap_seed(seed, 52001107, accepted.LOCOMO, "question", 10000)
ck("Q1  D-3: seed 999 refused", errors.Code.SEED_NOT_ACCEPTED.value in
   surface(lambda: R4.freeze_bootstrap_seed(TMP / "a.json", 999, accepted.LOCOMO, "question", 10000)))
ck("Q2  D-3: the transposed 52001170 refused", errors.Code.SEED_NOT_ACCEPTED.value in
   surface(lambda: R4.freeze_bootstrap_seed(TMP / "b.json", 52001170, accepted.LOCOMO, "question", 10000)))
forged = wj(TMP / "forged.json", {"bootstrap_seed": 999, "benchmark": accepted.LOCOMO, "scheme": "question",
                                  "replicates": 10000, "frozen_before_any_result": True,
                                  "runner_version": "x"})
ck("Q3  D-3: a hand-forged seed record is caught on READ",
   errors.Code.SEED_RECORD_DRIFT.value in surface(
       lambda: R4.read_bootstrap_seed(forged, accepted.LOCOMO, "question"))
   or errors.Code.SEED_RECORD_MALFORMED.value in surface(
       lambda: R4.read_bootstrap_seed(forged, accepted.LOCOMO, "question")))
ck("Q4  F20: nothing read out of a poisoned seed record reaches a message", CANARY not in surface(
    lambda: R4.read_bootstrap_seed(wj(TMP / "p.json", {"bootstrap_seed": 1, "benchmark": CANARY,
                                                       "scheme": CANARY, "replicates": 1, "runner_version": CANARY}),
                                   accepted.LOCOMO, "question")))
qids = list(m4["expected_question_to_cluster"])
cids = [m4["expected_question_to_cluster"][q] for q in qids]
recs = [{"question_id": q, "rotation_seed": int(s), "arm": a, "fractional_R3": 0.5}
        for q in qids for s in core.ROTATION_SEEDS for a in core.ARMS]
ck("Q5  D-2: a replicate count contradicting the frozen record is refused",
   errors.Code.REPLICATES_CONTRADICT_RECORD.value in surface(
       lambda: R4.compute_results(recs, qids, cids, m4, seed, benchmark=accepted.LOCOMO,
                                  scheme="question", replicates=7)))
ck("Q6  F12 ordering: an unstamped mapping is refused before anything in it is read",
   errors.Code.MAPPING_NOT_FROM_ACCEPTED_PATH.value in surface(
       lambda: R4.compute_results(recs, qids, cids, {"benchmark": CANARY}, seed,
                                  benchmark=accepted.LOCOMO, scheme="question", replicates=10000)))
ck("Q7  N-4 residual stays closed: an EMPTY mapping gives E-SRC-006, not KeyError",
   errors.Code.MAPPING_NOT_FROM_ACCEPTED_PATH.value in surface(
       lambda: R4.compute_results(recs, qids, cids, {}, seed, benchmark=accepted.LOCOMO,
                                  scheme="question", replicates=10000)))
res = R4.compute_results(recs, qids, cids, m4, seed, benchmark=accepted.LOCOMO,
                         scheme="question", replicates=10000)
ck("Q8  the accepted configuration still runs end to end on the ACCEPTED 1535-question cohort",
   res["n_questions"] == 1535 and res["n_clusters"] == 10
   and res["bootstrap_seed_record"]["replicates"] == 10000, f"n_q={res['n_questions']} n_c={res['n_clusters']}")
ck("Q9  D-6: the N-4 transform stamp is still checked",
   "N-4 VIOLATION" in surface(lambda: R4.assert_query_transform_is_inherited(
       __import__("numpy").zeros(core.DIM), __import__("numpy").eye(core.DIM), "not-the-stamp"))
   or "transform stamp" in surface(lambda: R4.assert_query_transform_is_inherited(
       __import__("numpy").zeros(core.DIM), __import__("numpy").eye(core.DIM), "not-the-stamp")))
ck("Q10 N-3: the conversation-cluster bootstrap is still REFUSED for LongMemEval",
   "REFUSED for LongMemEval" in surface(lambda: R4.compute_results(
       recs, qids, cids, m4, seed, benchmark=accepted.LONGMEMEVAL, scheme="conversation", replicates=10000)))
out = TMP / "res.json"
R4.write_results(out, res)
ck("Q11 the writer refuses to OVERWRITE", "exists" in surface(lambda: R4.write_results(out, res)).lower()
   or surface(lambda: R4.write_results(out, res)) != "")
ck("Q12 the real-data gate is closed by default and refuses first",
   core.REAL_DATA_EXECUTION_ENABLED is False and "not authorized" in surface(lambda: R4.run_on_real_corpus()))
ck("Q13 the closed core blob is byte-unchanged against the bound hash",
   hashlib.sha256(blob(COMMIT, "drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py")).hexdigest()
   == accepted.BOUND_CORE["blob_sha256"], accepted.BOUND_CORE["blob_sha256"][:20] + "…")

# ==========================================================================================
print("\n== R. D-1, D-7, D-8 and LongMemEval on the ACCEPTED cohort SHAPE ===========================")
# ==========================================================================================
# A synthetic LoCoMo source of the accepted manifest's SHAPE. Content is mine; no corpus is read.
bound = m4["expected_question_to_cluster"]
import re as _re
_QID = _re.compile(r"locomo_(\d+)_qa(\d+)")
byconv = {}
for q, c in bound.items():
    ci, pos = _QID.fullmatch(q).groups()
    byconv.setdefault((int(ci), c), {})[int(pos)] = q
src = []
for (ci, conv_id) in sorted(byconv):
    positions = byconv[(ci, conv_id)]
    nqa = max(positions) + 1
    conv = {"speaker_a": "A", "speaker_b": "B",
            "session_1": [{"dia_id": f"D1:{t}", "speaker": "A", "text": f"turn {t}"} for t in range(4)],
            "session_1_date_time": "1 Jan 2020"}
    qa = [{"question": CANARY, "answer": CANARY, "category": 1, "evidence": ["D1:0"]} for _ in range(nqa)]
    src.append({"sample_id": conv_id, "conversation": conv, "qa": qa})
say("INFO", "R0  synthetic source of the ACCEPTED SHAPE built from the manifest's id list only",
    f"{len(src)} conversations, {sum(len(x['qa']) for x in src)} qa entries, cohort {len(bound)}")


def build(evidence_override=None):
    s = json.loads(json.dumps(src))
    if evidence_override is not None:
        s[0]["qa"][0]["evidence"] = evidence_override
    return s


core.REAL_DATA_EXECUTION_ENABLED = True
try:
    for label, ev, expect in [
            ("R1  the accepted-shape cohort resolves clean", None, "ok"),
            ("R2  D-1: ONE partial question in 1535 STOPS the whole run", ["D1:0", "D9:9"], "E-COH-002"),
            ("R3  a fully unresolvable question does NOT stop (visible as empty_gold)", ["D9:9"], "ok"),
            ("R4  one malformed item in 1535 STOPS the run", ["D1:0", {"z": 1}], "E-COH-011")]:
        p = wj(TMP / f"shape_{abs(hash(label)) % 9999}" / "locomo10.json", build(ev))
        old = dict(I4.BOUND_SOURCES[accepted.LOCOMO])
        I4.BOUND_SOURCES[accepted.LOCOMO] = dict(old, filename=p.name,
                                                 sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                                 bytes=p.stat().st_size)
        t = surface(lambda pp=p: I4.summarise(I4.ingest_locomo(pp, m4)))
        I4.BOUND_SOURCES[accepted.LOCOMO] = old
        if expect == "ok":
            ck(label, t == "", t.strip().splitlines()[-1][:150] if t else "")
        else:
            ck(label, expect in t and CANARY not in t, t.strip().splitlines()[-1][:180])
    # measured accounting on the clean accepted-shape source
    p = wj(TMP / "shape_clean2" / "locomo10.json", build(None))
    old = dict(I4.BOUND_SOURCES[accepted.LOCOMO])
    I4.BOUND_SOURCES[accepted.LOCOMO] = dict(old, filename=p.name,
                                             sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                             bytes=p.stat().st_size)
    s = I4.summarise(I4.ingest_locomo(p, m4))
    I4.BOUND_SOURCES[accepted.LOCOMO] = old
    say("INFO", "R5  accounting on the accepted-shape source", json.dumps(s["evidence_accounting"]))
    ck("R6  raw == declared == resolved on a clean source of the accepted shape",
       s["evidence_accounting"]["raw_evidence_items"] == s["evidence_accounting"]["declared_reference_ids"]
       == s["evidence_accounting"]["resolved_reference_ids"] == 1535)
    ck("R7  no question excluded and no cohort changed", s["n_questions"] == 1535 and s["n_clusters"] == 10)

    # LongMemEval
    lme_map = R4.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lme_raw)
    lq = list(lme_map["expected_question_to_cluster"])[:3]
    lsrc = [{"question_id": q, "question": CANARY, "answer": CANARY,
             "haystack_session_ids": ["s0"], "haystack_dates": ["d0"],
             "haystack_sessions": [[{"role": "user", "content": CANARY, "has_answer": True}]]} for q in lq]
    p = wj(TMP / "lme" / "longmemeval_s_cleaned.json", lsrc)
    old = dict(I4.BOUND_SOURCES[accepted.LONGMEMEVAL])
    I4.BOUND_SOURCES[accepted.LONGMEMEVAL] = dict(old, filename=p.name,
                                                  sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                                  bytes=p.stat().st_size)
    t = surface(lambda: I4.ingest_longmemeval(p, lme_map))
    ck("R8  D-8/E-COH-005: a short LongMemEval source is refused on cohort size",
       errors.Code.COHORT_SIZE_MISMATCH.value in t or errors.Code.COHORT_RESOLUTION_FAILED.value in t,
       t.strip().splitlines()[-1][:170])
    # a 1-question toy binding to reach the accounting object
    toy = {"source_id": "f", "source_sha256": "0" * 64, "benchmark": accepted.LONGMEMEVAL,
           "expected_cluster_ids": ["longmemeval_single_connected_component_inherited_task3a1"],
           "expected_question_to_cluster": {"q0": "longmemeval_single_connected_component_inherited_task3a1"},
           "n_questions": 1}
    toy_raw = mb(toy)
    sv = dict(accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL])
    accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL] = dict(sv, blob_sha256=hashlib.sha256(toy_raw).hexdigest())
    tm = R4.load_accepted_mapping(accepted.LONGMEMEVAL, raw=toy_raw)
    for label, marker, expect in [("R9  a bool gold marker is accepted", True, "ok"),
                                  ("R10 D-7: the int 1 is REFUSED, not coerced", 1, "E-COH-009"),
                                  ("R11 the string 'true' is REFUSED", "true", "E-COH-009"),
                                  ("R12 null is REFUSED", None, "E-COH-009")]:
        rec = {"question_id": "q0", "question": CANARY, "answer": CANARY,
               "haystack_session_ids": ["s0"], "haystack_dates": ["d0"],
               "haystack_sessions": [[{"role": "user", "content": CANARY, "has_answer": marker}]]}
        p2 = wj(TMP / f"lme_{abs(hash(label)) % 9999}" / "longmemeval_s_cleaned.json", [rec])
        I4.BOUND_SOURCES[accepted.LONGMEMEVAL] = dict(old, filename=p2.name,
                                                      sha256=hashlib.sha256(p2.read_bytes()).hexdigest(),
                                                      bytes=p2.stat().st_size)
        t = surface(lambda pp=p2: I4.summarise(I4.ingest_longmemeval(pp, tm)))
        if expect == "ok":
            ck(label, t == "", t.strip().splitlines()[-1][:150] if t else "")
        else:
            ck(label, expect in t and CANARY not in t, t.strip().splitlines()[-1][:170])
    p2 = wj(TMP / "lme_ok2" / "longmemeval_s_cleaned.json",
            [{"question_id": "q0", "question": CANARY, "answer": CANARY,
              "haystack_session_ids": ["s0"], "haystack_dates": ["d0"],
              "haystack_sessions": [[{"role": "user", "content": CANARY, "has_answer": True}]]}])
    I4.BOUND_SOURCES[accepted.LONGMEMEVAL] = dict(old, filename=p2.name,
                                                  sha256=hashlib.sha256(p2.read_bytes()).hexdigest(),
                                                  bytes=p2.stat().st_size)
    ea = I4.summarise(I4.ingest_longmemeval(p2, tm))["evidence_accounting"]
    say("INFO", "R13 LongMemEval accounting object", json.dumps(ea))
    ck("R14 LongMemEval accounting is unchanged from v3: declared is null + NOT_APPLICABLE, and the "
       "two benchmarks' field SETS still differ",
       ea["declared_reference_ids"] is None and ea["declared_reference_ids_status"] == "NOT_APPLICABLE"
       and ea["gold_units_resolved"] == 1 and "raw_evidence_items" not in ea)
    accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL] = sv
    I4.BOUND_SOURCES[accepted.LONGMEMEVAL] = old
    # D-7 ragged arrays
    p3 = wj(TMP / "ragged" / "longmemeval_s_cleaned.json",
            [{"question_id": "q0", "question": "q", "answer": "a", "haystack_session_ids": ["s0", "s1"],
              "haystack_dates": ["d0"], "haystack_sessions": [[{"role": "u", "content": "c", "has_answer": True}]]}])
    I4.BOUND_SOURCES[accepted.LONGMEMEVAL] = dict(old, filename=p3.name,
                                                  sha256=hashlib.sha256(p3.read_bytes()).hexdigest(),
                                                  bytes=p3.stat().st_size)
    accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL] = dict(sv, blob_sha256=hashlib.sha256(toy_raw).hexdigest())
    t = surface(lambda: I4.ingest_longmemeval(p3, R4.load_accepted_mapping(accepted.LONGMEMEVAL, raw=toy_raw)))
    ck("R15 D-7: ragged parallel arrays still refused", errors.Code.RAGGED_PARALLEL_ARRAYS.value in t,
       t.strip().splitlines()[-1][:150])
    accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL] = sv
    I4.BOUND_SOURCES[accepted.LONGMEMEVAL] = old
finally:
    core.REAL_DATA_EXECUTION_ENABLED = False

print(f"\nTALLY-PART4 {TALLY}")
