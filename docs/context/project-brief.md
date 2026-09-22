# Project Brief

Status: Active
Last updated: 2026-07-16
Owner: Product + Tech Lead

## Product

AI Image Edit is a local, offline-after-setup image generation and portrait editing application for Windows.

## Product Thesis

The strongest product direction is a privacy-first local portrait editor. Text-to-image remains useful, but it
supports the edit-first workflow rather than defining the product.

## Project Goal

This is a private, non-commercial learning project. It should provide practical experience in:

- local AI runtime integration
- reliable long-running job orchestration
- image-generation and edit UX
- offline-first Windows operation
- reproducible installation and testing
- benchmark-driven model decisions

Commercial model restrictions are not a current selection blocker for private use. Model provenance and license
terms remain documented for any future sharing, distribution, or commercialization decision.

## Primary User

- the project owner as the first dogfood user
- portrait photographers and solo creators as the product-design reference audience
- privacy-sensitive Windows users who prefer local image processing

## Core Workflows

- Edit Photo
- Create from Scratch
- Generate -> Edit -> Refine
- Optional reference-guided portrait editing
- Review -> Reveal -> Compare -> Download or Reuse

## Hard Constraints

- the primary development and runtime machine is CPU-only
- there is no current budget or plan for GPU hardware or hosted GPU inference
- full model runs can take tens of minutes or longer
- daily development cannot depend on model execution
- model runs require explicit warning and approval
- the product remains offline after dependencies and model assets are installed
- no independent fresh tester machine is currently available

## Current Runtime Direction

- local draft edit lane: `flux2-klein-9b-gguf`
- intended edit acceptance lane: `qwen-image-edit-2511`, currently off-box because the local CPU path crashes
- supporting T2I lane: `qwen-image-2512`
- research lane: `sdxl-openvino`
- model replacement: benchmark-driven, not roadmap-driven

## Engineering Direction

- keep FastAPI, Next.js, SQLite, filesystem images, and runner abstractions
- use SQLite-backed durable orchestration as the default local path
- add attempts, leases, cancellation, bounded retry, and restart recovery incrementally
- keep Temporal deferred; SQLite remains the orchestrator until a new ADR adopts a workflow service
- use Saga compensation only for partial side effects
- keep browser Service Workers outside inference and job-lifecycle ownership

## Validation Direction

- current workstation: fast checks and local product development
- Windows Sandbox: clean Windows installation and non-model release-smoke surrogate
- Docker/WSL2: dependency/build reproducibility and future CI-style smoke
- independent physical machine: residual future compatibility evidence, not a current development dependency
- stronger off-box hardware: optional model acceptance evidence

## Scope Boundary

Current work improves reliability, reproducibility, performance, and workflow quality. It does not add masking,
batch editing, mobile, hosted inference, a broad model zoo, or a GPU requirement.
