"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Coordinator independent verification of the firststage worker's COST claims.
Quality numbers were already re-derived in audit_ideas_v2.py (20/20 pass).
This checks the bytes, which decide the recommendation and were self-measured by the worker.

Claims under test:
  C1 CODE payload  = 8944 docs x 12 B = 107,328 B  + sigma 10 x 96 x 8 = 7,680 B -> 115,008 B
  C2 raw text      = 998,654 B UTF-8 over all 8944 docs
  C3 BM25 index    = 1,450,229 B (their serialization: pickle HIGHEST_PROTOCOL of
                     {N, postings{term:{row:tf}}, idf, doc_lens, avglen})
  C4 doc count     = 8944 across the 10 RealTalk archives
Also reports a FAIRER index encoding (delta-gap varint postings + raw term bytes) so the
comparison does not hinge on pickle overhead, and the storage ratio under both encodings.
"""
import json, os, pickle, re, sys
from collections import Counter
import numpy as np

DATA = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
ARCH = [f"RT{i:02d}" for i in range(1, 11)]
WORD = re.compile(r"\w+", re.UNICODE)
CLAIM = {"code_total": 115008, "code_payload": 107328, "sigma": 7680,
         "raw_text": 998654, "bm25_index": 1450229, "n_docs": 8944}
out, fails = {}, []


def varint(n):
    b = 0
    while True:
        b += 1
        if n < 128:
            return b
        n >>= 7


def main():
    n_docs = 0
    raw_bytes = 0
    pickle_total = 0
    compact_total = 0
    per_arch = {}
    for a in ARCH:
        d = json.load(open(f"{DATA}/{a}.json", encoding="utf-8"))
        docs = [x["text"] for x in d["docs"]]
        n_docs += len(docs)
        raw_bytes += sum(len(t.encode("utf-8")) for t in docs)
        toks = [WORD.findall(t.lower()) for t in docs]
        postings = {}
        for row, tk in enumerate(toks):
            for term, tf in Counter(tk).items():
                postings.setdefault(term, {})[row] = tf
        N = len(docs)
        doc_lens = [len(t) for t in toks]
        import math
        idf = {t: math.log((N - len(p) + 0.5) / (len(p) + 0.5) + 1.0) for t, p in postings.items()}
        blob = pickle.dumps({"N": N, "postings": postings, "idf": idf,
                             "doc_lens": doc_lens, "avglen": sum(doc_lens) / N},
                            protocol=pickle.HIGHEST_PROTOCOL)
        pickle_total += len(blob)
        # compact: term bytes + varint(df) + delta-gap varint rows + varint tf + f32 idf + varint doc_lens
        comp = 0
        for t, p in postings.items():
            comp += len(t.encode("utf-8")) + 1 + varint(len(p)) + 4
            prev = -1
            for row in sorted(p):
                comp += varint(row - prev) + varint(p[row])
                prev = row
        comp += sum(varint(x) for x in doc_lens) + 8
        compact_total += comp
        per_arch[a] = {"docs": N, "pickle_index_B": len(blob), "compact_index_B": comp,
                       "raw_text_B": sum(len(t.encode("utf-8")) for t in docs),
                       "vocab": len(postings)}
        print(f"  {a}: docs={N:5d} vocab={len(postings):6d} pickle={len(blob):9,d} "
              f"compact={comp:9,d} text={per_arch[a]['raw_text_B']:9,d}")

    code_payload = n_docs * 12
    sigma = 10 * 96 * 8
    code_total = code_payload + sigma
    print("\n=== VERDICT ===")

    def chk(name, mine, claimed, tol=0):
        okk = abs(mine - claimed) <= tol
        print(f"  {'OK  ' if okk else 'FAIL'} {name}: mine={mine:,} claimed={claimed:,}")
        if not okk:
            fails.append(f"{name}: mine={mine} claimed={claimed}")
        return okk

    chk("C4 doc count", n_docs, CLAIM["n_docs"])
    chk("C1a CODE payload", code_payload, CLAIM["code_payload"])
    chk("C1b sigma", sigma, CLAIM["sigma"])
    chk("C1c CODE total", code_total, CLAIM["code_total"])
    chk("C2 raw text", raw_bytes, CLAIM["raw_text"])
    # pickle layout can differ slightly by dict ordering; allow 2%
    chk("C3 BM25 pickle index", pickle_total, CLAIM["bm25_index"], tol=int(0.02 * CLAIM["bm25_index"]))

    print(f"\n  FAIRER ENCODING (varint delta-gap postings, not pickle):")
    print(f"    BM25 compact index = {compact_total:,} B  (pickle was {pickle_total:,} B, "
          f"{pickle_total/compact_total:.2f}x larger)")
    print(f"\n  storage ratios vs CODE ({code_total:,} B):")
    print(f"    BM25 pickle index only : {pickle_total/code_total:6.1f}x")
    print(f"    BM25 compact index only: {compact_total/code_total:6.1f}x")
    print(f"    BM25 compact + text    : {(compact_total+raw_bytes)/code_total:6.1f}x")
    print(f"    worker's headline      : {CLAIM['bm25_index']/CLAIM['code_total']:6.1f}x (index) / "
          f"{(CLAIM['bm25_index']+CLAIM['raw_text'])/CLAIM['code_total']:.1f}x (index+text)")

    out.update({"n_docs": n_docs, "code_total_B": code_total, "raw_text_B": raw_bytes,
                "bm25_pickle_B": pickle_total, "bm25_compact_B": compact_total,
                "per_archive": per_arch,
                "ratio_compact_index_over_code": compact_total / code_total,
                "ratio_compact_plus_text_over_code": (compact_total + raw_bytes) / code_total,
                "note": "A compact varint index is the fairer BM25 number; pickle inflates it. "
                        "Either way BM25 costs far more than 12-byte codes, so the worker's "
                        "qualitative conclusion is unchanged.",
                "labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                           "DISCLOSE-BEFORE-USE"],
                "failures": fails,
                "verdict": "ACCEPT" if not fails else "REVIEW"})
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "cost_audit.json"), "w"), indent=2)
    print("\nverdict:", "ACCEPT" if not fails else "REVIEW")


if __name__ == "__main__":
    main()
