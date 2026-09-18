"""Denetlenmemis dosyalar icin risk onceligi — TypeSafe System One (Jev).

Problem: proje icerigi ~14.700 dosya; 4 denetim turu ~%13'une dokundu.
Muse kotasi 21 Eylul'e kadar kapali; o gun hangi dosyalarin denetlenecegini
anlamli secmek gerekiyor. Onceki secim regex sayi-aramayla yapildi (kaba).

Kod: hic denetlenmemis kod/sonuc dosyalarini bulur, bas kismini + baglami cikarir.
Model: "bu dosya yayinlanmis bir sonucu tasiyor mu, riski nedir" yargisi verir.
Karar: kodda; cikti oncelik sirali CSV.

Cikti: UNAUDITED_PRIORITY.json / .csv
"""
import json, re, sys, asyncio, collections
from pathlib import Path
MODEL = "jev-1.13.0"  # surum PINLI: alias degil (esikler bu surume gore)
from typesafe_sdk import AsyncTypeSafeClient, Noul, Score, Choice

W = Path("C:/Users/MDP/dev/llmzip-work")
OUT = W / "audit_hard_r4/UNAUDITED_PRIORITY.json"

PROJECT = (
    "Research project: compress a document embedding to 12-48 bytes and still retrieve the "
    "right document (per-archive TF-IDF + SVD -> sign codes), compared against a BM25 "
    "lexical baseline on RealTalk, PerLTQA, LoCoMo and LME. Published conclusion: STOP, "
    "because a fairly built BM25 beats the best 48-byte code. Four audit rounds have "
    "examined the decision pipeline itself; these files were never opened by any auditor. "
    "The audits' recurring finding was: computations are correct, but write-ups overstate, "
    "corrections get written and never applied, and samples get presented as full coverage."
)

SKIP = ("__pycache__", ".pytest_cache", ".hf_modules", ".git", "venv", "wheels_wsl", "node_modules")
# Denetim turlarinda ADI GECEN dosyalar haric tutulur (claimed set disaridan gelir)
TARGET_DIRS = ["incoming_20260916b", "incoming_20260916", "parallel_ideas_r1", "regen",
               "review_transfer", "residual8_pilot_r1", "hr-consolidation", "agent_out",
               "scratch", "verify_top10", "verify_ok", "theory_benchmark_test_v1",
               "pilots", "drive", "reports", "math_discovery_2026_09_13"]

QUESTIONS = {
    "feeds_published": Noul(instructions=(
        "Judging from this file's path, name and head content, does it plausibly PRODUCE or "
        "CONTAIN a result that could have fed the project's published numbers or conclusions? "
        "Answer no for scratch experiments, abandoned branches, environment setup, logs of "
        "failed runs, or self-contained side explorations."
    )),
    "makes_claims": Noul(instructions=(
        "Does this file assert findings or conclusions (as opposed to only holding raw data, "
        "configuration, or utility code)? Answer yes for reports, summaries, and analysis "
        "scripts that print verdicts."
    )),
    "could_contradict": Noul(instructions=(
        "Could this file plausibly contain a result that CONTRADICTS the project's published "
        "STOP conclusion or its headline comparisons - for example an arm that beat BM25, a "
        "measurement that was later dropped, or an experiment abandoned without disclosure?"
    )),
    "audit_value": Score(instructions=(
        "If an auditor spent one session on this file, how much would the project learn?"
    ), criteria=[
        "nothing; environment, cache, or duplicated content",
        "minor; confirms something already known",
        "useful; an unverified result or claim would get checked",
        "high; a load-bearing published number or a possible hidden contradiction",
    ]),
    "file_role": Choice(instructions=(
        "What role does this file play?"
    ), criteria={
        "producer_code": "Code that generates representations, scores or metrics",
        "analysis_code": "Code that analyses or aggregates existing results",
        "result_data": "Stored numeric results (per-query rows, summaries, caches)",
        "report": "A human-readable report, summary or set of findings",
        "config_or_meta": "Configuration, manifest, hashes, file listings",
        "log_or_scratch": "Run logs, scratch work, or abandoned material",
    }),
}


