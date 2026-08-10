---
name: todo-mastery
description: Use Oh My Pi's todo tool to its full capability: phased, heavily decomposed task lists with real-time progress tracking, from one-session tasks to 1000-todo programs. Teaches the agent how to plan work as phases of small verifiable todos, how to calibrate granularity to avoid over- and under-decomposition, how to keep the list honest as it works, and how to work at scale with master files and live windows. Use when starting any multi-step task, when the user provides a plan or checklist, when the task spans phases or sessions, when progress must stay visible, or when the todo list has drifted from reality.
---

# Todo Mastery

Phased decomposition + real-time tracking for the todo tool. The list is the agent's external working memory: it helps only when it IS the plan (not a summary of it), small enough to hold in view, and always true.

## The three failure modes

- Over-decomposition: ceremony, status churn, more time updating the list than working.
- Under-decomposition: bloated steps, no checkpoints, silent stall.
- Stale list: progress real but not tracked; the user sees a lie.

## The discipline in one pass

1. Plan before work. Goal → phases. Each phase → todos (3-8, one verifiable action each). A session task fits in 2-5 phases; bigger work gets more — see Workflow 5.
2. One `init` carries the whole surface: investigation → implementation → verification. Every item of a user-provided plan becomes its own task. Never trim.
3. Phase = a named outcome ("Auth", not "auth stuff"). Todo = one verifiable action, 5-10 words, what not how, globally unique wording.
4. Order = execution order. Cheap and reversible first; irreversible last. The tool auto-promotes the earliest open task, so list order decides what happens next.
5. Track in real time. Mark done the moment it's done; batch todo ops with real work; append discoveries; block what you can't act on; re-init when the plan changes.
6. Trust the system's nudges. Stop-time reminders, the 12-mutation nudge, and the error reminder all mean the list is behind. Fix it, then continue.

## Workflow 1: Plan (before the first edit)

- Decide phases by outcome: what is true when each is done? A phase with one todo is not a phase (fold it in). A phase with 8+ pending todos is two phases (split at the natural boundary).
- First phase: small, fast, verifiable — the cheapest place to learn the plan is wrong. Investigation before implementation. Irreversible work last.
- Each todo must name its verification. If you can't state the check, you can't write the todo. "Think about X" is not a todo; "Decide X and record it" is.
- If a todo needs 3+ distinct actions, it is 2-3 todos. If its only proof is the status flip, delete it.
- One `init`, covering everything. Do not init twice in a turn; append as you discover.

## Workflow 2: Track (while working)

- Mark done immediately after finishing — in the same message as the real work (todo ops never travel alone).
- Discovered a subtask? `append` it to the right phase (lazily creates the phase). New instructions mid-task? Capture before proceeding.
- Can't act (user decision, another agent, external service)? `block` with a reason. If the blocker is itself actionable, `append` an unblocking task instead. `unblock` when it clears.
- Plan changed materially? Re-`init` the whole list (also refreshes the session title). Otherwise prefer `append`/`rm`/`done` — the tool keeps everything else.
- Keep strings stable once introduced. Renaming a task orphans it (content IS the id). Before targeting a task from memory, `view` — never guess.
- Never mark a todo done on a subagent's word alone — verify the gate first.
- Finish a turn with the list matching reality: done items closed, leftovers listed, stale items abandoned or blocked.

## Workflow 3: Calibrate (when in doubt, run the procedure)

Ask in order:
1. Can I state its verification? No → rewrite or delete.
2. Can I finish and verify it in this turn? No → split.
3. Does it need 3+ distinct actions? Yes → split into 2-3 todos with own checks.
4. Phase has 8+ pending, or the todo is a phase of one? → split phase / merge todo.
5. Does completing it change anything observable? No → merge or delete.
6. Blocked by an earlier todo? Move it after its unblocker — don't preemptively `block`.

## Workflow 4: Recover (errors, drift, resume)

- Todo call errored → fix the payload and retry before continuing. The tool discards the whole failed op; nothing half-applied.
- At each phase boundary: compare done-criteria to reality, then update the plan (add/abandon phases) before proceeding. The plan is a hypothesis, not a contract.
- On resume the list is already restored from the transcript. `view` first; don't re-`init` blindly.
- Zombie todos (done work still pending, obsolete items) get auto-promoted and waste turns. Close them: done → done, obsolete → drop, unachievable → block with reason.

## Workflow 5: Work at scale (10s-100s of phases, 1000+ todos)

The tool has no hard limit: a 1000-todo list is accepted, the HUD stays bounded, the markdown round-trip is linear. Two real costs:

- Every todo op returns a summary of the whole list: about 29 tokens per task. Under ~450 todos the model sees it all; above that the middle is elided (head + tail only).
- The stop-time reminder lists EVERY open todo, uncapped: 1000 open todos ≈ 13k tokens per reminder.

Three regimes:

1. Small/medium, all live. 2-5 phases, 3-8 todos per phase, one session. Everything in the tool.
2. Large, all live. 10s of phases, up to ~400 todos. Everything in the tool. Phase names are the navigation — the HUD collapses inactive phases to one line and shows a counter. Keep task text short. Close phases as you go.
3. Massive, master file + window. 100s of phases, 1000+ todos. The master plan lives in a file (TODO.md or PLAN.md). The tool list holds only the window: current phase todos + next 1-2 phases. At each phase boundary: `done` the phase, `rm` its tasks, `append` the next phase's tasks, update the master file. The file is the store; the list is the working set.

Scale footguns:
- `done`, `drop`, `rm` with no target hit EVERYTHING. Always name the task or phase.
- `append` checks each new item against the whole list. Append in small batches.
- The HUD shows 5 tasks and 4 stages collapsed. It is not the plan; the list is.
- On resume the list is restored, but the master file is not re-read. Sync them at phase boundaries.

## What the system does for you (don't re-implement it)

- Auto-promotes the earliest open pending task; demotes extras. Order the list, don't micromanage `start`.
- Skips blocked tasks when promoting; excludes them from stop-time reminders.
- Nudges after 12 mutating calls without a todo touch (max 2 per cycle); reminds at stop (up to remindersMax, then auto-continues); injects an error reminder when a todo call fails.
- Auto-completes todos matched to a finished subagent (blocked included; failed/aborted excluded).
- Restores the list on resume; re-renders the HUD live; hides closed items from the HUD after 60s (still in `view`).
- The user can edit the list via `/todo` — respect removals; never re-add unless asked.

## Sizes

- Working set: about 7 open items at once. This is what the model holds and reconciles — not a limit on the list. The list may hold 1000; the model reasons about 7.
- A phase is 3-8 todos when you are doing the work. Bigger plans get more phases, not bigger phases.
- Heavily decomposed does NOT mean 20 tiny items per phase — it means each phase is cut to its verifiable units and the hard constraints (dependencies, interfaces) carry the depth.
- When a phase exceeds one session's work: delegate a subagent per slice instead of growing the list.

See [REFERENCE.md](REFERENCE.md) for the full guide (principles, warning signs, failure modes, settings, scale numbers). See [EXAMPLES.md](EXAMPLES.md) for good/bad lists, a tracking walkthrough, and a 100-phase plan.
