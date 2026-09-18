"""Provenance gate — bir metnin VAR OLMAYAN proje bulgusuna dayanip dayanmadigini bulur.

Bugun iki kez ayni hataya dusuldu: "spectral grouping" ve "B1 = encoder-state reduction".
Ikisi de akici, ikna edici yazilmisti; ikisinin de depoda karsiligi yoktu.

IS BOLUMU (llmzip-research skill kurali):
  KOD   : adaylari cikarir, `git grep` ile depoda ARAR  -> VARLIK KANITI SADECE BURADAN
  MODEL : cumle bir PROJE BULGUSU mu iddia ediyor, yoksa literatur/hipotez mi -> SADECE YARGI
  KOD   : karari verir (iddia ediyor + 0 isabet = PROVENANCE_FAIL)

Model hicbir varligi dogrulamaz. Model hicbir sayi uretmez.

Cikti: PROVENANCE_REPORT.json
"""
import json, re, subprocess, sys, asyncio
from pathlib import Path

MODEL = "jev-1.13.0"          # surum PINLI
from typesafe_sdk import AsyncTypeSafeClient, Noul, Choice

W    = Path("C:/Users/MDP/dev/llmzip-work")
REPO = W / "_wt_main"
OUT  = W / "audit_hard_r4/PROVENANCE_REPORT.json"

# ---------------------------------------------------------------- 1. ADAY CIKARMA (kod)
# Teknik ad adaylari: cok kelimeli kucuk harf terimler + tanimlayicilar + birimli sayilar
PATTERNS = [
    r"\b(?:[a-z]+[- ]){1,2}(?:grouping|hashing|encoder|predictor|certificate|reduction|ladder|diagnostic)\b",
    r"\b[A-Z]{1,3}\d{1,2}(?:-[a-z]+)?\b",                    # B1, C3, 4F1, RT03
    r"\b\d+[.,]\d+\s*(?:GB|MB|pp|B/doc|ms)\b",               # 10.13 GB, 19.86 pp
    r"\b(?:NanoBEIR|BRIGHT|BIRCO|DynamicCache|LongBench|RaBitQ|QuIVer|IsoHash|SnapKV)\b",
]
STOP = {  # gercek oldugu zaten bilinen / anlamsiz adaylar
    "B2","B3","V2","V3","V4","V5","V6","R1","R2","R3","R4","A1","A2","A3","A4","A5",
    "C1","C2","C3","C4","S1","S2","S3","T1","T2","T3","D1","F1","F2","F5","L1","G1","H1",
    "E1","E2","E3","E4","B0","K10","N10",
}

def candidates(text: str):
    found = {}
    for pat in PATTERNS:
        for m in re.finditer(pat, text, re.I):
            t = m.group(0).strip()
            if t.upper() in STOP or len(t) < 3:
                continue
            found.setdefault(t.lower(), t)
    return list(found.values())

# ---------------------------------------------------------------- 2. DEPODA ARAMA (kod)
# META dosyalar: bu belgeler bir terimin YOKLUGUNU belgeliyor. Onlari kanit saymak
# aracin kendi kendini kirletmesidir -- kalibrasyonda tam bu yasandi: "spectral grouping"
# 2 isabet verdi, ikisi de o deneyin YOK oldugunu yazan dosyalardi.
META = ("OPEN_QUESTIONS", "CONTINUITY_LEDGER", "TWELVE_BYTE_PILOT_README",
        "CORRECTION_LEDGER", "PROVENANCE_REPORT", "provenance_gate")

# PROSE kaynaklar: sohbet dokumu, dis inceleme yapistirmasi, el yazisi degerlendirme.
# Bunlar depoda DURUYOR ama OLCUM DEGIL -- baska bir LLM'in veya insanin cumleleridir.
# Bir sayinin yalnizca burada bulunmasi, o sayinin projede olculdugu anlamina GELMEZ.
# Kalibrasyonda tam bu yasandi: "10.13 GB" depoda bulundu, kaynagi bir ChatGPT dokumuydu.
PROSE = ("CHAT_TRANSCRIPT", "incoming_", "pasted_content", "EXTERNAL_REVIEW",
         "chat_literature_review", "HANDOFF")

