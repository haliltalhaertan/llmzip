"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Why did the SPLIT fix fail so badly (49.65% -> 33-35%)? Two suspects, one decisive test.

  S1 TRUNCATION: keeping only the first k SVD dims destroys the representation by itself.
  S2 BLOOM: the rare-term sketch is too lossy / too tie-heavy to contribute.

Decisive: measure SVD-ONLY at k = 96, 80, 64, 48 with NO bloom and NO fusion.
If SVD-only at k=48 is already ~33%, truncation is the killer and the bloom idea was
never given a fair chance. If SVD-only stays near 49%, then the bloom half is what broke it.
Also measures the bloom part ALONE, and reports its tie structure (distinct score count),
because a score with ~8 possible values ranks mostly by tie-break = near random.
"""
import hashlib, json, math, os, pickle, re, sys, time
from collections import Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
from audit_baseline_lib import det_top10, hrn

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
RT = R + "/bench3/runs/b3a_realtalk/rt_repr"
WORD = re.compile(r"\w+", re.UNICODE)
ARCH = [f"RT{i:02d}" for i in range(1, 11)]
KS = [96, 80, 64, 48, 32]


def toks(s):
    return WORD.findall(s.lower())


def bloom_bits(terms, nbits, salt="bloom-r1"):
    b = np.zeros(nbits, dtype=bool)
    for t in terms:
        h = int(hashlib.sha256(f"{salt}|{t}".encode()).hexdigest()[:8], 16)
        b[h % nbits] = True
    return b


def main():
    t0 = time.time()
    svd_only = {k: [] for k in KS}
    bloom_only = {nb: [] for nb in (16, 32, 48)}
    tie_stats = []
    for a in ARCH:
        exp = json.load(open(f"{DATA}/{a}.json", encoding="utf-8"))
        o = pickle.loads(open(f"{RT}/{a}.pkl", "rb").read())
        C = np.asarray(o["C"], np.float64); N = C.shape[0]
        dtok = [toks(x["text"]) for x in exp["docs"]]
        df = Counter()
        for dt in dtok:
            for t in set(dt):
                df[t] += 1
        idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
        doc_rare = [sorted(set(dt), key=lambda t: (-idf.get(t, 0.0), t))[:8] for dt in dtok]
        sg = np.maximum(np.std(C, axis=0, ddof=0), 1e-12)
        qmap = {q["qid"]: q for q in exp["queries"]}
        B = np.where(C >= 0, 1.0, -1.0)
        for qi, qid in enumerate(o["qids"]):
            gold = [int(x) for x in o["gold_rows"][qi]]
            if not gold or qid not in qmap:
                continue
            qC = np.asarray(o["QC"][qi], np.float64)
            for k in KS:
                s = B[:, :k] @ (qC[:k] / sg[:k])
                svd_only[k].append(hrn(det_top10(s, a, 10), gold, 10)[0])
            qt = toks(qmap[qid]["text"])
            qr = [t for t in set(qt) if idf.get(t, 0.0) >= 2.0]
            for nb in (16, 32, 48):
                DB = np.array([bloom_bits(doc_rare[j], nb) for j in range(N)])
                QB = bloom_bits(qr, nb)
                s = (DB & QB[None, :]).sum(axis=1).astype(float)
                bloom_only[nb].append(hrn(det_top10(s, a, 10), gold, 10)[0])
                if nb == 32:
                    tie_stats.append(len(np.unique(s)))
        print(f"  {a} {time.time()-t0:.0f}s", flush=True)

    print("\n=== SVD-ONLY (no bloom, no fusion): is truncation the killer? ===")
    print(f"{'svd bits':>9} {'payload B':>10} {'Hit@10':>9}")
    res_s = {}
    for k in KS:
        v = 100 * float(np.mean(svd_only[k]))
        res_s[k] = v
        print(f"{k:9d} {math.ceil(k/8):10d} {v:9.2f}")

    print("\n=== BLOOM-ONLY (rare-term sketch alone) ===")
    print(f"{'bits':>6} {'Hit@10':>9}")
    res_b = {}
    for nb in (16, 32, 48):
        v = 100 * float(np.mean(bloom_only[nb]))
        res_b[nb] = v
        print(f"{nb:6d} {v:9.2f}")
    print(f"\nbloom(32b) distinct scores per query: mean {np.mean(tie_stats):.2f}, "
          f"max {max(tie_stats)} -> a score with so few levels ranks mostly by tie-break")

    print("\n=== VERDICT ===")
    drop_trunc = res_s[96] - res_s[48]
    print(f"  SVD 96 -> 48 bits alone costs {drop_trunc:.2f} pp ({res_s[96]:.2f} -> {res_s[48]:.2f})")
    print(f"  full SPLIT_48 (svd48+bloom48) measured earlier: 33.48")
    print(f"  => truncation explains {'MOST' if res_s[48] < 40 else 'LITTLE'} of the split failure")
    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                          "DISCLOSE-BEFORE-USE"],
               "svd_only_hit10": res_s, "bloom_only_hit10": res_b,
               "bloom32_distinct_scores_mean": float(np.mean(tie_stats)),
               "prior_split_results": {"96": 49.65, "80": 33.33, "64": 34.61, "48": 33.48},
               "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, "split_failure_diag.json"), "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
