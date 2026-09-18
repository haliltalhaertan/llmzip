"""ESLESMIS SISTEM MALIYETI: RAM / CPU / gecikme. SIFIR MODEL CAGRISI.

Gun boyu olculmeden kalan tek kaldirac. Karar artik kalite ekseninde verilemiyor
(L-107 ayirt edilemez, L-115 router erisilemez), dolayisiyla maliyet belirleyici.

DURUSTLUK NOKTASI (projenin L-098'de geri cektigi hatanin tekrarini onlemek icin):
  "12 bayt" yalnizca DOKUMAN YUKU. Sorgu zamaninda sign96'nin kodlayiciya ihtiyaci var
  (TF-IDF -> SVD -> 96 boyut) ve o kodlayici depoda SAKLANMAMIS. Bu yuzden burada
  YENIDEN KURULUYOR ve maliyeti ACIKCA sayiliyor. Eski iddia tam bu parcayi atliyordu.

OLCULENLER (arsiv basina, gercek zamanlama):
  BM25   : indeks kurma suresi, indeks RAM (postings+IDF+doclen), sorgu gecikmesi
  sign96 : kodlayici fit suresi, KODLAYICI RAM (vocab+SVD bilesenleri),
           kod matrisi RAM (paketlenmis 96 bit = 12 B/dok), sorgu kodlama + tarama

Cikti: SYSTEM_COST.json
"""
import json, pickle, re, math, time, sys, gc
import numpy as np
from collections import Counter
from pathlib import Path

W=Path("C:/Users/MDP/dev/llmzip-work")
CKPT=W/"_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM=W/"regen/lme/items"
OUT =W/"audit_hard_r4/SYSTEM_COST.json"
K1,B=1.2,0.75; N_ARCH=40; REPS=5
FROZEN=re.compile(r"\b\w\w+\b")
STOP=set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m): return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m,dict) else str(m)[:1200]

