"""SORU PARCALAMA PILOTU: Jev eksik ikinci kaniti bulacak sorguyu uretebilir mi?

Dar arastirma sorusu:
  Coklu-gold LME sorularinda, ilk erisilebilir evidence + soru verildiginde,
  Jev eksik ikinci evidence'i bulmaya yarayacak sorguyu uretebilir mi?

UYGUN KUME (sifir tokenla belirlendi): 86 sorgu
  coklu gold + en az bir gold erisilebilir + en az bir gold top-10 DISINDA
  toplam 154 eksik gold

UC KOL, AYNI KOSU (Jev run-to-run oynadigi icin ayri kosu karsilastirmasi YASAK):
  A. taban        : orijinal soru            -> eksik gold tanim geregi top-10 disinda (recall 0)
  B. M2 lexical   : capa yuksek-IDF terimleri eklenmis sorgu  (L-112'de uctan uca basarisiz)
  C. decomposition: Jev'in urettigi takip sorgusu

ANA METRIK: missing-gold recall@10 -- nihai cevaba hic gecmeden mekanizma testi.

Cikti: DECOMPOSITION_PILOT.json
"""
import json, pickle, re, math, asyncio, time, random
import numpy as np
from collections import Counter
from pathlib import Path

MODEL="jev-1.13.0"
from typesafe_sdk import AsyncTypeSafeClient, Noul

W    = Path("C:/Users/MDP/dev/llmzip-work")
ITEM = W / "regen/lme/items"
ELIG = W / "audit_hard_r4/_decomp_eligible.json"
OUT  = W / "audit_hard_r4/DECOMPOSITION_PILOT.json"

K1,B=1.2,0.75; CONC=8; BOOT,SEED=20000,20260918
FROZEN=re.compile(r"\b\w\w+\b")
STOP=set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m): return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m,dict) else str(m)[:1200]

Q={"missing_information": Noul(instructions=(
    "You are given a question and one piece of evidence already retrieved from a conversation "
    "archive. The evidence alone does NOT fully answer the question. Identify the single specific "
    "piece of information that is still missing, and express it as a short search query of three "
    "to eight words that would retrieve it from the archive. Write only the search query itself, "
    "with no explanation, no quotes and no leading label. If the evidence already fully answers "
    "the question, repeat the most distinctive noun phrase of the question instead."))}

