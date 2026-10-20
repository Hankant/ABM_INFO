param([string]$RunDirectory)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$taskRuns = Join-Path $taskRoot '06_experiments/results/socioverse2_v4'
$taskLog = Join-Path $taskRoot '06_experiments/logs/socioverse2_v4/auto-resume.jsonl'
if (-not $RunDirectory) {
    $RunDirectory = Join-Path $taskRuns 'government-rumor-v4-openai-20261020-004902-188523'
}
$RunDirectory = (Resolve-Path -LiteralPath $RunDirectory).Path
$taskMutex = [System.Threading.Mutex]::new($false, 'Local\SocioVerse2V4AutoResume')
$taskOwned = $false
try {
    try { $taskOwned = $taskMutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $taskOwned = $true }
    if (-not $taskOwned) { throw 'An automatic resume supervisor is already active.' }
    $taskRetries = 0
    $taskBestTick = -1
    while ($true) {
        # Follow only direct descendants; never choose an unrelated latest experiment.
        $taskChildren = @(Get-ChildItem $taskRuns -Directory | Where-Object {
            $taskProvPath = Join-Path $_.FullName 'provenance.json'
            if (Test-Path -LiteralPath $taskProvPath) {
                $taskProv = Get-Content -LiteralPath $taskProvPath -Raw -Encoding utf8 | ConvertFrom-Json
                $taskProv.resumed_from -eq $RunDirectory
            }
        })
        if ($taskChildren.Count -gt 1) { throw 'Multiple continuation branches found; select the intended RunDirectory explicitly.' }
        if ($taskChildren.Count -eq 1) { $RunDirectory = $taskChildren[0].FullName; continue }
        $taskState = Get-Content (Join-Path $RunDirectory 'status.json') -Raw -Encoding utf8 | ConvertFrom-Json
        if ($taskState.status -eq 'completed_live' -and $taskState.last_completed_tick -ge 40) {
            Write-Host 'Completed 40 ticks. Supervisor stopped.'
            break
        }
        if ($taskState.status -eq 'running') { throw 'Run is marked running. Do not start a second instance; inspect its process first.' }
        $taskProv = Get-Content (Join-Path $RunDirectory 'provenance.json') -Raw -Encoding utf8 | ConvertFrom-Json
        $taskLatest = Get-ChildItem -LiteralPath $taskProv.audit_dir -Filter 'request-*.json' | Sort-Object Name -Descending | Select-Object -First 1
        if (-not $taskLatest) { throw 'No request diagnostic available.' }
        $taskRequest = Get-Content -LiteralPath $taskLatest.FullName -Raw -Encoding utf8 | ConvertFrom-Json
        if ($taskState.status -ne 'interrupted' -or $taskState.error_type -ne 'RuntimeError' -or
            $taskRequest.status -ne 'request_error' -or $taskRequest.diagnostic.exception_type -ne 'APITimeoutError') {
            throw 'Not a confirmed API timeout; automatic resume stopped for inspection.'
        }
        if ($taskState.last_completed_tick -gt $taskBestTick) {
            $taskBestTick = $taskState.last_completed_tick
            $taskRetries = 0
        }
        if ($taskRetries -ge 3) { throw 'Three automatic resumptions without a newly completed tick; stopped.' }
        if ([string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) { & "$PSScriptRoot/Configure-MiniMax.ps1" }
        if ([string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) { throw 'API key unavailable.' }
        $taskRetries++
        @{time=(Get-Date).ToString('o'); run=$RunDirectory; action='wait_then_resume'; seconds=60;
            attempt=$taskRetries; last_completed_tick=$taskBestTick; request=$taskLatest.Name} |
            ConvertTo-Json -Compress | Add-Content -LiteralPath $taskLog -Encoding utf8
        Write-Host "Timeout: resume in 60 seconds ($taskRetries/3), checkpoint tick $taskBestTick."
        Start-Sleep -Seconds 60
        try { & "$PSScriptRoot/Resume-MiniMax-Simulation.ps1" -RunDirectory $RunDirectory }
        catch { Write-Host 'Child run stopped; checking its durable diagnostic before any further retry.' }
        $taskNewChild = @(Get-ChildItem $taskRuns -Directory | Where-Object {
            $taskPath = Join-Path $_.FullName 'provenance.json'
            if (Test-Path -LiteralPath $taskPath) {
                (Get-Content -LiteralPath $taskPath -Raw -Encoding utf8 | ConvertFrom-Json).resumed_from -eq $RunDirectory
            }
        })
        if ($taskNewChild.Count -ne 1) { throw 'Resume did not create exactly one traceable child; inspect launch error.' }
        $RunDirectory = $taskNewChild[0].FullName
    }
} finally {
    if ($taskOwned) { $taskMutex.ReleaseMutex() }
    $taskMutex.Dispose()
}
