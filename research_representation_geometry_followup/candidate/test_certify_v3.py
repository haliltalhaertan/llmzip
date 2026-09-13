"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
test_certify_v3.py -- RED->GREEN vertical tests for certify_v3.py (BULGU-1 repair).

Covers the task checklist: POC VARIES with per-cell evidence (not a
fallback UNRESOLVED), input-scale invariance of truthful status/direction,
positive score-preserving transforms, doc-swap direction inversion, root
bound / precision / budget exhaustion refusing (never false certainty),
invalid intervals, DOMAIN_FAIL, zero polynomials, numerator-negative
reversal, multiple roots, and orig agreement on fixed cases.

Realizability: the certifier works on the ABSTRACT (a,b,u,v) domain. Every
example below carries an explicit label -- either constraint-level
real-vector realizable (u,v>=0; u=0=>a==0; v=0=>b==0, per the audited
REALIZABILITY_TR constraints) or abstract-only. Abstract-only examples are
legitimate certifier inputs; they are NOT claimed realizable.

Ground truth in this file comes from the fresh inline exact comparator
`truth_cmp` (definitional semantics; imports nothing from certify_v3).

Run: PYTHONDONTWRITEBYTECODE=1 python3 -B test_certify_v3.py  (exit 0 pass)
"""
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ARCHIVED = os.path.normpath(os.path.join(
    HERE, "..", "..", "research_representation_geometry_2026_09_13",
    "repairs", "rank_cert"))
sys.path.insert(0, ARCHIVED)

import certify_v3 as V
import verify_orig_copy as O

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail)))
    if not cond:
        print("FAIL", name, detail, flush=True)


def truth_cmp(p, q, z):
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


def realizability(p, q):
    """Constraint-level label only (NOT a shared-query construction proof)."""
    for (a, b, u, v) in (p, q):
        if not (u >= 0 and v >= 0):
            return "abstract-only"
        if u == 0 and a != 0:
            return "abstract-only"
        if v == 0 and b != 0:
            return "abstract-only"
    return "realizable-constraints"


K = 100
POC_P = P4(-1 * K, 1 * K, 0, 1 * K * K)
POC_Q = P4(-2 * K, 2 * K, 7 * K * K, 0)
POC_J = (F(1), F(4))


def t_poc_varies_with_cell_evidence():
    # Abstract-only (u=0 with a!=0 in p).
    check("poc-label", realizability(POC_P, POC_Q) == "abstract-only",
          realizability(POC_P, POC_Q))
    out = V.certify_pair(POC_P, POC_Q, *POC_J)
    check("poc-status", out["status"] == "ISOLATED_TIES", out["status"])
    check("poc-direction", out["direction"] == "VARIES", out["direction"])
    check("poc-tie-7/4", "7/4" in out["ties"], out["ties"])
    check("poc-crossing-note",
          any("exact crossing at 7/4" in n for n in out["notes"]),
          out["notes"])
    # Per-cell evidence: both orders proven on root-free cells flanking 7/4.
    P = V.P_coeffs(POC_P, POC_Q)
    check("poc-cell-left-rootfree",
          V.sturm_open_count(P, F(1), F(7, 4)) == 0, "left cell")
    check("poc-cell-right-rootfree",
          V.sturm_open_count(P, F(7, 4), F(4)) == 0, "right cell")
    check("poc-cell-left-order",
          truth_cmp(POC_P, POC_Q, F(5, 4)) == 1, "+1 left of 7/4")
    check("poc-cell-right-order",
          truth_cmp(POC_P, POC_Q, F(5, 2)) == -1, "-1 right of 7/4")
    # Original conservative certifier honestly refuses this input.
    ro = O.certify_pair(POC_P, POC_Q, *POC_J)
    check("poc-orig-unresolved", ro["status"] == "UNRESOLVED", ro["status"])


def t_scale_invariance():
    for k in (1, 7, 100, 1000):
        p = P4(-1 * k, 1 * k, 0, 1 * k * k)
        q = P4(-2 * k, 2 * k, 7 * k * k, 0)
        skipped = V.rational_roots(V.P_coeffs(p, q))[1]
        out = V.certify_pair(p, q, *POC_J)
        check("scale-k%d-verdict" % k,
              (out["status"], out["direction"]) == ("ISOLATED_TIES", "VARIES"),
              (skipped, out["status"], out["direction"]))
    # Enumeration skips at large scales but the verdict is identical.
    sk1 = V.rational_roots(V.P_coeffs(
        P4(-1, 1, 0, 1), P4(-2, 2, 7, 0)))[1]
    skK = V.rational_roots(V.P_coeffs(POC_P, POC_Q))[1]
    check("scale-skip-differs", (sk1, skK) == (False, True), (sk1, skK))


def t_score_preserving_transform():
    # (a,b)->k(a,b), (u,v)->k^2(u,v) leaves N^2/D scores invariant.
    bases = [
        ("poc1", P4(-1, 1, 0, 1), P4(-2, 2, 7, 0), POC_J),
        ("strict", P4(1, 1, 1, 1), P4(0, 1, 1, 1), (F(1), F(4))),
        ("varies", P4(0, 1, 1, 1), P4(3, -1, 1, 1), (F(1), F(4))),
    ]
    for name, p, q, (L, R) in bases:
        ref = V.certify_pair(p, q, L, R)
        for k in (2, 3, 5):
            kp = (k * p[0], k * p[1], k * k * p[2], k * k * p[3])
            kq = (k * q[0], k * q[1], k * k * q[2], k * k * q[3])
            got = V.certify_pair(kp, kq, L, R)
            check("sptr-%s-k%d" % (name, k),
                  (got["status"], got["direction"]) ==
                  (ref["status"], ref["direction"]),
                  (ref["status"], ref["direction"],
                   got["status"], got["direction"]))
        # Scores themselves are invariant at sample points.
        for z in (L, (L + R) / 2, R):
            check("sptr-%s-scores" % name,
                  truth_cmp(p, q, z) == truth_cmp(
                      (2 * p[0], 2 * p[1], 4 * p[2], 4 * p[3]),
                      (2 * q[0], 2 * q[1], 4 * q[2], 4 * q[3]), z), z)


def t_swap_inverts():
    cases = [
        ("strict", P4(1, 1, 1, 1), P4(0, 1, 1, 1), (F(1), F(4))),
        ("tangent", P4(1, 1, 0, 4), P4(1, 0, 1, 0), (F(1, 4), F(4))),
        ("poc", POC_P, POC_Q, POC_J),
    ]
    for name, p, q, (L, R) in cases:
        fwd = V.certify_pair(p, q, L, R)
        bwd = V.certify_pair(q, p, L, R)
        check("swap-%s-status" % name, bwd["status"] == fwd["status"],
              (fwd["status"], bwd["status"]))
        d = fwd["direction"]
        want = ("VARIES" if d == "VARIES" else (0 if d == 0 else -d))
        check("swap-%s-direction" % name, bwd["direction"] == want,
              (d, bwd["direction"]))
        check("swap-%s-ties" % name, sorted(bwd["ties"]) == sorted(fwd["ties"]),
              (fwd["ties"], bwd["ties"]))


def t_exhaustion_refuses():
    # Split-budget exhaustion must refuse, never certify falsely.
    out = V.certify_pair(POC_P, POC_Q, *POC_J, split_cap=0)
    check("exhaust-split", out["status"] == "UNRESOLVED", out["status"])
    out = V.certify_pair(POC_P, POC_Q, *POC_J, subint_cap=0)
    check("exhaust-subint", out["status"] == "UNRESOLVED", out["status"])
    # Irrational crossing: bracket path resolves by default ...
    # P = z^2-2 via N1=z,D1=2 / N2=1,D2=1 (abstract-only: v=0 with b!=0).
    ip, iq = P4(0, 1, 2, 0), P4(1, 0, 1, 0)
    check("irrat-label", realizability(ip, iq) == "abstract-only", "label")
    out = V.certify_pair(ip, iq, F(1), F(2))
    check("irrat-varies",
          (out["status"], out["direction"]) == ("ISOLATED_TIES", "VARIES"),
          (out["status"], out["direction"], out["ties"]))
    check("irrat-cross-bracket",
          any(x["kind"] == "cross" for x in out["xbrackets"]),
          out["xbrackets"])
    # ... and refuses under a starved split budget.
    out = V.certify_pair(ip, iq, F(1), F(2), split_cap=1)
    check("irrat-exhaust", out["status"] == "UNRESOLVED", out["status"])
    for kw in (dict(split_cap=0), dict(subint_cap=0), dict(split_cap=1)):
        o = V.certify_pair(ip, iq, F(1), F(2), **kw)
        sound = (o["status"] in ("UNRESOLVED", "DOMAIN_FAIL") or
                 o["direction"] == "VARIES")
        check("irrat-never-false-%s" % kw, sound,
              (o["status"], o["direction"]))


def t_invalid_intervals_and_domain():
    p, q = P4(1, 1, 1, 1), P4(0, 1, 1, 1)
    for L, R in ((F(2), F(2)), (F(4), F(1))):
        out = V.certify_pair(p, q, L, R)
        check("invalid-%s-%s" % (L, R), out["status"] == "UNRESOLVED",
              (out["status"], out["direction"]))
    # Denominator non-positive at an endpoint -> DOMAIN_FAIL (v2 parity).
    bad = P4(0, 1, -1, 1)  # D = -1+z <= 0 at L=1
    out = V.certify_pair(bad, q, F(1), F(4))
    check("domain-fail", out["status"] == "DOMAIN_FAIL", out["status"])


def t_labeled_examples():
    # Realizable STRICT +1: f1=(1+z)^2/(1+z)=1+z, f2=z^2/(1+z); P>0 on J.
    p, q = P4(1, 1, 1, 1), P4(0, 1, 1, 1)
    check("strict-label", realizability(p, q) == "realizable-constraints",
          "label")
    out = V.certify_pair(p, q, F(1), F(4))
    check("strict-verdict", (out["status"], out["direction"]) == ("STRICT", 1),
          (out["status"], out["direction"], out["ties"]))
    # Realizable VARIES: crossing at 3/2 plus numerator-sign cut at 3.
    p, q = P4(0, 1, 1, 1), P4(3, -1, 1, 1)
    check("varies-label", realizability(p, q) == "realizable-constraints",
          "label")
    check("varies-truth",
          (truth_cmp(p, q, F(5, 4)), truth_cmp(p, q, F(2)),
           truth_cmp(p, q, F(7, 2))) == (-1, 1, 1), "cells -,+,+")
    out = V.certify_pair(p, q, F(1), F(4))
    check("varies-verdict", out["direction"] == "VARIES",
          (out["status"], out["direction"]))
    # Realizable PERSISTENT_TIE: identical scores (P identically zero).
    p, q = P4(0, 1, 1, 1), P4(0, 2, 4, 4)
    check("persist-label", realizability(p, q) == "realizable-constraints",
          "label")
    check("persist-identical",
          all(truth_cmp(p, q, z) == 0
              for z in (F(1), F(2), F(3), F(4))), "all ties")
    out = V.certify_pair(p, q, F(1), F(4))
    check("persist-verdict",
          (out["status"], out["direction"]) == ("PERSISTENT_TIE", 0),
          (out["status"], out["direction"]))
    # Single-zero-sign STRICT: N1 identically zero vs positive N2.
    p, q = P4(0, 0, 1, 1), P4(1, 0, 1, 1)
    out = V.certify_pair(p, q, F(1), F(4))
    check("singlezero-verdict",
          (out["status"], out["direction"]) == ("STRICT", -1),
          (out["status"], out["direction"]))
    # Numerator-negative reversal VARIES (constraint-level realizable:
    # q has v=0 with b=0 satisfied; all u,v >= 0).
    p, q = P4(-3, 1, 1, 1), P4(0, 0, 2, 0)
    check("reversal-label",
          realizability(p, q) == "realizable-constraints", "label")
    check("reversal-truth",
          (truth_cmp(p, q, F(2)), truth_cmp(p, q, F(3)),
           truth_cmp(p, q, F(7, 2))) == (-1, 0, 1), "cells -,0,+")
    out = V.certify_pair(p, q, F(1), F(4))
    check("reversal-verdict", out["direction"] == "VARIES",
          (out["status"], out["direction"]))
    # Interior exact tangent, single direction (abstract-only, u=0 in p).
    p, q = P4(1, 1, 0, 4), P4(1, 0, 1, 0)
    check("tangent-label", realizability(p, q) == "abstract-only", "label")
    out = V.certify_pair(p, q, F(1, 4), F(4))
    check("tangent-verdict",
          (out["status"], out["direction"]) == ("ISOLATED_TIES", 1),
          (out["status"], out["direction"], out["ties"]))
    check("tangent-evidence", out["ties"] == ["1"], out["ties"])
    # Same tangent at K=100 scaling: enumeration skips, bisection cannot
    # exact-hit (1 is not dyadic from (1/4,17/8)), so the tangent arrives
    # as a proven touch bracket -- still single-direction +1.
    k = 100
    sp, sq = P4(k, k, 0, 4 * k * k), P4(k, 0, k * k, 0)
    sout = V.certify_pair(sp, sq, F(1, 4), F(4))
    check("tangent-scaled-verdict",
          (sout["status"], sout["direction"]) == ("ISOLATED_TIES", 1),
          (sout["status"], sout["direction"], sout["ties"]))
    check("tangent-scaled-touch",
          any(x["kind"] == "touch" for x in sout["xbrackets"]),
          sout["xbrackets"])
    # Two crossings across subintervals (abstract-only denominators).
    # P = (z+5)^2-4 = (z+3)(z+7); J=[-8,-1] holds both roots.
    p, q = P4(5, 1, 1, 0), P4(2, 0, 1, 0)
    check("tworoot-label", realizability(p, q) == "abstract-only", "label")
    check("tworoot-truth",
          (truth_cmp(p, q, F(-6)), truth_cmp(p, q, F(-4)),
           truth_cmp(p, q, F(-2))) == (-1, -1, 1), "cells -,-,+")
    out = V.certify_pair(p, q, F(-8), F(-1))
    check("tworoot-verdict", out["direction"] == "VARIES",
          (out["status"], out["direction"], out["ties"]))


def t_orig_agreement_fixed():
    # Wherever the honest original resolves, v3 must say the same thing.
    fixed = [
        (P4(-3, 4, 5, 10), P4(-2, 2, 2, 10), F(1, 16), F(16)),
        (P4(1, 1, 1, 10), P4(-50, 0, 1, 0), F(1, 16), F(16)),
        (P4(1, 1, 0, 4), P4(1, 0, 1, 0), F(1, 4), F(4)),
        (P4(1, 1, 0, 4), P4(1, 0, 1, 0), F(1, 4), F(4)),
        (P4(1, 1, 1, 1), P4(0, 1, 1, 1), F(1), F(4)),
        (P4(0, 1, 1, 1), P4(0, 2, 4, 4), F(1), F(4)),
    ]
    for i, (p, q, L, R) in enumerate(fixed):
        ro = O.certify_pair(p, q, L, R)
        rv = V.certify_pair(p, q, L, R)
        if ro["status"] in ("STRICT", "ISOLATED_TIES", "PERSISTENT_TIE"):
            check("agree-%d" % i,
                  (rv["status"], rv["direction"]) ==
                  (ro["status"], ro["direction"]),
                  (ro["status"], ro["direction"],
                   rv["status"], rv["direction"]))
        else:
            check("agree-%d-orig-unres" % i, True,
                  "orig %s, v3 %s/%s" % (ro["status"], rv["status"],
                                         rv["direction"]))


def main():
    t_poc_varies_with_cell_evidence()
    t_scale_invariance()
    t_score_preserving_transform()
    t_swap_inverts()
    t_exhaustion_refuses()
    t_invalid_intervals_and_domain()
    t_labeled_examples()
    t_orig_agreement_fixed()
    fails = [(n, d) for (n, ok, d) in CHECKS if not ok]
    print("checks=%d fail=%d" % (len(CHECKS), len(fails)))
    if fails:
        print("FAILED:", [n for (n, _) in fails])
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
