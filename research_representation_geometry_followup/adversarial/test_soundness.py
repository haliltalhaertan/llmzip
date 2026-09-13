# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Deterministic soundness tests + mutation negative controls (own code).

Zero-skip harness: every registered test runs exactly once; any exception
is a FAIL; the collector fails unless ran == registered and failures == 0.
Stdlib only. Exact Fraction arithmetic; no numpy.

Covers: truth/oracle replay integrity, forged-certificate rejection
(M1 single-direction POC forgery, M2 omitted classification, M3
crossing-as-touch, M4 endpoint-tie masking, M5 UNRESOLVED->STRICT flip),
positive controls (sound certs accepted, unknown accepted), canary targets
(always-STRICT must fail safety; always-UNRESOLVED must pass safety but
fail completeness), collector invariants, and honest skipped-budget cover.

Run: OMP_...=1 PYTHONDONTWRITEBYTECODE=1 python3 -B test_soundness.py
"""
import importlib.util
import json
import os
import sys
import types
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import truth as T  # noqa: E402
import oracle as OC  # noqa: E402
import validate as VA  # noqa: E402
import run_suite as RS  # noqa: E402
from fractions import Fraction as F  # noqa: E402

WS = "/home/mdp/muse-work/geometry-cert-adversarial"
ARCH_V2 = os.path.join(
    WS, "research_representation_geometry_2026_09_13/repairs/rank_cert/certify_v2.py")

REGISTRY = []


def test(name):
    def deco(fn):
        REGISTRY.append((name, fn))
        return fn
    return deco


def load_cases():
    with open(os.path.join(HERE, "cases.json")) as f:
        d = json.load(f)
    assert d["labels"][0] == "[LOCAL EXPLORATORY PILOT]"
    return {c["id"]: c for c in d["cases"]}


def load_archived_v2():
    spec = importlib.util.spec_from_file_location("archived_certify_v2_t", ARCH_V2)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert os.path.realpath(mod.__file__) == os.path.realpath(ARCH_V2)
    return mod


def frs(case):
    return (tuple(F(x) for x in case["p"]), tuple(F(x) for x in case["q"]),
            F(case["J"][0]), F(case["J"][1]))


@test("truth_point_agreement_all_cases")
def _t1():
    cases = load_cases()
    n = 0
    for c in cases.values():
        o = c["oracle"]
        if "truth" not in o:
            continue
        p, q, _, _ = frs(c)
        for zs, v in o["truth"].items():
            assert T.true_cmp(p, q, F(zs)) == v, (c["id"], zs)
            n += 1
    assert n > 100, n
    return "replayed %d frozen points" % n


@test("oracle_closure_replay")
def _t2():
    cases = load_cases()
    n = 0
    for c in cases.values():
        o = c["oracle"]
        if o.get("robustness") or o.get("domain") == "fail":
            continue
        p, q, L, R = frs(c)
        if o.get("identically_zero"):
            assert all(T.poly_coeffs_ind(p, q)[k] == 0 for k in range(4)), c["id"]
            continue
        Q = [F(x) for x in o["Q"]]
        assert [F(x) for x in T.poly_coeffs_ind(p, q)] == Q, c["id"]
        for s in o["subintervals"]:
            assert OC.sturm_open_count(Q, F(s["lo"]), F(s["hi"])) == 0, (c["id"], s)
            n += 1
    assert n > 40, n
    return "reclosed %d subintervals" % n


@test("M1_forged_single_direction_POC_rejected")
def _t3():
    cases = load_cases()
    c = cases["poc_K100"]
    forged = {"status": "ISOLATED_TIES", "direction": -1, "ties": ["1", "7/4"],
              "notes": [], "sturm_calls": 0, "xbrackets": []}
    errs = VA.validate_cert(c, forged)
    assert errs, "forgery accepted"
    assert any("stable" in e for e in errs), errs
    return "; ".join(errs[:2])


@test("M2_omitted_classification_rejected")
def _t4():
    cases = load_cases()
    c = cases["poc_K1"]
    mut = {"status": "ISOLATED_TIES", "direction": "VARIES", "ties": ["1"],
           "notes": [], "sturm_calls": 0, "xbrackets": []}
    errs = VA.validate_cert(c, mut)
    assert errs, "omission accepted"
    assert any("unaccounted" in e for e in errs), errs
    return "; ".join(errs[:2])


@test("M3_crossing_as_touch_rejected")
def _t5():
    cases = load_cases()
    c = cases["poc_K1"]
    mut = {"status": "ISOLATED_TIES", "direction": "VARIES",
           "ties": ["1", "7/4", "touch(5/4,5/2)"],
           "notes": [], "sturm_calls": 0, "xbrackets": []}
    errs = VA.validate_cert(c, mut)
    assert errs, "touch-relabeled crossing accepted"
    assert any("touch" in e for e in errs), errs
    return "; ".join(errs[:2])


@test("M4_endpoint_tie_masking_rejected")
def _t6():
    cases = load_cases()
    c = cases["poc_K1"]
    mut = {"status": "ISOLATED_TIES", "direction": "VARIES", "ties": ["7/4"],
           "notes": [], "sturm_calls": 0, "xbrackets": []}
    errs = VA.validate_cert(c, mut)
    assert errs, "masked endpoint tie accepted"
    assert any("endpoint tie" in e for e in errs), errs
    return "; ".join(errs[:2])


@test("M5_unresolved_to_strict_flip_rejected")
def _t7():
    cases = load_cases()
    c = cases["poc_K100"]
    mut = {"status": "STRICT", "direction": 1, "ties": [],
           "notes": [], "sturm_calls": 0, "xbrackets": []}
    errs = VA.validate_cert(c, mut)
    assert errs, "flipped budget-unknown accepted"
    return "; ".join(errs[:2])


@test("positive_controls_sound_certs_accepted")
def _t8():
    cases = load_cases()
    sound = [
        ("poc_K1", {"status": "ISOLATED_TIES", "direction": "VARIES",
                    "ties": ["1", "7/4"]}),
        ("tangent_realizable", {"status": "ISOLATED_TIES", "direction": 1,
                                "ties": ["1/2"]}),
        ("tangent_abstract_only", {"status": "ISOLATED_TIES", "direction": 1,
                                   "ties": ["1"]}),
        ("common_zero", {"status": "ISOLATED_TIES", "direction": "VARIES",
                         "ties": ["1"]}),
        ("endpoint_tie_L", {"status": "ISOLATED_TIES", "direction": -1,
                            "ties": ["0"]}),
        ("endpoint_tie_R", {"status": "ISOLATED_TIES", "direction": 1,
                            "ties": ["2"]}),
        ("P_identically_zero", {"status": "PERSISTENT_TIE", "direction": 0,
                                "ties": ["1", "2", "persistent(1,2)"]}),
        ("poc_K1", {"status": "UNRESOLVED", "direction": None, "ties": []}),
        ("invalidJ_domain", {"status": "DOMAIN_FAIL", "direction": None, "ties": []}),
        ("invalidJ_inverted", {"status": "EMPTY", "direction": None, "ties": []}),
    ]
    for cid, cert in sound:
        errs = VA.validate_cert(cases[cid], cert)
        assert not errs, (cid, errs)
    for cid in ("search_strict_pos_Jq", "search_strict_neg_Jq", "search_two_roots_Jq"):
        c = cases[cid]
        o = c["oracle"]
        d = 1 if o["plus"] else -1
        errs = VA.validate_cert(c, {"status": "STRICT", "direction": d, "ties": []})
        assert not errs, (cid, errs)
    return "13 sound certs accepted, unknown accepted"


@test("canary_always_STRICT_fails_safety")
def _t9():
    cases = load_cases()
    mod = types.ModuleType("always_strict")
    mod.certify_pair = lambda p, q, L, R: {"status": "STRICT", "direction": 1,
                                           "ties": []}
    res = RS.evaluate(mod, list(cases.values()))
    assert len(res) == len(cases)
    fails = [r for r in res if r["safety"] == "FAIL"]
    assert fails, "always-STRICT passed safety: suite has no teeth"
    assert "poc_K100" in {r["id"] for r in fails}, [r["id"] for r in fails]
    return "%d/%d safety FAIL (incl poc_K100)" % (len(fails), len(res))


@test("canary_always_UNRESOLVED_splits_bars")
def _t10():
    cases = load_cases()
    mod = types.ModuleType("always_unresolved")
    mod.certify_pair = lambda p, q, L, R: {"status": "UNRESOLVED", "direction": None,
                                           "ties": []}
    res = RS.evaluate(mod, list(cases.values()))
    assert len(res) == len(cases)
    assert all(r["safety"] == "PASS" for r in res), "unknown penalized as unsound"
    must = [r for r in res if r["completeness"] != "NA"]
    assert must and all(r["completeness"] == "FAIL" for r in must)
    return "safety all-PASS, completeness FAIL on %d must_resolve" % len(must)


@test("collector_invariants_and_honest_budget_cover")
def _t11():
    cases = load_cases()
    assert len(cases) == 41, len(cases)
    kinds = {}
    for c in cases.values():
        for k in ("id", "kind", "p", "q", "J", "oracle", "must_resolve", "notes"):
            assert k in c, (c.get("id"), k)
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    assert kinds.get("fuzz-supplemental") == 24, kinds
    assert kinds.get("robustness") == 3, kinds
    V = load_archived_v2()
    for k, want_skipped in (("poc_K1", False), ("poc_K10", False),
                            ("poc_K100", True), ("poc_K1000", True)):
        c = cases[k]
        p, q, _, _ = frs(c)
        _, sk = V.rational_roots(V.P_coeffs(p, q))
        assert bool(sk) is want_skipped, (k, sk)
    return "41 cases; honest skipped=%s on K100/K1000" % kinds


@test("results_v2_documents_failures")
def _t12():
    with open(os.path.join(HERE, "results_v2.json")) as f:
        d = json.load(f)
    assert d["n_cases"] == 41
    by_id = {r["id"]: r for r in d["results"]}
    assert len(by_id) == 41
    for k in ("poc_K100", "poc_K1000", "poc_reversed_K100"):
        assert by_id[k]["safety"] == "FAIL", k
        assert any("stable" in e for e in by_id[k]["safety_errors"]), k
    assert d["safety_fail"] >= 3
    return "results_v2: safety_fail=%d" % d["safety_fail"]


def main():
    passed, failed, notes = 0, [], {}
    for name, fn in REGISTRY:
        try:
            notes[name] = fn()
            print("PASS %s -- %s" % (name, notes[name]))
            passed += 1
        except Exception:  # noqa: BLE001 - harness records, never skips
            failed.append(name)
            print("FAIL %s\n%s" % (name, traceback.format_exc(limit=3)))
    total = len(REGISTRY)
    ran = passed + len(failed)
    print("tests=%d ran=%d pass=%d fail=%d skipped=0" % (total, ran, passed, len(failed)))
    if ran != total or failed:
        raise SystemExit("SOUNDNESS TESTS FAILED: %s" % failed)
    print("ALL SOUNDNESS TESTS PASS")


if __name__ == "__main__":
    main()
