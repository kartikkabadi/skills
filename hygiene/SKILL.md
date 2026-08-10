---
name: hygiene
description: Restore the environment after agent work: close only tabs you opened, kill only processes you started, delete only scratch you created, revert state you changed. Use when finishing any task or ending a session, after creating temp files, opening browser tabs or workspaces, or starting background processes.
---

# Hygiene

The rule: leave the environment as you found it, minus the one artifact the user asked for. The cleanup pass covers only what you created — files, tabs, workspaces, processes, state. Run it when work ends, not someday.

## Own it, or leave it

Cleanup only ever touches what you created. The test for anything you find is: did I make this? If not, leave it. If you are unsure, leave it and mention it.

User things are off limits: their files, their tabs and workspaces, their processes, their uncommitted changes. Deleting is for scratch only. The deliverable, verification artifacts the user will want (a diff, a log of a failure you are reporting), and anything referenced in your report all stay.

## During the work

Prevention beats cleanup, and the habits that prevent mess are also the record of what you created:

- **Scratch goes in /tmp or the system temp dir.** Never the home directory, never the repo root, never ~/Downloads unless the user asked for a file there. Name scratch files clearly: `/tmp/hygiene-audio-probe.py` beats `~/test2.py`.
- **Do not create files the user did not ask for.** No summary.md, notes.md, plan.md unless they requested a document. The chat reply is the summary.
- **One browser tab per task; one workspace per session.** Whatever browser surface you used — an in-app browser, ego-browser, Playwright, a CLI automation tool — keep its tabs and workspaces tidy by the same rule: tabs you opened close after the check; workspaces, spaces, or contexts you created close with the task. Use the browser tool's own teardown API when it has one (ego-browser's `completeTaskSpace`, Playwright's context close); that tool's skill documents its cleanup contract.
- **Kill what you start.** Background servers, watchers, tail -f, dev processes: stop them when done or hand them off explicitly ("left the dev server running, it's on :3000").

## At the end

Before you report done, walk the mess:

1. **Files.** List what you created outside the deliverable: scripts, downloaded fixtures, extracted archives, build output, screenshots. Delete the scratch ones. Keep only what the user asked for or what a future session genuinely needs, and put keepers somewhere sensible (the repo, a project folder), not /tmp and not home.
2. **Tabs, workspaces, windows.** Close the tabs you opened and the workspaces, spaces, or contexts you created, using the browser tool's own teardown API where one exists (ego-browser `completeTaskSpace`, Playwright context close, in-app browser close). Close preview panes and terminals you spawned for one-off checks. What you did not open stays: the user's tabs, workspaces, windows, and the browser's restore history are theirs.
3. **Processes.** Kill anything still running that isn't meant to outlive the session.
4. **Bloat inside files.** The cleanup applies to content too, not just file count. If you wrote 40 lines where 10 work, trim. Delete debug prints, commented-out dead code, and "notes to self" comments before calling it done.
5. **State you changed.** If you toggled a setting, checked out a branch, or pointed a config somewhere temporary, put it back.

## The report

If cleanup deleted or closed things, one line in the final report: "cleaned up: removed /tmp scratch, closed 3 tabs, killed the dev server." If nothing needed cleaning, say nothing.
