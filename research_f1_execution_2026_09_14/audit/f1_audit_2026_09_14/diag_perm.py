#!/usr/bin/env python3
"""Step-2 diagnosis: does NT=20 seeded-permutation FR@3 (frozen convention) explain the
~1e-4 gap between the exact-expectation coefficients and the contract's auditor targets?
Independent of coordinator code. Uses MY OWN seed families - I am not trying to hit a target,
I am measuring the SPREAD induced by the frozen NT=20 convention."""
import glob, json, pickle
import numpy as np
import sys
sys.path.insert(0, '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit')
from my_f1 import (avg_ranks, spearman, topbot64, competition, cos_scores, hamming,
                   load_lme, load_realtalk, load_perltqa, fr3_exact, K)

AUD = {  # contract R2_COMPETITION_RERUN_CONTRACT.md "Expected independent-audit targets"
 'LME':      (0.14168629605302735, 0.14045379360271315),
 'REALTALK': (0.09793912889111700, 0.12281952421315011),
 'PERLTQA':  (0.25416826537535475, 0.27978783415712220),
}
MINE = {
 'LME':      (0.1416251737011647, 0.14069387548880735),
 'REALTALK': (0.09793425648573494, 0.12307477776090332),
 'PERLTQA':  (0.25413844391463014, 0.27982715404990666),
}

def fr3_perm(d, gold, perms, K=3):
    gg = set(int(x) for x in np.asarray(gold).ravel())
    return float(np.mean([len(gg & set(int(t) for t in np.lexsort((p, d))[:K])) / len(gg)
                          for p in perms]))

def bench_rho_perm(rows, seedbase, NT=20):
    """Recompute the 2 coefficients using NT seeded permutations for the FR@3 tie-break,
    exactly as the frozen scorer does (lexsort with a random key), with a chosen seed family."""
    ac = {}
    def arch(C):
        k = id(C)
        if k not in ac:
            t, b, _ = topbot64(C); ac[k] = (C >= 0, t, b, {})
        return ac[k]
    dl = []; sg = []; tg = []
    for n, r in enumerate(rows):
        C = r['C']; qC = r['qC']; gold = r['gold']
        D0, tc, bc_, permcache = arch(C)
        N = C.shape[0]
        key = (seedbase, N)
        if key not in permcache:
            permcache[key] = [np.random.default_rng(seedbase + 7919 * t).random(N) for t in range(NT)]
        pr = permcache[key]
        Q0 = qC >= 0
        d_sign = hamming(D0, Q0).astype(float)
        s = cos_scores(C, qC)
        if not np.all(np.isfinite(s)): s = np.nan_to_num(s, nan=-1e18)
        fs = fr3_perm(d_sign, gold, pr)
        ff = fr3_perm(-s.astype(float), gold, pr)
        dl.append(fs - ff)
        cp = competition(hamming(D0, Q0, tc).astype(np.int64), hamming(D0, Q0, bc_).astype(np.int64), gold)
        sg.append(cp['STRICT_GAP']); tg.append(cp['TIE_GAP'])
    return spearman(dl, sg), spearman(dl, tg)

out = {}
for name, loader in (('LME', load_lme), ('REALTALK', load_realtalk), ('PERLTQA', load_perltqa)):
    rows, _ = loader()
    if name == 'PERLTQA':
        rows = rows  # full
    reps = []
    for sb in (11, 2027, 40009, 91000, 5100099, 777771):
        reps.append(bench_rho_perm(rows, sb))
        print(f'{name} seed {sb}: strict={reps[-1][0]!r} tie={reps[-1][1]!r}', flush=True)
    st = [r[0] for r in reps]; ti = [r[1] for r in reps]
    out[name] = dict(
        perm_strict=st, perm_tie=ti,
        perm_strict_min=min(st), perm_strict_max=max(st),
        perm_tie_min=min(ti), perm_tie_max=max(ti),
        exact_strict=MINE[name][0], exact_tie=MINE[name][1],
        auditor_strict=AUD[name][0], auditor_tie=AUD[name][1],
        auditor_strict_inside_perm_range=bool(min(st) <= AUD[name][0] <= max(st)),
        auditor_tie_inside_perm_range=bool(min(ti) <= AUD[name][1] <= max(ti)),
        exact_minus_auditor_strict=MINE[name][0] - AUD[name][0],
        exact_minus_auditor_tie=MINE[name][1] - AUD[name][1],
    )
    print(f'  -> {name} perm strict range [{min(st)!r},{max(st)!r}] auditor={AUD[name][0]!r} inside={out[name]["auditor_strict_inside_perm_range"]}')
    print(f'  -> {name} perm tie    range [{min(ti)!r},{max(ti)!r}] auditor={AUD[name][1]!r} inside={out[name]["auditor_tie_inside_perm_range"]}', flush=True)

json.dump(out, open('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit/evidence/perm_diagnosis.json', 'w'), indent=2)
print('OK')
