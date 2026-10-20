param(
    [ValidateSet('offline','http')][string]$Mode = 'offline',
    [int]$MaxRequests = 0,
    [ValidateSet(10,20,30,40,50)][int]$TG = 20,
    [ValidateSet('inside','random','outside')][string]$Targeting = 'inside',
    [ValidateSet(0.2,0.6,1.0)][double]$GT = 0.6,
    [string]$Output = ''
)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskBundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if (Test-Path -LiteralPath $taskBundled) { $taskPython = $taskBundled }
else {
    $taskFound = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $taskFound) { throw 'Python 3.11+ is required.' }
    $taskPython = $taskFound.Source
}
if ($Mode -eq 'http' -and $MaxRequests -lt 1) {
    $taskBudgetText = Read-Host 'Cumulative API request cap for this output directory (including retries; no default)'
    if (-not [int]::TryParse($taskBudgetText, [ref]$MaxRequests) -or $MaxRequests -lt 1) {
        throw 'A positive explicit request budget is required. No API request was made.'
    }
}
$taskEvent = Join-Path $taskRoot 'data/single_event/event_052/event.json'
if (-not (Test-Path -LiteralPath $taskEvent)) { throw 'Prepared event data is missing. Run: python run.py prepare-single' }
if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $taskRoot ('outputs/single_event_' + $Mode + '_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
}
Write-Host "Output / resume directory: $Output"
$taskArgs = @((Join-Path $taskRoot 'run.py'), 'single-event', '--event', $taskEvent,
    '--config', (Join-Path $taskRoot 'config/single_event.json'), '--tg', "$TG", '--targeting', $Targeting,
    '--gt', $GT.ToString([System.Globalization.CultureInfo]::InvariantCulture), '--output', $Output)
if ($Mode -eq 'offline') { $taskArgs += @('--provider','mock') }
else { $taskArgs += @('--provider','http','--max-api-requests',"$MaxRequests") }
$taskPriorKey = $env:RUMOR_LLM_API_KEY
$taskPointer = [IntPtr]::Zero
try {
    if ($Mode -eq 'http' -and [string]::IsNullOrWhiteSpace($env:RUMOR_LLM_API_KEY)) {
        $taskSecret = Read-Host 'API Key (hidden input)' -AsSecureString
        $taskPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($taskSecret)
        $env:RUMOR_LLM_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($taskPointer)
    }
    & $taskPython @taskArgs
    $taskExit = $LASTEXITCODE
    $taskRuns = Join-Path $Output 'runs'
    if (Test-Path -LiteralPath $taskRuns) {
        foreach ($taskRun in (Get-ChildItem -LiteralPath $taskRuns -Directory)) {
            if (Test-Path -LiteralPath (Join-Path $taskRun.FullName 'exports/summary.json')) {
                & $taskPython (Join-Path $taskRoot 'run.py') report --run $taskRun.FullName
                $taskReport = Join-Path $taskRun.FullName '单事件过程展示.html'
                if (Test-Path -LiteralPath $taskReport) { Invoke-Item -LiteralPath $taskReport }
            }
        }
    }
    if ($taskExit -ne 0) { throw "Run stopped (exit $taskExit). Committed rounds are saved. Resume using the SAME -Output path and settings. No mock replacement was used." }
} finally {
    if ($taskPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($taskPointer) }
    if ($null -eq $taskPriorKey) { Remove-Item Env:RUMOR_LLM_API_KEY -ErrorAction SilentlyContinue }
    else { $env:RUMOR_LLM_API_KEY = $taskPriorKey }
}
