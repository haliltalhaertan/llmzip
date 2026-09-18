#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]

scale.py -- SIGN96 tie-rate vs archive size N, three independent ways + definition sweep.
READ-ONLY on every llmzip-work cache. Writes only under agent_out/scale-contradiction/.

Usage:  ml-python scale.py <section>      section in {A,B,C,D}
  A = pooling independent LME archives (reproduce coordinator ladder) + definition sweep + delta
  B = subsampling rows inside ONE real archive (isolates N from pooling)
  C = natural N spread across real archive families (per-archive)
  D = synthetic controls (uncorrelated uniform codes vs correlated low-rank codes)
"""
import json, pickle, glob, os, sys
import numpy as np

W = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = f'{W}/agent_out/scale-contradiction/evidence'
os.makedirs(OUT, exist_ok=True)
KS = [1, 3, 5, 10, 20, 50]


# ---------------------------------------------------------------- primitives
def tie_stats(sorted_scores, Ks=KS):
    """sorted_scores ascending (lower = better). Returns dict of per-K boundary stats.
    frozen def: strictly=#{<thr}, bc=#{==thr}, slots=K-strictly, tie = bc>slots."""
    sd = sorted_scores
    n = len(sd)
    out = {}
    for K in Ks:
        if n <= K:
            continue
        thr = sd[K - 1]
        strictly = int(np.searchsorted(sd, thr, 'left'))
        hi = int(np.searchsorted(sd, thr, 'right'))
        bc = hi - strictly
        slots = K - strictly
        out[K] = dict(tie_overflow=int(bc > slots),      # frozen bc>slots
                      tie_shared=int(bc > 1),            # "K-th value is shared at all"
                      gap0=int(sd[K] == sd[K - 1]),      # gap==0
                      bc=bc, slots=slots, strictly=strictly,
                      gap=float(sd[K] - sd[K - 1]), thr=float(thr))
    return out


def fr_exact(scores, gold, K=3):
    """Exact expectation of FR@K under uniform random tie-break. scores: lower=better."""
    s = np.asarray(scores, float)
    srt = np.sort(s)
    thr = srt[K - 1]
    strictly = int(np.searchsorted(srt, thr, 'left'))
    bc = int(np.searchsorted(srt, thr, 'right')) - strictly
    slots = K - strictly
    g = np.asarray(gold).ravel().astype(int)
    gs = s[g]
    return float((int(np.sum(gs < thr)) + int(np.sum(gs == thr)) * slots / bc) / len(g))


def load_lme():
    files = sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl'))
    Cs, qs, gs, qids = [], [], [], []
    for f in files:
        d = pickle.load(open(f, 'rb'))
        Cs.append(np.asarray(d['C'], np.float32))
        qs.append(np.asarray(d['qC'], np.float32))
        gs.append(np.asarray(d['gold']).ravel().astype(int))
        qids.append(d['question_id'])
    return Cs, np.array(qs), gs, qids


def codes_and_norm(C):
    S = np.where(C >= 0, 1.0, -1.0).astype(np.float32)
    nn = np.linalg.norm(C, axis=1)
    nn[nn == 0] = 1.0
    Cn = (C / nn[:, None]).astype(np.float32)
    return S, Cn


