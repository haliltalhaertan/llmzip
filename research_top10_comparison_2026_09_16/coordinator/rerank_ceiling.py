"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Gate test for the proposal doc's Idea #1 (small code retrieves candidates, raw text reranks).

The doc itself states the precondition: "onces, mevcut aday kumelerinde kusursuz siralama
yapilsa FR@3 en fazla nereye cikabilir, bunu hesaplamaliyiz. Tavan dusukse yeniden
siralayiciya yatirim yapmak yanlis olur."

So: for candidate pool sizes M, compute the PERFECT-RERANKER CEILING = what FR@3 (and Hit@3)
you would get if an oracle reordered the top-M candidates optimally. This is an upper bound
no reranker can exceed. Compare against current FR@3 to get the headroom.

Arms use the 12-byte document codes we already have. Retrieval stage = qscale (current best
small-code arm). Also reports the lexical BM25 stage on REALTALK, since BM25 currently beats
every 12-byte arm there.

Ceiling definition (exact, tie-aware):
  Retrieve top-M by the stage scorer under the deterministic protocol tie rule.
  Oracle then places any gold found inside those M at the very top.
  FR@3_ceiling = min(3, |gold ∩ topM|) / |gold|        (fractional evidence recall @3)
  Hit@3_ceiling = 1 if |gold ∩ topM| > 0 else 0
  Hit@10_ceiling likewise with min(10,·).
