---
name: 10-10
description: "Use to verify finished work: independent verifier subagents grade it."
---

# Prove 10

"Do a 10/10 job" is a vibe. This skill is the machinery: every piece of
finished work gets graded by fresh-eyes verifiers against checkable
criteria, and anything short of 10/10 goes back for fixes before the user
ever sees it. The user is not in the loop — the verifiers are his quality
department.

## When to run

After any deliverable is "done" and before reporting to the user. Code,
transcripts, research briefs, setups, plans, configs — anything that will
be reported as finished. If the task was trivial (a one-line answer), skip;
everything else gets graded.

## The core move: build the rubric from the request, not from the work

The single biggest verifier failure is letting the checker see the work
first — it anchors on what exists and grades the author's effort, not the
user's need.

1. **Extract acceptance criteria from the ORIGINAL request** (plus standing
   rules: AGENTS.md, policies, the task's definition of done). Write them
   as checkable statements: "every chapter header present in order", "the
   script runs and exits 0", "no files left outside the target dir".
2. **Add objective criteria the user didn't state** but that are checkable:
   tests pass, the file opens, all links resolve, names spelled correctly,
   word count in range, no TODOs left.
3. **Each criterion must have a check method**: a command to run, a file to
   read, a diff to inspect, a source to compare against. "Seems good" is
   not a check method.

## Verifier independence (non-negotiable)

- The verifier must NOT be the context that did the work. Spawn a fresh
  subagent with `delegate_task`. Give it the rubric, the artifact paths,
  and permission to run checks — NOT the story of how the work went.
- The verifier's job is to FAIL the work, not to approve it. Brief it:
  "Your job is to find what's wrong. Approving broken work is your
  failure mode. Report PASS/FAIL per criterion with the evidence you
  actually collected — commands run, output seen."
- Scale verifiers to risk:
  - 1 verifier for normal work
  - 2-3 verifiers on different angles for anything the user will rely on
    heavily (published text, money-adjacent, destructive ops, setups
    other tools will depend on): e.g. one for correctness against the
    request, one for evidence/run-checks, one for domain accuracy
- Verifiers run in parallel; their reports come back to you.

## Verdicts

- **PASS on all criteria → 10/10.** Report to the user, mention what was
  verified in one line.
- **Any FAIL → fix loop.** You (or a fixer subagent) repair the failures,
  then RE-VERIFY the failed criteria with a fresh verifier. Max 2 fix
  rounds; after that, report the work with the failures named honestly
  as unverified — never launder them into "done".
- **Unverifiable criterion → say so.** "Not verified: X (no way to check
  Y here)" is a valid report line. Hiding it is not.

## Universal rubric seeds (always applicable; extend per domain)

**Every deliverable:**
- [ ] Does it exist where the user was told it would be? (stat the path)
- [ ] Does it cover the whole request, not the convenient half? (diff the
      request against the artifact section by section)
- [ ] Were all claims in the report actually executed? (re-run one or two
      of them yourself — spot checks keep the chain honest)
- [ ] No leftover scratch/artifacts outside the agreed locations?

**Code:** tests run green; the changed path was exercised for real (not
just unit mocks); failure paths behave; no unrelated changes in the diff.
**Writing/transcripts:** completeness vs source (sample 3 points in the
source, confirm each is represented); entities spelled correctly
(web-check); structure matches the spec (headers, order, format).
**Research:** every key claim traces to a primary source; sources are
linked; contradictions between sources are surfaced, not averaged.
**Setups/configs:** the thing actually runs after setup (run it);
config values match the official docs for the installed version.

## Pitfalls

- Verifier that only reads the artifact and vibes — require it to RUN at
  least one check and quote real output.
- Grading against the work instead of the request — always build the
  rubric from the original ask first.
- Accepting a reviewer's finding without checking its premise — verify
  each FAIL against the real system before acting on it; if the verifier's
  premise is wrong, say so with evidence and re-grade. Verifiers are
  fallible too. (Learned the hard way: a review once invented a size cap
  and the agent amputated a source file to comply.)
- **Wrong checkout / wrong target.** Before grading anything, confirm the
  artifact being graded is the one the request meant — right repo, right
  path, right file. Grading the wrong artifact passes broken work.
- **User-facing work needs e2e evidence**, not unit-level checks: exercise
  the flow the way a human would (screenshots, real inputs). "No fake
  data."
- Fix-loop laziness: "the verifier was too strict" — if the criterion came
  from the user's request, it stays; fix the work, not the rubric.
- Infinite fix loops — 2 rounds max, then honest reporting.
- Skipping verification because the task felt small but had blast radius
  (a config change other tools depend on is never small).

## Wiring

`handle-this` and `decide-for-me` invoke this skill before their final
report. Any agent can also be pointed at it directly: "prove it" after a
task should load this skill.