def _is_meta(path_line: str) -> bool:
    return any(m in path_line for m in META)

def _is_prose(path_line: str) -> bool:
    return any(m in path_line for m in PROSE)

def variants(term: str):
    """Sayisal terimler icin bicim varyantlari uret.

    KUSUR KAYDI 2026-09-18: ilk surum duz dizgi araması yapiyordu ve '19.86 pp'
    sorgusu, ham kanittaki '+19.86pp' (bosluksuz) ifadesini KACIRDI -> yanlis
    PROVENANCE_FAIL. Sayi bicimleri arasinda fark var: '19.86 pp' / '19.86pp' /
    '19,86 pp' / '+19.86'. Sayisal terimde ciplak sayiyi ve her iki ondalik
    ayiricisini ayri ayri aramak ZORUNLU.
    """
    out = {term}
    m = re.match(r"^([+-]?\d+)[.,](\d+)\s*(.*)$", term.strip())
    if m:
        a, b, unit = m.group(1).lstrip("+-"), m.group(2), m.group(3)
        for sep in (".", ","):
            if unit:
                # BIRIM ZORUNLU. Ciplak sayi ("10.13") arastirilmaz: kalibrasyonda
                # rastgele CSV hucrelerine carpip 162 sahte isabet uretti. Yalniz
                # boslukla/bosluksuz birimli bicimler sayilir.
                out.add(f"{a}{sep}{b} {unit}")
                out.add(f"{a}{sep}{b}{unit}")
            else:
                out.add(f"{a}{sep}{b}")
    return sorted(out, key=len, reverse=True)

_cache = {}
def repo_hits(term: str) -> dict:
    """main'de ara; 0 ise TUM uzak dallara genislet. Varlik kaniti yalnizca budur.

    META dosyalar haric tutulur: bir terimin yoklugunu kaydeden belge, o terimin
    varligina kanit degildir.
    """
    if term in _cache:
        return _cache[term]
    def run(args):
        try:
            r = subprocess.run(args, cwd=REPO, capture_output=True, text=True, timeout=180)
            return [l for l in r.stdout.splitlines() if l.strip()]
        except Exception:
            return []
    args = []
    for v in variants(term):
        args += ["-e", v]
    main_all = run(["git", "grep", "-lI"] + args)
    kept  = [f for f in main_all if not _is_meta(f)]
    prose = [f for f in kept if _is_prose(f)]
    main  = [f for f in kept if not _is_prose(f)]
    res = {"main_files": len(main), "prose_files": len(prose),
           "sample": (main or prose)[:3], "branch_hits": None,
           "meta_only": len(main_all) > 0 and not kept,
           "prose_only": bool(prose) and not main}
    if not main:
        brs = run(["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"])[:45]
        if brs:
            bb = [f for f in run(["git", "grep", "-lI"] + args + brs) if not _is_meta(f)]
            b  = [f for f in bb if not _is_prose(f)]
            res["branch_hits"]  = len(b)
            res["prose_files"] += len(bb) - len(b)
            res["prose_only"]   = bool(res["prose_files"]) and not b
            res["sample"] = (b or bb)[:3]
    _cache[term] = res
    return res

# ---------------------------------------------------------------- 3. MODEL (sadece yargi)
PROJECT = (
    "A research repository. Some sentences report THIS PROJECT's own measured experiments; "
    "others describe OTHER PEOPLE's published work found in a literature scan; others propose "
    "a hypothesis to test in future. These are different epistemic statuses and must not be mixed."
)

QUESTIONS = {
    "asserts_project_finding": Noul(instructions=(
        "Does this sentence assert that THIS PROJECT measured, observed, built or found the thing "
        "named by `term`? Answer yes only if the sentence treats it as an existing result or "
        "artifact of this project's own work. Answer no if the sentence attributes it to outside "
        "literature, proposes it as a future experiment, asks whether it could be done, or "
        "explicitly labels it as absent, retracted or non-existent."
    )),
    "kind": Choice(
        instructions="What epistemic status does the sentence give to `term`?",
        criteria={
            "project_result": "This project's own measured result, experiment or artifact",
            "literature": "Other people's published work, cited from a literature scan",
            "hypothesis": "A hypothesis, proposal or future experiment, not yet done",
            "marked_absent": "Explicitly marked as absent, retracted, withdrawn or non-existent",
        },
    ),
}

