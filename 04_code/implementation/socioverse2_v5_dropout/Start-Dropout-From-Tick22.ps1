$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
if (-not $env:RUMOR_LLM_API_KEY) { & "$PSScriptRoot/../socioverse2_v4/Configure-MiniMax.ps1" }
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$taskParent = Join-Path $taskRoot '06_experiments/results/socioverse2_v5/government-rumor-v5-openai-20261020-020101-641582'
Write-Host 'NEW dropout branch: replay ticks0-21, continue22. Technical failures permanently offline; old belief retained.'
& "$PSScriptRoot/../socioverse2_v4/.venv/Scripts/python.exe" "$PSScriptRoot/run.py" --live --config "$PSScriptRoot/../socioverse2_v4/minimax.run.config.json" --token-plan-run --max-requests 12200 --steps 40 --resume $taskParent --dropout-migration
if ($LASTEXITCODE -ne 0) { throw 'Global stop. Inspect diagnostic; resume this branch, do not repeat migration.' }
