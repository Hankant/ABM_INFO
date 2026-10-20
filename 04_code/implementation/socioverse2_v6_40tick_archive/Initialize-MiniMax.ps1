$ErrorActionPreference = 'Stop'
$credentialDir = Join-Path $env:LOCALAPPDATA 'SocioVerse2\secrets'
$credentialFile = Join-Path $credentialDir 'minimax-key.dpapi'
$secureKey = Read-Host 'Paste MiniMax Token Plan key (hidden), then press Enter' -AsSecureString
if ($secureKey.Length -eq 0) { throw 'Empty key. Nothing saved.' }
try {
    $encrypted = ConvertFrom-SecureString -SecureString $secureKey
    [System.IO.Directory]::CreateDirectory($credentialDir) | Out-Null
    [System.IO.File]::WriteAllText($credentialFile, $encrypted, [System.Text.Encoding]::ASCII)
    Write-Host 'Saved with Windows current-user encryption. No API request made.'
    Write-Host 'Return to the chat and say: initialized.'
} finally {
    if ($secureKey) { $secureKey.Dispose() }
    $encrypted = $null
}
