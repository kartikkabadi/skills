---
name: unit-economics-analysis
description: Analyze SaaS/product unit economics, pricing, margins, provider costs, break-even points, and sensitivity using verified numbers and The Algorithm.
version: 1.0.0-codex
author: Hermes Agent, adapted for Codex
license: MIT
---

# Unit Economics Analysis

Use when the user asks about pricing, costs, margins, profitability, “can this work at $X/month?”, included usage caps, or provider-cost tradeoffs.

The default posture: first-principles analysis, verified numbers, and deletion before optimization.

## Method

Apply The Algorithm in order:

1. Make requirements less wrong: identify real cost drivers, fixed vs variable costs, and constraints.
2. Delete: remove low-value variable-cost features, unlimited language, overage complexity, unnecessary storage, and tier sprawl.
3. Simplify: one plan, one price, one cap, hard limits when possible.
4. Optimize: target average usage, pre-gate expensive paths, shorten costly flows, use cheaper fallbacks where product-safe.
5. Automate: usage tracking, caps, kill switches, transparent reports.

## Verification Rules

- Never use stale/training-data pricing for current decisions.
- Verify provider costs from primary pricing docs or current repo/provider configuration.
- Inspect the actual tech stack before assuming providers, billing systems, database, or architecture.
- If browsing/current pricing is needed, use primary sources and cite them.
- If numbers are unknown, label assumptions and show sensitivity.

## Output Shape

Lead with the verdict, then numbers:

```text
Verdict
Verified Costs
Worst-Case Scenario
Break-Even Analysis
Sensitivity Table
Realistic Scenario
Algorithm Decisions
Open Risks / Needed Verification
```

Prefer tables over prose. Keep the answer direct.
