#!/usr/bin/env python3
"""Local regeneration check: build the T4D LoCoMo mixed96 representation from the
sealed script and compare per-conversation counts + frozen native R@3.

Uses only the sealed script's own functions (loaded via importlib).
"""
import importlib.util, json, os, sys, hashlib
import numpy as np

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[v] = "1"

SCRIPT = r"C:/Users/MDP/dev/llmzip-work/drive/v52_t4d_locomo_frozen_cross_benchmark.py"
RAW = r"C:/Users/MDP/dev/llmzip-work/drive/locomo10.json"
AUDIT = r"C:/Users/MDP/dev/llmzip-work/drive/audit_layer"
PROOF_CSV = r"C:/Users/MDP/dev/llmzip-work/scratch/t4dzip/V52_T4D_REPRESENTATION_TRANSFER_PROOF.csv"

spec = importlib.util.spec_from_file_location("t4d_frozen", SCRIPT)
t4d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t4d)

import sklearn
print("env: python", sys.version.split()[0], "sklearn", sklearn.__version__, "numpy", np.__version__)

convs, corr = t4d.load_dataset(t4d.Path(RAW), t4d.Path(AUDIT))
print("convs:", len(convs), "corrections:", len(corr))

reps = {}
for c in convs:
    reps[c["conv_id"]] = t4d.build_representation(c)

import csv as _csv
expected = {}
with open(PROOF_CSV, newline="", encoding="utf-8") as f:
    for row in _csv.DictReader(f):
        expected[row["conv_id"]] = row

fields = ["N", "archive_fit_docs", "mixed96_dim", "mixed_concat_features",
          "source_char_features", "source_word_features", "query_count", "no_nan"]
all_ok = True
for c in convs:
    r = reps[c["conv_id"]]
    e = expected[c["conv_id"]]
    got = {"N": r["N"], "archive_fit_docs": r["archive_fit_docs"], "mixed96_dim": r["mixed96_dim"],
           "mixed_concat_features": r["mixed_concat_features"], "source_char_features": r["source_char_features"],
           "source_word_features": r["source_word_features"], "query_count": r["query_count"],
           "no_nan": str(r["no_nan"])}
    bad = [k for k in fields if str(got[k]) != str(e[k])]
    all_ok &= not bad
    print(f"{c['conv_id']}: counts {'MATCH' if not bad else 'MISMATCH ' + str([(k, got[k], e[k]) for k in bad])}")

print("ALL COUNT FIELDS MATCH:", all_ok)

# Native audit fractional R@3, replicating evaluate_all's native path.
native_vals = []
valid = 0
for ci, c in enumerate(convs):
    r = reps[c["conv_id"]]
    C, QC, N = r["C"], r["QC"], r["N"]
    D0 = C >= 0
    Q0 = QC >= 0
    dist0 = np.count_nonzero(Q0[:, None, :] != D0[None, :, :], axis=2).astype(np.int16)
    priorities = [np.random.default_rng(t4d.stable_archive_seed(ci, t) + 99).random(N) for t in range(t4d.N_NUISANCE)]
    for qi, q in enumerate(r["qas"]):
        gold = t4d.evidence_rows(q["correct_evidence"], r["id_to_row"])
        if not gold:
            native_vals.append(np.nan)
            continue
        valid += 1
        tops = t4d.topks_by_hamming(dist0[qi], priorities)
        vals = [t4d.retrieval_metrics(x, gold)["fractional"] for x in tops]
        native_vals.append(t4d.mean_or_nan(vals))

native = float(np.nanmean(np.asarray(native_vals, dtype=float)))
print("valid questions:", valid)
print("native audit fractional R@3 recomputed:", repr(native))
print("frozen expected                        : 0.23654714666441054")
print("EXACT MATCH:", native == 0.23654714666441054, " abs error:", abs(native - 0.23654714666441054))

# Local matrix fingerprints (NOT canonical; environment-dependent) for the work log.
fp = {}
for cid, r in reps.items():
    fp[cid] = {
        "C_sha256_float64": hashlib.sha256(np.ascontiguousarray(r["C"], dtype=np.float64).tobytes()).hexdigest(),
        "QC_sha256_float64": hashlib.sha256(np.ascontiguousarray(r["QC"], dtype=np.float64).tobytes()).hexdigest(),
    }
print(json.dumps(fp, indent=1))
