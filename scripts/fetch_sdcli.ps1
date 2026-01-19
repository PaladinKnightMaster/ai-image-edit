param(
  [ValidateSet("avx2", "avx", "noavx", "cuda12")][string]$Variant = "avx2",
  [string]$VersionTag = "master-474-61659ef",
  [string]$InstallDir = ".\\tools\\sdcli"
)

$ErrorActionPreference = "Stop"

$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if (-not $curl) {
  throw "curl.exe not found. Install curl or download manually."
}

$commit = $VersionTag.Split("-")[-1]
$assetName = "sd-master-$commit-bin-win-$Variant-x64.zip"
$url = "https://github.com/leejet/stable-diffusion.cpp/releases/download/$VersionTag/$assetName"

$downloadDir = Join-Path $InstallDir "_downloads"
$extractDir = Join-Path $InstallDir $VersionTag
$extractDir = Join-Path $extractDir $Variant

New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null
New-Item -ItemType Directory -Force -Path $extractDir | Out-Null

$downloadPath = Join-Path $downloadDir $assetName

if (-not (Test-Path $downloadPath)) {
  Write-Host "Downloading $url -> $downloadPath"
  & $curl.Source -L -C - -o $downloadPath $url
} else {
  Write-Host "Skip: $downloadPath already exists."
}

$zipInfo = Get-Item $downloadPath
if ($zipInfo.Length -lt 1000000) {
  throw "Downloaded zip is too small ($($zipInfo.Length) bytes). Check the URL or network."
}

Write-Host "Extracting $downloadPath -> $extractDir"
Expand-Archive -Force -Path $downloadPath -DestinationPath $extractDir

$exe = Get-ChildItem -Path $extractDir -Recurse -Filter "sd-cli.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $exe) {
  $exe = Get-ChildItem -Path $extractDir -Recurse -Filter "sd.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
}

if (-not $exe) {
  throw "Could not find sd-cli.exe or sd.exe in $extractDir"
}

Write-Host "Done. Use this path for FLUX2_SDCLI_PATH:"
Write-Host $exe.FullName
