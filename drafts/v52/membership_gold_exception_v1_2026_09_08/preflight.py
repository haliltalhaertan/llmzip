"""Authorized source-only preflight. No representation, ranking or metrics."""
import hashlib
import json
from pathlib import Path
import subprocess
import types
from exception import resolve_with_exception

ROOT = Path(__file__).resolve().parents[3]


def blob(commit, path, digest=None):
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'cat-file', 'blob', commit + ':' + path])
    if digest is not None and hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('PIN_MISMATCH')
    return raw


def module(commit, path, digest):
    raw = blob(commit, path, digest)
    result = types.ModuleType('verified_module')
    exec(compile(raw, '<verified-module>', 'exec'), result.__dict__)
    return result


def main():
    report = dict(status='SOURCE_PREFLIGHT_STARTED', actual_experiment_started=False,
                  representation_fit=False, retrieval=False, scores=False)
    ns = 'drafts/v52/membership_correction_reader_v1_2026_09_08/'
    inventory = json.loads(blob('5a1dc16f37353effb68a3b582ad29284d0437101', ns + 'PAYLOAD_HASHES.json'))
    pin = next(p['sha256'] for p in inventory['payloads'] if p['path'] == 'reader.py')
    reader = module('5a1dc16f37353effb68a3b582ad29284d0437101', ns + 'reader.py', pin)
    expected = json.loads(blob('271f63dfd4dc19c274b6d1488b68de00a86867e1',
        'drafts/v52/membership_source_identity_v1_2026_09_08/EXPECTED_CORRECTION_IDENTITIES.json'))
    source = ROOT.parent / 'locomo_reproduction_tmp_20260907/preflight_source_bytes'
    payloads = {r['file']: (source / 'audit' / r['file']).read_bytes() for r in expected['files']}
    report['correction_files_identity_matched'] = sum(
        len(payloads[r['file']]) == r['bytes'] and hashlib.sha256(payloads[r['file']]).hexdigest() == r['sha256']
        for r in expected['files'])
    try:
        corrections = reader.parse_verified(payloads, expected['files'])
    except reader.ReaderError as exc:
        report.update(status='STOPPED_CORRECTION_READER', refusal_code=str(exc))
        print(json.dumps(report, sort_keys=True, indent=2))
        return 2
    report['correction_records'] = len(corrections)
    raw = (source / 'locomo10.json').read_bytes()
    if len(raw) != 2805274 or hashlib.sha256(raw).hexdigest() != '79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4':
        raise ValueError('SOURCE_MISMATCH')
    report['corpus_identity_matched'] = True
    corpus = reader._parse_json(raw)
    mapping = json.loads(blob('6911a03af68cb48a5090690b05acec59a67ce211',
        'drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json',
        '66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671'))
    ids = list(mapping['expected_question_to_cluster'])
    if len(ids) != 1535 or len(corpus) != 10:
        raise ValueError('COHORT_COUNT_MISMATCH')
    contract = module('56e67018b61c32fd0392f0d8f4234e731faf8ce9',
        'drafts/v52/membership_source_contracts_v1_2026_09_08/contracts.py',
        '15d5f102d6207755d180ca0477d02b1e8bb41a5985fd091bded4771503e99ae4')
    raw_gold, maps = {}, {}
    for qid in ids:
        prefix, question = qid.split('_qa')
        index = int(prefix.split('_')[1])
        if mapping['expected_question_to_cluster'][qid] != 'locomo_conv_' + str(index):
            raise ValueError('MAPPING_MISMATCH')
        row = corpus[index]['qa'][int(question)]
        raw_gold[qid] = reader._evidence(row.get('evidence'))
        conversation = corpus[index]['conversation']
        keys = sorted((k for k in conversation if k.startswith('session_') and not k.endswith('_date_time')),
                      key=lambda k: int(k.split('_')[1]))
        refs = [str(m.get('dia_id', '')) for k in keys for m in (conversation[k] or []) if m.get('dia_id')]
        if len(set(refs)) != len(refs):
            raise ValueError('DUPLICATE_MEMORY_ID')
        maps[qid] = dict(zip(refs, range(len(refs))))
    try:
        resolved = resolve_with_exception(contract, ids, raw_gold, corrections, maps)
    except contract.ContractError as exc:
        report.update(status='STOPPED_GOLD_CONTRACT', refusal_code=str(exc), cohort_questions=len(ids))
        problems = []
        for qid in ids:
            corrected = 'correct_evidence' in corrections.get(qid, {})
            refs = contract.evidence(corrections[qid]['correct_evidence'] if corrected else raw_gold[qid])
            missing = [ref for ref in refs if ref not in maps[qid]]
            if missing or not refs:
                problems.append(dict(question_id=qid, correction_applied=corrected,
                    declared_reference_count=len(refs), unresolved_reference_count=len(missing),
                    resolved_reference_count=len(refs)-len(missing)))
        report['gold_failures'] = problems
        report['gold_failure_questions'] = len(problems)
        print(json.dumps(report, sort_keys=True, indent=2))
        return 3
    report.update(status='SOURCE_GOLD_PREFLIGHT_PASS_WITH_APPROVED_EXCEPTION', cohort_questions=len(resolved),
                  exception_question='locomo_4_qa18', original_declared_references=7,
                  original_unresolved_references=1, effective_gold_references=6,
                  corrected_cohort_questions=sum(r['correction_applied'] for r in resolved.values()))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    failure = False
    try:
        status = main()
    except Exception:
        failure = True
    if failure:
        print('{"status":"STOPPED_INTERNAL_PREFLIGHT_ERROR","actual_experiment_started":false}')
        raise SystemExit(4)
    raise SystemExit(status)
