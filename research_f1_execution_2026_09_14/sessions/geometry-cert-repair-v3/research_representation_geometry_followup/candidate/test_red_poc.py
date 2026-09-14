"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# test_red_poc.py — RED regression for BULGU-1 (false single-direction certificate)

Deterministic one-command regression. Checks that the POC input does NOT
receive a false single-direction certificate. The failure mode on the
archived `certify_v2` MUST be the wrong claim itself (exit 1 with the
`FALSE SINGLE-DIRECTION CERTIFICATE` message), never an import or fixture
error. Ground truth below is established by the inline exact comparator
(written fresh here, importing nothing from the module under test) and
matches the coordinator receipt: `+1` on (1,7/4), tie at 7/4, `-1` on
(7/4,4], i.e. the order VARIES.

Run RED (archived v2, must FAIL with the wrong claim):

    CERT_DIR=<repo>/research_representation_geometry_2026_09_13/repairs/rank_cert \
    CERT_MODULE=certify_v2 python3 -B test_red_poc.py

Run GREEN (candidate v3, must PASS):

    CERT_DIR=<repo>/research_representation_geometry_followup/candidate \
    CERT_MODULE=certify_v3 python3 -B test_red_poc.py

This file is ADDITIVE and lives outside the published flawed package. It
does not import the module under test for ground truth, and it does not
monkeypatch anything.
"""
import importlib
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ARCHIVED_DIR = os.path.join(
    REPO, "research_representation_geometry_2026_09_13", "repairs", "rank_cert")

CERT_DIR = os.environ.get("CERT_DIR", ARCHIVED_DIR)
CERT_MODULE = os.environ.get("CERT_MODULE", "certify_v2")

sys.path.insert(0, CERT_DIR)
try:
    MOD = importlib.import_module(CERT_MODULE)
except Exception as e:
    print("FIXTURE ERROR (import failed, this is NOT the RED signal): %r" % e)
    sys.exit(3)


def truth_cmp(p, q, z):
    """Independent exact comparator (fresh code; the definitional semantics
    of pairwise rank order). Raises DomainError-like on bad denominators."""
    z = z if isinstance(z, F) else F(z)
    (a1, b1, u1, v1), (a2, b2, u2, v2) = p, q
    N1, D1 = a1 + b1 * z, u1 + v1 * z
    N2, D2 = a2 + b2 * z, u2 + v2 * z
    if not (D1 > 0 and D2 > 0):
        raise ValueError("denominator not positive at %s" % z)
    s1 = (N1 > 0) - (N1 < 0)
    s2 = (N2 > 0) - (N2 < 0)
    if s1 != s2:
        return (s1 > s2) - (s1 < s2)
    if s1 == 0:
        return 0
    c = ((N1 * N1 * D2) > (N2 * N2 * D1)) - ((N1 * N1 * D2) < (N2 * N2 * D1))
    return c if s1 > 0 else -c


def P4(a, b, u, v):
    return (F(a), F(b), F(u), F(v))


K = 100
P = P4(-1 * K, 1 * K, 0, 1 * K * K)
Q = P4(-2 * K, 2 * K, 7 * K * K, 0)
L, R = F(1), F(4)

EXPECTED_TRUTH = {F(5, 4): 1, F(3, 2): 1, F(7, 4): 0, F(5, 2): -1, F(4): -1}


def main():
    failures = []
    # 1. Ground-truth gate: independent comparator reproduces the coordinator
    #    receipt. If THIS fails, the fixture (not the module) is broken.
    for z, want in sorted(EXPECTED_TRUTH.items()):
        try:
            got = truth_cmp(P, Q, z)
        except Exception as e:
            print("FIXTURE ERROR (truth comparator failed at %s: %r)" % (z, e))
            return 3
        if got != want:
            print("FIXTURE ERROR: truth mismatch at %s: got %s want %s"
                  % (z, got, want))
            return 3
    print("truth gate OK (independent comparator): %s"
          % {str(k): v for k, v in sorted(EXPECTED_TRUTH.items())})

    # 2. Module under test must exist with the public surface.
    for attr in ("certify_pair", "P4"):
        if not hasattr(MOD, attr):
            print("FIXTURE ERROR: module %s lacks %s" % (CERT_MODULE, attr))
            return 3

    # 3. THE RED CHECK: no false single-direction certificate on the POC.
    try:
        out = MOD.certify_pair(P, Q, L, R)
    except Exception as e:
        print("FIXTURE ERROR (certify_pair raised: %r)" % e)
        return 3
    print("module outcome: status=%s direction=%s ties=%s"
          % (out.get("status"), out.get("direction"), out.get("ties")))
    st, d = out.get("status"), out.get("direction")
    if st == "ISOLATED_TIES" and d in (1, -1):
        print("FALSE SINGLE-DIRECTION CERTIFICATE: POC truth VARIES "
              "(+1 on (1,7/4), -1 on (7/4,4]) but module certifies "
              "ISOLATED_TIES direction %s" % d)
        return 1
    if st == "STRICT":
        # STRICT with any direction contradicts the observed +1/-1 pair.
        print("FALSE STRICT CERTIFICATE on a VARIES input")
        return 1
    if not ((st == "ISOLATED_TIES" and d == "VARIES") or st == "UNRESOLVED"):
        print("UNEXPECTED OUTCOME (neither sound VARIES nor UNRESOLVED): "
              "status=%s direction=%s" % (st, d))
        return 1
    print("SOUND OUTCOME: no false single-direction certificate. "
          "status=%s direction=%s" % (st, d))
    return 0


if __name__ == "__main__":
    sys.exit(main())

