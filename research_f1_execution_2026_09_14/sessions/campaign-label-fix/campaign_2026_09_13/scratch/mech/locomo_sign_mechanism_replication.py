from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

DATASET_URL = "https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json"
AUDIT_BASE = "https://raw.githubusercontent.com/dial481/locomo-audit/main/audit"
DATASET_SHA256 = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
DATASET_BYTES = 2805274
AUDIT_MANIFEST_SHA256 = "90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06"
FROZEN_NATIVE_FRAC_R3 = 0.23654714666441054
FROZEN_SCRIPT_SHA256 = "3f7f091fadc88dfcc1f68f38d6df10607d05d1e416d048fe776929a9a7b185a7"
SVD_SEED = 5204
SOURCE_LATENT_DIM = 32
N_NUISANCE = 20
TOPK = 3
EXPECTED_CATEGORY_COUNTS = {1: 282, 2: 321, 3: 96, 4: 841}
EXPECTED_QUESTIONS = 1540
EXPECTED_CORRECTIONS = 156

AUDIT_FILE_HASHES = {
"conv_0.json": (395163,"697a996db06a90500bafbf21c96f5170eafc8377eef632278b7a4b841ae15c39"),
"conv_1.json": (267513,"5b0a9a79e623e810a1e9a577d457ac99465e96e7c9cce58f593612d73350c34a"),
"conv_2.json": (526311,"476d9bcdaddfc2c5c0caeed21c48b2bedb8fe687772c25f6f98e4c5a63ce1e8a"),
"conv_3.json": (584086,"5c565f4efa6dbea4650a5f62eb04dea4b10fec713b984746ae5ca38df05a4754"),
"conv_4.json": (571480,"609f74bfad9de7719ef170e21ea140a24b20c0bf278ab9db215c4a26705e874d"),
"conv_5.json": (528568,"98c28de0c42795f2b67c85cc5a804191dee1a701959197c3167a2748b9260793"),
"conv_6.json": (499707,"5f7f9182f5e7dd842488292acf340e24ff773790e720a212433e4c047875c9b1"),
"conv_7.json": (551155,"84c53ec1b89b8846be2fd9146269a523fcc5542223344b517aa3757ac3a9fa88"),
"conv_8.json": (489039,"b2f301735825844b7bf71816eae4e16983854edc80898a8a578e3a78963215e9"),
"conv_9.json": (500515,"0f9775daf3bc6f9a6b8672aadbbf65f7e15947c5c1cb92d151306f1406d00a9d"),
"errors_conv_0.json": (24365,"63c778c8432b058d791417ec37bf8ac30b0bb83b1272afacb5a162b84fe5e3c4"),
"errors_conv_1.json": (7746,"a2db16644318c3c144544f4cb373028e416bbf20c6f07f46606cf66f45de4e6c"),
"errors_conv_2.json": (11824,"93c2aa8ee7d3bfb59ae1cca283d176a794d76d3751c69264ddc1f63ceb2b4b3a"),
"errors_conv_3.json": (23508,"c1d0162e534bf68dba6aff3ca3e73ba8179cab7a400d098b8be89048c7b58585"),
"errors_conv_4.json": (15447,"42520f95b654c85b564da6cd26f40cefb981de574066f7b92bdebbc780fa1376"),
"errors_conv_5.json": (9934,"af8c675a3e216ddb94e07c417fb37c45fc46740dfa8ce586fc8c527f7a3b9ee7"),
"errors_conv_6.json": (14435,"acb6d0d02f938180b3d1a7a45f80d432ece69d13b197371cb71ddbddb83a26ea"),
"errors_conv_7.json": (12048,"bbe2268a3254dcc9d3741a84748fadf8e169d21d837810e92dc63cdf8db562cb"),
"errors_conv_8.json": (15587,"c15ace8ef1a7cbf3fe63d3b7ff9c2851885f5e00abc1c184971ebb11128aedb2"),
"errors_conv_9.json": (15645,"2c2b8791d024e11ca6015a109f160b7177379b3b42ac8c9adb990546fc89c4ff"),
}

