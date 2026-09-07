# Authoring the skill

Conventions for writing the output skill so any harness can load it and a
fresh agent can follow it cold.

## Placement and naming

- Default location: `~/.agents/skills/<name>/` (the shared skills dir that
  harnesses symlink into). Use another directory only when the user names one.
- Name = folder name. Lowercase letters, digits, hyphens; under 64 chars;
  short and action/domain-oriented (`x-growth`, `link-to-skill`,
  `coast-export`).
- One folder per skill: required `SKILL.md`, optional `scripts/`,
  `references/`, `assets/`, `agents/`.

## SKILL.md

Frontmatter — keep it minimal:

```yaml
---
name: skill-name
description: "What it does. When it triggers. One boundary: when NOT to use."
---
```

- `name` and `description` are required. Strict validators (e.g. the Codex
  `quick_validate.py`) allow only `name`, `description`, `license`,
  `metadata`, `allowed-tools` — keys like `platforms` get rejected, so leave
  them out.
- The description is the routing surface: it is read BEFORE the body loads.
  Make it discriminating — a sibling skill with an overlapping trigger should
  lose. Name the sibling explicitly when helpful ("Not for X — use other-skill").

Body:

- Purpose in one short paragraph, then the workflow, real constraints, and
  links to references. Keep the entrypoint as short as the task permits.
- Assume the agent is already capable. Include only what changes its
  decisions: exact commands, non-obvious ordering, earned pitfalls, domain
  invariants. Cut generic advice, speculative edge cases, and restated
  policies the host already enforces.
- Match specificity to risk. Fixed sequences and absolute language are for
  fragile or dangerous steps; open-ended work gets outcome + decision
  criteria.
- Do not turn one example or one past failure into a universal rule. Encode
  what generalized.

## Progressive disclosure

- `references/<topic>.md` for detail needed only in some modes (per-source
  recipes, pattern tables, schemas). Link each reference from SKILL.md at the
  point it becomes relevant — no orphan files, no load-everything rule.
- `scripts/` for deterministic logic worth not re-deriving (this skill's
  `scripts/clean_captions.py` is the model: one file, does one thing,
  runnable without reading it).
- `assets/` for files that belong in generated output, not instructions.
- No README.md, changelog, or docs the skill does not use at runtime.

## Source fidelity

- The skill encodes the source's playbook, not a summary of it. Rules go in
  as operational instructions ("Share the workflow in full"), not book-report
  prose ("The author believes sharing is good").
- Distinguish *source-claimed* from *synthesized extension* while drafting;
  extensions are allowed (they make the advice usable) but never fabricate
  the source's results, metrics, or credentials.
- Never inject memory, prior sessions, or the user's other projects into the
  skill's content. Provenance note in the file is fine; contamination is not.

## Guardrails

When the skill's domain touches the outside world (posting, replies, DMs,
purchases, public repos, account changes), end SKILL.md with a Guardrails
section:

- Drafts/plans only by default; explicit approval before external action.
- No fabricated metrics, followers, or results in generated drafts.
- Preserve the user's voice and existing authorization boundaries.

## Validation

- Run the harness's skill validator when one exists. If none exists, at
  minimum: frontmatter parses, `name` matches the folder, every `references/`
  and `scripts/` link in SKILL.md resolves, any script executes on a trivial
  input.
- Re-read the final SKILL.md as a cold agent would: is the first action
  unambiguous? Is the stopping condition clear?
- Delete all scratch. The skill directory is the only surviving artifact.
