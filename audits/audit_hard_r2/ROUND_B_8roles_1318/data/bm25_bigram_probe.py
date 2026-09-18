#!/usr/bin/env python3
"""E-probe: BM25 with word bigrams (code's word channel uses 1-2 grams; T1 BM25 uses uni only).
Plus dup-twin hit check. READ-ONLY sources; writes OUT only."""
import json, re, math, hashlib
from collections import Counter, defaultdict

OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/data"
W = "/mnt/c/Users/MDP/dev/llmzip-work"
RT = f"{W}/top10_comparison_r1/data"

FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a about above after again against all am an and any are as at be because been before
being below between both but by could did do does doing down during each few for from further had has
have having he her here hers herself him himself his how i if in into is it its itself just me more most
my myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

def uni(s):
    return [w for w in FROZEN.findall((s or "").lower()) if w not in STOP]

def uni_bi(s):
    u = uni(s)
    return u + [a + " " + b for a, b in zip(u, u[1:])]

class BM25:
    def __init__(self, docs, k1, b):
        self.k1, self.b, self.N = k1, b, len(docs)
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / self.N if self.N else 1.0
        self.post = defaultdict(list)
        for i, d in enumerate(docs):
            tf = Counter(d)
            for w, c in tf.items():
                self.post[w].append((i, c))
        self.idf = {w: math.log(1 + (self.N - len(pl) + .5) / (len(pl) + .5)) for w, pl in self.post.items()}

    def score(self, q):
        s = [0.0] * self.N
        for w in set(q):
            pl = self.post.get(w)
            if not pl:
                continue
            idf = self.idf[w]
            for i, c in pl:
                if self.k1 == 0:
                    s[i] += idf
                else:
                    dl = self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
                    s[i] += idf * c * (self.k1 + 1) / (c + dl)
        return s

def det_top10(scores, aid, k=10):
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(scores))]
    return sorted(range(len(scores)), key=lambda r: (-scores[r], hs[r], r))[:k]

res = {}
for toks_fn, nm in ((uni, "frozen_uni_idfonly"), (uni_bi, "frozen_uniBI_idfonly")):
    hits = 0
    n = 0
    for i in range(1, 11):
        aid = f"RT{i:02d}"
        D = json.load(open(f"{RT}/{aid}.json", encoding="utf-8"))
        docs = D["docs"]
        bm = BM25([toks_fn(d["text"]) for d in docs], 0.0, 0.0)
        for q in D["queries"]:
            s = bm.score(toks_fn(q["text"]))
            top = det_top10(s, aid)
            g = set(int(x) for x in q["gold"])
            hits += 1.0 if (g & set(top)) else 0.0
            n += 1
    res[nm] = {"hit10": 100 * hits / n, "n": n}
    print(f"{nm}: Hit@10 {100*hits/n:.4f} (n={n})", flush=True)

# dup-twin check: non-gold doc with text identical to a gold doc, per query
twin_q = 0
twin_pairs = 0
for i in range(1, 11):
    aid = f"RT{i:02d}"
    D = json.load(open(f"{RT}/{aid}.json", encoding="utf-8"))
    by_text = defaultdict(list)
    for d in D["docs"]:
        by_text[d["text"]].append(d["row"])
    for q in D["queries"]:
        g = set(int(x) for x in q["gold"])
        tw = 0
        for x in list(g):
            t = next(d["text"] for d in D["docs"] if d["row"] == x)
            tw += sum(1 for r in by_text[t] if r not in g)
        if tw:
            twin_q += 1
            twin_pairs += tw
print(f"twin queries: {twin_q}/705, total twin pairs: {twin_pairs}", flush=True)
res["twins"] = {"queries_with_nongold_twin": twin_q, "twin_pairs": twin_pairs}

json.dump(res, open(f"{OUT}/audit_bm25_bigram_probe.json", "w"), indent=1)
print("WROTE audit_bm25_bigram_probe.json", flush=True)
