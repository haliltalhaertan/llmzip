"""EXACTLY-10 FUSION + EXCLUSIVE-GOLD RANK. Sifir model cagrisi.

KUSUR: fusion_depth.py sign5+bm25_5'i "10 aday butcesi" diye sundu ama tekrarlar
silinince ortalama 7.39 aday kaliyordu -- BM25 tek basina tam 10 kullanirken.
Adil olmayan karsilastirma. Dogrusu: birlestir, tekrarlari sil, SONRA siradaki
gorulmemis belgelerle TAM 10 benzersiz adaya tamamla (backfill).

Iki kontrol:
  1. Exactly-10 unique fusion -- dort fuzyon kurali, hepsi tam 10 aday
  2. Exclusive-gold rank dagilimi -- tamamlayici belgeler gercekten derinde mi?

Cikti: FUSION_EXACT10.json
"""
import json, pickle, re, math
from collections import Counter, defaultdict
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/FUSION_EXACT10.json"

K1, B = 1.2, 0.75
DEPTH = 20                     # backfill icin her listeden bu kadar cek
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    # 1200 kesme: matched_ci.py / jev_rerank_bm25.py ile AYNI olmali
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]

def bm25_rank(docs, query, k):
    D=[tok(d) for d in docs]; N=len(D); avg=sum(len(d) for d in D)/max(1,N)
    df=Counter()
    for d in D: df.update(set(d))
    idf={t: math.log(1+(N-n+0.5)/(n+0.5)) for t,n in df.items()}
    q=tok(query); sc=[]
    for d in D:
        tf,dl,s=Counter(d),len(d),0.0
        for t in q:
            if t in tf:
                f=tf[t]; s+=idf.get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
        sc.append(s)
    return sorted(range(N), key=lambda i:-sc[i])[:k]

# ---------------------------------------------------------------- veri
rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

Q=[]
for r in rows:
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    cache=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=cache["C"].shape[0]: continue
    # sign96: saklanmis siralama YALNIZ top-10. Backfill icin daha derini yok ->
    # sign tarafi en fazla 10 ile sinirli, bu SINIRLILIK kayda gecer.
    Q.append({"qid":qid, "gold":set(int(g) for g in cache["gold"]),
              "sign":r["sign96"]["ids"],
              "bm25":bm25_rank([text_of(m) for m in flat], item["question"], DEPTH)})
print(f"sorgu: {len(Q)} | sign derinligi 10 (saklanmis), bm25 derinligi {DEPTH}")

def cov(pools):
    hit=sum(1 for p,q in zip(pools,Q) if set(p)&q["gold"])
    return 100*hit/len(Q), sum(len(p) for p in pools)/len(pools)

# ---------------------------------------------------------------- fuzyon kurallari
def quota_backfill(q, a, b, target=10):
    """a/b kotasi, sonra SIRADAKI gorulmemis belgelerle tam 10'a tamamla."""
    pool, seen = [], set()
    for d in q["sign"][:a]:
        if d not in seen: seen.add(d); pool.append(d)
    for d in q["bm25"][:b]:
        if d not in seen: seen.add(d); pool.append(d)
    # backfill: iki listeden sirayla, gorulmemis olanlar
    i=j=0
    while len(pool)<target and (i<len(q["sign"]) or j<len(q["bm25"])):
        adv=False
        while i<len(q["sign"]):
            d=q["sign"][i]; i+=1
            if d not in seen: seen.add(d); pool.append(d); adv=True; break
        if len(pool)>=target: break
        while j<len(q["bm25"]):
            d=q["bm25"][j]; j+=1
            if d not in seen: seen.add(d); pool.append(d); adv=True; break
        if not adv: break
    return pool[:target]

def alternating(q, target=10):
    pool, seen = [], set()
    for i in range(max(len(q["sign"]), len(q["bm25"]))):
        for lst in (q["sign"], q["bm25"]):
            if i < len(lst) and lst[i] not in seen:
                seen.add(lst[i]); pool.append(lst[i])
                if len(pool)>=target: return pool
    return pool

