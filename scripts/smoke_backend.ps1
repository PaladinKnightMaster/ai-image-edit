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
$dotenvPath = Join-Path $backendRoot ".env.fast-check"

if (-not (Test-Path $dotenvPath)) {
  throw "Env file not found at $dotenvPath"
}

Write-Host "Running backend smoke mode=fast-check dotenv=$dotenvPath python=$python"

Push-Location $backendRoot
try {
  $env:DOTENV_PATH = $dotenvPath
  & $python -m unittest discover -s tests -p "test_startup_smoke.py"
}
finally {
  Pop-Location
}
