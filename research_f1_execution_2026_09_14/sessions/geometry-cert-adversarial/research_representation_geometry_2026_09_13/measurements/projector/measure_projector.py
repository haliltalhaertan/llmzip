# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit): paylasilan projektorun bayt maliyeti.

Mühürlü görev "Task4F1" siniri: HICBIR retrieval sonucu, recall/dogruluk, gold/evidence
etiketi, siralama, benchmark ya da sonuc sayisi hesaplanmaz. Bu betik yalnizca
temsili yeniden uyarlar (re-fit) ve uydurulan yapilarin SERILESMIS BOYUTLARINI
ölçer. Ölçülen boyutlar sadik bir yeniden-uydurmaya aittir; dondurulmus üretim
yapitinin (frozen production artifact) fiziksel serilesmesi hicbir zaman
bulunamadi, bu yuzden bu olcum o yapitin geri kazanimi DEGILDIR.

Hatti, kapisi gecmis olcumden aynen alir (reuse):
  fit_archive_representation(texts) -> hstack -> TruncatedSVD(96) -> normalize -> mu.
Yalnizca arsiv metinleri okunur; soru/cevap/gold/has_answer okunmaz.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import struct
import sys
import zlib

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
    "hattinin yeniden uyarlanmasindan okunan SERILESMIS BOYUTLARDIR. "
    "Dondurulmus yapitin fiziksel serilesmesi hic bulunamadi. "
    "Task4F1 muhru: retrieval/recall/gold/siralama/benchmark/sonuc sayisi YOK."
)
TASK_BOUNDARY = (
    "Mühürlü görev Task4F1: retrieval sonucu, recall/dogruluk, gold/evidence "
    "etiketi, siralama, benchmark, sonuc sayisi hesaplanmadi; yalnizca "
    "yeniden-uydurulan (re-fit) temsilin kalici yapilarinin bayt boyutlari olculdu."
)
SVD_SEED = 5204
N_COMPONENTS = 96
MARGINAL = 12


