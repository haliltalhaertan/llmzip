# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BULGU-1 executed reproduction against the ARCHIVED v2 (exact path import).

- Loads certify_v2.py ONLY from research_representation_geometry_2026_09_13/
  repairs/rank_cert/certify_v2.py via importlib file-location spec and asserts
  the loaded __file__ equals that archived path (no stray-module pickup; the
  old POC's hardcoded /home/mdp/muse-work/fix_rank_cert/out is never used).
- Truth comes from own truth.py (integer cross products), never v2.cmp_rank.
- Also records the conservative original (verify_orig_copy.py) verdict and the
  unscaled-twin v2 verdict for the receipt.
- Writes receipts/repro_bulgu1.json. Exit 0 documents EXISTENCE OF THE BUG,
  not repair success.

Run: OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
     NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -B repro_bulgu1.py
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import truth as T  # noqa: E402
from fractions import Fraction as F  # noqa: E402

ARCHIVE = os.path.join(
    os.path.dirname(HERE), "..", "..",
    "..", "..", "..", "..", "..", "..", "..", "..")
# Canonical archived module paths (exact, no search).
WS = "/home/mdp/muse-work/geometry-cert-adversarial"
ARCH_V2 = os.path.join(
    WS, "research_representation_geometry_2026_09_13/repairs/rank_cert/certify_v2.py")
ARCH_ORIG = os.path.join(
    WS, "research_representation_geometry_2026_09_13/repairs/rank_cert/verify_orig_copy.py")
STRAY = "/home/mdp/muse-work/fix_rank_cert/out/certify_v2.py"


def load_exact(name, path):
    assert os.path.isfile(path), "missing archived module: %s" % path
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = os.path.realpath(mod.__file__)
    want = os.path.realpath(path)
    assert got == want, "stray module pickup: %s != %s" % (got, want)
    return mod


def main():
    stray_present = os.path.exists(STRAY)
    print("stray POC path %s present=%s (never imported; archived path enforced below)"
          % (STRAY, stray_present))
    for m in list(sys.modules):
        assert "fix_rank_cert" not in m, "stray module already imported: %s" % m
    V = load_exact("archived_certify_v2", ARCH_V2)
    O = load_exact("archived_verify_orig", ARCH_ORIG)

    K = 100
    p = (F(-1 * K), F(1 * K), F(0), F(1 * K * K))
    q = (F(-2 * K), F(2 * K), F(7 * K * K), F(0))
    L, R = F(1), F(4)
    probes = (F(5, 4), F(3, 2), F(7, 4), F(5, 2), F(4))

    # Independent truth (integer route) + second-route polynomial check.
    tv = {str(z): T.true_cmp(p, q, z) for z in probes}
    Q = T.poly_coeffs_ind(p, q)
    Pv = V.P_coeffs(p, q)
    assert [F(c) for c in Q] == [F(c) for c in Pv], "P-route mismatch: %s vs %s" % (Q, Pv)
    # Roots of Q at the claimed ties (z=1 endpoint, z=7/4 interior).
    assert T.peval(Q, F(1)) == 0 and T.peval(Q, F(7, 4)) == 0, Q
    # v2 point comparator agrees with independent truth ON POINTS
    # (the bug is in certificate logic, not point evaluation).
    for z in probes:
        assert V.cmp_rank(p, q, z) == tv[str(z)], (z, V.cmp_rank(p, q, z), tv[str(z)])

    rrs, skipped = V.rational_roots(V.P_coeffs(p, q))
    rv = V.certify_pair(p, q, L, R)
    ro = O.certify_pair(p, q, L, R)
    p0 = (F(-1), F(1), F(0), F(1))
    q0 = (F(-2), F(2), F(7), F(0))
    rv0 = V.certify_pair(p0, q0, L, R)

    receipt = {
        "labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                   "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
        "archived_v2_file": os.path.realpath(ARCH_V2),
        "archived_orig_file": os.path.realpath(ARCH_ORIG),
        "inputs": {"p": [str(x) for x in p], "q": [str(x) for x in q],
                   "J": [str(L), str(R)]},
        "independent_truth": tv,
        "poly_Q": [str(c) for c in Q],
        "rational_roots_skipped": bool(skipped),
        "v2_certificate": {"status": rv["status"], "direction": rv["direction"],
                           "ties": list(rv["ties"])},
        "v2_unscaled_twin": {"status": rv0["status"], "direction": rv0["direction"],
                             "ties": list(rv0["ties"])},
        "original_conservative": {"status": ro["status"]},
    }
    with open(os.path.join(HERE, "receipts", "repro_bulgu1.json"), "w") as f:
        json.dump(receipt, f, indent=2)

    print("independent truth:", tv)
    print("rational_roots skipped:", skipped)
    print("v2 scaled:  ", rv["status"], rv["direction"], rv["ties"])
    print("v2 unscaled:", rv0["status"], rv0["direction"], rv0["ties"])
    print("orig scaled:", ro["status"])

    # Bug-existence assertions (exit 0 = BUG PRESENT, not fixed).
    assert tv == {"5/4": 1, "3/2": 1, "7/4": 0, "5/2": -1, "4": -1}, tv
    assert skipped is True
    assert (rv["status"], rv["direction"]) == ("ISOLATED_TIES", -1), rv
    assert (rv0["status"], rv0["direction"]) == ("ISOLATED_TIES", "VARIES"), rv0
    assert ro["status"] == "UNRESOLVED", ro
    print("POC CONFIRMED: v2 issues false ISOLATED_TIES/-1; truth VARIES; orig UNRESOLVED.")


if __name__ == "__main__":
    main()
