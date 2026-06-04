# Beta Scope Decision

Status: Locked for Sprint 4
Decision date: 2026-06-04
Owner: War Room Center / Tech Lead + Product
Related ticket: WR4-001

## Decision

Proceed with **draft-lane closed beta preparation**, not final Qwen-acceptance beta.

The beta scope is locked to workflow validation, setup validation, reveal/reuse confidence, tester
feedback, and local draft-lane behavior. The beta must not claim final `qwen-image-edit-2511` quality
until off-box Qwen acceptance evidence exists.

## Rationale

Sprint 3 closed with strong local product-flow evidence:

- reveal/reuse behavior has backend/API tests and scratch-copy validation
- the edit-first workflow has browser evidence for reveal, reuse, download, and output-library flows
- one approved FLUX draft run reached `pending_review` and produced a usable pending output
- status, recovery, and beta limitations are documented

Sprint 3 did not close the intended Qwen acceptance lane:

- local `qwen-image-edit-2511` remains blocked by a native Windows access violation
- FLUX draft evidence cannot be promoted to Qwen acceptance
- no off-box Qwen benchmark record exists yet

The best business and engineering path is to keep momentum with a narrow, honest beta lane while preparing
off-box Qwen validation in parallel.

## Allowed Beta Scope

The draft-lane closed beta may evaluate:

- setup and launch experience on target machines
- whether `Edit Photo` is the obvious primary workflow
- base image plus optional reference-image clarity
- portrait preset language and workflow usefulness
- long-running job status and recovery communication
- manual-review reveal behavior
- compare, download, reuse, and output-library behavior
- local FLUX draft-lane behavior as draft evidence only

## Not Allowed In This Beta Scope

The beta must not claim or depend on:

- final Qwen edit-model quality
- acceptance-tier portrait preset quality
- hosted GPU execution
- new engine families
- masking or region editing
- batch editing
- Android or mobile companion work
- broad new preset packs

## Required Wording Boundary

Use this boundary in tester-facing material:

This beta validates the local edit-first workflow and draft-lane behavior. The intended Qwen edit-quality
acceptance lane is still pending off-box validation and should not be judged from this machine's FLUX
draft outputs.

## Go / No-Go

| Beta type | Decision | Reason |
| --- | --- | --- |
| Internal dogfood | Go | Product-flow evidence is strong enough and limitations can be internal. |
| Limited draft-lane closed beta | Conditional go | Allowed only with explicit limitations and no Qwen quality claims. |
| Final Qwen-acceptance beta | No-go | Off-box `qwen-image-edit-2511` acceptance evidence is missing. |
| Public beta | No-go | Runtime/setup and Qwen acceptance are not yet strong enough. |

## Immediate Follow-Up

Sprint 4 should continue with:

1. WR4-002 off-box Qwen acceptance packet
2. WR4-004 clean-machine release smoke
3. WR4-005 final tester handoff aligned to this scope
4. WR4-007 release checklist and risk register

Keep WR3-007 job `dfc36b9bde8d4ee7b111c5196d8ecb24` pending as a benchmark fixture unless the fixture
decision changes explicitly.
