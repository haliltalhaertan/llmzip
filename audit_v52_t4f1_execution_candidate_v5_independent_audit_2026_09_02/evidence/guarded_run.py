#!/usr/bin/env python3
"""Mandatory outcome-boundary subprocess harness for the V5 delta audit.

Refuses, BEFORE launch, any command that could produce or touch a retrieval-quality
outcome. Also refuses to launch while the authorization HMAC key environment variable
is set, and strips it from every child environment.

Usage: guarded_run.py [--cwd DIR] -- <argv...>
"""
import json, os, subprocess, sys, time

FORBIDDEN_SUBSTRINGS = (
    "--mode run", "--mode finalize", "--mode=run", "--mode=finalize",
    "run_archives", "evaluate_archive", "finalize_results",
)
FORBIDDEN_TOKEN_PAIRS = (("--mode", "run"), ("--mode", "finalize"))
FORBIDDEN_MODE_VALUES = {"run", "finalize"}
AUTH_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"
LOG = os.environ.get("GUARDED_RUN_LOG", "")


def refuse(reason, argv):
    payload = {"refused": True, "reason": reason, "argv": argv,
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if LOG:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write("REFUSED " + json.dumps(payload) + "\n")
    print("HARNESS REFUSAL: " + reason, file=sys.stderr)
    print(json.dumps(payload), file=sys.stderr)
    sys.exit(97)


def main():
    args = sys.argv[1:]
    cwd = None
    if args and args[0] == "--cwd":
        cwd, args = args[1], args[2:]
    if args and args[0] == "--":
        args = args[1:]
    if not args:
        refuse("empty command", args)

    joined = " ".join(args)
    low = joined.lower()
    for bad in FORBIDDEN_SUBSTRINGS:
        if bad in low:
            refuse(f"command contains forbidden outcome-capable substring {bad!r}", args)
    for i, tok in enumerate(args):
        if tok == "--mode" and i + 1 < len(args) and args[i + 1].lower() in FORBIDDEN_MODE_VALUES:
            refuse(f"command requests forbidden mode {args[i+1]!r}", args)
        if tok.startswith("--mode=") and tok.split("=", 1)[1].lower() in FORBIDDEN_MODE_VALUES:
            refuse(f"command requests forbidden mode {tok!r}", args)

    if AUTH_ENV in os.environ:
        refuse(f"{AUTH_ENV} is present in the environment; refusing to launch", args)

    env = {k: v for k, v in os.environ.items() if k != AUTH_ENV}
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "PYTHONHASHSEED": "0",
    })
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    proc = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    record = {"refused": False, "utc": started, "cwd": cwd or os.getcwd(), "argv": args,
              "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    if LOG:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write("LAUNCHED " + json.dumps({k: record[k] for k in ("utc","cwd","argv","returncode")}) + "\n")
            fh.write("--- stdout ---\n" + proc.stdout)
            fh.write("--- stderr ---\n" + proc.stderr + "\n")
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
