$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path $Python)) {
    throw "Bundled Python runtime not found: $Python"
}

$env:PYTHONPATH = "$ProjectRoot;$ProjectRoot\vendor\python"
$env:XDG_CACHE_HOME = "$ProjectRoot\.cache"
$env:MPLCONFIGDIR = "$ProjectRoot\.mplcache"

Push-Location $ProjectRoot
try {
    & $Python .\scripts\run_navimro_fabrication.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $Python -c "import pathlib,sys,unittest; root=pathlib.Path.cwd(); sys.path.insert(0,str(root)); sys.path.insert(0,str(root/'vendor'/'python')); suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py'); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)"
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}

