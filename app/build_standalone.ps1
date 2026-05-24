$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

python -m pip install -r desktop_requirements.txt
python -m PyInstaller --clean LRNTrackingSystem.spec

Write-Host ""
Write-Host "Standalone build created at:"
Write-Host (Join-Path $PSScriptRoot "dist\LRN Tracking System\LRN Tracking System.exe")
