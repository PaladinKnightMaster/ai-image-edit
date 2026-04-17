# Decision Log

## 2026-04-17

### Decision: Public MVP is edit-first
Reason:
- stronger product wedge than generic T2I
- better fit for local/privacy-first positioning

### Decision: T2I remains a supporting workflow
Reason:
- current codebase is already relatively mature there
- it supports the generate-to-edit bridge

### Decision: CPU-only development requires a fast-check loop
Reason:
- full local Qwen runs are too slow for normal iteration

### Decision: Quality is primary, efficiency is a guardrail
Reason:
- war-room orchestration should improve decision quality and reduce hallucination, not optimize tokens at the expense of confidence

### Decision: Repo-backed continuity is the memory model
Reason:
- new sessions need durable docs, not dependence on prior chat history
