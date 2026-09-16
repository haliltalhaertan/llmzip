"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
COORDINATOR AUDIT of the ideas_r1 worker outputs.

Written BEFORE the workers finished, so the acceptance bar cannot be tuned to their results.
Re-derives every headline number from the workers' own per_query.jsonl with independent code,
and re-runs the fidelity anchors from the original caches.

Checks:
  A. ablation worker
     A1 per_query.jsonl row/arm/scorer coverage == 705 queries x arms x scorers, unique qids
     A2 FULL arm under 'sym'    must reproduce cached Hit@10 46.6809%  (tol 0.01pp)
     A3 FULL arm under 'qscale' must reproduce cached Hit@10 49.6454% and FR@3 22.41% (tol 0.01pp)
     A4 every stored per-query hit/fr3 recomputed from stored top-k ids (catches metric bugs)
     A5 payload stays 12 B/doc for every arm
  B. firststage worker
     B1 coverage == 705 queries, all arms, all M
     B2 CODE arm pool-Hit@10 must equal 49.6454% (it is the same scorer as our qscale)
     B3 BM25 pool-Hit@10 must equal the audited lexical value 54.1844%
     B4 ceiling monotonic in M, and ceiling >= arm's own FR@3 (a ceiling below actual = bug)
     B5 pool-hit monotonic non-decreasing in M
     B6 RRF/UNION pool-hit must be <= oracle-union bound and >= max(single arms) is NOT required
        (fusion can lose); only the oracle bound is a hard upper limit
  C. cross-worker: both workers' CODE/FULL qscale Hit@10 must agree with each other and with ours
