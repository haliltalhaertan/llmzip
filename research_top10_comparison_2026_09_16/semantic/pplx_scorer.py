"""PPLX semantic scorer: official quant formulas, scoring, ranking, metrics.

Official semantics (from ../official_st_quantize.py + ../model/st_quantize.py):
  INT8  = clip(round(127*tanh(pooled)), -128, 127)   [round = half-to-even]
  BIN   = +1 where pooled >= 0 else -1  (UNQUANTIZED pooled, NOT sign of INT8)
  PACK  = packbits(pooled >= 0) big-endian per np.packbits, axis=-1
Pooling: masked mean over attention_mask (1_Pooling/config.json:
  mean_tokens=true, all others false), no instruction prefix, max 1024.

Scoring (higher is better):
  INT8 cosine      = cosine(int8_q, int8_d); zero-norm -> 0.0 (declared)
  PREQUANT cosine  = cosine(pooled_q, pooled_d); zero-norm -> 0.0 (declared,
                     extra arm, NOT a paper full-precision baseline)
  BIN Hamming      = -popcount(q_bin != d_bin) (negative Hamming distance)
  ASYM int8 x bin  = cosine(int8_q as float, bin_d as +-1 float); zero -> 0.0
Ranking: descending score, then ascending SHA256('top10-r1|'+archive+'|'+row),
  then ascending row. Exactly 10, no duplicates. Nonfinite scores rejected.
"""
import hashlib
import math

import numpy as np

TIE_PREFIX = "top10-r1"


def official_int8(pooled: np.ndarray) -> np.ndarray:
    import torch
    x = torch.as_tensor(np.asarray(pooled, dtype=np.float32))
    return torch.clamp(torch.round(torch.tanh(x) * 127), -128, 127).numpy().astype(np.int8)


def official_binary(pooled: np.ndarray) -> np.ndarray:
    x = np.asarray(pooled)
    return np.where(x >= 0, np.int8(1), np.int8(-1))


def pack_sign(sign: np.ndarray) -> np.ndarray:
    s = np.asarray(sign)
    bits = (s >= 0)
    return np.packbits(bits, axis=-1).astype(np.uint8)


def unpack_sign(packed: np.ndarray, dim: int) -> np.ndarray:
    p = np.asarray(packed, dtype=np.uint8)
    bits = np.unpackbits(p, axis=-1)[..., :dim]
    return np.where(bits == 1, np.int8(1), np.int8(-1))


def masked_mean_pool(hidden: np.ndarray, mask: np.ndarray) -> np.ndarray:
    import torch
    h = torch.as_tensor(np.asarray(hidden, dtype=np.float32))
    m = torch.as_tensor(np.asarray(mask)).unsqueeze(-1).expand(h.size()).to(h.dtype)
    return ((h * m).sum(1) / m.sum(1).clamp(min=1e-9)).numpy()


def load_checkpoint(path, hashes, dim=1024):
    """Fail closed: matching text alone never makes unencoded rows complete."""
    n = len(hashes)
    blank = np.zeros((n, dim), dtype=np.float32)
    missing = np.zeros(n, dtype=bool)
    try:
        with np.load(path, allow_pickle=False) as old:
            op = old["pooled_f32"]
            complete = old["complete"]
            if (list(old["hashes"]) != list(hashes) or op.shape != (n, dim)
                    or complete.shape != (n,) or complete.dtype != np.bool_
                    or not np.isfinite(op[complete]).all()):
                return blank, missing
            return op.astype(np.float32), complete.copy()
    except (OSError, ValueError, KeyError):
        return blank, missing


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def plan_batches(lengths, batch_size: int = 8):
    """Length-sorted bucket batches preserving original indices."""
    idx = sorted(range(len(lengths)), key=lambda i: lengths[i])
    return [idx[i:i + batch_size] for i in range(0, len(idx), batch_size)]


def _tie_key(archive_id: str, row: int):
    return (hashlib.sha256(f"{TIE_PREFIX}|{archive_id}|{row}".encode()).hexdigest(), row)


def rank_top10(scores: np.ndarray, archive_id: str, rows) -> list:
    s = np.asarray(scores, dtype=np.float64)
    rows = list(rows)
    if s.shape[0] != len(rows):
        raise ValueError("scores/rows length mismatch")
    if not np.all(np.isfinite(s)):
        raise ValueError("nonfinite scores rejected")
    if len(set(rows)) != len(rows):
        raise ValueError("duplicate rows")
    order = sorted(range(len(rows)),
                   key=lambda i: (-s[i], *_tie_key(archive_id, rows[i])))
    return [rows[i] for i in order[:10]]


def cosine_scores_int8(q: np.ndarray, d: np.ndarray) -> np.ndarray:
    Q = np.asarray(q, dtype=np.float64)
    D = np.asarray(d, dtype=np.float64)
    qn = np.linalg.norm(Q, axis=1, keepdims=True)
    dn = np.linalg.norm(D, axis=1, keepdims=True).T  # [1,N]
    denom = qn * dn  # [Q,N]
    num = Q @ D.T
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(denom == 0, 0.0, num / np.where(denom == 0, 1.0, denom))
    return out


def cosine_scores_float(q: np.ndarray, d: np.ndarray) -> np.ndarray:
    return cosine_scores_int8(np.asarray(q, dtype=np.float64),
                              np.asarray(d, dtype=np.float64))


def hamming_scores_bin(qb: np.ndarray, db: np.ndarray) -> np.ndarray:
    Q = np.asarray(qb)
    D = np.asarray(db)
    # negative Hamming distance: higher (closer to 0) is better
    ne = (Q[:, None, :] != D[None, :, :]).sum(axis=2)
    return (-ne).astype(np.float64)


def asym_scores_int8xbin(q: np.ndarray, db: np.ndarray) -> np.ndarray:
    return cosine_scores_int8(np.asarray(q, dtype=np.float64),
                              np.asarray(db, dtype=np.float64))


def prf_metrics(top10: list, gold: list) -> dict:
    g = set(int(x) for x in gold)
    t = [int(x) for x in top10]
    if len(g) == 0:
        return {"hit10": 0, "recall10": 0.0, "ndcg10": 0.0}
    hits = [1 if x in g else 0 for x in t]
    hit10 = 1 if sum(hits) > 0 else 0
    recall10 = sum(hits) / len(g)
    dcg = sum(rel / math.log2(rank + 1) for rank, rel in enumerate(hits, start=1))
    ideal_n = min(len(g), 10)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_n + 1))
    ndcg = dcg / idcg if idcg > 0 else 0.0
    return {"hit10": hit10, "recall10": float(recall10), "ndcg10": float(ndcg)}
