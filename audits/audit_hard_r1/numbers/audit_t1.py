# Auditor's own T1 BM25 recomputation. Own tokenizer + own BM25 + own top-k.
# No coordinator code imported. Contract reimplemented from spec read (not copied).
import json, math, re, hashlib
import numpy as np
from collections import defaultdict

DATA = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
SALT = "top10-r1"
TOK_COARSE = re.compile(r"[a-z0-9]+")
TOK_FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a about above after again against all am an and any are as at be because been before being
below between both but by could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most my
myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

def tok_coarse(s):
    return TOK_COARSE.findall((s or "").lower())

def tok_frozen(s):
    return [w for w in TOK_FROZEN.findall((s or "").lower()) if w not in STOP]

def det_top10(scores, arch, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{SALT}|{arch}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])

class MyBM25:
    def __init__(self, docs, k1, b):
        self.k1, self.b = k1, b
        self.n = len(docs)
        self.lens = np.array([len(d) for d in docs], dtype=float)
        self.avg = self.lens.mean() if self.n else 1.0
        post = defaultdict(list)
        for i, d in enumerate(docs):
            tf = defaultdict(int)
            for w in d:
                tf[w] += 1
            for w, c in tf.items():
                post[w].append((i, c))
        self.post = dict(post)
        self.idf = {w: math.log(1.0 + (self.n - len(pl) + 0.5) / (len(pl) + 0.5))
                    for w, pl in self.post.items()}

    def score(self, q):
        s = np.zeros(self.n)
        if self.k1 == 0:
            for w in set(q):
                pl = self.post.get(w)
                if not pl:
                    continue
                v = self.idf[w]
                for i, _ in pl:
                    s[i] += v
            return s
        dl = self.k1 * (1 - self.b + self.b * self.lens / self.avg)
        for w in set(q):
            pl = self.post.get(w)
            if not pl:
                continue
            v = self.idf[w]
            k1 = self.k1
            for i, c in pl:
                s[i] += v * c * (k1 + 1) / (c + dl[i])
        return s

def run_variant(frozen, k1, b):
    hits, fr3s, nq = [], [], 0
    per_arch = {}
    for i in range(1, 11):
        aid = f"RT{i:02d}"
        d = json.load(open(f"{DATA}/{aid}.json", encoding="utf-8"))
        docs = d["docs"]
        row_of = {x["row"]: j for j, x in enumerate(docs)}
        qs = [q for q in d["queries"] if any(g in row_of for g in q.get("gold", []))]
        tk = tok_frozen if frozen else tok_coarse
        bm = MyBM25([tk(x["text"]) for x in docs], k1, b)
        h = f = 0.0
        for q in qs:
            s = bm.score(tk(q["text"]))
            top = det_top10(s, aid, 10)
            g = set(row_of[x] for x in q["gold"] if x in row_of)
            if g & set(top.tolist()):
                h += 1.0
            f += len(g & set(top[:3].tolist())) / len(g) if g else 0.0
        per_arch[aid] = (100*h/len(qs), 100*f/len(qs), len(qs))
        hits += [100*h/len(qs)] * 0  # placeholder
        hits.append((h, len(qs)))
        fr3s.append((f, len(qs)))
        nq += len(qs)
    H = 100*sum(h for h, _ in hits)/sum(n for _, n in hits)
    F = 100*sum(f for f, _ in fr3s)/sum(n for _, n in fr3s)
    return H, F, nq, per_arch

def main():
    coord = json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/coordinator/DECISION_TESTS.json",
                           encoding="utf-8"))["T1_fair_baseline"]["bm25_variants"]
    variants = {"coarse_textbook": (False, 1.2, 0.75), "frozen_textbook": (True, 1.2, 0.75),
                "coarse_idfonly": (False, 0.0, 0.0), "frozen_idfonly": (True, 0.0, 0.0)}
    res = {}
    for name, (frz, k1, b) in variants.items():
        H, F, nq, pa = run_variant(frz, k1, b)
        c = coord[name]
        res[name] = {"hit10": H, "fr3": F, "n": nq}
        print(f"{name}: audit Hit@10 {H:.6f} vs coord {c['hit10']:.6f} diff={H-c['hit10']:+.6f} | FR@3 audit {F:.6f} vs coord {c['fr3']:.6f} diff={F-c['fr3']:+.6f} n={nq}", flush=True)
    best = max(res, key=lambda v: res[v]["hit10"])
    print(f"strongest: {best} {res[best]['hit10']:.6f}")
    gap = 55.319148936170215 - res["frozen_idfonly"]["hit10"]
    print(f"24B/qscale(55.31914894) vs strongest gap: {gap:.6f} (claim -10.35460993)")
    json.dump(res, open("audit_t1_out.json", "w", encoding="utf-8"), indent=1)

if __name__ == "__main__":
    main()
