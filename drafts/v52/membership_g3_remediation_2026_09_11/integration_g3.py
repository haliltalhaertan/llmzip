"""SYNTHETIC ONLY bridge; no production authorization or independent acceptance.

Public hashes bind supplied fixture data, not its authenticity or historical execution.
The caller and Python process are trusted. Direct inherited production entry points,
real ingestion, frozen outcomes, independent review and sealing remain outside scope.
"""
from __future__ import annotations

import functools
import hashlib
import json
import math
from pathlib import Path

import membership_runner_g3 as runner


class IntegrationError(ValueError):
    pass


def _require(condition, code):
    if not condition:
        raise IntegrationError(code)


SYNTHETIC = "SYNTHETIC_ONLY"
VERSION = "g3_synthetic_delivery_v1"
HERE = Path(__file__).resolve().parent
CODE_FILES = ("integration_g3.py", "membership_runner_g3.py", "membership_scaling_core.py",
              "pipeline_g3.py", "corpus_ingest_g3.py", "errors.py", "safe_report.py",
              "authoritative/accepted_configuration.py", "authoritative/resolve_sources.py",
              "exact_oracle.py", "record_boundary.py")
ENVELOPE_KEYS = {"schema_version", "provenance", "benchmark", "question_ids", "cluster_ids",
                 "mapping", "records", "diagnostics", "source_identity", "code_hashes", "binding_sha256"}
RAW_DIAG_KEYS = {"archive_ordinal", "degenerate_coords", "flagged", "cv_sigma_before",
                 "cv_sigma_after", "sd_sigma_after"}
DIAG_KEYS = RAW_DIAG_KEYS | {"question_ids", "cv_sigma_before_status", "cv_sigma_after_status"}
RESULT_KEYS = {"schema_version", "provenance", "preparation", "scheme", "bootstrap_configuration",
               "estimates", "uncertainty", "result_sha256"}
SCALARS = ("G_bar_pp", "G_bar_scaled_pp", "Delta_bar_pp")
VECTORS = ("per_seed_G_pp", "per_seed_G_scaled_pp", "per_seed_Delta_pp")


def _boundary(fn):
    """Fixed error surface, including cause/context; traceback locals are out of scope."""
    @functools.wraps(fn)
    def call(*args, **kwargs):
        code = "E-G3-I90"
        try:
            return fn(*args, **kwargs)
        except IntegrationError as exc:
            if str(exc) in {f"E-G3-I{i:02d}" for i in range(100)}:
                code = str(exc)
        except Exception:
            pass
        # Raising outside except also removes the retained __context__ chain.
        raise IntegrationError(code)
    return call


def _copy(v, depth=0):
    _require(depth < 32, "E-G3-I01")
    if v is None or type(v) in (str, int, float, bool):
        return v
    if type(v) is list:
        return [_copy(x, depth + 1) for x in v]
    if type(v) is dict:
        _require(all(type(k) is str for k in v), "E-G3-I01")
        return {k: _copy(x, depth + 1) for k, x in v.items()}
    raise IntegrationError("E-G3-I01")


def _schema(v, keys, code):
    _require(type(v) is dict and set(v) == set(keys), code)


def _encoded(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def _digest(v):
    return hashlib.sha256(_encoded(v)).hexdigest()


def _hash(v):
    return type(v) is str and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _number(v, lo, hi):
    return type(v) in (int, float) and math.isfinite(v) and lo <= v <= hi


def _ids(v):
    _require(type(v) is list and len(v) > 0 and all(type(x) is str and 0 < len(x) <= 120
             and x == x.strip() and x.casefold() not in runner.MISSING_VALUE_TOKENS
             and all(ord(c) >= 32 and ord(c) != 127 for c in x) for x in v), "E-G3-I02")


def _code_hashes():
    result = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE_FILES}
    _require(result["membership_scaling_core.py"] == runner.BOUND_CORE["blob_sha256"], "E-G3-I03")
    return result


