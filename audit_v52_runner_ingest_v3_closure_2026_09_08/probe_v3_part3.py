"""Part 3: is the E9 partial-loss slip-through INHERITED, or introduced by v3?"""
import ast, hashlib, sys
from pathlib import Path
CO = Path(sys.argv[1]).resolve()
P3 = CO/"drafts/v52/membership_runner_ingest_v3_2026_09_08"
P2 = CO/"drafts/v52/membership_runner_ingest_v2_2026_09_08"
P1 = CO/"drafts/v52/membership_ingest_v1_2026_09_08"
def fn_src(p, name):
    t = p.read_text(encoding="utf-8"); tree = ast.parse(t); L = t.split("\n")
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return "\n".join(L[n.lineno-1:n.end_lineno])
    return None
for label, p in (("v1", P1/"corpus_ingest.py"), ("v2", P2/"corpus_ingest_v2.py"),
                 ("v3", P3/"corpus_ingest_v3.py")):
    s = fn_src(p, "_normalise_evidence")
    print(f"{label}: _normalise_evidence sha256 = {hashlib.sha256((s or '').encode()).hexdigest()[:32]}  len={len(s or '')}")
sys.path.insert(0, str(P3)); sys.path.insert(0, str(P2))
sys.path.insert(0, str(CO/"drafts/v52/membership_impl_v3_2026_09_07"))
import corpus_ingest_v3 as I3, corpus_ingest_v2 as I2
CASES = {"dict with missing id": [{"dia_id":"D1:0"},{"note":"second gold turn"}],
         "dict with empty id": [{"dia_id":"D1:0"},{"dia_id":""}],
         "dict with null id": [{"dia_id":"D1:0"},{"dia_id":None}],
         "list item not str/dict": ["D1:0", 12345],
         "list item None": ["D1:0", None],
         "free text + real id": "see D1:0 and also the bakery note"}
print("\n%-26s %-28s %s" % ("case", "v2 _normalise_evidence", "v3 _normalise_evidence"))
for k, v in CASES.items():
    print("%-26s %-28s %s" % (k, I2._normalise_evidence(v), I3._normalise_evidence(v)))
print("\nIDENTICAL BEHAVIOUR v2 vs v3:",
      all(I2._normalise_evidence(v) == I3._normalise_evidence(v) for v in CASES.values()))
