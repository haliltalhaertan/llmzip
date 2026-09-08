"""Synthetic integration and negative tests for the corpus-bound runner.

DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS. No corpus is read, downloaded or approximated; no real
fitting, retrieval, ranking or real-data bootstrap runs. Every input is fabricated by
`synthetic_adapter.py`.

WHAT THIS SUITE CLAIMS, AND WHAT IT DOES NOT. No claim is made that any wrong ingestion is necessarily
caught. What is demonstrated is: the declared input schema; the named rejection of each identifier
shape listed in `RUNNER_SPEC.md` section 3; the four-axis source-identity contract, including a
corruption that leaves the total cluster count UNCHANGED; the N-2, N-3 and N-4 obligations; and that
the output schema, the refusal to overwrite and the real-data gate all survive integration. Those are
the checks; nothing beyond them is asserted.

Run: python -B test_membership_runner.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "membership_impl_v3_2026_09_07"))

import membership_runner as R                                                    # noqa: E402
import membership_scaling_core as core                                           # noqa: E402
import synthetic_adapter as syn                                                  # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"ok    {label}   {detail}"[:150])
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}   {detail}"[:150])


def expect_violation(label, fn, needle):
    assert needle, "a negative test must name what it expects to see"
    try:
        fn()
    except core.DesignViolation as exc:
        ok = needle.lower() in str(exc).lower()
        check(label, ok, str(exc)[:100] if ok else f"wrong message: {exc}")
    except Exception as exc:                                                     # noqa: BLE001
        check(label, False, f"raised {type(exc).__name__}, not a named DesignViolation: {exc}")
    else:
        check(label, False, "no exception raised")


TMP = Path(tempfile.mkdtemp(prefix="v52_runner_"))
QIDS, CIDS = syn.build_cohort()
MAPPING = syn.build_mapping_manifest(QIDS, CIDS)
RECORDS = syn.build_records(QIDS)

print("=" * 100)
print("DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS - runner v1. No corpus, no real data, no run authority.")
print("=" * 100)

# --------------------------------------------------------------------------------------------
print("\n-- the core this runner binds to is the audited one -------------------------------------")
# --------------------------------------------------------------------------------------------
core_bytes = (HERE.parent / "membership_impl_v3_2026_09_07" / "membership_scaling_core.py").read_bytes()
import hashlib                                                                   # noqa: E402
check("the imported core is the v3 module", core.__file__.endswith("membership_scaling_core.py"),
      Path(core.__file__).parent.name)
check("BOUND_CORE names the closed v3 commit and its raw-blob hash",
      R.BOUND_CORE["commit"] == "dcb568d0a6c33154c1568500325ad457b4d6f455"
      and len(R.BOUND_CORE["blob_sha256"]) == 64)
check("the checked-out core matches that blob hash, OR differs only by line endings",
      hashlib.sha256(core_bytes).hexdigest() == R.BOUND_CORE["blob_sha256"]
      or hashlib.sha256(core_bytes.replace(b"\r\n", b"\n")).hexdigest() == R.BOUND_CORE["blob_sha256"],
      "raw-blob identity is the authority; a Windows checkout hashes differently")

# --------------------------------------------------------------------------------------------
print("\n-- 1. identifier validation: NEW-4 (missing indicators) ----------------------------------")
# --------------------------------------------------------------------------------------------
for bad, name in [("", "the empty string"), ("   ", "a whitespace-only string"),
                  ("nan", "the literal string 'nan'"), ("NaN", "'NaN' in another case"),
                  ("None", "the literal string 'None'"), ("null", "'null'"),
                  ("N/A", "'N/A'"), ("-", "a lone dash")]:
    expect_violation(f"NEW-4: {name} is rejected as a cluster id",
                     lambda b=bad: R.validate_identifier(b, "cluster id", 0), "missing-value indicator")

check("NEW-4: the rejection list is declared, not implicit",
      "nan" in R.MISSING_VALUE_TOKENS and "" in R.MISSING_VALUE_TOKENS,
      f"{len(R.MISSING_VALUE_TOKENS)} designated tokens")
check("a legitimate id containing a rejected token as a SUBSTRING is accepted unchanged",
      R.validate_identifier("nancy-01", "cluster id", 0) == "nancy-01")
check("a legitimate id is returned byte-identical, not normalised",
      R.validate_identifier("Conv-07", "cluster id", 0) == "Conv-07")

# --------------------------------------------------------------------------------------------
print("\n-- 2. identifier validation: NEW-5 (no int()-equal merging) ------------------------------")
# --------------------------------------------------------------------------------------------
for bad, name in [(1, "a python int"), (np.int64(1), "an np.int64"), (1.0, "a float"),
                  (True, "a bool"), (None, "None"), (b"c1", "bytes"), (("c", 1), "a tuple")]:
    expect_violation(f"NEW-5: {name} is rejected as an unsupported id type",
                     lambda b=bad: R.validate_identifier(b, "cluster id", 0), "unsupported type")
check("NEW-5 is structurally unreachable, not merely tested: no int ever reaches build_clusters",
      R.SUPPORTED_ID_TYPES == (str,),
      "the runner accepts string ids only, so int() keying cannot occur")

# --------------------------------------------------------------------------------------------
print("\n-- 3. identifier validation: no silent transformation ------------------------------------")
# --------------------------------------------------------------------------------------------
expect_violation("a leading-space id is REJECTED, not stripped (stripping would merge it)",
                 lambda: R.validate_identifier(" conv-01", "cluster id", 0), "whitespace")
expect_violation("a trailing-space id is rejected the same way",
                 lambda: R.validate_identifier("conv-01 ", "cluster id", 0), "whitespace")
check("proof that stripping WOULD have merged: the two differ only by that space",
      " conv-01".strip() == "conv-01" and " conv-01" != "conv-01")
expect_violation("misaligned id columns are rejected",
                 lambda: R.validate_identifier_columns(QIDS, CIDS[:-1]), "not aligned")
expect_violation("an empty cohort is rejected",
                 lambda: R.validate_identifier_columns([], []), "empty")
expect_violation("duplicate question ids are rejected",
                 lambda: R.validate_identifier_columns([QIDS[0]] + QIDS[:3], CIDS[:4]), "duplicate")

# --------------------------------------------------------------------------------------------
print("\n-- 4. source identity: the mapping contract ----------------------------------------------")
# --------------------------------------------------------------------------------------------
ident = R.verify_source_identity(QIDS, CIDS, MAPPING)
check("the clean synthetic cohort passes the identity contract",
      ident["cluster_id_set_matches"] and ident["question_to_cluster_matches"],
      f"{ident['n_questions']} questions in {ident['n_clusters']} conversations")
check("the contract records that a count check alone is NOT accepted",
      ident["count_check_alone_is_not_accepted"] and len(ident["checks_performed"]) == 6)

# THE CENTRAL NEGATIVE TEST. Swap two questions between two conversations. The grouping is corrupted
# - those questions now resample with the wrong conversation - while the cluster COUNT is unchanged.
swapped = list(CIDS)
i, j = QIDS.index("conv-01-q0"), QIDS.index("conv-02-q0")
swapped[i], swapped[j] = swapped[j], swapped[i]
check("the corrupted cohort has the SAME number of conversations as the clean one",
      len(set(swapped)) == len(set(CIDS)) == 10,
      "a count check would pass here; the grouping is silently corrupted")
expect_violation("a swapped question->conversation mapping is caught although the count is unchanged",
                 lambda: R.verify_source_identity(QIDS, swapped, MAPPING), "WRONG conversation")

# A whole conversation relabelled: count unchanged, set changed.
relabelled = ["conv-99" if c == "conv-05" else c for c in CIDS]
check("the relabelled cohort also has ten conversations", len(set(relabelled)) == 10)
expect_violation("a relabelled conversation is caught by SET equality, not by counting",
                 lambda: R.verify_source_identity(QIDS, relabelled, MAPPING), "set mismatch")

# A missing id rendered as "" for a whole conversation: still ten distinct labels.
blanked = ["" if c == "conv-03" else c for c in CIDS]
check("the blanked cohort STILL has ten distinct labels",
      len(set(blanked)) == 10,
      "'a visible 11th cluster' is not guaranteed; the grouping can break silently")
expect_violation("a blank conversation id is caught by identifier validation, before grouping",
                 lambda: R.verify_source_identity(QIDS, blanked, MAPPING), "missing-value indicator")

expect_violation("a dropped question is caught",
                 lambda: R.verify_source_identity(QIDS[:-1], CIDS[:-1], MAPPING), "missing against the bound source")
expect_violation("an unknown extra question is caught",
                 lambda: R.verify_source_identity(QIDS + ["ghost-q"], CIDS + ["conv-01"], MAPPING),
                 "not in the bound source")

bad_map = dict(MAPPING); bad_map["n_questions"] = 999
expect_violation("an internally inconsistent manifest is rejected",
                 lambda: R.verify_source_identity(QIDS, CIDS, bad_map), "declares n_questions")

# --------------------------------------------------------------------------------------------
print("\n-- 5. the mapping manifest is hash-bound -------------------------------------------------")
# --------------------------------------------------------------------------------------------
mpath = TMP / "mapping.json"
mpath.write_bytes(json.dumps(MAPPING, indent=2).encode("utf-8"))
mhash = hashlib.sha256(mpath.read_bytes()).hexdigest()
check("a manifest matching its bound hash loads",
      R.load_expected_mapping(mpath, mhash)["source_id"] == "synthetic-cohort-v1")
expect_violation("a manifest whose hash does not match the bound value is refused",
                 lambda: R.load_expected_mapping(mpath, "0" * 64), "hash mismatch")
extra_path = TMP / "mapping_extra.json"
extra = dict(MAPPING); extra["surprise"] = 1
extra_path.write_bytes(json.dumps(extra).encode("utf-8"))
expect_violation("a manifest with an unexpected field is refused",
                 lambda: R.load_expected_mapping(extra_path, hashlib.sha256(extra_path.read_bytes()).hexdigest()),
                 "schema mismatch")

# --------------------------------------------------------------------------------------------
print("\n-- 6. N-2: the bootstrap seed is frozen before any result ---------------------------------")
# --------------------------------------------------------------------------------------------
seed_path = TMP / "bootstrap_seed_locomo_question.json"
rec = R.freeze_bootstrap_seed(seed_path, 424242, R.LOCOMO, "question", 200)
check("N-2: the seed record is written and marked frozen before any result",
      rec["bootstrap_seed"] == 424242 and rec["frozen_before_any_result"] is True)
expect_violation("N-2: the seed record REFUSES to be overwritten with a second seed",
                 lambda: R.freeze_bootstrap_seed(seed_path, 999, R.LOCOMO, "question", 200), "refusing to overwrite")
expect_violation("N-2: a run with no frozen record is refused",
                 lambda: R.read_bootstrap_seed(TMP / "absent.json", R.LOCOMO, "question"), "no frozen bootstrap-seed record")
expect_violation("N-2: a record may not be reused across a different scheme",
                 lambda: R.read_bootstrap_seed(seed_path, R.LOCOMO, "cluster"), "may not be reused")
expect_violation("N-2: a non-integer seed is refused at freezing time",
                 lambda: R.freeze_bootstrap_seed(TMP / "s2.json", 1.5, R.LOCOMO, "question", 10), "must be an int")
expect_violation("N-2: a bool is not an integer seed",
                 lambda: R.freeze_bootstrap_seed(TMP / "s3.json", True, R.LOCOMO, "question", 10), "must be an int")

# --------------------------------------------------------------------------------------------
print("\n-- 7. N-4: the archive-learned transform is applied to the query --------------------------")
# --------------------------------------------------------------------------------------------
archive, query = syn.build_representations()
mu, D, diag = R.fit_archive_transform(archive)
A_t = R.apply_archive_transform(archive, mu, D)
Q_t = R.apply_archive_transform(query, mu, D)
check("N-4: the centering vector is the ARCHIVE mean", np.allclose(mu, archive.mean(axis=0)))
check("N-4: D is diagonal and archive-derived", D.shape == (core.DIM, core.DIM)
      and np.count_nonzero(D - np.diag(np.diag(D))) == 0)
check("N-4: the transformed archive is centred at zero", float(np.abs(A_t.mean(axis=0)).max()) < 1e-10,
      f"max |mean| = {float(np.abs(A_t.mean(axis=0)).max()):.2e}")
check("N-4: the transformed QUERY is NOT centred at zero - nothing was fitted to it",
      float(np.abs(Q_t.mean(axis=0)).max()) > 0.1,
      f"max |mean| = {float(np.abs(Q_t.mean(axis=0)).max()):.3f}")
R.assert_query_transform_is_inherited(mu, D, mu, D)
check("N-4: applying the identical objects passes the inheritance assertion", True)
mu_q, D_q, _ = R.fit_archive_transform(np.vstack([query, query + 1e-9]))
expect_violation("N-4: a transform fitted to the QUERY is rejected, bitwise",
                 lambda: R.assert_query_transform_is_inherited(mu, D, mu_q, D_q), "N-4 VIOLATION")
expect_violation("N-4: even a 1-ULP perturbation of D is rejected (this must not use a tolerance)",
                 lambda: R.assert_query_transform_is_inherited(mu, D, mu, D * (1 + 2**-52)), "N-4 VIOLATION")
check("N-4: the scaling diagnostics come from the core, unmodified",
      set(diag) == {"degenerate_coords", "flagged", "cv_sigma_before", "cv_sigma_after", "sd_sigma_after"})

# --------------------------------------------------------------------------------------------
print("\n-- 8. end-to-end integration on synthetic data --------------------------------------------")
# --------------------------------------------------------------------------------------------
res = R.compute_results(RECORDS, QIDS, CIDS, MAPPING, seed_path,
                        benchmark=R.LOCOMO, scheme="question", replicates=200,
                        scaling_diagnostics=diag)
check("integration: the result carries exactly the declared schema", set(res) == R.RESULT_KEYS)
check("integration: the estimates carry exactly the core's declared schema",
      set(res["estimates"]) == set(core.AGGREGATE_KEYS))
check("integration: the three pp quantities are present and linear",
      abs(res["estimates"]["Delta_bar_pp"]
          - (res["estimates"]["G_bar_scaled_pp"] - res["estimates"]["G_bar_pp"])) <= core.TOL,
      f"G={res['estimates']['G_bar_pp']:.4f} G_s={res['estimates']['G_bar_scaled_pp']:.4f} "
      f"D={res['estimates']['Delta_bar_pp']:.4f}")
check("integration: the fixture's scaled gap is smaller than the unscaled one",
      res["estimates"]["G_bar_scaled_pp"] < res["estimates"]["G_bar_pp"],
      "a property of the FIXTURE, not a prediction about the experiment")
check("integration: the frozen seed record travels into the output",
      res["bootstrap_seed_record"]["bootstrap_seed"] == 424242)
check("integration: the source-identity evidence travels into the output",
      res["source_identity"]["question_to_cluster_matches"] is True)
check("integration: the bound core identity travels into the output",
      res["core_identity"]["commit"] == "dcb568d0a6c33154c1568500325ad457b4d6f455")

cseed_path = TMP / "bootstrap_seed_locomo_cluster.json"
R.freeze_bootstrap_seed(cseed_path, 515151, R.LOCOMO, "cluster", 200)
res_c = R.compute_results(RECORDS, QIDS, CIDS, MAPPING, cseed_path,
                          benchmark=R.LOCOMO, scheme="cluster", replicates=200, scaling_diagnostics=diag)
check("integration: the LoCoMo cluster bootstrap runs and reports ten conversations",
      res_c["n_clusters"] == 10 and res_c["scheme"] == "cluster")
check("integration: cluster multiplicity is preserved in the slot denominator",
      res_c["uncertainty"]["mean_clusters_not_drawn_per_replicate"] > 0,
      f"{res_c['uncertainty']['mean_clusters_not_drawn_per_replicate']:.3f} per replicate")

# --------------------------------------------------------------------------------------------
print("\n-- 9. N-3: LongMemEval carries its tag and refuses a cluster bootstrap --------------------")
# --------------------------------------------------------------------------------------------
lme_map = syn.build_mapping_manifest(QIDS, CIDS, benchmark=R.LONGMEMEVAL, source_id="synthetic-lme-v1")
lme_seed = TMP / "bootstrap_seed_lme_question.json"
R.freeze_bootstrap_seed(lme_seed, 606060, R.LONGMEMEVAL, "question", 200)
res_l = R.compute_results(RECORDS, QIDS, CIDS, lme_map, lme_seed,
                          benchmark=R.LONGMEMEVAL, scheme="question", replicates=200)
check("N-3: the LongMemEval inheritance tag is emitted in the output",
      res_l["longmemeval_inheritance_tag"]["provenance"].startswith("inherited from Task 3A.1"))
check("N-3: the tag names the consequence, not just the fact",
      "ILL-POSED" in res_l["longmemeval_inheritance_tag"]["consequence"].upper())
check("N-3: LoCoMo outputs carry no LongMemEval tag", res["longmemeval_inheritance_tag"] is None)
lme_cseed = TMP / "bootstrap_seed_lme_cluster.json"
R.freeze_bootstrap_seed(lme_cseed, 707070, R.LONGMEMEVAL, "cluster", 200)
expect_violation("N-3: a LongMemEval CLUSTER bootstrap is refused",
                 lambda: R.compute_results(RECORDS, QIDS, CIDS, lme_map, lme_cseed,
                                           benchmark=R.LONGMEMEVAL, scheme="cluster", replicates=200),
                 "REFUSED for LongMemEval")
expect_violation("a mapping manifest for the wrong benchmark is refused",
                 lambda: R.compute_results(RECORDS, QIDS, CIDS, lme_map, seed_path,
                                           benchmark=R.LOCOMO, scheme="question", replicates=200),
                 "manifest is for")

# --------------------------------------------------------------------------------------------
print("\n-- 10. output protection and the real-data gate, THROUGH the integration ------------------")
# --------------------------------------------------------------------------------------------
out = TMP / "results" / "locomo_question.json"
write_path = R.write_results(out, res)
check("output: results are written to a new file", write_path.exists())
expect_violation("output: a second write to the same path is REFUSED",
                 lambda: R.write_results(out, res), "refusing to overwrite")
bad_res = dict(res); bad_res.pop("core_identity")
expect_violation("output: a result missing a declared field is not written",
                 lambda: R.write_results(TMP / "results" / "bad.json", bad_res), "not the declared one")
bad_res2 = dict(res); bad_res2["relative_change"] = 0.5
expect_violation("output: a result carrying an UNDECLARED field is not written",
                 lambda: R.write_results(TMP / "results" / "bad2.json", bad_res2), "not the declared one")

check("gate: real-data execution is OFF in the core", core.REAL_DATA_EXECUTION_ENABLED is False)
expect_violation("gate: the runner's only corpus entry point refuses",
                 lambda: R.run_on_real_corpus(), "not authorized")
expect_violation("gate: it refuses via the CORE's authorization check, not a private flag",
                 lambda: core.require_real_data_authorization(), "not authorized")
_prev = core.REAL_DATA_EXECUTION_ENABLED
try:
    core.REAL_DATA_EXECUTION_ENABLED = True
    expect_violation("gate: even with the flag flipped there is NO ingestion path behind it",
                     lambda: R.run_on_real_corpus(), "no real-corpus ingestion path exists")
finally:
    core.REAL_DATA_EXECUTION_ENABLED = _prev
check("gate: the flag is restored to False after that probe", core.REAL_DATA_EXECUTION_ENABLED is False)

# --------------------------------------------------------------------------------------------
print("\n-- 11. record validation still applies through the integration ----------------------------")
# --------------------------------------------------------------------------------------------
short = RECORDS[:-1]
expect_violation("a missing per-question record is refused at integration",
                 lambda: R.compute_results(short, QIDS, CIDS, MAPPING, seed_path,
                                           benchmark=R.LOCOMO, scheme="question", replicates=50),
                 "record validation failed")
dup = RECORDS + [RECORDS[0]]
expect_violation("a duplicated record is refused at integration",
                 lambda: R.compute_results(dup, QIDS, CIDS, MAPPING, seed_path,
                                           benchmark=R.LOCOMO, scheme="question", replicates=50),
                 "record validation failed")
expect_violation("an unknown resampling scheme is refused",
                 lambda: R.compute_results(RECORDS, QIDS, CIDS, MAPPING, seed_path,
                                           benchmark=R.LOCOMO, scheme="jackknife", replicates=50),
                 "unknown resampling scheme")
expect_violation("an unknown benchmark is refused",
                 lambda: R.compute_results(RECORDS, QIDS, CIDS, MAPPING, seed_path,
                                           benchmark="MMLU", scheme="question", replicates=50),
                 "unknown benchmark")

# --------------------------------------------------------------------------------------------
print("\n-- 12. the audited core is untouched by this runner ---------------------------------------")
# --------------------------------------------------------------------------------------------
check("the core file is byte-identical to what it was at import",
      (HERE.parent / "membership_impl_v3_2026_09_07" / "membership_scaling_core.py").read_bytes() == core_bytes)
check("the runner adds no attribute to the core module",
      not hasattr(core, "MISSING_VALUE_TOKENS") and not hasattr(core, "verify_source_identity"))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): {FAILURES}")
    raise SystemExit(1)
print("ALL PASS")
print("Scope: DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS. Not evidence of lock conformance, not a seal, "
      "and not authorization to run on real data.")
raise SystemExit(0)
