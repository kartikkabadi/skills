#!/usr/bin/env python3
"""Create a public skill export that excludes restricted material."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from render_notices import render


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="Directory to create")
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory")
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


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()

    if output == root:
        print("refusing to export over the source repository", file=sys.stderr)
        return 1
    if output.exists():
        if not args.force:
            print(f"output already exists: {output}; pass --force to replace it", file=sys.stderr)
            return 1
        if output.is_symlink():
            print(f"refusing to replace symlink output: {output}", file=sys.stderr)
            return 1
        shutil.rmtree(output)

    manifest = json.loads((root / "skills.provenance.json").read_text(encoding="utf-8"))
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
    if {record["path"] for record in license_records} != referenced_licenses:
        missing = sorted(referenced_licenses - {record["path"] for record in license_records})
        raise RuntimeError(f"manifest lacks referenced license records: {missing}")

    output.mkdir(parents=True)
    for entry in allowed:
        source_dir = root / entry["name"]
        reject_symlinks(source_dir)
        shutil.copytree(source_dir, output / entry["name"])

    for license_path in sorted(referenced_licenses):
        source_file = root / license_path
        reject_symlinks(source_file)
        destination = output / license_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)

    for name in ("DISTRIBUTION.md",):
        source_file = root / name
        reject_symlinks(source_file)
        shutil.copy2(source_file, output / name)

    public_manifest = {
        **manifest,
        "export": {
            "type": "public",
            "restricted_entries_excluded": [entry["name"] for entry in restricted],
        },
        "license_files": license_records,
        "skills": allowed,
    }
    (output / "skills.provenance.json").write_text(
        json.dumps(public_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output / "THIRD_PARTY_NOTICES.md").write_text(
        render(public_manifest), encoding="utf-8"
    )
    (output / "README.md").write_text(public_readme(public_manifest), encoding="utf-8")

    print(
        f"exported {len(allowed)} skills to {output}; excluded: "
        + ", ".join(entry["name"] for entry in restricted)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
