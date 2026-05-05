# Workflow

## Default operating sequence
1. recover project context from repo docs
2. clarify the objective and success criteria
3. choose the smallest useful mode
4. gather evidence before making recommendations
5. synthesize a single decision-ready answer
6. record durable context when decisions materially change the project plot

## Heavy model execution gate
- before any model run that can load large weights or hold substantial CPU or memory, notify the user about the expected resource cost
- get explicit user approval before starting that run
- default to dry-run, preflight, or non-model validation until approval is granted

## Existing-project workflow
- start read-only unless editing is requested
- map the current state before proposing large changes
- preserve codebase and docs during audits
- implement only after the path is clear enough to execute safely

## Decision-complete output rule
Every meaningful recommendation should include:
- rationale
- expected impact
- cost or effort
- technical risk
- simpler alternative
