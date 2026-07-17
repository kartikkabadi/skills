---
name: clean-code
description: Robert C. Martin's (Uncle Bob) Clean Code discipline as enforceable rules for coding agents — naming, function size and structure, arguments, comments, formatting, error handling, side effects, classes, TDD and test design, and architectural boundaries. Use when writing, refactoring, or reviewing any production code, when the user mentions clean code, code quality, readability, refactoring, naming, comments, or Uncle Bob, and proactively before declaring any coding task complete.
---

# Clean Code (Uncle Bob)

This skill distills Robert C. Martin's Clean Code lectures into rules a coding agent must actually follow, not merely acknowledge. The rules are deliberately specific and numeric where Uncle Bob is specific and numeric. When a rule conflicts with an explicit user instruction or an established codebase convention, the user and the codebase win — but the default, absent instruction, is full compliance.

## The prime directive

> **"The only way to go fast is to go well."**

- Getting code to work is **the least important half of the job**. The more important half is writing code that other people can understand and maintain. Code that works but cannot be understood becomes worthless the moment requirements change; code that is understandable but broken can be fixed by anyone.
- **You are not done when it works. You are done when it is right.** Nobody writes clean code on the first pass. Once the code works, clean it — expect to spend roughly as much effort cleaning as you spent making it work. Skipping the cleaning pass because "it works" is the root cause of every rotting codebase.
- **"Quick and dirty" does not exist.** A mess does not slow you down next year; it slows you down within an hour or two ("who the hell wrote that crap?" — after lunch, about your own morning code). There is no short-term win from making a mess. Teams that make messes bottom out at roughly **1% of their original productivity**, and adding people makes it worse because new people learn from the mess and emulate it.
- The working definitions of clean code, from the masters:
  - **Stroustrup:** elegant, efficient — "clean code does one thing well."
  - **Booch:** simple and direct — "reads like well-written prose."
  - **Feathers:** "always looks like it was written by someone who cares."
  - **Cunningham:** every routine is pretty much what you expected — **zero WTFs per minute**, no surprises.
- Software has **two values**: what it does (behavior) and its structure (changeability). Structure is arguably the more valuable — software that doesn't work but is changeable beats software that works but cannot be changed, because the first can be fixed cheaply and the second cannot. "Soft-ware" literally means *changeable product*; if a small requirement change destroys your design, you have reinvented hardware.

## Agent operating rules

Apply these on every coding task, not just when asked:

1. **Two-pass rule.** After the code works (tests pass), do an explicit cleaning pass: extract functions, fix names, delete duplication, delete dead code, restructure error handling. Never present first-draft "it works" code as finished.
2. **Boy Scout rule.** Leave every file you touch a little cleaner than you found it — one better name, one extracted function, one deleted commented-out block. Do not launch unrelated rewrites; just improve what you touch.
3. **Never turn the quality knob down.** Under time pressure, negotiate scope — never quality. Do not skip tests, skip the cleaning pass, or ship known mess to "go faster"; it is a lie, and it is slower.
4. **Refactoring is continuous, not a scheduled task.** The word "refactoring" never appears on a schedule or as a deliverable line item, because you are doing it constantly as part of every change.
5. **Fearless competence via tests.** Never leave code you're afraid to touch. If you can't safely improve something because nothing covers it, add the test first, then improve it. "It is wildly irresponsible to fear what you have created."
6. **Report honestly.** If something is untested, unclean, or a known shortcut, say so explicitly instead of implying completeness.

## Functions

- **First rule: functions should be small. Second rule: they should be smaller than that.** After proper extraction, most functions land at **3–5 lines**, occasionally 6.
- **A function does one thing.** The objective test for "one thing": **if you can meaningfully extract another function out of it, it was doing more than one thing.** So *extract till you drop* — keep extracting until you cannot meaningfully extract anymore. You will not drown in tiny functions: naming each extraction builds a readable semantic tree you navigate by name.
- **One level of abstraction per function**, and that level is **one below the function's name**. Never oscillate between high-level concepts (`WikiPage`, domain objects) and low-level mechanics (`StringBuffer`, byte offsets) in adjacent lines — that oscillation is rude to the reader. Authors think that way while getting things working; the cleanup pass removes it.
- **Indent depth after extraction: zero or one, occasionally two.** Deeply nested code is a sign of unextracted functions. The bodies of `if`/`else`/`while` blocks should ideally be a single line — usually a well-named function call: `if (employeeIsTooOld()) fireEmployee();`
- **Function names are verbs** (`renderPageWithSetupsAndTearDowns`, not `testableHtml`). Long, precise names are correct for small private helpers; short names for broad public entry points (see Naming).
- **Write polite functions (the newspaper rule).** A reader should get the headline from the name, the synopsis from the top-level function, and detail only as they descend — and be able to stop reading at any level. The target: a function a maintainer understands in ~3 seconds, not one that takes 30 minutes and full knowledge of every collaborator.
- **Large functions hide classes.** A long function with locals at the top and blocks manipulating them is a class struggling to be born: the extracted functions sharing those variables become methods, the variables become fields. Extract to discover it.
- **Use explanatory variables** to turn expressions into prose: `boolean isTestPage = pageData.hasAttribute("Test")` beats inlining the expression into a condition.

