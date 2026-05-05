param(
  [ValidateSet("headshot-cleanup", "studio-relight", "background-simplify", "multi-angle-portrait")]
  [string[]]$PresetRun = @("headshot-cleanup"),
  [switch]$ListTargets,
  [switch]$RunApproved,
  [int]$MaxWaitSec = 1800,
  [int]$PollIntervalSec = 5,
  [string]$SummaryPath = ".\\data\\benchmark-review-summary.json"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$scriptPath = Join-Path $PSScriptRoot "run_edit_benchmark_case.py"

. (Join-Path $PSScriptRoot "python_runtime.ps1")

function Update-SummaryArtifact {
  param(
    [string]$Path,
    [scriptblock]$Mutator
  )

  if (-not (Test-Path $Path)) {
    return
  }

  $raw = Get-Content -Path $Path -Raw -ErrorAction Stop
  if ([string]::IsNullOrWhiteSpace($raw)) {
    return
  }

  $summary = $raw | ConvertFrom-Json
  & $Mutator $summary
  $updated = $summary | ConvertTo-Json -Depth 12
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $updated, $utf8NoBom)
}

function Get-ProcessExitMetadata {
  param(
    [int]$ExitCode
  )

  $unsigned = [uint32]([int64]$ExitCode -band 0xFFFFFFFFL)
  $hexCode = ('0x{0:X8}' -f $unsigned)
  $meaning = switch ($unsigned) {
    0xC0000005 { "access_violation" }
    0xC0000409 { "stack_buffer_overrun" }
    0xC0000017 { "no_memory" }
    default { $null }
  }

  return [pscustomobject]@{
    HexCode = $hexCode
    Meaning = $meaning
  }
}

$targets = @{
  "headshot-cleanup" = [ordered]@{
    preset_id = "headshot-cleanup"
    case_id = "edit-001-headshot-cleanup"
    model_id = "qwen-image-edit-2511"
    base_fixture = "fixtures/private/benchmark-pack-v0/portrait-base-01-studio-headshot.png"
    prompt = "Clean up this headshot while preserving identity. Reduce stray hairs and temporary blemishes, even skin tone gently, keep pores and natural texture, maintain crisp eyes and hair detail, and keep the result realistic and believable."
    seed = 2101
    steps = 12
    guidance_scale = 4.2
    true_cfg_scale = 1.2
  }
  "studio-relight" = [ordered]@{
    preset_id = "studio-relight"
    case_id = "edit-002-studio-relight"
    model_id = "qwen-image-edit-2511"
    base_fixture = "fixtures/private/benchmark-pack-v0/portrait-base-02-window-light-three-quarter.png"
    prompt = "Relight this portrait as if it were captured in a controlled studio setup. Keep identity unchanged, lift the subject slightly from the background, balance highlights and shadows, add clean directional light, and keep skin tone natural and realistic."
    seed = 2102
    steps = 12
    guidance_scale = 4.6
    true_cfg_scale = 1.25
  }
  "background-simplify" = [ordered]@{
    preset_id = "background-simplify"
    case_id = "edit-003-background-simplify"
    model_id = "qwen-image-edit-2511"
    base_fixture = "fixtures/private/benchmark-pack-v0/portrait-base-03-outdoor-city-walkup.png"
    prompt = "Simplify the background around the portrait while preserving the subject exactly. Reduce distractions, keep edges clean around hair and shoulders, maintain natural depth, and make the portrait feel cleaner and more focused without looking cut out."
    seed = 2103
    steps = 12
    guidance_scale = 4.3
    true_cfg_scale = 1.2
  }
  "multi-angle-portrait" = [ordered]@{
    preset_id = "multi-angle-portrait"
    case_id = "ref-003-pose-and-crop-guidance"
    model_id = "qwen-image-edit-2511"
    base_fixture = "fixtures/private/benchmark-pack-v0/portrait-base-03-outdoor-city-walkup.png"
    reference_fixture = "fixtures/private/benchmark-pack-v0/reference-pose-03-three-quarter.png"
    prompt = "Use the base portrait as the primary identity source and keep the face consistent while refining the image toward a cohesive portrait look. Preserve facial structure, skin realism, and hair detail, and keep lighting and styling coherent across the final result."
    seed = 3103
    steps = 14
    guidance_scale = 4.5
    true_cfg_scale = 1.25
  }
}

if ($ListTargets) {
  Write-Host "Available preset review targets:"
  foreach ($name in $targets.Keys) {
    $target = $targets[$name]
    $caseId = $target.case_id
    Write-Host "  $name -> $caseId"
  }
  exit 0
}

