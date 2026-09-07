"""Write the report's .sha256 sidecar and HASH_MANIFEST.json (recursive sha256
over the audit namespace, excluding the manifest itself). Run from the repo root."""
import hashlib, json, sys
from pathlib import Path

NS = Path("audit_v52_acceptance_closure_2026_09_07")
MANIFEST = NS / "HASH_MANIFEST.json"
REPORT = NS / "CLOSURE_AUDIT_REPORT.md"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# sidecar first, so it is itself covered by the manifest
(NS / "CLOSURE_AUDIT_REPORT.md.sha256").write_bytes(
    f"{sha(REPORT)} *{REPORT.name}\n".encode())

entries = {}
for p in sorted(NS.rglob("*")):
    if not p.is_file():
        continue
    if p == MANIFEST or "__pycache__" in p.parts:
        continue
    entries[p.as_posix()] = {"sha256": sha(p), "bytes": p.stat().st_size}

MANIFEST.write_text(json.dumps({
    "namespace": NS.as_posix(),
    "branch": "audit/v52-acceptance-closure-2026-09-07",
    "audited_main_commit": "ed2b2f74347da6be68beae2c22d5c3d22992f1a3",
    "audited_research_commit": "0c9916bd7786d7ddb332f5b6da3d96d61a6223f0",
    "controlling_prompt_sha256": "c6a0da6a3076793b5b3cc0b0d0796b3fe30a1a21644e539c3b4f9a0bd1649faf",
    "verdict": "CLOSURE PASS WITH CAVEATS",
    "excludes": ["HASH_MANIFEST.json (itself)", "__pycache__", "virtualenvs", "corpora"],
    "file_count": len(entries),
    "files": entries,
}, indent=2))
print("report sha256:", sha(REPORT))
print("files in manifest:", len(entries))
for k, v in entries.items():
    print(" ", v["sha256"][:12], f"{v['bytes']:>9}", k)
