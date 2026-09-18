"""Terim tutarliligi denetimi — TypeSafe System One (Jev).

Problem: denetimler ayni terimin proje icinde FARKLI anlamlarda kullanildigini buldu
(ornek: "plain BM25" icin 54.18 / 55.32 / 61.70 / 65.67 dolasimda).
Kod: ayni terimi iceren cumle ciftlerini ayni sayfadan/farkli dosyalardan toplar.
Model: iki cumlenin ayni seyi mi soyledigini, yoksa CELISTIGINI mi yargilar.
Karar: kodda.

Cikti: CONTRADICTIONS.json
"""
import json, re, sys, asyncio, itertools, collections
from pathlib import Path
MODEL = "jev-1.13.0"  # surum PINLI: alias degil (esikler bu surume gore)
from typesafe_sdk import AsyncTypeSafeClient, Noul, Choice, Score

W = Path("C:/Users/MDP/dev/llmzip-work")
PUB = W / "_wt_top10/research_top10_comparison_2026_09_16"
OUT = W / "audit_hard_r4/CONTRADICTIONS.json"

DOCS = ["FINAL_STATE.md", "REPORT.md", "DECISION_TESTS.md", "LADDER_REALTALK.md",
        "EXTERNAL_AUDIT3_RESPONSE.md", "PUBLICATION_VERIFY.md"]

# Denetimlerin coklu-tanimli oldugunu gosterdigi terimler + genel riskli terimler
TERMS = ["BM25", "Hit@10", "FR@3", "fair", "honest", "ladder", "sigma", "sym", "qscale",
         "12 B", "24 B", "48 B", "gate", "C1", "C3", "ITQ", "float", "byte"]

PROJECT = (
    "Research project: 12-48 byte document codes vs a BM25 lexical baseline, on RealTalk, "
    "PerLTQA, LoCoMo and LME. Metrics Hit@10 and FR@3. Audits found the SAME term used with "
    "different meanings across documents - for example several different BM25 configurations "
    "(coarse 54.18, textbook 55.32, frozen 61.70, best-of-four 65.67) all referred to as "
    "'BM25', and 'standardized' applied to an arm that does not standardize."
)

QUESTIONS = {
    "same_quantity": Noul(instructions=(
        "Statement A and statement B both use the shared term in `shared_term`. Are they "
        "talking about the SAME underlying quantity, configuration or object? Answer no if "
        "the term silently refers to different configurations, different datasets, different "
        "metrics, or different experimental conditions in the two statements."
    )),
    "numerically_incompatible": Noul(instructions=(
        "Do these two statements report values that cannot both be true of the same thing at "
        "the same time? Answer yes only for a genuine conflict. Answer no when the numbers "
        "differ because the statements describe different settings, different widths, "
        "different datasets, or different stages of the work."
    )),
    "reader_would_confuse": Noul(instructions=(
        "Would an external reader, reading both statements without access to the code, likely "
        "believe they refer to the same configuration and therefore draw a wrong conclusion?"
    )),
    "severity": Score(instructions=(
        "How much does this inconsistency threaten the report's credibility?"
    ), criteria=[
        "no issue; the two statements are consistent and clearly scoped",
        "harmless variation a careful reader resolves from context",
        "ambiguous; the shared term needs a disambiguating qualifier",
        "actively misleading; a reader would take away a false comparison",
    ]),
    "issue_kind": Choice(instructions=(
        "What best describes the relationship between these two statements?"
    ), criteria={
        "consistent": "They agree, or describe clearly different things with adequate scoping",
        "ambiguous_term": "The same word denotes different configurations without saying so",
        "stale_value": "One statement carries an older value that a later one supersedes",
        "direct_conflict": "They make incompatible assertions about the same thing",
        "unrelated": "They do not actually bear on each other",
    }),
}


def sentences(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if len(s) < 40 or s.startswith(("```", "#")):
            continue
        if s.startswith("|") and s.count("|") > 3:
            s = " ".join(c.strip() for c in s.strip("|").split("|"))
            if len(s) < 40:
                continue
        out.append((i, s[:400]))
    return out


def build_pairs(max_per_term=6):
    per_term = collections.defaultdict(list)
    for d in DOCS:
        p = PUB / d
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for ln, s in sentences(t):
            has_num = bool(re.search(r"\d+\.\d+|\b\d{3,}\b", s))
            if not has_num:
                continue
            for term in TERMS:
                if re.search(re.escape(term), s, re.I):
                    per_term[term].append({"doc": d, "line": ln, "text": s})
    pairs = []
    for term, items in per_term.items():
        # farkli dosyalardan gelen ciftlere oncelik (celiski orada saklanir)
        cross = [(a, b) for a, b in itertools.combinations(items, 2) if a["doc"] != b["doc"]]
        same = [(a, b) for a, b in itertools.combinations(items, 2) if a["doc"] == b["doc"]]
        for a, b in (cross + same)[:max_per_term]:
            pairs.append({"shared_term": term, "A": a, "B": b})
    return pairs


def decide(j):
    if j["numerically_incompatible"] > 0.6 and j["same_quantity"] > 0.5:
        return "C1_DIRECT_CONFLICT"
    if j["same_quantity"] < 0.4 and j["reader_would_confuse"] > 0.6 and j["severity"] >= 2.0:
        return "C2_AMBIGUOUS_TERM_MISLEADS"
    if j["severity"] >= 2.5:
        return "C3_NEEDS_QUALIFIER"
    if j["reader_would_confuse"] > 0.6:
        return "C4_MINOR_AMBIGUITY"
    return "C5_CONSISTENT"


async def judge(client, p):
    state = {
        "project_context": PROJECT,
        "shared_term": p["shared_term"],
        "statement_A": {"document": p["A"]["doc"], "line": p["A"]["line"], "text": p["A"]["text"]},
        "statement_B": {"document": p["B"]["doc"], "line": p["B"]["line"], "text": p["B"]["text"]},
    }
    r = await client.system_one(model=MODEL, state=state, questions=QUESTIONS)
    return {
        "same_quantity": r.nouls["same_quantity"].noul,
        "numerically_incompatible": r.nouls["numerically_incompatible"].noul,
        "reader_would_confuse": r.nouls["reader_would_confuse"].noul,
        "severity": r.scores["severity"].score,
        "severity_conf": r.scores["severity"].confidence,
        "issue_kind": r.choices["issue_kind"].choice,
        "kind_conf": r.choices["issue_kind"].confidence,
        "model_used": getattr(r, "model", None),
        "usage_in": getattr(r.usage, "input_tokens", None),
        "usage_out": getattr(r.usage, "output_tokens", None),
    }


async def main(limit=None):
    pairs = build_pairs()
    if limit:
        pairs = pairs[:limit]
    print(f"olusturulan cift: {len(pairs)}")
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(6)
        async def one(p):
            async with sem:
                for a in range(3):
                    try:
                        j = await judge(client, p)
                        return {**p, **j, "verdict": decide(j)}
                    except Exception as e:
                        if a == 2:
                            return {**p, "error": str(e)[:180], "verdict": "ERROR"}
                        await asyncio.sleep(2 * (a + 1))
        out = await asyncio.gather(*(one(p) for p in pairs))
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    ok = [o for o in out if o["verdict"] != "ERROR"]
    print(f"islenen {len(ok)}/{len(out)} | token in="
          f"{sum(o.get('usage_in') or 0 for o in ok)} out={sum(o.get('usage_out') or 0 for o in ok)}")
    for k, v in collections.Counter(o["verdict"] for o in out).most_common():
        print(f"  {k:30s} {v}")
    return out


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else None))
