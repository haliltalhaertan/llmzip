"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Decisive test for the one surviving candidate:

  RealTalk / IDF_p2 / qscale FR@3, RARE band only: FULL 33.23 -> 38.01 (+4.78).
  The OVERALL FR@3 contrast was +2.61 pp with CI [-0.12, +5.30] -> not significant.
  Question: is the rare-band effect itself significant, or is it noise that happens to
  sit where the mechanism predicted?

Also resolves a bookkeeping discrepancy I must not paper over: the earlier
why_bm25_wins.py stratification put 341 queries in the rare band; this one puts 412.
Both used "max IDF among terms shared by query and gold, threshold 4" but tokenization
and df source differ. Report BOTH counts and re-run the band contrast under each rule,
so the conclusion does not depend on an undocumented choice.

A band-restricted contrast is a SUBGROUP test chosen AFTER seeing the numbers. It is
reported as exploratory and is NOT a preregistered finding, whatever it shows.
"""
import json, os, re, math
import numpy as np
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "math_r1", "repr", "per_query.jsonl")
RT_DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "rare_band_decisive.json")

TOKEN_A = re.compile(r"[a-z0-9]+")            # rule A (this round)
TOKEN_B = re.compile(r"[a-z]{2,}")            # rule B (stricter, closer to lexical arm)

def bands_for(tokre, min_len_filter):
    bands, meta = {}, {}
    for i in range(1, 11):
        p = os.path.join(RT_DATA, f"RT{i:02d}.json")
        if not os.path.exists(p):
            continue
        D = json.load(open(p, encoding="utf-8"))
        docs = D["docs"]; N = len(docs)
        df = defaultdict(int); dt = []
        for d_ in docs:
            t = set(tokre.findall((d_.get("text") or "").lower()))
            if min_len_filter:
                t = {w for w in t if len(w) >= 3}
            dt.append(t)
            for w in t:
                df[w] += 1
        row_of = {d_["row"]: j for j, d_ in enumerate(docs)}
        for q in D["queries"]:
            qt = set(tokre.findall((q.get("text") or "").lower()))
            if min_len_filter:
                qt = {w for w in qt if len(w) >= 3}
            best = -1.0
            for g in q.get("gold", []):
                j = row_of.get(g)
                if j is None:
                    continue
                for w in (qt & dt[j]):
                    best = max(best, math.log(N / df[w]))
            bands[q["qid"]] = ("no_shared" if best < 0 else
                               "common" if best < 2 else
                               "mid" if best < 4 else "rare")
            meta[q["qid"]] = D["archive_id"]
    return bands, meta

def main():
    fr3 = defaultdict(dict); hit = defaultdict(dict)
    with open(SRC, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if (r.get("benchmark") or r.get("bench")) != "RealTalk":
                continue
            k = (r.get("arm"), r.get("scorer"))
            qid = r.get("qid") or r.get("question_id")
            gold = set(r.get("gold") or [])
            top = r.get("top10") or r.get("top") or []
            fr3[k][qid] = (len(gold & set(top[:3])) / len(gold)) if gold else 0.0
            hit[k][qid] = 1.0 if (gold & set(top)) else 0.0

    out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "warning": "band-restricted contrast selected AFTER seeing results; exploratory subgroup test",
           "rules": {}}

    for rule_name, tokre, mlf in (("A_this_round", TOKEN_A, False),
                                  ("B_stricter", TOKEN_B, True)):
        bands, arch = bands_for(tokre, mlf)
        counts = defaultdict(int)
        for q, b in bands.items():
            counts[b] += 1
        print(f"\n=== rule {rule_name}: band sizes {dict(counts)} ===")
        rule_out = {"band_sizes": dict(counts), "contrasts": {}}

        for band in ("rare", "mid", "common"):
            qs = [q for q in fr3[("FULL", "qscale")] if bands.get(q) == band]
            if len(qs) < 30:
                continue
            clusters = defaultdict(list)
            for i, q in enumerate(qs):
                clusters[arch.get(q, "NA")].append(i)
            cl = list(clusters.values())
            rng = np.random.default_rng(20260916)

            for metric, store in (("fr3", fr3), ("hit10", hit)):
                d = np.array([store[("IDF_p2", "qscale")][q] - store[("FULL", "qscale")][q] for q in qs])
                est = 100 * d.mean()
                reps = np.empty(20000)
                for t in range(20000):
                    pick = rng.integers(0, len(cl), len(cl))
                    sel = np.concatenate([cl[j] for j in pick])
                    reps[t] = d[sel].mean()
                lo, hi = 100 * np.percentile(reps, [2.5, 97.5])
                ez = (lo > 0) or (hi < 0)
                rule_out["contrasts"][f"{band}/{metric}"] = {
                    "n": len(qs), "mean_diff_pp": est, "ci95_lo_pp": lo,
                    "ci95_hi_pp": hi, "excludes_zero": bool(ez), "clusters": len(cl)}
                print(f"  {band:8s} {metric:6s} n={len(qs):4d} {est:+7.2f} pp "
                      f"[{lo:+7.2f},{hi:+7.2f}] {'SIGNIFICANT' if ez else 'ns'}")
        out["rules"][rule_name] = rule_out

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nWROTE {OUT}")

if __name__ == "__main__":
    main()
