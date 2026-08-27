# Independent reproduction — V52 Task 4C2 audit

| Script | Purpose |
|---|---|
| `01_itq_orientation_proof.py` | Proves the adapter's ITQ Procrustes update attains the orthogonal-Procrustes optimum (`tr(MR)` equals the nuclear norm of `M`), that the transposed rule does not, and that the objective decreases monotonically only under the adapter's rule. Also checks orthogonality, determinant, determinism and seed sensitivity. |

Run from the repo root. Requires numpy. It loads
`adapters/longmemeval_v52_adapter.py` directly, so verify its SHA256 first:

```
python3 tools/verify_frozen_artifacts.py
python3 audit_v52_t4c2/repro/01_itq_orientation_proof.py
```

The remaining reproduction was done inline against
`docs/v52/task4c2/V52_T4C2_question_level.csv` (committed) and
`V52_T4C2_trial_results.csv` (Drive; SHA256 `c6d58cdd…` verified on download).
