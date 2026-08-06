---
name: clean-code
description: Practical clean-code discipline for writing, refactoring, and reviewing production software. Use when code must become easier to understand, test, change, or operate without altering required behavior.
version: 2.0.0
author: Kartik Kabadi
license: MIT
---

# Clean Code Discipline

Clean code reduces the cost of the next correct change. It makes behavior, ownership, failure modes, and extension points visible without requiring a reader to reconstruct the author's private reasoning.

Use this skill while writing new code, repairing defects, reviewing a change, or reducing technical debt. Apply it proportionately: a tiny script and a long-lived service need different amounts of structure, but both should be understandable and honest.

## 1. Preserve the Contract

Before changing structure, identify what must remain true:

- user-visible behavior
- public APIs and data formats
- persistence and migration rules
- performance or resource constraints
- security and authorization boundaries
- required compatibility
- observable errors and logs

Refactoring without an explicit contract is behavior change by accident. Add characterization tests when the current behavior is important but poorly documented.

## 2. Make Names Carry Meaning

Choose names that reveal purpose in the local domain.

Prefer:

- `resolveInvoiceRecipient` over `handleData`
- `remainingRetryBudget` over `count`
- `isSessionExpired` over `checkSession`
- `parseWebhookSignature` over `processInput`

Rules:

1. Use one term for one concept.
2. Do not hide units: use `timeoutMs`, `priceCents`, or a typed value.
3. Avoid generic containers such as `data`, `item`, `manager`, and `helper` when a domain name exists.
4. Name booleans as predicates.
5. Name functions for their effect or returned result.
6. Rename misleading code even when its current name is familiar.

A good name should reduce the amount of comment text needed around it.

## 3. Keep Units Focused

A function, class, module, or service should have a small, coherent reason to change.

Split code when it mixes independent concerns such as:

- parsing and persistence
- authorization and rendering
- domain decisions and transport formatting
- orchestration and low-level I/O
- state mutation and reporting

Do not split merely to make files short. Extract a unit when the new boundary has a clear contract, a useful name, and a stable owner.

## 4. Keep Control Flow Legible

Make the main path easy to follow.

Prefer:

- early returns for invalid states
- small validation functions with explicit results
- exhaustive handling of state variants
- tables or maps when they express stable lookup rules
- one visible orchestration path over scattered callbacks

Avoid:

- deeply nested conditionals
- Boolean parameters that switch unrelated behavior
- fallthrough that relies on incidental ordering
- exceptions used as ordinary branching
- duplicated conditions that can drift apart

When complexity is inherent, represent it directly with a state machine, decision table, or typed result rather than disguising it in nested branches.

## 5. Make Data Flow Explicit

Readers should be able to answer:

- where a value came from
- whether it was validated
- who may mutate it
- when it becomes durable
- which output depends on it

Prefer immutable values and narrow mutation boundaries. When mutation is required, give one component clear ownership and expose deliberate operations instead of shared writable state.

Normalize external input at the boundary. Internal code should not repeatedly defend against every provider's spelling, nullability, or shape differences.

## 6. Control Side Effects

Separate decisions from effects when practical.

A useful pattern is:

1. read and validate input
2. calculate the intended change
3. perform the effect
4. record or return the outcome

This makes code easier to test and prevents partial work. For multi-step effects, define rollback, idempotency, or recovery behavior explicitly.

Do not hide network calls, file writes, database mutations, process execution, or analytics inside functions that appear to be pure calculations.

## 7. Design Errors Deliberately

An error should help the caller decide what happens next.

Distinguish at least:

- invalid input
- missing resource
- conflict or stale state
- permission failure
- transient dependency failure
- permanent dependency failure
- internal invariant violation

Preserve useful context without exposing secrets. Wrap lower-level errors when the added layer contributes domain meaning; otherwise retain the original cause.

Never silently ignore a failure unless the behavior is intentional, documented, and observable enough to diagnose.

## 8. Use Comments for Information Code Cannot Express

Comments are appropriate for:

- why a surprising constraint exists
- a compatibility requirement
- a security assumption
- an external protocol quirk
- a non-obvious performance tradeoff
- a legal or attribution requirement

Comments should not narrate obvious syntax or compensate for unclear names. Remove stale explanations and dead commented-out code. Version control already records deleted implementations.

## 9. Keep Interfaces Narrow

Expose the smallest stable contract that callers need.

Prefer:

- explicit parameter objects for meaningful options
- domain types over loosely shaped dictionaries
- validated constructors or factories for constrained values
- result types that represent expected outcomes
- dependency injection at real boundaries, not everywhere

Avoid making internal representation public merely because it is convenient today. Every exported symbol becomes a compatibility promise.

## 10. Respect Dependency Direction

Domain policy should not depend directly on UI frameworks, database clients, HTTP libraries, or vendor SDKs.

Place volatile details behind boundaries that translate into the application's own types. This lets core behavior remain testable and reduces the blast radius of provider changes.

A boundary is justified when it isolates meaningful volatility or ownership. Do not add abstraction layers that merely rename the same API.

## 11. Write Tests That Protect Behavior

Tests should make important behavior safer to change.

Prioritize:

- public outcomes
- domain invariants
- permission boundaries
- parsing and serialization edges
- failure and recovery paths
- regressions for real defects

Use unit tests for focused logic and integration tests for boundaries. Avoid tests that duplicate implementation line by line or assert incidental formatting with no contract value.

A refactor is not complete when the tests pass for the wrong reason. Confirm that the test would fail if the protected behavior were broken.

## 12. Remove Duplication Carefully

Duplicate knowledge is dangerous when separate copies must evolve together. Similar-looking code is not automatically the same concept.

Before extracting shared code, ask:

1. Do these copies represent the same rule?
2. Will they change for the same reason?
3. Can the shared contract be named clearly?
4. Does extraction reduce coupling rather than spread it?

Prefer a small amount of honest repetition over a premature abstraction that joins unrelated behavior.

## 13. Refactor in Verified Steps

For a non-trivial cleanup:

1. establish the behavioral baseline
2. make one coherent structural change
3. run focused tests and static checks
4. inspect the diff for accidental behavior changes
5. repeat
6. run the broader verification suite

Do not combine broad formatting, renaming, architecture changes, and feature work in one opaque patch unless they are inseparable.

## 14. Review Checklist

Before declaring the change complete, verify:

- [ ] Required behavior and compatibility are preserved.
- [ ] Names express domain meaning.
- [ ] Each unit has a coherent responsibility.
- [ ] The main control flow is visible.
- [ ] Data ownership and mutation are explicit.
- [ ] Side effects are obvious and bounded.
- [ ] Errors are actionable and retain useful context.
- [ ] Comments explain constraints rather than syntax.
- [ ] Public interfaces are no wider than necessary.
- [ ] Volatile dependencies are kept outside domain policy.
- [ ] Tests cover important outcomes and regression risks.
- [ ] The diff contains no unrelated cleanup or dead code.
- [ ] Format, lint, type checks, tests, and build checks were run as applicable.

## Output When Reviewing Code

Report findings in priority order. For each finding include:

1. the exact location
2. the concrete maintenance or correctness risk
3. the smallest coherent improvement
4. the verification needed after the change

Do not report personal style preferences as defects. Tie every recommendation to clarity, correctness, testability, operability, security, performance, or future change cost.
