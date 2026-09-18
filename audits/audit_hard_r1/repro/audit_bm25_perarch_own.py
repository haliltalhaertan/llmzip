"""OWN audit code: per-archive BM25 variant winners on RealTalk (selection-bias check).

If the global 'frozen_idfonly' winner is best on most archives, selection generalizes;
if winners scatter, best-of-4 on seen gold overfits and the +10.35pp handicap is inflated.
Independent implementation (own tokenizer/BM25/tie-break, TIE_SALT top10-r1).
"""
import hashlib, json, math, re
from collections import defaultdict
import numpy as np

RT = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
FROZEN = re.compile(r"\b\w\w+\b")
TOKEN = re.compile(r"[a-z0-9]+")
STOP = set("""a about above after again against all am an and any are as at be because been before
being below between both but by could did do does doing down during each few for from further had has
have having he her here hers herself him himself his how i if in into is it its itself just me more most
my myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

def toks(s, frz):
    if frz:
        return [w for w in FROZEN.findall((s or "").lower()) if w not in STOP]
    return TOKEN.findall((s or "").lower())

def topk(scores, aid, k=10):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k]

variants = {"coarse_textbook": (False, 1.2, 0.75), "frozen_textbook": (True, 1.2, 0.75),
            "coarse_idfonly": (False, 0.0, 0.0), "frozen_idfonly": (True, 0.0, 0.0)}
print(f"{'arch':6s} {'nq':>4s} " + " ".join(f"{v:>16s}" for v in variants) + "  winner")
wins = defaultdict(int)
for i in range(1, 11):
    aid = f"RT{i:02d}"
    D = json.load(open(f"{RT}/{aid}.json", encoding="utf-8"))
    docs = D["docs"]
    row_of = {d["row"]: j for j, d in enumerate(docs)}
    qs = [q for q in D["queries"] if any(g in row_of for g in q.get("gold", []))]
    line = f"{aid:6s} {len(qs):4d} "
    best, bv = None, -1
    for v, (frz, k1, b) in variants.items():
        td = [toks(d["text"], frz) for d in docs]
        N = len(td)
        post = defaultdict(list)
        for j, d in enumerate(td):
            tf = defaultdict(int)
            for w in d:
                tf[w] += 1
            for w, c in tf.items():
                post[w].append((j, c))
        idf = {w: math.log(1 + (N - len(pl) + .5) / (len(pl) + .5)) for w, pl in post.items()}
        lens = np.array([len(d) for d in td], float)
        avg = lens.mean()
        h = 0
        for q in qs:
            s = np.zeros(N)
            dl = None if k1 == 0 else k1 * (1 - b + b * lens / avg)
            for w in set(toks(q["text"], frz)):
                pl = post.get(w)
                if not pl:
                    continue
                for j, c in pl:
                    s[j] += idf[w] if k1 == 0 else idf[w] * c * (k1 + 1) / (c + dl[j])
            g = {row_of[x] for x in q["gold"] if x in row_of}
            h += 1.0 if (g & set(topk(s, aid))) else 0.0
        acc = 100 * h / len(qs)
        line += f"{acc:16.2f} "
        if acc > bv:
            best, bv = v, acc
    wins[best] += 1
    print(line + " " + best)
print("archive-wins:", dict(wins))
