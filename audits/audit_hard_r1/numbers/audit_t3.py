# Auditor's own T3 recomputation. Document side rebuilt from raw PerLTQA mem data
# via the frozen recipe (read-only import of build_items/fit_archive steps is avoided;
# recipe reimplemented here from the read contract: word TF-IDF(1,2)+char_wb(3,5)+
# latent32 SVD(5101), concat, archive SVD(5204), L2 norm, mean-center).
# Query texts re-derived by reimplementing the deterministic qid scheme; every
# (qid->gold) mapping is cross-checked against cache_q_eval.pkl before scoring.
# SVD, sign coding, scoring, metrics are the auditor's own. Nothing written to sources.
import json, sys, ast, hashlib
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
BASE = f"{W}/bench3/PerLTQA/Dataset/en_v2"
SALT = "top10-r1"

def my_top10(scores, arch, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{SALT}|{arch}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])

def my_metrics(S, gold, arch):
    hit = fr3 = 0.0
    n = S.shape[0]
    for r in range(n):
        top = my_top10(S[r], arch, 10)
        g = set(int(x) for x in gold[r])
        hit += 1.0 if (g & set(int(x) for x in top.tolist())) else 0.0
        fr3 += len(g & set(int(x) for x in top[:3].tolist())) / len(g) if g else 0.0
    return 100 * hit / n, 100 * fr3 / n

def my_arms(C, QC, gold, arch):
    out = {}
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    out["sym"] = my_metrics(QB @ B.T, gold, arch)
    sg = C.std(axis=0, ddof=0)
    nconst = int(np.count_nonzero(sg < 1e-12))
    sg[sg < 1e-12] = 1e-12
    out["qscale"] = my_metrics((QC / sg) @ B.T, gold, arch)
    out["asym"] = my_metrics(QC @ B.T, gold, arch)
    return out, nconst, sg

