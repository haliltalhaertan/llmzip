# Baseline draft addendum: distinguish the two RQ32 configurations

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Status: PROPOSED NOMENCLATURE AND IMPLEMENTATION IDENTITY; NOT APPROVED ARMS, NOT SEALED, NO EXECUTION AUTHORIZATION.

Applies as an additive review proposal to baseline draft `a73393a62c6d3feaa78ee322b07b1d151f412c34` (`codex/twelve-byte-prereg-revision-2026-09-12`). No existing preregistration bytes or P1–P5 approvals are changed. This is sufficient to prevent the two paths being silently called the same baseline while retaining the scientific selection gate.

Source: `4001fc9d8ea2c932042de7823713c6efce8e56d0`, `research/v52/preseal_diagnostics_2026_09_12/task2/RESULTS.json`, SHA256 `35bdc2ee68c0f5c37c26b1b082cd6dcfffcec55134a22f1af6290a8f523bc190`.

| Proposed name | Recorded configuration ID | Implemented chain | Marginal bytes/vector | Shared serialized bytes |
|---|---|---|---:|---:|
| `RABITQ32_PLAIN` | `RQ32_PLAIN_NO_ROTATION` | Plain Faiss `IndexRaBitQ`, fitted centroid; no internal random rotation | 12 | 202 |
| `RABITQ32_ROTATED` | `RQ32_RANDOM_ROTATION_WRAPPER` | `IndexPreTransform(RandomRotationMatrix, IndexRaBitQ)` | 12 | 4,369 |

Both counts were measured with Faiss1.15.0; their 12-byte vector code consists of 4 sign-code bytes plus 8 additional factor bytes. The wrapper stores a 4,096-byte float32 rotation matrix; the complete shared-state difference is 4,167 bytes including wrapper/container overhead. These costs exclude common representation preprocessing, which remains unknown rather than zero.

The diagnostic wrapper used seed73002 and recorded query quantizer setting qb=4. These are identities of the cost diagnostic, not a newly approved scientific seed panel or scoring protocol. That diagnostic executed no queries. Final training/scoring/metric, random seed panel, preprocessing/dimension projection, storage boundary, archive-local versus shared deployment, and evaluation protocol must all be declared in the scientific draft before execution.

If proposed as a paired comparison, both paths must receive identical source-bound d32 training/database/query representations and equal evaluation settings, with the transform difference explicitly tracked. Centroid fitting and transformed state are part of the full chain. This can estimate the effect of adding the declared rotation procedure under those controls; neither its sign nor its causal mechanism is established by serialized size measurements.

Do not label the plain path as the complete paper algorithm by default. Do not label the wrapper as theorem-certified: estimator, randomness, normalization and query quantization assumptions still require an implementation-to-theorem match. No universal 'bound absent/present' or Xiao mechanism verdict is made.

ITQ remains an unresolved comparator proposal. The companion objective replay demonstrates synthetic training-loss reduction and prevents dismissal based only on rotation-distance medians. It provides neither retrieval evidence nor automatic acceptance of an ITQ arm. Global shared ITQ would require a separately declared deployment configuration under budget decision `89d3169adb65a9a2ab7f289997d7c49eb8ccf25c`.
