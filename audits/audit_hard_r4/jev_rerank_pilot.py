"""PILOT: 96-bit aday havuzu + Jev semantik yeniden siralama (LME).

HIPOTEZ: 96-bit kod dogru belgeyi top-10'a sokuyor ama yanlis siraya koyuyorsa,
semantik bir yeniden siralayici tam bu hatayi duzeltebilir. Daha once yalniz
SOZLUKSEL (BM25) yeniden siralama denendi; semantik olan hic denenmedi.

TAVAN KURALI: yeniden siralayici aday havuzunun disina cikamaz. Her kol icin
candidate Hit@10 (tavan) ve yeniden siralama sonrasi Hit@1/FR@3 AYRI raporlanir.

IS BOLUMU:
  KOD   : adaylari stored top-10 id'lerden alir, metni items/*.json'dan cikarir,
          skorlari toplar, siralar, metrikleri hesaplar.
  MODEL : her (soru, aday) cifti icin TEK yargi -- bu aday soruyu cevaplamaya yarar mi.
  KOD   : yeniden siralar ve karari verir. Hicbir sayi model tarafindan uretilmez.

Kollar: sign96 (12 B), float_raw, float_std, asym  -- hepsi ayni stored havuzdan.
Cikti: JEV_RERANK_PILOT.json
"""
import json, pickle, asyncio, sys, time
from pathlib import Path

MODEL = "jev-1.13.0"                       # surum PINLI
from typesafe_sdk import AsyncTypeSafeClient, Noul

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/JEV_RERANK_PILOT.json"

ARMS      = ["sign96", "float_raw", "float_std", "asym"]
N_QUERIES = int(sys.argv[1]) if len(sys.argv) > 1 else 60
CONC      = 8

QUESTION = {
    "answers": Noul(instructions=(
        "Does this candidate message contain the information needed to answer the question? "
        "Answer yes only if the message itself states the fact the question asks for. "
        "Answer no if it is merely on a related topic, mentions the same entities, or is part "
        "of the same conversation without containing the answer."
    )),
}

def load_query(qid):
    item  = json.load(open(ITEM / f"{qid}.json", encoding="utf-8"))
    cache = pickle.load(open(W / f"regen/lme/cache_repr/{qid}.pkl", "rb"))
    sess  = item["haystack_sessions"]
    flat  = [m for s in sess for m in s] if isinstance(sess[0], list) else sess
    if len(flat) != cache["C"].shape[0]:
        raise ValueError(f"{qid}: hizalama bozuk {len(flat)} vs {cache['C'].shape[0]}")
    return item, flat, set(int(g) for g in cache["gold"])

def text_of(msg):
    if isinstance(msg, dict):
        return f"{msg.get('role','')}: {msg.get('content','')}"[:1200]
    return str(msg)[:1200]

def fr3(ranked, gold):
    """Fractional evidence recall@3 -- ilk 3'teki altin orani."""
    if not gold:
        return 0.0
    return len(set(ranked[:3]) & gold) / len(gold)

