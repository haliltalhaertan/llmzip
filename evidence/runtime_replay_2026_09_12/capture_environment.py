"""Capture and hash installed distribution records without reading credentials."""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import sys
import faiss

HERE = Path(__file__).resolve().parent
packages = {}
for name in ('faiss-cpu', 'numpy', 'packaging'):
    dist = metadata.distribution(name)
    packages[name] = {'version': dist.version, 'metadata_records': {}}
    for name_in_dist in ('METADATA', 'WHEEL', 'RECORD'):
        value = dist.read_text(name_in_dist)
        if value is not None:
            raw = value.encode('utf-8')
            packages[name]['metadata_records'][name_in_dist] = {
                'sha256_of_utf8_text': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
report = {'python': sys.version, 'platform': platform.platform(),
          'faiss_compile_options': faiss.get_compile_options(), 'packages': packages,
          'scope': 'Installed distribution record fingerprints, not a claim of downloaded wheel hash verification.'}
(HERE / 'ENVIRONMENT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
