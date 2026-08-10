---
name: agent-council
description: Assemble an agent council to decide a contested question. One subagent per skill lens loads its skill, votes on the candidate options from that lens, later waves see earlier findings, then you tally and report. Use when Kartik wants multiple perspectives on a decision, says "give agents each of these skills and get them to decide", "1 agent per skill", "spawn a subagent per skill", or asks for votes, recommendations, or a council on an architecture, design, or approach.
---

# Skill: agent-council

## What this is

The council method: a contested question gets N answers, one per skill lens, and the tally plus the merged conditions beat any single agent's judgment. Facts come from primary sources, votes come from lenses, the tally is yours.

## When it fits

- A design, architecture, or approach question with real candidates.
- The owner names skills to involve, or the question touches many domains (performance, quality, security, ops, taste).
- One opinion is not enough and the owner asked for a vote.

## Steps

1. **Frame the decision.** Define 3-4 concrete candidates with verified facts each, plus a rejected baseline. Facts first: every feasibility claim rests on a cited primary source, not memory. Kill-the-design facts are the prize (a cloud VM where local compute was assumed, a paid beta platform without the critical dependency, a "pro" model that is text-only).
2. **Choose the lenses.** One subagent per skill the owner invoked, or one per relevant domain when the owner did not name skills. Each member gets the skill's path and the instruction: load it via the skill tool if available, else read the SKILL.md directly. A lens the owner named but you cannot load: evaluate from its description, and say so.
3. **Write the common brief.** Same facts and candidates for every member, so votes are comparable. Deliverable format, word cap, read-only. Each member returns: vote (A, B, C, or "none" plus what to change), top-3 recommendations from its lens, up to 2 red flags, one "verify first" sentence. Under 300 words.
4. **Run in waves.** Parallel within a wave. Brief later waves on earlier findings so votes build on votes. A member that returns empty gets one re-run in the next wave, not a silent missing vote.
5. **Tally and report.** Count the votes, name the winner, and describe the split honestly: which lens types voted which way, and what that means (a quality lens and an ops lens disagreeing is a real tradeoff, not noise).
6. **Merge the conditions.** The vote decides the spine, the losing side's conditions decide the details. Fold every surviving condition into the winning candidate and say which conditions came from which lens.
7. **Hand back.** Present the vote table, the winner with merged conditions, and the decisions only the owner can make, each with a recommendation. Wait for the answer. The owner's call on a lens recommendation (for example keeping 5 testers when a lens voted for 1) is final; note it in the record and move on.

## Guardrails

- Members never invent facts. When a vote hinges on a fact (cost, limits, capability), the member verifies it against a primary source and cites it.
- A member's self-report is not the tally. Check that every vote actually arrived and read the ones that disagree with the trend twice.
- Never skip a lens because it will "obviously" vote a certain way. The obvious vote is where the red flags hide.
- Keep each member's deliverable tight so the council costs what one deep read costs, not N long reports.
