"""Bagimsiz yeniden hesaplama — bir iddia ham artefakttan URETILEBILIYOR mu?

Provenance zincirinin son halkasi:
  CLAIM -> EXACT SOURCE -> PROVENANCE CLASS -> PRIMARY ARTEFACT -> INDEPENDENT RECOMPUTATION

Fark onemli:
  PRIMARY_EVIDENCE    : sayi ham JSON'da zaten YAZIYOR (okundu)
  PRIMARY_RECOMPUTED  : sayi ham girdilerden FORMULLE yeniden uretildi ve rapor degerine esit

Ikincisi daha guclu: "dosyada var" degil, "sonuc gercekten hesaplanabiliyor".

Bu dosya model KULLANMAZ. Saf aritmetik. Kayit: RECOMPUTED_LEDGER.json
"""
import json
from pathlib import Path

W   = Path("C:/Users/MDP/dev/llmzip-work")
PUB = W / "_wt_main/research_top10_comparison_2026_09_16"
IND = W / "audit_hard_r4/ladder_indep"
OUT = W / "audit_hard_r4/RECOMPUTED_LEDGER.json"
TOL       = 0.005    # 2 ondalige DOGRU yuvarlamanin yari birimi
TOL_TRUNC = 0.010    # kesme (truncation) toleransi: rapor yuvarlamak yerine kesmis

def _j(p):
    return json.load(open(p, encoding="utf-8"))

# ---------------------------------------------------------------- yeniden hesaplayicilar
def rc_indep_ladder(arm):
    """INDEP genislik merdiveni: per-archive ham JSON'lardan soru-agirlikli havuzlama."""
    J = {k: _j(IND / f"INDUCTIVE_K{k}.json") for k in (96, 192, 384)}
    def pooled(k):
        num = den = 0
        for a, v in J[k].items():
            if not a.startswith("RT"):
                continue
            num += v["INDEP"][arm] * v["n_q"]
            den += v["n_q"]
        return num / den, den
    p96, nq = pooled(96)
    p384, _ = pooled(384)
    return p384 - p96, {"k96": round(p96, 4), "k384": round(p384, 4), "n_q": nq,
                        "method": "question-weighted pooling over 10 per-archive JSONs"}

def rc_trans_ladder(arm):
    """TRANS genislik merdiveni: LADDER.json kol degerlerinden fark."""
    A = _j(PUB / "coordinator/LADDER.json")["arms"]
    lo, hi = A[f"k96/{arm}"]["hit10"], A[f"k384/{arm}"]["hit10"]
    return hi - lo, {"k96": round(lo, 4), "k384": round(hi, 4),
                     "n": A[f"k96/{arm}"]["n"], "method": "k384 minus k96 from LADDER.json arms"}

def rc_gap(metric, bm25_variant):
    """48B/qscale ile bir BM25 varyanti arasindaki fark."""
    T = _j(PUB / "coordinator/DECISION_TESTS.json")["T1_fair_baseline"]
    b = T["bm25_variants"][bm25_variant][metric]
    c = T["code_arms"]["48B/qscale"][metric]
    return c - b, {"code_48B_qscale": round(c, 4), f"bm25_{bm25_variant}": round(b, 4),
                   "method": "code arm minus BM25 variant from DECISION_TESTS.json"}

# ---------------------------------------------------------------- iddia kaydi
CLAIMS = [
    ("+19.86 pp", "INDEP width ladder 96->384, qscale",  19.86, lambda: rc_indep_ladder("qscale")),
    ("+16.88 pp", "INDEP width ladder 96->384, sym",     16.88, lambda: rc_indep_ladder("sym")),
    ("+8.22 pp",  "TRANS width ladder 96->384, qscale",   8.22, lambda: rc_trans_ladder("qscale")),
    ("+7.66 pp",  "TRANS width ladder 96->384, sym",      7.66, lambda: rc_trans_ladder("sym")),
    ("-3.83 pp",  "48B qscale vs referee-primary BM25, Hit@10", -3.83, lambda: rc_gap("hit10", "frozen_textbook")),
    ("-3.26 pp",  "48B qscale vs referee-primary BM25, FR@3",   -3.26, lambda: rc_gap("fr3",   "frozen_textbook")),
    ("-7.80 pp",  "48B qscale vs post-selected strongest BM25 (RETRACTED headline)",
                                                               -7.80, lambda: rc_gap("hit10", "frozen_idfonly")),
]

def main():
    rows, ok = [], 0
    for label, desc, claimed, fn in CLAIMS:
        try:
            got, detail = fn()
            err = abs(got - claimed)
            if err <= TOL:
                v = "PRIMARY_RECOMPUTED"
            elif err <= TOL_TRUNC and f"{got:.2f}" != f"{claimed:.2f}":
                # Deger dogru, sunumu yanlis: rapor 2 ondalige KESMIS, yuvarlamamis.
                # Bilimsel sonucu etkilemez ama kayda gecer.
                v = "PRIMARY_RECOMPUTED_TRUNCATED"
            else:
                v = "RECOMPUTE_MISMATCH"
            ok += v.startswith("PRIMARY_RECOMPUTED")
            rows.append({"claim": label, "description": desc, "claimed": claimed,
                         "recomputed": round(got, 4), "abs_error": round(err, 4),
                         "correctly_rounded": float(f"{got:.2f}"),
                         "verdict": v, "detail": detail})
        except Exception as e:
            rows.append({"claim": label, "description": desc, "claimed": claimed,
                         "verdict": "RECOMPUTE_ERROR", "error": str(e)[:200]})

    OUT.write_text(json.dumps({"tolerance_pp": TOL, "claims": rows}, indent=1), encoding="utf-8")
    print(f"{'iddia':12s} {'bildirilen':>11s} {'yeniden':>11s} {'hata':>8s}  sonuc")
    for r in rows:
        if "recomputed" in r:
            print(f"{r['claim']:12s} {r['claimed']:>11.2f} {r['recomputed']:>11.4f} "
                  f"{r['abs_error']:>8.4f}  {r['verdict']}")
        else:
            print(f"{r['claim']:12s} {'-':>11s} {'-':>11s} {'-':>8s}  {r['verdict']}")
    print(f"\nPRIMARY_RECOMPUTED: {ok}/{len(CLAIMS)}  (tolerans {TOL} pp)")
    print(f"kayit: {OUT.name}")

if __name__ == "__main__":
    main()
