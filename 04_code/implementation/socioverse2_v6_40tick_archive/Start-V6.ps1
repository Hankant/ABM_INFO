param([string]$Resume)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$loadedCredential = $false
if (-not $env:RUMOR_LLM_API_KEY) {
    $credentialFile = Join-Path $env:LOCALAPPDATA 'SocioVerse2\secrets\minimax-key.dpapi'
    if (-not (Test-Path -LiteralPath $credentialFile)) {
        throw 'Run Initialize-MiniMax.ps1 first. No request made.'
    }
    $secureKey = ConvertTo-SecureString ([System.IO.File]::ReadAllText($credentialFile))
    $pointer = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try {
        $env:RUMOR_LLM_API_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
        $loadedCredential = $true
    } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
        $secureKey.Dispose()
    }
}
$python = Join-Path $PSScriptRoot '..\socioverse2-contest\.venv\Scripts\python.exe'
$runArgs = @('run.py','--config','minimax.config.json','--live','--token-plan-run','--steps','40','--max-requests','12200')
if ($Resume) { $runArgs += @('--resume',$Resume) }
try {
    & $python @runArgs
    if ($LASTEXITCODE -ne 0) { throw 'V6 stopped. Inspect logs and resume this V6 branch; do not restart or increase budget automatically.' }
} finally {
    if ($loadedCredential) { Remove-Item Env:RUMOR_LLM_API_KEY -ErrorAction SilentlyContinue }
}
