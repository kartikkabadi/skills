---
name: repo-inspection
description: "Deep codebase inspection: understand repo structure, read key files, map dependencies, and summarize what is built, partial, missing, and blocked. Use when the user asks to inspect, audit, learn, or go deep on a repo."
version: 1.0.0-codex
author: Hermes Agent, adapted for Codex
license: MIT
platforms: [linux, macos, windows]
---

# Repo Inspection

Use this skill when the user says "check this repo," "inspect this codebase," "go deep into this project," "learn about this repo," or "what's the state of this project?"

Goal: produce a comprehensive understanding of what exists, what's partially built, and what's missing.

## When Not To Use

- the user wants a specific fix and the affected files are obvious.
- The repo is tiny; just read it directly.
- the user already knows the codebase and asked for direct implementation.

## Phase 1: Structural Survey

1. Read nearest `AGENTS.md`.
2. Confirm repo root before git operations.
3. List files with `rg --files` or `find`, excluding dependency/build directories.
4. Read manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.
5. Read README and source-of-truth docs.
6. Identify the framework and runtime entry points.

## Phase 2: Source Of Truth Files

Find and read the files that explain the architecture:

- data model/schema
- auth/access control
- API routes/handlers
- core business logic
- config/env examples, without reading secrets
- product specs/status docs
- tests and CI

Read in this order: README -> schema -> auth -> API routes -> core logic -> config -> tests. Stop only when you have a coherent mental model.

## Phase 3: Frontend Map

If applicable, inspect:

- route/layout files
- product components
- styling/theme tokens
- state management
- loading/error/empty states

Distinguish real implementation from shell:

- shell: hardcoded data, placeholder copy, static demo, "coming soon"
- real: backend wired, dynamic data, error/loading states, tests or runtime proof

For UI/UX implementation work, follow the user's OpenCode-first preference from AGENTS.md.

## Phase 4: Summary Shape

Return:

```text
What This Repo Is
What's Actually Built
What's Partial / Needs Work
What's Missing / Hard Blockers
The Real Bottleneck
Recommended Next Steps
Verification / What Was Read
```

## Exhaustive Mode

If the user asks for a complete audit, optimization audit, security audit, or says to read every file, do not stop at the coherent-model threshold. Read exhaustively within the stated scope, because dead code, duplicate implementations, template remnants, and security issues hide in files that normal inspection would skip.

## Multi-Repo Workspaces

Before reading code, map relationships:

- repo path
- remote URL
- branch
- last commits
- working tree status
- whether it is primary, stale, merged, local-only, or separate upstream

Skip source reads for stale/merged snapshots unless the user explicitly wants the historical branch inspected.
