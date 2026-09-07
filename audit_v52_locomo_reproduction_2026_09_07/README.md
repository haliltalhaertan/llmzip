# Limited LoCoMo reproduction audit, 2026-09-07

This namespace belongs to the cold-context reproduction auditor. Checkpoint and prior result claims are comparison targets, not evidence of a successful reproduction.

User scope receipt: commit `540580cfd87f70443123a3349979ab863e2fccc6`, branch `codex/v52-scale-uncertainty-2026-09-07`, path `reviews/v52/locomo_reproduction_authorization_2026_09_07.md` (parent reported remote publication before computation).

Source baseline: trigger `680b10b8`; audit checkout starts at `591e5d0fd7af8c265ac12a6176761475a19b2f02`. `preflight.py` verifies the trigger-to-seal relation, every seal-bound Git blob against the trigger and audit HEAD, and the transitive LoCoMo common source blob `6700454915176854a55b0b5cf6ffe922a22e35f2`. Execution sources are extracted from raw Git blobs to a separate temporary directory to avoid Windows checkout line-ending changes. Original source, seal, and research outputs are not edited.

Required numerical versions: Python 3.13, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, scikit-learn 1.8.0. This is a Windows run; the original workflow used Ubuntu. Exact package versions do not imply identical BLAS, compiler, architecture, or floating-point accumulation. Those differences must be disclosed, not repaired by tuning.

The preflight downloads and independently verifies the source corpus and all 20 audit correction files through the sealed common module's acquisition checks. Its dataset parser verifies 10 archives, 1,540 category-selected questions, and 156 corrections, without fitting or ranking. The runner itself re-downloads and re-verifies the source files before fitting. Source bytes and virtual environment remain in the task-specific temporary directory outside this Git checkout.

Only one real invocation is permitted, after readiness is communicated to the parent and the gate receipt is published. It uses every original seed 59001 through 59010 and all six original arms. No bootstrap, additional seed, method adjustment, LongMemEval rerun, GitHub Actions invocation, BEAM/Task4F1 execution, or HMAC operation is authorized.

`compare.py` compares gzip bytes, decompressed CSV bytes, and keyed question-level numeric values at absolute tolerance 1e-12. It requires 92,100 rows, 1,535 unique questions, the full ten-seed panel, and six arms. Duplicate keys, missing rows, changed seed, metadata drift, and nonfinite numeric values are rejected. A numeric perturbation must fail the numerical tolerance. All negative controls are synthetic. The saved CSV contains scores, not retrieval document IDs: score agreement does not establish identical top-three selections.

Commands and actual status are recorded in the machine-readable gate/run/comparison receipts and final report. A failed gate means BLOCKED with no fitting/ranking. Any run failure or comparison mismatch is retained without retry.
