"""MATCHED CI: sign96+Jev  vs  BM25+Jev  (LME, FR@3) -- eslestirilmis guven araligi.

Asil soru: Delta = FR@3(sign96+Jev) - FR@3(BM25+Jev). Nokta tahmini -1.21 pp,
araligi YOK cunku ilk kosu per-query sonuclari hesaplayip atti.

Bu betik YALNIZ IKI KARAR KOLUNU kosar (dort degil): sign96 ve BM25.
Her sorgu icin top-3 ve FR@3 KALICI saklanir -- ilk kosunun kusuru buydu.

Ayni Jev yeniden siralayicisi, ayni sorular, ayni altin etiketler.
Cikti: MATCHED_CI.json
"""
import json, pickle, re, math, random, asyncio, sys, time
from collections import Counter
from pathlib import Path

MODEL = "jev-1.13.0"
from typesafe_sdk import AsyncTypeSafeClient, Noul

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/MATCHED_CI.json"

N_QUERIES = int(sys.argv[1]) if len(sys.argv) > 1 else 470
CONC, K1, B, BOOT, SEED = 8, 1.2, 0.75, 20000, 20260918
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
    D = [tok(d) for d in docs]; N = len(D)
    avgdl = sum(len(d) for d in D) / max(1, N)
    df = Counter()
    for d in D: df.update(set(d))
    idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    q = tok(query); sc = []
    for d in D:
        tf, dl, s = Counter(d), len(d), 0.0
        for t in q:
            if t in tf:
                f = tf[t]
                s += idf.get(t, 0.0) * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / max(1, avgdl)))
        sc.append(s)
    return sorted(range(N), key=lambda i: -sc[i])[:10]

