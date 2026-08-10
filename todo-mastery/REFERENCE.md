# Reference — the full decomposition guide

## Principles (the why)

1. **Decomposition is the main lever for hard tasks — with a cost curve.** Least-to-Most: subproblems solved in sequence beat one-shot chain-of-thought (99% vs 16% on SCAN). Plan-and-Solve: writing the plan first fixes missing-step errors. Tree of Thoughts: intermediate checkpoints catch errors before they compound (4% to 74% on Game of 24). Decomposed Prompting: each piece must be simpler than the whole and verifiable on its own.
   Sources: arxiv.org/abs/2205.10625, arxiv.org/abs/2305.04091, arxiv.org/abs/2305.10601, arxiv.org/abs/2210.02406.

2. **Plans get evicted from context; eviction is expensive.** Plan signal in hidden state decays about 4x within one action-observation step; naive eviction cut ALFWorld success by ~35 points. Keep the plan short enough to survive compaction.
   Source: arxiv.org/abs/2606.22953.

3. **Over-decomposition has a documented failure mode: the no-recovery bottleneck.** Extreme memoryless decomposition makes errors at a few hard steps irreversible; steps with short lookahead and overlap recover. Isolation helps; total isolation hurts.
   Sources: arxiv.org/abs/2603.06870, arxiv.org/abs/2601.22311, arxiv.org/abs/2604.11978.

4. **Working memory is small; the list is the store, the working set is the memory.** Miller: ~7 chunks; Cowan: ~4. A todo list offloads memory, so list length matters less — but the open items the agent must reconcile behave like working memory. Keep the working set small; let the list be the store.
   Source: en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two; en.wikipedia.org/wiki/Cognitive_load.

5. **Visible progress motivates and orients; the start is the weakest point.** Goal-gradient: effort tracks the proportion of distance remaining (coffee-card study: bonus stamps beat plain cards). Make the first phase small and visible. The Zeigarnik memory advantage does not replicate, but resumption does (~67% of interrupted tasks get resumed) — open tasks are debts to close, not hooks to rely on. One visible next task beats a wall of pending items.
   Sources: business.columbia.edu goal-gradient PDF (Kivetz, Urminsky & Zheng 2006); nature.com/articles/s41599-025-05000-w.

6. **Every todo carries its own verification.** Without a check the agent can run, "looks done" is the only signal. One check per todo; don't pile on defensive checks.
   Source: code.claude.com/docs/en/best-practices.md.

7. **Cheap reversible steps early; expensive irreversible commitments late.** Early myopic commitments get amplified downstream. In code the reversible unit is the git-visible change; the irreversible unit is the migration, rename, or contract change. Defer it.
   Sources: arxiv.org/abs/2601.22311; langchain.com/blog/plan-and-execute-agents; github.com/yoheinakajima/babyagi_archive.

8. **The plan is a hypothesis, not a contract.** Drift is normal; manage it by re-baselining at phase boundaries, where re-planning is cheap. Decomposition pays where the task has hard constraints (dependencies, interfaces) — splitting elsewhere adds ceremony.
   Sources: arxiv.org/abs/2604.11978, arxiv.org/abs/2510.07772.

## Granularity heuristics

### Goal to phases

- 2-5 phases per session task; more for multi-session work (see "Sizes and scale"). Fewer than 2 = no plan; 6+ phases in a single session = planning at todo granularity with extra ceremony.
- A phase = one outcome you can point at, one risk profile, one review moment. Name it after the outcome.
- Order: small fast verifiable first; investigation before implementation; irreversible last; when either order works, pick the one that produces something checkable sooner.
- Add a phase: new outcome type with its own done-criteria; mid-task discovery; 8+ pending todos in a phase.
- Remove a phase: one todo (fold it in); boundary review never changes anything (merge it); discovery made it obsolete (abandon wholesale).

### Phase to todos

1. One todo = one verifiable action.
2. Completable in one session or turn.
3. 3+ distinct actions → 2-3 todos.
4. No verification → not a todo.
5. Content is what-not-how, 5-10 words, globally unique.

### Size calibration

- 1-3 todos = steps of one action → merge to one.
- 3-8 todos = the natural size for a phase in one session.
- 8+ in a phase → split the phase.
- An all-"research / think / maybe" phase is plan-shaped avoidance → one decision todo plus its verification.

### Ordering within a phase

Auto-promotion picks the earliest open pending task, so list order IS execution order. Cheap verification early; irreversible late; blocked items sit after their unblockers.

## Warning signs

Over-decomposition:
- Ceremony todos ("Update todos", "Check plan").
- No verification attached to most items.
- Status churn without work: the list updates every turn, the code barely moves.
- 8+ pending in one phase; a single action split across entries.
- Todos the agent must re-read to understand.
- Todos still pending after the work is done (zombies).
- Parallelism theater: sequential steps split into status flips without checkpoints.

