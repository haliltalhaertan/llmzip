"""98 yuksek riskli denetlenmemis dosyanin ICERIGINI okur — TypeSafe Jev (surum PINLI).

Onceki hat (prioritize_unaudited.py) yalniz dosyanin ILK 1500 karakterine bakti ve
"gizli celiski olabilir" dedi. Bu hat dosyayi GERCEKTEN acar ve tek soruyu sorar:
bu dosya, yayinlanan STOP sonucuyla celisen bir sonuc mu tasiyor?

Kod: dosyayi okur, buyukse bas+orta+son pencereleri alir, yayin capalarini state'e koyar.
Model: celiski/terk edilmis sonuc yargisi.
Karar: kodda.

Cikti: HIDDEN_CONTRADICTIONS.json
"""
import json, sys, asyncio, collections
from pathlib import Path

MODEL = "jev-1.13.0"  # surum PINLI: alias degil
from typesafe_sdk import AsyncTypeSafeClient, Noul, Score, Choice

W = Path("C:/Users/MDP/dev/llmzip-work")
IN = W / "audit_hard_r4/UNAUDITED_PRIORITY.json"
OUT = W / "audit_hard_r4/HIDDEN_CONTRADICTIONS.json"

# Yayinlanan sonucun capalari. Bir dosya bunlarla celisiyorsa bulmak istedigimiz sey odur.
PUBLISHED = {
    "verdict": "STOP: a fairly built BM25 beats the best 48-byte code, so this optimisation "
               "line was frozen.",
    "realtalk_hit10": {
        "BM25_coarse": 54.18, "BM25_textbook": 55.32, "BM25_frozen": 61.70,
        "BM25_best_of_four": 65.67,
        "code_12B_qscale": 49.65, "code_24B_qscale": 55.32, "code_48B_qscale": 57.87,
        "float_std_uncompressed": 48.51, "sign96_deterministic": 46.52, "PQ_12B": 33.05,
    },
    "gates": "C1 FAIL (no arm <=48 B beats a fair BM25 by >=2 pp FR@3 on both benchmarks); "
             "C3 FAIL (code+rerank does not beat BM25 alone by >=1 pp on undisputed gold).",
    "design_rule": "Per-archive fitting of the projector is a PREREGISTERED DESIGN RULE, not a "
                   "defect and not leakage. Queries and gold never enter the fit.",
    "known_retractions": [
        "'prespecified gates' is withdrawn (gates co-committed with results)",
        "'sign adds ~10 pp over float' holds only vs RAW float, not standardized float",
        "'all 30 clusters' for IDF_p2 / SHIFT_m1 was 10/30 archives",
        "'100% gold resolution' for RealTalk is 705/728",
        "the sigma-division explanation of the high-k decline is incomplete",
    ],
}

PROJECT = (
    "Research project: compress a document embedding to 12-48 bytes and still retrieve the right "
    "document (per-archive TF-IDF + SVD -> sign codes), against a BM25 lexical baseline on "
    "RealTalk, PerLTQA, LoCoMo and LME. Four audit rounds examined the decision pipeline. "
    "THIS FILE WAS NEVER OPENED BY ANY AUDITOR. The question now is whether the project's own "
    "archive contains a result that was quietly dropped."
)

QUESTIONS = {
    "contradicts_published": Noul(instructions=(
        "Does this file contain a measured result that CONTRADICTS the published conclusion in "
        "`published_anchors` - for example a compact-code arm beating a fairly built BM25, a "
        "gate passing that the publication reports as failing, or a number materially different "
        "from the published value for the same quantity and dataset? Answer no if the file "
        "agrees with the published picture, reports something unrelated, or contains no "
        "comparable measurement at all."
    )),
    "abandoned_result": Noul(instructions=(
        "Does this file record an experiment or a finding that appears to have been STOPPED, "
        "SUPERSEDED or left unfinished without its outcome being carried into the project's "
        "published documents? Look for partial runs, killed jobs, 'TODO', open defects with no "
        "recorded disposition, or verdicts that no later document repeats."
    )),
    "records_defects": Noul(instructions=(
        "Is this file a record of DEFECTS, review findings, or corrections against the project's "
        "own work - a defect table, an audit verdict, a coordinator review, an errata list?"
    )),
    "still_open": Score(instructions=(
        "If this file raises problems, how resolved do they look from the file's own content?"
    ), criteria=[
        "no problems raised, or every item explicitly closed with evidence",
        "problems raised and mostly dispositioned, a few loose ends",
        "problems raised with no visible disposition",
        "problems raised, explicitly unresolved, and load-bearing for a published claim",
    ]),
    "action": Choice(instructions=(
        "What should a coordinator do with this file next?"
    ), criteria={
        "read_now": "Contains a possible contradiction or an unresolved load-bearing defect",
        "reconcile": "Records defects or verdicts that should be checked against the current record",
        "note_as_abandoned": "An unfinished or superseded line; record that it exists and move on",
        "no_action": "Consistent with the published picture, or carries no comparable result",
    }),
}


