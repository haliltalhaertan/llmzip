"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Follow-up: FR@3 contrasts (the first pass bootstrapped Hit@10 only), plus the
mechanism check the round exists for - does any gain sit in the RARE-IDF band?

Two candidate signals to adjudicate:
  S1  IDF_p2 on RealTalk: FR@3 22.41 -> 25.02 (+2.61) but Hit@10 flat (+0.00).
  S2  SHIFT_m1 on PerLTQA: Hit@10 +1.58 SIGNIFICANT, but RealTalk -0.28 ns.

If IDF_p2's FR@3 gain is real AND concentrated in the rare band, the stated mechanism
(inflate rare-term variance so SVD keeps discriminative directions) is supported even
though Hit@10 did not move - that would mean better ORDERING inside an unchanged pool.
"""
import json, os, re, math, pickle
import numpy as np
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "math_r1", "repr", "per_query.jsonl")
RT_DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "repr_fr3_mechanism.json")

TOKEN = re.compile(r"[a-z0-9]+")

def toks(s):
    return set(TOKEN.findall((s or "").lower()))

def main():
    fr3 = defaultdict(dict)
    arch = {}
    with open(SRC, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            b = r.get("benchmark") or r.get("bench")
            k = (b, r.get("arm"), r.get("scorer"))
            qid = r.get("qid") or r.get("question_id")
            gold = set(r.get("gold") or [])
            top = r.get("top10") or r.get("top") or []
            fr3[k][qid] = (len(gold & set(top[:3])) / len(gold)) if gold else 0.0
            a = r.get("archive") or r.get("archive_id")
            if a is not None:
                arch[(b, qid)] = a

    out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "fr3_contrasts": {}, "mechanism": {}}

    for b in ("RealTalk", "PerLTQA"):
        qids = sorted(fr3[(b, "FULL", "qscale")].keys())
        clusters = defaultdict(list)
        for i, q in enumerate(qids):
            clusters[arch.get((b, q), "NA")].append(i)
        cl = list(clusters.values())
        rng = np.random.default_rng(20260916)
        idx = [rng.integers(0, len(cl), len(cl)) for _ in range(20000)]
        arms = sorted({k[1] for k in fr3 if k[0] == b})
        print(f"\n=== {b} FR@3 contrasts vs FULL (n={len(qids)}, {len(cl)} clusters) ===")
        for arm in arms:
            if arm in ("FULL", "IDF_p0", "SHIFT_m0"):
                continue
            for sc in ("sym", "qscale"):
                d = np.array([fr3[(b, arm, sc)][q] - fr3[(b, "FULL", sc)][q] for q in qids])
                est = 100 * d.mean()
                reps = np.empty(20000)
                for t, pick in enumerate(idx):
                    sel = np.concatenate([cl[j] for j in pick])
                    reps[t] = d[sel].mean()
                lo, hi = 100 * np.percentile(reps, [2.5, 97.5])
                ez = (lo > 0) or (hi < 0)
                out["fr3_contrasts"][f"{b}/{arm}/{sc}"] = {
                    "mean_diff_pp": est, "ci95_lo_pp": lo, "ci95_hi_pp": hi,
                    "excludes_zero": bool(ez)}
                print(f"  {arm:10s}/{sc:6s} {est:+7.2f} pp [{lo:+7.2f},{hi:+7.2f}] "
                      f"{'SIGNIFICANT' if ez else 'ns'}")

    # ---------- mechanism check on RealTalk (raw texts available) ----------
    print("\n=== MECHANISM: RealTalk FR@3 by rare-term band, IDF_p2 vs FULL ===")
    bands = {}
    for i in range(1, 11):
        p = os.path.join(RT_DATA, f"RT{i:02d}.json")
        if not os.path.exists(p):
            continue
        D = json.load(open(p, encoding="utf-8"))
        docs = D["docs"]
        N = len(docs)
        df = defaultdict(int)
        dt = []
        for d_ in docs:
            t = toks(d_.get("text"))
            dt.append(t)
            for w in t:
                df[w] += 1
        row_of = {d_["row"]: j for j, d_ in enumerate(docs)}
        for q in D["queries"]:
            qt = toks(q.get("text"))
            best = -1.0
            for g in q.get("gold", []):
                j = row_of.get(g)
                if j is None:
                    continue
                for w in (qt & dt[j]):
                    best = max(best, math.log(N / df[w]))
            band = ("no_shared" if best < 0 else
                    "common" if best < 2 else
                    "mid" if best < 4 else "rare")
            bands[q["qid"]] = band

    for sc in ("sym", "qscale"):
        print(f"\n  scorer={sc}")
        print(f"  {'band':10s} {'n':>5s} {'FULL':>8s} {'IDF_p2':>8s} {'diff':>8s}")
        agg = {}
        for band in ("no_shared", "common", "mid", "rare"):
            qs = [q for q in fr3[("RealTalk", "FULL", sc)] if bands.get(q) == band]
            if not qs:
                continue
            f0 = 100 * np.mean([fr3[("RealTalk", "FULL", sc)][q] for q in qs])
            f2 = 100 * np.mean([fr3[("RealTalk", "IDF_p2", sc)][q] for q in qs])
            agg[band] = {"n": len(qs), "FULL": f0, "IDF_p2": f2, "diff_pp": f2 - f0}
            print(f"  {band:10s} {len(qs):5d} {f0:8.2f} {f2:8.2f} {f2-f0:+8.2f}")
        out["mechanism"][sc] = agg

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nWROTE {OUT}")

if __name__ == "__main__":
    main()
