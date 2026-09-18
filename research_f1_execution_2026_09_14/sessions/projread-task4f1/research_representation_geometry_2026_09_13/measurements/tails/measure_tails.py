# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit), dondurulmus yapit DEGIL.

Gercek LongMemEval derlemi uzerinde temsil hatti yeniden uyarlanir ve
SADECE temsilin GEOMETRISI olculur (kuyruk istatistikleri, hubness,
puanlama fonksiyonlari arasi siralama uyumu).

SINIR (Task4F1 muhrune saygi): altin/evidence etiketleri acilmaz,
recall/dogruluk hesaplanmaz, hicbir siralamanin DOGRU olup olmadugu
degerlendirilmez, benchmark calistirilmaz. Puanlama fonksiyonlari
yalnizca BIRBIRIYLE karsilastirilir; gercekle (truth) karsilastirma
yoktur. Soru metni ve etiket alanlari hic okunmaz.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
from scipy import sparse
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

LABELS = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
REFIT_NOTICE = (
    "BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit): bu cikti dondurulmus "
    "uretim yapitinin geri kazanimi DEGILDIR; gercek derlem uzerinde temsil "
    "hattinin yeniden uyarlanmasindan okunan TANIMLAYICI GEOMETRI "
    "istatistikleridir. Etiket acilmamis, recall/dogruluk hesaplanmamis, "
    "siralama dogrulugu degerlendirilmemis, benchmark calistirilmamistir."
)
SVD_SEED = 5204  # Dondurulmus prob ile ayni (S96 blogu).
N_COMPONENTS = 96
CLIP_MAIN = 1.5
CLIP_SWEEP = [0.5, 1.0, 1.5, 2.0, 3.0]
TIEBREAK_BASE_SEED = 77000
KS = [3, 10]


def load_adapter(path):
    spec = importlib.util.spec_from_file_location("v52_adapter_tails", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def archive_texts_only(item):
    """YALNIZCA arsiv metinleri; etiket/soru alanlari OKUNMAZ."""
    sids = item["haystack_session_ids"]
    dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    texts = []
    for si, (sid, date, sess) in enumerate(zip(sids, dates, sessions)):
        if not isinstance(sess, list):
            continue
        for ti, turn in enumerate(sess):
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")
            content = turn.get("content")
            if not isinstance(content, str):
                content = "" if content is None else str(content)
            texts.append(f"[{date}] {role}: {content}")
    return texts


def skew_kurt_1d(x):
    """Populasyon momentleriyle carpiklik ve arti basiklik (excess kurtosis).

    m2/m3/m4 paydasinda N kullanilir (ddof=0); saf tanimlayici istatistik.
    Donus: (skew, excess_kurt).
    """
    a = np.asarray(x, dtype=np.float64).ravel()
    m = a.mean()
    d = a - m
    m2 = float(np.mean(d ** 2))
    if not np.isfinite(m2) or m2 <= 0:
        return float("nan"), float("nan")
    m3 = float(np.mean(d ** 3))
    m4 = float(np.mean(d ** 4))
    return m3 / (m2 ** 1.5), m4 / (m2 ** 2) - 3.0


def summarize(values):
    a = np.asarray(values, dtype=np.float64)
    return {
        "median": float(np.median(a)),
        "min": float(np.min(a)),
        "max": float(np.max(a)),
        "mean": float(np.mean(a)),
    }


def write_labeled_json(path, payload):
    head = (
        '{"_labels": ' + json.dumps(LABELS, ensure_ascii=False)
        + ",\n \"_refit_notice\": " + json.dumps(REFIT_NOTICE, ensure_ascii=False)
    )
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    assert body.startswith("{")
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + ",\n" + body[1:] + "\n")


def cosine_score_matrix(M):
    """Kosinüs benzerlik matrisi (yuksek=yakin); kosegen -inf (LOO)."""
    M = np.asarray(M, dtype=np.float64)
    nrm = np.linalg.norm(M, axis=1)
    nrm = np.where(nrm > 0, nrm, np.nan)
    S = (M @ M.T) / (nrm[:, None] * nrm[None, :])
    S[~np.isfinite(S)] = 0.0
    np.fill_diagonal(S, -np.inf)
    return S


