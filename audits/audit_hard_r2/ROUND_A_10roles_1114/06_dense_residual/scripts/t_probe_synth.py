"""Synthetic benign probes on COPIES only. No source mutation, no gold, no downloads."""
import sys, inspect
sys.path.insert(0, "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/06_dense_residual/copies")
import numpy as np
import lib_residual8 as R
import lib_b8 as B

out = []
# T1 byte budgets
def min_bytes(bits): return (bits + 7)//8
cases = {"SIGN96":96, "R4":100, "R8":104, "R16":112, "residual8_pilot[96+8]":104, "B8[88+8]":96, "SIGN88":88}
for k,v in cases.items():
    out.append(f"T1 {k} bits={v} min_bytes={min_bytes(v)}")
assert min_bytes(96)==12 and min_bytes(100)==13 and min_bytes(104)==13 and min_bytes(112)==14

# T1b packbits roundtrip on synthetic
rng = np.random.default_rng(0)
C = rng.standard_normal((5,96))
st = R.encode_archive(C)
assert st["packed"].shape==(5,13) and st["packed"].dtype==np.uint8
s,m = R.decode_packed(st["packed"])
assert s.shape==(5,96) and m.shape==(5,8)
# roundtrip: re-pack equals stored
rs = np.packbits(s,axis=1,bitorder="big"); rm = np.packbits(m,axis=1,bitorder="big")
assert np.array_equal(np.concatenate([rs,rm],axis=1), st["packed"])
out.append(f"T1b residual8 pack roundtrip OK shape={st['packed'].shape} bytes_per_doc=13 shared_axes=8B+thr64B=72B content")
# B8 payload
stb = B.fit_archive(C)
pb = B.encode_docs(C, stb)
assert pb.shape==(5,12)
out.append(f"T1c B8 pack OK shape={pb.shape} bytes_per_doc=12 shared=80B/archive (drop8+sel8+thr64)")

# T2 tie-only non-inversion (residual8 MAG8): stride must exceed residual range
# residual range: w in {1,2,4} products? (1+m_d)(1+m_q) in {1,2,4}; signed sum over 8 axes in [-32,+32]
assert R.STRIDE_MAG8==65 > 64 and R.STRIDE_SIGN8==17 > 16 and R.STRIDE_RAND8==9 > 8
# brute force: any pair with H differing cannot invert
rng2 = np.random.default_rng(1)
C2 = rng2.standard_normal((6,96)); st2=R.encode_archive(C2)
q = rng2.standard_normal(96); enc=R.encode_query(q, st2["axes"], st2["thresholds"])
sc = R.mag8_scores(st2["packed"], enc, st2["axes"])
H = R.hamming96(st2["packed"], enc["signs96"])
for i in range(6):
    for j in range(6):
        if H[i] < H[j]: assert sc[i] > sc[j], (i,j,H[i],H[j],sc[i],sc[j])
out.append("T2 MAG8 tie-only non-inversion OK on 6-doc synthetic (strict H order preserved)")
# SIGN_ONLY8 same
sc8 = R.signonly8_scores(st2["packed"], enc, st2["axes"])
for i in range(6):
    for j in range(6):
        if H[i] < H[j]: assert sc8[i] > sc8[j]
out.append("T2b SIGN_ONLY8 non-inversion OK")

# T3 code-only vs FLOAT oracle: inspect signatures consume float query?
out.append(f"T3 mag8_scores params={inspect.signature(R.mag8_scores)} (packed+encoded_query+axis_map; NO doc floats; query enters only via 8-axis quantized s8/m01 + packed signs)")
out.append(f"T3 asym_sign96_scores uses FULL float q: {inspect.getsource(B.asym_sign96_scores).strip()[:120]}")
out.append(f"T3 b8_scores uses FULL float q: {inspect.getsource(B.b8_scores).strip()[:120]}")
# fixture: asym consumes float precision, sym does not
q2 = np.array([-1.0,-4.0,-1.0]); D = np.array([[-9.0,1.0,-9.0],[1.0,-4.0,9.0]])
# pad to 96 dims with zeros? use direct cosine_from_code on 3-dim reconstruction analogue
P = np.where(D>=0,1.0,-1.0)
def cos_code(Rr,qq): return (Rr@qq)/(np.linalg.norm(Rr,axis=1)*np.linalg.norm(qq))
a_full = cos_code(P,q2)
q_q = np.where(q2>=0,1.0,-1.0)
a_q = cos_code(P,q_q)
out.append(f"T3 fixture asym float-q scores={a_full.round(4).tolist()} vs quantized-q scores={a_q.round(4).tolist()} (differ => consumes float query precision)")
h = np.count_nonzero((D>=0)!=(q2>=0),axis=1)
out.append(f"T3 sym Hamming={h.tolist()} (code-only both sides)")

# T5 leakage: select_axes signature has no query/gold
out.append(f"T5 residual8 select_axes source: {inspect.getsource(R.select_axes).strip()[:200]}")
assert "q" not in inspect.signature(R.select_axes).parameters and "gold" not in inspect.signature(R.select_axes).parameters
out.append("T5 select_axes(C) only: doc-only fit confirmed by signature; thresholds median(abs(C)) doc-fitted, query never fit (encode_query takes stored thr)")
# B8 fit same
assert "q" not in inspect.signature(B.fit_archive).parameters
out.append("T5b B8 fit_archive(C) only: doc-only confirmed")

# T6 dense-MRL arithmetic: isotropic null f at 1/8
out.append(f"T6 96/768={96/768:.4f} 12/96={12/96:.4f} isotropic null ~12.5% matches report 12.49-12.51% (k/n scaling)")
# loglog_fit copy check: p=-slope
v = np.array([10.0,5.0,2.5,1.25]); x=np.log(np.arange(1,5)); y=np.log(v)
slope,_=np.polyfit(x,y,1); out.append(f"T6 loglog p={-slope:.4f} (convention p=-slope, no division)")

print("\n".join(out))
