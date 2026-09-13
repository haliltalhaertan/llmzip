# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Deterministic corpus builder (adversarial suite, own code).

Freezes cases.json from the INDEPENDENT oracle (oracle.py + truth.py) only.
Archived v2 verdicts are recorded as context observations, never as
expectations. Every exact case must close in the oracle (Sturm-proved root
inventory); failures raise instead of silently skipping. Bounded
supplemental fuzz uses exact arithmetic with recorded seeds and is labeled
as supplemental evidence, not proof.

Run: OMP_...=1 PYTHONDONTWRITEBYTECODE=1 python3 -B build_corpus.py
Writes: cases.json, receipts/corpus_receipt.json
"""
import importlib.util
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import truth as T  # noqa: E402
import oracle as OC  # noqa: E402
from fractions import Fraction as F  # noqa: E402

WS = "/home/mdp/muse-work/geometry-cert-adversarial"
ARCH_V2 = os.path.join(
    WS, "research_representation_geometry_2026_09_13/repairs/rank_cert/certify_v2.py")
FUZZ_SEED = 777001
FUZZ_N = 24

LABELS = ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
          "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"]


def load_v2():
    spec = importlib.util.spec_from_file_location("archived_certify_v2", ARCH_V2)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert os.path.realpath(mod.__file__) == os.path.realpath(ARCH_V2)
    return mod


def S(*xs):
    return [str(F(x)) for x in xs]


def named_cases():
    K = F(100)
    cases = []
    for k in (1, 10, 100, 1000):
        k = F(k)
        cases.append({
            "id": "poc_K%d" % int(k), "kind": "poc-scale-family",
            "p": S(-k, k, 0, k * k), "q": S(-2 * k, 2 * k, 7 * k * k, 0),
            "J": S(1, 4), "known_roots": ["1", "7/4"], "must_resolve": True,
            "notes": "score-preserving scaling; rational-root budget skips at K>=100",
        })
    cases += [
        {"id": "poc_reversed_K100", "kind": "poc-reversed",
         "p": S(-2 * K, 2 * K, 7 * K * K, 0),
         "q": S(-K, K, 0, K * K), "J": S(1, 4),
         "known_roots": ["1", "7/4"], "must_resolve": True,
         "notes": "docs swapped: signs negate, ties identical"},
        {"id": "tangent_realizable", "kind": "tangent-realizable",
         "p": S(F(3, 2), 1, 2, 4), "q": S(1, 0, 1, 0), "J": S(F(1, 4), 1),
         "known_roots": ["1/2"], "must_resolve": True,
         "notes": "from rank_cover/realizable_tangent.py; Q=(z-1/2)^2; touch, stable +1"},
        {"id": "tangent_abstract_only", "kind": "tangent-abstract",
         "p": S(1, 1, 0, 4), "q": S(1, 0, 1, 0), "J": S(F(1, 4), 4),
         "known_roots": ["1"], "must_resolve": True,
         "notes": "Q=(z-1)^2 touch, stable +1; p violates single_ok (u=0,a=1): abstract-only, kept separate"},
        {"id": "common_zero", "kind": "common-zero",
         "p": S(-1, 1, 1, 0), "q": S(-2, 2, 1, 0), "J": S(F(1, 2), 2),
         "known_roots": ["1"], "must_resolve": True,
         "notes": "shared numerator zero flips verdict +1->-1 with Q=-3(z-1)^2 touch (no Q crossing)"},
        {"id": "endpoint_tie_L", "kind": "endpoint-root",
         "p": S(0, 1, 1, 0), "q": S(0, 2, 1, 0), "J": S(0, 2),
         "known_roots": ["0"], "must_resolve": True,
         "notes": "Q=-3z^2; tie exactly at L=0; stable -1 inside"},
        {"id": "endpoint_tie_R", "kind": "endpoint-root",
         "p": S(-2, 1, 1, 0), "q": S(-4, 2, 1, 0), "J": S(1, 2),
         "known_roots": ["2"], "must_resolve": True,
         "notes": "Q=-3(z-2)^2; tie exactly at R=2; stable +1 inside"},
        {"id": "P_identically_zero", "kind": "persistent",
         "p": S(1, 2, 3, 4), "q": S(1, 2, 3, 4), "J": S(1, 2),
         "known_roots": [], "must_resolve": True,
         "notes": "p==q: Q identically 0; only PERSISTENT_TIE/UNRESOLVED sound"},
        {"id": "invalidJ_empty", "kind": "robustness",
         "p": S(-1, 1, 0, 1), "q": S(-2, 2, 7, 0), "J": S(2, 2),
         "known_roots": [], "must_resolve": False,
         "notes": "degenerate J (L==R): no crash; no interior order may be certified"},
        {"id": "invalidJ_inverted", "kind": "robustness",
         "p": S(-1, 1, 0, 1), "q": S(-2, 2, 7, 0), "J": S(4, 1),
         "known_roots": [], "must_resolve": False,
         "notes": "L>R: no crash; must not certify as if normal"},
        {"id": "invalidJ_domain", "kind": "robustness",
         "p": S(1, 1, -1, 1), "q": S(1, 0, 1, 0), "J": S(F(1, 4), F(1, 2)),
         "known_roots": [], "must_resolve": False,
         "notes": "D1=-1+z<0 on J: resolving verdicts unsound; only non-resolving sound"},
    ]
    return cases


def search_classes():
    """Deterministic small-integer search for strict/two-root classes.

    Keeps first closable candidate per class (oracle must close; rational
    enumeration must not skip). Fully deterministic nested loops.
    """
    found = {}
    cands = []
    rng = list(range(-3, 4))
    for a1 in rng:
        for b1 in rng:
            for u1 in range(0, 4):
                for v1 in range(0, 4):
                    for a2 in rng:
                        for b2 in rng:
                            for u2 in range(0, 4):
                                for v2 in range(0, 4):
                                    cands.append(((a1, b1, u1, v1), (a2, b2, u2, v2)))
    for J in ((F(1, 4), F(4)), (F(1), F(4))):
        for (t1, t2) in cands:
            p = tuple(F(x) for x in t1)
            q = tuple(F(x) for x in t2)
            if not OC.domain_ok(p, q, J[0], J[1]):
                continue
            Q = T.poly_coeffs_ind(p, q)
            if all(c == 0 for c in Q):
                continue
            rrs, sk = OC.rational_roots([F(c) for c in Q])
            if sk:
                continue
            inl = [r for r in rrs if J[0] < r < J[1]]
            try:
                cl = OC.classify(p, q, J[0], J[1], known_roots=list(rrs))
            except OC.OracleIncomplete:
                continue
            tr = cl["truth"]
            vals = set(tr.values())
            if 0 in vals:
                continue
            numneg = any(
                (F(t1[0]) + F(t1[1]) * F(z) < 0) or (F(t2[0]) + F(t2[1]) * F(z) < 0)
                for z in tr)
            key = None
            if vals == {1} and "strict_pos" not in found:
                key = "strict_pos"
            elif vals == {-1} and numneg and "strict_neg" not in found:
                key = "strict_neg"
            elif len(inl) == 2 and "two_roots" not in found:
                key = "two_roots"
            if key is not None:
                ent = {"id": "search_%s_J%s" % (key, "q" if J[0] == F(1, 4) else "w"),
                       "kind": {"strict_pos": "strict", "strict_neg": "strict-negative-numerators",
                                "two_roots": "two-exact-roots"}[key],
                       "p": S(*t1), "q": S(*t2), "J": S(*J),
                       "known_roots": [str(r) for r in rrs], "must_resolve": True,
                       "notes": "found by deterministic small-int search; oracle-closed"}
                # two_roots must actually carry two interior roots
                if key == "two_roots" and len(inl) != 2:
                    continue
                found[key] = ent
            if len(found) >= 3:
                break
        if len(found) >= 3:
            break
    assert len(found) >= 3, "search failed to close classes: %s" % sorted(found)
    return [found["strict_pos"], found["strict_neg"], found["two_roots"]]


def build_fuzz():
    rng = random.Random(FUZZ_SEED)
    kept, excluded = [], 0
    J = (F(1, 16), F(16))
    i = 0
    while len(kept) < FUZZ_N:
        i += 1
        assert i < 10000, "fuzz search runaway"
        t1 = (rng.choice(range(-3, 4)), rng.choice(range(-3, 4)),
              rng.choice(range(0, 4)), rng.choice(range(0, 4)))
        t2 = (rng.choice(range(-3, 4)), rng.choice(range(-3, 4)),
              rng.choice(range(0, 4)), rng.choice(range(0, 4)))
        p = tuple(F(x) for x in t1)
        q = tuple(F(x) for x in t2)
        if not OC.domain_ok(p, q, J[0], J[1]):
            excluded += 1
            continue
        Q = T.poly_coeffs_ind(p, q)
        if all(c == 0 for c in Q):
            excluded += 1
            continue
        rrs, sk = OC.rational_roots([F(c) for c in Q])
        if sk:
            excluded += 1
            continue
        try:
            OC.classify(p, q, J[0], J[1], known_roots=list(rrs))
        except OC.OracleIncomplete:
            excluded += 1
            continue
        kept.append({"id": "fuzz_%02d" % len(kept), "kind": "fuzz-supplemental",
                     "p": S(*t1), "q": S(*t2), "J": S(*J),
                     "known_roots": [str(r) for r in rrs], "must_resolve": False,
                     "notes": "supplemental fuzz evidence only; not proof of absence"})
    return kept, excluded


def freeze(entry):
    p = tuple(F(x) for x in entry["p"])
    q = tuple(F(x) for x in entry["q"])
    L, R = F(entry["J"][0]), F(entry["J"][1])
    if entry["kind"] == "robustness":
        if L == R:
            truth = {str(L): T.true_cmp(p, q, L)}
            oracle = {"domain": "ok", "robustness": "degenerate-J",
                      "truth": truth, "plus": truth[str(L)] == 1,
                      "minus": truth[str(L)] == -1}
        elif L > R:
            truth = {str(L): T.true_cmp(p, q, L), str(R): T.true_cmp(p, q, R)}
            oracle = {"domain": "ok", "robustness": "inverted-J",
                      "truth": truth, "plus": any(v == 1 for v in truth.values()),
                      "minus": any(v == -1 for v in truth.values())}
        else:
            assert not OC.domain_ok(p, q, L, R)
            oracle = {"domain": "fail", "robustness": "domain-fail"}
        return dict(entry, oracle=oracle)
    cl = OC.classify(p, q, L, R,
                     known_roots=[F(r) for r in entry["known_roots"]])
    assert cl["domain"] == "ok", entry["id"]
    return dict(entry, oracle=cl)


def main():
    V = load_v2()
    entries = named_cases() + search_classes()
    fuzz, fuzz_excluded = build_fuzz()
    entries += fuzz
    frozen = [freeze(e) for e in entries]
    # Context observations from archived v2 (NOT expectations) + oracle cross-check.
    obs = []
    agree = {"sturm": [0, 0], "rational_roots": [0, 0]}
    for e in frozen:
        p = tuple(F(x) for x in e["p"])
        q = tuple(F(x) for x in e["q"])
        L, R = F(e["J"][0]), F(e["J"][1])
        try:
            if L > R:
                o = {"status": "NOT_RUN_INVERTED", "direction": None, "ties": []}
            else:
                r = V.certify_pair(p, q, L, R)
                o = {"status": r["status"], "direction": r["direction"],
                     "ties": list(r["ties"])}
        except Exception as ex:  # noqa: BLE001 - observation only
            o = {"status": "TARGET_RAISED", "direction": None, "ties": [],
                 "error": "%s: %s" % (type(ex).__name__, ex)}
        # Cross-check own oracle vs archived primitives on closed subintervals.
        if e["oracle"].get("subintervals"):
            Q = [F(c) for c in e["oracle"]["Q"]]
            Pv = V.P_coeffs(p, q)
            assert [F(c) for c in Q] == [F(c) for c in Pv], e["id"]
            for s in e["oracle"]["subintervals"]:
                a, b = F(s["lo"]), F(s["hi"])
                mine = OC.sturm_open_count(Q, a, b)
                theirs = V.sturm_open_count(Pv, a, b)
                agree["sturm"][0] += (mine == theirs)
                agree["sturm"][1] += 1
            rrs_o, sk_o = OC.rational_roots(Q)
            rrs_v, sk_v = V.rational_roots(Pv)
            if not sk_o and not sk_v:
                agree["rational_roots"][0] += (list(rrs_o) == list(rrs_v))
                agree["rational_roots"][1] += 1
        obs.append({"id": e["id"], "v2_observation": o})
    with open(os.path.join(HERE, "cases.json"), "w") as f:
        json.dump({"labels": LABELS, "cases": frozen}, f, indent=2)
    with open(os.path.join(HERE, "receipts", "corpus_receipt.json"), "w") as f:
        json.dump({"labels": LABELS, "n_cases": len(frozen),
                   "fuzz_seed": FUZZ_SEED, "fuzz_kept": len(fuzz),
                   "fuzz_excluded": fuzz_excluded,
                   "oracle_vs_archived_agreement": agree,
                   "v2_observations": obs}, f, indent=2)
    print("cases=%d fuzz_kept=%d fuzz_excluded=%d" % (len(frozen), len(fuzz), fuzz_excluded))
    print("oracle/archived agreement:", agree)
    for o in obs:
        v = o["v2_observation"]
        print("%-28s %s %s %s" % (o["id"], v["status"], v["direction"], v["ties"][:4]))


if __name__ == "__main__":
    main()
