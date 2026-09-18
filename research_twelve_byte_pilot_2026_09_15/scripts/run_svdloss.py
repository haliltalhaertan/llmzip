#!/usr/bin/env python3
"""Does the SVD actually discard rare terms? A test with no queries in it.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_rareterm.py` split queries by the rarest term shared between question and
gold, and found the 12-byte code wins on common-hinge queries and loses badly
on rare-hinge ones, on three benchmarks.  That was read as evidence that the
SVD discards rare terms.

**There is a circularity in that reading and it was not resolved.** BM25's
score IS the IDF-weighted overlap between question and document, so "the gold
shares a rare term with the question" and "BM25 ranks the gold highly" are
close to the same statement.  A gold-free control was attempted -- bucket by
the question's own rarest in-archive term -- and it was uninformative: 1,486 of
1,535 LoCoMo queries landed in one bucket, so it does not discriminate.

This script tests the mechanism claim DIRECTLY, in the representation, with no
query, no gold and no BM25 anywhere in it:

    for every term (column) of Z, how much of that column survives the rank-96
    truncation?

    survival_j = ||Zhat[:, j]||^2 / ||Z[:, j]||^2

where Zhat is the rank-96 reconstruction the pipeline's own SVD produces. If
the mechanism is right, survival must fall as document frequency falls. If
survival is flat in df, the SVD is NOT preferentially discarding rare terms
and the explanation in section 27 of the handoff is wrong, whatever the query
split showed.

Reported as mean survival by df bucket, plus the Spearman correlation between
df and survival, per archive and pooled.  Word-channel columns only: the
character n-gram block has no meaningful df interpretation and the LSA32 block
is already a projection.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_bottleneck as BN  # noqa: E402

SVD_SEED = 5204
EDGES = [1, 2, 3, 5, 10, 20, 50, 10**9]


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / d) if d > 0 else float("nan")


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    adapter = BN.load_adapter()
    files = sorted(glob.glob(BN.ITEMS))[:k]
    per_arch, all_df, all_surv = [], [], []

    for f in files:
        item = json.loads(open(f, encoding="utf-8").read())
        memories, _, issues = adapter.build_archive(item)
        if issues:
            continue
        texts = adapter.fit_input_payload(memories)
        wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(texts)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        n = Z.shape[0]
        sv = TruncatedSVD(n_components=96, random_state=SVD_SEED)
        U = sv.fit_transform(Z)                     # n x 96  (= U S)
        V = sv.components_                          # 96 x F
        # word-channel columns only
        lo = Xl.shape[1]
        hi = lo + Xw.shape[1]
        Zw = Z[:, lo:hi]
        Zhat_w = U @ V[:, lo:hi]                    # n x F_word
        num = (Zhat_w * Zhat_w).sum(axis=0)
        den = np.asarray(Zw.multiply(Zw).sum(axis=0)).ravel()
        keep = den > 1e-12
        surv = num[keep] / den[keep]
        df = np.asarray((Xw > 0).sum(axis=0)).ravel()[keep].astype(float)
        rho = spearman(df, surv)
        per_arch.append({"archive": os.path.basename(f)[:-5], "N": int(n),
                         "n_word_terms": int(keep.sum()),
                         "spearman_df_vs_survival": rho})
        all_df.append(df)
        all_surv.append(surv)
        print(f"  {os.path.basename(f)[:-5]}  N={n:4d}  "
              f"terim={int(keep.sum()):6d}  rho={rho:+.3f}", flush=True)

    df = np.concatenate(all_df)
    surv = np.concatenate(all_surv)
    buckets = []
    for i in range(len(EDGES) - 1):
        m = (df >= EDGES[i]) & (df < EDGES[i + 1])
        if m.sum() < 10:
            continue
        buckets.append({"df_from": EDGES[i], "df_to": EDGES[i + 1],
                        "n_terms": int(m.sum()),
                        "mean_survival": float(surv[m].mean()),
                        "median_survival": float(np.median(surv[m]))})

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "what": "fraction of each word-channel column's energy surviving "
                   "the rank-96 truncation; no query, no gold, no BM25",
           "n_archives": len(per_arch),
           "spearman_df_vs_survival_pooled": spearman(df, surv),
           "spearman_per_archive_mean": float(np.mean(
               [r["spearman_df_vs_survival"] for r in per_arch])),
           "by_df_bucket": buckets, "per_archive": per_arch}
    with open(os.path.join(HERE, "SVDLOSS.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"\n=== {len(per_arch)} LongMemEval arsivi, "
          f"{len(df):,} kelime sutunu ===")
    print(f"  {'df araligi':>14s}{'terim':>9s}{'ortalama hayatta kalma':>24s}"
          f"{'medyan':>10s}")
    for b in buckets:
        rng = (f"{b['df_from']}" if b["df_to"] > 10**8
               else f"{b['df_from']}-{b['df_to']-1}")
        print(f"  {rng:>14s}{b['n_terms']:>9d}"
              f"{b['mean_survival']:>24.4f}{b['median_survival']:>10.4f}")
    print(f"\n  Spearman(df, hayatta kalma) havuzlanmis : "
          f"{out['spearman_df_vs_survival_pooled']:+.4f}")
    print(f"  arsiv basina ortalama                   : "
          f"{out['spearman_per_archive_mean']:+.4f}")
    print("\nwrote SVDLOSS.json")


if __name__ == "__main__":
    main()
