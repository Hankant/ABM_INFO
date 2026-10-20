$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
if ([string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) {
    & "$PSScriptRoot/Configure-MiniMax.ps1"
}
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$taskParent = Join-Path $taskRoot '06_experiments/results/socioverse2_v4/government-rumor-v4-openai-20261019-223648-884905'
Write-Host 'Replay ticks0-19; continue tick20. Maximum4 generations per decision, not4 extra retries.'
Write-Host 'Reuse identical successful responses; retain original budget and failed responses.'
& "$PSScriptRoot/.venv/Scripts/python.exe" "$PSScriptRoot/run.py" --live --config "$PSScriptRoot/minimax.run.config.json" --token-plan-run --max-requests 12200 --steps 40 --resume $taskParent --retry-policy-migration
if ($LASTEXITCODE -ne 0) { throw 'Stopped/paused; inspect logs, then use Resume-MiniMax-Simulation.ps1 for this new run.' }
