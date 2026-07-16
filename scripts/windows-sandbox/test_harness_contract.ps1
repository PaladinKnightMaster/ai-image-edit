$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptRoot = $PSScriptRoot
$failures = @()
$powerShellFiles = @(
  (Join-Path $scriptRoot "prepare_smoke.ps1"),
  (Join-Path $scriptRoot "bootstrap_smoke.ps1"),
  (Join-Path $scriptRoot "..\release_smoke.ps1"),
  (Join-Path $scriptRoot "..\smoke_backend.ps1")
)

foreach ($path in $powerShellFiles) {
  $tokens = $null
  $parseErrors = $null
  [System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path $path),
    [ref]$tokens,
    [ref]$parseErrors
  ) | Out-Null
  foreach ($parseError in $parseErrors) {
    $failures += "$path parse error: $($parseError.Message)"
  }
}

$configPath = Join-Path $scriptRoot "prerequisites.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
if ($config.schema_version -ne 1) {
  $failures += "Unsupported prerequisite schema $($config.schema_version)."
}

$allowedHosts = @("www.python.org", "nodejs.org", "github.com")
foreach ($prerequisite in $config.prerequisites) {
  $uri = [Uri]$prerequisite.url
  if ($uri.Scheme -ne "https") {
    $failures += "$($prerequisite.name) URL is not HTTPS."
  }
  if ($uri.Host -notin $allowedHosts) {
    $failures += "$($prerequisite.name) URL host $($uri.Host) is not approved."
  }
  if ($prerequisite.url -notmatch [regex]::Escape($prerequisite.version)) {
    $failures += "$($prerequisite.name) URL does not pin version $($prerequisite.version)."
  }
  if ($prerequisite.url -notmatch [regex]::Escape($prerequisite.file_name)) {
    $failures += "$($prerequisite.name) URL does not end in the configured file name."
  }
  if (-not $prerequisite.signature_required) {
    $failures += "$($prerequisite.name) does not require Authenticode validation."
  }
}

$prepareContent = Get-Content (Join-Path $scriptRoot "prepare_smoke.ps1") -Raw
$bootstrapContent = Get-Content (Join-Path $scriptRoot "bootstrap_smoke.ps1") -Raw
$releaseContent = Get-Content (Join-Path $scriptRoot "..\release_smoke.ps1") -Raw
$backendSmokeContent = Get-Content (Join-Path $scriptRoot "..\smoke_backend.ps1") -Raw

$requiredPreparePatterns = @(
  "git archive",
  "Get-AuthenticodeSignature",
  "source_archive_sha256",
  'model_execution_authorized = $false',
  "<ReadOnly>true</ReadOnly>",
  "<VGpu>Disable</VGpu>"
)
foreach ($pattern in $requiredPreparePatterns) {
  if ($prepareContent -notmatch [regex]::Escape($pattern)) {
    $failures += "prepare_smoke.ps1 is missing required contract text: $pattern"
  }
}

$requiredBootstrapPatterns = @(
  "Assert-Hash",
  "model_execution_authorized",
  "scripts\release_smoke.ps1",
  'model_executed = $false'
)
foreach ($pattern in $requiredBootstrapPatterns) {
  if ($bootstrapContent -notmatch [regex]::Escape($pattern)) {
    $failures += "bootstrap_smoke.ps1 is missing required contract text: $pattern"
  }
}

$forbiddenBootstrapPatterns = @(
  "run_edit_benchmark_case",
  "smoke_qwen",
  "fetch_flux",
  "mirror_models",
  "/api/jobs"
)
foreach ($pattern in $forbiddenBootstrapPatterns) {
  if ($bootstrapContent -match [regex]::Escape($pattern)) {
    $failures += "bootstrap_smoke.ps1 contains forbidden inference entry point: $pattern"
  }
}

if ($releaseContent -notmatch '\$LASTEXITCODE\s+-ne\s+0') {
  $failures += "release_smoke.ps1 does not enforce native exit codes."
}
if ($backendSmokeContent -notmatch '\$LASTEXITCODE\s+-ne\s+0') {
  $failures += "smoke_backend.ps1 does not enforce the Python exit code."
}

if ($failures.Count -gt 0) {
  $failures | ForEach-Object { Write-Error $_ }
  exit 1
}

Write-Host "Windows Sandbox harness contract checks passed."
Write-Host "PowerShell files parsed: $($powerShellFiles.Count)"
Write-Host "Pinned signed prerequisites: $($config.prerequisites.Count)"
Write-Host "Model execution entry points: none"
