#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
sweep.py -- (E) definition sweep for a tie statistic that FALLS with N;
            (F) clean paired within-archive subsample ladder on ALL 470 LME archives;
            (G) paired delta-vs-N significance test on the pooled ladder.
READ-ONLY on all caches."""
import json, pickle, glob, os, sys
import numpy as np
from collections import defaultdict

W = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = f'{W}/agent_out/scale-contradiction/evidence'


def load_lme():
    Cs, qs, gs = [], [], []
    for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        Cs.append(np.asarray(d['C'], np.float32))
        qs.append(np.asarray(d['qC'], np.float32))
        gs.append(np.asarray(d['gold']).ravel().astype(int))
    return Cs, np.array(qs), gs


def defs(dh, cf, gl, K=3):
    """dh: hamming distances (unsorted, lower=better). cf: -cosine. gl: gold indices.
    Returns dict of candidate tie definitions -> 0/1 or float."""
    N = len(dh)
    sd = np.sort(dh)
    thr = sd[K - 1]
    strictly = int(np.searchsorted(sd, thr, 'left'))
    bc = int(np.searchsorted(sd, thr, 'right')) - strictly
    slots = K - strictly
    gdh = dh[gl]
    g_tied = int(np.sum(gdh == thr))
    o = {}
    o['D01_frozen_bc_gt_slots'] = int(bc > slots)
    o['D02_bc_gt_1_shared'] = int(bc > 1)
    o['D03_gap_eq_0'] = int(sd[K] == sd[K - 1]) if N > K else 0
    o['D04_strictly_eq_0_allK_tied'] = int(strictly == 0)
    o['D05_d1_eq_d2'] = int(sd[0] == sd[1])
    o['D06_d1_eq_d3'] = int(sd[0] == sd[2])
    o['D07_consequential_gold_at_boundary'] = int((bc > slots) and g_tied > 0)
    o['D08_bc_over_N'] = bc / N
    o['D09_gap_le_1'] = int(sd[K] - sd[K - 1] <= 1) if N > K else 0
    o['D10_frac_random_slots'] = (slots / K) if bc > slots else 0.0
    o['D11_thr_ge_40'] = int(thr >= 40)           # "3rd-nearest inside the concentrated mass"
    o['D12_thr_ge_44'] = int(thr >= 44)
    o['D13_thr_ge_48'] = int(thr >= 48)
    # float arm
    sf = np.sort(cf)
    fthr = sf[K - 1]
    fstr = int(np.sum(cf < fthr)); fbc = int(np.sum(cf == fthr))
    o['D14_float_bc_gt_slots'] = int(fbc > (K - fstr))
    # shortlist-relative: tie rate at K=3 INSIDE a sign shortlist of size M (two-stage)
    for M in (20, 50):
        idx = np.argsort(dh, kind='stable')[:M]
        sub = np.sort(dh[idx])
        t2 = sub[K - 1]
        st2 = int(np.sum(sub < t2)); bc2 = int(np.sum(sub == t2))
        o[f'D15_shortlistM{M}_bc_gt_slots'] = int(bc2 > (K - st2))
        # stage-2 rerank by float inside the sign shortlist -> tie there
        sub2 = np.sort(cf[idx])
        t3 = sub2[K - 1]
        st3 = int(np.sum(sub2 < t3)); bc3 = int(np.sum(sub2 == t3))
        o[f'D16_shortlistM{M}_float_rerank_tie'] = int(bc3 > (K - st3))
    # other K
    for KK in (1, 2, 5, 10, 20, 50, 100):
        if N > KK:
            t = sd[KK - 1]
            st = int(np.searchsorted(sd, t, 'left')); b = int(np.searchsorted(sd, t, 'right')) - st
            o[f'D17_K{KK}_bc_gt_slots'] = int(b > (KK - st))
            o[f'D18_K{KK}_strictly_eq_0'] = int(st == 0)
    o['_thr'] = float(thr); o['_bc'] = bc; o['_N'] = N
    return o


def section_E():
    Cs, Q, Gs = load_lme()
    nA = len(Cs)
    sizes = [c.shape[0] for c in Cs]
    off = np.cumsum([0] + sizes)
    Call = np.vstack(Cs)
    S = np.where(Call >= 0, 1.0, -1.0).astype(np.float32)
    nn = np.linalg.norm(Call, axis=1); nn[nn == 0] = 1
    Cn = (Call / nn[:, None]).astype(np.float32)
    MULT = [1, 2, 4, 10, 20, 50]
    perms = {i: np.random.default_rng(1234 + i).permutation(
        np.array([j for j in range(nA) if j != i])) for i in range(nA)}
    agg = defaultdict(lambda: defaultdict(list))
    for i in range(nA):
        sq = np.where(Q[i] >= 0, 1.0, -1.0).astype(np.float32)
        qn = (Q[i] / (np.linalg.norm(Q[i]) or 1.0)).astype(np.float32)
        d_all = (96.0 - (S @ sq)) * 0.5
        c_all = -(Cn @ qn)
        gglob = off[i] + Gs[i]
        for mm in MULT:
            ids = [i] + list(perms[i][:mm - 1])
            idx = np.concatenate([np.arange(off[j], off[j + 1]) for j in ids])
            pos = {int(v): k for k, v in enumerate(idx[:sizes[i]])}
            gl = np.array([pos[int(v)] for v in gglob], int)
            o = defs(d_all[idx], c_all[idx], gl)
            for k, v in o.items():
                agg[mm][k].append(v)
        if i % 150 == 0:
            print(f'  E q{i}/{nA}', flush=True)
    tab = []
    for mm in MULT:
        rec = {'mult': mm, 'n': len(agg[mm]['D01_frozen_bc_gt_slots'])}
        for k, v in agg[mm].items():
            rec[k] = float(np.mean(v))
        tab.append(rec)
    json.dump(tab, open(f'{OUT}/E_defsweep_pool.json', 'w'), indent=1)
    keys = [k for k in tab[0] if k.startswith('D')]
    print('\n=== E: DEFINITION SWEEP on POOLED LME ladder (n=470 queries each rung) ===')
    print('%-38s' % 'definition' + ''.join('%9s' % ('N=%d' % round(t['mult'] * 492.8)) for t in tab) + '   trend')
    for k in sorted(keys):
        vals = [t[k] for t in tab]
        tr = 'RISE' if vals[-1] > vals[0] + 0.02 else ('FALL' if vals[-1] < vals[0] - 0.02 else 'flat')
        print('%-38s' % k + ''.join('%9.3f' % v for v in vals) + '   ' + tr)


def section_F():
    """Clean paired within-archive subsample ladder, ALL 470 LME archives, R reps."""
    Cs, Q, Gs = load_lme()
    LAD = [25, 50, 100, 200, 300, 396]
    R = 20
    agg = defaultdict(lambda: defaultdict(list))
    for i in range(len(Cs)):
        C = Cs[i]; N0 = C.shape[0]
        S = np.where(C >= 0, 1.0, -1.0).astype(np.float32)
        nn = np.linalg.norm(C, axis=1); nn[nn == 0] = 1
        Cn = (C / nn[:, None]).astype(np.float32)
        sq = np.where(Q[i] >= 0, 1.0, -1.0).astype(np.float32)
        qn = (Q[i] / (np.linalg.norm(Q[i]) or 1.0)).astype(np.float32)
        d_full = (96.0 - (S @ sq)) * 0.5
        c_full = -(Cn @ qn)
        g = Gs[i]
        gset = set(g.tolist())
        nong = np.array([x for x in range(N0) if x not in gset], int)
        for Nt in LAD + ['FULL']:
            NN = N0 if Nt == 'FULL' else Nt
            if NN > N0:
                continue
            reps = 1 if Nt == 'FULL' else R
            for rep in range(reps):
                rng = np.random.default_rng(31000 + i * 211 + (NN * 13) + rep)
                if Nt == 'FULL':
                    sub = np.arange(N0); gl = g
                else:
                    take = min(NN - len(g), len(nong))
                    sub = np.concatenate([g, rng.choice(nong, take, replace=False)])
                    gl = np.arange(len(g))
                o = defs(d_full[sub], c_full[sub], gl)
                key = 'FULL' if Nt == 'FULL' else NN
                for k, v in o.items():
                    agg[key][k].append(v)
                # FR@3 both arms
                from_ = d_full[sub]
                sd = np.sort(from_); thr = sd[2]
                st = int(np.sum(from_ < thr)); bc = int(np.sum(from_ == thr))
                gs_ = from_[gl]
                agg[key]['fr3_sign'].append((int(np.sum(gs_ < thr)) + int(np.sum(gs_ == thr)) * (3 - st) / bc) / len(gl))
                cc = c_full[sub]; sc = np.sort(cc); thr2 = sc[2]
                st2 = int(np.sum(cc < thr2)); bc2 = int(np.sum(cc == thr2))
                gc = cc[gl]
                agg[key]['fr3_float'].append((int(np.sum(gc < thr2)) + int(np.sum(gc == thr2)) * (3 - st2) / bc2) / len(gl))
        if i % 150 == 0:
            print(f'  F a{i}/{len(Cs)}', flush=True)
    order = LAD + ['FULL']
    tab = []
    for k in order:
        if k not in agg:
            continue
        rec = {'N': k, 'n': len(agg[k]['D01_frozen_bc_gt_slots'])}
        for kk, v in agg[k].items():
            rec[kk] = float(np.mean(v))
        d = np.array(agg[k]['fr3_sign']) - np.array(agg[k]['fr3_float'])
        rec['delta_pp'] = float(d.mean() * 100)
        rec['delta_se_pp'] = float(d.std(ddof=1) / np.sqrt(len(d)) * 100)
        tab.append(rec)
    json.dump(tab, open(f'{OUT}/F_subsample_lme.json', 'w'), indent=1)
    print('\n=== F: WITHIN-ARCHIVE SUBSAMPLE, all 470 LME archives (gold forced in) ===')
    print('%7s %7s %8s %9s %9s %9s %9s %8s %8s %8s' % ('N', 'n', 'frozen', 'shared', 'strict0',
          'K1_ovf', 'K20_ovf', 'thr', 'delta', 'SE'))
    for r in tab:
        print('%7s %7d %8.3f %9.3f %9.3f %9.3f %9.3f %8.2f %8.2f %8.2f' % (
            r['N'], r['n'], r['D01_frozen_bc_gt_slots'], r['D02_bc_gt_1_shared'],
            r['D04_strictly_eq_0_allK_tied'], r['D17_K1_bc_gt_slots'],
            r.get('D17_K20_bc_gt_slots', float('nan')), r['_thr'], r['delta_pp'], r['delta_se_pp']))
    keys = [k for k in tab[0] if k.startswith('D')]
    print('\n-- F definition sweep trend (N=25 -> FULL~493) --')
    for k in sorted(keys):
        v0 = tab[0][k]; v1 = tab[-1][k]
        tr = 'RISE' if v1 > v0 + 0.02 else ('FALL' if v1 < v0 - 0.02 else 'flat')
        print('%-38s %8.3f -> %8.3f   %s' % (k, v0, v1, tr))


def section_G():
    """Paired significance of the delta's N-trend on the pooled ladder."""
    A = json.load(open(f'{OUT}/A_pool_rows.json'))
    byq = defaultdict(dict)
    for r in A:
        byq[r['q']][r['m']] = r
    ms = sorted(set(r['m'] for r in A))
    print('\n=== G: PAIRED delta-vs-N test, pooled LME ladder ===')
    d1 = np.array([byq[q][ms[0]]['fr3_sign'] - byq[q][ms[0]]['fr3_float'] for q in byq])
    out = {}
    for mm in ms[1:]:
        dm = np.array([byq[q][mm]['fr3_sign'] - byq[q][mm]['fr3_float'] for q in byq])
        dd = d1 - dm
        t = dd.mean() / (dd.std(ddof=1) / np.sqrt(len(dd)))
        out[f'm1_minus_m{mm}'] = {'mean_pp': float(dd.mean() * 100),
                                  'se_pp': float(dd.std(ddof=1) / np.sqrt(len(dd)) * 100),
                                  't': float(t), 'n': int(len(dd))}
        print('delta(N=493) - delta(N=%6d) = %+6.2f pp  +- %.2f (SE)   t=%+.2f  n=%d'
              % (round(mm * 492.8), dd.mean() * 100, dd.std(ddof=1) / np.sqrt(len(dd)) * 100, t, len(dd)))
    # also per-arm absolute levels
    print('\nabsolute arm levels along the pooled ladder:')
    for mm in ms:
        s = np.mean([byq[q][mm]['fr3_sign'] for q in byq])
        f = np.mean([byq[q][mm]['fr3_float'] for q in byq])
        print('  N=%6d  sign=%.4f  float=%.4f  delta=%+.2f pp' % (round(mm * 492.8), s, f, (s - f) * 100))
        out[f'levels_m{mm}'] = {'sign': float(s), 'float': float(f), 'delta_pp': float((s - f) * 100)}
    json.dump(out, open(f'{OUT}/G_delta_paired.json', 'w'), indent=1)


if __name__ == '__main__':
    for s in sys.argv[1:]:
        {'E': section_E, 'F': section_F, 'G': section_G}[s.upper()]()
    print('DONE', flush=True)