async def main():
    elig=json.load(open(ELIG,encoding="utf-8"))
    print(f"uygun vaka: {len(elig)} | eksik gold: {sum(x['n_missing'] for x in elig)} | {MODEL}", flush=True)

    ctx={}
    for e in elig:
        qid=e["qid"]
        item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
        c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
        sess=item["haystack_sessions"]
        flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
        texts=[text_of(m) for m in flat]
        D=[tok(x) for x in texts]; N=len(D); avg=sum(len(x) for x in D)/max(1,N)
        df=Counter()
        for x in D: df.update(set(x))
        idf={t: math.log(1+(N-n+0.5)/(n+0.5)) for t,n in df.items()}
        TF=[Counter(x) for x in D]; DL=[len(x) for x in D]
        ctx[qid]={"question":item["question"],"texts":texts,"D":D,"idf":idf,"TF":TF,"DL":DL,
                  "avg":avg,"N":N,"anchor":e["anchor"],"missing":e["missing"]}

    def score(cx,qterms):
        out=np.zeros(cx["N"])
        for i in range(cx["N"]):
            tf,dl,s=cx["TF"][i],cx["DL"][i],0.0
            for t in qterms:
                if t in tf:
                    f=tf[t]; s+=cx["idf"].get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,cx["avg"])))
            out[i]=s
        return out

    t0=time.time(); sem=asyncio.Semaphore(CONC); done=[0]
    async def gen(client,e):
        cx=ctx[e["qid"]]
        async with sem:
            try:
                r=await client.system_one(model=MODEL, questions=Q,
                    state={"question":cx["question"],"evidence_already_found":cx["texts"][cx["anchor"]]})
                out=r.nouls["missing_information"].noul
                e["followup"]=(out if isinstance(out,str) else str(out)).strip()[:200]
                e["ti"]=getattr(r.usage,"input_tokens",0); e["to"]=getattr(r.usage,"output_tokens",0)
            except Exception as ex:
                e["followup"]=""; e["error"]=str(ex)[:120]
            done[0]+=1
            if done[0]%25==0: print(f"  {done[0]}/{len(elig)} ({time.time()-t0:.0f}s)", flush=True)
        return e
    async with AsyncTypeSafeClient() as client:
        elig=await asyncio.gather(*(gen(client,e) for e in elig))

    per=[]
    for e in elig:
        cx=ctx[e["qid"]]; q=tok(cx["question"]); miss=set(e["missing"])
        base=score(cx,q)
        # B: M2 lexical expansion
        at=tok(cx["texts"][cx["anchor"]])
        vals=sorted((cx["idf"].get(t,0.0) for t in set(at)),reverse=True)
        thr=vals[max(0,int(0.25*len(vals))-1)] if vals else 0.0
        m2=score(cx,q+[t for t in at if cx["idf"].get(t,0.0)>=thr])
        # C: decomposition -- SADECE uretilen sorgu (soru tekrar eklenmez; yeni ihtiyac test edilir)
        ft=tok(e.get("followup",""))
        dec=score(cx,ft) if ft else base.copy()
        row={"qid":e["qid"],"section":e["section"],"followup":e.get("followup",""),
             "n_missing":len(miss)}
        for name,s in [("base",base),("m2",m2),("dec",dec)]:
            s=s.copy(); s[cx["anchor"]]=-1e9
            t10=set(map(int,np.argsort(-s,kind="stable")[:10]))
            row[f"{name}_hit"]=1.0 if (t10&miss) else 0.0
            row[f"{name}_rec"]=len(t10&miss)/len(miss)
        per.append(row)

    M=len(per)
    def mean(k): return 100*sum(x[k] for x in per)/M
    rnd=random.Random(SEED)
    def ci(ka,kb):
        ds=[]
        for _ in range(BOOT):
            s=[per[rnd.randrange(M)] for _ in range(M)]
            ds.append(100*(sum(x[ka] for x in s)-sum(x[kb] for x in s))/M)
        ds.sort(); return round(ds[int(.025*BOOT)],2), round(ds[int(.975*BOOT)],2)

    ti=sum(e.get("ti",0) for e in elig); to=sum(e.get("to",0) for e in elig)
    res={"model":MODEL,"n_queries":M,"n_missing_golds":sum(x["n_missing"] for x in per),
         "arms":{n:{"any_hit_pct":round(mean(f"{n}_hit"),2),"recall_pct":round(mean(f"{n}_rec"),2)}
                 for n in ["base","m2","dec"]},
         "dec_vs_base_hit":{"delta":round(mean("dec_hit")-mean("base_hit"),2),"ci95":list(ci("dec_hit","base_hit"))},
         "dec_vs_m2_hit":{"delta":round(mean("dec_hit")-mean("m2_hit"),2),"ci95":list(ci("dec_hit","m2_hit"))},
         "m2_vs_base_hit":{"delta":round(mean("m2_hit")-mean("base_hit"),2),"ci95":list(ci("m2_hit","base_hit"))},
         "tokens_in":ti,"tokens_out":to,"errors":sum(1 for e in elig if "error" in e),
         "elapsed_s":round(time.time()-t0,1),"per_query":per}
    OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")

    print(f"\n=== MISSING-GOLD RECALL@10 (n={M} sorgu) ===")
    print(f"{'kol':16s} {'en az bir':>10s} {'recall':>9s}")
    for n,lab in [("base","taban (soru)"),("m2","M2 lexical"),("dec","decomposition")]:
        print(f"{lab:16s} {mean(f'{n}_hit'):>9.2f}% {mean(f'{n}_rec'):>8.2f}%")
    for k,lab in [("dec_vs_base_hit","decomp - taban"),("dec_vs_m2_hit","decomp - M2"),
                  ("m2_vs_base_hit","M2 - taban")]:
        d=res[k]; sig="SIG" if not(d["ci95"][0]<=0<=d["ci95"][1]) else "AYIRT EDILEMEZ"
        print(f"  {lab:16s}: {d['delta']:+6.2f} pp  CI95 [{d['ci95'][0]:+.2f},{d['ci95'][1]:+.2f}]  {sig}")
    print(f"\ntoken {ti+to:,} | hata {res['errors']} | {res['elapsed_s']}s")
    print(f"\nornek uretilen sorgular:")
    for x in per[:6]:
        print(f"  [{'HIT' if x['dec_hit'] else '   '}] {x['followup'][:70]}")

if __name__=="__main__":
    asyncio.run(main())
