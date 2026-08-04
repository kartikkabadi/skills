#!/usr/bin/env python3
"""Verify pinned GitHub source files and license texts against upstream."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class FilePin:
    repository: str
    ref: str
    path: str
    blob: str
    sha256: str


@dataclass(frozen=True)
class CommitPin:
    repository: str
    ref: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root",
    )
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def request(url: str, *, accept: str | None = None) -> bytes:
    headers = {"User-Agent": "kartikkabadi-skills-provenance-v1"}
    if accept:
        headers["Accept"] = accept
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=30
            ) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(0.5 * (2**attempt))
    assert last_error is not None
    raise last_error


def validate_file_pin(pin: FilePin) -> list[str]:
    errors: list[str] = []
    if not REPOSITORY.fullmatch(pin.repository):
        return [f"invalid GitHub repository name: {pin.repository!r}"]
    if not HEX40.fullmatch(pin.ref):
        return [f"invalid Git ref for {pin.repository}: {pin.ref!r}"]
    if not HEX40.fullmatch(pin.blob):
        return [f"invalid Git blob for {pin.repository}:{pin.path}: {pin.blob!r}"]
    if not HEX64.fullmatch(pin.sha256):
        return [f"invalid SHA-256 for {pin.repository}:{pin.path}: {pin.sha256!r}"]

    encoded_path = "/".join(
        urllib.parse.quote(segment, safe="") for segment in pin.path.split("/")
    )
    url = f"https://raw.githubusercontent.com/{pin.repository}/{pin.ref}/{encoded_path}"
    try:
        content = request(url)
    except Exception as exc:
        return [f"failed to fetch {pin.repository}@{pin.ref}:{pin.path}: {exc}"]

    actual_sha256 = hashlib.sha256(content).hexdigest()
    actual_blob = hashlib.sha1(
        f"blob {len(content)}\0".encode("ascii") + content,
        usedforsecurity=False,
    ).hexdigest()
    if actual_sha256 != pin.sha256:
        errors.append(
            f"upstream SHA-256 mismatch for {pin.repository}@{pin.ref}:{pin.path}: "
            f"expected {pin.sha256}, got {actual_sha256}"
        )
    if actual_blob != pin.blob:
        errors.append(
            f"upstream Git blob mismatch for {pin.repository}@{pin.ref}:{pin.path}: "
            f"expected {pin.blob}, got {actual_blob}"
        )
    return errors


def validate_commit_pin(pin: CommitPin) -> list[str]:
    if not REPOSITORY.fullmatch(pin.repository):
        return [f"invalid GitHub repository name: {pin.repository!r}"]
    if not HEX40.fullmatch(pin.ref):
        return [f"invalid Git ref for {pin.repository}: {pin.ref!r}"]

    repository = urllib.parse.quote(pin.repository, safe="/")
    url = f"https://api.github.com/repos/{repository}/commits/{pin.ref}"
    try:
        payload = json.loads(request(url, accept="application/vnd.github+json"))
    except Exception as exc:
        return [f"failed to verify commit {pin.repository}@{pin.ref}: {exc}"]
    if payload.get("sha") != pin.ref:
        return [
            f"GitHub returned unexpected commit for {pin.repository}@{pin.ref}: "
            f"{payload.get('sha')!r}"
        ]
    return []


def source_to_pins(
    source: dict[str, Any],
    file_pins: set[FilePin],
    commit_pins: set[CommitPin],
) -> None:
    blob = source.get("blob")
    source_hash = source.get("sha256")
    if blob is not None and source_hash is not None:
        file_pins.add(
            FilePin(
                repository=source["repository"],
                ref=source["ref"],
                path=source["path"],
                blob=blob,
                sha256=source_hash,
            )
        )
    else:
        commit_pins.add(
            CommitPin(repository=source["repository"], ref=source["ref"])
        )


def main() -> int:
    args = parse_args()
    if args.workers < 1 or args.workers > 32:
        print("--workers must be between 1 and 32", file=sys.stderr)
        return 1

    root = args.root.resolve()
    manifest = json.loads(
        (root / "skills.provenance.json").read_text(encoding="utf-8")
    )
    file_pins: set[FilePin] = set()
    commit_pins: set[CommitPin] = set()

    for record in manifest["license_files"]:
        source = record.get("source")
        if source:
            source_to_pins(source, file_pins, commit_pins)
    for entry in manifest["skills"]:
        source = entry.get("source")
        if source:
            source_to_pins(source, file_pins, commit_pins)

    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(validate_file_pin, pin): pin
            for pin in sorted(
                file_pins,
                key=lambda item: (item.repository.lower(), item.ref, item.path),
            )
        }
        for future in as_completed(futures):
            try:
                errors.extend(future.result())
            except Exception as exc:
                pin = futures[future]
                errors.append(
                    f"unexpected verification failure for {pin.repository}:{pin.path}: {exc}"
                )

    for pin in sorted(commit_pins, key=lambda item: (item.repository.lower(), item.ref)):
        errors.extend(validate_commit_pin(pin))

    if errors:
        print("upstream provenance verification failed:", file=sys.stderr)
        for error in sorted(errors):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"verified {len(file_pins)} pinned upstream files and "
        f"{len(commit_pins)} commit-only source references"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
