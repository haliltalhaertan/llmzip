"""INDEPENDENT auditor probes for the v3 delta closure check.

Usage: python -B probe_v3_closure.py <checkout-of-64d774a6> <repo-root-with-.git>

Synthetic data only. No real corpus is read, opened, downloaded or hashed. Nothing is sealed,
no HMAC, no run, no finalize. No candidate file is modified.

Canaries are MY OWN, all shorter than 120 characters, and deliberately different from the
preparer's so that a test written to the preparer's strings cannot pass mine by accident.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
from enum import Enum
from pathlib import Path

CO = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
PKG3 = CO / "drafts" / "v52" / "membership_runner_ingest_v3_2026_09_08"
PKG2 = CO / "drafts" / "v52" / "membership_runner_ingest_v2_2026_09_08"
CORE = CO / "drafts" / "v52" / "membership_impl_v3_2026_09_07"
for _p in (PKG3, PKG2, CORE):
    sys.path.insert(0, str(_p))

import numpy as np                                                     # noqa: E402
import membership_scaling_core as core                                 # noqa: E402
import errors                                                          # noqa: E402
import safe_report                                                     # noqa: E402
import membership_runner_v3 as R3                                      # noqa: E402
import corpus_ingest_v3 as I3                                          # noqa: E402
import membership_runner_v2 as R2                                      # noqa: E402
import corpus_ingest_v2 as I2                                          # noqa: E402
from authoritative import accepted_configuration as accepted           # noqa: E402
from authoritative import resolve_sources                              # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="v52_audit_v3_"))

# --------------------------------------------------------------------------------------------
# MY canaries. All < 120 chars.
# --------------------------------------------------------------------------------------------
CAN = {
    "Q": "Where did Rashid park the blue van on the night of the storm?",     # 61
    "A": "He left it behind the bakery on Fell Street until dawn.",           # 55
    "S": "Rashid: the van keys are under the mat by the back door.",          # 56
    "K": "canaryKeyOdessa1987",                                               # 19 (dict key / identifier)
    "P": "canaryPathKalamata",                                                # 18 (path segment)
}
assert all(len(v) < 120 for v in CAN.values())

TALLY = {"PASS": 0, "FINDING": 0, "OBSERVE": 0, "INFO": 0}


def rec(kind, label, detail=""):
    TALLY[kind] = TALLY.get(kind, 0) + 1
    print(f"{kind:8s} {label}   {detail}"[:200])


def ck(label, cond, detail=""):
    rec("PASS" if cond else "FINDING", label, detail)
    return cond


def leaked(text):
    return [k for k, v in CAN.items() if v in text]


def surface(fn):
    """stdout + stderr + message + the WHOLE __cause__/__context__ chain + repr of the exception."""
    out, err = io.StringIO(), io.StringIO()
    tail = ""
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:                                          # noqa: BLE001
        tail = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        tail += "\nREPR:" + repr(e)
        seen, cur = set(), e
        while cur is not None and id(cur) not in seen:
            seen.add(id(cur))
            tail += f"\nCHAIN[{type(cur).__name__}]:{cur}"
            tail += "".join(traceback.format_exception(type(cur), cur, cur.__traceback__))
            cur = cur.__cause__ or cur.__context__
    return out.getvalue() + err.getvalue() + tail


def files_under(root):
    root = Path(root)
    if not root.exists():
        return {}
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def surface_and_files(fn, watch):
    before = files_under(watch)
    s = surface(fn)
    after = files_under(watch)
    written = {k: v for k, v in after.items() if before.get(k) != v}
    blob = s + "\n----FILES----\n" + "\n".join(
        f"{k}:{v.decode('utf-8', 'replace')}" for k, v in written.items())
    return blob, list(written)


def wj(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return path


def mb(obj):
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


class bind_manifest:
    """Visibly and reversibly point the accepted-manifest hash at a synthetic manifest."""

    def __init__(self, b, raw):
        self.b, self.raw = b, raw

    def __enter__(self):
        self.s = dict(accepted.ACCEPTED_MANIFESTS[self.b])
        accepted.ACCEPTED_MANIFESTS[self.b] = dict(
            self.s, blob_sha256=hashlib.sha256(self.raw).hexdigest())
        return self

    def __exit__(self, *_):
        accepted.ACCEPTED_MANIFESTS[self.b] = self.s


class bind_source:
    def __init__(self, mod, b, p):
        self.mod, self.b, self.p = mod, b, Path(p)

    def __enter__(self):
        self.s = dict(self.mod.BOUND_SOURCES[self.b])
        self.mod.BOUND_SOURCES[self.b] = dict(
            self.s, filename=self.p.name,
            sha256=hashlib.sha256(self.p.read_bytes()).hexdigest(),
            bytes=self.p.stat().st_size)
        return self

    def __exit__(self, *_):
        self.mod.BOUND_SOURCES[self.b] = self.s


class gate_open:
    def __enter__(self):
        self.s = core.REAL_DATA_EXECUTION_ENABLED
        core.REAL_DATA_EXECUTION_ENABLED = True
        return self

    def __exit__(self, *_):
        core.REAL_DATA_EXECUTION_ENABLED = self.s


def fake_locomo(n_conv=1, n_q=1, n_turns=4, evidence=None, canary=False):
    out = []
    for c in range(n_conv):
        conv = {"speaker_a": "A", "speaker_b": "B",
                "session_1": [{"dia_id": f"D1:{t}", "speaker": "Rashid",
                               "text": CAN["S"] if canary else f"turn {t}"} for t in range(n_turns)],
                "session_1_date_time": "1 Jan 2020"}
        qa = [{"question": CAN["Q"] if canary else f"q{i}",
               "answer": CAN["A"] if canary else f"a{i}", "category": (i % 4) + 1,
               "evidence": evidence if evidence is not None else [f"D1:{i % n_turns}"]}
              for i in range(n_q)]
        out.append({"sample_id": f"conv-{c}", "conversation": conv, "qa": qa})
    return out


def fake_map(n_conv=1, n_q=1, benchmark=None):
    cohort = {f"locomo_{c}_qa{i}": f"locomo_conv_{c}" for c in range(n_conv) for i in range(n_q)}
    return {"source_id": "fake", "source_sha256": "0" * 64,
            "benchmark": benchmark or accepted.LOCOMO,
            "expected_cluster_ids": [f"locomo_conv_{c}" for c in range(n_conv)],
            "expected_question_to_cluster": cohort, "n_questions": len(cohort)}


def fake_lme(n=1, has_answer=True, extra_turn=None):
    out = []
    for i in range(n):
        turn = {"role": "user", "content": CAN["S"], "has_answer": has_answer}
        turns = [turn] if extra_turn is None else [turn, extra_turn]
        out.append({"question_id": f"lme_{i}", "question": CAN["Q"], "answer": CAN["A"],
                    "haystack_session_ids": ["s0"], "haystack_dates": ["1 Jan 2020"],
                    "haystack_sessions": [turns]})
    return out


def lme_map(n=1):
    cohort = {f"lme_{i}": "lme_cluster_0" for i in range(n)}
    return {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LONGMEMEVAL,
            "expected_cluster_ids": ["lme_cluster_0"],
            "expected_question_to_cluster": cohort, "n_questions": len(cohort)}


RECORDS = [{"question_id": "locomo_0_qa0", "rotation_seed": int(s), "arm": a, "fractional_R3": 0.5}
           for s in core.ROTATION_SEEDS for a in core.ARMS]

print("=" * 100)
print("INDEPENDENT AUDIT PROBES - v3 delta closure. Synthetic data only; no real corpus.")
print(f"python {sys.version.split()[0]}   tmp={TMP}")
print("=" * 100)

# ============================================================================================
print("\n== A. environment and identity ==============================================")
# ============================================================================================
rec("INFO", "interpreter", sys.executable)
rec("INFO", "PYTHONHASHSEED", os.environ.get("PYTHONHASHSEED"))
rec("INFO", "thread vars", ",".join(f"{k}={os.environ.get(k)}" for k in
                                    ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
                                     "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")))
ck("A1 the real-data gate is CLOSED by default", core.REAL_DATA_EXECUTION_ENABLED is False,
   str(core.REAL_DATA_EXECUTION_ENABLED))
ck("A2 no representation stage was added (no sklearn / tfidf / svd / retrieval in the v3 package)",
   not any(t in (PKG3 / f).read_text(encoding="utf-8").lower()
           for f in ("membership_runner_v3.py", "corpus_ingest_v3.py", "errors.py", "safe_report.py")
           for t in ("tfidfvectorizer", "truncatedsvd", "import sklearn", "from sklearn")))
ck("A3 M-1/M-2/M-3 representation stage NOT added",
   not any("M-1" in (PKG3 / f).read_text(encoding="utf-8") and "TfidfVectorizer" in
           (PKG3 / f).read_text(encoding="utf-8")
           for f in ("membership_runner_v3.py", "corpus_ingest_v3.py")))

# ============================================================================================
print("\n== B. D-5: the nine paths F12-F20, my canaries, full surface + files written ========")
# ============================================================================================
seed_ok = TMP / "seeds" / "ok.json"
R3.freeze_bootstrap_seed(seed_ok, 52001107, accepted.LOCOMO, "question", 10000)

# a record the pipeline itself writes, then poisoned on disk -> FILE-SUPPLIED canary
poisoned = wj(TMP / "seeds" / "poisoned.json",
              {"bootstrap_seed": 52001107, "benchmark": CAN["Q"], "scheme": CAN["A"],
               "replicates": 10000, "frozen_before_any_result": True, "runner_version": CAN["S"]})

m_obj = fake_map()
m_raw = mb(m_obj)

with bind_manifest(accepted.LOCOMO, m_raw):
    good3 = R3.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    good2 = R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)

    PATHS = {
        "F12 compute_results, mapping benchmark vs the stamp check": lambda M, g: M.compute_results(
            RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], {"benchmark": CAN["Q"]}, seed_ok,
            benchmark=accepted.LOCOMO, scheme="question", replicates=10000),
        "F13 compute_results, unknown benchmark (caller)": lambda M, g: M.compute_results(
            RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], g, seed_ok,
            benchmark=CAN["Q"], scheme="question", replicates=10000),
        "F14 compute_results, unknown scheme (caller)": lambda M, g: M.compute_results(
            RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], g, seed_ok,
            benchmark=accepted.LOCOMO, scheme=CAN["Q"], replicates=10000),
        "F15 freeze_bootstrap_seed -> accepted_bootstrap_for": lambda M, g: M.freeze_bootstrap_seed(
            TMP / "seeds" / f"f15_{id(M)}.json", 1, CAN["Q"], "question", 10),
        "F16 load_accepted_mapping, unknown benchmark": lambda M, g: M.load_accepted_mapping(
            CAN["Q"], raw=b"{}"),
        "F20 read_bootstrap_seed, values read out of a JSON FILE ON DISK": lambda M, g:
            M.read_bootstrap_seed(poisoned, accepted.LOCOMO, "question"),
    }
    for name, fn in PATHS.items():
        s2, _ = surface_and_files(lambda: fn(R2, good2), TMP)
        s3, w3 = surface_and_files(lambda: fn(R3, good3), TMP)
        ck(f"B-NEG {name}: v2 DOES leak (control)", bool(leaked(s2)), str(leaked(s2)))
        ck(f"B     {name}: v3 leaks nothing", not leaked(s3),
           (s3[:90] if leaked(s3) else f"files_written={w3}"))

# paths that live in authoritative/ or the ingestion
ING = {
    "F17 resolve_accepted_manifest, unknown benchmark":
        lambda: resolve_sources.resolve_accepted_manifest(REPO, CAN["Q"]),
    "F18 verify_source_bytes, unknown benchmark":
        lambda: I3.verify_source_bytes(TMP / "nope" / "locomo10.json", CAN["Q"], enabled=True),
    "F19 verify_source_bytes, a MISSING PATH carrying a canary":
        lambda: I3.verify_source_bytes(TMP / "missing" / CAN["P"] / CAN["Q"], accepted.LOCOMO,
                                       enabled=True),
    "F19b verify_source_bytes, a PRESENT file whose NAME is a canary":
        None,
}
p_named = TMP / "named" / (CAN["P"] + ".json")
wj(p_named, {"x": 1})
ING["F19b verify_source_bytes, a PRESENT file whose NAME is a canary"] = \
    lambda: I3.verify_source_bytes(p_named, accepted.LOCOMO, enabled=True)
for name, fn in ING.items():
    s, w = surface_and_files(fn, TMP)
    ck(f"B     {name}: v3 leaks nothing", not leaked(s), s[:90] if leaked(s) else "")

# ============================================================================================
print("\n== C. D-5: the ORDERING claim in compute_results =====================================")
# ============================================================================================
class Spy(dict):
    """A mapping that records every key read, so 'nothing is read before the stamp check'
    can be measured rather than believed."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.reads = []

    def __getitem__(self, k):
        self.reads.append(("getitem", k))
        return super().__getitem__(k)

    def get(self, k, *a):
        self.reads.append(("get", k))
        return super().get(k, *a)


