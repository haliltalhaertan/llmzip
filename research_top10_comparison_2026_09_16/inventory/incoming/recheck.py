# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Re-aggregate the incoming 2026-09-16 package's OWN raw per-query CSVs.

Reads (read-only, outside our directory):
  HATA = .../LLMZIP_HATA_YERI_2026-09-16/.../results/readout_per_query.csv
  HIZ  = .../LLMZIP_HIZ_GENELLEME_2026-09-16/.../results/quality_per_query.csv
Compares re-aggregated means against the producers' own summary JSONs.
No benchmarks are run; no input file is modified.
Run with: $HOME/muse-work/ml-python recheck.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

LABELS = ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
          "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"]

EXT = Path("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916/extracted")
HATA = EXT / "LLMZIP_HATA_YERI_2026-09-16/LLMZIP_HATA_YERI_2026-09-16"
HIZ = EXT / "LLMZIP_HIZ_GENELLEME_2026-09-16/LLMZIP_HIZ_GENELLEME_2026-09-16"
HERE = Path(__file__).resolve().parent


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def aggregate(rows, metrics):
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for m in metrics:
            acc[(r["dataset"], r["arm"])][m].append(float(r[m]))
    return {k: {m: mean(v[m]) for m in metrics} for k, v in acc.items()}


