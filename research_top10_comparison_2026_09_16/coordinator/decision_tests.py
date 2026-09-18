"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

DECISION TESTS T1-T3. Gates fixed BEFORE running (referee's stopping rule, decision_r1/cost).

T1  FAIR BASELINE. Re-run every code-vs-BM25 comparison on RealTalk with BM25 given OUR OWN
    frozen tokenization (\\b\\w\\w+\\b, English stopwords, UNIGRAMS ONLY -- see note) and with
    the k1->0,b=0 variant the external audit found matters. Question: which historical
    "we beat BM25" claims survive? Uses the already-computed ladder arms; only BM25 is rebuilt.

    CORRECTION 2026-09-18: this docstring said "1-2 grams". The implementation at :113-126
    emits unigrams only (FROZEN = re.compile(r"\\b\\w\\w+\\b"), no bigram construction), so the
    frozen BM25 arm was never given bigrams. A separate bigram probe in the data audit did not
    move the result materially, so the T1 conclusion stands; the prose was wrong, not the code.
    Reported by an external reviewer, 2026-09-18.

T2  RERANK DISSOLUTION. The premise-killer, computed from 164,256 stored paired rows in the
    incoming package (text_rerank_per_query.csv). Two questions, paired per query:
      (a) does code+rerank beat BM25-alone?           gate: >= +1.0 pp FR@3, CI excluding 0
      (b) does a BETTER first stage stay better after reranking? (rank correlation across
          the 5 first stages, per benchmark)
    If (a) fails and (b) shows inversion, optimizing a compact first stage is optimizing
    something the reranker overwrites.

T3  PerLTQA k<n. Rebuild the ladder on the 8 archives holding fewer than 384 documents,
    with k_eff = min(k, n-1), and score BOTH standardized (qscale) and unstandardized (asym)
    arms. Question: does the 192->384 decline disappear once rank overflow is removed?

PRESPECIFIED GATES (referee's rule, not adjustable after seeing results):
  C1 some arm <=48 B beats FAIR BM25 by >= +2.0 pp FR@3, CI excluding 0, on BOTH benchmarks
  C3 best code+rerank beats BM25-alone by >= +1.0 pp FR@3, CI excluding 0
  S3 PerLTQA-corrected still flat-or-falling on UNSTANDARDIZED arms => real capacity law
Bootstrap: paired, archive-clustered, 20000 reps, seed 20260916.
"""
import csv, json, math, os, re, sys, time, pickle, importlib.util
from collections import defaultdict

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "DECISION_TESTS.json")
RERANK_CSV = (f"{W}/incoming_20260916b/extracted/LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/"
              "LLMZIP_FIKIR1_2026-09-16/results/text_rerank_per_query.csv")
PERLTQA_CACHE = f"{W}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PERLTQA_Q = f"{W}/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
STEP2 = f"{W}/bench3/runs/b3b_perltqa/step2_build.py"

def boot(diff, clusters, reps=20000, seed=20260916):
    """Paired archive-clustered bootstrap over a per-query difference vector."""
    rng = np.random.default_rng(seed)
    cl = list(clusters.values())
    out = np.empty(reps)
    for t in range(reps):
        pick = rng.integers(0, len(cl), len(cl))
        out[t] = diff[np.concatenate([cl[j] for j in pick])].mean()
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(100 * diff.mean()), float(100 * lo), float(100 * hi), bool(lo > 0 or hi < 0)

# ----------------------------------------------------------------- T2 first (cheapest)
def t2():
    rows = list(csv.DictReader(open(RERANK_CSV, encoding="utf-8")))
    per = defaultdict(dict)          # (ds, method) -> qid -> fr3
    arch = {}
    for r in rows:
        ds, m, q = r["dataset"], r["method"], r["qid"]
        per[(ds, m)][q] = float(r["fr3"])
        arch[(ds, q)] = r["archive"]
    res = {}
    for ds in sorted({k[0] for k in per}):
        methods = sorted({k[1] for k in per if k[0] == ds})
        qids = sorted(per[(ds, "BM25_full")].keys())
        clusters = defaultdict(list)
        for i, q in enumerate(qids):
            clusters[arch[(ds, q)]].append(i)
        clusters = {k: np.array(v) for k, v in clusters.items()}
        base = np.array([per[(ds, "BM25_full")][q] for q in qids])

        levels = {m: 100 * np.mean([per[(ds, m)][q] for q in qids])
                  for m in methods if len(per[(ds, m)]) >= len(qids)}
        # (a) each reranked arm vs BM25 alone
        contrasts = {}
        for m in methods:
            if not m.endswith("_bm25") or len(per[(ds, m)]) < len(qids):
                continue
            d = np.array([per[(ds, m)][q] for q in qids]) - base
            est, lo, hi, sig = boot(d, clusters)
            contrasts[m] = {"vs_BM25_alone_pp": est, "ci_lo": lo, "ci_hi": hi,
                            "excludes_zero": sig, "passes_C3_gate": bool(est >= 1.0 and sig)}
        # (b) does first-stage order survive reranking?
        pairs = []
        for m in methods:
            if m.endswith("_bm25") and m[:-5] in levels:
                pairs.append((m[:-5], levels[m[:-5]], m, levels[m]))
        pairs.sort(key=lambda x: -x[1])
        inversions = sum(1 for i in range(len(pairs)) for j in range(i + 1, len(pairs))
                         if pairs[i][3] < pairs[j][3])
        res[ds] = {"n_queries": len(qids), "n_clusters": len(clusters),
                   "levels_fr3": levels, "contrasts_vs_BM25_alone": contrasts,
                   "first_stage_order": [{"stage": a, "fr3_before": b, "after": d}
                                          for a, b, _, d in pairs],
                   "order_inversions": inversions,
                   "n_pairs": len(pairs) * (len(pairs) - 1) // 2}
    return res

# ----------------------------------------------------------------- T1
def t1():
    """Fair-vs-coarse BM25 on RealTalk, against the already-measured ladder arms."""
    ladder = json.load(open(os.path.join(HERE, "LADDER.json"), encoding="utf-8"))["arms"]
    RT = f"{W}/top10_comparison_r1/data"
    lib = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location("lib", f"{W}/top10_comparison_r1/audit/audit_baseline_lib.py"))
    importlib.util.spec_from_file_location(
        "lib", f"{W}/top10_comparison_r1/audit/audit_baseline_lib.py").loader.exec_module(lib)

    TOKEN = re.compile(r"[a-z0-9]+")
    FROZEN = re.compile(r"\b\w\w+\b")
    STOP = set("""a about above after again against all am an and any are as at be because been before
being below between both but by could did do does doing down during each few for from further had has
have having he her here hers herself him himself his how i if in into is it its itself just me more most
my myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

    def toks(s, frozen):
        if frozen:
            return [w for w in FROZEN.findall((s or "").lower()) if w not in STOP]
        return TOKEN.findall((s or "").lower())

    class BM25:
        def __init__(self, docs, k1, b):
            self.k1, self.b, self.N = k1, b, len(docs)
            self.len = np.array([len(d) for d in docs], float)
            self.avg = self.len.mean() if self.N else 1.0
            self.post = defaultdict(list)
            for i, d in enumerate(docs):
                tf = defaultdict(int)
                for w in d:
                    tf[w] += 1
                for w, c in tf.items():
                    self.post[w].append((i, c))
            self.idf = {w: math.log(1 + (self.N - len(pl) + .5) / (len(pl) + .5))
                        for w, pl in self.post.items()}

        def score(self, q):
            s = np.zeros(self.N)
            dl = self.k1 * (1 - self.b + self.b * self.len / self.avg) if self.k1 > 0 else None
            for w in set(q):
                pl = self.post.get(w)
                if not pl:
                    continue
                idf = self.idf[w]
                for i, c in pl:
                    s[i] += idf if self.k1 == 0 else idf * c * (self.k1 + 1) / (c + dl[i])
            return s

    variants = {"coarse_textbook": (False, 1.2, 0.75), "frozen_textbook": (True, 1.2, 0.75),
                "coarse_idfonly": (False, 0.0, 0.0), "frozen_idfonly": (True, 0.0, 0.0)}
    acc = {v: {"hit": [], "fr3": [], "per_q": {}} for v in variants}
    archof = {}
    for i in range(1, 11):
        aid = f"RT{i:02d}"
        D = json.load(open(f"{RT}/{aid}.json", encoding="utf-8"))
        docs = D["docs"]
        row_of = {d["row"]: j for j, d in enumerate(docs)}
        qs = [q for q in D["queries"] if any(g in row_of for g in q.get("gold", []))]
        gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
        for vname, (frz, k1, b) in variants.items():
            bm = BM25([toks(d["text"], frz) for d in docs], k1, b)
            for qi, q in enumerate(qs):
                s = bm.score(toks(q["text"], frz))
                top = lib.det_top10(s, aid, 10)
                g = set(gold[qi])
                acc[vname]["hit"].append(1.0 if (g & set(top)) else 0.0)
                acc[vname]["fr3"].append(len(g & set(top[:3])) / len(g))
                acc[vname]["per_q"][q["qid"]] = 1.0 if (g & set(top)) else 0.0
                archof[q["qid"]] = aid
    out = {"bm25_variants": {}, "code_arms": {}, "verdict": {}}
    for v in variants:
        out["bm25_variants"][v] = {"hit10": 100 * np.mean(acc[v]["hit"]),
                                   "fr3": 100 * np.mean(acc[v]["fr3"])}
    best = max(out["bm25_variants"], key=lambda v: out["bm25_variants"][v]["hit10"])
    out["strongest_bm25"] = {"variant": best, **out["bm25_variants"][best]}
    for k, bpd in ((96, 12), (192, 24), (384, 48)):
        for sc in ("sym", "qscale"):
            a = ladder[f"k{k}/{sc}"]
            out["code_arms"][f"{bpd}B/{sc}"] = {
                "hit10": a["hit10"], "fr3": a["fr3"],
                "vs_strongest_bm25_hit10_pp": a["hit10"] - out["strongest_bm25"]["hit10"],
                "vs_strongest_bm25_fr3_pp": a["fr3"] - out["strongest_bm25"]["fr3"]}
    out["verdict"]["any_arm_beats_strongest_bm25_hit10"] = any(
        v["vs_strongest_bm25_hit10_pp"] > 0 for v in out["code_arms"].values())
    out["verdict"]["C1_gate_plus2pp_fr3"] = any(
        v["vs_strongest_bm25_fr3_pp"] >= 2.0 for v in out["code_arms"].values())
    return out

if __name__ == "__main__":
    t0 = time.time()
    res = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "gates": {"C1": ">=+2.0pp FR@3 vs FAIR BM25, CI excl 0, BOTH benchmarks",
                     "C3": "code+rerank >= +1.0pp FR@3 vs BM25-alone, CI excl 0"}}
    print("=== T2 rerank dissolution (164k stored paired rows) ===", flush=True)
    res["T2_rerank"] = t2()
    for ds, v in res["T2_rerank"].items():
        print(f"\n{ds} (n={v['n_queries']}, {v['n_clusters']} clusters)")
        for m, c in sorted(v["contrasts_vs_BM25_alone"].items()):
            print(f"  {m:22s} {c['vs_BM25_alone_pp']:+6.2f} pp [{c['ci_lo']:+6.2f},{c['ci_hi']:+6.2f}] "
                  f"{'SIG' if c['excludes_zero'] else 'ns'}  C3={'PASS' if c['passes_C3_gate'] else 'FAIL'}")
        print(f"  first-stage order after rerank: {v['order_inversions']} inversions of {v['n_pairs']} pairs")
        for r in v["first_stage_order"]:
            print(f"     {r['stage']:16s} {r['fr3_before']:6.2f} -> {r['after']:6.2f}")
    print(f"\n=== T1 fair baseline (RealTalk) ===", flush=True)
    res["T1_fair_baseline"] = t1()
    for v, m in res["T1_fair_baseline"]["bm25_variants"].items():
        print(f"  BM25 {v:18s} Hit@10 {m['hit10']:6.2f}  FR@3 {m['fr3']:6.2f}")
    sb = res["T1_fair_baseline"]["strongest_bm25"]
    print(f"  -> strongest BM25: {sb['variant']} Hit@10 {sb['hit10']:.2f}")
    for k, v in res["T1_fair_baseline"]["code_arms"].items():
        print(f"  code {k:12s} Hit@10 {v['hit10']:6.2f} ({v['vs_strongest_bm25_hit10_pp']:+6.2f})  "
              f"FR@3 {v['fr3']:6.2f} ({v['vs_strongest_bm25_fr3_pp']:+6.2f})")
    print(f"  C1 gate: {'PASS' if res['T1_fair_baseline']['verdict']['C1_gate_plus2pp_fr3'] else 'FAIL'}")
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"\nWROTE {OUT}  elapsed {time.time()-t0:.0f}s")
