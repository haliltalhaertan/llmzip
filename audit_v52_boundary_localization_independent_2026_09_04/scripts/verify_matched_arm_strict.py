#!/usr/bin/env python3
"""Gate H (strict) — the RANDOM32 arm must place the SAME numeric Q32/Q64 as the
spectral B32 arm, differing only in coordinate membership (prereg SS7.2)."""
import json, numpy as np
ROT=list(range(58001,58011)); PART=list(range(68001,68011))
def haar_q(rng,d):
    A=rng.standard_normal((d,d)); Q,R=np.linalg.qr(A)
    return Q*np.where(np.diag(R)<0,-1.0,1.0)[None,:]
def bmat(seed,b):
    rng=np.random.default_rng(seed); qh=haar_q(rng,b); qt=haar_q(rng,96-b)
    R=np.zeros((96,96)); R[:b,:b]=qh; R[b:,b:]=qt; return R,qh,qt
rep={}; w_blk=0.0; w_orth=0.0; w_spec=0.0
for rs,ps in zip(ROT,PART):
    Rs,q32,q64=bmat(rs,32)                       # spectral B32
    perm=np.random.default_rng(ps).permutation(96).astype(int)
    S,T=perm[:32],perm[32:]
    Rr=np.zeros((96,96)); Rr[np.ix_(S,S)]=q32; Rr[np.ix_(T,T)]=q64
    # extract the blocks back out of the assembled random matrix
    e32=float(np.max(np.abs(Rr[np.ix_(S,S)]-q32)))
    e64=float(np.max(np.abs(Rr[np.ix_(T,T)]-q64)))
    # everything outside the two blocks must be exactly zero
    M=np.ones((96,96),bool); M[np.ix_(S,S)]=False; M[np.ix_(T,T)]=False
    off=float(np.max(np.abs(Rr[M])))
    orth=float(np.max(np.abs(Rr.T@Rr-np.eye(96))))
    # the two arms must NOT be the same matrix (membership genuinely differs)
    spectral_vs_random_diff=float(np.max(np.abs(Rr-Rs)))
    # is the permutation the identity-ordered split? (would collapse the control)
    trivial = bool(np.array_equal(np.sort(S),np.arange(32)))
    rep[str(rs)]={"block32_err":e32,"block64_err":e64,"outside_blocks_max":off,
                  "orthogonality_err":orth,"differs_from_spectral_B32":spectral_vs_random_diff,
                  "partition_is_trivially_leading32":trivial,
                  "n_S32_in_leading32":int(np.sum(S<32))}
    w_blk=max(w_blk,e32,e64,off); w_orth=max(w_orth,orth); w_spec=max(w_spec,spectral_vs_random_diff)
rep["_worst_block_placement_error"]=w_blk
rep["_worst_orthogonality"]=w_orth
rep["_min_difference_from_spectral_arm"]=min(v["differs_from_spectral_B32"] for k,v in rep.items() if k.isdigit())
rep["_any_trivial_partition"]=any(v["partition_is_trivially_leading32"] for k,v in rep.items() if k.isdigit())
json.dump(rep,open("audit_v52_boundary_localization_independent_2026_09_04/evidence/matched_arm_strict.json","w"),indent=2)
print(f"worst block-placement error (Q32/Q64 identity preserved): {w_blk:.3e}")
print(f"worst RANDOM32 orthogonality error                     : {w_orth:.3e}")
print(f"min |R_random - R_spectral| over seeds (must be > 0)   : {rep['_min_difference_from_spectral_arm']:.3f}")
print(f"any partition trivially equal to leading 32 coords     : {rep['_any_trivial_partition']}")
print("overlap |S32 ∩ {0..31}| per seed:", [rep[str(s)]['n_S32_in_leading32'] for s in ROT])