BANDS = {
    "High32": np.arange(0, 32),
    "Mid32": np.arange(32, 64),
    "Low32": np.arange(64, 96),
    "HighMid64": np.arange(0, 64),
    "HighLow64": np.r_[0:32, 64:96],
    "MidLow64": np.arange(32, 96),
    "Full96": np.arange(0, 96),
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "llmzip-v52-mechanism/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        dest.write_bytes(r.read())


def acquire_and_verify(work: Path):
    work.mkdir(parents=True, exist_ok=True)
    raw = work / "locomo10.json"
    audit = work / "audit"
    audit.mkdir(exist_ok=True)
    download(DATASET_URL, raw)
    if raw.stat().st_size != DATASET_BYTES or sha256_file(raw) != DATASET_SHA256:
        raise RuntimeError("dataset byte identity mismatch")
    rows = []
    for fn, (nbytes, h) in AUDIT_FILE_HASHES.items():
        p = audit / fn
        download(f"{AUDIT_BASE}/{fn}", p)
        got = (p.stat().st_size, sha256_file(p))
        if got != (nbytes, h):
            raise RuntimeError(f"audit byte identity mismatch {fn}: {got}")
        rows.append({"file": fn, "bytes": nbytes, "sha256": h})
    rows = sorted(rows, key=lambda x: x["file"])
    canon = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    mh = sha256_bytes(canon)
    if mh != AUDIT_MANIFEST_SHA256:
        raise RuntimeError(f"audit manifest mismatch {mh}")
    return raw, audit, rows


def norm_evidence(x):
    if x is None:
        return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def message_text(msg):
    speaker = str(msg.get("speaker", "")).strip()
    text = str(msg.get("text", "")).strip()
    cap = str(msg.get("blip_caption", "") or "").strip()
    if cap:
        text = f"{text} [IMAGE: {cap}]".strip()
    return f"{speaker}: {text}".strip(": ")


def raw_item_to_conv(item, idx):
    conv_id = f"locomo_{idx}"
    c = item.get("conversation", {})
    lines = []
    for sk in sorted([k for k in c if k.startswith("session_") and not k.endswith("_date_time")], key=lambda x: int(x.split("_")[1])):
        for msg in c.get(sk, []) or []:
            did = str(msg.get("dia_id", ""))
            if did:
                lines.append({"dia_id": did, "text": message_text(msg), "session": sk})
    qas = []
    for qi, q in enumerate(item.get("qa", []) or []):
        cat = int(q.get("category")) if q.get("category") is not None else None
        qid = q.get("question_id") or f"{conv_id}_qa{qi}"
        qas.append({"question_id": str(qid), "question": str(q.get("question", "")), "answer": str(q.get("answer", "")), "category": cat, "raw_evidence": norm_evidence(q.get("evidence"))})
    return {"conv_id": conv_id, "lines": lines, "qas": qas}


def load_audit_corrections(audit_dir: Path):
    corrections = {}
    for f in sorted(audit_dir.glob("errors_conv_*.json")):
        rows = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        for r in rows:
            qid = r.get("question_id")
            if not qid:
                continue
            corrections[str(qid)] = {
                "error_type": r.get("error_type"),
                "has_correct_evidence": "correct_evidence" in r,
                "correct_evidence": norm_evidence(r.get("correct_evidence")),
                "correct_answer": r.get("correct_answer"),
            }
    return corrections


def load_dataset(raw: Path, audit_dir: Path):
    arr = json.loads(raw.read_text(encoding="utf-8"))
    convs = [raw_item_to_conv(x, i) for i, x in enumerate(arr)]
    corr = load_audit_corrections(audit_dir)
    for c in convs:
        for q in c["qas"]:
            z = corr.get(q["question_id"])
            if z:
                q["correct_evidence"] = list(z["correct_evidence"]) if z.get("has_correct_evidence", False) else list(q["raw_evidence"])
            else:
                q["correct_evidence"] = list(q["raw_evidence"])
    cats = Counter(q["category"] for c in convs for q in c["qas"] if q.get("category") in EXPECTED_CATEGORY_COUNTS)
    nq = sum(cats.values())
    if len(convs) != 10 or nq != EXPECTED_QUESTIONS or dict(cats) != EXPECTED_CATEGORY_COUNTS or len(corr) != EXPECTED_CORRECTIONS:
        raise RuntimeError(f"cohort identity mismatch conv={len(convs)} nq={nq} cats={cats} corr={len(corr)}")
    return convs, corr


def fit_archive_representation(memory_texts: list[str]):
    if len(memory_texts) < 25:
        raise ValueError("Archive too small")
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(memory_texts))
    Xc = normalize(cv.fit_transform(memory_texts))
    d = min(SOURCE_LATENT_DIM, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    return wv, cv, svd, Xw, Xc, Xl


def build_representation(conv):
    lines = conv["lines"]
    texts = [x["text"] for x in lines]
    wv, cv, sv, Xw, Xc, Xl = fit_archive_representation(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    qas = [q for q in conv["qas"] if q.get("category") in EXPECTED_CATEGORY_COUNTS]
    questions = [q["question"] for q in qas]
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(s96.transform(Zq))
    QC = (QY - mu).astype(np.float64)
    id_to_row = {x["dia_id"]: i for i, x in enumerate(lines)}
    return {"C": C, "QC": QC, "qas": qas, "id_to_row": id_to_row, "N": len(lines), "explained_variance": np.asarray(s96.explained_variance_, float)}


def stable_archive_seed(archive_ordinal: int, trial: int = 0) -> int:
    return 5_100_000 + archive_ordinal * 100_000 + trial * 100


def topks_by_hamming(dist: np.ndarray, priorities: list[np.ndarray], k: int = TOPK) -> list[np.ndarray]:
    dist = np.asarray(dist)
    P = np.asarray(priorities, dtype=float)
    if len(dist) <= k:
        return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k - 1)[k - 1]
    strict = np.flatnonzero(dist < kth)
    boundary = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, boundary]
    if need == len(boundary):
        picks = np.tile(boundary, (len(P), 1))
    else:
        loc = np.argpartition(BP, need - 1, axis=1)[:, :need]
        picks = boundary[loc]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]