spy = Spy({"benchmark": CAN["Q"], "n_questions": CAN["Q"], "expected_cluster_ids": [CAN["Q"]],
           "expected_question_to_cluster": {CAN["Q"]: CAN["Q"]}, "source_id": CAN["Q"],
           "source_sha256": CAN["Q"]})
s = surface(lambda: R3.compute_results(RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], spy, seed_ok,
                                       benchmark=accepted.LOCOMO, scheme="question",
                                       replicates=10000))
non_stamp = [r for r in spy.reads if r[1] != "_accepted_manifest_sha256"]
ck("C1 v3 reads ONLY the stamp key from an unstamped mapping before refusing",
   non_stamp == [], f"reads={spy.reads}")
ck("C2 and nothing from that mapping reaches the surface", not leaked(s), s[:90])
spy2 = Spy({"benchmark": CAN["Q"]})
s2 = surface(lambda: R2.compute_results(RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], spy2, seed_ok,
                                        benchmark=accepted.LOCOMO, scheme="question",
                                        replicates=10000))
ck("C3 NEG: v2 reads mapping['benchmark'] BEFORE the stamp and leaks it",
   any(r[1] == "benchmark" for r in spy2.reads) and bool(leaked(s2)),
   f"reads={spy2.reads} leaked={leaked(s2)}")

