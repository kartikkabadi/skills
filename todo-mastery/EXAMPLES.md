# Examples

## 1. Worked example: add OAuth login to the API

Request: "Add Google OAuth login to the API."

Good init:

```
init list:
Phase "Investigate":
  - "Read auth docs and existing user model"
  - "Decide provider library and token shape"
  - "Record decisions in ADR"
Phase "Implement":
  - "Add OAuth config and env vars"
  - "Implement auth callback route"
  - "Add token validation middleware"
  - "Wire user creation on first login"
Phase "Verify":
  - "Add integration tests for login flow"
  - "Run full test suite and fix failures"
```

Why it is right: three outcome-named phases; 3-4 todos per phase; every todo names its check ("Run full test suite and fix failures"); irreversible work (middleware) sits after cheap exploration; verification is its own phase.

Tracking while working, batched in real time:

```
turn 5:  read(auth docs)                    + todo done "Read auth docs and existing user model"
turn 6:  read(provider docs)                + todo done "Decide provider library and token shape"
                                            + todo append "Document token refresh flow" to Implement
turn 7:  edit(env sample)                   + todo done "Add OAuth config and env vars"
```

Each todo op rides with real work. The list never lags the work by more than one action.

## 2. Over-decomposed: before and after

Bad (ceremony, no verification, one action split into three):

```
Phase "Setup":
  - "Create todo list"
  - "Update todo list"
  - "Check progress"
  - "Review plan"
  - "Write schema file"
  - "Write migration file"
  - "Run migration"
  ... 20 items, most unverifiable
```

Good:

```
Phase "Schema":
  - "Write migration and apply it"
  - "Verify schema loads in dev"
```

The fix: ceremony todos deleted; the three schema entries merged into one verifiable action; a check added.

## 3. Under-decomposed: before and after

Bad (one giant todo, no checkpoints, silent stall):

```
Phase "Feature":
  - "Add OAuth login"
```

Good: the example 1 list. The fix: split by outcome (investigate / implement / verify), each todo small enough to finish and verify in one turn.

## 4. Block and unblock

Waiting on a user decision:

```
todo block task "Decide provider library and token shape" reason "waiting on Kartik: pick provider"
```

The system excludes it from reminders; auto-promotion skips it. When the answer lands:

```
todo unblock task "Decide provider library and token shape"
```

It returns to pending and auto-promotes if nothing else is active.

Blocker is agent-actionable (needs reading a doc first): do not block. Append an unblocking task ahead of it:

```
todo append phase "Investigate" items ["Read provider docs"]
```

## 5. Re-plan mid-task

Mid-task the user adds admin roles. If the rest of the plan still holds, append:

```
todo append phase "Admin" items ["Add admin role to user model", "Guard admin routes"]
```

If the change is structural, re-init the whole list (also refreshes the session title):

```
todo init list: [ ...original phases re-enumerated + "Admin" phase... ]
```

## 6. Subagents and todos

Todo is parent-owned: subagents do not get the tool. A parent tracks a subagent's work as a todo whose wording matches the subagent's description. When the subagent succeeds, the matching todo auto-completes (blocked ones included — completion is the unblock signal). Failed or aborted subagents leave the todo open: verify what actually happened before closing it manually.

## 7. A 100-phase migration: master file + live window

Task: "Migrate the monolith to services. 12 services, about 9 phases each. Keep CI green."

Step 1 — write the master plan as a file (100 phases, 1000 todos). This is the store:

```
# Monolith migration
## Baseline
- [ ] Record API contract and freeze it
- [ ] Add contract tests to CI
- [ ] Measure request latency baseline
## Auth service
- [ ] Extract user store
- [ ] Route /auth to new service
- [ ] Verify auth integration tests
## Billing service
- [ ] Extract billing store
- [ ] Route /billing to new service
- [ ] Verify billing integration tests
... 97 more phases
```

Step 2 — open the window: init the live list with the first two phases only.

```
init list:
Phase "Baseline":
  - "Record API contract and freeze it"
  - "Add contract tests to CI"
  - "Measure request latency baseline"
Phase "Auth service":
  - "Extract user store"
  - "Route /auth to new service"
  - "Verify auth integration tests"
```

98 phases stay in the file. The per-op summary stays small (about 29 tokens per task), the stop-time reminder stays small (only window items are open), and the HUD shows the counter Todos · 1/100.

Step 3 — at each phase boundary, keep the window moving:

```
todo done phase "Baseline"
todo rm phase "Baseline"          (the file keeps the record)
todo append phase "Auth service" items ["Extract user store", "Route /auth to new service", "Verify auth integration tests"]
todo append phase "Billing service" items ["Extract billing store", "Route /billing to new service", "Verify billing integration tests"]
```

Then update the master file: mark Baseline done, check the append matches the file.

Step 4 — on a fresh session, restore the window from the file with /todo import, then `view` to confirm. The file is the store; the list is the working set.
