"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Coordinator: compute + audit the repr round from per_query.jsonl.

The worker timed out before writing RESULTS.json. Its per-query output is complete for
RealTalk (705 x 10 arms x 2 scorers) and PARTIAL for PerLTQA (2967 of 8265 queries).
Everything below is derived here, from stored top-10 ids + gold. Nothing is taken on trust.

Rules honoured:
  - PerLTQA is a SUBSET -> its FULL anchor will NOT equal the 80.00 full-run number.
    The subset FULL arm is the control; contrasts stay valid because they are paired
    within the same queries. The subset is stated, never hidden.
  - Paired archive-clustered bootstrap, 20000 reps, seed 20260916.
  - IDF_p0 and SHIFT_m0 are zero-arms: they MUST equal FULL exactly. If they do not,
    the worker's pipeline is not the production pipeline and every other arm is void.
"""
import json, os
import numpy as np
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "math_r1", "repr", "per_query.jsonl")
OUT = os.path.join(HERE, "repr_results.json")

ANCHOR_RT = {"FULL/qscale": 49.6454, "FULL/sym": 46.5248}

def main():
    hit = defaultdict(dict)    # (bench, arm, scorer) -> qid -> 0/1
    fr3 = defaultdict(dict)
    arch = {}                  # (bench, qid) -> archive id
    bad = 0

    with open(SRC, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            b = r.get("benchmark") or r.get("bench")
            arm, sc = r.get("arm"), r.get("scorer")
            qid = r.get("qid") or r.get("question_id")
            gold = set(r.get("gold") or [])
            top = r.get("top10") or r.get("top") or []
            if len(top) != 10:
                bad += 1
            a = r.get("archive") or r.get("archive_id")
            if a is not None:
                arch[(b, qid)] = a
            k = (b, arm, sc)
            hit[k][qid] = 1.0 if (gold & set(top)) else 0.0
            fr3[k][qid] = (len(gold & set(top[:3])) / len(gold)) if gold else 0.0

    print(f"top10_length_violations={bad}")

    benches = sorted({k[0] for k in hit})
    arms = sorted({k[1] for k in hit})
    out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "source": "computed by coordinator from worker per_query.jsonl (worker timed out)",
           "benchmarks": {}}

    for b in benches:
        qids = sorted(hit[(b, "FULL", "qscale")].keys())
        n = len(qids)
        complete = {"RealTalk": 705, "PerLTQA": 8265}[b]
        print(f"\n{'='*74}\n{b}: n={n} of {complete} {'(COMPLETE)' if n==complete else '(PARTIAL SUBSET)'}")

        bo = {"n_queries": n, "n_complete": complete, "is_subset": n != complete,
              "summary": {}, "contrasts_vs_FULL_pp": {}, "zero_arm_check": {}}

        # ---- summary ----
        print(f"\n{'arm':12s} {'sym hit10':>10s} {'qscale hit10':>13s} {'sym fr3':>9s} {'qscale fr3':>11s}")
        for arm in arms:
            row = {}
            for sc in ("sym", "qscale"):
                k = (b, arm, sc)
                h = np.array([hit[k][q] for q in qids])
                f = np.array([fr3[k][q] for q in qids])
                row[sc] = {"hit10_pct": 100*h.mean(), "fr3_pct": 100*f.mean()}
            bo["summary"][arm] = row
            print(f"{arm:12s} {row['sym']['hit10_pct']:10.2f} {row['qscale']['hit10_pct']:13.2f} "
                  f"{row['sym']['fr3_pct']:9.2f} {row['qscale']['fr3_pct']:11.2f}")

        # ---- zero-arm identity check ----
        print("\nzero-arm identity (must be exactly 0 differing queries):")
        for z in ("IDF_p0", "SHIFT_m0"):
            if z not in arms:
                continue
            tot = 0
            for sc in ("sym", "qscale"):
                ka, kf = (b, z, sc), (b, "FULL", sc)
                tot += sum(1 for q in qids if hit[ka][q] != hit[kf][q])
            bo["zero_arm_check"][z] = {"differing_queries": tot, "identical": tot == 0}
            print(f"   {z:10s} differing={tot}  {'OK' if tot==0 else 'DEFECT'}")

        # ---- anchors (RealTalk only; PerLTQA subset cannot match) ----
        if b == "RealTalk":
            print("\nproduction anchors:")
            for armsc, exp in ANCHOR_RT.items():
                a_, s_ = armsc.split("/")
                got = 100*np.mean([hit[(b, a_, s_)][q] for q in qids])
                print(f"   {armsc:12s} got={got:.4f} expect={exp:.4f} d={abs(got-exp):.4f} "
                      f"{'OK' if abs(got-exp)<0.01 else 'FAIL'}")

        # ---- clustered bootstrap contrasts ----
        clusters = defaultdict(list)
        for i, q in enumerate(qids):
            clusters[arch.get((b, q), "NA")].append(i)
        cl = list(clusters.values())
        rng = np.random.default_rng(20260916)
        idx = [rng.integers(0, len(cl), len(cl)) for _ in range(20000)]

        print(f"\ncontrasts vs FULL (paired, archive-clustered bootstrap, {len(cl)} clusters):")
        for arm in arms:
            if arm == "FULL":
                continue
            for sc in ("sym", "qscale"):
                ka, kf = (b, arm, sc), (b, "FULL", sc)
                d = np.array([hit[ka][q] - hit[kf][q] for q in qids])
                est = 100*d.mean()
                reps = np.empty(20000)
                for t, pick in enumerate(idx):
                    sel = np.concatenate([cl[j] for j in pick])
                    reps[t] = d[sel].mean()
                lo, hi = 100*np.percentile(reps, [2.5, 97.5])
                ez = (lo > 0) or (hi < 0)
                bo["contrasts_vs_FULL_pp"][f"{arm}/{sc}"] = {
                    "hit10": {"mean_diff_pp": est, "ci95_lo_pp": lo, "ci95_hi_pp": hi,
                              "excludes_zero": bool(ez), "reps": 20000, "seed": 20260916,
                              "clusters": len(cl)}}
                if arm not in ("IDF_p0", "SHIFT_m0"):
                    print(f"   {arm:10s}/{sc:6s} {est:+7.2f} pp  [{lo:+7.2f},{hi:+7.2f}] "
                          f"{'SIGNIFICANT' if ez else 'ns'}")
        out["benchmarks"][b] = bo

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nWROTE {OUT}")

if __name__ == "__main__":
    main()