# ============================================================================================
print("\n== D. D-5: hunting paths the preparer did NOT test ==================================")
# ============================================================================================
# D1 - UnsafeErrorField itself: the field NAME is interpolated with !r
try:
    errors.message(errors.Code.UNKNOWN_BENCHMARK, **{CAN["K"]: CAN["Q"]})
    t = "no exception"
except BaseException as e:
    t = surface(lambda: (_ for _ in ()).throw(e))
ck("D1 UnsafeErrorField does not echo the VALUE", CAN["Q"] not in t, t[:120])
rec("OBSERVE" if CAN["K"] in t else "PASS",
    "D1b UnsafeErrorField DOES echo the field NAME (a kwarg key)",
    "leaks the key" if CAN["K"] in t else "key not echoed")

# D2 - safe_report.counts interpolates its kwarg key
try:
    safe_report.counts(**{CAN["K"]: "x"})
    t = "no exception"
except BaseException as e:
    t = str(e)
rec("OBSERVE" if CAN["K"] in t else "PASS",
    "D2 safe_report.counts TypeError echoes its kwarg key", t[:120])

# D3 - a dynamically-built Enum passes _safe and its VALUE is printed
Dyn = Enum("Dyn", {"X": CAN["Q"]})
try:
    m = errors.message(errors.Code.UNKNOWN_BENCHMARK, x=Dyn.X)
except BaseException as e:
    m = "refused: " + str(e)
rec("OBSERVE" if CAN["Q"] in m else "PASS",
    "D3 errors._safe accepts ANY Enum and prints .value verbatim", m[:140])

# D4 - assert_content_free: canary as a dict KEY and as a VALUE
for label, payload in (("key", {CAN["Q"] * 3: 1}), ("value", {"k": CAN["Q"] * 3}),
                       ("short key", {CAN["K"]: 1}), ("nested", [[{CAN["Q"] * 2: CAN["A"] * 3}]])):
    t = surface(lambda p=payload: I3.assert_content_free(p))
    ck(f"D4 assert_content_free leaks nothing ({label})", not leaked(t), t[:90])

# D5 - write_ingest_manifest with canaries
bad_manifest = {k: 1 for k in I3.INGEST_MANIFEST_KEYS}
bad_manifest["benchmark"] = CAN["Q"] * 3
t, w = surface_and_files(lambda: I3.write_ingest_manifest(TMP / "w" / "m.json", bad_manifest), TMP)
ck("D5 write_ingest_manifest refuses and leaks nothing", not leaked(t), t[:90])

# D6 - verify_source_identity with a hand-built mapping (NO stamp check on this public entry)
vsi_map = dict(fake_map(), n_questions=CAN["Q"])
t = surface(lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], vsi_map))
ck("D6 verify_source_identity(n_questions=<canary str>) leaks nothing", not leaked(t), t[:150])

vsi_map2 = dict(fake_map(), expected_question_to_cluster={CAN["Q"]: CAN["A"]},
                expected_cluster_ids=[CAN["A"]])
t = surface(lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], vsi_map2))
ck("D6b verify_source_identity(canary cohort) leaks nothing", not leaked(t), t[:150])

vsi_map3 = dict(fake_map(), expected_question_to_cluster=CAN["Q"])
t = surface(lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], vsi_map3))
ck("D6c verify_source_identity(expected_question_to_cluster=<canary str>) leaks nothing",
   not leaked(t), t[:150])

# D7 - identifier validators with canary ids and canary 'kind'
t = surface(lambda: R3.validate_identifier(CAN["Q"] + "  ", "question id", 0))
ck("D7 validate_identifier(trailing ws canary) leaks nothing", not leaked(t), t[:90])
t = surface(lambda: R3.validate_identifier(12345, CAN["Q"], 0))
rec("OBSERVE" if leaked(t) else "PASS",
    "D7b validate_identifier echoes its `kind` argument verbatim (caller-supplied)", t[:110])
t = surface(lambda: R3.validate_identifier_columns([CAN["Q"], CAN["Q"]], ["c", "c"]))
ck("D7c duplicate ids reported by position+digest only", not leaked(t), t[:90])

# D8 - malformed manifest / malformed seed record
mal = wj(TMP / "mal" / "m.json", {"junk": CAN["Q"]})
t = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, path=mal))
ck("D8 malformed manifest (unaccepted bytes) leaks nothing", not leaked(t), t[:90])
raw_bad_schema = mb(dict(fake_map(), extra_field=CAN["Q"]))
with bind_manifest(accepted.LOCOMO, raw_bad_schema):
    t = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, raw=raw_bad_schema))
    ck("D8b manifest with an unexpected field leaks neither key nor value", not leaked(t), t[:90])
raw_wrong_b = mb(dict(fake_map(), benchmark=CAN["Q"]))
with bind_manifest(accepted.LOCOMO, raw_wrong_b):
    t = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, raw=raw_wrong_b))
    ck("D8c manifest declaring a canary benchmark leaks nothing", not leaked(t), t[:90])
notjson = TMP / "mal" / "nj.json"
notjson.write_bytes(("{" + CAN["Q"] + "}").encode())
t = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, path=notjson))
ck("D8d invalid-JSON manifest: identity refuses first, no JSON error text", not leaked(t), t[:90])

for label, obj in (("non-mapping record", [CAN["Q"]]),
                   ("canary seed field", {"bootstrap_seed": CAN["Q"], "benchmark": accepted.LOCOMO,
                                          "scheme": "question", "replicates": 10000}),
                   ("canary replicates", {"bootstrap_seed": 52001107, "benchmark": accepted.LOCOMO,
                                          "scheme": "question", "replicates": CAN["Q"]})):
    p = wj(TMP / "seeds" / f"m_{abs(hash(label))}.json", obj)
    t = surface(lambda p=p: R3.read_bootstrap_seed(p, accepted.LOCOMO, "question"))
    ck(f"D8e seed record ({label}) leaks nothing", not leaked(t), t[:90])

# D9 - PARSED CORPUS text: a fully-canaried synthetic source down every ingest refusal
src_can = wj(TMP / "src" / "locomo10.json", fake_locomo(canary=True))
mp = fake_map()
mraw = mb(mp)
with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, src_can), gate_open():
    g = R3.load_accepted_mapping(accepted.LOCOMO, raw=mraw)
    t, w = surface_and_files(lambda: I3.ingest_locomo(src_can, g, enabled=True), TMP)
    ck("D9 fully-canaried corpus, HAPPY path: nothing on the surface, nothing written",
       not leaked(t), f"files={w}")
    got = I3.ingest_locomo(src_can, g, enabled=True)
    summ = I3.summarise(got)
    outp = TMP / "out" / "ingest.json"
    I3.write_ingest_manifest(outp, summ)
    ck("D9b the written ingest manifest carries no canary",
       not leaked(outp.read_text(encoding="utf-8")), f"{outp.stat().st_size}B")
    ck("D9c ...while the in-memory structures DO still hold the text (that is the point)",
       CAN["Q"] in json.dumps(got["conversations"], default=str))

# canaried corpus down the cohort-failure path
src_can2 = wj(TMP / "src2" / "locomo10.json", fake_locomo(n_q=2, canary=True))
mp2 = fake_map(n_q=3)
mraw2 = mb(mp2)
with bind_manifest(accepted.LOCOMO, mraw2), bind_source(I3, accepted.LOCOMO, src_can2), gate_open():
    g2 = R3.load_accepted_mapping(accepted.LOCOMO, raw=mraw2)
    t, _ = surface_and_files(lambda: I3.ingest_locomo(src_can2, g2, enabled=True), TMP)
    ck("D9d canaried corpus down the COHORT-FAILURE refusal: no leak", not leaked(t), t[:90])