def _validate_envelope(e):
    _schema(e, ENVELOPE_KEYS, "E-G3-I06")
    _require(e["schema_version"] == VERSION and e["provenance"] == SYNTHETIC, "E-G3-I07")
    b, qs, cs = e["benchmark"], e["question_ids"], e["cluster_ids"]
    _require(type(b) is str and b in runner.BENCHMARKS, "E-G3-I08")
    _ids(qs)
    _ids(cs)
    _require(len(qs) == len(cs) and len(set(qs)) == len(qs), "E-G3-I02")
    _require(b != runner.LONGMEMEVAL or len(set(cs)) == 1, "E-G3-I09")
    m = e["mapping"]
    _schema(m, runner.MAPPING_FIELDS | {"provenance"}, "E-G3-I09")
    _ids(m["expected_cluster_ids"])
    _require(m["provenance"] == SYNTHETIC and m["source_id"] == "synthetic_fixture"
             and m["benchmark"] == b and _hash(m["source_sha256"])
             and type(m["n_questions"]) is int and m["n_questions"] == len(qs)
             and type(m["expected_question_to_cluster"]) is dict
             and m["expected_question_to_cluster"] == dict(zip(qs, cs))
             and len(m["expected_cluster_ids"]) == len(set(cs))
             and set(m["expected_cluster_ids"]) == set(cs), "E-G3-I09")
    s = e["source_identity"]
    _schema(s, {"provenance", "source_kind", "source_sha256", "source_bytes"}, "E-G3-I10")
    _require(s["provenance"] == SYNTHETIC and s["source_kind"] == "generated_fixture_bytes"
             and s["source_sha256"] == m["source_sha256"]
             and type(s["source_bytes"]) is int and s["source_bytes"] > 0, "E-G3-I10")
    _schema(e["code_hashes"], CODE_FILES, "E-G3-I03")
    _require(e["code_hashes"] == _code_hashes(), "E-G3-I03")
    records = e["records"]
    expected = {(q, s, a) for q in qs for s in runner.core.ROTATION_SEEDS for a in runner.core.ARMS}
    _require(type(records) is list and len(records) == len(expected), "E-G3-I04")
    seen = set()
    for r in records:
        _schema(r, runner.RECORD_FIELDS, "E-G3-I04")
        _require(type(r["question_id"]) is str and type(r["rotation_seed"]) is int
                 and type(r["arm"]) is str and _number(r["fractional_R3"], 0, 1), "E-G3-I04")
        key = (r["question_id"], r["rotation_seed"], r["arm"])
        _require(key in expected and key not in seen, "E-G3-I04")
        seen.add(key)
    diags, seen, ordinals, clusters_seen = e["diagnostics"], set(), set(), set()
    _require(type(diags) is list and len(diags) > 0, "E-G3-I05")
    for d in diags:
        _schema(d, DIAG_KEYS, "E-G3-I05")
        ordinal, ids, n = d["archive_ordinal"], d["question_ids"], d["degenerate_coords"]
        _ids(ids)
        _require(type(ordinal) is int and ordinal >= 0 and ordinal not in ordinals
                 and len(ids) == len(set(ids)) and set(ids) <= set(qs) and not seen.intersection(ids), "E-G3-I05")
        ordinals.add(ordinal)
        seen.update(ids)
        if b == runner.LOCOMO:
            cset = {m["expected_question_to_cluster"][q] for q in ids}
            _require(len(cset) == 1 and not cset.intersection(clusters_seen), "E-G3-I05")
            clusters_seen.update(cset)
        else:
            _require(len(ids) == 1 and ordinal == qs.index(ids[0]), "E-G3-I05")
        _require(type(n) is int and 0 <= n <= 96 and type(d["flagged"]) is bool
                 and d["flagged"] == (n > runner.core.DEGENERATE_FLAG_THRESHOLD)
                 and _number(d["sd_sigma_after"], 0, math.inf), "E-G3-I05")
        for name in ("cv_sigma_before", "cv_sigma_after"):
            if d[name] is None:
                _require(d[name + "_status"] == "undefined_zero_mean" and n == 96
                         and d["sd_sigma_after"] == 0 and d["cv_sigma_before"] is None
                         and d["cv_sigma_after"] is None, "E-G3-I05")
            else:
                _require(d[name + "_status"] == "defined" and _number(d[name], 0, math.inf), "E-G3-I05")
    _require(seen == set(qs), "E-G3-I05")
    _require(_hash(e["binding_sha256"]) and e["binding_sha256"] ==
             _digest({k: v for k, v in e.items() if k != "binding_sha256"}), "E-G3-I11")


