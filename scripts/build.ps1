param(
    [switch]$Clean,
    [switch]$OneDir
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $root
Push-Location $root

Write-Host "==> Building Timetable to Calendar ZJNU" -ForegroundColor Cyan

function Remove-WithRetry {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$Retries = 5,
        [int]$DelayMs = 500
    )
    if (-not (Test-Path $Path)) { return $true }
    for ($i = 0; $i -lt $Retries; $i++) {
        try {
            Remove-Item -Force -ErrorAction Stop -- $Path
            return $true
        }
        catch {
            Start-Sleep -Milliseconds $DelayMs
        }
    }
    return $false
}

# Ensure venv
$venv = Join-Path $root ".venv"
$pyExe = Join-Path $venv "Scripts/python.exe"
if (Test-Path $pyExe) {
    $python = $pyExe
}
else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    py -3 -m venv .venv
    $python = $pyExe
}

Write-Host "Using Python: $python"

# Upgrade pip and install deps
& $python -m pip install --upgrade pip > $null
& $python -m pip install -r requirements.txt pyinstaller > $null

# Clean
if ($Clean) {
    Write-Host "Cleaning build and dist..." -ForegroundColor Yellow
    try { Remove-Item -Recurse -Force -ErrorAction Stop build, dist } catch { }
}

# Generate version info
Write-Host "Generating version info..." -ForegroundColor Yellow
& $python "tools/generate_version_info.py"

# Build
Write-Host "Running PyInstaller..." -ForegroundColor Yellow
$spec = Join-Path $root "gui_win.spec"
$pyiArgs = @("-m", "PyInstaller", $spec, "--noconfirm")
if ($OneDir) { $pyiArgs += "--onedir" }

# Determine output path and try to remove existing EXE
$exeName = "Timetable to Calendar ZJNU.exe"
$distBase = Join-Path $root "dist"
$exe = Join-Path $distBase $exeName
if (Test-Path $exe) {
    if (-not (Remove-WithRetry -Path $exe -Retries 6 -DelayMs 700)) {
        Write-Warning "Could not remove existing EXE (it may be open). Will build into a new dist folder to avoid conflicts."
        $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $distAlt = Join-Path $distBase "build-$timestamp"
        $pyiArgs += @("--distpath", $distAlt)
        $exe = Join-Path $distAlt $exeName
    }
}

& $python $pyiArgs
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

# Show result
if (Test-Path $exe) {
    Write-Host "`nBuild complete: $exe" -ForegroundColor Green
    $vi = (Get-Item $exe).VersionInfo
    "Company:      {0}" -f $vi.CompanyName | Write-Host
    "Product:      {0}" -f $vi.ProductName | Write-Host
    "Description:  {0}" -f $vi.FileDescription | Write-Host
    "Version:      {0}" -f $vi.FileVersion | Write-Host
}
else {
    Write-Error "Build failed. Check PyInstaller output above."
}

Pop-Location
