$ErrorActionPreference = 'Stop'
$pythonPath = $env:CCS_PYTHON
if (-not $pythonPath) {
    $pointer = Join-Path $PSScriptRoot '.ccs-python'
    if (Test-Path -LiteralPath $pointer) {
        $pythonPath = (Get-Content -LiteralPath $pointer -Encoding UTF8 -Raw).Trim()
    }
}
if (-not $pythonPath) {
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $projectPython) { $pythonPath = $projectPython }
}
if (-not $pythonPath) {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($command) { $pythonPath = $command.Source }
}
if (-not $pythonPath -or -not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Python environment is missing. Run .\setup.ps1 or set CCS_PYTHON.'
}
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
& $pythonPath -m ccs @args
exit $LASTEXITCODE
