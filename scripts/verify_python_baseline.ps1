param(
  [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$requirements = Join-Path $backendRoot "requirements.txt"
$constraints = Join-Path $backendRoot "constraints.txt"
$expectedDiffusersSha = "d7a1c31f4f85bae5a9e01cdce49bd7346bd8ccd6"

if (-not (Test-Path $requirements)) {
  throw "Missing $requirements"
}
if (-not (Test-Path $constraints)) {
  throw "Missing $constraints"
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
  $candidate = Join-Path $repoRoot ".venv\Scripts\python.exe"
  if (Test-Path $candidate) {
    $PythonExe = $candidate
  }
  else {
    $PythonExe = (Get-Command python -ErrorAction Stop).Source
  }
}

$workRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("ai-image-edit-baseline-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $workRoot | Out-Null

function Get-ResolveFingerprint {
  param(
    [Parameter(Mandatory = $true)][string]$Label,
    [Parameter(Mandatory = $true)][string]$ReportPath
  )

  Write-Host "== Resolve $Label =="
  # Capture pip output so it does not leak into this function's return value.
  # pip writes progress to stderr; do not treat those records as terminating errors.
  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    $pipOutput = & $PythonExe -m pip install `
      --dry-run `
      --ignore-installed `
      --report $ReportPath `
      -c $constraints `
      -r $requirements `
      2>&1 | ForEach-Object { "$_" } | Out-String
  }
  finally {
    $ErrorActionPreference = $prevEap
  }
  Write-Host $pipOutput
  if ($LASTEXITCODE -ne 0) {
    throw "pip dry-run resolve failed for $Label"
  }

  $script = @"
import json
from pathlib import Path
report = json.loads(Path(r'$ReportPath').read_text(encoding='utf-8'))
items = []
for entry in report.get('install', []):
    meta = entry.get('metadata') or {}
    name = (meta.get('name') or '').lower().replace('_', '-')
    version = meta.get('version') or ''
    download = entry.get('download_info') or {}
    url = download.get('url') or ''
    vcs = ''
    vcs_info = download.get('vcs_info') or {}
    if vcs_info:
        vcs = vcs_info.get('commit_id') or ''
    items.append({
        'name': name,
        'version': version,
        'vcs': vcs,
        # Compare by archive name / VCS URL host path, not ephemeral query strings.
        'source': url.split('?')[0],
    })
items.sort(key=lambda row: (row['name'], row['version'], row['vcs'], row['source']))
print(json.dumps(items, separators=(',', ':')))
"@

  $fingerprint = (& $PythonExe -c $script 2>&1 | Out-String).Trim()
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to fingerprint resolve report for $Label : $fingerprint"
  }
  return ,$fingerprint
}

try {
  $reportA = Join-Path $workRoot "a.json"
  $reportB = Join-Path $workRoot "b.json"

  $baselineA = Get-ResolveFingerprint -Label "A" -ReportPath $reportA
  $baselineB = Get-ResolveFingerprint -Label "B" -ReportPath $reportB

  Write-Host "Baseline A packages: $((($baselineA | ConvertFrom-Json).Count))"
  Write-Host "Baseline B packages: $((($baselineB | ConvertFrom-Json).Count))"

  if ($baselineA -ne $baselineB) {
    throw "Two clean resolves produced different dependency baselines."
  }

  if ($baselineA -notmatch $expectedDiffusersSha) {
    throw "Diffusers git revision pin $expectedDiffusersSha missing from resolved baseline."
  }

  Write-Host "Two clean resolves matched the reviewed direct dependency baseline (Diffusers @$expectedDiffusersSha)."
}
finally {
  Remove-Item -Recurse -Force $workRoot -ErrorAction SilentlyContinue
}
