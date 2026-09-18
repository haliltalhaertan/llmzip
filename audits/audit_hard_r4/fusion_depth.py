"""FUSION DEPTH: union tavaninin ne kadari 10 adayla korunur? SIFIR MODEL CAGRISI.

H3 gosterdi ki fark aday uretiminden geliyor. Union tavani 91.91 ama 20 aday demek
= Jev maliyeti iki kat. Asil soru: sign96 top-a + BM25 top-b, a+b<=10 (tekrarsiz)
ile tavanin ne kadari korunur?

Saf aritmetik: saklanmis sign96 siralamasi + yeniden kurulan BM25 siralamasi.
Model cagrilmaz, token harcanmaz.

Cikti: FUSION_DEPTH.json
"""
import json, pickle, re, math
from collections import Counter, defaultdict
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/FUSION_DEPTH.json"

K1, B = 1.2, 0.75
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    # TUTARLILIK DUZELTMESI 2026-09-18: 1200 karakter kesme, matched_ci.py ve
    # jev_rerank_bm25.py ile AYNI olmali. Ilk surumde kesme yoktu ve BM25 tavani
    # 87.23 cikti (diger kosularda 87.87) -- ayni deneyin iki farkli sayisi.
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]

def bm25_rank(docs, query, k=10):
    D = [tok(d) for d in docs]; N = len(D)
    avg = sum(len(d) for d in D) / max(1, N)
    df = Counter()
    for d in D: df.update(set(d))
    idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    q = tok(query); sc = []
    for d in D:
        tf, dl, s = Counter(d), len(d), 0.0
        for t in q:
            if t in tf:
                f = tf[t]
                s += idf.get(t, 0.0) * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / max(1, avg)))
        sc.append(s)
    return sorted(range(N), key=lambda i: -sc[i])[:k]

# ---------------------------------------------------------------- veri
rows = []
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

Q = []
sec = {}
for r in rows:
    qid = r["qid"]
    item  = json.load(open(ITEM / f"{qid}.json", encoding="utf-8"))
    cache = pickle.load(open(W / f"regen/lme/cache_repr/{qid}.pkl", "rb"))
    sess = item["haystack_sessions"]
    flat = [m for s in sess for m in s] if isinstance(sess[0], list) else sess
    if len(flat) != cache["C"].shape[0]:
        continue
    Q.append({"qid": qid,
              "gold": set(int(g) for g in cache["gold"]),
              "sign": r["sign96"]["ids"],                       # saklanmis siralama
              "bm25": bm25_rank([text_of(m) for m in flat], item["question"])})
    sec[qid] = r.get("section", "?")
print(f"sorgu: {len(Q)}")

def coverage(a, b, cap=None):
    """sign96 top-a + BM25 top-b, sirayla birlestir, tekrarsiz, cap kadar kes."""
    hit = 0
    sizes = []
    for q in Q:
        pool, seen = [], set()
        for d in q["sign"][:a]:
            if d not in seen: seen.add(d); pool.append(d)
        for d in q["bm25"][:b]:
            if d not in seen: seen.add(d); pool.append(d)
        if cap: pool = pool[:cap]
        sizes.append(len(pool))
        if set(pool) & q["gold"]: hit += 1
    return 100 * hit / len(Q), sum(sizes) / len(sizes)

res = {"n": len(Q), "note": "zero model calls; stored sign96 ranking + deterministic BM25 rebuild"}

# temel referanslar
res["baseline"] = {
    "sign96_top10": round(coverage(10, 0)[0], 2),
    "bm25_top10":   round(coverage(0, 10)[0], 2),
    "union_10_10":  round(coverage(10, 10)[0], 2),
}
print(f"\nsign96 top10 = {res['baseline']['sign96_top10']:.2f}")
print(f"BM25   top10 = {res['baseline']['bm25_top10']:.2f}")
print(f"UNION 10+10  = {res['baseline']['union_10_10']:.2f}  (ort. havuz "
      f"{coverage(10,10)[1]:.1f} aday)")

# a+b = 10 matrisi (cap 10)
print(f"\n=== a+b<=10, TEKRARSIZ, en fazla 10 aday ===")
print(f"{'sign96':>7s} {'BM25':>6s} {'ort.havuz':>10s} {'kapsam':>8s} {'union fark':>11s}")
grid = []
u = res["baseline"]["union_10_10"]
for a in range(0, 11):
    b = 10 - a
    cov, sz = coverage(a, b, cap=10)
    grid.append({"sign": a, "bm25": b, "coverage": round(cov, 2),
                 "mean_pool": round(sz, 2), "vs_union": round(cov - u, 2)})
    print(f"{a:>7d} {b:>6d} {sz:>10.2f} {cov:>8.2f} {cov-u:>+11.2f}")
res["grid_sum10"] = grid

# daha derin birlesimler
print(f"\n=== daha genis havuzlar ===")
deep = []
for a, b, cap in [(5,5,10),(7,7,14),(10,5,15),(5,10,15),(10,10,20),(10,10,None)]:
    cov, sz = coverage(a, b, cap)
    deep.append({"sign": a, "bm25": b, "cap": cap, "coverage": round(cov,2), "mean_pool": round(sz,2)})
    print(f"  sign{a}+bm25{b} cap={str(cap):>4s}: havuz {sz:5.2f} -> kapsam {cov:.2f}")
res["deeper"] = deep

best = max(grid, key=lambda g: g["coverage"])
res["best_sum10"] = best
print(f"\nEN IYI a+b=10: sign{best['sign']}+bm25{best['bm25']} -> {best['coverage']:.2f} "
      f"(union'dan {best['vs_union']:+.2f}, ort. {best['mean_pool']:.1f} aday)")
print(f"  tek basina en iyiye gore: +{best['coverage']-max(res['baseline']['sign96_top10'], res['baseline']['bm25_top10']):.2f} pp")
print(f"  ayni aday sayisi (10), ayni Jev maliyeti")

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"\nkayit: {OUT.name}")
