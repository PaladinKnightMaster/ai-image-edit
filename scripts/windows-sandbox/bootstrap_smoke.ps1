param(
  [string]$InputRoot = "C:\AIImageEditInput",
  [string]$OutputRoot = "C:\AIImageEditOutput",
  [switch]$AutoClose
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$workRoot = "C:\AIImageEdit"
$sourceRoot = Join-Path $workRoot "source"
$pythonRoot = Join-Path $workRoot "Python312"
$transcriptPath = Join-Path $OutputRoot "sandbox-smoke.log"
$resultJsonPath = Join-Path $OutputRoot "sandbox-smoke-result.json"
$resultBlockPath = Join-Path $OutputRoot "sandbox-smoke-result.txt"
$result = [ordered]@{
  schema_version = 1
  evidence_class = "Windows Sandbox surrogate"
  status = "running"
  phase = "initializing"
  started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  completed_at_utc = $null
  source_commit = $null
  source_commit_short = $null
  python_version = $null
  node_version = $null
  npm_version = $null
  git_version = $null
  backend_fast_check = "not_run"
  frontend_lint = "not_run"
  frontend_typecheck = "not_run"
  frontend_build = "not_run"
  warnings = @()
  blocker = $null
  model_executed = $false
}
$transcriptStarted = $false
$exitCode = 1

function Save-Result {
  $result.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  $result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $resultJsonPath

  $checksPassed = $result.status -eq "passed"
  @"
Isolated clean-Windows smoke result
Date: $($result.completed_at_utc)
Evidence class: $($result.evidence_class)
Machine/environment: Windows Sandbox
Repo path: $sourceRoot
Commit: $($result.source_commit)
Primary command result: $($result.status)
Python override used: yes
Backend fast-check smoke: $(if ($checksPassed) { 'pass' } else { $result.backend_fast_check })
Frontend lint: $(if ($checksPassed) { 'pass' } else { $result.frontend_lint })
Frontend typecheck: $(if ($checksPassed) { 'pass' } else { $result.frontend_typecheck })
Frontend build: $(if ($checksPassed) { 'pass' } else { $result.frontend_build })
Warnings: $($result.warnings -join '; ')
Blockers: $($result.blocker)
Owner assignment if blocked: DevOps + Tech Lead
Terminal summary: $transcriptPath
Model executed: no
"@ | Set-Content -Encoding UTF8 $resultBlockPath
}

function Invoke-NativeChecked {
  param(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$Label
  )

  & $FilePath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE."
  }
}

function Invoke-Installer {
  param(
    [string]$FilePath,
    [string]$ArgumentList,
    [string]$Label
  )

  $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -Wait -PassThru
  if ($process.ExitCode -ne 0) {
    throw "$Label failed with exit code $($process.ExitCode)."
  }
}

function Assert-Hash {
  param(
    [string]$Path,
    [string]$Expected,
    [string]$Label
  )

  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
  if ($actual -ne $Expected.ToLowerInvariant()) {
    throw "$Label hash mismatch. Expected $Expected, got $actual."
  }
}

New-Item -ItemType Directory -Force -Path $OutputRoot, $workRoot | Out-Null

