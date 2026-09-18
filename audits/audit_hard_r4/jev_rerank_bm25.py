"""EKSIK KOL: BM25 aday havuzu + Jev yeniden siralama (LME).

jev_rerank_pilot.py kod havuzlarini Jev ile yeniden siraladi ve BM25'i TEK BASINA
gecti. Ama bu adil karsilastirma DEGIL: pahali yeniden siralanmis bir sistemi,
yeniden siralanmamis ucuz bir sisteme karsi olcuyor.

Dogru soru: AYNI Jev yeniden siralayicisi BM25 havuzuna uygulanirsa ne olur?
Kod havuzu ancak BM25 havuzunu da gecerse anlamli.

LME icin BM25 per-query top-10 saklanmadigi icin BM25'i BURADA kuruyoruz
(textbook k1=1.2, b=0.75; frozen tokenizer \\b\\w\\w+\\b -- hakem sozlesmesinin
birincil yapilandirmasi). Ayni items/*.json metinleri, ayni altin etiketler.

Cikti: JEV_RERANK_BM25.json
"""
import json, pickle, re, math, asyncio, sys, time
from collections import Counter, defaultdict
from pathlib import Path

MODEL = "jev-1.13.0"
from typesafe_sdk import AsyncTypeSafeClient, Noul

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/JEV_RERANK_BM25.json"

N_QUERIES = int(sys.argv[1]) if len(sys.argv) > 1 else 470
CONC, K1, B = 8, 1.2, 0.75
FROZEN = re.compile(r"\b\w\w+\b")

STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

QUESTION = {
    "answers": Noul(instructions=(
        "Does this candidate message contain the information needed to answer the question? "
        "Answer yes only if the message itself states the fact the question asks for. "
        "Answer no if it is merely on a related topic, mentions the same entities, or is part "
        "of the same conversation without containing the answer."
    )),
}

def tok(s):
    return [t for t in FROZEN.findall(s.lower()) if t not in STOP]

def bm25_top10(docs, query):
    """Ders kitabi BM25. docs: metin listesi. Doner: en iyi 10 indeks."""
    D    = [tok(d) for d in docs]
    N    = len(D)
    avgdl = sum(len(d) for d in D) / max(1, N)
    df   = Counter()
    for d in D:
        df.update(set(d))
    idf  = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    q    = tok(query)
    scores = []
    for i, d in enumerate(D):
        tf, dl, s = Counter(d), len(d), 0.0
        for t in q:
            if t in tf:
                f = tf[t]
                s += idf.get(t, 0.0) * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / max(1, avgdl)))
        scores.append(s)
    return sorted(range(N), key=lambda i: -scores[i])[:10]

def text_of(m):
    if isinstance(m, dict):
        return f"{m.get('role','')}: {m.get('content','')}"[:1200]
    return str(m)[:1200]

def fr3(ranked, gold):
    return len(set(ranked[:3]) & gold) / len(gold) if gold else 0.0

