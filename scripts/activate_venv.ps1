param(
  [string]$VenvPath = ".\\.venv"
)

$ErrorActionPreference = "Stop"

if ($MyInvocation.InvocationName -ne ".") {
  Write-Warning "Dot-source this script to persist activation: . $PSCommandPath"
}

if (-not (Test-Path $VenvPath)) {
  throw "Virtualenv not found at $VenvPath. Run: python -m venv .venv"
}

$activate = Join-Path $VenvPath "Scripts\\Activate.ps1"
if (-not (Test-Path $activate)) {
  throw "Activate.ps1 not found at $activate. Ensure the venv was created on Windows."
}

. $activate
Write-Host "Activated $VenvPath"
