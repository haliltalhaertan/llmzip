# Evidence — the twelve-byte cost measurements

These are the measurements behind the cost claims made about the twelve-byte
baseline preregistration on 2026-09-11. They are published so that they stop
being **relayed** and can be verified from bytes by any party.

**Base:** `main` at `489e5f94c344c9cee02aa357ff3d59c2029f5846` (L-087).
This branch is additive and is **not** merged into `main`.

## How to reproduce

```bash
pip install faiss-cpu==1.15.0
python3 evidence/twelve_byte_cost_2026_09_11/measure_twelve_byte_cost.py
```

The script is deterministic (`SEED = 0`) and prints JSON. `EVIDENCE.json` in this
directory is its output on the environment recorded inside that file.

## What it measures, and what it does not touch

Synthetic arrays only. The single repository input is the `N_archive` column of
`docs/v52/task4c2/V52_T4C2_feature_geometry.csv` (blob
`b4336dd47fcf14e4b39f65bed3377d56ea9e77c7`), which is archive cardinality — not a
retrieval outcome. The script verifies that blob id at run time and reports whether
it matches.

No corpus is read. No gold is read. No benchmark retrieval is computed. Task 4F1 is
untouched and remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
FORBIDDEN.

## Results, in one place

| claim | measured |
|---|---|
| `RaBitQuantizer(96).code_size` | **20 B**, not 12 |
| `RaBitQuantizer(96, METRIC_L2, 2).code_size` | **44 B** |
| RaBitQ overhead across `d ∈ {32,64,96,128,256,1024}` | **constant 8 B** — two float32 per-vector scalars |
| largest `d` within 12 B at `nb_bits=1` | **32** |
| `nb_bits` assigned after construction | **silently ignored**; `code_size` stays 20 while the attribute reads back 2 |
| `OPQ12_96,PQ12` serialized at `ntotal=0` | **135,325 B** (analytic content 135,168 B + 157 B header) |
| `S(N) = a + bN` over `N ∈ {0,1,100,1000,10000}` | **linear on all five arms**, max abs residual 0.00 B |
| marginal bytes/vector | SIGN96 12, TOP32_RABITQ32 12, RABITQ96 **20**, PQ96 12, OPQ_PQ96 12 |
| `min_points_per_centroid` | **39** — a warning threshold, **not** a trainability gate |
| hard training bound | **points < centroids**; 256 points trains, 255 raises |
| arm 6 cost over the 470 archives | **287.69 B/vector** (cost at mean N is 286.62; Jensen gap 1.07 B) |

## Two corrections this package records against earlier statements of mine

1. **`39 × k` is not a trainability limit.** It is faiss's points-per-centroid
   reliability warning. `m=12×8` does train at 396–616 points. The defensible
   statement is that `m=48×2` is the only listed twelve-byte configuration meeting
   faiss's default recommendation across the whole reported archive range.
2. **The quotable panel figure is the mean of the costs, not the cost at the mean.**
   `1/N` is convex, so they differ by 1.07 B. `287.69` is the panel figure.

## What the numbers do and do not establish

They establish **storage economics**. They say nothing about retrieval quality, and
nothing about which arm wins — that is unmeasured. They also do not establish that
the shared state amortises the way a deployed system would: the preregistration
fits per question archive, so the denominator here is `N_archive`, and whether a
deployed pipeline would share one codebook across archives is a design question the
preregistration has not yet answered in its own bytes.
