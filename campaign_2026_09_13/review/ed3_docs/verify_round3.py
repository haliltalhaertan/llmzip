#!/usr/bin/env python3
"""verify_round3.py — stdlib-only consistency checker for the round-3 additions (EDITION 3).

Run from the bundle root:  python3 verify_round3.py
Expected: ROUND-3 ALL CHECKS PASS (exit 0). No network; read-only.
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
R3 = ROOT / 'pilots/axis_attack_2026-09-12/round3'
ok = True

def check(name, cond, detail=''):
    global ok
    if not cond:
        ok = False
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ''))

def verify_manifest(mf):
    bad, n = [], 0
    for line in mf.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ' *' in line:
            h, path = line.split(' *', 1)
        else:
            h, path = line.split('  ', 1)
        p = ROOT / path.strip()
        n += 1
        if not p.exists():
            bad.append(f'missing:{path.strip()}')
        elif hashlib.sha256(p.read_bytes()).hexdigest() != h.strip():
            bad.append(f'mismatch:{path.strip()}')
    return n, bad

# ---- 1. manifests ----
n, bad = verify_manifest(R3 / 'HASHES_ROUND3_BUNDLE.txt')
check('round3 bundle manifest', not bad, f'{n} entries, problems={bad[:5]}')
for mf in ['pilots/axis_attack_2026-09-12/HASHES_AXIS_PILOT.txt',
           'pilots/axis_attack_2026-09-12/round2/HASHES_AXIS_PILOT_R2.txt']:
    p = ROOT / mf
    if p.exists():
        n, bad = verify_manifest(p)
        check(f'manifest {mf}', not bad, f'{n} entries, problems={bad[:3]}')

# ---- 2. LME (Deney 1) details consistency ----
d = json.loads((R3 / 'deney1_lme_details.json').read_text(encoding='utf-8'))
g = d['gate1_native']
check('LME native gate max_abs_diff', abs(g['max_abs_diff'] - 1.1102230246251565e-16) <= 1e-30, repr(g['max_abs_diff']))
check('LME native mean', abs(g['mean_all'] - 0.5419751773049645) <= 1e-15, repr(g['mean_all']))
gaps, allok = [], True
for sp in d['splits']:
    a, seeds = sp['arms'], sp['random_seeds']
    if seeds != [91000 + 10 * sp['s'] + j for j in range(10)]:
        allok = False
        print(f"  seed-list mismatch split {sp['s']}")
    rmax = max(a[f'RANDOM64_s{sd}']['test_FR'] for sd in seeds)
    gap = (sp['run']['drop64'] - rmax) * 100.0
    if abs(gap - sp['run']['gap64_vs_best_pp']) > 1e-9:
        allok = False
    gaps.append(gap)
    pq = sp.get('per_q_test', {}).get('drop64')
    if pq and abs(sum(pq) / len(pq) - sp['run']['drop64']) > 1e-12:
        allok = False
check('LME per-split gap recompute + seed formulas (+per_q means if present)', allok,
      f'mean_gap={sum(gaps)/len(gaps):.6f}pp')
check('LME summary mean gap', abs(sum(gaps) / len(gaps) - d['summary']['drop64_gap_vs_best_pp']['mean']) < 1e-9)
check('LME wins = 2/10', d['summary']['drop64_gap_vs_best_pp']['wins'] == '2/10')
allok = True
for sp in d['splits']:
    for k in (32, 48, 64):
        cols = sp['arms'][f'SPREAD{k}']['cols']
        if len(cols) != k or len(set(cols)) != k or any(c < 0 or c > 95 for c in cols):
            allok = False
check('LME SPREAD eff_k == k, unique, in-range', allok)
check('KILL trigger 1: LME mean-vs-best < +1.0pp', d['summary']['drop64_gap_vs_best_pp']['mean'] < 1.0,
      f"{d['summary']['drop64_gap_vs_best_pp']['mean']:.4f}")
check('KILL trigger 2: LME wins < 7/10', d['summary']['drop64_gap_vs_best_pp']['wins'] == '2/10')

# ---- 3. LoCoMo (Deney 1 mirror) details consistency ----
d2 = json.loads((R3 / 'deney1_loco_details.json').read_text(encoding='utf-8'))
check('LOCO native recomputed == anchor', d2['native_recomputed'] == d2['native_anchor'], repr(d2['native_recomputed']))
check('LOCO n_test == 767 all splits', all(sp['run']['n_test'] == 767 for sp in d2['splits']))
allok = True
for sp in d2['splits']:
    a, seeds = sp['arms'], sp['random_seeds']
    rmax = max(a[f'RANDOM64_s{sd}']['test_FR'] for sd in seeds)
    if abs((sp['run']['drop64'] - rmax) * 100.0 - sp['run']['gap64_vs_best_pp']) > 1e-9:
        allok = False
check('LOCO per-split gap recompute', allok)
check('LOCO summary mean == -0.14953631584987523',
      abs(d2['summary']['drop64_gap_vs_best_pp']['mean'] - (-0.14953631584987523)) < 1e-9)
check('KILL trigger 3: LOCO mean-vs-best <= 0', d2['summary']['drop64_gap_vs_best_pp']['mean'] <= 0,
      f"{d2['summary']['drop64_gap_vs_best_pp']['mean']:.4f}")
check('LOCO var_worst_all True', d2['summary']['var_worst_all'] is True)

# ---- 4. errata / F3 rechecks / banners presence ----
err = (R3 / 'muse_sessions/ERRATA_ROUND3_D5.md').read_text(encoding='utf-8')
for m in ['F1', 'F2', 'F3', 'C1', 'C5', 'C9']:
    check(f'ERRATA contains {m}', m in err)
f3 = (R3 / 'muse_sessions/d5/f3_rechecks.txt').read_text(encoding='utf-8')
check('f3 rechecks: LoCoMo counts match', 'all-counts-match: True' in f3)
check('f3 rechecks: >=5 EXACT spot results', f3.count('EXACT') >= 5, f"count={f3.count('EXACT')}")
check('f3 rechecks: delta64 cols equal', 'recomputed==stored: True' in f3)
for sess, tag in [('d1v', 'F3'), ('d2', 'F1'), ('d3', 'C5'), ('d4', 'C6'), ('c2', 'F2'), ('d5', None)]:
    files = sorted((R3 / 'muse_sessions' / sess).glob('*.md'))
    check(f'session {sess}: report present', len(files) >= 1)
    if tag and files:
        t = files[0].read_text(encoding='utf-8')
        check(f'session {sess}: errata banner ({tag})', 'ORCHESTRATOR ERRATA' in t and tag in t)

# ---- 5. missing-analyses (D5 follow-ups) ----
MA = R3 / 'missing_analyses'
m1 = json.loads((MA / 'm1_kill_null' / 'missing1_kill_null.json').read_text(encoding='utf-8'))
check('m1: LME null gap mean ~ -1.62pp', abs(m1['LME']['null_mean_pp'] + 1.62) < 0.05, f"{m1['LME']['null_mean_pp']}")
check('m1: drop64 LME percentile in [40,80]', 40 <= m1['LME']['drop64']['percentile_in_null'] <= 80,
      f"{m1['LME']['drop64']['percentile_in_null']:.0f}")
check('m1: LOCO null gap mean ~ -1.20pp', abs(m1['LOCOMO']['null_mean_pp'] + 1.20) < 0.05, f"{m1['LOCOMO']['null_mean_pp']}")
m2t = (MA / 'm2_d2multi' / 'd2x_report.md').read_text(encoding='utf-8')
check('m2: report shows multi-split T mean 0.821', '0.821' in m2t)
check('m2: gold-free 0/10 above kill-bar', '0/10' in m2t)
m3t = (MA / 'm3_c2ablation' / 'c2x_report.md').read_text(encoding='utf-8')
check('m3: report states not-prereg-ready', 'not prereg-ready' in m3t.lower() or 'NOT prereg-ready' in m3t)
check('m3: formal vs-random inside-noise present', 'inside-noise' in m3t.lower() or 'inside noise' in m3t.lower())

print()
print('ROUND-3 ALL CHECKS PASS' if ok else 'ROUND-3 CHECKS FAILED')
sys.exit(0 if ok else 1)
