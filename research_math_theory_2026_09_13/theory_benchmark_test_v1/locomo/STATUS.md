# STATUS — LoCoMo Model-H transfer (exploratory)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

- Workspace: /home/mdp/muse-work/theorybench-locomo (isolated outputs only)
- Source root (READ ONLY): /mnt/c/Users/MDP/dev/llmzip-work
- PLAN sealed: PLAN.md copied byte-exact, sha256 a0f9e8e6eb214e0129cb5b8e31d35bdb75599eb130332a7eed7780bdc8981a21, 6402 bytes
- Task: LoCoMo transfer only. No pooling, no PerLTQA tuning, no training/embeddings/API.
- Gate first: reproduce native SIGN96 = 0.23654714666441054 on 1535 valid QA + centered-float96 arrays; abort interventions on gate failure.
- Constraints: threads=1 env, PYTHONDONTWRITEBYTECODE=1, ml-python -B, no source writes, no push, no network/install.
- State: DONE (first pass complete).
- Gate: PASS — sign MC diff 0.0; per-QA vs npz 1.1e-16; vs perq exp 0.0; vs official MC bitwise 0.0. Counts 1540/1535/5/10 by code.
- Float baseline (fresh, sealed): 0.16826334541318252 (exp and MC).
- Outcome: PRIMARY NEGATIVE — LOW48 contrast -0.025829067783465175, CI [-0.03776758909603851, -0.013132051635781277] (wrong sign; falsifies proxy/transfer, not theorem).
- Controls: sign byte-identical across t; FULL96 bitwise invariant; t=1 identity exact.
- verification.py: 33/33 PASS. Sources unchanged (hashes after == before).
