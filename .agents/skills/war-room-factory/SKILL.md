---
name: war-room-factory
description: Dynamic war room entrypoint. Choose solo, consult, or war-room mode for non-trivial project work and return one synthesized recommendation.
---

# War Room Factory

Use this as the default entrypoint for non-trivial project work.

Goals:
- choose the correct mode
- choose the smallest useful specialist set
- protect quality and confidence first
- avoid unnecessary fan-out and duplicated analysis

Modes:
- Solo for narrow, low-risk work
- Consult for one main owner plus one or two cross-checks
- War Room for baseline audits, MVP decisions, release readiness, and quality-critical tradeoffs

Required commander output:
- objective
- chosen mode
- activated roles
- findings
- recommendation
- risks
- next actions

Use these references before doing substantial work:
- `AGENTS.md`
- `ai/core/*`
- `ai/war-room/*`
- `docs/context/*`
- `docs/planning/*`