def collect(claimed_names, per_dir=45):
    items = []
    for d in TARGET_DIRS:
        root = W / d
        if not root.exists():
            continue
        picked = 0
        for f in sorted(root.rglob("*")):
            if picked >= per_dir:
                break
            if not f.is_file() or any(s in str(f) for s in SKIP):
                continue
            if f.suffix not in (".py", ".md", ".json", ".jsonl", ".csv"):
                continue
            if f.name in claimed_names:
                continue
            try:
                sz = f.stat().st_size
                if sz < 200 or sz > 4_000_000:
                    continue
                head = f.read_text(encoding="utf-8", errors="replace")[:1500]
            except Exception:
                continue
            items.append({
                "path": str(f.relative_to(W)).replace("\\", "/"),
                "dir": d, "name": f.name, "suffix": f.suffix,
                "size_bytes": sz, "head": head,
            })
            picked += 1
    return items


def decide(j):
    if j["could_contradict"] > 0.6 and j["audit_value"] >= 2.0:
        return "A1_POSSIBLE_HIDDEN_CONTRADICTION"
    if j["feeds_published"] > 0.6 and j["audit_value"] >= 2.0:
        return "A2_FEEDS_PUBLISHED_NUMBERS"
    if j["makes_claims"] > 0.6 and j["audit_value"] >= 2.0:
        return "A3_UNVERIFIED_CLAIMS"
    if j["audit_value"] >= 1.5:
        return "A4_WORTH_A_LOOK"
    return "A5_SKIP"


async def judge(client, it):
    state = {
        "project_context": PROJECT,
        "file_path": it["path"],
        "file_name": it["name"],
        "size_bytes": it["size_bytes"],
        "file_head": it["head"],
    }
    r = await client.system_one(model=MODEL, state=state, questions=QUESTIONS)
    return {
        "feeds_published": r.nouls["feeds_published"].noul,
        "makes_claims": r.nouls["makes_claims"].noul,
        "could_contradict": r.nouls["could_contradict"].noul,
        "audit_value": r.scores["audit_value"].score,
        "audit_value_conf": r.scores["audit_value"].confidence,
        "file_role": r.choices["file_role"].choice,
        "role_conf": r.choices["file_role"].confidence,
        "model_used": getattr(r, "model", None),
        "usage_in": getattr(r.usage, "input_tokens", None),
        "usage_out": getattr(r.usage, "output_tokens", None),
    }


async def main(limit=None):
    claimed = set(json.load(open(W / "audit_hard_r4/_claimed_names.json", encoding="utf-8")))
    items = collect(claimed)
    if limit:
        items = items[:limit]
    print(f"degerlendirilecek denetlenmemis dosya: {len(items)}")
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(6)
        async def one(it):
            async with sem:
                for a in range(3):
                    try:
                        j = await judge(client, it)
                        return {**{k: v for k, v in it.items() if k != "head"},
                                **j, "priority": decide(j)}
                    except Exception as e:
                        if a == 2:
                            return {**{k: v for k, v in it.items() if k != "head"},
                                    "error": str(e)[:180], "priority": "ERROR"}
                        await asyncio.sleep(2 * (a + 1))
        out = await asyncio.gather(*(one(i) for i in items))
    out.sort(key=lambda o: (-(o.get("audit_value") or 0), o.get("priority", "")))
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    ok = [o for o in out if o["priority"] != "ERROR"]
    print(f"islenen {len(ok)}/{len(out)} | token in="
          f"{sum(o.get('usage_in') or 0 for o in ok)} out={sum(o.get('usage_out') or 0 for o in ok)}")
    for k, v in collections.Counter(o["priority"] for o in out).most_common():
        print(f"  {k:36s} {v}")
    return out


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else None))
