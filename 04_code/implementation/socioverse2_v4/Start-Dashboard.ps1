param([int]$Port = 8787)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$pythonExe = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$serverPath = Join-Path $projectRoot '04_code/third_party_reference/SocioVerse2/dashboard/server/app.py'
$resultsPath = Join-Path $projectRoot '06_experiments/results/socioverse2_v4'
& $pythonExe $serverPath --host 127.0.0.1 --port $Port --root $resultsPath
