$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
if ([string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) {
    & "$PSScriptRoot/Configure-MiniMax.ps1"
}
Write-Host 'Starting LIVE V4 engineering run: 582 agents, 305 LLM / 277 rule, 40 ticks.'
Write-Host 'MiniMax-M3; Token Plan quota/credits; maximum 12200 requests including retries.'
Write-Host 'PBd=0; GT=0.6; RF=0.6; inside strategy; government response at tick20.'
Write-Host 'No API-key files, no pay-as-you-go fallback, no scripted fallback.'
& "$PSScriptRoot/.venv/Scripts/python.exe" "$PSScriptRoot/run.py" --live --config "$PSScriptRoot/minimax.run.config.json" --token-plan-run --max-requests 12200 --steps 40
if ($LASTEXITCODE -ne 0) {
    throw 'Simulation stopped. Completed ticks are preserved; inspect latest status and diagnostics before restarting.'
}