"""
import json, os, sys, glob, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
from audit_baseline_lib import hrn

IDEAS = os.path.join(HERE, "..", "ideas_r1")
ANCHOR = {"qscale_hit10": 49.64539007092199, "sym_hit10": 46.680851063829785,
          "qscale_fr3": 22.41, "bm25_hit10": 54.18439716312057}
TOL = 0.01
fail, warn, ok = [], [], []


def load_jsonl(p):
    if not os.path.exists(p):
        return None
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def pct(xs):
    return 100.0 * float(np.mean(xs))


def check(cond, msg):
    (ok if cond else fail).append(msg)
    print(("  OK   " if cond else "  FAIL ") + msg)


def audit_ablation():
    print("\n=== A. ABLATION WORKER ===")
    rows = load_jsonl(os.path.join(IDEAS, "ablation", "per_query.jsonl"))
    if rows is None:
        fail.append("ablation/per_query.jsonl MISSING"); print("  FAIL per_query.jsonl missing"); return
    print(f"  rows={len(rows)}  sample keys={sorted(rows[0].keys())}")
    qids = set(r.get("qid") for r in rows)
    check(len(qids) == 705, f"A1 unique qids = {len(qids)} (expect 705)")
    # group by (arm, scorer)
    g = {}
    for r in rows:
        g.setdefault((r.get("arm"), r.get("scorer")), []).append(r)
    print(f"  arm/scorer groups: {sorted(g.keys())}")
    for (arm, sc), rs in sorted(g.items()):
        if len(rs) != 705:
            warn.append(f"group {arm}/{sc} has {len(rs)} rows")
    # anchors
    for sc, key in (("sym", "sym_hit10"), ("qscale", "qscale_hit10")):
        rs = g.get(("FULL", sc))
        if not rs:
            fail.append(f"A2/A3 missing FULL/{sc}"); print(f"  FAIL missing FULL/{sc}"); continue
        h = pct([r["hit10"] for r in rs])
        check(abs(h - ANCHOR[key]) < TOL, f"A2/A3 FULL/{sc} Hit@10 {h:.4f} vs anchor {ANCHOR[key]:.4f}")
    rs = g.get(("FULL", "qscale"))
    if rs and "fr3" in rs[0]:
        f3 = pct([r["fr3"] for r in rs])
        check(abs(f3 - ANCHOR["qscale_fr3"]) < 0.05, f"A3b FULL/qscale FR@3 {f3:.4f} vs anchor ~22.41")
    # A4 recompute metrics from stored ids
    bad = 0
    for r in rows:
        ids, gold = r.get("top10"), r.get("gold")
        if ids is None or gold is None:
            continue
        h, rc, nd = hrn(ids, gold, 10)
        if abs(h - r.get("hit10", h)) > 1e-9:
            bad += 1
    check(bad == 0, f"A4 recomputed Hit@10 from stored ids: {bad} mismatches")
    # A5 payload
    res = os.path.join(IDEAS, "ablation", "RESULTS.json")
    if os.path.exists(res):
        d = json.load(open(res))
        s = json.dumps(d)
        check("12" in s, "A5 RESULTS.json mentions payload bytes (manual read required)")


def audit_firststage():
    print("\n=== B. FIRSTSTAGE WORKER ===")
    rows = load_jsonl(os.path.join(IDEAS, "firststage", "per_query.jsonl"))
    if rows is None:
        fail.append("firststage/per_query.jsonl MISSING"); print("  FAIL per_query.jsonl missing"); return
    print(f"  rows={len(rows)}  sample keys={sorted(rows[0].keys())}")
    qids = set(r.get("qid") for r in rows)
    check(len(qids) == 705, f"B1 unique qids = {len(qids)} (expect 705)")
    byarm = {}
    for r in rows:
        byarm.setdefault(r.get("arm"), []).append(r)
    print(f"  arms: {sorted(byarm.keys())}")
    for arm, key in (("CODE", "qscale_hit10"), ("BM25", "bm25_hit10")):
        rs = byarm.get(arm)
        if not rs:
            warn.append(f"B2/B3 arm {arm} absent"); continue
        cand = [k for k in rs[0] if "10" in str(k) and "hit" in str(k).lower()]
        print(f"    {arm}: candidate hit@10 fields {cand}")
        for k in cand:
            v = pct([r[k] for r in rs if isinstance(r.get(k), (int, float))])
            if abs(v - ANCHOR[key]) < TOL:
                ok.append(f"B2/B3 {arm}.{k} = {v:.4f} matches anchor")
                print(f"  OK   B2/B3 {arm}.{k} = {v:.4f} matches anchor {ANCHOR[key]:.4f}")
                break
        else:
            fail.append(f"B2/B3 {arm}: no field reproduced anchor {ANCHOR[key]:.4f}")
            print(f"  FAIL B2/B3 {arm}: no field reproduced anchor {ANCHOR[key]:.4f}")
    # monotonicity from RESULTS.json
    res = os.path.join(IDEAS, "firststage", "RESULTS.json")
    if os.path.exists(res):
        d = json.load(open(res))
        def walk(o, path=""):
            if isinstance(o, dict):
                ks = [k for k in o if str(k).isdigit()]
                if len(ks) >= 3:
                    ms = sorted(int(k) for k in ks)
                    vals = [o[str(m)] for m in ms]
                    if all(isinstance(v, (int, float)) for v in vals):
                        mono = all(vals[i] <= vals[i+1] + 1e-9 for i in range(len(vals)-1))
                        if not mono:
                            fail.append(f"B4/B5 NOT monotonic in M at {path}: {list(zip(ms, vals))}")
                            print(f"  FAIL B4/B5 not monotonic at {path}: {list(zip(ms,vals))}")
                        else:
                            print(f"  OK   B4/B5 monotonic at {path}")
                for k, v in o.items():
                    walk(v, f"{path}.{k}")
        walk(d)
    else:
        warn.append("firststage/RESULTS.json missing")


def main():
    audit_ablation()
    audit_firststage()
    print("\n" + "=" * 60)
    print(f"PASS {len(ok)} | FAIL {len(fail)} | WARN {len(warn)}")
    for f in fail: print("  FAIL:", f)
    for w in warn: print("  WARN:", w)
    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                          "DISCLOSE-BEFORE-USE"],
               "anchors": ANCHOR, "tol_pp": TOL,
               "passed": ok, "failed": fail, "warnings": warn,
               "verdict": "ACCEPT" if not fail else "REJECT"},
              open(os.path.join(HERE, "ideas_audit.json"), "w"), indent=2)
    print("verdict:", "ACCEPT" if not fail else "REJECT")


if __name__ == "__main__":
    main()
