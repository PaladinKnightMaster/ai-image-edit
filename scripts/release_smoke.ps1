param(
  [switch]$SkipBackend,
  [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"

function Invoke-NpmCheck {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [string]$Script
  )

  Write-Host "== $Name =="
  npm.cmd run $Script
  if ($LASTEXITCODE -ne 0) {
    throw "$Name failed with exit code $LASTEXITCODE."
  }
}

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
    Invoke-NpmCheck -Name "Frontend lint" -Script "lint"
    Invoke-NpmCheck -Name "Frontend typecheck" -Script "typecheck"
    Invoke-NpmCheck -Name "Frontend build" -Script "build"
  }
  finally {
    Pop-Location
  }
}

Write-Host "Release smoke checks completed."
