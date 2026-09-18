"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

DIMENSION LADDER on RealTalk (10 archives, 705 queries, 8944 docs).

External audit 3 established, on LoCoMo/PerLTQA, that the rare-term deficit is a
DIMENSION BUDGET property, not a targeted discard: rare (df=1) columns survive a
rank-96 projection at 0.94x the random-subspace null, and raising k closes the gap
to BM25 monotonically (PerLTQA: -6.98 SIG at 96 -> +0.46 ns at 384).

This runs the same ladder on OUR benchmark, which the auditor did not cover
(RealTalk has no reconstructed-text arm in their run), and answers the question the
programme actually has to answer: WHAT DOES 12 BYTES COST, and where is the knee?

Arms (all rebuilt from raw text through the FROZEN code path; only k changes):
    k in {96, 192, 384, 768} x {sign quantization, full float}
    plus NOPROJ_WORD  : word channel, no SVD at all, cosine  (audit3 found this
                        nearly matches BM25 on LoCoMo -> tests the feature-mix
                        mechanism on RealTalk)
    plus NOPROJ_FULL  : full Z, no SVD, cosine
    plus BM25 reference, with BOTH the coarse tokenizer AND the frozen word-channel
                        tokenizer (audit3: the frozen tokenizer makes BM25 ~3pp
                        BETTER, so quoting only the coarse one handicaps the baseline)

HONEST BYTE ACCOUNTING (the whole point): sign coding costs k/8 bytes per document.
    k= 96 ->  12 B   k=192 -> 24 B   k=384 -> 48 B   k=768 -> 96 B
Float arms cost 4k bytes and are reported ONLY as the no-quantization reference.