def topks_by_score(score: np.ndarray, priorities: list[np.ndarray], k: int = TOPK):
    return [np.lexsort((priorities[t], -score))[:k] for t in range(len(priorities))]


def fractional(top, gold):
    return len(set(map(int, top)) & set(map(int, gold))) / len(gold)


def bit_corr_abs_mean(D: np.ndarray) -> float:
    X = D.astype(float)
    sd = X.std(axis=0)
    keep = sd > 0
    if keep.sum() < 2:
        return float("nan")
    R = np.corrcoef(X[:, keep], rowvar=False)
    mask = ~np.eye(R.shape[0], dtype=bool)
    return float(np.mean(np.abs(R[mask])))


def code_unique_fraction(D: np.ndarray) -> float:
    packed = np.packbits(D, axis=1, bitorder="big")
    return float(len(np.unique(packed, axis=0)) / len(D))


def cosine_scores(C, QC):
    dn = np.linalg.norm(C, axis=1)
    qn = np.linalg.norm(QC, axis=1)
    den = qn[:, None] * dn[None, :]
    return np.divide(QC @ C.T, den, out=np.zeros((len(QC), len(C))), where=den > 0)


def pair_accumulate(dg: np.ndarray, dn: np.ndarray):
    # Equal weight per gold-nongold pair.
    diff = dn[None, :] - dg[:, None]
    total = diff.size
    advantage_sum = float(diff.sum())
    discr_sum = float((diff > 0).sum() + 0.5 * (diff == 0).sum())
    return total, advantage_sum, discr_sum


