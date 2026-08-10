---
name: call-advisors
description: Get review and advice on a plan, a decision, or finished work from the fixed advisor roster in ~/.omp/agent/WATCHDOG.yml, either through the native background advisor loop or an on-demand council of one read-only subagent per advisor. Use when the user says "call the advisors", "ask the advisors", "ask the advisors for advice", "get advisor input", "run the advisor council", or "review this with the advisors", or wants multiple expert lenses on a plan or decision right now.
---

# Call the Advisors

## What this is

Ten advisors review your work. Each has a fixed lens: Architecture, Security, Fixer, Verifier, Bugs, Maintainability, Performance, ApiContract, RedTeam, Kartik.

The roster and each advisor's instructions live in `~/.omp/agent/WATCHDOG.yml`. That file is the source of truth. Read it before you act.

## Quick start

State the question, plan, or decision clearly in your turn. The next advisor review cycle addresses it. Notes arrive as advisor cards in the transcript.

## Choose a mode

- Native loop (default): work is in progress, the user wants ongoing watch, or advice can wait one turn. Costs nothing extra.
- On-demand council: the user asks for advice now, a decision is time-critical, or the user wants every lens on one plan immediately.

## Mode A - Native background loop

1. Check advisors are on. `advisor.enabled: true` in `~/.omp/agent/config.yml`.
2. State the question or plan in your turn. The next review cycle addresses it.
3. Read the notes. Severities: `nit` (aside), `concern` (material risk), `blocker` (work is broken). Only material notes are shown.

Silence is normal. The emission guard suppresses empty notes. Do not treat silence as broken advisors.

Verify advisors are live:
- Read `~/.omp/agent/sessions/<session-id>/__advisor.<slug>.jsonl`. One file per advisor.
- Slugs: architecture, security, fixer, verifier, bugs, maintainability, performance, apicontract, redteam, kartik.
- Files that contain assistant turns mean the advisors are reviewing.

Manual control:
- `/advisor status` in the TUI.
- `/advisor on` and `/advisor off` toggle for the session.

## Mode B - On-demand council

1. Read `~/.omp/agent/WATCHDOG.yml`. Take the enabled advisors and each advisor's `instructions` field.
2. Spawn one subagent per enabled advisor. Run them in parallel.
3. Give every subagent the same brief: the question/plan/work under review, the advisor's instructions verbatim as its role, the deliverable format, and the read-only rule.

Read-only rule (mandatory):
The council is strictly read-only. Subagents investigate with read, grep, and glob. They must NOT edit files, write anything, run state-changing commands, or install anything. A council gives perspective. It does not do work.

Deliverable format, state it in the brief:
- One note from its lens.
- Material findings only.
- Under 150 words.

Synthesize:
1. Merge the findings. Dedupe. Drop noise.
2. Present in chat with per-advisor attribution.
3. Mark each finding material (would change the plan) or nice-to-have.
4. Weigh the advice. Do not obey blindly. Advisors disagree sometimes. Say so honestly and give the tradeoff.

## Cost

Advisors run on the model in `modelRoles.advisor` from `~/.omp/agent/config.yml` (currently deepseek-v4-flash, cheap). A 10-subagent council is affordable.

## Advanced

See [REFERENCE.md](REFERENCE.md) for the full council brief template, the roster table, severity examples, and troubleshooting.
