# Audit script 5: topK characterization cross-checks + number recomputation.
from fractions import Fraction as F
import sys
sys.path.insert(0, "/home/mdp/muse-work/audit_rank/out")
import importlib.util
spec = importlib.util.spec_from_file_location("vc", "/home/mdp/muse-work/audit_rank/out/verify_copy.py")
vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
P4, cmp_rank = vc.P4, vc.cmp_rank

print("=== 1. Thm3a cross-check: topk_cert vs dense exact sampling (consistency, not proof) ===")
import random
random.seed(3)
disagree = 0; tested = 0
for trial in range(300):
    n = random.randint(3, 5); K = random.randint(1, n-1)
    docs = [P4(*[random.randint(-4,4) for _ in range(4)]) for _ in range(n)]
    L = F(random.randint(1,4),4); R = L + F(random.randint(1,6),4)
    prio = {i: i for i in range(n)}
    # domain must hold at all sample points; else skip
    grid = [L + (R-L)*F(i,20) for i in range(21)]
    try:
        for z in grid:
            for d in docs:
                _, D = vc.NZ(d, z)
                if not D > 0: raise vc.DomainError()
    except vc.DomainError:
        continue
    t = vc.topk_cert(docs, K, prio, L, R)
    # reference: prio-sets at grid points
    def pset(z):
        idx = list(range(n))
        for i in range(1, len(idx)):
            j = i
            while j > 0:
                c = cmp_rank(docs[idx[j]], docs[idx[j-1]], z)
                if c > 0 or (c == 0 and prio[idx[j]] < prio[idx[j-1]]):
                    idx[j], idx[j-1] = idx[j-1], idx[j]; j -= 1
                else: break
        return set(idx[:K])
    sets = [pset(z) for z in grid]
    grid_stable = all(s == sets[0] for s in sets)
    tested += 1
    if t["prio"] == "CERTIFIED_STABLE" and not grid_stable:
        disagree += 1; print("DISAGREE stable-but-grid-moves", trial)
    if t["prio"] == "CERTIFIED_UNSTABLE" and grid_stable:
        # unstable verdict needs a witness INSIDE J; grid may miss it -> check witness validity instead
        w = t["unstable_witness"]
        if w is None:
            disagree += 1; print("DISAGREE unstable-no-witness", trial)
print(f"tested={tested} disagreements={disagree}")
print("(CERTIFIED_UNSTABLE with grid-stable is fine iff witness points are in J and exact -- spot-checked below)")

print()
print("=== 2. Unstable-witness validity spot check ===")
t2 = vc.topk_cert([P4(-3,4,5,10), P4(-2,2,2,10), P4(-100,0,1,1)], 1, {0:0,1:1,2:2}, F(1,16), F(16))
print("S6b witness:", t2["unstable_witness"])

print()
print("=== 3. Complete top3 requirements for the LME query ===")
print("n_docs=474 (measured), K=3 -> cross pairs needed: 3*471 =", 3*471)
print("artifact certifies: 1 pair (gold56 vs rival368) on [1/16,1] only.")
print("missing: other 1412 pairs, full J coverage, tie-free-sample In determination, prio rule.")

print()
print("=== 4. Recompute S7 budget arithmetic ===")
V = list(range(-3,4)); QQ = [-2,-1,1,2]
docs11_per = len([(c,g) for c in V for g in V if not (c==0 and g==0)])
pairs_per = docs11_per*(docs11_per-1)//2
print(f"docs/grid={docs11_per} pairs/grid={pairs_per} qq-combos={len(QQ)**2} total={pairs_per*len(QQ)**2} (prose 18048)")

print()
print("=== 5. Recompute S6c expectation values ===")
E1 = P4(1,1,0,4); E2 = P4(1,0,1,0)
print("E @ 1/2,1,2:", [str(vc.expected_gold_topk([E1,E2],{1},1,z)) for z in [F(1,2),F(1),F(2)]],
      "(prose 0,1/2,0)")
A=P4(2,0,1,0); B=P4(1,0,1,0); A2=P4(1,0,1,0); B2=P4(1,0,1,0); C2b=P4(0,0,1,0)
print("non-necessity:", vc.expected_gold_topk([A,B,C2b],{0,1},1,F(1)),
      vc.expected_gold_topk([A2,B2,C2b],{0,1},1,F(1)), "(prose 1,1)")

print()
print("=== 6. Thm1(i) wording check: s_i!=s_j is ALWAYS strict ===")
print("'strict unless both zero' is vacuous: both-zero implies s_i==s_j, excluded by hypothesis.")
print("Minor prose sloppiness REPORT.md:100-101. Math unaffected (code line 57-58 always strict).")

print()
print("=== 7. P==0 single-zero locations lie OUTSIDE domain (unnoted) ===")
print("If P==0 identically and N1(z0)=0,N2(z0)!=0: 0=N2^2 D1 -> D1=0 -> z0 outside D.")
print("So on D, P==0 admits only: same-sign, common-zero, opposite-nonzero. Thm1(iv) complete on D. PASS (silent).")
