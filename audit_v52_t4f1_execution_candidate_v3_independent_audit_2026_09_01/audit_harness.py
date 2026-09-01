"""Outcome-free audit harness. Refuses forbidden candidate modes before launch."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys
from pathlib import Path

AUDIT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = AUDIT_ROOT.parent
CANDIDATE = REPO_ROOT / "task4f1_execution_candidate_v3_2026_09_01"
PARENT = REPO_ROOT.parent
CORPUS = PARENT / "BEAM_pinned_3e12035532eb85768f1a7cd779832b650c4b2ef9"
PYTHON = "/home/user/py31213/bin/python3"
COMMAND_LOG = AUDIT_ROOT / "COMMAND_LOG.txt"

FORBIDDEN_TOKENS = ("--mode run", "--mode finalize", "--mode=run", "--mode=finalize")
FORBIDDEN_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"

class ForbiddenCommand(RuntimeError):
    pass

def _guard(argv):
    joined = " ".join(str(a) for a in argv)
    for token in FORBIDDEN_TOKENS:
        if token in joined:
            raise ForbiddenCommand(f"HARNESS REFUSED FORBIDDEN COMMAND: {token}")
    if "run" in argv and "--mode" in argv and argv[argv.index("--mode") + 1] == "run":
        raise ForbiddenCommand("HARNESS REFUSED FORBIDDEN COMMAND: --mode run")
    if "--mode" in argv:
        mode = argv[argv.index("--mode") + 1]
        if mode in {"run", "finalize"}:
            raise ForbiddenCommand(f"HARNESS REFUSED FORBIDDEN COMMAND: --mode {mode}")
    if FORBIDDEN_ENV in os.environ:
        raise ForbiddenCommand("HARNESS REFUSED: HMAC key environment variable is set")

def locked_env():
    env = dict(os.environ)
    env.update({
        "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
    })
    env.pop(FORBIDDEN_ENV, None)
    return env

def run(argv, cwd=None, check=False, note=""):
    _guard(argv)
    proc = subprocess.run([str(a) for a in argv], cwd=str(cwd) if cwd else None,
                          env=locked_env(), capture_output=True, text=True, timeout=3600)
    with COMMAND_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"$ {' '.join(str(a) for a in argv)}\n")
        if note:
            fh.write(f"# {note}\n")
        fh.write(f"# exit={proc.returncode}\n")
        for line in (proc.stdout or "").splitlines():
            fh.write(f"  out| {line}\n")
        for line in (proc.stderr or "").splitlines()[-40:]:
            fh.write(f"  err| {line}\n")
        fh.write("\n")
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed: {argv}\n{proc.stdout}\n{proc.stderr}")
    return proc

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def emit(name, payload):
    p = AUDIT_ROOT / "evidence" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p

def note(text):
    with COMMAND_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"### {text}\n\n")
