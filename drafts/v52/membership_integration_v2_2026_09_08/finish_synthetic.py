"""Synthetic integration harness, NOT a production finalizer or authorization gate.

Uses the byte-pinned closed core's paired matrices/aggregate/bootstrap. Fixed
accepted seed values and replicate count; no categorical interpretation. Returned
objects contain synthetic scores and IDs. Arbitrary callers can supply real data:
the label is a scope declaration, not a technical detector of data origin.
"""
import hashlib
import json
from pathlib import Path

import pipeline as p
from pinned import PINS

SEEDS = {('LoCoMo', 'question'): 52001107, ('LoCoMo', 'cluster'): 52001207,
         ('LongMemEval', 'question'): 52002107}
REPLICATES = 10000


def compute_synthetic(ingested, anchors, **kwargs):
    """Compute full in-memory pipeline, then all defined resampling schemes.

No reading or mutation of accepted mapping objects, seed files or corpus artifacts.
Synthetic caller anchors are deliberately not certified as historical anchors.
"""
    computed = p.assemble_in_memory(ingested, anchors, **kwargs)
    ids = list(ingested['cohort_ids'])
    benchmark = ingested['benchmark']
    clusters = None
    if benchmark == 'LoCoMo':
        mapping = {}
        for label, group in ingested['conversations'].items():
            p.require(type(label) is str and bool(label.strip()) and label.strip() == label
                      and label.casefold() not in {'nan', 'none', 'null', 'na', 'n/a', 'nil', '-', '--', '?'},
                      'E-F-001: cluster label')
            for qid in group['questions']:
                mapping[qid] = label
        clusters = [mapping[q] for q in ids]
        p.require(len(set(clusters)) >= 2, 'E-F-002: cluster scheme needs multiple groups')
    g, gs = p.core.paired_matrices(computed['records'], ids)
    estimates = p.core.aggregate(g, gs)
    uncertainty = {'question': p.core.question_bootstrap(g, gs, SEEDS[(benchmark, 'question')], REPLICATES)}
    if clusters is not None:
        uncertainty['cluster'] = p.core.cluster_bootstrap(g, gs, clusters, SEEDS[(benchmark, 'cluster')], REPLICATES)
    identity = {name: {'commit': pin[0], 'path': pin[1], 'sha256': pin[2]} for name, pin in PINS.items()}
    return {'status': 'SYNTHETIC_ONLY_NOT_EXECUTION_READY', 'benchmark': benchmark,
            'question_ids': ids, 'n_questions': len(ids), 'estimates': estimates,
            'uncertainty': uncertainty, **computed,
            'provenance': {'pinned_sources': identity,
                           'bootstrap': {scheme: {'seed': SEEDS[(benchmark, scheme)], 'replicates': REPLICATES}
                                         for scheme in uncertainty},
                           'raw_source_identity_verified': False,
                           'historical_anchor_identity_verified': False},
            'longmemeval_limit': ('No conversation-cluster bootstrap. Single-component structure inherited '
                                 'from Task 3A.1, not recomputed here.') if benchmark == 'LongMemEval' else None}


def write_synthetic_bundle(destination, result):
    """Create-only directory; result first, checksum receipt last. No overwrite/retry repair.

A failure may leave a partial directory, which is retained and cannot be reused.
The checksum receipt is NOT an experiment seal. Serializes before creating output.
"""
    p.require(type(result) is dict and result.get('status') == 'SYNTHETIC_ONLY_NOT_EXECUTION_READY',
              'E-F-003: synthetic result required')
    p.require(type(result.get('question_ids')) is list and bool(result['question_ids']), 'E-F-004: empty result')
    p.validate_records(result.get('records'), result['question_ids'])
    failed = False
    try:
        raw = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    except Exception:
        failed = True
    if failed:
        raise p.PipelineError('E-F-005: serialization')
    failed = False
    try:
        folder = Path(destination)
        folder.mkdir(parents=False, exist_ok=False)
        with (folder / 'synthetic_result.json').open('xb') as stream:
            stream.write(raw)
        receipt = {'file': 'synthetic_result.json', 'sha256': hashlib.sha256(raw).hexdigest(),
                   'bytes': len(raw), 'status': 'SYNTHETIC_RECEIPT_NOT_SEAL'}
        with (folder / 'SYNTHETIC_RECEIPT.json').open('xb') as stream:
            stream.write((json.dumps(receipt, sort_keys=True) + '\n').encode('utf-8'))
    except Exception:
        failed = True
    if failed:
        raise p.PipelineError('E-F-006: output creation failed')
    return receipt


def run_on_real_corpus(*args, **kwargs):
    raise p.PipelineError('E-F-007: real execution not authorized')
