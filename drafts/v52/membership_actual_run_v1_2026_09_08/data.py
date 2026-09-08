"""Identity-bound LoCoMo source projection; no fitting, ranking or output writes."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import types

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT.parent / 'locomo_reproduction_tmp_20260907/preflight_source_bytes'
HISTORICAL = '692f599eedeb7e7a649443f24ff507e8c4d1c17d'
READER = '5a1dc16f37353effb68a3b582ad29284d0437101'
CONTRACT = '56e67018b61c32fd0392f0d8f4234e731faf8ce9'
EXCEPTION = '57167bcfb6c792415a9de0457fdea9435a594522'
INVENTORY = '271f63dfd4dc19c274b6d1488b68de00a86867e1'
MAPPING = '6911a03af68cb48a5090690b05acec59a67ce211'
CORPUS_HASH = '79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4'


class DataError(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise DataError(code)


def _blob(commit, path, pins, *, sha256=None, git_blob=None):
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'cat-file', 'blob', commit + ':' + path],
                                  stderr=subprocess.DEVNULL)
    digest = hashlib.sha256(raw).hexdigest()
    oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(sha256 is not None or git_blob is not None, 'E-D-001')
    need(sha256 is None or digest == sha256, 'E-D-002')
    need(git_blob is None or oid == git_blob, 'E-D-002')
    pins.append(dict(commit=commit, path=path, sha256=digest, git_blob=oid, bytes=len(raw)))
    return raw


def _module(commit, path, digest, pins):
    raw = _blob(commit, path, pins, sha256=digest)
    module = types.ModuleType('verified_source_helper')
    exec(compile(raw, '<verified-source-helper>', 'exec'), module.__dict__)
    return module


def _historical_text(pins):
    raw = _blob(HISTORICAL, 'research/v52/locomo_sign_mechanism_replication.py', pins,
                git_blob='6700454915176854a55b0b5cf6ffe922a22e35f2')
    names = {'message_text', 'raw_item_to_conv', 'norm_evidence'}
    tree = ast.parse(raw)
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    need(len(selected) == len(names), 'E-D-003')
    namespace = {'re': re}
    # Exact function ASTs, no historical imports, top-level execution or model code.
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<verified-historical-text>', 'exec'), namespace)
    return namespace['raw_item_to_conv']


def _load_locomo():
    pins = []
    reader = _module(READER, 'drafts/v52/membership_correction_reader_v1_2026_09_08/reader.py',
                     '2e903af52b12e9ba03886320d4721f36b02d95b486d64def1b691c4e9ef5cb12', pins)
    contract = _module(CONTRACT, 'drafts/v52/membership_source_contracts_v1_2026_09_08/contracts.py',
                       '15d5f102d6207755d180ca0477d02b1e8bb41a5985fd091bded4771503e99ae4', pins)
    exception = _module(EXCEPTION, 'drafts/v52/membership_gold_exception_v1_2026_09_08/exception.py',
                        '036611628238c9a36cde1e64359c09828ddcfd270e9d151538f994911d3e4e3f', pins)
    expected = json.loads(_blob(INVENTORY,
        'drafts/v52/membership_source_identity_v1_2026_09_08/EXPECTED_CORRECTION_IDENTITIES.json', pins,
        git_blob='b171712225c524c80387bbcd6579c04c531e85b0'))
    mapping = json.loads(_blob(MAPPING,
        'drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json', pins,
        sha256='66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671'))
    to_conv = _historical_text(pins)
    rows = expected['files']
    need(len(rows) == 10, 'E-D-004')
    payloads = {row['file']: (SOURCE / 'audit' / row['file']).read_bytes() for row in rows}
    raw = (SOURCE / 'locomo10.json').read_bytes()
    need(len(raw) == 2805274 and hashlib.sha256(raw).hexdigest() == CORPUS_HASH, 'E-D-005')
    # Reader checks every correction identity before parsing any correction.
    corrections = reader.parse_verified(payloads, rows)
    corpus = reader._parse_json(raw)
    clusters = dict(mapping['expected_question_to_cluster'])
    ids = list(clusters)
    need(type(corpus) is list and len(corpus) == 10 and len(ids) == 1535, 'E-D-006')
    need(mapping['source_sha256'] == CORPUS_HASH, 'E-D-007')
    archives, raw_gold, row_maps = [], {}, {}
    for ordinal, item in enumerate(corpus):
        # Empty QA projection prevents the historical helper from accessing answers.
        conv = to_conv({'conversation': item['conversation'], 'qa': []}, ordinal)
        refs = [line['dia_id'] for line in conv['lines']]
        need(bool(refs) and len(refs) == len(set(refs)), 'E-D-008')
        positions = dict(zip(refs, range(len(refs))))
        cluster = 'locomo_conv_' + str(ordinal)
        qids = [qid for qid in ids if clusters[qid] == cluster]
        need(bool(qids), 'E-D-009')
        queries = []
        for qid in qids:
            match = re.fullmatch(r'locomo_(\d+)_qa(\d+)', qid)
            need(match is not None and int(match[1]) == ordinal, 'E-D-010')
            position = int(match[2])
            question = item['qa'][position]
            need(str(question.get('question_id') or qid) == qid, 'E-D-011')
            query = str(question.get('question', ''))
            need(bool(query.strip()), 'E-D-012')
            queries.append(query)
            raw_gold[qid] = reader._evidence(question.get('evidence'))
            row_maps[qid] = positions
        archives.append(dict(ordinal=ordinal, units=[line['text'] for line in conv['lines']],
                             question_ids=qids, query_texts=queries))
    need(set(raw_gold) == set(ids) and len(raw_gold) == 1535, 'E-D-013')
    resolved = exception.resolve_with_exception(contract, ids, raw_gold, corrections, row_maps)
    for archive in archives:
        archive['gold_sets'] = [list(resolved[qid]['gold_rows']) for qid in archive['question_ids']]
    provenance = dict(benchmark='LoCoMo', source_path=str(SOURCE / 'locomo10.json'),
        source_bytes=len(raw), source_sha256=CORPUS_HASH, correction_identities=rows,
        bound_code_and_metadata=pins, question_count=len(ids), archive_count=len(archives),
        corrected_cohort_questions=sum(row['correction_applied'] for row in resolved.values()),
        gold_exception=dict(question_id=exception.QID,
                            policy='USER_APPROVED_HISTORICAL_SIX_REFERENCES',
                            original_declared=7, original_unresolved=1, effective_references=6),
        representation_fit=False, retrieval=False, scores=False)
    return archives, ids, clusters, provenance


def load_locomo():
    """Return archives, bound ID order, qid-to-cluster map, and identity provenance."""
    failure = None
    try:
        result = _load_locomo()
    except DataError as exc:
        failure = str(exc)
    except Exception:
        failure = 'E-D-014'
    if failure is not None:
        raise DataError(failure)
    return result
