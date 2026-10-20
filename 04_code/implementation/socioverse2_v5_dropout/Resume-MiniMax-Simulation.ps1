param([string]$RunDirectory)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
if (-not $RunDirectory) {
    $taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
    $taskRuns = Join-Path $taskRoot '06_experiments/results/socioverse2_v5_dropout'
    $taskCandidate = Get-ChildItem $taskRuns -Directory -Filter '*openai*' | Sort-Object Name -Descending | Where-Object {
        Test-Path (Join-Path $_.FullName 'status.json')
    } | Select-Object -First 1
    if (-not $taskCandidate) { throw 'No live run exists.' }
    $RunDirectory = $taskCandidate.FullName
}
$taskState = Get-Content (Join-Path $RunDirectory 'status.json') -Raw -Encoding utf8 | ConvertFrom-Json
if ($taskState.status -eq 'completed_live') { throw 'Latest run already completed; nothing to resume.' }
if ([string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) {
    & "$PSScriptRoot/../socioverse2_v4/Configure-MiniMax.ps1"
}
Write-Host "Resuming in a NEW output directory from: $RunDirectory"
& "$PSScriptRoot/../socioverse2_v4/.venv/Scripts/python.exe" "$PSScriptRoot/run.py" --live --config "$PSScriptRoot/../socioverse2_v4/minimax.run.config.json" --token-plan-run --max-requests 12200 --steps 40 --resume $RunDirectory
if ($LASTEXITCODE -ne 0) { throw 'Run paused/stopped; inspect diagnostics. Do not start a fresh run to bypass quota.' }