def hamming_score_matrix(D):
    """Isaret kodu icin -Hamming uzakligi (yuksek=yakin); kosegen -inf."""
    B = np.asarray(D, dtype=np.int16)
    ones = B.sum(axis=1).astype(np.int32)
    H = ones[:, None] + ones[None, :] - 2 * (B @ B.T)
    S = -H.astype(np.float64)
    np.fill_diagonal(S, -np.inf)
    return S


def topk_orders(score_mat, priority):
    """Her satir icin (skor azalan, oncelik artan) tam siralama."""
    n = score_mat.shape[0]
    orders = np.empty((n, n), dtype=np.int32)
    for i in range(n):
        orders[i] = np.lexsort((priority, -score_mat[i]))
    return orders


def hubness_stats(topk, k, n):
    """N_k dagilimi: carpiklik, max, ilk %1'in slot payi."""
    Nk = np.bincount(np.asarray(topk[:, :k]).ravel(), minlength=n).astype(np.float64)
    sk, _ = skew_kurt_1d(Nk)
    t = max(1, int(math.ceil(0.01 * n)))
    share = float(np.sort(Nk)[::-1][:t].sum() / (n * k))
    return {
        "k": int(k),
        "Nk_skew": float(sk),
        "Nk_max": int(Nk.max()),
        "Nk_mean": float(Nk.mean()),
        "Nk_std": float(Nk.std()),
        "top1pct_share": share,
        "top1pct_count": int(t),
        "Nk": [int(v) for v in Nk],
    }


def overlaps_and_rho(order_a, order_b, score_a, score_b):
    """Ortalama overlap@3/@10 ve prob basina tam-skor Spearman rho ortalamasi."""
    n = order_a.shape[0]
    ov3, ov10, rhos = [], [], []
    for i in range(n):
        sa3 = set(order_a[i, :3].tolist())
        sb3 = set(order_b[i, :3].tolist())
        ov3.append(len(sa3 & sb3) / 3.0)
        sa10 = set(order_a[i, :10].tolist())
        sb10 = set(order_b[i, :10].tolist())
        ov10.append(len(sa10 & sb10) / 10.0)
        with np.errstate(all="ignore"):
            r = spearmanr(score_a[i], score_b[i]).statistic
        rhos.append(float(r) if r is not None and np.isfinite(r) else float("nan"))
    return {
        "overlap_at_3_mean": float(np.mean(ov3)),
        "overlap_at_10_mean": float(np.mean(ov10)),
        "spearman_rho_mean": float(np.nanmean(rhos)),
        "spearman_rho_median": float(np.nanmedian(rhos)),
        "n_probes": int(n),
    }


def concentration_stats(C):
    """Ic-carpim yogunlasmasi: tum sirali-olmayan ciflerde (i<j).

    t_i = C_a,i*C_b,i; S = sum t_i.
    f1 = max|t|/|S|, f3 = top3|t| toplami/|S| (mekanizma hikayesinin
    ihtiyac duydugu nicelik; |S|~0 iken >1/sonsuz olabilir).
    g1/g3 = ayni paylarin sum|t|'ye orani (yardimci, [0,1] araliginda).
    """
    C = np.asarray(C, dtype=np.float64)
    n, d = C.shape
    f1_all, f3_all, g1_all, g3_all = [], [], [], []
    for i in range(n):
        T = C[i] * C[i + 1:]
        if T.shape[0] == 0:
            continue
        S = T.sum(axis=1)
        A = np.abs(T)
        part = np.partition(A, d - 3, axis=1)
        top1 = part[:, -1]
        top3 = part[:, -3:].sum(axis=1)
        denom = np.abs(S)
        sabs = A.sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            f1 = np.where(denom > 0, top1 / denom, np.inf)
            f3 = np.where(denom > 0, top3 / denom, np.inf)
            g1 = np.where(sabs > 0, top1 / sabs, np.nan)
            g3 = np.where(sabs > 0, top3 / sabs, np.nan)
        # 0/0 (tam sifir cifti) pratikte gorulmez; gorulurse nan birakilir.
        f1 = np.where((top1 == 0) & (denom == 0), np.nan, f1)
        f3 = np.where((top3 == 0) & (denom == 0), np.nan, f3)
        f1_all.append(f1)
        f3_all.append(f3)
        g1_all.append(g1)
        g3_all.append(g3)
    f1_all = np.concatenate(f1_all) if f1_all else np.array([])
    f3_all = np.concatenate(f3_all) if f3_all else np.array([])
    g1_all = np.concatenate(g1_all) if g1_all else np.array([])
    g3_all = np.concatenate(g3_all) if g3_all else np.array([])

    def dist(a):
        fin = a[np.isfinite(a)]
        return {
            "median": float(np.median(fin)) if fin.size else float("nan"),
            "p90": float(np.quantile(fin, 0.90)) if fin.size else float("nan"),
            "p99": float(np.quantile(fin, 0.99)) if fin.size else float("nan"),
            "max_finite": float(fin.max()) if fin.size else float("nan"),
            "frac_gt_0_5": float(np.mean(fin > 0.5)) if fin.size else float("nan"),
            "frac_gt_1_0": float(np.mean(fin > 1.0)) if fin.size else float("nan"),
            "n_inf": int(np.sum(np.isposinf(a))),
            "n_pairs": int(a.size),
        }

    return {"f1_vs_abs_sum": dist(f1_all), "f3_vs_abs_sum": dist(f3_all),
            "g1_vs_sum_abs_aux": dist(g1_all), "g3_vs_sum_abs_aux": dist(g3_all)}


