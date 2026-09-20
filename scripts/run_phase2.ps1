$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$CandidatePythons = @(
    $env:CODEX_PYTHON,
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "python"
) | Where-Object { $_ }

$Python = $null
foreach ($Candidate in $CandidatePythons) {
    try {
        $Command = Get-Command $Candidate -ErrorAction Stop
        if ($Command.Source) {
            $Python = $Command.Source
        } else {
            $Python = $Command.Path
        }
        break
    } catch {
        if (Test-Path -LiteralPath $Candidate) {
            $Python = $Candidate
            break
        }
    }
}

if (-not $Python) {
    throw "Python executable not found. Set CODEX_PYTHON to a Python 3.12 executable."
}

$env:PYTHONPATH = "$ProjectRoot;$ProjectRoot\vendor\python"
$env:MPLCONFIGDIR = "$ProjectRoot\.mplcache"
$env:XDG_CACHE_HOME = "$ProjectRoot\.cache"
& $Python "$PSScriptRoot\run_phase2.py"
exit $LASTEXITCODE
