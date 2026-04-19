param(
  [string]$BackendUrl = "http://127.0.0.1:8000",
  [int]$TimeoutSec = 1800,
  [int]$PollIntervalSec = 5
)

$ErrorActionPreference = "Stop"

function Get-Models {
  return Invoke-RestMethod -Uri "$BackendUrl/api/models" -Method Get
}

function Get-JobState {
  param(
    [Parameter(Mandatory = $true)]
    [string]$JobId
  )

  return Invoke-RestMethod -Uri "$BackendUrl/api/jobs/$JobId" -Method Get
}

$models = Get-Models
$model = $models | Where-Object { $_.id -eq "qwen-image-2512" } | Select-Object -First 1

if (-not $model) {
  $available = if ($models) {
    ($models | ForEach-Object { $_.id }) -join ", "
  } else {
    "<none>"
  }
  throw "qwen-image-2512 is not registered. Available models: $available"
}

if (-not $model.present) {
  $detail = if ($model.detail) { " Detail: $($model.detail)" } else { "" }
  throw "qwen-image-2512 is registered but not ready.$detail"
}

$payload = @{
  model_id = "qwen-image-2512"
  prompt = "a cinematic portrait of a robot painter"
  negative_prompt = "blurry, low quality"
  seed = 1234
  steps = 8
  width = 512
  height = 512
  guidance_scale = 3.5
  true_cfg_scale = 1.1
} | ConvertTo-Json

Write-Host "Submitting Sprint 1 smoke run to $BackendUrl using qwen-image-2512"
$job = Invoke-RestMethod -Uri "$BackendUrl/api/jobs/t2i" -Method Post -ContentType "application/json" -Body $payload
$jobId = $job.job_id

if (-not $jobId) {
  throw "Smoke run submission did not return a job_id."
}

Write-Host "Submitted job_id=$jobId"

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$lastStatus = ""

while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds $PollIntervalSec
  $state = Get-JobState -JobId $jobId
  if ($state.status -ne $lastStatus) {
    Write-Host "status=$($state.status)"
    $lastStatus = $state.status
  }

  if ($state.status -eq "succeeded") {
    $outputImageId = $state.run.output_image_id
    Write-Host "Smoke run succeeded. job_id=$jobId output_image_id=$outputImageId"
    exit 0
  }

  if ($state.status -eq "failed") {
    $error = if ($state.error) { $state.error } else { "unknown error" }
    throw "Smoke run failed for job_id=$jobId. $error"
  }
}

throw "Smoke run timed out after $TimeoutSec seconds for job_id=$jobId."
