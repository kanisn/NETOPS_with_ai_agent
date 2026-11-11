param(
    [string]$VenvPath = (Join-Path $PSScriptRoot '.venv'),
    [string]$WorkDirectory,
    [string]$PythonExecutable = 'python',
    [switch]$SkipDependencyInstall
)

$ErrorActionPreference = 'Stop'
$VenvPath = [System.IO.Path]::GetFullPath($VenvPath)
$venvParent = Split-Path -Parent $VenvPath
New-Item -ItemType Directory -Path $venvParent -Force | Out-Null

# Keep setup scratch and pip cache outside the synchronized project when D: is available.
if (-not $WorkDirectory -and $env:CCS_WORKING_ROOT) {
    $WorkDirectory = Join-Path $env:CCS_WORKING_ROOT 'setup-cache'
}
if (-not $WorkDirectory) {
    $WorkDirectory = if (Test-Path -LiteralPath 'D:\Codex\WorkingFiles') {
        Join-Path 'D:\Codex\WorkingFiles' 'ccs_testbed_setup'
    } else {
        Join-Path $venvParent 'setup-working'
    }
}
$workDirectory = [System.IO.Path]::GetFullPath($WorkDirectory)
New-Item -ItemType Directory -Path $workDirectory -Force | Out-Null
$env:TEMP = $workDirectory
$env:TMP = $workDirectory
$env:TMPDIR = $workDirectory
$env:PIP_CACHE_DIR = Join-Path $workDirectory 'pip-cache'
$env:PYTHONDONTWRITEBYTECODE = '1'

$python = Join-Path $VenvPath 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & $PythonExecutable -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' }
}
& $python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 'Python 3.11 or newer is required.')"
if ($LASTEXITCODE -ne 0) { throw 'Selected Python runtime is too old.' }

# Bootstrap only missing local configuration. Existing credentials, settings, and ledgers stay intact.
$configDirectory = Join-Path $PSScriptRoot 'configs'
New-Item -ItemType Directory -Path $configDirectory -Force | Out-Null
$localConfigs = @(
    @{ Source = (Join-Path $configDirectory 'ai.example.xml'); Destination = (Join-Path $configDirectory 'ai.local.xml') },
    @{ Source = (Join-Path $configDirectory 'system.example.xml'); Destination = (Join-Path $configDirectory 'system.xml') }
)
foreach ($item in $localConfigs) {
    if (-not (Test-Path -LiteralPath $item.Destination)) {
        Copy-Item -LiteralPath $item.Source -Destination $item.Destination
        Write-Output "Created missing local configuration: $($item.Destination)"
    } else {
        Write-Output "Kept existing local configuration: $($item.Destination)"
    }
}

Set-Content -LiteralPath (Join-Path $PSScriptRoot '.ccs-python') -Value $python -Encoding utf8
if (-not $SkipDependencyInstall) {
    & $python -m pip install -r (Join-Path $PSScriptRoot 'requirements.lock')
    if ($LASTEXITCODE -ne 0) { throw 'Pinned dependency installation failed.' }
}

Write-Output "Python environment: $python"
Write-Output 'Run .\ccs.ps1 doctor, then .\ccs.ps1 run --mode mock.'
