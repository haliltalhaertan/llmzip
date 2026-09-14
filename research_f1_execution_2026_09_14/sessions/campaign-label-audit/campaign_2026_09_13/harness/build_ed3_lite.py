#!/usr/bin/env python3
"""Build/refresh the ED3 LITE staging tree from the current FULL bundle (v1.1)."""
import shutil, json, hashlib
from pathlib import Path

RT = Path('C:/Users/MDP/dev/llmzip-work/review_transfer')
SRC = RT / 'EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13'
STG = RT / '_ed3_lite_stage/EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_LITE'

LITE_NOTE = """# LITE bundle note (EDITION 3, v1.1)

Excluded vs the FULL bundle: `sample_data/` (32 C-matrix pickles) and the root `muse_sessions/`
(raw review transcripts). For round 3: the per-question arrays are stripped from
`deney1_*_details.json` (per-split runs, arms, gates and summaries remain); the large session
details JSONs (d2/d1v/c2 and m3's `c2x_details.json`) are omitted — reports are included.
Manifests are pre-filtered to the files present, and recomputed over the LITE content (header
lines in those files state this).

v1.1 adds: the D5 follow-up missing analyses (m1 kill-null, m2 D2 multi-split + gold-free,
m3 c2 ablation) under `pilots/axis_attack_2026-09-12/round3/missing_analyses/`, and the updated
addendum/errata documents.

All stdlib checks pass here (`verify_round3.py`, `verify_pilot.py`, `verify_round2.py`). The
optional numpy spot-recomputation against the 32 shipped matrices requires the FULL bundle.
"""

if STG.exists():
    shutil.rmtree(STG)
STG.mkdir(parents=True)
for f in ['00_READ_ME_FIRST.md', '01_CANONICAL_STATUS.md', '01b_ROUND2_ADDENDUM.md',
          '01c_ROUND3_ADDENDUM.md', '02_INDEPENDENT_REVIEW_PROMPT.md', '03_VERIFY_COMMANDS.md',
          'REPORT.md', 'verify_pilot.py', 'verify_sample_numpy.py', 'verify_round3.py']:
    shutil.copy2(SRC / f, STG / f)
(STG / 'LITE_NOTE.md').write_text(LITE_NOTE, encoding='utf-8', newline='\n')

shutil.copytree(SRC / 'pilots', STG / 'pilots', ignore=shutil.ignore_patterns('round3'))
r3s = SRC / 'pilots/axis_attack_2026-09-12/round3'
r3d = STG / 'pilots/axis_attack_2026-09-12/round3'
r3d.mkdir(parents=True)
for f in ['DENEY1_REPORT.md', 'ROUND3_REPORT.md', 'RUN_LOG.md', 'deney1_loco_peraxis.npz']:
    shutil.copy2(r3s / f, r3d / f)
ms_s = r3s / 'muse_sessions'; ms_d = r3d / 'muse_sessions'
for sess in ['d1v', 'd2', 'd3', 'd4', 'c2', 'd5']:
    (ms_d / sess).mkdir(parents=True, exist_ok=True)
    for f in sorted((ms_s / sess).iterdir()):
        if f.suffix == '.md' or f.name in ('d3_details.json', 'd4_details.json', 'd4_lme_details.json') \
           or f.name == 'f3_rechecks.txt':
            shutil.copy2(f, ms_d / sess / f.name)
shutil.copy2(ms_s / 'ERRATA_ROUND3_D5.md', ms_d / 'ERRATA_ROUND3_D5.md')
# missing analyses (v1.1): include all; prune only the big m3 details
shutil.copytree(r3s / 'missing_analyses', r3d / 'missing_analyses')
p = r3d / 'missing_analyses/m3_c2ablation/c2x_details.json'
if p.exists():
    p.unlink()
# stripped deney1 summaries (same names, per-q arrays removed)
for name in ['deney1_lme_details.json', 'deney1_loco_details.json']:
    d = json.loads((r3s / name).read_text(encoding='utf-8'))
    for sp in d['splits']:
        sp.pop('per_q_test', None); sp.pop('per_q_train', None)
    (r3d / name).write_text(json.dumps(d), encoding='utf-8', newline='\n')
shutil.copytree(SRC / 'protocol_sources', STG / 'protocol_sources')
shutil.copytree(SRC / 'round3_sources', STG / 'round3_sources')

# manifests recomputed over LITE content (AFTER all copies)
def regen(full_manifest, out_path, comment=None):
    out = ([comment] if comment else [])
    for line in full_manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        pp = line.split(' *', 1)[1]
        f = STG / pp
        if f.exists():
            out.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()} *{pp}')
    out_path.write_text('\n'.join(out) + '\n', encoding='utf-8', newline='\n')
    return len(out) - (1 if comment else 0)

n1 = regen(r3s / 'HASHES_ROUND3_BUNDLE.txt', r3d / 'HASHES_ROUND3_BUNDLE.txt',
           comment='# LITE edition (v1.1): entries recomputed over the LITE content '
                   '(per-question arrays stripped from the two deney1_*_details.json files here; '
                   'full versions live in the FULL bundle).')
sup_out = []
for line in (SRC / 'SUPPLEMENTARY_PILOT_HASHES.txt').read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    h, pp = line.split('  ', 1)
    f = STG / pp
    if f.exists():
        sup_out.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {pp}')
(STG / 'SUPPLEMENTARY_PILOT_HASHES.txt').write_text('\n'.join(sup_out) + '\n', encoding='utf-8', newline='\n')

files = [p for p in STG.rglob('*') if p.is_file()]
print(f'LITE staged: {len(files)} files; round3-manifest {n1} entries; supplementary {len(sup_out)} entries')
print('LITE_BUILD_DONE')