def windows(text, n=3, w=2600):
    """Bas + orta + son pencereler: buyuk dosyada sonuc genelde sonda."""
    if len(text) <= w * n:
        return text
    mid = len(text) // 2
    return (text[:w] + "\n...[middle omitted]...\n" + text[mid:mid + w]
            + "\n...[omitted]...\n" + text[-w:])


def decide(j):
    if j["contradicts_published"] > 0.6:
        return "H1_CONTRADICTION_CANDIDATE"
    if j["records_defects"] > 0.6 and j["still_open"] >= 2.0:
        return "H2_OPEN_DEFECT_RECORD"
    if j["abandoned_result"] > 0.6 and j["still_open"] >= 1.5:
        return "H3_ABANDONED_UNRECORDED"
    if j["records_defects"] > 0.6:
        return "H4_DEFECT_RECORD_CLOSED"
    return "H5_NO_ACTION"


async def judge(client, it, body):
    state = {
        "project_context": PROJECT,
        "published_anchors": PUBLISHED,
        "file_path": it["path"],
        "file_size_bytes": it["size_bytes"],
        "file_content": body,
    }
    r = await client.system_one(state=state, questions=QUESTIONS, model=MODEL)
    return {
        "contradicts_published": r.nouls["contradicts_published"].noul,
        "abandoned_result": r.nouls["abandoned_result"].noul,
        "records_defects": r.nouls["records_defects"].noul,
        "still_open": r.scores["still_open"].score,
        "still_open_conf": r.scores["still_open"].confidence,
        "action": r.choices["action"].choice,
        "action_conf": r.choices["action"].confidence,
        "model_used": getattr(r, "model", None),
        "usage_in": getattr(r.usage, "input_tokens", None),
        "usage_out": getattr(r.usage, "output_tokens", None),
    }


async def main(limit=None):
    items = [o for o in json.load(open(IN, encoding="utf-8"))
             if o.get("priority") in ("A1_POSSIBLE_HIDDEN_CONTRADICTION",
                                      "A2_FEEDS_PUBLISHED_NUMBERS",
                                      "A3_UNVERIFIED_CLAIMS")]
    if limit:
        items = items[:limit]
    print(f"acilacak dosya: {len(items)}")
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(5)
        async def one(it):
            p = W / it["path"]
            try:
                body = windows(p.read_text(encoding="utf-8", errors="replace"))
            except Exception as e:
                return {**it, "error": f"read: {e}", "verdict": "READ_ERROR"}
            async with sem:
                for a in range(3):
                    try:
                        j = await judge(client, it, body)
                        return {**it, **j, "verdict": decide(j)}
                    except Exception as e:
                        if a == 2:
                            return {**it, "error": str(e)[:180], "verdict": "ERROR"}
                        await asyncio.sleep(2 * (a + 1))
        out = await asyncio.gather(*(one(i) for i in items))
    out.sort(key=lambda o: -(o.get("contradicts_published") or 0))
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    ok = [o for o in out if o["verdict"] not in ("ERROR", "READ_ERROR")]
    models = {o.get("model_used") for o in ok}
    print(f"islenen {len(ok)}/{len(out)} | model={models} | token in="
          f"{sum(o.get('usage_in') or 0 for o in ok)} out={sum(o.get('usage_out') or 0 for o in ok)}")
    for k, v in collections.Counter(o["verdict"] for o in out).most_common():
        print(f"  {k:32s} {v}")
    return out


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else None))