async def main():
    rows = []
    for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
        rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = rows[:N_QUERIES]
    print(f"sorgu: {len(rows)} | kollar: sign96, BM25 | {MODEL}", flush=True)

    tasks, meta, t0 = [], [], time.time()
    for n, r in enumerate(rows, 1):
        qid = r["qid"]
        item = json.load(open(ITEM / f"{qid}.json", encoding="utf-8"))
        cache = pickle.load(open(W / f"regen/lme/cache_repr/{qid}.pkl", "rb"))
        sess = item["haystack_sessions"]
        flat = [m for s in sess for m in s] if isinstance(sess[0], list) else sess
        if len(flat) != cache["C"].shape[0]:
            print(f"  ATLA {qid}"); continue
        gold  = set(int(g) for g in cache["gold"])
        texts = [text_of(m) for m in flat]
        pools = {"sign96": r["sign96"]["ids"], "bm25": bm25_top10(texts, item["question"])}
        meta.append({"qid": qid, "gold": gold, "pools": pools})
        for arm, ids in pools.items():
            for did in ids:
                tasks.append({"qid": qid, "arm": arm, "did": did,
                              "question": item["question"], "text": texts[did]})
        if n % 100 == 0:
            print(f"  hazirlik {n}/{len(rows)} ({time.time()-t0:.0f}s)", flush=True)

    print(f"model cagrisi: {len(tasks)}", flush=True)
    sem, done = asyncio.Semaphore(CONC), [0]
    async def judge(client, t):
        async with sem:
            try:
                r = await client.system_one(model=MODEL, questions=Q,
                        state={"question": t["question"], "candidate_message": t["text"]})
                t["score"] = r.nouls["answers"].noul
                t["ti"] = getattr(r.usage, "input_tokens", 0)
                t["to"] = getattr(r.usage, "output_tokens", 0)
            except Exception as e:
                t["score"], t["error"] = 0.0, str(e)[:120]
            done[0] += 1
            if done[0] % 500 == 0:
                print(f"  {done[0]}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
        return t
    async with AsyncTypeSafeClient() as client:
        tasks = await asyncio.gather(*(judge(client, t) for t in tasks))
    S = {(t["qid"], t["arm"], t["did"]): t["score"] for t in tasks}

    # --- per-query KALICI (ilk kosunun kusuru buydu)
    pq = []
    for m in meta:
        row = {"qid": m["qid"], "gold": sorted(m["gold"])}
        for arm, ids in m["pools"].items():
            rk = sorted(ids, key=lambda d: -S.get((m["qid"], arm, d), 0.0))
            row[f"{arm}_top3"]  = rk[:3]
            row[f"{arm}_fr3"]   = fr3(rk, m["gold"])
            row[f"{arm}_hit1"]  = 1.0 if rk[0] in m["gold"] else 0.0
            row[f"{arm}_cand"]  = 1.0 if (set(ids) & m["gold"]) else 0.0
        pq.append(row)

    def mean(k): return 100 * sum(r[k] for r in pq) / len(pq)
    d_fr3  = mean("sign96_fr3")  - mean("bm25_fr3")
    d_hit1 = mean("sign96_hit1") - mean("bm25_hit1")

    rnd = random.Random(SEED); N = len(pq)
    def boot(ka, kb):
        ds = []
        for _ in range(BOOT):
            s = [pq[rnd.randrange(N)] for _ in range(N)]
            ds.append(100 * (sum(r[ka] for r in s) - sum(r[kb] for r in s)) / N)
        ds.sort(); return ds[int(.025 * BOOT)], ds[int(.975 * BOOT)]
    ci_fr3  = boot("sign96_fr3",  "bm25_fr3")
    ci_hit1 = boot("sign96_hit1", "bm25_hit1")

    ti = sum(t.get("ti", 0) for t in tasks); to = sum(t.get("to", 0) for t in tasks)
    out = {"model": MODEL, "n": N, "boot_reps": BOOT, "seed": SEED,
           "sign96": {k: round(mean(f"sign96_{k}"), 2) for k in ("cand", "hit1", "fr3")},
           "bm25":   {k: round(mean(f"bm25_{k}"),   2) for k in ("cand", "hit1", "fr3")},
           "delta_fr3": round(d_fr3, 3),  "ci95_fr3": [round(c, 3) for c in ci_fr3],
           "delta_hit1": round(d_hit1, 3), "ci95_hit1": [round(c, 3) for c in ci_hit1],
           "fr3_excludes_zero":  not (ci_fr3[0] <= 0 <= ci_fr3[1]),
           "hit1_excludes_zero": not (ci_hit1[0] <= 0 <= ci_hit1[1]),
           "tokens_in": ti, "tokens_out": to,
           "tokens_per_query_per_arm": round((ti + to) / (2 * N), 1),
           "errors": sum(1 for t in tasks if "error" in t),
           "elapsed_s": round(time.time() - t0, 1), "per_query": pq}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"\n{'':10s} {'tavan':>7s} {'Hit@1':>7s} {'FR@3':>7s}")
    print(f"{'sign96':10s} {out['sign96']['cand']:>7.2f} {out['sign96']['hit1']:>7.2f} {out['sign96']['fr3']:>7.2f}")
    print(f"{'BM25':10s} {out['bm25']['cand']:>7.2f} {out['bm25']['hit1']:>7.2f} {out['bm25']['fr3']:>7.2f}")
    print(f"\nDelta FR@3  = {d_fr3:+.3f} pp  CI95 [{ci_fr3[0]:+.3f}, {ci_fr3[1]:+.3f}]  "
          f"{'SIG' if out['fr3_excludes_zero'] else 'AYIRT EDILEMEZ'}")
    print(f"Delta Hit@1 = {d_hit1:+.3f} pp  CI95 [{ci_hit1[0]:+.3f}, {ci_hit1[1]:+.3f}]  "
          f"{'SIG' if out['hit1_excludes_zero'] else 'AYIRT EDILEMEZ'}")
    print(f"\ntoken {ti+to:,} | kol basina sorgu {out['tokens_per_query_per_arm']:.0f} | "
          f"hata {out['errors']} | {out['elapsed_s']}s")

if __name__ == "__main__":
    asyncio.run(main())
