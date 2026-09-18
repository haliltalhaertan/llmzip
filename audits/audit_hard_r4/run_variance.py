"""RUN-TO-RUN VARYANS: Jev'in kararsizligi delta'ya ne kadar belirsizlik katiyor?

Mevcut bootstrap CI yalniz SORGU ORNEKLEME belirsizligini olcuyor. Iki kosu arasinda
delta -1.21 -> -2.10 kaydi; bu Jev'in kendi stokastikligi. Toplam belirsizlik:

    toplam = sorgu varyasyonu + model kosu varyasyonu

470 sorguyu 10 kez kosmak pahali. Sabit bir altkumede R bagimsiz tekrar yeterli:
run-to-run standart sapmasi ucuza tahmin edilir.

Ayni sabit altkume, ayni havuzlar, YALNIZ Jev yeniden cagrilir.
Cikti: RUN_VARIANCE.json
"""
import json, pickle, re, math, statistics, asyncio, sys, time
from collections import Counter
from pathlib import Path

MODEL = "jev-1.13.0"
from typesafe_sdk import AsyncTypeSafeClient, Noul

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/RUN_VARIANCE.json"

N_SUB = int(sys.argv[1]) if len(sys.argv) > 1 else 120     # sabit altkume
REPS  = int(sys.argv[2]) if len(sys.argv) > 2 else 4       # bagimsiz tekrar
CONC, K1, B = 8, 1.2, 0.75
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

Q = {"answers": Noul(instructions=(
    "Does this candidate message contain the information needed to answer the question? "
    "Answer yes only if the message itself states the fact the question asks for. "
    "Answer no if it is merely on a related topic, mentions the same entities, or is part "
    "of the same conversation without containing the answer."))}

def tok(s):  return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]
def fr3(r, g): return len(set(r[:3]) & g) / len(g) if g else 0.0

def bm25_top10(docs, query):
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
    return sorted(range(N), key=lambda i:-sc[i])[:10]

async def main():
    rows=[]
    for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
        rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = rows[:N_SUB]
    print(f"sabit altkume: {len(rows)} sorgu | {REPS} bagimsiz tekrar | {MODEL}", flush=True)

    # --- havuzlari BIR KEZ kur (her tekrarda ayni)
    meta, t0 = [], time.time()
    for r in rows:
        qid=r["qid"]
        item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
        cache=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
        sess=item["haystack_sessions"]
        flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
        if len(flat)!=cache["C"].shape[0]: continue
        texts=[text_of(m) for m in flat]
        meta.append({"qid":qid, "gold":set(int(g) for g in cache["gold"]),
                     "q":item["question"], "texts":texts,
                     "pools":{"sign96":r["sign96"]["ids"], "bm25":bm25_top10(texts,item["question"])}})
    print(f"havuzlar hazir ({time.time()-t0:.0f}s)", flush=True)

    sem=asyncio.Semaphore(CONC)
    async def judge(client, m, arm, did):
        async with sem:
            try:
                r=await client.system_one(model=MODEL, questions=Q,
                    state={"question": m["q"], "candidate_message": m["texts"][did]})
                return r.nouls["answers"].noul, getattr(r.usage,"input_tokens",0)+getattr(r.usage,"output_tokens",0)
            except Exception:
                return 0.0, 0

    reps=[]
    async with AsyncTypeSafeClient() as client:
        for rep in range(REPS):
            jobs=[(m,arm,d) for m in meta for arm,ids in m["pools"].items() for d in ids]
            res=await asyncio.gather(*(judge(client,m,a,d) for m,a,d in jobs))
            S={(m["qid"],a,d):s for (m,a,d),(s,_) in zip(jobs,res)}
            tok_total=sum(t for _,t in res)
            acc={"sign96":0.0,"bm25":0.0}
            for m in meta:
                for arm,ids in m["pools"].items():
                    rk=sorted(ids,key=lambda d:-S.get((m["qid"],arm,d),0.0))
                    acc[arm]+=fr3(rk,m["gold"])
            n=len(meta)
            fr={a: 100*v/n for a,v in acc.items()}
            delta=fr["sign96"]-fr["bm25"]
            reps.append({"rep":rep+1,"sign96_fr3":round(fr["sign96"],3),
                         "bm25_fr3":round(fr["bm25"],3),"delta":round(delta,3),
                         "tokens":tok_total})
            print(f"  tekrar {rep+1}/{REPS}: sign96={fr['sign96']:.2f} bm25={fr['bm25']:.2f} "
                  f"delta={delta:+.3f}  ({time.time()-t0:.0f}s)", flush=True)

    ds=[r["delta"] for r in reps]
    sd=statistics.stdev(ds) if len(ds)>1 else 0.0
    out={"model":MODEL,"n_queries":len(meta),"reps":REPS,"runs":reps,
         "delta_mean":round(statistics.mean(ds),3),
         "delta_sd_run_to_run":round(sd,3),
         "delta_range":[round(min(ds),3),round(max(ds),3)],
         "sign96_sd":round(statistics.stdev([r["sign96_fr3"] for r in reps]),3) if REPS>1 else 0,
         "bm25_sd":round(statistics.stdev([r["bm25_fr3"] for r in reps]),3) if REPS>1 else 0,
         "tokens_total":sum(r["tokens"] for r in reps),
         "elapsed_s":round(time.time()-t0,1)}
    OUT.write_text(json.dumps(out,indent=1),encoding="utf-8")
    print(f"\ndelta ortalama {out['delta_mean']:+.3f} | run-to-run SD {sd:.3f} pp | "
          f"aralik [{out['delta_range'][0]:+.2f},{out['delta_range'][1]:+.2f}]")
    print(f"sign96 SD {out['sign96_sd']:.3f} | bm25 SD {out['bm25_sd']:.3f}")
    print(f"token {out['tokens_total']:,} | {out['elapsed_s']}s")

if __name__=="__main__":
    asyncio.run(main())