Under-decomposition:
- A todo that spans multiple sessions.
- No intermediate checkpoints; one giant todo per feature.
- Silent stall: nothing is checkable, so nobody can tell it's stuck.
- No exploration phase; implementing against unverified understanding.
- Multiple unrelated outcomes in one todo.
- Refusal to start — the first todo is too big to grasp.

## Decision procedure

1. Can I state its verification? No → rewrite or delete.
2. One session/turn? No → split.
3. 3+ distinct actions? Yes → split.
4. Phase of one, or phase with 8+? → merge or split the phase.
5. Anything observable change? No → merge or delete.
6. Blocked by an earlier todo? Move it after its unblocker.

Merge when: two todos share one verification; sub-steps belong to one action; a phase has shrunk to one item.
Split when: it fails 2 or 3; its phase exceeds ~8 pending.
Leave when: it passes 1-4 and fails 5.

## Sizes and scale

The tool has NO hard limit on phases or todos. Schema caps: none anywhere (no maxItems, no maxLength). A 100-phase / 1000-todo init is accepted and persisted. What scales poorly is measured and known:

### Per-op cost

Every todo op returns a text summary of the whole list. formatSummary lists every open task twice (remaining-items block + per-phase dump), closed tasks once. Measured cost: about 115 bytes, ~29 tokens, per task, plus ~2 KB for 100 phase headers.

- 100 todos ≈ 11 KB ≈ 2.8k tokens per op.
- 500 todos ≈ 58 KB ≈ 14.5k tokens.
- 1000 todos ≈ 115 KB ≈ 29k tokens.

### The spill cap (the only automatic bound)

Above `tools.artifactSpillThreshold` (default 50 KiB, settings-schema.ts:710), the summary text is spilled to an artifact: the model sees head (≤ 20 KiB / 500 lines) + tail (≤ 20 KiB / 500 lines) with the middle elided, plus an artifact:// link. With 7-word tasks the boundary is around 450-500 todos. Below it the model sees the full plan; above it the model loses the middle of its own plan.

`details.phases` (the full array) is never sent to the model — it is for persistence, the TUI, and ACP sync only (session/messages.ts:229-232). The transcript grows ~84 KB per op at 1000 todos (session-file cost, not model cost).

### The stop-time reminder (the real at-scale killer)

checkCompletion lists EVERY open todo, phase by phase, no cap (todo-tracker.ts:209-223). 1000 open todos ≈ 52 KB ≈ 13k tokens per reminder, fired up to todo.remindersMax times. The visible TodoReminderComponent renders the same full list (todo-reminder.ts:29-43). `/todo edit` has the same problem: buildSystemReminder embeds the full markdown, ~100 KB at 1000 todos, not gated by any setting (todo-command-controller.ts:91-102).

Control: keep the OPEN count small (close phases as you go), or set todo.reminders=false for massive sessions.

### Three regimes

1. Small/medium, all live. 2-5 phases, 3-8 todos per phase, one session. Everything in the tool.
2. Large, all live. 10s of phases, up to ~400 todos. Everything in the tool. Phase names are the navigation; the HUD collapses inactive phases to one line and shows a counter (Todos · n/N). Keep task text short; close phases as you go.
3. Massive, master file + window. 100s of phases, 1000+ todos. The master plan lives in a file (TODO.md or PLAN.md), written with the normal edit tool — the full 1000-item store, greppable and diffable. The tool list holds only the window: current phase todos + next 1-2 phases. At each phase boundary: `done` the phase, `rm` its tasks from the live list (the file keeps the record), `append` the next phase's tasks (copied from the file), update the master file. On a fresh session, `todo import` from the file restores the window. The file is the store; the list is the working set.

### Scale footguns

- `done`, `drop`, `rm` with no target hit EVERY task (getTaskTargets returns all). At 1000 todos that clears or completes the plan. Always name the task or phase.
- `append` uniqueness-checks each new item against the whole list: O(k·n) per call. Append in small batches.
- The HUD shows 5 active tasks and 4 following stages collapsed (interactive-mode.ts:2104-2105). It is not the plan; the list is.
- The transient tool-result block caps at 8 items per phase (PREVIEW_LIMITS.COLLAPSED_ITEMS). Big inits render ~100 phase headers — display cost only.
- On resume the list is restored from the transcript; the master file is not re-read. Sync them at phase boundaries.
- Subagent auto-complete matches by description (≥6-char overlap). At 1000 todos, common words can collide — keep descriptions distinct.

### The science at scale

- LEAD: extreme memoryless decomposition makes errors at a few hard steps irreversible. The window pattern keeps context flowing (each todo carries its verification; the phase carries its outcome).
- Plan eviction: 1000-item plans get evicted from context. The master file survives; re-read it before each phase.
- The working set limit (~7 open items) is about what the model holds and reconciles, not about what the list may contain.

## Failure modes and fixes

