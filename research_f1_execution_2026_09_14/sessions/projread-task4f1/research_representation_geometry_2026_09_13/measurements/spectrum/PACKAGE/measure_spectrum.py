# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Beyan edilmis YENIDEN-UYARLAMA (re-fit): yalnizca temsilin tanimlayici
istatistikleri (tekil degerler ve koordinat basina varyans) okunur.

Bu betik dondurulmus uretim yapitini (frozen artifact) geri kazanmaz; gercek
LongMemEval derlemi uzerinde temsil hattini yeniden uyarlar ve spektrumun
TANIMLAYICI istatistiklerini olcer. Hicbir geri-getirim (retrieval), geri-cagirma
(recall)/dogruluk, altin/etiket (gold/evidence) kullanimi, belge siralama,
karsilastirma (benchmark) ya da sonuc sayisi hesaplanmaz.
"""
from __future__ import annotations

import argparse
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
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

LABELS = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
REFIT_NOTICE = (
    "BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit): bu cikti, dondurulmus "
    "uretim yapitinin geri kazanimi DEGILDIR; gercek derlem uzerinde temsil "
    "hattinin yeniden uyarlanmasindan okunan TANIMLAYICI istatistiklerdir. "
    "Hicbir retrieval/recall/gold/benchmark sonucu hesaplanmamistir."
)
SVD_SEED = 5204  # Dondurulmus probdan aynen: v52_t4c3_coordinate_axis_probe.py, satir 18 (SVD_SEED=5204).
N_COMPONENTS = 96


def load_adapter(path):
    spec = importlib.util.spec_from_file_location("v52_adapter_refit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def archive_texts_only(item):
    """YALNIZCA arsiv metinlerini kurar; etiketlere hic dokunmaz.

    Dondurulmus adapterdaki build_archive+fit_input_payload ile ayni metni uretir:
    memory_text = f"[{date}] {role}: {content}", ayni atlama/zorlama kurallariyla.
    Bu fonksiyon has_answer/answer/gold/question alanlarini OKUMAZ.
    """
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


def loglog_fit(values):
    """ln(v) = alpha - p*ln(i), i=1..n. Donus: (p, r2, n_kullanilan)."""
    v = np.asarray(values, dtype=np.float64)
    mask = v > 0
    v = v[mask]
    idx = np.arange(1, len(values) + 1, dtype=np.float64)[mask]
    x = np.log(idx)
    y = np.log(v)
    n = len(x)
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(-slope), float(r2), int(n)


def summarize(values):
    a = np.asarray(values, dtype=np.float64)
    return {"median": float(np.median(a)), "min": float(np.min(a)), "max": float(np.max(a))}


def write_labeled_json(path, payload):
    """Ilk satirda dort etiketi tasiyan gecerli JSON yazar."""
    head = (
        '{"_labels": ' + json.dumps(LABELS, ensure_ascii=False)
        + ",\n \"_refit_notice\": " + json.dumps(REFIT_NOTICE, ensure_ascii=False)
    )
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    assert body.startswith("{")
    text = head + ",\n" + body[1:] + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    ap = argparse.ArgumentParser(description="Tanimlayici spektrum olcumu (re-fit).")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--geometry", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--n-archives", type=int, default=15)
    args = ap.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # Dondurulmus geometri tablosu: sira korunur (ilk satir 001be529 olmalidir).
    import csv

    frozen = []
    with open(args.geometry, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            frozen.append(row)
    if not frozen or frozen[0]["question_id"] != "001be529":
        print("GEOMETRI SIRASI BEKLENMEDIK: ilk satir 001be529 degil", file=sys.stderr)
        sys.exit(2)
    targets = frozen[: args.n_archives]
    target_ids = [r["question_id"] for r in targets]

    ad = load_adapter(args.adapter)

    print(f"Derlem yukleniyor: {args.corpus}", flush=True)
    with open(args.corpus, encoding="utf-8") as f:
        data = json.load(f)
    by_id = {str(x["question_id"]): x for x in data}

    # --- ADIM 1: KAPI. Tum secili arsivlerde geometri birebir tutmalidir. ---
    gate_rows = []
    fitted = []  # (qid, texts, Xw, Xc, Xl, Z)
    for row in targets:
        qid = row["question_id"]
        item = by_id[qid]
        texts = archive_texts_only(item)  # Etiket yok, soru yok, siralama yok.
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
        fitted.append((qid, texts, Xw, Xc, Xl, Z))

    gate_pass = all(r["pass"] for r in gate_rows)
    write_labeled_json(
        os.path.join(outdir, "GATE.json"),
        {"gate": "ozellik geometrisi birebir eslesme", "overall_pass": bool(gate_pass), "rows": gate_rows},
    )
    if not gate_pass:
        print("KAPI KALDI: spektrum raporlanmayacak. Ayrinti icin GATE.json.", file=sys.stderr)
        sys.exit(3)
    print("KAPI GECTI: tum geometri degerleri birebir eslesti.", flush=True)

    # --- ADIM 2: Iki olcum. (A) ham SVD spektrumu, (B) yontemin gordugu varyans. ---
    per_archive = []
    for qid, texts, Xw, Xc, Xl, Z in fitted:
        # Dondurulmus probla ayni hat (buildrep, S96 blogu):
        s96 = TruncatedSVD(n_components=N_COMPONENTS, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)

        sigma = np.asarray(s96.singular_values_, dtype=np.float64)
        p_a, r2_a, _ = loglog_fit(sigma)
        frac12_a = float(np.sum(sigma[:12] ** 2) / np.sum(sigma ** 2))

        var_c = np.var(C, axis=0)  # ddof=0; probla ayni (hetero).
        p_b, r2_b, _ = loglog_fit(var_c)
        frac12_b = float(np.sum(var_c[:12]) / np.sum(var_c))

        occ = np.mean(C >= 0, axis=0)
        n_out_45 = int(np.sum((occ < 0.45) | (occ > 0.55)))
        n_out_30 = int(np.sum((occ < 0.30) | (occ > 0.70)))

        per_archive.append(
            {
                "question_id": qid,
                "N_archive": int(Z.shape[0]),
                "sigma": [float(x) for x in sigma],
                "p_A": p_a,
                "r2_A": r2_a,
                "frac12_A": frac12_a,
                "var_C": [float(x) for x in var_c],
                "p_B": p_b,
                "r2_B": r2_b,
                "frac12_B": frac12_b,
                "sign_balance": {
                    "occ_all": [float(x) for x in occ],
                    "occ_mean": float(np.mean(occ)),
                    "occ_min": float(np.min(occ)),
                    "occ_max": float(np.max(occ)),
                    "n_outside_045_055": n_out_45,
                    "n_outside_030_070": n_out_30,
                },
            }
        )
        print(
            f"OLCUM {qid}: p_A={p_a:.4f} R2_A={r2_a:.4f} f12_A={frac12_a:.4f} | "
            f"p_B={p_b:.4f} R2_B={r2_b:.4f} f12_B={frac12_b:.4f} | "
            f"isaret-disi(45)={n_out_45} isaret-disi(30)={n_out_30}",
            flush=True,
        )

    aggregate = {
        "n_archives": len(per_archive),
        "p_A": summarize([a["p_A"] for a in per_archive]),
        "r2_A": summarize([a["r2_A"] for a in per_archive]),
        "frac12_A": summarize([a["frac12_A"] for a in per_archive]),
        "p_B": summarize([a["p_B"] for a in per_archive]),
        "r2_B": summarize([a["r2_B"] for a in per_archive]),
        "frac12_B": summarize([a["frac12_B"] for a in per_archive]),
        "n_outside_045_055": summarize([a["sign_balance"]["n_outside_045_055"] for a in per_archive]),
        "n_outside_030_070": summarize([a["sign_balance"]["n_outside_030_070"] for a in per_archive]),
    }
    write_labeled_json(
        os.path.join(outdir, "SPECTRUM.json"),
        {"svd_seed": SVD_SEED, "n_components": N_COMPONENTS, "per_archive": per_archive, "aggregate": aggregate},
    )
    print("YAZILDI: GATE.json, SPECTRUM.json", flush=True)


if __name__ == "__main__":
    main()
