#!/usr/bin/env python3
"""E1 geometry core. No dataset parsing/refit: consumes already-frozen C/qC arrays supplied by a benchmark adapter."""
import numpy as np

def archive_geometry(C):
    C=np.asarray(C,dtype=np.float64)
    if C.ndim!=2 or C.shape[1]!=96:
        raise ValueError("C must be N x 96")
    v=np.mean(C*C,axis=0)
    mv=float(np.mean(v))
    s1=float(np.sum(v)); s2=float(np.sum(v*v))
    sign=np.where(C>=0.0,1.0,-1.0)
    return {
      "VAR_CV": float(np.std(v)/mv) if mv>0 else None,
      "EFF_COORD": float(s1*s1/s2) if s2>0 else None,
      "TOP64_VAR_SHARE": float(np.sum(np.sort(v)[-64:])/s1) if s1>0 else None,
      "SIGN_IMBALANCE": float(np.mean(np.abs(np.mean(sign,axis=0)))),
      "top64": np.argsort(v,kind="stable")[::-1][:64].tolist(),
      "bot64": np.argsort(v,kind="stable")[::-1][-64:].tolist(),
    }

def query_geometry(q):
    q=np.asarray(q,dtype=np.float64).reshape(-1)
    if q.shape!=(96,): raise ValueError("qC must be 96")
    a=np.abs(q); ma=float(np.mean(a)); s1=float(np.sum(a)); s2=float(np.sum(q*q))
    return {
      "Q_ABS_CV": float(np.std(a)/ma) if ma>0 else None,
      "Q_EFF": float(s1*s1/s2) if s2>0 else None,
    }
