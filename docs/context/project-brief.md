# Project Brief

## Product
AI Image Edit is a local, offline-after-setup image generation and portrait editing product.

## Product Thesis
The strongest public MVP is a privacy-first local portrait editor for Intel Windows desktops and laptops. Text-to-image remains important, but it supports the edit-first product rather than defining it.

## Primary User
- portrait photographers
- solo creators
- privacy-sensitive prosumers
- Intel Windows users who want local image enhancement and guided portrait edits

## Core Workflows
- Edit Photo
- Create from Scratch
- Generate -> Edit -> Refine
- Optional reference-guided portrait editing

## Constraints
- primary development machine is CPU-only
- full Qwen runs can be very slow locally
- local developer workflow must use a fast-check path
- product should remain offline after setup

## Current MVP Direction
- public MVP: edit-first
- T2I: secondary but important supporting workflow
- Qwen Edit: primary edit engine
- Qwen Image: supporting T2I engine
- FLUX GGUF: optional advanced lane
- OpenVINO: research lane until it solves real edit needs
