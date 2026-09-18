"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Independent baseline audit: full per-query Top10 ranking + actual metrics
from ORIGINAL caches and serialized codes, not summary only.

Own ranking/metrics (no import of baseline metrics_top10 for primary;
baseline module used ONLY as optional crosscheck after verdict).
Covers all 9440 (PerLTQA 8265, LME 470, REALTALK 705).

Usage: $HOME/muse-work/ml-python audit_baseline.py
Outputs (audit/ dir only): baseline_audit.json
"""
import glob
import hashlib
import json
import math
import os
import pickle
import time
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "baseline")
R = "/mnt/c/Users/MDP/dev/llmzip-work"
PERLTQA_ARCH = R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PERLTQA_Q = R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
LME_GLOB = R + "/regen/lme/cache_repr/*.pkl"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
TIE_SALT = "top10-r1"
SQRT96 = float(np.sqrt(96))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---- independent implementations (own) ----
def pack_signs_bool(b):
    return np.packbits(np.asarray(b, dtype=bool), axis=-1, bitorder="big").astype(np.uint8)


def decode_pm1(packed):
    bits = np.unpackbits(np.asarray(packed, dtype=np.uint8), axis=1, bitorder="big")[:, :96].astype(bool)
    return np.where(bits, 1, -1).astype(np.int8)


def hamming_packed(packed, q_bits):
    d = np.unpackbits(np.asarray(packed, dtype=np.uint8), axis=1, bitorder="big")[:, :96].astype(bool)
    return np.count_nonzero(d != np.asarray(q_bits, dtype=bool)[None, :], axis=1)


def cosine_raw(C, q):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))


def fit_std(C):
    std = np.std(np.asarray(C, dtype=np.float64), axis=0, ddof=0).astype(np.float64)
    return np.where(std == 0, 1.0, std)


def cosine_std(C, q, std):
    std = np.asarray(std, dtype=np.float64).reshape(-1)
    return cosine_raw(C / std[None, :], q / std)


def asym_scores(packed, q):
    D = decode_pm1(np.asarray(packed, dtype=np.uint8)).astype(np.float64)
    return (D @ np.asarray(q, dtype=np.float64).reshape(-1)) / SQRT96


def det_top10(scores, archive_id, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{TIE_SALT}|{archive_id}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


def hrn(top, gold, k=10):
    top = [int(x) for x in np.asarray(top).ravel().tolist()][:k]
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    inter = len([x for x in top if x in gset])
    hit = 1.0 if inter else 0.0
    rec = inter / len(gset)
    disc = [1.0 / math.log2(r + 2) for r in range(k)]
    idcg = sum(disc[:min(k, len(gset))])
    dcg = sum(disc[r] for r, d in enumerate(top) if d in gset)
    return hit, rec, (dcg / idcg if idcg else 0.0)


def expected_hit(scores, gold, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    uniq = np.unique(s)[::-1]
    better = 0
    for lv in uniq:
        idx = np.nonzero(s == lv)[0]
        Bb = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + Bb <= k:
            if gb > 0:
                return 1.0
            better += Bb
        else:
            take = int(k - better)
            if gb == 0:
                return 0.0
            return float(1.0 - (math.comb(Bb - gb, take) if (Bb - gb) >= take else 0) / math.comb(Bb, take))
    return 0.0


def expected_recall(scores, gold, k=3):
    s = np.asarray(scores, dtype=np.float64).ravel()
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    uniq = np.unique(s)[::-1]
    better, exp = 0, 0.0
    for lv in uniq:
        idx = np.nonzero(s == lv)[0]
        Bb = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + Bb <= k:
            exp += gb
        else:
            exp += (k - better) * gb / Bb
            break
        better += Bb
    return float(exp / len(gset))