def main():
    out = {"labels": LABELS, "checks": {}}

    # ---------- HATA readout ----------
    hrows = load_csv(HATA / "results/readout_per_query.csv")
    out["checks"]["hata_rows"] = len(hrows)
    out["checks"]["hata_n_queries"] = len({(r["dataset"], r["archive"], r["qid"]) for r in hrows})
    hagg = aggregate(hrows, ["hit3", "recall3", "hit10", "recall10", "hit100", "recall100"])
    hsum = json.loads((HATA / "results/readout_summary.json").read_text())
    hdiag = json.loads((HATA / "results/DIAGNOSIS_SUMMARY.json").read_text())
    maxdev_summary = 0.0
    maxdev_diag = 0.0
    detail = {}
    for (ds, arm), vals in sorted(hagg.items()):
        rep = hsum["datasets"][ds]["arms"][arm]
        devs = {m: abs(vals[m] - rep[m]) for m in vals}
        maxdev_summary = max(maxdev_summary, max(devs.values()))
        cell = {"n": len([r for r in hrows if r["dataset"] == ds and r["arm"] == arm]),
                "reagg_hit10": vals["hit10"],
                "summary_hit10": rep["hit10"],
                "max_abs_dev_over_6_metrics": max(devs.values())}
        # DIAGNOSIS_SUMMARY carries a subset of arms in percent
        if arm in hdiag["hit10_percent"].get(ds, {}):
            diag_frac = hdiag["hit10_percent"][ds][arm] / 100.0
            cell["diagnosis_hit10"] = diag_frac
            cell["abs_dev_vs_diagnosis_hit10"] = abs(vals["hit10"] - diag_frac)
            maxdev_diag = max(maxdev_diag, cell["abs_dev_vs_diagnosis_hit10"])
        detail[f"{ds}|{arm}"] = cell
    out["hata_reagg_vs_readout_summary"] = {
        "max_abs_dev_over_all_cells_and_6_metrics": maxdev_summary}
    out["hata_reagg_vs_diagnosis_summary_hit10"] = {"max_abs_dev": maxdev_diag}
    out["hata_detail"] = detail

    # HATA paired-contrast spot check (recompute two contrasts from raw rows)
    lookup = {(r["archive"], r["qid"], r["arm"]): float(r["hit10"])
              for r in hrows if r["dataset"] == "RealTalk"}
    qs = sorted({(r["archive"], r["qid"]) for r in hrows if r["dataset"] == "RealTalk"})
    for a, b in [("standardized_cos", "doc_sign_query_std"),
                 ("standardized_cos", "query_sign_doc_std")]:
        d = [lookup[(aid, q, b)] - lookup[(aid, q, a)] for aid, q in qs]
        rep = hsum["paired"]["RealTalk"][a + " -> " + b]["delta_pp"]
        out.setdefault("hata_paired_spotcheck", {})[f"RealTalk|{a}->{b}"] = {
            "reagg_delta_pp": mean(d) * 100, "reported_delta_pp": rep}

    # ---------- HIZ quality ----------
    zrows = load_csv(HIZ / "results/quality_per_query.csv")
    out["checks"]["hiz_rows"] = len(zrows)
    out["checks"]["hiz_n_queries"] = len({(r["dataset"], r["archive"], r["qid"]) for r in zrows})
    zagg = aggregate(zrows, ["hit3", "recall3", "hit10", "recall10", "hit100", "recall100"])
    fin = json.loads((HIZ / "results/FINAL_SUMMARY.json").read_text())
    maxdev_fin = 0.0
    zdetail = {}
    for (ds, arm), vals in sorted(zagg.items()):
        rep_pct = fin["datasets"][ds]["hit10_percent"][arm]
        dev = abs(vals["hit10"] * 100 - rep_pct)
        maxdev_fin = max(maxdev_fin, dev)
        zdetail[f"{ds}|{arm}"] = {"n": len([r for r in zrows if r["dataset"] == ds and r["arm"] == arm]),
                                  "reagg_hit10_pct": vals["hit10"] * 100,
                                  "final_hit10_pct": rep_pct,
                                  "abs_dev_pp": dev}
    out["hiz_reagg_vs_final_summary_hit10_pp"] = {"max_abs_dev_pp": maxdev_fin}
    out["hiz_detail"] = zdetail

    # Headline deltas: weighted(new/qscale) minus hamming, per benchmark
    out["headline_weighted_minus_hamming_pp"] = {}
    for ds in ["LME", "PerLTQA", "RealTalk", "LoCoMo"]:
        w = zagg[(ds, "weighted")]["hit10"] * 100
        h = zagg[(ds, "hamming")]["hit10"] * 100
        out["headline_weighted_minus_hamming_pp"][ds] = {
            "weighted": w, "hamming": h, "delta_pp": w - h}

    # CRITICAL: qscale(new) minus old asym, per benchmark, from BOTH raw sources
    out["critical_new_minus_oldasym_pp"] = {}
    for ds in ["LME", "PerLTQA", "RealTalk"]:
        new = hagg[(ds, "doc_sign_query_std")]["hit10"] * 100
        old = hagg[(ds, "doc_sign_query_raw")]["hit10"] * 100
        out["critical_new_minus_oldasym_pp"][ds + "|HATA"] = {
            "new_qscale": new, "old_asym": old, "delta_pp": new - old}
    for ds in ["LME", "PerLTQA", "RealTalk", "LoCoMo"]:
        new = zagg[(ds, "weighted")]["hit10"] * 100
        old = zagg[(ds, "asym_raw")]["hit10"] * 100
        out["critical_new_minus_oldasym_pp"][ds + "|HIZ"] = {
            "new_qscale": new, "old_asym": old, "delta_pp": new - old}

    # LoCoMo headline numbers
    out["locomo_hit10_pct"] = {arm: zagg[("LoCoMo", arm)]["hit10"] * 100
                               for arm in ["hamming", "asym_raw", "weighted", "float32"]}
    out["locomo_n"] = len({(r["archive"], r["qid"]) for r in zrows if r["dataset"] == "LoCoMo"})

    # LoCoMo adapter cohort
    adap = json.loads((HIZ / "results/locomo_adapter_before_scores.json").read_text())
    by_reason = defaultdict(int)
    for e in adap["excluded"]:
        by_reason[e["reason"]] += 1
    out["locomo_adapter"] = {
        "total_questions": adap["total_questions"],
        "kept_questions": adap["kept_questions"],
        "n_excluded": len(adap["excluded"]),
        "excluded_by_reason": dict(by_reason),
        "n_normalizations": len(adap["normalizations"]),
        "policy": adap["policy"],
        "source_sha256": adap["source_sha256"],
        "per_archive_kept": {c["id"]: c["queries"] for c in adap["counts"]},
        "per_archive_docs": {c["id"]: c["docs"] for c in adap["counts"]},
    }

    # LoCoMo paired comparisons re-derivation (delta + win/loss counts from raw)
    zlook = {(r["archive"], r["qid"], r["arm"]): float(r["hit10"]) for r in zrows
             if r["dataset"] == "LoCoMo"}
    zqs = sorted({(r["archive"], r["qid"]) for r in zrows if r["dataset"] == "LoCoMo"})
    pairs = json.loads((HIZ / "results/locomo_paired_comparisons.json").read_text())
    out["locomo_pairs_rederived"] = {}
    for a, b in [("hamming", "weighted"), ("asym_raw", "weighted"), ("float_std64", "weighted")]:
        d = [zlook[(aid, q, b)] - zlook[(aid, q, a)] for aid, q in zqs]
        rep = pairs[f"{a} -> {b}"]
        out["locomo_pairs_rederived"][f"{a}->{b}"] = {
            "reagg_delta_pp": mean(d) * 100, "reported_delta_pp": rep["delta_pp"],
            "reagg_improved": sum(1 for v in d if v > 1e-12),
            "reported_improved": rep.get("query_improvements"),
            "reagg_regressed": sum(1 for v in d if v < -1e-12),
            "reported_regressed": rep.get("query_regressions")}

    with open(HERE / "recheck_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({
        "hata_rows": out["checks"]["hata_rows"],
        "hata_maxdev_vs_summary": out["hata_reagg_vs_readout_summary"],
        "hata_maxdev_vs_diag": out["hata_reagg_vs_diagnosis_summary_hit10"],
        "hiz_rows": out["checks"]["hiz_rows"],
        "hiz_maxdev_vs_final_pp": out["hiz_reagg_vs_final_summary_hit10_pp"],
        "deltas_w_minus_h": {k: round(v["delta_pp"], 4)
                             for k, v in out["headline_weighted_minus_hamming_pp"].items()},
        "critical": {k: round(v["delta_pp"], 4)
                     for k, v in out["critical_new_minus_oldasym_pp"].items()},
        "locomo": {k: round(v, 4) for k, v in out["locomo_hit10_pct"].items()},
        "locomo_n": out["locomo_n"],
        "adapter": out["locomo_adapter"]["excluded_by_reason"],
    }, indent=2))


if __name__ == "__main__":
    main()
