"""Denetim bulgulari triyaji — TypeSafe System One (Jev).

Kod is akisini yonetir; model yalnizca semantik yargi verir.
Bulgu metni ZATEN ajanlarca uretilmis; model yeni sayi/iddia URETMEZ, siniflandirir.

Cikti: FINDINGS_TRIAGED.json (her bulgu icin ham yargilar + kod kararı)
"""
import json, os, sys, asyncio
from pathlib import Path
MODEL = "jev-1.13.0"  # surum PINLI: alias degil (esikler bu surume gore)
from typesafe_sdk import AsyncTypeSafeClient, Noul, Score, Choice

W = Path("C:/Users/MDP/dev/llmzip-work")
IN = W / "audit_hard_r4/FINDINGS_RAW.json"
OUT = W / "audit_hard_r4/FINDINGS_TRIAGED.json"

# Projeye ozgu baglam: modelin karari bunun isiginda vermesi gerekiyor.
PROJECT = (
    "Research project: compress a document embedding to 12-48 bytes and still retrieve "
    "the right document. Pipeline: per-archive TF-IDF + SVD -> sign codes. Rival: BM25. "
    "Verdict: STOP (fair BM25 61.70 beats best 48-byte code 57.87 on RealTalk Hit@10). "
    "IMPORTANT PROJECT RULE: fitting the projector on each archive's own documents is a "
    "DOCUMENTED PREREGISTERED DESIGN RULE, not a defect and not data leakage; queries and "
    "gold labels never enter the fit. A finding that merely restates this design rule as "
    "'leakage' is a mislabel, not a real defect."
)

QUESTIONS = {
    # 1) Gercekten yayinlanan bir sayiyi yanlislayan bir sey mi?
    "overturns_number": Noul(instructions=(
        "Does this audit finding show that a PUBLISHED NUMBER or a PUBLISHED CONCLUSION "
        "is actually wrong? Answer yes only if a specific reported value or conclusion "
        "must change. Answer no if the finding is about wording, labelling, missing "
        "documentation, an uncounted cost, a weak test, or an unverified claim."
    )),
    # 2) Sadece etiket/anlatim sorunu mu?
    "wording_only": Noul(instructions=(
        "Is this finding purely about how something is DESCRIBED (a wrong label, a stale "
        "sentence, an overstated claim, missing disclosure) while the underlying computed "
        "values remain correct?"
    )),
    # 3) Projenin tasarim kuralini kusur sanma hatasi mi?
    "misreads_design_rule": Noul(instructions=(
        "Does this finding treat the project's documented per-archive fitting rule (or the "
        "fact that an index is built from the corpus it searches) as if it were a defect, "
        "leakage, or cheating? Answer yes only when the finding's complaint IS that design "
        "choice itself."
    )),
    # 4) Duzeltme maliyeti
    "fix_effort": Score(instructions=(
        "How much work is needed to resolve this finding, assuming the team wants to act on it?"
    ), criteria=[
        "edit one sentence or one label in a document",
        "recompute or regenerate a table from data already stored",
        "write new code and run a new experiment",
        "re-run a large measurement campaign or redesign the protocol",
    ]),
    # 5) Yayina engel mi?
    "publication_blocker": Score(instructions=(
        "If this project were written up for external readers, how much does this finding "
        "block publication as-is?"
    ), criteria=[
        "no effect; internal detail only",
        "should be mentioned as a limitation",
        "a specific claim must be softened or scoped before publishing",
        "a claim must be withdrawn or a number corrected before publishing",
    ]),
    # 6) Kategori
    "category": Choice(instructions=(
        "What kind of problem does this finding describe?"
    ), criteria={
        "wrong_number": "A computed or reported value is incorrect",
        "mislabel": "A value is correct but named, labelled or described wrongly",
        "overclaim": "A claim is stated more broadly or more strongly than the evidence supports",
        "missing_evidence": "Something was never measured, never run, or cannot be verified",
        "cost_accounting": "A resource, storage or computation cost is uncounted or understated",
        "weak_test": "A test, gate or control exists but does not actually test what it claims",
        "no_defect": "No real problem; the finding confirms correct behaviour or misreads a design rule",
    }),
}


async def judge(client, f):
    state = {
        "project_context": PROJECT,
        "audit_round": f["round"],
        "auditor_role": f["role"],
        "finding_id": f["id"],
        "severity_claimed_by_auditor": f["claimed_sev"],
        "finding_text": f["text"],
    }
    r = await client.system_one(model=MODEL, state=state, questions=QUESTIONS)
    return {
        "overturns_number": r.nouls["overturns_number"].noul,
        "wording_only": r.nouls["wording_only"].noul,
        "misreads_design_rule": r.nouls["misreads_design_rule"].noul,
        "fix_effort": r.scores["fix_effort"].score,
        "fix_effort_conf": r.scores["fix_effort"].confidence,
        "publication_blocker": r.scores["publication_blocker"].score,
        "publication_blocker_conf": r.scores["publication_blocker"].confidence,
        "category": r.choices["category"].choice,
        "category_conf": r.choices["category"].confidence,
        "model_used": getattr(r, "model", None),
        "usage_in": r.usage.input_tokens if hasattr(r, "usage") else None,
        "usage_out": r.usage.output_tokens if hasattr(r, "usage") else None,
    }


def decide(j):
    """Karar KODDA. Model yalnizca sinyal uretti."""
    if j["misreads_design_rule"] > 0.65:
        return "REJECT_MISREADS_DESIGN"
    if j["overturns_number"] > 0.70 and j["publication_blocker"] >= 2.5:
        return "P1_MUST_FIX_BEFORE_PUBLISH"
    if j["publication_blocker"] >= 2.5:
        return "P2_SCOPE_OR_WITHDRAW_CLAIM"
    if j["wording_only"] > 0.70 and j["fix_effort"] <= 1.2:
        return "P3_CHEAP_TEXT_FIX"
    if j["publication_blocker"] >= 1.5:
        return "P4_DISCLOSE_AS_LIMITATION"
    return "P5_INTERNAL_ONLY"


async def main(limit=None):
    items = json.load(open(IN, encoding="utf-8"))
    if limit:
        items = items[:limit]
    out = []
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(6)
        async def one(f):
            async with sem:
                for attempt in range(3):
                    try:
                        j = await judge(client, f)
                        return {**f, **j, "decision": decide(j)}
                    except Exception as e:
                        if attempt == 2:
                            return {**f, "error": str(e)[:200], "decision": "ERROR"}
                        await asyncio.sleep(2 * (attempt + 1))
        out = await asyncio.gather(*(one(f) for f in items))
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    ok = [o for o in out if o.get("decision") != "ERROR"]
    tin = sum(o.get("usage_in") or 0 for o in ok)
    tout = sum(o.get("usage_out") or 0 for o in ok)
    print(f"islenen {len(ok)}/{len(out)} | token in={tin} out={tout}")
    import collections
    print(collections.Counter(o["decision"] for o in out))
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(main(n))
