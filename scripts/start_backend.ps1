param(
  [ValidateSet("main", "fast-check")]
  [string]$Mode = "main",
  [int]$Port = 8000,
  [switch]$NoReload
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"

function Resolve-PythonPath {
  $candidates = @(
    (Join-Path $backendRoot ".venv\Scripts\python.exe"),
    (Join-Path $repoRoot ".venv\Scripts\python.exe")
  )

  foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
      return $candidate
    }
  }

  throw "No Windows venv Python found. Expected one of: $($candidates -join ', ')"
}

$python = Resolve-PythonPath
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
  & $python -m uvicorn app.main:app @reloadArgs --host 0.0.0.0 --port $Port
}
finally {
  Pop-Location
}
