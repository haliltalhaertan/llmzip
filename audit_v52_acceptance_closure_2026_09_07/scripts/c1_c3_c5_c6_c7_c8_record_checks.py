"""Cold-start closure audit of the V52 coordinate-scale acceptance record.

Gates C1, C3, C5, C6, C7, C8. Every value is derived from RAW GIT BLOBS
(`git cat-file -p`), never from the checked-out working tree, except where the
blob-vs-checkout divergence is itself the measurement.

Every check carries a negative control that is shown actually failing.

Run from the repository root:
    python <this file> <output.json>
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path

MAIN = "ed2b2f74347da6be68beae2c22d5c3d22992f1a3"
RESEARCH = "0c9916bd7786d7ddb332f5b6da3d96d61a6223f0"
L057 = "37a39a4"      # first commit of the audited range on main
L056_BASE = "a0944522"  # parent of the audited range
RESEARCH_BASE = "591e5d0"

OUT = Path(sys.argv[1])
R = {"gates": {}, "negative_controls": {}, "meta": {}}


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(" ".join(args) + "\n" + p.stderr.decode("utf8", "replace"))
    return p.stdout if binary else p.stdout.decode("utf8", "replace")


def blob(commit, path):
    return git("show", f"{commit}:{path}", binary=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def text(commit, path):
    return blob(commit, path).decode("utf8")


R["meta"]["python"] = sys.version
R["meta"]["main_commit"] = git("rev-parse", MAIN).strip()
R["meta"]["research_commit"] = git("rev-parse", RESEARCH).strip()
R["meta"]["core_autocrlf"] = git("config", "--get", "core.autocrlf").strip()

# ============================================================ C1 — identity ===
DOCS = [
    (MAIN, "docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md",
     "docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md.sha256",
     "8ba55a616c33f23fd3e8cc6daf4565830b7e993f4749e8440c9c62e082d31d3f"),
    (MAIN, "docs/v52/V52_ACCEPTANCE_DECISION_CLARIFICATION_2026-09-07.md",
     "docs/v52/V52_ACCEPTANCE_DECISION_CLARIFICATION_2026-09-07.md.sha256", None),
    (MAIN, "docs/v52/V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07.md",
     "docs/v52/V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07.md.sha256", None),
    (MAIN, "prompts/V52_ACCEPTANCE_CLOSURE_NARROW_AUDIT_PROMPT_2026-09-07.md",
     "prompts/V52_ACCEPTANCE_CLOSURE_NARROW_AUDIT_PROMPT_2026-09-07.md.sha256",
     "c6a0da6a3076793b5b3cc0b0d0796b3fe30a1a21644e539c3b4f9a0bd1649faf"),
    (RESEARCH, "research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md",
     "research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md.sha256",
     "4f70340774624b0bcdc4e519f6c42f0733b549a2b065a3a4e0b939c5aa5f22dc"),
    (RESEARCH, "research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md",
     None, "de6672119010bf561179014748e21836bff5c0ebf6efa10379213c59de5203fe"),
]

state = json.loads(text(MAIN, "ops/CURRENT_STATE.json"))
state_raw = text(MAIN, "ops/CURRENT_STATE.json")

c1 = []
for commit, path, sidecar, prompt_expected in DOCS:
    b = blob(commit, path)
    h = sha(b)
    row = {"commit": commit[:8], "path": path, "blob_sha256": h, "bytes": len(b),
           "git_blob_id": git("rev-parse", f"{commit}:{path}").strip()}
    if sidecar:
        sc = text(commit, sidecar).strip()
        row["sidecar_raw"] = sc
        row["sidecar_hash"] = sc.split()[0]
        row["sidecar_names_basename"] = sc.split()[-1].lstrip("*") == Path(path).name
        row["sidecar_matches_blob"] = row["sidecar_hash"] == h
    if prompt_expected:
        row["prompt_declared_value"] = prompt_expected
        row["matches_declared"] = prompt_expected == h
    row["appears_in_state_file"] = h in state_raw
    # blob vs checkout, reported separately as the prompt requires
    wt = Path(path)
    if wt.is_file():
        row["checkout_sha256"] = sha(wt.read_bytes())
        row["checkout_equals_blob"] = row["checkout_sha256"] == h
    c1.append(row)
R["gates"]["C1"] = c1

# NC: a one-byte perturbation of the decision document must break the sidecar match
b = blob(MAIN, "docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md")
R["negative_controls"]["NC_C1_sidecar_can_fail"] = {
    "perturbation": "append one newline byte",
    "perturbed_sha256": sha(b + b"\n"),
    "still_matches_sidecar": sha(b + b"\n") == "8ba55a616c33f23fd3e8cc6daf4565830b7e993f4749e8440c9c62e082d31d3f",
    "control_passes_iff_false": True,
}

# ============================================= C3 — deviation record accuracy ==
prereg = text(RESEARCH, "research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md")
decision = text(MAIN, "docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md")


def unquote(block):
    """Strip a markdown blockquote back to the source text it claims to quote."""
    lines = []
    for ln in block.split("\n"):
        ln = ln[2:] if ln.startswith("> ") else (ln[1:] if ln == ">" else ln)
        lines.append(ln)
    return "\n".join(lines)


def quoted_blocks(doc):
    out, cur = [], []
    for ln in doc.split("\n"):
        if ln.startswith(">"):
            cur.append(ln)
        elif cur:
            out.append("\n".join(cur)); cur = []
    if cur:
        out.append("\n".join(cur))
    return out


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def norm_dashes(s):
    return s.replace("—", "-").replace("–", "-").replace("’", "'")


CLAIMED = {
    "s7_secondary": "**Secondary:** the interaction on the fraction scale, `I_frac = frac_full - frac_block`. It is\nsecondary precisely because the pilot showed it nearly vanishes once the floor effect is removed.",
    "s9_positive": "**Positive (`I` large).** Supports that relative coordinate scale *participates* in the damage from\ncross-band mixing.",
}
c3 = {"quotes": {}}
for name, claimed in CLAIMED.items():
    present_in_decision = claimed in decision or ("> " + claimed.replace("\n", "\n> ")) in decision
    c3["quotes"][name] = {
        "claimed_text": claimed,
        "byte_exact_in_preregistration": claimed in prereg,
        "present_as_blockquote_in_decision": present_in_decision,
        "whitespace_normalised_in_preregistration": norm_ws(claimed) in norm_ws(prereg),
    }

# the section 7 estimand block, quoted in decision 2.1 — check verbatim fidelity
s7_quote = None
for blk in quoted_blocks(decision):
    if "frac_full  =" in blk:
        s7_quote = unquote(blk)
        break
c3["s7_estimand_quote"] = {"found": s7_quote is not None}
if s7_quote:
    frags = [f for f in s7_quote.split("\n") if f.strip() and not f.strip().startswith("```")]
    detail = []
    for f in frags:
        detail.append({
            "fragment": f[:110],
            "byte_exact_in_prereg": f in prereg,
            "exact_after_dash_and_ws_normalisation": norm_ws(norm_dashes(f)) in norm_ws(norm_dashes(prereg)),
            "exact_after_removing_bold_markers": norm_ws(norm_dashes(f.replace("**", ""))) in norm_ws(norm_dashes(prereg.replace("**", ""))),
        })
    c3["s7_estimand_quote"]["fragments"] = detail
    c3["s7_estimand_quote"]["all_fragments_byte_exact"] = all(d["byte_exact_in_prereg"] for d in detail)
    c3["s7_estimand_quote"]["all_exact_modulo_dashes_and_bold"] = all(
        d["exact_after_removing_bold_markers"] for d in detail)

# defect 1 — section 7 demotes I_frac, section 9 attaches the licence to it
c3["defect_1_demotion_and_licence"] = {
    "s7_calls_interaction_secondary": "**Secondary:** the interaction on the fraction scale" in prereg,
    "s7_calls_frac_arm_primary": "It is the primary" in prereg and "quantity, reported **per arm**" in prereg,
    "s9_positive_clause_present": "**Positive (`I` large).**" in prereg,
    "s9_clause_names_I_not_I_frac": "**Positive (`I` large).**" in prereg and "Positive (`I_frac`" not in prereg,
    "note": ("section 9 writes `I`, not `I_frac`. The identification is an inference the record makes "
             "silently; it is supported because section 7 bars the percentage-point interaction from "
             "carrying any verdict, leaving I_frac as the only interaction that can."),
}

# defect 2 — no threshold, band or direction test for I_frac anywhere
ifrac_lines = [(i + 1, ln) for i, ln in enumerate(prereg.split("\n"))
               if "I_frac" in ln or re.search(r"`I`", ln)]
band_numbers_near_ifrac = [(n, ln) for n, ln in ifrac_lines if re.search(r"\d\.\d{2}", ln)]
c3["defect_2_no_operational_threshold"] = {
    "all_mentions_of_I_or_I_frac": [{"line": n, "text": ln.strip()[:220]} for n, ln in ifrac_lines],
    "mentions_carrying_a_two_decimal_number": [{"line": n, "text": ln.strip()[:220]} for n, ln in band_numbers_near_ifrac],
    "string_large_is_defined": bool(re.search(r"`?I(_frac)?`?\s*(>=|>|≥)\s*[0-9]", prereg)),
    "frac_arm_bands_present": "`frac >= 0.70`" in prereg and "`frac <= 0.20`" in prereg,
    "auditor_reading": ("no numeric band, threshold or operational direction test for I_frac exists "
                        "anywhere in the preregistration. Section 9 does supply a QUALITATIVE "
                        "dichotomy (`I` large vs `I` approximately 0), which is a direction "
                        "distinction without an operational cut."),
}
c3["record_selects_no_clause"] = {
    "decision_states_no_clause_selected": "**No clause is selected by this decision.**" in decision,
    "register_states_not_adjudicated": "**Not adjudicated.**" in text(RESEARCH, "research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md"),
}
R["gates"]["C3"] = c3

# NC: a quote that is NOT in the preregistration must be reported as not-exact
R["negative_controls"]["NC_C3_quote_check_can_fail"] = {
    "fake_quote": "**Secondary:** the interaction on the fraction scale, `I_frac = frac_full + frac_block`.",
    "byte_exact_in_preregistration": "**Secondary:** the interaction on the fraction scale, `I_frac = frac_full + frac_block`." in prereg,
    "control_passes_iff_false": True,
}
R["negative_controls"]["NC_C3_threshold_search_can_fail"] = {
    "probe": "search the same document for the frac_arm band that DOES exist",
    "found_frac_band": "`frac >= 0.70`" in prereg,
    "control_passes_iff_true": True,
    "meaning": "the search finds a real band when one exists, so its silence on I_frac is evidence",
}

# ========================= C5 — provenance versus recomputation, honestly split =
EV_A = "docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md"
EV_B = "adapters/longmemeval_v52_adapter_v2.py"
EV_COMMIT = "e97fbe052306e9042e994d2e83031c6e8edd6b3d"
a_b = blob(EV_COMMIT, EV_A)
b_b = blob(EV_COMMIT, EV_B)
base_src = text(RESEARCH, "research/v52/longmemeval_spectral_band_haar_causal.py")
m = re.search(r'A2_SHA256\s*=\s*"([0-9a-f]{64})"', base_src)
DECISIVE = ("Dependency graph: 1 component(s), largest=470/470. question-level bootstrap cannot be "
            "interpreted as independent underlying-memory population inference.")
clarif = text(MAIN, "docs/v52/V52_ACCEPTANCE_DECISION_CLARIFICATION_2026-09-07.md")

c5 = {
    "evidence_A": {
        "path": EV_A, "commit": EV_COMMIT,
        "git_blob_id": git("rev-parse", f"{EV_COMMIT}:{EV_A}").strip(),
        "declared_blob_id": "36505bcffd7d1ce983a71c5ec4d000a2c94ae1ac",
        "sha256": sha(a_b), "declared_sha256": "930db8e923652319f169ba0701febdc07a8cebc49b21c978960384682b37bef1",
        "bytes": len(a_b), "declared_bytes": 744,
        "decisive_sentence_present_verbatim": DECISIVE in norm_ws(a_b.decode("utf8")) or DECISIVE in a_b.decode("utf8"),
        "decisive_sentence_present_after_ws_norm": norm_ws(DECISIVE) in norm_ws(a_b.decode("utf8")),
    },
    "evidence_B": {
        "path": EV_B, "commit": EV_COMMIT,
        "git_blob_id": git("rev-parse", f"{EV_COMMIT}:{EV_B}").strip(),
        "declared_blob_id": "aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1",
        "sha256": sha(b_b), "declared_sha256": "643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218",
        "states_same_finding": "1 component" in b_b.decode("utf8") or "largest=470/470" in b_b.decode("utf8"),
        "finding_lines": [ln.strip()[:200] for ln in b_b.decode("utf8").split("\n")
                          if "component" in ln.lower() and "470" in ln][:5],
    },
    "A2_SHA256_pin": {
        "source": "research/v52/longmemeval_spectral_band_haar_causal.py",
        "source_blob_id": git("rev-parse", f"{RESEARCH}:research/v52/longmemeval_spectral_band_haar_causal.py").strip(),
        "declared_source_blob": "79dd4a5ec462102da5d82530088a4b7e89bef437",
        "pinned_value": m.group(1) if m else None,
        "equals_evidence_B_sha256": bool(m) and m.group(1) == sha(b_b),
    },
}
c5["evidence_A"]["blob_id_matches"] = c5["evidence_A"]["git_blob_id"] == c5["evidence_A"]["declared_blob_id"]
c5["evidence_A"]["sha_matches"] = c5["evidence_A"]["sha256"] == c5["evidence_A"]["declared_sha256"]
c5["evidence_A"]["bytes_match"] = c5["evidence_A"]["bytes"] == 744
c5["evidence_B"]["blob_id_matches"] = c5["evidence_B"]["git_blob_id"] == c5["evidence_B"]["declared_blob_id"]
c5["evidence_B"]["sha_matches"] = c5["evidence_B"]["sha256"] == c5["evidence_B"]["declared_sha256"]

# does anything in the record claim the graph was RECOMPUTED in this stage?
RECOMP_PAT = re.compile(
    r"(recomputed|re-computed|recount|re-count|rebuil|re-deriv|rederiv|recalculat)[a-z]*[^.\n]{0,120}"
    r"(dependency graph|component|470|session[- ]sharing|haystack)", re.I)
REVERSE_PAT = re.compile(
    r"(dependency graph|component structure|components|470)[^.\n]{0,120}"
    r"(recomputed|re-computed|recounted|rebuilt|re-derived|recalculated)", re.I)
scan_targets = {
    "acceptance_decision": decision,
    "clarification_note": clarif,
    "deviation_register": text(RESEARCH, "research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md"),
    "ledger_L057_L060": "\n".join(text(MAIN, "docs/CONTINUITY_LEDGER.md").split("### L-057")[1:]),
    "current_state": state_raw,
}
hits = {}
for k, v in scan_targets.items():
    found = [mm.group(0)[:220] for mm in RECOMP_PAT.finditer(v)] + \
            [mm.group(0)[:220] for mm in REVERSE_PAT.finditer(v)]
    hits[k] = found
c5["recomputation_claim_scan"] = hits
c5["required_citation_label"] = {
    "label": "[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE VERIFIED, NOT RECOMPUTED HERE]",
    "present_in_clarification_note": "INHERITED FROM TASK 3A.1" in clarif and "NOT RECOMPUTED HERE" in clarif,
    "present_in_state_file": "INHERITED FROM TASK 3A.1" in state_raw and "NOT RECOMPUTED HERE" in state_raw,
    "present_in_acceptance_decision": "INHERITED FROM TASK 3A.1" in decision,
    "present_in_deviation_register": "INHERITED FROM TASK 3A.1" in scan_targets["deviation_register"],
    "clarification_states_not_recomputed": "was **not recomputed**" in clarif,
    "clarification_states_inherited": "inherited from the Task 3A.1 stage" in clarif,
    "clarification_states_confirming_is_not_confirming": "Confirming that a file contains a number is not confirming the number." in clarif,
}
R["gates"]["C5"] = c5

R["negative_controls"]["NC_C5_pin_check_can_fail"] = {
    "probe": "compare the A2_SHA256 pin against evidence A's sha256 instead of evidence B's",
    "would_match": bool(m) and m.group(1) == sha(a_b),
    "control_passes_iff_false": True,
}
R["negative_controls"]["NC_C5_recomputation_scan_can_fire"] = {
    "probe": "run the same regex over a synthetic sentence that DOES claim recomputation",
    "synthetic": "In this stage we recomputed the dependency graph and recounted its components.",
    "fires": bool(RECOMP_PAT.search("In this stage we recomputed the dependency graph and recounted its components.")),
    "control_passes_iff_true": True,
}

# ==================================== C6 — current-state consistency ===========
ledger = text(MAIN, "docs/CONTINUITY_LEDGER.md")
entries = re.findall(r"^### (L-\d+)", ledger, re.M)
newest = max(entries, key=lambda e: int(e.split("-")[1]))
c6 = {
    "state_ledger_entry": state.get("ledger_entry"),
    "ledger_entries_found": entries[-6:],
    "newest_entry_by_number": newest,
    "last_entry_in_file_order": entries[-1],
    "state_matches_newest": state.get("ledger_entry") == newest == entries[-1],
    "state_id": state.get("state_id"),
    "task_4f1_run": state.get("task_state", {}).get("task_4f1_run"),
    "outcome_access": state.get("task_state", {}).get("retrieval_quality_outcome_access"),
}
# surviving "awaiting adjudication" text
aw = [ln.strip()[:200] for ln in state_raw.split("\n") if re.search(r"awaiting.{0,30}adjudicat", ln, re.I)]
c6["awaiting_adjudication_in_state_file"] = aw
c6["awaiting_adjudication_in_decision"] = [ln.strip()[:200] for ln in decision.split("\n")
                                           if re.search(r"awaiting.{0,30}adjudicat", ln, re.I)]

# label sets
LBL = re.compile(r"\[[A-Z][A-Z0-9 ,/()—–.:%'-]{15,200}\]")


def labels(doc):
    return sorted({norm_ws(norm_dashes(x)) for x in LBL.findall(doc)})


STAGE_LABEL_KEYS = ("LOCOMO COMPUTATIONAL REPRODUCTION", "COMPARATIVE MECHANISM CLAIM",
                    "UNCERTAINTY ANALYSIS IS POST-OUTCOME", "NOT INDEPENDENTLY AUDITED",
                    "MOST / PARTIAL")


def stage_labels(doc):
    return sorted(l for l in labels(doc) if any(k in l for k in STAGE_LABEL_KEYS))


ls_state, ls_dec, ls_reg = (stage_labels(state_raw), stage_labels(decision),
                            stage_labels(scan_targets["deviation_register"]))
c6["label_sets"] = {
    "state_file": ls_state, "acceptance_decision": ls_dec, "deviation_register": ls_reg,
    "state_equals_decision": set(ls_state) == set(ls_dec),
    "decision_equals_register": set(ls_dec) == set(ls_reg),
    "in_decision_not_in_register": sorted(set(ls_dec) - set(ls_reg)),
    "in_register_not_in_decision": sorted(set(ls_reg) - set(ls_dec)),
}
# accepted-conclusion text consistency between decision and state file
def accepted_text(doc):
    mm = re.search(r"On a fixed pipeline.*?(corpora\.)", doc, re.S)
    return norm_ws(norm_dashes(mm.group(0).replace(">", ""))) if mm else None


c6["accepted_conclusion_text"] = {
    "decision": accepted_text(decision),
    "state_file": accepted_text(state_raw),
    "identical": accepted_text(decision) == accepted_text(state_raw),
}
R["gates"]["C6"] = c6
R["negative_controls"]["NC_C6_newest_entry_check_can_fail"] = {
    "probe": "assert the state file points at L-055 instead of the newest entry",
    "would_pass": "L-055" == newest,
    "control_passes_iff_false": True,
}

# ========================================= C7 — additivity ====================
FROZEN_PAT = re.compile(
    r"(SEAL|seal)|PREREG|CHECKPOINT|prereg|checkpoint|scale_outputs|task4f1|"
    r"^audit_|^task4f1_|^remediation_|adapters/", re.M)
main_diff = git("diff", "--name-status", L056_BASE, MAIN).strip().split("\n")
res_diff = git("diff", "--name-status", RESEARCH_BASE, RESEARCH).strip().split("\n")


def classify(lines):
    out = []
    for ln in lines:
        if not ln.strip():
            continue
        status, path = ln.split("\t", 1)
        out.append({"status": status, "path": path,
                    "is_addition": status.startswith("A"),
                    "touches_frozen_namespace": bool(FROZEN_PAT.search(path))})
    return out


c7 = {
    "main_range": f"{L056_BASE}..{MAIN[:8]}",
    "main_commits": [l for l in git("log", "--format=%h %s", f"{L056_BASE}..{MAIN}").strip().split("\n")],
    "main_changes": classify(main_diff),
    "research_range": f"{RESEARCH_BASE}..{RESEARCH[:8]}",
    "research_commits": [l for l in git("log", "--format=%h %s", f"{RESEARCH_BASE}..{RESEARCH}").strip().split("\n")],
    "research_changes": classify(res_diff),
}
c7["non_addition_paths_on_main"] = [c["path"] for c in c7["main_changes"] if not c["is_addition"]]
c7["non_addition_paths_on_research"] = [c["path"] for c in c7["research_changes"] if not c["is_addition"]]
c7["any_frozen_namespace_touched"] = sorted(
    {c["path"] for c in c7["main_changes"] + c7["research_changes"] if c["touches_frozen_namespace"]})
# register D1/D2 still stale at the research tip
reg = scan_targets["deviation_register"]
c7["register_D1_D2_left_stale"] = {
    "D1_row": [ln for ln in reg.split("\n") if ln.startswith("| D1 ")],
    "D2_row": [ln for ln in reg.split("\n") if ln.startswith("| D2 ")],
    "research_tip_is_the_register_commit": git("rev-parse", "origin/research/v52-sign-mechanism-locomo-2026-09-04").strip() == RESEARCH,
    "superseded_in_writing_by_decision": "superseded by\n**§2 and §3 of this document**" in decision or "superseded by" in decision,
}
# the one deliberate in-place state change
cf = "cf03007"
c7["in_place_state_change"] = {
    "commit": git("rev-parse", cf).strip()[:12],
    "message": git("log", "-1", "--format=%B", cf).strip(),
    "files": git("diff", "--name-only", cf + "^", cf).strip().split("\n"),
    "own_commit": len(git("diff", "--name-only", cf + "^", cf).strip().split("\n")) == 1,
    "disclosed_in_ledger": "cf03007" in ledger,
    "disclosed_in_audit_prompt": "cf03007" in text(MAIN, "prompts/V52_ACCEPTANCE_CLOSURE_NARROW_AUDIT_PROMPT_2026-09-07.md")
                                 or "stale key rename" in text(MAIN, "prompts/V52_ACCEPTANCE_CLOSURE_NARROW_AUDIT_PROMPT_2026-09-07.md"),
}
# did the rename preserve the conclusion text verbatim, as the commit message claims?
old_state = json.loads(text(cf + "^", "ops/CURRENT_STATE.json"))


def find_key(d, key):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == key:
                return v
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(d, list):
        for v in d:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


old_txt = find_key(old_state, "proposed_narrow_conclusion_not_adopted")
new_txt = find_key(state, "narrow_conclusion_text_ACCEPTED_2026_09_07")
prefix = "On a fixed pipeline"
c7["in_place_state_change"]["old_key_present"] = old_txt is not None
c7["in_place_state_change"]["new_key_present"] = new_txt is not None
if old_txt and new_txt:
    o = old_txt[:old_txt.rindex(". ") + 1]
    n = new_txt[:new_txt.rindex(". ") + 1] if ". " in new_txt else new_txt
    common = old_txt.split("corpora.")[0] + "corpora."
    c7["in_place_state_change"]["body_before_final_sentence_identical"] = new_txt.startswith(common)
    c7["in_place_state_change"]["old_trailing"] = old_txt[len(common):].strip()
    c7["in_place_state_change"]["new_trailing"] = new_txt[len(common):].strip()
    c7["in_place_state_change"]["claim_verbatim_apart_from_trailing_sentence"] = new_txt.startswith(common)
    c7["in_place_state_change"]["old_key_recoverable_only_from_git_history"] = "proposed_narrow_conclusion_not_adopted" not in state_raw
R["gates"]["C7"] = c7
R["negative_controls"]["NC_C7_additivity_check_can_fail"] = {
    "probe": "classify a synthetic modification line as an addition",
    "sample": classify(["M\tresearch/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md"]),
    "detected_as_non_addition_and_frozen": (not classify(["M\tresearch/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md"])[0]["is_addition"]
                                            and classify(["M\tresearch/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md"])[0]["touches_frozen_namespace"]),
    "control_passes_iff_true": True,
}

# ============================================ C8 — boundary ===================
T4F1_PAT = re.compile(r"--mode\s+(run|finalize)|V52_T4F1_AUTH_HMAC_KEY_HEX|run_archives|"
                      r"evaluate_archive|finalize_results", re.I)
all_paths = [c["path"] for c in c7["main_changes"] + c7["research_changes"]]
c8 = {
    "paths_changed_in_range": all_paths,
    "any_path_under_task4f1_namespace": [p for p in all_paths if "task4f1" in p.lower() or "4f1" in p.lower()],
    "any_candidate_or_seal_path": [p for p in all_paths
                                   if re.search(r"candidate|SEAL|seal", p)],
    "any_corpus_or_data_path": [p for p in all_paths if p.startswith("data/") or "corpus" in p.lower()],
    "any_result_package_path": [p for p in all_paths if "scale_outputs" in p or p.endswith(".csv.gz")],
    "t4f1_tokens_in_added_docs": {
        "acceptance_decision": [mm.group(0) for mm in T4F1_PAT.finditer(decision)],
        "clarification_note": [mm.group(0) for mm in T4F1_PAT.finditer(clarif)],
    },
    "state_hard_stops_intact": {
        "task_4f1_run": state["task_state"]["task_4f1_run"],
        "outcome_access": state["task_state"]["retrieval_quality_outcome_access"],
        "hard_stops_mention_mode_run": any("--mode run" in h for h in state.get("hard_stops", [])),
        "hard_stops_mention_hmac": any("V52_T4F1_AUTH_HMAC_KEY_HEX" in h for h in state.get("hard_stops", [])),
    },
    "hard_stops_unchanged_across_range": (json.dumps(old_state.get("hard_stops"))
                                          == json.dumps(state.get("hard_stops"))),
    "hard_stops_unchanged_L056_to_L060": (
        json.dumps(json.loads(text(L056_BASE, "ops/CURRENT_STATE.json")).get("hard_stops"))
        == json.dumps(state.get("hard_stops"))),
    "task_state_4f1_unchanged_L056_to_L060": (
        json.loads(text(L056_BASE, "ops/CURRENT_STATE.json"))["task_state"]["task_4f1_run"]
        == state["task_state"]["task_4f1_run"]),
    "note": ("the only T4F1 tokens in the added documents are inside PROHIBITION sentences; "
             "listed above so the reader can confirm the context."),
}
R["gates"]["C8"] = c8
R["negative_controls"]["NC_C8_boundary_scan_can_fire"] = {
    "synthetic": "python runner.py --mode run --auth $V52_T4F1_AUTH_HMAC_KEY_HEX",
    "fires": bool(T4F1_PAT.search("python runner.py --mode run --auth $V52_T4F1_AUTH_HMAC_KEY_HEX")),
    "control_passes_iff_true": True,
}

OUT.write_text(json.dumps(R, indent=2))
print("wrote", OUT)
print(json.dumps({
    "C1_all_sidecars_match": all(r.get("sidecar_matches_blob", True) for r in c1),
    "C1_all_declared_match": all(r.get("matches_declared", True) for r in c1),
    "C1_checkout_equals_blob": all(r.get("checkout_equals_blob", True) for r in c1),
    "C3_s7_quote_byte_exact": c3["s7_estimand_quote"].get("all_fragments_byte_exact"),
    "C3_s7_quote_exact_modulo_dashes_bold": c3["s7_estimand_quote"].get("all_exact_modulo_dashes_and_bold"),
    "C3_secondary_quote_exact": c3["quotes"]["s7_secondary"]["byte_exact_in_preregistration"],
    "C3_positive_quote_exact": c3["quotes"]["s9_positive"]["byte_exact_in_preregistration"],
    "C3_no_ifrac_threshold": not c3["defect_2_no_operational_threshold"]["string_large_is_defined"],
    "C5_evA_ok": c5["evidence_A"]["blob_id_matches"] and c5["evidence_A"]["sha_matches"] and c5["evidence_A"]["bytes_match"],
    "C5_evB_ok": c5["evidence_B"]["blob_id_matches"] and c5["evidence_B"]["sha_matches"],
    "C5_pin_ok": c5["A2_SHA256_pin"]["equals_evidence_B_sha256"],
    "C5_recomputation_claims": {k: len(v) for k, v in hits.items()},
    "C5_label_present": c5["required_citation_label"]["present_in_clarification_note"],
    "C6_state_matches_newest": c6["state_matches_newest"],
    "C6_awaiting_adjudication_hits": len(c6["awaiting_adjudication_in_state_file"]),
    "C6_state_eq_decision_labels": c6["label_sets"]["state_equals_decision"],
    "C6_decision_eq_register_labels": c6["label_sets"]["decision_equals_register"],
    "C6_accepted_text_identical": c6["accepted_conclusion_text"]["identical"],
    "C7_non_addition_main": c7["non_addition_paths_on_main"],
    "C7_non_addition_research": c7["non_addition_paths_on_research"],
    "C7_frozen_touched": c7["any_frozen_namespace_touched"],
    "C8_t4f1_paths": c8["any_path_under_task4f1_namespace"],
    "C8_hard_stops_unchanged": c8["hard_stops_unchanged_L056_to_L060"],
}, indent=2))
