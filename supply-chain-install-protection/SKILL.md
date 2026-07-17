---
name: supply-chain-install-protection
description: Configure, verify, and reason about install-time package-manager protection, minimum release age gates, Socket Firewall shims, dependency audits, and supply-chain risk on developer machines and repos.
version: 1.0.0-codex
author: Hermes Agent, adapted for Codex
license: MIT
---

# Supply-Chain Install Protection

Use when the user asks to verify, harden, troubleshoot, or bypass package-manager install-time protection, or when auditing whether a machine/repo is affected by dependency compromise.

Goal: make the safe path the default path for future installs. Do not pretend future-fetch protection retroactively audits already-installed packages.

## Scope Model

Separate four jobs:

1. Install-time firewalling: intercept future package artifact fetches.
2. Cache reset: remove local package caches so future installs must fetch through protection.
3. Existing dependency audit: scan manifests, lockfiles, SBOMs, and installed state.
4. Whole-machine security review: OS/package posture, repo discovery, dependency audits, LaunchAgents/services, and redacted secret-pattern triage.

Do not conflate them.

## Default Workflow

1. Inspect authoritative docs before changing security config.
2. Verify current local state: package managers, shims, shell resolution, and relevant config.
3. Prefer PATH shims over aliases for developer-machine hardening.
4. Wrap only documented-supported managers; unsupported wrappers are security theater.
5. Preserve bypass and rollback.
6. Verify with no-install smoke tests before real installs.
7. Ask before cache clearing, external scans, installs/upgrades, CI changes, or private metadata upload.

## Whole-Machine Audit Workflow

Use when the user asks for a machine-wide supply-chain/security check.

1. Inventory before scanning: git repos, manifests/locks, package manager state, OS update state, Homebrew outdated state, launch agents/services when relevant.
2. Keep secret scanning redacted: report detector/confidence/file/line only; do not print candidate values.
3. Exclude `.env`, credential stores, SSH material, browser profiles, and protected dotfiles unless explicitly scoped.
4. Ask before transmitting dependency metadata externally.
5. Run ecosystem audits from the correct working directory:
   - `npm audit --json --audit-level=low` where npm lockfiles exist.
   - `pnpm audit --json --audit-level=low` where `pnpm-lock.yaml` exists.
   - `bun audit --json` where Bun locks exist.
   - `uvx pip-audit ...` for Python requirements/project locks.
   - `cargo-audit audit --json` from each `Cargo.lock` parent directory.
6. Report clean signals, active repo risks, archive/reference noise, manual review queues, and recommended next actions separately.

## Minimum Release Age Verification

Distinguish native age gates from firewalling:

- npm: `min-release-age` / moving `before` cutoff.
- pnpm: `minimumReleaseAge` in minutes (`pnpm config set minimumReleaseAge 4320 --global` or `~/.config/pnpm/config.yaml`; does **not** read npm `min-release-age` from `~/.npmrc`).
- Yarn Berry: `npmMinimalAgeGate`.
- Bun: `[install].minimumReleaseAge` in seconds.
- uv: `exclude-newer`.
- raw pip and standard cargo do not have first-class rolling minimum-release-age gates.

Existing lockfiles and already-installed packages are not automatically re-aged. Age gates mainly affect future resolution/fetch behavior.

## Remediation Workflow

1. Patch repo-by-repo, not with one machine-wide upgrade blast.
2. Check `git status` and preserve user work before dependency edits.
3. Use the repo's native package manager and lockfile.
4. Use overrides/resolutions only when normal updates cannot lift a vulnerable transitive dependency.
5. Re-run the exact audit after each repo patch and report advisory counts.
6. Run the smallest meaningful build/test gate after the audit is clean.
7. Use install-protection bypass only for tests/builds when no package fetch is occurring; do not bypass protected installs unless the user explicitly approves.

## Pitfalls

- Do not report protection as active just because a tool is installed. Active means package-manager invocations actually route through protection.
- Do not say a machine is clean just because future-fetch protection is active.
- Do not scan private repos with external services without approval.
- Do not read or print full dotfiles if they may contain secrets; target relevant snippets.
- Do not run one root audit and assume nested workspaces were covered.

## Socket Firewall (sfw) — machine layout

**Interactive shells (done on the user Mac):** aliases at end of `~/.zshrc` / `~/.bashrc` → `sfw <pm>`. Bypass: `command npm …`.

**Non-interactive / Codex / Cursor agents:** aliases do not apply. Use:

1. `~/.sfw-agent-bin/<pm>` wrappers (`exec /opt/homebrew/bin/sfw <pm> "$@"`).
2. Codex `[shell_environment_policy.set] PATH` prepends `~/.sfw-agent-bin` (keep `inherit = "core"`).
3. Cursor user rule: prefix installs with `sfw` unless the user approves bypass.

Do not put agent shims on global interactive PATH (fnm ordering).

**CI:** Per job, after checkout:

```yaml
- uses: socketdev/action@v1.3.1
  with:
    mode: firewall-free
```

Then `sfw npm ci`, `sfw pnpm install …`, `sfw bun install …`, `sfw cargo fetch` / `sfw cargo build` on cold registry fetches. Skip label-bot / spell-check workflows with no installs.

**Bazel-heavy jobs:** wrap explicit `pnpm`/`cargo` steps first; pilot before mass Bazel edits.
