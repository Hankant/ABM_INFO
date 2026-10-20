$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$sourcePath = Join-Path $projectRoot '04_code/third_party_reference/SocioVerse2'
$pinnedCommit = '9c3ac774816511c121184ca11f539dc398ba1544'
if (-not (Test-Path -LiteralPath $sourcePath)) {
    git clone https://github.com/sii-research/SocioVerse2.git $sourcePath
    if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
    git -C $sourcePath checkout --detach $pinnedCommit
    if ($LASTEXITCODE -ne 0) { throw 'Pinned source checkout failed' }
}
$actualCommit = git -C $sourcePath rev-parse HEAD
if ($actualCommit -ne $pinnedCommit) { throw 'Upstream commit changed; review before changing the baseline.' }
uv venv --allow-existing --python 3.12 "$PSScriptRoot/.venv"
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
uv pip install --python "$PSScriptRoot/.venv/Scripts/python.exe" -r "$PSScriptRoot/requirements-lock.txt"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
uv pip install --python "$PSScriptRoot/.venv/Scripts/python.exe" --no-deps -e $sourcePath
if ($LASTEXITCODE -ne 0) { throw 'SocioVerse2 installation failed' }
