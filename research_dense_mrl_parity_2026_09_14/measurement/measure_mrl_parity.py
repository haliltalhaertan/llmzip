# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Beyan edilmis YENIDEN-UYARLAMA (declared re-fit) - YOGUN (dense) KANAL PARITESI.

Leksikal tarafin dondurulmus olcumuyle (measure_spectrum.py, p_B=0.861 f12_B=0.357)
BIREBIR ayni boru hattini yogun gomme uzerinde kosturur:
    satir L2  ->  merkezle  ->  koordinat varyansi (ddof=0)  ->  p = -slope(loglog)

Ayni 15 arsiv, ayni metin insasi, ayni loglog_fit.

SINIR: yalnizca haystack_sessions / haystack_dates / haystack_session_ids okunur.
answer, answer_session_ids, question, question_type alanlarina DOKUNULMAZ.
Hicbir retrieval / recall / gold / siralama / benchmark hesaplanmaz.
"""
from __future__ import annotations
import argparse, csv, json, os, sys, time

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np

LABELS = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"


# --- measure_spectrum.py'den BIREBIR kopyalandi (satir 73-87) -----------------
def loglog_fit(values):
    """ln(v) = alpha - p*ln(i), i=1..n. Donus: (p, r2, n_kullanilan)."""
    v = np.asarray(values, dtype=np.float64)
    mask = v > 0
    v = v[mask]
    idx = np.arange(1, len(values) + 1, dtype=np.float64)[mask]
    x = np.log(idx)
    y = np.log(v)
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(-slope), float(r2), int(len(x))


# --- measure_spectrum.py'den BIREBIR kopyalandi (archive_texts_only) ----------
def archive_texts_only(item):
    sids = item["haystack_session_ids"]
    dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    texts = []
    for sid, date, sess in zip(sids, dates, sessions):
        if not isinstance(sess, list):
            continue
        for turn in sess:
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")
            content = turn.get("content")
            if not isinstance(content, str):
                content = "" if content is None else str(content)
            texts.append("[" + str(date) + "] " + str(role) + ": " + content)
    return texts


MODELS = {
    "arctic-xs": dict(hf="Snowflake/snowflake-arctic-embed-xs",
                      pool="cls", prefix="", remote=False),
    "arctic-m-1.5": dict(hf="Snowflake/snowflake-arctic-embed-m-v1.5",
                         pool="cls", prefix="", remote=False),
    "nomic-1.5": dict(hf="nomic-ai/nomic-embed-text-v1.5",
                      pool="mean", prefix="search_document: ", remote=True),
    # MRL + ikili (binary) kuantalama icin egitilmis; duz BertModel, uzaktan kod YOK.
    "mxbai-large": dict(hf="mixedbread-ai/mxbai-embed-large-v1",
                        pool="cls", prefix="", remote=False),
}


def embed(texts, cfg, tok, model, torch, batch=32, maxlen=512):
    order = np.argsort([-len(t) for t in texts])   # uzunluga gore: verimli batch
    out = np.zeros((len(texts), model.config.hidden_size), dtype=np.float32)
    for i in range(0, len(order), batch):
        idx = order[i:i + batch]
        bt = [cfg["prefix"] + texts[j] for j in idx]
        enc = tok(bt, padding=True, truncation=True, max_length=maxlen,
                  return_tensors="pt")
        with torch.no_grad():
            h = model(**enc).last_hidden_state
        if cfg["pool"] == "cls":
            e = h[:, 0, :]
        else:
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            e = (h * m).sum(1) / m.sum(1).clamp(min=1e-9)
        out[idx] = e.cpu().numpy()
    return out


def geometry_stats(E, ks):
    """Leksikal tarafla ayni hat: satir L2 -> merkezle -> var(ddof=0)."""
    Y = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-12)
    C = (Y - Y.mean(0, keepdims=True)).astype(np.float64)
    v = np.var(C, axis=0)
    vs = np.sort(v)[::-1]
    tot = float(v.sum())
    p_nom, r2_nom, _ = loglog_fit(v)
    p_srt, r2_srt, _ = loglog_fit(vs)
    occ = np.mean(C >= 0, axis=0)
    return {
        "D": int(E.shape[1]),
        "f_nominal": {str(k): float(v[:k].sum() / tot) for k in ks},
        "f_sorted": {str(k): float(vs[:k].sum() / tot) for k in ks},
        "p_nominal": p_nom, "r2_nominal": r2_nom,
        "p_sorted": p_srt, "r2_sorted": r2_srt,
        "n_outside_045_055": int(np.sum((occ < 0.45) | (occ > 0.55))),
        "n_outside_030_070": int(np.sum((occ < 0.30) | (occ > 0.70))),
    }


def isotropic_null(N, D, ks, reps=60, seed=20260914):
    rng = np.random.default_rng(seed)
    acc = [geometry_stats(rng.standard_normal((N, D)).astype(np.float32), ks)
           for _ in range(reps)]
    out = {"f_nominal": {}, "f_sorted": {}}
    for k in ks:
        out["f_nominal"][str(k)] = float(np.mean([a["f_nominal"][str(k)] for a in acc]))
        out["f_sorted"][str(k)] = float(np.mean([a["f_sorted"][str(k)] for a in acc]))
    out["p_nominal"] = float(np.mean([a["p_nominal"] for a in acc]))
    out["p_sorted"] = float(np.mean([a["p_sorted"] for a in acc]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--geometry", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--model", required=True, choices=list(MODELS))
    ap.add_argument("--n-archives", type=int, default=15)
    ap.add_argument("--batch", type=int, default=32)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    cfg = MODELS[a.model]

    with open(a.geometry, encoding="utf-8") as f:
        frozen = list(csv.DictReader(f))
    if not frozen or frozen[0]["question_id"] != "001be529":
        print("GEOMETRI SIRASI BEKLENMEDIK", file=sys.stderr)
        sys.exit(2)
    targets = frozen[: a.n_archives]

    print("Derlem yukleniyor: " + a.corpus, flush=True)
    with open(a.corpus, encoding="utf-8") as f:
        data = json.load(f)
    by_id = {str(x["question_id"]): x for x in data}

    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.set_num_threads(int(os.environ.get("TORCH_THREADS", max(1, (os.cpu_count() or 4) // 2))))
    print("Model yukleniyor: " + cfg["hf"], flush=True)
    tok = AutoTokenizer.from_pretrained(cfg["hf"], trust_remote_code=cfg["remote"])
    model = AutoModel.from_pretrained(cfg["hf"], trust_remote_code=cfg["remote"])
    model.eval()
    D = int(model.config.hidden_size)
    KS = sorted({48, D // 8, 96, D // 2})
    print("D=%d  olculecek k=%s" % (D, KS), flush=True)

    per = []
    for row in targets:
        qid = row["question_id"]
        texts = archive_texts_only(by_id[qid])
        n_exp = int(row["N_archive"])
        ok = (len(texts) == n_exp)
        t0 = time.time()
        E = embed(texts, cfg, tok, model, torch, batch=a.batch)
        st = geometry_stats(E, KS)
        st.update(question_id=qid, N=len(texts), N_expected=n_exp,
                  n_gate_pass=bool(ok), seconds=round(time.time() - t0, 1))
        per.append(st)
        print("%s: N=%d/%d %s | f48nom=%.4f f48srt=%.4f | p_nom=%.4f p_srt=%.4f | %.1fs"
              % (qid, len(texts), n_exp, "GECTI" if ok else "KALDI",
                 st["f_nominal"]["48"], st["f_sorted"]["48"],
                 st["p_nominal"], st["p_sorted"], st["seconds"]), flush=True)

    def med(xs):
        return float(np.median(xs))

    agg = {
        "model": a.model, "hf": cfg["hf"], "pool": cfg["pool"], "D": D,
        "n_archives": len(per),
        "N_gate_all_pass": all(x["n_gate_pass"] for x in per),
        "N_median": med([x["N"] for x in per]),
        "f_nominal": {str(k): med([x["f_nominal"][str(k)] for x in per]) for k in KS},
        "f_sorted": {str(k): med([x["f_sorted"][str(k)] for x in per]) for k in KS},
        "p_nominal": med([x["p_nominal"] for x in per]),
        "r2_nominal": med([x["r2_nominal"] for x in per]),
        "p_sorted": med([x["p_sorted"] for x in per]),
        "r2_sorted": med([x["r2_sorted"] for x in per]),
        "sign_outside_045_055_median": med([x["n_outside_045_055"] for x in per]),
        "sign_outside_030_070_median": med([x["n_outside_030_070"] for x in per]),
    }
    print("\nIzotropik bos hipotez hesaplaniyor...", flush=True)
    agg["isotropic_null"] = isotropic_null(int(agg["N_median"]), D, KS)

    out = {"_labels": LABELS,
           "_notice": "Beyan edilmis yeniden-uyarlama. Retrieval/recall/gold YOK.",
           "aggregate": agg, "per_archive": per}
    p = os.path.join(a.outdir, "MRL_PARITY_" + a.model + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nYAZILDI: " + p)
    print(json.dumps(agg, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
