param([ValidateSet('offline','api')][string]$Mode = 'offline')
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskBundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if (Test-Path -LiteralPath $taskBundled) {
    $taskPython = $taskBundled
} else {
    $taskFound = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $taskFound) { throw 'Python 3.11+ is required. Install Python and reopen this launcher.' }
    $taskPython = $taskFound.Source
}
if ($Mode -eq 'offline') {
    & $taskPython (Join-Path $taskRoot 'test_all.py')
    if ($LASTEXITCODE -ne 0) { throw 'Offline tests failed; see output above.' }
    $taskRunName = 'outputs/my_offline_check_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
    & $taskPython (Join-Path $taskRoot 'run.py') run --event (Join-Path $taskRoot 'data/imported/event_052/event.json') --provider mock --tg 50 --output (Join-Path $taskRoot $taskRunName)
    if ($LASTEXITCODE -ne 0) { throw 'Offline run failed; see status.json and output above.' }
} else {
    $taskPreviousKey = $env:RUMOR_LLM_API_KEY
    $taskSecret = Read-Host 'API Key (hidden input)' -AsSecureString
    $taskPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($taskSecret)
    try {
        $env:RUMOR_LLM_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($taskPointer)
        & $taskPython (Join-Path $taskRoot 'tools/probe_api.py')
        if ($LASTEXITCODE -ne 0) { throw 'API probe failed. Inspect the provider audit; no simulation result was substituted.' }
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($taskPointer)
        if ($null -eq $taskPreviousKey) { Remove-Item Env:RUMOR_LLM_API_KEY -ErrorAction SilentlyContinue }
        else { $env:RUMOR_LLM_API_KEY = $taskPreviousKey }
    }
}
