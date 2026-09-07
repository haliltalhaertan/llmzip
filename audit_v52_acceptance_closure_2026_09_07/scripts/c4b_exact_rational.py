"""C4b — exact-rational cross-check of the acceptance decision's A/B table.

The per-question rows are decimal strings; every downstream operation is a
sum, a division and a mean. All of that is exact in Q. So the true values of
A and B are computable exactly, and both the document's float literals and my
own float recomputation can be measured against them.

Also checks the document's "A - B" column: whether each stated difference is
the exact difference, the correctly-rounded float difference, or a truncation.

Negative control included and shown failing.
"""
import gzip, csv, sys, json
from fractions import Fraction as F
from decimal import Decimal, getcontext
from pathlib import Path
from collections import defaultdict

getcontext().prec = 60
WORK = Path(sys.argv[1]); OUT = Path(sys.argv[2])
SEEDS = list(range(59001, 59011))
ARMS = ["NATIVE", "FULLHAAR_FRESH", "SCALED_FULLHAAR", "BLOCK32_FRESH", "SCALED_BLOCK32"]


def exact_arm_seed_means(path):
    sums = defaultdict(F); counts = defaultdict(int)
    with gzip.open(path, "rt", newline="") as fh:
        for row in csv.DictReader(fh):
            k = (row["arm"], int(row["rotation_seed"]))
            sums[k] += F(row["fractional_R3"]); counts[k] += 1
    return {k: sums[k] / counts[k] for k in sums if k[0] in ARMS}


def exact_AB(m):
    M = {a: sum((m[(a, s)] for s in SEEDS), F(0)) / len(SEEDS) for a in ARMS}
    out = {}
    for label, fresh, scaled in (("full", "FULLHAAR_FRESH", "SCALED_FULLHAAR"),
                                 ("block", "BLOCK32_FRESH", "SCALED_BLOCK32")):
        ps = [(m[(scaled, s)] - m[(fresh, s)]) / (M["NATIVE"] - m[(fresh, s)]) for s in SEEDS]
        A = sum(ps, F(0)) / len(ps)
        B = (M[scaled] - M[fresh]) / (M["NATIVE"] - M[fresh])
        out[label] = (A, B)
    return out


def d(fr, n=30):
    return str(+Decimal(fr.numerator) / Decimal(fr.denominator)).__str__()[:n + 2]


DOC = {
    ("LoCoMo", "full"):      ("0.7271861342884777", "0.7261069075901362", "0.0010792266983414844"),
    ("LoCoMo", "block"):     ("0.4454425786787960", "0.6516429195680419", "-0.2062003408892458"),
    ("LongMemEval", "full"): ("0.6569781664714960", "0.6563342970957214", "0.0006438693757745"),
    ("LongMemEval", "block"):("0.3165111621882831", "0.3084585844542308", "0.0080525777340523"),
}

res = {}
rows = []
for bench, f in (("LoCoMo", "locomo.csv.gz"), ("LongMemEval", "lme.csv.gz")):
    ab = exact_AB(exact_arm_seed_means(WORK / f))
    for arm in ("full", "block"):
        A, B = ab[arm]
        dA, dB, dD = DOC[(bench, arm)]
        errA = abs(F(dA) - A); errB = abs(F(dB) - B)
        exact_diff = A - B
        stated = F(dD)
        # is the stated difference the correctly rounded float of docA-docB?
        float_docdiff = float(dA) - float(dB)
        rows.append({
            "benchmark": bench, "arm": arm,
            "exact_A": d(A), "doc_A": dA, "abs_err_doc_A": f"{float(errA):.3e}",
            "exact_B": d(B), "doc_B": dB, "abs_err_doc_B": f"{float(errB):.3e}",
            "exact_A_minus_B": d(exact_diff),
            "doc_A_minus_B": dD,
            "abs_err_doc_diff_vs_exact": f"{float(abs(stated - exact_diff)):.3e}",
            "doc_diff_equals_float(docA)-float(docB)": float(dD) == float_docdiff,
            "float(docA)-float(docB)": repr(float_docdiff),
            "doc_diff_is_truncation_of_exact": d(exact_diff, 25).startswith(dD.rstrip("0")) if dD[0] != "-" else d(exact_diff, 25).startswith(dD.rstrip("0")),
        })
    res[bench] = {a: {"A": d(ab[a][0]), "B": d(ab[a][1])} for a in ("full", "block")}

# NEGATIVE CONTROL: a value one decimal digit off must register a large error.
fakeA = F("0.7271861342884877")
trueA = F(res["LoCoMo"]["full"]["A"])
nc = {
    "NC5_exact_check_can_fail": {
        "fake_A": str(fakeA),
        "abs_err": f"{float(abs(fakeA - trueA)):.3e}",
        "would_be_accepted_at_1e-15": float(abs(fakeA - trueA)) < 1e-15,
        "control_passes_iff_false": True,
    }
}

OUT.write_text(json.dumps({"exact": res, "rows": rows, "negative_controls": nc}, indent=2))
for r in rows:
    print(json.dumps(r, indent=1))
print("NEGATIVE CONTROL:", json.dumps(nc))
