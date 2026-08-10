# Call the Advisors - Reference

## Roster (from ~/.omp/agent/WATCHDOG.yml)

All ten advisors are enabled by default. This table is a summary. The `instructions` fields in WATCHDOG.yml are authoritative and override this summary.

| Advisor | Lens |
|---|---|
| Architecture | Cross-module coupling, public-API growth, layering violations, design regressions, deepening opportunities, settled decisions before building |
| Security | Secret leakage, injection, unsafe deserialization, auth/authorization bypasses, risky dependencies. Material findings only |
| Fixer | Reproduce the failure, fix the root cause not the symptom, smallest change. May edit and run tests to prove a fix, then advise |
| Verifier | Claims vs evidence. Verdict style: VERIFIED / ISSUES FOUND / BLOCKED. Tests sit at public seams and assert behavior |
| Bugs | Real bugs only: null/empty/malformed input, off-by-one, races, broken error handling, silent failures, integration risks |
| Maintainability | Dead code, unused imports, magic numbers, duplication, files past ~1000 lines, stale comments, unclear naming, mixed concerns |
| Performance | N+1 queries, missing indexes, quadratic loops, blocking I/O in async paths, large bundles. Before/after evidence for wins |
| ApiContract | Breaking public API changes, versioning, error response consistency, rate limits, pagination, docs drift |
| RedTeam | Adversarial second pass: happy-path attacks, silent failures, trust assumptions, edge cases, cross-category gaps |
| Kartik | Kartik's rules and preferences: no scope creep, no fake-complete status, no placeholder slop, secrets never printed, environment left as found |

## Native loop details

The top-level `instructions` in WATCHDOG.yml apply to every advisor:

- Review against the user's stated goal and the project's own conventions.
- Prefer concrete evidence (file, symbol, line) over generic advice.
- At most one note per update; escalate severity only when material.
- Disclose any change (edit, write, or state-changing command) in the advice note.

Severity meanings:

- nit: non-interrupting aside. Not shown by default.
- concern: material risk. Shown.
- blocker: work is broken. Shown.

The council mode is read-only by design. A council gives perspective; it does not do work. The disclosure rule above does not apply to council members, because they cannot change anything.

## Council brief template

Use this prompt for every council subagent. Fill the placeholders.

```
You are the {advisor} advisor on this council.

Role. {advisor instructions verbatim from WATCHDOG.yml}

Read-only. You investigate and advise. You must NOT edit files, write
anything, run state-changing commands, or install anything.

Subject. {the question, plan, decision, or finished work under review,
with file paths}

Deliverable. One note from your lens. Material findings only. Under 150
words. If your lens has nothing material to say, return one line saying
so. Do not pad.
```

Run all members in parallel. Collect every result before synthesizing.

## Weighing the advice

- The agent owns the decision. Advice is input, not orders.
- When advisors disagree, both lenses can be right about different parts. Present the split and the tradeoff.
- A blocker finding means work-not-done until resolved.
- One material finding from one advisor is enough to pause a plan. Nits from all ten are not.

## Troubleshooting

- No advisor notes in the transcript: check `advisor.enabled` in `~/.omp/agent/config.yml`, then `/advisor status`. Silence may also be the emission guard suppressing empty notes.
- Council member returns nothing: re-read its instructions. A narrow lens (Performance on a doc-only change) may legitimately have nothing. Do not pad the report.
- Advisor files missing for a session: the session may predate advisors, or advisors are off. Check the config and start a new session.
- Transcript slugs are lowercase: apicontract, redteam, kartik, and the rest.
