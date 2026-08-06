---
name: private-intelligence-reader
description: Build private, source-grounded personal intelligence readers from feeds, vault notes, summaries, and source bundles with validation gates, anti-slop UI, and explicit public-publishing boundaries.
version: 1.0.0-codex
author: Hermes Agent, adapted for Codex
license: MIT
platforms: [macos, linux]
---

# Private Intelligence Reader

Use when building or improving a private blog-shaped intelligence system: feeds, X/Twitter, YouTube, newsletters, local notes, or web research become a personalized reading surface with summaries, examples, action plans, and source-grounded validation.

The goal is not a generic blog generator. The goal is a private editor/researcher pipeline with a pleasant reader.

## Architecture

Keep the system split:

1. Collectors gather source material.
2. Source bundles store excerpts, URLs, timestamps, authors, and collector metadata.
3. Validation notes check important claims against source context.
4. Rendered posts are the reader-facing summaries, examples, and recommendations.
5. Action ledger tracks follow-ups separately from prose.
6. Web reader renders validated markdown/MDX; it should not invent hidden context at render time.
7. Public publishing lane is downstream and explicit.

## Source-Grounding Contract

For each generated post, require:

- source bundle path or explicit source references
- validation note path
- confidence level: `High`, `Medium`, `Low`, or `Blocked`
- TL;DR
- why it matters to the user
- concrete next actions
- clear blocked states when source context is missing

Hard rule: if the context was not read from a file, API response, transcript, or source bundle, do not present it as fact.

## Reader Pattern

For a markdown-native reader, Astro is a strong default:

- keep dependencies minimal
- pin exact package versions
- respect release-age controls
- validate content before rendering
- sync only valid vault posts into `src/content/`
- constrain MDX with component allowlists if used
- test that source-bearing components reference the declared source bundle

Do not fuse daemon and reader. The daemon writes validated markdown/MDX plus source bundles; the reader displays them.

## Anti-Slop UI

Private readers fail when they look like generic AI SaaS dashboards.

Fix order:

1. Delete noisy metadata from the main feed.
2. Show only reader-useful metadata: source count, confidence, date, action count.
3. Use plain user-specific copy about what the reader helps decide today.
4. Use an editorial/product UI style with restrained hierarchy.
5. Make confidence/action/source state quiet but legible.
6. Verify in browser and critique the rendered page, not just build output.

For frontend implementation, follow the user's OpenCode-first preference from AGENTS.md, then review and fix with Codex.

## Public Publishing Boundary

Public posts require a separate promotion step:

- strip private notes and action ledgers
- re-check citations and permissions
- reframe from personal action advice to public value
- keep public domain/deploy separate until the user explicitly approves publishing