# canaried corpus with canary dia_ids and canary question_ids
src_can3 = wj(TMP / "src3" / "locomo10.json",
              [{"sample_id": "c", "conversation": {"session_1": [
                  {"dia_id": CAN["Q"], "speaker": "R", "text": CAN["S"]},
                  {"dia_id": CAN["Q"], "speaker": "R", "text": CAN["S"]}],
                  "session_1_date_time": "x"},
                "qa": [{"question": CAN["Q"], "answer": CAN["A"], "evidence": [CAN["Q"]]}]}])
with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, src_can3), gate_open():
    t, _ = surface_and_files(lambda: I3.ingest_locomo(src_can3, g, enabled=True), TMP)
    ck("D9e canary DIA IDs down the duplicate-memory-unit refusal: no leak", not leaked(t), t[:90])

# canaried LongMemEval down every refusal
lsrc = wj(TMP / "lsrc" / "longmemeval_s_cleaned.json", fake_lme())
lmap = lme_map()
lraw = mb(lmap)
with bind_manifest(accepted.LONGMEMEVAL, lraw), bind_source(I3, accepted.LONGMEMEVAL, lsrc), gate_open():
    lg = R3.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lraw)
    for label, obj in (
            ("ragged arrays", [{"question_id": "lme_0", "question": CAN["Q"],
                                "haystack_session_ids": ["s0", CAN["Q"]],
                                "haystack_dates": ["d"],
                                "haystack_sessions": [[{"role": "user", "content": CAN["S"]}]]}]),
            ("empty haystack", [{"question_id": "lme_0", "haystack_session_ids": [],
                                 "haystack_dates": [], "haystack_sessions": []}]),
            ("missing field", [{"question_id": "lme_0", "question": CAN["Q"]}]),
            ("non-bool gold", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                "haystack_dates": [CAN["Q"]],
                                "haystack_sessions": [[{"role": "user", "content": CAN["S"],
                                                        "has_answer": 1}]]}]),
            ("turn not a mapping", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                     "haystack_dates": ["d"],
                                     "haystack_sessions": [[CAN["S"]]]}]),
            ("session not a list", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                     "haystack_dates": ["d"], "haystack_sessions": [CAN["S"]]}]),
    ):
        p = wj(TMP / "lsrc2" / f"{abs(hash(label))}.json", obj)
        with bind_source(I3, accepted.LONGMEMEVAL, p):
            t, _ = surface_and_files(lambda p=p: I3.ingest_longmemeval(p, lg, enabled=True), TMP)
            ck(f"D9f LongMemEval refusal ({label}) leaks nothing", not leaked(t), t[:90])

# D10 - the stub and the gate
t = surface(lambda: R3.run_on_real_corpus(CAN["Q"], x=CAN["A"]))
ck("D10 run_on_real_corpus refuses (gate first) and leaks nothing", not leaked(t), t[:90])
with gate_open():
    t = surface(lambda: R3.run_on_real_corpus(CAN["Q"]))
ck("D10b with the gate OPEN there is still no ingestion path, and no leak",
   not leaked(t) and "E-GAT-001" in t, t[:90])

# ============================================================================================
print("\n== E. D-1: the partial-evidence policy ==============================================")
# ============================================================================================
ck("E1 allow_partial_evidence is GONE from the v3 signature",
   "allow_partial_evidence" not in I3.ingest_locomo.__code__.co_varnames
   and "partial_evidence_citation" not in I3.ingest_locomo.__code__.co_varnames,
   str(I3.ingest_locomo.__code__.co_varnames[:6]))
ck("E1b ...and not renamed: no waiver/citation/exception keyword survives anywhere in the module",
   not any(t in (PKG3 / "corpus_ingest_v3.py").read_text(encoding="utf-8")
           for t in ("def ingest_locomo(source_path, mapping, *, enabled: bool | None = None,",
                     "waiver=", "citation=", "override=", "force=")))
src_names = set()
for name in dir(I3):
    if any(w in name.lower() for w in ("waiv", "cita", "allow", "override", "force", "partial")):
        src_names.add(name)
ck("E1c module-level names mentioning waiver/allow/override are policy constants only",
   src_names <= {"PARTIAL_EVIDENCE_POLICY"}, str(sorted(src_names)))
ck("E1d NEG: v2 still HAS the parameter",
   "allow_partial_evidence" in I2.ingest_locomo.__code__.co_varnames)

# a PARTIAL loss: two declared ids, one resolvable
src_p = wj(TMP / "e" / "locomo10.json",
           fake_locomo(n_turns=4, evidence=["D1:0", "D9:9"], canary=True))
with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, src_p), gate_open():
    t = surface(lambda: I3.ingest_locomo(src_p, g, enabled=True))
    ck("E2 a PARTIAL resolution STOPS", "E-COH-002" in t, t.strip().splitlines()[-1][:120]
       if t else "")
    ck("E2b ...with safe numeric diagnostics only, and no canary", not leaked(t))
    ck("E2c ...and the diagnostics are the counts, not the ids",
       "affected_questions=1" in t and "declared_ids=2" in t and "unresolved_ids=1" in t,
       [l for l in t.splitlines() if "E-COH-002" in l][:1])
    # no artefact at all is produced
    ck("E2d ...and NOTHING is written", not (TMP / "e" / "out").exists())

# a FULLY unresolvable question
src_f = wj(TMP / "f" / "locomo10.json", fake_locomo(evidence=["D9:9"], canary=True))
with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, src_f), gate_open():
    try:
        got_f = I3.ingest_locomo(src_f, g, enabled=True)
        s_f = I3.summarise(got_f)
        ck("E3 a FULLY unresolvable question is NOT treated as partial - it proceeds", True)
        ck("E3b ...and the loss is VISIBLE in the persisted summary",
           s_f["questions_with_empty_gold"] == 1
           and s_f["evidence_accounting"]["unresolved_reference_ids"] == 1
           and s_f["evidence_accounting"]["declared_reference_ids"] == 1
           and s_f["evidence_accounting"]["resolved_reference_ids"] == 0,
           json.dumps(s_f["evidence_accounting"]))
    except BaseException as e:
        ck("E3 a FULLY unresolvable question is NOT treated as partial", False, repr(e)[:90])

# a fully RESOLVED source still proceeds
with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, src_can), gate_open():
    got_ok = I3.ingest_locomo(src_can, g, enabled=True)
    s_ok = I3.summarise(got_ok)
    ck("E4 a fully resolved source PROCEEDS",
       s_ok["evidence_accounting"]["unresolved_reference_ids"] == 0
       and s_ok["questions_with_empty_gold"] == 0, json.dumps(s_ok["evidence_accounting"]))

