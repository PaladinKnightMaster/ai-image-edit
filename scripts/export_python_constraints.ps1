param(
  [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$constraintsPath = Join-Path $backendRoot "constraints.txt"

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
  $candidate = Join-Path $repoRoot ".venv\Scripts\python.exe"
  if (Test-Path $candidate) {
    $PythonExe = $candidate
  }
  else {
    $PythonExe = (Get-Command python -ErrorAction Stop).Source
  }
}

$direct = @(
  "accelerate",
  "annotated-doc",
  "annotated-types",
  "anyio",
  "certifi",
  "charset-normalizer",
  "click",
  "colorama",
  "fastapi",
  "filelock",
  "fsspec",
  "h11",
  "httpcore",
  "httptools",
  "httpx",
  "huggingface-hub",
  "idna",
  "importlib_metadata",
  "Jinja2",
  "MarkupSafe",
  "mpmath",
  "networkx",
  "numpy",
  "packaging",
  "pillow",
  "psutil",
  "pydantic",
  "pydantic_core",
  "python-dotenv",
  "python-multipart",
  "PyYAML",
  "regex",
  "requests",
  "ruff",
  "safetensors",
  "setuptools",
  "starlette",
  "sympy",
  "tokenizers",
  "torch",
  "torchvision",
  "tqdm",
  "transformers",
  "typing-inspection",
  "typing_extensions",
  "urllib3",
  "uvicorn",
  "watchfiles",
  "websockets",
  "zipp"
)

$script = @"
import importlib.metadata as m
pkgs = $(ConvertTo-Json $direct -Compress)
lines = []
for name in pkgs:
    try:
        version = m.version(name)
    except Exception:
        alt = name.replace('_', '-')
        version = m.version(alt)
    # Prefer the distribution's reported name for hyphenated packages.
    try:
        dist_name = m.distribution(name).metadata['Name']
    except Exception:
        dist_name = name
    lines.append(f'{dist_name}=={version}')
print('\n'.join(sorted(lines, key=str.lower)))
"@

$header = @"
# Reviewed transitive pin set for backend/requirements.txt (CPU baseline).
# Regenerate after intentional upgrades with:
#   powershell -NoProfile -File .\scripts\export_python_constraints.ps1
#
# Diffusers is pinned by git SHA in requirements.txt (not listed here).
# Optional extras (OpenVINO, FLUX sd-cli bindings) are intentionally excluded.

"@

$body = & $PythonExe -c $script
if ($LASTEXITCODE -ne 0) {
  throw "Failed to export package versions from $PythonExe"
}

Set-Content -Path $constraintsPath -Value ($header + $body + "`n") -Encoding utf8
Write-Host "Wrote $constraintsPath"