def load_adapter(path):
    spec = importlib.util.spec_from_file_location("v52_adapter_refit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def archive_texts_only(item):
    """Yalnizca arsiv metinleri; etiket/soru okunmaz (spektrum betiginden aynen)."""
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


def vocab_terms_in_order(vec):
    vocab = vec.vocabulary_
    terms = [None] * len(vocab)
    for t, i in vocab.items():
        terms[i] = t
    return terms


def vocab_structured_bytes(terms):
    """Siralama index sirasi; her terim: uint32 LE uzunluk + UTF-8. Cozulebilir en az yapi."""
    parts = []
    for t in terms:
        b = t.encode("utf-8")
        parts.append(struct.pack("<I", len(b)))
        parts.append(b)
    return b"".join(parts)


def vocab_delim_bytes(terms):
    """Alt-sinir referansi: UTF-8 terimler + terim basi 1 ayrac (\\n). Guvenligi ayrica denetlenir."""
    if not terms:
        return b""
    return b"\n".join(t.encode("utf-8") for t in terms) + b"\n"


def numeric_raw(arr, dtype):
    return np.asarray(arr).astype(dtype, copy=False).tobytes()


def zcomp(raw):
    return zlib.compress(raw, 6)


def write_labeled_json(path, payload):
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
    ap = argparse.ArgumentParser(description="Projektor bayt olcumu (re-fit, boyut only).")
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

    gate_rows = []
    per_archive = []
    fitted_ok = True
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
        if not ok:
            fitted_ok = False
            continue
        # Dondurulmus hat: SVD96 + normalize + mu (spektrum betiginden aynen).
        s96 = TruncatedSVD(n_components=N_COMPONENTS, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        d_lex = int(sv.components_.shape[0])

        # --- Boyut olcumu: sorgu aninda gereken kalici nesneler. ---
        w_terms = vocab_terms_in_order(wv)
        c_terms = vocab_terms_in_order(cv)
        w_struct = vocab_structured_bytes(w_terms)
        c_struct = vocab_structured_bytes(c_terms)
        w_utf8 = sum(len(t.encode("utf-8")) for t in w_terms)
        c_utf8 = sum(len(t.encode("utf-8")) for t in c_terms)
        # Ayrac guvenligi: \\n ve \\x00 hicbir terimde var mi?
        w_bad = sum(1 for t in w_terms if ("\n" in t or "\x00" in t))
        c_bad = sum(1 for t in c_terms if ("\n" in t or "\x00" in t))
        w_delim_len = w_utf8 + len(w_terms)  # 1 bayt/terim alt sinir
        c_delim_len = c_utf8 + len(c_terms)
        w_z = zcomp(w_struct)
        c_z = zcomp(c_struct)

        w_idf = np.asarray(wv.idf_)
        c_idf = np.asarray(cv.idf_)
        sv_c = np.asarray(sv.components_)
        s96_c = np.asarray(s96.components_)
        mu1 = np.asarray(mu).reshape(-1)

        def num_entry(a):
            r32 = numeric_raw(a, np.float32)
            r16 = numeric_raw(a, np.float16)
            return {
                "n": int(a.size),
                "raw64_ref": int(a.size * 8),
                "raw32": int(len(r32)),
                "raw16": int(len(r16)),
                "zlib32": int(len(zcomp(r32))),
                "zlib16": int(len(zcomp(r16))),
            }

        e_widf = num_entry(w_idf)
        e_cidf = num_entry(c_idf)
        e_sv = num_entry(sv_c)
        e_s96 = num_entry(s96_c)
        e_mu = num_entry(mu1)
        e_sv["shape"] = [int(x) for x in sv_c.shape]
        e_s96["shape"] = [int(x) for x in s96_c.shape]

        v_struct = len(w_struct) + len(c_struct)
        v_z = len(w_z) + len(c_z)
        n32 = e_widf["raw32"] + e_cidf["raw32"] + e_sv["raw32"] + e_s96["raw32"] + e_mu["raw32"]
        n16 = e_widf["raw16"] + e_cidf["raw16"] + e_sv["raw16"] + e_s96["raw16"] + e_mu["raw16"]
        n32z = e_widf["zlib32"] + e_cidf["zlib32"] + e_sv["zlib32"] + e_s96["zlib32"] + e_mu["zlib32"]
        n16z = e_widf["zlib16"] + e_cidf["zlib16"] + e_sv["zlib16"] + e_s96["zlib16"] + e_mu["zlib16"]
        n64 = e_widf["raw64_ref"] + e_cidf["raw64_ref"] + e_sv["raw64_ref"] + e_s96["raw64_ref"] + e_mu["raw64_ref"]

        tot_a = v_struct + n32
        tot_b = v_struct + n16
        tot_az = v_z + n32z
        tot_bz = v_z + n16z
        tot_nat = v_struct + n64
        nvec = int(Z.shape[0])

        def ratio(tot):
            spv = tot / nvec
            return {"shared_total": int(tot), "shared_per_vector": float(spv), "effective": float(MARGINAL + spv)}

        def breake(tot):
            return {"to_12": int(math.ceil(tot / 12)), "to_1": int(tot)}

        per_archive.append({
            "question_id": qid,
            "N_archive": nvec,
            "word_columns": int(Xw.shape[1]),
            "char_columns": int(Xc.shape[1]),
            "combined_columns": int(Z.shape[1]),
            "lexical_dim_d": d_lex,
            "components": {
                "word_vocab": {"n_terms": len(w_terms), "utf8_sum": int(w_utf8),
                               "structured_bytes": int(len(w_struct)), "delim1_bytes_ref": int(w_delim_len),
                               "zlib_bytes": int(len(w_z)), "bad_delim_terms": int(w_bad)},
                "char_vocab": {"n_terms": len(c_terms), "utf8_sum": int(c_utf8),
                               "structured_bytes": int(len(c_struct)), "delim1_bytes_ref": int(c_delim_len),
                               "zlib_bytes": int(len(c_z)), "bad_delim_terms": int(c_bad)},
                "word_idf": e_widf, "char_idf": e_cidf,
                "sv_components": e_sv, "s96_components": e_s96, "mu": e_mu,
            },
            "totals": {"a_raw_f32_struct": int(tot_a), "b_raw_f16_struct": int(tot_b),
                       "a_zlib": int(tot_az), "b_zlib": int(tot_bz),
                       "native_f64_struct_ref": int(tot_nat),
                       "vocab_struct": int(v_struct), "vocab_zlib": int(v_z),
                       "numeric_f32": int(n32), "numeric_f16": int(n16),
                       "numeric_f32_zlib": int(n32z), "numeric_f16_zlib": int(n16z)},
            "ratios": {"a_raw": ratio(tot_a), "b_raw": ratio(tot_b),
                       "a_zlib": ratio(tot_az), "b_zlib": ratio(tot_bz)},
            "breakeven": {"a_raw": breake(tot_a), "b_raw": breake(tot_b),
                          "a_zlib": breake(tot_az), "b_zlib": breake(tot_bz)},
        })
        print(f"BOYUT {qid}: N={nvec} d={d_lex} a_raw={tot_a} b_raw={tot_b} a_z={tot_az} b_z={tot_bz}", flush=True)
        del wv, cv, sv, Xw, Xc, Xl, Z, s96, Y, mu

    gate_pass = all(r["pass"] for r in gate_rows)
    write_labeled_json(os.path.join(outdir, "GATE.json"),
        {"task_boundary": TASK_BOUNDARY, "gate": "ozellik geometrisi birebir eslesme",
         "overall_pass": bool(gate_pass), "rows": gate_rows})
    if not gate_pass:
        print("KAPI KALDI: boyut raporlanmayacak. Ayrinti icin GATE.json.", file=sys.stderr)
        sys.exit(3)
    print("KAPI GECTI: tum geometri degerleri birebir eslesti.", flush=True)

    def med(xs):
        return float(np.median(np.asarray(xs, dtype=np.float64)))

    def summarize_totals(key):
        xs = [a["totals"][key] for a in per_archive]
        return {"median": float(np.median(np.asarray(xs, float))), "min": int(min(xs)), "max": int(max(xs))}

    agg = {
        "n_archives": len(per_archive),
        "marginal_bytes_per_vector": MARGINAL,
        "totals": {k: summarize_totals(k) for k in
                   ["a_raw_f32_struct", "b_raw_f16_struct", "a_zlib", "b_zlib", "native_f64_struct_ref"]},
        "ratios_median": {},
        "breakeven_median": {},
    }
    for rk in ["a_raw", "b_raw", "a_zlib", "b_zlib"]:
        agg["ratios_median"][rk] = {
            "shared_total": med([a["ratios"][rk]["shared_total"] for a in per_archive]),
            "shared_per_vector": med([a["ratios"][rk]["shared_per_vector"] for a in per_archive]),
            "effective": med([a["ratios"][rk]["effective"] for a in per_archive]),
        }
        agg["breakeven_median"][rk] = {
            "to_12": int(med([a["breakeven"][rk]["to_12"] for a in per_archive])),
            "to_1": int(med([a["breakeven"][rk]["to_1"] for a in per_archive])),
        }

    payload = {
        "task_boundary": TASK_BOUNDARY,
        "config": {"corpus": args.corpus, "adapter": args.adapter, "geometry": args.geometry,
                   "n_archives": args.n_archives, "svd_seed": SVD_SEED, "n_components": N_COMPONENTS,
                   "marginal_bytes_per_vector": MARGINAL,
                   "query_path": "wv.transform -> cv.transform -> sv.transform(Qw) -> hstack -> s96.transform -> (.-mu)",
                   "svd_mean_offset": "yok (TruncatedSVD.transform yalnizca components_ kullanir; kaynakta dogrulandi)"},
        "vocab_encoding": {"ana": "index sirasi + terim basi uint32 LE uzunluk + UTF-8 (cozulebilir)",
                           "alt_sinir_ref": "UTF-8 toplami + terim basi 1 ayrac (guvenlik her arsivde denetlendi)"},
        "numeric_encoding": {"a": "yogun float32", "b": "yogun float16 (olasi ucuz secim)",
                             "ref": "yerel float64 (sklearn ciktisi); karsilastirma icin"},
        "compression": "nesne basi zlib seviye 6; toplamlar sikistirilmis parcalarin toplami",
        "unavoidable_vs_choices": {
            "kacinilmaz": ["word vocab + IDF", "char vocab + IDF", "sv.components_", "s96.components_", "mu"],
            "secim": ["float32/float16/float64 duyarligi", "vocab yapisi (uzunluk-onek vs ayrac)",
                      "sikistirma acik/kapali", "fazladan SVD alanlarini (singular_values_ vb.) saklamamak"],
        },
        "excluded_with_reason": {
            "singular_values_/explained_variance_": "transform kullanmaz; sorgu icin gerekmez",
            "stop_words listesi": "kod sabiti ('english'); arsiv-ozel uydurma degil",
            "normalize/hstack/shape/skalerler": "durumsuz ya da ihmal edilebilir (<100 B)",
            "ITQ/rastgele izdusumler/imza kontrolleri": "yerel SIGN96 sorgu yolunda yok; ayri analizler",
            "oncelik (priority)": "cekirdekten uretilir, saklanmaz; ihmal edilebilir",
        },
        "per_archive": per_archive,
        "aggregate": agg,
        "not_checked": [
            "float16/float32 duyarlik dusurmenin geri-getirim davranisina etkisi (Task4F1 yasagi: bakilmadi)",
            "sikistirilmis saklamanin sorgu gecikmesine etkisi (bakilmadi)",
            "arsivler-arasi/global projektor (farkli dagitim; bu olcumun sonucu degil)",
            "dondurulmus uretim yapitinin boyutu (yapit bulunamadi; yalnizca re-fit olculdu)",
        ],
    }
    write_labeled_json(os.path.join(outdir, "PROJECTOR_BYTES.json"), payload)
    print("YAZILDI: GATE.json, PROJECTOR_BYTES.json", flush=True)


if __name__ == "__main__":
    main()
