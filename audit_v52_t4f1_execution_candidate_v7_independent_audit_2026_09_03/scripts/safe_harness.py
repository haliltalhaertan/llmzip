#!/usr/bin/env python3
"""Mandatory outcome-free subprocess harness for the V7 independent audit.

Refuses, BEFORE launch, any command that could produce a retrieval-quality outcome:
  * any token containing '--mode run' or '--mode finalize' (in any spelling/join form)
  * any '--mode' whose value is not an allow-listed outcome-free mode
  * any invocation with the HMAC authorization key environment variable set
Every launched and every refused command is appended to COMMAND_LOG.txt.
"""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT_ROOT = Path(__file__).resolve().parent.parent
COMMAND_LOG = AUDIT_ROOT / "COMMAND_LOG.txt"
AUTH_HMAC_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"

FORBIDDEN_MODES = {"run", "finalize"}
ALLOWED_MODES = {"preflight"}


class Refused(RuntimeError):
    pass


def _normalise(argv: list[str]) -> str:
    return " ".join(argv).lower().replace("=", " ")


def screen(argv: list[str], env: dict) -> None:
    flat = _normalise(argv)
    for bad in FORBIDDEN_MODES:
        if f"--mode {bad}" in flat:
            raise Refused(f"REFUSED_BEFORE_LAUNCH: forbidden mode '{bad}' in command")
    # explicit --mode value check (covers '--mode', 'X' and '--mode=X')
    tokens: list[str] = []
    for a in argv:
        tokens.extend(a.split("=", 1) if a.startswith("--mode=") else [a])
    for i, tok in enumerate(tokens):
        if tok == "--mode":
            if i + 1 >= len(tokens):
                raise Refused("REFUSED_BEFORE_LAUNCH: --mode with no value")
            val = tokens[i + 1].lower()
            if val not in ALLOWED_MODES:
                raise Refused(f"REFUSED_BEFORE_LAUNCH: mode '{val}' is not outcome-free")
    if AUTH_HMAC_ENV in env:
        raise Refused(f"REFUSED_BEFORE_LAUNCH: {AUTH_HMAC_ENV} present in environment")
    for fn in ("run_archives", "evaluate_archive", "finalize_results"):
        if fn in flat:
            raise Refused(f"REFUSED_BEFORE_LAUNCH: outcome-capable entry point '{fn}'")


def _log(record: dict) -> None:
    with COMMAND_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def run(argv: list[str], cwd: str | None = None, env: dict | None = None,
        expect_fail: bool = False) -> dict:
    env = dict(env if env is not None else os.environ)
    env.pop(AUTH_HMAC_ENV, None)
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env.setdefault(k, "1")
    env.setdefault("PYTHONHASHSEED", "0")
    stamp = datetime.now(timezone.utc).isoformat()
    try:
        screen(argv, env)
    except Refused as exc:
        rec = {"utc": stamp, "argv": argv, "cwd": cwd, "launched": False, "refusal": str(exc)}
        _log(rec)
        return rec
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    rec = {"utc": stamp, "argv": argv, "cwd": cwd, "launched": True,
           "returncode": proc.returncode,
           "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:],
           "expect_fail": expect_fail}
    _log(rec)
    return rec


if __name__ == "__main__":
    r = run(sys.argv[1:])
    print(json.dumps(r, indent=2, sort_keys=True))
