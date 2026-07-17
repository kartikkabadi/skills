---
name: telephony-product-architecture
description: Design and feasibility-check phone-call products across carrier routing, forwarding, iOS/Android constraints, CPaaS providers, caller ID, and AI call handling.
version: 1.0.0-codex
author: Hermes Agent, adapted for Codex
license: MIT
---

# Telephony Product Architecture

Use when working on phone-call products: spam screening, honeypots, voicemail replacement, AI receptionists, CPaaS numbers, call forwarding, caller ID, or native mobile call integrations.

## Core Principle

Cellular call routing lives in the carrier network, not inside the app UI.

Always separate:

- carrier/network-level routing
- OS caller ID/blocking APIs
- CPaaS-controlled numbers
- user-device setup flows
- AI/call webhook handling

## First Checks

1. Define the number being controlled: user SIM, CPaaS-owned, ported, secondary/eSIM.
2. Define desired routing timing: before ring, no-answer, busy, unreachable, all calls, unknown callers only.
3. Define platform constraints: iOS, Android, carrier portal/star codes, server-side CPaaS webhook.
4. Verify carrier/API reality from primary sources when making current claims.

## Platform Reality

iOS apps can support caller ID and blocking, but they cannot act as cellular call routers for normal mobile calls.

Android may support more device-assisted dialer/MMI flows depending on API level, permissions, carrier, and OEM behavior, but that is not the same as server-side carrier control.

CPaaS-controlled or ported numbers give programmable routing through provider webhooks/APIs, but porting and adoption create friction.

## Common Architecture Options

- Manual conditional call forwarding: fastest path for existing mobile numbers, but carrier-dependent and usually not unknown-call-only.
- Port number to CPaaS: most control, slower adoption and trust burden.
- Secondary/eSIM shield number: fast programmable control, requires behavior change.
- Carrier partner APIs: strategic/BD path unless exact self-serve docs exist.

## Output Shape

Lead with the recommendation, then:

```text
What carriers/network routing can do
What iOS/Android can and cannot do
Hard blocker
Ship-fast architecture
Long-term architecture
Verification still needed
```
