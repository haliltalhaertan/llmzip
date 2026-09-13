"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
fuzz_v3.py -- bounded SYNTHETIC fuzz for certify_v3.py + cert_validator_v3.py.

Task4F1 seal: no corpus, no queries, no gold/evidence, no LME cache, no
recall/ranking-accuracy/benchmark, no embeddings, no refit. Only synthetic
small-integer (a,b,u,v) pairs with exact Fraction arithmetic, exactly as
the severe-loading corner of the archived fuzz (same seed family, same J,
same ranges) but WITHOUT the archive-derived artifact cases.

Per case, soundness gates (all must hold; exit nonzero otherwise):
  (a) the independent validator accepts every v3 verdict that claims
      something (STRICT / ISOLATED_TIES / PERSISTENT_TIE);
  (b) whenever the honest original AND v3 both resolve, they agree;
  (c) no counter-sign sample among 65 uniform probes for single-direction
      certs (falsification witness; the proof is the validator, not this);
  (d) VARIES certs show both nonzero signs among probes+bracket endpoints.
Measured (secondary to soundness, exit-zero regardless): unresolved rates,
recovered count, mono direction (v3 UNRESOLVED => orig UNRESOLVED).

Run: PYTHONDONTWRITEBYTECODE=1 python3 -B fuzz_v3.py  (writes
UNRESOLVED_RATE_V3.json next to itself; prints a summary receipt)
"""
import json
import os
import random
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ARCHIVED = os.path.normpath(os.path.join(
    HERE, "..", "..", "research_representation_geometry_2026_09_13",
    "repairs", "rank_cert"))
sys.path.insert(0, ARCHIVED)

import certify_v3 as V3
import verify_orig_copy as O
from cert_validator_v3 import validate_cert_v3

SEED = 20260914
N_FUZZ = 2000
J = (F(1, 16), F(16))
A_RANGE = list(range(-3, 4))
B_RANGE = list(range(-3, 4))
U_RANGE = list(range(0, 4))
V_RANGE = list(range(0, 4))
RESOLVED = ("STRICT", "ISOLATED_TIES", "PERSISTENT_TIE")


def probes(p, q, L, R, n=65):
    out = []
    for k in range(n):
        z = L + (R - L) * k / (n - 1)
        try:
            out.append((z, O.cmp_rank(p, q, z)))
        except O.DomainError:
            out.append((z, None))
    return out


def main():
    t0 = time.time()
    rng = random.Random(SEED)
    fz = {"n": N_FUZZ, "domain_fail": 0, "orig_unres": 0, "v3_unres": 0,
          "agree_viol": 0, "mono_viol": 0, "valid_fail": 0,
          "countersign_fail": 0, "varies_witness_fail": 0,
          "tie_surprise": 0, "recovered": 0, "examples": []}
    for i in range(N_FUZZ):
        p = O.P4(rng.choice(A_RANGE), rng.choice(B_RANGE),
                 rng.choice(U_RANGE), rng.choice(V_RANGE))
        q = O.P4(rng.choice(A_RANGE), rng.choice(B_RANGE),
                 rng.choice(U_RANGE), rng.choice(V_RANGE))
        ro = O.certify_pair(p, q, J[0], J[1])
        rv = V3.certify_pair(p, q, J[0], J[1])
        if ro["status"] == "DOMAIN_FAIL":
            fz["domain_fail"] += 1
            if rv["status"] != "DOMAIN_FAIL":
                fz["mono_viol"] += 1
            continue
        if ro["status"] == "UNRESOLVED":
            fz["orig_unres"] += 1
        if rv["status"] == "UNRESOLVED":
            fz["v3_unres"] += 1
        else:
            if ro["status"] == "UNRESOLVED":
                fz["recovered"] += 1
                if len(fz["examples"]) < 5:
                    fz["examples"].append(
                        {"p": [str(x) for x in p], "q": [str(x) for x in q],
                         "v3": rv["status"], "dir": rv["direction"],
                         "ties": rv["ties"][:4]})
            err = validate_cert_v3(p, q, J[0], J[1], rv)
            if err is not None:
                fz["valid_fail"] += 1
                if len(fz["examples"]) < 10:
                    fz["examples"].append(
                        {"VALIDATION_FAILURE": err,
                         "p": [str(x) for x in p],
                         "q": [str(x) for x in q],
                         "v3": rv["status"], "dir": rv["direction"]})
        if ro["status"] in RESOLVED and rv["status"] in RESOLVED:
            if not (rv["status"] == ro["status"] and
                    rv["direction"] == ro["direction"]):
                fz["agree_viol"] += 1
        if rv["status"] == "UNRESOLVED" and ro["status"] != "UNRESOLVED":
            fz["mono_viol"] += 1
        if rv["status"] in RESOLVED:
            ps = probes(p, q, J[0], J[1])
            vals = set(v for (_, v) in ps)
            if rv["direction"] in (1, -1):
                if -rv["direction"] in vals:
                    fz["countersign_fail"] += 1
                for (z, v) in ps:
                    if v == 0 and str(z) not in rv["ties"]:
                        inside = any(
                            F(x["lo"]) < z < F(x["hi"])
                            for x in rv.get("xbrackets", []))
                        if not inside:
                            fz["tie_surprise"] += 1
            elif rv["direction"] == "VARIES":
                seen = set(v for (_, v) in ps if v is not None)
                for x in rv.get("xbrackets", []):
                    try:
                        seen.add(O.cmp_rank(p, q, F(x["lo"])))
                        seen.add(O.cmp_rank(p, q, F(x["hi"])))
                    except O.DomainError:
                        pass
                seen.discard(0)
                if len(seen) < 2:
                    fz["varies_witness_fail"] += 1
    eff = N_FUZZ - fz["domain_fail"]
    out = {"labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                      "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
           "seed": SEED, "J": ["1/16", "16"],
           "ranges": {"a": A_RANGE, "b": B_RANGE, "u": U_RANGE,
                      "v": V_RANGE},
           "fuzz": dict(fz, effective_n=eff,
                        rates={"orig": [fz["orig_unres"], eff],
                               "v3": [fz["v3_unres"], eff]}),
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(HERE, "UNRESOLVED_RATE_V3.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("fuzz: n=%d eff=%d fails=%d | orig %d v3 %d | recovered %d" %
          (N_FUZZ, eff, fz["domain_fail"], fz["orig_unres"],
           fz["v3_unres"], fz["recovered"]))
    print("agree_viol=%d mono_viol=%d valid_fail=%d countersign_fail=%d "
          "varies_witness_fail=%d tie_surprise=%d elapsed=%.1fs" %
          (fz["agree_viol"], fz["mono_viol"], fz["valid_fail"],
           fz["countersign_fail"], fz["varies_witness_fail"],
           fz["tie_surprise"], time.time() - t0))
    sound = (fz["agree_viol"] == 0 and fz["valid_fail"] == 0 and
             fz["countersign_fail"] == 0 and fz["varies_witness_fail"] == 0)
    print("SOUNDNESS: %s" % ("HOLD" if sound else "VIOLATED"))
    return 0 if sound else 1


if __name__ == "__main__":
    sys.exit(main())
