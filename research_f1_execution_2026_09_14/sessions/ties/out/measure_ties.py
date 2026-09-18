# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit): SIGN96 kod geometrisinin
TANIMLAYICI bag-cozunurluk olcumu. Dondurulmus uretim yapitinin geri kazanimi DEGILDIR.

SINIR (Task4F1 muhur): altin/etiket (gold/evidence) acilmaz, kullanilmaz; geri-cagirma
(recall)/dogruluk hesaplanmaz; hicbir getirimin DOGRU olup olmadigi degerlendirilmez;
karsilastirma (benchmark) calistirilmaz. Tum iddialar COZUNURLUK KAPASITESI
(cozunurluk geometrisi) hakkindadir: "Hamming sinirinda kac aday bagli", "surekli
sorgu kac bagi cozer". "Dogru cozer" iddiasi YOKTUR ve burada olculemez.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

LABELS = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
REFIT_NOTICE = (
    "BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit): bu cikti, dondurulmus "
    "uretim yapitinin geri kazanimi DEGILDIR; gercek derlem uzerinde temsil "
    "hattinin yeniden uyarlanmasindan okunan TANIMLAYICI bag-geometrisi "
    "istatistikleridir. Hicbir retrieval/recall/dogruluk/gold/benchmark sonucu "
    "hesaplanmamistir; bag cozumlemek dogru cozumlemek demek DEGILDIR."
)
BOUNDARY = (
    "Mühürlü Task4F1: gold/evidence etiketleri acilmadi ve kullanilmadi; recall/"
    "dogruluk hesaplanmadi; getirimin dogrulugu degerlendirilmedi; benchmark "
    "calistirilmadi. Tum olcumler kod GEOMETRISI (cozunurluk kapasitesi) hakkindadir."
)
SPECTRUM_MODULE_PATH = "/home/mdp/muse-work/spectrum/out/PACKAGE/measure_spectrum.py"
SENT = 999  # Hamming matrisinde leave-one-out disi-birakma nobetcisi (Hamming <= 96).
CHUNK = 256


def load_spectrum_module(path):
    spec = importlib.util.spec_from_file_location("measure_spectrum_gated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_labeled_json(path, payload):
    head = (
        '{"_labels": ' + json.dumps(LABELS, ensure_ascii=False)
        + ",\n \"_refit_notice\": " + json.dumps(REFIT_NOTICE, ensure_ascii=False)
    )
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    assert body.startswith("{")
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + ",\n" + body[1:] + "\n")


def hamming_loo(D, chunk=CHUNK):
    """Leave-one-out Hamming olcutleri. D: (N,96) bool. Donus: sozluk + H (int16)."""
    D = np.ascontiguousarray(D, dtype=bool)
    n = D.shape[0]
    H = np.empty((n, n), dtype=np.int16)
    min_p = np.empty(n, dtype=np.int64)
    d3 = np.empty(n, dtype=np.int64)
    bc = np.empty(n, dtype=np.int64)
    dist20 = np.empty(n, dtype=np.int64)
    sum_ = np.zeros(n, dtype=np.float64)
    sumsq = np.zeros(n, dtype=np.float64)
    max_p = np.empty(n, dtype=np.int64)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        Hb = np.count_nonzero(D[s:e, None, :] != D[None, :, :], axis=2).astype(np.int64)
        Hb[np.arange(e - s), np.arange(s, e)] = SENT
        H[s:e] = Hb.astype(np.int16)
        sum_[s:e] = Hb.sum(axis=1) - SENT
        sumsq[s:e] = (Hb.astype(np.float64) ** 2).sum(axis=1) - float(SENT) ** 2
        min_p[s:e] = Hb.min(axis=1)
        Hs = np.sort(Hb, axis=1)
        max_p[s:e] = Hs[:, -2]  # En buyuk SENT nobetcisidir; gercek maks bir oncekidir.
        d3[s:e] = Hs[:, 2]
        bc[s:e] = (Hb == d3[s:e, None]).sum(axis=1)
        k = min(20, n - 1)
        for i, r in enumerate(Hs):
            dist20[s + i] = len(np.unique(r[:k]))
    denom = float(n - 1)
    mean_p = sum_ / denom
    var_p = np.maximum((sumsq - sum_ ** 2 / denom) / denom, 0.0)
    sd_p = np.sqrt(var_p)
    tot = float(sum_.sum())
    tnp = float(n * (n - 1))
    pooled_var = max((float(sumsq.sum()) - tot ** 2 / tnp) / tnp, 0.0)
    return {
        "H": H,
        "mean_p": mean_p, "sd_p": sd_p, "min_p": min_p, "max_p": max_p,
        "d3": d3, "bc": bc, "dist20": dist20,
        "pooled": {
            "mean": float(tot / tnp), "sd": float(np.sqrt(pooled_var)),
            "min": int(min_p.min()), "max": int(max_p.max()),
            "n_pairs": int(tnp),
        },
    }


