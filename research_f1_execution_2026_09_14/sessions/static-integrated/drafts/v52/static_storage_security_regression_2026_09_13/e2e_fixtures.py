"""Realistic end-to-end fixture builder for the security regression suite.

Builds a complete, valid 470-archive LongMemEval preparation set against the
REAL pinned anchor (``docs/v52/task4c2/V52_T4C2_feature_geometry.csv``) and the
REAL measurement contract, so the gate's public entrypoint runs its full
``parent guard -> anchor semantics -> V6 bindings`` chain on temp files.

No fixture in this module is valid by construction alone: every file's SHA is
computed from its bytes and handed to the gate as the expected digest, exactly
as a real caller must. Mutation helpers below re-issue the expected digests
after sabotage so each test isolates ONE layer (hash identity vs semantics).
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import gate_adapter

ANCHOR_PATH = gate_adapter.REPO_ROOT / "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"
CONTRACT_PATH = (
    gate_adapter.REPO_ROOT
    / "drafts/v52/static_storage_contract_2026_09_12/MEASUREMENT_CONTRACT_TR.md"
)

EXPECTED_ARCHIVES = 470


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass
class FixtureSet:
    root: Path
    plan_path: Path
    plan_sha: str
    fixture_path: Path
    fixture_sha: str
    physical_path: Path
    physical_sha: str


def anchor_rows():
    with ANCHOR_PATH.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == EXPECTED_ARCHIVES, f"anchor rows: {len(rows)}"
    return [(r["question_id"], int(r["N_archive"])) for r in rows]


def _fixture_artifact_bytes() -> bytes:
    return json.dumps({
        "schema": "V52_SYNTHETIC_FIXTURE_BUNDLE_V3",
        "transform": {"input_utf8": "probe"},
        "id_mapping": {"rows": [
            {"logical_id": "L0", "offset": 0, "payload_utf8": "a"},
            {"logical_id": "L1", "offset": 1, "payload_utf8": "b"}]},
        "corruption": {"strategy": "XOR_SINGLE_BYTE", "byte_offset": 0,
                       "xor_mask": 7},
    }, sort_keys=True).encode("utf-8")


def _plan_dict(run_id: str, contract_sha: str, fixture_sha: str,
               archive_counts: dict[str, int] | None = None):
    aids = anchor_rows()
    if archive_counts:
        aids = [(aid, archive_counts.get(aid, n)) for aid, n in aids]
    archives, probes, populations, copies = [], [], [], []
    for i, (aid, n) in enumerate(aids):
        archives.append({"id": aid, "N_i": n})
        pid = f"pr-{i}"
        probes.append({"id": pid, "archive_id": aid, "N": n, "q": 1,
                       "fixture_id": "fx1"})
        popb, popa = f"pop-{i}-b", f"pop-{i}-a"
        populations.append({"id": popb, "archive_id": aid, "probe_id": pid,
                            "phase": "BEFORE", "count": n,
                            "member_ids_sha256": sha_bytes(f"m{aid}b".encode())})
        populations.append({"id": popa, "archive_id": aid, "probe_id": pid,
                            "phase": "AFTER", "count": n + 1,
                            "member_ids_sha256": sha_bytes(f"m{aid}a".encode())})
        copies.append({"id": f"copy-{i}", "item_id": "item1", "archive_id": aid,
                       "config_id": "cfg1", "format_id": "fmt1",
                       "artifact_identity": f"phys-ident-{i:04d}",
                       "artifact_sha256": None, "population_ids": [popb, popa]})
    return archives, probes, populations, copies


def build_valid_set(root: Path, run_id: str) -> FixtureSet:
    """Write plan + bindings + artifacts; return paths with matching digests."""
    root.mkdir(parents=True, exist_ok=True)
    contract_sha = sha_bytes(CONTRACT_PATH.read_bytes())
    fixture_raw = _fixture_artifact_bytes()
    (root / "fixture0.bin").write_bytes(fixture_raw)
    fixture_sha = sha_bytes(fixture_raw)
    aids = anchor_rows()
    archives, probes, populations, copies = _plan_dict(run_id, contract_sha,
                                                       fixture_sha)
    phys_rows = []
    for i, (aid, _n) in enumerate(aids):
        praw = f"physical-bytes-{run_id}-{i:04d}".encode()
        (root / f"phys-{i:04d}.bin").write_bytes(praw)
        copies[i]["artifact_sha256"] = sha_bytes(praw)
        phys_rows.append({"physical_copy_id": copies[i]["id"],
                          "physical_locator": f"phys-{i:04d}.bin",
                          "source_raw_byte_length": len(praw),
                          "artifact_sha256": sha_bytes(praw),
                          "sharing_denominator_rule": "POPULATION_COUNT",
                          "absence_basis": None})
    ops = [{"id": "op-t", "kind": "TRANSFORM",
            "implementation_identity": "impl-t"},
           {"id": "op-m", "kind": "ID_MAPPING",
            "implementation_identity": "impl-m"}]
    controls, k = [], 0
    for op in ops:
        controls.append({"id": f"ct-{k}", "config_id": "cfg1",
                         "operation_id": op["id"], "scope": "BASELINE",
                         "item_ids": [], "action": "BASELINE",
                         "expected_outcome": "MATCH",
                         "reference_identity": "ref-base",
                         "applicability": "APPLICABLE", "na_reason": None})
        k += 1
        for act in ("REMOVE", "RESTORE", "CORRUPT"):
            controls.append({"id": f"ct-{k}", "config_id": "cfg1",
                             "operation_id": op["id"],
                             "scope": "FALLBACK_COMBINED", "item_ids": ["item1"],
                             "action": act, "expected_outcome": "MATCH",
                             "reference_identity": "ref-comb",
                             "applicability": "APPLICABLE", "na_reason": None})
            k += 1
            controls.append({"id": f"ct-{k}", "config_id": "cfg1",
                             "operation_id": op["id"], "scope": "PER_ITEM",
                             "item_ids": ["item1"], "action": act,
                             "expected_outcome": "MATCH",
                             "reference_identity": "ref-item",
                             "applicability": "APPLICABLE", "na_reason": None})
            k += 1
    plan = {"schema": "v52.static-storage-plan", "version": 1, "status": "READY",
            "contract_sha256": contract_sha, "run_id": run_id,
            "weighting": {"primary": "archive_weighted_mean_i(C_i/N_i)",
                          "secondary": "vector_weighted_sum_i(C_i)/sum_i(N_i)"},
            "archives": archives,
            "formats": [{"id": "fmt1", "serialization": "raw", "dtype": "uint8",
                         "representation": "REAL"}],
            "analysis_mode": "PREDECLARED", "parent_plan_sha256": None,
            "configurations": [{"id": "cfg1", "format_ids": ["fmt1"],
                                "item_ids": ["item1"]}],
            "probes": probes,
            "items": [{"id": "item1", "role": "sample",
                       "disposition": "INCLUDED", "reason": "needed",
                       "cost_scope": "PER_VECTOR", "source_identity": "src-1",
                       "exclusion_basis": None}],
            "populations": populations, "physical_copies": copies,
            "fixtures": [{"id": "fx1", "kind": "SYNTHETIC", "sha256": fixture_sha,
                          "generator_identity": "gen-e2e"}],
            "operations": ops, "controls": controls}
    plan_raw = json.dumps(plan, sort_keys=True).encode("utf-8")
    plan_path = root / "plan.json"
    plan_path.write_bytes(plan_raw)
    fxdoc = {"schema": "v52.fixture-bindings", "version": 3, "fixtures": [{
        "fixture_id": "fx1", "relative_path": "fixture0.bin",
        "byte_length": len(fixture_raw), "sha256": fixture_sha,
        "content_schema": "V52_SYNTHETIC_FIXTURE_BUNDLE_V3",
        "consumer_sections": {"TRANSFORM": "transform",
                              "ID_MAPPING": "id_mapping",
                              "CORRUPT": "corruption"}}]}
    fx_raw = json.dumps(fxdoc, sort_keys=True).encode("utf-8")
    fixture_path = root / "fixture.bindings.json"
    fixture_path.write_bytes(fx_raw)
    pdoc = {"schema": "v52.physical-copy-bindings", "version": 4,
            "physical_copies": phys_rows}
    phys_raw = json.dumps(pdoc, sort_keys=True).encode("utf-8")
    physical_path = root / "physical.bindings.json"
    physical_path.write_bytes(phys_raw)
    return FixtureSet(root, plan_path, sha_bytes(plan_raw), fixture_path,
                      sha_bytes(fx_raw), physical_path, sha_bytes(phys_raw))


def corrupt_first_physical_artifact(fx: FixtureSet) -> None:
    """Rewrite one artifact in place (digest now stale on purpose)."""
    target = fx.root / "phys-0000.bin"
    raw = target.read_bytes()
    target.write_bytes(raw + b"\x00CORRUPTED")


def rewrite_physical_bindings_with_duplicate(fx: FixtureSet) -> FixtureSet:
    """Append a second row reusing copy-0's id; re-issue the bindings digest."""
    doc = json.loads(fx.physical_path.read_bytes().decode("utf-8"))
    dup = dict(doc["physical_copies"][0])
    dup["physical_locator"] = "phys-0001.bin"
    doc["physical_copies"].append(dup)
    raw = json.dumps(doc, sort_keys=True).encode("utf-8")
    fx.physical_path.write_bytes(raw)
    fx.physical_sha = sha_bytes(raw)
    return fx


def rewrite_plan_with_inflated_denominator(fx: FixtureSet,
                                           extra: int = 1000) -> FixtureSet:
    """Raise archive-0's probe N and BEFORE count by ``extra``; re-issue digest.

    The tampered plan stays guard-shaped (count == N) so only the anchored
    semantic layer can refuse it: N no longer equals the pinned N_archive.
    """
    plan = json.loads(fx.plan_path.read_bytes().decode("utf-8"))
    aid0 = plan["archives"][0]["id"]
    probe = next(p for p in plan["probes"] if p["archive_id"] == aid0)
    probe["N"] += extra
    for pop in plan["populations"]:
        if pop["probe_id"] == probe["id"]:
            pop["count"] += extra
    raw = json.dumps(plan, sort_keys=True).encode("utf-8")
    fx.plan_path.write_bytes(raw)
    fx.plan_sha = sha_bytes(raw)
    return fx


def rewrite_plan_with_new_run_id(fx: FixtureSet, run_id: str) -> bytes:
    """Return tampered-but-content-valid plan bytes (caller keeps stale digest)."""
    plan = json.loads(fx.plan_path.read_bytes().decode("utf-8"))
    plan["run_id"] = run_id
    return json.dumps(plan, sort_keys=True).encode("utf-8")
