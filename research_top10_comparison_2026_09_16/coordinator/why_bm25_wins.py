"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
WHY does plain BM25 beat our pipeline? A mathematical hypothesis, and a same-budget fix.

THE OBSERVATION THAT REFRAMES EVERYTHING (RealTalk, n=705, already verified):
    float_std  (96 dims, FULL float, 384 B/doc, NO compression) = 48.51%
    sign96     (96 dims, 1 bit each,  12 B/doc, compressed)     = 46.68%
    BM25       (plain word matching)                            = 54.18%
Compression costs only 1.83 pp. BM25 beats the UNCOMPRESSED representation by 5.67 pp.
=> The bottleneck is NOT the 12-byte budget. It is the 96-dim representation itself.
   No amount of smarter bit-packing can recover information SVD already discarded.

THE MATHEMATICAL HYPOTHESIS (H1):
  TruncatedSVD keeps the directions of LARGEST VARIANCE. It is the optimal rank-96
  approximation in Frobenius norm - it minimizes reconstruction error.
  But retrieval does not need reconstruction; it needs DISCRIMINATION.
  IDF says the most discriminative terms are the RAREST ones. A rare term appears in
  few documents => it has LOW variance across the corpus => SVD discards it first.
  So SVD's objective and retrieval's objective point in OPPOSITE directions.
  BM25 does the reverse: idf = log(N/df) explicitly UP-weights exactly those rare terms.

  H1 predicts: CODE should fail disproportionately on queries whose gold document is
  identified by a RARE shared term (a name, a date, a number), and should do fine when
  the gold shares common words.

TEST 1 (diagnostic): stratify the 705 queries by the max IDF among query-gold shared
  terms. If H1 holds, the CODE-vs-BM25 gap widens monotonically with rarity.

TEST 2 (same-budget fix): if H1 holds, spend part of the SAME 96 bits on rare terms.
    SPLIT_k: first k bits = sign of top-k SVD dims; remaining (96-k) bits = a Bloom
    sketch of the document's highest-IDF terms.
  Total stays EXACTLY 12 bytes. Arms: k=96 (current), 80, 64, 48.
  Fusion rule fixed BEFORE running: RRF with k_rrf=60 over (svd-part rank, bloom rank),
  the same constant already used elsewhere in this programme. No tuning.
  IDF and Bloom are built from DOCUMENTS ONLY - never from queries or gold.