"""
import glob, json, os, pickle, sys, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
from audit_baseline_lib import decode_pm1, det_top10, hrn, pack_signs_bool

R = "/mnt/c/Users/MDP/dev/llmzip-work"
MS = [3, 10, 20, 50, 100, 200, 500]
DATA = R + "/top10_comparison_r1/data"


def qscale_scores(C, q):
    C = np.asarray(C, np.float64); q = np.asarray(q, np.float64).reshape(-1)
    sg = np.maximum(np.std(C, axis=0, ddof=0), 1e-12)
    B = decode_pm1(pack_signs_bool(C >= 0)).astype(np.float64)
    return B @ (q / sg)


def ceilings(scores, gold, aid, N):
    """Returns dict M -> (fr3_ceiling, hit3_ceiling, hit10_ceiling)."""
    g = set(int(x) for x in np.asarray(gold).ravel().tolist())
    order = det_top10(scores, aid, min(max(MS), N))
    out = {}
    for M in MS:
        if M > N:
            out[M] = None; continue
        found = len(g.intersection(int(x) for x in order[:M].tolist()))
        out[M] = (min(3, found) / len(g), 1.0 if found else 0.0, 1.0 if found else 0.0)
    return out


def current_fr3(scores, gold, aid):
    """FR@3 actually achieved now by this scorer (deterministic tie rule)."""
    g = set(int(x) for x in np.asarray(gold).ravel().tolist())
    top3 = det_top10(scores, aid, 3)[:3]
    return len(g.intersection(int(x) for x in top3.tolist())) / len(g)


def bm25_scores(docs_tok, q_tok, avglen):
    import math
    from collections import Counter
    N = len(docs_tok); df = Counter()
    for dt in docs_tok:
        for t in set(dt):
            df[t] += 1
    idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
    qtf = Counter(q_tok); out = np.zeros(N)
    for j, dt in enumerate(docs_tok):
        tf = Counter(dt); norm = 1.5 * (1 - 0.75 + 0.75 * len(dt) / avglen)
        s = 0.0
        for t in qtf:
            if t in idf and tf.get(t, 0):
                f = tf[t]; s += idf[t] * (f * 2.5 / (f + norm))
        out[j] = s
    return out


def main():
    t0 = time.time()
    acc = defaultdict(lambda: defaultdict(list))

    arch = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
    Q = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
    by = defaultdict(list)
    for qid, q in Q.items():
        by[q["char"]].append(qid)
    for ch, qids in sorted(by.items()):
        C = np.asarray(arch[ch]["C"], np.float64); N = C.shape[0]
        for qid in sorted(qids):
            s = qscale_scores(C, Q[qid]["qC"]); g = Q[qid]["gold"]
            acc["PerLTQA"]["cur"].append(current_fr3(s, g, ch))
            for M, v in ceilings(s, g, ch, N).items():
                if v: acc["PerLTQA"][f"M{M}"].append(v[0]); acc["PerLTQA"][f"H{M}"].append(v[1])
    print(f"  PerLTQA {time.time()-t0:.0f}s", flush=True)

    for f in sorted(glob.glob(R + "/regen/lme/cache_repr/*.pkl")):
        d = pickle.loads(open(f, "rb").read()); qid = d["question_id"]
        C = np.asarray(d["C"], np.float64); N = C.shape[0]
        s = qscale_scores(C, d["qC"]); g = d["gold"]
        acc["LME"]["cur"].append(current_fr3(s, g, qid))
        for M, v in ceilings(s, g, qid, N).items():
            if v: acc["LME"][f"M{M}"].append(v[0]); acc["LME"][f"H{M}"].append(v[1])

    for f in sorted(glob.glob(R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
        o = pickle.loads(open(f, "rb").read()); aid = str(o["conv_id"])
        C = np.asarray(o["C"], np.float64); N = C.shape[0]
        exp = json.loads(open(f"{DATA}/{aid}.json").read())
        docs_tok = [__import__("re").findall(r"\w+", x["text"].lower()) for x in exp["docs"]]
        avglen = sum(len(x) for x in docs_tok) / len(docs_tok)
        qtext = {q["qid"]: q["text"] for q in exp["queries"]}
        for qi, qid in enumerate(o["qids"]):
            g = [int(x) for x in o["gold_rows"][qi]]
            if not g: continue
            s = qscale_scores(C, o["QC"][qi])
            acc["REALTALK"]["cur"].append(current_fr3(s, g, aid))
            for M, v in ceilings(s, g, aid, N).items():
                if v: acc["REALTALK"][f"M{M}"].append(v[0]); acc["REALTALK"][f"H{M}"].append(v[1])
            if qid in qtext:
                sb = bm25_scores(docs_tok, __import__("re").findall(r"\w+", qtext[qid].lower()), avglen)
                acc["RT_BM25"]["cur"].append(current_fr3(sb, g, aid))
                for M, v in ceilings(sb, g, aid, N).items():
                    if v: acc["RT_BM25"][f"M{M}"].append(v[0]); acc["RT_BM25"][f"H{M}"].append(v[1])
    print(f"  REALTALK {time.time()-t0:.0f}s", flush=True)

    print("\n=== PERFECT-RERANKER CEILING on FR@3 (%) — no reranker can beat these ===")
    print("stage = 12-byte qscale codes (RT_BM25 = lexical stage, for contrast)")
    hdr = f"{'bench':10} {'n':>5} {'now':>7} " + " ".join(f"M={m:<4}".rjust(8) for m in MS)
    print(hdr)
    res = {}
    for b in ("PerLTQA", "LME", "REALTALK", "RT_BM25"):
        if not acc[b]["cur"]: continue
        cur = 100 * float(np.mean(acc[b]["cur"]))
        row = [100 * float(np.mean(acc[b][f"M{m}"])) if acc[b][f"M{m}"] else float("nan") for m in MS]
        res[b] = {"n": len(acc[b]["cur"]), "fr3_now": cur,
                  "fr3_ceiling": {str(m): row[i] for i, m in enumerate(MS)},
                  "hit_ceiling": {str(m): 100 * float(np.mean(acc[b][f"H{m}"])) for m in MS if acc[b][f"H{m}"]}}
        print(f"{b:10} {len(acc[b]['cur']):5d} {cur:7.2f} " + " ".join(f"{v:8.2f}" for v in row))

    print("\n=== HEADROOM: ceiling minus current FR@3 (pp) — the prize a perfect reranker wins ===")
    print(hdr)
    for b in res:
        row = [res[b]["fr3_ceiling"][str(m)] - res[b]["fr3_now"] for m in MS]
        print(f"{b:10} {res[b]['n']:5d} {'':>7} " + " ".join(f"{v:+8.2f}" for v in row))

    print("\n=== candidate-pool Hit ceiling (%) = is gold even IN the pool? ===")
    print(hdr)
    for b in res:
        row = [res[b]["hit_ceiling"].get(str(m), float('nan')) for m in MS]
        print(f"{b:10} {res[b]['n']:5d} {'':>7} " + " ".join(f"{v:8.2f}" for v in row))

    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                          "DISCLOSE-BEFORE-USE"],
               "what": "perfect-reranker ceiling gate for proposal idea #1",
               "stage_scorer": "qscale on existing 12-byte codes; RT_BM25 = lexical control",
               "caveat": "Ceiling assumes an ORACLE reranker with gold knowledge. Real rerankers "
                         "land far below. A low ceiling kills the idea; a high ceiling does NOT "
                         "prove a real reranker can reach it.",
               "results": res, "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, "rerank_ceiling.json"), "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
