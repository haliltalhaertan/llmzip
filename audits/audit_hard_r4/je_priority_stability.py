"""Jev oncelik kovalarinin kosudan-kosuya kararliligi. SIFIR onceki veri ezme.

Gerekce: rerank hattinda tek kosu sayisinin sonuc olmadigi olculdu (-1.21 -> -2.10).
Ayni soru yargi kovalari icin HIC sorulmadi: 98 A1 isareti ikinci kosuda da A1 mi?
Eger kovalar savruluyorsa 21 Eylul Muse hedef listesi saglam degil.

Tasarim: mevcut 674 yargidan 15 A1 + 15 A5 tabakali ornek, YALNIZ bunlari yeniden
yargila, kova uyumunu olc. prioritize_unaudited.py ile AYNI sorular, AYNI model,
AYNI karar fonksiyonu (cagri sekli o dosyadan kopya). Cikti ayri dosya.
"""
import json, random, asyncio
from pathlib import Path
from prioritize_unaudited import QUESTIONS, decide, judge

W = Path("C:/Users/MDP/dev/llmzip-work")
OUT = W / "audit_hard_r4/JE_PRIORITY_STABILITY.json"
from typesafe_sdk import AsyncTypeSafeClient

rng = random.Random(20260919)
d = json.load(open(W / "audit_hard_r4/UNAUDITED_PRIORITY.json", encoding="utf-8"))
a1 = [x for x in d if x.get("priority") == "A1_POSSIBLE_HIDDEN_CONTRADICTION"]
a5 = [x for x in d if x.get("priority") == "A5_SKIP"]
sample = rng.sample(a1, 15) + rng.sample(a5, 15)
print(f"ornek: 15 A1 + 15 A5 = {len(sample)}", flush=True)

# head'ler yargi dosyasında yok; diskten tekrar oku (1500 char, ayni pencere)
for it in sample:
    p = W / it["path"]
    try:
        it["head"] = p.read_text(encoding="utf-8", errors="replace")[:1500]
    except Exception as e:
        it["head"] = ""; it["unreadable"] = str(e)[:100]

async def main():
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(6)
        async def one(it):
            async with sem:
                for a in range(3):
                    try:
                        j = await judge(client, it)
                        return {"path": it["path"], "old": it["priority"],
                                "new": decide(j), "scores": {k: round(v, 3) if isinstance(v, float) else v
                                                             for k, v in j.items() if not k.startswith("usage")},
                                "tin": j.get("usage_in"), "tout": j.get("usage_out")}
                    except Exception as e:
                        if a == 2:
                            return {"path": it["path"], "old": it["priority"], "new": "ERROR",
                                    "error": str(e)[:120]}
                        await asyncio.sleep(2 * (a + 1))
        out = await asyncio.gather(*(one(i) for i in sample))
    agree = sum(1 for o in out if o["new"] == o["old"])
    a1stay = sum(1 for o in out if o["old"].startswith("A1") and o["new"].startswith("A1"))
    a5stay = sum(1 for o in out if o["old"] == "A5_SKIP" and o["new"] == "A5_SKIP")
    res = {"n": len(out), "exact_bucket_agreement": agree,
           "A1_stays_A1": f"{a1stay}/15", "A5_stays_A5": f"{a5stay}/15",
           "tokens_in": sum(o.get("tin") or 0 for o in out),
           "tokens_out": sum(o.get("tout") or 0 for o in out),
           "errors": sum(1 for o in out if o["new"] == "ERROR"),
           "rows": out}
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"kova uyumu: {agree}/{len(out)} | A1->A1 {a1stay}/15 | A5->A5 {a5stay}/15 | "
          f"hata {res['errors']} | tin {res['tokens_in']} tout {res['tokens_out']}")
    for o in out:
        if o["new"] != o["old"]:
            print(f"  KAYMA: {o['old'][:12]:12s} -> {o['new'][:12]:12s}  {o['path'][:70]}")

if __name__ == "__main__":
    asyncio.run(main())
