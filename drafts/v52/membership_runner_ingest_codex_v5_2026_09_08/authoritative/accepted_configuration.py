"""THE single authoritative source for this package. Everything downstream resolves from here.

Answers finding D-3 (the accepted seed values governed nothing) and part of the source-trust item: the
expected manifest hash is no longer an arbitrary caller argument, it is resolved from this chain.

WHY THIS IS A PYTHON MODULE AND NOT A JSON FILE. A committed JSON file is checked out through Git's
end-of-line filter, and on a default Windows clone (`core.autocrlf=true`, which is set in this
machine's SYSTEM config) its bytes differ from the blob it was written as — that is exactly finding
D-4. A Python module is read by the interpreter as source, so the VALUES below cannot be altered by a
line-ending filter. The artifacts these values point at are materialised byte-preservingly from Git
blobs by `resolve_sources.py`; nothing here trusts a checked-out copy.

NOTHING HERE IS NEW. Every value is transcribed from documents already accepted and hash-recorded on
`main` in ledger entries L-074 and L-075. No value is chosen, adjusted or invented in this file.
"""
from __future__ import annotations

# ------------------------------------------------------------------------------------------------
# Where the acceptance itself is recorded. A reader who lands in this package first should be able to
# get back to the decision without searching — that absence is what the review's governance question
# (a) called out, and this constant is the fix for it.
# ------------------------------------------------------------------------------------------------
ACCEPTANCE_RECORD = {
    "document": "drafts/v52/membership_ingest_v1_2026_09_08/BOUND_CONFIGURATION_ACCEPTANCE_2026-09-08.md",
    "commit": "22e44608bab838974a6e65aa1a4297c815b5506b",
    "sha256": "c5d2e63956426f61f28b19856e1298ac964b3a8228b7acf72ae32128f79e1d83",
    "ledger_entries": ["L-074", "L-075"],
    "ledger_branch": "main",
    "configuration_identity": {
        "document": "drafts/v52/membership_runner_v1_2026_09_08/CONFIGURATION_IDENTITY_2026-09-08.md",
        "commit": "e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf",
        "sha256": "33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739"},
}

# How to read the word "PROPOSED" in the older files, stated once, here, so nobody has to infer it.
PROPOSED_VS_ACCEPTED = (
    "Several files under drafts/v52/membership_runner_v1_2026_09_08/binding/ still carry the string "
    "'PROPOSED - NOT BOUND' in their own text and in their sidecars. That word records their state "
    "WHEN THEY WERE WRITTEN. It does NOT describe their status now. They were deliberately left "
    "byte-unchanged so their hashes keep resolving in L-072 and L-073, and the acceptance is carried "
    "by ACCEPTANCE_RECORD above. This module — not those files' own text — is what says which of them "
    "is accepted, which is superseded, and which was never accepted. Their identical wording is why "
    "the independent review called the relation coherent but ambiguous."
)

# ------------------------------------------------------------------------------------------------
# Benchmarks
# ------------------------------------------------------------------------------------------------
LOCOMO = "LoCoMo"
LONGMEMEVAL = "LongMemEval"
BENCHMARKS = (LOCOMO, LONGMEMEVAL)

# ------------------------------------------------------------------------------------------------
# The ACCEPTED cohort/mapping manifests. Addressed by (commit, path) and pinned by RAW GIT BLOB hash.
# ------------------------------------------------------------------------------------------------
ACCEPTED_MANIFESTS = {
    LOCOMO: {
        "commit": "6911a03af68cb48a5090690b05acec59a67ce211",
        "path": "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json",
        "blob_sha256": "66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671",
        "n_questions": 1535,
        "n_clusters": 10,
        "status": "ACCEPTED",
    },
    LONGMEMEVAL: {
        "commit": "e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf",
        "path": ("drafts/v52/membership_runner_v1_2026_09_08/binding/"
                 "PROPOSED_mapping_longmemeval_v2_source_resolved.json"),
        "blob_sha256": "d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714",
        "n_questions": 470,
        "n_clusters": 1,
        "status": "ACCEPTED (v2)",
    },
}

