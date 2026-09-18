"""Yayin iddialarinin denetimi — TypeSafe System One (Jev).

Kod: iddiayi cikarir, sayilari ham veri dosyalarinda izler, kanit parcasini toplar.
Model: SADECE semantik yargi verir (asiri genelleme, kapsam, geri cekilmis iddia tekrari,
       kanitin iddiayi destekleyip desteklemedigi).
Karar: KODDA.

Cikti: CLAIMS_AUDITED.json
"""
import json, re, sys, asyncio
from pathlib import Path
MODEL = "jev-1.13.0"  # surum PINLI: alias degil (esikler bu surume gore)
from typesafe_sdk import AsyncTypeSafeClient, Noul, Score, Choice

W = Path("C:/Users/MDP/dev/llmzip-work")
IN = W / "audit_hard_r4/CLAIMS_WITH_EVIDENCE.json"
OUT = W / "audit_hard_r4/CLAIMS_AUDITED.json"

PROJECT = (
    "Research project: compress a document embedding to 12-48 bytes and still retrieve the "
    "right document. Per-archive TF-IDF + SVD -> sign codes. Rival: BM25. "
    "Verdict: STOP (a fairly built BM25 beats the best 48-byte code on RealTalk). "
    "DESIGN RULE (not a defect): the projector is fitted on each archive's own documents; "
    "queries and gold labels never enter the fit. This is preregistered and documented."
)

# Koordinatorun ELLE dogruladigi geri cekmeler. Bir iddia bunlardan birini
# duzeltme uyarisi olmadan tekrarliyorsa kirmizi bayrak.
RETRACTIONS = [
    "The decision gates were NOT proven to be fixed before the results existed: the gate "
    "definitions and the results were committed together. Calling the stopping rule "
    "'prespecified' or 'pre-registered' is withdrawn.",
    "The headline gap of -7.80 pp was measured against the strongest of four BM25 variants "
    "selected on the evaluation data. Against the referee's primary textbook BM25 the gap "
    "is -3.83 pp Hit@10 / -3.26 pp FR@3.",
    "The claim that the sigma-division explains the high-k decline is incomplete: the 'sym' "
    "arm never divides by sigma yet declines too.",
    "'With reranking the first stage does not matter' is an overgeneralization; first-stage "
    "candidate recall still bounds the result.",
    "The claim that sign coding adds about +10 pp over the float source is reference-dependent: "
    "it holds against raw float, but not against standardized float.",
    "The per-archive fitting of the projector is a documented design rule, NOT data leakage. "
    "Describing published scores as 'inflated by leakage' is withdrawn.",
    "'All 30 clusters' for the PerLTQA representation contrasts (IDF_p2, SHIFT_m1) is false: "
    "those ran on 10 of 30 archives (2967 of 8265 queries).",
    "'100% gold resolution' for RealTalk is false: 23 questions have zero resolvable gold and "
    "46 are partial; 705 of 728 were evaluated.",
    "The lexical 'expected_hit_at_10' column actually contains expected Recall@10, not Hit@10.",
]

QUESTIONS = {
    "evidence_supports": Noul(instructions=(
        "Look at `claim` and at `evidence_snippets`, which are raw excerpts from the "
        "project's own stored result files, retrieved by matching the numbers that appear "
        "in the claim. Do these excerpts actually support the claim's numbers as the claim "
        "uses them? Answer no if the excerpts are about a different quantity, a different "
        "dataset, or a different setting than the claim describes, or if they are unrelated "
        "text that merely contains the same digits."
    )),
    "overgeneralized": Noul(instructions=(
        "Does this claim state a general rule (using words like all, every, never, always, "
        "no arm, or an unqualified present tense) when the evidence it references comes from "
        "one dataset, one setting, or one width? Answer no when the claim already names its "
        "scope, or when it is explicitly about a single measurement."
    )),
    "repeats_retraction": Noul(instructions=(
        "Compare `claim` against `withdrawn_statements`, a list of statements this project "
        "has already withdrawn or corrected. Does the claim restate any of them as if still "
        "true, without a correction marker, retraction note, or hedge? Answer no if the claim "
        "states the corrected version, if it explicitly marks the correction, or if it is "
        "about a different matter."
    )),
    "names_its_evidence": Noul(instructions=(
        "Does the claim itself point a reader to where its number came from - naming a file, "
        "a script, a benchmark, a sample size, or a specific experiment? Answer no for a bare "
        "assertion that a reader could not trace."
    )),
    "hedging": Score(instructions=(
        "How carefully does this claim limit itself to what a single exploratory measurement "
        "can support?"
    ), criteria=[
        "stated as an established general fact with no qualification",
        "stated plainly, scope inferable only from surrounding text",
        "names its dataset or setting inside the claim",
        "names its scope and also its uncertainty, sample size, or known limitation",
    ]),
    "risk_if_wrong": Score(instructions=(
        "If this particular claim turned out to be wrong, how much damage would it do to the "
        "project's credibility with an external reviewer?"
    ), criteria=[
        "trivial; a passing remark or bookkeeping detail",
        "a supporting detail would need correcting",
        "a stated finding would have to be withdrawn",
        "the project's main conclusion would be undermined",
    ]),
    "claim_kind": Choice(instructions=(
        "What kind of statement is this?"
    ), criteria={
        "measurement": "Reports a measured value from an experiment",
        "comparison": "Asserts one method beats, matches or loses to another",
        "mechanism": "Explains WHY something happens",
        "methodology": "Describes how the work was done, or a procedural guarantee",
        "limitation": "States a known weakness, gap or caveat",
        "bookkeeping": "Administrative: file names, commit ids, counts of files, dates",
    }),
}


