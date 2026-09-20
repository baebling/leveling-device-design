$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $env:USERPROFILE ".cache\leveling-cadquery-py312"
$CadQueryInit = Join-Path $Runtime "cadquery\__init__.py"

if (-not (Test-Path $CadQueryInit)) {
    New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
    python -m pip install --no-index --find-links (Join-Path $ProjectRoot "wheelhouse") --target $Runtime cadquery==2.8.0 ezdxf==1.4.4 vtk==9.6.2 reportlab==5.0.1
}

$env:PYTHONPATH = "$Runtime;$ProjectRoot"
$env:XDG_CACHE_HOME = Join-Path $ProjectRoot ".cache"
$env:MPLCONFIGDIR = Join-Path $ProjectRoot ".mplcache"

Push-Location $ProjectRoot
try {
    python -m unittest tests.test_manual_turnbuckle_rev_m2 -v
    python -m unittest tests.test_manual_turnbuckle_rev_m2_stability -v
    python scripts/build_manual_turnbuckle_rev_m2.py
    python scripts/verify_manual_turnbuckle_rev_m2.py
    python scripts/verify_manual_turnbuckle_rev_m2_stability.py
}
finally {
    Pop-Location
}
