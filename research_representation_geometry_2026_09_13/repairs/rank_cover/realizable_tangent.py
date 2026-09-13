# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""realizable_tangent.py — C2: gerceklesebilir teget ornegi + vektor insasi.

Sorgu paylasimli, rasyonel vektorler (tum girisler Fraction):
  tamamlayici blok (2 boy): qc=[1,1/2], c1=[1,1], c2=[1,0]
  grup blogu (1 boy): qg=[1/2], g1=[2], g2=[0]
  toplam boy 3, sabit grup G = {2} (0-bazli son koordinat).
Turetim: a=qc.c, b=qg.g, u=||c||^2, v=||g||^2.
Hedef: (3/2,1,2,4) karsi (1,0,1,0), P=(z-1/2)^2, hukum [1,0,1].

Kullanim:
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B realizable_tangent.py
Stdlib-only. Cikis sifirdan farkliysa bir beklenti bozulmustur.
Bagimsiz denetimden GECMEMISTIR.
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import coverage_v2 as C

CHECKS = []
def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail)))
    if not cond:
        print("FAIL", name, detail, flush=True)

def dot(x, y):
    return sum(a * b for a, b in zip(x, y))

def n2(x):
    return dot(x, x)

def tup_from_blocks(qc, qg, c, g):
    return (dot(qc, c), dot(qg, g), n2(c), n2(g))

def single_ok(a, b, u, v):
    if not (u >= 0 and v >= 0):
        return False
    if u == 0 and a != 0:
        return False
    if v == 0 and b != 0:
        return False
    return True

def main():
    qc = [F(1), F(1, 2)]
    c1 = [F(1), F(1)]
    c2 = [F(1), F(0)]
    qg = [F(1, 2)]
    g1 = [F(2)]
    g2 = [F(0)]
    t1 = tup_from_blocks(qc, qg, c1, g1)
    t2 = tup_from_blocks(qc, qg, c2, g2)
    check("C2-tuple1", t1 == (F(3, 2), F(1), F(2), F(4)), t1)
    check("C2-tuple2", t2 == (F(1), F(0), F(1), F(0)), t2)
    check("C2-shared-query", True, "ayni qc,qg iki belgede")
    check("C2-single-ok1", single_ok(*t1), t1)
    check("C2-single-ok2", single_ok(*t2), t2)
    p, q = C.P4(*t1), C.P4(*t2)
    P = C.P_coeffs(p, q)
    check("C2-P-dual", P == C.audit_P_coeffs(p, q), P)
    check("C2-P-square", P == [F(1, 4), F(-1), F(1), F(0)], P)
    check("C2-P-factors", C.peval(P, F(1, 2)) == 0
          and C.peval([F(1, 4), F(-1), F(1)], F(1, 4)) == F(1, 16), P)
    zs = [F(1, 4), F(1, 2), F(1)]
    got = [C.cmp_rank(p, q, z) for z in zs]
    aud = [C.audit_cmp(p, q, z) for z in zs]
    check("C2-verdicts-101", got == [1, 0, 1], got)
    check("C2-audit-agrees", aud == got, aud)
    r = C.certify_pair_orig(p, q, F(1, 4), F(1))
    check("C2-cert-touch", r["status"] == "ISOLATED_TIES"
          and r["direction"] == 1 and r["ties"] == ["1/2"], r)
    # S4 karsitligi: soyut-ailede gecerli, gerceklesemez (u=0, a!=0)
    e1 = (F(1), F(1), F(0), F(4))
    check("C2-S4-abstract-only", not single_ok(*e1), e1)
    fails = [n for (n, ok, _) in CHECKS if not ok]
    print("checks=%d fail=%d" % (len(CHECKS), len(fails)), flush=True)
    print("vektorler: qc=%s c1=%s c2=%s qg=%s g1=%s g2=%s" % (qc, c1, c2, qg, g1, g2), flush=True)
    print("P=%s hukum=%s" % ([str(c) for c in P], got), flush=True)
    if fails:
        print("FAILED:", fails, flush=True)
        sys.exit(1)
    print("ALL PASS", flush=True)

if __name__ == "__main__":
    main()
