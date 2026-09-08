"""A synthetic data adapter - the ONLY adapter shipped, and it touches no corpus.

It fabricates a cohort whose conversation mapping is KNOWN by construction, so the source-identity
contract can be demonstrated against ground truth rather than against a plausible-looking file. It
also fabricates archive and query representations so the N-4 obligation can be exercised end to end.

Nothing here reads, downloads or approximates any real dataset. The numbers are drawn from a seeded
generator and mean nothing scientifically; they exist so the plumbing can be tested.
"""
from __future__ import annotations

import numpy as np

import membership_runner as R
import membership_scaling_core as core

CONVERSATIONS = tuple(f"conv-{i:02d}" for i in range(1, 11))          # ten, as LoCoMo has ten
QUESTIONS_PER_CONVERSATION = 4


def build_cohort():
    """Return (question_ids, cluster_ids) with a known, exact question -> conversation mapping."""
    q, c = [], []
    for conv in CONVERSATIONS:
        for j in range(QUESTIONS_PER_CONVERSATION):
            q.append(f"{conv}-q{j}")
            c.append(conv)
    return q, c


def build_mapping_manifest(question_ids, cluster_ids, benchmark=R.LOCOMO,
                           source_id="synthetic-cohort-v1", source_sha256="0" * 64) -> dict:
    """The expected-mapping manifest for this synthetic cohort, in the runner's declared schema."""
    return {
        "source_id": source_id,
        "source_sha256": source_sha256,
        "benchmark": benchmark,
        "expected_cluster_ids": sorted(set(cluster_ids)),
        "expected_question_to_cluster": dict(zip(question_ids, cluster_ids)),
        "n_questions": len(question_ids),
    }


def build_records(question_ids, seed=20260908, effect_pp=0.08, shrink=0.55):
    """Per-question fractional R@3 for all six arms at all ten rotation seeds.

    The generator is arranged so the gap `B32 - RANDOM32` is positive on average and the scaled gap
    is a shrunken version of it, which is what the estimand is shaped to measure. That is a fixture
    property, chosen for testability. It is NOT a prediction about the real experiment.
    """
    rng = np.random.default_rng(seed)
    records = []
    for q in question_ids:
        for k in core.ROTATION_SEEDS:
            base = float(rng.uniform(0.25, 0.55))
            gap = effect_pp * float(rng.uniform(0.6, 1.4))
            vals = {
                "NATIVE": base + 0.05,
                "SCALED_NATIVE": base + 0.045,
                "RANDOM32_FRESH": base,
                "B32_FRESH": base + gap,
                "SCALED_RANDOM32": base + 0.002,
                "SCALED_B32": base + 0.002 + gap * shrink,
            }
            for arm, v in vals.items():
                records.append({"question_id": q, "rotation_seed": int(k), "arm": arm,
                                "fractional_R3": float(min(max(v, 0.0), 1.0))})
    return records


def build_representations(n_archive=64, n_query=12, seed=5204):
    """A synthetic archive and a synthetic query block, both (n, 96).

    The query block is drawn from a DIFFERENT distribution than the archive on purpose: if a runner
    ever estimated the centering vector or D from the query, the two would visibly disagree, so the
    N-4 test is testing something rather than confirming an identity that holds by luck.
    """
    rng = np.random.default_rng(seed)
    archive = rng.normal(loc=0.3, scale=1.7, size=(n_archive, core.DIM))
    query = rng.normal(loc=-1.1, scale=0.4, size=(n_query, core.DIM))
    return archive, query
