param(
  [switch]$SkipBackend,
  [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"

if (-not $SkipBackend) {
  Write-Host "== Backend fast-check startup smoke =="
  & (Join-Path $PSScriptRoot "smoke_backend.ps1")
}

if (-not $SkipFrontend) {
  if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) {
    throw "Frontend package.json not found at $frontendRoot"
  }

  Push-Location $frontendRoot
  try {
    Write-Host "== Frontend lint =="
    npm.cmd run lint
    Write-Host "== Frontend typecheck =="
    npm.cmd run typecheck
    Write-Host "== Frontend build =="
    npm.cmd run build
  }
  finally {
    Pop-Location
  }
}

Write-Host "Release smoke checks completed."
