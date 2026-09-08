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
from pathlib import Path

from . import accepted_configuration as cfg


class SourceResolutionError(RuntimeError):
    """Raised when an accepted artifact cannot be produced byte-identically to its accepted hash."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _diagnose(raw: bytes, expected: str) -> str:
    """Say WHY the bytes are wrong, when we can tell. Never used to accept them."""
    if _sha256(raw.replace(b"\r\n", b"\n")) == expected:
        return (" — the bytes match the accepted hash after CRLF-to-LF conversion, so this is a "
                "line-ending-translated checkout (finding D-4). It is REFUSED rather than normalised: "
                "normalising here would also hide a genuine substitution.")
    if _sha256(raw.replace(b"\n", b"\r\n")) == expected:
        return " — the bytes match after LF-to-CRLF conversion; the accepted artifact was stored with CRLF."
    return " — the difference is not a line-ending translation; the content itself differs."


def git_blob(repo_root, commit: str, path: str) -> bytes:
    """The exact bytes Git stores. No checkout, no filter, no platform translation."""
    result = subprocess.run(["git", "-C", str(repo_root), "cat-file", "blob", f"{commit}:{path}"],
                            capture_output=True)
    if result.returncode != 0:
        raise SourceResolutionError(
            f"cannot read the accepted artifact from Git: {commit}:{path} (git exited "
            f"{result.returncode})")
    return result.stdout


def resolve_accepted_manifest(repo_root, benchmark: str) -> tuple[bytes, dict]:
    """Return the accepted manifest's ORIGINAL bytes for `benchmark`, hash-verified.

    The expected hash comes from `accepted_configuration`, NOT from the caller. That is the second
    half of the source-trust fix: there is no argument a caller can pass to change what "accepted"
    means.
    """
    if benchmark not in cfg.ACCEPTED_MANIFESTS:
        raise SourceResolutionError(f"no accepted manifest for benchmark {benchmark!r}")
    entry = cfg.ACCEPTED_MANIFESTS[benchmark]
    raw = git_blob(repo_root, entry["commit"], entry["path"])
    got = _sha256(raw)
    if got != entry["blob_sha256"]:
        raise SourceResolutionError(
            f"the accepted {benchmark} manifest does not hash to its accepted value: expected "
            f"{entry['blob_sha256']}, got {got}{_diagnose(raw, entry['blob_sha256'])}")
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
        raise SourceResolutionError(
            f"materialisation did not preserve bytes for {benchmark}: wrote {len(raw)} bytes, read "
            f"back {len(landed)} with hash {_sha256(landed)}")
    return target


def verify_manifest_bytes(raw: bytes, benchmark: str) -> dict:
    """Verify bytes a caller already holds against the ACCEPTED hash, and name a superseded one.

    A superseded manifest is refused with the reason it was superseded, not merely as a hash
    mismatch — otherwise a successor sees "does not match" and cannot tell substitution from staleness.
    """
    got = _sha256(raw)
    for name, sup in cfg.SUPERSEDED_MANIFESTS.items():
        if got == sup["blob_sha256"]:
            raise SourceResolutionError(
                f"this is the SUPERSEDED {sup['benchmark']} manifest ({name}); it is not accepted and "
                f"must not be loaded. Superseded by {sup['superseded_by']}. Reason: {sup['reason']}")
    if benchmark not in cfg.ACCEPTED_MANIFESTS:
        raise SourceResolutionError(f"no accepted manifest for benchmark {benchmark!r}")
    entry = cfg.ACCEPTED_MANIFESTS[benchmark]
    if got != entry["blob_sha256"]:
        raise SourceResolutionError(
            f"manifest bytes for {benchmark} do not match the accepted hash: expected "
            f"{entry['blob_sha256']}, got {got}{_diagnose(raw, entry['blob_sha256'])}")
    return entry
