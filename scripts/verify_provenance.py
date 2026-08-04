#!/usr/bin/env python3
"""Verify the skill provenance manifest and its local legal files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SKILL_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
CLASSIFICATIONS = {
    "original",
    "original-adaptation",
    "third-party-exact",
    "third-party-adapted",
    "third-party-restricted",
}
REDISTRIBUTION = {"allowed", "restricted"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository or export root to verify",
    )
    return parser.parse_args()


def require_string(errors: list[str], value: Any, label: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return False
    return True


def require_safe_relative_path(errors: list[str], value: Any, label: str) -> bool:
    if not require_string(errors, value, label):
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        errors.append(f"{label} must be a normalized relative path without traversal")
        return False
    return True


def verify_local_file(errors: list[str], root: Path, relative: str, label: str) -> Path | None:
    path = root / relative
    if path.is_symlink() or path.parent.is_symlink():
        errors.append(f"{label} must not be a symlink: {relative}")
        return None
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError:
        errors.append(f"missing {label}: {relative}")
        return None
    if root != resolved and root not in resolved.parents:
        errors.append(f"{label} escapes the verification root: {relative}")
        return None
    if not resolved.is_file():
        errors.append(f"{label} is not a regular file: {relative}")
        return None
    return resolved


def verify_source(
    errors: list[str],
    source: Any,
    label: str,
    *,
    require_blob: bool,
    require_hash: bool,
    require_license: bool = True,
) -> None:
    if not isinstance(source, dict):
        errors.append(f"{label}.source must be an object")
        return

    for field in ("repository", "ref", "path"):
        require_string(errors, source.get(field), f"{label}.source.{field}")
    if require_license:
        require_string(errors, source.get("license"), f"{label}.source.license")

    ref = source.get("ref")
    if isinstance(ref, str) and not HEX40.fullmatch(ref):
        errors.append(f"{label}.source.ref must be a 40-character lowercase Git SHA")

    blob = source.get("blob")
    if require_blob:
        if not isinstance(blob, str) or not HEX40.fullmatch(blob):
            errors.append(f"{label}.source.blob must be a 40-character lowercase Git blob SHA")
    elif blob is not None and (not isinstance(blob, str) or not HEX40.fullmatch(blob)):
        errors.append(f"{label}.source.blob must be null or a 40-character lowercase Git blob SHA")

    source_hash = source.get("sha256")
    if require_hash:
        if not isinstance(source_hash, str) or not HEX64.fullmatch(source_hash):
            errors.append(f"{label}.source.sha256 must be a 64-character lowercase SHA-256")
    elif source_hash is not None and (
        not isinstance(source_hash, str) or not HEX64.fullmatch(source_hash)
    ):
        errors.append(f"{label}.source.sha256 must be null or a 64-character lowercase SHA-256")

    license_file = source.get("license_file")
    if license_file is not None and not isinstance(license_file, str):
        errors.append(f"{label}.source.license_file must be a string or null")


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    manifest_path = root / "skills.provenance.json"
    errors: list[str] = []

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: missing {manifest_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {manifest_path}: {exc}", file=sys.stderr)
        return 1

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    require_string(errors, manifest.get("repository"), "repository")

    license_records = manifest.get("license_files")
    if not isinstance(license_records, list):
        errors.append("license_files must be an array")
        license_records = []

    license_paths: set[str] = set()
    license_record_by_path: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(license_records):
        label = f"license_files[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        path_value = record.get("path")
        if not require_safe_relative_path(errors, path_value, f"{label}.path"):
            continue
        if path_value != "LICENSE" and not path_value.startswith("LICENSES/"):
            errors.append(f"{label}.path must be LICENSE or a file under LICENSES/")
        if path_value in license_paths:
            errors.append(f"duplicate license file record: {path_value}")
        license_paths.add(path_value)
        license_record_by_path[path_value] = record
        path = verify_local_file(errors, root, path_value, "license file")
        if path is not None:
            actual_hash = digest(path)
            expected_hash = record.get("sha256")
            if actual_hash != expected_hash:
                errors.append(
                    f"license hash mismatch for {path_value}: expected {expected_hash}, got {actual_hash}"
                )
        source = record.get("source")
        if path_value == "LICENSE":
            if source is not None:
                errors.append("root LICENSE record must not claim an upstream source")
        else:
            verify_source(
                errors,
                source,
                label,
                require_blob=True,
                require_hash=True,
                require_license=False,
            )
            if isinstance(source, dict) and source.get("sha256") != record.get("sha256"):
                errors.append(f"{label}.source.sha256 must equal the preserved local license hash")

    actual_license_files = set()
    for path in (root / "LICENSES").glob("*"):
        if path.is_symlink():
            errors.append(f"LICENSES/ must not contain symlinks: {path.name}")
        elif path.is_file():
            actual_license_files.add(str(path.relative_to(root)))
    expected_license_files = {path for path in license_paths if path.startswith("LICENSES/")}
    if actual_license_files != expected_license_files:
        missing = sorted(expected_license_files - actual_license_files)
        extra = sorted(actual_license_files - expected_license_files)
        if missing:
            errors.append(f"license files missing from disk: {missing}")
        if extra:
            errors.append(f"unmanifested files in LICENSES/: {extra}")

    entries = manifest.get("skills")
    if not isinstance(entries, list):
        errors.append("skills must be an array")
        entries = []

    names: list[str] = []
    manifest_paths: set[str] = set()
    for index, item in enumerate(entries):
        label = f"skills[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue

        name = item.get("name")
        path_value = item.get("path")
        if not require_string(errors, name, f"{label}.name"):
            continue
        names.append(name)
        if not SKILL_NAME.fullmatch(name):
            errors.append(f"{label}.name must use lowercase letters, digits, and internal hyphens")
        expected_path = f"{name}/SKILL.md"
        if not require_safe_relative_path(errors, path_value, f"{label}.path"):
            continue
        if path_value != expected_path:
            errors.append(f"{label}.path must equal {expected_path!r}")
            continue
        if path_value in manifest_paths:
            errors.append(f"duplicate skill path: {path_value}")
        manifest_paths.add(path_value)

        classification = item.get("classification")
        redistribution = item.get("redistribution")
        license_id = item.get("license")
        license_file = item.get("license_file")
        source = item.get("source")

        if classification not in CLASSIFICATIONS:
            errors.append(f"{label}.classification is invalid: {classification!r}")
        if redistribution not in REDISTRIBUTION:
            errors.append(f"{label}.redistribution is invalid: {redistribution!r}")
        require_string(errors, license_id, f"{label}.license")
        require_string(errors, item.get("attribution"), f"{label}.attribution")
        require_string(errors, item.get("modifications"), f"{label}.modifications")

        skill_dir = root / name
        if skill_dir.is_symlink():
            errors.append(f"skill directory must not be a symlink: {name}")
            continue
        skill_path = verify_local_file(errors, root, path_value, "skill file")
        if skill_path is None:
            continue
        actual_hash = digest(skill_path)
        expected_hash = item.get("local_sha256")
        if not isinstance(expected_hash, str) or not HEX64.fullmatch(expected_hash):
            errors.append(f"{label}.local_sha256 must be a 64-character lowercase SHA-256")
        elif actual_hash != expected_hash:
            errors.append(
                f"skill hash mismatch for {name}: expected {expected_hash}, got {actual_hash}"
            )

        if license_file is not None and license_file not in license_paths:
            errors.append(f"{label}.license_file is not present in license_files: {license_file!r}")

        if redistribution == "allowed":
            if license_id == "NOASSERTION":
                errors.append(f"{label} cannot be redistributable with license NOASSERTION")
            if not isinstance(license_file, str):
                errors.append(f"{label} must reference a local license_file")
        elif redistribution == "restricted":
            if classification != "third-party-restricted":
                errors.append(f"{label} restricted entries must use third-party-restricted")
            if license_id != "NOASSERTION":
                errors.append(f"{label} restricted entries must use license NOASSERTION")
            if license_file is not None:
                errors.append(f"{label} restricted entries must not inherit a local license_file")

        if classification == "original":
            if source is not None:
                errors.append(f"{label} original entries must not claim an upstream source")
            if license_file != "LICENSE":
                errors.append(f"{label} original entries must use the root LICENSE")
        elif classification == "original-adaptation":
            if license_file != "LICENSE":
                errors.append(f"{label} original adaptations must use the root LICENSE")
            verify_source(errors, source, label, require_blob=False, require_hash=False)
            if isinstance(source, dict):
                source_license_file = source.get("license_file")
                if source_license_file not in license_paths:
                    errors.append(
                        f"{label}.source.license_file is not preserved locally: {source_license_file!r}"
                    )
                else:
                    license_source = license_record_by_path[source_license_file].get("source")
                    if not isinstance(license_source, dict) or license_source.get("repository") != source.get("repository"):
                        errors.append(
                            f"{label}.source.license_file must be pinned from the same upstream repository"
                        )
        elif classification == "third-party-exact":
            if license_file == "LICENSE":
                errors.append(f"{label} exact third-party imports cannot use the root LICENSE")
            verify_source(errors, source, label, require_blob=True, require_hash=True)
            if isinstance(source, dict):
                if source.get("sha256") != actual_hash:
                    errors.append(f"{label} exact import source hash must equal the local skill hash")
                if source.get("license") != license_id or source.get("license_file") != license_file:
                    errors.append(f"{label} must preserve the same upstream license and license_file")
                license_source = license_record_by_path.get(license_file, {}).get("source")
                if not isinstance(license_source, dict) or license_source.get("repository") != source.get("repository"):
                    errors.append(f"{label}.license_file must be pinned from the same upstream repository")
        elif classification == "third-party-adapted":
            if license_file == "LICENSE":
                errors.append(f"{label} adapted third-party imports cannot use the root LICENSE")
            verify_source(errors, source, label, require_blob=True, require_hash=True)
            if isinstance(source, dict):
                if source.get("sha256") == actual_hash:
                    errors.append(f"{label} adapted import must not be byte-identical to its source")
                if source.get("license") != license_id or source.get("license_file") != license_file:
                    errors.append(f"{label} must preserve the same upstream license and license_file")
                license_source = license_record_by_path.get(license_file, {}).get("source")
                if not isinstance(license_source, dict) or license_source.get("repository") != source.get("repository"):
                    errors.append(f"{label}.license_file must be pinned from the same upstream repository")
        elif classification == "third-party-restricted":
            verify_source(errors, source, label, require_blob=True, require_hash=True)
            if isinstance(source, dict):
                if source.get("license") != "NOASSERTION":
                    errors.append(f"{label}.source.license must be NOASSERTION")
                if source.get("license_file") is not None:
                    errors.append(f"{label}.source.license_file must be null")
                if source.get("sha256") != actual_hash:
                    errors.append(f"{label} restricted exact source hash must equal local hash")

    if names != sorted(names):
        errors.append("skills entries must be sorted by name")
    if len(names) != len(set(names)):
        errors.append("skills entries contain duplicate names")

    actual_skill_paths = {
        str(path.relative_to(root))
        for path in root.glob("*/SKILL.md")
        if path.is_file()
    }
    if actual_skill_paths != manifest_paths:
        unmanifested = sorted(actual_skill_paths - manifest_paths)
        missing = sorted(manifest_paths - actual_skill_paths)
        if unmanifested:
            errors.append(f"skill files missing from manifest: {unmanifested}")
        if missing:
            errors.append(f"manifest paths missing from disk: {missing}")

    for required in ("LICENSE", "THIRD_PARTY_NOTICES.md", "DISTRIBUTION.md"):
        verify_local_file(errors, root, required, "required legal file")

    if errors:
        print("provenance verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    counts: dict[str, int] = {}
    for item in entries:
        counts[item["classification"]] = counts.get(item["classification"], 0) + 1
    summary = ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
    print(f"verified {len(entries)} skills and {len(license_records)} license files ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
