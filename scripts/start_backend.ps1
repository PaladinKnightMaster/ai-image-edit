param(
  [ValidateSet("main", "fast-check")]
  [string]$Mode = "main",
  [int]$Port = 8000,
  [switch]$NoReload
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
. (Join-Path $PSScriptRoot "python_runtime.ps1")

$python = Resolve-PythonSpec -RepoRoot $repoRoot -BackendRoot $backendRoot -RequiredImports @(
  "dotenv",
  "fastapi",
  "uvicorn"
)
$dotenvPath = if ($Mode -eq "fast-check") {
  Join-Path $backendRoot ".env.fast-check"
} else {
  Join-Path $backendRoot ".env"
}

if (-not (Test-Path $dotenvPath)) {
  throw "Env file not found at $dotenvPath"
}

$reloadArgs = @()
if (-not $NoReload) {
  $reloadArgs += "--reload"
}

Write-Host "Starting backend mode=$Mode dotenv=$dotenvPath python=$python port=$Port"

Push-Location $backendRoot
try {
  $env:DOTENV_PATH = $dotenvPath
  Write-Host "Resolved runtime source=$($python.Source) executable=$($python.Executable)"
  Invoke-WithPythonSitePackages -SitePackages $python.SitePackages -ScriptBlock {
    & $python.Executable -m uvicorn app.main:app @reloadArgs --host 0.0.0.0 --port $Port
  }
}
finally {
  Pop-Location
}