async def judge(client, items):
    sem = asyncio.Semaphore(8)
    done = [0]
    async def one(it):
        async with sem:
            state = {
                "project_context": PROJECT,
                "term": it["term"],
                "sentence": it["sentence"],
                "surrounding_text": it["context"],
                "source_document": it["source"],
            }
            try:
                r = await client.system_one(model=MODEL, state=state, questions=QUESTIONS)
                it["asserts"]    = r.nouls["asserts_project_finding"].noul
                it["kind"]       = r.choices["kind"].choice
                it["kind_conf"]  = r.choices["kind"].confidence
                it["model_used"] = getattr(r, "model", None) or MODEL
            except Exception as e:
                it["error"] = str(e)[:150]
            done[0] += 1
            if done[0] % 25 == 0:
                print(f"  islenen {done[0]}/{len(items)}", flush=True)
        return it
    return await asyncio.gather(*(one(i) for i in items))

# ---------------------------------------------------------------- 4. KARAR (kod)
def verdict(it) -> str:
    if "error" in it:
        return "ERROR"
    hits = it["main_files"] + (it["branch_hits"] or 0)
    asserts = it["asserts"] >= 0.60
    if it["kind"] == "marked_absent":
        return "OK_MARKED_ABSENT"
    if hits == 0 and it.get("prose_only") and asserts:
        return "PROVENANCE_PROSE_ONLY"     # yalniz sohbet/inceleme duzyazisinda -- olcum degil
    if hits == 0 and asserts:
        return "PROVENANCE_FAIL"           # iddia ediyor ama depoda hic yok
    if hits == 0:
        return "OK_NOT_CLAIMED"            # depoda yok ama zaten iddia edilmiyor
    if hits and it["kind"] == "literature":
        return "OK_LITERATURE"
    return "OK_GROUNDED"

def sentences(text):
    for para in text.split("\n\n"):
        for s in re.split(r"(?<=[.!?])\s+|\n(?=[-*|#])", para):
            s = s.strip()
            if 25 < len(s) < 900:
                yield s

async def main():
    srcs = []
    for p, label in [
        (Path("C:/Users/MDP/AppData/Roaming/Hermes/composer-pastes/pasted_content_2026-09-18_11-42-37-914_0e61e2.txt"), "DIS_LISTE_47"),
        (W / "OPEN_QUESTIONS_2026-09-18.md", "BIZIM_LISTE"),
        (REPO / "TWELVE_BYTE_PILOT_README.md", "PILOT_README"),
    ]:
        if p.exists():
            srcs.append((label, p.read_text(encoding="utf-8", errors="replace")))
    print("kaynak:", [s[0] for s in srcs], flush=True)

    items, seen = [], set()
    for label, text in srcs:
        sents = list(sentences(text))
        for i, s in enumerate(sents):
            for term in candidates(s):
                key = (label, term.lower())
                if key in seen:
                    continue
                seen.add(key)
                h = repo_hits(term)
                items.append({"source": label, "term": term, "sentence": s,
                              "context": " ".join(sents[max(0,i-1):i+2])[:900], **h})
    print(f"aday iddia: {len(items)} | benzersiz terim: {len(_cache)}", flush=True)
    if not items:
        return

    async with AsyncTypeSafeClient() as client:
        items = await judge(client, items)

    for it in items:
        it["verdict"] = verdict(it)
    OUT.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")

    from collections import Counter
    c = Counter(i["verdict"] for i in items)
    print("\n--- SONUC ---")
    for k, v in c.most_common():
        print(f"  {k:24s} {v}")
    print(f"\nmodel: {set(i.get('model_used', '?') for i in items)}")
    fails = [i for i in items if i["verdict"] == "PROVENANCE_FAIL"]
    if fails:
        print(f"\n--- PROVENANCE_FAIL ({len(fails)}) ---")
        for f in sorted(fails, key=lambda x: -x["asserts"])[:20]:
            print(f"\n[{f['source']}] term={f['term']!r} asserts={f['asserts']:.2f} hits=0")
            print(f"  {f['sentence'][:200]}")

if __name__ == "__main__":
    asyncio.run(main())
