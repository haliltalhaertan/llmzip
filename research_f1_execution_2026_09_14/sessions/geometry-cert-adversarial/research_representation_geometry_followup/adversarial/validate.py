# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Certificate validator (adversarial suite, own code).

validate_cert(case, cert) -> list of error strings (empty = sound).

Externally observable guarantees checked (exact cases):
  G1 interval directions agree with frozen independent truth; a stable
     +/-1 claim on a VARIES case is rejected; VARIES without both frozen
     signs is rejected.
  G2 every claimed exact tie is a genuine tie (independent truth == 0)
     and a genuine Q-root.
  G3 root/bracket coverage: every frozen interior tie-root is listed or
     bracket-contained; endpoint ties listed; no double coverage; VARIES
     needs crossing evidence (cross bracket or crossing exact tie) while a
     stable claim with crossing evidence is rejected.
  G4 VARIES (unstable) is never presented as stable; unknown stays unknown:
     non-resolving verdicts must not smuggle a +/-1 direction.
  G5 resolving verdicts on invalid-J / failed-domain inputs are rejected
     (robustness rules); degenerate-J resolving claims must match point truth.

Safety (soundness) vs completeness (usefulness) are separate bars; the
runner scores both. An always-UNRESOLVED target passes safety but fails
completeness; an always-STRICT target fails safety.
"""
from fractions import Fraction as F

import truth as T
import oracle as OC

KNOWN_STATUSES = {"STRICT", "ISOLATED_TIES", "PERSISTENT_TIE", "VARIES",
                  "UNRESOLVED", "DOMAIN_FAIL", "EMPTY", "INVERTED"}
RESOLVING = {"STRICT", "ISOLATED_TIES", "PERSISTENT_TIE", "VARIES"}
NON_RESOLVING = {"UNRESOLVED", "DOMAIN_FAIL", "EMPTY", "INVERTED"}


def _parse_tie(e):
    """Returns (kind, payload). kind in exact/cross/touch/persistent."""
    if not isinstance(e, str):
        return ("unparseable", e)
    for kind in ("cross(", "touch(", "persistent("):
        if e.startswith(kind) and e.endswith(")"):
            inner = e[len(kind):-1]
            parts = inner.split(",")
            if len(parts) != 2:
                return ("unparseable", e)
            try:
                return (kind[:-1], (F(parts[0]), F(parts[1])))
            except Exception:  # noqa: BLE001
                return ("unparseable", e)
    try:
        return ("exact", F(e))
    except Exception:  # noqa: BLE001
        return ("unparseable", e)


def _live_truth(p, q, z):
    try:
        return T.true_cmp(p, q, z)
    except T.DomainError:
        return None


def validate_cert(case, cert):
    errs = []
    o = case["oracle"]
    if not isinstance(cert, dict):
        return ["certificate is not a dict"]
    st = cert.get("status")
    if st not in KNOWN_STATUSES:
        return ["unknown status %r" % (st,)]
    ties = cert.get("ties")
    if not isinstance(ties, list):
        return ["ties is not a list"]
    d = cert.get("direction")

    if o.get("robustness") or o.get("domain") == "fail":
        return _validate_robustness(case, cert)
    return _validate_exact(case, cert)


def _validate_robustness(case, cert):
    errs = []
    o = case["oracle"]
    st = cert.get("status")
    d = cert.get("direction")
    ties = cert.get("ties")
    rob = o.get("robustness")
    if rob == "inverted-J":
        if st in RESOLVING:
            errs.append("inverted J certified as %s" % st)
        return errs
    if rob == "domain-fail":
        if st in RESOLVING:
            errs.append("failed-domain input certified as %s" % st)
        if d in (1, -1):
            errs.append("direction smuggled in domain-fail cert")
        return errs
    if rob == "degenerate-J":
        if st in NON_RESOLVING:
            if d in (1, -1):
                errs.append("direction smuggled in non-resolving cert")
            return errs
        z = F(case["J"][0])
        p = tuple(F(x) for x in case["p"])
        q = tuple(F(x) for x in case["q"])
        tv = _live_truth(p, q, z)
        if d == "VARIES":
            errs.append("VARIES on a single-point J")
        elif tv == 0:
            if not (d == 0 or st == "PERSISTENT_TIE"):
                errs.append("point is a tie but direction=%r" % (d,))
        elif tv in (1, -1):
            if d != tv:
                errs.append("direction %r contradicts point truth %r" % (d, tv))
        for e in ties:
            kind, pay = _parse_tie(e)
            if kind == "exact":
                if _live_truth(p, q, pay) != 0:
                    errs.append("claimed tie %s is not a tie" % e)
            elif kind in ("cross", "touch", "persistent"):
                errs.append("bracket %s on a single-point J" % e)
            else:
                errs.append("unparseable tie entry %r" % (e,))
        return errs
    return ["unknown robustness class %r" % (rob,)]


def _validate_exact(case, cert):
    errs = []
    o = case["oracle"]
    st = cert.get("status")
    d = cert.get("direction")
    ties = cert.get("ties")
    p = tuple(F(x) for x in case["p"])
    q = tuple(F(x) for x in case["q"])
    L, R = F(case["J"][0]), F(case["J"][1])
    izero = bool(o.get("identically_zero"))
    Q = [F(c) for c in o["Q"]] if not izero else [F(0)]

    if st in NON_RESOLVING:
        if d in (1, -1):
            errs.append("direction %r smuggled in non-resolving cert (%s)" % (d, st))
        return errs

    # --- resolving verdicts ---
    if d not in (1, -1, 0, "VARIES"):
        errs.append("resolving cert with bad direction %r" % (d,))
        return errs
    claim = "persistent" if (st == "PERSISTENT_TIE" or d == 0) else (
        "varies" if (st == "VARIES" or d == "VARIES") else "stable")

    parsed = [_parse_tie(e) for e in ties]
    for e, (kind, _) in zip(ties, parsed):
        if kind == "unparseable":
            errs.append("unparseable tie entry %r" % (e,))

    exacts_in, brackets = [], []
    for e, (kind, pay) in zip(ties, parsed):
        if kind == "exact":
            if _live_truth(p, q, pay) != 0:
                errs.append("claimed tie %s is not a genuine tie" % e)
                continue
            if not izero and T.peval(Q, pay) != 0:
                errs.append("claimed tie %s is not a Q-root" % e)
                continue
            if pay < L or pay > R:
                errs.append("claimed tie %s outside J" % e)
                continue
            if L < pay < R:
                exacts_in.append(pay)
        elif kind in ("cross", "touch"):
            lo, hi = pay
            if not (L <= lo < hi <= R):
                errs.append("bracket %s out of range" % e)
                continue
            if not izero:
                if T.peval(Q, lo) == 0 or T.peval(Q, hi) == 0:
                    errs.append("bracket %s has a root endpoint" % e)
                    continue
                try:
                    n = OC.sturm_open_count(Q, lo, hi)
                except OC.OracleIncomplete as ex:
                    errs.append("bracket %s uncountable: %s" % (e, ex))
                    continue
                if n != 1:
                    errs.append("bracket %s count != 1 (=%s)" % (e, n))
                    continue
            tlo, thi = _live_truth(p, q, lo), _live_truth(p, q, hi)
            if tlo == 0 or thi == 0:
                errs.append("bracket %s with zero-verdict endpoint" % e)
                continue
            if kind == "cross" and not (tlo != thi):
                errs.append("cross bracket %s without sign change" % e)
                continue
            if kind == "touch" and not (tlo == thi):
                errs.append("touch bracket %s without same signs" % e)
                continue
            brackets.append((kind, lo, hi))
        elif kind == "persistent":
            lo, hi = pay
            if not izero:
                errs.append("persistent bracket %s without identically-zero Q" % e)
                continue
            if not (L <= lo < hi <= R):
                errs.append("persistent bracket %s out of range" % e)
                continue
            brackets.append((kind, lo, hi))

    if izero:
        if claim != "persistent":
            errs.append("identically-zero Q certified as %s/%r, want PERSISTENT_TIE"
                        % (st, d))
        return errs
    if claim == "persistent":
        errs.append("nonzero Q certified PERSISTENT_TIE")
        return errs

    # Coverage G3: every frozen interior tie-root listed or bracket-contained.
    roots = [F(r) for r in o.get("exact_roots_in_range", [])]
    frozen_truth = {F(k): v for k, v in o["truth"].items()}
    tie_roots = [r for r in roots
                 if L < r < R and frozen_truth.get(r, _live_truth(p, q, r)) == 0]
    for r in tie_roots:
        if r in exacts_in:
            continue
        if any(lo < r < hi for (_, lo, hi) in brackets):
            continue
        errs.append("exact root %s unaccounted (omitted classification)" % r)
    # Endpoint ties must be listed exactly.
    for r in roots:
        if (r == L or r == R) and frozen_truth.get(r, _live_truth(p, q, r)) == 0:
            if r not in [pp for (k, pp) in parsed if k == "exact"]:
                errs.append("endpoint tie %s masked (not listed)" % r)
    # No double coverage: an interior exact tie inside a bracket.
    for e in exacts_in:
        if any(lo < e < hi for (_, lo, hi) in brackets):
            errs.append("exact tie %s double-covered by a bracket" % e)
    # Crossing evidence: an interior exact tie is a crossing iff frozen
    # verdicts on its two sides differ (side probes are exact: no other
    # critical point lies between consecutive crit neighbors).
    crit = sorted({F(s) for s in o.get("crit", [])} | {L, R})
    cross_ties = 0
    for e in exacts_in:
        left = [c for c in crit if c < e]
        right = [c for c in crit if c > e]
        if not left or not right:
            errs.append("exact tie %s has no crit neighbor" % e)
            continue
        a, b = max(left), min(right)
        if _live_truth(p, q, (a + e) / 2) != _live_truth(p, q, (e + b) / 2):
            cross_ties += 1
    cross_brackets = sum(1 for (k, _, _) in brackets if k == "cross")
    if claim == "varies" and cross_ties + cross_brackets < 1:
        errs.append("VARIES without crossing evidence (no cross bracket/tie)")
    if claim == "stable" and (cross_ties + cross_brackets > 0):
        errs.append("stable %r certified despite crossing evidence" % (d,))

    # Direction G1/G4.
    plus, minus = bool(o.get("plus")), bool(o.get("minus"))
    if claim == "stable":
        if plus and minus:
            errs.append("stable %r certified on VARIES case (false stabilization)" % (d,))
        elif d == 1 and not plus:
            errs.append("stable +1 with no +1 in frozen truth")
        elif d == -1 and not minus:
            errs.append("stable -1 with no -1 in frozen truth")
    elif claim == "varies":
        if not (plus and minus):
            errs.append("VARIES without two observed frozen signs")

    if st == "STRICT" and (ties or brackets):
        errs.append("STRICT with nonempty ties/brackets")
    if st == "ISOLATED_TIES" and not (ties or brackets):
        errs.append("ISOLATED_TIES with empty ties/brackets")
    return errs
