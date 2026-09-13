#!/usr/bin/env python3
"""Campaign disclosure-label checker (deterministic, stdlib only).

Scans the campaign_2026_09_13 tree, selects in-scope narrative documents by
explicit basename rules, and verifies the exact standalone disclosure banner
appears prominently (within the first 40 lines).

Selection (basename-only, case-insensitive; ext .md/.txt):
  R1        report|analysis|result|summary|finding|audit|dispo|receipt|
            campaign|readme|overview            (independent audit rule)
  NARR_MD   result|review|verification|analysis|certification|summary|
            disposition|inventory               (.md narrative documents)
  TXT_LIKE  receipt|result                      (report-like .txt)
Scope = R1 UNION NARR_MD UNION TXT_LIKE.

Excluded with reason: raw logs (.log, rerun_log.txt, stderr/stdout.txt,
smoke_log.txt, environment.txt, run.log), machine tables/data (.json/.csv/
.npz...), hash files (HASHES*.txt, det_hash_*.txt, *.sha256), code (.py),
and .md/.txt files matching none of the rules (prompts/working notes that
are not narrative documents).

The banner marks the campaign *distribution copy* status; it does not change
historical event provenance.

Usage:
  check_campaign_labels.py [--root CAMPAIGN_DIR] [--json OUT.json]
Exit 0 iff every in-scope file carries the exact banner in its first 40
lines; exit 1 otherwise (prints missing list).
"""
import json
import os
import re
import sys

BANNER = (b"[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
          b"[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]")
PROMINENCE_LINES = 40

R1 = re.compile(r"report|analysis|result|summary|finding|audit|dispo|"
                r"receipt|campaign|readme|overview", re.I)
NARR_MD = re.compile(r"result|review|verification|analysis|certification|"
                     r"summary|disposition|inventory", re.I)
TXT_LIKE = re.compile(r"receipt|result", re.I)

MACHINE_EXTS = {".json", ".csv", ".npz", ".npy", ".pkl", ".parquet"}
HASH_NAMES = re.compile(r"^HASHES.*\.txt$|^det_hash_.*\.txt$|\.sha256$", re.I)
RAW_LOG_NAMES = re.compile(
    r"\.log$|^rerun_log\.txt$|^stderr\.txt$|^stdout\.txt$|^smoke_log\.txt$|"
    r"^environment\.txt$|^run\.log$", re.I)


def default_root():
    # disclosure_fix/<this> -> campaign_2026_09_13/
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(here) == "disclosure_fix":
        return os.path.dirname(here)
    return os.getcwd()


def classify(path):
    """Return (in_scope: bool, reason: str) for a campaign-relative path."""
    base = os.path.basename(path)
    if path.endswith(".md"):
        if R1.search(base) and NARR_MD.search(base):
            return True, "R1+NARR_MD"
        if R1.search(base):
            return True, "R1"
        if NARR_MD.search(base):
            return True, "NARR_MD"
        return False, "md-non-narrative"
    if path.endswith(".txt"):
        if R1.search(base) or TXT_LIKE.search(base):
            return True, ("R1" if R1.search(base) else "TXT_LIKE")
        if RAW_LOG_NAMES.search(base):
            return False, "raw-log"
        if HASH_NAMES.search(base):
            return False, "hash-file"
        return False, "txt-non-narrative"
    if os.path.splitext(base)[1].lower() in MACHINE_EXTS:
        return False, "machine-data"
    if HASH_NAMES.search(base):
        return False, "hash-file"
    if RAW_LOG_NAMES.search(base) or base.endswith(".log"):
        return False, "raw-log"
    if base.endswith(".py"):
        return False, "code"
    return False, "other-ext"


def banner_state(data):
    lines = data.split(b"\n")
    head = b"\n".join(lines[:PROMINENCE_LINES])
    nonblank = [ln for ln in data.split(b"\n") if ln.strip()]
    return {
        "prominent": BANNER in head,
        "anywhere": BANNER in data,
        "first_nonempty": bool(nonblank) and BANNER in nonblank[0],
    }


def run(root):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, os.path.dirname(root))
            # root-relative "campaign_2026_09_13/..." style when root is the
            # campaign dir; otherwise relative to root's parent.
            all_files.append((rel, full))
    all_files.sort()
    scoped, missing, excluded = [], [], {}
    for rel, full in all_files:
        if os.path.basename(full) == "MANIFEST.sha256":
            excluded["manifest-self"] = excluded.get("manifest-self", 0) + 1
            continue
        in_scope, reason = classify(rel)
        if not in_scope:
            excluded[reason] = excluded.get(reason, 0) + 1
            continue
        with open(full, "rb") as fh:
            data = fh.read()
        st = banner_state(data)
        entry = {"path": rel, "rule": reason, **st, "bytes": len(data)}
        scoped.append(entry)
        if not st["prominent"]:
            missing.append(entry)
    counts = {
        "files_total": len(all_files),
        "in_scope": len(scoped),
        "pass": len(scoped) - len(missing),
        "missing_or_nonprominent": len(missing),
        "excluded": excluded,
    }
    return scoped, missing, counts


def main(argv):
    root = default_root()
    json_out = None
    i = 0
    while i < len(argv):
        if argv[i] == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
            i += 2
        elif argv[i] == "--json" and i + 1 < len(argv):
            json_out = argv[i + 1]
            i += 2
        else:
            print("usage: check_campaign_labels.py [--root DIR] [--json OUT]",
                  file=sys.stderr)
            return 2
    scoped, missing, counts = run(root)
    result = {"banner": BANNER.decode(),
              "prominence_lines": PROMINENCE_LINES,
              "counts": counts, "in_scope": scoped,
              "missing_or_nonprominent": missing}
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=False)
            fh.write("\n")
    print("in-scope: %d  pass: %d  missing/nonprominent: %d" % (
        counts["in_scope"], counts["pass"],
        counts["missing_or_nonprominent"]))
    print("excluded: " + ", ".join(
        "%s=%d" % kv for kv in sorted(counts["excluded"].items())))
    for e in missing:
        print(("ANYWHERE " if e["anywhere"] else "ABSENT   ") +
              e["path"] + "  [%s]" % e["rule"])
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
