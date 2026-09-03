#!/usr/bin/env python3
"""Independently verify INDEPENDENT_V6_EXECUTION_AUDIT_HASHES.json against the bytes on disk."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

NS = Path("/home/user/llmzip/audit_v52_t4f1_execution_candidate_v6_independent_audit_2026_09_03")
SELF = "INDEPENDENT_V6_EXECUTION_AUDIT_HASHES.json"
man = json.loads((NS / SELF).read_text())

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()

on_disk = {p.relative_to(NS).as_posix() for p in NS.rglob("*")
           if p.is_file() and "__pycache__" not in p.parts} - {SELF}
declared = set(man["files"])
bad = [n for n, rec in man["files"].items()
       if not (NS / n).is_file() or sha(NS / n) != rec["sha256"] or (NS / n).stat().st_size != rec["bytes"]]

ok = not bad and on_disk == declared
print(f"declared outputs      : {len(declared)}")
print(f"present on disk       : {len(on_disk)}")
print(f"missing from manifest : {sorted(on_disk - declared)}")
print(f"declared but absent   : {sorted(declared - on_disk)}")
print(f"hash/size mismatches  : {bad}")
print(f"manifest sha256       : {sha(NS / SELF)}")
print(f"VERIFIED              : {ok}")
sys.exit(0 if ok else 1)