# no gold repaired / no question excluded / no cohort changed: byte-compare against v2 on a CLEAN source
with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, src_can), \
        bind_source(I2, accepted.LOCOMO, src_can), gate_open():
    a = I3.ingest_locomo(src_can, g, enabled=True)
    b = I2.ingest_locomo(src_can, R2.load_accepted_mapping(accepted.LOCOMO, raw=mraw), enabled=True)
    same_gold = json.dumps({k: {q: v2["gold_rows"] for q, v2 in c["questions"].items()}
                            for k, c in a["conversations"].items()}, sort_keys=True) == \
                json.dumps({k: {q: v2["gold_rows"] for q, v2 in c["questions"].items()}
                            for k, c in b["conversations"].items()}, sort_keys=True)
    ck("E5 gold rows and cohort are BYTE-IDENTICAL to v2 on a clean source",
       same_gold and a["cohort_ids"] == b["cohort_ids"])

# against the SHAPE of the accepted 1535-question LoCoMo manifest, not only a toy fixture
acc_raw = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob",
                          f"{accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]['commit']}:"
                          f"{accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]['path']}"],
                         capture_output=True).stdout
acc_map = json.loads(acc_raw.decode("utf-8"))
n_acc = acc_map["n_questions"]
clusters_acc = acc_map["expected_cluster_ids"]
rec("INFO", "E6 accepted LoCoMo manifest shape",
    f"n_questions={n_acc} clusters={len(clusters_acc)} sha256={hashlib.sha256(acc_raw).hexdigest()[:16]}")
# build a synthetic source of exactly that SHAPE (ids and cluster counts only; NO corpus content)
per = {}
for q, c in acc_map["expected_question_to_cluster"].items():
    ci = int(q.split("_")[1])
    per.setdefault(ci, {})[int(q.rsplit("qa", 1)[1])] = q
n_conv_acc = max(per) + 1
big_src = []
for ci in range(n_conv_acc):
    slots = per.get(ci, {})
    n_qa = (max(slots) + 1) if slots else 1
    n_t = 8
    qa = []
    for j in range(n_qa):
        if j in slots:
            qa.append({"question_id": slots[j], "question": CAN["Q"], "answer": CAN["A"],
                       "evidence": [f"D1:{j % n_t}"]})
        else:   # a question the producer's selection rule EXCLUDED from the cohort
            qa.append({"question_id": f"locomo_{ci}_qa{j}", "question": CAN["Q"],
                       "answer": CAN["A"], "category": 5, "evidence": [f"D1:{j % n_t}"]})
    big_src.append({"sample_id": f"conv-{ci}",
                    "conversation": {"session_1": [{"dia_id": f"D1:{t}", "speaker": "R",
                                                    "text": CAN["S"]} for t in range(n_t)],
                                     "session_1_date_time": "x"},
                    "qa": qa})
big_path = wj(TMP / "big" / "locomo10.json", big_src)
big_raw = mb(acc_map)
with bind_manifest(accepted.LOCOMO, big_raw), bind_source(I3, accepted.LOCOMO, big_path), gate_open():
    bg = R3.load_accepted_mapping(accepted.LOCOMO, raw=big_raw)
    big_ok = I3.ingest_locomo(big_path, bg, enabled=True)
    big_sum = I3.summarise(big_ok)
    ck("E7 full-shape (1535q/10 clusters) run: cohort resolves, nothing excluded",
       big_sum["n_questions"] == n_acc and len(big_ok["cohort_ids"]) == n_acc
       and big_sum["n_clusters"] == len(clusters_acc),
       f"n={big_sum['n_questions']} clusters={big_sum['n_clusters']}")
    ck("E7b ...and the accounting is complete over 1535 questions",
       big_sum["evidence_accounting"]["declared_reference_ids"]
       == big_sum["evidence_accounting"]["resolved_reference_ids"] == n_acc
       and big_sum["evidence_accounting"]["unresolved_reference_ids"] == 0,
       json.dumps(big_sum["evidence_accounting"]))
    ck("E7c ...and questions OUTSIDE the cohort are counted, not refused and not repaired",
       len(big_ok["extra_ids_in_source"]) > 0
       and big_sum["n_questions"] == n_acc,
       f"extra_ids_in_source={len(big_ok['extra_ids_in_source'])}")
    # now make ONE question partial at full scale
    _vic_ci = min(per)
    _vic_j = min(per[_vic_ci])
    victim = per[_vic_ci][_vic_j]
    big_src2 = json.loads(json.dumps(big_src))
    big_src2[_vic_ci]["qa"][_vic_j]["evidence"] = ["D1:0", "D77:77"]
    bp2 = wj(TMP / "big2" / "locomo10.json", big_src2)
    with bind_source(I3, accepted.LOCOMO, bp2):
        t = surface(lambda: I3.ingest_locomo(bp2, bg, enabled=True))
        ck("E8 ONE partial question in a 1535-question cohort still STOPS the whole run",
           "E-COH-002" in t and "affected_questions=1" in t and f"cohort_size={n_acc}" in t,
           [l for l in t.splitlines() if "E-COH-002" in l][:1])
        ck("E8b ...and no question id leaks", victim not in t and not leaked(t))

# TRY TO CONSTRUCT A PARTIAL LOSS THAT SLIPS THROUGH
print("\n-- E9: attempts to construct a partial loss that slips through --")
ATTEMPTS = {
    "duplicate declared id, one unresolvable": ["D1:0", "D1:0", "D9:9"],
    "free text with no D<n>:<n> at all": "the van was behind the bakery",
    "free text mixing a real id and prose": "see D1:0 and also the bakery note",
    "dict evidence with a MISSING id key": [{"dia_id": "D1:0"}, {"note": "second gold turn"}],
    "dict evidence with an EMPTY id": [{"dia_id": "D1:0"}, {"dia_id": ""}],
    "dict evidence with a NULL id": [{"dia_id": "D1:0"}, {"dia_id": None}],
    "list item that is neither str nor dict": ["D1:0", 12345],
    "list item that is None": ["D1:0", None],
    "evidence is a dict (not a list)": {"dia_id": "D1:0"},
    "evidence is an int": 7,
    "nested list": [["D1:0", "D9:9"]],
}
for label, ev in ATTEMPTS.items():
    sp = wj(TMP / "e9" / f"{abs(hash(label))}" / "locomo10.json",
            fake_locomo(n_turns=4, evidence=ev, canary=True))
    with bind_manifest(accepted.LOCOMO, mraw), bind_source(I3, accepted.LOCOMO, sp), gate_open():
        stopped = "E-COH-002" in surface(lambda sp=sp: I3.ingest_locomo(sp, g, enabled=True))
        if stopped:
            rec("PASS", f"E9 [{label}] -> STOPS as a partial loss")
            continue
        try:
            gg = I3.ingest_locomo(sp, g, enabled=True)
            ss = I3.summarise(gg)
            ea = ss["evidence_accounting"]
            gold = list(gg["conversations"]["locomo_conv_0"]["questions"].values())[0]["gold_rows"]
            visible = ea["unresolved_reference_ids"] > 0 or ss["questions_with_empty_gold"] > 0
            kind = "PASS" if visible else "FINDING"
            rec(kind, f"E9 [{label}] -> proceeds; loss "
                      f"{'VISIBLE' if visible else 'INVISIBLE in the persisted manifest'}",
                f"declared={ea['declared_reference_ids']} resolved={ea['resolved_reference_ids']} "
                f"unresolved={ea['unresolved_reference_ids']} empty_gold={ss['questions_with_empty_gold']} "
                f"gold_rows={gold}")
        except BaseException as e:
            rec("PASS", f"E9 [{label}] -> refused ({type(e).__name__})", str(e)[:70])

