"""COK-ADIMLI HAT: ipucu cikarma yontemleri x capa secimi. SIFIR MODEL CAGRISI.

Kullanicinin hatti:
  soru -> ilk retrieval -> ilk kanit -> AYIRT EDICI IPUCLARINI CIKAR -> ikinci retrieval
  -> eksik kanitlari topla -> birlestir

Iki eksen olculur:

EKSEN 1 -- CAPA SECIMI (kritik durustluk noktasi)
  oracle : capa = havuzdaki GERCEK gold. Sistem bunu BILEMEZ. Ust sinir.
  gercek : capa = BM25 top-1 (ne olursa olsun). Konuslanabilir sistem budur.
  Onceki M1 olcumu yalniz ORACLE idi -> hattin gercek degeri bilinmiyordu.

EKSEN 2 -- IPUCU CIKARMA (M1..M4)
  M1 tam metin        : capanin tum kelimeleri
  M2 yuksek-IDF       : yalniz nadir terimler (ust %25 IDF)
  M4 fark terimleri   : capada olup soruda OLMAYAN terimler
  M2+M4 kesisim       : hem nadir hem yeni

OLCUM: nihai FR@3 (uctan uca), rank hareketi degil. Ikinci turda capa haric
top-3 secilir; birinci turun capasi zaten cevaba dahil sayilir (hat boyle calisir).

Cikti: MULTISTEP_PIPELINE.json
"""
import json, pickle, re, math, random
import numpy as np
from collections import Counter
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/MULTISTEP_PIPELINE.json"

K1, B = 1.2, 0.75
BOOT, SEED = 20000, 20260918
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

ARMS=["baseline","oracle_M1","oracle_M2","oracle_M4","oracle_M2M4",
      "real_M1","real_M2","real_M4","real_M2M4"]
per_query=[]
print(f"sorgu: {len(rows)} | 1 taban + 8 hat varyanti", flush=True)

for n,r in enumerate(rows,1):
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    gold=set(int(g) for g in c["gold"])
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=c["C"].shape[0]: continue
    texts=[text_of(m) for m in flat]

    D=[tok(d) for d in texts]; N=len(D); avg=sum(len(x) for x in D)/max(1,N)
    df=Counter()
    for x in D: df.update(set(x))
    idf={t: math.log(1+(N-cn+0.5)/(cn+0.5)) for t,cn in df.items()}
    TF=[Counter(x) for x in D]; DL=[len(x) for x in D]
    def score(qterms):
        out=np.zeros(N)
        for i in range(N):
            tf,dl,s=TF[i],DL[i],0.0
            for t in qterms:
                if t in tf:
                    f=tf[t]; s+=idf.get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
            out[i]=s
        return out

    q=tok(item["question"]); qset=set(q)
    base=score(q)
    order=list(map(int,np.argsort(-base,kind="stable")))
    top3=order[:3]
    row={"qid":qid,"n_gold":len(gold),
         "baseline":len(set(top3)&gold)/len(gold)}

    pool=set(order[:10])|set(r["sign96"]["ids"])
    found=[g for g in gold if g in pool]
    anchors={"oracle": (found[0] if found else None), "real": order[0]}

    # IDF esigi: capa terimlerinin ust %25'i
    for mode,anchor in anchors.items():
        if anchor is None:
            for m2 in ["M1","M2","M4","M2M4"]: row[f"{mode}_{m2}"]=row["baseline"]
            continue
        at=tok(texts[anchor]); aset=set(at)
        if at:
            vals=sorted((idf.get(t,0.0) for t in aset), reverse=True)
            thr=vals[max(0,int(0.25*len(vals))-1)] if vals else 0.0
        else: thr=0.0
        hints={
         "M1":   at,
         "M2":   [t for t in at if idf.get(t,0.0)>=thr],
         "M4":   [t for t in at if t not in qset],
         "M2M4": [t for t in at if t not in qset and idf.get(t,0.0)>=thr],
        }
        for name,h in hints.items():
            s2=score(q+h)
            s2[anchor]=-1e9                     # capa tekrar secilmesin
            t3=list(map(int,np.argsort(-s2,kind="stable")[:3]))
            # hat: capa zaten elde + ikinci turdan 2 aday (toplam 3 belge butcesi)
            final=[anchor]+t3[:2]
            row[f"{mode}_{name}"]=len(set(final)&gold)/len(gold)
    per_query.append(row)
    if n%150==0: print(f"  {n}/{len(rows)}", flush=True)

M=len(per_query)
def mean(k): return 100*sum(x[k] for x in per_query)/M
rnd=random.Random(SEED)
def boot_ci(ka,kb):
    ds=[]
    for _ in range(BOOT):
        s=[per_query[rnd.randrange(M)] for _ in range(M)]
        ds.append(100*(sum(x[ka] for x in s)-sum(x[kb] for x in s))/M)
    ds.sort(); return round(ds[int(.025*BOOT)],3), round(ds[int(.975*BOOT)],3)

print(f"\ncozumlenen: {M}")
print(f"\n{'kol':16s} {'FR@3':>8s} {'taban farki':>12s} {'CI95':>22s}")
print(f"{'baseline':16s} {mean('baseline'):>8.2f}")
res={"n":M,"model_calls":0,"baseline_fr3":round(mean("baseline"),2),"arms":{}}
for mode in ["oracle","real"]:
    for m2 in ["M1","M2","M4","M2M4"]:
        k=f"{mode}_{m2}"; v=mean(k); d=v-mean("baseline"); ci=boot_ci(k,"baseline")
        sig = "SIG" if not (ci[0]<=0<=ci[1]) else "-"
        res["arms"][k]={"fr3":round(v,2),"delta":round(d,3),"ci95":list(ci),"significant":sig=="SIG"}
        print(f"{k:16s} {v:>8.2f} {d:>+12.3f}   [{ci[0]:+.3f},{ci[1]:+.3f}] {sig}")

# oracle ile gercek arasindaki ucurum
gap={m2: round(mean(f"oracle_{m2}")-mean(f"real_{m2}"),3) for m2 in ["M1","M2","M4","M2M4"]}
res["oracle_minus_real"]=gap
print(f"\noracle - gercek ucurumu: {gap}")
best_real=max(["M1","M2","M4","M2M4"], key=lambda m2: mean(f"real_{m2}"))
res["note"]=("oracle anchor = the actual gold in the pool, which a deployed system cannot know; "
             "real anchor = BM25 top-1. Only the 'real' arms are deployable.")
res["per_query"]=per_query
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"kayit: {OUT.name}")
