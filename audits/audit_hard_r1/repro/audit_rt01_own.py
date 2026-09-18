"""OWN audit code: independent BM25 + deterministic ranking on RT01 (frozen_idfonly).

Does not import decision_tests_copy or audit_baseline_lib. Reimplements from the
documented contract: frozen tokens \b\w\w+\b minus English stopwords, IDF-only
(k1=0 -> score = sum of idf over matched terms), tie-break descending score then
ascending SHA256('top10-r1|'+archive+'|'+row) then row (PROTOCOL.md).
Compares against the copied pipeline restricted to RT01 (which uses lib.det_top10).
"""
import hashlib, json, math, re
from collections import defaultdict
import numpy as np

RT = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
AID = "RT01"
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a about above after again against all am an and any are as at be because been before
being below between both but by could did do does doing down during each few for from further had has
have having he her here hers herself him himself his how i if in into is it its itself just me more most
my myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

D = json.load(open(f"{RT}/{AID}.json", encoding="utf-8"))
docs = D["docs"]
row_of = {d["row"]: j for j, d in enumerate(docs)}
qs = [q for q in D["queries"] if any(g in row_of for g in q.get("gold", []))]
print(f"RT01: {len(docs)} docs, {len(qs)} valid-gold queries")

def toks(s):
    return [w for w in FROZEN.findall((s or "").lower()) if w not in STOP]

tok_docs = [toks(d["text"]) for d in docs]
N = len(tok_docs)
post = defaultdict(list)
for i, d in enumerate(tok_docs):
    tf = defaultdict(int)
    for w in d:
        tf[w] += 1
    for w, c in tf.items():
        post[w].append((i, c))
idf = {w: math.log(1 + (N - len(pl) + .5) / (len(pl) + .5)) for w, pl in post.items()}

# own deterministic top-10
order_key = {}
def own_topk(scores, k):
    s = np.asarray(scores, float).ravel()
    key = []
    for r in range(len(s)):
        h = hashlib.sha256(f"top10-r1|{AID}|{r}".encode()).hexdigest()
        key.append((0 if np.isfinite(s[r]) else 1, -s[r], h, r))
    return [r for _, _, _, r in sorted(key)][:k]

hits = 0
for q in qs:
    s = np.zeros(N)
    for w in set(toks(q["text"])):
        pl = post.get(w)
        if not pl:
            continue
        for i, c in pl:
            s[i] += idf[w]  # k1 = 0
    top = own_topk(s, 10)
    g = {row_of[x] for x in q["gold"] if x in row_of}
    hits += 1.0 if (g & set(top)) else 0.0
own_hit = 100 * hits / len(qs)
print(f"OWN RT01 frozen_idfonly Hit@10 = {own_hit:.4f} (n={len(qs)})")

# copied pipeline restricted to RT01 (uses lib.det_top10)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "lib", "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/audit/audit_baseline_lib.py")
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)
TOKEN = re.compile(r"[a-z0-9]+")
FROZ2 = re.compile(r"\b\w\w+\b")
def toks2(s):
    return [w for w in FROZ2.findall((s or "").lower()) if w not in STOP]
class BM25:
    def __init__(self, docs, k1, b):
        self.k1, self.b, self.N = k1, b, len(docs)
        self.len = np.array([len(d) for d in docs], float)
        self.avg = self.len.mean()
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
        for w in set(q):
            pl = self.post.get(w)
            if not pl:
                continue
            for i, c in pl:
                s[i] += self.idf[w]
        return s
bm = BM25([toks2(d["text"]) for d in docs], 0.0, 0.0)
hits2 = 0
for qi, q in enumerate(qs):
    top = lib.det_top10(bm.score(toks2(q["text"])), AID, 10)
    g = {row_of[x] for x in q["gold"] if x in row_of}
    hits2 += 1.0 if (g & set(top)) else 0.0
copy_hit = 100 * hits2 / len(qs)
print(f"COPY RT01 frozen_idfonly Hit@10 = {copy_hit:.4f} (n={len(qs)})")
print(f"DIFF = {abs(own_hit - copy_hit):.2e} -> {'MATCH' if own_hit == copy_hit else 'MISMATCH'}")
