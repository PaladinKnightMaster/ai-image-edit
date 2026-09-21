param(
  [string]$SourceRef = "HEAD",
  [string]$OutputRoot,
  [string]$PrerequisiteCache,
  [int]$MemoryInMB = 8192,
  [switch]$DownloadPrerequisites,
  [switch]$AllowDirtyHost,
  [switch]$Launch,
  [switch]$AutoClose,
  [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptRoot = $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..\..")).Path
if (-not $OutputRoot) {
  $OutputRoot = Join-Path $repoRoot ".artifacts\windows-sandbox-smoke"
}
if (-not $PrerequisiteCache) {
  $PrerequisiteCache = Join-Path $repoRoot ".artifacts\windows-sandbox-cache"
}

function Invoke-Git {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

  $stderrPath = [IO.Path]::GetTempFileName()
  $previousErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $output = @(& git @Arguments 2> $stderrPath)
    $exitCode = $LASTEXITCODE
    $stderr = @(Get-Content -LiteralPath $stderrPath -ErrorAction SilentlyContinue)
  }
  finally {
    $ErrorActionPreference = $previousErrorActionPreference
    Remove-Item -LiteralPath $stderrPath -Force -ErrorAction SilentlyContinue
  }

  if ($exitCode -ne 0) {
    throw "git $($Arguments -join ' ') failed: $($stderr -join [Environment]::NewLine)"
  }
  foreach ($line in $stderr) {
    Write-Verbose "git: $line"
  }
  return $output
}

function Assert-AuthenticodeSignature {
  param([string]$Path)

  $signature = Get-AuthenticodeSignature -FilePath $Path
  if ($signature.Status -ne "Valid") {
    throw "Authenticode validation failed for $Path with status $($signature.Status)."
  }
  return $signature.SignerCertificate.Subject
}

function Get-OrDownloadPrerequisite {
  param(
    [pscustomobject]$Definition,
    [string]$CacheRoot,
    [bool]$MayDownload
  )

  $path = Join-Path $CacheRoot $Definition.file_name
  if (-not (Test-Path $path)) {
    if (-not $MayDownload) {
      throw "Missing prerequisite $($Definition.file_name). Rerun with -DownloadPrerequisites."
    }

    New-Item -ItemType Directory -Force -Path $CacheRoot | Out-Null
    $partialPath = "$path.partial"
    Write-Host "Downloading $($Definition.name) $($Definition.version) from $($Definition.url)"
    Invoke-WebRequest -UseBasicParsing -Uri $Definition.url -OutFile $partialPath
    Move-Item -LiteralPath $partialPath -Destination $path -Force
  }

  $signer = $null
  if ($Definition.signature_required) {
    $signer = Assert-AuthenticodeSignature -Path $path
  }

  return [pscustomobject]@{
    name = $Definition.name
    version = $Definition.version
    file_name = $Definition.file_name
    install_type = $Definition.install_type
    source_url = $Definition.url
    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    signer = $signer
    cache_path = $path
  }
}

if ($MemoryInMB -lt 4096) {
  throw "MemoryInMB must be at least 4096."
}

$null = Get-Command git -ErrorAction Stop
$sandboxCommand = Get-Command WindowsSandbox.exe -ErrorAction Stop
$sourceCommit = (Invoke-Git rev-parse "$SourceRef^{commit}" | Select-Object -First 1).Trim()
$sourceCommitShort = (Invoke-Git rev-parse --short $sourceCommit | Select-Object -First 1).Trim()
$hostStatus = @(Invoke-Git -Arguments @("status", "--porcelain"))
$hostIsClean = $hostStatus.Count -eq 0

if (-not $hostIsClean -and -not $AllowDirtyHost) {
  throw "The host worktree is dirty. Commit the checkpoint or rerun with -AllowDirtyHost; the source archive always comes from SourceRef."
}

$requiredSourcePaths = @(
  "scripts/release_smoke.ps1",
  "scripts/windows-sandbox/bootstrap_smoke.ps1",
  "scripts/windows-sandbox/prerequisites.json"
)
foreach ($path in $requiredSourcePaths) {
  $null = Invoke-Git -Arguments @("cat-file", "-e", "${sourceCommit}:$path")
}

$definitionsJson = (Invoke-Git show "${sourceCommit}:scripts/windows-sandbox/prerequisites.json") -join "`n"
$definitions = $definitionsJson | ConvertFrom-Json
if ($definitions.schema_version -ne 1) {
  throw "Unsupported prerequisite manifest schema $($definitions.schema_version)."
}

if ($ValidateOnly) {
  Write-Host "Windows Sandbox harness validation passed for commit $sourceCommitShort."
  Write-Host "Windows Sandbox executable: $($sandboxCommand.Source)"
  Write-Host "Host worktree clean: $hostIsClean"
  return
}

$resolvedOutputRoot = [IO.Path]::GetFullPath($OutputRoot)
$resolvedCacheRoot = [IO.Path]::GetFullPath($PrerequisiteCache)
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$runRoot = Join-Path $resolvedOutputRoot "$timestamp-$sourceCommitShort"
$inputRoot = Join-Path $runRoot "input"
$sandboxOutputRoot = Join-Path $runRoot "output"
$prerequisiteInputRoot = Join-Path $inputRoot "prerequisites"
New-Item -ItemType Directory -Force -Path $prerequisiteInputRoot, $sandboxOutputRoot | Out-Null

$sourceZip = Join-Path $inputRoot "source.zip"
$null = Invoke-Git archive --format=zip --output=$sourceZip $sourceCommit
$sourceSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceZip).Hash.ToLowerInvariant()

