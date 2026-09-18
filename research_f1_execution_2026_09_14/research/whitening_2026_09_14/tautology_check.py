import numpy as np
rng=np.random.default_rng(0)
C=rng.normal(size=(500,96)); sig=C.std(axis=0)
a=(C>=0); b=((C/sig)>=0)
print("sign(x) == sign(x/sigma) for all entries:", bool((a==b).all()))
print("-> dividing by a POSITIVE per-axis sigma cannot change a sign bit.")
print("   My signwhit arm was VACUOUS BY CONSTRUCTION; the +0.0000 pp was a tautology,")
print("   not a measurement. Disclosed.")