async def main():
    rows = []
    for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    rows = rows[:N_QUERIES]
    print(f"sorgu: {len(rows)} | kol: {ARMS} | model: {MODEL}", flush=True)

    # --- 1. Adaylari ve metinleri topla (KOD)
    tasks, meta = [], []
    for r in rows:
        qid = r["qid"]
        try:
            item, flat, gold = load_query(qid)
        except Exception as e:
            print(f"  ATLA {qid}: {e}", flush=True)
            continue
        for arm in ARMS:
            ids = r[arm]["ids"]
            meta.append({"qid": qid, "arm": arm, "ids": ids, "gold": gold,
                         "question": item["question"], "n_docs": r["N"]})
            for did in ids:
                tasks.append({"qid": qid, "arm": arm, "did": did,
                              "question": item["question"], "text": text_of(flat[did])})
    print(f"model cagrisi: {len(tasks)} (soru x kol x 10 aday)", flush=True)

    # --- 2. Yargi (MODEL) -- sadece ilgililik, hicbir sayi degil
    sem, done, t0 = asyncio.Semaphore(CONC), [0], time.time()
    async def judge(client, t):
        async with sem:
            state = {"question": t["question"], "candidate_message": t["text"]}
            try:
                r = await client.system_one(model=MODEL, state=state, questions=QUESTION)
                t["score"] = r.nouls["answers"].noul
                t["model_used"] = getattr(r, "model", None) or MODEL
                t["tok_in"]  = getattr(r.usage, "input_tokens", 0)
                t["tok_out"] = getattr(r.usage, "output_tokens", 0)
            except Exception as e:
                t["score"], t["error"] = 0.0, str(e)[:120]
            done[0] += 1
            if done[0] % 100 == 0:
                print(f"  {done[0]}/{len(tasks)}  ({time.time()-t0:.0f}s)", flush=True)
        return t

    async with AsyncTypeSafeClient() as client:
        tasks = await asyncio.gather(*(judge(client, t) for t in tasks))

    S = {(t["qid"], t["arm"], t["did"]): t["score"] for t in tasks}

    # --- 3. Yeniden sirala ve olc (KOD)
    from collections import defaultdict
    agg = defaultdict(lambda: {"n": 0, "cand_hit10": 0.0,
                               "base_hit1": 0.0, "base_fr3": 0.0,
                               "jev_hit1": 0.0,  "jev_fr3": 0.0})
    per_query = []
    for m in meta:
        gold, ids = m["gold"], m["ids"]
        ranked = sorted(ids, key=lambda d: -S.get((m["qid"], m["arm"], d), 0.0))
        a = agg[m["arm"]]
        a["n"] += 1
        a["cand_hit10"] += 1.0 if (set(ids) & gold) else 0.0
        a["base_hit1"]  += 1.0 if ids[0] in gold else 0.0
        a["jev_hit1"]   += 1.0 if ranked[0] in gold else 0.0
        a["base_fr3"]   += fr3(ids, gold)
        a["jev_fr3"]    += fr3(ranked, gold)
        # KUSUR DUZELTMESI 2026-09-18: ilk surum yalniz top1'i sakladi ve per-query
        # FR@3'u hesaplayip ATTI -- bu, denetimlerin T1'de bulup elestirdigi kusurun
        # birebir tekrariydi (decision_tests.py:156-191). Araliksiz sayi uretilemez.
        per_query.append({"qid": m["qid"], "arm": m["arm"],
                          "base_top1": ids[0], "jev_top1": ranked[0],
                          "gold": sorted(gold),
                          "base_hit1": 1.0 if ids[0] in gold else 0.0,
                          "jev_hit1":  1.0 if ranked[0] in gold else 0.0,
                          "base_fr3":  fr3(ids, gold),
                          "jev_fr3":   fr3(ranked, gold),
                          "improved": (ranked[0] in gold) and (ids[0] not in gold),
                          "broke":    (ids[0] in gold) and (ranked[0] not in gold)})

    res = {}
    for arm, a in agg.items():
        n = a["n"]
        res[arm] = {k: round(100 * v / n, 2) for k, v in a.items() if k != "n"}
        res[arm]["n"] = n
        res[arm]["delta_hit1"] = round(res[arm]["jev_hit1"] - res[arm]["base_hit1"], 2)
        res[arm]["delta_fr3"]  = round(res[arm]["jev_fr3"]  - res[arm]["base_fr3"], 2)

    tok_in  = sum(t.get("tok_in", 0)  for t in tasks)
    tok_out = sum(t.get("tok_out", 0) for t in tasks)
    errs    = sum(1 for t in tasks if "error" in t)
    out = {"model": MODEL, "n_queries": len(rows), "arms": ARMS,
           "elapsed_s": round(time.time() - t0, 1),
           "model_calls": len(tasks), "errors": errs,
           "tokens_in": tok_in, "tokens_out": tok_out,
           "tokens_per_query": round((tok_in + tok_out) / max(1, len(rows)), 1),
           "results": res, "per_query": per_query}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"\n{'kol':11s} {'tavan H@10':>11s} {'H@1 once':>9s} {'H@1 Jev':>8s} {'delta':>7s} "
          f"{'FR3 once':>9s} {'FR3 Jev':>8s} {'delta':>7s}")
    for arm in ARMS:
        r = res.get(arm)
        if r:
            print(f"{arm:11s} {r['cand_hit10']:>11.2f} {r['base_hit1']:>9.2f} {r['jev_hit1']:>8.2f} "
                  f"{r['delta_hit1']:>+7.2f} {r['base_fr3']:>9.2f} {r['jev_fr3']:>8.2f} {r['delta_fr3']:>+7.2f}")
    imp = sum(1 for p in per_query if p["improved"]); brk = sum(1 for p in per_query if p["broke"])
    print(f"\nduzeltti: {imp} | bozdu: {brk} | hata: {errs}")
    print(f"token: in={tok_in:,} out={tok_out:,} | sorgu basi {out['tokens_per_query']:.0f} | sure {out['elapsed_s']}s")

if __name__ == "__main__":
    asyncio.run(main())
