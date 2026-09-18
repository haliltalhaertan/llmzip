"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Independent lexical audit: reimplement BM25/TFIDF + protocol ranking from
data/RTxx.json exports only (no import of producer scoring), verify top10
and actual metrics exactly, recompute CORRECT expected-Hit and true boundary
ties, verify source/export alignment and unresolved annotations.

Writes ONLY to this audit/ dir; never edits ../data.
Usage: $HOME/muse-work/ml-python audit_lexical.py
Outputs: per_query_bm25_corrected.jsonl, per_query_tfidf_corrected.jsonl,
  per_query_corrected.jsonl, lexical_audit.json, source_hashes.json
"""
import glob
import hashlib
import json
import math
import os
import pickle
import re
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
R = "/mnt/c/Users/MDP/dev/llmzip-work"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
K1 = 1.5
B = 0.75
WORD_RE = re.compile(r"\w+", re.UNICODE)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tok(text):
    return WORD_RE.findall(str(text).lower())


def tie_hash(archive_id, row):
    return hashlib.sha256(f"top10-r1|{archive_id}|{row}".encode("utf-8")).hexdigest()


def rank_top10(scores, archive_id):
    safe = [s if math.isfinite(float(s)) else float("-inf") for s in scores]
    order = sorted(range(len(safe)), key=lambda r: (-safe[r], tie_hash(archive_id, r), r))
    assert len(set(order[:10])) == 10
    return order[:10]


def correct_expected_hit(scores, gold, k=10):
    s = [float(x) if math.isfinite(float(x)) else float("-inf") for x in scores]
    gset = set(int(g) for g in gold)
    assert gset
    buckets = {}
    for i, v in enumerate(s):
        buckets.setdefault(v, []).append(i)
    better = 0
    for lv in sorted(buckets.keys(), reverse=True):
        idx = buckets[lv]
        Bb = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if i in gset)
        if better + Bb <= k:
            if gb > 0:
                return 1.0
            better += Bb
        else:
            take = int(k - better)
            if gb == 0:
                return 0.0
            denom = math.comb(Bb, take)
            numer = math.comb(Bb - gb, take) if (Bb - gb) >= take else 0
            return float(1.0 - numer / denom)
    return 0.0


def tie_info(scores, gold, k=10):
    s = [float(x) if math.isfinite(float(x)) else float("-inf") for x in scores]
    gset = set(int(g) for g in gold)
    buckets = {}
    for i, v in enumerate(s):
        buckets.setdefault(v, []).append(i)
    better = 0
    for lv in sorted(buckets.keys(), reverse=True):
        idx = buckets[lv]
        Bb = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if i in gset)
        if better + Bb <= k:
            better += Bb
            continue
        return {"better": int(better), "bucket_size": int(Bb),
                "gold_in_bucket": int(gb), "take": int(k - better),
                "is_tie_at_cut": bool(Bb > 1),
                "cutoff_score": float(lv)}
    return {"better": int(min(better, k)), "bucket_size": 0,
            "gold_in_bucket": 0, "take": 0, "is_tie_at_cut": False,
            "cutoff_score": None}


def ndcg_at_10(top10, gold):
    gset = set(int(g) for g in gold)
    disc = [1.0 / math.log2(r + 2) for r in range(10)]
    idcg = sum(disc[:min(10, len(gset))])
    if idcg <= 0:
        return 0.0
    return sum(disc[r] for r, d in enumerate(top10) if int(d) in gset) / idcg


def bm25_scores(docs_tok, q_tok, avglen):
    N = len(docs_tok)
    df = Counter()
    for dt in docs_tok:
        for t in set(dt):
            df[t] += 1
    idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
    out = [0.0] * N
    for j, dt in enumerate(docs_tok):
        dl = len(dt)
        tf = Counter(dt)
        norm = K1 * (1 - B + B * dl / avglen) if avglen > 0 else K1
        tot = 0.0
        for t in set(q_tok):
            if t not in idf or tf.get(t, 0) == 0:
                continue
            f = tf[t]
            tot += idf[t] * (f * (K1 + 1) / (f + norm))
        out[j] = tot
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
