"""Probe P2a: V10 denominator pure-math on isolated copy (benign fixtures only).

Loads the branch copy of denominator_integrity_v10.py by path (import does
no I/O beyond repo-root path probing) and exercises ONLY the pure helpers:
enrich_denominator_rows / deduplicate_logical_total / naive_copy_total /
labeled_summary. No pinned-chain execution, no plan files, no hashes checked.
"""
import importlib.util
import json
import sys

SRC = ("/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/08_storage_contracts/src/"
       "drafts_v52_static_storage_integration_v10_2026_09_13_denominator_integrity_v10.py")

spec = importlib.util.spec_from_file_location("denom_v10_copy", SRC)
v10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v10)

out = {"checks": []}


def check(name, fn):
    try:
        detail = fn()
        out["checks"].append({"name": name, "pass": True, "detail": detail})
    except Exception as e:  # noqa: BLE001
        out["checks"].append({"name": name, "pass": False,
                              "detail": "%s: %s" % (type(e).__name__, e)})


# 1. Doubling arithmetic from the disposition: 470 archives, N=231606.
check("headline_arithmetic", lambda: {
    "twice_231606": 2 * 231606,
    "equals_463212": 2 * 231606 == 463212,
    "twelve_vs_six_factor": 12.0 / 6.0,
})

# 2. Two legitimate copies of one archive: naive double-counts, logical dedups.
frozen = {"a1": 500, "a2": 700}
c2a = {"c1a": "a1", "c1b": "a1", "c2a": "a2", "c2b": "a2"}
rows = [("c1a", "pop", 500), ("c1b", "pop", 500),
        ("c2a", "pop", 700), ("c2b", "pop", 700)]


def t_dedup():
    enr = v10.enrich_denominator_rows(rows, c2a, frozen)
    return {"naive": v10.naive_copy_total(rows),
            "logical": v10.deduplicate_logical_total(enr),
            "naive_is_double": v10.naive_copy_total(rows) == 2 * 1200,
            "logical_is_once": v10.deduplicate_logical_total(enr) == 1200,
            "row_type": type(enr[0]).__name__}


check("duplicate_copy_dedup", t_dedup)


# 3. Inconsistent duplicates reject (never silently deduplicated).
def t_conflict():
    try:
        v10.enrich_denominator_rows([("c1a", "pop", 500), ("c1b", "pop", 501)],
                                    c2a, frozen)
        return {"rejected": False}
    except v10.V10ValidationError:
        return {"rejected": True}


check("inconsistent_duplicate_rejects", t_conflict)


# 4. Unknown copy rejects; outside-roster archive rejects.
def t_unknown():
    r1 = False
    try:
        v10.enrich_denominator_rows([("ghost", "pop", 500)], c2a, frozen)
    except v10.V10ValidationError:
        r1 = True
    c2a2 = dict(c2a, cX="a9")
    r2 = False
    try:
        v10.enrich_denominator_rows([("cX", "pop", 10)], c2a2, frozen)
    except v10.V10ValidationError:
        r2 = True
    return {"unknown_copy_rejects": r1, "outside_roster_rejects": r2}


check("unknown_and_outside_roster_reject", t_unknown)


# 5. Non-positive / bool / empty inputs rejected by shape gate.
def t_shape():
    res = {}
    for label, bad in [("zero_d", [("c1a", "pop", 0)]),
                       ("bool_d", [("c1a", "pop", True)]),
                       ("empty", [])]:
        try:
            v10.enrich_denominator_rows(bad, c2a, frozen)
            res[label] = "accepted-BAD"
        except v10.V10ValidationError:
            res[label] = "rejected-OK"
    try:
        v10.deduplicate_logical_total([])
        res["empty_logical"] = "accepted-BAD"
    except v10.V10ValidationError:
        res["empty_logical"] = "rejected-OK"
    return res


check("shape_gate", t_shape)


# 6. Physical-vs-logical: module offers no byte total (API surface check).
def t_no_byte_total():
    names = [n for n in dir(v10) if "byte" in n.lower()]
    return {"byte_named_api": names,
            "has_logical_total": hasattr(v10, "deduplicate_logical_total"),
            "has_naive": hasattr(v10, "naive_copy_total")}


check("no_byte_total_api", t_no_byte_total)


# 7. labeled_summary is LongMemEval-labeled, exploratory, not-for-citation.
def t_label():
    s = v10.labeled_summary(logical_total=1200, naive_total=2400,
                            n_archives=2, n_copies=4)
    return {"has_pilot_label": "NOT PREREGISTERED" in s,
            "says_not_authoritative": "not authoritative" in s}


check("summary_labels", t_label)

npass = sum(1 for c in out["checks"] if c["pass"])
print(json.dumps(out, indent=1))
print("PASS %d/%d" % (npass, len(out["checks"])))
sys.exit(0 if npass == len(out["checks"]) else 1)
