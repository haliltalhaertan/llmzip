"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Coordinator independent audit of the math_r1/quant worker.

Everything is RE-DERIVED from per_query.jsonl (stored top-10 ids + gold). The worker's
RESULTS.json is only the thing being CHECKED - never a source of truth.

Checks:
  A. FULL arm reproduces the frozen production anchors (both benchmarks).
  B. Every summary hit10/fr3/hit3 recomputed from stored ids.
  C. Every contrast mean recomputed as a paired per-query difference.
  D. The headline claim: is the RealTalk ITQ collapse real, and is ITQ != random?
  E. Sanity: rotation arms must still be 96 bits; ids must be a permutation-free top-10.
"""
import json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(HERE, "..", "math_r1", "quant")

ANCHOR = {
    "RealTalk": {"FULL/qscale": {"hit10": 49.6454, "fr3": 22.41},
                 "FULL/sym":    {"hit10": 46.5248}},
    "PerLTQA":  {"FULL/qscale": {"hit10": 80.0000, "fr3": 53.24},
                 "FULL/sym":    {"hit10": 75.6806}},
}

def main():
    res = json.load(open(os.path.join(Q, "RESULTS.json"), encoding="utf-8"))

    # ---- load per-query rows, recompute metrics ourselves ----
    hit = defaultdict(list)     # (bench, arm/scorer) -> per-query 0/1
    fr3 = defaultdict(list)
    hit3 = defaultdict(list)
    per_q = defaultdict(dict)   # (bench, arm/scorer) -> qid -> hit  (for paired contrasts)
    nbits = set()
    bad_len = 0
    n_rows = 0

    with open(os.path.join(Q, "per_query.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            n_rows += 1
            b = r.get("benchmark") or r.get("bench")
            arm = r.get("arm"); sc = r.get("scorer")
            qid = r.get("qid") or r.get("question_id")
            gold = set(r.get("gold") or [])
            top = r.get("top10") or r.get("top") or []
            if len(top) != 10:
                bad_len += 1
            if "n_bits" in r:
                nbits.add(r["n_bits"])
            key = (b, f"{arm}/{sc}")
            h = 1.0 if (gold & set(top)) else 0.0
            hit[key].append(h)
            t3 = set(top[:3])
            fr3[key].append(len(gold & t3) / len(gold) if gold else 0.0)
            hit3[key].append(1.0 if (gold & t3) else 0.0)
            per_q[key][qid] = h

    print(f"rows={n_rows}  top10_length_violations={bad_len}  n_bits_seen={sorted(nbits)}")

    def pct(v):
        return 100.0 * sum(v) / len(v) if v else float("nan")

    # ---- A. anchors ----
    print("\n=== A. production anchors (FULL arm) ===")
    a_fail = 0
    for b, arms in ANCHOR.items():
        for armsc, exp in arms.items():
            got = pct(hit[(b, armsc)])
            d = abs(got - exp["hit10"])
            ok = d < 0.01
            a_fail += 0 if ok else 1
            print(f"  {b:9s} {armsc:14s} hit10 got={got:.4f} expect={exp['hit10']:.4f} d={d:.4f} {'OK' if ok else 'FAIL'}")
            if "fr3" in exp:
                g2 = pct(fr3[(b, armsc)]); d2 = abs(g2 - exp["fr3"])
                ok2 = d2 < 0.01
                a_fail += 0 if ok2 else 1
                print(f"  {b:9s} {armsc:14s} fr3   got={g2:.4f} expect={exp['fr3']:.4f} d={d2:.4f} {'OK' if ok2 else 'FAIL'}")

    # ---- B. every reported summary number ----
    print("\n=== B. summary numbers re-derived from stored ids ===")
    b_fail = 0
    for b, v in res["benchmarks"].items():
        for armsc, s in v["summary"].items():
            key = (b, armsc)
            if key not in hit:
                print(f"  MISSING per-query rows for {b} {armsc}"); b_fail += 1; continue
            for field, mine in (("hit10_pct", pct(hit[key])),
                                ("fr3_pct", pct(fr3[key])),
                                ("hit3_pct", pct(hit3[key]))):
                theirs = s.get(field)
                if theirs is None:
                    continue
                d = abs(mine - theirs)
                if d > 0.01:
                    print(f"  MISMATCH {b} {armsc} {field}: mine={mine:.4f} theirs={theirs:.4f}")
                    b_fail += 1
            if s.get("n") != len(hit[key]):
                print(f"  N MISMATCH {b} {armsc}: mine={len(hit[key])} theirs={s.get('n')}")
                b_fail += 1
    print(f"  summary mismatches: {b_fail}")

    # ---- C. contrasts (paired means) ----
    print("\n=== C. contrast means re-derived (paired per query) ===")
    c_fail = 0
    for b, v in res["benchmarks"].items():
        for block in ("contrasts_vs_FULL_pp", "itq_minus_rand_pp"):
            for name, c in v.get(block, {}).items():
                base, scorer = name.rsplit("/", 1)
                if "-" not in base:
                    continue
                lhs, rhs = base.split("-", 1)
                ka, kb = (b, f"{lhs}/{scorer}"), (b, f"{rhs}/{scorer}")
                if ka not in per_q or kb not in per_q:
                    continue
                common = set(per_q[ka]) & set(per_q[kb])
                mine = 100.0 * sum(per_q[ka][q] - per_q[kb][q] for q in common) / len(common)
                theirs = c["hit10"]["mean_diff_pp"]
                d = abs(mine - theirs)
                if d > 0.01:
                    print(f"  MISMATCH {b} {name}: mine={mine:+.4f} theirs={theirs:+.4f}")
                    c_fail += 1
    print(f"  contrast mismatches: {c_fail}")

    # ---- D. the headline ----
    print("\n=== D. headline: ITQ collapse on RealTalk, ITQ vs random ===")
    for b in ("RealTalk", "PerLTQA"):
        f = pct(hit[(b, "FULL/qscale")])
        i = pct(hit[(b, "ITQ_C/qscale")])
        rs = [pct(hit[(b, f"RAND_{s}/qscale")]) for s in (20260916, 20260917, 20260918)]
        rmean = sum(rs) / len(rs)
        print(f"  {b:9s} FULL={f:.2f}  ITQ={i:.2f}  RAND(mean of 3)={rmean:.2f}  "
              f"ITQ-FULL={i-f:+.2f}  ITQ-RAND={i-rmean:+.2f}")
        print(f"            RAND spread: {min(rs):.2f}..{max(rs):.2f}")

    # ---- E. cost reality check ----
    print("\n=== E. cost: is the rotation bigger than the payload it improves? ===")
    for b, v in res["benchmarks"].items():
        c = v["cost"]
        pay = c["payload_bytes_total"]
        r32 = c["rotation_R_bytes"]["float32_total"]
        print(f"  {b:9s} payload={pay:,} B   R(float32)={r32:,} B   ratio={r32/pay:.2f}x")

    verdict = "ACCEPT" if (a_fail == 0 and b_fail == 0 and c_fail == 0 and bad_len == 0) else "REJECT"
    print(f"\n=== VERDICT: {verdict} (anchors={a_fail}, summary={b_fail}, contrasts={c_fail}, len={bad_len}) ===")

if __name__ == "__main__":
    main()
