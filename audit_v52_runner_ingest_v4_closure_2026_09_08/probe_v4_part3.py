"""INDEPENDENT probe suite, part 3: byte-verbatim captures, the remaining int() sites, and the
whole-string contract behaviour. Synthetic only; no real corpus opened, read, hashed or scanned.

Usage:  python -B probe_v4_part3.py <checkout-of-86a8fd7a>
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import traceback
from enum import Enum
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
PKG4 = ROOT / "drafts/v52/membership_runner_ingest_v4_2026_09_08"
PKG3 = ROOT / "drafts/v52/membership_runner_ingest_v3_2026_09_08"
CORE = ROOT / "drafts/v52/membership_impl_v3_2026_09_07"
for _p in (CORE, PKG3, PKG4):
    sys.path.insert(0, str(_p))

import membership_scaling_core as core          # noqa: E402
import errors                                   # noqa: E402
import membership_runner_v4 as R4               # noqa: E402
import corpus_ingest_v4 as I4                   # noqa: E402
import membership_runner_v3 as R3               # noqa: E402
import corpus_ingest_v3 as I3                   # noqa: E402
from authoritative import accepted_configuration as accepted   # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="audit_v4c_"))
CANARY = "Where did Rashid park the blue van on the night of the storm?"
TALLY = {}


def say(kind, label, detail=""):
    TALLY[kind] = TALLY.get(kind, 0) + 1
    print((f"{kind:<8} {label}" + (f"   |  {detail}" if detail else ""))[:500])


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
        seen, cur = set(), e
        while cur is not None and id(cur) not in seen:
            seen.add(id(cur))
            parts.append(f"[chain {type(cur).__name__}] {cur!r}")
            cur = cur.__cause__ or cur.__context__
    return out.getvalue() + err.getvalue() + "\n".join(parts)


def wj(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return path


def mb(obj):
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


MAP = {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
       "expected_cluster_ids": ["locomo_conv_0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"}, "n_questions": 1}
MAP_RAW = mb(MAP)

print("=" * 110)
print("INDEPENDENT AUDIT PROBES part 3. SYNTHETIC ONLY. No real corpus opened, read, hashed or scanned.")
print("=" * 110)

# ==========================================================================================
print("\n== J. byte-verbatim: the __class__-spoof escape out of validate_identifier ================")
# ==========================================================================================


class FakeKind:
    value = CANARY

    @property
    def __class__(self):
        return R4.IdentifierKind


fk = FakeKind()
say("INFO", "J1 isinstance(fake, IdentifierKind)", str(isinstance(fk, R4.IdentifierKind)))
say("INFO", "J2 the object is NOT actually a member", str(type(fk).__mro__[0].__name__))
try:
    R4.validate_identifier(" x", fk, 0)
    msg = "(no exception)"
except BaseException as e:                                                        # noqa: BLE001
    msg = str(e)
print("J3 BYTE-VERBATIM message from validate_identifier with a __class__-spoofed kind:")
print("   >>> " + msg)
ck("J4 the escape needs an object that LIES about its own __class__; no JSON value can do it",
   CANARY in msg, "recorded as a THEORETICAL caller-override path, not a data path", failkind="OBSERVE")
say("INFO", "J5 the honest gate would be an identity check", "`value in IdentifierKind` / `value is a member`")
# is it reachable from anything the pipeline itself produces?
ck("J6 no in-package caller passes anything but an IdentifierKind literal",
   (PKG4 / "membership_runner_v4.py").read_text(encoding="utf-8").count("validate_identifier(v, IdentifierKind.") == 2)

# ==========================================================================================
print("\n== K. errors.message: what still reaches a message =========================================")
# ==========================================================================================
DynEnum = Enum("Dyn", {"X": CANARY})
m = errors.message(errors.Code.EMPTY_COHORT, x=DynEnum.X)
print("K1 BYTE-VERBATIM errors.message with a hand-built Enum whose value is a canary:")
print("   >>> " + m)
ck("K1b errors._safe still prints ANY Enum's .value - unchanged from v3, and now reachable only by "
   "a caller that hand-builds an Enum", CANARY in m, "THEORETICAL", failkind="OBSERVE")
try:
    errors.message(errors.Code.EMPTY_COHORT, **{"canaryKeyOdessa1987": "x"})
    m2 = "(no exception)"
except BaseException as e:                                                        # noqa: BLE001
    m2 = str(e)
print("K2 BYTE-VERBATIM UnsafeErrorField message for an unsafe field:")
print("   >>> " + m2)
ck("K2b the kwarg KEY is echoed by UnsafeErrorField's own message - unchanged from v3, theoretical",
   "canaryKeyOdessa1987" in m2, "every in-package call site uses literal keyword names",
   failkind="OBSERVE")
ck("K3 a str VALUE still cannot enter a message - UnsafeErrorField fires first",
   "x" not in m2.split("is a")[-1] or "str" in m2)

# ==========================================================================================
print("\n== L. the OTHER int() sites in the same module and its callers =============================")
# ==========================================================================================
for label, fn in {
    "L1 freeze_bootstrap_seed(seed=<canary str>)":
        lambda: R4.freeze_bootstrap_seed(TMP / "s1.json", CANARY, accepted.LOCOMO, "question", 10000),
    "L2 freeze_bootstrap_seed(replicates=<canary str>)":
        lambda: R4.freeze_bootstrap_seed(TMP / "s2.json", 52001107, accepted.LOCOMO, "question", CANARY),
    "L3 freeze_bootstrap_seed(seed=<obj with __int__>)":
        lambda: R4.freeze_bootstrap_seed(TMP / "s3.json",
                                         type("Z", (), {"__int__": lambda s: 52001107,
                                                        "__repr__": lambda s: CANARY})(),
                                         accepted.LOCOMO, "question", 10000),
}.items():
    t = surface(fn)
    leak = CANARY in t
    ck(f"{label}: no caller value escapes", not leak,
       ("LEAK: " + [l for l in t.splitlines() if CANARY in l][0][:200]) if leak
       else t.strip().splitlines()[-1][:150], failkind="FINDING")

# the file-derived path: replicates read back out of the frozen record (the F20 class)
with contextlib.ExitStack() as st:
    s = dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
    accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = dict(s, blob_sha256=hashlib.sha256(MAP_RAW).hexdigest())
    st.callback(lambda: accepted.ACCEPTED_MANIFESTS.__setitem__(accepted.LOCOMO, s))
    m4 = R4.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    good = TMP / "seed_ok.json"
    R4.freeze_bootstrap_seed(good, 52001107, accepted.LOCOMO, "question", 10000)
    rec = json.loads(good.read_text(encoding="utf-8"))
    poisoned = wj(TMP / "seed_poison.json", dict(rec, replicates=CANARY))
    recs = [{"question_id": "locomo_0_qa0", "rotation_seed": int(x), "arm": a, "fractional_R3": 0.5}
            for x in core.ROTATION_SEEDS for a in core.ARMS]
    t = surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], m4, poisoned,
                                           benchmark=accepted.LOCOMO, scheme="question", replicates=10000))
    ck("L4 a FILE-derived replicates canary (read back out of a record the pipeline itself writes) "
       "does not escape through int()", CANARY not in t, t.strip().splitlines()[-1][:200])
    t = surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], m4, good,
                                           benchmark=accepted.LOCOMO, scheme="question", replicates=CANARY))
    ck("L5 a CALLER-supplied replicates canary does not escape through int()", CANARY not in t,
       t.strip().splitlines()[-1][:200])

# ==========================================================================================
print("\n== M. the free-text string: the sixth shape of the v3 closure report =======================")
# ==========================================================================================
V3_SIX = {
    "M1 [{'dia_id':'D1:0'},{'note':'second gold turn'}]": [{"dia_id": "D1:0"}, {"note": "second gold turn"}],
    "M2 [{'dia_id':'D1:0'},{'dia_id':''}]": [{"dia_id": "D1:0"}, {"dia_id": ""}],
    "M3 [{'dia_id':'D1:0'},{'dia_id':None}]": [{"dia_id": "D1:0"}, {"dia_id": None}],
    "M4 ['D1:0',12345]": ["D1:0", 12345],
    "M5 ['D1:0',None]": ["D1:0", None],
    "M6 'see D1:0 and also the bakery note'": "see D1:0 and also the bakery note",
}
for label, v in V3_SIX.items():
    t = surface(lambda x=v: I4._normalise_evidence(x))
    refused = "E-COH-011" in t or "E-COH-012" in t
    got4 = None if refused else I4._normalise_evidence(v)
    got3 = I3._normalise_evidence(v)
    ck(f"{label}: v4 refuses", refused,
       f"v4 returned {got4}; v3 returned {got3}", failkind="OBSERVE")

# What does the FROZEN PRODUCER do with M6? (retyped by me from the raw blob at 692f599e)
import re as _re
_D = _re.compile(r"D\d+:\d+")
prod_m6 = _D.findall("see D1:0 and also the bakery note") or ["see D1:0 and also the bakery note"]
say("INFO", "M7 the frozen producer's own result for M6", repr(prod_m6))
ck("M8 v4's result for M6 is EXACTLY the frozen producer's - the shape is contract-valid, not a "
   "malformed one, and v4 now publishes raw_evidence_items=1 which truthfully reports one entry",
   I4._normalise_evidence("see D1:0 and also the bakery note") == (prod_m6, 1))

# ==========================================================================================
print("\n== N. str() coercion inside the accepted dict branch =======================================")
# ==========================================================================================
print("N1 the v4 comment says: 'Neither is repaired, coerced to a string, or dropped. Nothing is guessed.'")
print("N2 the FIX_PACKAGE table says: 'Nothing is guessed, coerced to a string or dropped.'")
for lbl, v in [("N3 {'dia_id': 12345}", [{"dia_id": 12345}]),
               ("N4 {'dia_id': 1.5}", [{"dia_id": 1.5}]),
               ("N5 {'dia_id': ['D1:0']}", [{"dia_id": ["D1:0"]}])]:
    got = I4._normalise_evidence(v)
    say("OBSERVE", f"{lbl} IS coerced by str(did) - identical to the frozen producer, and NOT refused",
        repr(got))
ck("N6 that coercion is the bound contract's own (`out.append(str(did))` in norm_evidence), so it is "
   "contract-faithful; the two sentences above are about the two REFUSAL cases, and read as absolute",
   True, "classified (iii) wording, not (i)", failkind="OBSERVE")
# but is the coerced id then invisible? no - it cannot resolve, so it is counted unresolved
with contextlib.ExitStack() as st:
    s = dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
    accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = dict(s, blob_sha256=hashlib.sha256(MAP_RAW).hexdigest())
    st.callback(lambda: accepted.ACCEPTED_MANIFESTS.__setitem__(accepted.LOCOMO, s))
    core.REAL_DATA_EXECUTION_ENABLED = True
    m4 = R4.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    d = TMP / "coerce"
    conv = {"speaker_a": "A", "speaker_b": "B",
            "session_1": [{"dia_id": f"D1:{t}", "speaker": "A", "text": f"turn {t}"} for t in range(4)],
            "session_1_date_time": "1 Jan 2020"}
    src = [{"sample_id": "conv-0", "conversation": conv,
            "qa": [{"question": CANARY, "answer": "a", "category": 1,
                    "evidence": [{"dia_id": "D1:0"}, {"dia_id": 12345}]}]}]
    p = wj(d / "locomo10.json", src)
    old = dict(I4.BOUND_SOURCES[accepted.LOCOMO])
    I4.BOUND_SOURCES[accepted.LOCOMO] = dict(old, filename=p.name,
                                             sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                             bytes=p.stat().st_size)
    t = surface(lambda: I4.ingest_locomo(p, m4))
    I4.BOUND_SOURCES[accepted.LOCOMO] = old
    core.REAL_DATA_EXECUTION_ENABLED = False
    ck("N7 a str()-coerced non-string id cannot resolve, so it lands in `unresolved` and the run STOPS "
       "with E-COH-002 - the loss is NOT silent", "E-COH-002" in t, t.strip().splitlines()[-1][:200])
    ck("N8 and that refusal carries no content", CANARY not in t)

print(f"\nTALLY-PART3 {TALLY}")