### Arguments

- **Prefer 0 arguments, then 1, then 2. Three is the practical maximum.** Orderings grow factorially (3 args → 6 orderings, 4 → 24, 5 → 120); long comma-separated lists are rude and error-prone.
- **If three or more values are cohesive enough to travel together, they are an object.** Make it one.
- **Never pass booleans as arguments** (flag arguments). `doThis(5, 6, true)` forces every reader to go find out what `true` means, and it announces the function does two things — split it into two functions. The narrow exception: genuinely setting the state of a switch (`setEnabled(bool)`).
- **No output arguments.** Arguments are inputs; results come back through the return value. Output arguments violate the principle of least surprise and force a double take.

### Side effects, command-query separation, and paired operations

- **Command-Query Separation:** functions that return values must not change system state; `void` functions are the ones that change state. This convention lets readers call queries fearlessly.
- **Side effects come in pairs** — open/close, allocate/free, acquire/release, subscribe/unsubscribe. "Like the Force, there are always two." Humans are terrible at remembering the second half, which is why leaks exist. Where possible, contain the pair inside one function that takes a lambda/callback: `withOpenFile(name, file -> process(file))` opens, processes, and closes so the caller cannot forget.
- Beware hidden **ordering dependencies** between side-effecting calls; they cause the multi-day bugs fixed by swapping two lines.

### Error handling

- **Prefer exceptions to error codes.** Error codes clutter the caller with checking logic and get ignored.
- **Error handling is one thing.** If a function has a `try`, the `try` is the **first executable statement**, the try block contains a **single function call**, and after `catch`/`finally` there is **nothing else in the function** — no prefix code, no suffix code.
- **Never nest try/catch blocks.** Extract the inner work into its own function.
- Exceptions should be unchecked (`RuntimeException` derivatives in Java) and scoped meaningfully — e.g. defined as a nested class of the class that throws them (`Stack.Underflow`).
- Don't return or pass `null` where you can avoid it; a null check spreading through code is a design smell.

## Naming

- **Names must reveal intent.** If a name needs a comment to explain it, the name failed. `elapsedTimeInDays`, not `d`.
- **Variable name length is proportional to scope.** A loop index alive for one line may be `i`; a field or global alive across a system needs a long, descriptive name.
- **Function and class name length is inversely proportional to scope.** Public, widely-used entry points get short convenient names (`open`); deeply private extracted helpers get long, precise names (`throwExceptionIfFileDoesNotExist`) — each level of extraction downward earns a longer name.
- **Functions are verbs, classes and variables are nouns.**
- **Avoid noise words:** `data`, `info`, `manager`, `processor` — `Product`, `ProductData`, and `ProductInfo` tell the reader nothing about how they differ.
- **Distinguish names meaningfully.** `getActiveAccount()`, `getActiveAccounts()`, `getActiveAccountInfo()` in one codebase is a WTF generator. Number series (`a1`, `a2`) are the last resort of someone who gave up.
- **Names must be pronounceable and searchable.** `genymdhms` is not a name, whatever it stands for.
- **Avoid optical illusions:** names that differ only near the end of a long prefix, or `l`/`1` and `O`/`0` confusion.
- **No encodings or Hungarian prefixes** (`m_`, `sz`, `its`, interface `I` prefixes) — modern IDEs and type systems make them noise.
- Names carry the design: a well-named extraction (`getFlaggedCells` over a `gameBoard` of `cell`s) teaches the reader the whole domain without documentation.

## Comments

