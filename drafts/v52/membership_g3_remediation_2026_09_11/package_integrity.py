"""Inventory exact delivery bytes; this hash manifest is not a seal or acceptance."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PREFIX = HERE.relative_to(REPO).as_posix() + '/'
MANIFEST = PREFIX + 'FILE_HASHES.json'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def digest(b):
    return hashlib.sha256(b).hexdigest()


def paths(ref=None):
    raw = (git('ls-tree', '-rz', '--name-only', ref, '--', PREFIX) if ref else
           git('ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', PREFIX))
    found = sorted(set(p.decode('utf-8') for p in raw.split(b'\0') if p))
    for p in found:
        if not p.startswith(PREFIX) or '..' in PurePosixPath(p).parts:
            raise RuntimeError('manifest path outside namespace')
    return [p for p in found if p != MANIFEST]


def read(path, ref=None):
    return git('cat-file', 'blob', ref + ':' + path) if ref else (REPO / path).read_bytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--ref')
    args = parser.parse_args()
    if args.write and args.ref:
        parser.error('--write and --ref are exclusive')
    if args.write:
        entries = []
        for p in paths():
            b = read(p)
            entries.append({'path': p[len(PREFIX):], 'bytes': len(b), 'sha256': digest(b)})
        value = {'status': 'SCOPED_SYNTHETIC_CANDIDATE_AWAITING_INDEPENDENT_AUDIT',
                 'base_commit': '4f2429b257546d6899f3ed48f605cd18210aeae0',
                 'manifest_self_excluded': True, 'files': entries}
        (REPO / MANIFEST).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    blob = read(MANIFEST, args.ref)
    value = json.loads(blob)
    declared = [PREFIX + e['path'] for e in value['files']]
    if declared != paths(args.ref):
        raise RuntimeError('file inventory mismatch')
    for e in value['files']:
        b = read(PREFIX + e['path'], args.ref)
        if len(b) != e['bytes'] or digest(b) != e['sha256']:
            raise RuntimeError('byte identity mismatch: ' + e['path'])
    print(json.dumps({'status': 'PASS', 'files': len(declared), 'ref': args.ref,
                      'manifest_sha256': digest(blob)}, sort_keys=True))


if __name__ == '__main__':
    main()
