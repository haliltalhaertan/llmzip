"""Create-only LoCoMo membership execution; no retries or control relaxation."""
import argparse
import ast
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import numpy as np
import pipeline as p
import data

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPECTED = {'cloudpickle': '3.1.2', 'joblib': '1.6.0', 'numpy': '2.3.5',
            'pandas': '2.2.3', 'python-dateutil': '2.9.0.post0', 'pytz': '2026.3.post1',
            'scikit-learn': '1.8.0', 'scipy': '1.17.0', 'six': '1.17.0',
            'threadpoolctl': '3.6.0', 'tzdata': '2026.3'}
THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')


def write_json(path, obj):
    raw = (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    with Path(path).open('xb') as stream:
        stream.write(raw)
    return hashlib.sha256(raw).hexdigest()


def native_reference():
    source = data._blob(data.HISTORICAL, 'research/v52/locomo_coordinate_scale.py', [],
        sha256='df1bdded0a196ab62fc43363b5b90edba791a08ca6a3ebdb5a7c7a4d22a716a4')
    values = [ast.literal_eval(n.value) for n in ast.parse(source).body
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
              and t.id == 'FROZEN_NATIVE_R3' for t in n.targets)]
    p.require(len(values) == 1 and type(values[0]) is float, 'E-RUN-001')
    return values[0]


def aggregate_native_gate(records, ids, expected):
    p.validate_records(records, ids)
    means = []
    for seed in p.core.ROTATION_SEEDS:
        values = {r['question_id']: r['fractional_R3'] for r in records
                  if r['arm'] == 'NATIVE' and r['rotation_seed'] == seed}
        p.require(set(values) == set(ids), 'E-RUN-002')
        means.append(float(np.mean([values[q] for q in ids])))
    p.require(all(abs(value - expected) <= p.core.TOL for value in means), 'E-RUN-003')
    return dict(historical_reference=expected, per_seed_means=means,
                tolerance=p.core.TOL, passed=True)


def check_environment():
    p.require(sys.version_info[:3] == (3, 13, 15), 'E-RUN-004')
    packages = {name: importlib.metadata.version(name) for name in EXPECTED}
    p.require(packages == EXPECTED, 'E-RUN-005')
    p.require(os.environ.get('PYTHONHASHSEED') == '0' and
              all(os.environ.get(name) == '1' for name in THREADS), 'E-RUN-006')
    return dict(python=sys.version, packages=packages,
                thread_environment={name: os.environ[name] for name in THREADS},
                PYTHONHASHSEED='0', thread_introspection_claim=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--binding', required=True)
    args = parser.parse_args()
    environment = check_environment()
    binding = json.loads(Path(args.binding).read_bytes())
    p.require(binding['status'] == 'APPROVED_FOR_ONE_LOCOMO_EXECUTION', 'E-RUN-007')
    for row in binding['payloads']:
        raw = (HERE / row['path']).read_bytes()
        p.require(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'E-RUN-008')
    output = Path(args.output)
    output.mkdir(parents=False, exist_ok=False)
    write_json(output / 'PRE_RUN_BINDING.json', dict(binding=binding, environment=environment,
               head=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()))
    stage, completed = 'SOURCE_LOAD', 0
    failure = None
    try:
        archives, ids, clusters, provenance = data.load_locomo()
        p.require(len(archives) == 10 and len(ids) == 1535 and len(set(clusters.values())) == 10, 'E-RUN-009')
        expected = native_reference()
        write_json(output / 'SOURCE_IDENTITY.json', provenance)
        records, diagnostics = [], []
        started = time.monotonic()
        for archive in archives:
            stage = 'REPRESENTATION'
            print(json.dumps(dict(event='ARCHIVE_STARTED', archive=archive['ordinal'], completed=completed)), flush=True)
            rep = p.Representation(archive['units'])
            stage = 'SCORING_AND_CONTROLS'
            rows, diag = p.score_archive(rep, archive['query_texts'], archive['gold_sets'],
                                        archive['question_ids'], archive['ordinal'])
            write_json(output / ('archive_%02d.json' % archive['ordinal']),
                       dict(records=rows, diagnostics=diag, archive=archive['ordinal']))
            records.extend(rows)
            diagnostics.append(dict(archive=archive['ordinal'], **diag))
            completed += 1
            print(json.dumps(dict(event='ARCHIVE_COMPLETED', completed=completed,
                                 elapsed_seconds=round(time.monotonic()-started, 2))), flush=True)
        stage = 'NATIVE_AGGREGATE_GATE'
        gate = aggregate_native_gate(records, ids, expected)
        stage = 'STATISTICS'
        g, gs = p.core.paired_matrices(records, ids)
        summary = dict(status='COMPUTED_PENDING_POSTRUN_AUDIT', benchmark='LoCoMo', n_questions=len(ids),
                       n_records=len(records), n_archives=completed, native_gate=gate,
                       estimates=p.core.aggregate(g, gs), diagnostics=diagnostics,
                       uncertainty=dict(question=p.core.question_bootstrap(g, gs, 52001107, 10000),
                           cluster=p.core.cluster_bootstrap(g, gs, [clusters[q] for q in ids], 52001207, 10000)),
                       other_benchmark_status='LongMemEval_NOT_RUN_BY_THIS_DRIVER',
                       elapsed_seconds=time.monotonic()-started)
        write_json(output / 'RESULT.json', summary)
        manifest = [dict(path=f.name, bytes=f.stat().st_size,
                        sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(output.iterdir()) if f.is_file()]
        write_json(output / 'OUTPUT_HASHES.json', dict(status='COMPUTED_PENDING_POSTRUN_AUDIT', payloads=manifest))
    except Exception as exc:
        text = str(exc)
        code = text.split(':', 1)[0]
        failure = code if re.fullmatch(r'E-[A-Z0-9]+-\d+', code) else 'E-RUN-010'
    if failure is not None:
        write_json(output / 'STOPPED.json', dict(status='INVALID_VERDICT_WITHHELD', stage=stage,
                   code=failure, completed_archives=completed, auto_retry=False))
        print(json.dumps(dict(status='INVALID_VERDICT_WITHHELD', stage=stage, code=failure)), flush=True)
        return 2
    print(json.dumps(dict(status='COMPUTED_PENDING_POSTRUN_AUDIT', archives=completed)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