def boundary_summary(bc):
    bc = np.asarray(bc, dtype=np.int64)
    return {
        "median": float(np.median(bc)),
        "p90": float(np.percentile(bc, 90)),
        "max": int(bc.max()),
        "mean": float(bc.mean()),
        "frac_gt1": float(np.mean(bc > 1)),
        "frac_gt3": float(np.mean(bc > 3)),
        "frac_gt10": float(np.mean(bc > 10)),
        "n_probes": int(bc.size),
    }


def qsummary(x):
    x = np.asarray(x, dtype=np.float64)
    return {
        "mean": float(x.mean()), "median": float(np.median(x)),
        "min": float(x.min()), "max": float(x.max()),
    }


def continuous_analysis(C, H, ms=(10, 50, 200)):
    """Surekli-sorgu cozunurlugu: S = C @ B.T, B = +-1 kodlar. Tum adaylar ayni arsivden."""
    n = C.shape[0]
    B = np.where(C >= 0, 1.0, -1.0)
    S = C.astype(np.float64) @ B.T
    S[np.arange(n), np.arange(n)] = -np.inf
    Hs = np.sort(H.astype(np.int64), axis=1)
    d3 = Hs[:, 2]
    t_list, u_list = [], []
    remaining_pairs = 0
    cont_d3_tied = 0
    contain = {m: [] for m in ms}
    full3 = {m: [] for m in ms}
    for p in range(n):
        T = np.flatnonzero(H[p].astype(np.int64) == d3[p])
        t = int(T.size)
        sc = S[p, T]
        u = int(len(np.unique(sc)))
        t_list.append(t)
        u_list.append(u)
        _, cnt = np.unique(sc, return_counts=True)
        remaining_pairs += int(np.sum(cnt * (cnt - 1) // 2))
        s_sorted = np.sort(S[p])[::-1]
        if np.sum(S[p] == s_sorted[2]) > 1:
            cont_d3_tied += 1
        top3 = set(np.argsort(-S[p], kind="stable")[:3].tolist())
        for m in ms:
            short = set(np.argsort(H[p].astype(np.int64), kind="stable")[:m].tolist())
            hit = len(top3 & short)
            contain[m].append(hit / 3.0)
            full3[m].append(1.0 if hit == 3 else 0.0)
    t_arr = np.array(t_list, dtype=np.int64)
    u_arr = np.array(u_list, dtype=np.int64)
    tied = t_arr > 1
    return {
        "n_probes": n,
        "n_tied_probes": int(tied.sum()),
        "full_resolve_frac": float(np.mean(u_arr[tied] == t_arr[tied])) if tied.any() else 1.0,
        "mean_distinct_coverage": float(np.mean(u_arr[tied] / t_arr[tied])) if tied.any() else 1.0,
        "total_tied_slots": int(t_arr[tied].sum()),
        "total_distinct_scores": int(u_arr[tied].sum()),
        "total_remaining_slots": int((t_arr[tied] - u_arr[tied]).sum()),
        "probes_with_remaining": int(np.sum(u_arr[tied] < t_arr[tied])),
        "remaining_pairs": int(remaining_pairs),
        "continuous_d3_boundary_tie_frac": float(cont_d3_tied / n),
        "containment": {
            f"M{m}": {"mean": float(np.mean(contain[m])), "frac_full_3of3": float(np.mean(full3[m]))}
            for m in ms
        },
    }


def main():
    ap = argparse.ArgumentParser(description="SIGN96 bag geometrisi olcumu (re-fit).")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--geometry", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--n-archives", type=int, default=10)
    args = ap.parse_args()
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    sp = load_spectrum_module(SPECTRUM_MODULE_PATH)
    SVD_SEED = int(sp.SVD_SEED)
    NCOMP = int(sp.N_COMPONENTS)
    print(f"Kapili yukleyici yeniden kullaniliyor: {SPECTRUM_MODULE_PATH} "
          f"(SVD_SEED={SVD_SEED}, NCOMP={NCOMP})", flush=True)

    frozen = []
    with open(args.geometry, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            frozen.append(row)
    if not frozen or frozen[0]["question_id"] != "001be529":
        print("GEOMETRI SIRASI BEKLENMEDIK: ilk satir 001be529 degil", file=sys.stderr)
        sys.exit(2)
    targets = frozen[: args.n_archives]
    ad = sp.load_adapter(args.adapter)

    print(f"Derlem yukleniyor: {args.corpus}", flush=True)
    with open(args.corpus, encoding="utf-8") as f:
        data = json.load(f)
    by_id = {str(x["question_id"]): x for x in data}

    # --- ADIM 1: KAPI ---
    gate_rows = []
    fitted = []
    for row in targets:
        qid = row["question_id"]
        texts = sp.archive_texts_only(by_id[qid])
        wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(texts)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        exp = {"N_archive": int(row["N_archive"]), "word_columns": int(row["word_columns"]),
               "char_columns": int(row["char_columns"]), "combined_columns": int(row["combined_columns"])}
        got = {"N_archive": int(Z.shape[0]), "word_columns": int(Xw.shape[1]),
               "char_columns": int(Xc.shape[1]), "combined_columns": int(Z.shape[1])}
        ok = all(got[k] == exp[k] for k in exp)
        gate_rows.append({"question_id": qid, "expected": exp, "measured": got, "pass": bool(ok)})
        print(f"KAPI {qid}: beklenen={exp} olculen={got} -> {'GECTI' if ok else 'KALDI'}", flush=True)
        s96 = TruncatedSVD(n_components=NCOMP, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        D = (C >= 0)
        fitted.append({"qid": qid, "N": int(Z.shape[0]), "C": C, "D": D})

    gate_pass = all(r["pass"] for r in gate_rows)
    write_labeled_json(os.path.join(outdir, "GATE.json"),
                       {"gate": "ozellik geometrisi birebir eslesme",
                        "boundary": BOUNDARY, "overall_pass": bool(gate_pass), "rows": gate_rows})
    if not gate_pass:
        print("KAPI KALDI: olcum raporlanmayacak. Ayrinti icin GATE.json.", file=sys.stderr)
        sys.exit(3)
    print("KAPI GECTI: tum geometri degerleri birebir eslesti.", flush=True)

    # --- ADIM 2 + ADIM 4: arsiv ici LOO ---
    per_archive = []
    all_bc = []
    for fa in fitted:
        loo = hamming_loo(fa["D"])
        cont = continuous_analysis(fa["C"], loo["H"])
        fa["H"] = loo["H"]
        all_bc.append(loo["bc"])
        per_archive.append({
            "question_id": fa["qid"], "N_archive": fa["N"],
            "hamming": {
                "pooled": loo["pooled"],
                "d3_3rd_nearest": qsummary(loo["d3"]),
                "per_probe_mean": qsummary(loo["mean_p"]),
                "per_probe_sd": qsummary(loo["sd_p"]),
                "per_probe_min": qsummary(loo["min_p"]),
                "distinct_among_20nearest": qsummary(loo["dist20"]),
                "boundary": boundary_summary(loo["bc"]),
            },
            "continuous": cont,
        })
        b = per_archive[-1]["hamming"]["boundary"]
        print(f"OLCUM {fa['qid']} N={fa['N']}: sinir-tie medyan={b['median']:.0f} "
              f"p90={b['p90']:.1f} maks={b['max']} frac>1={b['frac_gt1']:.3f} "
              f"cozum-tam={cont['full_resolve_frac']:.4f}", flush=True)
    all_bc = np.concatenate(all_bc)
    aggregate = {"n_archives": len(per_archive),
                 "boundary_pooled_probes": boundary_summary(all_bc)}

    # --- ADIM 3a: arsiv ici alt-ornekleme (satir alt-kumesi; uyum tam-arşiv uyumudur) ---
    sub_levels = [50, 100, 200, 400]
    subsample = {}
    for ns in sub_levels:
        per_a, pool_bc = [], []
        for ai, fa in enumerate(fitted):
            n = fa["N"]
            if ns >= n:
                bc = hamming_loo(fa["D"])["bc"]
                used = n
            else:
                rng = np.random.default_rng(9000 + ai)
                idx = rng.choice(n, ns, replace=False)
                bc = hamming_loo(fa["D"][idx])["bc"]
                used = ns
            pool_bc.append(bc)
            s = boundary_summary(bc)
            s["N_used"] = used
            per_a.append({"question_id": fa["qid"], "N_used": used, "boundary": s})
        pool = boundary_summary(np.concatenate(pool_bc))
        subsample[f"N{ns}"] = {"N_target": ns, "pooled": pool, "per_archive": per_a}
        print(f"ALT-ORNEK N={ns}: havuz medyan={pool['median']:.0f} p90={pool['p90']:.1f} "
              f"maks={pool['max']} frac>1={pool['frac_gt1']:.3f}", flush=True)
    subsample["Nfull"] = {"N_target": "full", "pooled": aggregate["boundary_pooled_probes"]}

    # --- ADIM 3b: arsivler-arasi havuzlama (farkli koordinat sistemleri!) ---
    pool_caveat = (
        "DIKKAT: her arsiv ayri uyarlandi; havuzlanmis vektorler ortak bir koordinat "
        "sistemi paylasmaz. Havuz figuru, bu genislik ve yogunluktaki bir kodun bag "
        "davranisina olcek siniri verir; TEK bir ~5000 turluk arsivin olcumu DEGILDIR."
    )
    pooling_steps = []
    for k in [2, 4, 6, 8, 10]:
        kk = min(k, len(fitted))
        Dp = np.vstack([fa["D"] for fa in fitted[:kk]])
        loo = hamming_loo(Dp)
        pooling_steps.append({
            "k_archives": kk, "N_pooled": int(Dp.shape[0]),
            "pooled_hamming": loo["pooled"],
            "d3_3rd_nearest": qsummary(loo["d3"]),
            "distinct_among_20nearest": qsummary(loo["dist20"]),
            "boundary": boundary_summary(loo["bc"]),
        })
        b = pooling_steps[-1]["boundary"]
        print(f"HAVUZ k={kk} N={Dp.shape[0]}: medyan={b['median']:.0f} p90={b['p90']:.1f} "
              f"maks={b['max']} frac>1={b['frac_gt1']:.3f}", flush=True)

    hist, _ = np.histogram(all_bc, bins=list(range(1, 22)) + [10 ** 9])
    payload = {
        "boundary": BOUNDARY,
        "svd_seed": SVD_SEED, "n_components": NCOMP,
        "probe_turu": "arsivin KENDI merkezlenmis vektorleri (leave-one-out); "
                       "gold-baglantili sorgu yok",
        "aggregate_fullN": aggregate,
        "bc_histogram_fullN": {"bins_1_to_20": [int(x) for x in hist[:-1]],
                               "gt_20": int(hist[-1])},
        "per_archive": per_archive,
        "subsample": subsample,
        "pooling": {"caveat": pool_caveat, "steps": pooling_steps},
        "not_checked": [
            "Bagli adaylarin dogru cevabi icerme sikligi (gold gerekir; bakilmadi).",
            "Surekli skorun bagi DOGRU cozme orani (gold gerekir; bakilmadi).",
            "Tek bir gercek ~5000 turluk arsivde bag yapisi (derlemde yok; olculmedi).",
            "Farkli tohum/uyarlamalarda sonuclarin kararliligi (tek uyum; bakilmadi).",
        ],
    }
    write_labeled_json(os.path.join(outdir, "TIES.json"), payload)
    print("YAZILDI: GATE.json, TIES.json", flush=True)


if __name__ == "__main__":
    main()