# Explicitly SUPERSEDED. Named here so the refusal can say WHY, instead of only "hash mismatch".
SUPERSEDED_MANIFESTS = {
    "d5b8ed69-predecessor": {
        "benchmark": LONGMEMEVAL,
        "path": "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_longmemeval.json",
        "blob_sha256": "bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886",
        "superseded_by": ACCEPTED_MANIFESTS[LONGMEMEVAL]["blob_sha256"],
        "reason": ("its source_sha256 was the placeholder 'UNRESOLVED-see-BINDING_PROPOSAL-section-1'. "
                   "v2 carries the verified raw-file identity. The 470 question ids and the sentinel "
                   "cluster are IDENTICAL in both, so a substitution would not be visible in the "
                   "cohort — only in the source binding."),
    },
}

# ------------------------------------------------------------------------------------------------
# The ACCEPTED bootstrap configuration. D-3: these are now consulted, not merely documented.
# ------------------------------------------------------------------------------------------------
SCHEMES = ("question", "cluster")

ACCEPTED_BOOTSTRAP = {
    (LOCOMO, "question"): {"seed": 52001107, "replicates": 10000},
    (LOCOMO, "cluster"): {"seed": 52001207, "replicates": 10000},
    (LONGMEMEVAL, "question"): {"seed": 52002107, "replicates": 10000},
}
# (LONGMEMEVAL, "cluster") is deliberately ABSENT: R2 line 141 defines no conversation-cluster
# bootstrap for LongMemEval. Its absence here is the authority for refusing that combination.

PERCENTILES = (2.5, 97.5)

RNG_RULE = {
    "algorithm": "numpy.random.Generator over the PCG64 bit generator, via numpy.random.default_rng(seed)",
    "generators": "one per (benchmark, scheme), seeded once from the accepted value, never reseeded mid-run",
    "question_scheme": ("one rng.integers(0, n_questions, size=n_questions) per replicate, the SAME index "
                        "set applied to all six arms and all ten rotation seeds; the seed panel is fixed "
                        "and never resampled (R1 section 6)"),
    "cluster_scheme": ("LoCoMo only: one rng.integers(0, n_clusters, size=n_clusters) per replicate, "
                       "conversations drawn WITH REPLACEMENT, each contributing ALL of its questions, "
                       "multiplicity preserved, the mean divided by the TOTAL NUMBER OF SELECTED QUESTION "
                       "SLOTS (acceptance record section 4)"),
    "source_of_the_values": ("drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_bootstrap_seeds.json "
                             "@ 6911a03af68cb48a5090690b05acec59a67ce211, blob sha256 "
                             "3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea, accepted by "
                             "ACCEPTANCE_RECORD"),
}

# ------------------------------------------------------------------------------------------------
# The ACCEPTED corpus source identities. Verified in the narrow data-identity task (L-074).
# ------------------------------------------------------------------------------------------------
ACCEPTED_SOURCES = {
    LOCOMO: {"filename": "locomo10.json",
             "sha256": "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4",
             "bytes": 2805274},
    LONGMEMEVAL: {"filename": "longmemeval_s_cleaned.json",
                  "sha256": "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442",
                  "bytes": 277383467},
}

# ------------------------------------------------------------------------------------------------
# The computation core this package binds to. Closed; byte-unchanged.
# ------------------------------------------------------------------------------------------------
BOUND_CORE = {
    "path": "drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py",
    "commit": "dcb568d0a6c33154c1568500325ad457b4d6f455",
    "blob_sha256": "bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72",
    "closure": ("audit/v52-membership-v3-closure-2026-09-07 @ aa0ee8a9b1468ceaf7fa6dc3acab17acc8423ae9, "
                "CLOSURE PASS"),
}

PACKAGE_VERSION = "membership runner+ingest Codex v5 2026-09-08"


def accepted_bootstrap(benchmark: str, scheme: str) -> dict:
    """The accepted seed and replicate count, or a description of why there is none.

    Returns the entry, or raises KeyError — callers turn that into a named refusal. Kept deliberately
    dumb: this module decides nothing, it only holds what was accepted.
    """
    return ACCEPTED_BOOTSTRAP[(benchmark, scheme)]