@_boundary
def prepare_synthetic_envelope(ingested, prepared, source_bytes):
    """Bind generated fixture ingestion to prepared records; performs no corpus I/O."""
    _require(type(source_bytes) is bytes and len(source_bytes) > 0, "E-G3-I10")
    i, p = _copy(ingested), _copy(prepared)
    _schema(p, {"records", "diagnostics"}, "E-G3-I06")
    _require(i["questions_with_empty_gold"] == [] and i["questions_with_partial_evidence_loss"] == [], "E-G3-I12")
    identity, mapping, qs, b = i["identity"], i["mapping"], i["cohort_ids"], i["benchmark"]
    _schema(mapping, runner.MAPPING_FIELDS | {"provenance"}, "E-G3-I09")
    _schema(identity, {"source_file", "source_sha256", "source_bytes"}, "E-G3-I10")
    sha = hashlib.sha256(source_bytes).hexdigest()
    _require(identity["source_file"] == "synthetic_fixture.json" and identity["source_sha256"] == sha
             and type(identity["source_bytes"]) is int and identity["source_bytes"] == len(source_bytes)
             and mapping["source_sha256"] == sha, "E-G3-I10")
    cs = [mapping["expected_question_to_cluster"][q] for q in qs]
    if b == runner.LOCOMO:
        groups = [(c["index"], list(c["questions"])) for c in i["conversations"].values() if c["questions"]]
    else:
        _require(b == runner.LONGMEMEVAL and set(i["questions"]) == set(qs), "E-G3-I08")
        groups = [(j, [q]) for j, q in enumerate(qs)]
    _require(all(type(j) is int and j >= 0 for j, _ in groups)
             and len(dict(groups)) == len(groups) == len(p["diagnostics"]), "E-G3-I05")
    for d in p["diagnostics"]:
        _schema(d, RAW_DIAG_KEYS, "E-G3-I05")
        _require(type(d["archive_ordinal"]) is int and d["archive_ordinal"] in dict(groups), "E-G3-I05")
        d["question_ids"] = dict(groups)[d["archive_ordinal"]]
        for name in ("cv_sigma_before", "cv_sigma_after"):
            undefined = type(d[name]) is float and math.isnan(d[name])
            d[name + "_status"] = "undefined_zero_mean" if undefined else "defined"
            if undefined:
                d[name] = None
    e = {"schema_version": VERSION, "provenance": SYNTHETIC, "benchmark": b,
         "question_ids": qs, "cluster_ids": cs, "mapping": mapping, "records": p["records"],
         "diagnostics": p["diagnostics"], "code_hashes": _code_hashes(),
         "source_identity": {"provenance": SYNTHETIC, "source_kind": "generated_fixture_bytes",
                             "source_sha256": sha, "source_bytes": len(source_bytes)}}
    e["binding_sha256"] = _digest(e)
    _validate_envelope(e)
    return _copy(e)


