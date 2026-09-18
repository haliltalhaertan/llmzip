"""SEMANTIK IPUCU SECIMI: decomposition'in Jev ile yapilabilen bicimi.

BULGU (once kaydedilmeli): Jev serbest metin URETMIYOR. TypeSafe primitifleri
Noul (evet/hayir), Choice (etiket secimi), Score (sirali) -- hepsi YARGI.
Dolayisiyla "Jev takip sorgusu uretsin" LITERAL OLARAK IMKANSIZ.
Ilk pilot bu yuzden gecersizdi: Noul 0.63 gibi skorlar dondurdu, metin degil.

YENIDEN KURULUM: decomposition'in cekirdegi "hangi baglanti cozulmemis?" sorusudur.
Bu bir SECIM gorevidir ve Jev bunu yapabilir:
  capadan aday varliklar cikar -> Jev'e "bu varlik, sorunun ihtiyac duydugu ama
  kanitin cozmedigi baglanti mi?" diye sor -> en yuksek skorlu varlikla ikinci arama.

Bu, M2'den farkli: M2 capanin TUM yuksek-IDF kelimelerini ekler (kor).
Bu kol, Jev'in sectigi TEK varligi kullanir (secici).

UC KOL, AYNI KOSU:
  A. taban        : orijinal soru
  B. M2 lexical   : capa yuksek-IDF terimleri (kor genisletme)
  C. jev_secim    : Jev'in sectigi tek varlik + soru

ANA METRIK: missing-gold recall@10
Cikti: HINT_SELECTION_PILOT.json
"""
import json, pickle, re, math, asyncio, time, random
import numpy as np
from collections import Counter
from pathlib import Path

MODEL="jev-1.13.0"
from typesafe_sdk import AsyncTypeSafeClient, Noul

W=Path("C:/Users/MDP/dev/llmzip-work"); ITEM=W/"regen/lme/items"
ELIG=W/"audit_hard_r4/_decomp_eligible.json"
OUT =W/"audit_hard_r4/HINT_SELECTION_PILOT.json"
K1,B=1.2,0.75; CONC=8; BOOT,SEED=20000,20260918; MAXC=8
FROZEN=re.compile(r"\b\w\w+\b")
STOP=set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m): return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m,dict) else str(m)[:1200]

Q={"is_unresolved_link": Noul(instructions=(
   "A question is being answered from a conversation archive. One piece of evidence has already "
   "been retrieved, but it does not fully answer the question. Consider the candidate term below, "
   "which appears in that evidence. Answer yes only if finding MORE information specifically about "
   "this term is what would complete the answer - that is, the evidence refers to it but leaves it "
   "unexplained. Answer no if the term is already fully explained, is incidental, or is merely "
   "repeating something the question already states."))}

