#!/usr/bin/env python3
"""Outcome-free subprocess harness for the V4 independent audit.

Refuses, BEFORE launch, any command containing '--mode run' or '--mode finalize'.
Every launched command and its exit status is appended to COMMAND_LOG.txt.
"""
from __future__ import annotations
import os, subprocess, sys, datetime
from pathlib import Path

AUDIT_ROOT = Path(__file__).resolve().parent.parent
LOG = AUDIT_ROOT / "COMMAND_LOG.txt"
FORBIDDEN = ("--mode run", "--mode finalize", "--mode=run", "--mode=finalize")
COUNTERS = AUDIT_ROOT / "evidence" / "execution_counters.json"


def _forbidden(argv: list[str]) -> str | None:
    joined = " ".join(argv)
    for token in FORBIDDEN:
        if token in joined:
            return token
    # also catch split forms: ['--mode','run']
    for i, a in enumerate(argv):
        if a == "--mode" and i + 1 < len(argv) and argv[i + 1] in ("run", "finalize"):
            return f"--mode {argv[i+1]}"
    return None


def log(line: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip("\n") + "\n")


def run(argv: list[str], env: dict[str, str] | None = None, cwd: str | None = None,
        note: str = "", check: bool = False) -> subprocess.CompletedProcess:
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hit = _forbidden(argv)
    if hit:
        log(f"{stamp} REJECTED_BEFORE_LAUNCH token={hit!r} argv={argv!r} note={note}")
        raise SystemExit(f"[AUDIT HARNESS REFUSAL] outcome-capable mode blocked: {hit}")
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    if "V52_T4F1_AUTH_HMAC_KEY_HEX" in full_env:
        log(f"{stamp} REJECTED_BEFORE_LAUNCH reason=HMAC_KEY_PRESENT argv={argv!r}")
        raise SystemExit("[AUDIT HARNESS REFUSAL] production HMAC key must never be set")
    log(f"{stamp} LAUNCH argv={argv!r} cwd={cwd or os.getcwd()!r} env_overrides={sorted((env or {}).keys())!r} note={note}")
    proc = subprocess.run(argv, env=full_env, cwd=cwd, capture_output=True, text=True)
    log(f"{stamp} EXIT rc={proc.returncode} stdout_bytes={len(proc.stdout)} stderr_bytes={len(proc.stderr)}")
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed rc={proc.returncode}: {proc.stderr[-2000:]}")
    return proc
