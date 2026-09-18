# Task 2: shared-state storage accounting

Scope: synthetic storage measurements and the pinned T4C2 N_archive column only.
No queries, distances, rankings, recall, corpus/gold, Task 1, Task 3, OPQ fit,
preregistration edit, seal or HMAC operation. G3 is untouched.

Base: `ae9175676b840ae6a80a31eba9836187dc1b7491`.
Worker branch: `codex/v52-preseal-cost-worker-2026-09-12`.
Parent integrates this task after Task 1; the worker owns only the root
`measure_shared_state_cost.py` script and this `task2/` directory. Root
README/RESULTS/HASHES and other task files belong to the parent.

The executable result is `task2/RESULTS.json`, with `status`, `environment`,
source identities, per-arm training/addition measurements, integer checks and
limits. `task2/ENVIRONMENT.json` separately identifies runtime versions and binary
hashes. `task2/SOURCE_REFERENCES.json` records the producer hash, pinned raw Git
cardinality blob and exact upstream Faiss source hashes/URLs. No upstream hash
claims that the installed wheel was built from that commit.

Run with the authorized environment, from the repository root:

```powershell
& 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/.venvs/faiss-replay-20260912/Scripts/python.exe' research/v52/preseal_diagnostics_2026_09_12/measure_shared_state_cost.py
```

Only the script and files under task2/ are produced/changed. Official Faiss source
hashes are fetched from the pinned upstream commit, so source receipt generation
requires network access. No research script is imported. The native Faiss warnings
are captured in `FAISS_TRAINING_WARNINGS.log`; training succeeds/fails independently
of the points-per-centroid reliability recommendation, which is reported explicitly.

Synthetic training inputs have n=256,257,1000; each resulting fitted/fixed state is
serialized at added n=0,1,256,257,1000 without retraining between additions. Actual
integer differences must equal n times the declared marginal bytes. The declared
cap is <=12 B/vector (SIGN32 uses4); no approximate slope regression or byte
tolerance is used. Negative controls reject16-byte two-uint64 packing, extra bytes,
over-cap declarations, and noninteger accounting. Code plane roundtrips test zeros
and threshold equality. Faiss index and transform serializers roundtrip their bytes.

Definitions and limitations:

Measured storage summary (bytes; identical shared sizes at all three training
input counts). Effective means use each of the 470 pinned archive cardinalities:

| Package | Marginal/vector | Raw fitted | Raw nonfitted | Headers/configuration | Shared/archive | Mean effective/vector |
|---|---:|---:|---:|---:|---:|---:|
| SIGN96 + BinaryFlat | 12 | 0 | 0 | 33 | 33 | 12.067229 |
| SIGN32 + BinaryFlat | 4 | 0 | 0 | 33 | 33 | 4.067229 |
| QuIVer-style48x2 compact | 12 | 0 | 0 | 0 | 0 | 12.000000 |
| ITQ96 matrix surrogate + BinaryFlat | 12 | 0 | 36864 | 71 | 36935 | 87.245314 |
| PQ96 m12x8 | 12 | 98304 | 0 | 86 | 98390 | 212.443657 |
| Plain RQ32 | 12 | 128 | 0 | 74 | 202 | 12.411522 |
| RandomRotationMatrix + RQ32 wrapper | 12 | 128 | 4096 | 145 | 4369 | 20.900684 |

Plain RQ32's 202 bytes are 128 centroid bytes plus 74 bytes of serialized
configuration/header. No rotation is present. The explicit rotated wrapper stores
4096 matrix bytes: rotation serialization is 4126 bytes, inner RQ32 is 202 bytes,
and the pretransform wrapper adds 41 bytes. This is not a four-byte seed state.
RQ32's per-vector 12 bytes comprise 4 sign-code bytes and two float32 factors.
These are package measurements, not a complete retrieval-system byte budget.

- SIGN96/SIGN32: deterministic packed synthetic sign codes and a real BinaryFlat
  code store. Zero algorithm-specific learned state does not remove its header.
- QuIVer-style48x2: strict `>0` sign, strict `abs(x)>mean(abs(x))` magnitude;
  two6-byte planes per row. The pure serializer has no Faiss header and no fitted
  state. It is not the complete QuIVer graph/reranking system. Thresholds are not
  retained per vector. There is no scoring function in this producer.
- ITQ96_MATRIX_SURROGATE: a seeded synthetic orthogonal96x96 float32 matrix is
  installed in an ITQMatrix serializer and paired with a BinaryFlat code store.
  The serialized `is_trained=true` flag identifies a populated matrix object,
  **not an ITQ fit**. Fitted-content bytes are zero in this probe; the36,864-byte
  matrix is explicitly nonfitted surrogate content. Actual ITQ fit/training
  identity, convergence and stability belong to Task 3 and are not claimed here.
- PQ96_M12X8: actual synthetic archive-local PQ training,10 iterations, explicit
  seed; a storage probe, not an approved retrieval training configuration.
- RQ32_PLAIN_NO_ROTATION: actual centroid fit, actual factor/code storage, no
  internal random rotation or rotation seed. This is not silently labeled a
  complete implementation of the paper's randomized quantizer assumptions.
- RQ32_RANDOM_ROTATION_WRAPPER: explicitly initialized RandomRotationMatrix plus
  IndexRaBitQ inside IndexPreTransform. The populated rotation survives training;
  the wrapper serializer stores the matrix, not only a seed.

Shared state is split into fitted raw content, nonfitted raw content, and actual
serialization/configuration overhead. **Common preprocessing is unmeasured/unknown,
not zero.** Each effective cost and shared/(N*marginal) ratio is package-only and
uses the archive's own N, from the authorized pinned T4C2 column. The470-row source
is not presented as a LoCoMo result. The CSV outputs only N, source-row ordinal and
storage arithmetic, without question IDs or any quality column. Mean per-archive
effective cost is distinguished from cost at mean N.

`serialized_examples/` contains actual package bytes for training n1000 and added
n0/n1000. Their lengths/hashes are in RESULTS. They are reproducibility evidence;
duplicated evidence files are not counted as additional deployed model state.

`task2/HASHES.txt` hashes the script and every task2 payload file, using paths
relative to the preseal directory. It excludes itself, avoiding recursive self-hash.
No root manifest, ledger/state or literature assessment is modified. Completion of
this task is not retrieval-runner integration approval or seal authorization.
