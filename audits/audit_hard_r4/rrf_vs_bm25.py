"""Matched 10-candidate RRF-vs-BM25 semantic rerank test.

KARAR DENEYI. Iki kol AYNI KOSUDA, ayni sorular, ayni model, eslestirilmis.
Jev run-to-run oynadigi icin eski BM25+Jev sayisiyla karsilastirma YAPILMAZ.

  kol A: BM25 top-10            -> Jev   (aday tavani 87.87)
  kol B: RRF k=60 top-10 unique -> Jev   (aday tavani 90.00)

Her iki kol da TAM 10 aday -> Jev maliyeti ozdes.
MALIYET NOTU: RRF retrieval tarafinda HEM sign96 HEM BM25 calistirir.
CPU + RAM/index maliyeti = sign96 + BM25. Jev acisindan bedava, sistem acisindan degil.

Uc olasi sonuc:
  - RRF belirgin kazanir  -> hibrit aday uretimi gercek kalite kaldiraci
  - ayni kalir            -> +2.13 pp kapsam final kaliteye cevrilemiyor
  - kotulesir            -> ek distractor'lar reranker'i bozuyor (mekanizma sonucu)

Cikti: RRF_VS_BM25.json
"""
import json, pickle, re, math, random, asyncio, sys, time, statistics
from collections import Counter, defaultdict
from pathlib import Path

MODEL = "jev-1.13.0"
from typesafe_sdk import AsyncTypeSafeClient, Noul

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/RRF_VS_BM25.json"

N_Q   = int(sys.argv[1]) if len(sys.argv) > 1 else 470
CONC, K1, B = 8, 1.2, 0.75
BM25_DEPTH, RRF_K, BOOT, SEED = 20, 60, 20000, 20260918
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

Q = {"answers": Noul(instructions=(
    "Does this candidate message contain the information needed to answer the question? "
    "Answer yes only if the message itself states the fact the question asks for. "
    "Answer no if it is merely on a related topic, mentions the same entities, or is part "
    "of the same conversation without containing the answer."))}

def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]
def fr3(r, g): return len(set(r[:3]) & g) / len(g) if g else 0.0

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

def rrf_pool(sign, bm25, target=10, k=RRF_K):
    sc=defaultdict(float)
    for lst in (sign, bm25):
        for r,d in enumerate(lst,1): sc[d]+=1.0/(k+r)
    return [d for d,_ in sorted(sc.items(), key=lambda x:-x[1])[:target]]

