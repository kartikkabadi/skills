---
name: git-branch-worktree-discipline
description: "Disciplined Git workflows for Codex: branch/worktree safety, preflight checks, destructive-command boundaries, conflict handling, PR readiness, and parallel-agent isolation."
version: 1.0.0-codex
author: Hermes Agent, adapted for Codex
license: MIT
---

# Git Branch And Worktree Discipline

Git is shared mutable state. Inspect before writes, checkpoint before risk, and never rewrite or delete work without explicit approval.

## Use When

- Starting code work in a git repo.
- Creating, switching, merging, rebasing, deleting, or pushing branches.
- Running parallel agents or model variants in the same repo.
- Using `git worktree`.
- Preparing a PR, resolving conflicts, or cleaning up after merge.

## Non-Negotiable Safety

Before changing git state:

```bash
git status --short
git branch --show-current
git diff --stat
git log --oneline --decorate -5
```

Require explicit user confirmation before:

- `git reset --hard`, `git clean -f*`, `git branch -D`, `git worktree remove -f`, `git reflog expire`, `git filter-branch`, `git filter-repo`
- `git push --force` or `git push --force-with-lease`
- rebasing, amending, deleting, or force-updating commits that may be shared
- changing remotes, Git credentials, global Git identity, auth, config, or security settings
- deleting branches/worktrees with uncommitted or unmerged work

Prefer safer alternatives:

- undo one file: inspect diff, then `git restore <file>`
- undo staged file: `git restore --staged <file>`
- undo public commit: `git revert <sha>`
- delete branch: `git branch -d <branch>` first
- clean files: `git clean -nfd` before any execution
- parallel work: separate worktree plus branch per agent

## Worktree Workflow

Use a separate worktree when multiple agents, variants, or tasks need to edit concurrently.

```bash
git worktree add -b agent/<task-slug> ../repo-agent-<task-slug> main
```

Each worker must know:

- exact working directory
- exact branch
- allowed files/scope
- forbidden side effects
- verification commands
- that other agents may be editing elsewhere

After completion, inspect before integrating:

```bash
git status --short
git log --oneline --decorate -5
git diff --stat main..HEAD
```

Never delete worktree directories with `rm -rf`; use `git worktree remove`.

## PR-Ready Loop

Before opening or handing off:

```bash
git fetch origin
git status --short
git diff --stat origin/main..HEAD
git log --oneline origin/main..HEAD
```

Run the project’s real checks. Review that only intended files changed, no secrets/debug junk were added, and the working tree is clean if a commit/PR is being handed off.
