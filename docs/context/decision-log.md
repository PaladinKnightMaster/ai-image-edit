# Decision Log

Status: Active index
Last updated: 2026-07-16

## 2026-07-16

### CPU-only operation is a hard roadmap constraint

- no current GPU budget or hosted-GPU plan
- daily development and release smoke remain viable without model execution
- source: `docs/adr/0005-cpu-first-product-and-validation-strategy.md`

### Windows Sandbox is the clean-Windows surrogate

- no independent fresh tester machine is available
- Sandbox can provide disposable Windows installation evidence
- Docker/WSL2 remains reproducibility evidence, not native Windows acceptance

### SQLite-backed orchestration remains the default

- the product is single-user, local, and offline-first
- attempts, leases, cancellation, retry, and recovery are proven before adding a required workflow service
- source: `docs/adr/0006-durable-job-orchestration.md`

### Temporal is an optional learning lane

- the first spike uses fake activities and no model
- Temporal must justify its local service and packaging overhead before adoption

### Saga compensation is selective

- compensation applies to temporary output, leases, and partial metadata
- user uploads and committed successful outputs are preserved

### Documentation uses explicit lifecycle authority

- live context is concise and current
- accepted ADRs hold durable decisions
- prepared runbooks do not count as execution evidence
- superseded live snapshots are archived

## 2026-04-17

### Public MVP is edit-first

The edit-first direction is a stronger product wedge than a generic image generator and fits local/private use.

### T2I remains a supporting workflow

Generation supports the generate-to-edit bridge.

### CPU development uses a fast-check loop

Full local model runs are too slow for normal iteration.

### Quality is primary and efficiency is a guardrail

The war-room process optimizes decision quality before speed or token savings.

### Repo-backed continuity is canonical

New sessions recover the project from repository docs rather than prior chat history.

The full original 2026-04-17 snapshot is preserved at
`docs/archive/context/decision-log-2026-04-17.md`.
