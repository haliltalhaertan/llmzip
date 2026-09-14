"""Byte-preserving resolution of the accepted manifests. Answers finding D-4.

THE DEFECT. `load_expected_mapping` hashed the file ON DISK against a hash computed from the RAW GIT
BLOB. The repository ships no `.gitattributes`, and this machine's SYSTEM Git config sets
`core.autocrlf=true`, so a default clone rewrites every LF to CRLF on checkout. Measured by the
review: `PROPOSED_mapping_locomo.json` is 59268 bytes / `66379b9d…` as a blob and 60823 bytes /
`4a1f7c2d…` in a default checkout, 1555 CRLFs apart. The accepted configuration could not be loaded by
its own hash-pinned loader. It fails CLOSED, so it blocks rather than corrupts.

THE FIX, AND THE TWO THINGS IT DELIBERATELY DOES NOT DO.

  It resolves manifests from **Git's original bytes** — `git cat-file blob <commit>:<path>` — which is
  the byte stream the accepted hash was computed over, and materialises them with `open(..., "wb")`,
  which performs no newline translation on any platform. That is the whole path, described here so it
  is not folklore.

  It does NOT relax the hash check. A mismatch is refused.

  It does NOT normalise line endings to make a mismatch go away. When the bytes fail, it *diagnoses*
  whether a CRLF checkout would explain it — and still refuses. Hiding the mismatch by normalising is
  precisely how a substituted manifest would slip through, so the diagnosis is a message, never a
  fallback.

  It changes NO global Git setting and adds NO `.gitattributes`. The review offered those as the
  cleanest fix; they are out of scope by instruction, and they would also fix the symptom in one
  clone rather than the mechanism in the code.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from . import accepted_configuration as cfg

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import errors                                                                    # noqa: E402


class SourceResolutionError(RuntimeError):
    """Raised when an accepted artifact cannot be produced byte-identically to its accepted hash."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _diagnose(raw: bytes, expected: str) -> dict:
    """Say WHY the bytes are wrong, as SAFE FLAGS. Never used to accept them.

    v2 returned a sentence. v3 returns booleans and lengths, because a diagnosis is exactly the
    kind of helpful message that grows a value in it later.
    """
    return {"crlf_to_lf_would_match": _sha256(raw.replace(b"\r\n", b"\n")) == expected,
            "lf_to_crlf_would_match": _sha256(raw.replace(b"\n", b"\r\n")) == expected,
            "got_bytes": len(raw)}


def git_blob(repo_root, commit: str, path: str) -> bytes:
    """The exact bytes Git stores. No checkout, no filter, no platform translation."""
    result = subprocess.run(["git", "-C", str(repo_root), "cat-file", "blob", f"{commit}:{path}"],
                            capture_output=True)
    if result.returncode != 0:
        errors.raise_violation(SourceResolutionError, errors.Code.GIT_BLOB_UNREADABLE,
                               git_exit_code=result.returncode)
    return result.stdout


def resolve_accepted_manifest(repo_root, benchmark: str) -> tuple[bytes, dict]:
    """Return the accepted manifest's ORIGINAL bytes for `benchmark`, hash-verified.

    The expected hash comes from `accepted_configuration`, NOT from the caller. That is the second
    half of the source-trust fix: there is no argument a caller can pass to change what "accepted"
    means.
    """
    # N-2 / F17: the benchmark is validated against the closed set BEFORE it could reach a message.
    if benchmark not in cfg.ACCEPTED_MANIFESTS:
        errors.raise_violation(SourceResolutionError, errors.Code.UNKNOWN_BENCHMARK,
                               accepted_benchmarks=len(cfg.ACCEPTED_MANIFESTS))
    entry = cfg.ACCEPTED_MANIFESTS[benchmark]
    raw = git_blob(repo_root, entry["commit"], entry["path"])
    got = _sha256(raw)
    if got != entry["blob_sha256"]:
        errors.raise_violation(SourceResolutionError, errors.Code.SOURCE_IDENTITY_MISMATCH,
                               expected_bytes=entry.get("bytes", -1),
                               **_diagnose(raw, entry["blob_sha256"]))
    return raw, entry


def materialize_accepted_manifest(repo_root, benchmark: str, out_dir) -> Path:
    """Write the accepted manifest into `out_dir` byte-preservingly, and verify what landed.

    `open(..., "wb")` performs no newline translation on any platform. The file is re-read and
    re-hashed afterwards, so the guarantee is checked rather than assumed.
    """
    raw, entry = resolve_accepted_manifest(repo_root, benchmark)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / Path(entry["path"]).name
    with target.open("wb") as handle:
        handle.write(raw)
    landed = target.read_bytes()
    if _sha256(landed) != entry["blob_sha256"]:
        errors.raise_violation(SourceResolutionError, errors.Code.MATERIALISATION_NOT_BYTE_PRESERVING,
                               wrote_bytes=len(raw), read_back_bytes=len(landed))
    return target


def verify_manifest_bytes(raw: bytes, benchmark: str) -> dict:
    """Verify bytes a caller already holds against the ACCEPTED hash, and name a superseded one.

    A superseded manifest is refused with the reason it was superseded, not merely as a hash
    mismatch — otherwise a successor sees "does not match" and cannot tell substitution from staleness.
    """
    got = _sha256(raw)
    for _name, sup in cfg.SUPERSEDED_MANIFESTS.items():
        if got == sup["blob_sha256"]:
            # The code itself says SUPERSEDED, so the distinction from a substitution survives
            # without printing the reason text, which is data from the configuration module.
            errors.raise_violation(SourceResolutionError, errors.Code.MANIFEST_SUPERSEDED,
                                   superseded_manifests_known=len(cfg.SUPERSEDED_MANIFESTS))
    # N-2 / F16: validated against the closed set before any message could use it.
    if benchmark not in cfg.ACCEPTED_MANIFESTS:
        errors.raise_violation(SourceResolutionError, errors.Code.UNKNOWN_BENCHMARK,
                               accepted_benchmarks=len(cfg.ACCEPTED_MANIFESTS))
    entry = cfg.ACCEPTED_MANIFESTS[benchmark]
    if got != entry["blob_sha256"]:
        errors.raise_violation(SourceResolutionError, errors.Code.MANIFEST_NOT_ACCEPTED,
                               **_diagnose(raw, entry["blob_sha256"]))
    return entry
