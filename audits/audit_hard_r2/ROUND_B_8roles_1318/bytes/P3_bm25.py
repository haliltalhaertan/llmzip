"""P3: BM25 true storage from actual RealTalk corpora, both tokenizers.
READ-ONLY. Recomputes cost_audit compact encoding + pickle size + raw text.
Writes P3_bm25.json in THIS dir. Pure python3 (no sklearn)."""
import json, math, os, pickle, re
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
ARCH = [f"RT{i:02d}" for i in range(1, 11)]
WORD = re.compile(r"\w+", re.UNICODE)  # cost_audit coarse rule
FROZEN_TOKEN = re.compile(r"\b\w\w+\b")  # ladder frozen rule
STOP = set("""a about above after again against all am an and any are as at be because been before being
below between both but by could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most my
myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

def toks_coarse(s):
    return WORD.findall((s or "").lower())

def toks_frozen(s):
    return [w for w in FROZEN_TOKEN.findall((s or "").lower()) if w not in STOP]

def varint(n):
    b = 0
    while True:
        b += 1
        if n < 128:
            return b
        n >>= 7

def index_size(docs_tok):
    postings = {}
    for row, tk in enumerate(docs_tok):
        for term, tf in Counter(tk).items():
            postings.setdefault(term, {})[row] = tf
    N = len(docs_tok)
    doc_lens = [len(t) for t in docs_tok]
    idf = {t: math.log((N - len(p) + 0.5) / (len(p) + 0.5) + 1.0) for t, p in postings.items()}
    blob = pickle.dumps({"N": N, "postings": postings, "idf": idf,
                         "doc_lens": doc_lens, "avglen": sum(doc_lens) / N},
                        protocol=pickle.HIGHEST_PROTOCOL)
    comp = 0
    for t, p in postings.items():
        comp += len(t.encode("utf-8")) + 1 + varint(len(p)) + 4
        prev = -1
        for row in sorted(p):
            comp += varint(row - prev) + varint(p[row])
            prev = row
    comp += sum(varint(x) for x in doc_lens) + 8
    return {"vocab": len(postings), "pickle": len(blob), "compact": comp,
            "N": N, "ntok_total": sum(doc_lens)}

out = {"per_archive": {}, "totals": {}}
for a in ARCH:
    d = json.load(open(f"{DATA}/{a}.json", encoding="utf-8"))
    texts = [x["text"] for x in d["docs"]]
    raw_text = sum(len(t.encode("utf-8")) for t in texts)
    c = index_size([toks_coarse(t) for t in texts])
    f = index_size([toks_frozen(t) for t in texts])
    out["per_archive"][a] = {"N": c["N"], "raw_text_B": raw_text,
        "coarse": c, "frozen": f}
    print(f"{a} N={c['N']} raw={raw_text} coarse_vocab={c['vocab']} coarse_compact={c['compact']} frozen_vocab={f['vocab']} frozen_compact={f['compact']}", flush=True)
tc = sum(v["coarse"]["compact"] for v in out["per_archive"].values())
tf = sum(v["frozen"]["compact"] for v in out["per_archive"].values())
pc = sum(v["coarse"]["pickle"] for v in out["per_archive"].values())
pf = sum(v["frozen"]["pickle"] for v in out["per_archive"].values())
rt = sum(v["raw_text_B"] for v in out["per_archive"].values())
out["totals"] = {"coarse_compact": tc, "frozen_compact": tf, "coarse_pickle": pc,
                 "frozen_pickle": pf, "raw_text": rt,
                 "coarse_compact_plus_text": tc + rt, "frozen_compact_plus_text": tf + rt}
print(json.dumps(out["totals"], indent=1))
json.dump(out, open(os.path.join(HERE, "P3_bm25.json"), "w"), indent=1)
print("WROTE P3_bm25.json")
