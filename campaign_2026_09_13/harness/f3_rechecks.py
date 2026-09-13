#!/usr/bin/env python3
"""F3/C9 rechecks requested by the D5 adversarial review (2026-09-13).
Checks: (B) LoCoMo split counts+balance all 10 splits + membership spot-check (5 test qids
recomputed FR vs stored); (C) LME delta64 col-set check for split 0; (D) report HASHES check
done separately. Read-only. Writes only stdout + f3_rechecks.txt alongside.
"""
import hashlib, json, re, pickle
import numpy as np
from pathlib import Path
from collections import Counter

BASE = Path('C:/Users/MDP/dev/llmzip-work')
R3 = BASE/'pilots/axis_attack_2026-09-12/round3'
OUT = R3/'muse_sessions'/'d5'/'f3_rechecks.txt'
lines = []
def log(s):
    print(s, flush=True); lines.append(s)

# ---------- helpers (verbatim from deney1_loco.py) ----------
def norm_evidence(x):
    if x is None: return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x); return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z); out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did: out.append(str(did))
        return list(dict.fromkeys(out))
    return []

def load_audit_corrections(audit_dir):
    corrections = {}
    for f in sorted(audit_dir.glob("errors_conv_*.json")):
        rows = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(rows, list): continue
        for r in rows:
            qid = r.get("question_id")
            if not qid: continue
            corrections[str(qid)] = {"has_correct_evidence": "correct_evidence" in r,
                                     "correct_evidence": norm_evidence(r.get("correct_evidence"))}
    return corrections

def stable_archive_seed(ci, t=0): return 5_100_000 + ci*100_000 + t*100

def topks_by_hamming(dist, priorities, k=3):
    dist = np.asarray(dist); P = np.asarray(priorities, dtype=float)
    if len(dist) <= k: return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k-1)[k-1]
    strict = np.flatnonzero(dist < kth); boundary = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, boundary]
    picks = np.tile(boundary, (len(P), 1)) if need == len(boundary) else boundary[np.argpartition(BP, need-1, axis=1)[:, :need]]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]

def evidence_rows(ids, id_to_row):
    out = [int(id_to_row[x]) for x in ids if x in id_to_row]
    return list(dict.fromkeys(out))

t0 = ''
# ---------- Check B1: LoCoMo splits ----------
z = np.load(R3/'deney1_loco_peraxis.npz')
qids = [str(q) for q in z['qids']]; cats = list(map(int, z['cats']))
det = json.loads((R3/'deney1_loco_details.json').read_text(encoding='utf-8'))

def make_split(s):
    tr, te = [], []
    for c in (1, 2, 3, 4):
        qs = sorted([q for q, cc in zip(qids, cats) if cc == c],
                    key=lambda q: hashlib.sha256(f'deney1loco|{s}|{q}'.encode()).hexdigest())
        for i, q in enumerate(qs):
            (tr if i % 2 == 0 else te).append(q)
    return sorted(tr), sorted(te)

allok = True
for s in range(10):
    tr, te = make_split(s)
    n_test = det['splits'][s]['run']['n_test']
    m = 'OK' if len(te) == n_test else 'MISMATCH'
    if len(te) != n_test: allok = False
    log(f'B1 s={s}: derived_test={len(te)} stored_n_test={n_test} {m} test_cats={dict(sorted(Counter(cats[qids.index(q)] for q in te).items()))}')
log(f'B1 all-counts-match: {allok}')

# ---------- Check B2: membership spot-check (s=0, drop64, first 5 test qids) ----------
cols = np.array(det['splits'][0]['arms']['drop64']['cols'])
stored = det['splits'][0]['per_q_test']['drop64']
tr0, te0 = make_split(0)
# load raw + corrections + pkls
raw = json.loads((BASE/'drive/locomo10.json').read_text(encoding='utf-8'))
corr = load_audit_corrections(BASE/'drive/audit_layer')
convs = []
for idx, item in enumerate(raw):
    qas = []
    for qi, q in enumerate(item.get("qa", []) or []):
        c = int(q.get("category")) if q.get("category") is not None else None
        if c not in (1, 2, 3, 4): continue
        qid = str(q.get("question_id") or f"locomo_{idx}_qa{qi}")
        zc = corr.get(qid)
        ce = (list(zc["correct_evidence"]) if zc.get("has_correct_evidence", False)
              else list(norm_evidence(q.get("evidence")))) if zc else list(norm_evidence(q.get("evidence")))
        qas.append({"question_id": qid, "cat": c, "ce": ce})
    convs.append(qas)

def fr_of(qid, cols):
    for ci in range(10):
        ids = [q["question_id"] for q in convs[ci]]
        if qid in ids:
            qi = ids.index(qid)
            d = pickle.load(open(BASE/'regen/locomo'/f'locomo_{ci}.pkl', 'rb'))
            C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
            gold = evidence_rows(convs[ci][qi]["ce"], d['id_to_row'])
            A = ((QC[qi, cols] >= 0)[None, :] != (C[:, cols] >= 0)).sum(axis=1)
            pr = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(len(C)) for t in range(20)]
            tot = 0.0
            for t in range(20):
                top = topks_by_hamming(A, [pr[t]])[0][:3]
                inter = len(set(map(int, top)) & set(gold))
                tot += inter / len(gold)
            return tot / 20
    return None

# pick first 5 test qids with NONZERO stored FR (stronger membership evidence)
picks = []
for i, q in enumerate(te0):
    if stored[i] > 1e-12:
        picks.append((i, q))
    if len(picks) == 5:
        break
n_zero = sum(1 for i in range(len(te0)) if stored[i] <= 1e-12)
log(f'B2: stored test FR zero-count = {n_zero}/{len(te0)}; using first 5 nonzero for spot-check')
for i, q in picks:
    v = fr_of(q, cols)
    sv = stored[i]
    m = 'EXACT' if v is not None and abs(v - sv) < 1e-12 else f'DIFF ({v} vs {sv})'
    log(f'B2 s=0 test[{i}] {q}: recomputed={v!r} stored={sv!r} {m}')

# ---------- Check C: LME delta64 cols (split 0) ----------
import csv
zp = np.load(BASE/'pilots/axis_attack_2026-09-12/per_axis_matrices.npz')
delta = zp['delta']; qidsL = [str(q) for q in zp['qids']]
qtype = {}
with open(BASE/'drive/t4c3/V52_T4C3_question_level.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f): qtype[row['question_id']] = row['question_type']
trL, teL = [], []
for t in sorted(set(qtype[q] for q in qidsL)):
    qs = sorted([q for q in qidsL if qtype[q] == t],
                key=lambda q: hashlib.sha256(f'deney1|0|{q}'.encode()).hexdigest())
    for i, q in enumerate(qs):
        (trL if i % 2 == 0 else teL).append(q)
qi_of = {q: i for i, q in enumerate(qidsL)}
U_delta = delta[[qi_of[q] for q in trL]].mean(axis=0)
colsL = np.sort(np.argsort(U_delta)[::-1][:64])
detL = json.loads((R3/'deney1_lme_details.json').read_text(encoding='utf-8'))
storedL = np.array(detL['splits'][0]['arms']['delta64']['cols'])
log(f'C delta64 s=0: recomputed==stored: {bool(np.array_equal(colsL, storedL))} '
    f'(n={len(colsL)}; stored n={len(storedL)})')

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
print('wrote', OUT)
print('F3_RECHECKS_DONE')
