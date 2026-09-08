"""Run one synthetic suite with an observed Python-level source-I/O guard.

This is not an OS sandbox and makes no claim about arbitrary native or subprocess I/O.
The owned subprocess negative control installs its own guard in test_codex_v5.py.
"""
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile

suite = Path(sys.argv[1]).resolve()
root = Path(tempfile.mkdtemp(prefix="v52_codex_guard_")).resolve()
tempfile.tempdir = str(root)
os.environ["TEMP"] = os.environ["TMP"] = str(root)
events = []


def audit(event, args):
    if event == "socket.connect":
        raise PermissionError("network forbidden in synthetic suite")
    if event not in ("open", "os.scandir", "os.listdir") or not args:
        return
    if not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    data = path.suffix.lower() in {".json", ".jsonl", ".csv", ".gz"}
    tree = any(p.lower() in {"beam", "dataset", "datasets"} for p in path.parts)
    if data or tree:
        allowed = path == root or root in path.parents
        events.append({"event": event, "allowed": allowed})
        if not allowed:
            raise PermissionError("source access outside synthetic temporary root")


sys.addaudithook(audit)
code = 0
try:
    runpy.run_path(str(suite), run_name="__main__")
except SystemExit as exc:
    code = exc.code or 0
finally:
    print("PYTHON_IO_GUARD " + json.dumps({
        "observed_data_events": len(events),
        "denied_data_events": sum(not e["allowed"] for e in events),
        "scope": "Python open/scandir/listdir data events; no native IO proof",
    }, sort_keys=True))
if any(not e["allowed"] for e in events):
    code = 1
raise SystemExit(code)
