#!/usr/bin/env python3
"""Adversarial probe rig for the V6 single-source gate.

Every probe runs on a throwaway copy under /tmp. The real candidate is never touched.
After mutating a payload the rig REBINDS PAYLOAD_HASHES.json and the seal's
payload_inventory.sha256 -- exactly what an implementer would do when editing a
declarative payload -- so that probes reach the single-source sweep rather than
stopping at the closure check.
"""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path("/home/user/llmzip")
CAND = REPO / "task4f1_execution_candidate_v6_2026_09_03"
PY = "/opt/py31213/bin/python3"

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def stage() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="v6probe_"))
    shutil.copytree(CAND, tmp / CAND.name)
    dst = tmp / "docs" / "v52" / "task4f1"
    dst.mkdir(parents=True)
    shutil.copy2(REPO / "docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json", dst)
    return tmp / CAND.name

def rebind(root: Path) -> None:
    """Recompute the inventory over the actual closure and re-bind the seal."""
    mpath = root / "PAYLOAD_HASHES.json"
    spath = root / "CANDIDATE_EXECUTION_SEAL.json"
    manifest = json.loads(mpath.read_text())
    files = sorted(
        {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        - {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"}
    )
    manifest["files"] = [
        {"bytes": (root / n).stat().st_size, "name": n, "sha256": sha256(root / n)} for n in files
    ]
    manifest["file_count_excluding_inventory_and_seal"] = len(files)
    mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    seal = json.loads(spath.read_text())
    seal["payload_inventory"]["sha256"] = sha256(mpath)
    seal["payload_inventory"]["file_count_excluding_inventory_and_seal"] = len(files)
    spath.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
    seal2 = json.loads(spath.read_text())
    assert seal2["payload_inventory"]["sha256"] == sha256(mpath)

def gate(root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [PY, "-B", str(root / "candidate_package_preflight.py")],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0"},
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()

def verdict(name: str, rc: int, out: str, expect_block: bool) -> dict:
    blocked = rc != 0
    tail = out.splitlines()[-1][:240] if out else ""
    status = "CAUGHT" if blocked else "NOT CAUGHT"
    ok = blocked == expect_block
    print(f"[{'ok ' if ok else 'XX '}] {name}: {status}")
    if tail and blocked:
        print(f"        -> {tail}")
    return {"probe": name, "blocked": blocked, "expected_block": expect_block,
            "gate_behaved_as_required": ok, "detail": tail}
