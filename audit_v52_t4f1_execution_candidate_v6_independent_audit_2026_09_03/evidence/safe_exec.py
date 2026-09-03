#!/usr/bin/env python3
"""No-outcome subprocess harness for the V6 independent delta audit.

Refuses, BEFORE launch, any command whose argv contains a forbidden mode or the
production HMAC key environment variable. Appends every launch to COMMAND_LOG.txt.
"""
from __future__ import annotations
import subprocess, sys, os, datetime, pathlib, shlex

FORBIDDEN_SUBSTRINGS = ("--mode run", "--mode finalize", "--mode=run", "--mode=finalize")
FORBIDDEN_ARGV_PAIRS = (("--mode", "run"), ("--mode", "finalize"))
FORBIDDEN_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"
LOG = pathlib.Path(__file__).resolve().parent.parent / "COMMAND_LOG.txt"

def refuse(reason: str, argv: list[str]) -> None:
    line = f"{datetime.datetime.now(datetime.UTC).isoformat()} REFUSED [{reason}] {shlex.join(argv)}"
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line)
    raise SystemExit(97)

def run(argv: list[str], cwd: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    joined = " ".join(argv)
    for bad in FORBIDDEN_SUBSTRINGS:
        if bad in joined:
            refuse(f"forbidden mode substring {bad!r}", argv)
    for i in range(len(argv) - 1):
        if (argv[i], argv[i + 1]) in FORBIDDEN_ARGV_PAIRS:
            refuse(f"forbidden mode pair {argv[i]} {argv[i+1]}", argv)
    for token in argv:
        if token in ("run", "finalize") and "--mode" in joined:
            refuse(f"forbidden mode token {token!r}", argv)
    merged = dict(os.environ if env is None else env)
    if FORBIDDEN_ENV in merged:
        refuse(f"{FORBIDDEN_ENV} present in environment", argv)
    merged.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    for var in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"):
        merged.setdefault(var, "1")
    merged.setdefault("PYTHONHASHSEED", "0")
    proc = subprocess.run(argv, cwd=cwd, env=merged, capture_output=True, text=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.datetime.now(datetime.UTC).isoformat()} LAUNCH rc={proc.returncode} cwd={cwd} {shlex.join(argv)}\n")
    return proc

if __name__ == "__main__":
    p = run(sys.argv[1:])
    sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); raise SystemExit(p.returncode)
