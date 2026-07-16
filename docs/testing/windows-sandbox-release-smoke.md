# Windows Sandbox Release Smoke

Status: Harness implemented; first isolated run pending
Last updated: 2026-07-16
Sprint: Sprint 4 evidence closure / WR5-001
Owner: DevOps + Release Guard

## Purpose

Run the required non-model release smoke from an immutable Git export inside disposable Windows Sandbox. The
harness installs Python, Node.js, Git, backend dependencies, and frontend dependencies inside Sandbox. It does
not copy host environments, model assets, databases, generated images, or caches.

The result is `Windows Sandbox surrogate` evidence. It is not independent physical-machine compatibility proof.

## Safety Contract

- the source ZIP comes from an exact Git commit
- the host worktree must be clean by default
- prerequisite downloads use pinned official URLs and must have valid Authenticode signatures
- the Sandbox rechecks SHA-256 hashes before installation
- the source mapping is read-only and the evidence mapping is writable
- vGPU, clipboard, audio/video input, and printer redirection are disabled
- the package manifest sets `model_execution_authorized` to `false`
- the bootstrap never submits a job or invokes a model runner

## Prepare And Launch

Commit the approved checkpoint first. From the repository root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-sandbox\prepare_smoke.ps1 `
  -DownloadPrerequisites `
  -Launch
```

The first preparation downloads pinned Python, Node.js, and Git installers into ignored `.artifacts` storage.
Project dependency installation occurs inside Sandbox and may download several gigabytes. No model is downloaded
or run.

Use `-AutoClose` only when automatic Sandbox shutdown after evidence capture is desired. Use `-MemoryInMB` to
change the default 8192 MB allocation, but do not set less than 4096 MB.

## Generated Package

Each run creates a timestamped directory under `.artifacts/windows-sandbox-smoke/`:

```text
<timestamp>-<commit>/
  ai-image-edit-smoke.wsb
  input/
    SOURCE_COMMIT.txt
    package-manifest.json
    source.zip
    bootstrap_smoke.ps1
    prerequisites/
  output/
```

The manifest records the full source commit, source ZIP hash, host-clean state, prerequisite versions, download
URLs, installer hashes, signer subjects, evidence class, and model authorization state.

## Returned Evidence

The writable `output/` directory receives:

- `sandbox-smoke.log`: full installation and validation transcript
- `sandbox-smoke-result.json`: structured result and failure phase
- `sandbox-smoke-result.txt`: operator result block ready for the canonical result log

Pass requires all four checks:

- backend fast-check startup smoke
- frontend lint
- frontend typecheck
- frontend production build

If setup or a check fails, the result remains `blocked`; do not convert it to a pass manually. Record the failure
phase and blocker in `docs/testing/target-clean-machine-smoke-result-log.md`.

## Validation Without Launch

Run the cheap local contract test without downloading or launching:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-sandbox\test_harness_contract.ps1
```

After the harness is committed, validate the committed source contract and Sandbox availability:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-sandbox\prepare_smoke.ps1 -ValidateOnly
```

This verifies the Sandbox executable, clean host state, source commit, required committed paths, and manifest
schema. It is not smoke evidence.