async def main():
    rows = []
    for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    rows = rows[:N_QUERIES]
    print(f"sorgu: {len(rows)} | BM25 textbook k1={K1} b={B} frozen tokenizer", flush=True)

    tasks, meta, t0 = [], [], time.time()
    for n, r in enumerate(rows, 1):
        qid  = r["qid"]
        item = json.load(open(ITEM / f"{qid}.json", encoding="utf-8"))
        cache = pickle.load(open(W / f"regen/lme/cache_repr/{qid}.pkl", "rb"))
        sess = item["haystack_sessions"]
        flat = [m for s in sess for m in s] if isinstance(sess[0], list) else sess
        if len(flat) != cache["C"].shape[0]:
            print(f"  ATLA {qid}: hizalama"); continue
        gold = set(int(g) for g in cache["gold"])
        ids  = bm25_top10([text_of(m) for m in flat], item["question"])
        meta.append({"qid": qid, "ids": ids, "gold": gold})
        for did in ids:
            tasks.append({"qid": qid, "did": did, "question": item["question"],
                          "text": text_of(flat[did])})
        if n % 100 == 0:
            print(f"  BM25 kuruldu {n}/{len(rows)} ({time.time()-t0:.0f}s)", flush=True)

    print(f"model cagrisi: {len(tasks)}", flush=True)
    sem, done = asyncio.Semaphore(CONC), [0]
    async def judge(client, t):
        async with sem:
            try:
                r = await client.system_one(model=MODEL,
                        state={"question": t["question"], "candidate_message": t["text"]},
                        questions=QUESTION)
                t["score"]   = r.nouls["answers"].noul
                t["tok_in"]  = getattr(r.usage, "input_tokens", 0)
                t["tok_out"] = getattr(r.usage, "output_tokens", 0)
            except Exception as e:
                t["score"], t["error"] = 0.0, str(e)[:120]
            done[0] += 1
            if done[0] % 500 == 0:
                print(f"  {done[0]}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
        return t

    async with AsyncTypeSafeClient() as client:
        tasks = await asyncio.gather(*(judge(client, t) for t in tasks))
    S = {(t["qid"], t["did"]): t["score"] for t in tasks}

    agg = {"n": 0, "cand_hit10": 0.0, "base_hit1": 0.0, "base_fr3": 0.0,
           "jev_hit1": 0.0, "jev_fr3": 0.0}
    per_query = []   # KUSUR DUZELTMESI 2026-09-18: ilk surumde hic saklanmiyordu
    for m in meta:
        ids, gold = m["ids"], m["gold"]
        ranked = sorted(ids, key=lambda d: -S.get((m["qid"], d), 0.0))
        agg["n"] += 1
        agg["cand_hit10"] += 1.0 if (set(ids) & gold) else 0.0
        agg["base_hit1"]  += 1.0 if ids[0] in gold else 0.0
        agg["jev_hit1"]   += 1.0 if ranked[0] in gold else 0.0
        agg["base_fr3"]   += fr3(ids, gold)
        agg["jev_fr3"]    += fr3(ranked, gold)
        per_query.append({"qid": m["qid"], "base_top1": ids[0], "jev_top1": ranked[0],
                          "gold": sorted(gold),
                          "base_hit1": 1.0 if ids[0] in gold else 0.0,
                          "jev_hit1":  1.0 if ranked[0] in gold else 0.0,
                          "base_fr3":  fr3(ids, gold), "jev_fr3": fr3(ranked, gold)})

    n = agg["n"]
    res = {k: round(100 * v / n, 2) for k, v in agg.items() if k != "n"}
    res["n"] = n
    res["delta_hit1"] = round(res["jev_hit1"] - res["base_hit1"], 2)
    res["delta_fr3"]  = round(res["jev_fr3"]  - res["base_fr3"], 2)
    ti = sum(t.get("tok_in", 0) for t in tasks); to = sum(t.get("tok_out", 0) for t in tasks)
    OUT.write_text(json.dumps({"model": MODEL, "arm": "BM25_textbook_frozen",
                               "k1": K1, "b": B, "results": res,
                               "tokens_in": ti, "tokens_out": to,
                               "elapsed_s": round(time.time()-t0, 1),
                               "errors": sum(1 for t in tasks if "error" in t),
                               "per_query": per_query},
                              indent=1), encoding="utf-8")
    print(f"\nBM25 havuzu: tavan H@10={res['cand_hit10']:.2f}")
    print(f"  H@1  {res['base_hit1']:.2f} -> {res['jev_hit1']:.2f}  ({res['delta_hit1']:+.2f})")
    print(f"  FR@3 {res['base_fr3']:.2f} -> {res['jev_fr3']:.2f}  ({res['delta_fr3']:+.2f})")
    print(f"token in={ti:,} out={to:,} | sure {time.time()-t0:.0f}s")

if __name__ == "__main__":
    asyncio.run(main())
