"""Extract expected identities from pinned code, never read correction data."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

COMMIT = '692f599eedeb7e7a649443f24ff507e8c4d1c17d'
SOURCE = 'research/v52/locomo_sign_mechanism_replication.py'
SOURCE_HASH = 'a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b'
FULL_HASH = '90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06'
SUBSET_HASH = '7df45317f0cb3029fc8cb008d8480ee5c8e61ac01dd0d77bc1cfcd6a3eb7224a'


def canonical(rows):
    return json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('utf-8')


def expected_inventory():
    root = Path(__file__).resolve().parents[3]
    raw = subprocess.check_output(['git', '-C', str(root), 'cat-file', 'blob', COMMIT + ':' + SOURCE])
    if hashlib.sha256(raw).hexdigest() != SOURCE_HASH:
        raise RuntimeError('SOURCE_IDENTITY_MISMATCH')
    assignments = {n.targets[0].id: n.value for n in ast.parse(raw).body
                   if isinstance(n, ast.Assign) and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name)}
    mapping = ast.literal_eval(assignments['AUDIT_FILE_HASHES'])
    rows = [dict(file=k, bytes=v[0], sha256=v[1]) for k, v in sorted(mapping.items())]
    if len(rows) != 20 or hashlib.sha256(canonical(rows)).hexdigest() != FULL_HASH:
        raise RuntimeError('FULL_INVENTORY_MISMATCH')
    if ast.literal_eval(assignments['AUDIT_MANIFEST_SHA256']) != FULL_HASH:
        raise RuntimeError('DECLARED_INVENTORY_MISMATCH')
    subset = [r for r in rows if r['file'].startswith('errors_conv_')]
    if [r['file'] for r in subset] != [f'errors_conv_{i}.json' for i in range(10)]:
        raise RuntimeError('SUBSET_MEMBERSHIP_MISMATCH')
    if hashlib.sha256(canonical(subset)).hexdigest() != SUBSET_HASH:
        raise RuntimeError('SUBSET_INVENTORY_MISMATCH')
    return dict(status='EXPECTED_IDENTITIES_ONLY_ACTUAL_FILES_NOT_READ',
                producer_commit=COMMIT, producer_path=SOURCE, producer_sha256=SOURCE_HASH,
                full20_inventory_sha256=FULL_HASH, subset10_inventory_sha256=SUBSET_HASH,
                canonicalization='UTF-8 compact sorted-key JSON; rows sorted by file', files=subset)


if __name__ == '__main__':
    print(json.dumps(expected_inventory(), sort_keys=True, indent=2))
