#!/usr/bin/env python3
"""Would run-length encoding shrink the 96-bit codes?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The proposal: write 111110001100 as (5x1)(3x0)(2x1)(2x0), i.e. "51302120".
That is run-length encoding, and it is the right instinct -- it is how you
compress anything with long stretches of the same value.

Whether it helps here is an empirical question about OUR codes, so this
measures it rather than reasoning about it:

  1. the real run-length distribution over every code in every benchmark
  2. what RLE would actually COST in bits, under three honest encodings,
     compared against the 96 bits it replaces
  3. whether there is any exploitable structure at all: per-position bit
     balance, and correlation between neighbouring bits

The trap the decimal notation hides: "51302120" looks like 8 symbols against
12 bits, but those symbols are not bits.  A run needs a length AND a value,
and the length needs enough bits to cover the longest run.  The comparison
must be bits against bits.
"""
import glob
import json
import os
import pickle
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

DIM = 96


def runs_of(row):
    """run lengths of a boolean row, in order."""
    idx = np.flatnonzero(np.diff(row))
    return np.diff(np.concatenate(([-1], idx, [len(row) - 1])))


def rle_costs(bits):
    """bits: n x 96 bool.  Returns mean cost per code under three encodings."""
    n = bits.shape[0]
    tot_fixed = tot_elias = 0
    nruns = Counter()
    lens = Counter()
    for r in bits:
        rl = runs_of(r)
        nruns[len(rl)] += 1
        for L in rl:
            lens[int(L)] += 1
        # (a) fixed 7-bit length fields, 1 bit for the first value
        tot_fixed += 1 + 7 * len(rl)
        # (b) Elias-gamma lengths, 1 bit for the first value
        tot_elias += 1 + sum(2 * int(L).bit_length() - 1 for L in rl)
    return {
        "mean_runs_per_code": float(
            sum(k * v for k, v in nruns.items()) / n),
        "mean_run_length": float(
            sum(k * v for k, v in lens.items()) / sum(lens.values())),
        "max_run_length": int(max(lens)),
        "rle_fixed7_bits": tot_fixed / n,
        "rle_elias_bits": tot_elias / n,
        "run_length_histogram": {str(k): lens[k] for k in sorted(lens)[:12]},
    }


def structure(bits):
    """Is there anything to exploit: bit balance and neighbour correlation."""
    p = bits.mean(axis=0)                       # P(bit=1) per position
    a = bits[:, :-1].astype(np.int8) * 2 - 1
    b = bits[:, 1:].astype(np.int8) * 2 - 1
    corr = float((a * b).mean())                # +1 = always equal, 0 = none
    return {"bit_balance_min": float(p.min()),
            "bit_balance_max": float(p.max()),
            "bit_balance_mean": float(p.mean()),
            "neighbour_correlation": corr}


def collect(name):
    out = []
    if name == "lme":
        for f in sorted(glob.glob(H.LME_GLOB)):
            out.append(np.asarray(pickle.loads(open(f, "rb").read())["C"],
                                  float) >= 0)
    elif name == "realtalk":
        for f in sorted(glob.glob(H.RT_GLOB)):
            out.append(np.asarray(pickle.loads(open(f, "rb").read())["C"],
                                  float) >= 0)
    elif name == "locomo":
        g = os.path.join(H.SRC, "regen", "locomo", "locomo_*.pkl")
        for f in sorted(glob.glob(g)):
            out.append(np.asarray(pickle.load(open(f, "rb"))["C"], float) >= 0)
    elif name == "perltqa":
        arch = pickle.load(open(H.ARCH_PKL, "rb"))
        for ch in sorted(arch):
            out.append(np.asarray(arch[ch]["C"], float) >= 0)
    return np.vstack(out)


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "question": "does run-length encoding shrink the 96-bit code",
           "baseline_bits": DIM,
           "note": ("a run costs a length AND a value; decimal digits are not "
                    "bits, so the comparison is made in bits"),
           "benchmarks": {}}
    for name in ("lme", "perltqa", "realtalk", "locomo"):
        bits = collect(name)
        r = rle_costs(bits)
        r.update(structure(bits))
        r["n_codes"] = int(bits.shape[0])
        r["best_rle_bits"] = min(r["rle_fixed7_bits"], r["rle_elias_bits"])
        r["ratio_vs_96"] = r["best_rle_bits"] / DIM
        res["benchmarks"][name] = r
        print(f"{name:9s} n={r['n_codes']:6d}  "
              f"ortalama kosu uzunlugu {r['mean_run_length']:.2f}  "
              f"kosu sayisi {r['mean_runs_per_code']:.1f}  "
              f"RLE {r['best_rle_bits']:6.1f} bit  "
              f"({r['ratio_vs_96']*100:5.1f}% of 96)  "
              f"komsu korelasyon {r['neighbour_correlation']:+.4f}",
              flush=True)

    with open(os.path.join(HERE, "RLE.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote RLE.json")


if __name__ == "__main__":
    main()
