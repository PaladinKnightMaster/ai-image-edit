function Invoke-WithPythonSitePackages {
  param(
    [string]$SitePackages,
    [scriptblock]$ScriptBlock
  )

  $previousPythonPath = $env:PYTHONPATH
  try {
    if ($SitePackages) {
      if ($previousPythonPath) {
        $env:PYTHONPATH = "$SitePackages;$previousPythonPath"
      }
      else {
        $env:PYTHONPATH = $SitePackages
      }
    }

    & $ScriptBlock
  }
  finally {
    if ($null -eq $previousPythonPath) {
      Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    }
    else {
      $env:PYTHONPATH = $previousPythonPath
    }
  }
}

function Get-BasePythonPath {
  param(
    [string]$PyVenvCfgPath
  )

  if (-not (Test-Path $PyVenvCfgPath)) {
    return $null
  }

  $lines = Get-Content $PyVenvCfgPath
  $executableLine = $lines | Where-Object { $_ -match '^executable\s*=' } | Select-Object -First 1
  if ($executableLine) {
    $executable = ($executableLine -split '=', 2)[1].Trim()
    if ($executable) {
      return $executable
    }
  }

  $homeLine = $lines | Where-Object { $_ -match '^home\s*=' } | Select-Object -First 1
  if ($homeLine) {
    $home = ($homeLine -split '=', 2)[1].Trim()
    if ($home) {
      return Join-Path $home "python.exe"
    }
  }

  return $null
}

function Test-PythonSpec {
  param(
    [pscustomobject]$Spec,
    [string[]]$RequiredImports
  )

  if (-not (Test-Path $Spec.Executable)) {
    return $false
  }

  $probeScript = (($RequiredImports | ForEach-Object { "import $_" }) + "print('ok')") -join "; "

  try {
    Invoke-WithPythonSitePackages -SitePackages $Spec.SitePackages -ScriptBlock {
      & $Spec.Executable -c $probeScript *> $null
    }
    return $LASTEXITCODE -eq 0
  }
  catch {
    return $false
  }
}

function Resolve-PythonSpec {
  param(
    [string]$RepoRoot,
    [string]$BackendRoot,
    [string[]]$RequiredImports
  )

  $attempted = @()
  $overrideExecutable = $env:AI_IMAGE_EDIT_PYTHON
  $overrideSitePackages = $env:AI_IMAGE_EDIT_PYTHON_SITE_PACKAGES
  if ($overrideExecutable) {
    $overrideSpec = [pscustomobject]@{
      Executable = $overrideExecutable
      SitePackages = $overrideSitePackages
      Source = "env-override"
    }
    $attempted += if ($overrideSitePackages) {
      "$overrideExecutable + $overrideSitePackages"
    }
    else {
      $overrideExecutable
    }
    if (Test-PythonSpec -Spec $overrideSpec -RequiredImports $RequiredImports) {
      return $overrideSpec
    }
  }

  $venvRoots = @(
    (Join-Path $backendRoot ".venv"),
    (Join-Path $repoRoot ".venv")
  )

  foreach ($venvRoot in $venvRoots) {
    $launcher = Join-Path $venvRoot "Scripts\python.exe"
    $sitePackages = Join-Path $venvRoot "Lib\site-packages"
    $pyvenvCfg = Join-Path $venvRoot "pyvenv.cfg"

    $launcherSpec = [pscustomobject]@{
      Executable = $launcher
      SitePackages = $null
      Source = "venv-launcher"
    }

    if (Test-Path $launcher) {
      $attempted += $launcher
      if (Test-PythonSpec -Spec $launcherSpec -RequiredImports $RequiredImports) {
        return $launcherSpec
      }
    }

    $basePython = Get-BasePythonPath -PyVenvCfgPath $pyvenvCfg
    if ($basePython -and (Test-Path $basePython) -and (Test-Path $sitePackages)) {
      $attempted += "$basePython + $sitePackages"
      $fallbackSpec = [pscustomobject]@{
        Executable = $basePython
        SitePackages = $sitePackages
        Source = "base-python-with-site-packages"
      }

      if (Test-PythonSpec -Spec $fallbackSpec -RequiredImports $RequiredImports) {
        return $fallbackSpec
      }
    }
  }

  throw "No working Python runtime found. Attempted: $($attempted -join ', ')"
}
