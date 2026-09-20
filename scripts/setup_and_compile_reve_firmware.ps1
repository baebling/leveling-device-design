param(
    [string]$ArduinoCliVersion = "1.5.1"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ToolDir = Join-Path $Root ".tools\arduino-cli"
$DownloadDir = Join-Path $Root ".codex_tmp\arduino-cli"
$ArduinoRoot = Join-Path $Root ".arduino"
$ZipName = "arduino-cli_${ArduinoCliVersion}_Windows_64bit.zip"
$ZipPath = Join-Path $DownloadDir $ZipName
$ChecksumsPath = Join-Path $DownloadDir "checksums.txt"
$BaseUrl = "https://github.com/arduino/arduino-cli/releases/download/v$ArduinoCliVersion"

New-Item -ItemType Directory -Force $ToolDir, $DownloadDir, $ArduinoRoot | Out-Null

if (-not (Test-Path $ZipPath)) {
    Invoke-WebRequest -Uri "$BaseUrl/$ZipName" -OutFile $ZipPath
}
Invoke-WebRequest -Uri "$BaseUrl/$ArduinoCliVersion-checksums.txt" -OutFile $ChecksumsPath

$checksumLine = Get-Content $ChecksumsPath | Where-Object { $_ -match [regex]::Escape($ZipName) } | Select-Object -First 1
if (-not $checksumLine) {
    throw "Checksum for $ZipName was not found."
}
$expectedHash = ($checksumLine -split '\s+')[0].ToUpperInvariant()
$actualHash = (Get-FileHash -Algorithm SHA256 $ZipPath).Hash.ToUpperInvariant()
if ($actualHash -ne $expectedHash) {
    throw "Arduino CLI checksum mismatch: expected $expectedHash, got $actualHash"
}

Expand-Archive -Path $ZipPath -DestinationPath $ToolDir -Force
$Cli = Join-Path $ToolDir "arduino-cli.exe"
if (-not (Test-Path $Cli)) {
    throw "arduino-cli.exe was not extracted to $ToolDir"
}

$env:ARDUINO_DIRECTORIES_DATA = Join-Path $ArduinoRoot "data"
$env:ARDUINO_DIRECTORIES_DOWNLOADS = Join-Path $ArduinoRoot "staging"
$env:ARDUINO_DIRECTORIES_USER = Join-Path $ArduinoRoot "user"
$env:ARDUINO_UPDATER_ENABLE_NOTIFICATION = "false"

& $Cli version
& $Cli core update-index
if ($LASTEXITCODE -ne 0) { throw "Arduino package index update failed." }
& $Cli core install arduino:avr
if ($LASTEXITCODE -ne 0) { throw "arduino:avr core installation failed." }

$Sketch = Join-Path $Root "firmware\reve_leveling_controller"
$Build = Join-Path $Root "outputs\profile_radial_revE_poc_release_candidate\firmware_build"
New-Item -ItemType Directory -Force $Build | Out-Null
& $Cli compile --fqbn arduino:avr:mega --warnings all --output-dir $Build $Sketch
if ($LASTEXITCODE -ne 0) { throw "Rev E Mega2560 firmware compilation failed." }

$record = @(
    "Arduino CLI version: $ArduinoCliVersion",
    "Arduino CLI SHA256: $actualHash",
    "FQBN: arduino:avr:mega",
    "Sketch: $Sketch",
    "Build output: $Build",
    "Compiled UTC: $([DateTime]::UtcNow.ToString('o'))"
)
$record | Set-Content -Encoding UTF8 (Join-Path $Build "compile_record.txt")
Write-Host "Rev E firmware compile PASS"
