$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$tmpRoot = Join-Path $projectRoot 'tmp'
$stage = Join-Path $tmpRoot ("Profile_Radial_3RPS_RevD_package_" + [guid]::NewGuid().ToString('N'))
$tempZip = "$stage.zip"
$targetZip = Join-Path $projectRoot 'output\Profile_Radial_3RPS_RevD_Fusion360_Native.zip'
$hashPath = "$targetZip.sha256"

$stageFull = [IO.Path]::GetFullPath($stage)
$tmpFull = [IO.Path]::GetFullPath($tmpRoot).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $stageFull.StartsWith($tmpFull, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Unsafe stage path: $stageFull"
}

$files = @(
    'design_basis\profile_radial_revD_fusion_native_2026-08-31.md',
    'fusion_scripts\ProfileRadialRevD\__init__.py',
    'fusion_scripts\ProfileRadialRevD\ProfileRadialRevD.manifest',
    'fusion_scripts\ProfileRadialRevD\ProfileRadialRevD.py',
    'fusion_scripts\ProfileRadialRevD\revd_data.py',
    'logs\work_history.md',
    'procurement\profile_radial_revD_structural_bom_2026-08-31.md',
    'procurement\profile_radial_revd_navimro_candidate_bom_2026-09-01.csv',
    'procurement\profile_radial_revd_navimro_candidate_bom_2026-09-01.md',
    'procurement\profile_radial_revd_split_source_order_groups_2026-09-01.csv',
    'procurement\profile_radial_revd_split_source_purchase_plan_2026-09-01.md',
    'procurement\profile_radial_revd_single_order_gap_list_2026-09-01.csv',
    'procurement\profile_radial_revd_single_order_readiness_2026-09-01.md',
    'scripts\export_profile_radial_revd_fabrication.py',
    'scripts\verify_profile_radial_revd_step.py',
    'scripts\package_profile_radial_revd.ps1',
    'tests\test_profile_radial_revd.py',
    'PROJECT_HANDOFF.md',
    'README.md'
)

New-Item -ItemType Directory -Path $stage -Force | Out-Null
foreach ($relative in $files) {
    $source = Join-Path $projectRoot $relative
    $destination = Join-Path $stage $relative
    New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Force
}

$outputRelative = 'outputs\profile_radial_revD_fusion_native'
$outputParent = Join-Path $stage 'outputs'
New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot $outputRelative) -Destination $outputParent -Recurse -Force

Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $tempZip -CompressionLevel Optimal
Move-Item -LiteralPath $tempZip -Destination $targetZip -Force

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($targetZip)
try {
    $buffer = New-Object byte[] 81920
    foreach ($entry in $archive.Entries) {
        if ([string]::IsNullOrEmpty($entry.Name)) { continue }
        $stream = $entry.Open()
        try {
            while ($stream.Read($buffer, 0, $buffer.Length) -gt 0) { }
        }
        finally {
            $stream.Dispose()
        }
    }
    $entryCount = $archive.Entries.Count
}
finally {
    $archive.Dispose()
}

$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $targetZip).Hash.ToLowerInvariant()
Set-Content -LiteralPath $hashPath -Value "$hash *$(Split-Path $targetZip -Leaf)" -Encoding ascii

Remove-Item -LiteralPath $stage -Recurse -Force

[pscustomobject]@{
    Zip = $targetZip
    Entries = $entryCount
    Bytes = (Get-Item -LiteralPath $targetZip).Length
    Sha256 = $hash
    CrcRead = 'PASS'
}