$extractRoot = Join-Path $runRoot "contract-extract"
Expand-Archive -LiteralPath $sourceZip -DestinationPath $extractRoot
try {
  Copy-Item -LiteralPath (Join-Path $extractRoot "scripts\windows-sandbox\bootstrap_smoke.ps1") -Destination (Join-Path $inputRoot "bootstrap_smoke.ps1")
  Copy-Item -LiteralPath (Join-Path $extractRoot "scripts\windows-sandbox\prerequisites.json") -Destination (Join-Path $inputRoot "prerequisites.json")
}
finally {
  Remove-Item -LiteralPath $extractRoot -Recurse -Force
}

$preparedPrerequisites = @()
foreach ($definition in $definitions.prerequisites) {
  $prepared = Get-OrDownloadPrerequisite -Definition $definition -CacheRoot $resolvedCacheRoot -MayDownload $DownloadPrerequisites.IsPresent
  Copy-Item -LiteralPath $prepared.cache_path -Destination (Join-Path $prerequisiteInputRoot $prepared.file_name)
  $preparedPrerequisites += [ordered]@{
    name = $prepared.name
    version = $prepared.version
    file_name = $prepared.file_name
    install_type = $prepared.install_type
    source_url = $prepared.source_url
    sha256 = $prepared.sha256
    signer = $prepared.signer
  }
}

$manifest = [ordered]@{
  schema_version = 1
  evidence_class = "Windows Sandbox surrogate"
  generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  source_ref = $SourceRef
  source_commit = $sourceCommit
  source_commit_short = $sourceCommitShort
  source_archive = "source.zip"
  source_archive_sha256 = $sourceSha256
  host_worktree_clean = $hostIsClean
  model_execution_authorized = $false
  prerequisites = $preparedPrerequisites
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $inputRoot "package-manifest.json")
Set-Content -Encoding ASCII -Path (Join-Path $inputRoot "SOURCE_COMMIT.txt") -Value $sourceCommit

$escapedInputRoot = [Security.SecurityElement]::Escape($inputRoot)
$escapedOutputRoot = [Security.SecurityElement]::Escape($sandboxOutputRoot)
$autoCloseArgument = if ($AutoClose) { " -AutoClose" } else { "" }
$wsbContent = @"
<Configuration>
  <VGpu>Disable</VGpu>
  <Networking>Enable</Networking>
  <AudioInput>Disable</AudioInput>
  <VideoInput>Disable</VideoInput>
  <PrinterRedirection>Disable</PrinterRedirection>
  <ClipboardRedirection>Disable</ClipboardRedirection>
  <MemoryInMB>$MemoryInMB</MemoryInMB>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>$escapedInputRoot</HostFolder>
      <SandboxFolder>C:\AIImageEditInput</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <MappedFolder>
      <HostFolder>$escapedOutputRoot</HostFolder>
      <SandboxFolder>C:\AIImageEditOutput</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\AIImageEditInput\bootstrap_smoke.ps1$autoCloseArgument</Command>
  </LogonCommand>
</Configuration>
"@
$wsbPath = Join-Path $runRoot "ai-image-edit-smoke.wsb"
$wsbContent | Set-Content -Encoding UTF8 $wsbPath

Write-Host "Prepared Windows Sandbox smoke package."
Write-Host "Source commit: $sourceCommit"
Write-Host "WSB: $wsbPath"
Write-Host "Evidence output: $sandboxOutputRoot"
Write-Host "Model execution authorized: false"

if ($Launch) {
  Write-Host "Launching Windows Sandbox. Dependency installation and non-model build checks may take a long time."
  Start-Process -FilePath $sandboxCommand.Source -ArgumentList "`"$wsbPath`""
}
