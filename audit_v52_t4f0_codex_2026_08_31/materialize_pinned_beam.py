#!/usr/bin/env python3
"""Materialize audit-relevant BEAM files at one pinned Git commit.

This script downloads no model outputs and performs no retrieval.  It verifies
every downloaded byte against the Git blob id reported by the pinned recursive
tree before accepting the local file.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


REPO = "mohammadtavakoli78/BEAM"
PINNED_COMMIT = "3e12035532eb85768f1a7cd779832b650c4b2ef9"
CHAT_RE = re.compile(r"^chats/(100K|500K|1M|10M)/([^/]+)/chat\.json$")
QUESTION_RE = re.compile(
    r"^chats/(100K|500K|1M|10M)/([^/]+)/probing_questions/probing_questions\.json$"
)
SOURCE_PATHS = {
    "README.md",
    "src/prompts.py",
    "src/beam/main.py",
    "src/beam/ten_milion_pipeline.py",
    "src/beam/download_dataset.py",
}


def request_bytes(url: str, attempts: int = 5) -> bytes:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "V52-Task-4F0-independent-audit",
                    "Accept": "application/vnd.github+json",
                },
            )
            with urllib.request.urlopen(req, timeout=180) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"download failed after {attempts} attempts: {url}: {last}")


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    tree_url = f"https://api.github.com/repos/{REPO}/git/trees/{PINNED_COMMIT}?recursive=1"
    tree_bytes = request_bytes(tree_url)
    tree = json.loads(tree_bytes)
    if tree.get("sha") != PINNED_COMMIT or tree.get("truncated") is not False:
        raise RuntimeError(
            f"unexpected tree response: sha={tree.get('sha')} truncated={tree.get('truncated')}"
        )
    blobs = {
        row["path"]: row
        for row in tree["tree"]
        if row.get("type") == "blob" and isinstance(row.get("path"), str)
    }
    selected = {
        path: row
        for path, row in blobs.items()
        if CHAT_RE.match(path) or QUESTION_RE.match(path) or path in SOURCE_PATHS
    }

    tree_manifest = {
        "repository": REPO,
        "commit": PINNED_COMMIT,
        "tree_response_sha256": hashlib.sha256(tree_bytes).hexdigest(),
        "recursive_tree_truncated": tree["truncated"],
        "recursive_blob_count": len(blobs),
        "selected_blob_count": len(selected),
        "selected_total_bytes": sum(int(row["size"]) for row in selected.values()),
        "selected": [
            {
                "path": path,
                "git_blob_sha1": row["sha"],
                "size": row["size"],
            }
            for path, row in sorted(selected.items())
        ],
    }
    (args.output / "pinned_tree_manifest.json").write_text(
        json.dumps(tree_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    def fetch_one(item: tuple[str, dict]) -> dict:
        path, row = item
        url = f"https://raw.githubusercontent.com/{REPO}/{PINNED_COMMIT}/{path}"
        data = request_bytes(url)
        actual_blob = git_blob_sha1(data)
        actual_sha256 = hashlib.sha256(data).hexdigest()
        target = args.output / "corpus" / Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if len(data) != int(row["size"]) or actual_blob != row["sha"]:
            return {
                "path": path,
                "status": "FAIL_IDENTITY",
                "expected_size": row["size"],
                "actual_size": len(data),
                "expected_git_blob_sha1": row["sha"],
                "actual_git_blob_sha1": actual_blob,
                "sha256": actual_sha256,
            }
        target.write_bytes(data)
        return {
            "path": path,
            "status": "PASS",
            "size": len(data),
            "git_blob_sha1": actual_blob,
            "sha256": actual_sha256,
        }

    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch_one, item) for item in sorted(selected.items())]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            results.append(result)
            print(f"[{index}/{len(futures)}] {result['status']} {result['path']}", flush=True)

    results.sort(key=lambda row: row["path"])
    summary = {
        "repository": REPO,
        "commit": PINNED_COMMIT,
        "selected_files": len(results),
        "passed_files": sum(row["status"] == "PASS" for row in results),
        "failed_files": sum(row["status"] != "PASS" for row in results),
        "total_verified_bytes": sum(row.get("size", 0) for row in results),
        "results": results,
    }
    (args.output / "materialization_hash_log.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if summary["failed_files"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