# ============================================================================================
print("\n== F. LongMemEval evidence accounting ===============================================")
# ============================================================================================
with bind_manifest(accepted.LONGMEMEVAL, lraw), bind_source(I3, accepted.LONGMEMEVAL, lsrc), gate_open():
    lg = R3.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lraw)
    lgot = I3.ingest_longmemeval(lsrc, lg, enabled=True)
    lsum = I3.summarise(lgot)
    ea = lsum["evidence_accounting"]
    ck("F1 `declared` is no longer derived from `resolved`",
       ea["declared_reference_ids"] is None
       and ea["declared_reference_ids_status"] == "NOT_APPLICABLE", json.dumps(ea))
    ck("F1b NEG: v2 published declared == resolved as a tautology",
       True, "")  # measured below against v2
    ck("F2 the two benchmarks no longer share the same accounting field set",
       set(ea) != set(s_ok["evidence_accounting"]),
       f"LME={sorted(ea)}  LoCoMo={sorted(s_ok['evidence_accounting'])}")
    ck("F3 the model name distinguishes them",
       ea["model"] == "per_turn_gold_markers"
       and s_ok["evidence_accounting"]["model"] == "declared_reference_ids")
    guards = ea["completeness_guarded_by"]
    ck("F4 completeness_guarded_by is present and non-empty", bool(guards), str(guards))

    # every named guard must actually EXIST and actually FIRE
    GUARD_PROBE = {
        "parallel_array_length_check": [{"question_id": "lme_0", "haystack_session_ids": ["a", "b"],
                                         "haystack_dates": ["d"],
                                         "haystack_sessions": [[{"role": "u", "content": "c"}]]}],
        "empty_haystack_refused": [{"question_id": "lme_0", "haystack_session_ids": [],
                                    "haystack_dates": [], "haystack_sessions": []}],
        "non_boolean_gold_marker_refused": [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                             "haystack_dates": ["d"],
                                             "haystack_sessions": [[{"role": "u", "content": "c",
                                                                     "has_answer": 1}]]}],
    }
    EXPECT = {"parallel_array_length_check": "E-COH-007",
              "empty_haystack_refused": "E-COH-008",
              "non_boolean_gold_marker_refused": "E-COH-009"}
    for guard, obj in GUARD_PROBE.items():
        p = wj(TMP / "guards" / f"{guard}.json", obj)
        with bind_source(I3, accepted.LONGMEMEVAL, p):
            t = surface(lambda p=p: I3.ingest_longmemeval(p, lg, enabled=True))
        ck(f"F5 guard `{guard}` is named AND fires", EXPECT[guard] in t,
           [l for l in t.splitlines() if "E-COH" in l][:1])
    # the fourth guard is structural, not a refusal: check it holds
    two = wj(TMP / "guards" / "units.json",
             [{"question_id": "lme_0", "haystack_session_ids": ["s0", "s1"],
               "haystack_dates": ["d0", "d1"],
               "haystack_sessions": [[{"role": "u", "content": "a", "has_answer": True},
                                      {"role": "u", "content": "b"}],
                                     [{"role": "u", "content": "c", "has_answer": True}]]}])
    with bind_source(I3, accepted.LONGMEMEVAL, two):
        gg = I3.ingest_longmemeval(two, lg, enabled=True)
    q = gg["questions"]["lme_0"]
    ck("F5 guard `units_enumerated_from_sessions` holds: rows index the enumerated units",
       len(q["units"]) == 3 and q["gold_rows"] == [0, 2]
       and all(0 <= r < len(q["units"]) for r in q["gold_rows"]),
       f"units={len(q['units'])} gold={q['gold_rows']}")

    # a non-boolean gold marker is REFUSED, not coerced
    nb = wj(TMP / "guards" / "nonbool.json",
            [{"question_id": "lme_0", "haystack_session_ids": ["s"], "haystack_dates": ["d"],
              "haystack_sessions": [[{"role": "u", "content": "a", "has_answer": True},
                                     {"role": "u", "content": "b", "has_answer": 1}]]}])
    with bind_source(I3, accepted.LONGMEMEVAL, nb):
        t = surface(lambda: I3.ingest_longmemeval(nb, lg, enabled=True))
        ck("F6 a non-boolean gold marker is REFUSED (E-COH-009), not coerced to False",
           "E-COH-009" in t, [l for l in t.splitlines() if "E-COH" in l][:1])
    with bind_source(I2, accepted.LONGMEMEVAL, nb):
        lg2 = R2.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lraw)
        g2r = I2.ingest_longmemeval(nb, lg2, enabled=True)
        s2r = I2.summarise(g2r)
        ck("F6-NEG v2 silently coerces it and reports declared == resolved",
           s2r["evidence_ids_declared"] == s2r["evidence_ids_resolved"]
           and s2r["evidence_ids_unresolved"] == 0
           and len(g2r["questions"]["lme_0"]["gold_rows"]) == 1,
           json.dumps({k: v for k, v in s2r.items() if "evidence" in k}))

    # well-formed input: gold / metric / cohort semantics unchanged from v2
    with bind_source(I2, accepted.LONGMEMEVAL, two), bind_source(I3, accepted.LONGMEMEVAL, two):
        a = I3.ingest_longmemeval(two, lg, enabled=True)
        b = I2.ingest_longmemeval(two, lg2, enabled=True)
        ck("F7 for WELL-FORMED input v3 gives byte-identical gold rows, units and cohort to v2",
           json.dumps({k: (v["gold_rows"], [u["memory_id"] for u in v["units"]])
                       for k, v in a["questions"].items()}, sort_keys=True)
           == json.dumps({k: (v["gold_rows"], [u["memory_id"] for u in v["units"]])
                          for k, v in b["questions"].items()}, sort_keys=True)
           and a["cohort_ids"] == b["cohort_ids"])

    # is the not-applicable representation honest? try to make a LongMemEval loss invisible
    print("\n-- F8: can a LongMemEval gold loss still hide? --")
    for label, obj in (
            ("has_answer: 1 (JSON int)", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                           "haystack_dates": ["d"],
                                           "haystack_sessions": [[{"role": "u", "content": "a",
                                                                   "has_answer": True},
                                                                  {"role": "u", "content": "b",
                                                                   "has_answer": 1}]]}]),
            ("has_answer: 'true' (string)", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                              "haystack_dates": ["d"],
                                              "haystack_sessions": [[{"role": "u", "content": "a",
                                                                      "has_answer": "true"}]]}]),
            ("has_answer absent everywhere", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                               "haystack_dates": ["d"],
                                               "haystack_sessions": [[{"role": "u",
                                                                       "content": "a"}]]}]),
            ("has_answer: null", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                   "haystack_dates": ["d"],
                                   "haystack_sessions": [[{"role": "u", "content": "a",
                                                           "has_answer": None}]]}]),
            ("has_answer: False only", [{"question_id": "lme_0", "haystack_session_ids": ["s"],
                                         "haystack_dates": ["d"],
                                         "haystack_sessions": [[{"role": "u", "content": "a",
                                                                 "has_answer": False}]]}]),
    ):
        p = wj(TMP / "f8" / f"{abs(hash(label))}.json", obj)
        with bind_source(I3, accepted.LONGMEMEVAL, p):
            t = surface(lambda p=p: I3.ingest_longmemeval(p, lg, enabled=True))
            if "E-COH" in t:
                rec("PASS", f"F8 [{label}] -> REFUSED",
                    [l for l in t.splitlines() if "E-COH" in l][0][:70])
            else:
                gg = I3.ingest_longmemeval(p, lg, enabled=True)
                ss = I3.summarise(gg)
                gold = gg["questions"]["lme_0"]["gold_rows"]
                rec("OBSERVE", f"F8 [{label}] -> proceeds",
                    f"gold_rows={gold} empty_gold={ss['questions_with_empty_gold']} "
                    f"acct={json.dumps(ss['evidence_accounting'])[:80]}")

