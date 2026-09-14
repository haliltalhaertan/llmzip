"""Bounded diagnostic descriptions used by selected runner error paths.

THE DEFECT. v1's claim — byte-verbatim, `corpus_ingest.py:35-36` — was:

    "Question, answer, dialogue and session text is held in memory and handed to the caller. It is
     never printed, logged, put in an exception message, or written to disk."

False. The content policy ran only inside the manifest writer and never touched exception text. The
review got source-derived text out through SEVEN paths using fragments all SHORTER than the 120
character limit, the worst being `_describe()` — `f"{type(value).__name__}({value!r})"` with no cap —
which dumped a whole record dict, question and answer and session text, in one 482-character message.
`assert_content_free` even interpolated a sub-120 dict KEY verbatim into its own error.

`describe()` reports a builtin type category, its length or shape, and a short digest for builtin
values. Other objects are opaque: their custom repr, type name and length hooks are not called.
Digests reveal equality and may permit guessing low-entropy inputs; they are NOT a confidentiality
guarantee. The closed error-code formatter lives in errors.py, not in this module.

THE 120-CHARACTER LIMIT IS NOT USED AS A GUARANTEE ANYWHERE. It was never one: every leak the review
demonstrated used a fragment under it. The limit survives only in `assert_content_free`, as one
blunt structural check among others on data about to be written — not as the reason anything is safe.

WHAT IS STILL ALLOWED OUT, stated so it is not mistaken for nothing:
  * counts, indices, positions, lengths and shapes;
  * fixed error codes and field names drawn from this package's own vocabulary, never from data;
  * builtin type categories (other objects are reported as object);
  * short hex digests of values.
Identifiers are NOT on that list. An identifier can carry text when a source is malformed — that is
exactly what the review's `_describe()` probe exploited — so ids are reported by digest and position.
"""
from __future__ import annotations

import hashlib

DIGEST_CHARS = 12


def digest(value) -> str:
    """A short fingerprint for builtin-only values; opaque marker for custom objects.

    Not a secrecy guarantee. Avoid invoking custom repr hooks, including nested objects.
    """
    if not _builtin_tree(value):
        return hashlib.sha256(b"<opaque object>").hexdigest()[:DIGEST_CHARS]
    try:
        material = repr(value).encode("utf-8", errors="replace")
    except Exception:                                                            # noqa: BLE001
        material = f"<unrepresentable {type(value).__name__}>".encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:DIGEST_CHARS]


def _builtin_tree(value, seen=None) -> bool:
    if type(value) in (str, bytes, bytearray, int, float, bool, type(None)):
        return True
    if type(value) not in (dict, list, tuple, set, frozenset):
        return False
    seen = set() if seen is None else seen
    if id(value) in seen:
        return False
    seen.add(id(value))
    try:
        items = (item for pair in value.items() for item in pair) if type(value) is dict else value
        return all(_builtin_tree(item, seen) for item in items)
    finally:
        seen.remove(id(value))


def _shape(value) -> str:
    if type(value) is str:
        return f"len={len(value)}"
    if type(value) in (bytes, bytearray):
        return f"bytes={len(value)}"
    if type(value) is dict:
        return f"keys={len(value)}"
    if type(value) in (list, tuple, set, frozenset):
        return f"items={len(value)}"
    return "scalar"


def describe(value) -> str:
    """Builtin type category, shape and digest for selected diagnostic paths.

    Replaces v1's `_describe`, which interpolated the value itself with no cap.
    """
    category = type(value).__name__ if type(value) in (
        str, bytes, bytearray, int, float, bool, type(None), dict, list, tuple, set, frozenset) else "object"
    return f"<{category} {_shape(value)} digest={digest(value)}>"


def describe_many(values, limit: int = 3) -> str:
    """The same, for a handful of values, with the total said plainly rather than implied."""
    items = list(values)
    shown = ", ".join(describe(v) for v in items[:limit])
    if len(items) > limit:
        shown += f", … ({len(items)} total)"
    elif not items:
        shown = "none"
    return shown


def positions(pairs, limit: int = 5) -> str:
    """Report WHERE something went wrong by position, never WHAT was there.

    `pairs` is an iterable of (position, value); the value is reduced to a digest.
    """
    items = list(pairs)
    shown = ", ".join(f"position {p} (digest={digest(v)})" for p, v in items[:limit])
    if len(items) > limit:
        shown += f", … ({len(items)} total)"
    elif not items:
        shown = "none"
    return shown


def counts(**kwargs) -> str:
    """Numbers only. For messages whose whole content is a tally."""
    for key, value in kwargs.items():
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"counts() takes ints only; {key} is {type(value).__name__}")
    return ", ".join(f"{k}={v}" for k, v in kwargs.items())
