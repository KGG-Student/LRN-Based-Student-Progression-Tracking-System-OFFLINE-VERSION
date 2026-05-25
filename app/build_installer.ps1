$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$appExe = Join-Path $PSScriptRoot "dist\LRN Tracking System\LRN Tracking System.exe"
$installerScript = Join-Path $PSScriptRoot "LRNTrackingSystemInstaller.iss"

if (-not (Test-Path $appExe)) {
    Write-Host "Standalone build was not found."
    Write-Host "Run this first:"
    Write-Host "  .\build_standalone.ps1"
    exit 1
}

$isccCommand = Get-Command "iscc.exe" -ErrorAction SilentlyContinue
$isccPath = if ($isccCommand) { $isccCommand.Source } else { $null }

if (-not $isccPath) {
    $commonPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )

    foreach ($path in $commonPaths) {
        if ($path -and (Test-Path $path)) {
            $isccPath = $path
            break
        }
    }
}

if (-not $isccPath) {
    Write-Host "Inno Setup compiler was not found."
    Write-Host "Install Inno Setup 6, then run this command again:"
    Write-Host "  .\build_installer.ps1"
    Write-Host ""
    Write-Host "Download: https://jrsoftware.org/isdl.php"
    exit 1
}

& $isccPath $installerScript

Write-Host ""
Write-Host "Installer created at:"
Write-Host (Join-Path $PSScriptRoot "installer\LRN-Tracking-System-Setup.exe")