def main(archives):
    import pickle
    qa = json.load(open(f"{BASE}/perltqa_en_v2.json", encoding="utf-8"))
    mem = json.load(open(f"{BASE}/perltmem_en_v2.json", encoding="utf-8"))
    qachars = [list(e.keys())[0] for e in qa]
    BANKED = sorted([c for c in qachars if c in mem])
    ORD = {c: i for i, c in enumerate(BANKED)}
    SEC = {'profile': 'PRF', 'social_relationship': 'SOC', 'events': 'EVE', 'dialogues': 'DLG'}
    arch_cache = pickle.load(open(f"{W}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
    q_cache = pickle.load(open(f"{W}/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))

    def parse_social(v):
        return v if isinstance(v, dict) else ast.literal_eval(v)

    def build_texts(char):
        b = mem[char]
        texts = []
        for f, v in b['profile'].items():
            texts.append(f'[profile] {f}: {v}')
        texts.append(f"[profile_description] {b['profile_description']}")
        soc = parse_social(b['social_relationship'])
        for k in sorted(soc.keys()):
            e = soc[k]
            extra = ''.join(f'; {kk}: {vv}' for kk, vv in sorted(e.items())
                            if kk not in ('Supporting Characters', 'Relationship', 'Description'))
            texts.append(f"[social {k}] {e.get('Supporting Characters','')} ({e.get('Relationship','')}): {e.get('Description','')}{extra}")
        for k in sorted(b['events'].keys()):
            ev = b['events'][k]
            content = ev['content'] if isinstance(ev, dict) and 'content' in ev else (ev if isinstance(ev, str) else json.dumps(ev))
            texts.append(f'[event {k}] {content}')
        for k in sorted(b['dialogues'].keys()):
            for ts in sorted(b['dialogues'][k]['contents'].keys()):
                for turn in b['dialogues'][k]['contents'][ts]:
                    texts.append(f'[dialogue {k} @ {ts}] {turn}')
        return texts

    def refkey(s):
        s = s.strip()
        if s.startswith('['):
            return [str(x) for x in ast.literal_eval(s)]
        return [s]

    out = {}
    for char in archives:
        texts = build_texts(char)
        n = len(texts)
        assert n == arch_cache[char]['N'], f"N mismatch {char}: {n} vs {arch_cache[char]['N']}"
        # --- frozen feature recipe (own run) ---
        wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
        cv = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
        Xw = normalize(wv.fit_transform(texts)); Xc = normalize(cv.fit_transform(texts))
        d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
        svd32 = TruncatedSVD(n_components=d, random_state=5101)
        Xl = normalize(svd32.fit_transform(Xw))
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format='csr')
        # --- rebuild qrecs (own) and validate gold vs cache ---
        b = mem[char]
        prof_keys = list(b['profile'].keys())
        soc_keys = sorted(parse_social(b['social_relationship']).keys())
        ev_keys = sorted(b['events'].keys())
        base = len(prof_keys) + 1 + len(soc_keys) + len(ev_keys)
        dlg_turns = {}
        t = 0
        for k in sorted(b['dialogues'].keys()):
            idxs = []
            for ts in sorted(b['dialogues'][k]['contents'].keys()):
                for turn in b['dialogues'][k]['contents'][ts]:
                    idxs.append(base + t); t += 1
            dlg_turns[k] = idxs
        turn_text = {i: tx for i, tx in enumerate(texts)}
        A_soc = {k: len(prof_keys) + 1 + i for i, k in enumerate(soc_keys)}
        A_ev = {k: len(prof_keys) + 1 + len(soc_keys) + i for i, k in enumerate(ev_keys)}
        A_prof = {f: i for i, f in enumerate(prof_keys)}
        qrecs = []
        for entry in qa:
            if char not in entry:
                continue
            dd = entry[char]
            for qi, qq in enumerate(dd['profile']):
                rk = refkey(qq['Reference Memory'])[0]
                g = [A_prof[rk]] if rk in A_prof else []
                qrecs.append((f'PQ{ORD[char]:03d}_PRF_q{qi:03d}', str(qq['Question']), g))
            for s in ['social_relationship', 'events', 'dialogues']:
                qi = 0
                for g_ in dd[s]:
                    k = list(g_.keys())[0]
                    for qq in list(g_.values())[0]:
                        qid = f'PQ{ORD[char]:03d}_{SEC[s]}_q{qi:03d}'; qi += 1
                        if s == 'social_relationship':
                            g = [A_soc[k]] if k in A_soc else []
                        elif s == 'events':
                            g = [A_ev[k]] if k in A_ev else []
                        else:
                            if k not in dlg_turns:
                                g = []
                            else:
                                idxs = dlg_turns[k]
                                ancs = [(list(x.keys())[0], list(x.values())[0]) for x in qq['Memory Anchors']]
                                num = [x for x, sp in ancs if sp != [-1, -1]]
                                hit = [i for i in idxs if any(x.lower() in turn_text[i].lower() for x in num)] if num else []
                                g = hit if hit else list(idxs)
                        qrecs.append((qid, str(qq['Question']), g))
        qrecs = [(qid, qt, g) for (qid, qt, g) in qrecs if g]
        # validate against cache
        cache_qids = {qid: v for qid, v in q_cache.items() if v.get('char') == char}
        mine = {qid: sorted(g) for qid, _, g in qrecs}
        theirs = {qid: sorted(int(x) for x in v['gold']) for qid, v in cache_qids.items()}
        gold_ok = (mine == theirs)
        print(f"{char}: N={n} my_q={len(mine)} cache_q={len(theirs)} gold_match={gold_ok}", flush=True)
        if not gold_ok:
            only_m = sorted(set(mine) - set(theirs))[:5]
            only_t = sorted(set(theirs) - set(mine))[:5]
            print(f"  qid diff mine-not-theirs={only_m} theirs-not-mine={only_t}", flush=True)
            mism = [qid for qid in mine if qid in theirs and mine[qid] != theirs[qid]][:3]
            print(f"  gold mismatches sample={[(m_, mine[m_], theirs[m_]) for m_ in mism]}", flush=True)
            out[char] = {"gold_match": False}
            continue
        questions = [qt for _, qt, _ in qrecs]
        gold = [g for _, _, g in qrecs]
        Qw = normalize(wv.transform(questions)); Qc = normalize(cv.transform(questions))
        Ql = normalize(svd32.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format='csr')
        arms = {}
        gate = None
        const = {}
        for k in [96, 192, 384]:
            k_eff = min(k, n - 1, min(Z.shape) - 1)
            svd = TruncatedSVD(n_components=k_eff, random_state=5204)
            Y = normalize(svd.fit_transform(Z))
            mu = Y.mean(axis=0, keepdims=True)
            C = (Y - mu).astype(np.float64)
            QY = normalize(svd.transform(Zq))
            QC = (QY - mu).astype(np.float64)
            if k == 96:
                Cc = arch_cache[char]['C']
                gate = {"differing_bits": int(np.count_nonzero((C >= 0) != (Cc >= 0))), "n_bits": int(C.size)}
            scored, nconst, _ = my_arms(C, QC, gold, char)
            const[k] = {"k_eff": k_eff, "nconst": nconst}
            for sc, (h, f) in scored.items():
                arms[f"k{k}/{sc}"] = {"hit10": h, "fr3": f, "k_eff": k_eff}
            print(f"  k={k}(eff {k_eff}) nconst={nconst} " +
                  " ".join(f"{sc}=({v[0]:.2f},{v[1]:.2f})" for sc, v in scored.items()), flush=True)
        print(f"  gate96: {gate} (cache N={arch_cache[char]['N']})", flush=True)
        out[char] = {"gold_match": True, "n": n, "nq": len(qrecs), "gate": gate, "const": const, "arms": arms}
    tag = "_".join(a.split()[0] for a in archives)
    json.dump(out, open(f"audit_t3_out_{tag}.json", "w", encoding="utf-8"), indent=1)
    print(f"WROTE audit_t3_out_{tag}.json")

if __name__ == "__main__":
    main(sys.argv[1:])
