# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BEYAN EDILMIS YENIDEN-UYARLAMA (declared re-fit): rol geometrisi olcumu.

Yalnizca temsilin GEOMETRISI (merkezlenmis C + dondurulmus isaret kodu) ve
derlemin YAPISAL ustverisi (konusmaci rolu, sira) olculur. Altin/kanit
etiketi (gold/evidence) ACILMAZ; recall/dogruluk/siralama/benchmark
hesaplanmaz; hicbir geri-getirimin DOGRU olup olmadigi degerlendirilmez.
item['question']/['answer']/['answer_session_ids'] ve turn etiket alanlari
bu betikte hicbir yerde OKUNMAZ. Adapterin build_archive islevi
CAGRILMAZ (etiket okudugu icin); arsiv metni, kapili gerceklesmedeki gibi
yalnizca [date]/role/content alanlarindan kurulur.
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
    "hattinin yeniden uyarlanmasindan okunan TANIMLAYICI geometri "
    "olcumleridir. Hicbir retrieval/recall/gold/benchmark sonucu "
    "hesaplanmamistir; geri-getirim etkisi OL katolmus/cikarilamaz."
)
SVD_SEED = 5204  # Dondurulmus probdan aynen (SVD_SEED=5204).
N_COMPONENTS = 96
RNG_SEED = 7  # Rastgele-karsi-ornekleme icin sabit tohum.
N_RANDOM = 20  # Asistan basina rastgele diger-tur orneklemi.
THRESHOLDS = (4, 8, 16)


