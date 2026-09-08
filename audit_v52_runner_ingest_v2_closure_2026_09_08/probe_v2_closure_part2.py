"""Part 2 of the independent closure probes: the items part 1 left open.

Usage:  python probe_v2_closure_part2.py <checkout-of-9b56968> <repo-root>
"""
import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
V2 = PKG / "drafts" / "v52" / "membership_runner_ingest_v2_2026_09_08"
V1R = PKG / "drafts" / "v52" / "membership_runner_v1_2026_09_08"
V1I = PKG / "drafts" / "v52" / "membership_ingest_v1_2026_09_08"
CORE = PKG / "drafts" / "v52" / "membership_impl_v3_2026_09_07"
for p in (V2, CORE, V1R, V1I):
    sys.path.insert(0, str(p))

TMP = Path(tempfile.mkdtemp(prefix="probe2_"))

import membership_scaling_core as core
import membership_runner_v2 as R2
import corpus_ingest_v2 as I2
import safe_report
from authoritative import accepted_configuration as ACC
import membership_runner as R1
import corpus_ingest as I1

CANARY = {"question": "What did Melanie say about her sister's wedding in Lisbon last spring?",
          "answer": "She said the ceremony was on a rooftop and it rained.",
          "id": "Melanie's private note about the Lisbon trip"}


def leaks(t):
    return sorted(k for k, v in CANARY.items() if v in str(t))


@contextlib.contextmanager
def capture():
    out, err = io.StringIO(), io.StringIO()
    box = {"exc": ""}
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            yield box
    except BaseException as exc:                                     # noqa: BLE001
        box["exc"] = "".join(traceback.format_exception(exc))
    finally:
        box["all"] = out.getvalue() + err.getvalue() + box["exc"]


def rec(pid, verdict, label, detail=""):
    print(f"[{verdict:7}] {pid:<8} {label}")
    for line in str(detail).splitlines():
        print(f"                     | {line}")


def raises(fn, *a, **k):
    try:
        return None, fn(*a, **k)
    except BaseException as exc:                                     # noqa: BLE001
        return exc, None


# P1 - the corrected v1 negative control for assert_content_free (my part-1 F25 was mis-built:
#      I put the long value under key "x", so v1 echoed "x" and not the canary)
payload = {CANARY["question"]: "x" * 400}
with capture() as b:
    I1.assert_content_free(payload)
rec("P1", "PASS" if leaks(b["all"]) else "FINDING",
    "CORRECTED v1 NEGATIVE CONTROL: v1's assert_content_free echoes a sub-120 dict KEY verbatim",
    f"canaries: {leaks(b['all'])}\n{b['all'].strip().splitlines()[-1][:220]}")
with capture() as b2:
    I2.assert_content_free(payload)
rec("P2", "PASS" if not leaks(b2["all"]) else "FINDING",
    "v2's assert_content_free reports the key by digest only",
    f"canaries: {leaks(b2['all']) or 'none'}\n{b2['all'].strip().splitlines()[-1][:220]}")

# P3 - residual D-8 class inside the RUNNER: an unguarded mapping["benchmark"]
e, _ = raises(R2.compute_results, [], [], [], {}, TMP / "n.json",
              benchmark=R2.LOCOMO, scheme="question")
rec("P3", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "compute_results with a mapping that has no 'benchmark' key",
    f"{type(e).__name__}: {e}")

# P4 - do the F12..F20 values ever reach a WRITTEN FILE, or only an exception?
writers = [n for n in dir(R2) if n.startswith("write") or n.startswith("freeze")] + \
          [n for n in dir(I2) if n.startswith("write")]
rec("P4", "INFO", "every writer in the two v2 modules (all route through core.safe_write_json)",
    str(sorted(set(writers))))
s = (V2 / "membership_runner_v2.py").read_text(encoding="utf-8") + \
    (V2 / "corpus_ingest_v2.py").read_text(encoding="utf-8")
rec("P5", "PASS" if "open(" not in s.replace('path.open("rb")', "") else "FINDING",
    "no v2 module opens a file for writing except through the core writer",
    "checked by source inspection")

# P6 - is the D-5 claim in each module byte-verbatim false?
r2doc = (V2 / "membership_runner_v2.py").read_text(encoding="utf-8")
i2doc = (V2 / "corpus_ingest_v2.py").read_text(encoding="utf-8")
rec("P6", "INFO", "the two content claims, byte-verbatim",
    "runner_v2.py:68  " + [l for l in r2doc.splitlines()
                           if "no value is interpolated" in l][0].strip() + "\n"
    "corpus_ingest_v2.py:46  " + [l for l in i2doc.splitlines()
                                  if "NO value is interpolated" in l][0].strip())
_w = [l.strip() for l in i2doc.splitlines()
      if "in the manifest rather than waived" in l or "recorded" in l]
rec("P7", "INFO", "the D-1 waiver claim, byte-verbatim", "\n".join(_w[:5]))

# P8 - count the interpolation sites that survive in each v2 module
import re
sites = []
for name, text in (("membership_runner_v2.py", r2doc), ("corpus_ingest_v2.py", i2doc)):
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"\{([A-Za-z_][^{}]*?)(![rs])?\}", line):
            expr = m.group(1)
            if expr.startswith(("safe_report", "len(", "sorted(", "int(")) or expr in (
                    "_path", "i", "si", "ti", "position", "kind"):
                continue
            sites.append((name, i, expr, line.strip()[:110]))
print()
rec("P8", "INFO", f"{len(sites)} raw interpolation sites survive in the two v2 modules",
    "\n".join(f"{n}:{i}  {{{e}}}   {t}" for n, i, e, t in sites))

# P9 - the LongMemEval evidence tally is a tautology by construction (source inspection)
tally = [l.strip() for l in i2doc.splitlines() if '"evidence_tally"' in l or '"declared": sum' in l
         or '"resolved": sum' in l or '"unresolved": 0' in l]
rec("P9", "INFO", "how the LongMemEval evidence tally is built", "\n".join(tally))

print()
print("done. temp:", TMP)
