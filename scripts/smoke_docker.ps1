param(
  [string]$ImageTag = "ai-image-edit:wr5-002-smoke",
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$containerName = "ai-image-edit-wr5-002-smoke"

function Invoke-NativeChecked {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [Parameter(Mandatory = $true)][string[]]$Arguments,
    [Parameter(Mandatory = $true)][string]$Label
  )
  Write-Host "== $Label =="
  & $FilePath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE."
  }
}

Push-Location $repoRoot
try {
  if (-not $SkipBuild) {
    Invoke-NativeChecked -FilePath "docker" -Arguments @(
      "build", "-t", $ImageTag, "-f", "Dockerfile", "."
    ) -Label "Docker build (non-model)"
  }

  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    docker rm -f $containerName 2>$null | Out-Null
  }
  finally {
    $ErrorActionPreference = $prevEap
  }

  Invoke-NativeChecked -FilePath "docker" -Arguments @(
    "run", "-d",
    "--name", $containerName,
    "-p", "18000:8000",
    "-e", "WARMUP_MODELS=0",
    "-e", "DOTENV_PATH=/app/backend/.env.fast-check",
    $ImageTag
  ) -Label "Docker run API container"

  $deadline = (Get-Date).AddSeconds(90)
  $healthy = $false
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri "http://127.0.0.1:18000/health" -UseBasicParsing -TimeoutSec 5
      if ($response.StatusCode -eq 200) {
        $healthy = $true
        break
      }
    }
    catch {
      Start-Sleep -Seconds 2
    }
  }

  if (-not $healthy) {
    docker logs $containerName
    throw "Docker smoke timed out waiting for /health on port 18000."
  }

  Write-Host "== In-container startup unittest =="
  docker exec $containerName python -m unittest discover -s tests -p "test_startup_smoke.py"
  if ($LASTEXITCODE -ne 0) {
    docker logs $containerName
    throw "In-container startup smoke failed with exit code $LASTEXITCODE."
  }

  Write-Host "Docker non-model smoke passed (image=$ImageTag)."
}
finally {
  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    docker rm -f $containerName 2>$null | Out-Null
  }
  finally {
    $ErrorActionPreference = $prevEap
  }
  Pop-Location
}