def load_adapter(path):
    spec = importlib.util.spec_from_file_location("v52_adapter_refit_roles", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def archive_texts_and_roles(item):
    """YALNIZCA yapi alanlarini okur: etiket/soru/cevap alanlarina dokunmaz.

    Dondurulmus adapterdaki build_archive+fit_input_payload ile ayni metni
    uretir: memory_text = f"[{date}] {role}: {content}", ayni sirayla.
    Donus: (texts, roles, sess_idx, turn_idx) — tum listeler ayni sirada.
    """
    sids = item["haystack_session_ids"]
    dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    texts, roles, sess_idx, turn_idx = [], [], [], []
    for si, (sid, date, sess) in enumerate(zip(sids, dates, sessions)):
        if not isinstance(sess, list):
            continue
        for ti, turn in enumerate(sess):
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")  # yapi: 'user'/'assistant' beklenir
            content = turn.get("content")
            if not isinstance(content, str):
                content = "" if content is None else str(content)
            texts.append(f"[{date}] {role}: {content}")
            roles.append(role)
            sess_idx.append(si)
            turn_idx.append(ti)
    return texts, roles, np.asarray(sess_idx), np.asarray(turn_idx)


def hamming_matrix(D):
    return np.count_nonzero(D[:, None, :] != D[None, :, :], axis=2).astype(np.int32)


def cosine_matrix(C):
    n = np.linalg.norm(C, axis=1, keepdims=True)
    n[n == 0] = 1.0
    Cn = C / n
    return Cn @ Cn.T


def auc_greater(a, b):
    """P(b > a) + 0.5*P(b == a); a=komsu, b=diger. Sirali-birlestirme ile."""
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    order_a = np.argsort(a, kind="mergesort")
    order_b = np.argsort(b, kind="mergesort")
    sa = a[order_a]
    sb = b[order_b]
    # Her a icin: b'de a'dan buyuklerin sayisi + esitlerin yarisini topla.
    import bisect

    sb_list = sb.tolist()
    total = 0.0
    nb = len(sb_list)
    for v in sa.tolist():
        lo = bisect.bisect_right(sb_list, v)
        hi = bisect.bisect_left(sb_list, v)
        total += (nb - lo) + 0.5 * (lo - hi)
    return float(total / (len(sa) * nb))


def qstats(x):
    a = np.asarray(x, dtype=np.float64).ravel()
    return {
        "n": int(a.size),
        "median": float(np.median(a)) if a.size else float("nan"),
        "mean": float(np.mean(a)) if a.size else float("nan"),
        "q25": float(np.quantile(a, 0.25)) if a.size else float("nan"),
        "q75": float(np.quantile(a, 0.75)) if a.size else float("nan"),
        "min": float(np.min(a)) if a.size else float("nan"),
        "max": float(np.max(a)) if a.size else float("nan"),
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


def main():
    ap = argparse.ArgumentParser(description="Rol geometrisi olcumu (re-fit, etiketsiz).")
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
    target_ids = [r["question_id"] for r in targets]

    ad = load_adapter(args.adapter)

    print(f"Derlem yukleniyor: {args.corpus}", flush=True)
    with open(args.corpus, encoding="utf-8") as f:
        data = json.load(f)
    by_id = {str(x["question_id"]): x for x in data}

    # --- ADIM 1 (yapi): rol sayimi. Etiket alanlari okunmaz. ---
    role_values = {}
    n_turns_all, n_sess_all = 0, 0
    for it in data:
        for s in it["haystack_sessions"]:
            if not isinstance(s, list):
                continue
            n_sess_all += 1
            for turn in s:
                if not isinstance(turn, dict):
                    continue
                r = turn.get("role")
                role_values[repr(r)] = role_values.get(repr(r), 0) + 1
                n_turns_all += 1

    # --- KAPI: tum secili arsivlerde geometri birebir tutmalidir. ---
    gate_rows = []
    fitted = []
    for row in targets:
        qid = row["question_id"]
        item = by_id[qid]
        texts, roles, sess_idx, turn_idx = archive_texts_and_roles(item)
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
        gate_rows.append({"question_id": qid, "expected": exp, "measured": got,
                          "pass": bool(ok)})
        print(f"KAPI {qid}: beklenen={exp} olculen={got} -> "
              f"{'GECTI' if ok else 'KALDI'}", flush=True)
        fitted.append((qid, texts, roles, sess_idx, turn_idx, Z))

    gate_pass = all(r["pass"] for r in gate_rows)
    write_labeled_json(
        os.path.join(outdir, "GATE.json"),
        {"gate": "ozellik geometrisi birebir eslesme",
         "overall_pass": bool(gate_pass), "rows": gate_rows},
    )
    if not gate_pass:
        print("KAPI KALDI: rol olcumu raporlanmayacak. Ayrinti: GATE.json.",
              file=sys.stderr)
        sys.exit(3)
    print("KAPI GECTI: tum geometri degerleri birebir eslesti.", flush=True)

    # --- ADIM 2: rol geometrisi. ---
    rng = np.random.default_rng(RNG_SEED)
    per_archive = []
    for qid, texts, roles, sess_idx, turn_idx, Z in fitted:
        s96 = TruncatedSVD(n_components=N_COMPONENTS, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        D = C >= 0  # dondurulmus isaret kodu

        n = len(texts)
        roles_arr = np.asarray(roles)
        is_user = roles_arr == "user"
        is_ast = roles_arr == "assistant"
        n_user = int(is_user.sum())
        n_ast = int(is_ast.sum())

        H = hamming_matrix(D)
        S = cosine_matrix(C)

        # Komsuluk anahtarlari: (oturum, tur) -> arsiv sirasi.
        key_to_pos = {(int(s), int(t)): i
                      for i, (s, t) in enumerate(zip(sess_idx.tolist(),
                                                     turn_idx.tolist()))}

        # A. Bitisik-cift: her asistan turu -> HEMEN ONCEKI (ayni oturum,
        # turn_index-1) kullanici turu.
        adj_h, adj_c = [], []
        other_h_pool, other_c_pool = [], []
        rand_h, rand_c = [], []
        n_ast_with_prev_user = 0
        n_ast_prev_nonuser = 0
        for i in range(n):
            if roles[i] != "assistant":
                continue
            j = key_to_pos.get((int(sess_idx[i]), int(turn_idx[i]) - 1))
            if j is None or roles[j] != "user":
                n_ast_prev_nonuser += 1
                continue
            n_ast_with_prev_user += 1
            adj_h.append(int(H[i, j]))
            adj_c.append(float(S[i, j]))
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            mask[j] = False
            other_h_pool.extend(H[i][mask].tolist())
            other_c_pool.extend(S[i][mask].tolist())
            cand = np.flatnonzero(mask)
            pick = cand[rng.choice(len(cand),
                                   size=min(N_RANDOM, len(cand)),
                                   replace=False)]
            rand_h.extend(H[i][pick].tolist())
            rand_c.extend(S[i][pick].tolist())
        adj_h = np.asarray(adj_h, dtype=np.float64)
        adj_c = np.asarray(adj_c, dtype=np.float64)
        other_h_pool = np.asarray(other_h_pool, dtype=np.float64)
        other_c_pool = np.asarray(other_c_pool, dtype=np.float64)

        adjacent = {
            "n_assistant_with_preceding_user": int(n_ast_with_prev_user),
            "n_assistant_without_preceding_user": int(n_ast_prev_nonuser),
            "hamming_adjacent": qstats(adj_h),
            "hamming_all_other": qstats(other_h_pool),
            "hamming_random20": qstats(rand_h),
            "hamming_median_gap_all_other_minus_adjacent": float(
                np.median(other_h_pool) - np.median(adj_h)) if adj_h.size else float("nan"),
            "hamming_auc_other_greater_than_adjacent": auc_greater(adj_h, other_h_pool),
            "frac_adjacent_below_random_median": float(
                np.mean(adj_h < np.median(other_h_pool))) if adj_h.size else float("nan"),
            "cosine_adjacent": qstats(adj_c),
            "cosine_all_other": qstats(other_c_pool),
            "cosine_random20": qstats(rand_c),
            "cosine_median_gap_adjacent_minus_all_other": float(
                np.median(adj_c) - np.median(other_c_pool)) if adj_c.size else float("nan"),
        }

        # B. Komsu bilesimi: her tur prob (kendi-disinda), Hamming ilk-3/10.
        # Esitlik-bozma: (uzaklik, arsiv-sirasi) sozluk sirasi — belirlenimci.
        idx = np.arange(n)
        sesh_frac3, sesh_frac10, part_frac3, part_frac10 = [], [], [], []
        hit3, hit10 = [], []
        by_role = {}
        for role in ("user", "assistant"):
            sel = np.flatnonzero(roles_arr == role)
            f3_s, f10_s, f3_p, f10_p, h3, h10 = [], [], [], [], [], []
            for i in sel.tolist():
                order = np.lexsort((idx, H[i].astype(np.int64)))
                order = order[order != i]
                top3, top10 = order[:3], order[:10]
                f3_s.append(float(np.mean(sess_idx[top3] == sess_idx[i])))
                f10_s.append(float(np.mean(sess_idx[top10] == sess_idx[i])))
                partners = set()
                for dt in (-1, 1):
                    k = (int(sess_idx[i]), int(turn_idx[i]) + dt)
                    if k in key_to_pos:
                        partners.add(key_to_pos[k])
                p3 = sum(1 for t in top3 if t in partners)
                p10 = sum(1 for t in top10 if t in partners)
                f3_p.append(p3 / 3.0)
                f10_p.append(p10 / 10.0)
                h3.append(1.0 if p3 > 0 else 0.0)
                h10.append(1.0 if p10 > 0 else 0.0)
            by_role[role] = {
                "n_probes": int(len(sel)),
                "same_session_frac_top3_mean": float(np.mean(f3_s)) if f3_s else float("nan"),
                "same_session_frac_top10_mean": float(np.mean(f10_s)) if f10_s else float("nan"),
                "partner_frac_top3_mean": float(np.mean(f3_p)) if f3_p else float("nan"),
                "partner_frac_top10_mean": float(np.mean(f10_p)) if f10_p else float("nan"),
                "partner_hit_top3_rate": float(np.mean(h3)) if h3 else float("nan"),
                "partner_hit_top10_rate": float(np.mean(h10)) if h10 else float("nan"),
            }
            sesh_frac3.extend(f3_s)
            sesh_frac10.extend(f10_s)
            part_frac3.extend(f3_p)
            part_frac10.extend(f10_p)
            hit3.extend(h3)
            hit10.extend(h10)
        neighbours = {
            "tie_break": "(hamming, archive_index) lexicographic; leave-one-out",
            "by_role": by_role,
            "overall_same_session_frac_top3_mean": float(np.mean(sesh_frac3)),
            "overall_same_session_frac_top10_mean": float(np.mean(sesh_frac10)),
            "overall_partner_frac_top3_mean": float(np.mean(part_frac3)),
            "overall_partner_frac_top10_mean": float(np.mean(part_frac10)),
            "overall_partner_hit_top3_rate": float(np.mean(hit3)),
            "overall_partner_hit_top10_rate": float(np.mean(hit10)),
        }

        # C. Rol asimetrisi: en-yakin-komsu Hamming dagilimi (rol bazinda).
        asym = {}
        for role in ("user", "assistant"):
            sel = np.flatnonzero(roles_arr == role)
            nn = []
            for i in sel.tolist():
                row = H[i].astype(np.int64)
                row[i] = 10 ** 9
                nn.append(float(row.min()))
            asym[role] = qstats(nn)
            asym[role]["frac_exact_duplicate_nn"] = float(np.mean(np.asarray(nn) == 0)) if nn else float("nan")
        asym["median_gap_user_minus_assistant"] = float(
            asym["user"]["median"] - asym["assistant"]["median"])

        # D. Kopya olcegi: tum sirali-olmayan ciftler + esikler.
        iu = np.triu_indices(n, k=1)
        all_h = H[iu]
        total_pairs = int(all_h.size)
        adj_pairs_total = 0
        adj_mask = np.zeros(total_pairs, dtype=bool)
        # Bitisik ciftler: ayni oturum, ardisik tur, roller farkli.
        for k in range(total_pairs):
            i, j = int(iu[0][k]), int(iu[1][k])
            if (sess_idx[i] == sess_idx[j]
                    and abs(int(turn_idx[i]) - int(turn_idx[j])) == 1
                    and roles[i] != roles[j]):
                adj_mask[k] = True
        adj_pairs_total = int(adj_mask.sum())
        dup = {"total_pairs": total_pairs, "adjacent_pairs_total": adj_pairs_total,
               "thresholds": {}}
        for th in THRESHOLDS:
            m = all_h <= th
            n_th = int(m.sum())
            n_adj = int((m & adj_mask).sum())
            dup["thresholds"][str(th)] = {
                "n_pairs_le_th": n_th,
                "frac_of_all_pairs": float(n_th / total_pairs) if total_pairs else 0.0,
                "n_adjacent_among_them": n_adj,
                "frac_adjacent_among_them": float(n_adj / n_th) if n_th else 0.0,
            }

        # ADIM 3: havuz daralmasi + elenecek yakin-kopya sayisi (sayim).
        # user-only dizinde elenen = en az bir assistant iceren ciftler.
        iu_i, iu_j = iu[0], iu[1]
        has_ast = is_ast[iu_i] | is_ast[iu_j]
        has_user = is_user[iu_i] | is_user[iu_j]
        shrink = {
            "N": int(n),
            "N_user": n_user,
            "N_assistant": n_ast,
            "frac_user": float(n_user / n),
            "frac_assistant": float(n_ast / n),
            "eliminated_pairs": {},
        }
        for th in THRESHOLDS:
            m = all_h <= th
            shrink["eliminated_pairs"][str(th)] = {
                "under_user_only": int((m & has_ast).sum()),
                "under_assistant_only": int((m & has_user).sum()),
            }

        per_archive.append({
            "question_id": qid,
            "N_archive": int(n),
            "N_user": n_user,
            "N_assistant": n_ast,
            "adjacent": adjacent,
            "neighbours": neighbours,
            "asymmetry": asym,
            "duplication": dup,
            "shrink": shrink,
        })
        a = adjacent
        print(f"OLCUM {qid}: N={n} U={n_user} A={n_ast} "
              f"bitisik-H-med={a['hamming_adjacent']['median']:.1f} "
              f"diger-H-med={a['hamming_all_other']['median']:.1f} "
              f"AUC={a['hamming_auc_other_greater_than_adjacent']:.3f} "
              f"bitisik-C-med={a['cosine_adjacent']['median']:.3f} "
              f"diger-C-med={a['cosine_all_other']['median']:.3f}", flush=True)

    def med_of(key):
        v = [p[key] for p in per_archive]
        return v

    aggregate = {
        "n_archives": len(per_archive),
        "adjacent_hamming_median_per_archive": [p["adjacent"]["hamming_adjacent"]["median"] for p in per_archive],
        "other_hamming_median_per_archive": [p["adjacent"]["hamming_all_other"]["median"] for p in per_archive],
        "adjacent_cosine_median_per_archive": [p["adjacent"]["cosine_adjacent"]["median"] for p in per_archive],
        "other_cosine_median_per_archive": [p["adjacent"]["cosine_all_other"]["median"] for p in per_archive],
        "auc_per_archive": [p["adjacent"]["hamming_auc_other_greater_than_adjacent"] for p in per_archive],
        "nn_median_user_per_archive": [p["asymmetry"]["user"]["median"] for p in per_archive],
        "nn_median_assistant_per_archive": [p["asymmetry"]["assistant"]["median"] for p in per_archive],
    }

    step1 = {
        "corpus_role_values": role_values,
        "corpus_n_turns": int(n_turns_all),
        "corpus_n_sessions": int(n_sess_all),
        "adapter_build_archive_static_reading": {
            "role_source": "turn['role']; beklenen degerler {'user','assistant'}",
            "memory_text": "[date] role: content — rol, metin on-eki olarak TEMSIL GIRDISINE GIRER",
            "role_filter": "YOK: her tur (rol ne olursa olsun) memories'e eklenir; "
                           "gecersiz rol yalnizca 'issues' kaydina yazilir, eleme yapilmaz",
            "structured_role_in_fit": "fit_input_payload yalnizca memory_text dizgilerini verir; "
                                      "yapisal 'role' alani uyarlamaya ayri bir ozellik olarak GIRMEZ",
            "both_roles_indexed": True,
            "note": "Bu okuma, adapter KAYNAK KODUNUN statik incelemesidir; "
                    "build_archive CALISTIRILMAMISTIR (etiket okudugu icin).",
        },
    }

    write_labeled_json(
        os.path.join(outdir, "ROLES.json"),
        {"svd_seed": SVD_SEED, "n_components": N_COMPONENTS,
         "random_seed": RNG_SEED, "n_random_per_assistant": N_RANDOM,
         "step1": step1, "per_archive": per_archive, "aggregate": aggregate,
         "not_measured": "Geri-getirim etkisi OLCULMEDI ve bu veriden "
                         "cikarilamaz: aday eleme, kanit iceren bellekleri de siler; "
                         "fayda/zarar yonu icin altin etiket gerekir ve etiket "
                         "acilmamistir."},
    )
    print("YAZILDI: GATE.json, ROLES.json", flush=True)


if __name__ == "__main__":
    main()
