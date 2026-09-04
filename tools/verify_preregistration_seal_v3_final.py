#!/usr/bin/env python3
"""Final production verifier for the unchanged V52 Task 4F1 Seal V3.

This is deliberately a thin second layer over tools/verify_preregistration_seal.py.
The existing verifier remains the semantic/source verifier. This module adds the three
Head-Researcher closure requirements without changing Seal V3 bytes:

1. production identity: the exact Seal V3 SHA256 is pinned and cross-checked against its sidecar;
2. exact §6 rule equality: the complete authoritative Sign-boundary arithmetic paragraph is bound;
3. exact extraction-rule equality: marker-containing paraphrases are not accepted.

Production verification enforces identity first. Tests may call verify_content_sources() directly
on mutated temporary seals so semantic negative controls are not trivially shadowed by a self-hash
mismatch.

Reads only. Imports no outcome-capable candidate and accesses no retrieval-quality outcome.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_VERIFIER_PATH = ROOT / "tools" / "verify_preregistration_seal.py"
SEAL_PATH = ROOT / "docs" / "v52" / "task4f1" / "TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json"
SIDECAR_PATH = ROOT / "docs" / "v52" / "task4f1" / "TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json.sha256"
ACCEPTED_SEAL_SHA256 = "e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4"
ACCEPTED_SEAL_FILENAME = "TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json"
SIGN_RULE_MARKER = "**Sign-boundary arithmetic.**"
IMPL_NOTE_MARKER = "Implementation note, not a defect in this preregistration:"
EXACT_EXTRACTION_RULE = (
    "the paragraph of the artifact beginning "
    "'Implementation note, not a defect in this preregistration:'"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_base_verifier():
    spec = importlib.util.spec_from_file_location("v52_prereg_base_verifier", BASE_VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load base preregistration verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_sidecar(path: Path) -> tuple[str, str] | None:
    """Return exactly (digest, filename); reject extra lines/tokens or malformed data."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return None
    parts = lines[0].split()
    if len(parts) != 2:
        return None
    digest, filename = parts
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        return None
    return digest, filename


def verify_identity(
    seal_path: Path = SEAL_PATH,
    sidecar_path: Path = SIDECAR_PATH,
) -> list[str]:
    """Production identity layer: only the accepted immutable Seal V3 bytes are recognized."""
    fail: list[str] = []
    if not seal_path.is_file():
        return [f"Seal V3 missing: {seal_path}"]

    actual = sha256_file(seal_path)
    if actual != ACCEPTED_SEAL_SHA256:
        fail.append(
            "Seal V3 identity mismatch: "
            f"{actual} != accepted {ACCEPTED_SEAL_SHA256}"
        )

    parsed = parse_sidecar(sidecar_path)
    if parsed is None:
        fail.append("Seal V3 sidecar missing or malformed")
    else:
        declared_digest, declared_filename = parsed
        if declared_filename != ACCEPTED_SEAL_FILENAME:
            fail.append(
                "Seal V3 sidecar filename mismatch: "
                f"{declared_filename!r} != {ACCEPTED_SEAL_FILENAME!r}"
            )
        if declared_digest != ACCEPTED_SEAL_SHA256:
            fail.append(
                "Seal V3 sidecar digest mismatch: "
                f"{declared_digest} != accepted {ACCEPTED_SEAL_SHA256}"
            )
        if declared_digest != actual:
            fail.append("Seal V3 sidecar digest does not match the bytes under SEAL_PATH")
    return fail


def extract_authoritative_rule(base, draft_text: str) -> str | None:
    """Reproduce the V3 builder's exact §6 paragraph extraction."""
    s6 = base.section(draft_text, 6)
    for paragraph in s6.split("\n\n"):
        if paragraph.startswith(SIGN_RULE_MARKER):
            return paragraph.rstrip()
    return None


def verify_exactness(seal_path: Path, base=None) -> list[str]:
    """Checks the two exact-text conditions that the base verifier historically checked weakly."""
    fail: list[str] = []
    if base is None:
        base = load_base_verifier()
    try:
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read Seal V3 for exactness checks: {exc}"]

    try:
        b = seal["bindings"]
        b1 = b["1_approved_preregistration_draft"]
        b8 = b["8_exact_rational_sign_classification_condition"]
        src8 = b8["implementation_condition_source"]
    except (KeyError, TypeError) as exc:
        return [f"missing field required for exactness checks: {exc}"]

    draft_path = ROOT / b1["path"]
    if not draft_path.is_file():
        fail.append("approved draft unavailable for exact §6 rule extraction")
    else:
        draft_text = draft_path.read_text(encoding="utf-8")
        extracted_rule = extract_authoritative_rule(base, draft_text)
        if extracted_rule is None:
            fail.append("authoritative Sign-boundary arithmetic paragraph absent from §6")
        elif b8.get("preregistered_rule_verbatim") != extracted_rule:
            fail.append(
                "binding 8 preregistered_rule_verbatim is not exactly the authoritative §6 paragraph"
            )

    if src8.get("extraction_rule") != EXACT_EXTRACTION_RULE:
        fail.append("binding 8 extraction_rule is not exactly the sealed V3 extraction rule")

    return fail


def verify_content_sources(seal_path: Path = SEAL_PATH) -> list[str]:
    """Semantic/source layer, intentionally callable on mutated test seals without identity gating."""
    base = load_base_verifier()
    old_path = base.SEAL_PATH
    try:
        base.SEAL_PATH = seal_path
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = base.main()
        fail: list[str] = []
        if rc != 0:
            text = output.getvalue().strip()
            fail.append("base semantic/source verifier rejected seal" + (f": {text}" if text else ""))
        fail.extend(verify_exactness(seal_path, base=base))
        return fail
    finally:
        base.SEAL_PATH = old_path


def main() -> int:
    identity_fail = verify_identity()
    if identity_fail:
        print("PREREGISTRATION_SEAL_V3_FINAL: BLOCKED")
        print("layer=identity")
        for item in identity_fail:
            print(f"- {item}")
        return 1

    semantic_fail = verify_content_sources()
    if semantic_fail:
        print("PREREGISTRATION_SEAL_V3_FINAL: BLOCKED")
        print("layer=content/source")
        for item in semantic_fail:
            print(f"- {item}")
        return 1

    print("PREREGISTRATION_SEAL_V3_FINAL: PASS")
    print(f"seal_sha256={ACCEPTED_SEAL_SHA256}")
    print("identity_layer=PASS")
    print("content_source_layer=PASS")
    print("outcome_access=FORBIDDEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