# ---------------------------------------------------------------- A: pooling
def section_A():
    Cs, Q, Gs, qids = load_lme()
    nA = len(Cs)
    sizes = [c.shape[0] for c in Cs]
    off = np.cumsum([0] + sizes)
    Call = np.vstack(Cs)
    Sall, Cnall = codes_and_norm(Call)
    print('A: stacked', Call.shape, flush=True)

    MULT = [1, 2, 4, 10, 20, 50]
    # nested deterministic pools so the ladder is PAIRED across N
    perms = {i: np.random.default_rng(1234 + i).permutation(
        np.array([j for j in range(nA) if j != i])) for i in range(nA)}

    rows = []
    for i in range(nA):
        sq = np.where(Q[i] >= 0, 1.0, -1.0).astype(np.float32)
        qn = Q[i] / (np.linalg.norm(Q[i]) or 1.0)
        d_all = (96.0 - (Sall @ sq)) * 0.5           # hamming to every row in the universe
        c_all = -(Cnall @ qn.astype(np.float32))     # negative cosine: lower = better
        g_glob = off[i] + Gs[i]
        for m in MULT:
            ids = [i] + list(perms[i][:m - 1])
            idx = np.concatenate([np.arange(off[j], off[j + 1]) for j in ids])
            pos = {int(v): k for k, v in enumerate(idx[:sizes[i]])}  # archive i occupies prefix
            dh = d_all[idx]
            cf = c_all[idx]
            gl = np.array([pos[int(v)] for v in g_glob], int)
            r = dict(q=i, m=m, N=int(len(idx)))
            r['fr3_sign'] = fr_exact(dh, gl, 3)
            r['fr3_float'] = fr_exact(cf, gl, 3)
            ts = tie_stats(np.sort(dh))
            tf = tie_stats(np.sort(cf))
            for K, v in ts.items():
                for k2, v2 in v.items():
                    r[f'sign_K{K}_{k2}'] = v2
            for K, v in tf.items():
                r[f'float_K{K}_tie_overflow'] = v['tie_overflow']
                r[f'float_K{K}_tie_shared'] = v['tie_shared']
            r['sign_dmin'] = float(np.min(dh))
            r['sign_dmean'] = float(np.mean(dh))
            rows.append(r)
        if i % 100 == 0:
            print(f'  A q{i}/{nA}', flush=True)
    json.dump(rows, open(f'{OUT}/A_pool_rows.json', 'w'))
    print('A rows', len(rows), flush=True)


