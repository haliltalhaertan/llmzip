# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Suite runner / collector (adversarial suite, own code).

Evaluates every case in cases.json against a target module exposing
  certify_pair(p, q, L, R) -> dict(status, direction, ties, ...)
with p, q 4-tuples of Fraction and L, R Fractions.

Target selection: --target PATH (aka GATE_UNDER_TEST_PATH env). Default is
the archived v2 (fixed reference). Expectations are NEVER edited after
outputs; the runner only reads cases.json.

Collector discipline: every case runs exactly once; exceptions become FAILs
(never skips); result count must equal case count or the collector itself
fails. Safety (soundness) and completeness (usefulness) are separate bars.

Run: OMP_...=1 PYTHONDONTWRITEBYTECODE=1 python3 -B run_suite.py
     [--target PATH] [--out results.json]
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate as VA  # noqa: E402
from fractions import Fraction as F  # noqa: E402

WS = "/home/mdp/muse-work/geometry-cert-adversarial"
DEFAULT_TARGET = os.path.join(
    WS, "research_representation_geometry_2026_09_13/repairs/rank_cert/certify_v2.py")
LABELS = ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
          "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"]
RESOLVING = {"STRICT", "ISOLATED_TIES", "PERSISTENT_TIE", "VARIES"}


def load_target(path):
    if not os.path.isfile(path):
        raise SystemExit("target not found: %s" % path)
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    spec = importlib.util.spec_from_file_location("gate_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert os.path.realpath(mod.__file__) == os.path.realpath(path), \
        "target path mismatch: %s" % mod.__file__
    if not hasattr(mod, "certify_pair"):
        raise SystemExit("target lacks certify_pair: %s" % path)
    return mod, sha


def evaluate(mod, cases):
    results = []
    for c in cases:
        rec = {"id": c["id"], "kind": c["kind"], "must_resolve": c["must_resolve"]}
        p = tuple(F(x) for x in c["p"])
        q = tuple(F(x) for x in c["q"])
        L, R = F(c["J"][0]), F(c["J"][1])
        try:
            cert = mod.certify_pair(p, q, L, R)
        except Exception as ex:  # noqa: BLE001 - target faults are FAILs
            rec["safety"] = "FAIL"
            rec["safety_errors"] = ["target raised %s: %s" % (type(ex).__name__, ex)]
            rec["completeness"] = "FAIL" if c["must_resolve"] else "NA"
            rec["cert"] = None
            results.append(rec)
            continue
        try:
            safely = dict(cert) if isinstance(cert, dict) else {"unparseable": repr(cert)[:200]}
            rec["cert"] = {"status": safely.get("status"),
                           "direction": safely.get("direction"),
                           "ties": list(safely.get("ties", []))
                           if isinstance(safely.get("ties"), list) else safely.get("ties")}
        except Exception:  # noqa: BLE001
            rec["cert"] = {"unparseable": True}
        errs = VA.validate_cert(c, cert)
        rec["safety"] = "PASS" if not errs else "FAIL"
        rec["safety_errors"] = errs
        if c["must_resolve"]:
            resolved = isinstance(cert, dict) and cert.get("status") in RESOLVING
            rec["completeness"] = "PASS" if (resolved and not errs) else "FAIL"
        else:
            rec["completeness"] = "NA"
        results.append(rec)
    return results


def main(argv):
    target_path = DEFAULT_TARGET
    out_name = "results_gate.json"
    i = 0
    while i < len(argv):
        if argv[i] == "--target" and i + 1 < len(argv):
            target_path = argv[i + 1]
            i += 2
        elif argv[i] == "--out" and i + 1 < len(argv):
            out_name = argv[i + 1]
            i += 2
        else:
            raise SystemExit("unknown arg: %s" % argv[i])
    env_gate = os.environ.get("GATE_UNDER_TEST_PATH")
    if env_gate and target_path == DEFAULT_TARGET:
        target_path = env_gate
    with open(os.path.join(HERE, "cases.json")) as f:
        cases = json.load(f)["cases"]
    mod, sha = load_target(target_path)
    results = evaluate(mod, cases)
    # Collector invariant: no missing, no skips.
    ran_ids = [r["id"] for r in results]
    if len(results) != len(cases) or set(ran_ids) != {c["id"] for c in cases}:
        raise SystemExit("COLLECTOR FAILURE: case coverage mismatch")
    for r in results:
        if r["safety"] not in ("PASS", "FAIL"):
            raise SystemExit("COLLECTOR FAILURE: bad verdict in %s" % r["id"])
    n_sf = sum(1 for r in results if r["safety"] == "FAIL")
    n_cf = sum(1 for r in results if r["completeness"] == "FAIL")
    n_na = sum(1 for r in results if r["completeness"] == "NA")
    out = {"labels": LABELS, "target": {"path": os.path.realpath(target_path), "sha256": sha},
           "n_cases": len(cases), "safety_fail": n_sf,
           "completeness_fail": n_cf, "completeness_na": n_na,
           "results": results}
    with open(os.path.join(HERE, out_name), "w") as f:
        json.dump(out, f, indent=2)
    print("target=%s" % os.path.realpath(target_path))
    print("cases=%d safety_fail=%d completeness_fail=%d completeness_na=%d -> %s"
          % (len(cases), n_sf, n_cf, n_na, out_name))
    for r in results:
        if r["safety"] == "FAIL" or r["completeness"] == "FAIL":
            c = r["cert"] or {}
            print("FAIL %-28s safety=%s compl=%s cert=%s/%s %s | %s"
                  % (r["id"], r["safety"], r["completeness"], c.get("status"),
                     c.get("direction"), (c.get("ties") or [])[:4], r["safety_errors"][:2]
                     if r["safety"] == "FAIL" else ""))
    if n_sf:
        raise SystemExit("SUITE FOUND %d UNSOUND CERTIFICATES (see %s)" % (n_sf, out_name))


if __name__ == "__main__":
    main(sys.argv[1:])
