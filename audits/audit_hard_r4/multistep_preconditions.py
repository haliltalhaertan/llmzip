"""COK-ADIMLI HAFIZA CAGIRMA: mekanizma ailelerinin ONKOSULLARI. SIFIR MODEL CAGRISI.

Beyin firtinasi oncesi uc olcum. Amac fikir uretmek degil, hangi fikirlerin
ONKOSULUNUN zaten saglandigini/saglanmadigini gostermek.

A) ONKOSUL: coklu-gold sorgularda ilk adim calisiyor mu?
   Cok-adimli geri cagirma "once bir kaniti bul" varsayar. Eger gold'lardan HICBIRI
   top-10'da degilse ikinci tur da imkansiz.

B) ORACLE TAVAN: "ilk kaniti sorguya ekle" ailesi (mekanizma 1-3)
   Oracle: bulunan gold'un metnini soruya ekle, KALAN gold'larin BM25 rank'i duzeliyor mu?
   Bu ailenin UST SINIRI. Gercek sistem bundan iyi olamaz.
   SINIR: yalniz lexical taraf hesaplanabilir; sign96 icin kodlayici yok (qC saklı, encoder degil).

C) KAPSAM BASLIGI: "cesitlilik-farkindali top-3 secimi" (mekanizma 13)
   FR@3 = |top3 ∩ gold|/|gold| -> cesitlilik odullendiriyor. Havuzda birden fazla gold
   varken kac tanesi top-3'e girmis? Girmediyse SIFIR ek retrieval ile kazanc var demektir.

Cikti: MULTISTEP_PRECONDITIONS.json
"""
import json, pickle, re, math
import numpy as np
from collections import Counter
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/MULTISTEP_PRECONDITIONS.json"

K1, B = 1.2, 0.75
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]

def bm25_factory(docs):
    """Ayni korpus icin tekrar tekrar sorgu atmak uzere IDF'i bir kez kur."""
    D=[tok(d) for d in docs]; N=len(D); avg=sum(len(x) for x in D)/max(1,N)
    df=Counter()
    for x in D: df.update(set(x))
    idf={t: math.log(1+(N-c+0.5)/(c+0.5)) for t,c in df.items()}
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
    return score, idf

def rank_of(scores, i):
    gs=scores[i]; return int((scores>gs).sum())+1, int((scores>gs).sum())+int((scores==gs).sum())

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

A_ok=A_no=0; A_multi=0
expand=[]      # oracle genisletme sonuclari
cover=[]       # kapsam basligi
print(f"sorgu: {len(rows)} | oracle genisletme BM25 tarafinda hesaplaniyor...", flush=True)

for n,r in enumerate(rows,1):
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    golds=[int(g) for g in c["gold"]]
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=c["C"].shape[0]: continue
    texts=[text_of(m) for m in flat]
    score,idf=bm25_factory(texts)
    q=tok(item["question"])
    base=score(q)
    top10=set(map(int,np.argsort(-base,kind="stable")[:10]))
    sign10=set(r["sign96"]["ids"])
    pool=top10|sign10

    # --- C) kapsam basligi: havuzda kac gold var, top-3'e kac girdi
    in_pool=[g for g in golds if g in top10]
    if len(in_pool)>=2:
        top3=list(map(int,np.argsort(-base,kind="stable")[:3]))
        cover.append({"qid":qid,"n_gold":len(golds),"golds_in_pool":len(in_pool),
                      "golds_in_top3":sum(1 for g in golds if g in top3)})

    if len(golds)<2: continue
    A_multi+=1
    found=[g for g in golds if g in pool]
    if not found: A_no+=1; continue
    A_ok+=1

    # --- B) ORACLE: bulunan gold'un metnini soruya ekle, KALAN gold'lar duzeliyor mu?
    anchor=found[0]
    rest=[g for g in golds if g!=anchor]
    if not rest: continue
    q_exp = q + tok(texts[anchor])
    exp = score(q_exp)
    # yalniz anchor'i disla (kendini bulmasin)
    exp[anchor]=-1e9; base_m=base.copy(); base_m[anchor]=-1e9
    for g in rest:
        b_o,b_p = rank_of(base_m,g); e_o,e_p = rank_of(exp,g)
        expand.append({"qid":qid,"gold":g,"rank_before":b_p,"rank_after":e_p,
                       "improved":e_p<b_p,"into_top10":(e_p<=10 and b_p>10)})
    if n%150==0: print(f"  {n}/{len(rows)}", flush=True)

print(f"\n=== A) ONKOSUL: ilk adim calisiyor mu? (coklu-gold sorgular) ===")
print(f"  coklu-gold sorgu            : {A_multi}")
print(f"  en az bir gold havuzda      : {A_ok}  ({100*A_ok/max(1,A_multi):.1f}%)")
print(f"  hicbiri havuzda degil       : {A_no}  ({100*A_no/max(1,A_multi):.1f}%)")

imp=sum(1 for x in expand if x["improved"]); tot=len(expand)
into=sum(1 for x in expand if x["into_top10"])
before_top10=sum(1 for x in expand if x["rank_before"]<=10)
after_top10 =sum(1 for x in expand if x["rank_after"]<=10)
med_b=int(np.median([x["rank_before"] for x in expand])) if expand else 0
med_a=int(np.median([x["rank_after"]  for x in expand])) if expand else 0
print(f"\n=== B) ORACLE TAVAN: 'ilk kaniti sorguya ekle' (lexical taraf) ===")
print(f"  test edilen kalan-gold      : {tot}")
print(f"  rank'i IYILESEN             : {imp}  ({100*imp/max(1,tot):.1f}%)")
print(f"  top-10 DISINDAN ICINE giren : {into}")
print(f"  top-10'da olan: once {before_top10} -> sonra {after_top10}  ({after_top10-before_top10:+d})")
print(f"  medyan rank   : once {med_b} -> sonra {med_a}")

c2=[x for x in cover if x["golds_in_pool"]>x["golds_in_top3"]]
print(f"\n=== C) KAPSAM BASLIGI: cesitlilik-farkindali top-3 ===")
print(f"  havuzda >=2 gold olan sorgu : {len(cover)}")
print(f"  havuzda olup top-3'e GIRMEYEN gold barindiran: {len(c2)}")
if cover:
    tot_pool=sum(x["golds_in_pool"] for x in cover); tot_t3=sum(x["golds_in_top3"] for x in cover)
    print(f"  havuzdaki gold toplami {tot_pool} -> top-3'e giren {tot_t3} "
          f"(kacirilan {tot_pool-tot_t3})")

res={"A_precondition":{"multi_gold_queries":A_multi,"at_least_one_gold_in_pool":A_ok,
      "none_in_pool":A_no,"pct_first_step_works":round(100*A_ok/max(1,A_multi),1)},
     "B_oracle_expansion":{"n_remaining_golds":tot,"improved":imp,
      "pct_improved":round(100*imp/max(1,tot),1),"entered_top10":into,
      "in_top10_before":before_top10,"in_top10_after":after_top10,
      "median_rank_before":med_b,"median_rank_after":med_a,
      "limit":"lexical/BM25 side only; sign96 expansion needs the encoder, which is not stored"},
     "C_coverage_headroom":{"queries_with_2plus_golds_in_pool":len(cover),
      "queries_missing_a_pooled_gold_from_top3":len(c2),
      "pooled_golds":sum(x["golds_in_pool"] for x in cover) if cover else 0,
      "pooled_golds_in_top3":sum(x["golds_in_top3"] for x in cover) if cover else 0},
     "note":"zero model calls; oracle = upper bound, a real system cannot exceed it"}
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nkayit: {OUT.name}")
