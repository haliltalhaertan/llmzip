"""G-3 obligation-4 bridge for synthetic/in-memory verification only.

This module consumes already prepared per-question records and delegates aggregation,
bootstrap, provenance checks, and overwrite-protected persistence to the reviewed G-3
runner lineage. It contains no corpus reader, no experiment driver, no seal/finalize
operation, no authorization construction, and no outcome-access path.
"""
from __future__ import annotations

from pathlib import Path

import membership_runner_g3 as runner


class IntegrationError(ValueError):
    pass


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise IntegrationError(code)


def compute_accepted_result(prepared, question_ids, cluster_ids, mapping, seed_record_path, *,
                            benchmark: str, scheme: str,
                            replicates: int = runner.core.BOOTSTRAP_REPLICATES):
    """Route an in-memory prepared record set through the accepted result path.

    The mapping and seed record remain governed by ``membership_runner_g3``; this
    function adds only a fail-closed non-empty/schema guard around the preparation
    handoff. It does not read a corpus or authorize any experiment.
    """
    _require(type(prepared) is dict, "E-G3-I01: prepared result schema")
    records = prepared.get("records")
    diagnostics = prepared.get("diagnostics")
    _require(type(records) is list and len(records) > 0, "E-G3-I02: empty prepared records")
    _require(type(diagnostics) is list and len(diagnostics) > 0,
             "E-G3-I03: missing preparation diagnostics")
    _require(type(question_ids) is list and len(question_ids) > 0
             and all(type(q) is str for q in question_ids)
             and len(question_ids) == len(set(question_ids)),
             "E-G3-I04: question ids")
    _require(type(cluster_ids) is list and len(cluster_ids) == len(question_ids)
             and all(type(c) is str for c in cluster_ids),
             "E-G3-I05: cluster ids")
    return runner.compute_results(
        records, question_ids, cluster_ids, mapping, Path(seed_record_path),
        benchmark=benchmark, scheme=scheme, replicates=replicates,
        scaling_diagnostics={"archives": diagnostics},
    )


def write_accepted_result(path, result):
    """Persist a computed synthetic result through the inherited no-overwrite writer."""
    return runner.write_results(Path(path), result)


def run_on_real_corpus(*_args, **_kwargs):
    raise IntegrationError("E-G3-I99: real execution not authorized")