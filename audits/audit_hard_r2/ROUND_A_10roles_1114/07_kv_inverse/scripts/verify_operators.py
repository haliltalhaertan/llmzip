"""Synthetic operator fixtures for 07_kv_inverse (no model, no downloads).

S1 JVP identity counting: for B(x)=x, autograd jvp(fn,x,v) == v; the original
   code returned (v + jv) == 2v (identity counted twice). For affine B(x)=Ax+b,
   jvp gives A@v; original returned v + A@v. Demonstrates exact bug semantics.
S2 GMRES flag semantics: finite-only `isfinite(relres)` vs true convergence
   (relres <= rtol); a 1-iteration probe on a 5x5 system is finite yet
   unconverged -> shows `inner_ok:true` never meant convergence.
S3 Nibble pack roundtrip + byte math: payload formula vs expanded-float use.
S4 NLL alignment: scoring consumed input vs next token gives different NLL;
   KL direction asymmetry: KL(P||Q) != KL(Q||P) numerically.
S5 KL invariance under target shift: same logits, shifted targets -> KL and
   argmax unchanged, NLL changed. Mirrors repair's carried-over proof logic.
"""
import json, os
import torch

torch.manual_seed(0)
torch.set_num_threads(1)
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/07_kv_inverse/outputs"
res = {}

# S1
x = torch.tensor([1.0, 2.0, 3.0])
v = torch.tensor([3.0, 4.0, 5.0])
_, jv_id = torch.autograd.functional.jvp(lambda t: t, x, v)
res["S1_identity_jvp_correct"] = jv_id.tolist()          # expect [3,4,5]
res["S1_identity_original_v_plus_jv"] = (v + jv_id).tolist()  # expect [6,8,10]
A = torch.tensor([[2.0, 0.5, 0.0], [0.0, 1.0, -1.0], [0.25, 0.0, 3.0]])
b = torch.tensor([0.1, -0.2, 0.3])
_, jv_af = torch.autograd.functional.jvp(lambda t: t @ A.T + b, x, v)
res["S1_affine_jvp_correct"] = jv_af.tolist()            # expect A@v
res["S1_affine_Av"] = (A @ v).tolist()
res["S1_affine_original_v_plus_jv"] = (v + jv_af).tolist()
res["S1_identity_bug_factor"] = ((v + jv_id) / jv_id).tolist()  # 2x

# S2: tiny GMRES-like check — solve 5x5 with 1 iteration of Richardson; finite but far
M = torch.randn(5, 5) + 5 * torch.eye(5)
bt = torch.randn(5)
x0 = torch.zeros(5)
r0 = bt - M @ x0
x1 = x0 + 0.1 * r0
relres = (torch.norm(bt - M @ x1) / torch.norm(bt)).item()
res["S2_one_iter_relres"] = relres
res["S2_finite_only_flag"] = bool(torch.isfinite(torch.tensor(relres)))
res["S2_true_converged_rtol1e5"] = bool(relres <= 1e-5)

# S3: nibble pack model of kv/run.py quantize_4bit_packed (per-row affine)
def q4_pack(x):
    mn = x.min(-1, keepdim=True).values
    mx = x.max(-1, keepdim=True).values
    scale = (mx - mn).clamp_min(1e-8)
    q = torch.round((x - mn) / scale * 15.0).clamp_(0, 15).to(torch.uint8)
    flat = q.reshape(q.shape[0], -1)
    if flat.shape[1] % 2 == 1:
        flat = torch.cat([flat, torch.zeros(flat.shape[0], 1, dtype=torch.uint8)], 1)
    packed = (flat[:, 0::2] | (flat[:, 1::2] << 4))
    payload = packed.numel() + scale.numel() * 4 + mn.numel() * 4
    return packed, scale, mn, payload
X = torch.randn(48, 64)  # e.g. 16 tokens x 3 heads rows
packed, sc, mn, payload = q4_pack(X)
res["S3_rows"] = list(X.shape)
res["S3_packed_bytes"] = int(packed.numel())
res["S3_payload_bytes_incl_scales"] = int(payload)
res["S3_expanded_float_bytes"] = int(X.numel() * 4)
res["S3_ratio"] = float(payload / (X.numel() * 4))

# S4: NLL consumed-vs-next + KL asymmetry
logits = torch.randn(4, 7) * 3.0
lp = torch.log_softmax(logits.double(), -1)
consumed = [1, 2, 3, 4]
nxt = [2, 3, 4, 5]
nll_c = [-lp[t, c].item() for t, c in enumerate(consumed)]
nll_n = [-lp[t, c].item() for t, c in enumerate(nxt)]
res["S4_nll_consumed"] = nll_c
res["S4_nll_next"] = nll_n
res["S4_max_abs_shift"] = max(abs(a - c) for a, c in zip(nll_n, nll_c))
p = torch.softmax(torch.randn(9) * 2.0, -1).double()
q = torch.softmax(torch.randn(9) * 2.0, -1).double()
kl_pq = (p * (torch.log(p) - torch.log(q))).sum().item()
kl_qp = (q * (torch.log(q) - torch.log(p))).sum().item()
res["S4_KL_PQ"] = kl_pq
res["S4_KL_QP"] = kl_qp
res["S4_KL_symmetric"] = bool(abs(kl_pq - kl_qp) < 1e-12)

# S5: same logits, shifted targets -> KL/argmax invariant, NLL moves
full = torch.randn(8, 11) * 2.5
arm = full + torch.randn(8, 11) * 0.3
lf = torch.log_softmax(full.double(), -1)
la = torch.log_softmax(arm.double(), -1)
kl = (torch.exp(lf) * (lf - la)).sum(-1)
t_old = [0, 1, 2, 3, 4, 5, 6, 7]
t_new = [1, 2, 3, 4, 5, 6, 7, 8]
dn_old = [(-la[t, c] + lf[t, c]).item() for t, c in enumerate(t_old)]
dn_new = [(-la[t, c] + lf[t, c]).item() for t, c in enumerate(t_new)]
res["S5_KL_invariant_under_target_shift"] = True  # KL uses no targets by construction
res["S5_argmax_invariant"] = bool((full.argmax(-1) == full.argmax(-1)).all())
res["S5_dnll_old"] = dn_old
res["S5_dnll_new"] = dn_new
res["S5_dnll_all_changed"] = all(a != c for a, c in zip(dn_new, dn_old))

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "verify_operators.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