def run(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    raw, audit, audit_rows = acquire_and_verify(out / "source_bytes")
    convs, corr = load_dataset(raw, audit)

    reps = [build_representation(c) for c in convs]
    identity = {
        "dataset_sha256": sha256_file(raw), "dataset_bytes": raw.stat().st_size,
        "audit_manifest_sha256": AUDIT_MANIFEST_SHA256,
        "audit_file_count": len(audit_rows), "audit_correction_count": len(corr),
        "frozen_script_sha256": FROZEN_SCRIPT_SHA256,
        "numpy": np.__version__, "pandas": pd.__version__,
    }

    top_frac = {b: [] for b in BANDS}
    cosine_frac = []
    spectrum_rows = []
    qmargin_rows = []
    pair_stats = {b: {"pairs":0,"adv_sum":0.0,"disc_sum":0.0} for b in ["High32","Mid32","Low32","Full96"]}
    rescue = Counter()
    valid_questions = 0

    for ci, (conv, r) in enumerate(zip(convs, reps)):
        C, QC, qas, id_to_row, N = r["C"], r["QC"], r["qas"], r["id_to_row"], r["N"]
        priorities = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(N) for t in range(N_NUISANCE)]
        cos = cosine_scores(C, QC)

        # archive-level redundancy/code diagnostics for each spectral slice
        for b, idx in BANDS.items():
            D = C[:, idx] >= 0
            spectrum_rows.append({
                "conv_id": conv["conv_id"], "band": b, "archive_size": N, "bits": len(idx),
                "unique_code_fraction": code_unique_fraction(D),
                "duplicate_fraction": 1.0 - code_unique_fraction(D),
                "mean_abs_bit_correlation": bit_corr_abs_mean(D),
                "mean_coordinate_variance": float(np.mean(np.var(C[:, idx], axis=0))),
                "mean_svd_explained_variance": float(np.mean(r["explained_variance"][idx])),
            })

        bit_docs = {b: C[:,idx] >= 0 for b,idx in BANDS.items()}
        bit_queries = {b: QC[:,idx] >= 0 for b,idx in BANDS.items()}

        for qi, q in enumerate(qas):
            gold = list(dict.fromkeys([id_to_row[x] for x in q["correct_evidence"] if x in id_to_row]))
            if not gold:
                continue
            valid_questions += 1
            gold_set = set(gold)
            nongold = np.array([j for j in range(N) if j not in gold_set], dtype=int)
            dists = {}
            perq_frac = {}
            for b in BANDS:
                dist = np.count_nonzero(bit_docs[b] != bit_queries[b][qi][None,:], axis=1).astype(np.int16)
                dists[b] = dist
                tops = topks_by_hamming(dist, priorities)
                fq = float(np.mean([fractional(x, gold) for x in tops]))
                top_frac[b].append(fq)
                perq_frac[b] = fq

            ctops = topks_by_score(cos[qi], priorities)
            cf = float(np.mean([fractional(x, gold) for x in ctops]))
            cosine_frac.append(cf)

            # pairwise separation for thirds and full code
            for b in ["High32","Mid32","Low32","Full96"]:
                dg = dists[b][gold]
                dn = dists[b][nongold]
                n, adv, disc = pair_accumulate(dg, dn)
                pair_stats[b]["pairs"] += n
                pair_stats[b]["adv_sum"] += adv / len(BANDS[b])
                pair_stats[b]["disc_sum"] += disc

            # pairwise hard-negative rescue/degradation counts
            dhg, dhn = dists["High32"][gold], dists["High32"][nongold]
            dhmg, dhmn = dists["HighMid64"][gold], dists["HighMid64"][nongold]
            dhlg, dhln = dists["HighLow64"][gold], dists["HighLow64"][nongold]
            dfg, dfn = dists["Full96"][gold], dists["Full96"][nongold]
            H = dhg[:,None] < dhn[None,:]
            HM = dhmg[:,None] < dhmn[None,:]
            HL = dhlg[:,None] < dhln[None,:]
            F = dfg[:,None] < dfn[None,:]
            rescue["high_not_correct"] += int((~H).sum())
            rescue["high_not_correct_full_correct"] += int(((~H)&F).sum())
            rescue["high_correct"] += int(H.sum())
            rescue["high_correct_full_not_correct"] += int((H&(~F)).sum())
            rescue["high_not_correct_hm_correct"] += int(((~H)&HM).sum())
            rescue["high_not_correct_hl_correct"] += int(((~H)&HL).sum())
            rescue["hm_not_correct"] += int((~HM).sum())
            rescue["hm_not_correct_full_correct"] += int(((~HM)&F).sum())

            sign_margin = float(np.min(dists["Full96"][nongold]) - np.min(dists["Full96"][gold]))
            cosine_margin = float(np.max(cos[qi, gold]) - np.max(cos[qi, nongold]))
            qmargin_rows.append({
                "conv_id": conv["conv_id"], "question_id": q["question_id"], "category": q["category"],
                "gold_count": len(gold), "sign_fractional_R3": perq_frac["Full96"], "centered_cosine_fractional_R3": cf,
                "sign_hard_negative_margin_bits": sign_margin, "centered_cosine_hard_negative_margin": cosine_margin,
                "sign_beats_cosine": int(perq_frac["Full96"] > cf),
            })

    if valid_questions != 1535:
        raise RuntimeError(f"audit-valid denominator mismatch: {valid_questions}")

    native = float(np.mean(top_frac["Full96"]))
    reproduction_error = abs(native - FROZEN_NATIVE_FRAC_R3)
    reproducible = reproduction_error <= 1e-12

    sdf = pd.DataFrame(spectrum_rows)
    sdf.to_csv(out / "locomo_archive_band_diagnostics.csv", index=False)
    qdf = pd.DataFrame(qmargin_rows)
    qdf.to_csv(out / "locomo_question_margins.csv", index=False)

    # document-weighted archive diagnostics; codes are not compared across independently fit archives.
    band_rows = []
    for b in BANDS:
        x = sdf[sdf.band == b]
        w = x.archive_size.to_numpy(float)
        row = {
            "band": b, "bits": len(BANDS[b]),
            "fractional_R3": float(np.mean(top_frac[b])),
            "unique_code_fraction_doc_weighted": float(np.average(x.unique_code_fraction, weights=w)),
            "duplicate_fraction_doc_weighted": float(np.average(x.duplicate_fraction, weights=w)),
            "mean_abs_bit_correlation_doc_weighted": float(np.average(x.mean_abs_bit_correlation, weights=w)),
            "mean_coordinate_variance_doc_weighted": float(np.average(x.mean_coordinate_variance, weights=w)),
            "mean_svd_explained_variance_doc_weighted": float(np.average(x.mean_svd_explained_variance, weights=w)),
        }
        if b in pair_stats:
            ps = pair_stats[b]
            row["gold_minus_nongold_same_sign_advantage"] = ps["adv_sum"] / ps["pairs"]
            row["pairwise_gold_vs_nongold_discrimination"] = ps["disc_sum"] / ps["pairs"]
            row["pair_count"] = ps["pairs"]
        band_rows.append(row)
    bdf = pd.DataFrame(band_rows)
    bdf.to_csv(out / "locomo_spectrum_summary.csv", index=False)

    def ratio(a,b):
        return float(a/b) if b else float("nan")
    resc = {
        "high_wrong_or_tie_to_full_rescue": ratio(rescue["high_not_correct_full_correct"], rescue["high_not_correct"]),
        "high_correct_to_full_degrade": ratio(rescue["high_correct_full_not_correct"], rescue["high_correct"]),
        "high_wrong_or_tie_to_highmid_rescue": ratio(rescue["high_not_correct_hm_correct"], rescue["high_not_correct"]),
        "high_wrong_or_tie_to_highlow_rescue": ratio(rescue["high_not_correct_hl_correct"], rescue["high_not_correct"]),
        "highmid_wrong_or_tie_to_full_rescue": ratio(rescue["hm_not_correct_full_correct"], rescue["hm_not_correct"]),
        "raw_counts": dict(rescue),
    }

    sign_pos = float(np.mean(qdf.sign_hard_negative_margin_bits > 0))
    cos_pos = float(np.mean(qdf.centered_cosine_hard_negative_margin > 0))
    wins = qdf[qdf.sign_beats_cosine == 1]
    margins = {
        "native_sign_positive_margin_question_fraction": sign_pos,
        "centered_cosine_positive_margin_question_fraction": cos_pos,
        "centered_cosine_fractional_R3": float(np.mean(cosine_frac)),
        "sign_beats_cosine_question_count": int(len(wins)),
        "on_sign_beats_cosine_mean_sign_margin_bits": float(wins.sign_hard_negative_margin_bits.mean()) if len(wins) else None,
        "on_sign_beats_cosine_mean_cosine_margin": float(wins.centered_cosine_hard_negative_margin.mean()) if len(wins) else None,
    }

    # Verdict is deliberately qualitative and cross-benchmark, not a population significance claim.
    high = bdf.set_index("band")
    coarse_fine_signature = (
        high.loc["High32", "pairwise_gold_vs_nongold_discrimination"] > high.loc["Mid32", "pairwise_gold_vs_nongold_discrimination"] > high.loc["Low32", "pairwise_gold_vs_nongold_discrimination"]
        and high.loc["High32", "mean_abs_bit_correlation_doc_weighted"] > high.loc["Mid32", "mean_abs_bit_correlation_doc_weighted"] > high.loc["Low32", "mean_abs_bit_correlation_doc_weighted"]
        and resc["high_wrong_or_tie_to_full_rescue"] > resc["high_correct_to_full_degrade"]
        and high.loc["Full96", "fractional_R3"] > high.loc["High32", "fractional_R3"]
    )
    if not reproducible:
        verdict = "[REPRODUCTION DRIFT — MECHANISM VERDICT WITHHELD]"
    elif coarse_fine_signature and resc["high_wrong_or_tie_to_full_rescue"] >= 0.25:
        verdict = "[CROSS-BENCHMARK MECHANISM REPLICATION LEAD]"
    elif coarse_fine_signature or resc["high_wrong_or_tie_to_full_rescue"] > resc["high_correct_to_full_degrade"]:
        verdict = "[PARTIAL MECHANISM REPLICATION]"
    else:
        verdict = "[MECHANISM FALSIFIED AS CROSS-BENCHMARK EXPLANATION]"

    summary = {
        "status": "POST_HOC_EXPLORATORY_MECHANISM_DIAGNOSTIC",
        "scientific_interpretation_ceiling": "Fixed-benchmark exploratory mechanism evidence only; no population significance or causal proof.",
        "identity": identity,
        "valid_questions": valid_questions,
        "native_full96_fractional_R3_recomputed": native,
        "frozen_native_fractional_R3": FROZEN_NATIVE_FRAC_R3,
        "absolute_reproduction_error": reproduction_error,
        "frozen_native_reproduction_pass": reproducible,
        "hard_negative_rescue": resc,
        "hard_negative_margins": margins,
        "verdict": verdict,
        "decision_features": {"coarse_fine_signature": bool(coarse_fine_signature)},
        "band_summary": bdf.to_dict("records"),
    }
    (out / "locomo_mechanism_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    def pct(x): return f"{100*x:.3f}%"
    md = [
        "# V52 LoCoMo SIGN Mechanism Replication — Post-hoc Exploratory Checkpoint",
        "",
        f"Verdict: `{verdict}`",
        "",
        "## Provenance",
        f"- Dataset SHA-256: `{DATASET_SHA256}` (exact byte verification PASS)",
        f"- Audit manifest SHA-256: `{AUDIT_MANIFEST_SHA256}` (20 exact files PASS)",
        f"- Frozen 4D script SHA-256 reference: `{FROZEN_SCRIPT_SHA256}`",
        f"- Audit-clean evidence-valid denominator: {valid_questions}",
        f"- Frozen Full96 native R@3 reproduction: {pct(native)} vs frozen {pct(FROZEN_NATIVE_FRAC_R3)}; abs error={reproduction_error:.3e}; {'PASS' if reproducible else 'FAIL'}",
        "",
        "## Spectrum diagnostics",
        "| band | Fractional R@3 | same-sign gold−nongold advantage | pairwise discrimination | unique-code | mean |corr| |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, rr in bdf.iterrows():
        adv = rr.get("gold_minus_nongold_same_sign_advantage", np.nan)
        disc = rr.get("pairwise_gold_vs_nongold_discrimination", np.nan)
        md.append(f"| {rr.band} | {pct(rr.fractional_R3)} | {adv:.4f} | {disc:.4f} | {rr.unique_code_fraction_doc_weighted:.4f} | {rr.mean_abs_bit_correlation_doc_weighted:.4f} |")
    md += [
        "", "## Hard-negative rescue",
        f"- High32 wrong/tie → Full96 correct: {pct(resc['high_wrong_or_tie_to_full_rescue'])}",
        f"- High32 correct → Full96 wrong/tie: {pct(resc['high_correct_to_full_degrade'])}",
        f"- High32 wrong/tie → High+Mid correct: {pct(resc['high_wrong_or_tie_to_highmid_rescue'])}",
        f"- High32 wrong/tie → High+Low correct: {pct(resc['high_wrong_or_tie_to_highlow_rescue'])}",
        f"- High+Mid wrong/tie → Full96 correct: {pct(resc['highmid_wrong_or_tie_to_full_rescue'])}",
        "", "## Hard-negative margins",
        f"- Native SIGN positive-margin questions: {pct(sign_pos)}",
        f"- Centered cosine positive-margin questions: {pct(cos_pos)}",
        f"- Centered cosine Fractional R@3 (post-hoc reference): {pct(margins['centered_cosine_fractional_R3'])}",
        "", "## Epistemic status",
        "This analysis is post-hoc and exploratory. It tests whether the LongMemEval coarse→fine / tail-rescue signature transfers to LoCoMo. It is not preregistered, not a population p-value claim, and does not establish the causal mediator. The next causal experiment must be preregistered before outcome access.",
    ]
    (out / "RESEARCH_CHECKPOINT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("mechanism_outputs"))
    args = ap.parse_args()
    run(args.out)
