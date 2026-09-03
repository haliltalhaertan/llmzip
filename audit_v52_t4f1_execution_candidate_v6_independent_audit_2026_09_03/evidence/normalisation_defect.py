#!/usr/bin/env python3
"""Isolates the interaction between the gate's normalise() and its token lookarounds.

normalise() strips ALL whitespace, so a token is concatenated with its neighbouring
words. The patterns then require the adjacent character not to be a hex character.
Any preceding word ending in [0-9a-f], or following word starting with [0-9a-f],
silently suppresses the match.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

def normalise(t: str) -> str: return re.sub(r"\s+", "", t).casefold()
PATTERN = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
TOKEN = "a" * 63 + "b"

prefixes = ["digest ", "probe ", "V4 ", "the ", "sha256 ", "canary ", "is "]
suffixes = ["\n", " and the rest\n", " for the cohort\n", " is pinned\n", " (pinned)\n"]
cases = []
for p in prefixes:
    for s in suffixes:
        seen = bool(PATTERN.search(normalise(p + TOKEN + s)))
        cases.append({"prefix": p, "suffix": s, "token_seen_by_gate": seen,
                      "prev_char_after_normalise": normalise(p)[-1:] if p.strip() else "",
                      "next_char_after_normalise": normalise(s)[:1]})
missed = [c for c in cases if not c["token_seen_by_gate"]]
out = {
    "token": TOKEN,
    "cases_tested": len(cases),
    "cases_where_token_is_invisible": len(missed),
    "invisible_fraction": round(len(missed) / len(cases), 3),
    "explanation": ("normalise() deletes the whitespace that the lookarounds rely on to establish "
                    "token boundaries; the adjacent word's character then suppresses the match. "
                    "No error is raised and payloads_swept is unaffected."),
    "cases": cases,
}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(f"{len(missed)}/{len(cases)} ordinary prose contexts make the token invisible to the gate")