# ---------------------------------------------------------------- B: subsample
def section_B():
    """Subsample rows inside ONE real archive. Gold is irrelevant to the tie rate, so the
    subsample is unconstrained for tie statistics; for FR@3 we force-keep gold rows."""
    arch = []   # (label, C, qC list, gold list)
    for f in sorted(glob.glob(f'{W}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        arch.append(('RT:' + str(d.get('chat_no', os.path.basename(f))),
                     np.asarray(d['C'], np.float32), np.asarray(d['QC'], np.float32),
                     [np.asarray(g).ravel().astype(int) for g in d['gold_rows']]))
    for i in range(10):
        d = pickle.load(open(f'{W}/regen/locomo/locomo_{i}.pkl', 'rb'))
        C = np.asarray(d['C'], np.float32); QC = np.asarray(d['QC'], np.float32)
        i2r = d['id_to_row']
        gl = []
        for qa in d['qas']:
            ev = qa.get('raw_evidence') or []
            if isinstance(ev, str):
                ev = [ev]
            rr = [i2r[e] for e in ev if e in i2r]
            gl.append(np.array(sorted(set(rr)), int))
        arch.append((f'LOCOMO:{d["conv_id"]}', C, QC, gl))
    # a few LME archives too (N~500)
    for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl'))[:40]:
        d = pickle.load(open(f, 'rb'))
        arch.append(('LME:' + d['question_id'], np.asarray(d['C'], np.float32),
                     np.asarray(d['qC'], np.float32)[None, :],
                     [np.asarray(d['gold']).ravel().astype(int)]))
    print('B archives', len(arch), 'Nmax', max(a[1].shape[0] for a in arch), flush=True)

    LAD = [25, 50, 100, 200, 400, 800, 1200, 1500]
    R = 12
    rows = []
    for lab, C, QC, GL in arch:
        N0 = C.shape[0]
        S, Cn = codes_and_norm(C)
        for j in range(QC.shape[0]):
            qC = QC[j]
            sq = np.where(qC >= 0, 1.0, -1.0).astype(np.float32)
            qn = qC / (np.linalg.norm(qC) or 1.0)
            d_full = (96.0 - (S @ sq)) * 0.5
            c_full = -(Cn @ qn.astype(np.float32))
            g = GL[j] if j < len(GL) else np.array([], int)
            for Nt in LAD + [N0]:
                if Nt > N0:
                    continue
                for rep in range(R if Nt < N0 else 1):
                    rng = np.random.default_rng(777000 + hash(lab) % 100000 + j * 97 + Nt * 7 + rep)
                    sub = rng.choice(N0, Nt, replace=False) if Nt < N0 else np.arange(N0)
                    dh = np.sort(d_full[sub]); cf = np.sort(c_full[sub])
                    r = dict(fam=lab.split(':')[0], arch=lab, q=j, N=int(Nt), rep=rep, N0=int(N0))
                    for K, v in tie_stats(dh).items():
                        r[f'sign_K{K}_tie_overflow'] = v['tie_overflow']
                        r[f'sign_K{K}_tie_shared'] = v['tie_shared']
                        r[f'sign_K{K}_gap0'] = v['gap0']
                        r[f'sign_K{K}_bc'] = v['bc']
                        r[f'sign_K{K}_thr'] = v['thr']
                    for K, v in tie_stats(cf).items():
                        r[f'float_K{K}_tie_overflow'] = v['tie_overflow']
                    r['sign_dmin'] = float(dh[0]); r['sign_dmean'] = float(dh.mean())
                    rows.append(r)
                # FR@3 with gold forced in (single rep, deterministic)
                if len(g) and Nt >= len(g) + 3:
                    rng = np.random.default_rng(555000 + hash(lab) % 100000 + j * 91 + Nt)
                    pool_non = np.array([x for x in range(N0) if x not in set(g.tolist())], int)
                    take = min(Nt - len(g), len(pool_non))
                    sub = np.concatenate([g, rng.choice(pool_non, take, replace=False)])
                    gl = np.arange(len(g))
                    rows[-1]['fr3_sign'] = fr_exact(d_full[sub], gl, 3)
                    rows[-1]['fr3_float'] = fr_exact(c_full[sub], gl, 3)
    json.dump(rows, open(f'{OUT}/B_subsample_rows.json', 'w'))
    print('B rows', len(rows), flush=True)


