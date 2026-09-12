"""Build the receipt only after both actual replay outputs exist."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
c = json.loads((HERE / "COMPARISON.json").read_text(encoding="utf-8"))
s = json.loads((HERE / "SUPPLEMENTARY.json").read_text(encoding="utf-8"))
r = json.loads((HERE / "REPLAY.json").read_text(encoding="utf-8"))
assert c["returncode"] == 0 and c["float_tolerant_equal"]
assert r["environment"]["blob_matches"]
assert s["simhash"]["rounded"] == "0.38271667"
strict = c["strict_non_environment_equal"]
verdict = "EXACT NON-ENVIRONMENT MATCH" if strict else "MATCH WITH DECLARED FLOAT ROUNDOFF"
readme = f"""# Twelve-byte cost runtime replay — 2026-09-12

Verdict: **{verdict}**. This is a source-pinned runtime cost reproduction,
not baseline execution readiness and not a cold-start scientific audit.

The executor did not author the pinned producer script. Producer environment was
Linux / Python 3.11.15; this replay ran on Windows / Python {r['environment']['python']}.
Both use Faiss 1.15.0 and NumPy 2.4.6. The immutable script and reference JSON were
SHA256 checked before execution; the frozen archive-cardinality CSV was checked
against raw Git blob b4336dd47fcf14e4b39f65bed3377d56ea9e77c7 before use.

## Results and exact scope

- Actual subprocess exit: {c['returncode']}.
- Strict equality excluding environment: {strict}.
- Non-environment differing leaves: {len(c['differences'])}; every difference and
  the independently declared float tolerance are in COMPARISON.json.
- Per-vector bytes: SIGN96 12, TOP32_RABITQ32 12, RABITQ96 20, 2-bit RaBitQ96 44,
  PQ96 m12x8 12 and OPQ/PQ96 m12x8 12. Integer serialization points must match exactly.
- OPQ/PQ96 serialized shared state: {r['serialized_versus_analytic']['OPQ_PQ96_serialized']} B;
  analytic content: {r['serialized_versus_analytic']['OPQ_PQ96_analytic_content']} B.
- Mean effective OPQ/PQ cost over 470 frozen archive sizes:
  {r['archive_cost']['mean_cost_over_archives']:.12f} B/vector. This is distinct from
  the cost evaluated at mean archive size.
- The post-construction nb_bits assignment trap and 39*k warning versus hard
  points<centroids training bound were actually re-executed.

This closes the separate runtime reproduction item for these byte-cost claims
at the stated exact/tolerance level. It does not approve a baseline preregistration,
candidate, quality comparison, mechanism claim or experiment. The old 20-byte
RaBitQ96 comparator remains ineligible for the <=12 marginal-byte comparison.

## Supplementary checks

The published SIMHASH panel's exact decimal mean is 0.3827166666, rounding to
0.38271667 at eight decimal places. The report source digest, panel and rounding
rule are recorded in SUPPLEMENTARY.json.

A stronger functional scale probe holds direction fixed and varies positive scale.
Reconstruction magnitudes scale accordingly. This supports a functional scale claim,
not the attribution to unbiased-estimator correction terms, a theorem or a proof
that no alternative smaller encoding exists.

## Reproduction

Use a clean Python environment with faiss-cpu==1.15.0 and numpy==2.4.6. The source
namespace and frozen archive-size file from commit
8217704700d793862a6c43130b88236da551f010 must be present. This branch retains them.

```text
python -B evidence/runtime_replay_2026_09_12/replay.py
python -B evidence/runtime_replay_2026_09_12/supplementary_checks.py
python -B evidence/runtime_replay_2026_09_12/capture_environment.py
python -B evidence/runtime_replay_2026_09_12/build_receipt.py
```

replay.py runs the unchanged original script in a subprocess with four computational
threads and captures its exact stdout/stderr. It reports strict comparison first;
only finite float differences may use the tolerance declared before execution.
Package hashes exclude HASHES.json itself to avoid recursive self-hashing.
Reproduction overwrites this namespace's generated verification outputs only;
use a scratch checkout to preserve this committed receipt.

## Boundary

Synthetic byte-cost calculations and the frozen archive-cardinality input only.
No real corpus, retrieval outcome, ranking evaluation, seal, finalize, HMAC or
production authorization. Task 4F1: SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN.
"""
(HERE / "README.md").write_text(readme, encoding="utf-8", newline="\n")
files = {}
for p in sorted(HERE.iterdir()):
    if p.is_file() and p.name != "HASHES.json":
        raw = p.read_bytes()
        files[p.name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
(HERE / "HASHES.json").write_text(json.dumps({"files": files}, indent=2) + "\n", encoding="utf-8")
print(verdict)
