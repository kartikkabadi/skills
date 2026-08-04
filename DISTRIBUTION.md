# Distribution Policy

This is a private mixed-provenance skill collection. Possession of a file in this repository does not by itself establish authorship or permission to redistribute it.

## Publicly redistributable set

A skill may be included in a public mirror, package, archive, or release only when its entry in `skills.provenance.json` has:

- `redistribution: allowed`
- a recognized license identifier
- a preserved `license_file`
- complete source and attribution information when it is imported or adapted
- a `local_sha256` matching the distributed file

The public export must also include:

- `LICENSE`
- `LICENSES/`
- `THIRD_PARTY_NOTICES.md`
- `skills.provenance.json`

Do not describe the complete collection as MIT. The root MIT license covers only entries whose manifest record points to the root `LICENSE`. Imported skills retain their own upstream terms.

## Restricted set

A skill with `redistribution: restricted` is for private internal use only. It must be excluded from every public export unless its copyright holder grants permission or the upstream project publishes a license that permits redistribution.

Current restricted entries: **none**.

The previous unlicensed `find-skills` copy was replaced with independently written material. The restriction mechanism remains mandatory for any future entry whose permission is missing or unclear.

Do not infer permission from public GitHub visibility, popularity, installation tooling, or copies in third-party registries.

## Modifying imported skills

When an imported skill is modified:

1. Change its classification from `third-party-exact` to `third-party-adapted`.
2. Preserve its upstream source revision, source path, attribution, and license.
3. Describe the local modifications precisely.
4. Recalculate `local_sha256`.
5. Confirm that the upstream license permits derivative works and that its notice obligations are preserved.

Never replace an upstream copyright notice with Kartik's name.

## Adding a skill

Before committing a new skill:

1. Identify whether it is original, imported, or adapted.
2. Locate the authoritative source repository rather than a registry mirror.
3. Pin the exact source commit and path.
4. Verify the upstream license from an actual license file or authoritative grant.
5. Preserve the required license text in `LICENSES/`.
6. Add one complete entry to `skills.provenance.json`.
7. Mark unlicensed or unclear material as restricted, or do not add it.
8. Run the provenance verifier.

Frontmatter fields such as `author` and `license` are useful metadata but are not sufficient evidence on their own.

## Private installation

A private installation may copy all current skill directories. If a future restricted entry is added, it may be retained only for the specifically authorized internal use recorded in its provenance entry and must not be republished.

Public distribution must use the manifest-controlled export path. The exporter includes all currently allowed entries and will exclude any future restricted entry automatically.
