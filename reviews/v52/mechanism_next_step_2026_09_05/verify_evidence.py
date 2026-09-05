"""Read pinned Git blobs and reconstruct persisted results; never import runners.

Usage: python -B reviews/v52/mechanism_next_step_2026_09_05/verify_evidence.py
Writes only this review's evidence and inventory. Standard library only.
"""
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAIN = "45e6ddea247fdb8614715a717bea8015283178d0"
TARGET = "1a33ef0d1a2715257920201f7a3db8ab4677a007"
AUDIT = "27f50f44490b419921b1d634f11006529b290a6f"
NS = "audit_v52_boundary_localization_independent_2026_09_04/"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def blob(commit, path):
    return git("cat-file", "blob", commit + ":" + path)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify():
    state = json.loads(blob(MAIN, "ops/CURRENT_STATE.json"))
    require(state["task_state"]["task_4f1_run"] == "BLOCKED", "run state drift")
    require(state["task_state"]["retrieval_quality_outcome_access"] == "FORBIDDEN", "outcome state drift")
    require(git("rev-parse", AUDIT + "^").decode().strip() == TARGET, "audit parent drift")
    measured = {}
    declared = json.loads(blob(AUDIT, NS + "AUDIT_HASHES.json"))["files"]
    for path, record in declared.items():
        data = blob(TARGET, path)
        sha = digest(data)
        obj = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(sha == record["sha256_measured"], "SHA256 mismatch: " + path)
        require(obj == record["git_blob_sha1_measured"], "blob mismatch: " + path)
        require(len(data) == record["bytes"], "size mismatch: " + path)
        measured[path] = {"sha256": sha, "bytes": len(data), "git_blob": obj}
    report = blob(AUDIT, NS + "AUDIT_REPORT.md")
    sidecar = blob(AUDIT, NS + "AUDIT_REPORT.md.sha256").decode().split()[0]
    require(digest(report) == sidecar, "audit report sidecar mismatch")
    additions = git("diff-tree", "--no-commit-id", "--name-status", "-r", AUDIT).decode().splitlines()
    require(all(line.startswith("A\t" + NS) for line in additions), "audit modifies non-audit paths")
    audit_files = {}
    for line in additions:
        path = line.split("\t", 1)[1]
        data = blob(AUDIT, path)
        audit_files[path] = {"sha256": digest(data), "bytes": len(data)}
    datasets = {}
    for name, prefix, count, native_anchor, full_anchor in [
        ("LoCoMo", "locomo", 1535, 0.23654714666441054, 0.13770827054136),
        ("LongMemEval", "longmemeval", 470, 0.5419751773049646, 0.38271666666667),
    ]:
        base = "research/v52/" + prefix + "_boundary_outputs/"
        rows = list(csv.DictReader(io.StringIO(gzip.decompress(blob(TARGET, base + prefix + "_boundary_per_question.csv.gz")).decode())))
        arms = ["B16", "B24", "B32", "B48", "B64", "RANDOM32"]
        seeds = list(range(58001, 58011))
        groups = {(arm, seed): [] for arm in arms for seed in seeds}
        native = {}
        seen = set()
        for row in rows:
            q = row["question_id"]
            arm, seed = row["arm"], int(row["rotation_seed"])
            key = (q, arm, seed)
            require(key not in seen, "duplicate cell")
            seen.add(key)
            value, nv = float(row["fractional_R3"]), float(row["native_fractional_R3"])
            require(math.isfinite(value) and 0 <= value <= 1, "invalid contribution")
            require(math.isfinite(nv) and 0 <= nv <= 1, "invalid native contribution")
            if q in native:
                require(native[q] == nv, "inconsistent native per question")
            native[q] = nv
            groups[arm, seed].append(value)
        require(len(native) == count and len(rows) == count * 60, "cohort count mismatch")
        require(all(len(v) == count for v in groups.values()), "unbalanced cells")
        native_mean = statistics.mean(native.values())
        require(abs(native_mean - native_anchor) <= 1e-12, "native reproduction mismatch")
        means = {k: statistics.mean(v) for k, v in groups.items()}
        declared_rows = list(csv.DictReader(io.StringIO(blob(TARGET, base + prefix + "_boundary_seed_results.csv").decode())))
        errors = [abs(means[r["arm"], int(r["rotation_seed"])] - float(r["R3"])) for r in declared_rows]
        require(len(errors) == 60 and max(errors) <= 1e-12, "declared seed reconstruction mismatch")
        rho = {a: (native_mean - statistics.mean(means[a, s] for s in seeds)) / (native_anchor - full_anchor) for a in arms}
        datasets[name] = {"questions": count, "rows": len(rows), "csv_fields": list(rows[0]),
                          "native": native_mean, "max_seed_R3_error": max(errors), "rho": rho,
                          "sufficient_boundaries": [int(a[1:]) for a in arms[:-1] if rho[a] <= .25],
                          "delta32": rho["RANDOM32"] - rho["B32"],
                          "direct_B32_minus_RANDOM32_R3": statistics.mean(means["B32", s] - means["RANDOM32", s] for s in seeds)}
    common = sorted(set(datasets["LoCoMo"]["sufficient_boundaries"]) & set(datasets["LongMemEval"]["sufficient_boundaries"]))
    return {"status": "PASS", "scope": "Pinned-byte receipt and persisted-result reconstruction, not cold-start audit or raw retrieval reproduction",
            "main": MAIN, "target": TARGET, "audit": AUDIT, "audit_report_sha256": sidecar,
            "verified_target_files": measured, "pinned_audit_file_inventory": audit_files,
            "audit_inventory_scope": "Original AUDIT_HASHES.json covers target files; this review additionally hashes all audit additions",
            "datasets": datasets, "S_common": common, "new_retrieval_runs": 0,
            "Task4F1_outcome_access": False, "canonical_state_changed": False}


if __name__ == "__main__":
    result = verify()
    (HERE / "VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    payloads = {p.name: {"sha256": digest(p.read_bytes()), "bytes": p.stat().st_size}
                for p in sorted(HERE.iterdir()) if p.is_file() and p.name != "REVIEW_HASHES.json"}
    (HERE / "REVIEW_HASHES.json").write_text(json.dumps({"files": payloads}, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "target_files": len(result["verified_target_files"]),
                      "audit_files": len(result["pinned_audit_file_inventory"]), "datasets": result["datasets"], "S_common": result["S_common"]}, indent=2))
