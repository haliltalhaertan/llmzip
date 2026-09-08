"""Execute only named, SHA256-verified source blobs; ignore checkout line endings.

Git executable and installed Python packages are trusted environment dependencies.
This is source identity verification, not an OS sandbox or execution authorization.
"""
import hashlib
from pathlib import Path
import subprocess
import types

ROOT = Path(__file__).resolve().parents[3]
PINS = {
    'core': ('dcb568d0a6c33154c1568500325ad457b4d6f455',
             'drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py',
             'bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72'),
    'contracts': ('56e67018b61c32fd0392f0d8f4234e731faf8ce9',
                  'drafts/v52/membership_source_contracts_v1_2026_09_08/contracts.py',
                  '15d5f102d6207755d180ca0477d02b1e8bb41a5985fd091bded4771503e99ae4'),
}


def load_pinned(name):
    if type(name) is not str or name not in PINS:
        raise RuntimeError('E-P-001')
    commit, path, digest = PINS[name]
    failed = False
    try:
        result = subprocess.run(['git', '-C', str(ROOT), 'cat-file', 'blob', commit + ':' + path],
                                capture_output=True, check=False)
        raw = result.stdout
        failed = result.returncode != 0 or hashlib.sha256(raw).hexdigest() != digest
    except Exception:
        failed = True
    if failed:
        raise RuntimeError('E-P-002')
    mod = types.ModuleType('membership_v2_pinned_' + name)
    mod.__file__ = str(ROOT / path)
    exec(compile(raw, '<pinned-' + name + '>', 'exec'), mod.__dict__)
    return mod
