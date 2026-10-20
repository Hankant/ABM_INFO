param([switch]$TestConnection)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$taskSecret = Read-Host 'MiniMax API Key (hidden input)' -AsSecureString
$env:RUMOR_LLM_API_KEY = ([System.Net.NetworkCredential]::new('', $taskSecret).Password).Trim()
Remove-Variable taskSecret
if ([string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) { throw 'API Key is empty' }
Write-Host 'MiniMax key set for this PowerShell session only. No key was saved to disk.'
Write-Host 'Config: minimax.config.json | MiniMax-M3 | https://api.minimax.cn/v1'
if ($TestConnection) {
    & "$PSScriptRoot/.venv/Scripts/python.exe" "$PSScriptRoot/check_minimax.py"
    if ($LASTEXITCODE -ne 0) { throw 'Connection check failed. See the local diagnostic path printed above.' }
} else {
    Write-Host 'No API call made. To make one paid synthetic check: ./.venv/Scripts/python.exe check_minimax.py'
}
