---
name: find-skills
description: Locate, evaluate, and install reusable agent skills for a concrete task. Use when a repeatable capability may already exist and the user would benefit from comparing trustworthy skill sources before building from scratch.
version: 2.0.0
author: Kartik Kabadi
license: MIT
---

# Find Skills

Find a reusable skill only when it is likely to save meaningful work or provide specialized procedures. Do not turn a simple question into a package search.

## Decide Whether Search Is Worthwhile

Search for a skill when the request involves:

- a repeatable engineering or operational workflow
- a specialist domain with important conventions
- a task the user expects to perform again
- tooling that may require exact setup steps
- a request to extend the agent's installed capabilities

Help directly instead when the task is small, one-off, or already covered by the agent's built-in abilities.

## 1. Define the Required Capability

Turn the request into a short capability statement before searching.

Capture:

- the outcome
- the domain
- the runtime or agent harness
- important constraints
- actions the skill must or must not perform

Example:

```text
Need: review Rust pull requests for correctness and unsafe-code risks
Harness: Codex-compatible skills
Constraints: no automatic approval or merge
```

Use the smallest distinctive search terms. Search for the capability, not the user's whole sentence.

## 2. Check Existing Local Skills First

Do not install a duplicate before checking the current collection.

Inspect available skill names and descriptions. A broader existing skill may already cover the task. Prefer extending or invoking a trusted installed skill over adding another near-copy.

## 3. Search the Skill Ecosystem

The Skills CLI can search public skill registries:

```bash
npx skills find "<keywords>"
```

Try two or three focused variants when terminology differs:

```bash
npx skills find "rust code review"
npx skills find "unsafe rust audit"
npx skills find "pull request reviewer"
```

Registry results are discovery leads, not proof of quality, authorship, safety, or permission.

## 4. Follow Every Candidate to Its Authoritative Source

Before recommending or installing a result, open its actual source repository.

Verify:

1. **Identity** — Is this the original repository or merely a mirror?
2. **License** — Does an explicit license permit the intended use and redistribution?
3. **Content** — Read the complete skill, including referenced files and scripts.
4. **Scope** — Does it perform only the capability the user requested?
5. **Maintenance** — Are its instructions compatible with current tools and APIs?
6. **Security** — Does it ask for secrets, destructive commands, broad permissions, or unreviewed installation hooks?
7. **Provenance** — Can the exact skill file be tied to a source revision?

Do not infer permission from a public repository, install count, star count, or appearance in a registry.

## 5. Compare Candidates on Substance

When several skills overlap, compare them using concrete criteria:

| Criterion | Question |
|---|---|
| Fit | Does it solve the user's exact task? |
| Authority | Is the publisher credible for this domain? |
| Permission | Is the license clear and compatible? |
| Safety | Are commands and requested privileges proportionate? |
| Quality | Are procedures specific, testable, and internally consistent? |
| Freshness | Do tool names, versions, and APIs still exist? |
| Redundancy | Does an installed skill already provide the same value? |

Popularity can be one signal, but it must not override license, security, or technical fit.

## 6. Present a Recommendation Before Installation

For each serious candidate, report:

- skill name
- authoritative repository
- what it adds
- why it fits
- declared license
- meaningful risks or limitations
- exact installation command

Recommend one default when the evidence supports it. Do not dump an undifferentiated search-result list on the user.

Example structure:

```text
Recommended: owner/repository@skill-name
Why: Covers the requested workflow and includes explicit verification steps.
License: MIT
Risk: Executes a project-local formatter; review the command before enabling.
Install: npx skills add owner/repository@skill-name -g
```

## 7. Install Only With Authorization

Do not install a skill merely because it was found.

When the user authorizes installation:

1. pin the intended repository and skill name
2. review the downloaded files before execution
3. avoid bypass flags unless they are necessary and understood
4. do not expose credentials in commands or logs
5. verify the installed directory and source revision
6. report exactly what changed

A typical command is:

```bash
npx skills add owner/repository@skill-name -g
```

Use non-interactive confirmation flags only when the user has already approved the exact source and operation.

## When No Suitable Skill Exists

Do not force a weak match.

Instead:

1. state what was searched
2. explain why the candidates were unsuitable
3. help with the task directly
4. suggest creating an original skill only when the workflow is repeatable

A new skill should have one clear responsibility, explicit trigger conditions, bounded permissions, verification steps, and documented provenance.

## Completion Checklist

- [ ] The requested capability was defined precisely.
- [ ] Existing installed skills were checked first.
- [ ] Candidates were traced to authoritative repositories.
- [ ] Licenses and provenance were verified.
- [ ] Complete skill content and referenced scripts were reviewed.
- [ ] Security and permission risks were surfaced.
- [ ] The recommendation is specific and justified.
- [ ] Installation occurred only after authorization.
- [ ] The installed result and exact changes were verified.
