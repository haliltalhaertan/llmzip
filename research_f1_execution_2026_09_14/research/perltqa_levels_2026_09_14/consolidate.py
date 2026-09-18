#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] consolidate all evidence into evidence/results.json"""
import json
from pathlib import Path
E = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels/evidence')
out = {'labels': ['LOCAL EXPLORATORY PILOT', 'NOT PREREGISTERED', 'NOT FOR CITATION', 'DISCLOSE-BEFORE-USE']}
for nm, f in [('control_gate', 'control.json'), ('cross_check', 'results.json'),
              ('levels_summary', 'levels_summary.json'), ('levels_xbench', 'step6.json'),
              ('slope_vs_level', 'step7.json'), ('locomo', 'locomo.json')]:
    p = E / f
    if p.exists():
        try: out[nm] = json.load(open(p))
        except Exception as e: out[nm] = f'unreadable: {e}'
json.dump(out, open(E / 'results.json', 'w'), indent=2, default=float)
print('keys:', sorted(out.keys()))
print('bytes:', (E / 'results.json').stat().st_size)
for f in sorted(E.iterdir()): print(f'  {f.name:32s} {f.stat().st_size:>10d}')
