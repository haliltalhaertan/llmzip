"""Self-test for the runner's pure functions, on synthetic data only.

The full runner cannot be exercised here because the corpus is not in git. What CAN be tested is
every function that does not touch the corpus - and those are where the design premises live.
No corpus, no benchmark outcome, no Task 4F1 contact.
"""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("runner", HERE / "locomo_coordinate_scale.py")
r = importlib.util.module_from_spec(spec); sys.modules["runner"] = r
try:
    spec.loader.exec_module(r)
except Exception as e:                      # pandas/base import may be unavailable; functions still testable
    print(f"note: module exec raised ({type(e).__name__}); re-loading source-only")
    raise

class FakeBase:
    @staticmethod
    def haar_q(rng, d):
        A = rng.standard_normal((d, d)); Q, R = np.linalg.qr(A)
        return Q * np.where(np.diag(R) < 0, -1.0, 1.0)[None, :]

fails = 0
def check(name, ok, detail=""):
    global fails
    print(("ok    " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok: fails += 1

rng = np.random.default_rng(0)
sd = 0.93 ** np.arange(96)
C = rng.standard_normal((300, 96)) * sd
QC = rng.standard_normal((12, 96)) * sd
C = C - C.mean(axis=0); QC = QC - QC.mean(axis=0)

D, ndeg, cv = r.scale_matrix(C)
check("scale_matrix returns a positive diagonal", bool(np.all(np.diag(D) > 0)) and np.count_nonzero(D - np.diag(np.diag(D))) == 0)
check("no degenerate coordinates in a healthy archive", ndeg == 0, f"cv_before={cv:.3f}")
check("rescaling equalises variance", abs((C @ D).std(axis=0).std()) < 1e-9)

r.check_identity(C, QC, D)
check("sign(xD) = sign(x) holds bit-identically", True)

Cd = C.copy(); Cd[:, -7:] = 0.0                      # 7 truly dead coordinates
Dd, ndeg_d, _ = r.scale_matrix(Cd)
check("degenerate coordinates fall back to d=1", ndeg_d == 7 and np.allclose(np.diag(Dd)[-7:], 1.0), f"n={ndeg_d}")
r.check_identity(Cd, QC, Dd)
check("identity survives degenerate fallback", True)

bad = np.diag(np.r_[np.ones(95), -1.0])              # a NEGATIVE diagonal must be rejected
try:
    r.check_identity(C, QC, bad); check("negative diagonal is rejected", False, "identity check passed a sign flip")
except RuntimeError:
    check("negative diagonal is rejected", True)

Rb = r.block_matrix(FakeBase, 59001)
check("block matrix is orthogonal", float(np.max(np.abs(Rb.T @ Rb - np.eye(96)))) < 1e-12)
check("block matrix is block-diagonal at 32", np.all(Rb[:32, 32:] == 0) and np.all(Rb[32:, :32] == 0))
Rb2 = r.block_matrix(FakeBase, 59001)
check("block matrix is deterministic in its seed", np.array_equal(Rb, Rb2))
Rf = r.full_matrix(FakeBase, 59001)
check("full matrix is orthogonal", float(np.max(np.abs(Rf.T @ Rf - np.eye(96)))) < 1e-12)
check("full and block matrices differ", float(np.max(np.abs(Rf - Rb))) > 0.1)

n, d = r.check_rotation_invariance(C @ D, Rf)
check("norm/dot invariance holds WITHIN the rescaled representation", n < 1e-12 and d < 1e-9, f"norm={n:.2e} dot={d:.2e}")
n2, _ = r.check_rotation_invariance(C, Rf)
check("norm/dot invariance holds WITHIN the original representation", n2 < 1e-12)
check("invariance is NOT claimed between original and rescaled",
      float(np.max(np.abs(np.linalg.norm(C @ D, axis=1) - np.linalg.norm(C, axis=1)))) > 1e-6)

check("frac = 1 when rescaling fully restores native", abs(r.frac(0.5, 0.3, 0.5) - 1.0) < 1e-15)
check("frac = 0 when rescaling does nothing", abs(r.frac(0.5, 0.3, 0.3)) < 1e-15)
check("frac may exceed 1 (overshoot admitted)", r.frac(0.5, 0.3, 0.6) > 1.0)
check("frac is nan on a zero denominator", not np.isfinite(r.frac(0.5, 0.5, 0.6)))
check("band: >= 0.70 -> most", r.band(0.70).startswith("[SCALE ACCOUNTS FOR MOST"))
check("band: <= 0.20 -> little", r.band(0.20).startswith("[SCALE ACCOUNTS FOR LITTLE"))
check("band: between -> partial", r.band(0.45) == "[PARTIAL]")
check("band admits overshoot", r.band(1.4).startswith("[SCALE ACCOUNTS FOR MOST"))

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
raise SystemExit(1 if fails else 0)
