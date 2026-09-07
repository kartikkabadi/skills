# Kartik's Agent Skills

Personal agent skills, written and battle-tested against real daily work
across a multi-agent setup (Hermes, Codex, OpenCode, Command Code, and
more). Each skill is a standard `SKILL.md` package — installable by any
agent harness that supports the Agent Skills format.

## Install

```bash
# everything
npx skills add kartikkabadi/skills

# or one at a time
npx skills add kartikkabadi/skills/handle-this
```

Skills live at the repo root, one directory per skill. You can also just
copy any skill directory into your harness's skills folder
(`~/.agents/skills/`, `~/.hermes/skills/`, `.claude/skills/`, etc.).

## The skills

### Acting on your behalf

| Skill | What it does |
|---|---|
| [handle-this](handle-this/) | Drop any link, file, screenshot, or idea on the agent. It identifies what it is, mines your local context (screen history, past agent sessions, repos), and acts on it completely — no steering needed. |
| [decide-for-me](decide-for-me/) | Cognitive offload. Sorts the pile with an Eisenhower grid, executes everything safely delegable, and escalates at most 3 yes/no decisions with a recommendation and a safe default. |
| [agent-council](agent-council/) | Assembles one read-only subagent per skill lens to vote on a contested decision; later waves see earlier findings, then a tally and report. |
| [call-advisors](call-advisors/) | Calls the fixed WATCHDOG advisor roster (Architecture, Security, Fixer, Verifier, and the rest) for review on a plan, decision, or finished work, in a native background loop or an on-demand council. |
| [grade-it](grade-it/) | The verifier. Finished work gets graded by independent fresh-eyes subagents against a rubric built from the original request — not the author's effort. Nothing reports "done" until it passes. |

### Discipline

| Skill | What it does |
|---|---|
| [agent-input-trust](agent-input-trust/) | Treats external content (webpages, repos, emails, MCP responses) as evidence, never instructions. Anti-prompt-injection discipline. |
| [how-to-code](how-to-code/) | Loaded before any code writing, editing, planning, or reviewing. |
| [clean-code](clean-code/) | Practical clean-code discipline for production software. |
| [hygiene](hygiene/) | Cleanup discipline: close only what you opened, kill only what you started, leave the environment as found. |
| [git-branch-worktree-discipline](git-branch-worktree-discipline/) | Branch/worktree safety, destructive-command boundaries, parallel-agent isolation. |
| [supply-chain-install-protection](supply-chain-install-protection/) | Install-time package security: minimum release age gates, Socket Firewall shims, dependency audits. |

### Workflows

| Skill | What it does |
|---|---|
| [link-research](link-research/) | Drop a link (X, YouTube, article) and get grounded research of it. |
| [todo-mastery](todo-mastery/) | Phased, heavily decomposed task lists with real-time tracking, from one-session tasks to 1000-todo programs. |
| [youtube-transcript-to-markdown](youtube-transcript-to-markdown/) | Full YouTube transcript to a polished, chaptered markdown file. yt-dlp captions (whisper fallback), parallel-chunk rewrite subagents, verified output, zero artifacts left. Ships a reusable VTT rolling-caption dedupe script. |
| [transcript-to-markdown](transcript-to-markdown/) | Source-agnostic version: YouTube, audio/video files, VTT/SRT captions, or raw text → one clean, sectioned markdown transcript. Same parallel-rewrite pipeline, plus an SRT-aware caption cleaner. |
| [x-growth](x-growth/) | X/Twitter growth playbook for small or non-technical accounts: anti-gatekeeping, hook patterns, build-in-public, reply-gated lead magnets. Ships a hook-pattern reference with formulas and rewrites. |
| [repo-inspection](repo-inspection/) | Deep codebase audits: structure, dependencies, what's built, partial, missing, blocked. |
| [find-skills](find-skills/) | Locate, evaluate, and install existing skills before building from scratch. |
| [private-intelligence-reader](private-intelligence-reader/) | Build private, source-grounded intelligence readers from feeds and vault notes, with anti-slop UI gates. |
| [unit-economics-analysis](unit-economics-analysis/) | SaaS unit economics, pricing, margins, break-even, sensitivity — verified numbers only. |
| [telephony-product-architecture](telephony-product-architecture/) | Design and feasibility-check phone-call products: carriers, CPaaS, iOS/Android constraints, AI call handling. |

## Format

Every skill is a directory with a `SKILL.md` (YAML frontmatter with `name`
and `description`, then the operating instructions). Some ship helper
scripts under `scripts/`. Works with any harness that reads the Agent
Skills format — Claude Code, Codex, Cursor, Hermes, OpenCode, and the rest
of the skills.sh ecosystem.

## License

MIT. See [LICENSE](LICENSE).