# ---------------------------------------------------------------- C: natural
def section_C():
    rows = []

    def do(fam, lab, C, QC, GL):
        S, Cn = codes_and_norm(C)
        for j in range(QC.shape[0]):
            qC = QC[j]
            sq = np.where(qC >= 0, 1.0, -1.0).astype(np.float32)
            qn = qC / (np.linalg.norm(qC) or 1.0)
            dh = np.sort((96.0 - (S @ sq)) * 0.5)
            cf = np.sort(-(Cn @ qn.astype(np.float32)))
            r = dict(fam=fam, arch=lab, q=j, N=int(C.shape[0]))
            for K, v in tie_stats(dh).items():
                r[f'sign_K{K}_tie_overflow'] = v['tie_overflow']
                r[f'sign_K{K}_tie_shared'] = v['tie_shared']
                r[f'sign_K{K}_bc'] = v['bc']
            for K, v in tie_stats(cf).items():
                r[f'float_K{K}_tie_overflow'] = v['tie_overflow']
            g = GL[j] if j < len(GL) else np.array([], int)
            if len(g):
                d_full = (96.0 - (S @ sq)) * 0.5
                c_full = -(Cn @ qn.astype(np.float32))
                r['fr3_sign'] = fr_exact(d_full, g, 3)
                r['fr3_float'] = fr_exact(c_full, g, 3)
            rows.append(r)

    for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        do('LME', d['question_id'], np.asarray(d['C'], np.float32),
           np.asarray(d['qC'], np.float32)[None, :], [np.asarray(d['gold']).ravel().astype(int)])
    arch = pickle.load(open(f'{W}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    QD = pickle.load(open(f'{W}/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    byc = {}
    for qid, q in QD.items():
        byc.setdefault(q['char'], []).append(q)
    for c, a in arch.items():
        qs = byc.get(c, [])
        if not qs:
            continue
        do('PERLTQA', c, np.asarray(a['C'], np.float32),
           np.stack([np.asarray(q['qC'], np.float32) for q in qs]),
           [np.asarray(q['gold']).ravel().astype(int) for q in qs])
    for i in range(10):
        d = pickle.load(open(f'{W}/regen/locomo/locomo_{i}.pkl', 'rb'))
        i2r = d['id_to_row']; gl = []
        for qa in d['qas']:
            ev = qa.get('raw_evidence') or []
            if isinstance(ev, str):
                ev = [ev]
            gl.append(np.array(sorted(set(i2r[e] for e in ev if e in i2r)), int))
        do('LOCOMO', d['conv_id'], np.asarray(d['C'], np.float32),
           np.asarray(d['QC'], np.float32), gl)
    for f in sorted(glob.glob(f'{W}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        do('REALTALK', 'RT' + str(d.get('chat_no', '')), np.asarray(d['C'], np.float32),
           np.asarray(d['QC'], np.float32), [np.asarray(g).ravel().astype(int) for g in d['gold_rows']])
    json.dump(rows, open(f'{OUT}/C_natural_rows.json', 'w'))
    print('C rows', len(rows), flush=True)


# ---------------------------------------------------------------- D: synthetic
def section_D():
    """Directly test the relayed mechanism story on codes whose Hamming distribution really IS a
    concentrated Binomial(96,1/2): uncorrelated uniform random signs. Plus a correlated control."""
    LAD = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 25000, 100000]
    out = []
    for kind in ('uniform', 'lowrank8', 'lowrank32'):
        for N in LAD:
            agg = {}
            NQ = 200
            rng = np.random.default_rng(20260914)
            for t in range(NQ):
                if kind == 'uniform':
                    S = np.where(rng.random((N, 96)) >= 0.5, 1.0, -1.0).astype(np.float32)
                    sq = np.where(rng.random(96) >= 0.5, 1.0, -1.0).astype(np.float32)
                else:
                    r = 8 if kind == 'lowrank8' else 32
                    Z = rng.standard_normal((N, r)).astype(np.float32)
                    B = rng.standard_normal((r, 96)).astype(np.float32)
                    X = Z @ B + 0.5 * rng.standard_normal((N, 96)).astype(np.float32)
                    X = X - X.mean(0, keepdims=True)
                    S = np.where(X >= 0, 1.0, -1.0).astype(np.float32)
                    zq = rng.standard_normal(r).astype(np.float32) @ B
                    sq = np.where(zq >= 0, 1.0, -1.0).astype(np.float32)
                dh = np.sort((96.0 - (S @ sq)) * 0.5)
                for K, v in tie_stats(dh).items():
                    for nm in ('tie_overflow', 'tie_shared', 'bc', 'thr'):
                        agg.setdefault(f'K{K}_{nm}', []).append(v[nm])
                agg.setdefault('dmin', []).append(float(dh[0]))
                agg.setdefault('dmean', []).append(float(dh.mean()))
            rec = dict(kind=kind, N=N, nq=NQ)
            for k, v in agg.items():
                rec[k] = float(np.mean(v))
            out.append(rec)
            print('D', kind, N, 'K3_ovf=%.3f K3_shared=%.3f bc=%.2f thr=%.1f'
                  % (rec['K3_tie_overflow'], rec['K3_tie_shared'], rec['K3_bc'], rec['K3_thr']), flush=True)
    json.dump(out, open(f'{OUT}/D_synth.json', 'w'), indent=1)


if __name__ == '__main__':
    sec = sys.argv[1].upper()
    {'A': section_A, 'B': section_B, 'C': section_C, 'D': section_D}[sec]()
    print('DONE', sec, flush=True)
