"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Coordinator audit v2 - corrected for the workers' ACTUAL schemas.

v1 raised 3 failures; all three were defects in v1 itself, recorded honestly:
  v1-bug-1: anchored FULL/sym to 46.6809 (the EXPECTED-hit value) while the worker reported
            REALIZED hit 46.5248. Baseline REPORT.md lists sign96 realized .4652 / expected .4668.
            Worker's exp_hit10 = 46.6809 exactly. Worker correct, anchor wrong.
  v1-bug-2: generic "monotonic in M" walker treated `gold_size_dist` (a histogram over gold set
            sizes) as an M-curve. False positive.
  v1-bug-3: assumed flat per-arm rows; firststage uses nested {pool_metrics:{ARM:{M:...}}, own:{}}.
This file does the real work: recompute EVERYTHING from the workers' stored raw candidate lists.
"""
import json, os, sys, hashlib, math
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IDEAS = os.path.join(HERE, "..", "ideas_r1")
MS = [10, 20, 50, 100, 200, 500]
RRF_K = 60
fail, ok, notes = [], [], []


def chk(c, m):
    (ok if c else fail).append(m)
    print(("  OK   " if c else "  FAIL ") + m)


def pct(x):
    return 100.0 * float(np.mean(x))


def audit_firststage():
    print("\n=== FIRSTSTAGE: recompute from stored top-500 candidate lists ===")
    rows = [json.loads(l) for l in open(os.path.join(IDEAS, "firststage", "per_query.jsonl"),
                                        encoding="utf-8") if l.strip()]
    chk(len(rows) == 705 and len({r["qid"] for r in rows}) == 705, f"coverage {len(rows)} rows / unique qids")

    # 1. recompute pool hit/recall/ceiling from raw lists
    mine = defaultdict(lambda: defaultdict(list))
    theirs = defaultdict(lambda: defaultdict(list))
    maxdev = 0.0
    for r in rows:
        g = set(int(x) for x in r["gold"])
        for arm, key in (("CODE", "code_top500"), ("BM25", "bm25_top500"), ("RRF", "rrf_top500")):
            lst = [int(x) for x in r[key]]
            if len(set(lst)) != len(lst):
                fail.append(f"{r['qid']} {arm}: duplicate ids in candidate list")
            for M in MS:
                found = len(g.intersection(lst[:M]))
                mine[arm][f"hit{M}"].append(1.0 if found else 0.0)
                mine[arm][f"rec{M}"].append(found / len(g))
                mine[arm][f"ceil{M}"].append(min(3, found) / len(g))
                pm = r["pool_metrics"][arm][str(M)]
                theirs[arm][f"hit{M}"].append(pm["hit"])
                theirs[arm][f"rec{M}"].append(pm["recall"])
                theirs[arm][f"ceil{M}"].append(pm["ceiling"])
    for arm in ("CODE", "BM25", "RRF"):
        for k in mine[arm]:
            d = abs(pct(mine[arm][k]) - pct(theirs[arm][k]))
            maxdev = max(maxdev, d)
    chk(maxdev < 1e-9, f"recomputed pool metrics match worker's to {maxdev:.2e} pp (all arms/M)")

    # 2. independently REBUILD RRF from the CODE and BM25 orderings
    bad_rrf = 0
    for r in rows:
        code = [int(x) for x in r["code_top500"]]
        bm = [int(x) for x in r["bm25_top500"]]
        rc = {d: i + 1 for i, d in enumerate(code)}
        rb = {d: i + 1 for i, d in enumerate(bm)}
        sc = {}
        for d in set(code) | set(bm):
            sc[d] = (1.0 / (RRF_K + rc[d]) if d in rc else 0.0) + (1.0 / (RRF_K + rb[d]) if d in rb else 0.0)
        aid = r["archive_id"]
        order = sorted(sc, key=lambda d: (-sc[d],
                       hashlib.sha256(f"top10-r1|{aid}|{d}".encode()).hexdigest(), d))
        if order[:10] != [int(x) for x in r["rrf_top500"]][:10]:
            bad_rrf += 1
    chk(bad_rrf == 0, f"independently rebuilt RRF(k=60) top10: {bad_rrf}/705 mismatches")

    # 3. anchors + headline table
    print("\n  pool quality recomputed by coordinator (%):")
    print(f"  {'arm':6} " + " ".join(f"{'H@'+str(m):>8}" for m in MS) + "   |" +
          " ".join(f"{'ceil'+str(m):>8}" for m in MS))
    res = {}
    for arm in ("CODE", "BM25", "RRF"):
        h = [pct(mine[arm][f"hit{m}"]) for m in MS]
        c = [pct(mine[arm][f"ceil{m}"]) for m in MS]
        res[arm] = {"hit": dict(zip(map(str, MS), h)), "ceiling": dict(zip(map(str, MS), c))}
        print(f"  {arm:6} " + " ".join(f"{v:8.2f}" for v in h) + "   |" + " ".join(f"{v:8.2f}" for v in c))
        chk(all(h[i] <= h[i+1] + 1e-9 for i in range(len(h)-1)), f"{arm} pool-hit monotonic in M")
        chk(all(c[i] <= c[i+1] + 1e-9 for i in range(len(c)-1)), f"{arm} ceiling monotonic in M")

    chk(abs(res["CODE"]["hit"]["10"] - 49.64539007092199) < 0.01,
        f"CODE pool-Hit@10 {res['CODE']['hit']['10']:.4f} == qscale anchor 49.6454")
    chk(abs(res["BM25"]["hit"]["10"] - 54.18439716312057) < 0.01,
        f"BM25 pool-Hit@10 {res['BM25']['hit']['10']:.4f} == audited lexical anchor 54.1844")

    # 4. ceiling must be >= the arm's own achieved FR@3
    own_fr3 = {a: pct([r["own"][a]["fr3"] for r in rows]) for a in ("CODE", "BM25", "RRF")}
    for a in ("CODE", "BM25", "RRF"):
        chk(res[a]["ceiling"]["10"] >= own_fr3[a] - 1e-9,
            f"{a} ceiling@10 {res[a]['ceiling']['10']:.2f} >= own FR@3 {own_fr3[a]:.2f}")

    # 5. oracle-union bound is a hard upper limit on any fusion
    orc = {}
    for M in (10, 100):
        v = []
        for r in rows:
            g = set(int(x) for x in r["gold"])
            a = g.intersection([int(x) for x in r["code_top500"]][:M])
            b = g.intersection([int(x) for x in r["bm25_top500"]][:M])
            v.append(1.0 if (a or b) else 0.0)
        orc[M] = pct(v)
        chk(res["RRF"]["hit"][str(M)] <= orc[M] + 1e-9,
            f"RRF pool-Hit@{M} {res['RRF']['hit'][str(M)]:.2f} <= oracle-union bound {orc[M]:.2f}")
    return {"pool": res, "own_fr3": own_fr3, "oracle_union": orc, "rrf_rebuild_mismatches": bad_rrf}


def audit_ablation():
    print("\n=== ABLATION: anchors on the correct metric + per-query recompute ===")
    p = os.path.join(IDEAS, "ablation", "per_query.jsonl")
    if not os.path.exists(p):
        notes.append("ablation per_query.jsonl absent (worker may still be running)"); return None
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    g = defaultdict(list)
    for r in rows:
        g[(r["arm"], r["scorer"])].append(r)
    arms = sorted({a for a, _ in g})
    print(f"  arms present: {arms}")
    fs = g[("FULL", "sym")]
    chk(abs(pct([r["exp_hit10"] for r in fs]) - 46.6809) < 0.01,
        f"FULL/sym EXPECTED-Hit@10 {pct([r['exp_hit10'] for r in fs]):.4f} == anchor 46.6809")
    chk(abs(pct([r["hit10"] for r in fs]) - 46.5248) < 0.01,
        f"FULL/sym REALIZED-Hit@10 {pct([r['hit10'] for r in fs]):.4f} == baseline realized 46.5248")
    fq = g[("FULL", "qscale")]
    chk(abs(pct([r["hit10"] for r in fq]) - 49.6454) < 0.01,
        f"FULL/qscale Hit@10 {pct([r['hit10'] for r in fq]):.4f} == anchor 49.6454")
    # recompute hit/fr3 from stored ids
    bad = 0
    for r in rows:
        gold = set(int(x) for x in r["gold"]); top = [int(x) for x in r["top10"]]
        if (1.0 if gold.intersection(top) else 0.0) != r["hit10"]:
            bad += 1
        if abs(len(gold.intersection(top[:3])) / len(gold) - r["fr3"]) > 1e-9:
            bad += 1
    chk(bad == 0, f"per-query hit10/fr3 recomputed from stored ids: {bad} mismatches")
    out = {}
    print(f"\n  {'arm':10} {'sym H@10':>9} {'qs H@10':>9} {'qs FR@3':>9}  (vs FULL, pp)")
    base = {sc: pct([r["hit10"] for r in g[("FULL", sc)]]) for sc in ("sym", "qscale")}
    basef = pct([r["fr3"] for r in g[("FULL", "qscale")]])
    for a in arms:
        if ("FULL", "sym") not in g or (a, "sym") not in g:
            continue
        s = pct([r["hit10"] for r in g[(a, "sym")]])
        q = pct([r["hit10"] for r in g[(a, "qscale")]])
        f3 = pct([r["fr3"] for r in g[(a, "qscale")]])
        out[a] = {"sym_hit10": s, "qscale_hit10": q, "qscale_fr3": f3}
        print(f"  {a:10} {s:9.2f} {q:9.2f} {f3:9.2f}   "
              f"({s-base['sym']:+.2f} / {q-base['qscale']:+.2f} / {f3-basef:+.2f})")
    return out


def main():
    fsres = audit_firststage()
    abres = audit_ablation()
    print("\n" + "=" * 62)
    print(f"PASS {len(ok)} | FAIL {len(fail)}")
    for f in fail:
        print("  FAIL:", f)
    for n in notes:
        print("  NOTE:", n)
    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                          "DISCLOSE-BEFORE-USE"],
               "v1_bugs_were_in_the_audit_not_the_workers": [
                   "anchored sym to expected-hit while worker reported realized",
                   "treated gold_size_dist histogram as an M-curve",
                   "assumed flat schema; firststage is nested"],
               "firststage": fsres, "ablation": abres,
               "passed": ok, "failed": fail, "notes": notes,
               "verdict": "ACCEPT" if not fail else "REJECT"},
              open(os.path.join(HERE, "ideas_audit_v2.json"), "w"), indent=2)
    print("verdict:", "ACCEPT" if not fail else "REJECT")


if __name__ == "__main__":
    main()
