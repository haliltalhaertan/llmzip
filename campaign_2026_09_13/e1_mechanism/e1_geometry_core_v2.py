#!/usr/bin/env python3
"""E1 V2 archive geometry core. Pure metrics only; no dataset parsing, fitting or scoring."""
from __future__ import annotations
import numpy as np


def _effdim_cov(X):
    X=np.asarray(X,dtype=np.float64)
    if X.ndim!=2 or X.shape[0] < 1:
        return None
    Xc=X-X.mean(axis=0,keepdims=True)
    S=(Xc.T@Xc)/X.shape[0]
    tr=float(np.trace(S)); den=float(np.sum(S*S))
    return (tr*tr/den) if den>0 else None


def _mean_abs_phi(B):
    B=np.asarray(B,dtype=np.float64)
    sd=B.std(axis=0)
    keep=np.flatnonzero(sd>0)
    if len(keep)<2:
        return None, int(len(keep))
    Z=(B[:,keep]-B[:,keep].mean(axis=0))/B[:,keep].std(axis=0)
    R=(Z.T@Z)/B.shape[0]
    tri=np.triu_indices(len(keep),1)
    return float(np.mean(np.abs(R[tri]))), int(len(keep))


def _dup_fraction(B):
    B=np.asarray(B)
    if B.ndim!=2 or B.shape[0]==0:
        return None
    packed=np.packbits(B>0,axis=1,bitorder='little')
    _,counts=np.unique(packed,axis=0,return_counts=True)
    return float(counts[counts>1].sum()/B.shape[0])


def _subset(B,idx):
    X=B[:,idx]
    phi,n_valid=_mean_abs_phi(X)
    return {
      'mean_abs_phi':phi,
      'phi_valid_bits':n_valid,
      'sign_effdim':_effdim_cov(X),
      'dup_fraction':_dup_fraction(X),
    }


def archive_geometry_v2(C):
    C=np.asarray(C,dtype=np.float64)
    if C.ndim!=2 or C.shape[1]!=96 or C.shape[0]<1:
        raise ValueError('C must be non-empty N x 96')
    if not np.isfinite(C).all():
        raise ValueError('C must be finite')
    v=np.mean(C*C,axis=0)
    mv=float(v.mean()); s1=float(v.sum()); s2=float(np.sum(v*v))
    order=np.argsort(v,kind='stable')[::-1]
    top=order[:64]; bot=order[-64:]
    B=np.where(C>=0.0,1,-1).astype(np.int8)
    top_s=_subset(B,top); bot_s=_subset(B,bot)
    return {
      'VAR_CV':float(v.std()/mv) if mv>0 else None,
      'EFF_COORD':float(s1*s1/s2) if s2>0 else None,
      'TOP64_VAR_SHARE':float(v[top].sum()/s1) if s1>0 else None,
      'SIGN_IMBALANCE':float(np.mean(np.abs(B.mean(axis=0)))),
      'top64':top.tolist(),
      'bot64':bot.tolist(),
      'MEAN_ABS_PHI_TOP64':top_s['mean_abs_phi'],
      'MEAN_ABS_PHI_BOT64':bot_s['mean_abs_phi'],
      'PHI_VALID_BITS_TOP64':top_s['phi_valid_bits'],
      'PHI_VALID_BITS_BOT64':bot_s['phi_valid_bits'],
      'PHI_GAP':None if top_s['mean_abs_phi'] is None or bot_s['mean_abs_phi'] is None else top_s['mean_abs_phi']-bot_s['mean_abs_phi'],
      'SIGN_EFFDIM_TOP64':top_s['sign_effdim'],
      'SIGN_EFFDIM_BOT64':bot_s['sign_effdim'],
      'EFFDIM_GAP':None if top_s['sign_effdim'] is None or bot_s['sign_effdim'] is None else bot_s['sign_effdim']-top_s['sign_effdim'],
      'DUP_FRAC_TOP64':top_s['dup_fraction'],
      'DUP_FRAC_BOT64':bot_s['dup_fraction'],
      'DUP_GAP':None if top_s['dup_fraction'] is None or bot_s['dup_fraction'] is None else top_s['dup_fraction']-bot_s['dup_fraction'],
    }


def query_geometry(q):
    q=np.asarray(q,dtype=np.float64).reshape(-1)
    if q.shape!=(96,) or not np.isfinite(q).all():
        raise ValueError('qC must be finite length-96')
    a=np.abs(q); ma=float(a.mean()); s1=float(a.sum()); s2=float(np.sum(q*q))
    return {
      'Q_ABS_CV':float(a.std()/ma) if ma>0 else None,
      'Q_EFF':float(s1*s1/s2) if s2>0 else None,
    }
