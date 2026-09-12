"""Published scalar provenance and synthetic fixed-ray scale probe only."""
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path
import subprocess
import faiss
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
raw = subprocess.check_output(["git", "cat-file", "blob",
    "8217704700d793862a6c43130b88236da551f010:audit_v52_t4c3/AUDIT_REPORT.md"], cwd=ROOT)
digest = hashlib.sha256(raw).hexdigest()
assert digest == "8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238"
values = ["36.1395390", "39.1393617", "37.9320922", "38.0195035", "40.1278369"]
for value in values:
    assert value.encode() in raw
mean = sum(map(Decimal, values)) / Decimal(500)
rounded = mean.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN)
assert rounded == Decimal("0.38271667")

faiss.omp_set_num_threads(4)
rng = np.random.default_rng(0)
quantizer = faiss.RaBitQuantizer(96)
quantizer.train(rng.standard_normal((2000, 96)).astype("float32"))
# Exactly one direction with three positive scales removes changes in direction
# as an alternative explanation of changing reconstructed magnitudes.
direction = rng.standard_normal((1, 96)).astype("float32")
x = np.vstack([direction * s for s in (0.125, 1.0, 8.0)])
codes = quantizer.compute_codes(x)
decoded = quantizer.decode(codes)
input_norms = np.linalg.norm(x, axis=1)
decoded_norms = np.linalg.norm(decoded, axis=1)
ratios = decoded_norms / input_norms
assert quantizer.code_size == 20
assert np.all(np.diff(decoded_norms) > 0)
assert np.allclose(ratios, ratios[1], rtol=1e-5, atol=0)
report = {
    "simhash": {"source_sha256": digest, "seeds": [43001,43002,43003,43004,43005],
                "published_percentages": values, "mean_fraction_decimal": str(mean),
                "rounding": "8 decimal places; Decimal ROUND_HALF_EVEN", "rounded": str(rounded)},
    "fixed_ray_probe": {"code_size": int(quantizer.code_size),
        "input_norms": input_norms.tolist(), "decoded_norms": decoded_norms.tolist(),
        "decoded_to_input_norm_ratio": ratios.tolist(),
        "code_byte_positions_varying_with_scale": np.flatnonzero(np.any(codes != codes[1], axis=0)).tolist(),
        "functional_scale_preserved": True,
        "limitation": "No attribution to unbiased-estimator correction terms or theorem; no minimal-encoding impossibility claim."},
    "boundary": "Published aggregate scalars and synthetic vectors only. No retrieval outcomes computed."
}
(OUT / "SUPPLEMENTARY.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
