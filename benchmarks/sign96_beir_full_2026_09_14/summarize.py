#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
TASKS = ["scifact", "scidocs", "arguana", "fiqa", "nfcorpus", "trec-covid"]


def find_result(root: Path, task: str) -> Path:
    matches = [p for p in root.rglob(f"{task}.json") if "pre_qrels" not in p.name]
    if len(matches) != 1:
        raise RuntimeError(f"{task}: expected 1 result, found {matches}")
    return matches[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for task in TASKS:
        data = json.loads(find_result(args.root, task).read_text(encoding="utf-8"))
        rows.append({
            "task": task,
            "documents": data["sizes"]["documents"],
            "queries": data["sizes"]["queries"],
            "delta_recall@3_pp": data["metrics"]["recall@3"]["delta_pp"],
            "delta_ndcg@10_pp": data["metrics"]["ndcg@10"]["delta_pp"],
            "float_recall@3": data["metrics"]["recall@3"]["float"],
            "sign_recall@3": data["metrics"]["recall@3"]["sign"],
            "float_ndcg@10": data["metrics"]["ndcg@10"]["float"],
            "sign_ndcg@10": data["metrics"]["ndcg@10"]["sign"],
            "frozen_rankings_sha256": data["integrity"]["frozen_rankings_sha256"],
        })
    dr = np.asarray([r["delta_recall@3_pp"] for r in rows], dtype=float)
    dn = np.asarray([r["delta_ndcg@10_pp"] for r in rows], dtype=float)
    summary = {
        "label": LABEL,
        "tasks": rows,
        "aggregate": {
            "recall@3": {
                "wins": int(np.sum(dr > 0)), "ties": int(np.sum(dr == 0)), "losses": int(np.sum(dr < 0)),
                "macro_delta_pp": float(np.mean(dr)), "median_delta_pp": float(np.median(dr)),
            },
            "ndcg@10": {
                "wins": int(np.sum(dn > 0)), "ties": int(np.sum(dn == 0)), "losses": int(np.sum(dn < 0)),
                "macro_delta_pp": float(np.mean(dn)), "median_delta_pp": float(np.median(dn)),
            },
            "total_documents_across_task_corpora": int(sum(r["documents"] for r in rows)),
            "total_queries": int(sum(r["queries"] for r in rows)),
        },
    }
    (args.outdir / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [LABEL, "", "# Full BEIR wave-1 summary", "", "| Task | Docs | Queries | Δ Recall@3 pp | Δ nDCG@10 pp |", "|---|---:|---:|---:|---:|"]
    for r in rows:
        md.append(f"| {r['task']} | {r['documents']:,} | {r['queries']:,} | {r['delta_recall@3_pp']:+.3f} | {r['delta_ndcg@10_pp']:+.3f} |")
    md += ["", f"Recall@3 W/T/L: **{summary['aggregate']['recall@3']['wins']}/{summary['aggregate']['recall@3']['ties']}/{summary['aggregate']['recall@3']['losses']}**, macro Δ **{summary['aggregate']['recall@3']['macro_delta_pp']:+.3f} pp**.", f"nDCG@10 W/T/L: **{summary['aggregate']['ndcg@10']['wins']}/{summary['aggregate']['ndcg@10']['ties']}/{summary['aggregate']['ndcg@10']['losses']}**, macro Δ **{summary['aggregate']['ndcg@10']['macro_delta_pp']:+.3f} pp**.", "", "96 bits = 12 active SIGN code bytes only; this is not a whole-system storage-cost claim."]
    (args.outdir / "SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary["aggregate"], indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
