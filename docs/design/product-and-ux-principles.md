# Product and UX Principles

## Product identity

This product is a local portrait studio, not a model arena.

The strongest public promise is:

- private
- offline-after-setup
- practical
- portrait-focused

## Experience principles

### 1. Edit-first

The default mental model is:

- bring in a photo
- describe the change
- preview
- compare
- refine
- save

### 2. Generate supports editing

Text-to-image exists to feed the `generate -> edit -> refine` loop, not to define the whole product.

### 3. Preview before final

The product should lean into the CPU reality:

- fast preview first
- slower final render only when requested

### 4. Presets before raw knobs

Most users should see photography and portrait language first:

- headshot cleanup
- studio relight
- background simplify
- fashion portrait

Raw steps, CFG, seeds, and engine controls should exist, but they belong in advanced settings.

### 5. Compare over inspect

The UI should prioritize before/after comparison and result confidence over exposing low-level model details by default.

### 6. Calm, premium, local

The visual language should move away from "arena" and toward "local studio":

- fewer maintenance controls on the main screen
- cleaner workflow boundaries
- less debug noise in the default surface

## Current drift to resolve

- shell language still leans on a shared chat surface instead of explicit create/edit workflow framing
- mode is implicit instead of explicit
- cleanup and debug actions are too close to core product actions