def deep_size(o, seen=None):
    """Gercek RAM: ic ice python nesnelerini tekrarsiz say."""
    if seen is None: seen=set()
    i=id(o)
    if i in seen: return 0
    seen.add(i); s=sys.getsizeof(o)
    if isinstance(o,dict):
        for k,v in o.items(): s+=deep_size(k,seen)+deep_size(v,seen)
    elif isinstance(o,(list,tuple,set)):
        for x in o: s+=deep_size(x,seen)
    elif isinstance(o,np.ndarray): s=o.nbytes
    return s

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows+=[json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
rows=rows[:N_ARCH]
print(f"arsiv: {len(rows)} | tekrar: {REPS} | zamanlama perf_counter", flush=True)

recs=[]
for n,r in enumerate(rows,1):
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    C=c["C"]; N=C.shape[0]
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=N: continue
    texts=[text_of(m) for m in flat]; question=item["question"]

    # ---------------- BM25: kurma + RAM + sorgu
    gc.collect(); t=time.perf_counter()
    D=[tok(x) for x in texts]; avg=sum(len(x) for x in D)/max(1,N)
    df=Counter()
    for x in D: df.update(set(x))
    idf={t_: math.log(1+(N-k+0.5)/(k+0.5)) for t_,k in df.items()}
    TF=[Counter(x) for x in D]; DL=[len(x) for x in D]
    bm_build=time.perf_counter()-t
    bm_ram=deep_size(idf)+deep_size(TF)+deep_size(DL)

    q=tok(question)
    def bm_query():
        o=np.zeros(N)
        for i in range(N):
            tf,dl,s=TF[i],DL[i],0.0
            for t_ in q:
                if t_ in tf:
                    f=tf[t_]; s+=idf.get(t_,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
            o[i]=s
        return np.argsort(-o,kind="stable")[:10]
    bm_query()
    t=time.perf_counter()
    for _ in range(REPS): bm_query()
    bm_lat=(time.perf_counter()-t)/REPS

    # ---------------- sign96: kodlayici YENIDEN KURULUR (depoda yok)
    gc.collect(); t=time.perf_counter()
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    vec=TfidfVectorizer(stop_words=list(STOP), token_pattern=r"\b\w\w+\b")
    Xt=vec.fit_transform(texts)
    k=min(96, max(2, min(Xt.shape)-1))
    svd=TruncatedSVD(n_components=k, random_state=0)
    Z=svd.fit_transform(Xt)
    codes=np.packbits(Z>0, axis=1)               # 96 bit -> 12 bayt/dokuman
    sg_build=time.perf_counter()-t
    enc_ram=deep_size(vec.vocabulary_)+svd.components_.nbytes+ \
            (svd.singular_values_.nbytes if hasattr(svd,"singular_values_") else 0)
    code_ram=codes.nbytes

    def sg_query():
        z=svd.transform(vec.transform([question]))[0]
        qb=np.packbits(z>0)
        d=np.unpackbits(codes^qb,axis=1).sum(1)   # Hamming
        return np.argsort(d,kind="stable")[:10]
    sg_query()
    t=time.perf_counter()
    for _ in range(REPS): sg_query()
    sg_lat=(time.perf_counter()-t)/REPS
    # yalniz tarama (kodlama haric) -- "12 bayt ucuz" iddiasinin test edildigi yer
    z=svd.transform(vec.transform([question]))[0]; qb=np.packbits(z>0)
    t=time.perf_counter()
    for _ in range(REPS):
        d=np.unpackbits(codes^qb,axis=1).sum(1); np.argsort(d,kind="stable")[:10]
    scan_lat=(time.perf_counter()-t)/REPS
    encode_lat=sg_lat-scan_lat

    recs.append({"qid":qid,"N":N,
      "bm25":{"build_s":bm_build,"ram_bytes":bm_ram,"query_ms":1000*bm_lat},
      "sign96":{"build_s":sg_build,"encoder_ram_bytes":enc_ram,"code_ram_bytes":code_ram,
                "total_ram_bytes":enc_ram+code_ram,"query_ms":1000*sg_lat,
                "scan_only_ms":1000*scan_lat,"encode_ms":1000*encode_lat,
                "svd_components":k}})
    if n%10==0: print(f"  {n}/{len(rows)}", flush=True)

def med(f): return float(np.median([f(x) for x in recs]))
M=len(recs); Nmed=med(lambda x:x["N"])
res={"n_archives":M,"median_docs":Nmed,"reps":REPS,"model_calls":0,
 "bm25":{"build_s":round(med(lambda x:x["bm25"]["build_s"]),4),
         "ram_kb":round(med(lambda x:x["bm25"]["ram_bytes"])/1024,1),
         "query_ms":round(med(lambda x:x["bm25"]["query_ms"]),3)},
 "sign96":{"build_s":round(med(lambda x:x["sign96"]["build_s"]),4),
   "encoder_ram_kb":round(med(lambda x:x["sign96"]["encoder_ram_bytes"])/1024,1),
   "code_ram_kb":round(med(lambda x:x["sign96"]["code_ram_bytes"])/1024,1),
   "total_ram_kb":round(med(lambda x:x["sign96"]["total_ram_bytes"])/1024,1),
   "query_ms":round(med(lambda x:x["sign96"]["query_ms"]),3),
   "scan_only_ms":round(med(lambda x:x["sign96"]["scan_only_ms"]),3),
   "encode_ms":round(med(lambda x:x["sign96"]["encode_ms"]),3)},
 "encoder_note":("the sign96 encoder was NEVER stored in this repo, so it is rebuilt here and its "
   "cost is counted explicitly. The original '12 bytes' claim omitted exactly this component."),
 "per_archive":recs}
res["ratios"]={
 "ram_sign96_over_bm25":round(res["sign96"]["total_ram_kb"]/res["bm25"]["ram_kb"],2),
 "ram_codes_only_over_bm25":round(res["sign96"]["code_ram_kb"]/res["bm25"]["ram_kb"],3),
 "query_sign96_over_bm25":round(res["sign96"]["query_ms"]/res["bm25"]["query_ms"],2),
 "scan_only_over_bm25":round(res["sign96"]["scan_only_ms"]/res["bm25"]["query_ms"],3),
 "build_sign96_over_bm25":round(res["sign96"]["build_s"]/res["bm25"]["build_s"],1)}
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")

print(f"\n=== ESLESMIS MALIYET (medyan, {M} arsiv, ~{Nmed:.0f} belge) ===")
print(f"{'':22s} {'BM25':>12s} {'sign96':>12s} {'oran':>8s}")
print(f"{'indeks RAM (KB)':22s} {res['bm25']['ram_kb']:>12.1f} {res['sign96']['total_ram_kb']:>12.1f} "
      f"{res['ratios']['ram_sign96_over_bm25']:>8.2f}x")
print(f"{'  - yalniz kodlar':22s} {'':>12s} {res['sign96']['code_ram_kb']:>12.1f} "
      f"{res['ratios']['ram_codes_only_over_bm25']:>8.3f}x")
print(f"{'  - kodlayici':22s} {'':>12s} {res['sign96']['encoder_ram_kb']:>12.1f}")
print(f"{'sorgu (ms)':22s} {res['bm25']['query_ms']:>12.3f} {res['sign96']['query_ms']:>12.3f} "
      f"{res['ratios']['query_sign96_over_bm25']:>8.2f}x")
print(f"{'  - yalniz tarama':22s} {'':>12s} {res['sign96']['scan_only_ms']:>12.3f} "
      f"{res['ratios']['scan_only_over_bm25']:>8.3f}x")
print(f"{'  - sorgu kodlama':22s} {'':>12s} {res['sign96']['encode_ms']:>12.3f}")
print(f"{'kurma (s)':22s} {res['bm25']['build_s']:>12.4f} {res['sign96']['build_s']:>12.4f} "
      f"{res['ratios']['build_sign96_over_bm25']:>8.1f}x")
print(f"\nkayit: {OUT.name}")