BLOCKING FIDELITY GATE: the k=96 sign arm must reproduce the cached production C/QC
bit-exactly and hit the frozen anchors (qscale 49.6454, sym-deterministic 46.5248)
before any other number is written.
"""
import json, math, os, re, sys, time, pickle, importlib.util
from collections import defaultdict

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = f"{W}/drive/v52_t4d_locomo_frozen_cross_benchmark.py"
LIB = f"{W}/top10_comparison_r1/audit/audit_baseline_lib.py"
RT = f"{W}/top10_comparison_r1/data"
CACHE = f"{W}/bench3/runs/b3a_realtalk/rt_repr"

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

frozen = _load("frozen", FROZEN)
lib = _load("lib", LIB)

# COORDINATOR NOTE 2026-09-16: k=768 dropped after the first run timed out.
# Cost: RT06 (1548 docs) alone took 27 min, dominated by the k=768 SVD, and the whole
# run died at 3000 s having written nothing. Justification for dropping rather than
# waiting: the incoming package's independently verified ladder already shows 48 B
# (384 dims) is WORSE than 24 B on 2 of 3 benchmarks, so 96 B is not where the answer is.
# The decision is recorded here rather than silently changing the grid.
KS = [96, 192, 384]
TOKEN = re.compile(r"[a-z0-9]+")
FROZEN_TOKEN = re.compile(r"\b\w\w+\b")

STOP = set("""a about above after again against all am an and any are as at be because been before being
below between both but by could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most my
myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves""".split())

def toks(s, frozen_rule=False):
    if frozen_rule:
        return [w for w in FROZEN_TOKEN.findall((s or "").lower()) if w not in STOP]
    return TOKEN.findall((s or "").lower())

class BM25:
    """Inverted-index BM25. k1/b configurable; audit3 showed textbook params are a
    real choice, not a neutral default, so both settings are reported."""
    def __init__(self, docs, k1=1.2, b=0.75):
        self.k1, self.b = k1, b
        self.N = len(docs)
        self.len = np.array([len(d) for d in docs], dtype=np.float64)
        self.avg = self.len.mean() if self.N else 1.0
        self.post = defaultdict(list)
        for i, d in enumerate(docs):
            tf = defaultdict(int)
            for w in d:
                tf[w] += 1
            for w, c in tf.items():
                self.post[w].append((i, c))
        self.idf = {}
        for w, pl in self.post.items():
            df = len(pl)
            self.idf[w] = math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))

    def score(self, q):
        s = np.zeros(self.N)
        denom_len = self.k1 * (1 - self.b + self.b * self.len / self.avg)
        for w in set(q):
            pl = self.post.get(w)
            if not pl:
                continue
            idf = self.idf[w]
            for i, c in pl:
                s[i] += idf * c * (self.k1 + 1) / (c + denom_len[i])
        return s

def build(texts, questions, k, channels=("LSA", "WORD", "CHAR")):
    """Frozen path; ONLY k and the channel mask vary."""
    payload = frozen.fit_input_payload(list(texts))
    wv, cv, sv, Xw, Xc, Xl = frozen.fit_archive_representation(payload)
    blocks = {"LSA": sparse.csr_matrix(Xl), "WORD": Xw, "CHAR": Xc}
    Z = sparse.hstack([blocks[c] for c in channels], format="csr")
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(sv.transform(Qw))
    qb = {"LSA": sparse.csr_matrix(Ql), "WORD": Qw, "CHAR": Qc}
    Zq = sparse.hstack([qb[c] for c in channels], format="csr")
    if k is None:                                   # no projection at all
        Y = normalize(Z).toarray().astype(np.float64)
        QY = normalize(Zq).toarray().astype(np.float64)
        mu = Y.mean(axis=0, keepdims=True)
        return Y - mu, QY - mu, int(Z.shape[1])
    kk = min(k, min(Z.shape) - 1)
    sv2 = TruncatedSVD(n_components=kk, random_state=frozen.SVD_SEED)
    Y = normalize(sv2.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    QY = normalize(sv2.transform(Zq))
    return (Y - mu).astype(np.float64), (QY - mu).astype(np.float64), kk

def metrics(S, gold, arch):
    hit = fr3 = 0.0
    n = S.shape[0]
    for r in range(n):
        top = lib.det_top10(S[r], arch, 10)
        g = set(gold[r])
        hit += 1.0 if (g & set(top)) else 0.0
        fr3 += len(g & set(top[:3])) / len(g) if g else 0.0
    return 100 * hit / n, 100 * fr3 / n

def score_arms(C, QC, gold, arch):
    """sign (sym + qscale) and float cosine, from the SAME C."""
    out = {}
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    out["sym"] = metrics(QB @ B.T, gold, arch)
    sigma = C.std(axis=0, ddof=0)
    sigma[sigma < 1e-12] = 1e-12
    out["qscale"] = metrics((QC / sigma) @ B.T, gold, arch)
    out["float"] = metrics(normalize(QC) @ normalize(C).T, gold, arch)
    return out

def main():
    res = defaultdict(lambda: defaultdict(list))
    gate = {}
    t0 = time.time()
    # Resumable: the first run died at the 3000 s timeout having written nothing,
    # because everything was held in memory until the end. Now each archive's
    # aggregates are appended as soon as it finishes.
    cache_path = os.path.join(HERE, "LADDER_CACHE.jsonl")
    done = set()
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                done.add(r["archive"])
                gate[r["archive"]] = r["gate"]
                for key, mv in r["arms"].items():
                    res[key]["hit10"].append((mv["hit10"], r["n"]))
                    res[key]["fr3"].append((mv["fr3"], r["n"]))
        print(f"  resumed {len(done)} archives from cache", flush=True)

    for i in range(1, 11):
        aid = f"RT{i:02d}"
        if aid in done:
            continue
        D = json.load(open(f"{RT}/{aid}.json", encoding="utf-8"))
        docs = D["docs"]
        texts = [d["text"] for d in docs]
        row_of = {d["row"]: j for j, d in enumerate(docs)}
        qs = [q for q in D["queries"] if any(g in row_of for g in q.get("gold", []))]
        questions = [q["text"] for q in qs]
        gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]

        # ---- fidelity gate at k=96 ----
        C96, Q96, _ = build(texts, questions, 96)
        cached = pickle.load(open(f"{CACHE}/{aid}.pkl", "rb"))
        Cc = cached["C"]
        nd = int(np.count_nonzero((C96 >= 0) != (Cc >= 0)))
        g = {"differing_bits": nd, "n_bits": int(C96.size),
             "max_abs": float(np.max(np.abs(C96 - Cc)))}
        gate[aid] = g
        arms = {}

        for k in KS:
            C, QC, kk = build(texts, questions, k)
            for sc, (h, f) in score_arms(C, QC, gold, aid).items():
                arms[f"k{k}/{sc}"] = {"hit10": h, "fr3": f}

        for nm, ch in (("NOPROJ_WORD", ("WORD",)), ("NOPROJ_FULL", ("LSA", "WORD", "CHAR"))):
            C, QC, nf = build(texts, questions, None, ch)
            h, f = score_arms(C, QC, gold, aid)["float"]
            arms[f"{nm}/float"] = {"hit10": h, "fr3": f}

        for tag, frz in (("BM25_coarse", False), ("BM25_frozen", True)):
            bm = BM25([toks(t, frz) for t in texts])
            S = np.vstack([bm.score(toks(q, frz)) for q in questions])
            h, f = metrics(S, gold, aid)
            arms[f"{tag}/-"] = {"hit10": h, "fr3": f}

        for key, mv in arms.items():
            res[key]["hit10"].append((mv["hit10"], len(qs)))
            res[key]["fr3"].append((mv["fr3"], len(qs)))
        with open(cache_path, "a", encoding="utf-8") as cf:
            cf.write(json.dumps({"archive": aid, "n": len(qs), "gate": g, "arms": arms}) + "\n")
        print(f"  {aid} done n={len(qs)} gate_diff={nd} {time.time()-t0:.0f}s", flush=True)

    tot_diff = sum(g["differing_bits"] for g in gate.values())
    tot_bits = sum(g["n_bits"] for g in gate.values())
    print(f"\n=== FIDELITY GATE: {tot_diff} differing of {tot_bits} bits ===")

    def agg(key, metric):
        vals = res[key][metric]
        n = sum(v[1] for v in vals)
        return sum(v[0] * v[1] for v in vals) / n, n

    print(f"\n{'arm':22s} {'bytes/doc':>10s} {'Hit@10':>8s} {'FR@3':>8s}")
    out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "gate": {"differing_bits": tot_diff, "n_bits": tot_bits}, "arms": {}}
    for k in KS:
        for sc in ("sym", "qscale", "float"):
            key = f"k{k}/{sc}"
            h, n = agg(key, "hit10"); f, _ = agg(key, "fr3")
            b = k / 8 if sc != "float" else 4 * k
            out["arms"][key] = {"hit10": h, "fr3": f, "bytes_per_doc": b, "n": n}
            print(f"{key:22s} {b:10.0f} {h:8.2f} {f:8.2f}")
    for key in ("NOPROJ_WORD/float", "NOPROJ_FULL/float", "BM25_coarse/-", "BM25_frozen/-"):
        h, n = agg(key, "hit10"); f, _ = agg(key, "fr3")
        out["arms"][key] = {"hit10": h, "fr3": f, "bytes_per_doc": None, "n": n}
        print(f"{key:22s} {'—':>10s} {h:8.2f} {f:8.2f}")

    json.dump(out, open(os.path.join(HERE, "LADDER.json"), "w", encoding="utf-8"), indent=1)
    print(f"\nWROTE LADDER.json  elapsed {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
