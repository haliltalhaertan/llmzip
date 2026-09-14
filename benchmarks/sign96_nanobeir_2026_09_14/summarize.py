#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    for p in sorted(args.input.rglob("Nano*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        if obj.get("schema") != "LLMZIP_SIGN96_NANOBEIR_SWEEP_V1":
            continue
        rows.append(obj)
    if len(rows) != 13:
        raise RuntimeError(f"expected 13 task result JSONs, found {len(rows)}")

    table = []
    for r in sorted(rows, key=lambda z: z["task"]):
        table.append({
            "task": r["task"],
            "n_docs": r["dataset"]["n_docs"],
            "n_queries": r["dataset"]["n_queries"],
            "float_r3": r["metrics"]["recall@3"]["float"],
            "sign_r3": r["metrics"]["recall@3"]["sign"],
            "delta_r3_pp": r["metrics"]["recall@3"]["delta_pp"],
            "float_ndcg10": r["metrics"]["ndcg@10"]["float"],
            "sign_ndcg10": r["metrics"]["ndcg@10"]["sign"],
            "delta_ndcg10_pp": r["metrics"]["ndcg@10"]["delta_pp"],
            "tie_rate3": r["diagnostics"]["sign_boundary_tie_rate_at_3"],
        })

    dr = np.array([x["delta_r3_pp"] for x in table], dtype=float)
    dn = np.array([x["delta_ndcg10_pp"] for x in table], dtype=float)
    summary = {
        "label": LABEL,
        "schema": "LLMZIP_SIGN96_NANOBEIR_SWEEP_SUMMARY_V1",
        "n_tasks": len(table),
        "sign_wins_recall3": int(np.sum(dr > 0)),
        "ties_recall3": int(np.sum(np.isclose(dr, 0))),
        "sign_losses_recall3": int(np.sum(dr < 0)),
        "macro_delta_recall3_pp": float(dr.mean()),
        "median_delta_recall3_pp": float(np.median(dr)),
        "sign_wins_ndcg10": int(np.sum(dn > 0)),
        "ties_ndcg10": int(np.sum(np.isclose(dn, 0))),
        "sign_losses_ndcg10": int(np.sum(dn < 0)),
        "macro_delta_ndcg10_pp": float(dn.mean()),
        "median_delta_ndcg10_pp": float(np.median(dn)),
        "tasks": table,
        "interpretation_boundary": (
            "Exploratory NanoBEIR cross-benchmark screen. "
            "Do not call this a 12-byte full-system result; 12 B is active SIGN96 code only."
        ),
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        LABEL,
        "",
        "# SIGN96 vs FLOAT96 — NanoBEIR 13-task sweep",
        "",
        f"- Recall@3 W/T/L: **{summary['sign_wins_recall3']}/{summary['ties_recall3']}/{summary['sign_losses_recall3']}**",
        f"- Macro Δ Recall@3: **{summary['macro_delta_recall3_pp']:+.3f} pp**",
        f"- Median Δ Recall@3: **{summary['median_delta_recall3_pp']:+.3f} pp**",
        f"- nDCG@10 W/T/L: **{summary['sign_wins_ndcg10']}/{summary['ties_ndcg10']}/{summary['sign_losses_ndcg10']}**",
        f"- Macro Δ nDCG@10: **{summary['macro_delta_ndcg10_pp']:+.3f} pp**",
        "",
        "| Task | Docs | Q | FLOAT R@3 | SIGN R@3 | Δ R@3 pp | FLOAT nDCG@10 | SIGN nDCG@10 | Δ nDCG pp | tie@3 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for x in table:
        lines.append(
            f"| {x['task']} | {x['n_docs']} | {x['n_queries']} | "
            f"{x['float_r3']:.4f} | {x['sign_r3']:.4f} | {x['delta_r3_pp']:+.3f} | "
            f"{x['float_ndcg10']:.4f} | {x['sign_ndcg10']:.4f} | {x['delta_ndcg10_pp']:+.3f} | "
            f"{x['tie_rate3']:.3f} |"
        )
    lines += [
        "",
        "## Boundary",
        "",
        "This is an exploratory generalization screen, not Task4F1, not causal proof, and not a full storage-accounting result.",
        "FLOAT96 and SIGN96 share the exact same centered 96D input; only sign/Hamming replaces centered-cosine ranking.",
        "Qrels are loaded only after rankings are frozen in memory.",
    ]
    args.out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
