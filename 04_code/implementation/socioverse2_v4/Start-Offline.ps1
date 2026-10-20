$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
Push-Location $PSScriptRoot
try {
    & "$PSScriptRoot/.venv/Scripts/python.exe" run.py @args
    if ($LASTEXITCODE -ne 0) { throw 'Run stopped. Inspect the run status and local audit logs.' }
} finally { Pop-Location }