"""
import hashlib, json, math, os, re, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
from audit_baseline_lib import det_top10, hrn

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
RT = R + "/bench3/runs/b3a_realtalk/rt_repr"
WORD = re.compile(r"\w+", re.UNICODE)
ARCH = [f"RT{i:02d}" for i in range(1, 11)]
RRF_K = 60
SPLITS = [96, 80, 64, 48]
BLOOM_TERMS = 8          # doc's top-IDF terms written into the sketch (fixed pre-run)


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
    strat = defaultdict(lambda: {"code": [], "bm25": [], "n": 0})
    split_res = {k: {"hit10": [], "fr3": []} for k in SPLITS}
    rows_out = []

    for a in ARCH:
        exp = json.load(open(f"{DATA}/{a}.json", encoding="utf-8"))
        import pickle
        o = pickle.loads(open(f"{RT}/{a}.pkl", "rb").read())
        C = np.asarray(o["C"], np.float64)
        N = C.shape[0]
        docs = [x["text"] for x in exp["docs"]]
        dtok = [toks(t) for t in docs]

        # --- IDF from DOCUMENTS ONLY ---
        df = Counter()
        for dt in dtok:
            for t in set(dt):
                df[t] += 1
        idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
        avglen = sum(len(d) for d in dtok) / N

        # --- per-doc bloom source: its own highest-IDF terms ---
        doc_rare = []
        for dt in dtok:
            uniq = sorted(set(dt), key=lambda t: (-idf.get(t, 0.0), t))[:BLOOM_TERMS]
            doc_rare.append(uniq)

        sg = np.maximum(np.std(C, axis=0, ddof=0), 1e-12)
        qmap = {q["qid"]: q for q in exp["queries"]}

        for qi, qid in enumerate(o["qids"]):
            gold = [int(x) for x in o["gold_rows"][qi]]
            if not gold or qid not in qmap:
                continue
            q = qmap[qid]
            qt = toks(q["text"])
            qC = np.asarray(o["QC"][qi], np.float64)

            # ---- current CODE (qscale, all 96 bits) ----
            Bfull = np.where(C >= 0, 1.0, -1.0)
            s_code = Bfull @ (qC / sg)
            code_hit = hrn(det_top10(s_code, a, 10), gold, 10)[0]

            # ---- BM25 ----
            qtf = Counter(qt)
            s_bm = np.zeros(N)
            for j, dt in enumerate(dtok):
                tf = Counter(dt); nrm = 1.5 * (1 - 0.75 + 0.75 * len(dt) / avglen); sc = 0.0
                for t in qtf:
                    if t in idf and tf.get(t, 0):
                        f = tf[t]; sc += idf[t] * (f * 2.5 / (f + nrm))
                s_bm[j] = sc
            bm_hit = hrn(det_top10(s_bm, a, 10), gold, 10)[0]

            # ---- TEST 1 stratify by rarity of the query-gold shared terms ----
            shared = set(qt).intersection(*[set(dtok[g]) for g in gold]) if len(gold) == 1 \
                     else set(qt).intersection(set(dtok[gold[0]]))
            mx = max([idf[t] for t in shared if t in idf], default=0.0)
            band = ("no_shared" if not shared else
                    "common"   if mx < 2.0 else
                    "mid"      if mx < 4.0 else
                    "rare")
            strat[band]["code"].append(code_hit)
            strat[band]["bm25"].append(bm_hit)
            strat[band]["n"] += 1

            # ---- TEST 2 same-budget split codes ----
            for k in SPLITS:
                nb = 96 - k
                if nb == 0:
                    s = s_code
                else:
                    svd_part = np.where(C[:, :k] >= 0, 1.0, -1.0) @ (qC[:k] / sg[:k])
                    DB = np.array([bloom_bits(doc_rare[j], nb) for j in range(N)])
                    qr = [t for t in set(qt) if idf.get(t, 0.0) >= 2.0]
                    QB = bloom_bits(qr, nb)
                    bloom_part = (DB & QB[None, :]).sum(axis=1).astype(float)
                    r1 = {int(d): i for i, d in enumerate(det_top10(svd_part, a, N))}
                    r2 = {int(d): i for i, d in enumerate(det_top10(bloom_part, a, N))}
                    s = np.array([1.0 / (RRF_K + r1[j] + 1) + 1.0 / (RRF_K + r2[j] + 1)
                                  for j in range(N)])
                top = det_top10(s, a, 10)
                h, rc, nd = hrn(top, gold, 10)
                split_res[k]["hit10"].append(h)
                g3 = set(gold).intersection(int(x) for x in top[:3].tolist())
                split_res[k]["fr3"].append(len(g3) / len(gold))
            rows_out.append({"qid": qid, "archive_id": a, "band": band, "max_idf": mx,
                             "code_hit": code_hit, "bm25_hit": bm_hit})
        print(f"  {a} done {time.time()-t0:.0f}s", flush=True)

    print("\n=== TEST 1: does CODE fail on RARE-term queries? (Hit@10 %) ===")
    print(f"{'rarity band':12} {'n':>5} {'CODE':>8} {'BM25':>8} {'BM25-CODE':>10}")
    order = ["no_shared", "common", "mid", "rare"]
    t1 = {}
    for b in order:
        d = strat[b]
        if not d["n"]:
            continue
        c = 100 * float(np.mean(d["code"])); m = 100 * float(np.mean(d["bm25"]))
        t1[b] = {"n": d["n"], "code": c, "bm25": m, "gap": m - c}
        print(f"{b:12} {d['n']:5d} {c:8.2f} {m:8.2f} {m-c:+10.2f}")

    print("\n=== TEST 2: same 12 bytes, split between SVD bits and rare-term bits ===")
    print(f"{'svd bits':>9} {'bloom bits':>11} {'Hit@10':>9} {'FR@3':>9}")
    t2 = {}
    for k in SPLITS:
        h = 100 * float(np.mean(split_res[k]["hit10"]))
        f = 100 * float(np.mean(split_res[k]["fr3"]))
        t2[k] = {"hit10": h, "fr3": f}
        print(f"{k:9d} {96-k:11d} {h:9.2f} {f:9.2f}")

    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                          "DISCLOSE-BEFORE-USE"],
               "hypothesis": "SVD maximizes variance; IDF says rare=informative; rare terms are "
                             "low-variance so SVD discards exactly the discriminative signal.",
               "anchor_facts": {"float_std_no_compression": 48.51, "sign96_12B": 46.68,
                                "bm25": 54.18,
                                "reading": "compression costs 1.83pp; BM25 beats the "
                                           "UNCOMPRESSED representation by 5.67pp"},
               "test1_rarity_strata": t1, "test2_same_budget_split": t2,
               "bloom_terms_per_doc": BLOOM_TERMS, "rrf_k": RRF_K,
               "caveats": ["RealTalk only, 10 clusters, exploratory",
                           "Bloom/IDF fitted on DOCUMENTS ONLY, no gold or query fitting",
                           "split arms keep total payload at exactly 12 bytes",
                           "no CI computed here; this is a direction-finding probe"],
               "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, "why_bm25_wins.json"), "w"), indent=2)
    with open(os.path.join(HERE, "why_bm25_per_query.jsonl"), "w") as f:
        for r in rows_out:
            f.write(json.dumps(r) + "\n")
    print(f"\nelapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