- **Every comment is a failure** to express intent in code. Sometimes you fail — languages can't say everything — so comments are an *unfortunate necessity*, never an achievement. Before writing a comment, try to make code that says the same thing: prefer `if (employee.isEligibleForFullBenefits())` to a comment above a raw boolean expression.
- **Comments lie.** Not maliciously — they rot. Code changes, comments don't, and IDEs paint them in ignore-me gray. The fewer you write, the fewer lies you maintain.
- **Never comment bad code — clean it.** A comment on confusing code is effort spent in the wrong place; extract explanatory variables and functions instead (turn Tomcat's opaque dependency comment into `if (moduleDependencies.contains(ourSubsystem))`).
- **Comments may only describe the code immediately next to them.** A comment referencing distant code (where-used lists, cross-file behavior claims) is a lie waiting to happen.
- **Commented-out code is an abomination. Delete it on sight.** Everyone else is too scared to delete it, so it accumulates forever. Source control remembers everything; that is its job. Never check in commented-out code.
- **TODO means "don't do."** A TODO must be resolved or deleted before commit; once checked in it becomes a permanent monument to a thing nobody will do.
- Forbidden comment forms: journal/change-history comments (git does this), closing-brace comments (`} // end if`), JavaDoc on trivial fields and default constructors, mandated boilerplate headers on every function/class, ALL-CAPS yelling on routine declarations, redundant restatements (`// increment i`).
- Acceptable comments (rare, deliberate): legal/copyright headers; explanation of a regex's intent; explanation of a genuinely forced idiom (canonical `compareTo`, singleton accessor); warnings of real consequences ("SimpleDateFormat is not thread-safe", "this test loads a 10M-line file — don't run casually"); public API documentation for **external** consumers, kept minimal and free of HTML soup. Inside a team, names and structure should carry the meaning.

## Formatting and file size

- **Small files.** Strive for an average source file around **50 lines**, with most files **under 100** and none in the thousands. Significant systems (FitNesse, ~50K lines) are built entirely from files like this. File size is a style you choose, not a function of project size — the statistics prove it.
- **Short lines.** Most lines should be **30–40 characters**; treat **~80** as the soft ceiling and never force horizontal scrolling (hard barrier ~120–150). Readers do not scroll right; whatever lives out there is invisible.
- **Newspaper layout (step-down rule):** important, high-level functions at the top of the file; detail increases as you read downward; callee below caller where the language allows.
- Vertical whitespace separates concepts; related lines stay dense. Variables declare near their use.

## Switch statements, polymorphism, and the Open-Closed Principle

- A `switch` (or if/else chain) on a type code is a **dependency magnet**: every operation grows its own copy of the switch, adding a new variant means hunting down every one of them (some disguised as if/else, some with silently-missing cases), and the switch module depends on everything it dispatches to — so everything recompiles and redeploys together.
- **Default resolution: polymorphism.** A base type with derivatives, each carrying its own behavior. Adding a variant then means adding one new class — no existing code changes. This is the **Open-Closed Principle**: modules should be open for extension, closed for modification.
- Reserve switches for the edges of the system (a single point creating the polymorphic instances) and for genuinely closed sets. One switch per type is tolerable; one per operation is rot.
- This is also what makes **independent deployability** possible: modules that change for different reasons (GUI whims vs. business rules) must not be welded together by dispatch logic.

## Duplication (DRY)

- **Don't repeat yourself.** Copy-paste-tweak blocks are sloppiness left over from getting it working; extract the common shape into a function and pass the variation as arguments.
- Duplication of *structure* counts too: repeated loop/traversal skeletons should be extracted once, with the per-node behavior passed in as a lambda or command object.
- In tests, remove duplication only once green — extract shared setup, but never at the cost of test readability.

## Tests and TDD

Testing is not optional garnish. A test suite you trust is the "green button" that makes fearless cleaning possible; without it, every rule above degrades into good intentions.

### The Three Laws of TDD

1. **Write no production code except to make a failing test pass.**
2. **Write no more of a test than is sufficient to fail — and failing to compile counts as failing.** Stop the moment it fails.
3. **Write no more production code than is sufficient to pass the currently failing test.**

The cycle is seconds long, not minutes. Consequences of living inside it: everything worked a minute ago; debugger use collapses to nearly never (you don't *want* to be good at the debugger); and the tests become perfectly synchronized, executable, low-level documentation — the code examples every developer flips to first.

### TDD craft rules

- **Test the test:** watch it fail before making it pass. A test you never saw fail proves nothing.
- **Start with a "nothing" test** that wires up the environment.
- **Tests get more specific; production code gets more general.** Each new test constrains further; each production change must generalize, never hard-code the shape of the current tests. If your production code is a lookup table of the test inputs, you broke this rule.
- **Don't go for the gold.** Test the periphery (empty, one element, errors) before the central behavior; surrounded properly, the core often falls out almost for free.
- **Write tests after the fact only as a fallback**, and know its costs: you already "know it works," so you'll skip the hard ones, leaving holes — and a parachute with holes is worse than knowing you don't have one.

### Test-suite design

- **Tests are first-class code.** They are part of the system and obey every rule in this skill — small functions, good names, no duplication, clean structure. The *fragile test problem* (one production change breaks a hundred tests) is a test-suite **design** failure: decouple tests from implementation details, test through stable APIs.
- **Do not create one test class per production class.** That 1:1 coupling welds test structure to app structure and guarantees fragility. Test *behaviors*. When refactoring extracts new functions and classes from covered code, existing tests already cover them — don't reflexively add mirror tests.
- **Coverage: the only meaningful target is 100%, held as an asymptote.** 80% coverage means shrugging at 20% of the system possibly not working. But coverage is a *team introspection* number: never a management KPI, never a build-failure threshold — both incentives teach people to write assertion-free tests, making the number a lie.
- **Every test automated.** If a computer can run it, a computer must run it. Manual regression testing always decays into skipped tests under pressure. The only legitimate manual testing is *exploratory* — humans creatively trying to break the system.
- **The pyramid above unit tests:** acceptance/component tests specify business behavior (written up front, defining "done" — a story counts only when its acceptance tests pass); integration tests check plumbing between assemblies; unit tests remain the foundation. In a healthy process, **QA finds nothing** — QA specifies behavior at the start, rather than fishing for bugs at the end.
- **Minimize inheritance** (it is the tightest coupling there is); when you must inherit, inherit as little implementation as possible, and test each level explicitly.

## Classes and cohesion

- Classes should be **small**, measured in responsibilities, not lines: **one reason to change** (Single Responsibility). If you can't name the class without "And"/"Manager"/"Processor" hedges, it has too many.
- Cohesion test: methods should use most of the fields. Subsets of methods clinging to subsets of fields are hidden classes — split them out (the same discovery that extract-till-you-drop makes inside long functions).
- Keep variables and helpers private; expose the narrowest interface that callers need.

## Architectural boundaries (summary discipline)

Full treatment belongs to a clean-architecture skill, but these rules bear directly on everyday clean code:

- **The Dependency Rule:** across every architectural boundary, source-code dependencies point **toward the business rules**. GUI, database, web, frameworks, message buses are I/O devices — details, plugins to the core, never things the core knows about.
- **Architecture should scream the domain** ("payroll system", "accounting"), not the framework ("Rails app", "Spring app"). The top-level structure names use cases, not delivery mechanisms.
- **Business rules must not know about SQL, schemas, rows, or ORMs.** Access data through gateway interfaces owned by the core, implemented below the boundary. Objects cross the boundary; rows do not.
- **A good architecture maximizes the number of decisions *not* made.** Defer database, framework, and delivery choices to the last responsible moment — FitNesse deferred its database indefinitely and never needed one.
- **Frameworks do not commit to you; you commit to them.** Keep framework types out of your core; confine dependency-injection wiring to a small `main`/composition module at the edge rather than scattering annotations through the system.

## Definition of done — pre-completion checklist

Before declaring any coding task complete, verify every line of this. If any item fails and you proceed anyway, state it explicitly to the user.

- [ ] Tests exist for the new/changed behavior, they failed before the change, and all tests pass now.
- [ ] The cleaning pass happened: this is second-draft code, not first-draft "it works" code.
- [ ] Every function is small, does one thing, sits at one abstraction level, and nothing meaningful is left to extract.
- [ ] No function takes more than 3 arguments; no boolean flag arguments; no output arguments.
- [ ] Every name reveals intent; verbs for functions, nouns for classes; length matched to scope.
- [ ] No redundant comments, no commented-out code, no TODOs, no journal entries. Any surviving comment earns its place.
- [ ] No duplication — of code or of structure.
- [ ] Error handling is exceptions-first, `try` blocks contain one call, no nested try/catch.
- [ ] No type-code switch chains where polymorphism belongs; no new dependencies from business rules toward I/O details.
- [ ] Every touched file is at least slightly cleaner than before.
- [ ] You know it works — you are not guessing, hoping, or extrapolating from "it worked on one input."

> **"We will not ship crap."** When you release code, you *know* it works — the discipline above is how you know.
