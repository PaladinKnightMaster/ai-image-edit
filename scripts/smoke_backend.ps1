$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
. (Join-Path $PSScriptRoot "python_runtime.ps1")

$python = Resolve-PythonSpec -RepoRoot $repoRoot -BackendRoot $backendRoot -RequiredImports @(
  "dotenv",
  "fastapi"
)
$dotenvPath = Join-Path $backendRoot ".env.fast-check"

if (-not (Test-Path $dotenvPath)) {
  throw "Env file not found at $dotenvPath"
}

Write-Host "Running backend startup smoke mode=fast-check dotenv=$dotenvPath executable=$($python.Executable) source=$($python.Source)"

Push-Location $backendRoot
try {
  $env:DOTENV_PATH = $dotenvPath
  Invoke-WithPythonSitePackages -SitePackages $python.SitePackages -ScriptBlock {
    & $python.Executable -m unittest discover -s tests -p "test_startup_smoke.py"
    if ($LASTEXITCODE -ne 0) {
      throw "Backend fast-check startup smoke failed with exit code $LASTEXITCODE."
    }
  }
}
finally {
  Pop-Location
}
