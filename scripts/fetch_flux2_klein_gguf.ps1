param(
  [string]$OutputDir = ".\\models\\flux2_klein_9b_gguf",
  [string]$Quant = "Q4_K_M",
  [ValidateSet("fp4", "fp8")][string]$TextEncoder = "fp4",
  [string]$LlmFile = "Qwen3-8B-Q6_K.gguf",
  [string]$Token = "",
  [switch]$SkipLlm,
  [switch]$CleanCache
)

$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  throw "python not found. Install Python 3.10+ and retry."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$helper = Join-Path $scriptDir "fetch_flux2_klein_assets.py"

$envPrecision = $env:FLUX2_TEXT_ENCODER_PRECISION
if (-not $PSBoundParameters.ContainsKey("TextEncoder") -and $envPrecision) {
  if ($envPrecision -in @("fp4", "fp8")) {
    $TextEncoder = $envPrecision
  }
}
$envLlmFile = $env:FLUX2_LLM_FILE
if (-not $PSBoundParameters.ContainsKey("LlmFile") -and $envLlmFile) {
  $LlmFile = $envLlmFile
}

$argsList = @(
  $helper,
  "--output-dir", $OutputDir,
  "--quant", $Quant,
  "--text-encoder", $TextEncoder,
  "--llm-file", $LlmFile
)
if ($Token) {
  $argsList += @("--token", $Token)
}
if ($SkipLlm) {
  $argsList += "--skip-llm"
}
if ($CleanCache) {
  $argsList += "--clean-cache"
}

& $python.Source @argsList