| Mode | What it looks like | Fix |
|---|---|---|
| Early myopic commitments | Locks the first approach; error amplified downstream | Cheap exploration first; irreversible steps late; test the plan early |
| No-recovery bottleneck | Each step isolated; one failure poisons the chain | Keep context flowing: short next-step note, lookahead, merge state-sharing steps |
| Plan eviction | Long output or compaction pushes the plan out; agent drifts | Short plan; re-read the list before each phase; goal readable in phase names |
| Plan drift | List says one thing, work another | Phase-boundary review: compare done-criteria to reality, update the plan |
| Zombie todos | Finished or obsolete items stay pending and keep getting promoted | Close them at the end of every turn: done, drop, or block with reason |
| Premature locking | New information ignored; executing an obsolete plan | Re-init on material change; capture mid-task instructions |
| Greedy serial execution | Never re-orders; no cheap-checks-first | Order the list; ordering IS scheduling |
| List-maintenance stall | More time updating than working | 8-item cap; verify by running things, not editing the list |

## What the system does automatically

- Auto-promotion and the single-active-task invariant (demotes extras, promotes earliest open pending).
- Blocked-skip in promotion and in stop-time reminders.
- Discard-on-error: any error in an op rolls back the whole op; nothing half-applied.
- Lenient op repair: a missing `op` is inferred for unambiguous payloads.
- Stop-time reminders (up to remindersMax, auto-continues the loop, blocked excluded).
- Mid-run nudge after 12 mutating calls without a todo touch (max 2 per cycle).
- Error reminder after a failed todo call: fix the payload and retry.
- Eager prelude when `todo.eager` is set (preferred = nudge, always = forced first init).
- Session-title refresh on `init` (treated as a replan).
- Resume reconstruction of the list from transcript entries.
- Subagent auto-complete: a todo matching a finished subagent's description is completed (blocked included; failed/aborted excluded).
- HUD live re-render; display-only auto-clear of closed items after tasks.todoClearDelay (60s default; `view` still shows them).
- `/todo` user edits: persisted as user_todo_edit entries and announced to the model; removals carry do-not-re-add intent.

## Settings

| Setting | Default | Note |
|---|---|---|
| todo.enabled | true | master switch for the tool, reminders, HUD |
| todo.reminders | true | stop-time reminders and the mid-run nudge; off tames the at-scale reminder |
| todo.remindersMax | 3 | per prompt cycle; raise to 5 for long work |
| todo.eager | "default" | "preferred" nudges; "always" forces the first init |
| tasks.todoClearDelay | 60 | HUD display-only; -1 = never clear |
| tools.artifactSpillThreshold | 50 KiB | elides the middle of huge summaries (head+tail 20 KiB each) |
| task.prewalk | false | when on, subagents keep todo and must commit their own list |
| title.refreshOnReplan | true | auto title refresh on init |

## Mechanics and quirks

- Content = identity. Task wording must be globally unique; duplicates are rejected by init and append. Renaming a task orphans it — the old string is the only key.
- ID-lookalike targeting gets a coaching error: "Tasks are referenced by content, not by IDs."
- Targeting order: task, then phase, then everything. `rm` or `done` with no target hits ALL tasks — name your target at scale.
- `block` never reopens closed tasks; re-blocking refines the reason; the reason is collapsed to one line.
- `start` demotes any other in-progress task before marking the target.
- `view` is read-only and safe anytime.
- Markdown round-trip: `[ ]` pending, `[/]` in progress, `[x]` done, `[-]` abandoned, `[!]` blocked, blocker reason in `<!-- blocker: ... -->`; `>` and `~` aliases parse back. Unknown markers abort the parse. Strictly linear, no size limits.
- Default phase names differ by path ("Tasks" vs "Todos") — always pass explicit phase names.
- On resume the list is restored from the transcript: `view` first, never re-init blindly.
- storage: "session" vs "memory" in tool details is metadata only.

## Sources

- arxiv.org/abs/2205.10625 (Least-to-Most), 2305.04091 (Plan-and-Solve), 2305.10601 (Tree of Thoughts), 2210.02406 (Decomposed Prompting), 2510.07772 (ACONIC), 2402.02716 (planning survey)
- arxiv.org/abs/2606.22953 (Plans Don't Persist), 2603.06870 (LEAD), 2604.11978 (HORIZON), 2601.22311 (Why Reasoning Fails to Plan)
- en.wikipedia.org: Miller's number, cognitive load, goal-gradient hypothesis, Zeigarnik effect, INVEST, vertical slice
- nature.com/articles/s41599-025-05000-w (Zeigarnik/Ovsiankina meta-analysis)
- code.claude.com/docs/en/best-practices.md, code.claude.com/docs/en/agent-sdk/todo-tracking.md, code.claude.com/docs/en/how-claude-code-works.md
- geminicli.com/docs/tools/todos
- docs.langchain.com/oss/python/langchain/agents; langchain.com/blog/plan-and-execute-agents
- github.com/yoheinakajima/babyagi_archive; docs.agpt.co
- Local: @oh-my-pi/pi-coding-agent@17.2.12 source (tools/todo.ts, session/todo-tracker.ts, prompts/tools/todo.md, prompts/system/*, settings-schema.ts, session/messages.ts, output-meta.ts); ~/.agents/rules/core.md
