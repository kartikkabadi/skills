---
name: link-to-skill
description: "Turn any link — X/Twitter post or video, YouTube video, article, podcast, or other media — into a standalone agent skill. Extracts or transcribes the source, distills its actionable playbook, and authors a validated SKILL.md package in the user's skills directory. Use when the user wants a link's content converted into a reusable skill. Not for plain transcripts (transcript-to-markdown) or research digests (link-research)."
---

# Link to Skill

One pipeline: link in, skill out. The transcript or article text is evidence —
the deliverable is a working skill another agent can load and follow without
ever seeing the source.

## Pipeline

1. **Classify** the link: X/Twitter (status URL or direct `video.twimg.com`
   media), YouTube, article/blog, audio/podcast, local file, other.
2. **Extract** the source content using the per-source recipe in
   [references/sources.md](references/sources.md). End state: clean text on
   disk in the scratch dir, sanity-checked (word count ≈ minutes × 130–190).
3. **Distill** the playbook (below).
4. **Author** the skill per [references/authoring.md](references/authoring.md).
5. **Validate and clean up** (below), then report.

## Distill the playbook

A skill is not a summary. Before writing, answer:

- **What does this content make an agent DO differently?** Workflows, rules,
  constraints, decision criteria — that is the skill. Opinions and motivation
  alone are not skill material; if the source is thin, say so and propose the
  right artifact instead (or ask the user).
- **What is claimed vs. demonstrated?** Mark each rule as *source-claimed* or
  *synthesized extension* in your working notes. The skill may extend and
  operationalize, but never fabricate the source's results or credentials.
- **Source fidelity (non-negotiable):** the distilled content contains only
  what the source says. No background from memory, prior sessions, or the
  user's other projects. Shared context passed to helpers = spelling
  conventions only.
- Read the WHOLE extraction — page through the file; no first-page summaries.

## Author the skill

- Location: `~/.agents/skills/<name>/` unless the user names another skills
  directory. Name = folder name: lowercase letters, digits, hyphens, short and
  action/domain-oriented.
- `SKILL.md` frontmatter: `name` and `description` only. The description must
  say what it does, when it triggers, and one boundary (when NOT to use).
  Extra keys can fail strict validators — keep them out.
- Body: purpose, the workflow, real constraints, and links into `references/`.
  Assume the agent is capable — include only what changes its decisions:
  exact commands, non-obvious ordering, earned pitfalls, guardrails.
- Progressive disclosure: mode/source detail → `references/`; deterministic
  reusable logic → `scripts/` (this skill's own
  `scripts/clean_captions.py` is the model); output boilerplate → `assets/`.
- If the domain has external side effects (posting, DMs, purchases, public
  repos), the skill needs a Guardrails section: drafts-only by default,
  explicit approval before any external action, no fabricated metrics.
- Full conventions: [references/authoring.md](references/authoring.md).

## Validate and clean up

- Re-read the written `SKILL.md`: frontmatter parses, every linked file
  exists, the description would route a fresh agent correctly.
- Run a skill validator if the harness has one (e.g. a `quick_validate.py`
  under a skill-creator install). Check scripts actually run.
- Delete the entire scratch dir. The only surviving artifact is the new
  skill directory — the chat reply is the summary.
- Report: skill path, what it encodes, what was verified, what remains.

## Pitfalls

- Direct `video.twimg.com` URLs 401 without `Referer: https://x.com/` and a
  browser User-Agent. That is expected, not a dead link.
- The media snowflake in a twimg path is NOT the tweet ID. Use the full
  status URL for API lookups.
- Never naive-flatten VTT — rolling captions triple the text. Use
  `scripts/clean_captions.py` (keeps only `<c>`-tagged cues).
- Whisper: only use models already at `~/.local/share/whisper/`; never
  download new ones. Output files appear only when the process exits — wait,
  do not tail.
- Login walls (X timeline, replies) mean the shared browser session is
  logged out — use public APIs (fxtwitter, syndication) instead of asking
  for credentials.
- A transcript longer than ~3,000 words should not be distilled in a single
  subagent pass — split at chapter/section granularity.
- Do not promise "viral" outcomes in generated skill text — encode the
  tactic, not the guarantee.