def main():
    ap = argparse.ArgumentParser(description="Kuyruk/hubness geometri olcumu (re-fit).")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--geometry", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--n-archives", type=int, default=15)
    args = ap.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    frozen = []
    with open(args.geometry, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            frozen.append(row)
    if not frozen or frozen[0]["question_id"] != "001be529":
        print("GEOMETRI SIRASI BEKLENMEDIK: ilk satir 001be529 degil", file=sys.stderr)
        sys.exit(2)
    targets = frozen[: args.n_archives]

    ad = load_adapter(args.adapter)

    print(f"Derlem yukleniyor: {args.corpus}", flush=True)
    with open(args.corpus, encoding="utf-8") as f:
        data = json.load(f)
    by_id = {str(x["question_id"]): x for x in data}

    # --- ADIM 0: KAPI. Tum secili arsivlerde geometri birebir tutmalidir. ---
    gate_rows = []
    fitted = []
    for row in targets:
        qid = row["question_id"]
        item = by_id[qid]
        texts = archive_texts_only(item)
        wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(texts)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        exp = {
            "N_archive": int(row["N_archive"]),
            "word_columns": int(row["word_columns"]),
            "char_columns": int(row["char_columns"]),
            "combined_columns": int(row["combined_columns"]),
        }
        got = {
            "N_archive": int(Z.shape[0]),
            "word_columns": int(Xw.shape[1]),
            "char_columns": int(Xc.shape[1]),
            "combined_columns": int(Z.shape[1]),
        }
        ok = all(got[k] == exp[k] for k in exp)
        gate_rows.append({"question_id": qid, "expected": exp, "measured": got, "pass": bool(ok)})
        print(f"KAPI {qid}: beklenen={exp} olculen={got} -> {'GECTI' if ok else 'KALDI'}", flush=True)
        fitted.append((qid, Z))

    gate_pass = all(r["pass"] for r in gate_rows)
    write_labeled_json(
        os.path.join(outdir, "GATE.json"),
        {"gate": "ozellik geometrisi birebir eslesme", "overall_pass": bool(gate_pass),
         "rows": gate_rows},
    )
    if not gate_pass:
        print("KAPI KALDI: olcum raporlanmayacak. Ayrinti icin GATE.json.", file=sys.stderr)
        sys.exit(3)
    print("KAPI GECTI: tum geometri degerleri birebir eslesti.", flush=True)

    # --- ADIM 1-3: Kuyruk, hubness, siralama uyumu (saf geometri). ---
    per_archive = []
    for ordinal, (qid, Z) in enumerate(fitted):
        s96 = TruncatedSVD(n_components=N_COMPONENTS, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        n, d = C.shape
        sigma = C.std(axis=0, ddof=0)

        # ADIM 1: koordinat basina ve havuzlanmis kuyruk istatistikleri.
        per_sk, per_ku = [], []
        for j in range(d):
            sk, ku = skew_kurt_1d(C[:, j])
            per_sk.append(sk)
            per_ku.append(ku)
        per_sk = np.array(per_sk)
        per_ku = np.array(per_ku)
        pool_sk, pool_ku = skew_kurt_1d(C.ravel())
        occ = np.mean(C >= 0, axis=0)
        conc = concentration_stats(C)

        # ADIM 2-3: uc puanlama fonksiyonu, LOO problar, sabit bag-kirma.
        # Bag-kirma: arsiv-sirali sabit tohumlu rastgele oncelik (etiket disi,
        # deterministik; indeks-yanliligi yaratmaz). Tum skorlar icin ayni vektor.
        priority = np.random.default_rng(TIEBREAK_BASE_SEED + ordinal).random(n)
        S_raw = cosine_score_matrix(C)
        Cc_main = np.clip(C, -CLIP_MAIN * sigma, CLIP_MAIN * sigma)
        S_clip = cosine_score_matrix(Cc_main)
        S_sign = hamming_score_matrix(C >= 0)
        O_raw = topk_orders(S_raw, priority)
        O_clip = topk_orders(S_clip, priority)
        O_sign = topk_orders(S_sign, priority)

        hub = {}
        for name, O in (("raw_cosine", O_raw), ("clipped_cosine_1.5", O_clip),
                        ("sign_hamming", O_sign)):
            hub[name] = {f"k{k}": hubness_stats(O, k, n) for k in KS}

        agree = {
            "raw_vs_clipped1.5": overlaps_and_rho(O_raw, O_clip, S_raw, S_clip),
            "raw_vs_sign": overlaps_and_rho(O_raw, O_sign, S_raw, S_sign),
            "clipped1.5_vs_sign": overlaps_and_rho(O_clip, O_sign, S_clip, S_sign),
        }

        sweep = {}
        for t in CLIP_SWEEP:
            Cc = np.clip(C, -t * sigma, t * sigma)
            S_t = cosine_score_matrix(Cc)
            O_t = topk_orders(S_t, priority)
            sweep[str(t)] = overlaps_and_rho(O_t, O_sign, S_t, S_sign)

        per_archive.append({
            "question_id": qid,
            "N_archive": int(n),
            "tails": {
                "per_coord_skew": [float(v) for v in per_sk],
                "per_coord_excess_kurt": [float(v) for v in per_ku],
                "per_coord_skew_summary": summarize(per_sk),
                "per_coord_kurt_summary": summarize(per_ku),
                "pooled_skew": float(pool_sk),
                "pooled_excess_kurt": float(pool_ku),
                "sign_balance": {
                    "occ_mean": float(np.mean(occ)),
                    "occ_min": float(np.min(occ)),
                    "occ_max": float(np.max(occ)),
                    "n_outside_045_055": int(np.sum((occ < 0.45) | (occ > 0.55))),
                    "n_outside_030_070": int(np.sum((occ < 0.30) | (occ > 0.70))),
                },
                "concentration": conc,
            },
            "hubness": hub,
            "agreement": agree,
            "clip_sweep_vs_sign": sweep,
        })
        h = hub
        print(
            f"OLCUM {qid} (N={n}): kuyruk med kurt={np.median(per_ku):.3f} "
            f"med skew={np.median(per_sk):.3f} havuz kurt={pool_ku:.3f} "
            f"skew={pool_sk:.3f} | hub k=10 egiklik ham={h['raw_cosine']['k10']['Nk_skew']:.3f} "
            f"kirp={h['clipped_cosine_1.5']['k10']['Nk_skew']:.3f} "
            f"isaret={h['sign_hamming']['k10']['Nk_skew']:.3f} | "
            f"uyum@10 ham-isaret={agree['raw_vs_sign']['overlap_at_10_mean']:.3f} "
            f"kirp-isaret={agree['clipped1.5_vs_sign']['overlap_at_10_mean']:.3f}",
            flush=True,
        )

    # Toplu ozet: arsivler arasi medyan/min/maks.
    def col(fn):
        return [fn(a) for a in per_archive]

    aggregate = {
        "n_archives": len(per_archive),
        "per_coord_kurt_median": summarize(col(lambda a: np.median(a["tails"]["per_coord_excess_kurt"]))),
        "per_coord_skew_median": summarize(col(lambda a: np.median(a["tails"]["per_coord_skew"]))),
        "per_coord_kurt_all": summarize([v for a in per_archive for v in a["tails"]["per_coord_excess_kurt"]]),
        "per_coord_skew_all": summarize([v for a in per_archive for v in a["tails"]["per_coord_skew"]]),
        "pooled_kurt": summarize(col(lambda a: a["tails"]["pooled_excess_kurt"])),
        "pooled_skew": summarize(col(lambda a: a["tails"]["pooled_skew"])),
        "conc_f1_median": summarize(col(lambda a: a["tails"]["concentration"]["f1_vs_abs_sum"]["median"])),
        "conc_f1_p90": summarize(col(lambda a: a["tails"]["concentration"]["f1_vs_abs_sum"]["p90"])),
        "conc_f1_p99": summarize(col(lambda a: a["tails"]["concentration"]["f1_vs_abs_sum"]["p99"])),
        "conc_f3_median": summarize(col(lambda a: a["tails"]["concentration"]["f3_vs_abs_sum"]["median"])),
        "conc_f3_p99": summarize(col(lambda a: a["tails"]["concentration"]["f3_vs_abs_sum"]["p99"])),
        "conc_g1_median_aux": summarize(col(lambda a: a["tails"]["concentration"]["g1_vs_sum_abs_aux"]["median"])),
        "conc_g3_median_aux": summarize(col(lambda a: a["tails"]["concentration"]["g3_vs_sum_abs_aux"]["median"])),
        "n_outside_045_055": summarize(col(lambda a: a["tails"]["sign_balance"]["n_outside_045_055"])),
        "n_outside_030_070": summarize(col(lambda a: a["tails"]["sign_balance"]["n_outside_030_070"])),
    }
    for name in ("raw_cosine", "clipped_cosine_1.5", "sign_hamming"):
        for k in KS:
            aggregate[f"hub_{name}_k{k}_skew"] = summarize(
                col(lambda a, n=name, k=k: a["hubness"][n][f"k{k}"]["Nk_skew"]))
            aggregate[f"hub_{name}_k{k}_max"] = summarize(
                col(lambda a, n=name, k=k: a["hubness"][n][f"k{k}"]["Nk_max"]))
            aggregate[f"hub_{name}_k{k}_top1pct"] = summarize(
                col(lambda a, n=name, k=k: a["hubness"][n][f"k{k}"]["top1pct_share"]))
    for pair in ("raw_vs_clipped1.5", "raw_vs_sign", "clipped1.5_vs_sign"):
        for met in ("overlap_at_3_mean", "overlap_at_10_mean", "spearman_rho_mean"):
            aggregate[f"agree_{pair}_{met.split('_mean')[0]}"] = summarize(
                col(lambda a, p=pair, m=met: a["agreement"][p][m]))
    for t in CLIP_SWEEP:
        for met in ("overlap_at_3_mean", "overlap_at_10_mean", "spearman_rho_mean"):
            aggregate[f"sweep_t{t}_{met.split('_mean')[0]}"] = summarize(
                col(lambda a, t=t, m=met: a["clip_sweep_vs_sign"][str(t)][m]))

    params = {
        "svd_seed": SVD_SEED,
        "n_components": N_COMPONENTS,
        "clip_main": CLIP_MAIN,
        "clip_sweep": CLIP_SWEEP,
        "tiebreak": f"arsiv-sirali sabit tohum (base={TIEBREAK_BASE_SEED}) rastgele oncelik; tum skorlarda ayni vektor",
        "sd_def": "per-coordinate population sd (ddof=0)",
        "moment_def": "populasyon momentleri (paydada N); carpiklik=m3/m2^1.5, arti basiklik=m4/m2^2-3",
        "sweep_peak_rule": "her metrikte arsivler-arasi ortalama uyumun en yuksek oldugu esik",
    }
    write_labeled_json(
        os.path.join(outdir, "TAILS.json"),
        {"params": params, "per_archive": per_archive, "aggregate": aggregate},
    )
    print("YAZILDI: GATE.json, TAILS.json", flush=True)


if __name__ == "__main__":
    main()
