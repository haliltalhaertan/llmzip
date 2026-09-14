#!/usr/bin/env python3
"""Independent checker for the greedy-allocation pass (stdlib only).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reads results.json, re-derives every claimed P_err from the stored model spec
using its OWN implementation (gap-law convolution over Fractions; no import
from verify.py), re-simulates greedy, and re-checks the S-part MSE numbers.
Then validates a deliberately BROKEN table and requires rejection.
Fail-closed: prints FAIL + exit 1 on any mismatch.
"""
from fractions import Fraction as F
from itertools import product
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def parse(s):
    return F(s)


def pmf_from(spec):
    return [(parse(v), parse(p)) for (v, p) in spec]


def decode_levels(pmf, bits, t):
    if bits == 0:
        return {v: F(0) for (v, _) in pmf}
    if bits == 1:
        up = [(v, p) for (v, p) in pmf if v > 0]
        dn = [(v, p) for (v, p) in pmf if v < 0]
        mu = sum(v * p for (v, p) in up) / sum(p for (_, p) in up)
        md = sum(v * p for (v, p) in up) and None
        md = sum(v * p for (v, p) in dn) / sum(p for (_, p) in dn)
        return {v: (mu if v > 0 else (md if v < 0 else F(0))) for (v, _) in pmf}
    region = {}
    for (v, _) in pmf:
        if v >= t:
            region[v] = 'hp'
        elif v > 0:
            region[v] = 'lp'
        elif v > -t:
            region[v] = 'ln'
        else:
            region[v] = 'hn'
    acc = {}
    for (v, p) in pmf:
        k = region[v]
        acc.setdefault(k, [F(0), F(0)])
        acc[k][0] += v * p
        acc[k][1] += p
    avg = {k: (n / d if d else F(0)) for k, (n, d) in acc.items()}
    return {v: avg[region[v]] for (v, _) in pmf}


def p_err_convolution(pmfs, q, alloc, t):
    law = {(F(0), F(0)): F(1)}
    for j, (pmf, b) in enumerate(zip(pmfs, alloc)):
        lv = decode_levels(pmf, b, t)
        gj = {}
        for (a, pa) in pmf:
            for (c, pc) in pmf:
                k = (q[j] * (a - c), q[j] * (lv[a] - lv[c]))
                gj[k] = gj.get(k, F(0)) + pa * pc
        nxt = {}
        for (M, Mh), m in law.items():
            for (d, dh), md in gj.items():
                k = (M + d, Mh + dh)
                nxt[k] = nxt.get(k, F(0)) + m * md
        law = nxt
    num = F(0)
    den = F(0)
    for (M, Mh), m in law.items():
        if M == 0:
            continue
        den += m
        if Mh == 0:
            num += m / 2
        elif (Mh > 0) != (M > 0):
            num += m
    return num, den, num / den


def mse_of(pmf, bits, t):
    lv = decode_levels(pmf, bits, t)
    return sum(p * (v - lv[v]) ** 2 for (v, p) in pmf)


fails = []


def check(name, ok, detail):
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)
    if not ok:
        fails.append(name)


def main():
    with open(os.path.join(HERE, "results.json")) as f:
        res = json.load(f)
    spec = res["model_spec"]
    t = parse(spec["threshold"])
    pmfs = [pmf_from(s) for s in spec["supports"]]
    q = [parse(x) for x in spec["query"]]
    allocs = res["main_instance"]["allocs"]
    for a_str, entry in allocs.items():
        a = tuple(int(x) for x in a_str.strip("()").split(","))
        n, d, v = p_err_convolution(pmfs, q, a, t)
        ok = (str(n) == entry["P_num"] and str(d) == entry["P_den"]
              and str(v) == entry["P_err"])
        check("checker_alloc_" + a_str.replace(" ", ""), ok,
              "recomputed %s/%s=%s" % (n, d, v))
    # greedy re-simulation from recomputed values
    val = {}
    nodes = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 2, 0),
             (1, 1, 0), (0, 1, 1), (1, 1, 1)]
    for a in nodes:
        val[a] = p_err_convolution(pmfs, q, a, t)[2]
    mv0 = sorted([(val[(0, 0, 0)] - val[(1, 0, 0)], 0),
                  (val[(0, 0, 0)] - val[(0, 1, 0)], 1),
                  (val[(0, 0, 0)] - val[(0, 0, 1)], 2)], key=lambda x: -x[0])
    check("checker_greedy_step0", mv0[0][1] == 1 and mv0[0][0] > mv0[1][0],
          "step0 picks C2 strictly, MV=%s" % mv0[0][0])
    mv1 = sorted([(val[(0, 1, 0)] - val[(1, 1, 0)], 0),
                  (val[(0, 1, 0)] - val[(0, 2, 0)], 1),
                  (val[(0, 1, 0)] - val[(0, 1, 1)], 2)], key=lambda x: -x[0])
    check("checker_greedy_step1", mv1[0][1] == 2 and mv1[0][0] > mv1[1][0],
          "step1 picks C3 strictly, MV=%s" % mv1[0][0])
    # S-part MSE spot re-derivation
    q4 = pmf_from(spec["quat_support"])
    sp = pmf_from(spec["supports"][0])
    check("checker_quat_mse", [mse_of(q4, b, t) for b in (0, 1, 2)] ==
          [F(5), F(1), F(0)], "quat e=(5,1,0)")
    check("checker_sparse_mse", [mse_of(sp, b, t) for b in (0, 1, 2)] ==
          [F(109, 10), F(729, 100), F(0)], "sparse e=(109/10,729/100,0)")
    # broken variant must be rejected
    bad = dict(allocs)
    bad["(2, 1, 0)"] = {"P_num": "21", "P_den": "359",
                        "P_err": "21/359", "P_float": 0.0}
    n, d, v = p_err_convolution(pmfs, q, (2, 1, 0), t)
    rejected = not (bad["(2, 1, 0)"]["P_num"] == str(n)
                    and bad["(2, 1, 0)"]["P_den"] == str(d))
    check("checker_broken_variant_rejected", rejected,
          "tampered P(2,1,0)=21/359 != true %s/%s" % (n, d))
    if fails:
        print("CHECKER FAIL:", fails)
        sys.exit(1)
    print("CHECKER ALL PASS")


if __name__ == "__main__":
    main()
