# Quality and Efficiency Policy

This project treats correctness and product quality as the governing objective. Efficiency, token control, and latency control are guardrails.

## Quality-first rules
- do not under-scope analysis to save tokens
- do not skip verification when quality risk is real
- expand specialist coverage when confidence, domain judgment, or trust requires it
- use benchmark-driven review for quality-sensitive outputs
- do not start heavyweight model execution without explicit user approval after warning about likely memory and compute cost

## Efficiency guardrails
- default to solo mode for small tasks
- escalate to consult or war-room mode only when independence exists
- avoid duplicated role analysis
- prefer durable docs over repeated rediscovery
- stop once sufficient confidence is reached
- prefer approval-gated runner scripts and dry-run paths for heavy local model work

## Context compression
Use durable docs to reduce avoidable context load:
- project brief
- current state
- session handoff
- ADRs
- MVP roadmap
- sprint plans

## Output compression
- summary first
- decision-centric docs
- no long preambles
- no repeated background explanation
