"""Finisher v2 for the llmzip heavy backup.

Fixes v1's failure mode: subprocess resolution of bare "python" on this host can land
on a runtime python WITHOUT httplib2 (WinError/ModuleNotFoundError). v2 pins the
absolute venv python that has httplib2+googleapiclient, and skips files already present
in the Drive folder (idempotent).

Run:  "C:\\Users\\MDP\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe" _finish_backup2.py
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

WORK = Path(r"C:\Users\MDP\dev\llmzip-work")
B = WORK / "_drive_backup_2026_09_13"
FOLDER = "1-8DYki9uXVPIVsKBAL2xCzw_LeUJH0q4"
WRAPPER = str(WORK / "_gapi_netfix.py")
PYTHON = r"C:\Users\MDP\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

ARCHIVES = [
    "01_datasets_REALTALK.tar.gz",
    "02_dataset_PerLTQA.tar.gz",
    "03_regen_caches.tar.gz",
    "04_bench3_runs_caches.tar.gz",
    "05_transcripts.tar.gz",
    "06_review_transfer.tar",
    "07_drive_frozen.tar.gz",
    "08_wheels_and_smalls.tar.gz",
]


def gapi(*args):
    r = subprocess.run([PYTHON, WRAPPER, *args], capture_output=True, text=True)
    return r.stdout or ""


# 1) wait for archives present + stable (fast if already done)
deadline = time.time() + 3600
while True:
    missing = [n for n in ARCHIVES if not (B / n).exists() or (B / n).stat().st_size == 0]
    if not missing:
        s1 = [(B / n).stat().st_size for n in ARCHIVES]
        time.sleep(20)
        s2 = [(B / n).stat().st_size for n in ARCHIVES]
        if s1 == s2:
            print("all archives present & stable", flush=True)
            break
    if time.time() > deadline:
        print("TIMEOUT waiting for archives; missing:", missing, flush=True)
        sys.exit(2)
    time.sleep(20)

# 2) manifest (rewrite identically; cheap insurance)
lines = []
for n in ARCHIVES + ["00_BACKUP_README.md"]:
    h = hashlib.sha256()
    with (B / n).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    lines.append(f"{h.hexdigest()}  {n}")
(B / "MANIFEST_sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("manifest written", flush=True)

# 3) what is already in the Drive folder?
existing = set()
try:
    out = gapi("drive", "search", f"'{FOLDER}' in parents", "--raw-query", "--max", "50")
    for f in json.loads(out):
        existing.add(f.get("name"))
except Exception as e:
    print("folder query failed (will upload all):", repr(e)[:120], flush=True)
print("already on Drive:", sorted(existing), flush=True)

uploads = [n for n in ARCHIVES if n != "01_datasets_REALTALK.tar.gz"] + [
    "00_BACKUP_README.md",
    "MANIFEST_sha256.txt",
]
uploads = [n for n in uploads if n not in existing]
print("to upload:", uploads, flush=True)

for n in uploads:
    ok = False
    for attempt in (1, 2, 3):
        r = subprocess.run(
            [PYTHON, WRAPPER, "drive", "upload", str(B / n), "--name", n, "--parent", FOLDER],
            capture_output=True, text=True,
        )
        out = (r.stdout or "").replace("\n", " ")
        if '"status": "uploaded"' in out:
            print(f"UPLOADED {n} :: {out[:220]}", flush=True)
            ok = True
            break
        print(f"RETRY {n} attempt={attempt} err={(r.stderr or '')[-160:]}", flush=True)
        time.sleep(8)
    if not ok:
        print(f"FAILED {n}", flush=True)

print("FINISHER2_DONE", flush=True)