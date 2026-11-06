$ErrorActionPreference = "Stop"

$installDir = Join-Path $env:LOCALAPPDATA "Programs\media_dn"
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

py -3 -m pip install --user -r (Join-Path $PSScriptRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Check that Python is installed."
}

Copy-Item (Join-Path $PSScriptRoot "media_dn.py") $installDir -Force

$wrapper = @'
@echo off
py -3 "%~dp0media_dn.py" %*
'@
Set-Content (Join-Path $installDir "media_dn.cmd") $wrapper -Encoding ASCII

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$paths = @($userPath -split ";" | Where-Object { $_ })
if ($paths -notcontains $installDir) {
    $newPath = (@($paths) + $installDir) -join ";"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
}

Write-Host ""
Write-Host "Installed. Close and reopen your terminal, then run:"
Write-Host "  media_dn"
Write-Host '  media-dn "search words" --quality 1080'