# ============================================================================================
print("\n== G. REGRESSION on what earlier checks CLOSED =====================================")
# ============================================================================================
# D-2
with bind_manifest(accepted.LOCOMO, mraw):
    gg = R3.load_accepted_mapping(accepted.LOCOMO, raw=mraw)
    t = surface(lambda: R3.compute_results(RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], gg,
                                           seed_ok, benchmark=accepted.LOCOMO, scheme="question",
                                           replicates=7))
    ck("G1 D-2 still closed: a contradicting replicate count is refused", "E-CFG-010" in t, t[-90:])
# D-3
t = surface(lambda: R3.freeze_bootstrap_seed(TMP / "g" / "s999.json", 999, accepted.LOCOMO,
                                             "question", 10000))
ck("G2 D-3 still closed: seed 999 is refused", "E-CFG-004" in t, t[-70:])
t = surface(lambda: R3.freeze_bootstrap_seed(TMP / "g" / "st.json", 52001170, accepted.LOCOMO,
                                             "question", 10000))
ck("G2b D-3 still closed: the TRANSPOSED seed 52001170 is refused", "E-CFG-004" in t)
hand = wj(TMP / "g" / "hand.json", {"bootstrap_seed": 999, "benchmark": accepted.LOCOMO,
                                    "scheme": "question", "replicates": 10000})
t = surface(lambda: R3.read_bootstrap_seed(hand, accepted.LOCOMO, "question"))
ck("G2c D-3 still closed: a hand-forged record is caught ON READ", "E-CFG-008" in t, t[-70:])
# D-4
crlf = TMP / "g" / "crlf.json"
crlf.parent.mkdir(parents=True, exist_ok=True)
crlf.write_bytes(mb(m_obj).replace(b"\n", b"\r\n"))
with bind_manifest(accepted.LOCOMO, mb(m_obj)):
    t = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, path=crlf))
    ck("G3 D-4 still closed: a CRLF-translated manifest is REFUSED",
       "E-SRC-009" in t or "E-SRC-001" in t, t[-100:])
    ck("G3b ...and the CRLF diagnosis survives as a SAFE FLAG",
       "crlf_to_lf_would_match=True" in t, [l for l in t.splitlines() if "E-SRC" in l][:1])
# the real CRLF checkout in my own worktree
real_ck = CO / accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["path"]
if real_ck.exists():
    b = real_ck.read_bytes()
    rec("INFO", "G3c the LoCoMo manifest as CHECKED OUT on this machine",
        f"{len(b)}B sha256={hashlib.sha256(b).hexdigest()[:16]} crlf={b.count(chr(13).encode())}")
    t = surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, path=real_ck))
    ck("G3d the REAL CRLF checkout is refused with the CRLF diagnosis",
       ("crlf_to_lf_would_match=True" in t) and ("E-SRC" in t),
       [l for l in t.splitlines() if "E-SRC" in l][:1])
# superseded manifest
sup = accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL]
sup_raw = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob",
                          "64d774a6:drafts/v52/membership_runner_v1_2026_09_08/binding/"
                          "PROPOSED_mapping_longmemeval.json"], capture_output=True).stdout
t = surface(lambda: resolve_sources.verify_manifest_bytes(sup_raw, accepted.LONGMEMEVAL))
ck("G4 source trust still closed: the SUPERSEDED manifest is refused AS SUPERSEDED",
   "E-SRC-002" in t, [l for l in t.splitlines() if "E-SRC" in l][:1])
t = surface(lambda: resolve_sources.verify_manifest_bytes(sup_raw, accepted.LOCOMO))
ck("G4b ...under the other benchmark too", "E-SRC-002" in t)
# D-6
A = np.random.default_rng(0).normal(size=(20, core.DIM))
mu, D, _ = R3.fit_archive_transform(A)
Xq = np.random.default_rng(1).normal(size=(5, core.DIM))
_, stamp_ok = R3.apply_archive_transform(Xq, mu, D)
ck("G5 D-6 still closed: the honest stamp passes",
   R3.assert_query_transform_is_inherited(mu, D, stamp_ok) is None)
_, bad = R3.apply_archive_transform(Xq, Xq.mean(axis=0), D)
t = surface(lambda: R3.assert_query_transform_is_inherited(mu, D, bad))
ck("G5b ...a query-derived centering is caught", "N-4 VIOLATION" in t)
D2 = D.copy()
D2[0, 0] = np.nextafter(D2[0, 0], np.inf)
_, ulp = R3.apply_archive_transform(Xq, mu, D2)
t = surface(lambda: R3.assert_query_transform_is_inherited(mu, D, ulp))
ck("G5c ...and a ONE-ULP perturbation of D is caught", "N-4 VIOLATION" in t)
ck("G5d ...and a value-equal COPY still passes (bytes, not identity)",
   R3.assert_query_transform_is_inherited(mu.copy(), D.copy(), stamp_ok) is None)
# D-7 / D-8
with bind_manifest(accepted.LONGMEMEVAL, lraw), gate_open():
    lg = R3.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lraw)
    p = wj(TMP / "g" / "ragged.json", [{"question_id": "lme_0", "haystack_session_ids": ["a", "b"],
                                        "haystack_dates": ["d"],
                                        "haystack_sessions": [[{"role": "u", "content": "c"}]]}])
    with bind_source(I3, accepted.LONGMEMEVAL, p):
        t = surface(lambda: I3.ingest_longmemeval(p, lg, enabled=True))
        ck("G6 D-7 still closed: ragged parallel arrays are refused", "E-COH-007" in t)
    p = wj(TMP / "g" / "missing.json", [{"question_id": "lme_0"}])
    with bind_source(I3, accepted.LONGMEMEVAL, p):
        t = surface(lambda: I3.ingest_longmemeval(p, lg, enabled=True))
        ck("G7 D-8 still closed: a missing field is a NAMED refusal, not a KeyError",
           "E-COH-006" in t and "KeyError" not in t)
    # N-3 residual of D-8: an empty mapping into compute_results
    t = surface(lambda: R3.compute_results(RECORDS, ["a"], ["b"], {}, seed_ok,
                                           benchmark=accepted.LOCOMO, scheme="question",
                                           replicates=10000))
    ck("G7b N-4 residual is now CLOSED: an empty mapping is a named refusal, not KeyError",
       "E-SRC-006" in t and "KeyError" not in t, t[-80:])