def rrf(q, target=10, k=60):
    sc=defaultdict(float)
    for lst in (q["sign"], q["bm25"]):
        for r,d in enumerate(lst,1): sc[d]+=1.0/(k+r)
    return [d for d,_ in sorted(sc.items(), key=lambda x:-x[1])[:target]]

def minrank(q, target=10):
    best={}
    for lst in (q["sign"], q["bm25"]):
        for r,d in enumerate(lst,1): best[d]=min(best.get(d,1e9), r)
    return [d for d,_ in sorted(best.items(), key=lambda x:x[1])[:target]]

res={"n":len(Q), "sign_depth":10, "bm25_depth":DEPTH,
     "note":"exactly-10 unique pools via backfill; zero model calls"}
base_sign,_=cov([q["sign"][:10] for q in Q])
base_bm,_  =cov([q["bm25"][:10] for q in Q])
union,usz  =cov([list(dict.fromkeys(q["sign"][:10]+q["bm25"][:10])) for q in Q])
res["baseline"]={"sign96_top10":round(base_sign,2),"bm25_top10":round(base_bm,2),
                 "union_10_10":round(union,2),"union_mean_pool":round(usz,2)}
print(f"\nsign96 top10={base_sign:.2f}  BM25 top10={base_bm:.2f}  UNION={union:.2f} ({usz:.1f} aday)")

print(f"\n=== TAM 10 BENZERSIZ ADAY (backfill'li) ===")
print(f"{'kural':26s} {'ort.havuz':>10s} {'kapsam':>8s} {'BM25 farki':>11s}")
out=[]
for name,fn in [("quota 5/5 + backfill", lambda q: quota_backfill(q,5,5)),
                ("quota 3/7 + backfill", lambda q: quota_backfill(q,3,7)),
                ("quota 7/3 + backfill", lambda q: quota_backfill(q,7,3)),
                ("quota 2/8 + backfill", lambda q: quota_backfill(q,2,8)),
                ("alternating merge",    alternating),
                ("RRF k=60",             rrf),
                ("min-rank",             minrank)]:
    pools=[fn(q) for q in Q]
    c,sz=cov(pools)
    out.append({"rule":name,"coverage":round(c,2),"mean_pool":round(sz,2),
                "vs_bm25":round(c-base_bm,2)})
    print(f"{name:26s} {sz:>10.2f} {c:>8.2f} {c-base_bm:>+11.2f}")
res["exactly10"]=out

# ---------------------------------------------------------------- exclusive gold rank
print(f"\n=== EXCLUSIVE GOLD RANK: tamamlayici belgeler derinde mi? ===")
sign_only=[]; bm_only=[]
for q in Q:
    s10=set(q["sign"][:10]); b10=set(q["bm25"][:10]); g=q["gold"]
    if (s10&g) and not (b10&g):
        r=min(q["sign"].index(d)+1 for d in g if d in s10); sign_only.append(r)
    if (b10&g) and not (s10&g):
        r=min(q["bm25"].index(d)+1 for d in g if d in b10); bm_only.append(r)
def dist(v,label):
    if not v: return {}
    hist=Counter(v)
    d={"n":len(v),"mean_rank":round(sum(v)/len(v),2),
       "rank_1_4":sum(1 for x in v if x<=4),"rank_5_7":sum(1 for x in v if 5<=x<=7),
       "rank_8_10":sum(1 for x in v if x>=8)}
    print(f"  {label}: n={d['n']} ort.rank={d['mean_rank']:.2f} | "
          f"rank1-4: {d['rank_1_4']} | rank5-7: {d['rank_5_7']} | rank8-10: {d['rank_8_10']}")
    print(f"    dagilim: {dict(sorted(hist.items()))}")
    return d
res["sign_only_gold_rank"]=dist(sign_only,"BM25'in kacirdigi, gold'un sign96 rank'i")
res["bm25_only_gold_rank"]=dist(bm_only,  "sign96'nin kacirdigi, gold'un BM25 rank'i")

best=max(out,key=lambda x:x["coverage"])
res["best_exactly10"]=best
print(f"\nEN IYI tam-10 kural: {best['rule']} -> {best['coverage']:.2f} "
      f"(BM25'e gore {best['vs_bm25']:+.2f} pp, union {union:.2f})")
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"kayit: {OUT.name}")
