"""Independent read-only identity audit; writes only this audit namespace. No test execution."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

AUDIT = Path(__file__).resolve().parent
REPO = AUDIT.parent
CANDIDATE = '24d3351f068f6982148c14a9e3338c29a2769449'
PREFIX = 'drafts/v52/membership_g3_remediation_2026_09_11/'
NS = REPO / PREFIX
SCRATCH = AUDIT / 'v52/membership_g3_remediation_2026_09_11'
BASE = '4f2429b257546d6899f3ed48f605cd18210aeae0'

def git(*args, cwd=REPO):
    return subprocess.check_output(['git', '-C', str(cwd), *args])

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def blob(ref, path):
    return git('cat-file', 'blob', ref + ':' + path)

def write(name, value):
    (AUDIT / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8', newline='\n')

checks = []
def check(name, condition, **details):
    checks.append(dict(name=name, passed=bool(condition), **details))

check('candidate HEAD', git('rev-parse', 'HEAD').decode().strip() == CANDIDATE)
check('local LF configuration', git('config', '--local', 'core.autocrlf').strip() == b'false')
check('candidate remote at clone', git('rev-parse', 'origin/codex/g3-remediation-delivery-2026-09-12').decode().strip() == CANDIDATE)
main = git('rev-parse', 'origin/main').decode().strip()
changes = git('diff', '--name-status', BASE, CANDIDATE).decode().splitlines()
check('candidate additive namespace only', all(x.startswith('A\t' + PREFIX) for x in changes), file_count=len(changes))
manifest_raw = blob(CANDIDATE, PREFIX + 'FILE_HASHES.json')
manifest = json.loads(manifest_raw)
actual = git('ls-tree', '-r', '--name-only', CANDIDATE, '--', PREFIX).decode().splitlines()
check('manifest exact coverage', [PREFIX + x['path'] for x in manifest['files']] == [x for x in actual if x != PREFIX + 'FILE_HASHES.json'])
inventory = []
for item in manifest['files']:
    path = PREFIX + item['path']
    raw = blob(CANDIDATE, path)
    checked = (REPO / path).read_bytes()
    passed = sha(raw) == item['sha256'] and len(raw) == item['bytes'] and checked == raw
    check('raw manifest and checkout ' + item['path'], passed)
    inventory.append(dict(path=path, bytes=len(raw), sha256=sha(raw)))
write('CANDIDATE_FILE_IDENTITIES.json', dict(candidate=CANDIDATE, manifest_sha256=sha(manifest_raw), files=inventory))

docs = json.loads((NS / 'provenance/final/SOURCE_DOCUMENTS.json').read_bytes())['documents']
references = AUDIT / 'authority'
references.mkdir(exist_ok=True)
for doc in docs:
    raw = blob(doc['commit'], doc['path'])
    check('authority raw ' + doc['label'], sha(raw) == doc['sha256'] == doc['expected_sha256'])
    (references / (doc['label'] + '.md')).write_bytes(raw)
write('AUTHORITY_IDENTITIES.json', docs)
recovered = json.loads((NS / 'RECOVERY_INPUT.json').read_bytes())
for item in recovered['files']:
    raw = (NS / 'provenance/pre_edit' / item['path']).read_bytes()
    check('recovery bytes ' + item['path'], len(raw) == item['bytes'] and sha(raw) == item['sha256'])
for item in json.loads((NS / 'provenance/final/MATERIALIZED.json').read_bytes()):
    raw = blob(item['commit'], item['source'])
    checked = (NS / item['destination'].replace('\\', '/')).read_bytes()
    check('inherited raw source ' + item['destination'], raw == checked and sha(raw) == item['sha256'] and len(raw) == item['bytes'])
for first, second in [('dcb568d0a6c33154c1568500325ad457b4d6f455', '07ec929243068914676a0f30efd10c9f294c7e71'), ('07ec929243068914676a0f30efd10c9f294c7e71', 'ed4e22c520b7dc0ae2f43f915e0c621070c72a87')]:
    check('source ancestry ' + first + ' -> ' + second, subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', first, second]).returncode == 0)

receipt = json.loads((SCRATCH / 'evidence/independent_once/RESULTS.json').read_bytes())
check('suite exact observed count and success', receipt['test_methods_observed'] == 53 and receipt['status'] == 'PASS' and receipt['failures'] == receipt['errors'] == receipt['skips'] == 0)
source_records = []
for path, digest in receipt['source_sha256'].items():
    raw = blob(CANDIDATE, PREFIX + path)
    check('executed bytes bound to commit ' + path, sha(raw) == digest and raw == (SCRATCH / path).read_bytes() == (NS / path).read_bytes())
    source_records.append(dict(path=path, sha256=digest, bytes=len(raw)))
write('EXECUTED_SOURCE_BINDING.json', dict(candidate=CANDIDATE, relocation='Byte-identical root Python and authoritative Python files copied into audit/v52/package; same directory depth, same pinned interpreter, unchanged launcher and assertions.', sources=source_records))
out = AUDIT / 'suite_once'
out.mkdir(exist_ok=False)
for name in ('RESULTS.json', 'COMMAND.json', 'stdout.txt', 'stderr.txt'):
    (out / name).write_bytes((SCRATCH / 'evidence/independent_once' / name).read_bytes())

# Observe the named original source files, index and Git status only. Never enumerate data files.
original = REPO.parent / 'llmzip'
observed = dict(scope='Read-only current original source/index/status observation; not a reconstruction of past filesystem actions.')
observed['head'] = git('rev-parse', 'HEAD', cwd=original).decode().strip()
observed['status'] = git('status', '--short', '--untracked-files=normal', cwd=original).decode()
index = git('rev-parse', '--git-path', 'index', cwd=original).decode().strip()
index_path = Path(index) if Path(index).is_absolute() else original / index
observed['index_sha256'] = sha(index_path.read_bytes())
observed['source_files'] = []
for item in recovered['files']:
    raw = (original / PREFIX / item['path']).read_bytes()
    observed['source_files'].append(dict(path=item['path'], sha256=sha(raw), matches_recovery=sha(raw) == item['sha256']))
observed['head_matches_receipt'] = observed['head'] == recovered['source_head']
observed['index_matches_receipt'] = observed['index_sha256'] == recovered['index_sha256']
observed['status_matches_receipt'] = observed['status'] == recovered['source_status']
write('ORIGINAL_SOURCE_OBSERVATION.json', observed)
write('IDENTITY_RESULTS.json', dict(candidate=CANDIDATE, base=BASE, origin_main_at_audit=main, check_count=len(checks), failed=sum(not x['passed'] for x in checks), checks=checks))
print(json.dumps(dict(checks=len(checks), failed=sum(not x['passed'] for x in checks), suite_methods=receipt['test_methods_observed'], subtests=receipt['subtests_observed'], original_head_match=observed['head_matches_receipt'], original_index_match=observed['index_matches_receipt'], original_status_match=observed['status_matches_receipt'], original_files_match=all(x['matches_recovery'] for x in observed['source_files']))))