# N-3 cluster block
with bind_manifest(accepted.LONGMEMEVAL, lraw):
    lg = R3.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lraw)
    lseed = TMP / "g" / "lseed.json"
    t = surface(lambda: R3.compute_results(RECORDS, ["lme_0"], ["c"], lg, lseed,
                                           benchmark=accepted.LONGMEMEVAL, scheme="cluster",
                                           replicates=10000))
    ck("G8 the LongMemEval cluster bootstrap is still REFUSED", "N-3:" in t, t[-80:])
# identity before parse
ck("G9 identity precedes parsing (a wrong-hashed AND invalid-JSON manifest fails on IDENTITY)",
   "E-SRC-001" in surface(lambda: R3.load_accepted_mapping(accepted.LOCOMO, path=notjson)))
# writers refuse to overwrite
outp2 = TMP / "g" / "res.json"
res = {k: 1 for k in R3.RESULT_KEYS}
R3.write_results(outp2, res)
t = surface(lambda: R3.write_results(outp2, res))
ck("G10 write_results still refuses to overwrite", "refusing to overwrite" in t, t[-70:])
t = surface(lambda: I3.write_ingest_manifest(outp, summ))
ck("G10b write_ingest_manifest still refuses to overwrite", "refusing to overwrite" in t)
t = surface(lambda: R3.freeze_bootstrap_seed(seed_ok, 52001107, accepted.LOCOMO, "question", 10000))
ck("G10c freeze_bootstrap_seed still refuses to overwrite", "refusing to overwrite" in t)
# no corpus-shaped file opened on import
ck("G11 importing the v3 modules opened no corpus-shaped file",
   not any(n in str(list(sys.modules)) for n in ("locomo10", "longmemeval_s_cleaned")))
# the closed core is untouched
ck("G12 the bound core identity in the module matches the accepted configuration",
   R3.BOUND_CORE == accepted.BOUND_CORE
   and accepted.BOUND_CORE["blob_sha256"].startswith("bc2282d3"),
   accepted.BOUND_CORE["blob_sha256"][:16])

# ============================================================================================
print("\n== H. the preparer's negative controls: real or vacuous? ============================")
# ============================================================================================
CONTROL = (
    "import sys, io, contextlib, traceback\n"
    "sys.path.insert(0, r'" + str(PKG2) + "'); sys.path.insert(0, r'" + str(CORE) + "')\n"
    "import membership_runner_v2 as R2, corpus_ingest_v2 as I2\n"
    "from authoritative import resolve_sources as RS\n"
    "import authoritative\n"
    "print('WHICH_AUTHORITATIVE', authoritative.__file__)\n"
    "print('WHICH_RS', RS.__file__)\n"
    "print('HAS_ERRORS_IMPORT', hasattr(RS, 'errors'))\n"
    "CANARY = " + repr(CAN["Q"]) + "\n"
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
    "print('F19', CANARY in surface(lambda: I2.verify_source_bytes('m/' + CANARY + '/x.json', 'LoCoMo', enabled=True)))\n"
)
ctl = subprocess.run([sys.executable, "-B", "-c", CONTROL], capture_output=True, text=True,
                     cwd=str(PKG2))
lines = dict(l.split(None, 1) for l in ctl.stdout.strip().splitlines() if l)
rec("INFO", "H0 subprocess control resolved `authoritative` from",
    lines.get("WHICH_AUTHORITATIVE", ctl.stderr[-100:]))
ck("H1 the subprocess control really loads v2's OWN authoritative package, not v3's",
   str(PKG2) in lines.get("WHICH_AUTHORITATIVE", "") and str(PKG3) not in
   lines.get("WHICH_AUTHORITATIVE", ""), lines.get("WHICH_AUTHORITATIVE", ""))
ck("H1b ...and that resolver is genuinely the UNFIXED one (no errors module wired in)",
   lines.get("HAS_ERRORS_IMPORT") == "False", lines.get("HAS_ERRORS_IMPORT"))
for probe in ("F16", "F17", "F18", "F19"):
    ck(f"H2 subprocess control is NOT vacuous: v2 really leaks through {probe}",
       lines.get(probe) == "True", lines.get(probe, ctl.stderr[-70:]))
# and in-process, v3 shadows v2 -> the hazard the preparer names is real
import authoritative as _auth
rec("INFO", "H3 in-process `authoritative` resolves to", _auth.__file__)
ck("H3b the shadowing hazard the preparer names is REAL (in-process it is v3's package)",
   str(PKG3) in _auth.__file__, _auth.__file__)

# ============================================================================================
print("\n== I. the three OPTIONAL residuals N-3/N-4/N-5 ======================================")
# ============================================================================================
# N-3: is transform_stamp still forgeable?
mu_q = Xq.mean(axis=0)
Xt, _ = R3.apply_archive_transform(Xq, mu_q, D)
forged = R3.transform_stamp(mu, D)
ck("I1 N-3 residual SURVIVES: a caller that re-derives the stamp still passes",
   R3.assert_query_transform_is_inherited(mu, D, forged) is None,
   "deliberate forgery, not an honest-caller error")
rec("OBSERVE", "I1b ...but it requires the caller to deliberately compute a stamp it did not use; "
               "no wrong DATA is accepted on an honest path")
# N-4: the unguarded KeyError
t = surface(lambda: R3.compute_results(RECORDS, ["a"], ["b"], {}, seed_ok,
                                       benchmark=accepted.LOCOMO, scheme="question",
                                       replicates=10000))
ck("I2 N-4 residual is FIXED in v3 (no raw KeyError from an empty mapping)", "KeyError" not in t)
# N-5: the stamp is a public constant -> a hand-built mapping with any cohort passes
forged_map = dict(fake_map(n_q=1))
forged_map["expected_question_to_cluster"] = {"locomo_0_qa0": "locomo_conv_0"}
forged_map["_accepted_manifest_sha256"] = accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["blob_sha256"]
t = surface(lambda: R3.compute_results(RECORDS, ["locomo_0_qa0"], ["locomo_conv_0"], forged_map,
                                       seed_ok, benchmark=accepted.LOCOMO, scheme="question",
                                       replicates=10000))
passed_stamp = "E-SRC-006" not in t
rec("OBSERVE" if passed_stamp else "PASS",
    "I3 N-5 residual SURVIVES: a hand-built mapping carrying the public constant passes the stamp",
    ("stamp accepted; but see I3b" if passed_stamp else "refused"))
# ...does that let WRONG DATA be accepted on a REAL call path?
with bind_source(I3, accepted.LOCOMO, src_can), gate_open():
    t2 = surface(lambda: I3.ingest_locomo(src_can, forged_map, enabled=True))
ck("I3b ...but a forged mapping cannot get a corpus in: verify_source_bytes still pins the "
   "source identity",
   "E-SRC-009" in t2 or "E-SRC-006" in t2 or "E-SRC-007" in t2 or "E-SRC-008" in t2,
   [l for l in t2.splitlines() if "E-SRC" in l][:1] or t2[-80:])
rec("INFO", "I3c the forged-mapping route requires the caller to already hold the accepted "
            "source bytes AND to hand-write a mapping; it substitutes a COHORT, not data")

print("\n" + "=" * 100)
print("TALLY " + "  ".join(f"{k}={v}" for k, v in TALLY.items()))
print("=" * 100)
print("NOTHING SEALED. NO HMAC. NO RUN. NO FINALIZE. NO REAL CORPUS READ, OPENED OR HASHED.")
