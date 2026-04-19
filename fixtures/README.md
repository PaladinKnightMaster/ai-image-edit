# Fixtures

This directory is reserved for local benchmark and QA fixture assets.

## Private benchmark assets

Do not commit portrait or reference fixture images to the repo unless they are explicitly approved for
public source control.

Store local-only benchmark assets under:

`fixtures/private/benchmark-pack-v0/`

Those files are gitignored. Filenames should match the asset ids documented in:

- `docs/testing/benchmark-pack.md`
- `docs/testing/benchmark-pack.v0.json`

## Intended use

- acceptance-tier quality review
- preset tuning against fixed cases
- reference-guided workflow validation once Sprint 2 lands
