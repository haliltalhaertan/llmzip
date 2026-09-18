#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Top10-r1 DATA worker: BM25 + TFIDF lexical controls on the SAME 705 queries.
Reads ONLY this dir's RTxx.json exports. Writes per_query_*.jsonl here.
No model downloads, no refit of old encoders. Per-archive fit on DOCUMENTS ONLY.
Zero-vector handling (declared before run): empty token sequence -> zero vector;
TFIDF zero-norm rows score 0; nonfinite scores map to -inf (worst). Higher better.
Deterministic protocol tie rule: descending score, ascending
SHA256('top10-r1|'+archive_id+'|'+str(row)), ascending row. Exactly 10 IDs.
Usage: $HOME/muse-work/ml-python run_lexical.py
"""
import hashlib
import json
import math
import os
import re
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "tdd_lexical.log")
K1 = 1.5
B = 0.75
WORD_RE = re.compile(r"\w+", re.UNICODE)


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)


def tok(text):
    return WORD_RE.findall(str(text).lower())


def tie_key(archive_id):
    def h(row):
        return hashlib.sha256(
            f"top10-r1|{archive_id}|{row}".encode("utf-8")).hexdigest()
    return h


def rank_top10(scores, archive_id):
    """scores: list[float] len N. Returns exactly 10 row indices, protocol order."""
    import math as _m
    safe = [s if _m.isfinite(s) else float("-inf") for s in scores]
    h = tie_key(archive_id)
    order = sorted(range(len(safe)),
                   key=lambda r: (-safe[r], h(r), r))
    assert len(set(order[:10])) == 10
    return order[:10]


def expected_hit(scores, gold):
    """Exact expected Hit@10 under uniform within-bucket tiebreak (tie-sensitivity)."""
    import math as _m
    s = [x if _m.isfinite(x) else float("-inf") for x in scores]
    gset = set(int(g) for g in gold)
    assert gset
    buckets = {}
    for i, v in enumerate(s):
        buckets.setdefault(v, []).append(i)
    better, exp = 0, 0.0
    for lv in sorted(buckets.keys(), reverse=True):
        idx = buckets[lv]
        if better >= 10:
            break
        gb = sum(1 for i in idx if i in gset)
        if better + len(idx) <= 10:
            exp += gb
        else:
            exp += (10 - better) * gb / len(idx)
            break
        better += len(idx)
    return exp / len(gset)


def ndcg_at_10(top10, gold):
    gset = set(int(g) for g in gold)
    disc = [1.0 / math.log2(r + 2) for r in range(10)]
    idcg = sum(disc[:min(10, len(gset))])
    if idcg <= 0:
        return 0.0
    return sum(disc[r] for r, d in enumerate(top10)
               if int(d) in gset) / idcg


def bm25_scores(docs_tok, q_tok, avglen):
    N = len(docs_tok)
    df = Counter()
    for dt in docs_tok:
        for t in set(dt):
            df[t] += 1
    idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0)
           for t, c in df.items()}
    qtf = Counter(q_tok)
    out = [0.0] * N
    for j, dt in enumerate(docs_tok):
        dl = len(dt)
        tf = Counter(dt)
        s = 0.0
        norm = K1 * (1 - B + B * dl / avglen) if avglen > 0 else K1
        for t, qn in qtf.items():
            if t not in idf or tf.get(t, 0) == 0:
                continue
            f = tf[t]
            s += idf[t] * (f * (K1 + 1) / (f + norm))
        out[j] = s
    return out


def tfidf_scores(docs_tok, q_tok):
    N = len(docs_tok)
    df = Counter()
    for dt in docs_tok:
        for t in set(dt):
            df[t] += 1
    idf = {t: math.log((1 + N) / (1 + c)) + 1.0 for t, c in df.items()}
    dtf = [Counter(d) for d in docs_tok]
    qtf = Counter(q_tok)
    qn = math.sqrt(sum((c * idf.get(t, 0.0)) ** 2 for t, c in qtf.items()))
    out = []
    for j in range(N):
        num = 0.0
        den2 = 0.0
        for t, c in dtf[j].items():
            w = c * idf[t]
            den2 += w * w
            if t in qtf:
                num += w * (qtf[t] * idf[t])
        den = math.sqrt(den2) * qn
        out.append(num / den if den > 0 else 0.0)
    return out


def main():
    t0 = time.time()
    if os.path.exists(LOG):
        os.remove(LOG)
    assert os.path.exists(os.path.join(HERE, "EXPORT_DONE.json")), \
        "export must finish first"
    arms = {"bm25": bm25_scores, "tfidf": tfidf_scores}
    combined = open(os.path.join(HERE, "per_query.jsonl"), "w", encoding="utf-8")
    summary = {}
    for arm in ("bm25", "tfidf"):
        fp = open(os.path.join(HERE, f"per_query_{arm}.jsonl"), "w",
                  encoding="utf-8")
        n = h = 0
        rsum = nsum = esum = 0.0
        t_arm = time.time()
        for i in range(1, 11):
            aid = f"RT{i:02d}"
            exp = json.load(open(os.path.join(HERE, aid + ".json"),
                                 encoding="utf-8"))
            docs = [d["text"] for d in exp["docs"]]
            N = len(docs)
            docs_tok = [tok(d) for d in docs]
            avglen = sum(len(d) for d in docs_tok) / N
            for q in exp["queries"]:
                qt = tok(q["text"])
                if arm == "bm25":
                    scores = bm25_scores(docs_tok, qt, avglen)
                else:
                    scores = tfidf_scores(docs_tok, qt)
                assert len(scores) == N
                assert all(math.isfinite(s) for s in scores), \
                    f"{aid} {q['qid']} nonfinite {arm}"
                top = rank_top10(scores, aid)
                g = [int(x) for x in q["gold"]]
                inter = len(set(g).intersection(top))
                row = {"arm": arm, "archive_id": aid,
                       "source_file": exp["source_file"], "qid": q["qid"],
                       "category": q["category"], "N": N, "gold": g,
                       "gold_size": len(g), "top10": [int(x) for x in top],
                       "top10_scores": [float(scores[x]) for x in top],
                       "hit_at_10": int(inter > 0),
                       "recall_at_10": inter / len(g),
                       "ndcg_at_10": ndcg_at_10(top, g),
                       "expected_hit_at_10": expected_hit(scores, g)}
                fp.write(json.dumps(row, ensure_ascii=False) + "\n")
                combined.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
                h += row["hit_at_10"]
                rsum += row["recall_at_10"]
                nsum += row["ndcg_at_10"]
                esum += row["expected_hit_at_10"]
        fp.close()
        summary[arm] = {"n": n, "hit_at_10": h / n, "recall_at_10": rsum / n,
                        "ndcg_at_10": nsum / n,
                        "expected_hit_at_10": esum / n,
                        "elapsed_s": time.time() - t_arm}
        log(f"{arm}: n={n} hit@10={h / n:.4f} recall@10={rsum / n:.4f} "
            f"ndcg@10={nsum / n:.4f} expHit@10={esum / n:.4f}")
        assert n == 705, (arm, n)
    combined.close()
    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                          "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
               "tokenizer": "lowercased Unicode word regex \\w+",
               "bm25": {"k1": K1, "b": B,
                        "idf": "log((N-df+0.5)/(df+0.5)+1)",
                        "fit": "per-archive DOCUMENTS ONLY"},
               "tfidf": {"tf": "raw count",
                         "idf": "log((1+N)/(1+df))+1 (smooth)",
                         "score": "cosine, zero-norm rows score 0",
                         "fit": "per-archive DOCUMENTS ONLY (idf from docs)"},
               "tie_rule": "desc score, asc SHA256('top10-r1|archive|row'), "
                           "asc row; exactly 10; gold-unaware",
               "zero_vector": "empty token seq -> zero vector; "
                              "nonfinite -> -inf (none observed)",
               "arms": summary,
               "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, "lexical_summary.json"), "w"), indent=2)
    log(f"LEXICAL DONE elapsed={time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