async def main():
    elig=json.load(open(ELIG,encoding="utf-8"))
    ctx={}; tasks=[]
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
        ctx[qid]={"q":item["question"],"texts":texts,"idf":idf,"TF":TF,"DL":DL,"avg":avg,"N":N,
                  "anchor":e["anchor"],"missing":set(e["missing"])}
        qset=set(tok(item["question"]))
        at=tok(texts[e["anchor"]])
        cands=sorted({t for t in at if t not in qset and idf.get(t,0)>0},
                     key=lambda t:-idf.get(t,0))[:MAXC]
        e["cands"]=cands
        for t in cands:
            tasks.append({"qid":qid,"term":t,"question":item["question"],
                          "evidence":texts[e["anchor"]]})
    print(f"vaka {len(elig)} | aday varlik {len(tasks)} | {MODEL}", flush=True)

    t0=time.time(); sem=asyncio.Semaphore(CONC); done=[0]
    async def judge(client,t):
        async with sem:
            try:
                r=await client.system_one(model=MODEL, questions=Q,
                    state={"question":t["question"],"evidence_already_found":t["evidence"],
                           "candidate_term":t["term"]})
                t["s"]=r.nouls["is_unresolved_link"].noul
                t["ti"]=getattr(r.usage,"input_tokens",0); t["to"]=getattr(r.usage,"output_tokens",0)
            except Exception as ex:
                t["s"]=0.0; t["error"]=str(ex)[:100]
            done[0]+=1
            if done[0]%150==0: print(f"  {done[0]}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
        return t
    async with AsyncTypeSafeClient() as client:
        tasks=await asyncio.gather(*(judge(client,t) for t in tasks))
    S={}
    for t in tasks: S.setdefault(t["qid"],{})[t["term"]]=t["s"]

    def score(cx,qt):
        o=np.zeros(cx["N"])
        for i in range(cx["N"]):
            tf,dl,s=cx["TF"][i],cx["DL"][i],0.0
            for t in qt:
                if t in tf:
                    f=tf[t]; s+=cx["idf"].get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,cx["avg"])))
            o[i]=s
        return o

    per=[]
    for e in elig:
        cx=ctx[e["qid"]]; q=tok(cx["q"]); miss=cx["missing"]
        at=tok(cx["texts"][cx["anchor"]])
        vals=sorted((cx["idf"].get(t,0.0) for t in set(at)),reverse=True)
        thr=vals[max(0,int(0.25*len(vals))-1)] if vals else 0.0
        sc=S.get(e["qid"],{})
        pick=max(sc,key=sc.get) if sc else None
        arms={"base":q,"m2":q+[t for t in at if cx["idf"].get(t,0.0)>=thr],
              "jev":q+([pick]*3 if pick else [])}
        row={"qid":e["qid"],"section":e["section"],"pick":pick,
             "pick_score":round(sc.get(pick,0.0),3) if pick else None,"n_missing":len(miss)}
        for nm,qt in arms.items():
            s=score(cx,qt); s[cx["anchor"]]=-1e9
            t10=set(map(int,np.argsort(-s,kind="stable")[:10]))
            row[f"{nm}_hit"]=1.0 if (t10&miss) else 0.0
            row[f"{nm}_rec"]=len(t10&miss)/len(miss)
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
    ti=sum(t.get("ti",0) for t in tasks); to=sum(t.get("to",0) for t in tasks)
    res={"model":MODEL,"n_queries":M,"n_candidates_judged":len(tasks),
         "sdk_finding":("Jev/TypeSafe exposes only judgment primitives (Noul yes/no, Choice label, "
           "Score ordinal). It CANNOT generate free text, so literal question decomposition - "
           "'have the model write a follow-up query' - is impossible with this model. Reformulated "
           "as selection: Jev picks which anchor entity is the unresolved link."),
         "arms":{n:{"any_hit_pct":round(mean(f"{n}_hit"),2),"recall_pct":round(mean(f"{n}_rec"),2)}
                 for n in ["base","m2","jev"]},
         "jev_vs_base":{"delta":round(mean("jev_hit")-mean("base_hit"),2),"ci95":list(ci("jev_hit","base_hit"))},
         "jev_vs_m2":{"delta":round(mean("jev_hit")-mean("m2_hit"),2),"ci95":list(ci("jev_hit","m2_hit"))},
         "m2_vs_base":{"delta":round(mean("m2_hit")-mean("base_hit"),2),"ci95":list(ci("m2_hit","base_hit"))},
         "tokens":ti+to,"errors":sum(1 for t in tasks if "error" in t),
         "elapsed_s":round(time.time()-t0,1),"per_query":per}
    OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
    print(f"\n=== MISSING-GOLD RECALL@10 (n={M}) ===")
    for n,lab in [("base","taban"),("m2","M2 kor lexical"),("jev","Jev secili varlik")]:
        print(f"  {lab:18s} en az bir {mean(f'{n}_hit'):>6.2f}%   recall {mean(f'{n}_rec'):>6.2f}%")
    for k,lab in [("jev_vs_base","Jev - taban"),("jev_vs_m2","Jev - M2"),("m2_vs_base","M2 - taban")]:
        d=res[k]; sig="SIG" if not(d["ci95"][0]<=0<=d["ci95"][1]) else "AYIRT EDILEMEZ"
        print(f"    {lab:12s}: {d['delta']:+6.2f} pp CI95 [{d['ci95'][0]:+.2f},{d['ci95'][1]:+.2f}] {sig}")
    print(f"\ntoken {ti+to:,} | hata {res['errors']} | {res['elapsed_s']}s")
    print("ornek secimler:", [(x["pick"],x["pick_score"]) for x in per[:6]])

if __name__=="__main__":
    asyncio.run(main())