try {
  Start-Transcript -Path $transcriptPath -Force | Out-Null
  $transcriptStarted = $true
  Write-Host "AI Image Edit Windows Sandbox non-model smoke"
  Write-Host "Model execution authorized: false"

  $result.phase = "verifying-package"
  $manifestPath = Join-Path $InputRoot "package-manifest.json"
  $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
  if ($manifest.schema_version -ne 1) {
    throw "Unsupported package manifest schema $($manifest.schema_version)."
  }
  if ($manifest.model_execution_authorized) {
    throw "Package manifest unexpectedly authorizes model execution."
  }

  $result.source_commit = $manifest.source_commit
  $result.source_commit_short = $manifest.source_commit_short
  $sourceZip = Join-Path $InputRoot $manifest.source_archive
  Assert-Hash -Path $sourceZip -Expected $manifest.source_archive_sha256 -Label "Source archive"
  foreach ($prerequisite in $manifest.prerequisites) {
    $path = Join-Path (Join-Path $InputRoot "prerequisites") $prerequisite.file_name
    Assert-Hash -Path $path -Expected $prerequisite.sha256 -Label $prerequisite.name
  }

  $result.phase = "extracting-source"
  Expand-Archive -LiteralPath $sourceZip -DestinationPath $sourceRoot
  Set-Content -Encoding ASCII -Path (Join-Path $sourceRoot "SOURCE_COMMIT.txt") -Value $manifest.source_commit

  $result.phase = "installing-prerequisites"
  foreach ($prerequisite in $manifest.prerequisites) {
    $installer = Join-Path (Join-Path $InputRoot "prerequisites") $prerequisite.file_name
    switch ($prerequisite.install_type) {
      "python-exe" {
        Invoke-Installer -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 Include_launcher=0 Include_test=0 Include_pip=1 PrependPath=0 TargetDir=`"$pythonRoot`"" -Label "Python install"
      }
      "node-msi" {
        Invoke-Installer -FilePath "msiexec.exe" -ArgumentList "/i `"$installer`" /qn /norestart" -Label "Node.js install"
      }
      "git-exe" {
        Invoke-Installer -FilePath $installer -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP-" -Label "Git install"
      }
      default {
        throw "Unsupported installer type $($prerequisite.install_type)."
      }
    }
  }

  $python = Join-Path $pythonRoot "python.exe"
  $nodeRoot = "C:\Program Files\nodejs"
  $gitRoot = "C:\Program Files\Git\cmd"
  $env:Path = "$pythonRoot;$pythonRoot\Scripts;$nodeRoot;$gitRoot;$env:Path"
  $node = Join-Path $nodeRoot "node.exe"
  $npm = Join-Path $nodeRoot "npm.cmd"
  $git = Join-Path $gitRoot "git.exe"

  foreach ($requiredPath in @($python, $node, $npm, $git)) {
    if (-not (Test-Path $requiredPath)) {
      throw "Installed prerequisite was not found at $requiredPath."
    }
  }

  $result.python_version = (& $python --version 2>&1 | Out-String).Trim()
  $result.node_version = (& $node --version 2>&1 | Out-String).Trim()
  $result.npm_version = (& $npm --version 2>&1 | Out-String).Trim()
  $result.git_version = (& $git --version 2>&1 | Out-String).Trim()

  $result.phase = "installing-backend-dependencies"
  $venvRoot = Join-Path $sourceRoot ".venv"
  Invoke-NativeChecked -FilePath $python -Arguments @("-m", "venv", $venvRoot) -Label "Virtual environment creation"
  $venvPython = Join-Path $venvRoot "Scripts\python.exe"
  Invoke-NativeChecked -FilePath $venvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip") -Label "pip upgrade"
  Invoke-NativeChecked -FilePath $venvPython -Arguments @("-m", "pip", "install", "-c", (Join-Path $sourceRoot "backend\constraints.txt"), "-r", (Join-Path $sourceRoot "backend\requirements.txt")) -Label "Backend dependency install"

  $result.phase = "installing-frontend-dependencies"
  $frontendRoot = Join-Path $sourceRoot "frontend"
  Push-Location $frontendRoot
  try {
    Invoke-NativeChecked -FilePath $npm -Arguments @("ci", "--no-audit", "--no-fund") -Label "Frontend dependency install"
    Copy-Item -LiteralPath (Join-Path $frontendRoot ".env.example") -Destination (Join-Path $frontendRoot ".env.local") -Force
  }
  finally {
    Pop-Location
  }

  $result.phase = "running-release-smoke"
  $env:AI_IMAGE_EDIT_PYTHON = $venvPython
  $env:AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES = Join-Path $venvRoot "Lib\site-packages"
  & (Join-Path $sourceRoot "scripts\release_smoke.ps1")

  $result.backend_fast_check = "pass"
  $result.frontend_lint = "pass"
  $result.frontend_typecheck = "pass"
  $result.frontend_build = "pass"
  $result.phase = "complete"
  $result.status = "passed"
  $exitCode = 0
}
catch {
  $result.status = "blocked"
  $result.blocker = $_.Exception.Message
  Write-Host "BLOCKED: $($result.blocker)" -ForegroundColor Red
}
finally {
  try {
    Save-Result
  }
  catch {
    Write-Warning "Failed to save result evidence: $($_.Exception.Message)"
  }
  if ($transcriptStarted) {
    Stop-Transcript | Out-Null
  }
  if ($AutoClose) {
    Start-Process -FilePath "shutdown.exe" -ArgumentList "/s /t 15 /c `"AI Image Edit smoke complete; evidence returned to host.`""
  }
}

exit $exitCode