$selectedTargets = @()
foreach ($name in $PresetRun) {
  if (-not $targets.ContainsKey($name)) {
    throw "Unknown preset review target '$name'. Use -ListTargets to inspect supported targets."
  }
  $selectedTargets += [ordered]@{} + $targets[$name]
}

$summaryPathResolved = if ([System.IO.Path]::IsPathRooted($SummaryPath)) {
  $SummaryPath
} else {
  Join-Path $repoRoot $SummaryPath
}

if (-not $RunApproved) {
  Write-Host "Model run approval required."
  Write-Host "This command can load qwen-image-edit-2511 and hold substantial CPU and memory for an extended time."
  Write-Host "Selected targets:"
  foreach ($target in $selectedTargets) {
    $reference = if ($target.Contains("reference_fixture")) { " + reference" } else { "" }
    Write-Host "  - $($target.preset_id) ($($target.case_id))$reference"
  }
  Write-Host "No model execution started."
  Write-Host "Re-run with -RunApproved only after the user explicitly approves the model run."
  exit 0
}

foreach ($target in $selectedTargets) {
  $baseFixture = Join-Path $repoRoot $target.base_fixture
  if (-not (Test-Path $baseFixture)) {
    throw "Base fixture not found: $baseFixture"
  }
  if ($target.Contains("reference_fixture")) {
    $referenceFixture = Join-Path $repoRoot $target.reference_fixture
    if (-not (Test-Path $referenceFixture)) {
      throw "Reference fixture not found: $referenceFixture"
    }
  }
}

$planPath = Join-Path ([System.IO.Path]::GetTempPath()) ("edit-review-plan-" + [guid]::NewGuid().ToString() + ".json")
$planPayload = @{
  targets = $selectedTargets
} | ConvertTo-Json -Depth 8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($planPath, $planPayload, $utf8NoBom)

$previousPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = $backendRoot

try {
  Write-Host "Resolving Python runtime for benchmark review..."
  $python = Resolve-PythonSpec -RepoRoot $repoRoot -BackendRoot $backendRoot -RequiredImports @(
    "fastapi",
    "dotenv",
    "diffusers",
    "PIL",
    "torch"
  )
  Write-Host "Resolved Python runtime source: $($python.Source)"
  Write-Host "Running approval-gated edit benchmark review using $($python.Executable)"
  Write-Host "Summary path: $summaryPathResolved"
  Write-Host "Launching benchmark harness..."
  Invoke-WithPythonSitePackages -SitePackages $python.SitePackages -ScriptBlock {
    & $python.Executable $scriptPath `
      --repo-root $repoRoot `
      --plan-path $planPath `
      --summary-path $summaryPathResolved `
      --max-wait-seconds $MaxWaitSec `
      --poll-seconds $PollIntervalSec
  }
  $pythonExitCode = $LASTEXITCODE
  $exitMeta = Get-ProcessExitMetadata -ExitCode $pythonExitCode
  Update-SummaryArtifact -Path $summaryPathResolved -Mutator {
    param($summary)
    $summary | Add-Member -NotePropertyName wrapper_exit_code -NotePropertyValue $pythonExitCode -Force
    $summary | Add-Member -NotePropertyName wrapper_exit_hex -NotePropertyValue $exitMeta.HexCode -Force
    if ($exitMeta.Meaning) {
      $summary | Add-Member -NotePropertyName wrapper_exit_meaning -NotePropertyValue $exitMeta.Meaning -Force
    }
    $summary | Add-Member -NotePropertyName wrapper_finished_at -NotePropertyValue ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) -Force
    if ($pythonExitCode -ne 0 -and $summary.runner_status -eq "running") {
      $summary.runner_status = "process_exit"
      $hasFatalError = $null -ne $summary.PSObject.Properties["fatal_error"]
      if (-not $hasFatalError) {
        $summary | Add-Member -NotePropertyName fatal_error -NotePropertyValue "runner exited before writing a terminal status" -Force
      }
      elseif ([string]::IsNullOrWhiteSpace([string]$summary.fatal_error)) {
        $summary.fatal_error = "runner exited before writing a terminal status"
      }
    }
  }
  exit $pythonExitCode
}
finally {
  if ($null -eq $previousPythonPath) {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
  }
  else {
    $env:PYTHONPATH = $previousPythonPath
  }
  Remove-Item $planPath -ErrorAction SilentlyContinue
}
