#!/usr/bin/env python3
"""Verify archival bytes only. Does not execute archived research code."""
import hashlib, json, sys
from pathlib import Path
root=Path(__file__).resolve().parent
m=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
errors=[]
for rec in m['files']:
    path=root/rec['archive_member']
    if not path.is_file():
        errors.append(f"MISSING {rec['archive_member']}"); continue
    data=path.read_bytes()
    if len(data)!=rec['bytes'] or hashlib.sha256(data).hexdigest()!=rec['sha256']:
        errors.append(f"MISMATCH {rec['archive_member']}")
print(json.dumps({'files':len(m['files']),'verified':len(m['files'])-len(errors),'errors':errors},indent=2))
sys.exit(bool(errors))
