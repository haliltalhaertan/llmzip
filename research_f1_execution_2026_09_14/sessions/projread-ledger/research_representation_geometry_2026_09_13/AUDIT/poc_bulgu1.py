# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BULGU-1 tekrar-üretimi: certify_v2 yanlis belge (ISOLATED_TIES/-1, gercek VARIES).

Kosma (paketlere yazmaz):
  OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -B poc_bulgu1.py
Beklenen: v2 ISOLATED_TIES/-1 derken z=5/4 ve 3/2'de gercek +1 (CELISKI).
"""
import sys
sys.path.insert(0, "/home/mdp/muse-work/fix_rank_cert/out")
from fractions import Fraction as F
import certify_v2 as V
import verify_orig_copy as O

K = 100
p = V.P4(-1 * K, 1 * K, 0, 1 * K * K)
q = V.P4(-2 * K, 2 * K, 7 * K * K, 0)
L, R = F(1), F(4)

rr, sk = V.rational_roots(V.P_coeffs(p, q))
print("rational_roots skipped:", sk)
truth = {z: V.cmp_rank(p, q, z) for z in (F(5, 4), F(3, 2), F(7, 4), F(5, 2), F(4))}
print("gercek hukumler:", {str(k): v for k, v in truth.items()})
rv = V.certify_pair(p, q, L, R)
print("v2:", rv["status"], rv["direction"], rv["ties"])
ro = O.certify_pair(p, q, L, R)
print("orig:", ro["status"])
p0, q0 = V.P4(-1, 1, 0, 1), V.P4(-2, 2, 7, 0)
rv0 = V.certify_pair(p0, q0, L, R)
print("v2-olceksiz:", rv0["status"], rv0["direction"], rv0["ties"])
assert sk is True
assert truth[F(5, 4)] == 1 and truth[F(5, 2)] == -1  # gercek VARIES
assert (rv["status"], rv["direction"]) == ("ISOLATED_TIES", -1)  # sahte belge
print("POC DOGRULANDI: v2 yanlis belgeliyor.")
