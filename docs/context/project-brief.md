# Project Brief

Status: Active
Last updated: 2026-09-22
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

Updated 2026-09-22. The older FLUX-as-draft / Qwen-as-acceptance / SDXL-as-research split is superseded for daily use.

- **local mainline:** `sdxl-openvino` for text-to-image and prompt-guided edit on CPU
- optional slow draft: `flux2-klein-9b-gguf`
- frontier edit and T2I: `qwen-image-edit-2511` and `qwen-image-2512`, off-box / GPU only
- Qwen-Image-2.1: catalogued candidate only
- model replacement: benchmark-driven, not roadmap-driven

## Product Surface Direction

The daily screen is a private studio, learned from online create pages and prompt galleries, without a public Explore feed.

- the prompt and Run edit stay pinned
- portrait presets are the prompt library; the next gap is a real thumbnail on each preset
- recent runs are the gallery
- Setup and Utilities open from a collapsible rail and stay off the portrait until asked

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

Current work improves the studio workflow on the existing CPU runtime. It does not add masking,
batch editing, mobile apps, hosted inference, a broad model zoo, or a GPU requirement.