async def main():
    rows=[]
    for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
        rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = rows[:N_Q]
    print(f"sorgu: {len(rows)} | kollar: BM25-top10, RRF-top10 | {MODEL}", flush=True)

    tasks, meta, t0 = [], [], time.time()
    dup_total = 0
    for n, r in enumerate(rows, 1):
        qid=r["qid"]
        item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
        cache=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
        sess=item["haystack_sessions"]
        flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
        if len(flat)!=cache["C"].shape[0]:
            print(f"  ATLA {qid}"); continue
        gold=set(int(g) for g in cache["gold"])
        texts=[text_of(m) for m in flat]
        sign=r["sign96"]["ids"]
        bm_deep=bm25_rank(texts,item["question"],BM25_DEPTH)
        bm10=bm_deep[:10]
        rrf10=rrf_pool(sign,bm_deep,10)
        dup_total += len(set(sign[:10]) & set(bm10))
        pools={"bm25":bm10,"rrf":rrf10}
        meta.append({"qid":qid,"gold":gold,"pools":pools})
        for arm,ids in pools.items():
            for did in ids:
                tasks.append({"qid":qid,"arm":arm,"did":did,
                              "question":item["question"],"text":texts[did]})
        if n%100==0: print(f"  hazirlik {n}/{len(rows)} ({time.time()-t0:.0f}s)", flush=True)

    print(f"model cagrisi: {len(tasks)} | sign/bm25 ortak belge ort: {dup_total/len(meta):.2f}/10", flush=True)
    sem, done = asyncio.Semaphore(CONC), [0]
    async def judge(client,t):
        async with sem:
            try:
                r=await client.system_one(model=MODEL, questions=Q,
                    state={"question":t["question"],"candidate_message":t["text"]})
                t["score"]=r.nouls["answers"].noul
                t["ti"]=getattr(r.usage,"input_tokens",0); t["to"]=getattr(r.usage,"output_tokens",0)
            except Exception as e:
                t["score"],t["error"]=0.0,str(e)[:120]
            done[0]+=1
            if done[0]%500==0: print(f"  {done[0]}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
        return t
    async with AsyncTypeSafeClient() as client:
        tasks=await asyncio.gather(*(judge(client,t) for t in tasks))
    S={(t["qid"],t["arm"],t["did"]):t["score"] for t in tasks}

    pq=[]
    for m in meta:
        row={"qid":m["qid"],"gold":sorted(m["gold"])}
        for arm,ids in m["pools"].items():
            rk=sorted(ids,key=lambda d:-S.get((m["qid"],arm,d),0.0))
            row[f"{arm}_top3"]=rk[:3]
            row[f"{arm}_fr3"]=fr3(rk,m["gold"])
            row[f"{arm}_hit1"]=1.0 if rk[0] in m["gold"] else 0.0
            row[f"{arm}_cand"]=1.0 if (set(ids)&m["gold"]) else 0.0
        row["rescued"]=row["rrf_hit1"]>row["bm25_hit1"]
        row["broke"]  =row["rrf_hit1"]<row["bm25_hit1"]
        pq.append(row)

    def mean(k): return 100*sum(r[k] for r in pq)/len(pq)
    rnd=random.Random(SEED); N=len(pq)
    def boot(ka,kb):
        ds=[]
        for _ in range(BOOT):
            s=[pq[rnd.randrange(N)] for _ in range(N)]
            ds.append(100*(sum(r[ka] for r in s)-sum(r[kb] for r in s))/N)
        ds.sort(); return ds[int(.025*BOOT)], ds[int(.975*BOOT)]
    d_fr3=mean("rrf_fr3")-mean("bm25_fr3"); ci_fr3=boot("rrf_fr3","bm25_fr3")
    d_h1 =mean("rrf_hit1")-mean("bm25_hit1"); ci_h1=boot("rrf_hit1","bm25_hit1")

    ti=sum(t.get("ti",0) for t in tasks); to=sum(t.get("to",0) for t in tasks)
    out={"model":MODEL,"n":N,"boot_reps":BOOT,"seed":SEED,
         "bm25":{k:round(mean(f"bm25_{k}"),2) for k in ("cand","hit1","fr3")},
         "rrf": {k:round(mean(f"rrf_{k}"), 2) for k in ("cand","hit1","fr3")},
         "delta_fr3":round(d_fr3,3),"ci95_fr3":[round(c,3) for c in ci_fr3],
         "delta_hit1":round(d_h1,3),"ci95_hit1":[round(c,3) for c in ci_h1],
         "fr3_excludes_zero":not(ci_fr3[0]<=0<=ci_fr3[1]),
         "hit1_excludes_zero":not(ci_h1[0]<=0<=ci_h1[1]),
         "rescued":sum(1 for r in pq if r["rescued"]),
         "broke":sum(1 for r in pq if r["broke"]),
         "mean_overlap_sign_bm25":round(dup_total/len(meta),2),
         "tokens_in":ti,"tokens_out":to,
         "tokens_per_query_per_arm":round((ti+to)/(2*N),1),
         "errors":sum(1 for t in tasks if "error" in t),
         "elapsed_s":round(time.time()-t0,1),"per_query":pq}
    OUT.write_text(json.dumps(out,indent=1),encoding="utf-8")

    print(f"\n{'':8s} {'tavan':>7s} {'Hit@1':>7s} {'FR@3':>7s}")
    print(f"{'BM25':8s} {out['bm25']['cand']:>7.2f} {out['bm25']['hit1']:>7.2f} {out['bm25']['fr3']:>7.2f}")
    print(f"{'RRF':8s} {out['rrf']['cand']:>7.2f} {out['rrf']['hit1']:>7.2f} {out['rrf']['fr3']:>7.2f}")
    print(f"\nDelta FR@3  = {d_fr3:+.3f} pp  CI95 [{ci_fr3[0]:+.3f}, {ci_fr3[1]:+.3f}]  "
          f"{'SIG' if out['fr3_excludes_zero'] else 'AYIRT EDILEMEZ'}")
    print(f"Delta Hit@1 = {d_h1:+.3f} pp  CI95 [{ci_h1[0]:+.3f}, {ci_h1[1]:+.3f}]  "
          f"{'SIG' if out['hit1_excludes_zero'] else 'AYIRT EDILEMEZ'}")
    print(f"\nkurtardi {out['rescued']} | bozdu {out['broke']} | ortak belge {out['mean_overlap_sign_bm25']:.2f}/10")
    print(f"token {ti+to:,} | kol basina sorgu {out['tokens_per_query_per_arm']:.0f} | "
          f"hata {out['errors']} | {out['elapsed_s']}s")

if __name__=="__main__":
    asyncio.run(main())
