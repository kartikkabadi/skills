#!/usr/bin/env python3
"""Render THIRD_PARTY_NOTICES.md from skills.provenance.json."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def render(manifest: dict[str, Any]) -> str:
    entries = manifest["skills"]
    groups: dict[tuple[str, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        source = entry.get("source")
        if source:
            key = (
                source["repository"],
                source.get("license", entry["license"]),
                source.get("license_file"),
            )
            groups[key].append(entry)

    lines = [
        "# Third-Party Notices",
        "",
        "This repository is a mixed-provenance collection. The root `LICENSE` applies only to entries whose `license_file` is `LICENSE` in `skills.provenance.json`. It does not relicense imported material.",
        "",
        "`skills.provenance.json` is the authoritative path-level record. It pins every source repository, revision, path, Git blob when applicable, local SHA-256 hash, license, attribution, modification status, and redistribution status.",
        "",
        "## Imported source families",
        "",
    ]

    for (repository, license_id, license_file), items in sorted(groups.items()):
        items = sorted(items, key=lambda item: item["name"])
        allowed = [item for item in items if item["redistribution"] == "allowed"]
        restricted = [item for item in items if item["redistribution"] == "restricted"]
        skill_list = ", ".join(f"`{item['name']}`" for item in items)

        lines.extend(
            [
                f"### `{repository}`",
                "",
                f"- License: `{license_id}`",
                (
                    f"- Preserved license text: `{license_file}`"
                    if license_file
                    else "- Preserved license text: none available upstream"
                ),
                f"- Skills: {skill_list}",
            ]
        )
        if allowed:
            noun = "entry" if len(allowed) == 1 else "entries"
            lines.append(
                f"- Redistribution: allowed under the stated upstream license for {len(allowed)} {noun}"
            )
        if restricted:
            noun = "entry" if len(restricted) == 1 else "entries"
            lines.append(f"- Redistribution: **restricted** for {len(restricted)} {noun}")

        lines.extend(
            [
                "",
                "| Skill | Classification | Pinned source | Modifications |",
                "|---|---|---|---|",
            ]
        )
        for item in items:
            source = item["source"]
            pin = f"`{source['ref']}` · `{source['path']}`"
            modifications = item["modifications"].replace("|", "\\|")
            lines.append(
                f"| `{item['name']}` | `{item['classification']}` | {pin} | {modifications} |"
            )
        lines.append("")

    restricted_entries = [
        item for item in entries if item["redistribution"] == "restricted"
    ]
    if restricted_entries:
        lines.extend(["## Restricted material", ""])
        for item in restricted_entries:
            source = item["source"]
            lines.append(
                f"- `{item['name']}` is byte-identical to `{source['repository']}` at "
                f"`{source['ref']}` (`{source['path']}`), but the upstream source declares no "
                "license. It is retained for private internal use only and must not be included "
                "in a public mirror, package, archive, or release without permission or a later "
                "upstream license grant."
            )
        lines.extend(
            [
                "",
                "No license in this repository grants redistribution rights for these entries.",
                "",
            ]
        )

    original = [item for item in entries if item["license_file"] == "LICENSE"]
    lines.extend(
        [
            "## Original and locally authored material",
            "",
            "The following entries are covered by the root MIT license:",
            "",
        ]
    )
    for item in original:
        lines.append(f"- `{item['name']}` — {item['attribution']}")

    lines.append("")
    names = {item["name"] for item in entries}
    if "how-to-code" in names:
        lines.extend(
            [
                "`how-to-code` is original skill text with explicit conceptual lineage to Mario Zechner and the MIT-licensed `earendil-works/pi` project. The pi license is preserved at `LICENSES/Earendil-pi-MIT.txt`.",
                "",
            ]
        )
    if "clean-code" in names:
        lines.extend(
            [
                "`clean-code` was independently rewritten during the provenance audit. The previous book-derived digest and its direct quotations are not licensed or redistributed by the current file.",
                "",
            ]
        )
    if "find-skills" in names:
        lines.extend(
            [
                "`find-skills` was independently rewritten during the provenance audit. The previous unlicensed upstream copy is not licensed or redistributed by the current file.",
                "",
            ]
        )
    lines.extend(
        [
            "## Source of truth",
            "",
            "When this document and a per-skill frontmatter field differ, use `skills.provenance.json` and the preserved upstream license text. Frontmatter is operational metadata and is not sufficient proof of ownership or permission.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository or export root",
    )
    parser.add_argument("--check", action="store_true", help="Fail if the notice is stale")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "skills.provenance.json").read_text(encoding="utf-8"))
    expected = render(manifest)
    output = root / "THIRD_PARTY_NOTICES.md"

    if args.check:
        try:
            actual = output.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"missing generated notice: {output}", file=sys.stderr)
            return 1
        if actual != expected:
            print(
                "THIRD_PARTY_NOTICES.md is stale; run python3 scripts/render_notices.py",
                file=sys.stderr,
            )
            return 1
        print("THIRD_PARTY_NOTICES.md is current")
        return 0

    output.write_text(expected, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
