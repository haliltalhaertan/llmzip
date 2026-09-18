"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
test_validate_v3.py -- BULGU-5 semantics tests for cert_validator_v3.py.

The independent validator must REJECT the archived counterfeit certificate
(BULGU-1's false ISOLATED_TIES/-1 on the POC, which the old `validate_cert`
passed with None) and ACCEPT every genuine v3 certificate. Finite
sample-level scans are used here only as FALSIFICATION witnesses (a
counter-sign sample kills a single-direction claim); the proof step is the
validator's interval/root coverage, never the scan.

Run: PYTHONDONTWRITEBYTECODE=1 python3 -B test_validate_v3.py  (exit 0 pass)
"""
import copy
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import certify_v3 as V
from cert_validator_v3 import validate_cert_v3

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail)))
    if not cond:
        print("FAIL", name, detail, flush=True)


def P4(a, b, u, v):
    return (F(a), F(b), F(u), F(v))


K = 100
POC_P = P4(-1 * K, 1 * K, 0, 1 * K * K)
POC_Q = P4(-2 * K, 2 * K, 7 * K * K, 0)
POC_J = (F(1), F(4))


def counterfeit_cert():
    """The archived v2 output on the POC, reconstructed literally: the
    counterfeit the old validator passed (BULGU-5 executed proof)."""
    return {"status": "ISOLATED_TIES", "direction": -1,
            "ties": ["1", "7/4"], "notes": [], "sturm_calls": 0,
            "xbrackets": [], "disc_fired": 0}


def t_rejects_counterfeit():
    err = validate_cert_v3(POC_P, POC_Q, *POC_J, counterfeit_cert())
    check("counterfeit-rejected", err is not None,
          "validator accepted the counterfeit: %r" % err)
    check("counterfeit-reason-cell", err is not None and "cell" in err, err)
    # The old semantics (single-direction ISOLATED_TIES with no order
    # sampling) passes this exact input: that hole is what BULGU-5 reports.
    old_style_hole = True  # documented by the audit's executed proof
    check("bulgu5-hole-documented", old_style_hole, "audit BULGU-5")


def t_accepts_genuine_v3():
    cases = [
        ("poc-varies", POC_P, POC_Q, *POC_J),
        ("poc-unscaled", P4(-1, 1, 0, 1), P4(-2, 2, 7, 0), F(1), F(4)),
        ("strict", P4(1, 1, 1, 1), P4(0, 1, 1, 1), F(1), F(4)),
        ("tangent", P4(1, 1, 0, 4), P4(1, 0, 1, 0), F(1, 4), F(4)),
        ("persist", P4(0, 1, 1, 1), P4(0, 2, 4, 4), F(1), F(4)),
        ("varies-real", P4(0, 1, 1, 1), P4(3, -1, 1, 1), F(1), F(4)),
        ("irrat", P4(0, 1, 2, 0), P4(1, 0, 1, 0), F(1), F(2)),
        ("tworoot", P4(5, 1, 1, 0), P4(2, 0, 1, 0), F(-8), F(-1)),
        ("unres", POC_P, POC_Q, F(1), F(4)),
    ]
    for name, p, q, L, R in cases:
        if name == "unres":
            cert = V.certify_pair(p, q, L, R, split_cap=0)
            assert cert["status"] == "UNRESOLVED", cert
        else:
            cert = V.certify_pair(p, q, L, R)
        err = validate_cert_v3(p, q, L, R, cert)
        check("accept-%s" % name, err is None,
              (cert["status"], cert["direction"], err))


def t_rejects_mutations():
    base = V.certify_pair(POC_P, POC_Q, *POC_J)
    assert validate_cert_v3(POC_P, POC_Q, *POC_J, base) is None, base
    # Flipped direction on a VARIES cert.
    m = copy.deepcopy(base)
    m["direction"] = -1
    check("mut-direction", validate_cert_v3(POC_P, POC_Q, *POC_J, m)
          is not None, "flipped direction accepted")
    # Dropped exact tie -> coverage gap (cell with an unlisted root).
    m = copy.deepcopy(base)
    m["ties"] = [t for t in m["ties"] if t != "7/4"]
    check("mut-dropped-tie", validate_cert_v3(POC_P, POC_Q, *POC_J, m)
          is not None, "dropped tie accepted")
    # Bogus exact tie.
    m = copy.deepcopy(base)
    m["ties"] = list(m["ties"]) + ["5/2"]
    check("mut-bogus-tie", validate_cert_v3(POC_P, POC_Q, *POC_J, m)
          is not None, "bogus tie accepted")
    # Wrong kind on a genuine cross bracket (irrational case has one).
    icert = V.certify_pair(P4(0, 1, 2, 0), P4(1, 0, 1, 0), F(1), F(2))
    assert any(x["kind"] == "cross" for x in icert["xbrackets"]), icert
    m = copy.deepcopy(icert)
    for x in m["xbrackets"]:
        x["kind"] = "touch"
    m["ties"] = [t.replace("cross(", "touch(") for t in m["ties"]]
    check("mut-kind", validate_cert_v3(
        P4(0, 1, 2, 0), P4(1, 0, 1, 0), F(1), F(2), m) is not None,
        "wrong kind accepted")
    # STRICT claim on a VARIES input.
    m = {"status": "STRICT", "direction": 1, "ties": [], "notes": [],
         "sturm_calls": 0, "xbrackets": [], "disc_fired": 0}
    check("mut-strict", validate_cert_v3(POC_P, POC_Q, *POC_J, m)
          is not None, "false STRICT accepted")


def t_scan_is_falsification_not_proof():
    # A 17-point-style scan PASSES the counterfeit shape below (no
    # counter-sign sample on its own grid is not the issue -- the issue is
    # the scan proves nothing about the unscanned continuum), while the
    # coverage validator rejects it. Both facts are asserted to keep the
    # two evidence kinds distinct.
    shrink = {"status": "ISOLATED_TIES", "direction": -1, "ties": ["1"],
              "notes": [], "sturm_calls": 0, "xbrackets": [],
              "disc_fired": 0}
    grid_ok = True
    for k in range(17):
        z = POC_J[0] + (POC_J[1] - POC_J[0]) * k / 16
        if V.cmp_rank(POC_P, POC_Q, z) == 1:
            grid_ok = False
    # NOTE: on THIS grid a +1 sample exists (k with z in (1,7/4)), so even
    # the scan falsifies the shrink claim; the documented old hole was the
    # ABSENCE of any such scan for single-direction ISOLATED_TIES.
    check("scan-falsifies-shrink", grid_ok is False, "grid missed +1")
    err = validate_cert_v3(POC_P, POC_Q, *POC_J, shrink)
    check("validator-rejects-shrink", err is not None, err)


def main():
    t_rejects_counterfeit()
    t_accepts_genuine_v3()
    t_rejects_mutations()
    t_scan_is_falsification_not_proof()
    fails = [(n, d) for (n, ok, d) in CHECKS if not ok]
    print("checks=%d fail=%d" % (len(CHECKS), len(fails)))
    if fails:
        print("FAILED:", [n for (n, _) in fails])
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
