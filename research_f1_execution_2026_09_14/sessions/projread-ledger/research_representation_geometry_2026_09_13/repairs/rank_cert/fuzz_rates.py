# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""fuzz_rates.py — önce/sonra UNRESOLVED oranları + v2 sağlamlık çapraz denetimi.

Deterministik (seed sabit). İki ölçüm:
  1) Arşivin kendi çağrıları: S6+S8 içindeki 6 certify_pair çağrısı.
  2) Sistematik fuzz: N rastgele küçük-tamsayı çifti, J=[1/16,16].
Üç kip: orig, disc-only (yalnızca ayrıştırıcı), full v2.
Ayrıca: v2'nin orig-çözümlü davalarda orig ile çelişmemesi (uyuşma),
v2-UNRESOLVED => orig-UNRESOLVED (tekdüze), ve v2 belgelerinin
bağımsız yeniden-sayım ile doğrulanması denetlenir.
Çıktı: UNRESOLVED_RATE.json (stdout'a özet de basar).
"""
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fractions import Fraction as F
import verify_orig_copy as O
import certify_v2 as V

SEED = 20260913
N_FUZZ = 2000
J = (F(1, 16), F(16))
A_RANGE = list(range(-3, 4))
B_RANGE = list(range(-3, 4))
U_RANGE = list(range(0, 4))
V_RANGE = list(range(0, 4))


def artifact_cases():
    C1 = O.P4(-3, 4, 5, 10); C2 = O.P4(-2, 2, 2, 10)
    F1 = O.P4(1, 1, 1, 10); F2 = O.P4(-1, -1, 10, 1)
    E1 = O.P4(1, 1, 0, 4); E2 = O.P4(1, 0, 1, 0)
    Lo50 = O.P4(-50, 0, 1, 0)
    return [
        ("S6a:0vs2", F1, Lo50, J[0], J[1]),
        ("S6a:1vs2", F2, Lo50, J[0], J[1]),
        ("S6c:t3", E1, E2, F(1, 4), F(4)),
        ("S6c:t3b", E1, E2, F(1, 4), F(4)),
    ]


def lme_pair():
    import pickle
    import numpy as np
    d = pickle.load(open(O.LME_PKL, "rb"))
    C = np.asarray(d["C"], dtype=float)
    qC = np.asarray(d["qC"], dtype=float)
    n = C.shape[1]
    order = __import__("numpy").lexsort((__import__("numpy").arange(n), abs(qC)))
    G = order[:48]
    gR, rR = 56, 368
    comp = __import__("numpy").ones(n, dtype=bool)
    comp[G] = False
    grp = ~comp

    def dot_exact(ii, mask):
        return sum(F(float(qC[k])) * F(float(C[ii][k])) for k in range(n) if mask[k])

    def norm2_exact(ii, mask):
        return sum(F(float(C[ii][k])) * F(float(C[ii][k])) for k in range(n) if mask[k])

    pg = O.P4(dot_exact(gR, comp), dot_exact(gR, grp),
              norm2_exact(gR, comp), norm2_exact(gR, grp))
    pr = O.P4(dot_exact(rR, comp), dot_exact(rR, grp),
              norm2_exact(rR, comp), norm2_exact(rR, grp))
    return pg, pr


def validate_cert(p, q, L, R, cert):
    """v2 belgesinin bağımsız yeniden-doğrulaması. Hata dizgesi ya da None."""
    st = cert["status"]
    if st in ("DOMAIN_FAIL", "UNRESOLVED"):
        return None
    P = V.P_coeffs(p, q)
    for e in cert["ties"]:
        if e.startswith(("cross(", "touch(", "persistent(")):
            continue
        if V.cmp_rank(p, q, F(e)) != 0:
            return "exact tie %s not a tie" % e
    for x in cert.get("xbrackets", []):
        lo, hi = F(x["lo"]), F(x["hi"])
        if not (L <= lo < hi <= R):
            return "bracket out of range"
        if V.sturm_open_count(P, lo, hi) != 1:
            return "bracket count != 1"
        va, vb = V.cmp_rank(p, q, lo), V.cmp_rank(p, q, hi)
        if x["kind"] == "cross" and not (va != 0 and vb != 0 and va != vb):
            return "cross bracket without sign change"
        if x["kind"] == "touch" and not (va != 0 and va == vb):
            return "touch bracket without same signs"
    if st == "STRICT":
        d = cert["direction"]
        for k in range(17):
            z = L + (R - L) * k / 16
            if V.cmp_rank(p, q, z) != d:
                return "STRICT contradicted at sample %s" % z
    if st == "ISOLATED_TIES" and cert["direction"] == "VARIES":
        seen = set()
        for k in range(33):
            z = L + (R - L) * k / 32
            seen.add(V.cmp_rank(p, q, z))
        seen.discard(0)
        for x in cert.get("xbrackets", []):
            if x["kind"] == "cross":
                seen.add(V.cmp_rank(p, q, F(x["lo"])))
                seen.add(V.cmp_rank(p, q, F(x["hi"])))
        if len(seen) < 2:
            return "VARIES without two observed signs"
    return None


def run_case(p, q, L, R):
    ro = O.certify_pair(p, q, L, R)
    rd = V.certify_pair(p, q, L, R, isolate=False)
    rv = V.certify_pair(p, q, L, R, isolate=True)
    return ro, rd, rv


def main():
    t0 = time.time()
    pg, pr = lme_pair()
    cases = artifact_cases() + [("S8:cA", pg, pr, F(1, 16), F(1)),
                                ("S8:cB", pg, pr, F(1), F(16))]
    art = {"n": len(cases), "orig_unres": 0, "disc_unres": 0, "v2_unres": 0,
           "details": []}
    for name, p, q, L, R in cases:
        ro, rd, rv = run_case(p, q, L, R)
        for tag, r in (("orig", ro), ("disc", rd), ("v2", rv)):
            if r["status"] == "UNRESOLVED":
                art[tag + "_unres"] += 1
        art["details"].append({"case": name, "orig": ro["status"],
                               "disc": rd["status"], "v2": rv["status"],
                               "v2dir": rv["direction"]})
    rng = random.Random(SEED)
    fuzz = {"n": N_FUZZ, "domain_fail": 0, "orig_unres": 0, "disc_unres": 0,
            "v2_unres": 0, "agree_viol": 0, "mono_viol": 0, "valid_fail": 0,
            "recovered": 0, "examples": []}
    for i in range(N_FUZZ):
        p = O.P4(rng.choice(A_RANGE), rng.choice(B_RANGE),
                 rng.choice(U_RANGE), rng.choice(V_RANGE))
        q = O.P4(rng.choice(A_RANGE), rng.choice(B_RANGE),
                 rng.choice(U_RANGE), rng.choice(V_RANGE))
        ro, rd, rv = run_case(p, q, J[0], J[1])
        if ro["status"] == "DOMAIN_FAIL":
            fuzz["domain_fail"] += 1
            if not (rd["status"] == "DOMAIN_FAIL" and rv["status"] == "DOMAIN_FAIL"):
                fuzz["mono_viol"] += 1
            continue
        if ro["status"] == "UNRESOLVED":
            fuzz["orig_unres"] += 1
        if rd["status"] == "UNRESOLVED":
            fuzz["disc_unres"] += 1
        if rv["status"] == "UNRESOLVED":
            fuzz["v2_unres"] += 1
        else:
            if ro["status"] == "UNRESOLVED":
                fuzz["recovered"] += 1
                if len(fuzz["examples"]) < 5:
                    fuzz["examples"].append(
                        {"p": [str(x) for x in p], "q": [str(x) for x in q],
                         "v2": rv["status"], "dir": rv["direction"],
                         "ties": rv["ties"][:4]})
        if ro["status"] in ("STRICT", "ISOLATED_TIES", "PERSISTENT_TIE"):
            if not (rv["status"] == ro["status"] and
                    rv["direction"] == ro["direction"]):
                fuzz["agree_viol"] += 1
        if rv["status"] == "UNRESOLVED" and ro["status"] != "UNRESOLVED":
            fuzz["mono_viol"] += 1
        err = validate_cert(p, q, J[0], J[1], rv)
        if err is not None:
            fuzz["valid_fail"] += 1
            if len(fuzz["examples"]) < 8:
                fuzz["examples"].append({"VALIDATION_FAILURE": err})
    eff = N_FUZZ - fuzz["domain_fail"]
    out = {"labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                      "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
           "artifact_cases": art,
           "fuzz": dict(fuzz, seed=SEED, J=["1/16", "16"],
                        ranges={"a": A_RANGE, "b": B_RANGE, "u": U_RANGE,
                                "v": V_RANGE},
                        effective_n=eff,
                        rates={"orig": [fuzz["orig_unres"], eff],
                                "disc_only": [fuzz["disc_unres"], eff],
                                "v2": [fuzz["v2_unres"], eff]}),
           "recovery": {"artifact": art["orig_unres"] - art["v2_unres"],
                        "fuzz": fuzz["recovered"],
                        "total": (art["orig_unres"] - art["v2_unres"] +
                                  fuzz["recovered"])},
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(HERE, "UNRESOLVED_RATE.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("artifact: orig %d/%d UNRES, disc %d, v2 %d" %
          (art["orig_unres"], art["n"], art["disc_unres"], art["v2_unres"]))
    print("fuzz: n=%d eff=%d fails=%d | orig %d disc %d v2 %d | recovered %d" %
          (N_FUZZ, eff, fuzz["domain_fail"], fuzz["orig_unres"],
           fuzz["disc_unres"], fuzz["v2_unres"], fuzz["recovered"]))
    print("agree_viol=%d mono_viol=%d valid_fail=%d elapsed=%.1fs" %
          (fuzz["agree_viol"], fuzz["mono_viol"], fuzz["valid_fail"],
           time.time() - t0))


if __name__ == "__main__":
    main()