def _validate_result(r):
    _schema(r, RESULT_KEYS, "E-G3-I14")
    _require(r["schema_version"] == VERSION and r["provenance"] == SYNTHETIC, "E-G3-I07")
    e, scheme = r["preparation"], r["scheme"]
    _validate_envelope(e)
    _require(type(scheme) is str and scheme in ("question", "cluster")
             and not (e["benchmark"] == runner.LONGMEMEVAL and scheme == "cluster"), "E-G3-I15")
    cfg, want = r["bootstrap_configuration"], runner.accepted_bootstrap_for(e["benchmark"], scheme)
    _schema(cfg, {"provenance", "seed_origin", "benchmark", "scheme", "seed", "replicates"}, "E-G3-I16")
    _require(cfg["provenance"] == SYNTHETIC and cfg["seed_origin"] == "shared_configuration"
             and cfg["benchmark"] == e["benchmark"] and cfg["scheme"] == scheme
             and type(cfg["seed"]) is int and cfg["seed"] == want["seed"]
             and type(cfg["replicates"]) is int and cfg["replicates"] == want["replicates"] == 10000, "E-G3-I16")
    a = r["estimates"]
    _schema(a, runner.core.AGGREGATE_KEYS, "E-G3-I17")
    _require(type(a["n_question_slots"]) is int and a["n_question_slots"] == len(e["question_ids"]), "E-G3-I17")
    for scalar, vector, bound in zip(SCALARS, VECTORS, (100, 100, 200)):
        _require(_number(a[scalar], -bound, bound) and type(a[vector]) is list and len(a[vector]) == 10
                 and all(_number(v, -bound, bound) for v in a[vector])
                 and abs(a[scalar] - math.fsum(a[vector]) / 10) <= runner.core.TOL, "E-G3-I17")
    _require(all(abs(d - (y - x)) <= runner.core.TOL for x, y, d in
                 zip(a[VECTORS[0]], a[VECTORS[1]], a[VECTORS[2]])), "E-G3-I17")
    u = r["uncertainty"]
    _schema(u, {"scheme", "replicates", "percentiles", "intervals", "interpretation"}, "E-G3-I18")
    _require(u["scheme"] == scheme and type(u["replicates"]) is int and u["replicates"] == 10000
             and type(u["percentiles"]) is list and all(type(v) is float for v in u["percentiles"])
             and u["percentiles"] == [2.5, 97.5]
             and u["interpretation"] == "synthetic_sensitivity_not_certified_interval", "E-G3-I18")
    _schema(u["intervals"], SCALARS, "E-G3-I18")
    for key, bound in zip(SCALARS, (100, 100, 200)):
        interval = u["intervals"][key]
        _schema(interval, {"lo", "hi", "spans_zero"}, "E-G3-I18")
        lo, hi = interval["lo"], interval["hi"]
        _require(_number(lo, -bound, bound) and _number(hi, -bound, bound) and lo <= hi
                 and type(interval["spans_zero"]) is bool and interval["spans_zero"] == (lo <= 0 <= hi), "E-G3-I18")
    _require(_hash(r["result_sha256"]) and r["result_sha256"] ==
             _digest({k: v for k, v in r.items() if k != "result_sha256"}), "E-G3-I20")


@_boundary
def compute_synthetic_result(envelope, *, scheme="question"):
    e = _copy(envelope)
    _validate_envelope(e)
    _require(type(scheme) is str and scheme in ("question", "cluster")
             and not (e["benchmark"] == runner.LONGMEMEVAL and scheme == "cluster"), "E-G3-I15")
    computed = runner.compute_synthetic_results(e["records"], e["question_ids"], e["cluster_ids"],
                                               benchmark=e["benchmark"], scheme=scheme)
    _schema(computed, {"estimates", "uncertainty", "bootstrap_configuration"}, "E-G3-I14")
    u = computed["uncertainty"]
    _require(u["scheme"] == ("question-level" if scheme == "question" else "conversation-cluster"), "E-G3-I18")
    # Persist only the explicitly selected numeric uncertainty fields, not core prose.
    r = _copy({"schema_version": VERSION, "provenance": SYNTHETIC, "preparation": e, "scheme": scheme,
         "bootstrap_configuration": computed["bootstrap_configuration"], "estimates": computed["estimates"],
         "uncertainty": {"scheme": scheme, "replicates": u["replicates"], "percentiles": u["percentiles"],
             "intervals": {k: u[k] for k in SCALARS}, "interpretation": "synthetic_sensitivity_not_certified_interval"}})
    r["result_sha256"] = _digest(r)
    _validate_result(r)
    return r


@_boundary
def write_synthetic_result(path, result):
    """Validate/serialize first, then exclusive-create. Parent must exist.

    A failed new write may leave a partial file; no atomic-publication claim is made.
    Existing files, including ones created concurrently, are never truncated.
    """
    r = _copy(result)
    _validate_result(r)
    raw = _encoded(r) + b"\n"
    _require(type(path) in (str, type(HERE)), "E-G3-I21")
    exists = False
    try:
        with Path(path).open("xb") as stream:
            stream.write(raw)
    except FileExistsError:
        exists = True
    if exists:
        raise IntegrationError("E-G3-I98")
    return Path(path)


def compute_accepted_result(*_args, **_kwargs):
    raise IntegrationError("E-G3-I99")


def write_accepted_result(*_args, **_kwargs):
    raise IntegrationError("E-G3-I99")


def run_on_real_corpus(*_args, **_kwargs):
    raise IntegrationError("E-G3-I99")