def decide(j):
    """Karar kodda; model yalniz sinyal verdi."""
    if j["repeats_retraction"] > 0.65:
        return "R1_REPEATS_WITHDRAWN_CLAIM"
    if j["evidence_supports"] < 0.35 and j["risk_if_wrong"] >= 2.0:
        return "R2_EVIDENCE_MISMATCH_HIGH_RISK"
    if j["overgeneralized"] > 0.65 and j["risk_if_wrong"] >= 2.0:
        return "R3_OVERGENERALIZED_HIGH_RISK"
    if j["overgeneralized"] > 0.65:
        return "R4_OVERGENERALIZED"
    if j["risk_if_wrong"] >= 2.0 and j["names_its_evidence"] < 0.4:
        return "R5_HIGH_RISK_UNTRACEABLE"
    if j["hedging"] < 1.0 and j["risk_if_wrong"] >= 1.5:
        return "R6_NEEDS_HEDGE"
    return "R7_OK"


async def judge(client, c):
    state = {
        "project_context": PROJECT,
        "source_document": c["doc"],
        "line_number": c["line"],
        "claim": c["claim"],
        "surrounding_text": c.get("context", "")[:900],
        "evidence_snippets": c.get("evidence_snippets", []),
        "withdrawn_statements": RETRACTIONS,
    }
    r = await client.system_one(model=MODEL, state=state, questions=QUESTIONS)
    return {
        "evidence_supports": r.nouls["evidence_supports"].noul,
        "overgeneralized": r.nouls["overgeneralized"].noul,
        "repeats_retraction": r.nouls["repeats_retraction"].noul,
        "names_its_evidence": r.nouls["names_its_evidence"].noul,
        "hedging": r.scores["hedging"].score,
        "hedging_conf": r.scores["hedging"].confidence,
        "risk_if_wrong": r.scores["risk_if_wrong"].score,
        "risk_conf": r.scores["risk_if_wrong"].confidence,
        "claim_kind": r.choices["claim_kind"].choice,
        "kind_conf": r.choices["claim_kind"].confidence,
        "model_used": getattr(r, "model", None),
        "usage_in": getattr(r.usage, "input_tokens", None),
        "usage_out": getattr(r.usage, "output_tokens", None),
    }


async def main(limit=None):
    items = json.load(open(IN, encoding="utf-8"))
    if limit:
        items = items[:limit]
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(6)
        async def one(c):
            async with sem:
                for a in range(3):
                    try:
                        j = await judge(client, c)
                        return {**c, **j, "verdict": decide(j)}
                    except Exception as e:
                        if a == 2:
                            return {**c, "error": str(e)[:180], "verdict": "ERROR"}
                        await asyncio.sleep(2 * (a + 1))
        out = await asyncio.gather(*(one(c) for c in items))
    for o in out:
        o.pop("context", None)
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    ok = [o for o in out if o["verdict"] != "ERROR"]
    print(f"islenen {len(ok)}/{len(out)} | token in="
          f"{sum(o.get('usage_in') or 0 for o in ok)} out={sum(o.get('usage_out') or 0 for o in ok)}")
    import collections
    for k, v in collections.Counter(o["verdict"] for o in out).most_common():
        print(f"  {k:34s} {v}")
    return out


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else None))
