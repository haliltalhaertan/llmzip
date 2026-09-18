"""Own audit: Claim 6 — fair BM25 65.67.

Attack: IDF-only (k1=0,b=0) is a BM25 COMPONENT, not BM25; real BM25 is k1=1.2,b=0.75.
Question: does the program's "we beat BM25" claim survive against GENUINE BM25?

Own code throughout: own tokenizers (coarse [a-z0-9]+ vs frozen \\b\\w\\w+\\b +
English stopwords — same published CONTRACT, my implementation), own BM25
(k1=1.2/b=0.75 textbook vs k1=0/b=0 sum-of-IDF limit), own stable-sort top-10,
Hit@10 + FR@3 micro-averaged on read-only top10_comparison_r1/data (exact n=705
cohort via same gold-in-row filter as ladder.py).

Reports: (a) do I reproduce the ordering/handicap pattern? (b) does code lose to
genuine frozen+textbook BM25 too? (c) is IDF-only a legitimate "BM25" label?
"""
import json, math, re, time
import numpy as np
from collections import defaultdict

DATA = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
T0 = time.time(); DEADLINE = 160
TOKEN = re.compile(r"[a-z0-9]+")
FROZEN_TOKEN = re.compile(r"\b\w\w+\b")
STOP = set("""a about above after again against all am an and any are as at be because been before being
below between both but by could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most my
myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

def toks(s, frozen):
    if frozen:
        return [w for w in FROZEN_TOKEN.findall((s or "").lower()) if w not in STOP]
    return TOKEN.findall((s or "").lower())

class BM25:
    def __init__(self, docs, k1, b):
        self.k1, self.b = k1, b
        self.N = len(docs)
        self.dlen = np.array([len(d) for d in docs], float)
        self.avg = self.dlen.mean() if self.N else 1.0
        self.post = defaultdict(list)
        for i, d in enumerate(docs):
            tf = defaultdict(int)
            for w in d:
                tf[w] += 1
            for w, c in tf.items():
                self.post[w].append((i, c))
        self.idf = {w: math.log(1.0 + (self.N - len(pl) + 0.5) / (len(pl) + 0.5))
                    for w, pl in self.post.items()}

    def score(self, q):
        s = np.zeros(self.N)
        if self.k1 == 0:
            for w in set(q):
                pl = self.post.get(w)
                if not pl:
                    continue
                for i, _ in pl:
                    s[i] += self.idf[w]
            return s
        dl = self.k1 * (1 - self.b + self.b * self.dlen / self.avg)
        for w in set(q):
            pl = self.post.get(w)
            if not pl:
                continue
            idf = self.idf[w]
            for i, c in pl:
                s[i] += idf * c * (self.k1 + 1) / (c + dl[i])
        return s

VARIANTS = {"coarse_textbook": (False, 1.2, 0.75), "frozen_textbook": (True, 1.2, 0.75),
            "coarse_idfonly": (False, 0.0, 0.0), "frozen_idfonly": (True, 0.0, 0.0)}
acc = {v: [0.0, 0.0, 0] for v in VARIANTS}  # hit, fr3, n
for i in range(1, 11):
    if time.time() - T0 > DEADLINE:
        print(f"TIME CAP at RT{i:02d}; partials preserved"); break
    aid = f"RT{i:02d}"
    D = json.load(open(f"{DATA}/{aid}.json", encoding="utf-8"))
    docs = D["docs"]
    row_of = {d["row"]: j for j, d in enumerate(docs)}
    qs = [q for q in D["queries"] if any(g in row_of for g in q.get("gold", []))]
    gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
    for v, (frz, k1, b) in VARIANTS.items():
        bm = BM25([toks(d["text"], frz) for d in docs], k1, b)
        for qi, q in enumerate(qs):
            s = bm.score(toks(q["text"], frz))
            order = np.argsort(-s, kind="stable")[:10]
            g = set(gold[qi])
            acc[v][0] += 1.0 if (g & set(order.tolist())) else 0.0
            acc[v][1] += len(g & set(order[:3].tolist())) / len(g)
            acc[v][2] += 1
print(f"n={sum(v[2] for v in acc.values())//4}")
mine = {}
for v in VARIANTS:
    h, f, n = acc[v]
    mine[v] = (100 * h / n, 100 * f / n)
    print(f"  BM25 {v:16s} Hit@10={mine[v][0]:6.2f} FR@3={mine[v][1]:6.2f}")
PUBL = json.load(open(f"{PUB}/coordinator/DECISION_TESTS.json"))["T1_fair_baseline"]["bm25_variants"]
print("published: " + "; ".join(f"{v} {PUBL[v]['hit10']:.2f}" for v in VARIANTS))
best = max(mine, key=lambda v: mine[v][0])
print(f"my strongest: {best} {mine[best][0]:.2f} "
      f"(published: frozen_idfonly 65.67; handicap coarse_textbook->best: "
      f"mine {mine[best][0]-mine['coarse_textbook'][0]:+.2f} vs publ +10.35)")
print(f"code 12B qscale Hit@10=49.65 vs my genuine frozen_textbook={mine['frozen_textbook'][0]:.2f} "
      f"-> gap {49.65-mine['frozen_textbook'][0]:+.2f} (publ textbook gap was quoted vs 55.32)")
print(f"code 48B qscale Hit@10=57.87 vs my genuine frozen_textbook -> gap "
      f"{57.87-mine['frozen_textbook'][0]:+.2f}")
