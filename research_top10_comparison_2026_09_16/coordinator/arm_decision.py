"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Decision-grade paired comparison of the SMALL-CODE arms we already have, on data we already own.
No new method. Question: does the incoming 'qscale' beat the asymmetric arm we ALREADY had?

Arms (identical 12-byte document codes for all three; only query-side reading differs):
  sign96 = -Hamming(b_d, b_q)
  asym   = dot(b_d, qC) / sqrt(96)        [what we already had]
  qscale = dot(b_d, qC / sigma)           [incoming proposal]
sigma: per-archive std of DOCUMENT columns, ddof=0, floor 1e-12. Documents only, no gold fitting.

Paired, archive-clustered bootstrap (20000 reps, seed 20260916) because queries share archives.
Reports realized Hit@10 per protocol tie rule AND exact expected Hit@10 under uniform ties.
"""
import glob, json, os, pickle, sys, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
from audit_baseline_lib import decode_pm1, det_top10, expected_hit, hrn, pack_signs_bool

R = "/mnt/c/Users/MDP/dev/llmzip-work"
SQRT96 = float(np.sqrt(96))
NBOOT, SEED = 20000, 20260916


def arms(C, q, aid):
    C = np.asarray(C, np.float64); q = np.asarray(q, np.float64).reshape(-1)
    sg = np.maximum(np.std(C, axis=0, ddof=0), 1e-12)
    B = decode_pm1(pack_signs_bool(C >= 0)).astype(np.float64)
    qb = np.where(q >= 0, 1.0, -1.0)
    return {"sign96": B @ qb, "asym": (B @ q) / SQRT96, "qscale": B @ (q / sg)}


def collect():
    rec = defaultdict(list)
    arch = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
    Q = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
    by = defaultdict(list)
    for qid, q in Q.items():
        by[q["char"]].append(qid)
    for ch, qids in sorted(by.items()):
        C = np.asarray(arch[ch]["C"], np.float64)
        for qid in sorted(qids):
            g = np.asarray(Q[qid]["gold"]).ravel().astype(int)
            S = arms(C, Q[qid]["qC"], ch)
            rec["PerLTQA"].append((ch, {a: (hrn(det_top10(s, ch, 10), g)[0], expected_hit(s, g, 10))
                                        for a, s in S.items()}))
    for f in sorted(glob.glob(R + "/regen/lme/cache_repr/*.pkl")):
        d = pickle.loads(open(f, "rb").read()); qid = d["question_id"]
        g = np.asarray(d["gold"]).ravel().astype(int)
        S = arms(d["C"], d["qC"], qid)
        rec["LME"].append((qid, {a: (hrn(det_top10(s, qid, 10), g)[0], expected_hit(s, g, 10))
                                 for a, s in S.items()}))
    for f in sorted(glob.glob(R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
        o = pickle.loads(open(f, "rb").read()); aid = str(o["conv_id"])
        C = np.asarray(o["C"], np.float64)
        for qi, qid in enumerate(o["qids"]):
            g = [int(x) for x in o["gold_rows"][qi]]
            if not g:
                continue
            g = np.asarray(g, int)
            S = arms(C, o["QC"][qi], aid)
            rec["REALTALK"].append((aid, {a: (hrn(det_top10(s, aid, 10), g)[0], expected_hit(s, g, 10))
                                          for a, s in S.items()}))
    return rec


def boot(rows, a, b, idx):
    """Paired archive-clustered bootstrap of (a-b) in percentage points, on expected Hit@10."""
    groups = defaultdict(list)
    for aid, m in rows:
        groups[aid].append(m[a][idx] - m[b][idx])
    keys = list(groups)
    arrs = [np.asarray(groups[k], float) for k in keys]
    sums = np.array([x.sum() for x in arrs]); cnts = np.array([len(x) for x in arrs])
    rng = np.random.default_rng(SEED)
    out = np.empty(NBOOT)
    for i in range(NBOOT):
        p = rng.integers(0, len(keys), len(keys))
        out[i] = 100.0 * sums[p].sum() / cnts[p].sum()
    point = 100.0 * sums.sum() / cnts.sum()
    return point, float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)), len(keys)


def main():
    t0 = time.time()
    rec = collect()
    res = {}
    for b in ("LME", "PerLTQA", "REALTALK"):
        rows = rec[b]
        res[b] = {"n": len(rows), "n_archives": len(set(a for a, _ in rows)), "means": {}, "contrasts": {}}
        for a in ("sign96", "asym", "qscale"):
            res[b]["means"][a] = {
                "realized": 100 * float(np.mean([m[a][0] for _, m in rows])),
                "expected": 100 * float(np.mean([m[a][1] for _, m in rows]))}
        for x, y in (("qscale", "sign96"), ("asym", "sign96"), ("qscale", "asym")):
            pt, lo, hi, k = boot(rows, x, y, 1)
            w = sum(1 for _, m in rows if m[x][1] > m[y][1])
            l = sum(1 for _, m in rows if m[x][1] < m[y][1])
            res[b]["contrasts"][f"{x}-{y}"] = {"point_pp": pt, "ci95": [lo, hi], "clusters": k,
                                               "better": w, "worse": l, "same": len(rows) - w - l,
                                               "ci_excludes_zero": bool(lo > 0 or hi < 0)}
    print("=== expected Hit@10 (%), 12-byte document codes in ALL arms ===")
    print(f"{'bench':9} {'n':>5} {'sign96':>8} {'asym':>8} {'qscale':>8}")
    for b in res:
        m = res[b]["means"]
        print(f"{b:9} {res[b]['n']:5d} {m['sign96']['expected']:8.2f} {m['asym']['expected']:8.2f} {m['qscale']['expected']:8.2f}")
    print("\n=== paired archive-clustered bootstrap, 20000 reps (pp) ===")
    print(f"{'bench':9} {'contrast':16} {'point':>8} {'ci95_low':>9} {'ci95_high':>9} {'clust':>6} {'W/L/=':>16} {'signif':>7}")
    for b in res:
        for c, d in res[b]["contrasts"].items():
            wl = "{}/{}/{}".format(d["better"], d["worse"], d["same"])
            sig = "YES" if d["ci_excludes_zero"] else "no"
            lo, hi = d["ci95"]
            print(f"{b:9} {c:16} {d['point_pp']:+8.3f} {lo:+9.3f} {hi:+9.3f} "
                  f"{d['clusters']:6d} {wl:>16} {sig:>7}")
    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                          "DISCLOSE-BEFORE-USE"],
               "note": "Archive-clustered paired bootstrap; RealTalk has only 10 clusters, PerLTQA 30. "
                       "LME has one archive per question so clusters=questions and independence is assumed, "
                       "not established. Exploratory, not a preregistered confirmation.",
               "nboot": NBOOT, "seed": SEED, "results": res, "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, "arm_decision.json"), "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
