#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

METHODS = ("SIGN96", "SIGN96_R4", "SIGN96_R8", "SIGN96_R16")


def sign(x: float, eps: float = 1e-12) -> int:
    return 1 if x > eps else (-1 if x < -eps else 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    for p in sorted(args.input.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("schema") == "LLMZIP_SIGN96_MICRO_RESIDUAL_NANOBEIR_V1":
            rows.append(d)
    if len(rows) != 13:
        raise RuntimeError(f"expected 13 result JSONs, found {len(rows)}")

    summary = {
        "label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
        "schema": "LLMZIP_SIGN96_MICRO_RESIDUAL_NANOBEIR_SUMMARY_V1",
        "tasks": len(rows),
        "total_queries": int(sum(r["dataset"]["n_queries"] for r in rows)),
        "total_documents": int(sum(r["dataset"]["n_docs"] for r in rows)),
        "primary_method": "SIGN96_R8",
        "methods": {},
        "per_task": [],
    }

    for method in METHODS:
        for metric in ("recall@3", "ndcg@10"):
            dvf = np.array([r["methods"][method]["metrics"][metric]["delta_vs_float_pp"] for r in rows], dtype=float)
            dvs = np.array([r["methods"][method]["metrics"][metric]["delta_vs_sign96_pp"] for r in rows], dtype=float)
            block = summary["methods"].setdefault(method, {})
            block[metric] = {
                "macro_delta_vs_float_pp": float(dvf.mean()),
                "median_delta_vs_float_pp": float(np.median(dvf)),
                "wtl_vs_float": {
                    "wins": int(np.sum(dvf > 1e-12)),
                    "ties": int(np.sum(np.abs(dvf) <= 1e-12)),
                    "losses": int(np.sum(dvf < -1e-12)),
                },
                "macro_delta_vs_sign96_pp": float(dvs.mean()),
                "median_delta_vs_sign96_pp": float(np.median(dvs)),
                "wtl_vs_sign96": {
                    "wins": int(np.sum(dvs > 1e-12)),
                    "ties": int(np.sum(np.abs(dvs) <= 1e-12)),
                    "losses": int(np.sum(dvs < -1e-12)),
                },
            }
        summary["methods"][method]["active_bits"] = rows[0]["methods"][method]["active_bits"]
        summary["methods"][method]["min_byte_aligned_packed_bytes"] = rows[0]["methods"][method]["min_byte_aligned_packed_bytes"]
        summary["methods"][method]["macro_doc_collision_fraction"] = float(np.mean([
            r["methods"][method]["collision"]["doc_collision_fraction"] for r in rows
        ]))
        summary["methods"][method]["macro_top3_boundary_tie_rate"] = float(np.mean([
            r["methods"][method]["top3_boundary_tie_rate"] for r in rows
        ]))

    # Does the residual preferentially help tasks where base SIGN96 lost to FLOAT96?
    base = np.array([r["methods"]["SIGN96"]["metrics"]["recall@3"]["delta_vs_float_pp"] for r in rows])
    losing = base < -1e-12
    for method in ("SIGN96_R4", "SIGN96_R8", "SIGN96_R16"):
        improve = np.array([r["methods"][method]["metrics"]["recall@3"]["delta_vs_sign96_pp"] for r in rows])
        summary["methods"][method]["loss_task_rescue_recall@3"] = {
            "base_sign96_losing_tasks": int(losing.sum()),
            "mean_improvement_pp_on_base_losing_tasks": float(improve[losing].mean()) if losing.any() else None,
            "improved_count": int(np.sum(improve[losing] > 1e-12)) if losing.any() else 0,
            "worsened_count": int(np.sum(improve[losing] < -1e-12)) if losing.any() else 0,
        }

    for r in sorted(rows, key=lambda x: x["task"]):
        item = {"task": r["task"]}
        for method in METHODS:
            item[method] = {
                "recall3_delta_vs_float_pp": r["methods"][method]["metrics"]["recall@3"]["delta_vs_float_pp"],
                "recall3_delta_vs_sign96_pp": r["methods"][method]["metrics"]["recall@3"]["delta_vs_sign96_pp"],
                "ndcg10_delta_vs_float_pp": r["methods"][method]["metrics"]["ndcg@10"]["delta_vs_float_pp"],
                "collision_fraction": r["methods"][method]["collision"]["doc_collision_fraction"],
                "top3_tie_rate": r["methods"][method]["top3_boundary_tie_rate"],
            }
        summary["per_task"].append(item)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# SIGN96 micro-residual NanoBEIR summary",
        "",
        summary["label"],
        "",
        f"Tasks: {summary['tasks']} | queries: {summary['total_queries']} | documents: {summary['total_documents']}",
        "",
        "Primary candidate was frozen before outcomes: **SIGN96_R8 (104 active bits; minimum 13 byte-aligned packed bytes)**.",
        "",
        "## Macro results",
        "",
        "| Method | Bytes | Recall@3 Δ vs FLOAT (pp) | W/T/L vs FLOAT | Recall@3 Δ vs SIGN96 (pp) | nDCG@10 Δ vs FLOAT (pp) | Collision frac | Top-3 tie rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        m = summary["methods"][method]
        rr = m["recall@3"]
        nn = m["ndcg@10"]
        w = rr["wtl_vs_float"]
        lines.append(
            f"| {method} | {m['min_byte_aligned_packed_bytes']} | {rr['macro_delta_vs_float_pp']:+.3f} | "
            f"{w['wins']}/{w['ties']}/{w['losses']} | {rr['macro_delta_vs_sign96_pp']:+.3f} | "
            f"{nn['macro_delta_vs_float_pp']:+.3f} | {m['macro_doc_collision_fraction']:.4f} | {m['macro_top3_boundary_tie_rate']:.4f} |"
        )

    lines += ["", "## Per-task Recall@3 deltas versus FLOAT96", "",
              "| Task | SIGN96 | +4R | +8R primary | +16R |", "|---|---:|---:|---:|---:|"]
    for item in summary["per_task"]:
        lines.append(
            f"| {item['task']} | {item['SIGN96']['recall3_delta_vs_float_pp']:+.3f} | "
            f"{item['SIGN96_R4']['recall3_delta_vs_float_pp']:+.3f} | "
            f"{item['SIGN96_R8']['recall3_delta_vs_float_pp']:+.3f} | "
            f"{item['SIGN96_R16']['recall3_delta_vs_float_pp']:+.3f} |"
        )

    p = summary["methods"]["SIGN96_R8"]["recall@3"]
    rescue = summary["methods"]["SIGN96_R8"]["loss_task_rescue_recall@3"]
    lines += [
        "",
        "## Frozen primary readout",
        "",
        f"SIGN96_R8 macro Recall@3 change versus SIGN96: **{p['macro_delta_vs_sign96_pp']:+.3f} pp**.",
        f"On the {rescue['base_sign96_losing_tasks']} tasks where base SIGN96 lost to FLOAT96, R8 changed Recall@3 by "
        f"**{rescue['mean_improvement_pp_on_base_losing_tasks']:+.3f} pp on average**; "
        f"{rescue['improved_count']} improved and {rescue['worsened_count']} worsened.",
        "",
        "Residual ranking is lexicographic: base 96-bit Hamming remains primary, residual Hamming only resolves base-Hamming ties. "
        "These are active-code figures only, not whole-system storage costs.",
    ]
    args.out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "primary": "SIGN96_R8",
        "macro_delta_vs_sign96_recall3_pp": p["macro_delta_vs_sign96_pp"],
        "macro_delta_vs_float_recall3_pp": p["macro_delta_vs_float_pp"],
        "r8_collision_fraction": summary["methods"]["SIGN96_R8"]["macro_doc_collision_fraction"],
        "sign96_collision_fraction": summary["methods"]["SIGN96"]["macro_doc_collision_fraction"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
