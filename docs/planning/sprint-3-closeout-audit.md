# Sprint 3 Closeout Audit

Status: Closed
Sprint: Sprint 3 - Reliability, Iteration, Quality Review, and Beta Readiness
Closed: 2026-06-04
Owner: War Room Center / Tech Lead

## Verdict

Sprint 3 is closed as a successful local draft-lane hardening sprint.

The product flow is materially more trustworthy for internal dogfooding and scoped draft-lane beta
planning. It is not closed as final Qwen edit acceptance evidence. Local `qwen-image-edit-2511` signoff
remains blocked on this machine and must stay off-box.

## Scope Boundary

Sprint 3 did not add new engines or broad editing surfaces. Work stayed focused on reliability, reveal,
iteration, preset-review process, status communication, and beta readiness.

The real WR3-007 benchmark DB output remains `pending_review` intentionally:

- job id: `dfc36b9bde8d4ee7b111c5196d8ecb24`
- pending output image id: `6ea3269b9814425fa91ab6bdf149b01a`
- reason: keep it available as a pending-review fixture unless explicitly revealed later

## Definition Of Done Audit

| Sprint 3 DoD item | Result | Evidence |
| --- | --- | --- |
| Result iteration is clear: `edit -> reveal if needed -> compare -> refine -> download/reuse` | Pass for local draft lane | Recent-runs and output-library browser validation; revealed outputs expose `Edit this` and `Download`. |
| Pending-review reveal behavior has lightweight live/API validation without launching a new model | Pass | Temp-DB tests, copied benchmark DB API checks, scratch-copy WR3-007 reveal validation. |
| Reference-guided editing is understandable and optional | Pass | UI and workflow copy now distinguish base identity/source image from optional visual guide image. |
| Key job/recovery states are documented and validated with cheap checks | Pass | `docs/testing/job-status-and-recovery-states.md`; backend tests for reveal, delete, recovery, and status metadata. |
| Preset quality review separates local FLUX draft evidence from Qwen signoff | Pass | `docs/testing/preset-quality-review-worksheet.md`; WR3-007 FLUX draft run recorded as draft only. |
| Beta readiness criteria and known limitations are documented and reviewable | Pass with blocker | Beta checklist and tester limitations handoff exist; Qwen acceptance remains the blocker for final edit-model beta. |

## Completed Ticket Summary

| Ticket | Closeout status | Notes |
| --- | --- | --- |
| WR3-001 Validate pending-review reveal path | Complete | Reveal transitions validated without new model jobs. |
| WR3-002 Harden result iteration loop | Complete for local draft lane | Reveal, reuse, download, and output-library paths have browser evidence. |
| WR3-003 Add cheap job/recovery API checks | Complete | Non-model backend tests cover reveal, deletion cleanup, and restart recovery. |
| WR3-004 Improve status and error communication | Complete | Frontend copy helpers plus backend/API presentation metadata. |
| WR3-005 Polish reference-guided UX copy | Complete for Sprint 3 scope | Copy-only polish, no advanced reference weighting UI. |
| WR3-006 Create preset quality review worksheet | Complete | Worksheet exists with evidence lanes, cases, statuses, and watchouts. |
| WR3-007 Run approval-gated draft preset review where feasible | Complete for local FLUX draft lane | One approved FLUX draft run reached `pending_review`; scratch reveal/reuse passed. |
| WR3-008 Add beta readiness checklist and limitations doc | Complete with blocker | Docs exist; verdict remains constrained by Qwen acceptance. |

## Evidence Highlights

- WR3-007 approved FLUX draft run:
  - job id: `dfc36b9bde8d4ee7b111c5196d8ecb24`
  - run id: `37706e19de514559a21a0696d3705d5d`
  - status: `pending_review`
  - elapsed: 2387 seconds
  - pending output image: `6ea3269b9814425fa91ab6bdf149b01a`
  - wrapper exit: `0x00000000`
- Scratch-copy reveal/reuse validation for that run:
  - reveal returned the pending image id
  - status promoted to `succeeded`
  - `pending_output_image_id` cleared
  - run appeared in reusable succeeded history
  - image retrieval returned 200
  - real benchmark DB remained unchanged

## Remaining Blockers

| Blocker | Impact | Recommended owner |
| --- | --- | --- |
| Local `qwen-image-edit-2511` edit signoff crashes with native Windows access violation | Blocks final Qwen acceptance on this machine | AI/ML + Infra |
| No off-box Qwen acceptance record yet | Blocks full intended edit-model beta | AI/ML |
| Clean-machine beta setup has not been revalidated after Sprint 3 | Blocks confident beta handoff | DevOps |
| Live WR3-007 pending output is not revealed | Not a blocker; fixture decision remains open | Tech Lead |

## Beta Decision

Current decision: do not claim final Qwen beta readiness.

Allowed next path: prepare a narrowly scoped draft-lane closed beta or internal dogfood if the limitations
explicitly say FLUX is draft evidence and Qwen acceptance is not complete.

Recommended next sprint: Sprint 4 - Beta Scope Lock and Acceptance Validation.
