import sys
sys.path.insert(0, "/mnt/c/Users/MDP/dev/llmzip-work/harness/ref")
import numpy as np
import measure_representation_diagnostics as m
# C1: exact-zero matrix 4x96
z = np.zeros((4,96))
d = m.matrix_diagnostics(z)
print("zeros: ge=%.6f gt=%.6f zm=%.6f cv=%s D4=%s resid=%.3g" % (d['sign_entropy_ge'], d['sign_entropy_gt'], d['zero_mass'], d['cv_sigma'], d['correlation_proxy'], d['residual_mean_max_abs']))
# C2: perfect correlation pair (cols 0,1 = scaled copies), rest constant zero variance? use random others? use frozen-style: y[:,0]=[-1,0,0,1], y[:,1]=[-2,0,0,2]
y=np.zeros((4,96)); y[:,0]=[-1,0,0,1]; y[:,1]=[-2,0,0,2]
d2=m.matrix_diagnostics(y)
print("perfect-corr: active=%d off_mass=%.12f expect=%.12f median=%.6f p95=%.6f" % (d2['active_coordinates'], d2['correlation_proxy']['off_mass'], 1/np.sqrt(2), d2['correlation_proxy']['median_abs'], d2['correlation_proxy']['p95_abs']))
# C3: checkerboard +-1 (no zeros): occupancy 0.5 each coord -> entropy exactly 1.0
c = np.tile([[-1.,1.]], (50,48))
print("checker shapes", c.shape, "ge=", m.matrix_diagnostics(c)['sign_entropy_ge'], "gt=", m.matrix_diagnostics(c)['sign_entropy_gt'], "zm=", m.matrix_diagnostics(c)['zero_mass'])
# C4: single active coordinate only -> D4 null
s=np.zeros((5,96)); s[:,7]=[-2,-1,0,1,2]
d4=m.matrix_diagnostics(s)
print("single-active: active=%d D4=%s cv=%s" % (d4['active_coordinates'], d4['correlation_proxy'], d4['cv_sigma']))
# C5: zeros present shift ge vs gt: col [-1,0,0,1]: p_ge=0.75 -> H=0.811278; p_gt=0.25 -> H=0.811278 (symmetric) — use [-2,0,1,1]: p_ge=0.75,p_gt=0.5
a=np.zeros((4,96)); a[:,0]=[-2,0,1,1]
da=m.matrix_diagnostics(a)
print("zero-col: ge=%.6f gt=%.6f zm=%.6f" % (da['sign_entropy_ge'], da['sign_entropy_gt'], da['zero_mass']))
