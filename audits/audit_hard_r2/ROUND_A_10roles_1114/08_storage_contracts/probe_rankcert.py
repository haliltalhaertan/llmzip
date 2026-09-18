"""Probe P2b: BULGU-1 POC on isolated copies of certify_v2 vs certify_v3.

Benign exact-arithmetic fixture only (the published POC pair). No corpus
build, no fuzzing. Checks:
  v2 verdict on POC (expected: wrong ISOLATED_TIES/-1 per audit),
  v3 verdict on POC (expected: ISOLATED_TIES/VARIES),
  independent truth via the shared exact comparator at sample points,
  scale invariance of v3 over k in {1,7,100,1000}.
"""
import importlib.util
import json
import sys
from fractions import Fraction as F

D = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/08_storage_contracts/src/"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v2 = load("cert_v2_copy", D + "rank_certify_v2.py")
v3 = load("cert_v3_copy", D + "rank_certify_v3.py")

out = {"checks": []}


def check(name, fn):
    try:
        out["checks"].append({"name": name, "pass": True, "detail": fn()})
    except Exception as e:  # noqa: BLE001
        out["checks"].append({"name": name, "pass": False,
                              "detail": "%s: %s" % (type(e).__name__, e)})


p = (-100, 100, 0, 10000)
q = (-200, 200, 70000, 0)


def truth_samples():
    pts = {"5/4": F(5, 4), "3/2": F(3, 2), "7/4": F(7, 4),
           "5/2": F(5, 2), "4": F(4)}
    got = {}
    for k, z in pts.items():
        got[k] = v2.cmp_rank(v2.P4(*p), v2.P4(*q), z)
    return got  # audit truth: +1,+1,0,-1,-1 => VARIES


check("independent_truth_samples", truth_samples)


def v2_poc():
    r = v2.certify_pair(v2.P4(*p), v2.P4(*q), F(1), F(4))
    return {"status": r.get("status"), "direction": r.get("direction")}


check("v2_poc_verdict", v2_poc)


def v3_poc():
    r = v3.certify_pair(v3.P4(*p), v3.P4(*q), F(1), F(4))
    return {"status": r.get("status"), "direction": r.get("direction")}


check("v3_poc_verdict", v3_poc)


def v3_scales():
    res = {}
    for k in (1, 7, 100, 1000):
        pk = (p[0] * k, p[1] * k, p[2] * k, p[3] * k)
        qk = (q[0] * k, q[1] * k, q[2] * k, q[3] * k)
        r = v3.certify_pair(v3.P4(*pk), v3.P4(*qk), F(1), F(4))
        res[str(k)] = (r.get("status"), r.get("direction"))
    res["all_identical"] = len(set(res[str(k)] for k in (1, 7, 100, 1000))) == 1
    return res


check("v3_scale_invariance", v3_scales)


def v3_invalid_j():
    res = {}
    try:
        r = v3.certify_pair(v3.P4(*p), v3.P4(*q), F(4), F(4))
        res["L==R"] = (r.get("status"), r.get("direction"))
    except Exception as e:  # noqa: BLE001
        res["L==R"] = "raises:%s" % type(e).__name__
    try:
        r = v3.certify_pair(v3.P4(*p), v3.P4(*q), F(4), F(1))
        res["L>R"] = (r.get("status"), r.get("direction"))
    except Exception as e:  # noqa: BLE001
        res["L>R"] = "raises:%s" % type(e).__name__
    return res


check("v3_invalid_J_robustness", v3_invalid_j)

npass = sum(1 for c in out["checks"] if c["pass"])
print(json.dumps(out, indent=1, default=str))
print("PASS %d/%d" % (npass, len(out["checks"])))
sys.exit(0 if npass == len(out["checks"]) else 1)
