#!/usr/bin/env python3
"""Create a public skill export that excludes restricted material."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from render_notices import render

MARKER = ".skills-public-export"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="Directory to create")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output only when it carries the export marker",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Source repository root",
    )
    return parser.parse_args()


def reject_symlinks(path: Path) -> None:
    for candidate in [path, *path.rglob("*")]:
        if candidate.is_symlink():
            raise RuntimeError(f"refusing to export symlink: {candidate}")


def public_readme(manifest: dict) -> str:
    entries = manifest["skills"]
    lines = [
        "# Agent Skills — Public Export",
        "",
        f"This export contains {len(entries)} skills whose provenance records permit redistribution.",
        "",
        "It was generated from `kartikkabadi/skills` using `scripts/export_public.py`. Restricted internal-only entries were excluded. The collection is mixed-provenance; do not treat every skill as Kartik-authored or as covered by one blanket license.",
        "",
        "See:",
        "",
        "- `skills.provenance.json` for the authoritative path-level source and license record",
        "- `THIRD_PARTY_NOTICES.md` for readable attribution",
        "- `LICENSES/` for preserved upstream license texts",
        "- `DISTRIBUTION.md` for distribution rules",
        "",
        "## Included skills",
        "",
        "| Skill | Classification | License | Source |",
        "|---|---|---|---|",
    ]
    for entry in entries:
        source = entry.get("source")
        source_name = source["repository"] if source else "Kartik Kabadi"
        lines.append(
            f"| `{entry['name']}` | `{entry['classification']}` | `{entry['license']}` | `{source_name}` |"
        )
    lines.append("")
    return "\n".join(lines)


def validate_output_location(root: Path, output: Path) -> None:
    if output == root or output in root.parents:
        raise RuntimeError("refusing to export over the source repository or one of its parents")

    if root in output.parents:
        relative = output.relative_to(root)
        if not relative.parts or relative.parts[0] != "dist":
            raise RuntimeError("exports inside the repository must be placed under dist/")


def prepare_output(output: Path, force: bool) -> None:
    if not output.exists():
        return
    if output.is_symlink():
        raise RuntimeError(f"refusing to replace symlink output: {output}")
    if not force:
        raise RuntimeError(f"output already exists: {output}; pass --force to replace it")

    marker = output / MARKER
    if marker.is_symlink() or not marker.is_file():
        raise RuntimeError(
            f"refusing to remove unmarked directory: {output}; expected regular file {marker}"
        )
    shutil.rmtree(output)


def build_export(root: Path, destination: Path, manifest: dict) -> tuple[int, list[str]]:
    allowed = [entry for entry in manifest["skills"] if entry["redistribution"] == "allowed"]
    restricted = [entry for entry in manifest["skills"] if entry["redistribution"] != "allowed"]
    if not restricted:
        print("warning: manifest contains no restricted entries", file=sys.stderr)

    referenced_licenses = {"LICENSE"}
    for entry in allowed:
        if entry.get("license_file"):
            referenced_licenses.add(entry["license_file"])
        source = entry.get("source")
        if source and source.get("license_file"):
            referenced_licenses.add(source["license_file"])

    license_records = [
        record
        for record in manifest["license_files"]
        if record["path"] in referenced_licenses
    ]
    recorded = {record["path"] for record in license_records}
    if recorded != referenced_licenses:
        missing = sorted(referenced_licenses - recorded)
        raise RuntimeError(f"manifest lacks referenced license records: {missing}")

    for entry in allowed:
        source_dir = root / entry["name"]
        reject_symlinks(source_dir)
        shutil.copytree(source_dir, destination / entry["name"])

    for license_path in sorted(referenced_licenses):
        source_file = root / license_path
        reject_symlinks(source_file)
        target = destination / license_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)

    source_distribution = root / "DISTRIBUTION.md"
    reject_symlinks(source_distribution)
    shutil.copy2(source_distribution, destination / "DISTRIBUTION.md")

    public_manifest = {
        **manifest,
        "export": {
            "type": "public",
            "restricted_entries_excluded": [entry["name"] for entry in restricted],
        },
        "license_files": license_records,
        "skills": allowed,
    }
    (destination / "skills.provenance.json").write_text(
        json.dumps(public_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (destination / "THIRD_PARTY_NOTICES.md").write_text(
        render(public_manifest), encoding="utf-8"
    )
    (destination / "README.md").write_text(
        public_readme(public_manifest), encoding="utf-8"
    )
    (destination / MARKER).write_text(
        json.dumps(
            {
                "format": "kartikkabadi-skills-public-export-v1",
                "included_skills": len(allowed),
                "excluded_skills": [entry["name"] for entry in restricted],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return len(allowed), [entry["name"] for entry in restricted]


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    output = args.output.expanduser().resolve()

    try:
        validate_output_location(root, output)
        verifier = root / "scripts" / "verify_provenance.py"
        subprocess.run(
            [sys.executable, str(verifier), "--root", str(root)],
            check=True,
        )
        prepare_output(output, args.force)

        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent)
        )
        try:
            manifest = json.loads(
                (root / "skills.provenance.json").read_text(encoding="utf-8")
            )
            included, excluded = build_export(root, staging, manifest)
            os.replace(staging, output)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"exported {included} skills to {output}; excluded: " + ", ".join(excluded)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
